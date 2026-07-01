import numpy as np
from pathlib import Path
from project.solver.spectral_solver import SpectralSolver
from src.spectral2d.diagnostics.spectrum_tools import compute_kinetic_energy_spectrum_from_vorticity

def run_math_audit():
    print("--- STARTING MATHEMATICAL AUDIT ---")
    solver = SpectralSolver(nx=128, ny=128, Re=1000, run_path=Path('.'))
    
    # Create X and Y grids manually since they aren't explicit attributes
    x = np.linspace(0, 2*np.pi, 128, endpoint=False)
    y = np.linspace(0, 2*np.pi, 128, endpoint=False)
    X, Y = np.meshgrid(x, y, indexing='ij')
    
    k_x_target, k_y_target = 3.0, 4.0
    solver.w = 2.0 * np.sin(k_x_target * X + k_y_target * Y)
    
    psihat = np.fft.fft2(solver.w) / solver.k2
    u = np.fft.ifft2(1j * solver.ky * psihat).real
    v = np.fft.ifft2(-1j * solver.kx * psihat).real
    
    diagnostic_E = solver.energy(u, v)
    
    k_bins, E_shells, mode_counts = compute_kinetic_energy_spectrum_from_vorticity(
        solver.w, solver.kx, solver.ky
    )
    spectral_sum = np.sum(E_shells)
    
    print("\n--- RESULTS ---")
    print(f"Target Value:      4.000000e-02")
    print(f"Diagnostic Energy: {diagnostic_E:e}")
    print(f"Spectral Sum:      {spectral_sum:e}")
    print(f"Absolute Diff:     {abs(diagnostic_E - spectral_sum):e}")

if __name__ == "__main__":
    run_math_audit()

