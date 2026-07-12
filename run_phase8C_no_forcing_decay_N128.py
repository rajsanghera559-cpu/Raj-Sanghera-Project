import traceback
from types import MethodType

import numpy as np

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver


def run_phase8c_no_forcing_decay_n128():
    manager = RunManager(base_path="experiments/runs")

    re_value = 1000
    nx = 128
    ny = 128
    dt = 0.005
    steps = 1001

    mode_kx = 2
    mode_ky = 2
    k_squared = mode_kx**2 + mode_ky**2
    amplitude = 0.01
    nu = 1.0 / re_value

    comparison_intervals = 1000
    comparison_time = comparison_intervals * dt
    expected_logged_ratio = float(np.exp(-2.0 * nu * k_squared * comparison_time))

    run_path = manager.create_run_folder()

    config = {
        "mode": "phase8C_no_forcing_single_mode_decay_N128",
        "Re": re_value,
        "nu": nu,
        "nx": nx,
        "ny": ny,
        "dt": dt,
        "steps": steps,
        "forcing": "zero_forcing_override",
        "initial_condition": "single_fourier_mode",
        "initial_condition_formula": "amplitude * sin(2X) * cos(2Y)",
        "amplitude": amplitude,
        "mode_kx": mode_kx,
        "mode_ky": mode_ky,
        "k_squared": k_squared,
        "comparison_intervals": comparison_intervals,
        "comparison_time": comparison_time,
        "expected_diagnostic_steps": [0, 500, 1000],
        "expected_logged_energy_ratio_step1000_over_step0": expected_logged_ratio,
        "phase8A_reference": "experiments/runs/run_2026-07-03_23-57-36",
        "purpose": "resolution sensitivity check for no-forcing viscous decay benchmark using N=128",
    }

    metadata = manager.save_metadata(run_path, config, status="running")

    print("Starting Phase 8C no-forcing decay resolution sensitivity benchmark")
    print(f"Re: {re_value}")
    print(f"nu: {nu}")
    print(f"Grid: {nx} x {ny}")
    print(f"dt: {dt}")
    print(f"steps: {steps}")
    print(f"Initial mode: sin({mode_kx}X) * cos({mode_ky}Y)")
    print(f"k_squared: {k_squared}")
    print(f"Comparison time: {comparison_time}")
    print(f"Expected logged energy ratio step1000/step0: {expected_logged_ratio:.12e}")
    print(f"Logging to: {run_path}")

    status = "failed"

    try:
        solver = SpectralSolver(
            nx=nx,
            ny=ny,
            Re=re_value,
            run_path=run_path,
            dt=dt,
            steps=steps,
        )

        solver.w = amplitude * np.sin(mode_kx * solver.X) * np.cos(mode_ky * solver.Y)

        def zero_forcing(self):
            return np.zeros_like(self.w)

        solver.forcing = MethodType(zero_forcing, solver)

        solver.run()
        status = "completed"

    except Exception:
        status = "failed"
        with open(run_path / "error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise

    finally:
        manager.save_metadata(run_path, metadata, status=status)

    print("Phase 8C no-forcing decay resolution sensitivity benchmark finished")
    print(f"Status: {status}")
    print(f"Run folder: {run_path}")


if __name__ == "__main__":
    run_phase8c_no_forcing_decay_n128()