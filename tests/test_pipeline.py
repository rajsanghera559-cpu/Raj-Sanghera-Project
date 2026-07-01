import sys
from pathlib import Path

import numpy as np

# Force the project root into the system path so modules are always found
sys.path.append(str(Path(__file__).resolve().parent.parent))

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

            guard_solver_state(
                step=step,
                omega=omega,
                energy=energy,
                cfl=cfl,
                cfl_limit=1.0,
            )


def test_pipeline_states_use_temp_run_folder(tmp_path):
    """
    Pipeline smoke test.

    Important guardrail:
    pytest must not write fake test runs into experiments/runs/.
    Test runs belong in pytest's temporary directory.
    """
    manager = RunManager(base_path=tmp_path / "runs")

    expected_status = {
        "normal": "completed",
        "nan": "failed",
        "cfl": "failed",
    }

    for mode, expected in expected_status.items():
        run_path = manager.create_run_folder()
        metadata = manager.save_metadata(run_path, {"mode": mode}, status="running")

        try:
            solver = MockSolver()
            solver.run(mode=mode)
            status = "completed"
        except Exception as e:
            status = "failed"
            with open(run_path / "error.log", "w", encoding="utf-8") as f:
                f.write(str(e))

        manager.save_metadata(run_path, metadata, status=status)

        assert status == expected

        saved_metadata = run_path / "metadata.json"
        assert saved_metadata.exists()

        # Guardrail: this test must use pytest temp folders, not the real archive.
        assert "experiments" not in str(run_path)