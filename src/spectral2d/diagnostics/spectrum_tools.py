import numpy as np

def compute_kinetic_energy_spectrum_from_vorticity(w, kx, ky):
    w = np.asarray(w)
    kx = np.asarray(kx)
    ky = np.asarray(ky)

    if kx.shape != w.shape or ky.shape != w.shape:
        raise ValueError(f"Shape mismatch: w={w.shape}, kx={kx.shape}, ky={ky.shape}")

    nx, ny = w.shape
    n_tot = nx * ny

    w_hat = np.fft.fft2(w)

    k_sq = kx**2 + ky**2
    nonzero = k_sq > 0

    w_hat_power_normalized = np.abs(w_hat)**2 / (n_tot**2)

    energy_mode = np.zeros_like(w_hat_power_normalized, dtype=float)
    energy_mode[nonzero] = 0.5 * w_hat_power_normalized[nonzero] / k_sq[nonzero]

    k_mag = np.sqrt(k_sq)
    k_shell = np.rint(k_mag).astype(int)

    k_max = int(k_shell.max())
    k_bins = np.arange(1, k_max + 1)

    e_shells = np.zeros(len(k_bins), dtype=float)
    mode_counts = np.zeros(len(k_bins), dtype=int)

    for i, k_val in enumerate(k_bins):
        mask = k_shell == k_val
        e_shells[i] = np.sum(energy_mode[mask])
        mode_counts[i] = int(np.sum(mask))

    return k_bins, e_shells, mode_counts
