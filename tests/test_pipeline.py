import sys
from pathlib import Path
# Force the project root into the system path so modules are always found
sys.path.append(str(Path(__file__).resolve().parent.parent))

import json
import numpy as np
from src.spectral2d.diagnostics.safety import guard_solver_state
from src.spectral2d.experiments.run_manager import RunManager

class MockSolver:
    def run(self, mode="normal"):
        """Simulates solver steps with different failure modes."""
        for step in range(5):
            omega = np.random.rand(10, 10)
            energy = 1.0
            cfl = 0.5
            
            if mode == "nan":
                omega = np.array([np.nan])
            elif mode == "cfl":
                cfl = 2.0
                
            guard_solver_state(step=step, omega=omega, energy=energy, cfl=cfl, cfl_limit=1.0)

def test_pipeline_states():
    manager = RunManager(base_path="experiments/runs")
    
    modes = ["normal", "nan", "cfl"]
    
    for mode in modes:
        run_path = manager.create_run_folder()
        metadata = manager.save_metadata(run_path, {"mode": mode})
        
        try:
            solver = MockSolver()
            solver.run(mode=mode)
            status = "completed"
        except Exception as e:
            status = "failed"
            with open(run_path / "error.log", "w") as f:
                f.write(str(e))
        
        # Update metadata
        metadata["status"] = status
        with open(run_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
            
        print(f"Mode: {mode} | Status: {status}")

if __name__ == "__main__":
    test_pipeline_states()
