import traceback

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver


def run_ladder():
    manager = RunManager(base_path="experiments/runs")

    reynolds_values = [100, 250, 500, 1000]

    nx = 128
    ny = 128
    dt = 0.005
    steps = 1000

    for Re in reynolds_values:
        run_path = manager.create_run_folder()

        config = {
            "mode": "phase6A_re_ladder",
            "Re": Re,
            "nx": nx,
            "ny": ny,
            "dt": dt,
            "steps": steps,
        }

        metadata = manager.save_metadata(run_path, config, status="running")

        print("\n======================================")
        print(f"Starting Phase 6A ladder run: Re={Re}")
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
                Re=Re,
                run_path=run_path,
                dt=dt,
                steps=steps,
            )
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
    run_ladder()