import traceback

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver


def run_phase7b_smoke():
    manager = RunManager(base_path="experiments/runs")

    re_value = 1000
    nx = 64
    ny = 64
    dt = 0.005

    # Use 1001 steps so the existing solver cadence logs step 0, 500, and 1000.
    steps = 1001

    run_path = manager.create_run_folder()

    config = {
        "mode": "phase7B_reproducibility_smoke",
        "Re": re_value,
        "nx": nx,
        "ny": ny,
        "dt": dt,
        "steps": steps,
        "forcing": "default_solver_forcing",
        "purpose": "short fresh run to verify current code can generate finite diagnostics and spectrum",
        "expected_diagnostic_steps": [0, 500, 1000],
    }

    metadata = manager.save_metadata(run_path, config, status="running")

    print("Starting Phase 7B reproducibility smoke run")
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

        solver.run()
        status = "completed"

    except Exception:
        status = "failed"
        with open(run_path / "error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise

    finally:
        manager.save_metadata(run_path, metadata, status=status)

    print("Phase 7B smoke run finished")
    print(f"Status: {status}")
    print(f"Run folder: {run_path}")


if __name__ == "__main__":
    run_phase7b_smoke()