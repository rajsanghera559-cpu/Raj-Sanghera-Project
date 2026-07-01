import traceback

import numpy as np

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver


def apply_deterministic_multimode_perturbation(solver, amplitude):
    """
    Add a tiny deterministic multi-mode vorticity perturbation.

    Forcing remains unchanged.
    This only changes the initial condition.
    """
    X = solver.X
    Y = solver.Y

    perturbation = (
        np.sin(3 * X) * np.sin(5 * Y)
        + 0.5 * np.sin(5 * X + 2 * Y)
        + 0.25 * np.cos(7 * X - 3 * Y)
    )

    perturbation = perturbation - np.mean(perturbation)
    solver.w = amplitude * perturbation


def run_perturbed_ic_tests():
    manager = RunManager(base_path="experiments/runs")

    re_value = 1000
    nx = 128
    ny = 128
    dt = 0.005
    steps = 10000

    perturbation_amplitudes = [1e-6, 1e-4]

    for amplitude in perturbation_amplitudes:
        run_path = manager.create_run_folder()

        config = {
            "mode": "phase6C_perturbed_ic",
            "Re": re_value,
            "nx": nx,
            "ny": ny,
            "dt": dt,
            "steps": steps,
            "perturbation_amplitude": amplitude,
            "initial_condition": "deterministic_multimode_vorticity",
            "forcing": "unchanged_single_low_k_forcing",
            "purpose": "test_whether_multimode_initial_condition_breaks_k3_single_shell_lock",
        }

        metadata = manager.save_metadata(run_path, config, status="running")

        print("\n======================================")
        print("Starting Phase 6C perturbed-IC test")
        print(f"Re: {re_value}")
        print(f"Grid: {nx} x {ny}")
        print(f"dt: {dt}")
        print(f"steps: {steps}")
        print(f"perturbation amplitude: {amplitude}")
        print(f"Logging to: {run_path}")
        print("======================================")

        status = "running"

        try:
            solver = SpectralSolver(
                nx=nx,
                ny=ny,
                Re=re_value,
                run_path=run_path,
                dt=dt,
                steps=steps,
            )

            apply_deterministic_multimode_perturbation(solver, amplitude)
            solver.run()

            status = "completed"

        except BaseException:
            status = "failed"
            print("Run failed or interrupted. Check error.log.")

            with open(run_path / "error.log", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())

            raise

        finally:
            manager.save_metadata(run_path, metadata, status=status)
            print(f"Status saved as: {status}")


if __name__ == "__main__":
    run_perturbed_ic_tests()