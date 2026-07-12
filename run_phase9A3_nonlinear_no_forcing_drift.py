import traceback
from types import MethodType

import numpy as np
import pandas as pd

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver


def rms(field):
    return float(np.sqrt(np.mean(np.asarray(field) ** 2)))


def rescale_to_rms(field, target_rms):
    field_rms = rms(field)
    if field_rms == 0:
        raise ValueError("Cannot rescale a zero-RMS field.")
    return field * (target_rms / field_rms)


def build_phase6d_like_initial_condition(solver, target_rms):
    X = solver.X
    Y = solver.Y

    raw = (
        np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(Y)
        + 0.50 * np.sin(X) * np.cos(4 * Y)
        + 0.35 * np.cos(4 * X - 2 * Y)
    )

    return rescale_to_rms(raw, target_rms)


def compute_invariants(solver, w):
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)

    energy = solver.energy(u, v)
    enstrophy = 0.5 * np.mean(w * w)
    k_bins, ek, mode_counts = solver.energy_spectrum(w)
    sum_spectrum = float(np.sum(ek))

    peak_index = int(np.argmax(ek))
    peak_k = int(k_bins[peak_index])
    peak_fraction = float(ek[peak_index] / sum_spectrum) if sum_spectrum > 0 else np.nan

    return {
        "energy": float(energy),
        "enstrophy": float(enstrophy),
        "sum_spectrum": sum_spectrum,
        "peak_k": peak_k,
        "peak_fraction": peak_fraction,
    }


def run_phase9a3_nonlinear_no_forcing_drift():
    manager = RunManager(base_path="experiments/runs")

    re_value = 1_000_000
    nx = 64
    ny = 64
    dt = 0.001
    steps = 1001

    target_rms = 0.01
    nu = 1.0 / re_value
    comparison_intervals = 1000
    comparison_time = comparison_intervals * dt

    run_path = manager.create_run_folder()

    config = {
        "mode": "phase9A3_nonlinear_no_forcing_drift",
        "Re": re_value,
        "nu": nu,
        "nx": nx,
        "ny": ny,
        "dt": dt,
        "steps": steps,
        "forcing": "zero_forcing_override",
        "initial_condition": "phase6d_like_multimode_vorticity",
        "target_initial_rms": target_rms,
        "comparison_intervals": comparison_intervals,
        "comparison_time": comparison_time,
        "expected_diagnostic_steps": [0, 500, 1000],
        "purpose": "short nonlinear no-forcing drift test for energy and enstrophy behavior",
        "note": "This is a nonlinear validation test, not a turbulence or k^-3 claim.",
    }

    metadata = manager.save_metadata(run_path, config, status="running")

    print("Starting Phase 9A.3 nonlinear no-forcing short-time drift test")
    print(f"Re: {re_value}")
    print(f"nu: {nu}")
    print(f"Grid: {nx} x {ny}")
    print(f"dt: {dt}")
    print(f"steps: {steps}")
    print(f"comparison time: {comparison_time}")
    print(f"initial condition: phase6d-like multimode, RMS={target_rms}")
    print(f"forcing: zero")
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

        solver.w = build_phase6d_like_initial_condition(solver, target_rms)

        initial_invariants = compute_invariants(solver, solver.w)

        initial_df = pd.DataFrame(
            [
                {
                    "step_label": "pre_run_initial",
                    "energy": initial_invariants["energy"],
                    "enstrophy": initial_invariants["enstrophy"],
                    "sum_spectrum": initial_invariants["sum_spectrum"],
                    "peak_k": initial_invariants["peak_k"],
                    "peak_fraction": initial_invariants["peak_fraction"],
                    "field_rms": rms(solver.w),
                }
            ]
        )
        initial_df.to_csv(run_path / "initial_invariants.csv", index=False)

        metadata["config"].update(
            {
                "initial_energy": initial_invariants["energy"],
                "initial_enstrophy": initial_invariants["enstrophy"],
                "initial_sum_spectrum": initial_invariants["sum_spectrum"],
                "initial_peak_k": initial_invariants["peak_k"],
                "initial_peak_fraction": initial_invariants["peak_fraction"],
                "initial_field_rms": rms(solver.w),
            }
        )
        manager.save_metadata(run_path, metadata, status="running")

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

    print("Phase 9A.3 nonlinear no-forcing drift test finished")
    print(f"Status: {status}")
    print(f"Run folder: {run_path}")


if __name__ == "__main__":
    run_phase9a3_nonlinear_no_forcing_drift()