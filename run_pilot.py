import traceback
from pathlib import Path

# Adjusting imports based on your folder structure
from src.spectral2d.experiments.run_manager import RunManager
from project.solver.spectral_solver import SpectralSolver

def run_sweeps():
    manager = RunManager(base_path="experiments/runs")
    
    # We are running your two pilot values: Re=100 and Re=250
    for Re in [100, 250]:
        run_path = manager.create_run_folder()
        metadata = manager.save_metadata(run_path, {"mode": "pilot_sweep", "Re": Re})
        
        print(f"\n======================================")
        print(f"Starting Pilot Run: Re={Re}")
        print(f"Logging to: {run_path}")
        print(f"======================================")
        
        try:
            # Tiny real test: 1000 steps instead of 20000 so you can see it finish quickly
            solver = SpectralSolver(nx=128, ny=128, Re=Re, run_path=run_path, dt=0.005, steps=1000)
            solver.run()
            status = "completed"
            
        except BaseException as e:
            status = "failed"
            print(f"Run failed or interrupted! Check error.log")
            with open(run_path / "error.log", "w") as f:
                f.write(traceback.format_exc())
            if isinstance(e, KeyboardInterrupt):
                raise
                
        finally:
            metadata["status"] = status
            manager.save_metadata(run_path, metadata)
            print(f"Status saved as: {status}")

if __name__ == "__main__":
    run_sweeps()
