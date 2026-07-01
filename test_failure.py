import traceback
from pathlib import Path
from src.spectral2d.experiments.run_manager import RunManager

def test_failure_handling():
    manager = RunManager(base_path="experiments/runs")
    run_path = manager.create_run_folder()
    metadata = manager.save_metadata(run_path, {"test": "forced_failure"}, status="running")
    
    print(f"Forcing a failure in: {run_path}")
    
    try:
        # Simulate a crash mid-run
        raise RuntimeError("CRITICAL_FAILURE: Forced test exception")
        
    except BaseException as e:
        print("Caught exception! Logging to error.log and updating metadata.")
        with open(run_path / "error.log", "w") as f:
            f.write(traceback.format_exc())
        
        metadata["status"] = "failed"
        metadata["error_type"] = type(e).__name__
        metadata["error_message"] = str(e)
        manager.save_metadata(run_path, metadata, status="failed")

if __name__ == "__main__":
    test_failure_handling()