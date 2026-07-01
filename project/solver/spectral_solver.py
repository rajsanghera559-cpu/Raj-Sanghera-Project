import numpy as np
import pandas as pd
from pathlib import Path

from src.spectral2d.diagnostics.spectrum_tools import (
    compute_kinetic_energy_spectrum_from_vorticity,
)


class SpectralSolver:
    def __init__(self, nx, ny, Re, run_path, dt=0.005, steps=20000):
        if nx != ny:
            raise ValueError("This solver currently expects a square grid: nx == ny")

        self.N = nx
        self.dt = dt
        self.nu = 1.0 / Re
        self.steps = steps
        self.L = 2 * np.pi
        self.dx = self.L / self.N
        self.run_path = Path(run_path)
        self.run_path.mkdir(parents=True, exist_ok=True)

        self.x = np.linspace(0, self.L, self.N, endpoint=False)
        self.X, self.Y = np.meshgrid(self.x, self.x)

        self.k = np.fft.fftfreq(self.N, d=self.dx) * 2 * np.pi
        self.kx, self.ky = np.meshgrid(self.k, self.k)

        self.k2 = self.kx**2 + self.ky**2
        self.k2[0, 0] = 1.0

        kmax = np.max(np.abs(self.k))
        self.deal = (np.abs(self.kx) < (2 / 3) * kmax) & (np.abs(self.ky) < (2 / 3) * kmax)

        self.w = np.zeros((self.N, self.N))
        self.diagnostics_history = []

    def streamfunction(self, w):
        """Solve Poisson equation for streamfunction from vorticity."""
        return np.fft.ifft2(-np.fft.fft2(w) / self.k2).real

    def velocity(self, psi):
        """Compute velocity from streamfunction."""
        psihat = np.fft.fft2(psi)
        u = np.fft.ifft2(1j * self.ky * psihat).real
        v = np.fft.ifft2(-1j * self.kx * psihat).real
        return u, v

    def laplacian_spectral(self, w):
        """Spectral diffusion operator."""
        return np.fft.ifft2(-self.nu * self.k2 * np.fft.fft2(w)).real

    def forcing(self):
        """Low-wavenumber energy injection."""
        return 0.01 * np.sin(2 * self.X) * np.cos(2 * self.Y)

    def energy(self, u, v):
        return 0.5 * np.mean(u * u + v * v)

    def energy_spectrum(self, w):
        """
        Compute normalized kinetic energy spectrum from vorticity.

        Sum over E(k) should be comparable to total kinetic energy.
        """
        return compute_kinetic_energy_spectrum_from_vorticity(w, self.kx, self.ky)

    def run(self):
        print(f"Starting solver loop for Re={1.0 / self.nu:.1f} at {self.run_path.name}")

        for n in range(self.steps):
            psi = self.streamfunction(self.w)
            u, v = self.velocity(psi)

            wx = (np.roll(self.w, -1, 1) - np.roll(self.w, 1, 1)) / (2 * self.dx)
            wy = (np.roll(self.w, -1, 0) - np.roll(self.w, 1, 0)) / (2 * self.dx)

            adv = u * wx + v * wy
            k1 = -adv + self.laplacian_spectral(self.w) + self.forcing()
            w1 = self.w + self.dt * k1

            psi = self.streamfunction(w1)
            u, v = self.velocity(psi)

            wx = (np.roll(w1, -1, 1) - np.roll(w1, 1, 1)) / (2 * self.dx)
            wy = (np.roll(w1, -1, 0) - np.roll(w1, 1, 0)) / (2 * self.dx)

            adv = u * wx + v * wy
            k2 = -adv + self.laplacian_spectral(w1) + self.forcing()

            w_new = self.w + 0.5 * self.dt * (k1 + k2)

            W = np.fft.fft2(w_new)
            W *= self.deal
            self.w = np.fft.ifft2(W).real

            Z = 0.5 * np.mean(self.w * self.w)

            if n % 500 == 0:
                psi = self.streamfunction(self.w)
                u, v = self.velocity(psi)

                E = self.energy(u, v)
                k_bins, Ek, mode_counts = self.energy_spectrum(self.w)

                idx_k4 = np.where(k_bins == 4)[0]
                Ek4 = float(Ek[idx_k4[0]]) if len(idx_k4) else np.nan

                print(f"step={n}, E={E:.6e}, Z={Z:.6e}, E(k=4)={Ek4:.3e}")

                self.diagnostics_history.append(
                    {
                        "step": n,
                        "energy": E,
                        "enstrophy": Z,
                        "E_k4": Ek4,
                    }
                )

                diag_df = pd.DataFrame(self.diagnostics_history)
                diag_df.to_csv(self.run_path / "diagnostics.csv", index=False)

                spec_df = pd.DataFrame(
                    {
                        "k": k_bins,
                        "E(k)": Ek,
                        "mode_count": mode_counts,
                    }
                )
                spec_df.to_csv(self.run_path / "spectrum.csv", index=False)
