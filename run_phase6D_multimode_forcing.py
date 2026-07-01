import traceback
from types import MethodType

import numpy as np

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver


def build_rms_matched_multimode_forcing(solver):
    """
    Build deterministic low-k multimode forcing.

    The RMS is matched to the original single-mode forcing:
        0.01 * sin(2X) * cos(2Y)

    This changes forcing geometry without simply increasing total forcing scale.
    """
    X = solver.X
    Y = solver.Y

    base = 0.01 * np.sin(2 * X) * np.cos(2 * Y)

    raw = (
        1.00 * np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(1 * Y)
        + 0.50 * np.sin(1 * X) * np.cos(4 * Y)
        + 0.35 * np.cos(4 * X - 2 * Y)
    )

    raw = raw - np.mean(raw)

    base_rms = float(np.sqrt(np.mean(base * base)))
    raw_rms = float(np.sqrt(np.mean(raw * raw)))

    if raw_rms == 0.0:
        raise ValueError("Raw multimode forcing has zero RMS.")

    forcing_field = raw * (base_rms / raw_rms)

    forcing_stats = {
        "forcing_type": "rms_matched_deterministic_low_k_multimode",
        "base_single_mode_rms": base_rms,
        "raw_multimode_rms": raw_rms,
        "matched_multimode_rms": float(np.sqrt(np.mean(forcing_field * forcing_field))),
        "forcing_terms": [
            "sin(2X)cos(2Y)",
            "0.75*sin(3X)cos(Y)",
            "0.50*sin(X)cos(4Y)",
            "0.35*cos(4X-2Y)",
        ],
    }

    return forcing_field, forcing_stats


def run_multimode_forcing_test():
    manager = RunManager(base_path="experiments/runs")

    re_value = 1000
    nx = 128
    ny = 128
    dt = 0.005
    steps = 10000

    run_path = manager.create_run_folder()

    config = {
        "mode": "phase6D_multimode_forcing",
        "Re": re_value,
        "nx": nx,
        "ny": ny,
        "dt": dt,
        "steps": steps,
        "initial_condition": "zero_vorticity",
        "purpose": "test_whether_rms_matched_multimode_forcing_breaks_k3_single_shell_lock",
    }

    metadata = manager.save_metadata(run_path, config, status="running")

    print("\n======================================")
    print("Starting Phase 6D multimode-forcing test")
    print(f"Re: {re_value}")
    print(f"Grid: {nx} x {ny}")
    print(f"dt: {dt}")
    print(f"steps: {steps}")
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

        forcing_field, forcing_stats = build_rms_matched_multimode_forcing(solver)

        metadata["config"].update(forcing_stats)
        manager.save_metadata(run_path, metadata, status="running")

        def forcing_override(self):
            return forcing_field

        solver.forcing = MethodType(forcing_override, solver)

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
    run_multimode_forcing_test()