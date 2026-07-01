import json
import subprocess
from datetime import datetime
from pathlib import Path


def get_git_revision_hash():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()


def get_git_status():
    return subprocess.call(["git", "diff-index", "--quiet", "HEAD", "--"]) != 0


class RunManager:
    def __init__(self, base_path: str = "experiments/runs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_run_folder(self) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_path = self.base_path / f"run_{timestamp}"
        run_path.mkdir(parents=True, exist_ok=True)
        return run_path

    def save_metadata(self, run_path: Path, config=None, status=None):
        """
        Save flat run metadata.

        Accepts either:
        1. A plain config dict, e.g. {"mode": "pilot_sweep", "Re": 100}
        2. An existing metadata dict returned from this method

        This prevents nested metadata inside metadata["config"].
        """
        now = datetime.now().isoformat()

        is_existing_metadata = (
            isinstance(config, dict)
            and "run_id" in config
            and "project" in config
            and "config" in config
            and "status" in config
        )

        if is_existing_metadata:
            metadata = dict(config)
            metadata["git_commit"] = get_git_revision_hash()
            metadata["git_dirty"] = get_git_status()
            metadata["status"] = status if status is not None else metadata.get("status", "running")
            metadata["updated_at"] = now
            metadata.setdefault("started_at", now)
        else:
            metadata = {
                "run_id": run_path.name,
                "project": "Raj-Sanghera-Project",
                "git_commit": get_git_revision_hash(),
                "git_dirty": get_git_status(),
                "config": config or {},
                "status": status if status is not None else "running",
                "started_at": now,
            }

        with open(run_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        return metadata
