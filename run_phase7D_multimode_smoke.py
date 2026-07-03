import traceback
from types import MethodType

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver
from run_phase6D_multimode_forcing import build_rms_matched_multimode_forcing


def run_phase7d_multimode_smoke():
    manager = RunManager(base_path="experiments/runs")

    re_value = 1000
    nx = 64
    ny = 64
    dt = 0.005

    # Use 1001 steps so the existing solver cadence logs step 0, 500, and 1000.
    steps = 1001

    run_path = manager.create_run_folder()

    config = {
        "mode": "phase7D_multimode_smoke",
        "Re": re_value,
        "nx": nx,
        "ny": ny,
        "dt": dt,
        "steps": steps,
        "forcing": "phase6D_rms_matched_deterministic_low_k_multimode",
        "source_forcing_builder": "run_phase6D_multimode_forcing.build_rms_matched_multimode_forcing",
        "purpose": "short fresh run to test whether Phase 6D multimode forcing still broadens the spectrum",
        "expected_diagnostic_steps": [0, 500, 1000],
    }

    metadata = manager.save_metadata(run_path, config, status="running")

    print("Starting Phase 7D controlled multimode smoke run")
    print(f"Re: {re_value}")
    print(f"Grid: {nx} x {ny}")
    print(f"dt: {dt}")
    print(f"steps: {steps}")
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

        forcing_field, forcing_stats = build_rms_matched_multimode_forcing(solver)

        metadata["config"].update(forcing_stats)
        manager.save_metadata(run_path, metadata, status="running")

        def forcing_override(self):
            return forcing_field

        solver.forcing = MethodType(forcing_override, solver)

        solver.run()
        status = "completed"

    except Exception:
        status = "failed"
        with open(run_path / "error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise

    finally:
        manager.save_metadata(run_path, metadata, status=status)

    print("Phase 7D multimode smoke run finished")
    print(f"Status: {status}")
    print(f"Run folder: {run_path}")


if __name__ == "__main__":
    run_phase7d_multimode_smoke()