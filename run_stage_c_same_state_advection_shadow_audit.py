"""
Controlled Stage C same-state advection-form shadow audit.

Usage:
    python -B run_stage_c_same_state_advection_shadow_audit.py inspect
    python -B run_stage_c_same_state_advection_shadow_audit.py run

The inspection path parses and verifies this source and all frozen repository
identities without importing project modules, constructing a solver, writing
files, or executing numerical timesteps.

The run path replays only the archived baseline centered-advection trajectory.
Seven advection operators are evaluated on the same baseline current and RK2
stage states. Shadow results never enter the accepted update and never define
alternate trajectories.

This is a local implemented-operator diagnostic. It does not establish method
superiority, formal convergence, physical validation, turbulence, a cascade,
an inertial range, a k^-3 law, production readiness, or unique physical
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
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np


# ============================================================================
# Frozen identities
# ============================================================================

RUNNER_NAME = "run_stage_c_same_state_advection_shadow_audit.py"

AUTHORIZED_DESIGN_COMMIT = (
    "362fd2382ecb12cae875f4bf8ead656f69643103"
)

STAGE_C_DESIGN_PATH = Path(
    "STAGE_C_SAME_STATE_ADVECTION_FORM_SHADOW_AUDIT_DESIGN.md"
)

EXPECTED_STAGE_C_DESIGN_SHA256 = (
    "4C14EEA8E492CC5824686C3540D9ABF96EA3413C5F4B9B9A8E1D5EDD470D7D0C"
)

EXPECTED_STAGE_C_DESIGN_BLOB = (
    "d60a4c180dfb6ed6e0fe23e977645d5ec5e2bf02"
)

STAGE_B_EVIDENCE_COMMIT = (
    "a5c200b25b17a9cc4ce709dae3695ceca8e63aba"
)

STAGE_B_EXECUTION_COMMIT = (
    "5c464c21f61e917f26e00c73c5ec691fadc2bed9"
)

STAGE_B_RUNNER_PATH = Path(
    "run_stage_b_exact_operator_ledger_replay.py"
)

EXPECTED_STAGE_B_RUNNER_SHA256 = (
    "970AE47D4DF69819FA6D831557FC2679D843B860D901CF367361A3A34126E246"
)

STAGE_B_REPORT_PATH = Path(
    "STAGE_B_EXACT_OPERATOR_LEDGER_EVIDENCE_REPORT.md"
)

EXPECTED_STAGE_B_REPORT_SHA256 = (
    "5419765B72A757A4C048761CDBC55B1AAD8ED2A0414E3D9E79CC118A64D40DE4"
)

SPECTRAL_SOLVER_PATH = (
    Path("project") / "solver" / "spectral_solver.py"
)

EXPECTED_SPECTRAL_SOLVER_SHA256 = (
    "1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1"
)

ADVECTION_OPERATORS_PATH = (
    Path("project") / "solver" / "advection_operators.py"
)

EXPECTED_ADVECTION_OPERATORS_BLOB = (
    "849b3d5c95c955a7db73313d8680c942fd32c571"
)

SELECTABLE_SOLVER_PATH = (
    Path("project") / "solver" / "selectable_advection_solver.py"
)

EXPECTED_SELECTABLE_SOLVER_BLOB = (
    "cc3b757e327a5b1a0b6cea2287c672adebd77c15"
)

FORCING_BUDGET_DIAGNOSTIC_PATH = Path(
    "forcing_budget_diagnostic.py"
)

EXPECTED_FORCING_BUDGET_DIAGNOSTIC_SHA256 = (
    "A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B"
)

STAGE_B_EVIDENCE_DIRECTORY = (
    Path("experiments")
    / "forcing_budget_stage_b_ledger"
    / "stage_b_exact_operator_ledger_20260720T063420Z_5c464c2"
)

STAGE_B_EVIDENCE_HASHES = {
    "run_metadata.json":
        "08FF6613861561E0A508650946DF82CC3B15AB4A8A72AAD683C53C34B63B5538",
    "operator_ledger_per_step.csv":
        "5EABDFB33B932089910B61C119A223EED83D4EF9247593C3B02DA68B1D74B115",
    "high_cadence_budget.csv":
        "BC05B327A5728B2F6C3DE876F73EAE3F5067F689C377A261EF94C3A91AFC98D9",
    "operator_ledger_time_blocks.csv":
        "3D0A289FF0730AE2AE107711D3F7EBDE93E81151A6524A2ED4EC6B69A64280FB",
    "operator_ledger_final_window.csv":
        "ADA03C5BE2B65E6CB09CD92C634300B8B518A499C3282A2E8DD1DB4C73022E61",
    "operator_ledger_summary.json":
        "A3A0633401B071774E72188E6574EFB2A1C92D33C1502E778EAF68CA6FAA9600",
    "file_inventory.csv":
        "A29D6D1E774E96D6C197B05C7124388EC5AE8A962DACA7B5938A92AAAB07F2C9",
}

LONG_ARCHIVE_DIRECTORY = (
    Path("experiments")
    / "forcing_budget_stationarity"
    / "forcing_budget_stationarity_20260719T083403Z_9a9f2e0"
)

LONG_ARCHIVE_HASHES = {
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

EXPECTED_STAGE_B_FINAL_WINDOW_ADVECTION_INTEGRAL = (
    0.0006482912173695466
)

EXPECTED_STAGE_B_FULL_RUN_ADVECTION_INTEGRAL = (
    0.0015368528716236765
)


# ============================================================================
# Frozen numerical configuration and thresholds
# ============================================================================

N = 64
RE = 1000
NU = 1.0 / RE
DT = 0.005
STEPS = 20001
FINAL_PHYSICAL_TIME = 100.005

EXPECTED_STATE_REFERENCE_ROWS = 20001
EXPECTED_SHADOW_ROWS = 140007
EXPECTED_TIME_BLOCK_ROWS = 42
EXPECTED_ARCHIVE_MATCHES = 201

ARCHIVE_MATCH_INTERVAL = 100
PROGRESS_INTERVAL = 500
CSV_FLUSH_INTERVAL = 250

FORCING_TARGET_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14

BASELINE_ARCHIVE_RELATIVE_TOLERANCE = 1.0e-11
BASELINE_ARCHIVE_ABSOLUTE_FLOOR = 1.0e-14
BASELINE_HELPER_NORMALIZED_TOLERANCE = 1.0e-15
SHADOW_STATE_HASH_MUTATION_LIMIT = 0
CENTERED_FORM_IDENTITY_LIMIT = 1.0e-12
SKEW_IDENTITY_LIMIT = 1.0e-15
PSEUDO_PROJECTION_IDENTITY_LIMIT = 1.0e-12
ARAKAWA_IDENTITY_LIMIT = 1.0e-12
TRANSPORT_RHS_SIGN_LIMIT = 1.0e-14
SPECTRAL_DIVERGENCE_LIMIT = 1.0e-12
IMAGINARY_RATIO_LIMIT = 1.0e-13

NEAR_NEUTRAL_ACTIVITY_LIMIT = 0.10
NEAR_NEUTRAL_SIGNED_LIMIT = 0.10
NEAR_NEUTRAL_MAXIMUM_LIMIT = 0.25
PERSISTENCE_ACTIVITY_LIMIT = 0.50
PERSISTENCE_SIGNED_LIMIT = 0.50
PERSISTENCE_MAXIMUM_LIMIT = 0.25
MINIMUM_N90_STEPS = 5

RESIDUAL_FLOOR = 1.0e-30
SIGN_NONZERO_FLOOR = 1.0e-30

SENTINEL_LOOP_INDICES = (
    0,
    4000,
    8000,
    12000,
    16000,
    20000,
)

OUTPUT_ROOT = (
    Path("experiments")
    / "advection_form_shadow_audit"
)

RUN_PREFIX = "stage_c_same_state_advection_shadow_"

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
        "expected_steps": 4001,
    },
    {
        "block_id": 2,
        "label": "20.005 < t <= 40.005",
        "lower": 20.005,
        "upper": 40.005,
        "lower_inclusive": False,
        "expected_steps": 4000,
    },
    {
        "block_id": 3,
        "label": "40.005 < t <= 60.005",
        "lower": 40.005,
        "upper": 60.005,
        "lower_inclusive": False,
        "expected_steps": 4000,
    },
    {
        "block_id": 4,
        "label": "60.005 < t <= 80.005",
        "lower": 60.005,
        "upper": 80.005,
        "lower_inclusive": False,
        "expected_steps": 4000,
    },
    {
        "block_id": 5,
        "label": "80.005 < t <= 100.005",
        "lower": 80.005,
        "upper": 100.005,
        "lower_inclusive": False,
        "expected_steps": 4000,
    },
    {
        "block_id": 6,
        "label": "full run: 0.005 <= t <= 100.005",
        "lower": 0.005,
        "upper": 100.005,
        "lower_inclusive": True,
        "expected_steps": 20001,
    },
)

OPERATOR_REGISTRY = (
    {
        "operator_id": "BASE_FD_ADVECTIVE_V1",
        "operator_family": "BASELINE",
        "classification_role": "baseline",
        "primary_alternate": False,
    },
    {
        "operator_id": "SHADOW_FD_ADVECTIVE_PROJECTED_V1",
        "operator_family": "CENTERED_PROJECTED_MECHANISM",
        "classification_role": "mechanism_check",
        "primary_alternate": False,
    },
    {
        "operator_id": "SHADOW_FD_CONSERVATIVE_V1",
        "operator_family": "CENTERED_ALGEBRAIC",
        "classification_role": "primary_alternate",
        "primary_alternate": True,
    },
    {
        "operator_id": "SHADOW_FD_SKEW_V1",
        "operator_family": "CENTERED_ALGEBRAIC",
        "classification_role": "primary_alternate",
        "primary_alternate": True,
    },
    {
        "operator_id": "SHADOW_PS_ADVECTIVE_RAW_V1",
        "operator_family": "PSEUDO_SPECTRAL",
        "classification_role": "primary_alternate",
        "primary_alternate": True,
    },
    {
        "operator_id": "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
        "operator_family": "PSEUDO_SPECTRAL",
        "classification_role": "primary_alternate",
        "primary_alternate": True,
    },
    {
        "operator_id": "SHADOW_ARAKAWA_V1",
        "operator_family": "ARAKAWA",
        "classification_role": "primary_alternate",
        "primary_alternate": True,
    },
)

OPERATOR_IDS = tuple(
    item["operator_id"]
    for item in OPERATOR_REGISTRY
)

PRIMARY_ALTERNATE_IDS = tuple(
    item["operator_id"]
    for item in OPERATOR_REGISTRY
    if item["primary_alternate"]
)

PRIMARY_FAMILIES = (
    "CENTERED_ALGEBRAIC",
    "PSEUDO_SPECTRAL",
    "ARAKAWA",
)

STAGE_STATE_POLICY = (
    "baseline_current_and_baseline_rk2_stage_only"
)


# ============================================================================
# Output schemas
# ============================================================================

STATE_REFERENCE_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "forcing_sha256",
    "omega_current_sha256",
    "omega_stage_sha256",
    "omega_filtered_sha256",
    "z_current",
    "z_stage",
    "z_filtered",
    "baseline_stage1_work_replay",
    "baseline_stage1_work_archived",
    "baseline_stage1_work_difference",
    "baseline_stage2_work_replay",
    "baseline_stage2_work_archived",
    "baseline_stage2_work_difference",
    "baseline_rk2_work_replay",
    "baseline_rk2_work_archived",
    "baseline_rk2_work_difference",
    "baseline_scalar_equivalence_pass",
    "stage1_baseline_helper_checked",
    "stage1_baseline_helper_exact_equal",
    "stage1_baseline_helper_normalized_difference",
    "stage2_baseline_helper_checked",
    "stage2_baseline_helper_exact_equal",
    "stage2_baseline_helper_normalized_difference",
    "stage1_centered_velocity_divergence_rms",
    "stage1_centered_velocity_divergence_max_abs",
    "stage1_centered_product_rule_defect_rms",
    "stage1_centered_product_rule_defect_max_abs",
    "stage1_centered_form_identity_residual_rms",
    "stage1_normalized_centered_form_identity_residual",
    "stage1_centered_work_identity_residual",
    "stage1_centered_divergence_work_term",
    "stage1_centered_product_rule_work_term",
    "stage1_spectral_velocity_divergence_rms",
    "stage1_spectral_velocity_divergence_max_abs",
    "stage1_normalized_spectral_velocity_divergence",
    "stage1_pseudo_product_removed_rms",
    "stage1_pseudo_product_removed_max_abs",
    "stage1_pseudo_product_removed_work",
    "stage1_pseudo_projection_fractional_work_reduction",
    "stage1_pseudo_raw_spectral_fraction_outside_mask",
    "stage1_arakawa_sign_identity_residual",
    "stage1_arakawa_secondary_energy_work",
    "stage1_maximum_imaginary_ratio",
    "stage2_centered_velocity_divergence_rms",
    "stage2_centered_velocity_divergence_max_abs",
    "stage2_centered_product_rule_defect_rms",
    "stage2_centered_product_rule_defect_max_abs",
    "stage2_centered_form_identity_residual_rms",
    "stage2_normalized_centered_form_identity_residual",
    "stage2_centered_work_identity_residual",
    "stage2_centered_divergence_work_term",
    "stage2_centered_product_rule_work_term",
    "stage2_spectral_velocity_divergence_rms",
    "stage2_spectral_velocity_divergence_max_abs",
    "stage2_normalized_spectral_velocity_divergence",
    "stage2_pseudo_product_removed_rms",
    "stage2_pseudo_product_removed_max_abs",
    "stage2_pseudo_product_removed_work",
    "stage2_pseudo_projection_fractional_work_reduction",
    "stage2_pseudo_raw_spectral_fraction_outside_mask",
    "stage2_arakawa_sign_identity_residual",
    "stage2_arakawa_secondary_energy_work",
    "stage2_maximum_imaginary_ratio",
    "sentinel_order_invariance_checked",
    "sentinel_order_invariance_pass",
    "all_shadow_state_hashes_unchanged",
    "all_shadow_arrays_finite",
    "all_integrity_gates_pass",
)

SHADOW_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "operator_id",
    "operator_family",
    "classification_role",
    "stage_state_policy",
    "stage1_transport_work",
    "stage1_rhs_work",
    "stage1_rhs_rms",
    "stage1_rhs_max_abs",
    "stage1_work_alignment",
    "stage1_difference_from_baseline_rms",
    "stage1_normalized_difference_from_baseline",
    "stage1_cosine_similarity_with_baseline",
    "stage1_rhs_mean",
    "stage2_transport_work",
    "stage2_rhs_work",
    "stage2_rhs_rms",
    "stage2_rhs_max_abs",
    "stage2_work_alignment",
    "stage2_difference_from_baseline_rms",
    "stage2_normalized_difference_from_baseline",
    "stage2_cosine_similarity_with_baseline",
    "stage2_rhs_mean",
    "stage_weighted_rhs_work",
    "difference_from_baseline_stage_weighted_work",
    "ratio_to_baseline_stage_weighted_work",
    "absolute_ratio_to_baseline_stage_weighted_work",
    "sign_agreement_with_baseline",
    "input_state_unchanged",
    "operator_output_finite",
    "transport_rhs_sign_identity_residual",
    "operator_specific_identity_residual",
    "operator_integrity_pass",
)

TIME_BLOCK_FIELDNAMES = (
    "block_id",
    "block_label",
    "operator_id",
    "operator_family",
    "classification_role",
    "step_count",
    "integrated_signed_work",
    "integrated_absolute_activity",
    "mean_signed_rate",
    "median_signed_rate",
    "mean_absolute_rate",
    "maximum_absolute_rate",
    "positive_count",
    "negative_count",
    "zero_count",
    "sign_agreement_fraction_with_baseline",
    "n90_steps",
    "absolute_activity_ratio_to_baseline",
    "signed_integral_magnitude_ratio_to_baseline",
    "maximum_rate_ratio_to_baseline",
    "signed_integral_ratio_to_baseline",
    "near_neutral_pass",
    "persistence_pass",
    "integrity_failure_count",
)

INVENTORY_FIELDNAMES = (
    "relative_path",
    "bytes",
    "sha256",
    "inventory_note",
)

OUTPUT_FILENAMES = (
    "run_metadata.json",
    "shadow_state_reference.csv",
    "shadow_advection_per_step.csv",
    "shadow_advection_time_blocks.csv",
    "shadow_advection_summary.json",
    "STAGE_C_SAME_STATE_ADVECTION_FORM_SHADOW_AUDIT_REPORT.md",
    "file_inventory.csv",
)


# ============================================================================
# Generic utilities
# ============================================================================

class IntegrityFailure(RuntimeError):
    def __init__(
        self,
        gate: str,
        message: str,
        *,
        operator_id: str | None = None,
        stage: str | None = None,
    ) -> None:
        super().__init__(message)
        self.gate = gate
        self.operator_id = operator_id
        self.stage = stage


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
        git_process(repo, *args, text=False).stdout
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


def max_abs(value: object) -> float:
    return float(np.max(np.abs(np.asarray(value))))


def enstrophy(value: object) -> float:
    array = np.asarray(value, dtype=np.float64)
    return 0.5 * float(np.mean(array * array))


def mean_product(first: object, second: object) -> float:
    return float(
        np.mean(
            np.asarray(first, dtype=np.float64)
            * np.asarray(second, dtype=np.float64)
        )
    )


def cosine_similarity(first: object, second: object) -> float:
    first_array = np.asarray(first, dtype=np.float64).ravel()
    second_array = np.asarray(second, dtype=np.float64).ravel()
    denominator = float(
        np.linalg.norm(first_array)
        * np.linalg.norm(second_array)
    )

    if denominator <= RESIDUAL_FLOOR:
        return 1.0 if np.array_equal(first_array, second_array) else 0.0

    return float(np.dot(first_array, second_array) / denominator)


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


def normalized_scalar_residual(
    value: float,
    scale_values: Sequence[float],
) -> float:
    scale = max(
        *(abs(float(item)) for item in scale_values),
        RESIDUAL_FLOOR,
    )
    return abs(float(value)) / scale


def archived_scalar_comparison(
    observed: float,
    archived: float,
) -> tuple[float, float, bool]:
    absolute_difference = abs(observed - archived)
    relative_difference = absolute_difference / max(
        abs(archived),
        BASELINE_ARCHIVE_ABSOLUTE_FLOOR,
    )
    passed = (
        absolute_difference <= BASELINE_ARCHIVE_ABSOLUTE_FLOOR
        or relative_difference <= BASELINE_ARCHIVE_RELATIVE_TOLERANCE
    )
    return absolute_difference, relative_difference, passed


def all_numeric_values_finite(row: Mapping[str, object]) -> bool:
    for value in row.values():
        if value is None or isinstance(value, (str, bool)):
            continue

        if isinstance(value, (int, float, np.integer, np.floating)):
            if not math.isfinite(float(value)):
                return False

    return True


def assert_unique_headers(
    name: str,
    fieldnames: Sequence[str],
) -> None:
    observed = tuple(fieldnames)

    if len(observed) != len(set(observed)):
        duplicates = sorted(
            item
            for item in set(observed)
            if observed.count(item) > 1
        )
        raise RuntimeError(
            f"duplicate headers in {name}: {duplicates}"
        )


def assert_all_output_headers_unique() -> None:
    assert_unique_headers(
        "shadow_state_reference.csv",
        STATE_REFERENCE_FIELDNAMES,
    )
    assert_unique_headers(
        "shadow_advection_per_step.csv",
        SHADOW_FIELDNAMES,
    )
    assert_unique_headers(
        "shadow_advection_time_blocks.csv",
        TIME_BLOCK_FIELDNAMES,
    )
    assert_unique_headers(
        "file_inventory.csv",
        INVENTORY_FIELDNAMES,
    )


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
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        assert_unique_headers(path.name, fieldnames)
        return list(reader)


class IncrementalCsvWriter:
    def __init__(
        self,
        path: Path,
        fieldnames: Sequence[str],
        *,
        flush_interval: int = CSV_FLUSH_INTERVAL,
    ) -> None:
        assert_unique_headers(path.name, fieldnames)
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
        observed_keys = set(row)
        expected_keys = set(self.fieldnames)

        if observed_keys != expected_keys:
            raise RuntimeError(
                f"CSV row schema mismatch for {self.path.name}: "
                f"missing={sorted(expected_keys - observed_keys)}, "
                f"extra={sorted(observed_keys - expected_keys)}"
            )

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
# Repository and source gates
# ============================================================================

def verify_file_hash(
    repo: Path,
    relative_path: Path,
    expected_sha256: str,
) -> str:
    path = repo / relative_path

    if not path.is_file():
        raise RuntimeError(f"required file is missing: {relative_path.as_posix()}")

    observed = sha256_file(path)

    if observed != expected_sha256:
        raise RuntimeError(
            f"SHA256 mismatch for {relative_path.as_posix()}: "
            f"observed={observed}, expected={expected_sha256}"
        )

    return observed


def verify_git_blob(
    repo: Path,
    relative_path: Path,
    expected_blob: str,
) -> str:
    relative = relative_path.as_posix()
    working_blob = git_read(
        repo,
        "hash-object",
        f"--path={relative}",
        "--",
        relative,
    )
    committed_blob = git_read(repo, "rev-parse", f"HEAD:{relative}")

    if working_blob != expected_blob:
        raise RuntimeError(
            f"working-tree Git blob mismatch for {relative}: "
            f"observed={working_blob}, expected={expected_blob}"
        )

    if committed_blob != expected_blob:
        raise RuntimeError(
            f"committed Git blob mismatch for {relative}: "
            f"observed={committed_blob}, expected={expected_blob}"
        )

    return working_blob


def verify_inventory(
    directory: Path,
    expected_hashes: Mapping[str, str],
) -> None:
    inventory_path = directory / "file_inventory.csv"

    if not inventory_path.is_file():
        raise RuntimeError(
            f"inventory is missing: {inventory_path}"
        )

    with inventory_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    by_name = {
        str(row["relative_path"]): row
        for row in rows
    }

    for name, expected_hash in expected_hashes.items():
        path = directory / name

        if not path.is_file():
            raise RuntimeError(
                f"archived source is missing: {path}"
            )

        observed_hash = sha256_file(path)

        if observed_hash != expected_hash:
            raise RuntimeError(
                f"archived source SHA256 mismatch for {path}: "
                f"observed={observed_hash}, expected={expected_hash}"
            )

        if name == "file_inventory.csv":
            continue

        row = by_name.get(name)

        if row is None:
            raise RuntimeError(
                f"inventory entry is missing for {path}"
            )

        recorded_hash = str(row.get("sha256", "")).strip().upper()
        recorded_bytes = int(str(row.get("bytes", "0")).strip())

        if recorded_hash != expected_hash:
            raise RuntimeError(
                f"inventory-recorded SHA256 mismatch for {path}"
            )

        if recorded_bytes != path.stat().st_size:
            raise RuntimeError(
                f"inventory-recorded byte count mismatch for {path}"
            )


def verify_source_identities(repo: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}

    hashes["stage_c_design"] = verify_file_hash(
        repo,
        STAGE_C_DESIGN_PATH,
        EXPECTED_STAGE_C_DESIGN_SHA256,
    )

    verify_git_blob(
        repo,
        STAGE_C_DESIGN_PATH,
        EXPECTED_STAGE_C_DESIGN_BLOB,
    )

    hashes["stage_b_runner"] = verify_file_hash(
        repo,
        STAGE_B_RUNNER_PATH,
        EXPECTED_STAGE_B_RUNNER_SHA256,
    )

    hashes["stage_b_report"] = verify_file_hash(
        repo,
        STAGE_B_REPORT_PATH,
        EXPECTED_STAGE_B_REPORT_SHA256,
    )

    hashes["spectral_solver"] = verify_file_hash(
        repo,
        SPECTRAL_SOLVER_PATH,
        EXPECTED_SPECTRAL_SOLVER_SHA256,
    )

    hashes["advection_operators_blob"] = verify_git_blob(
        repo,
        ADVECTION_OPERATORS_PATH,
        EXPECTED_ADVECTION_OPERATORS_BLOB,
    )

    hashes["selectable_solver_blob"] = verify_git_blob(
        repo,
        SELECTABLE_SOLVER_PATH,
        EXPECTED_SELECTABLE_SOLVER_BLOB,
    )

    hashes["forcing_budget_diagnostic"] = verify_file_hash(
        repo,
        FORCING_BUDGET_DIAGNOSTIC_PATH,
        EXPECTED_FORCING_BUDGET_DIAGNOSTIC_SHA256,
    )

    verify_inventory(
        repo / STAGE_B_EVIDENCE_DIRECTORY,
        STAGE_B_EVIDENCE_HASHES,
    )

    verify_inventory(
        repo / LONG_ARCHIVE_DIRECTORY,
        LONG_ARCHIVE_HASHES,
    )

    for name, value in STAGE_B_EVIDENCE_HASHES.items():
        hashes[f"stage_b/{name}"] = value

    for name, value in LONG_ARCHIVE_HASHES.items():
        hashes[f"long_archive/{name}"] = value

    return hashes


def verify_inspection_repository_state(
    repo: Path,
    runner: Path,
) -> None:
    branch = git_read(repo, "branch", "--show-current")

    if branch != "phase4_validation":
        raise RuntimeError(
            f"active branch is {branch!r}, expected 'phase4_validation'"
        )

    head = git_read(repo, "rev-parse", "HEAD")

    if head != AUTHORIZED_DESIGN_COMMIT:
        raise RuntimeError(
            f"HEAD is {head}, expected Stage C design checkpoint "
            f"{AUTHORIZED_DESIGN_COMMIT}"
        )

    status_lines = [
        line
        for line in git_read(
            repo,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ).splitlines()
        if line
    ]

    expected = [f"?? {runner.name}"]

    if status_lines != expected:
        raise RuntimeError(
            "inspection requires exactly one untracked runner; "
            f"observed={status_lines!r}"
        )


def verify_runner_commit_shape(
    repo: Path,
    runner: Path,
) -> str:
    branch = git_read(repo, "branch", "--show-current")

    if branch != "phase4_validation":
        raise RuntimeError(
            f"active branch is {branch!r}, expected 'phase4_validation'"
        )

    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )

    if status:
        raise RuntimeError(
            f"working tree is not clean: {status!r}"
        )

    head = git_read(repo, "rev-parse", "HEAD")
    parent = git_read(repo, "rev-parse", "HEAD^")

    if parent != AUTHORIZED_DESIGN_COMMIT:
        raise RuntimeError(
            f"runner commit parent is {parent}, expected "
            f"{AUTHORIZED_DESIGN_COMMIT}"
        )

    changed = [
        line
        for line in git_read(
            repo,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
        ).splitlines()
        if line
    ]

    if changed != [runner.name]:
        raise RuntimeError(
            "runner commit must change exactly one file; "
            f"observed={changed!r}"
        )

    committed_bytes = git_bytes(
        repo,
        "show",
        f"HEAD:{runner.name}",
    )

    working_bytes = runner.read_bytes()

    if committed_bytes != working_bytes:
        raise RuntimeError(
            "working runner bytes differ from committed runner bytes"
        )

    remote_head = git_read(
        repo,
        "rev-parse",
        "origin/phase4_validation",
    )

    if remote_head != head:
        raise RuntimeError(
            f"origin/phase4_validation is {remote_head}, expected {head}"
        )

    return head


# ============================================================================
# Frozen forcing and archived references
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

    raw = np.asarray(raw, dtype=np.float64)
    raw = raw - np.mean(raw)
    base_rms = field_rms(base)
    raw_rms = field_rms(raw)

    if raw_rms <= 0.0:
        raise IntegrityFailure(
            "forcing_raw_rms",
            "raw multimode forcing has zero RMS",
        )

    coefficient = base_rms / raw_rms
    forcing = np.ascontiguousarray(
        coefficient * raw,
        dtype=np.float64,
    )

    forcing_rms = field_rms(forcing)
    forcing_hash = sha256_array(forcing)

    if not math.isclose(
        forcing_rms,
        FORCING_TARGET_RMS,
        rel_tol=0.0,
        abs_tol=FORCING_RMS_TOLERANCE,
    ):
        raise IntegrityFailure(
            "forcing_rms",
            f"forcing RMS={forcing_rms}, expected={FORCING_TARGET_RMS}",
        )

    if forcing_hash != EXPECTED_FORCING_SHA256:
        raise IntegrityFailure(
            "forcing_sha256",
            f"forcing SHA256={forcing_hash}, "
            f"expected={EXPECTED_FORCING_SHA256}",
        )

    if forcing.shape != (N, N):
        raise IntegrityFailure(
            "forcing_shape",
            f"forcing shape={forcing.shape}, expected={(N, N)}",
        )

    if not np.isfinite(forcing).all():
        raise IntegrityFailure(
            "forcing_finite",
            "forcing contains a nonfinite value",
        )

    forcing.setflags(write=False)

    statistics = {
        "forcing_sha256": forcing_hash,
        "forcing_terms": list(FORCING_TERMS),
        "target_rms": FORCING_TARGET_RMS,
        "base_single_mode_rms": base_rms,
        "raw_rms": raw_rms,
        "normalization_coefficient": coefficient,
        "normalized_rms": forcing_rms,
        "mean": float(np.mean(forcing)),
        "maximum_absolute_value": max_abs(forcing),
        "shape": list(forcing.shape),
        "dtype": str(forcing.dtype),
        "finite": True,
        "real": bool(np.isrealobj(forcing)),
        "writeable": bool(forcing.flags.writeable),
    }

    return forcing, statistics


def load_archived_budget(
    repo: Path,
) -> dict[int, dict[str, str]]:
    path = repo / LONG_ARCHIVE_DIRECTORY / "forcing_budget.csv"
    rows = read_csv_rows(path)
    result: dict[int, dict[str, str]] = {}

    for row in rows:
        loop_index = int(row["loop_index"])

        if loop_index in result:
            raise RuntimeError(
                f"duplicate archived budget loop index: {loop_index}"
            )

        result[loop_index] = row

    expected = set(range(0, STEPS, ARCHIVE_MATCH_INTERVAL))

    if set(result) != expected:
        missing = sorted(expected - set(result))
        extra = sorted(set(result) - expected)
        raise RuntimeError(
            f"archived budget index set mismatch; "
            f"missing={missing[:10]}, extra={extra[:10]}"
        )

    return result


def load_stage_b_summary(repo: Path) -> dict[str, object]:
    summary = read_json(
        repo
        / STAGE_B_EVIDENCE_DIRECTORY
        / "operator_ledger_summary.json"
    )

    if summary.get("classification") != (
        "LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION"
    ):
        raise RuntimeError(
            "Stage B summary classification is not the frozen reference"
        )

    integrity = summary.get("integrity", {})

    if not bool(integrity.get("all_per_step_gates_passed")):
        raise RuntimeError(
            "Stage B summary does not report all per-step gates passed"
        )

    replay = summary.get("replay_equivalence", {})

    if (
        not bool(replay.get("all_matches_pass"))
        or int(replay.get("match_count", -1)) != EXPECTED_ARCHIVE_MATCHES
    ):
        raise RuntimeError(
            "Stage B summary replay-equivalence reference is invalid"
        )

    return summary


def open_stage_b_ledger(
    repo: Path,
) -> tuple[object, csv.DictReader]:
    path = (
        repo
        / STAGE_B_EVIDENCE_DIRECTORY
        / "operator_ledger_per_step.csv"
    )

    handle = path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    )
    reader = csv.DictReader(handle)
    assert_unique_headers(
        path.name,
        tuple(reader.fieldnames or ()),
    )
    return handle, reader


# ============================================================================
# Baseline numerical mirror
# ============================================================================

def centered_gradients(
    field: object,
    dx: float,
) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(field, dtype=np.float64)
    x_gradient = (
        np.roll(array, -1, axis=1)
        - np.roll(array, 1, axis=1)
    ) / (2.0 * dx)
    y_gradient = (
        np.roll(array, -1, axis=0)
        - np.roll(array, 1, axis=0)
    ) / (2.0 * dx)
    return x_gradient, y_gradient


def spectral_gradients_with_imaginary(
    field: object,
    kx: np.ndarray,
    ky: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    array = np.asarray(field, dtype=np.float64)
    field_hat = np.fft.fft2(array)
    x_complex = np.fft.ifft2(1j * kx * field_hat)
    y_complex = np.fft.ifft2(1j * ky * field_hat)
    real_scale = max(
        field_rms(x_complex.real),
        field_rms(y_complex.real),
        RESIDUAL_FLOOR,
    )
    imaginary_ratio = max(
        field_rms(x_complex.imag),
        field_rms(y_complex.imag),
    ) / real_scale
    return x_complex.real, y_complex.real, imaginary_ratio


def project_field_with_imaginary(
    field: object,
    mask: np.ndarray,
) -> tuple[np.ndarray, float]:
    field_hat = np.fft.fft2(np.asarray(field, dtype=np.float64))
    projected_complex = np.fft.ifft2(field_hat * mask)
    imaginary_ratio = field_rms(projected_complex.imag) / max(
        field_rms(projected_complex.real),
        RESIDUAL_FLOOR,
    )
    return projected_complex.real, imaginary_ratio


def spectral_fraction_outside_mask(
    field: object,
    mask: np.ndarray,
) -> float:
    field_hat = np.fft.fft2(np.asarray(field, dtype=np.float64))
    total = float(np.sum(np.abs(field_hat) ** 2))
    outside = float(np.sum(np.abs(field_hat[~mask]) ** 2))
    return outside / max(total, RESIDUAL_FLOOR)


def baseline_step(
    solver: object,
    baseline_omega: np.ndarray,
    forcing: np.ndarray,
    *,
    loop_index: int,
) -> dict[str, object]:
    current = np.asarray(baseline_omega, dtype=np.float64)

    if current.shape != (N, N):
        raise IntegrityFailure(
            "baseline_state_shape",
            f"baseline state shape={current.shape}, expected={(N, N)}",
        )

    if not np.isfinite(current).all():
        raise IntegrityFailure(
            "baseline_current_finite",
            "baseline current state contains a nonfinite value",
        )

    psi_1 = solver.streamfunction(current)
    u_1, v_1 = solver.velocity(psi_1)
    omega_x_1, omega_y_1 = centered_gradients(current, solver.dx)
    transport_1 = u_1 * omega_x_1 + v_1 * omega_y_1
    advection_1 = -transport_1
    viscous_1 = solver.laplacian_spectral(current)
    total_1 = advection_1 + viscous_1 + forcing
    stage = current + solver.dt * total_1

    psi_2 = solver.streamfunction(stage)
    u_2, v_2 = solver.velocity(psi_2)
    omega_x_2, omega_y_2 = centered_gradients(stage, solver.dx)
    transport_2 = u_2 * omega_x_2 + v_2 * omega_y_2
    advection_2 = -transport_2
    viscous_2 = solver.laplacian_spectral(stage)
    total_2 = advection_2 + viscous_2 + forcing

    unfiltered = (
        current
        + 0.5 * solver.dt * (total_1 + total_2)
    )
    unfiltered_hat = np.fft.fft2(unfiltered)
    filtered_complex = np.fft.ifft2(
        unfiltered_hat * solver.deal
    )
    filtered = filtered_complex.real

    if not (
        np.isfinite(stage).all()
        and np.isfinite(unfiltered).all()
        and np.isfinite(filtered).all()
    ):
        raise IntegrityFailure(
            "baseline_state_finite",
            "baseline stage, unfiltered, or accepted state is nonfinite",
        )

    z_current = enstrophy(current)
    z_stage = enstrophy(stage)
    z_unfiltered = enstrophy(unfiltered)
    z_filtered = enstrophy(filtered)

    stage1_advection_work = mean_product(current, advection_1)
    stage2_advection_work = mean_product(stage, advection_2)
    stage1_viscous_work = mean_product(current, viscous_1)
    stage2_viscous_work = mean_product(stage, viscous_2)
    stage1_forcing_work = mean_product(current, forcing)
    stage2_forcing_work = mean_product(stage, forcing)

    rk2_advection = 0.5 * (
        stage1_advection_work + stage2_advection_work
    )
    rk2_viscous = 0.5 * (
        stage1_viscous_work + stage2_viscous_work
    )
    rk2_forcing = 0.5 * (
        stage1_forcing_work + stage2_forcing_work
    )

    total_difference = total_2 - total_1
    rk2_remainder = (
        solver.dt
        / 8.0
        * float(np.mean(total_difference * total_difference))
    )

    discarded_hat = np.where(
        solver.deal,
        0.0,
        unfiltered_hat,
    )
    removed_complex = np.fft.ifft2(discarded_hat)
    mask_loss = 0.5 * float(
        np.mean(np.abs(removed_complex) ** 2)
    )
    mask_rate = -mask_loss / solver.dt
    observed_filtered_rate = (
        z_filtered - z_current
    ) / solver.dt

    return {
        "loop_index": loop_index,
        "completed_steps": loop_index + 1,
        "physical_time": (loop_index + 1) * solver.dt,
        "current": current,
        "stage": stage,
        "unfiltered": unfiltered,
        "filtered": filtered,
        "psi_1": psi_1,
        "u_1": u_1,
        "v_1": v_1,
        "psi_2": psi_2,
        "u_2": u_2,
        "v_2": v_2,
        "transport_1": transport_1,
        "advection_1": advection_1,
        "viscous_1": viscous_1,
        "total_1": total_1,
        "transport_2": transport_2,
        "advection_2": advection_2,
        "viscous_2": viscous_2,
        "total_2": total_2,
        "z_current": z_current,
        "z_stage": z_stage,
        "z_unfiltered": z_unfiltered,
        "z_filtered": z_filtered,
        "stage1_advection_work_rate": stage1_advection_work,
        "stage2_advection_work_rate": stage2_advection_work,
        "rk2_advection_rate": rk2_advection,
        "rk2_viscous_rate": rk2_viscous,
        "rk2_forcing_rate": rk2_forcing,
        "rk2_quadratic_remainder_rate": rk2_remainder,
        "mask_enstrophy_change_rate": mask_rate,
        "observed_filtered_enstrophy_rate": observed_filtered_rate,
        "filtered_imaginary_ratio": (
            field_rms(filtered_complex.imag)
            / max(field_rms(filtered), RESIDUAL_FLOOR)
        ),
    }


STAGE_B_SCALAR_FIELDS = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "z_current",
    "z_stage",
    "z_unfiltered",
    "z_filtered",
    "stage1_advection_work_rate",
    "stage2_advection_work_rate",
    "rk2_advection_rate",
    "rk2_viscous_rate",
    "rk2_forcing_rate",
    "rk2_quadratic_remainder_rate",
    "mask_enstrophy_change_rate",
    "observed_filtered_enstrophy_rate",
)


def compare_stage_b_ledger_row(
    replay: Mapping[str, object],
    archived: Mapping[str, str],
) -> dict[str, object]:
    differences: dict[str, float] = {}
    passed = True

    for name in STAGE_B_SCALAR_FIELDS:
        if name in ("loop_index", "completed_steps"):
            observed_int = int(replay[name])
            archived_int = int(archived[name])
            field_pass = observed_int == archived_int
            differences[name] = float(observed_int - archived_int)
        else:
            observed = finite_float(name, replay[name])
            archived_value = finite_float(
                f"archived_{name}",
                archived[name],
            )
            absolute, _, field_pass = archived_scalar_comparison(
                observed,
                archived_value,
            )
            differences[name] = absolute

        passed = passed and field_pass

    return {
        "passed": passed,
        "differences": differences,
        "maximum_absolute_difference": max(
            differences.values(),
            default=0.0,
        ),
    }


# ============================================================================
# Same-state shadow operators and mechanism diagnostics
# ============================================================================

def freeze_array(array: np.ndarray) -> np.ndarray:
    result = np.asarray(array)
    result.setflags(write=False)
    return result


def freeze_solver_environment(solver: object) -> dict[str, str]:
    identities: dict[str, str] = {}

    for name in (
        "x",
        "X",
        "Y",
        "k",
        "kx",
        "ky",
        "k2",
        "deal",
        "w",
    ):
        value = np.asarray(getattr(solver, name))
        value.setflags(write=False)
        identities[name] = sha256_bytes(
            np.ascontiguousarray(value).tobytes(order="C")
        )

    identities["N"] = sha256_bytes(str(int(solver.N)).encode())
    identities["dt"] = sha256_bytes(repr(float(solver.dt)).encode())
    identities["nu"] = sha256_bytes(repr(float(solver.nu)).encode())
    identities["dx"] = sha256_bytes(repr(float(solver.dx)).encode())
    return identities


def verify_solver_environment(
    solver: object,
    expected: Mapping[str, str],
) -> None:
    observed = freeze_solver_environment(solver)

    if dict(observed) != dict(expected):
        changed = sorted(
            key
            for key in set(observed) | set(expected)
            if observed.get(key) != expected.get(key)
        )
        raise IntegrityFailure(
            "solver_environment_mutation",
            f"solver environment changed: {changed}",
        )


def operator_metadata(operator_id: str) -> Mapping[str, object]:
    for item in OPERATOR_REGISTRY:
        if item["operator_id"] == operator_id:
            return item

    raise KeyError(operator_id)


def operator_identity_limit(operator_id: str) -> float:
    if operator_id == "SHADOW_FD_SKEW_V1":
        return SKEW_IDENTITY_LIMIT

    if operator_id in (
        "SHADOW_FD_ADVECTIVE_PROJECTED_V1",
        "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
    ):
        return PSEUDO_PROJECTION_IDENTITY_LIMIT

    if operator_id == "SHADOW_FD_CONSERVATIVE_V1":
        return CENTERED_FORM_IDENTITY_LIMIT

    if operator_id == "SHADOW_ARAKAWA_V1":
        return ARAKAWA_IDENTITY_LIMIT

    return TRANSPORT_RHS_SIGN_LIMIT


def compute_shared_state_fields(
    solver: object,
    state: np.ndarray,
    psi: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    *,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    helper_advection_fd: Callable[..., np.ndarray] | None,
    helper_advection_arakawa: Callable[..., np.ndarray] | None,
    helper_check: bool,
) -> dict[str, object]:
    state_array = np.asarray(state, dtype=np.float64)
    state_hash_before = sha256_array(state_array)
    writeable_before = bool(state_array.flags.writeable)

    omega_x_c, omega_y_c = centered_gradients(
        state_array,
        float(solver.dx),
    )
    baseline_transport = u * omega_x_c + v * omega_y_c

    projected_baseline, projected_baseline_imaginary = (
        project_field_with_imaginary(
            baseline_transport,
            np.asarray(solver.deal),
        )
    )

    ux_c, _ = centered_gradients(u, float(solver.dx))
    _, vy_c = centered_gradients(v, float(solver.dx))
    centered_divergence = ux_c + vy_c

    ux_omega, _ = centered_gradients(
        u * state_array,
        float(solver.dx),
    )
    _, vy_omega = centered_gradients(
        v * state_array,
        float(solver.dx),
    )
    conservative_transport = ux_omega + vy_omega
    skew_transport = 0.5 * (
        baseline_transport + conservative_transport
    )

    product_rule_defect = (
        conservative_transport
        - baseline_transport
        - state_array * centered_divergence
    )
    centered_form_identity_residual = (
        conservative_transport
        - baseline_transport
        - state_array * centered_divergence
        - product_rule_defect
    )

    centered_work_left = mean_product(
        state_array,
        conservative_transport - baseline_transport,
    )
    centered_divergence_work = mean_product(
        state_array * state_array,
        centered_divergence,
    )
    centered_product_rule_work = mean_product(
        state_array,
        product_rule_defect,
    )
    centered_work_identity_residual = (
        centered_work_left
        - centered_divergence_work
        - centered_product_rule_work
    )

    omega_x_s, omega_y_s, omega_gradient_imaginary = (
        spectral_gradients_with_imaginary(
            state_array,
            np.asarray(solver.kx),
            np.asarray(solver.ky),
        )
    )
    pseudo_raw_transport = u * omega_x_s + v * omega_y_s
    pseudo_projected_transport, pseudo_projected_imaginary = (
        project_field_with_imaginary(
            pseudo_raw_transport,
            np.asarray(solver.deal),
        )
    )
    pseudo_removed = (
        pseudo_raw_transport - pseudo_projected_transport
    )

    u_x_s, _, u_gradient_imaginary = (
        spectral_gradients_with_imaginary(
            u,
            np.asarray(solver.kx),
            np.asarray(solver.ky),
        )
    )
    _, v_y_s, v_gradient_imaginary = (
        spectral_gradients_with_imaginary(
            v,
            np.asarray(solver.kx),
            np.asarray(solver.ky),
        )
    )
    spectral_divergence = u_x_s + v_y_s

    arakawa_jacobian = np.asarray(
        jacobian_arakawa_periodic(
            psi,
            state_array,
            float(solver.dx),
        ),
        dtype=np.float64,
    )
    arakawa_transport = -arakawa_jacobian

    transports = {
        "BASE_FD_ADVECTIVE_V1": np.asarray(
            baseline_transport,
            dtype=np.float64,
        ),
        "SHADOW_FD_ADVECTIVE_PROJECTED_V1": np.asarray(
            projected_baseline,
            dtype=np.float64,
        ),
        "SHADOW_FD_CONSERVATIVE_V1": np.asarray(
            conservative_transport,
            dtype=np.float64,
        ),
        "SHADOW_FD_SKEW_V1": np.asarray(
            skew_transport,
            dtype=np.float64,
        ),
        "SHADOW_PS_ADVECTIVE_RAW_V1": np.asarray(
            pseudo_raw_transport,
            dtype=np.float64,
        ),
        "SHADOW_PS_ADVECTIVE_PROJECTED_V1": np.asarray(
            pseudo_projected_transport,
            dtype=np.float64,
        ),
        "SHADOW_ARAKAWA_V1": np.asarray(
            arakawa_transport,
            dtype=np.float64,
        ),
    }

    if tuple(transports) != OPERATOR_IDS:
        raise IntegrityFailure(
            "operator_registry_order",
            f"computed operator order={tuple(transports)!r}",
        )

    for operator_id, transport in transports.items():
        if transport.shape != state_array.shape:
            raise IntegrityFailure(
                "operator_shape",
                f"{operator_id} shape={transport.shape}, "
                f"expected={state_array.shape}",
                operator_id=operator_id,
            )

        if not np.isfinite(transport).all():
            raise IntegrityFailure(
                "operator_finite",
                f"{operator_id} produced a nonfinite value",
                operator_id=operator_id,
            )

        transport.setflags(write=False)

    helper_exact_equal: bool | None = None
    helper_normalized_difference: float | None = None
    helper_arakawa_normalized_difference: float | None = None

    if helper_check:
        if helper_advection_fd is None or helper_advection_arakawa is None:
            raise IntegrityFailure(
                "helper_availability",
                "sentinel helper check was requested without helper functions",
            )

        helper_baseline = np.asarray(
            helper_advection_fd(solver, state_array),
            dtype=np.float64,
        )
        _, helper_normalized_difference = normalized_rms_difference(
            helper_baseline,
            baseline_transport,
        )
        helper_exact_equal = bool(
            np.array_equal(helper_baseline, baseline_transport)
        )

        if (
            helper_normalized_difference
            > BASELINE_HELPER_NORMALIZED_TOLERANCE
        ):
            raise IntegrityFailure(
                "baseline_helper_equivalence",
                "baseline helper differs from embedded mirror: "
                f"{helper_normalized_difference}",
                operator_id="BASE_FD_ADVECTIVE_V1",
            )

        helper_arakawa = np.asarray(
            helper_advection_arakawa(solver, state_array),
            dtype=np.float64,
        )
        _, helper_arakawa_normalized_difference = (
            normalized_rms_difference(
                helper_arakawa,
                arakawa_transport,
            )
        )

        if (
            helper_arakawa_normalized_difference
            > ARAKAWA_IDENTITY_LIMIT
        ):
            raise IntegrityFailure(
                "arakawa_helper_equivalence",
                "Arakawa helper differs from shared-state mirror: "
                f"{helper_arakawa_normalized_difference}",
                operator_id="SHADOW_ARAKAWA_V1",
            )

    state_hash_after = sha256_array(state_array)
    writeable_after = bool(state_array.flags.writeable)
    state_unchanged = (
        state_hash_after == state_hash_before
        and writeable_after == writeable_before
    )

    if not state_unchanged:
        raise IntegrityFailure(
            "shadow_state_mutation",
            "shadow evaluation changed input state bytes or writeability",
        )

    centered_identity_normalized = (
        field_rms(centered_form_identity_residual)
        / max(
            field_rms(conservative_transport),
            field_rms(baseline_transport),
            field_rms(state_array * centered_divergence),
            field_rms(product_rule_defect),
            RESIDUAL_FLOOR,
        )
    )

    skew_identity_residual = (
        skew_transport
        - 0.5 * (
            baseline_transport + conservative_transport
        )
    )
    skew_identity_normalized = (
        field_rms(skew_identity_residual)
        / max(field_rms(skew_transport), RESIDUAL_FLOOR)
    )

    projected_baseline_reconstruction, _ = (
        project_field_with_imaginary(
            baseline_transport,
            np.asarray(solver.deal),
        )
    )
    projected_baseline_identity = normalized_rms_difference(
        projected_baseline,
        projected_baseline_reconstruction,
    )[1]

    pseudo_projected_reconstruction, _ = (
        project_field_with_imaginary(
            pseudo_raw_transport,
            np.asarray(solver.deal),
        )
    )
    pseudo_projection_identity = normalized_rms_difference(
        pseudo_projected_transport,
        pseudo_projected_reconstruction,
    )[1]

    arakawa_sign_identity = normalized_rms_difference(
        arakawa_transport,
        -arakawa_jacobian,
    )[1]

    spectral_divergence_normalized = (
        field_rms(spectral_divergence)
        / max(
            field_rms(u_x_s),
            field_rms(v_y_s),
            RESIDUAL_FLOOR,
        )
    )

    maximum_imaginary_ratio = max(
        omega_gradient_imaginary,
        projected_baseline_imaginary,
        pseudo_projected_imaginary,
        u_gradient_imaginary,
        v_gradient_imaginary,
    )

    mechanism = {
        "centered_velocity_divergence_rms": field_rms(
            centered_divergence
        ),
        "centered_velocity_divergence_max_abs": max_abs(
            centered_divergence
        ),
        "centered_product_rule_defect_rms": field_rms(
            product_rule_defect
        ),
        "centered_product_rule_defect_max_abs": max_abs(
            product_rule_defect
        ),
        "centered_form_identity_residual_rms": field_rms(
            centered_form_identity_residual
        ),
        "normalized_centered_form_identity_residual": (
            centered_identity_normalized
        ),
        "centered_work_identity_residual": (
            centered_work_identity_residual
        ),
        "centered_divergence_work_term": (
            centered_divergence_work
        ),
        "centered_product_rule_work_term": (
            centered_product_rule_work
        ),
        "spectral_velocity_divergence_rms": field_rms(
            spectral_divergence
        ),
        "spectral_velocity_divergence_max_abs": max_abs(
            spectral_divergence
        ),
        "normalized_spectral_velocity_divergence": (
            spectral_divergence_normalized
        ),
        "pseudo_product_removed_rms": field_rms(
            pseudo_removed
        ),
        "pseudo_product_removed_max_abs": max_abs(
            pseudo_removed
        ),
        "pseudo_product_removed_work": mean_product(
            state_array,
            -pseudo_raw_transport
            + pseudo_projected_transport,
        ),
        "pseudo_projection_fractional_work_reduction": (
            1.0
            - abs(mean_product(state_array, -pseudo_projected_transport))
            / max(
                abs(mean_product(state_array, -pseudo_raw_transport)),
                RESIDUAL_FLOOR,
            )
        ),
        "pseudo_raw_spectral_fraction_outside_mask": (
            spectral_fraction_outside_mask(
                pseudo_raw_transport,
                np.asarray(solver.deal),
            )
        ),
        "arakawa_sign_identity_residual": (
            arakawa_sign_identity
        ),
        "arakawa_secondary_energy_work": mean_product(
            psi,
            arakawa_jacobian,
        ),
        "maximum_imaginary_ratio": maximum_imaginary_ratio,
        "baseline_helper_checked": helper_check,
        "baseline_helper_exact_equal": helper_exact_equal,
        "baseline_helper_normalized_difference": (
            helper_normalized_difference
        ),
        "arakawa_helper_normalized_difference": (
            helper_arakawa_normalized_difference
        ),
        "state_unchanged": state_unchanged,
        "all_arrays_finite": all(
            np.isfinite(value).all()
            for value in transports.values()
        ),
        "operator_identity_residuals": {
            "BASE_FD_ADVECTIVE_V1": 0.0,
            "SHADOW_FD_ADVECTIVE_PROJECTED_V1": (
                projected_baseline_identity
            ),
            "SHADOW_FD_CONSERVATIVE_V1": (
                centered_identity_normalized
            ),
            "SHADOW_FD_SKEW_V1": skew_identity_normalized,
            "SHADOW_PS_ADVECTIVE_RAW_V1": 0.0,
            "SHADOW_PS_ADVECTIVE_PROJECTED_V1": (
                pseudo_projection_identity
            ),
            "SHADOW_ARAKAWA_V1": arakawa_sign_identity,
        },
    }

    integrity_checks = {
        "centered_form_identity": (
            centered_identity_normalized
            <= CENTERED_FORM_IDENTITY_LIMIT
        ),
        "skew_identity": (
            skew_identity_normalized <= SKEW_IDENTITY_LIMIT
        ),
        "projected_baseline_identity": (
            projected_baseline_identity
            <= PSEUDO_PROJECTION_IDENTITY_LIMIT
        ),
        "pseudo_projection_identity": (
            pseudo_projection_identity
            <= PSEUDO_PROJECTION_IDENTITY_LIMIT
        ),
        "arakawa_identity": (
            arakawa_sign_identity <= ARAKAWA_IDENTITY_LIMIT
        ),
        "spectral_divergence": (
            spectral_divergence_normalized
            <= SPECTRAL_DIVERGENCE_LIMIT
        ),
        "imaginary_ratio": (
            maximum_imaginary_ratio <= IMAGINARY_RATIO_LIMIT
        ),
        "state_unchanged": state_unchanged,
        "arrays_finite": bool(mechanism["all_arrays_finite"]),
    }

    failed = [
        name
        for name, passed in integrity_checks.items()
        if not passed
    ]

    if failed:
        raise IntegrityFailure(
            "shadow_mechanism_integrity",
            f"same-state mechanism checks failed: {failed}",
        )

    return {
        "transports": transports,
        "mechanism": mechanism,
        "state_hash": state_hash_before,
    }


def stage_operator_metrics(
    state: np.ndarray,
    transports: Mapping[str, np.ndarray],
) -> dict[str, dict[str, object]]:
    baseline_rhs = -np.asarray(
        transports["BASE_FD_ADVECTIVE_V1"],
        dtype=np.float64,
    )
    baseline_rms = field_rms(baseline_rhs)
    result: dict[str, dict[str, object]] = {}

    for operator_id in OPERATOR_IDS:
        transport = np.asarray(
            transports[operator_id],
            dtype=np.float64,
        )
        rhs = -transport
        transport_work = mean_product(state, transport)
        rhs_work = mean_product(state, rhs)
        sign_residual = abs(rhs_work + transport_work) / max(
            abs(rhs_work),
            abs(transport_work),
            RESIDUAL_FLOOR,
        )

        difference = rhs - baseline_rhs
        difference_rms = field_rms(difference)
        normalized_difference = difference_rms / max(
            baseline_rms,
            RESIDUAL_FLOOR,
        )
        alignment = rhs_work / max(
            field_rms(state) * field_rms(rhs),
            RESIDUAL_FLOOR,
        )
        identity_residual = 0.0

        result[operator_id] = {
            "transport_work": transport_work,
            "rhs_work": rhs_work,
            "rhs_rms": field_rms(rhs),
            "rhs_max_abs": max_abs(rhs),
            "work_alignment": alignment,
            "difference_from_baseline_rms": difference_rms,
            "normalized_difference_from_baseline": (
                normalized_difference
            ),
            "cosine_similarity_with_baseline": (
                cosine_similarity(rhs, baseline_rhs)
            ),
            "rhs_mean": float(np.mean(rhs)),
            "transport_rhs_sign_identity_residual": (
                sign_residual
            ),
            "operator_specific_identity_residual": identity_residual,
            "finite": bool(
                np.isfinite(rhs).all()
                and all_numeric_values_finite(
                    {
                        "transport_work": transport_work,
                        "rhs_work": rhs_work,
                        "rhs_rms": field_rms(rhs),
                        "alignment": alignment,
                    }
                )
            ),
        }

        if sign_residual > TRANSPORT_RHS_SIGN_LIMIT:
            raise IntegrityFailure(
                "transport_rhs_sign_identity",
                f"{operator_id} sign residual={sign_residual}",
                operator_id=operator_id,
            )

    return result


def apply_operator_identity_residuals(
    metrics: dict[str, dict[str, object]],
    mechanism: Mapping[str, object],
) -> None:
    residuals = mechanism["operator_identity_residuals"]
    assert isinstance(residuals, Mapping)

    for operator_id in OPERATOR_IDS:
        residual = float(residuals[operator_id])
        metrics[operator_id][
            "operator_specific_identity_residual"
        ] = residual

        if residual > operator_identity_limit(operator_id):
            raise IntegrityFailure(
                "operator_specific_identity",
                f"{operator_id} identity residual={residual}",
                operator_id=operator_id,
            )


def evaluate_operator_order(
    transports: Mapping[str, np.ndarray],
    order: Sequence[str],
) -> dict[str, tuple[str, float, float]]:
    result: dict[str, tuple[str, float, float]] = {}

    for operator_id in order:
        transport = np.asarray(
            transports[operator_id],
            dtype=np.float64,
        )
        result[operator_id] = (
            sha256_array(transport),
            field_rms(transport),
            max_abs(transport),
        )

    return result


def sentinel_order_invariance(
    stage1: Mapping[str, np.ndarray],
    stage2: Mapping[str, np.ndarray],
) -> bool:
    forward = tuple(OPERATOR_IDS)
    reverse = tuple(reversed(OPERATOR_IDS))

    stage1_forward = evaluate_operator_order(stage1, forward)
    stage1_reverse = evaluate_operator_order(stage1, reverse)
    stage2_forward = evaluate_operator_order(stage2, forward)
    stage2_reverse = evaluate_operator_order(stage2, reverse)

    return (
        stage1_forward == stage1_reverse
        and stage2_forward == stage2_reverse
    )



def compute_single_shadow_transport(
    operator_id: str,
    solver: object,
    state: np.ndarray,
    psi: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    *,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
) -> np.ndarray:
    state_array = np.asarray(state, dtype=np.float64)
    omega_x_c, omega_y_c = centered_gradients(
        state_array,
        float(solver.dx),
    )
    baseline = u * omega_x_c + v * omega_y_c

    if operator_id == "BASE_FD_ADVECTIVE_V1":
        result = baseline

    elif operator_id == "SHADOW_FD_ADVECTIVE_PROJECTED_V1":
        result = project_field_with_imaginary(
            baseline,
            np.asarray(solver.deal),
        )[0]

    elif operator_id == "SHADOW_FD_CONSERVATIVE_V1":
        ux_omega = centered_gradients(
            u * state_array,
            float(solver.dx),
        )[0]
        vy_omega = centered_gradients(
            v * state_array,
            float(solver.dx),
        )[1]
        result = ux_omega + vy_omega

    elif operator_id == "SHADOW_FD_SKEW_V1":
        conservative = (
            centered_gradients(
                u * state_array,
                float(solver.dx),
            )[0]
            + centered_gradients(
                v * state_array,
                float(solver.dx),
            )[1]
        )
        result = 0.5 * (baseline + conservative)

    elif operator_id in (
        "SHADOW_PS_ADVECTIVE_RAW_V1",
        "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
    ):
        omega_x_s, omega_y_s, _ = (
            spectral_gradients_with_imaginary(
                state_array,
                np.asarray(solver.kx),
                np.asarray(solver.ky),
            )
        )
        raw = u * omega_x_s + v * omega_y_s

        if operator_id == "SHADOW_PS_ADVECTIVE_RAW_V1":
            result = raw
        else:
            result = project_field_with_imaginary(
                raw,
                np.asarray(solver.deal),
            )[0]

    elif operator_id == "SHADOW_ARAKAWA_V1":
        result = -np.asarray(
            jacobian_arakawa_periodic(
                psi,
                state_array,
                float(solver.dx),
            ),
            dtype=np.float64,
        )

    else:
        raise KeyError(operator_id)

    output = np.ascontiguousarray(
        result,
        dtype=np.float64,
    )

    if not np.isfinite(output).all():
        raise IntegrityFailure(
            "sentinel_operator_finite",
            f"{operator_id} produced nonfinite sentinel output",
            operator_id=operator_id,
        )

    return output


def sentinel_order_invariance_recompute(
    solver: object,
    *,
    current: np.ndarray,
    stage: np.ndarray,
    psi_1: np.ndarray,
    u_1: np.ndarray,
    v_1: np.ndarray,
    psi_2: np.ndarray,
    u_2: np.ndarray,
    v_2: np.ndarray,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
) -> bool:
    current_hash = sha256_array(current)
    stage_hash = sha256_array(stage)

    def evaluate(
        state: np.ndarray,
        psi: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        order: Sequence[str],
    ) -> dict[str, str]:
        return {
            operator_id: sha256_array(
                compute_single_shadow_transport(
                    operator_id,
                    solver,
                    state,
                    psi,
                    u,
                    v,
                    jacobian_arakawa_periodic=(
                        jacobian_arakawa_periodic
                    ),
                )
            )
            for operator_id in order
        }

    forward = tuple(OPERATOR_IDS)
    reverse = tuple(reversed(OPERATOR_IDS))

    stage1_forward = evaluate(
        current,
        psi_1,
        u_1,
        v_1,
        forward,
    )
    stage1_reverse = evaluate(
        current,
        psi_1,
        u_1,
        v_1,
        reverse,
    )
    stage2_forward = evaluate(
        stage,
        psi_2,
        u_2,
        v_2,
        forward,
    )
    stage2_reverse = evaluate(
        stage,
        psi_2,
        u_2,
        v_2,
        reverse,
    )

    state_unchanged = (
        sha256_array(current) == current_hash
        and sha256_array(stage) == stage_hash
    )

    return (
        state_unchanged
        and stage1_forward == stage1_reverse
        and stage2_forward == stage2_reverse
    )


def build_shadow_rows(
    baseline: Mapping[str, object],
    stage1_metrics: Mapping[str, Mapping[str, object]],
    stage2_metrics: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    baseline_stage_weighted = 0.5 * (
        float(
            stage1_metrics["BASE_FD_ADVECTIVE_V1"][
                "rhs_work"
            ]
        )
        + float(
            stage2_metrics["BASE_FD_ADVECTIVE_V1"][
                "rhs_work"
            ]
        )
    )

    rows: list[dict[str, object]] = []

    for registry_item in OPERATOR_REGISTRY:
        operator_id = str(registry_item["operator_id"])
        first = stage1_metrics[operator_id]
        second = stage2_metrics[operator_id]
        stage_weighted = 0.5 * (
            float(first["rhs_work"])
            + float(second["rhs_work"])
        )
        difference = stage_weighted - baseline_stage_weighted
        ratio = stage_weighted / (
            baseline_stage_weighted
            if abs(baseline_stage_weighted) > RESIDUAL_FLOOR
            else RESIDUAL_FLOOR
        )
        absolute_ratio = abs(stage_weighted) / max(
            abs(baseline_stage_weighted),
            RESIDUAL_FLOOR,
        )

        if (
            abs(stage_weighted) <= SIGN_NONZERO_FLOOR
            and abs(baseline_stage_weighted) <= SIGN_NONZERO_FLOOR
        ):
            sign_agreement = True
        else:
            sign_agreement = (
                math.copysign(1.0, stage_weighted)
                == math.copysign(1.0, baseline_stage_weighted)
            )

        sign_identity_residual = max(
            float(
                first[
                    "transport_rhs_sign_identity_residual"
                ]
            ),
            float(
                second[
                    "transport_rhs_sign_identity_residual"
                ]
            ),
        )
        operator_specific_residual = max(
            float(
                first[
                    "operator_specific_identity_residual"
                ]
            ),
            float(
                second[
                    "operator_specific_identity_residual"
                ]
            ),
        )
        finite = bool(first["finite"] and second["finite"])
        operator_integrity_pass = (
            finite
            and sign_identity_residual
            <= TRANSPORT_RHS_SIGN_LIMIT
            and operator_specific_residual
            <= operator_identity_limit(operator_id)
        )

        row = {
            "loop_index": int(baseline["loop_index"]),
            "completed_steps": int(baseline["completed_steps"]),
            "physical_time": float(baseline["physical_time"]),
            "operator_id": operator_id,
            "operator_family": registry_item[
                "operator_family"
            ],
            "classification_role": registry_item[
                "classification_role"
            ],
            "stage_state_policy": STAGE_STATE_POLICY,
            "stage1_transport_work": first[
                "transport_work"
            ],
            "stage1_rhs_work": first["rhs_work"],
            "stage1_rhs_rms": first["rhs_rms"],
            "stage1_rhs_max_abs": first["rhs_max_abs"],
            "stage1_work_alignment": first[
                "work_alignment"
            ],
            "stage1_difference_from_baseline_rms": first[
                "difference_from_baseline_rms"
            ],
            "stage1_normalized_difference_from_baseline": first[
                "normalized_difference_from_baseline"
            ],
            "stage1_cosine_similarity_with_baseline": first[
                "cosine_similarity_with_baseline"
            ],
            "stage1_rhs_mean": first["rhs_mean"],
            "stage2_transport_work": second[
                "transport_work"
            ],
            "stage2_rhs_work": second["rhs_work"],
            "stage2_rhs_rms": second["rhs_rms"],
            "stage2_rhs_max_abs": second["rhs_max_abs"],
            "stage2_work_alignment": second[
                "work_alignment"
            ],
            "stage2_difference_from_baseline_rms": second[
                "difference_from_baseline_rms"
            ],
            "stage2_normalized_difference_from_baseline": second[
                "normalized_difference_from_baseline"
            ],
            "stage2_cosine_similarity_with_baseline": second[
                "cosine_similarity_with_baseline"
            ],
            "stage2_rhs_mean": second["rhs_mean"],
            "stage_weighted_rhs_work": stage_weighted,
            "difference_from_baseline_stage_weighted_work": (
                difference
            ),
            "ratio_to_baseline_stage_weighted_work": ratio,
            "absolute_ratio_to_baseline_stage_weighted_work": (
                absolute_ratio
            ),
            "sign_agreement_with_baseline": sign_agreement,
            "input_state_unchanged": True,
            "operator_output_finite": finite,
            "transport_rhs_sign_identity_residual": (
                sign_identity_residual
            ),
            "operator_specific_identity_residual": (
                operator_specific_residual
            ),
            "operator_integrity_pass": operator_integrity_pass,
        }

        if not all_numeric_values_finite(row):
            raise IntegrityFailure(
                "shadow_row_finite",
                f"{operator_id} shadow row contains nonfinite data",
                operator_id=operator_id,
            )

        if not operator_integrity_pass:
            raise IntegrityFailure(
                "shadow_operator_integrity",
                f"{operator_id} failed operator integrity",
                operator_id=operator_id,
            )

        rows.append(row)

    if len(rows) != len(OPERATOR_IDS):
        raise IntegrityFailure(
            "shadow_row_count_per_step",
            f"shadow rows per step={len(rows)}",
        )

    return rows


# ============================================================================
# Archived trajectory comparison
# ============================================================================

ARCHIVE_COMPARISON_FIELDS = (
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


def initialize_archive_equivalence() -> dict[str, object]:
    return {
        "match_count": 0,
        "all_matches_pass": True,
        "fields": {
            name: {
                "maximum_absolute_difference": 0.0,
                "maximum_relative_difference": 0.0,
                "loop_index_of_maximum_absolute_difference": None,
                "loop_index_of_maximum_relative_difference": None,
            }
            for name in ARCHIVE_COMPARISON_FIELDS
        },
    }


def compare_archive_snapshot(
    *,
    loop_index: int,
    replay: Mapping[str, object],
    archived: Mapping[str, str],
    state: dict[str, object],
) -> None:
    fields = state["fields"]
    assert isinstance(fields, dict)
    all_pass = True

    for name in ARCHIVE_COMPARISON_FIELDS:
        observed = finite_float(
            f"replay_{name}",
            replay[name],
        )
        expected = finite_float(
            f"archive_{name}",
            archived[name],
        )
        absolute, relative, passed = archived_scalar_comparison(
            observed,
            expected,
        )
        record = fields[name]
        assert isinstance(record, dict)

        if absolute > float(
            record["maximum_absolute_difference"]
        ):
            record["maximum_absolute_difference"] = absolute
            record[
                "loop_index_of_maximum_absolute_difference"
            ] = loop_index

        if relative > float(
            record["maximum_relative_difference"]
        ):
            record["maximum_relative_difference"] = relative
            record[
                "loop_index_of_maximum_relative_difference"
            ] = loop_index

        all_pass = all_pass and passed

    state["match_count"] = int(state["match_count"]) + 1
    state["all_matches_pass"] = bool(
        state["all_matches_pass"]
    ) and all_pass

    if not all_pass:
        raise IntegrityFailure(
            "archived_trajectory_equivalence",
            f"archived trajectory comparison failed at "
            f"loop_index={loop_index}",
        )


# ============================================================================
# Time-block accumulation and classification
# ============================================================================

def block_ids_for_time(physical_time: float) -> tuple[int, int]:
    primary: int | None = None

    for block in TIME_BLOCKS[:5]:
        lower = float(block["lower"])
        upper = float(block["upper"])
        lower_inclusive = bool(block["lower_inclusive"])

        lower_pass = (
            physical_time >= lower - 1.0e-12
            if lower_inclusive
            else physical_time > lower + 1.0e-12
        )
        upper_pass = physical_time <= upper + 1.0e-12

        if lower_pass and upper_pass:
            primary = int(block["block_id"])
            break

    if primary is None:
        raise IntegrityFailure(
            "time_block_membership",
            f"physical time does not belong to a primary block: "
            f"{physical_time}",
        )

    return primary, 6


def new_block_accumulators() -> dict[tuple[int, str], dict[str, object]]:
    result: dict[tuple[int, str], dict[str, object]] = {}

    for block in TIME_BLOCKS:
        for item in OPERATOR_REGISTRY:
            key = (
                int(block["block_id"]),
                str(item["operator_id"]),
            )
            result[key] = {
                "block": block,
                "registry": item,
                "rates": [],
                "sign_agreements": 0,
                "integrity_failure_count": 0,
            }

    return result


def update_block_accumulator(
    accumulator: dict[str, object],
    row: Mapping[str, object],
) -> None:
    rates = accumulator["rates"]
    assert isinstance(rates, list)
    rates.append(float(row["stage_weighted_rhs_work"]))

    if bool(row["sign_agreement_with_baseline"]):
        accumulator["sign_agreements"] = (
            int(accumulator["sign_agreements"]) + 1
        )

    if not bool(row["operator_integrity_pass"]):
        accumulator["integrity_failure_count"] = (
            int(accumulator["integrity_failure_count"]) + 1
        )


def n90_steps(rates: Sequence[float]) -> int:
    activities = sorted(
        (abs(float(value)) for value in rates),
        reverse=True,
    )
    total = sum(activities)

    if total <= RESIDUAL_FLOOR:
        return len(activities)

    target = 0.90 * total
    running = 0.0

    for index, value in enumerate(activities, start=1):
        running += value

        if running >= target:
            return index

    return len(activities)


def summarize_rate_series(
    rates: Sequence[float],
) -> dict[str, object]:
    array = np.asarray(rates, dtype=np.float64)

    if array.size == 0:
        raise IntegrityFailure(
            "time_block_empty",
            "time-block operator accumulator is empty",
        )

    positive = int(np.count_nonzero(array > 0.0))
    negative = int(np.count_nonzero(array < 0.0))
    zero = int(array.size - positive - negative)

    return {
        "step_count": int(array.size),
        "integrated_signed_work": float(
            DT * np.sum(array)
        ),
        "integrated_absolute_activity": float(
            DT * np.sum(np.abs(array))
        ),
        "mean_signed_rate": float(np.mean(array)),
        "median_signed_rate": float(np.median(array)),
        "mean_absolute_rate": float(
            np.mean(np.abs(array))
        ),
        "maximum_absolute_rate": float(
            np.max(np.abs(array))
        ),
        "positive_count": positive,
        "negative_count": negative,
        "zero_count": zero,
        "n90_steps": n90_steps(array.tolist()),
    }


def finalize_time_blocks(
    accumulators: Mapping[
        tuple[int, str],
        Mapping[str, object],
    ],
) -> tuple[
    list[dict[str, object]],
    dict[str, dict[str, dict[str, object]]],
]:
    base_summaries: dict[
        tuple[int, str],
        dict[str, object],
    ] = {}

    for key, accumulator in accumulators.items():
        rates = accumulator["rates"]
        assert isinstance(rates, list)
        base_summaries[key] = summarize_rate_series(rates)

    rows: list[dict[str, object]] = []
    structured: dict[
        str,
        dict[str, dict[str, object]],
    ] = {}

    for block in TIME_BLOCKS:
        block_id = int(block["block_id"])
        expected_steps = int(block["expected_steps"])
        block_key = str(block_id)
        structured[block_key] = {}
        baseline_summary = base_summaries[
            (block_id, "BASE_FD_ADVECTIVE_V1")
        ]
        baseline_integral = float(
            baseline_summary["integrated_signed_work"]
        )
        baseline_activity = float(
            baseline_summary["integrated_absolute_activity"]
        )
        baseline_maximum = float(
            baseline_summary["maximum_absolute_rate"]
        )

        for registry_item in OPERATOR_REGISTRY:
            operator_id = str(registry_item["operator_id"])
            accumulator = accumulators[(block_id, operator_id)]
            summary = dict(
                base_summaries[(block_id, operator_id)]
            )

            if int(summary["step_count"]) != expected_steps:
                raise IntegrityFailure(
                    "time_block_step_count",
                    f"block={block_id}, operator={operator_id}, "
                    f"steps={summary['step_count']}, "
                    f"expected={expected_steps}",
                    operator_id=operator_id,
                )

            activity_ratio = (
                float(summary["integrated_absolute_activity"])
                / max(baseline_activity, RESIDUAL_FLOOR)
            )
            signed_magnitude_ratio = (
                abs(float(summary["integrated_signed_work"]))
                / max(abs(baseline_integral), RESIDUAL_FLOOR)
            )
            maximum_ratio = (
                float(summary["maximum_absolute_rate"])
                / max(baseline_maximum, RESIDUAL_FLOOR)
            )
            signed_ratio = (
                float(summary["integrated_signed_work"])
                / (
                    baseline_integral
                    if abs(baseline_integral) > RESIDUAL_FLOOR
                    else RESIDUAL_FLOOR
                )
            )

            integrity_failure_count = int(
                accumulator["integrity_failure_count"]
            )
            integrity_pass = integrity_failure_count == 0

            near_neutral = (
                operator_id in PRIMARY_ALTERNATE_IDS
                and integrity_pass
                and activity_ratio
                <= NEAR_NEUTRAL_ACTIVITY_LIMIT
                and signed_magnitude_ratio
                <= NEAR_NEUTRAL_SIGNED_LIMIT
                and maximum_ratio
                <= NEAR_NEUTRAL_MAXIMUM_LIMIT
                and int(summary["n90_steps"])
                >= MINIMUM_N90_STEPS
            )
            persistence = (
                operator_id in PRIMARY_ALTERNATE_IDS
                and integrity_pass
                and activity_ratio
                >= PERSISTENCE_ACTIVITY_LIMIT
                and signed_magnitude_ratio
                >= PERSISTENCE_SIGNED_LIMIT
                and maximum_ratio
                >= PERSISTENCE_MAXIMUM_LIMIT
            )

            step_count = int(summary["step_count"])
            sign_agreement_fraction = (
                int(accumulator["sign_agreements"])
                / step_count
            )

            row = {
                "block_id": block_id,
                "block_label": block["label"],
                "operator_id": operator_id,
                "operator_family": registry_item[
                    "operator_family"
                ],
                "classification_role": registry_item[
                    "classification_role"
                ],
                **summary,
                "sign_agreement_fraction_with_baseline": (
                    sign_agreement_fraction
                ),
                "absolute_activity_ratio_to_baseline": (
                    activity_ratio
                ),
                "signed_integral_magnitude_ratio_to_baseline": (
                    signed_magnitude_ratio
                ),
                "maximum_rate_ratio_to_baseline": (
                    maximum_ratio
                ),
                "signed_integral_ratio_to_baseline": (
                    signed_ratio
                ),
                "near_neutral_pass": near_neutral,
                "persistence_pass": persistence,
                "integrity_failure_count": (
                    integrity_failure_count
                ),
            }

            if not all_numeric_values_finite(row):
                raise IntegrityFailure(
                    "time_block_row_finite",
                    f"time-block row is nonfinite: "
                    f"block={block_id}, operator={operator_id}",
                    operator_id=operator_id,
                )

            rows.append(row)
            structured[block_key][operator_id] = dict(row)

    if len(rows) != EXPECTED_TIME_BLOCK_ROWS:
        raise IntegrityFailure(
            "time_block_output_count",
            f"time-block rows={len(rows)}, "
            f"expected={EXPECTED_TIME_BLOCK_ROWS}",
        )

    return rows, structured


def classify_shadow_response(
    structured: Mapping[
        str,
        Mapping[str, Mapping[str, object]],
    ],
) -> str:
    final_window = structured["5"]
    full_run = structured["6"]

    all_integrity_pass = all(
        int(row["integrity_failure_count"]) == 0
        for block in structured.values()
        for row in block.values()
    )

    if not all_integrity_pass:
        return "NUMERICAL INTEGRITY FAILURE"

    all_near_neutral = all(
        bool(final_window[operator_id]["near_neutral_pass"])
        and bool(full_run[operator_id]["near_neutral_pass"])
        for operator_id in PRIMARY_ALTERNATE_IDS
    )

    if all_near_neutral:
        return "SHADOW SET SUPPORTS CURRENT-FORM SPECIFICITY"

    persistent_families: set[str] = set()

    for operator_id in PRIMARY_ALTERNATE_IDS:
        final_persistent = bool(
            final_window[operator_id]["persistence_pass"]
        )
        full_persistent = bool(
            full_run[operator_id]["persistence_pass"]
        )

        if final_persistent and full_persistent:
            persistent_families.add(
                str(
                    operator_metadata(operator_id)[
                        "operator_family"
                    ]
                )
            )

    if len(persistent_families) >= 2:
        return "NONZERO WORK PERSISTS ACROSS MULTIPLE FORMS"

    near_neutral_any = any(
        bool(final_window[operator_id]["near_neutral_pass"])
        or bool(full_run[operator_id]["near_neutral_pass"])
        for operator_id in PRIMARY_ALTERNATE_IDS
    )
    persistent_any = any(
        bool(final_window[operator_id]["persistence_pass"])
        or bool(full_run[operator_id]["persistence_pass"])
        for operator_id in PRIMARY_ALTERNATE_IDS
    )

    intermediate_any = any(
        not bool(final_window[operator_id]["near_neutral_pass"])
        and not bool(final_window[operator_id]["persistence_pass"])
        for operator_id in PRIMARY_ALTERNATE_IDS
    )

    if near_neutral_any and (persistent_any or intermediate_any):
        return "SHADOW RESPONSE IS FORM-DEPENDENT AND MIXED"

    if not near_neutral_any:
        return "SHADOW SET DOES NOT SHOW STRONG FORM SEPARATION"

    return "SAME-STATE SHADOW AUDIT INCONCLUSIVE"


# ============================================================================
# Mechanism aggregation
# ============================================================================

MECHANISM_KEYS = (
    "centered_velocity_divergence_rms",
    "centered_velocity_divergence_max_abs",
    "centered_product_rule_defect_rms",
    "centered_product_rule_defect_max_abs",
    "normalized_centered_form_identity_residual",
    "centered_work_identity_residual",
    "centered_divergence_work_term",
    "centered_product_rule_work_term",
    "spectral_velocity_divergence_rms",
    "spectral_velocity_divergence_max_abs",
    "normalized_spectral_velocity_divergence",
    "pseudo_product_removed_rms",
    "pseudo_product_removed_max_abs",
    "pseudo_product_removed_work",
    "pseudo_projection_fractional_work_reduction",
    "pseudo_raw_spectral_fraction_outside_mask",
    "arakawa_sign_identity_residual",
    "arakawa_secondary_energy_work",
    "maximum_imaginary_ratio",
)


def new_mechanism_accumulator() -> dict[str, list[float]]:
    return {
        f"stage{stage}_{key}": []
        for stage in (1, 2)
        for key in MECHANISM_KEYS
    }


def update_mechanism_accumulator(
    accumulator: dict[str, list[float]],
    stage: int,
    mechanism: Mapping[str, object],
) -> None:
    for key in MECHANISM_KEYS:
        accumulator[f"stage{stage}_{key}"].append(
            finite_float(
                f"stage{stage}_{key}",
                mechanism[key],
            )
        )


def summarize_mechanisms(
    accumulator: Mapping[str, Sequence[float]],
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}

    for name, values in accumulator.items():
        array = np.asarray(values, dtype=np.float64)

        if array.size != STEPS:
            raise IntegrityFailure(
                "mechanism_record_count",
                f"{name} count={array.size}, expected={STEPS}",
            )

        result[name] = {
            "mean": float(np.mean(array)),
            "median": float(np.median(array)),
            "minimum": float(np.min(array)),
            "maximum": float(np.max(array)),
            "maximum_absolute": float(
                np.max(np.abs(array))
            ),
        }

    return result


# ============================================================================
# Report and inventory
# ============================================================================

def write_csv_table(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[Mapping[str, object]],
) -> None:
    assert_unique_headers(path.name, fieldnames)
    temporary = path.with_name(path.name + ".tmp")

    try:
        with temporary.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=list(fieldnames),
                extrasaction="raise",
                lineterminator="\n",
            )
            writer.writeheader()

            expected_keys = set(fieldnames)

            for row in rows:
                observed_keys = set(row)

                if observed_keys != expected_keys:
                    raise RuntimeError(
                        f"CSV row schema mismatch for {path.name}: "
                        f"missing={sorted(expected_keys - observed_keys)}, "
                        f"extra={sorted(observed_keys - expected_keys)}"
                    )

                writer.writerow(row)

            handle.flush()
            os.fsync(handle.fileno())

        temporary.replace(path)

    finally:
        if temporary.exists():
            temporary.unlink()


def render_stage_c_report(
    *,
    run_id: str,
    execution_commit: str,
    classification: str,
    structured: Mapping[
        str,
        Mapping[str, Mapping[str, object]],
    ],
    archive_equivalence: Mapping[str, object],
    mechanism_summary: Mapping[
        str,
        Mapping[str, float],
    ],
    baseline_reproduction: Mapping[str, object],
) -> str:
    final_window = structured["5"]
    full_run = structured["6"]

    lines = [
        "# Stage C Same-State Advection-Form Shadow Audit Report",
        "",
        "## 0. Document control",
        "",
        f"- Run ID: `{run_id}`",
        f"- Execution commit: `{execution_commit}`",
        f"- Design commit: `{AUTHORIZED_DESIGN_COMMIT}`",
        f"- Stage B evidence commit: `{STAGE_B_EVIDENCE_COMMIT}`",
        "- Audit type: same-state local operator comparison",
        "- Accepted trajectory changed by shadows: no",
        "- Alternate trajectories executed: no",
        "- Protected solver run loop called: no",
        "- Method-superiority claim authorized: no",
        "",
        "## 1. Classification",
        "",
        f"> **{classification}**",
        "",
        "This classification applies only to the frozen same-state shadow set.",
        "It is not a solver-selection result.",
        "",
        "## 2. Baseline reproduction",
        "",
        f"- Baseline steps: `{baseline_reproduction['step_count']}`",
        (
            "- Stage B per-step scalar rows passed: "
            f"`{baseline_reproduction['per_step_rows_passed']}`"
        ),
        (
            "- Archived comparison points passed: "
            f"`{archive_equivalence['match_count']} / "
            f"{EXPECTED_ARCHIVE_MATCHES}`"
        ),
        (
            "- Final-window baseline integrated work: "
            f"`{baseline_reproduction['final_window_integral']:.16e}`"
        ),
        (
            "- Full-run baseline integrated work: "
            f"`{baseline_reproduction['full_run_integral']:.16e}`"
        ),
        "",
        "## 3. Final-window operator comparison",
        "",
        (
            "| Operator | Family | Integrated signed work | "
            "Absolute-activity ratio | Signed-magnitude ratio | "
            "Maximum-rate ratio | Near-neutral | Persistent |"
        ),
        "|---|---|---:|---:|---:|---:|---|---|",
    ]

    for item in OPERATOR_REGISTRY:
        operator_id = str(item["operator_id"])
        row = final_window[operator_id]
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{operator_id}`",
                    f"`{row['operator_family']}`",
                    f"{float(row['integrated_signed_work']):.12e}",
                    (
                        f"{float(row['absolute_activity_ratio_to_baseline']):.12e}"
                    ),
                    (
                        f"{float(row['signed_integral_magnitude_ratio_to_baseline']):.12e}"
                    ),
                    (
                        f"{float(row['maximum_rate_ratio_to_baseline']):.12e}"
                    ),
                    str(bool(row["near_neutral_pass"])),
                    str(bool(row["persistence_pass"])),
                )
            )
            + " |"
        )

    lines.extend(
        (
            "",
            "## 4. Full-run operator comparison",
            "",
            (
                "| Operator | Family | Integrated signed work | "
                "Absolute-activity ratio | Signed-magnitude ratio | "
                "Maximum-rate ratio | Near-neutral | Persistent |"
            ),
            "|---|---|---:|---:|---:|---:|---|---|",
        )
    )

    for item in OPERATOR_REGISTRY:
        operator_id = str(item["operator_id"])
        row = full_run[operator_id]
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{operator_id}`",
                    f"`{row['operator_family']}`",
                    f"{float(row['integrated_signed_work']):.12e}",
                    (
                        f"{float(row['absolute_activity_ratio_to_baseline']):.12e}"
                    ),
                    (
                        f"{float(row['signed_integral_magnitude_ratio_to_baseline']):.12e}"
                    ),
                    (
                        f"{float(row['maximum_rate_ratio_to_baseline']):.12e}"
                    ),
                    str(bool(row["near_neutral_pass"])),
                    str(bool(row["persistence_pass"])),
                )
            )
            + " |"
        )

    lines.extend(
        (
            "",
            "## 5. Same-state policy",
            "",
            "Every shadow operator was evaluated at the baseline accepted state",
            "and the baseline RK2 stage state. Only baseline centered advection",
            "entered the accepted update. No shadow result advanced a state.",
            "",
            "## 6. Mechanism diagnostics",
            "",
            (
                "- Maximum stage-1 centered-form identity residual: "
                f"`{mechanism_summary['stage1_normalized_centered_form_identity_residual']['maximum_absolute']:.12e}`"
            ),
            (
                "- Maximum stage-2 centered-form identity residual: "
                f"`{mechanism_summary['stage2_normalized_centered_form_identity_residual']['maximum_absolute']:.12e}`"
            ),
            (
                "- Maximum stage-1 spectral-divergence ratio: "
                f"`{mechanism_summary['stage1_normalized_spectral_velocity_divergence']['maximum_absolute']:.12e}`"
            ),
            (
                "- Maximum stage-2 spectral-divergence ratio: "
                f"`{mechanism_summary['stage2_normalized_spectral_velocity_divergence']['maximum_absolute']:.12e}`"
            ),
            (
                "- Maximum stage-1 Arakawa sign residual: "
                f"`{mechanism_summary['stage1_arakawa_sign_identity_residual']['maximum_absolute']:.12e}`"
            ),
            (
                "- Maximum stage-2 Arakawa sign residual: "
                f"`{mechanism_summary['stage2_arakawa_sign_identity_residual']['maximum_absolute']:.12e}`"
            ),
            "",
            "## 7. Claim boundaries",
            "",
            "This audit does not establish:",
            "",
            "- formal temporal or spatial convergence;",
            "- physical validation;",
            "- long-time alternate-method behavior;",
            "- which method should replace the baseline;",
            "- turbulence, a cascade, an inertial range, or a spectral law;",
            "- production readiness or unique physical causation.",
            "",
            "Same-state shadow work is a local implemented-operator diagnostic.",
            "",
        )
    )

    return "\n".join(lines)


def write_inventory(
    run_directory: Path,
    inventory_path: Path,
    paths: Sequence[Path],
) -> str:
    rows: list[dict[str, object]] = []

    for path in paths:
        if not path.is_file():
            continue

        rows.append(
            {
                "relative_path": path.relative_to(
                    run_directory
                ).as_posix(),
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
                "self-hash omitted to avoid circular self-reference"
            ),
        }
    )

    write_csv_table(
        inventory_path,
        INVENTORY_FIELDNAMES,
        rows,
    )
    return sha256_file(inventory_path)


# ============================================================================
# Static inspection
# ============================================================================

FORBIDDEN_TRAJECTORY_NAMES = (
    "omega_arakawa_next",
    "omega_pseudo_next",
    "omega_conservative_next",
    "shadow_omega_next",
    "alternate_omega",
)

FORBIDDEN_CALL_NAMES = (
    "step_once_selectable",
    "run_selectable_diagnostic",
    "polyfit",
    "curve_fit",
)


def call_name(node: ast.Call) -> str:
    function = node.func

    if isinstance(function, ast.Name):
        return function.id

    if isinstance(function, ast.Attribute):
        return function.attr

    return ""


def enclosing_function_name(
    node: ast.AST,
    parent_map: Mapping[ast.AST, ast.AST],
) -> str | None:
    current: ast.AST | None = node

    while current is not None:
        if isinstance(
            current,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            return current.name

        current = parent_map.get(current)

    return None


def inspect_ast(source: str) -> dict[str, object]:
    tree = ast.parse(source, filename=RUNNER_NAME)
    parent_map = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }

    project_imports: list[tuple[str, str | None]] = []
    constructor_calls = 0
    forbidden_calls: list[str] = []
    run_calls: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""

            if (
                module.startswith("project.")
                or module == "forcing_budget_diagnostic"
            ):
                project_imports.append(
                    (
                        module,
                        enclosing_function_name(node, parent_map),
                    )
                )

        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("project."):
                    project_imports.append(
                        (
                            alias.name,
                            enclosing_function_name(
                                node,
                                parent_map,
                            ),
                        )
                    )

        elif isinstance(node, ast.Call):
            name = call_name(node)

            if name == "SpectralSolver":
                constructor_calls += 1

            if name in FORBIDDEN_CALL_NAMES:
                forbidden_calls.append(name)

            if name == "run" and isinstance(node.func, ast.Attribute):
                receiver = node.func.value

                if (
                    isinstance(receiver, ast.Name)
                    and receiver.id in (
                        "solver",
                        "selectable_solver",
                        "baseline_solver",
                    )
                ):
                    run_calls.append(
                        f"{receiver.id}.run"
                    )

    invalid_imports = [
        (module, scope)
        for module, scope in project_imports
        if scope != "execute_audit"
    ]

    if invalid_imports:
        raise RuntimeError(
            f"project imports outside execute_audit: "
            f"{invalid_imports}"
        )

    if constructor_calls != 1:
        raise RuntimeError(
            f"SpectralSolver constructor calls={constructor_calls}, "
            "expected=1"
        )

    if forbidden_calls:
        raise RuntimeError(
            f"forbidden call sites present: {forbidden_calls}"
        )

    if run_calls:
        raise RuntimeError(
            "a protected or selectable run() call is present"
        )

    identifier_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }

    forbidden_identifiers = sorted(
        set(FORBIDDEN_TRAJECTORY_NAMES)
        & identifier_names
    )

    if forbidden_identifiers:
        raise RuntimeError(
            "forbidden alternate-trajectory identifiers present: "
            f"{forbidden_identifiers}"
        )

    baseline_assignments = 0

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue

        targets: list[ast.expr] = []

        if isinstance(node, ast.Assign):
            targets.extend(node.targets)
        else:
            targets.append(node.target)

        for target in targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "baseline_omega"
            ):
                baseline_assignments += 1

    if baseline_assignments < 2:
        raise RuntimeError(
            "baseline_omega does not have the expected initialization "
            "and accepted-state assignment"
        )

    missing_operator_ids = [
        operator_id
        for operator_id in OPERATOR_IDS
        if operator_id not in source
    ]

    if missing_operator_ids:
        raise RuntimeError(
            f"missing operator IDs: {missing_operator_ids}"
        )

    return {
        "project_import_count": len(project_imports),
        "project_imports": project_imports,
        "spectral_solver_constructor_calls": constructor_calls,
        "baseline_omega_assignments": baseline_assignments,
        "forbidden_calls": forbidden_calls,
        "run_calls": run_calls,
    }


def inspect_runner(repo: Path) -> int:
    runner = Path(__file__).resolve()

    if runner.name != RUNNER_NAME:
        fail(
            f"runner filename is {runner.name!r}, "
            f"expected {RUNNER_NAME!r}"
        )

    raw = runner.read_bytes()

    if b"\r" in raw:
        fail("runner bytes are not LF-only")

    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        fail(f"runner is not valid UTF-8: {error}")

    try:
        compile(source, str(runner), "exec")
    except SyntaxError as error:
        fail(f"runner does not compile: {error}")

    verify_inspection_repository_state(repo, runner)
    source_hashes = verify_source_identities(repo)
    assert_all_output_headers_unique()
    ast_summary = inspect_ast(source)

    if len(OPERATOR_REGISTRY) != 7:
        fail(
            f"operator count={len(OPERATOR_REGISTRY)}, expected=7"
        )

    if len(PRIMARY_ALTERNATE_IDS) != 5:
        fail(
            f"primary alternate count={len(PRIMARY_ALTERNATE_IDS)}, "
            "expected=5"
        )

    expected_operator_ids = (
        "BASE_FD_ADVECTIVE_V1",
        "SHADOW_FD_ADVECTIVE_PROJECTED_V1",
        "SHADOW_FD_CONSERVATIVE_V1",
        "SHADOW_FD_SKEW_V1",
        "SHADOW_PS_ADVECTIVE_RAW_V1",
        "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
        "SHADOW_ARAKAWA_V1",
    )

    if OPERATOR_IDS != expected_operator_ids:
        fail(
            f"operator registry differs from frozen design: "
            f"{OPERATOR_IDS!r}"
        )

    expected_thresholds = (
        NEAR_NEUTRAL_ACTIVITY_LIMIT,
        NEAR_NEUTRAL_SIGNED_LIMIT,
        NEAR_NEUTRAL_MAXIMUM_LIMIT,
        PERSISTENCE_ACTIVITY_LIMIT,
        PERSISTENCE_SIGNED_LIMIT,
        PERSISTENCE_MAXIMUM_LIMIT,
        MINIMUM_N90_STEPS,
    )

    if expected_thresholds != (
        0.10,
        0.10,
        0.25,
        0.50,
        0.50,
        0.25,
        5,
    ):
        fail(
            "classification thresholds differ from frozen design"
        )

    expected_integrity_limits = (
        BASELINE_ARCHIVE_RELATIVE_TOLERANCE,
        BASELINE_ARCHIVE_ABSOLUTE_FLOOR,
        BASELINE_HELPER_NORMALIZED_TOLERANCE,
        CENTERED_FORM_IDENTITY_LIMIT,
        SKEW_IDENTITY_LIMIT,
        PSEUDO_PROJECTION_IDENTITY_LIMIT,
        ARAKAWA_IDENTITY_LIMIT,
        TRANSPORT_RHS_SIGN_LIMIT,
        SPECTRAL_DIVERGENCE_LIMIT,
        IMAGINARY_RATIO_LIMIT,
    )

    if expected_integrity_limits != (
        1.0e-11,
        1.0e-14,
        1.0e-15,
        1.0e-12,
        1.0e-15,
        1.0e-12,
        1.0e-12,
        1.0e-14,
        1.0e-12,
        1.0e-13,
    ):
        fail(
            "integrity tolerances differ from frozen design"
        )

    if SENTINEL_LOOP_INDICES != (
        0,
        4000,
        8000,
        12000,
        16000,
        20000,
    ):
        fail("sentinel index set differs from frozen design")

    if EXPECTED_SHADOW_ROWS != STEPS * len(OPERATOR_REGISTRY):
        fail("expected shadow-row formula is incorrect")

    if EXPECTED_TIME_BLOCK_ROWS != (
        len(TIME_BLOCKS) * len(OPERATOR_REGISTRY)
    ):
        fail("expected time-block-row formula is incorrect")

    print()
    print("=" * 72)
    print(
        "STAGE C SAME-STATE ADVECTION-FORM "
        "SHADOW RUNNER INSPECTION: PASS"
    )
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", sha256_bytes(raw))
    print("Design commit:", AUTHORIZED_DESIGN_COMMIT)
    print(
        "Stage C design SHA256:",
        source_hashes["stage_c_design"],
    )
    print("Configuration: N64, Re1000, dt0.005, steps20001")
    print("Baseline steps expected:", EXPECTED_STATE_REFERENCE_ROWS)
    print("Shadow operators:", len(OPERATOR_REGISTRY))
    print("Primary alternate operators:", len(PRIMARY_ALTERNATE_IDS))
    print("Expected shadow rows:", EXPECTED_SHADOW_ROWS)
    print("Expected time-block rows:", EXPECTED_TIME_BLOCK_ROWS)
    print("Expected archived comparisons:", EXPECTED_ARCHIVE_MATCHES)
    print("All output header lists unique: PASS")
    print("Frozen classification thresholds: PASS")
    print("Frozen integrity tolerances: PASS")
    print("Same baseline current state for shadows: PRESENT")
    print("Same baseline RK2 stage state for shadows: PRESENT")
    print("Sentinel forward/reverse order gate: PRESENT")
    print("Centered product-rule diagnostics: PRESENT")
    print("Pseudo-spectral projection diagnostics: PRESENT")
    print("Arakawa sign diagnostics: PRESENT")
    print(
        "Project imports outside run path:",
        "NO",
    )
    print(
        "SpectralSolver constructor calls:",
        ast_summary["spectral_solver_constructor_calls"],
    )
    print("Protected or selectable run() calls: NO")
    print("Selectable step calls: NO")
    print("Alternate trajectory variables: NO")
    print("Project modules imported: NO")
    print("Solver constructed: NO")
    print("Numerical steps executed: NO")
    print("Files written: NO")
    print("Git mutations: NONE")
    print("Method superiority authorized: NO")
    print("Numerical shadow audit authorized by inspection: NO")

    return 0


# ============================================================================
# Controlled execution
# ============================================================================

def execute_audit(repo: Path) -> int:
    runner = Path(__file__).resolve()
    execution_commit = verify_runner_commit_shape(
        repo,
        runner,
    )
    source_hashes = verify_source_identities(repo)
    stage_b_summary_reference = load_stage_b_summary(repo)
    archived_budget = load_archived_budget(repo)
    assert_all_output_headers_unique()

    output_root = repo / OUTPUT_ROOT
    existing = (
        sorted(output_root.glob(f"{RUN_PREFIX}*"))
        if output_root.is_dir()
        else []
    )

    if existing:
        raise RuntimeError(
            "a Stage C output already exists; no rerun is allowed: "
            + ", ".join(str(path) for path in existing)
        )

    created = utc_now()
    created_utc = utc_text(created)
    stamp = created.strftime("%Y%m%dT%H%M%SZ")
    run_id = (
        f"{RUN_PREFIX}{stamp}_{execution_commit[:7]}"
    )
    run_directory = output_root / run_id

    if not path_is_git_ignored(repo, run_directory):
        raise RuntimeError(
            "planned Stage C output is not Git-ignored: "
            f"{run_directory.relative_to(repo)}"
        )

    run_directory.mkdir(parents=True, exist_ok=False)

    metadata_path = run_directory / "run_metadata.json"
    state_path = run_directory / "shadow_state_reference.csv"
    shadow_path = run_directory / "shadow_advection_per_step.csv"
    block_path = run_directory / "shadow_advection_time_blocks.csv"
    summary_path = run_directory / "shadow_advection_summary.json"
    report_path = (
        run_directory
        / "STAGE_C_SAME_STATE_ADVECTION_FORM_SHADOW_AUDIT_REPORT.md"
    )
    inventory_path = run_directory / "file_inventory.csv"

    state_writer: IncrementalCsvWriter | None = None
    shadow_writer: IncrementalCsvWriter | None = None
    ledger_handle: object | None = None
    last_completed_loop_index: int | None = None
    failed_gate: str | None = None
    failed_operator: str | None = None
    failed_stage: str | None = None
    state_rows = 0
    shadow_rows_count = 0
    inventory_hash: str | None = None

    metadata: dict[str, object] = {
        "schema_id": (
            "STAGE_C_SAME_STATE_ADVECTION_SHADOW_METADATA_V1"
        ),
        "run_id": run_id,
        "status": "running",
        "classification": None,
        "created_utc": created_utc,
        "completed_utc": None,
        "repository": {
            "name": "Raj-Sanghera-Project",
            "branch": "phase4_validation",
            "design_commit": AUTHORIZED_DESIGN_COMMIT,
            "stage_b_execution_commit": STAGE_B_EXECUTION_COMMIT,
            "stage_b_evidence_commit": STAGE_B_EVIDENCE_COMMIT,
            "execution_commit": execution_commit,
            "runner_path": runner.name,
            "runner_sha256": sha256_file(runner),
            "source_identities": source_hashes,
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
            "forcing_target_rms": FORCING_TARGET_RMS,
            "forcing_sha256": EXPECTED_FORCING_SHA256,
            "accepted_update_operator": (
                "BASE_FD_ADVECTIVE_V1"
            ),
            "stage_state_policy": STAGE_STATE_POLICY,
            "shadow_operator_count": len(OPERATOR_REGISTRY),
            "primary_alternate_count": len(
                PRIMARY_ALTERNATE_IDS
            ),
            "alternate_trajectories_executed": False,
            "protected_solver_run_called": False,
        },
        "operator_registry": [
            dict(item)
            for item in OPERATOR_REGISTRY
        ],
        "expected_counts": {
            "state_reference_rows": EXPECTED_STATE_REFERENCE_ROWS,
            "shadow_rows": EXPECTED_SHADOW_ROWS,
            "time_block_rows": EXPECTED_TIME_BLOCK_ROWS,
            "archive_matches": EXPECTED_ARCHIVE_MATCHES,
        },
        "thresholds": {
            "near_neutral_activity_limit": (
                NEAR_NEUTRAL_ACTIVITY_LIMIT
            ),
            "near_neutral_signed_limit": (
                NEAR_NEUTRAL_SIGNED_LIMIT
            ),
            "near_neutral_maximum_limit": (
                NEAR_NEUTRAL_MAXIMUM_LIMIT
            ),
            "persistence_activity_limit": (
                PERSISTENCE_ACTIVITY_LIMIT
            ),
            "persistence_signed_limit": (
                PERSISTENCE_SIGNED_LIMIT
            ),
            "persistence_maximum_limit": (
                PERSISTENCE_MAXIMUM_LIMIT
            ),
            "minimum_n90_steps": MINIMUM_N90_STEPS,
            "baseline_archive_relative_tolerance": (
                BASELINE_ARCHIVE_RELATIVE_TOLERANCE
            ),
            "baseline_archive_absolute_floor": (
                BASELINE_ARCHIVE_ABSOLUTE_FLOOR
            ),
            "baseline_helper_normalized_tolerance": (
                BASELINE_HELPER_NORMALIZED_TOLERANCE
            ),
            "centered_form_identity_limit": (
                CENTERED_FORM_IDENTITY_LIMIT
            ),
            "skew_identity_limit": SKEW_IDENTITY_LIMIT,
            "pseudo_projection_identity_limit": (
                PSEUDO_PROJECTION_IDENTITY_LIMIT
            ),
            "arakawa_identity_limit": (
                ARAKAWA_IDENTITY_LIMIT
            ),
            "transport_rhs_sign_limit": (
                TRANSPORT_RHS_SIGN_LIMIT
            ),
            "spectral_divergence_limit": (
                SPECTRAL_DIVERGENCE_LIMIT
            ),
            "imaginary_ratio_limit": (
                IMAGINARY_RATIO_LIMIT
            ),
        },
        "forcing": None,
        "progress": {
            "last_completed_loop_index": None,
            "state_reference_rows": 0,
            "shadow_rows": 0,
        },
        "output_files": {
            "run_metadata": metadata_path.name,
            "shadow_state_reference": state_path.name,
            "shadow_advection_per_step": shadow_path.name,
            "shadow_advection_time_blocks": block_path.name,
            "shadow_advection_summary": summary_path.name,
            "report": report_path.name,
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
            "baseline_replacement": False,
            "alternate_trajectory_claims": False,
        },
    }

    atomic_write_json(metadata_path, metadata)

    try:
        from forcing_budget_diagnostic import (
            forcing_budget_snapshot,
        )
        from project.solver.advection_operators import (
            advection_arakawa,
            advection_fd_centered,
            jacobian_arakawa_periodic,
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
                "initial_solver_state",
                "solver did not initialize with exact zero vorticity",
            )

        if (
            int(solver.N) != N
            or not math.isclose(
                float(solver.dt),
                DT,
                rel_tol=0.0,
                abs_tol=0.0,
            )
            or not math.isclose(
                float(solver.nu),
                NU,
                rel_tol=0.0,
                abs_tol=1.0e-15,
            )
        ):
            raise IntegrityFailure(
                "solver_configuration",
                "solver configuration differs from frozen Stage C values",
            )

        solver_environment = freeze_solver_environment(
            solver
        )
        forcing, forcing_statistics = (
            build_rms_matched_multimode_forcing(solver)
        )
        forcing_hash = str(
            forcing_statistics["forcing_sha256"]
        )
        metadata["forcing"] = forcing_statistics
        atomic_write_json(metadata_path, metadata)

        ledger_handle, ledger_reader = open_stage_b_ledger(
            repo
        )

        state_writer = IncrementalCsvWriter(
            state_path,
            STATE_REFERENCE_FIELDNAMES,
        )
        shadow_writer = IncrementalCsvWriter(
            shadow_path,
            SHADOW_FIELDNAMES,
        )

        block_accumulators = new_block_accumulators()
        mechanism_accumulator = new_mechanism_accumulator()
        archive_equivalence = initialize_archive_equivalence()

        baseline_omega = np.zeros(
            (N, N),
            dtype=np.float64,
        )

        per_step_rows_passed = 0
        maximum_stage_b_scalar_difference = 0.0
        sentinel_checks_passed = 0
        maximum_state_mutation_count = 0

        for loop_index in range(STEPS):
            try:
                archived_ledger_row = next(ledger_reader)
            except StopIteration as error:
                raise IntegrityFailure(
                    "stage_b_ledger_row_count",
                    f"Stage B ledger ended before loop_index={loop_index}",
                ) from error

            baseline = baseline_step(
                solver,
                baseline_omega,
                forcing,
                loop_index=loop_index,
            )

            current = np.asarray(
                baseline["current"],
                dtype=np.float64,
            )
            stage = np.asarray(
                baseline["stage"],
                dtype=np.float64,
            )
            filtered = np.asarray(
                baseline["filtered"],
                dtype=np.float64,
            )

            current.setflags(write=False)
            stage.setflags(write=False)

            helper_check = True
            sentinel_check = (
                loop_index in SENTINEL_LOOP_INDICES
            )

            stage1_bundle = compute_shared_state_fields(
                solver,
                current,
                np.asarray(baseline["psi_1"]),
                np.asarray(baseline["u_1"]),
                np.asarray(baseline["v_1"]),
                jacobian_arakawa_periodic=(
                    jacobian_arakawa_periodic
                ),
                helper_advection_fd=advection_fd_centered,
                helper_advection_arakawa=advection_arakawa,
                helper_check=helper_check,
            )
            stage2_bundle = compute_shared_state_fields(
                solver,
                stage,
                np.asarray(baseline["psi_2"]),
                np.asarray(baseline["u_2"]),
                np.asarray(baseline["v_2"]),
                jacobian_arakawa_periodic=(
                    jacobian_arakawa_periodic
                ),
                helper_advection_fd=advection_fd_centered,
                helper_advection_arakawa=advection_arakawa,
                helper_check=helper_check,
            )

            stage1_transports = stage1_bundle["transports"]
            stage2_transports = stage2_bundle["transports"]
            assert isinstance(stage1_transports, Mapping)
            assert isinstance(stage2_transports, Mapping)

            stage1_mechanism = stage1_bundle["mechanism"]
            stage2_mechanism = stage2_bundle["mechanism"]
            assert isinstance(stage1_mechanism, Mapping)
            assert isinstance(stage2_mechanism, Mapping)

            stage1_metrics = stage_operator_metrics(
                current,
                stage1_transports,
            )
            stage2_metrics = stage_operator_metrics(
                stage,
                stage2_transports,
            )
            apply_operator_identity_residuals(
                stage1_metrics,
                stage1_mechanism,
            )
            apply_operator_identity_residuals(
                stage2_metrics,
                stage2_mechanism,
            )

            order_checked = sentinel_check
            order_pass = True

            if order_checked:
                order_pass = sentinel_order_invariance_recompute(
                    solver,
                    current=current,
                    stage=stage,
                    psi_1=np.asarray(baseline["psi_1"]),
                    u_1=np.asarray(baseline["u_1"]),
                    v_1=np.asarray(baseline["v_1"]),
                    psi_2=np.asarray(baseline["psi_2"]),
                    u_2=np.asarray(baseline["u_2"]),
                    v_2=np.asarray(baseline["v_2"]),
                    jacobian_arakawa_periodic=(
                        jacobian_arakawa_periodic
                    ),
                )

                if not order_pass:
                    raise IntegrityFailure(
                        "sentinel_order_invariance",
                        f"operator order changed results at "
                        f"loop_index={loop_index}",
                    )

                sentinel_checks_passed += 1
                verify_solver_environment(
                    solver,
                    solver_environment,
                )

                if sha256_array(forcing) != forcing_hash:
                    raise IntegrityFailure(
                        "forcing_mutation",
                        f"forcing bytes changed at "
                        f"loop_index={loop_index}",
                    )

            shadow_rows = build_shadow_rows(
                baseline,
                stage1_metrics,
                stage2_metrics,
            )

            comparison = compare_stage_b_ledger_row(
                baseline,
                archived_ledger_row,
            )

            if not bool(comparison["passed"]):
                raise IntegrityFailure(
                    "stage_b_per_step_reproduction",
                    f"baseline scalar replay mismatch at "
                    f"loop_index={loop_index}; "
                    f"differences={comparison['differences']}",
                )

            per_step_rows_passed += 1
            maximum_stage_b_scalar_difference = max(
                maximum_stage_b_scalar_difference,
                float(
                    comparison[
                        "maximum_absolute_difference"
                    ]
                ),
            )

            stage1_baseline = stage1_metrics[
                "BASE_FD_ADVECTIVE_V1"
            ]
            stage2_baseline = stage2_metrics[
                "BASE_FD_ADVECTIVE_V1"
            ]
            baseline_stage1_work = float(
                stage1_baseline["rhs_work"]
            )
            baseline_stage2_work = float(
                stage2_baseline["rhs_work"]
            )
            baseline_rk2_work = 0.5 * (
                baseline_stage1_work
                + baseline_stage2_work
            )

            route_stage1_residual = normalized_scalar_residual(
                baseline_stage1_work
                - float(
                    baseline["stage1_advection_work_rate"]
                ),
                (
                    baseline_stage1_work,
                    float(
                        baseline[
                            "stage1_advection_work_rate"
                        ]
                    ),
                ),
            )
            route_stage2_residual = normalized_scalar_residual(
                baseline_stage2_work
                - float(
                    baseline["stage2_advection_work_rate"]
                ),
                (
                    baseline_stage2_work,
                    float(
                        baseline[
                            "stage2_advection_work_rate"
                        ]
                    ),
                ),
            )
            route_rk2_residual = normalized_scalar_residual(
                baseline_rk2_work
                - float(baseline["rk2_advection_rate"]),
                (
                    baseline_rk2_work,
                    float(baseline["rk2_advection_rate"]),
                ),
            )

            if max(
                route_stage1_residual,
                route_stage2_residual,
                route_rk2_residual,
            ) > BASELINE_HELPER_NORMALIZED_TOLERANCE:
                raise IntegrityFailure(
                    "baseline_shadow_route_equivalence",
                    "baseline shadow route differs from baseline "
                    f"update mirror at loop_index={loop_index}",
                    operator_id="BASE_FD_ADVECTIVE_V1",
                )

            state_hashes_unchanged = bool(
                stage1_mechanism["state_unchanged"]
                and stage2_mechanism["state_unchanged"]
            )
            shadow_arrays_finite = bool(
                stage1_mechanism["all_arrays_finite"]
                and stage2_mechanism["all_arrays_finite"]
            )

            if not state_hashes_unchanged:
                maximum_state_mutation_count += 1

            all_integrity_gates_pass = (
                bool(comparison["passed"])
                and state_hashes_unchanged
                and shadow_arrays_finite
                and order_pass
                and all(
                    bool(row["operator_integrity_pass"])
                    for row in shadow_rows
                )
            )

            state_row: dict[str, object] = {
                "loop_index": loop_index,
                "completed_steps": loop_index + 1,
                "physical_time": float(
                    baseline["physical_time"]
                ),
                "forcing_sha256": forcing_hash,
                "omega_current_sha256": str(
                    stage1_bundle["state_hash"]
                ),
                "omega_stage_sha256": str(
                    stage2_bundle["state_hash"]
                ),
                "omega_filtered_sha256": sha256_array(
                    filtered
                ),
                "z_current": float(baseline["z_current"]),
                "z_stage": float(baseline["z_stage"]),
                "z_filtered": float(baseline["z_filtered"]),
                "baseline_stage1_work_replay": (
                    baseline_stage1_work
                ),
                "baseline_stage1_work_archived": float(
                    archived_ledger_row[
                        "stage1_advection_work_rate"
                    ]
                ),
                "baseline_stage1_work_difference": (
                    baseline_stage1_work
                    - float(
                        archived_ledger_row[
                            "stage1_advection_work_rate"
                        ]
                    )
                ),
                "baseline_stage2_work_replay": (
                    baseline_stage2_work
                ),
                "baseline_stage2_work_archived": float(
                    archived_ledger_row[
                        "stage2_advection_work_rate"
                    ]
                ),
                "baseline_stage2_work_difference": (
                    baseline_stage2_work
                    - float(
                        archived_ledger_row[
                            "stage2_advection_work_rate"
                        ]
                    )
                ),
                "baseline_rk2_work_replay": baseline_rk2_work,
                "baseline_rk2_work_archived": float(
                    archived_ledger_row[
                        "rk2_advection_rate"
                    ]
                ),
                "baseline_rk2_work_difference": (
                    baseline_rk2_work
                    - float(
                        archived_ledger_row[
                            "rk2_advection_rate"
                        ]
                    )
                ),
                "baseline_scalar_equivalence_pass": bool(
                    comparison["passed"]
                ),
                "stage1_baseline_helper_checked": helper_check,
                "stage1_baseline_helper_exact_equal": (
                    stage1_mechanism[
                        "baseline_helper_exact_equal"
                    ]
                ),
                "stage1_baseline_helper_normalized_difference": (
                    stage1_mechanism[
                        "baseline_helper_normalized_difference"
                    ]
                ),
                "stage2_baseline_helper_checked": helper_check,
                "stage2_baseline_helper_exact_equal": (
                    stage2_mechanism[
                        "baseline_helper_exact_equal"
                    ]
                ),
                "stage2_baseline_helper_normalized_difference": (
                    stage2_mechanism[
                        "baseline_helper_normalized_difference"
                    ]
                ),
                "sentinel_order_invariance_checked": (
                    order_checked
                ),
                "sentinel_order_invariance_pass": order_pass,
                "all_shadow_state_hashes_unchanged": (
                    state_hashes_unchanged
                ),
                "all_shadow_arrays_finite": (
                    shadow_arrays_finite
                ),
                "all_integrity_gates_pass": (
                    all_integrity_gates_pass
                ),
            }

            mechanism_field_mapping = {
                "centered_velocity_divergence_rms":
                    "centered_velocity_divergence_rms",
                "centered_velocity_divergence_max_abs":
                    "centered_velocity_divergence_max_abs",
                "centered_product_rule_defect_rms":
                    "centered_product_rule_defect_rms",
                "centered_product_rule_defect_max_abs":
                    "centered_product_rule_defect_max_abs",
                "centered_form_identity_residual_rms":
                    "centered_form_identity_residual_rms",
                "normalized_centered_form_identity_residual":
                    "normalized_centered_form_identity_residual",
                "centered_work_identity_residual":
                    "centered_work_identity_residual",
                "centered_divergence_work_term":
                    "centered_divergence_work_term",
                "centered_product_rule_work_term":
                    "centered_product_rule_work_term",
                "spectral_velocity_divergence_rms":
                    "spectral_velocity_divergence_rms",
                "spectral_velocity_divergence_max_abs":
                    "spectral_velocity_divergence_max_abs",
                "normalized_spectral_velocity_divergence":
                    "normalized_spectral_velocity_divergence",
                "pseudo_product_removed_rms":
                    "pseudo_product_removed_rms",
                "pseudo_product_removed_max_abs":
                    "pseudo_product_removed_max_abs",
                "pseudo_product_removed_work":
                    "pseudo_product_removed_work",
                "pseudo_projection_fractional_work_reduction":
                    "pseudo_projection_fractional_work_reduction",
                "pseudo_raw_spectral_fraction_outside_mask":
                    "pseudo_raw_spectral_fraction_outside_mask",
                "arakawa_sign_identity_residual":
                    "arakawa_sign_identity_residual",
                "arakawa_secondary_energy_work":
                    "arakawa_secondary_energy_work",
                "maximum_imaginary_ratio":
                    "maximum_imaginary_ratio",
            }

            for stage_number, mechanism in (
                (1, stage1_mechanism),
                (2, stage2_mechanism),
            ):
                for source_name, output_name in (
                    mechanism_field_mapping.items()
                ):
                    state_row[
                        f"stage{stage_number}_{output_name}"
                    ] = mechanism[source_name]

            if not all_numeric_values_finite(state_row):
                raise IntegrityFailure(
                    "state_reference_row_finite",
                    f"state-reference row contains nonfinite "
                    f"data at loop_index={loop_index}",
                )

            if not all_integrity_gates_pass:
                raise IntegrityFailure(
                    "per_step_integrity",
                    f"per-step integrity failed at "
                    f"loop_index={loop_index}",
                )

            state_writer.write(state_row)
            state_rows += 1

            primary_block, full_block = block_ids_for_time(
                float(baseline["physical_time"])
            )

            for row in shadow_rows:
                shadow_writer.write(row)
                shadow_rows_count += 1
                operator_id = str(row["operator_id"])
                update_block_accumulator(
                    block_accumulators[
                        (primary_block, operator_id)
                    ],
                    row,
                )
                update_block_accumulator(
                    block_accumulators[
                        (full_block, operator_id)
                    ],
                    row,
                )

            update_mechanism_accumulator(
                mechanism_accumulator,
                1,
                stage1_mechanism,
            )
            update_mechanism_accumulator(
                mechanism_accumulator,
                2,
                stage2_mechanism,
            )

            if (
                loop_index % ARCHIVE_MATCH_INTERVAL == 0
                or loop_index == STEPS - 1
            ):
                snapshot = forcing_budget_snapshot(
                    omega=filtered,
                    forcing=forcing,
                    nu=solver.nu,
                    kx=solver.kx,
                    ky=solver.ky,
                    dt=solver.dt,
                    loop_index=loop_index,
                )
                compare_archive_snapshot(
                    loop_index=loop_index,
                    replay=snapshot,
                    archived=archived_budget[loop_index],
                    state=archive_equivalence,
                )

            baseline_omega = np.array(
                filtered,
                dtype=np.float64,
                copy=True,
                order="C",
            )

            last_completed_loop_index = loop_index
            metadata["progress"] = {
                "last_completed_loop_index": loop_index,
                "state_reference_rows": state_rows,
                "shadow_rows": shadow_rows_count,
            }

            if (
                loop_index % PROGRESS_INTERVAL == 0
                or loop_index == STEPS - 1
            ):
                print(
                    "progress",
                    f"t={float(baseline['physical_time']):.3f}",
                    f"Z={float(baseline['z_filtered']):.6e}",
                    (
                        "Rbase="
                        f"{baseline_rk2_work:.6e}"
                    ),
                    (
                        "Rcons="
                        f"{float(shadow_rows[2]['stage_weighted_rhs_work']):.6e}"
                    ),
                    (
                        "Rskew="
                        f"{float(shadow_rows[3]['stage_weighted_rhs_work']):.6e}"
                    ),
                    (
                        "Rps="
                        f"{float(shadow_rows[4]['stage_weighted_rhs_work']):.6e}"
                    ),
                    (
                        "Rarakawa="
                        f"{float(shadow_rows[6]['stage_weighted_rhs_work']):.6e}"
                    ),
                )

            if loop_index % CSV_FLUSH_INTERVAL == 0:
                atomic_write_json(metadata_path, metadata)

        try:
            extra_ledger_row = next(ledger_reader)
        except StopIteration:
            extra_ledger_row = None

        if extra_ledger_row is not None:
            raise IntegrityFailure(
                "stage_b_ledger_row_count",
                "Stage B ledger contains extra rows",
            )

        if ledger_handle is not None:
            ledger_handle.close()
            ledger_handle = None

        state_writer.close()
        shadow_writer.close()
        state_writer = None
        shadow_writer = None

        if state_rows != EXPECTED_STATE_REFERENCE_ROWS:
            raise IntegrityFailure(
                "state_reference_row_count",
                f"state rows={state_rows}, "
                f"expected={EXPECTED_STATE_REFERENCE_ROWS}",
            )

        if shadow_rows_count != EXPECTED_SHADOW_ROWS:
            raise IntegrityFailure(
                "shadow_row_count",
                f"shadow rows={shadow_rows_count}, "
                f"expected={EXPECTED_SHADOW_ROWS}",
            )

        if sentinel_checks_passed != len(
            SENTINEL_LOOP_INDICES
        ):
            raise IntegrityFailure(
                "sentinel_check_count",
                f"sentinel checks={sentinel_checks_passed}, "
                f"expected={len(SENTINEL_LOOP_INDICES)}",
            )

        if maximum_state_mutation_count != 0:
            raise IntegrityFailure(
                "state_mutation_count",
                f"state mutation count={maximum_state_mutation_count}",
            )

        if (
            int(archive_equivalence["match_count"])
            != EXPECTED_ARCHIVE_MATCHES
            or not bool(
                archive_equivalence["all_matches_pass"]
            )
        ):
            raise IntegrityFailure(
                "archive_match_count",
                f"archive equivalence={archive_equivalence}",
            )

        verify_solver_environment(
            solver,
            solver_environment,
        )

        if sha256_array(forcing) != forcing_hash:
            raise IntegrityFailure(
                "final_forcing_identity",
                "forcing bytes changed by the Stage C audit",
            )

        block_rows, structured = finalize_time_blocks(
            block_accumulators
        )

        final_window_integral = float(
            structured["5"]["BASE_FD_ADVECTIVE_V1"][
                "integrated_signed_work"
            ]
        )
        full_run_integral = float(
            structured["6"]["BASE_FD_ADVECTIVE_V1"][
                "integrated_signed_work"
            ]
        )

        final_abs, final_rel, final_pass = (
            archived_scalar_comparison(
                final_window_integral,
                EXPECTED_STAGE_B_FINAL_WINDOW_ADVECTION_INTEGRAL,
            )
        )
        full_abs, full_rel, full_pass = (
            archived_scalar_comparison(
                full_run_integral,
                EXPECTED_STAGE_B_FULL_RUN_ADVECTION_INTEGRAL,
            )
        )

        if not final_pass or not full_pass:
            raise IntegrityFailure(
                "baseline_integrated_work_reference",
                "baseline integrated-work reference mismatch: "
                f"final=(abs={final_abs}, rel={final_rel}), "
                f"full=(abs={full_abs}, rel={full_rel})",
            )

        classification = classify_shadow_response(
            structured
        )

        if classification == "NUMERICAL INTEGRITY FAILURE":
            raise IntegrityFailure(
                "stage_c_classification",
                f"Stage C classification is {classification}",
            )

        write_csv_table(
            block_path,
            TIME_BLOCK_FIELDNAMES,
            block_rows,
        )
        mechanism_summary = summarize_mechanisms(
            mechanism_accumulator
        )

        baseline_reproduction = {
            "step_count": STEPS,
            "per_step_rows_passed": per_step_rows_passed,
            "maximum_stage_b_scalar_absolute_difference": (
                maximum_stage_b_scalar_difference
            ),
            "final_window_integral": final_window_integral,
            "final_window_reference": (
                EXPECTED_STAGE_B_FINAL_WINDOW_ADVECTION_INTEGRAL
            ),
            "final_window_absolute_difference": final_abs,
            "final_window_relative_difference": final_rel,
            "full_run_integral": full_run_integral,
            "full_run_reference": (
                EXPECTED_STAGE_B_FULL_RUN_ADVECTION_INTEGRAL
            ),
            "full_run_absolute_difference": full_abs,
            "full_run_relative_difference": full_rel,
            "sentinel_checks_passed": sentinel_checks_passed,
            "state_mutation_count": maximum_state_mutation_count,
        }

        completed_utc = utc_text()
        summary = {
            "schema_id": (
                "STAGE_C_SAME_STATE_ADVECTION_SHADOW_SUMMARY_V1"
            ),
            "run_id": run_id,
            "classification": classification,
            "created_utc": created_utc,
            "completed_utc": completed_utc,
            "repository": metadata["repository"],
            "configuration": metadata["configuration"],
            "forcing": forcing_statistics,
            "operator_registry": metadata[
                "operator_registry"
            ],
            "same_state_policy": {
                "baseline_current_state_only": True,
                "baseline_rk2_stage_state_only": True,
                "shadow_results_entered_update": False,
                "alternate_trajectories_executed": False,
            },
            "counts": {
                "state_reference_rows": state_rows,
                "shadow_rows": shadow_rows_count,
                "time_block_rows": len(block_rows),
                "archive_matches": archive_equivalence[
                    "match_count"
                ],
            },
            "baseline_reproduction": baseline_reproduction,
            "archive_equivalence": archive_equivalence,
            "time_blocks": structured,
            "final_window": structured["5"],
            "full_run": structured["6"],
            "mechanism_diagnostics": mechanism_summary,
            "integrity": {
                "all_gates_passed": True,
                "failed_gate_count": 0,
                "failed_gate": None,
                "last_completed_loop_index": (
                    last_completed_loop_index
                ),
            },
            "limitations": {
                "local_same_state_operator_diagnostic": True,
                "method_superiority": False,
                "formal_temporal_convergence": False,
                "formal_spatial_convergence": False,
                "physical_validation": False,
                "alternate_trajectory_behavior": False,
                "turbulence": False,
                "cascade": False,
                "inertial_range": False,
                "k_minus_3": False,
                "production_readiness": False,
                "unique_physical_causation": False,
            },
            "stage_b_reference": {
                "summary": stage_b_summary_reference,
            },
            "outputs": metadata["output_files"],
        }

        atomic_write_json(summary_path, summary)
        atomic_write_text(
            report_path,
            render_stage_c_report(
                run_id=run_id,
                execution_commit=execution_commit,
                classification=classification,
                structured=structured,
                archive_equivalence=archive_equivalence,
                mechanism_summary=mechanism_summary,
                baseline_reproduction=baseline_reproduction,
            ),
        )

        metadata["status"] = "completed"
        metadata["classification"] = classification
        metadata["completed_utc"] = completed_utc
        metadata["progress"] = {
            "last_completed_loop_index": (
                last_completed_loop_index
            ),
            "state_reference_rows": state_rows,
            "shadow_rows": shadow_rows_count,
        }
        atomic_write_json(metadata_path, metadata)

        inventory_hash = write_inventory(
            run_directory,
            inventory_path,
            (
                metadata_path,
                state_path,
                shadow_path,
                block_path,
                summary_path,
                report_path,
            ),
        )

        observed_outputs = sorted(
            path.name
            for path in run_directory.iterdir()
            if path.is_file()
        )

        if observed_outputs != sorted(OUTPUT_FILENAMES):
            raise IntegrityFailure(
                "output_file_set",
                f"output files={observed_outputs}, "
                f"expected={sorted(OUTPUT_FILENAMES)}",
            )

        print()
        print("=" * 72)
        print(
            "STAGE C SAME-STATE ADVECTION-FORM "
            "SHADOW AUDIT: COMPLETE"
        )
        print("=" * 72)
        print("Baseline trajectory replay: PASS")
        print("Baseline per-step ledger reproduction: PASS")
        print(
            "Archived comparison points:",
            f"{archive_equivalence['match_count']} / "
            f"{EXPECTED_ARCHIVE_MATCHES} PASS",
        )
        print("Baseline steps:", state_rows)
        print("Shadow methods:", len(OPERATOR_REGISTRY))
        print("Shadow rows:", shadow_rows_count)
        print("Time-block rows:", len(block_rows))
        print("Accepted trajectory changed by shadows: NO")
        print("Alternate trajectories executed: NO")
        print("Protected solver run loop called: NO")
        print("Method superiority authorized: NO")
        print("Classification:", classification)
        print("Run directory:", run_directory)
        print("File inventory SHA256:", inventory_hash)

        return 0

    except BaseException as error:
        if isinstance(error, IntegrityFailure):
            failed_gate = error.gate
            failed_operator = error.operator_id
            failed_stage = error.stage
        else:
            failed_gate = type(error).__name__

        for writer in (state_writer, shadow_writer):
            if writer is not None:
                try:
                    writer.close()
                except Exception:
                    pass

        if ledger_handle is not None:
            try:
                ledger_handle.close()
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
        metadata["failed_operator"] = failed_operator
        metadata["failed_stage"] = failed_stage
        metadata["progress"] = {
            "last_completed_loop_index": (
                last_completed_loop_index
            ),
            "state_reference_rows": state_rows,
            "shadow_rows": shadow_rows_count,
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
                    state_path,
                    shadow_path,
                    block_path,
                    summary_path,
                    report_path,
                ),
            )
        except Exception:
            inventory_hash = None

        print()
        print("STAGE C SAME-STATE SHADOW AUDIT FAILURE")
        print("Failed gate:", failed_gate)

        if failed_operator is not None:
            print("Failed operator:", failed_operator)

        if failed_stage is not None:
            print("Failed stage:", failed_stage)

        print("Partial evidence preserved at:", run_directory)
        print("Do not rerun automatically.")

        if inventory_hash is not None:
            print("Partial inventory SHA256:", inventory_hash)

        raise


# ============================================================================
# Command line
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the controlled Stage C same-state "
            "advection-form shadow audit."
        )
    )
    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help=(
            "inspect source without numerical execution, or run the "
            "single controlled same-state audit"
        ),
    )
    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent

    if arguments.mode == "inspect":
        return inspect_runner(repo)

    if arguments.mode == "run":
        return execute_audit(repo)

    raise RuntimeError(
        f"unsupported mode: {arguments.mode!r}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
