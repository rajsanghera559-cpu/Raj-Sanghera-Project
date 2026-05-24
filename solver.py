import argparse
import csv
import os

import numpy as np


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run a 2D vorticity turbulence simulation and save spectra."
    )
    parser.add_argument("--N", type=int, default=256, help="Grid size. Default: 256")
    parser.add_argument("--dt", type=float, default=0.0005, help="Timestep. Default: 0.0005")
    parser.add_argument("--nu", type=float, default=0.001, help="Viscosity. Default: 0.001")
    parser.add_argument(
        "--drag-alpha",
        type=float,
        default=0.0,
        help="Global linear vorticity drag coefficient. Default: 0.0",
    )
    parser.add_argument(
        "--lowk-drag-alpha",
        type=float,
        default=0.0,
        help="Low-k selective vorticity drag coefficient. Default: 0.0",
    )
    parser.add_argument(
        "--lowk-drag-kmax",
        type=float,
        default=4.0,
        help="Maximum wavenumber for low-k selective drag. Default: 4",
    )
    parser.add_argument("--steps", type=int, default=50000, help="Number of timesteps. Default: 50000")
    parser.add_argument("--save-every", type=int, default=1000, help="Save interval. Default: 1000")
    parser.add_argument("--seed", type=int, default=0, help="Initial-condition seed. Default: 0")
    parser.add_argument(
        "--forcing-amplitude",
        type=float,
        default=0.01,
        help="Vorticity forcing amplitude. Default: 0.01",
    )
    parser.add_argument(
        "--forcing-mode",
        type=int,
        default=2,
        help="Integer forcing mode m in sin(m x) cos(m y). Default: 2",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for spectra. Default: outputs_spectra/nu_<nu>_f_<amp>_m_<mode>",
    )
    return parser


def make_output_dir(args):
    if args.output_dir:
        return args.output_dir

    drag_suffix = f"_drag_{args.drag_alpha:g}" if args.drag_alpha != 0.0 else ""
    lowk_drag_suffix = (
        f"_lowkdrag_{args.lowk_drag_alpha:g}_k{args.lowk_drag_kmax:g}"
        if args.lowk_drag_alpha != 0.0
        else ""
    )

    return os.path.join(
        "outputs_spectra",
        (
            f"nu_{args.nu:g}_f_{args.forcing_amplitude:g}_m_{args.forcing_mode}"
            f"{drag_suffix}{lowk_drag_suffix}"
        ),
    )


def write_metadata(output_dir, args):
    metadata_path = os.path.join(output_dir, "metadata.csv")
    rows = [
        ("N", args.N),
        ("dt", args.dt),
        ("nu", args.nu),
        ("drag_alpha", args.drag_alpha),
        ("lowk_drag_alpha", args.lowk_drag_alpha),
        ("lowk_drag_kmax", args.lowk_drag_kmax),
        ("steps", args.steps),
        ("save_every", args.save_every),
        ("seed", args.seed),
        ("forcing_amplitude", args.forcing_amplitude),
        ("forcing_mode", args.forcing_mode),
    ]

    with open(metadata_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["key", "value"])
        writer.writerows(rows)


def run_simulation(args):
    output_dir = make_output_dir(args)
    os.makedirs(output_dir, exist_ok=True)
    write_metadata(output_dir, args)

    rng = np.random.default_rng(args.seed)

    L = 2 * np.pi
    dx = L / args.N

    x = np.linspace(0, L, args.N, endpoint=False)
    X, Y = np.meshgrid(x, x)

    k = np.fft.fftfreq(args.N, d=dx) * 2 * np.pi
    kx, ky = np.meshgrid(k, k)

    k2 = kx**2 + ky**2
    k_mag_grid = np.sqrt(k2)
    k2_safe = k2.copy()
    k2_safe[0, 0] = 1.0

    kmax = np.max(np.abs(k))
    dealias_mask = (np.abs(kx) < (2 / 3) * kmax) & (np.abs(ky) < (2 / 3) * kmax)
    lowk_drag_mask = (k_mag_grid > 0) & (k_mag_grid <= args.lowk_drag_kmax)

    w = 1e-4 * rng.standard_normal((args.N, args.N))
    forcing_field = (
        args.forcing_amplitude
        * np.sin(args.forcing_mode * X)
        * np.cos(args.forcing_mode * Y)
    )

    def streamfunction(vorticity):
        w_hat = np.fft.fft2(vorticity)
        psi_hat = -w_hat / k2_safe
        psi_hat[0, 0] = 0.0
        return np.fft.ifft2(psi_hat).real

    def velocity(psi):
        psi_hat = np.fft.fft2(psi)
        u = np.fft.ifft2(1j * ky * psi_hat).real
        v = np.fft.ifft2(-1j * kx * psi_hat).real
        return u, v

    def diffusion(vorticity):
        w_hat = np.fft.fft2(vorticity)
        return np.fft.ifft2(-args.nu * k2 * w_hat).real

    def lowk_drag(vorticity):
        if args.lowk_drag_alpha == 0.0:
            return 0.0

        w_hat = np.fft.fft2(vorticity)
        return np.fft.ifft2(-args.lowk_drag_alpha * lowk_drag_mask * w_hat).real

    def jacobian(a, b):
        ax = (np.roll(a, -1, axis=1) - np.roll(a, 1, axis=1)) / (2 * dx)
        ay = (np.roll(a, -1, axis=0) - np.roll(a, 1, axis=0)) / (2 * dx)
        bx = (np.roll(b, -1, axis=1) - np.roll(b, 1, axis=1)) / (2 * dx)
        by = (np.roll(b, -1, axis=0) - np.roll(b, 1, axis=0)) / (2 * dx)
        return ax * by - ay * bx

    def rhs(vorticity):
        psi = streamfunction(vorticity)
        adv = jacobian(psi, vorticity)
        adv = np.fft.ifft2(np.fft.fft2(adv) * dealias_mask).real
        drag = -args.drag_alpha * vorticity
        return -adv + diffusion(vorticity) + forcing_field + drag + lowk_drag(vorticity)

    def kinetic_energy(vorticity):
        psi = streamfunction(vorticity)
        u, v = velocity(psi)
        return 0.5 * np.mean(u * u + v * v)

    def energy_spectrum(vorticity):
        w_hat = np.fft.fft2(vorticity) / (args.N * args.N)
        energy_density = np.zeros_like(k2, dtype=float)
        nonzero = k2 > 0
        energy_density[nonzero] = 0.5 * (np.abs(w_hat[nonzero]) ** 2) / k2[nonzero]

        k_mag = np.sqrt(k2).flatten()
        e_flat = energy_density.flatten()

        bins = np.arange(1, args.N // 2)
        spectrum = np.zeros_like(bins, dtype=float)

        for i, kb in enumerate(bins):
            shell = (k_mag >= kb - 0.5) & (k_mag < kb + 0.5)
            spectrum[i] = np.sum(e_flat[shell])

        return bins, spectrum

    print(
        "Running simulation: "
        f"N={args.N}, dt={args.dt}, nu={args.nu}, steps={args.steps}, "
        f"forcing_amplitude={args.forcing_amplitude}, forcing_mode={args.forcing_mode}"
    )
    print(f"output_dir={output_dir}")

    for n in range(args.steps):
        k1 = rhs(w)
        w1 = w + args.dt * k1
        k2_rhs = rhs(w1)
        w_new = w + 0.5 * args.dt * (k1 + k2_rhs)

        W = np.fft.fft2(w_new)
        W *= dealias_mask
        w = np.fft.ifft2(W).real

        if np.isnan(w).any() or np.isinf(w).any():
            print(f"Blow-up detected at step {n}")
            break

        if n % args.save_every == 0:
            energy = kinetic_energy(w)
            k_bins, spectrum = energy_spectrum(w)

            np.save(os.path.join(output_dir, f"spectrum_k_{n:05d}.npy"), spectrum)
            np.save(os.path.join(output_dir, "spectrum_bins.npy"), k_bins)

            k4_value = spectrum[k_bins == 4][0] if np.any(k_bins == 4) else np.nan
            print(f"step={n}, E={energy:.6e}, E(k=4)={k4_value:.3e}")

    print("Simulation complete.")
    return output_dir


if __name__ == "__main__":
    run_simulation(build_parser().parse_args())
