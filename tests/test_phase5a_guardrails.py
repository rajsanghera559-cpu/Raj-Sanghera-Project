import json
import sys
from pathlib import Path

import numpy as np

# Force project root into path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from project.solver.spectral_solver import SpectralSolver
from src.spectral2d.experiments.run_manager import RunManager


def test_metadata_update_does_not_nest_metadata(tmp_path):
    manager = RunManager(base_path=tmp_path / "runs")
    run_path = manager.create_run_folder()

    metadata = manager.save_metadata(
        run_path,
        {"mode": "pilot_sweep", "Re": 100},
        status="running",
    )

    manager.save_metadata(run_path, metadata, status="completed")

    saved = json.loads((run_path / "metadata.json").read_text(encoding="utf-8"))

    assert saved["status"] == "completed"
    assert saved["config"]["mode"] == "pilot_sweep"
    assert saved["config"]["Re"] == 100

    # Guardrail: metadata must not be nested inside config.
    assert "run_id" not in saved["config"]
    assert "project" not in saved["config"]
    assert "git_commit" not in saved["config"]
    assert "status" not in saved["config"]


def test_solver_spectrum_sum_matches_diagnostic_energy(tmp_path):
    run_path = tmp_path / "pilot_run"

    solver = SpectralSolver(
        nx=32,
        ny=32,
        Re=100,
        run_path=run_path,
        steps=501,
    )
    solver.run()

    diagnostics_path = run_path / "diagnostics.csv"
    spectrum_path = run_path / "spectrum.csv"

    assert diagnostics_path.exists()
    assert spectrum_path.exists()

    diagnostics = np.genfromtxt(
        diagnostics_path,
        delimiter=",",
        names=True,
        dtype=None,
        encoding="utf-8",
    )

    spectrum = np.genfromtxt(
        spectrum_path,
        delimiter=",",
        names=True,
        dtype=None,
        encoding="utf-8",
    )

    final_energy = float(diagnostics["energy"][-1])
    spectrum_sum = float(np.sum(spectrum["Ek"]))

    assert np.isfinite(final_energy)
    assert np.isfinite(spectrum_sum)

    # Guardrail: saved E(k) must be normalized kinetic energy,
    # not raw FFT power.
    assert np.isclose(spectrum_sum, final_energy, rtol=1e-10, atol=1e-18)