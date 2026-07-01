import traceback

from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver


def run_spreading_test():
    manager = RunManager(base_path="experiments/runs")

    re_value = 1000
    nx = 128
    ny = 128
    dt = 0.005
    step_values = [1000, 2500, 5000, 10000]

    for steps in step_values:
        run_path = manager.create_run_folder()

        config = {
            "mode": "phase6B_spreading_test",
            "Re": re_value,
            "nx": nx,
            "ny": ny,
            "dt": dt,
            "steps": steps,
            "purpose": "test_energy_spreading_beyond_forced_k3_shell",
        }

        metadata = manager.save_metadata(run_path, config, status="running")

        print("\n======================================")
        print("Starting Phase 6B spectral spreading test")
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
    run_spreading_test()