
"""
Controlled Stage B exact operator-ledger replay.

Usage:
    python -B run_stage_b_exact_operator_ledger_replay.py inspect
    python -B run_stage_b_exact_operator_ledger_replay.py run

The inspection path parses and verifies this file and all frozen source
identities without importing project modules, constructing a solver, writing
files, or executing numerical timesteps.

The run path externally mirrors the protected solver's RK2-plus-mask update,
records an exact per-step enstrophy ledger, and compares the replay against the
archived longer-run evidence. It never calls the protected solver run loop and
does not modify protected or archived source files.

This is implemented-ledger attribution only. It does not establish formal
convergence, physical validation, turbulence, a cascade, an inertial range,
a k^-3 law, method superiority, production readiness, or unique physical
causation.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np


# ============================================================================
# Frozen identities
# ============================================================================

RUNNER_NAME = "run_stage_b_exact_operator_ledger_replay.py"

AUTHORIZED_RUNNER_DESIGN_COMMIT = (
    "2109b2d6046302085b47cb2219e61231432b1b03"
)

EXACT_LEDGER_DESIGN_PATH = Path(
    "STAGE_B_EXACT_OPERATOR_LEDGER_DESIGN_REVIEW.md"
)

EXPECTED_EXACT_LEDGER_DESIGN_SHA256 = (
    "584A94C8A857D4869A95CC01BE31108CDFBC201C0BF56C03A0A8F9860D083B4C"
)

RUNNER_DESIGN_PATH = Path(
    "STAGE_B_STANDALONE_REPLAY_RUNNER_DESIGN.md"
)

EXPECTED_RUNNER_DESIGN_SHA256 = (
    "A0E039CAFF9A71BBB8CA33C9043169C24CDC0E1B1F330F829752BE11F45C4710"
)

EXPECTED_SOLVER_SHA256 = (
    "1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1"
)

EXPECTED_BUDGET_SHA256 = (
    "A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B"
)

ARCHIVED_SOURCE_DIRECTORY = (
    Path("experiments")
    / "forcing_budget_stationarity"
    / "forcing_budget_stationarity_20260719T083403Z_9a9f2e0"
)

ARCHIVED_SOURCE_HASHES = {
    "run_metadata.json":
        "57640568F657C26E47F495B1BE7C4C23F54EF0ACB882250ECB596A426F504ED9",
    "forcing_budget.csv":
        "38D01CE7278979EB4D7433414C849F65820C729DC5928A964FFED1EB3E4F482F",
    "forcing_spectra.csv":
        "62235ED6A5C9BD17D4FF21D22A1F830EE637FC22F26ABD43B483359B5873275A",
    "stationarity_window.csv":
        "FD1C5017DC24C6BF9F12F3BB56E44631491BA8178B174968743175976C06ED9A",
    "stationarity_summary.json":
        "3573F19100A4BD817B97C603B3C13D0137AD56D1F52FD05D602DFFC6400DBE1E",
    "file_inventory.csv":
        "3745C4E279E304A1A04CA14CEFE04BAA0FABD1A6072BB2E4C407FAB78CA1A028",
}

EXPECTED_FORCING_SHA256 = (
    "504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB"
)


# ============================================================================
# Frozen numerical configuration
# ============================================================================

N = 64
RE = 1000
NU = 1.0 / RE
DT = 0.005
STEPS = 20001
FINAL_PHYSICAL_TIME = 100.005

LEDGER_OUTPUT_INTERVAL = 1
HIGH_CADENCE_INTERVAL = 10
ARCHIVE_MATCH_INTERVAL = 100
PROGRESS_INTERVAL = 500

EXPECTED_LEDGER_ROWS = 20001
EXPECTED_HIGH_CADENCE_ROWS = 2001
EXPECTED_FINAL_WINDOW_ROWS = 4001
EXPECTED_ARCHIVE_MATCHES = 201
EXPECTED_TIME_BLOCK_ROWS = 6

FINAL_WINDOW_START = 80.005
FINAL_WINDOW_END = 100.005

FORCING_TARGET_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14

RESIDUAL_FLOOR = 1.0e-30

LEDGER_CLOSURE_LIMIT = 1.0e-10
FILTER_BOOKKEEPING_LIMIT = 1.0e-10
MASK_CROSSCHECK_LIMIT = 1.0e-10
VISCOUS_IDENTITY_LIMIT = 1.0e-10
FORCING_IDENTITY_LIMIT = 1.0e-12
STATE_RECONSTRUCTION_LIMIT = 1.0e-13
IMAGINARY_RATIO_LIMIT = 1.0e-13
SIGN_TOLERANCE_FACTOR = 1.0e-14

ARCHIVE_TIME_ABS_TOLERANCE = 1.0e-14
ARCHIVE_FORCING_RMS_ABS_TOLERANCE = 1.0e-14
ARCHIVE_RELATIVE_TOLERANCE = 1.0e-11
ARCHIVE_ABSOLUTE_FLOOR = 1.0e-14

DOMINANCE_SHARE_LIMIT = 0.70
DOMINANCE_REDUCTION_LIMIT = 0.70
DOMINANCE_MIN_N90_STEPS = 5
MULTIPLE_SHARE_LIMIT = 0.20
CANCELLATION_RATIO_LIMIT = 0.20
SIGN_NONZERO_FLOOR = 1.0e-30

CSV_FLUSH_INTERVAL = 250

OUTPUT_ROOT = (
    Path("experiments")
    / "forcing_budget_stage_b_ledger"
)

RUN_PREFIX = "stage_b_exact_operator_ledger_"

FORCING_TERMS = (
    "sin(2X)cos(2Y)",
    "0.75*sin(3X)cos(Y)",
    "0.50*sin(X)cos(4Y)",
    "0.35*cos(4X-2Y)",
)

TIME_BLOCKS = (
    {
        "block_id": 1,
        "label": "0.005 <= t <= 20.005",
        "lower": 0.005,
        "upper": 20.005,
        "lower_inclusive": True,
    },
    {
        "block_id": 2,
        "label": "20.005 < t <= 40.005",
        "lower": 20.005,
        "upper": 40.005,
        "lower_inclusive": False,
    },
    {
        "block_id": 3,
        "label": "40.005 < t <= 60.005",
        "lower": 40.005,
        "upper": 60.005,
        "lower_inclusive": False,
    },
    {
        "block_id": 4,
        "label": "60.005 < t <= 80.005",
        "lower": 60.005,
        "upper": 80.005,
        "lower_inclusive": False,
    },
    {
        "block_id": 5,
        "label": "80.005 < t <= 100.005",
        "lower": 80.005,
        "upper": 100.005,
        "lower_inclusive": False,
    },
    {
        "block_id": 6,
        "label": "full run: 0.005 <= t <= 100.005",
        "lower": 0.005,
        "upper": 100.005,
        "lower_inclusive": True,
    },
)

EXPECTED_BLOCK_COUNTS = {
    1: 4001,
    2: 4000,
    3: 4000,
    4: 4000,
    5: 4000,
    6: 20001,
}

COMPONENTS = (
    "advection",
    "viscous",
    "forcing",
    "rk2",
    "mask",
    "non_forcing_non_viscous",
    "observed",
)

ATTRIBUTION_COMPONENTS = (
    "advection",
    "rk2",
    "mask",
)


# ============================================================================
# Output schemas
# ============================================================================

LEDGER_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "dt",
    "forcing_sha256",
    "z_current",
    "z_stage",
    "z_unfiltered",
    "z_filtered",
    "stage1_advection_work_rate",
    "stage1_viscous_work_rate",
    "stage1_forcing_work_rate",
    "stage1_total_work_rate",
    "stage1_advection_rms",
    "stage1_viscous_rms",
    "stage1_total_rhs_rms",
    "stage2_advection_work_rate",
    "stage2_viscous_work_rate",
    "stage2_forcing_work_rate",
    "stage2_total_work_rate",
    "stage2_advection_rms",
    "stage2_viscous_rms",
    "stage2_total_rhs_rms",
    "rk2_advection_rate",
    "rk2_viscous_rate",
    "rk2_viscous_dissipation_rate",
    "rk2_forcing_rate",
    "rk2_quadratic_remainder_rate",
    "rk2_quadratic_remainder_expanded",
    "rk2_remainder_crosscheck_residual",
    "mask_field_removal_rms",
    "mask_enstrophy_change",
    "mask_enstrophy_change_rate",
    "mask_enstrophy_loss",
    "mask_enstrophy_loss_rate",
    "mask_enstrophy_loss_spectral",
    "mask_enstrophy_loss_crosscheck_residual",
    "normalized_mask_enstrophy_loss_crosscheck_residual",
    "observed_unfiltered_enstrophy_rate",
    "unfiltered_ledger_rate",
    "unfiltered_closure_residual",
    "normalized_unfiltered_closure_residual",
    "observed_filtered_enstrophy_rate",
    "filtered_ledger_rate",
    "filtered_closure_residual",
    "normalized_filtered_closure_residual",
    "filter_bookkeeping_residual",
    "normalized_filter_bookkeeping_residual",
    "stage1_viscous_dissipation_actual",
    "stage1_viscous_dissipation_gradient",
    "stage1_viscous_identity_residual",
    "normalized_stage1_viscous_identity_residual",
    "stage2_viscous_dissipation_actual",
    "stage2_viscous_dissipation_gradient",
    "stage2_viscous_identity_residual",
    "normalized_stage2_viscous_identity_residual",
    "stage1_forcing_identity_residual",
    "normalized_stage1_forcing_identity_residual",
    "stage2_forcing_identity_residual",
    "normalized_stage2_forcing_identity_residual",
    "stage_reconstruction_rms",
    "normalized_stage_reconstruction_rms",
    "unfiltered_reconstruction_rms",
    "normalized_unfiltered_reconstruction_rms",
    "filtered_reconstruction_rms",
    "normalized_filtered_reconstruction_rms",
    "inverse_fft_imaginary_rms",
    "normalized_inverse_fft_imaginary_rms",
    "all_numeric_values_finite",
    "rk2_remainder_sign_pass",
    "mask_rate_sign_pass",
    "all_integrity_gates_pass",
)

HIGH_CADENCE_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "energy",
    "enstrophy",
    "forcing_rms",
    "energy_injection_rate",
    "enstrophy_injection_rate",
    "viscous_energy_dissipation_rate",
    "viscous_enstrophy_dissipation_rate",
    "continuous_energy_rhs",
    "continuous_enstrophy_rhs",
    "interval_duration",
    "observed_energy_rate",
    "mean_continuous_energy_rhs",
    "energy_budget_residual",
    "mean_energy_injection_rate",
    "mean_viscous_energy_dissipation_rate",
    "normalized_energy_budget_residual",
    "observed_enstrophy_rate",
    "mean_continuous_enstrophy_rhs",
    "enstrophy_budget_residual",
    "mean_enstrophy_injection_rate",
    "mean_viscous_enstrophy_dissipation_rate",
    "normalized_enstrophy_budget_residual",
    "forcing_sha256",
    "all_numeric_values_finite",
)

TIME_BLOCK_FIELDNAMES = (
    "block_id",
    "label",
    "step_count",
    "time_start",
    "time_end",
    "classification",
    "integrity_failure_count",
    "median_normalized_unfiltered_closure",
    "maximum_normalized_unfiltered_closure",
    "median_normalized_filtered_closure",
    "maximum_normalized_filtered_closure",
    "median_normalized_mask_crosscheck",
    "maximum_normalized_mask_crosscheck",
    "integrated_non_forcing_non_viscous",
    "cancellation_ratio",
    "advection_activity_share",
    "rk2_activity_share",
    "mask_activity_share",
    "advection_integrated_signed",
    "rk2_integrated_signed",
    "mask_integrated_signed",
    "advection_reduction_fraction",
    "rk2_reduction_fraction",
    "mask_reduction_fraction",
    "advection_n90_steps",
    "rk2_n90_steps",
    "mask_n90_steps",
    "advection_dominance_pass",
    "rk2_dominance_pass",
    "mask_dominance_pass",
) + tuple(
    f"{component}_{metric}"
    for component in COMPONENTS
    for metric in (
        "mean_signed_rate",
        "median_signed_rate",
        "mean_absolute_rate",
        "maximum_absolute_rate",
        "integrated_signed",
        "integrated_absolute_activity",
        "positive_count",
        "negative_count",
        "zero_count",
    )
)

INVENTORY_FIELDNAMES = (
    "relative_path",
    "bytes",
    "sha256",
    "inventory_note",
)


# ============================================================================
# Generic utilities
# ============================================================================

class IntegrityFailure(RuntimeError):
    def __init__(self, gate: str, message: str) -> None:
        super().__init__(message)
        self.gate = gate


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def utc_text(value: datetime.datetime | None = None) -> str:
    moment = utc_now() if value is None else value
    return moment.replace(microsecond=0).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def sha256_array(value: object) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    return sha256_bytes(array.tobytes(order="C"))


def git_process(
    repo: Path,
    *args: str,
    check: bool = True,
    text: bool = True,
) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        shell=False,
        check=check,
        capture_output=True,
        text=text,
        encoding="utf-8" if text else None,
        errors="strict" if text else None,
    )


def git_read(repo: Path, *args: str) -> str:
    return str(git_process(repo, *args).stdout).strip()


def git_bytes(repo: Path, *args: str) -> bytes:
    return bytes(
        git_process(
            repo,
            *args,
            text=False,
        ).stdout
    )


def path_is_git_ignored(repo: Path, path: Path) -> bool:
    relative = path.relative_to(repo).as_posix()

    result = git_process(
        repo,
        "check-ignore",
        "-q",
        "--no-index",
        "--",
        relative,
        check=False,
    )

    return result.returncode == 0


def finite_float(name: str, value: object) -> float:
    result = float(value)

    if not math.isfinite(result):
        raise IntegrityFailure(
            "finite_scalar",
            f"{name} is nonfinite: {value!r}",
        )

    return result


def field_rms(value: object) -> float:
    array = np.asarray(value, dtype=np.float64)
    return float(np.sqrt(np.mean(array * array)))


def enstrophy(value: object) -> float:
    array = np.asarray(value, dtype=np.float64)
    return 0.5 * float(np.mean(array * array))


def arithmetic_mean_product(first: object, second: object) -> float:
    return float(
        np.mean(
            np.asarray(first, dtype=np.float64)
            * np.asarray(second, dtype=np.float64)
        )
    )


def normalized_difference(
    first: float,
    second: float,
    floor: float = RESIDUAL_FLOOR,
) -> float:
    return abs(first - second) / max(
        abs(first),
        abs(second),
        floor,
    )


def normalized_rms_difference(
    observed: object,
    expected: object,
) -> tuple[float, float]:
    observed_array = np.asarray(observed, dtype=np.float64)
    expected_array = np.asarray(expected, dtype=np.float64)

    difference = field_rms(observed_array - expected_array)
    normalized = difference / max(
        field_rms(expected_array),
        RESIDUAL_FLOOR,
    )

    return difference, normalized


def all_numeric_values_finite(row: Mapping[str, object]) -> bool:
    for value in row.values():
        if value is None or isinstance(value, (str, bool)):
            continue

        if isinstance(value, (int, float, np.integer, np.floating)):
            if not math.isfinite(float(value)):
                return False

    return True


def atomic_write_text(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")

    try:
        with temporary.open(
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())

        temporary.replace(path)

    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, value: object) -> None:
    atomic_write_text(
        path,
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
    )


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


class IncrementalCsvWriter:
    def __init__(
        self,
        path: Path,
        fieldnames: Sequence[str],
        *,
        flush_interval: int = CSV_FLUSH_INTERVAL,
    ) -> None:
        self.path = path
        self.fieldnames = tuple(fieldnames)
        self.flush_interval = flush_interval
        self.count = 0
        self.handle = path.open(
            "w",
            encoding="utf-8",
            newline="",
        )
        self.writer = csv.DictWriter(
            self.handle,
            fieldnames=list(self.fieldnames),
            extrasaction="raise",
            lineterminator="\n",
        )
        self.writer.writeheader()
        self.flush()

    def write(self, row: Mapping[str, object]) -> None:
        self.writer.writerow(row)
        self.count += 1

        if self.count % self.flush_interval == 0:
            self.flush()

    def flush(self) -> None:
        self.handle.flush()
        os.fsync(self.handle.fileno())

    def close(self) -> None:
        if self.handle.closed:
            return

        self.flush()
        self.handle.close()


# ============================================================================
# Source identity and Git gates
# ============================================================================

def verify_source_identities(repo: Path) -> dict[str, str]:
    paths = {
        "exact_ledger_design": repo / EXACT_LEDGER_DESIGN_PATH,
        "runner_design": repo / RUNNER_DESIGN_PATH,
        "spectral_solver":
            repo / "project" / "solver" / "spectral_solver.py",
        "forcing_budget_diagnostic":
            repo / "forcing_budget_diagnostic.py",
    }

    expected = {
        "exact_ledger_design":
            EXPECTED_EXACT_LEDGER_DESIGN_SHA256,
        "runner_design":
            EXPECTED_RUNNER_DESIGN_SHA256,
        "spectral_solver":
            EXPECTED_SOLVER_SHA256,
        "forcing_budget_diagnostic":
            EXPECTED_BUDGET_SHA256,
    }

    observed: dict[str, str] = {}

    for name, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"required source is missing: {path}")

        digest = sha256_file(path)
        observed[name] = digest

        if digest != expected[name]:
            raise RuntimeError(
                f"source hash mismatch for {name}: {digest}"
            )

    archive = repo / ARCHIVED_SOURCE_DIRECTORY

    for filename, expected_hash in ARCHIVED_SOURCE_HASHES.items():
        path = archive / filename

        if not path.is_file():
            raise RuntimeError(
                f"archived source is missing: {path}"
            )

        digest = sha256_file(path)
        observed[f"archive/{filename}"] = digest

        if digest != expected_hash:
            raise RuntimeError(
                f"archived source hash mismatch for "
                f"{filename}: {digest}"
            )

    inventory_rows = read_csv_rows(
        archive / "file_inventory.csv"
    )

    inventory_map = {
        row["relative_path"]: row["sha256"]
        for row in inventory_rows
        if row["sha256"].strip() != ""
    }

    for filename, expected_hash in ARCHIVED_SOURCE_HASHES.items():
        if filename == "file_inventory.csv":
            continue

        if inventory_map.get(filename) != expected_hash:
            raise RuntimeError(
                f"archived inventory does not confirm {filename}"
            )

    return observed


def verify_runner_commit_shape(
    repo: Path,
    runner: Path,
) -> str:
    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        raise RuntimeError("active branch is not phase4_validation")

    if git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ) != "":
        raise RuntimeError("working tree is not clean")

    head = git_read(repo, "rev-parse", "HEAD")
    parent = git_read(repo, "rev-parse", "HEAD^")

    if parent != AUTHORIZED_RUNNER_DESIGN_COMMIT:
        raise RuntimeError(
            f"runner commit parent is {parent}, "
            f"expected {AUTHORIZED_RUNNER_DESIGN_COMMIT}"
        )

    changed = git_read(
        repo,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "HEAD",
    ).splitlines()

    if changed != [runner.name]:
        raise RuntimeError(
            f"runner commit changed unexpected files: {changed!r}"
        )

    tracked = git_process(
        repo,
        "ls-files",
        "--error-unmatch",
        "--",
        runner.name,
        check=False,
    )

    if tracked.returncode != 0:
        raise RuntimeError("runner is not tracked")

    if git_bytes(
        repo,
        "show",
        f"HEAD:{runner.name}",
    ) != runner.read_bytes():
        raise RuntimeError(
            "working runner bytes differ from committed bytes"
        )

    return head


# ============================================================================
# Frozen forcing and archived comparison data
# ============================================================================

def build_rms_matched_multimode_forcing(
    solver: object,
) -> tuple[np.ndarray, dict[str, object]]:
    x = np.asarray(solver.X)
    y = np.asarray(solver.Y)

    base = 0.01 * np.sin(2.0 * x) * np.cos(2.0 * y)

    raw = (
        1.00 * np.sin(2.0 * x) * np.cos(2.0 * y)
        + 0.75 * np.sin(3.0 * x) * np.cos(y)
        + 0.50 * np.sin(x) * np.cos(4.0 * y)
        + 0.35 * np.cos(4.0 * x - 2.0 * y)
    )

    raw = raw - np.mean(raw)

    base_rms = field_rms(base)
    raw_rms = field_rms(raw)

    if raw_rms == 0.0:
        raise RuntimeError("raw multimode forcing has zero RMS")

    coefficient = base_rms / raw_rms

    forcing = np.ascontiguousarray(
        raw * coefficient,
        dtype=np.float64,
    )

    matched_rms = field_rms(forcing)

    if forcing.shape != (N, N):
        raise RuntimeError(
            f"forcing shape is {forcing.shape}, expected {(N, N)}"
        )

    if not np.isrealobj(forcing):
        raise RuntimeError("forcing is not real-valued")

    if not np.isfinite(forcing).all():
        raise RuntimeError("forcing contains a nonfinite value")

    if abs(matched_rms - FORCING_TARGET_RMS) > FORCING_RMS_TOLERANCE:
        raise RuntimeError(
            f"forcing RMS is {matched_rms}, "
            f"expected {FORCING_TARGET_RMS}"
        )

    forcing_hash = sha256_array(forcing)

    if forcing_hash != EXPECTED_FORCING_SHA256:
        raise RuntimeError(
            f"forcing SHA256 is {forcing_hash}, "
            f"expected {EXPECTED_FORCING_SHA256}"
        )

    forcing.setflags(write=False)

    return forcing, {
        "forcing_terms": FORCING_TERMS,
        "normalization_coefficient": coefficient,
        "base_single_mode_rms": base_rms,
        "raw_multimode_rms": raw_rms,
        "normalized_multimode_rms": matched_rms,
        "forcing_mean": float(np.mean(forcing)),
        "forcing_max_abs": float(np.max(np.abs(forcing))),
        "forcing_sha256": forcing_hash,
        "forcing_array_shape": list(forcing.shape),
        "forcing_array_dtype": str(forcing.dtype),
        "forcing_is_finite": bool(np.isfinite(forcing).all()),
        "forcing_is_real": bool(np.isrealobj(forcing)),
        "forcing_is_writeable": bool(forcing.flags.writeable),
    }


def load_archived_budget(
    repo: Path,
) -> dict[int, dict[str, float]]:
    path = (
        repo
        / ARCHIVED_SOURCE_DIRECTORY
        / "forcing_budget.csv"
    )

    raw_rows = read_csv_rows(path)
    output: dict[int, dict[str, float]] = {}

    fields = (
        "physical_time",
        "energy",
        "enstrophy",
        "forcing_rms",
        "energy_injection_rate",
        "enstrophy_injection_rate",
        "viscous_energy_dissipation_rate",
        "viscous_enstrophy_dissipation_rate",
        "continuous_energy_rhs",
        "continuous_enstrophy_rhs",
    )

    for raw in raw_rows:
        loop_index = int(raw["loop_index"])
        output[loop_index] = {
            field: finite_float(
                f"archived {field}",
                raw[field],
            )
            for field in fields
        }

    if len(output) != EXPECTED_ARCHIVE_MATCHES:
        raise RuntimeError(
            f"expected {EXPECTED_ARCHIVE_MATCHES} archived "
            f"budget snapshots, found {len(output)}"
        )

    expected_indices = set(range(0, STEPS, ARCHIVE_MATCH_INTERVAL))

    if set(output) != expected_indices:
        raise RuntimeError(
            "archived budget loop indices are incomplete"
        )

    return output


# ============================================================================
# Exact per-step ledger
# ============================================================================

def spectral_viscous_dissipation(
    omega: np.ndarray,
    *,
    nu: float,
    solver_k2: np.ndarray,
) -> float:
    """
    Evaluate the exact spectral quadratic form used by the protected
    diffusion operator.

    The protected solver sets k2[0,0] to 1.0 to avoid division by zero in
    its shared Poisson array. This function intentionally preserves that
    frozen zero-mode convention so the cross-check measures the actual
    implemented diffusion array, not an idealized gradient operator.
    """
    omega_hat = np.fft.fft2(omega)
    k2_array = np.asarray(solver_k2, dtype=np.float64)

    return nu * float(
        np.sum(
            k2_array * np.abs(omega_hat) ** 2
        )
        / float(omega.size ** 2)
    )


def ledger_step(
    solver: object,
    forcing: np.ndarray,
    forcing_hash: str,
    *,
    loop_index: int,
    forcing_budget_snapshot: object,
) -> tuple[dict[str, object], np.ndarray]:
    current = np.asarray(solver.w, dtype=np.float64)

    if not np.isfinite(current).all():
        raise IntegrityFailure(
            "current_state_finite",
            "current vorticity contains a nonfinite value",
        )

    psi_1 = solver.streamfunction(current)
    u_1, v_1 = solver.velocity(psi_1)

    omega_x_1 = (
        np.roll(current, -1, 1)
        - np.roll(current, 1, 1)
    ) / (2.0 * solver.dx)

    omega_y_1 = (
        np.roll(current, -1, 0)
        - np.roll(current, 1, 0)
    ) / (2.0 * solver.dx)

    transport_1 = u_1 * omega_x_1 + v_1 * omega_y_1
    advection_1 = -transport_1
    viscous_1 = solver.laplacian_spectral(current)
    total_1 = advection_1 + viscous_1 + forcing
    stage = current + solver.dt * total_1

    if not np.isfinite(stage).all():
        raise IntegrityFailure(
            "stage_state_finite",
            "RK2 stage state contains a nonfinite value",
        )

    psi_2 = solver.streamfunction(stage)
    u_2, v_2 = solver.velocity(psi_2)

    omega_x_2 = (
        np.roll(stage, -1, 1)
        - np.roll(stage, 1, 1)
    ) / (2.0 * solver.dx)

    omega_y_2 = (
        np.roll(stage, -1, 0)
        - np.roll(stage, 1, 0)
    ) / (2.0 * solver.dx)

    transport_2 = u_2 * omega_x_2 + v_2 * omega_y_2
    advection_2 = -transport_2
    viscous_2 = solver.laplacian_spectral(stage)
    total_2 = advection_2 + viscous_2 + forcing

    unfiltered = (
        current
        + 0.5 * solver.dt * (total_1 + total_2)
    )

    unfiltered_hat = np.fft.fft2(unfiltered)
    filtered_hat = unfiltered_hat * solver.deal
    filtered_complex = np.fft.ifft2(filtered_hat)
    filtered = filtered_complex.real

    if not np.isfinite(filtered).all():
        raise IntegrityFailure(
            "accepted_state_finite",
            "accepted state contains a nonfinite value",
        )

    z_current = enstrophy(current)
    z_stage = enstrophy(stage)
    z_unfiltered = enstrophy(unfiltered)
    z_filtered = enstrophy(filtered)

    stage1_advection_work = arithmetic_mean_product(
        current,
        advection_1,
    )
    stage1_viscous_work = arithmetic_mean_product(
        current,
        viscous_1,
    )
    stage1_forcing_work = arithmetic_mean_product(
        current,
        forcing,
    )
    stage1_total_work = arithmetic_mean_product(
        current,
        total_1,
    )

    stage2_advection_work = arithmetic_mean_product(
        stage,
        advection_2,
    )
    stage2_viscous_work = arithmetic_mean_product(
        stage,
        viscous_2,
    )
    stage2_forcing_work = arithmetic_mean_product(
        stage,
        forcing,
    )
    stage2_total_work = arithmetic_mean_product(
        stage,
        total_2,
    )

    rk2_advection = 0.5 * (
        stage1_advection_work
        + stage2_advection_work
    )

    rk2_viscous = 0.5 * (
        stage1_viscous_work
        + stage2_viscous_work
    )

    rk2_forcing = 0.5 * (
        stage1_forcing_work
        + stage2_forcing_work
    )

    total_difference = total_2 - total_1

    rk2_remainder = (
        solver.dt
        / 8.0
        * float(np.mean(total_difference * total_difference))
    )

    rk2_remainder_expanded = (
        solver.dt
        / 8.0
        * (
            float(np.mean(total_1 * total_1))
            - 2.0 * float(np.mean(total_1 * total_2))
            + float(np.mean(total_2 * total_2))
        )
    )

    remainder_crosscheck = (
        rk2_remainder
        - rk2_remainder_expanded
    )

    observed_mask_change = z_filtered - z_unfiltered

    discarded_hat = np.where(
        solver.deal,
        0.0,
        unfiltered_hat,
    )

    removed_physical_complex = np.fft.ifft2(
        discarded_hat
    )

    mask_loss = 0.5 * float(
        np.mean(
            np.abs(removed_physical_complex) ** 2
        )
    )
    mask_loss_rate = mask_loss / solver.dt
    mask_change = -mask_loss
    mask_rate = -mask_loss_rate

    mask_loss_spectral = float(
        np.sum(np.abs(discarded_hat) ** 2)
        / (2.0 * float(N ** 4))
    )

    mask_crosscheck = (
        mask_loss
        - mask_loss_spectral
    )

    mask_crosscheck_normalized = abs(mask_crosscheck) / max(
        abs(mask_loss),
        abs(mask_loss_spectral),
        RESIDUAL_FLOOR,
    )

    observed_unfiltered_rate = (
        z_unfiltered - z_current
    ) / solver.dt

    unfiltered_ledger_rate = (
        rk2_advection
        + rk2_viscous
        + rk2_forcing
        + rk2_remainder
    )

    unfiltered_closure = (
        observed_unfiltered_rate
        - unfiltered_ledger_rate
    )

    observed_filtered_rate = (
        z_filtered - z_current
    ) / solver.dt

    filtered_ledger_rate = (
        unfiltered_ledger_rate
        + mask_rate
    )

    filtered_closure = (
        observed_filtered_rate
        - filtered_ledger_rate
    )

    filter_bookkeeping = (
        observed_filtered_rate
        - observed_unfiltered_rate
        - mask_rate
    )

    ledger_scale = max(
        abs(observed_filtered_rate),
        abs(rk2_advection)
        + abs(rk2_viscous)
        + abs(rk2_forcing)
        + abs(rk2_remainder)
        + abs(mask_rate),
        RESIDUAL_FLOOR,
    )

    normalized_unfiltered_closure = (
        abs(unfiltered_closure) / ledger_scale
    )

    normalized_filtered_closure = (
        abs(filtered_closure) / ledger_scale
    )

    normalized_filter_bookkeeping = (
        abs(filter_bookkeeping) / ledger_scale
    )

    stage1_viscous_actual = -stage1_viscous_work
    stage2_viscous_actual = -stage2_viscous_work

    stage1_viscous_gradient = spectral_viscous_dissipation(
        current,
        nu=float(solver.nu),
        solver_k2=np.asarray(solver.k2),
    )

    stage2_viscous_gradient = spectral_viscous_dissipation(
        stage,
        nu=float(solver.nu),
        solver_k2=np.asarray(solver.k2),
    )

    stage1_viscous_residual = (
        stage1_viscous_actual
        - stage1_viscous_gradient
    )

    stage2_viscous_residual = (
        stage2_viscous_actual
        - stage2_viscous_gradient
    )

    normalized_stage1_viscous = normalized_difference(
        stage1_viscous_actual,
        stage1_viscous_gradient,
    )

    normalized_stage2_viscous = normalized_difference(
        stage2_viscous_actual,
        stage2_viscous_gradient,
    )

    stage1_budget = forcing_budget_snapshot(
        omega=current,
        forcing=forcing,
        nu=solver.nu,
        kx=solver.kx,
        ky=solver.ky,
        dt=solver.dt,
        loop_index=loop_index,
    )

    stage2_budget = forcing_budget_snapshot(
        omega=stage,
        forcing=forcing,
        nu=solver.nu,
        kx=solver.kx,
        ky=solver.ky,
        dt=solver.dt,
        loop_index=loop_index,
    )

    stage1_forcing_residual = (
        stage1_forcing_work
        - float(stage1_budget["enstrophy_injection_rate"])
    )

    stage2_forcing_residual = (
        stage2_forcing_work
        - float(stage2_budget["enstrophy_injection_rate"])
    )

    normalized_stage1_forcing = normalized_difference(
        stage1_forcing_work,
        float(stage1_budget["enstrophy_injection_rate"]),
    )

    normalized_stage2_forcing = normalized_difference(
        stage2_forcing_work,
        float(stage2_budget["enstrophy_injection_rate"]),
    )

    stage_expected = (
        current + solver.dt * total_1
    )

    unfiltered_expected = (
        current
        + 0.5 * solver.dt * (total_1 + total_2)
    )

    filtered_expected_complex = np.fft.ifft2(
        np.fft.fft2(unfiltered_expected)
        * solver.deal
    )

    filtered_expected = filtered_expected_complex.real

    stage_reconstruction_rms, normalized_stage_reconstruction = (
        normalized_rms_difference(
            stage,
            stage_expected,
        )
    )

    (
        unfiltered_reconstruction_rms,
        normalized_unfiltered_reconstruction,
    ) = normalized_rms_difference(
        unfiltered,
        unfiltered_expected,
    )

    (
        filtered_reconstruction_rms,
        normalized_filtered_reconstruction,
    ) = normalized_rms_difference(
        filtered,
        filtered_expected,
    )

    imaginary_rms = field_rms(
        filtered_complex.imag
    )

    normalized_imaginary = imaginary_rms / max(
        field_rms(filtered),
        RESIDUAL_FLOOR,
    )

    rk2_remainder_sign_pass = (
        rk2_remainder
        >= -SIGN_TOLERANCE_FACTOR * ledger_scale
    )

    mask_rate_sign_pass = (
        mask_rate
        <= SIGN_TOLERANCE_FACTOR * ledger_scale
    )

    gates = {
        "normalized_unfiltered_closure": (
            normalized_unfiltered_closure
            <= LEDGER_CLOSURE_LIMIT
        ),
        "normalized_filtered_closure": (
            normalized_filtered_closure
            <= LEDGER_CLOSURE_LIMIT
        ),
        "normalized_filter_bookkeeping": (
            normalized_filter_bookkeeping
            <= FILTER_BOOKKEEPING_LIMIT
        ),
        "normalized_mask_crosscheck": (
            mask_crosscheck_normalized
            <= MASK_CROSSCHECK_LIMIT
        ),
        "normalized_stage1_viscous_identity": (
            normalized_stage1_viscous
            <= VISCOUS_IDENTITY_LIMIT
        ),
        "normalized_stage2_viscous_identity": (
            normalized_stage2_viscous
            <= VISCOUS_IDENTITY_LIMIT
        ),
        "normalized_stage1_forcing_identity": (
            normalized_stage1_forcing
            <= FORCING_IDENTITY_LIMIT
        ),
        "normalized_stage2_forcing_identity": (
            normalized_stage2_forcing
            <= FORCING_IDENTITY_LIMIT
        ),
        "normalized_stage_reconstruction": (
            normalized_stage_reconstruction
            <= STATE_RECONSTRUCTION_LIMIT
        ),
        "normalized_unfiltered_reconstruction": (
            normalized_unfiltered_reconstruction
            <= STATE_RECONSTRUCTION_LIMIT
        ),
        "normalized_filtered_reconstruction": (
            normalized_filtered_reconstruction
            <= STATE_RECONSTRUCTION_LIMIT
        ),
        "normalized_inverse_fft_imaginary": (
            normalized_imaginary
            <= IMAGINARY_RATIO_LIMIT
        ),
        "rk2_remainder_sign": rk2_remainder_sign_pass,
        "mask_rate_sign": mask_rate_sign_pass,
    }

    row: dict[str, object] = {
        "loop_index": loop_index,
        "completed_steps": loop_index + 1,
        "physical_time": (loop_index + 1) * solver.dt,
        "dt": solver.dt,
        "forcing_sha256": forcing_hash,
        "z_current": z_current,
        "z_stage": z_stage,
        "z_unfiltered": z_unfiltered,
        "z_filtered": z_filtered,
        "stage1_advection_work_rate": stage1_advection_work,
        "stage1_viscous_work_rate": stage1_viscous_work,
        "stage1_forcing_work_rate": stage1_forcing_work,
        "stage1_total_work_rate": stage1_total_work,
        "stage1_advection_rms": field_rms(advection_1),
        "stage1_viscous_rms": field_rms(viscous_1),
        "stage1_total_rhs_rms": field_rms(total_1),
        "stage2_advection_work_rate": stage2_advection_work,
        "stage2_viscous_work_rate": stage2_viscous_work,
        "stage2_forcing_work_rate": stage2_forcing_work,
        "stage2_total_work_rate": stage2_total_work,
        "stage2_advection_rms": field_rms(advection_2),
        "stage2_viscous_rms": field_rms(viscous_2),
        "stage2_total_rhs_rms": field_rms(total_2),
        "rk2_advection_rate": rk2_advection,
        "rk2_viscous_rate": rk2_viscous,
        "rk2_viscous_dissipation_rate": -rk2_viscous,
        "rk2_forcing_rate": rk2_forcing,
        "rk2_quadratic_remainder_rate": rk2_remainder,
        "rk2_quadratic_remainder_expanded": (
            rk2_remainder_expanded
        ),
        "rk2_remainder_crosscheck_residual": (
            remainder_crosscheck
        ),
        "mask_field_removal_rms": field_rms(
            unfiltered - filtered
        ),
        "mask_enstrophy_change": mask_change,
        "mask_enstrophy_change_rate": mask_rate,
        "mask_enstrophy_loss": mask_loss,
        "mask_enstrophy_loss_rate": mask_loss_rate,
        "mask_enstrophy_loss_spectral": mask_loss_spectral,
        "mask_enstrophy_loss_crosscheck_residual": (
            mask_crosscheck
        ),
        "normalized_mask_enstrophy_loss_crosscheck_residual": (
            mask_crosscheck_normalized
        ),
        "observed_unfiltered_enstrophy_rate": (
            observed_unfiltered_rate
        ),
        "unfiltered_ledger_rate": unfiltered_ledger_rate,
        "unfiltered_closure_residual": unfiltered_closure,
        "normalized_unfiltered_closure_residual": (
            normalized_unfiltered_closure
        ),
        "observed_filtered_enstrophy_rate": (
            observed_filtered_rate
        ),
        "filtered_ledger_rate": filtered_ledger_rate,
        "filtered_closure_residual": filtered_closure,
        "normalized_filtered_closure_residual": (
            normalized_filtered_closure
        ),
        "filter_bookkeeping_residual": filter_bookkeeping,
        "normalized_filter_bookkeeping_residual": (
            normalized_filter_bookkeeping
        ),
        "stage1_viscous_dissipation_actual": (
            stage1_viscous_actual
        ),
        "stage1_viscous_dissipation_gradient": (
            stage1_viscous_gradient
        ),
        "stage1_viscous_identity_residual": (
            stage1_viscous_residual
        ),
        "normalized_stage1_viscous_identity_residual": (
            normalized_stage1_viscous
        ),
        "stage2_viscous_dissipation_actual": (
            stage2_viscous_actual
        ),
        "stage2_viscous_dissipation_gradient": (
            stage2_viscous_gradient
        ),
        "stage2_viscous_identity_residual": (
            stage2_viscous_residual
        ),
        "normalized_stage2_viscous_identity_residual": (
            normalized_stage2_viscous
        ),
        "stage1_forcing_identity_residual": (
            stage1_forcing_residual
        ),
        "normalized_stage1_forcing_identity_residual": (
            normalized_stage1_forcing
        ),
        "stage2_forcing_identity_residual": (
            stage2_forcing_residual
        ),
        "normalized_stage2_forcing_identity_residual": (
            normalized_stage2_forcing
        ),
        "stage_reconstruction_rms": stage_reconstruction_rms,
        "normalized_stage_reconstruction_rms": (
            normalized_stage_reconstruction
        ),
        "unfiltered_reconstruction_rms": (
            unfiltered_reconstruction_rms
        ),
        "normalized_unfiltered_reconstruction_rms": (
            normalized_unfiltered_reconstruction
        ),
        "filtered_reconstruction_rms": (
            filtered_reconstruction_rms
        ),
        "normalized_filtered_reconstruction_rms": (
            normalized_filtered_reconstruction
        ),
        "inverse_fft_imaginary_rms": imaginary_rms,
        "normalized_inverse_fft_imaginary_rms": (
            normalized_imaginary
        ),
        "all_numeric_values_finite": True,
        "rk2_remainder_sign_pass": rk2_remainder_sign_pass,
        "mask_rate_sign_pass": mask_rate_sign_pass,
        "all_integrity_gates_pass": all(gates.values()),
    }

    row["all_numeric_values_finite"] = all_numeric_values_finite(
        row
    )

    row["all_integrity_gates_pass"] = (
        bool(row["all_numeric_values_finite"])
        and all(gates.values())
    )

    if not bool(row["all_integrity_gates_pass"]):
        failed = [
            name
            for name, passed in gates.items()
            if not passed
        ]

        if not bool(row["all_numeric_values_finite"]):
            failed.insert(0, "all_numeric_values_finite")

        raise IntegrityFailure(
            failed[0],
            "exact ledger integrity gate failed at "
            f"loop index {loop_index}: {failed}",
        )

    return row, filtered


# ============================================================================
# High-cadence budget and archive equivalence
# ============================================================================

def high_cadence_row(
    snapshot: Mapping[str, float | int],
    previous: Mapping[str, float | int] | None,
    *,
    forcing_hash: str,
    forcing_budget_interval: object,
) -> dict[str, object]:
    row: dict[str, object] = {
        **snapshot,
        "interval_duration": None,
        "observed_energy_rate": None,
        "mean_continuous_energy_rhs": None,
        "energy_budget_residual": None,
        "mean_energy_injection_rate": None,
        "mean_viscous_energy_dissipation_rate": None,
        "normalized_energy_budget_residual": None,
        "observed_enstrophy_rate": None,
        "mean_continuous_enstrophy_rhs": None,
        "enstrophy_budget_residual": None,
        "mean_enstrophy_injection_rate": None,
        "mean_viscous_enstrophy_dissipation_rate": None,
        "normalized_enstrophy_budget_residual": None,
        "forcing_sha256": forcing_hash,
        "all_numeric_values_finite": True,
    }

    if previous is not None:
        interval = forcing_budget_interval(
            previous,
            snapshot,
        )

        mean_energy_injection = 0.5 * (
            float(previous["energy_injection_rate"])
            + float(snapshot["energy_injection_rate"])
        )

        mean_energy_dissipation = 0.5 * (
            float(previous["viscous_energy_dissipation_rate"])
            + float(snapshot["viscous_energy_dissipation_rate"])
        )

        mean_enstrophy_injection = 0.5 * (
            float(previous["enstrophy_injection_rate"])
            + float(snapshot["enstrophy_injection_rate"])
        )

        mean_enstrophy_dissipation = 0.5 * (
            float(previous["viscous_enstrophy_dissipation_rate"])
            + float(snapshot["viscous_enstrophy_dissipation_rate"])
        )

        row.update(interval)

        row["mean_energy_injection_rate"] = (
            mean_energy_injection
        )
        row["mean_viscous_energy_dissipation_rate"] = (
            mean_energy_dissipation
        )
        row["normalized_energy_budget_residual"] = (
            abs(float(interval["energy_budget_residual"]))
            / max(
                abs(mean_energy_injection),
                abs(mean_energy_dissipation),
                RESIDUAL_FLOOR,
            )
        )
        row["mean_enstrophy_injection_rate"] = (
            mean_enstrophy_injection
        )
        row["mean_viscous_enstrophy_dissipation_rate"] = (
            mean_enstrophy_dissipation
        )
        row["normalized_enstrophy_budget_residual"] = (
            abs(float(interval["enstrophy_budget_residual"]))
            / max(
                abs(mean_enstrophy_injection),
                abs(mean_enstrophy_dissipation),
                RESIDUAL_FLOOR,
            )
        )

    row["all_numeric_values_finite"] = all_numeric_values_finite(
        row
    )

    if not bool(row["all_numeric_values_finite"]):
        raise IntegrityFailure(
            "high_cadence_budget_finite",
            "high-cadence budget contains a nonfinite value",
        )

    return row


def initialize_archive_equivalence() -> dict[str, object]:
    fields = (
        "physical_time",
        "energy",
        "enstrophy",
        "forcing_rms",
        "energy_injection_rate",
        "enstrophy_injection_rate",
        "viscous_energy_dissipation_rate",
        "viscous_enstrophy_dissipation_rate",
        "continuous_energy_rhs",
        "continuous_enstrophy_rhs",
    )

    return {
        "match_count": 0,
        "fields": {
            field: {
                "maximum_absolute_difference": 0.0,
                "maximum_relative_difference": 0.0,
                "loop_index_of_maximum_absolute_difference": None,
                "loop_index_of_maximum_relative_difference": None,
            }
            for field in fields
        },
        "all_matches_pass": True,
    }


def compare_archive_snapshot(
    *,
    loop_index: int,
    replay: Mapping[str, float | int],
    archived: Mapping[str, float],
    state: dict[str, object],
) -> None:
    for field, archived_value in archived.items():
        replay_value = float(replay[field])
        absolute = abs(replay_value - archived_value)
        relative = absolute / max(
            abs(archived_value),
            ARCHIVE_ABSOLUTE_FLOOR,
        )

        field_state = state["fields"][field]

        if absolute > field_state["maximum_absolute_difference"]:
            field_state["maximum_absolute_difference"] = absolute
            field_state[
                "loop_index_of_maximum_absolute_difference"
            ] = loop_index

        if relative > field_state["maximum_relative_difference"]:
            field_state["maximum_relative_difference"] = relative
            field_state[
                "loop_index_of_maximum_relative_difference"
            ] = loop_index

        if field == "physical_time":
            passed = (
                absolute <= ARCHIVE_TIME_ABS_TOLERANCE
            )

        elif field == "forcing_rms":
            passed = (
                absolute
                <= ARCHIVE_FORCING_RMS_ABS_TOLERANCE
            )

        else:
            passed = (
                relative <= ARCHIVE_RELATIVE_TOLERANCE
                or absolute <= ARCHIVE_ABSOLUTE_FLOOR
            )

        if not passed:
            state["all_matches_pass"] = False

            raise IntegrityFailure(
                "archived_replay_equivalence",
                f"archive equivalence failed for {field} "
                f"at loop index {loop_index}: "
                f"replay={replay_value!r}, "
                f"archive={archived_value!r}, "
                f"absolute={absolute:.12e}, "
                f"relative={relative:.12e}",
            )

    state["match_count"] += 1


# ============================================================================
# Block aggregation and attribution
# ============================================================================

def block_ids_for_time(physical_time: float) -> tuple[int, int]:
    tolerance = 1.0e-12
    primary: int | None = None

    for block in TIME_BLOCKS[:-1]:
        lower = float(block["lower"])
        upper = float(block["upper"])
        lower_inclusive = bool(block["lower_inclusive"])

        lower_ok = (
            physical_time >= lower - tolerance
            if lower_inclusive
            else physical_time > lower + tolerance
        )

        if lower_ok and physical_time <= upper + tolerance:
            primary = int(block["block_id"])
            break

    if primary is None:
        raise IntegrityFailure(
            "time_block_assignment",
            f"could not assign time {physical_time} to a block",
        )

    return primary, 6


def new_block_accumulator(
    block: Mapping[str, object],
) -> dict[str, object]:
    return {
        "block_id": int(block["block_id"]),
        "label": str(block["label"]),
        "time_start": None,
        "time_end": None,
        "step_count": 0,
        "integrity_failure_count": 0,
        "normalized_unfiltered_closure": [],
        "normalized_filtered_closure": [],
        "normalized_mask_crosscheck": [],
        "components": {
            component: []
            for component in COMPONENTS
        },
    }


def update_block_accumulator(
    accumulator: dict[str, object],
    row: Mapping[str, object],
) -> None:
    physical_time = float(row["physical_time"])

    if accumulator["time_start"] is None:
        accumulator["time_start"] = physical_time

    accumulator["time_end"] = physical_time
    accumulator["step_count"] += 1

    accumulator["normalized_unfiltered_closure"].append(
        float(row["normalized_unfiltered_closure_residual"])
    )
    accumulator["normalized_filtered_closure"].append(
        float(row["normalized_filtered_closure_residual"])
    )
    accumulator["normalized_mask_crosscheck"].append(
        float(
            row[
                "normalized_mask_enstrophy_loss_crosscheck_residual"
            ]
        )
    )

    advection = float(row["rk2_advection_rate"])
    viscous = float(row["rk2_viscous_rate"])
    forcing = float(row["rk2_forcing_rate"])
    rk2 = float(row["rk2_quadratic_remainder_rate"])
    mask = float(row["mask_enstrophy_change_rate"])
    nfv = advection + rk2 + mask
    observed = float(row["observed_filtered_enstrophy_rate"])

    values = {
        "advection": advection,
        "viscous": viscous,
        "forcing": forcing,
        "rk2": rk2,
        "mask": mask,
        "non_forcing_non_viscous": nfv,
        "observed": observed,
    }

    for component, value in values.items():
        accumulator["components"][component].append(value)


def sign_counts(values: Sequence[float]) -> tuple[int, int, int]:
    positive = sum(value > 0.0 for value in values)
    negative = sum(value < 0.0 for value in values)
    zero = len(values) - positive - negative
    return positive, negative, zero


def minimum_steps_for_fraction(
    values: Sequence[float],
    fraction: float,
) -> int:
    activities = sorted(
        (abs(value) * DT for value in values),
        reverse=True,
    )

    total = sum(activities)

    if total <= 0.0:
        return 0

    target = fraction * total
    cumulative = 0.0

    for index, activity in enumerate(activities, start=1):
        cumulative += activity

        if cumulative >= target:
            return index

    return len(activities)


def signed_same_direction(first: float, second: float) -> bool:
    if (
        abs(first) <= SIGN_NONZERO_FLOOR
        or abs(second) <= SIGN_NONZERO_FLOOR
    ):
        return False

    return math.copysign(1.0, first) == math.copysign(1.0, second)


def summarize_component(
    values: Sequence[float],
) -> dict[str, object]:
    array = np.asarray(values, dtype=np.float64)
    positive, negative, zero = sign_counts(values)

    return {
        "mean_signed_rate": float(np.mean(array)),
        "median_signed_rate": float(np.median(array)),
        "mean_absolute_rate": float(np.mean(np.abs(array))),
        "maximum_absolute_rate": float(np.max(np.abs(array))),
        "integrated_signed": float(DT * np.sum(array)),
        "integrated_absolute_activity": float(
            DT * np.sum(np.abs(array))
        ),
        "positive_count": positive,
        "negative_count": negative,
        "zero_count": zero,
    }


def classify_block(
    summaries: Mapping[str, Mapping[str, object]],
    components: Mapping[str, Sequence[float]],
    integrity_failure_count: int,
) -> tuple[str, dict[str, object]]:
    if integrity_failure_count != 0:
        return (
            "NUMERICAL INTEGRITY FAILURE",
            {
                "cancellation_ratio": None,
                "activity_shares": {},
                "reduction_fractions": {},
                "n90_steps": {},
                "dominance_pass": {},
            },
        )

    integrated_nfv = float(
        summaries["non_forcing_non_viscous"]["integrated_signed"]
    )

    absolute_integrated_sum = sum(
        abs(float(summaries[name]["integrated_signed"]))
        for name in ATTRIBUTION_COMPONENTS
    )

    activity_total = sum(
        float(summaries[name]["integrated_absolute_activity"])
        for name in ATTRIBUTION_COMPONENTS
    )

    cancellation_ratio = (
        abs(integrated_nfv)
        / max(absolute_integrated_sum, RESIDUAL_FLOOR)
    )

    activity_shares: dict[str, float] = {}
    reduction_fractions: dict[str, float] = {}
    n90_steps: dict[str, int] = {}
    dominance_pass: dict[str, bool] = {}

    for name in ATTRIBUTION_COMPONENTS:
        integrated = float(
            summaries[name]["integrated_signed"]
        )

        share = (
            float(
                summaries[name]["integrated_absolute_activity"]
            )
            / max(activity_total, RESIDUAL_FLOOR)
        )

        reduction = 1.0 - (
            abs(integrated_nfv - integrated)
            / max(abs(integrated_nfv), RESIDUAL_FLOOR)
        )

        n90 = minimum_steps_for_fraction(
            components[name],
            0.90,
        )

        passes = (
            share >= DOMINANCE_SHARE_LIMIT
            and signed_same_direction(
                integrated,
                integrated_nfv,
            )
            and reduction >= DOMINANCE_REDUCTION_LIMIT
            and n90 >= DOMINANCE_MIN_N90_STEPS
        )

        activity_shares[name] = share
        reduction_fractions[name] = reduction
        n90_steps[name] = n90
        dominance_pass[name] = passes

    passing = [
        name
        for name, passed in dominance_pass.items()
        if passed
    ]

    if len(passing) == 1:
        labels = {
            "advection":
                "LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION",
            "rk2":
                "LEADING LEDGER CONTRIBUTOR: RK2 REMAINDER",
            "mask":
                "LEADING LEDGER CONTRIBUTOR: MASK",
        }

        classification = labels[passing[0]]

    elif len(passing) > 1:
        classification = "MULTIPLE LEDGER CONTRIBUTORS"

    elif cancellation_ratio <= CANCELLATION_RATIO_LIMIT:
        classification = "CANCELLING LEDGER CONTRIBUTORS"

    elif sum(
        share >= MULTIPLE_SHARE_LIMIT
        for share in activity_shares.values()
    ) >= 2:
        classification = "MULTIPLE LEDGER CONTRIBUTORS"

    else:
        classification = "LEDGER ATTRIBUTION INCONCLUSIVE"

    return classification, {
        "cancellation_ratio": cancellation_ratio,
        "activity_shares": activity_shares,
        "reduction_fractions": reduction_fractions,
        "n90_steps": n90_steps,
        "dominance_pass": dominance_pass,
    }


def finalize_block(
    accumulator: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    block_id = int(accumulator["block_id"])
    observed_count = int(accumulator["step_count"])
    expected_count = EXPECTED_BLOCK_COUNTS[block_id]

    if observed_count != expected_count:
        raise IntegrityFailure(
            "time_block_count",
            f"block {block_id} contains {observed_count} steps, "
            f"expected {expected_count}",
        )

    component_summaries = {
        component: summarize_component(
            accumulator["components"][component]
        )
        for component in COMPONENTS
    }

    classification, attribution = classify_block(
        component_summaries,
        accumulator["components"],
        int(accumulator["integrity_failure_count"]),
    )

    unfiltered = np.asarray(
        accumulator["normalized_unfiltered_closure"],
        dtype=np.float64,
    )
    filtered = np.asarray(
        accumulator["normalized_filtered_closure"],
        dtype=np.float64,
    )
    mask_crosscheck = np.asarray(
        accumulator["normalized_mask_crosscheck"],
        dtype=np.float64,
    )

    row: dict[str, object] = {
        "block_id": block_id,
        "label": accumulator["label"],
        "step_count": observed_count,
        "time_start": accumulator["time_start"],
        "time_end": accumulator["time_end"],
        "classification": classification,
        "integrity_failure_count": int(
            accumulator["integrity_failure_count"]
        ),
        "median_normalized_unfiltered_closure": float(
            np.median(unfiltered)
        ),
        "maximum_normalized_unfiltered_closure": float(
            np.max(unfiltered)
        ),
        "median_normalized_filtered_closure": float(
            np.median(filtered)
        ),
        "maximum_normalized_filtered_closure": float(
            np.max(filtered)
        ),
        "median_normalized_mask_crosscheck": float(
            np.median(mask_crosscheck)
        ),
        "maximum_normalized_mask_crosscheck": float(
            np.max(mask_crosscheck)
        ),
        "integrated_non_forcing_non_viscous": float(
            component_summaries[
                "non_forcing_non_viscous"
            ]["integrated_signed"]
        ),
        "cancellation_ratio": attribution["cancellation_ratio"],
        "advection_activity_share": attribution[
            "activity_shares"
        ]["advection"],
        "rk2_activity_share": attribution[
            "activity_shares"
        ]["rk2"],
        "mask_activity_share": attribution[
            "activity_shares"
        ]["mask"],
        "advection_integrated_signed": float(
            component_summaries["advection"]["integrated_signed"]
        ),
        "rk2_integrated_signed": float(
            component_summaries["rk2"]["integrated_signed"]
        ),
        "mask_integrated_signed": float(
            component_summaries["mask"]["integrated_signed"]
        ),
        "advection_reduction_fraction": attribution[
            "reduction_fractions"
        ]["advection"],
        "rk2_reduction_fraction": attribution[
            "reduction_fractions"
        ]["rk2"],
        "mask_reduction_fraction": attribution[
            "reduction_fractions"
        ]["mask"],
        "advection_n90_steps": attribution["n90_steps"]["advection"],
        "rk2_n90_steps": attribution["n90_steps"]["rk2"],
        "mask_n90_steps": attribution["n90_steps"]["mask"],
        "advection_dominance_pass": attribution[
            "dominance_pass"
        ]["advection"],
        "rk2_dominance_pass": attribution[
            "dominance_pass"
        ]["rk2"],
        "mask_dominance_pass": attribution[
            "dominance_pass"
        ]["mask"],
    }

    for component, summary in component_summaries.items():
        for metric, value in summary.items():
            row[f"{component}_{metric}"] = value

    structured = {
        "block_id": block_id,
        "label": accumulator["label"],
        "step_count": observed_count,
        "time_start": accumulator["time_start"],
        "time_end": accumulator["time_end"],
        "classification": classification,
        "integrity_failure_count": int(
            accumulator["integrity_failure_count"]
        ),
        "closure": {
            "median_normalized_unfiltered": float(
                np.median(unfiltered)
            ),
            "maximum_normalized_unfiltered": float(
                np.max(unfiltered)
            ),
            "median_normalized_filtered": float(
                np.median(filtered)
            ),
            "maximum_normalized_filtered": float(
                np.max(filtered)
            ),
            "median_normalized_mask_crosscheck": float(
                np.median(mask_crosscheck)
            ),
            "maximum_normalized_mask_crosscheck": float(
                np.max(mask_crosscheck)
            ),
        },
        "components": component_summaries,
        "attribution": attribution,
    }

    return row, structured


# ============================================================================
# Inventory and inspection
# ============================================================================

def write_inventory(
    directory: Path,
    inventory_path: Path,
    paths: Sequence[Path],
) -> str:
    rows: list[dict[str, object]] = []

    for path in paths:
        if not path.exists():
            continue

        rows.append(
            {
                "relative_path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "inventory_note": "",
            }
        )

    rows.append(
        {
            "relative_path": inventory_path.name,
            "bytes": "",
            "sha256": "",
            "inventory_note": (
                "self-hash intentionally omitted to avoid "
                "circular self-reference"
            ),
        }
    )

    temporary = inventory_path.with_name(
        inventory_path.name + ".tmp"
    )

    with temporary.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(INVENTORY_FIELDNAMES),
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
        handle.flush()
        os.fsync(handle.fileno())

    temporary.replace(inventory_path)
    return sha256_file(inventory_path)


def inspect_runner(repo: Path) -> int:
    runner = Path(__file__).resolve()
    raw = runner.read_bytes()

    if runner.name != RUNNER_NAME:
        fail(
            f"runner filename is {runner.name!r}, "
            f"expected {RUNNER_NAME!r}"
        )

    if b"\r" in raw:
        fail("runner is not LF-only")

    source = raw.decode("utf-8", errors="strict")
    tree = ast.parse(source, filename=str(runner))
    compile(tree, str(runner), "exec", dont_inherit=True)

    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        fail("active branch is not phase4_validation")

    head = git_read(repo, "rev-parse", "HEAD")

    if head != AUTHORIZED_RUNNER_DESIGN_COMMIT:
        fail(
            f"HEAD is {head}, expected runner-design checkpoint "
            f"{AUTHORIZED_RUNNER_DESIGN_COMMIT}"
        )

    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ).splitlines()

    if status != [f"?? {runner.name}"]:
        fail(f"unexpected Git status: {status!r}")

    try:
        verify_source_identities(repo)
    except RuntimeError as error:
        fail(str(error))

    parents: dict[ast.AST, ast.AST] = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def enclosing_function(node: ast.AST) -> str | None:
        current = node

        while current in parents:
            current = parents[current]

            if isinstance(current, ast.FunctionDef):
                return current.name

        return None

    project_imports: list[tuple[str, str | None, int]] = []
    solver_run_lines: list[int] = []
    forbidden_calls: list[tuple[str, int]] = []
    call_counts = {
        "SpectralSolver": 0,
        "forcing_budget_snapshot": 0,
        "forcing_budget_interval": 0,
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""

            if (
                module.startswith("project")
                or module == "forcing_budget_diagnostic"
            ):
                project_imports.append(
                    (
                        module,
                        enclosing_function(node),
                        node.lineno,
                    )
                )

        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            if node.func.id in call_counts:
                call_counts[node.func.id] += 1

            if node.func.id in {"eval", "exec"}:
                forbidden_calls.append(
                    (node.func.id, node.lineno)
                )

        if isinstance(node.func, ast.Attribute):
            owner = node.func.value

            if (
                node.func.attr == "run"
                and isinstance(owner, ast.Name)
                and owner.id == "solver"
            ):
                solver_run_lines.append(node.lineno)

            if node.func.attr in {
                "polyfit",
                "curve_fit",
            }:
                forbidden_calls.append(
                    (node.func.attr, node.lineno)
                )

    bad_imports = [
        item
        for item in project_imports
        if item[1] != "execute_replay"
    ]

    if bad_imports:
        fail(
            "project imports are not confined to execute_replay: "
            f"{bad_imports!r}"
        )

    if solver_run_lines:
        fail(
            f"actual solver.run calls found at {solver_run_lines}"
        )

    if forbidden_calls:
        fail(
            f"forbidden dynamic or fit calls: {forbidden_calls!r}"
        )

    expected_calls = {
        "SpectralSolver": 1,
        "forcing_budget_snapshot": 3,
        "forcing_budget_interval": 1,
    }

    for name, expected in expected_calls.items():
        if call_counts[name] != expected:
            fail(
                f"expected {expected} calls to {name}, "
                f"found {call_counts[name]}"
            )

    constants: dict[str, object] = {}

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]

            if isinstance(target, ast.Name):
                try:
                    constants[target.id] = ast.literal_eval(node.value)
                except Exception:
                    pass

    expected_constants = {
        "N": 64,
        "RE": 1000,
        "DT": 0.005,
        "STEPS": 20001,
        "FINAL_PHYSICAL_TIME": 100.005,
        "HIGH_CADENCE_INTERVAL": 10,
        "ARCHIVE_MATCH_INTERVAL": 100,
        "PROGRESS_INTERVAL": 500,
        "EXPECTED_LEDGER_ROWS": 20001,
        "EXPECTED_HIGH_CADENCE_ROWS": 2001,
        "EXPECTED_FINAL_WINDOW_ROWS": 4001,
        "EXPECTED_ARCHIVE_MATCHES": 201,
        "EXPECTED_TIME_BLOCK_ROWS": 6,
        "LEDGER_CLOSURE_LIMIT": 1.0e-10,
        "MASK_CROSSCHECK_LIMIT": 1.0e-10,
        "VISCOUS_IDENTITY_LIMIT": 1.0e-10,
        "FORCING_IDENTITY_LIMIT": 1.0e-12,
        "STATE_RECONSTRUCTION_LIMIT": 1.0e-13,
        "IMAGINARY_RATIO_LIMIT": 1.0e-13,
        "DOMINANCE_SHARE_LIMIT": 0.70,
        "DOMINANCE_REDUCTION_LIMIT": 0.70,
        "DOMINANCE_MIN_N90_STEPS": 5,
        "MULTIPLE_SHARE_LIMIT": 0.20,
        "CANCELLATION_RATIO_LIMIT": 0.20,
    }

    for name, expected in expected_constants.items():
        if constants.get(name) != expected:
            fail(
                f"{name} is {constants.get(name)!r}, "
                f"expected {expected!r}"
            )

    required_functions = {
        "verify_source_identities",
        "verify_runner_commit_shape",
        "build_rms_matched_multimode_forcing",
        "load_archived_budget",
        "ledger_step",
        "high_cadence_row",
        "compare_archive_snapshot",
        "update_block_accumulator",
        "finalize_block",
        "write_inventory",
        "inspect_runner",
        "execute_replay",
        "main",
    }

    observed_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    missing = required_functions - observed_functions

    if missing:
        fail(f"required functions are missing: {sorted(missing)}")

    required_fragments = (
        "rk2_remainder = (",
        "solver.dt",
        "/ 8.0",
        "total_difference * total_difference",
        "mask_loss_spectral = float(",
        "np.sum(np.abs(discarded_hat) ** 2)",
        "observed_filtered_rate",
        "filtered_ledger_rate",
        "ARCHIVED_SOURCE_HASHES",
        "EXPECTED_FORCING_SHA256",
        "operator_ledger_per_step.csv",
        "high_cadence_budget.csv",
        "operator_ledger_time_blocks.csv",
        "operator_ledger_final_window.csv",
        "operator_ledger_summary.json",
        "LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION",
        "LEADING LEDGER CONTRIBUTOR: RK2 REMAINDER",
        "LEADING LEDGER CONTRIBUTOR: MASK",
        "MULTIPLE LEDGER CONTRIBUTORS",
        "CANCELLING LEDGER CONTRIBUTORS",
        "LEDGER ATTRIBUTION INCONCLUSIVE",
        "NUMERICAL INTEGRITY FAILURE",
        'if arguments.mode == "inspect":',
        'if arguments.mode == "run":',
    )

    for fragment in required_fragments:
        if fragment not in source:
            fail(f"required source fragment absent: {fragment}")

    print()
    print("=" * 72)
    print("STAGE B EXACT OPERATOR-LEDGER RUNNER INSPECTION: PASS")
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", sha256_bytes(raw))
    print("Runner-design commit:", AUTHORIZED_RUNNER_DESIGN_COMMIT)
    print("Exact-ledger design SHA256:", EXPECTED_EXACT_LEDGER_DESIGN_SHA256)
    print("Runner-design SHA256:", EXPECTED_RUNNER_DESIGN_SHA256)
    print("Configuration: N64, Re1000, dt0.005, steps20001")
    print("Ledger cadence: every step")
    print("High-cadence budget: every 10 steps / 0.05 time units")
    print("Expected ledger rows: 20001")
    print("Expected high-cadence rows: 2001")
    print("Expected final-window rows: 4001")
    print("Expected archived replay matches: 201")
    print("Exact RK2 remainder formula: PRESENT")
    print("Exact physical/spectral mask-loss cross-check: PRESENT")
    print("Archived replay-equivalence gate: PRESENT")
    print("Protected and archived source hashes: PASS")
    print("Spectral slope fitting present: NO")
    print("Project modules imported: NO")
    print("Solver constructed: NO")
    print("Numerical steps executed: NO")
    print("Files written: NO")
    print("Git mutations: NONE")
    print("Numerical replay authorized by inspection: NO")

    return 0


# ============================================================================
# Controlled replay
# ============================================================================

def execute_replay(repo: Path) -> int:
    runner = Path(__file__).resolve()

    execution_commit = verify_runner_commit_shape(
        repo,
        runner,
    )

    source_hashes = verify_source_identities(repo)
    archived_budget = load_archived_budget(repo)

    output_root = repo / OUTPUT_ROOT

    existing = (
        sorted(output_root.glob(f"{RUN_PREFIX}*"))
        if output_root.is_dir()
        else []
    )

    if existing:
        raise RuntimeError(
            "a Stage B replay output already exists; "
            "no rerun is allowed: "
            + ", ".join(str(path) for path in existing)
        )

    created = utc_now()
    created_utc = utc_text(created)
    stamp = created.strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{RUN_PREFIX}{stamp}_{execution_commit[:7]}"
    run_directory = output_root / run_id

    if not path_is_git_ignored(repo, run_directory):
        raise RuntimeError(
            "planned Stage B output is not Git-ignored: "
            f"{run_directory.relative_to(repo)}"
        )

    run_directory.mkdir(parents=True, exist_ok=False)

    metadata_path = run_directory / "run_metadata.json"
    ledger_path = run_directory / "operator_ledger_per_step.csv"
    high_cadence_path = run_directory / "high_cadence_budget.csv"
    block_path = run_directory / "operator_ledger_time_blocks.csv"
    final_window_path = run_directory / "operator_ledger_final_window.csv"
    summary_path = run_directory / "operator_ledger_summary.json"
    inventory_path = run_directory / "file_inventory.csv"

    ledger_writer: IncrementalCsvWriter | None = None
    high_cadence_writer: IncrementalCsvWriter | None = None
    final_window_writer: IncrementalCsvWriter | None = None

    last_completed_loop_index: int | None = None
    failed_gate: str | None = None
    ledger_rows = 0
    high_cadence_rows = 0
    final_window_rows = 0
    final_budget_snapshot: dict[str, object] | None = None
    forcing_statistics: dict[str, object] | None = None
    inventory_hash: str | None = None

    metadata: dict[str, object] = {
        "schema_id": "STAGE_B_EXACT_OPERATOR_LEDGER_METADATA_V1",
        "run_id": run_id,
        "status": "running",
        "classification": None,
        "created_utc": created_utc,
        "completed_utc": None,
        "repository": {
            "name": "Raj-Sanghera-Project",
            "branch": "phase4_validation",
            "runner_design_commit": AUTHORIZED_RUNNER_DESIGN_COMMIT,
            "execution_commit": execution_commit,
            "runner_path": runner.name,
            "runner_sha256": sha256_file(runner),
            "exact_ledger_design_path": (
                EXACT_LEDGER_DESIGN_PATH.as_posix()
            ),
            "exact_ledger_design_sha256": (
                EXPECTED_EXACT_LEDGER_DESIGN_SHA256
            ),
            "runner_design_path": RUNNER_DESIGN_PATH.as_posix(),
            "runner_design_sha256": (
                EXPECTED_RUNNER_DESIGN_SHA256
            ),
            "source_hashes": source_hashes,
        },
        "environment": {
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "operating_system": platform.platform(),
            "floating_dtype": "float64",
            "machine_epsilon": float(np.finfo(np.float64).eps),
        },
        "configuration": {
            "grid": [N, N],
            "Re": RE,
            "nu": NU,
            "dt": DT,
            "steps": STEPS,
            "final_physical_time": FINAL_PHYSICAL_TIME,
            "initial_vorticity": "exact_zero",
            "time_integrator": "external mirror of protected RK2",
            "protected_solver_run_called": False,
            "ledger_interval_steps": LEDGER_OUTPUT_INTERVAL,
            "high_cadence_interval_steps": HIGH_CADENCE_INTERVAL,
            "high_cadence_interval_time": (
                HIGH_CADENCE_INTERVAL * DT
            ),
            "archive_match_interval_steps": (
                ARCHIVE_MATCH_INTERVAL
            ),
            "progress_interval_steps": PROGRESS_INTERVAL,
            "final_window_start": FINAL_WINDOW_START,
            "final_window_end": FINAL_WINDOW_END,
        },
        "expected_counts": {
            "ledger_rows": EXPECTED_LEDGER_ROWS,
            "high_cadence_rows": EXPECTED_HIGH_CADENCE_ROWS,
            "final_window_rows": EXPECTED_FINAL_WINDOW_ROWS,
            "archive_matches": EXPECTED_ARCHIVE_MATCHES,
            "time_block_rows": EXPECTED_TIME_BLOCK_ROWS,
        },
        "integrity_tolerances": {
            "ledger_closure_limit": LEDGER_CLOSURE_LIMIT,
            "filter_bookkeeping_limit": FILTER_BOOKKEEPING_LIMIT,
            "mask_crosscheck_limit": MASK_CROSSCHECK_LIMIT,
            "viscous_identity_limit": VISCOUS_IDENTITY_LIMIT,
            "forcing_identity_limit": FORCING_IDENTITY_LIMIT,
            "state_reconstruction_limit": STATE_RECONSTRUCTION_LIMIT,
            "imaginary_ratio_limit": IMAGINARY_RATIO_LIMIT,
            "sign_tolerance_factor": SIGN_TOLERANCE_FACTOR,
            "archive_time_absolute_tolerance": (
                ARCHIVE_TIME_ABS_TOLERANCE
            ),
            "archive_forcing_rms_absolute_tolerance": (
                ARCHIVE_FORCING_RMS_ABS_TOLERANCE
            ),
            "archive_relative_tolerance": (
                ARCHIVE_RELATIVE_TOLERANCE
            ),
            "archive_absolute_floor": ARCHIVE_ABSOLUTE_FLOOR,
        },
        "attribution_thresholds": {
            "dominance_share_limit": DOMINANCE_SHARE_LIMIT,
            "dominance_reduction_limit": (
                DOMINANCE_REDUCTION_LIMIT
            ),
            "dominance_minimum_n90_steps": (
                DOMINANCE_MIN_N90_STEPS
            ),
            "multiple_share_limit": MULTIPLE_SHARE_LIMIT,
            "cancellation_ratio_limit": (
                CANCELLATION_RATIO_LIMIT
            ),
        },
        "forcing": None,
        "progress": {
            "last_completed_loop_index": None,
            "ledger_rows": 0,
            "high_cadence_rows": 0,
            "final_window_rows": 0,
        },
        "output_files": {
            "run_metadata": metadata_path.name,
            "operator_ledger_per_step": ledger_path.name,
            "high_cadence_budget": high_cadence_path.name,
            "operator_ledger_time_blocks": block_path.name,
            "operator_ledger_final_window": (
                final_window_path.name
            ),
            "operator_ledger_summary": summary_path.name,
            "file_inventory": inventory_path.name,
        },
        "claims": {
            "formal_temporal_convergence": False,
            "formal_spatial_convergence": False,
            "physical_validation": False,
            "turbulence": False,
            "cascade": False,
            "inertial_range": False,
            "k_minus_3": False,
            "method_superiority": False,
            "production_readiness": False,
            "unique_physical_causation": False,
        },
    }

    atomic_write_json(metadata_path, metadata)

    try:
        from forcing_budget_diagnostic import (
            forcing_budget_interval,
            forcing_budget_snapshot,
        )

        from project.solver.spectral_solver import SpectralSolver

        solver = SpectralSolver(
            nx=N,
            ny=N,
            Re=RE,
            run_path=run_directory,
            dt=DT,
            steps=STEPS,
        )

        if not np.array_equal(
            solver.w,
            np.zeros_like(solver.w),
        ):
            raise IntegrityFailure(
                "initial_state_zero",
                "solver did not initialize with exact zero vorticity",
            )

        if not math.isclose(
            float(solver.nu),
            NU,
            rel_tol=0.0,
            abs_tol=1.0e-15,
        ):
            raise IntegrityFailure(
                "solver_viscosity",
                f"solver viscosity is {solver.nu}, expected {NU}",
            )

        forcing, forcing_statistics = (
            build_rms_matched_multimode_forcing(solver)
        )

        forcing_hash = str(
            forcing_statistics["forcing_sha256"]
        )

        metadata["forcing"] = forcing_statistics
        atomic_write_json(metadata_path, metadata)

        ledger_writer = IncrementalCsvWriter(
            ledger_path,
            LEDGER_FIELDNAMES,
        )

        high_cadence_writer = IncrementalCsvWriter(
            high_cadence_path,
            HIGH_CADENCE_FIELDNAMES,
        )

        final_window_writer = IncrementalCsvWriter(
            final_window_path,
            LEDGER_FIELDNAMES,
        )

        block_accumulators = {
            int(block["block_id"]): new_block_accumulator(block)
            for block in TIME_BLOCKS
        }

        archive_equivalence = initialize_archive_equivalence()
        previous_high_cadence_snapshot: (
            dict[str, float | int] | None
        ) = None

        maxima = {
            "absolute_rk2_advection_rate": {
                "value": 0.0,
                "loop_index": None,
            },
            "absolute_rk2_remainder_rate": {
                "value": 0.0,
                "loop_index": None,
            },
            "absolute_mask_rate": {
                "value": 0.0,
                "loop_index": None,
            },
            "normalized_filtered_closure": {
                "value": 0.0,
                "loop_index": None,
            },
            "normalized_mask_crosscheck": {
                "value": 0.0,
                "loop_index": None,
            },
            "normalized_inverse_fft_imaginary": {
                "value": 0.0,
                "loop_index": None,
            },
        }

        for loop_index in range(STEPS):
            row, filtered = ledger_step(
                solver,
                forcing,
                forcing_hash,
                loop_index=loop_index,
                forcing_budget_snapshot=forcing_budget_snapshot,
            )

            solver.w = filtered

            ledger_writer.write(row)
            ledger_rows += 1

            physical_time = float(row["physical_time"])
            primary_block, full_block = block_ids_for_time(
                physical_time
            )

            update_block_accumulator(
                block_accumulators[primary_block],
                row,
            )

            update_block_accumulator(
                block_accumulators[full_block],
                row,
            )

            if (
                physical_time
                >= FINAL_WINDOW_START - 1.0e-12
                and physical_time
                <= FINAL_WINDOW_END + 1.0e-12
            ):
                final_window_writer.write(row)
                final_window_rows += 1

            maximum_candidates = {
                "absolute_rk2_advection_rate": abs(
                    float(row["rk2_advection_rate"])
                ),
                "absolute_rk2_remainder_rate": abs(
                    float(
                        row["rk2_quadratic_remainder_rate"]
                    )
                ),
                "absolute_mask_rate": abs(
                    float(row["mask_enstrophy_change_rate"])
                ),
                "normalized_filtered_closure": float(
                    row[
                        "normalized_filtered_closure_residual"
                    ]
                ),
                "normalized_mask_crosscheck": float(
                    row[
                        "normalized_mask_enstrophy_loss_crosscheck_residual"
                    ]
                ),
                "normalized_inverse_fft_imaginary": float(
                    row[
                        "normalized_inverse_fft_imaginary_rms"
                    ]
                ),
            }

            for name, value in maximum_candidates.items():
                if value > float(maxima[name]["value"]):
                    maxima[name]["value"] = value
                    maxima[name]["loop_index"] = loop_index

            if (
                loop_index % HIGH_CADENCE_INTERVAL == 0
                or loop_index == STEPS - 1
            ):
                observed_forcing_hash = sha256_array(forcing)

                if observed_forcing_hash != forcing_hash:
                    raise IntegrityFailure(
                        "forcing_identity",
                        "forcing SHA256 changed during replay",
                    )

                snapshot = forcing_budget_snapshot(
                    omega=solver.w,
                    forcing=forcing,
                    nu=solver.nu,
                    kx=solver.kx,
                    ky=solver.ky,
                    dt=DT,
                    loop_index=loop_index,
                )

                budget_row = high_cadence_row(
                    snapshot,
                    previous_high_cadence_snapshot,
                    forcing_hash=forcing_hash,
                    forcing_budget_interval=forcing_budget_interval,
                )

                high_cadence_writer.write(budget_row)
                high_cadence_rows += 1
                previous_high_cadence_snapshot = dict(snapshot)
                final_budget_snapshot = dict(budget_row)

                if loop_index % ARCHIVE_MATCH_INTERVAL == 0:
                    compare_archive_snapshot(
                        loop_index=loop_index,
                        replay=snapshot,
                        archived=archived_budget[loop_index],
                        state=archive_equivalence,
                    )

            if (
                loop_index % PROGRESS_INTERVAL == 0
                or loop_index == STEPS - 1
            ):
                print(
                    "progress",
                    f"t={physical_time:.3f}",
                    f"Z={float(row['z_filtered']):.6e}",
                    (
                        "Zrate="
                        f"{float(row['observed_filtered_enstrophy_rate']):.6e}"
                    ),
                    f"RA={float(row['rk2_advection_rate']):.6e}",
                    f"RV={float(row['rk2_viscous_rate']):.6e}",
                    f"RF={float(row['rk2_forcing_rate']):.6e}",
                    (
                        "RRK2="
                        f"{float(row['rk2_quadratic_remainder_rate']):.6e}"
                    ),
                    (
                        "RP="
                        f"{float(row['mask_enstrophy_change_rate']):.6e}"
                    ),
                    (
                        "closure="
                        f"{float(row['normalized_filtered_closure_residual']):.3e}"
                    ),
                )

            last_completed_loop_index = loop_index
            metadata["progress"] = {
                "last_completed_loop_index": (
                    last_completed_loop_index
                ),
                "ledger_rows": ledger_rows,
                "high_cadence_rows": high_cadence_rows,
                "final_window_rows": final_window_rows,
            }

            if loop_index % CSV_FLUSH_INTERVAL == 0:
                atomic_write_json(metadata_path, metadata)

        ledger_writer.close()
        high_cadence_writer.close()
        final_window_writer.close()

        ledger_writer = None
        high_cadence_writer = None
        final_window_writer = None

        if ledger_rows != EXPECTED_LEDGER_ROWS:
            raise IntegrityFailure(
                "ledger_row_count",
                f"ledger rows={ledger_rows}, "
                f"expected={EXPECTED_LEDGER_ROWS}",
            )

        if high_cadence_rows != EXPECTED_HIGH_CADENCE_ROWS:
            raise IntegrityFailure(
                "high_cadence_row_count",
                f"high-cadence rows={high_cadence_rows}, "
                f"expected={EXPECTED_HIGH_CADENCE_ROWS}",
            )

        if final_window_rows != EXPECTED_FINAL_WINDOW_ROWS:
            raise IntegrityFailure(
                "final_window_row_count",
                f"final-window rows={final_window_rows}, "
                f"expected={EXPECTED_FINAL_WINDOW_ROWS}",
            )

        if (
            int(archive_equivalence["match_count"])
            != EXPECTED_ARCHIVE_MATCHES
        ):
            raise IntegrityFailure(
                "archive_match_count",
                f"archive matches={archive_equivalence['match_count']}, "
                f"expected={EXPECTED_ARCHIVE_MATCHES}",
            )

        if final_budget_snapshot is None:
            raise IntegrityFailure(
                "final_budget_snapshot",
                "final budget snapshot is missing",
            )

        if int(final_budget_snapshot["completed_steps"]) != STEPS:
            raise IntegrityFailure(
                "final_completed_steps",
                "final completed-step count is incorrect",
            )

        if not math.isclose(
            float(final_budget_snapshot["physical_time"]),
            FINAL_PHYSICAL_TIME,
            rel_tol=0.0,
            abs_tol=1.0e-14,
        ):
            raise IntegrityFailure(
                "final_physical_time",
                "final physical time is incorrect",
            )

        block_rows: list[dict[str, object]] = []
        block_summaries: list[dict[str, object]] = []

        for block in TIME_BLOCKS:
            row, structured = finalize_block(
                block_accumulators[int(block["block_id"])]
            )
            block_rows.append(row)
            block_summaries.append(structured)

        temporary_block = block_path.with_name(
            block_path.name + ".tmp"
        )

        with temporary_block.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=list(TIME_BLOCK_FIELDNAMES),
                extrasaction="raise",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(block_rows)
            handle.flush()
            os.fsync(handle.fileno())

        temporary_block.replace(block_path)

        final_window_summary = next(
            item
            for item in block_summaries
            if int(item["block_id"]) == 5
        )

        full_run_summary = next(
            item
            for item in block_summaries
            if int(item["block_id"]) == 6
        )

        summary = {
            "schema_id": "STAGE_B_EXACT_OPERATOR_LEDGER_SUMMARY_V1",
            "run_id": run_id,
            "classification": final_window_summary[
                "classification"
            ],
            "created_utc": created_utc,
            "completed_utc": utc_text(),
            "repository": metadata["repository"],
            "configuration": metadata["configuration"],
            "forcing": forcing_statistics,
            "counts": {
                "ledger_rows": ledger_rows,
                "high_cadence_rows": high_cadence_rows,
                "final_window_rows": final_window_rows,
                "archive_matches": archive_equivalence[
                    "match_count"
                ],
                "time_block_rows": len(block_rows),
            },
            "replay_equivalence": archive_equivalence,
            "time_blocks": block_summaries,
            "final_window_attribution": final_window_summary,
            "full_run_attribution": full_run_summary,
            "global_maxima": maxima,
            "final_budget_snapshot": final_budget_snapshot,
            "integrity": {
                "all_per_step_gates_passed": True,
                "failed_gate_count": 0,
                "failed_gate": None,
                "last_completed_loop_index": (
                    last_completed_loop_index
                ),
            },
            "limitations": {
                "implemented_ledger_attribution_only": True,
                "unique_physical_causation": False,
                "formal_temporal_convergence": False,
                "formal_spatial_convergence": False,
                "physical_validation": False,
                "turbulence": False,
                "cascade": False,
                "inertial_range": False,
                "k_minus_3": False,
                "method_superiority": False,
                "production_readiness": False,
                "shadow_tests_included": False,
                "checkpoint_arrays_included": False,
            },
            "outputs": metadata["output_files"],
        }

        atomic_write_json(summary_path, summary)

        metadata["status"] = "completed"
        metadata["classification"] = summary["classification"]
        metadata["completed_utc"] = summary["completed_utc"]
        metadata["progress"] = {
            "last_completed_loop_index": (
                last_completed_loop_index
            ),
            "ledger_rows": ledger_rows,
            "high_cadence_rows": high_cadence_rows,
            "final_window_rows": final_window_rows,
        }

        atomic_write_json(metadata_path, metadata)

        inventory_hash = write_inventory(
            run_directory,
            inventory_path,
            (
                metadata_path,
                ledger_path,
                high_cadence_path,
                block_path,
                final_window_path,
                summary_path,
            ),
        )

        print()
        print("=" * 72)
        print("STAGE B EXACT OPERATOR-LEDGER REPLAY: COMPLETE")
        print("=" * 72)
        print("Classification:", summary["classification"])
        print("Run directory:", run_directory)
        print("Ledger rows:", ledger_rows)
        print("High-cadence budget rows:", high_cadence_rows)
        print("Final-window ledger rows:", final_window_rows)
        print(
            "Archived replay matches:",
            archive_equivalence["match_count"],
        )
        print(
            "Final-window advection activity share:",
            f"{float(final_window_summary['attribution']['activity_shares']['advection']):.12e}",
        )
        print(
            "Final-window RK2 activity share:",
            f"{float(final_window_summary['attribution']['activity_shares']['rk2']):.12e}",
        )
        print(
            "Final-window mask activity share:",
            f"{float(final_window_summary['attribution']['activity_shares']['mask']):.12e}",
        )
        print(
            "Maximum normalized filtered closure:",
            f"{float(maxima['normalized_filtered_closure']['value']):.12e}",
        )
        print(
            "Maximum normalized mask cross-check:",
            f"{float(maxima['normalized_mask_crosscheck']['value']):.12e}",
        )
        print("File inventory SHA256:", inventory_hash)
        print("Protected solver run loop called: NO")
        print("Formal claims authorized: NO")
        print("Unique physical causation authorized: NO")

        return 0

    except BaseException as error:
        if isinstance(error, IntegrityFailure):
            failed_gate = error.gate
        else:
            failed_gate = type(error).__name__

        for writer in (
            ledger_writer,
            high_cadence_writer,
            final_window_writer,
        ):
            if writer is not None:
                try:
                    writer.close()
                except Exception:
                    pass

        metadata["status"] = "failed"
        metadata["classification"] = (
            "NUMERICAL INTEGRITY FAILURE"
        )
        metadata["completed_utc"] = utc_text()
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = str(error)
        metadata["failed_gate"] = failed_gate
        metadata["progress"] = {
            "last_completed_loop_index": (
                last_completed_loop_index
            ),
            "ledger_rows": ledger_rows,
            "high_cadence_rows": high_cadence_rows,
            "final_window_rows": final_window_rows,
        }

        try:
            atomic_write_json(metadata_path, metadata)
        except Exception:
            pass

        try:
            inventory_hash = write_inventory(
                run_directory,
                inventory_path,
                (
                    metadata_path,
                    ledger_path,
                    high_cadence_path,
                    block_path,
                    final_window_path,
                    summary_path,
                ),
            )
        except Exception:
            inventory_hash = None

        print()
        print("STAGE B NUMERICAL INTEGRITY FAILURE")
        print("Failed gate:", failed_gate)
        print("Partial evidence preserved at:", run_directory)

        if inventory_hash is not None:
            print("Partial inventory SHA256:", inventory_hash)

        raise


# ============================================================================
# Command line
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the controlled Stage B exact "
            "operator-ledger replay."
        )
    )

    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help=(
            "inspect source without numerical execution, "
            "or run the single controlled replay"
        ),
    )

    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent

    if arguments.mode == "inspect":
        return inspect_runner(repo)

    if arguments.mode == "run":
        return execute_replay(repo)

    raise RuntimeError(f"unsupported mode: {arguments.mode!r}")


if __name__ == "__main__":
    raise SystemExit(main())
