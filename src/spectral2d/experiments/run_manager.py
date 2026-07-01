import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def get_git_status():
    return subprocess.call(['git', 'diff-index', '--quiet', 'HEAD']) != 0

class RunManager:
    def __init__(self, base_path: str = "experiments/runs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_run_folder(self) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_path = self.base_path / f"run_{timestamp}"
        run_path.mkdir(parents=True, exist_ok=True)
        return run_path

    def save_metadata(self, run_path: Path, config: dict, status: str = "running"):
        metadata = {
            "run_id": run_path.name,
            "project": "Raj-Sanghera-Project",
            "git_commit": get_git_revision_hash(),
            "git_dirty": get_git_status(),
            "config": config,
            "status": status,
            "started_at": datetime.now().isoformat()
        }
        with open(run_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
        return metadata

# Example Usage:
# manager = RunManager()
# run_path = manager.create_run_folder()
# manager.save_metadata(run_path, {"Re": 100})