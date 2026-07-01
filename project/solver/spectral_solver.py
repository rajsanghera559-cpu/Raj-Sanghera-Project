import numpy as np
import pandas as pd
from pathlib import Path

class SpectralSolver:
    def __init__(self, nx, ny, Re, run_path, dt=0.005, steps=20000):
        # ============================================================
        # PARAMETERS
        # ============================================================
        self.N = nx
        self.dt = dt
        self.nu = 1.0 / Re  # Replaces fixed nu to allow Reynolds sweeps
        self.steps = steps
        self.L = 2 * np.pi
        self.dx = self.L / self.N
        self.run_path = Path(run_path)

        # ============================================================
        # GRID + WAVENUMBERS
        # ============================================================
        self.x = np.linspace(0, self.L, self.N, endpoint=False)
        self.X, self.Y = np.meshgrid(self.x, self.x)

        self.k = np.fft.fftfreq(self.N, d=self.dx) * 2 * np.pi
        self.kx, self.ky = np.meshgrid(self.k, self.k)
        self.k2 = self.kx**2 + self.ky**2
        self.k2[0, 0] = 1.0

        # ============================================================
        # 2/3 DEALIASING MASK (Tier 3)
        # ============================================================
        kmax = np.max(np.abs(self.k))
        self.deal = (np.abs(self.kx) < (2/3) * kmax) & (np.abs(self.ky) < (2/3) * kmax)

        # ============================================================
        # INITIAL CONDITION
        # ============================================================
        self.w = np.zeros((self.N, self.N))
        
        # Array to store diagnostics history for CSV saving
        self.diagnostics_history = []

    # ============================================================
    # OPERATORS
    # ============================================================
    def streamfunction(self, w):
        """FFT Poisson solve: ψ = -∇⁻² ω"""
        return np.fft.ifft2(-np.fft.fft2(w) / self.k2).real

    def velocity(self, psi):
        """u = ∂y ψ, v = -∂x ψ"""
        psihat = np.fft.fft2(psi)
        u = np.fft.ifft2(1j * self.ky * psihat).real
        v = np.fft.ifft2(-1j * self.kx * psihat).real
        return u, v

    def laplacian_spectral(self, w):
        """Spectral diffusion operator (Tier 2 consistency fix)"""
        return np.fft.ifft2(-self.nu * self.k2 * np.fft.fft2(w)).real

    def jacobian(self, a, b):
        """Physical-space nonlinear term"""
        ax = (np.roll(a, -1, 1) - np.roll(a, 1, 1)) / (2 * self.dx)
        ay = (np.roll(a, -1, 0) - np.roll(a, 1, 0)) / (2 * self.dx)
        bx = (np.roll(b, -1, 1) - np.roll(b, 1, 1)) / (2 * self.dx)
        by = (np.roll(b, -1, 0) - np.roll(b, 1, 0)) / (2 * self.dx)
        return ax * by - ay * bx

    # ============================================================
    # TIER 1: FORCING (steady turbulence driver)
    # ============================================================
    def forcing(self):
        """Low-wavenumber energy injection"""
        return 0.01 * np.sin(2 * self.X) * np.cos(2 * self.Y)

    # ============================================================
    # TIER 2: ENERGY DIAGNOSTIC
    # ============================================================
    def energy(self, u, v):
        return 0.5 * np.mean(u*u + v*v)

    # ============================================================
    # TIER 2: ENERGY SPECTRUM (basic radial binning)
    # ============================================================
    def energy_spectrum(self, w):
        w_hat = np.fft.fft2(w)
        E = np.abs(w_hat)**2

        k_mag = np.sqrt(self.kx**2 + self.ky**2).flatten()
        E_flat = E.flatten()

        bins = np.arange(1, self.N//2)
        Ek = np.zeros_like(bins, dtype=float)

        for i, kb in enumerate(bins):
            mask = (k_mag >= kb - 0.5) & (k_mag < kb + 0.5)
            Ek[i] = np.sum(E_flat[mask])

        return bins, Ek

    # ============================================================
    # TIER 1–2–3 CORE TIME INTEGRATION (RK2 + forcing + dealiasing)
    # ============================================================
    def run(self):
        print(f"Starting solver loop for Re={1.0/self.nu:.1f} at {self.run_path.name}")
        
        for n in range(self.steps):
            # ----------------------------
            # RK2 STAGE 1
            # ----------------------------
            psi = self.streamfunction(self.w)
            u, v = self.velocity(psi)

            wx = (np.roll(self.w, -1, 1) - np.roll(self.w, 1, 1)) / (2 * self.dx)
            wy = (np.roll(self.w, -1, 0) - np.roll(self.w, 1, 0)) / (2 * self.dx)

            adv = u * wx + v * wy

            k1 = -adv + self.laplacian_spectral(self.w) + self.forcing()
            w1 = self.w + self.dt * k1

            # ----------------------------
            # RK2 STAGE 2
            # ----------------------------
            psi = self.streamfunction(w1)
            u, v = self.velocity(psi)

            wx = (np.roll(w1, -1, 1) - np.roll(w1, 1, 1)) / (2 * self.dx)
            wy = (np.roll(w1, -1, 0) - np.roll(w1, 1, 0)) / (2 * self.dx)

            adv = u * wx + v * wy

            k2 = -adv + self.laplacian_spectral(w1) + self.forcing()

            # update
            w_new = self.w + 0.5 * self.dt * (k1 + k2)

            # ----------------------------
            # TIER 3: DEALIASING
            # ----------------------------
            W = np.fft.fft2(w_new)
            W *= self.deal
            self.w = np.fft.ifft2(W).real
            
            #============================================================
            # ENSTROPHY + DIAGNOSTICS (CLEAN CONTROL BLOCK)
            #============================================================
            # ----------------------------
            # ENSTROPHY (computed every step)
            # ----------------------------
            Z = 0.5 * np.mean(self.w * self.w)

            # ----------------------------
            # DIAGNOSTICS (computed every 500 steps)
            # ----------------------------
            if n % 500 == 0:
                psi = self.streamfunction(self.w)
                u, v = self.velocity(psi)

                E = self.energy(u, v)
                k_bins, Ek = self.energy_spectrum(self.w)

                # safety check for spectrum length
                if len(Ek) > 4:
                    Ek4 = Ek[4]
                else:
                    Ek4 = np.nan

                print(f"step={n}, E={E:.6e}, Z={Z:.6e}, E(k=4)={Ek4:.3e}")
                
                # Update history and save to CSVs in the run_path
                self.diagnostics_history.append({
                    "step": n,
                    "energy": E,
                    "enstrophy": Z,
                    "E_k4": Ek4
                })
                
                diag_df = pd.DataFrame(self.diagnostics_history)
                diag_df.to_csv(self.run_path / "diagnostics.csv", index=False)
                
                spec_df = pd.DataFrame({"k": k_bins, "E(k)": Ek})
                spec_df.to_csv(self.run_path / "spectrum.csv", index=False)
