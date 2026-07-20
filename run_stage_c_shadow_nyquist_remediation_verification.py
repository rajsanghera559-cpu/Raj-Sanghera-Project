"""
Controlled Stage C shadow-only Nyquist remediation verification.

Usage:
    python -B run_stage_c_shadow_nyquist_remediation_verification.py inspect
    python -B run_stage_c_shadow_nyquist_remediation_verification.py run

The inspection path verifies the source and frozen repository identities without
importing project modules, constructing a solver, writing files, executing a
numerical timestep, or mutating Git state.

The run path reproduces the accepted centered-advection baseline through loop
index 3059 only. It reproduces the historical raw-ik imaginary-ratio failure at
loop index 3059, stage 2, evaluates a local Nyquist-zeroed real-compatible
shadow route on the identical states, compares real derivatives, transports,
and shadow work, writes one focused evidence bundle, and stops.

It does not execute a full Stage C audit, advance an alternate trajectory,
modify the protected solver, or produce an operator-form-specificity
classification.
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

RUNNER_NAME = (
    "run_stage_c_shadow_nyquist_remediation_verification.py"
)

AUTHORIZED_DESIGN_COMMIT = (
    "b276d48e18fa7dafdae6f9f076721e2238aa1f45"
)

REMEDIATION_DESIGN_PATH = Path(
    "STAGE_C_SHADOW_DIAGNOSTIC_NYQUIST_REMEDIATION_DESIGN.md"
)
EXPECTED_REMEDIATION_DESIGN_SHA256 = (
    "62F4B615F7CB9DC65402FD99FC8F72634F27177222CCCA3BD3FCD121991F0787"
)

LOCALIZATION_REPORT_PATH = Path(
    "STAGE_C_NYQUIST_FAILURE_LOCALIZATION_EVIDENCE_REPORT.md"
)
EXPECTED_LOCALIZATION_REPORT_SHA256 = (
    "EEFB82BFBC74C5E2EEC75C816D0A8F4C56601921E3EAEFD1D5B820B5F74BBE7D"
)

LOCALIZATION_DESIGN_PATH = Path(
    "STAGE_C_NYQUIST_IMAGINARY_RATIO_FAILURE_LOCALIZATION_AND_REMEDIATION_DESIGN.md"
)
EXPECTED_LOCALIZATION_DESIGN_SHA256 = (
    "809196A724D4CD94C936A6A96BB7A6B39717A6667EB57D932ED023C6469EC1A2"
)

ORIGINAL_STAGE_C_RUNNER_PATH = Path(
    "run_stage_c_same_state_advection_shadow_audit.py"
)
EXPECTED_ORIGINAL_STAGE_C_RUNNER_SHA256 = (
    "5E13CF350DF5356E1E8E44F0D921A7C92FFDD6830978466DFA5B6648818F4BC1"
)

LOCALIZATION_RUNNER_PATH = Path(
    "run_stage_c_nyquist_failure_localization.py"
)
EXPECTED_LOCALIZATION_RUNNER_SHA256 = (
    "945CD7D940CBAA823A15AC6A3E5885F97ED4E46AFE4919C40181F3FCA6B9BFA0"
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

STAGE_B_EVIDENCE_DIRECTORY = (
    Path("experiments")
    / "forcing_budget_stage_b_ledger"
    / "stage_b_exact_operator_ledger_20260720T063420Z_5c464c2"
)
STAGE_B_LEDGER_PATH = (
    STAGE_B_EVIDENCE_DIRECTORY / "operator_ledger_per_step.csv"
)
EXPECTED_STAGE_B_LEDGER_SHA256 = (
    "5EABDFB33B932089910B61C119A223EED83D4EF9247593C3B02DA68B1D74B115"
)

PARTIAL_STAGE_C_DIRECTORY = (
    Path("experiments")
    / "advection_form_shadow_audit"
    / "stage_c_same_state_advection_shadow_20260720T210332Z_c6b2cac"
)
PARTIAL_STAGE_C_HASHES = {
    "run_metadata.json":
        "E31762AE53BE53D6BCCC291296BCD1FC5A3571D605A327EB381E20FCC82DD400",
    "shadow_state_reference.csv":
        "DE01C0F7C0502B3A4917A4FDC70F6295D06A910D8CF60240351C602AF9E32A36",
    "shadow_advection_per_step.csv":
        "08D540C4170A0E7FC326E02E4D172945188A296E896330A60C77DB4A1FAB4944",
    "file_inventory.csv":
        "E76B55EFD5D8C8FF16BA044856D3D9AFEF39219937C754C292D48D8D12227C09",
}

LOCALIZATION_EVIDENCE_DIRECTORY = (
    Path("experiments")
    / "advection_form_shadow_audit_localization"
    / "stage_c_nyquist_failure_localization_20260720T215450Z_d7e4247"
)
EXPECTED_LOCALIZATION_INVENTORY_SHA256 = (
    "9FF4E524A0A05ED2E2CC5214E5EE4075254D11852F8CECF895C1F22F87328D5C"
)

EXPECTED_FORCING_SHA256 = (
    "504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB"
)


# ============================================================================
# Frozen numerical configuration and remediation policy
# ============================================================================

N = 64
RE = 1000
NU = 1.0 / RE
DT = 0.005
FULL_STAGE_C_STEPS = 20001

LAST_PASSING_LOOP_INDEX = 3058
STOP_LOOP_INDEX = 3059
EXPECTED_REPLAY_ROWS = 3060
EXPECTED_PARTIAL_ROWS = 3059
EXPECTED_STAGE_B_ROWS_COMPARED = 3060

EXPECTED_FAILURE_STAGE = 2
EXPECTED_FAILURE_QUANTITY = (
    "omega_gradient_imaginary_ratio"
)
EXPECTED_RAW_FAILURE_RATIO = (
    1.0021037272233111e-13
)
EXPECTED_REAL_COMPATIBLE_RATIO = (
    7.983551748537457e-16
)

EXPECTED_LAST_PASSING_TIME = 15.295
EXPECTED_LAST_PASSING_Z = 0.00247703643047042
EXPECTED_LAST_PASSING_BASELINE_WORK = (
    1.7413851867416074e-07
)
EXPECTED_LAST_PASSING_STAGE1_RATIO = (
    3.2467038768288357e-15
)
EXPECTED_LAST_PASSING_STAGE2_RATIO = (
    9.955198638157299e-14
)

IMAGINARY_RATIO_LIMIT = 1.0e-13
RESIDUAL_FLOOR = 1.0e-30
SPECTRAL_POWER_FLOOR = 1.0e-300

BASELINE_COMPARE_RELATIVE_TOLERANCE = 1.0e-12
BASELINE_COMPARE_ABSOLUTE_TOLERANCE = 1.0e-18

RAW_RATIO_REPRODUCTION_RELATIVE_TOLERANCE = 1.0e-12
RAW_RATIO_REPRODUCTION_ABSOLUTE_TOLERANCE = 1.0e-18

REAL_DERIVATIVE_RELATIVE_LIMIT = 1.0e-10
REAL_TRANSPORT_RELATIVE_LIMIT = 1.0e-10
WORK_ABSOLUTE_LIMIT = 1.0e-14
WORK_RELATIVE_LIMIT = 1.0e-6

FORCING_TARGET_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14

OUTPUT_ROOT = (
    Path("experiments")
    / "advection_form_shadow_audit_remediation"
)
RUN_PREFIX = (
    "stage_c_shadow_nyquist_remediation_verification_"
)

FORCING_TERMS = (
    "sin(2X)cos(2Y)",
    "0.75*sin(3X)cos(Y)",
    "0.50*sin(X)cos(4Y)",
    "0.35*cos(4X-2Y)",
)

QUANTITY_IDS = (
    "omega_gradient_imaginary_ratio",
    "projected_baseline_transport_imaginary_ratio",
    "projected_pseudo_transport_imaginary_ratio",
    "u_x_gradient_imaginary_ratio",
    "v_y_gradient_imaginary_ratio",
)

OPERATOR_IDS = (
    "BASE_FD_ADVECTIVE_V1",
    "SHADOW_FD_ADVECTIVE_PROJECTED_V1",
    "SHADOW_FD_CONSERVATIVE_V1",
    "SHADOW_FD_SKEW_V1",
    "SHADOW_PS_ADVECTIVE_RAW_V1",
    "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
    "SHADOW_ARAKAWA_V1",
)

PSEUDO_OPERATOR_IDS = (
    "SHADOW_PS_ADVECTIVE_RAW_V1",
    "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
)

PRIMARY_CONCLUSIONS = (
    "SHADOW NYQUIST REMEDIATION CONSISTENT WITH LOCALIZATION",
    "SHADOW NYQUIST REMEDIATION NOT CONSISTENT WITH LOCALIZATION",
    "SHADOW NYQUIST REMEDIATION INCONCLUSIVE",
    "NUMERICAL INTEGRITY FAILURE",
)

EFFECT_CONCLUSIONS = (
    "REAL SHADOW WORK PRESERVED UNDER REMEDIATION",
    "REAL SHADOW WORK MATERIALLY CHANGED UNDER REMEDIATION",
    "REAL SHADOW WORK EFFECT INCONCLUSIVE",
)


# ============================================================================
# Output schemas
# ============================================================================

TRACE_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "stage",
    "route",
    "quantity_id",
    "dominant_direction",
    "real_rms",
    "imaginary_rms",
    "imaginary_ratio",
    "real_max_abs",
    "imaginary_max_abs",
    "ratio_denominator",
    "denominator_uses_floor",
    "threshold",
    "threshold_pass",
    "is_historical_failure",
    "raw_to_real_compatible_real_difference_rms",
    "raw_to_real_compatible_real_difference_max_abs",
    "raw_to_real_compatible_real_difference_relative",
    "raw_to_real_compatible_real_cosine_similarity",
    "relevant_nyquist_power_fraction",
    "raw_hermitian_residual",
    "real_compatible_hermitian_residual",
    "state_sha256",
)

WORK_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "stage",
    "operator_id",
    "raw_transport_rms",
    "real_compatible_transport_rms",
    "transport_difference_rms",
    "transport_difference_max_abs",
    "transport_difference_relative",
    "transport_cosine_similarity",
    "raw_work",
    "real_compatible_work",
    "work_absolute_difference",
    "work_relative_difference",
    "work_sign_changed",
    "near_zero_character_changed",
    "material_real_work_change",
)

INVENTORY_FIELDNAMES = (
    "relative_path",
    "bytes",
    "sha256",
    "inventory_note",
)

OUTPUT_FILENAMES = (
    "run_metadata.json",
    "raw_and_real_compatible_trace.csv",
    "real_work_comparison.csv",
    "remediation_summary.json",
    "STAGE_C_SHADOW_NYQUIST_REMEDIATION_VERIFICATION_REPORT.md",
    "file_inventory.csv",
)


# ============================================================================
# Exceptions and generic utilities
# ============================================================================

class IntegrityFailure(RuntimeError):
    def __init__(
        self,
        gate: str,
        message: str,
        *,
        quantity_id: str | None = None,
        stage: int | None = None,
    ) -> None:
        super().__init__(message)
        self.gate = gate
        self.quantity_id = quantity_id
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
    array = np.ascontiguousarray(
        np.asarray(value, dtype=np.float64)
    )
    return sha256_bytes(array.tobytes(order="C"))


def field_rms(value: object) -> float:
    array = np.asarray(value, dtype=np.float64)
    return float(np.sqrt(np.mean(array * array)))


def complex_rms(value: object) -> float:
    array = np.asarray(value, dtype=np.complex128)
    return float(np.sqrt(np.mean(np.abs(array) ** 2)))


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


def cosine_similarity(
    first: object,
    second: object,
) -> float:
    first_array = np.asarray(
        first,
        dtype=np.float64,
    ).ravel()
    second_array = np.asarray(
        second,
        dtype=np.float64,
    ).ravel()
    denominator = float(
        np.linalg.norm(first_array)
        * np.linalg.norm(second_array)
    )
    if denominator <= RESIDUAL_FLOOR:
        return (
            1.0
            if np.array_equal(first_array, second_array)
            else 0.0
        )
    return float(
        np.dot(first_array, second_array) / denominator
    )


def scalar_matches(
    observed: float,
    expected: float,
    *,
    relative: float = BASELINE_COMPARE_RELATIVE_TOLERANCE,
    absolute: float = BASELINE_COMPARE_ABSOLUTE_TOLERANCE,
) -> bool:
    return math.isclose(
        float(observed),
        float(expected),
        rel_tol=relative,
        abs_tol=absolute,
    )


def relative_difference(
    first: float,
    second: float,
    *,
    floor: float = RESIDUAL_FLOOR,
) -> float:
    return (
        abs(float(first) - float(second))
        / max(
            abs(float(first)),
            abs(float(second)),
            floor,
        )
    )


def all_numeric_values_finite(
    row: Mapping[str, object],
) -> bool:
    for value in row.values():
        if (
            value is None
            or isinstance(value, (str, bool))
        ):
            continue
        if isinstance(
            value,
            (int, float, np.integer, np.floating),
        ):
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
            value
            for value in set(observed)
            if observed.count(value) > 1
        )
        raise RuntimeError(
            f"duplicate headers in {name}: {duplicates}"
        )


def assert_all_output_headers_unique() -> None:
    assert_unique_headers(
        "raw_and_real_compatible_trace.csv",
        TRACE_FIELDNAMES,
    )
    assert_unique_headers(
        "real_work_comparison.csv",
        WORK_FIELDNAMES,
    )
    assert_unique_headers(
        "file_inventory.csv",
        INVENTORY_FIELDNAMES,
    )


def atomic_write_text(
    path: Path,
    text: str,
) -> None:
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


def atomic_write_json(
    path: Path,
    value: object,
) -> None:
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
    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        return json.load(handle)


def read_csv_rows(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        assert_unique_headers(
            path.name,
            tuple(reader.fieldnames or ()),
        )
        return list(reader)


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
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


# ============================================================================
# Git and identity helpers
# ============================================================================

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


def git_read(
    repo: Path,
    *args: str,
) -> str:
    return str(
        git_process(repo, *args).stdout
    ).strip()


def git_bytes(
    repo: Path,
    *args: str,
) -> bytes:
    return bytes(
        git_process(
            repo,
            *args,
            text=False,
        ).stdout
    )


def path_is_git_ignored(
    repo: Path,
    path: Path,
) -> bool:
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


def verify_file_hash(
    repo: Path,
    relative_path: Path,
    expected_sha256: str,
) -> str:
    path = repo / relative_path
    if not path.is_file():
        raise RuntimeError(
            f"required file is missing: "
            f"{relative_path.as_posix()}"
        )
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise RuntimeError(
            f"SHA256 mismatch for "
            f"{relative_path.as_posix()}: "
            f"observed={observed}, "
            f"expected={expected_sha256}"
        )
    return observed


def verify_git_blob(
    repo: Path,
    relative_path: Path,
    expected_blob: str,
) -> str:
    relative = relative_path.as_posix()
    working = git_read(
        repo,
        "hash-object",
        f"--path={relative}",
        "--",
        relative,
    )
    committed = git_read(
        repo,
        "rev-parse",
        f"HEAD:{relative}",
    )
    if (
        working != expected_blob
        or committed != expected_blob
    ):
        raise RuntimeError(
            f"Git blob mismatch for {relative}: "
            f"working={working}, "
            f"committed={committed}, "
            f"expected={expected_blob}"
        )
    return working


def verify_partial_stage_c_evidence(
    repo: Path,
) -> dict[str, str]:
    directory = repo / PARTIAL_STAGE_C_DIRECTORY
    if not directory.is_dir():
        raise RuntimeError(
            "preserved partial Stage C directory is missing"
        )
    observed: dict[str, str] = {}
    for name, expected in PARTIAL_STAGE_C_HASHES.items():
        path = directory / name
        if not path.is_file():
            raise RuntimeError(
                f"preserved partial file is missing: {path}"
            )
        value = sha256_file(path)
        if value != expected:
            raise RuntimeError(
                f"preserved partial SHA256 mismatch for "
                f"{path}: observed={value}, expected={expected}"
            )
        observed[name] = value
    actual_files = sorted(
        path.name
        for path in directory.iterdir()
        if path.is_file()
    )
    expected_files = sorted(PARTIAL_STAGE_C_HASHES)
    if actual_files != expected_files:
        raise RuntimeError(
            "preserved partial file set changed: "
            f"observed={actual_files}, "
            f"expected={expected_files}"
        )
    return observed


def verify_localization_evidence(
    repo: Path,
) -> dict[str, str]:
    directory = repo / LOCALIZATION_EVIDENCE_DIRECTORY
    if not directory.is_dir():
        raise RuntimeError(
            "focused localization evidence directory is missing"
        )
    inventory_path = directory / "file_inventory.csv"
    if sha256_file(inventory_path) != (
        EXPECTED_LOCALIZATION_INVENTORY_SHA256
    ):
        raise RuntimeError(
            "focused localization inventory hash mismatch"
        )
    inventory_rows = read_csv_rows(inventory_path)
    recorded = {
        str(row["relative_path"]): str(
            row.get("sha256", "")
        ).strip().upper()
        for row in inventory_rows
        if str(row.get("sha256", "")).strip()
    }
    actual_files = sorted(
        path.name
        for path in directory.iterdir()
        if path.is_file()
    )
    expected_files = sorted(
        (
            "file_inventory.csv",
            "imaginary_ratio_trace.csv",
            "localization_summary.json",
            "nyquist_spectral_content.csv",
            "raw_vs_nyquist_zeroed.csv",
            "run_metadata.json",
            "STAGE_C_NYQUIST_FAILURE_LOCALIZATION_REPORT.md",
        )
    )
    if actual_files != expected_files:
        raise RuntimeError(
            "focused localization evidence file set changed"
        )
    observed = {
        "file_inventory.csv":
            EXPECTED_LOCALIZATION_INVENTORY_SHA256
    }
    for name in expected_files:
        path = directory / name
        value = sha256_file(path)
        if name != "file_inventory.csv":
            if recorded.get(name) != value:
                raise RuntimeError(
                    "focused localization inventory-recorded "
                    f"hash mismatch for {name}"
                )
        observed[name] = value
    summary = read_json(
        directory / "localization_summary.json"
    )
    if summary.get("primary_conclusion") != (
        "FAILURE CONSISTENT WITH NYQUIST "
        "DERIVATIVE CONVENTION"
    ):
        raise RuntimeError(
            "focused localization primary conclusion changed"
        )
    if summary.get("effect_conclusion") != (
        "NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT"
    ):
        raise RuntimeError(
            "focused localization effect conclusion changed"
        )
    return observed


def verify_source_identities(
    repo: Path,
) -> dict[str, str]:
    identities = {
        "remediation_design": verify_file_hash(
            repo,
            REMEDIATION_DESIGN_PATH,
            EXPECTED_REMEDIATION_DESIGN_SHA256,
        ),
        "localization_report": verify_file_hash(
            repo,
            LOCALIZATION_REPORT_PATH,
            EXPECTED_LOCALIZATION_REPORT_SHA256,
        ),
        "localization_design": verify_file_hash(
            repo,
            LOCALIZATION_DESIGN_PATH,
            EXPECTED_LOCALIZATION_DESIGN_SHA256,
        ),
        "original_stage_c_runner": verify_file_hash(
            repo,
            ORIGINAL_STAGE_C_RUNNER_PATH,
            EXPECTED_ORIGINAL_STAGE_C_RUNNER_SHA256,
        ),
        "localization_runner": verify_file_hash(
            repo,
            LOCALIZATION_RUNNER_PATH,
            EXPECTED_LOCALIZATION_RUNNER_SHA256,
        ),
        "spectral_solver": verify_file_hash(
            repo,
            SPECTRAL_SOLVER_PATH,
            EXPECTED_SPECTRAL_SOLVER_SHA256,
        ),
        "advection_operators_blob": verify_git_blob(
            repo,
            ADVECTION_OPERATORS_PATH,
            EXPECTED_ADVECTION_OPERATORS_BLOB,
        ),
        "selectable_solver_blob": verify_git_blob(
            repo,
            SELECTABLE_SOLVER_PATH,
            EXPECTED_SELECTABLE_SOLVER_BLOB,
        ),
        "stage_b_ledger": verify_file_hash(
            repo,
            STAGE_B_LEDGER_PATH,
            EXPECTED_STAGE_B_LEDGER_SHA256,
        ),
    }
    for name, value in (
        verify_partial_stage_c_evidence(repo).items()
    ):
        identities[f"partial/{name}"] = value
    for name, value in (
        verify_localization_evidence(repo).items()
    ):
        identities[f"localization/{name}"] = value
    return identities


def verify_inspection_repository_state(
    repo: Path,
    runner: Path,
) -> None:
    branch = git_read(
        repo,
        "branch",
        "--show-current",
    )
    if branch != "phase4_validation":
        fail(
            f"active branch is {branch!r}, "
            "expected 'phase4_validation'"
        )
    head = git_read(repo, "rev-parse", "HEAD")
    if head != AUTHORIZED_DESIGN_COMMIT:
        fail(
            f"HEAD is {head}, expected remediation "
            f"design checkpoint {AUTHORIZED_DESIGN_COMMIT}"
        )
    remote = git_read(
        repo,
        "rev-parse",
        "origin/phase4_validation",
    )
    if remote != head:
        fail(
            f"origin/phase4_validation is {remote}, "
            f"expected {head}"
        )
    status = [
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
    if status != expected:
        fail(
            f"Git status is {status!r}, "
            f"expected {expected!r}"
        )


def verify_runner_commit_shape(
    repo: Path,
    runner: Path,
) -> str:
    branch = git_read(
        repo,
        "branch",
        "--show-current",
    )
    if branch != "phase4_validation":
        raise RuntimeError(
            "active branch is not phase4_validation"
        )
    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise RuntimeError(
            f"working tree is not clean: {status}"
        )
    head = git_read(repo, "rev-parse", "HEAD")
    parent = git_read(repo, "rev-parse", "HEAD^")
    if parent != AUTHORIZED_DESIGN_COMMIT:
        raise RuntimeError(
            f"runner commit parent is {parent}, "
            f"expected {AUTHORIZED_DESIGN_COMMIT}"
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
    if (
        git_bytes(
            repo,
            "show",
            f"HEAD:{runner.name}",
        )
        != runner.read_bytes()
    ):
        raise RuntimeError(
            "working runner bytes differ from committed bytes"
        )
    remote = git_read(
        repo,
        "rev-parse",
        "origin/phase4_validation",
    )
    if remote != head:
        raise RuntimeError(
            f"remote branch is {remote}, expected {head}"
        )
    return head


# ============================================================================
# Static inspection
# ============================================================================

FORBIDDEN_CALL_NAMES = {
    "step_once_selectable",
    "run_selectable_diagnostic",
}

FORBIDDEN_CLASSIFICATION_STRINGS = {
    "SHADOW SET SUPPORTS CURRENT-" + "FORM SPECIFICITY",
    "NONZERO WORK PERSISTS ACROSS MULTIPLE " + "FORMS",
    "SHADOW RESPONSE IS FORM-DEPENDENT AND " + "MIXED",
    "SHADOW SET DOES NOT SHOW STRONG FORM " + "SEPARATION",
}


def inspect_ast(
    source: str,
) -> dict[str, object]:
    tree = ast.parse(
        source,
        filename=RUNNER_NAME,
    )
    parent: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    def containing_function(
        node: ast.AST,
    ) -> str | None:
        current = parent.get(node)
        while current is not None:
            if isinstance(
                current,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                return current.name
            current = parent.get(current)
        return None

    project_imports: list[str] = []
    constructor_calls = 0
    forbidden_calls: list[str] = []
    run_calls: list[str] = []
    solver_wavenumber_assignments: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("project."):
                if containing_function(node) != (
                    "execute_remediation"
                ):
                    raise RuntimeError(
                        "project import outside run path: "
                        f"{module}"
                    )
                project_imports.append(module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id == "SpectralSolver":
                    constructor_calls += 1
                if node.func.id in FORBIDDEN_CALL_NAMES:
                    forbidden_calls.append(node.func.id)
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in FORBIDDEN_CALL_NAMES:
                    forbidden_calls.append(node.func.attr)
                if node.func.attr == "run":
                    if not (
                        isinstance(
                            node.func.value,
                            ast.Name,
                        )
                        and node.func.value.id == "subprocess"
                    ):
                        run_calls.append("run")
        elif isinstance(
            node,
            (ast.Assign, ast.AnnAssign, ast.AugAssign),
        ):
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets.extend(node.targets)
            else:
                targets.append(node.target)
            for target in targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "solver"
                    and target.attr in {"kx", "ky"}
                ):
                    solver_wavenumber_assignments.append(
                        f"solver.{target.attr}"
                    )

    if constructor_calls != 1:
        raise RuntimeError(
            f"SpectralSolver constructor calls="
            f"{constructor_calls}, expected=1"
        )
    if forbidden_calls:
        raise RuntimeError(
            f"forbidden selectable calls: {forbidden_calls}"
        )
    if run_calls:
        raise RuntimeError(
            "protected or selectable run() call is present"
        )
    if solver_wavenumber_assignments:
        raise RuntimeError(
            "solver wavenumber mutation assignments present: "
            f"{solver_wavenumber_assignments}"
        )

    for text in FORBIDDEN_CLASSIFICATION_STRINGS:
        if text in source:
            raise RuntimeError(
                "full Stage C classification string present: "
                f"{text}"
            )

    required_fragments = (
        "STOP_LOOP_INDEX = 3059",
        "range(STOP_LOOP_INDEX + 1)",
        "kx_real_compatible = np.array(",
        "ky_real_compatible = np.array(",
        "route=\"raw\"",
        "route=\"real_compatible\"",
        "Full Stage C rerun authorized: NO",
        "Focused remediation numerical execution "
        "authorized by inspection: NO",
    )
    missing = [
        fragment
        for fragment in required_fragments
        if fragment not in source
    ]
    if missing:
        raise RuntimeError(
            f"required source fragments missing: {missing}"
        )

    return {
        "project_imports": sorted(project_imports),
        "spectral_solver_constructor_calls":
            constructor_calls,
        "forbidden_calls": forbidden_calls,
        "run_calls": run_calls,
        "solver_wavenumber_assignments":
            solver_wavenumber_assignments,
    }


def inspect_runner(
    repo: Path,
) -> int:
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
        compile(source, str(runner), "exec")
    except (
        UnicodeDecodeError,
        SyntaxError,
    ) as error:
        fail(f"runner source is invalid: {error}")

    verify_inspection_repository_state(repo, runner)
    identities = verify_source_identities(repo)
    assert_all_output_headers_unique()
    ast_summary = inspect_ast(source)

    if STOP_LOOP_INDEX != 3059:
        fail("focused stop index differs from 3059")
    if LAST_PASSING_LOOP_INDEX != 3058:
        fail("last passing index differs from 3058")
    if IMAGINARY_RATIO_LIMIT != 1.0e-13:
        fail("historical threshold was changed")
    if EXPECTED_REPLAY_ROWS != 3060:
        fail("expected replay-row count differs")
    if len(QUANTITY_IDS) != 5:
        fail("five-quantity registry differs")
    if len(OPERATOR_IDS) != 7:
        fail("seven-operator registry differs")
    if len(OUTPUT_FILENAMES) != 6:
        fail("focused output-file count differs")

    print()
    print("=" * 72)
    print(
        "STAGE C SHADOW NYQUIST REMEDIATION "
        "RUNNER INSPECTION: PASS"
    )
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", sha256_bytes(raw))
    print("Design commit:", AUTHORIZED_DESIGN_COMMIT)
    print(
        "Remediation design SHA256:",
        identities["remediation_design"],
    )
    print(
        "Localization evidence-report SHA256:",
        identities["localization_report"],
    )
    print("Configuration: N64, Re1000, dt0.005")
    print("Authorized replay range: loop index 0 through 3059")
    print("Hard stop loop index: 3059")
    print("Expected replay rows: 3060")
    print("Historical raw route: PRESENT")
    print("Real-compatible Nyquist-zeroed route: PRESENT")
    print("Both routes use identical baseline states: PRESENT")
    print("Local copied wavenumber arrays: PRESENT")
    print("Solver wavenumber mutation: ABSENT")
    print("Raw historical failure reproduction gate: PRESENT")
    print("Real derivative preservation gates: PRESENT")
    print("Real transport preservation gates: PRESENT")
    print("Real shadow-work preservation gates: PRESENT")
    print("Preserved partial Stage C identities: PASS")
    print("Focused localization evidence identities: PASS")
    print("All output header lists unique: PASS")
    print("Historical threshold unchanged: PASS")
    print(
        "SpectralSolver constructor calls:",
        ast_summary[
            "spectral_solver_constructor_calls"
        ],
    )
    print("Project imports outside run path: NO")
    print("Protected or selectable run() calls: NO")
    print("Selectable step calls: NO")
    print("Alternate trajectories: NO")
    print("Full Stage C classification strings: NO")
    print("Project modules imported: NO")
    print("Solver constructed: NO")
    print("Numerical steps executed: NO")
    print("Files written: NO")
    print("Git mutations: NONE")
    print("Protected baseline update modification authorized: NO")
    print("Focused remediation numerical execution authorized by inspection: NO")
    print("Full Stage C rerun authorized: NO")
    return 0


# ============================================================================
# Baseline replay and frozen forcing
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


def build_rms_matched_multimode_forcing(
    solver: object,
) -> tuple[np.ndarray, dict[str, object]]:
    x = np.asarray(solver.X)
    y = np.asarray(solver.Y)
    base = (
        0.01
        * np.sin(2.0 * x)
        * np.cos(2.0 * y)
    )
    raw = (
        1.00 * np.sin(2.0 * x) * np.cos(2.0 * y)
        + 0.75 * np.sin(3.0 * x) * np.cos(y)
        + 0.50 * np.sin(x) * np.cos(4.0 * y)
        + 0.35 * np.cos(4.0 * x - 2.0 * y)
    )
    raw = np.asarray(raw, dtype=np.float64)
    raw = raw - np.mean(raw)
    raw_rms = field_rms(raw)
    if raw_rms <= 0.0:
        raise IntegrityFailure(
            "forcing_raw_rms",
            "raw forcing has zero RMS",
        )
    base_rms = field_rms(base)
    coefficient = base_rms / raw_rms
    forcing = np.ascontiguousarray(
        coefficient * raw,
        dtype=np.float64,
    )
    forcing_hash = sha256_array(forcing)
    if forcing_hash != EXPECTED_FORCING_SHA256:
        raise IntegrityFailure(
            "forcing_sha256",
            f"forcing SHA256={forcing_hash}, "
            f"expected={EXPECTED_FORCING_SHA256}",
        )
    forcing_rms = field_rms(forcing)
    if not math.isclose(
        forcing_rms,
        FORCING_TARGET_RMS,
        rel_tol=0.0,
        abs_tol=FORCING_RMS_TOLERANCE,
    ):
        raise IntegrityFailure(
            "forcing_rms",
            f"forcing RMS={forcing_rms}, "
            f"expected={FORCING_TARGET_RMS}",
        )
    forcing.setflags(write=False)
    return forcing, {
        "forcing_sha256": forcing_hash,
        "forcing_terms": list(FORCING_TERMS),
        "target_rms": FORCING_TARGET_RMS,
        "normalized_rms": forcing_rms,
        "normalization_coefficient": coefficient,
        "shape": list(forcing.shape),
        "dtype": str(forcing.dtype),
        "writeable": bool(forcing.flags.writeable),
    }


def baseline_step(
    solver: object,
    baseline_omega: np.ndarray,
    forcing: np.ndarray,
    *,
    loop_index: int,
) -> dict[str, object]:
    current = np.asarray(
        baseline_omega,
        dtype=np.float64,
    )

    psi_1 = solver.streamfunction(current)
    u_1, v_1 = solver.velocity(psi_1)
    omega_x_1, omega_y_1 = centered_gradients(
        current,
        float(solver.dx),
    )
    transport_1 = (
        u_1 * omega_x_1
        + v_1 * omega_y_1
    )
    advection_1 = -transport_1
    viscous_1 = solver.laplacian_spectral(current)
    total_1 = advection_1 + viscous_1 + forcing
    stage = current + float(solver.dt) * total_1

    psi_2 = solver.streamfunction(stage)
    u_2, v_2 = solver.velocity(psi_2)
    omega_x_2, omega_y_2 = centered_gradients(
        stage,
        float(solver.dx),
    )
    transport_2 = (
        u_2 * omega_x_2
        + v_2 * omega_y_2
    )
    advection_2 = -transport_2
    viscous_2 = solver.laplacian_spectral(stage)
    total_2 = advection_2 + viscous_2 + forcing

    unfiltered = (
        current
        + 0.5
        * float(solver.dt)
        * (total_1 + total_2)
    )
    filtered_complex = np.fft.ifft2(
        np.fft.fft2(unfiltered)
        * np.asarray(solver.deal)
    )
    filtered = filtered_complex.real

    arrays = (
        current,
        stage,
        unfiltered,
        filtered,
        psi_1,
        u_1,
        v_1,
        psi_2,
        u_2,
        v_2,
        transport_1,
        transport_2,
    )
    if not all(
        np.isfinite(value).all()
        for value in arrays
    ):
        raise IntegrityFailure(
            "baseline_finite",
            f"baseline state is nonfinite at "
            f"loop_index={loop_index}",
        )

    stage1_advection_work = mean_product(
        current,
        advection_1,
    )
    stage2_advection_work = mean_product(
        stage,
        advection_2,
    )

    return {
        "loop_index": loop_index,
        "completed_steps": loop_index + 1,
        "physical_time":
            (loop_index + 1) * float(solver.dt),
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
        "transport_2": transport_2,
        "z_current": enstrophy(current),
        "z_stage": enstrophy(stage),
        "z_unfiltered": enstrophy(unfiltered),
        "z_filtered": enstrophy(filtered),
        "stage1_advection_work_rate":
            stage1_advection_work,
        "stage2_advection_work_rate":
            stage2_advection_work,
        "rk2_advection_rate": 0.5 * (
            stage1_advection_work
            + stage2_advection_work
        ),
    }


# ============================================================================
# Spectral route diagnostics
# ============================================================================

def complex_measurement(
    quantity_id: str,
    components: Mapping[str, np.ndarray],
) -> dict[str, object]:
    if not components:
        raise ValueError("components must not be empty")

    component_values: dict[
        str,
        dict[str, float],
    ] = {}
    for direction, value in components.items():
        array = np.asarray(
            value,
            dtype=np.complex128,
        )
        component_values[direction] = {
            "real_rms": field_rms(array.real),
            "imaginary_rms":
                field_rms(array.imag),
            "real_max_abs": max_abs(array.real),
            "imaginary_max_abs":
                max_abs(array.imag),
        }

    real_direction = max(
        component_values,
        key=lambda key:
            component_values[key]["real_rms"],
    )
    imaginary_direction = max(
        component_values,
        key=lambda key:
            component_values[key]["imaginary_rms"],
    )

    real_rms = component_values[
        real_direction
    ]["real_rms"]
    imaginary_rms = component_values[
        imaginary_direction
    ]["imaginary_rms"]
    denominator = max(real_rms, RESIDUAL_FLOOR)

    return {
        "quantity_id": quantity_id,
        "dominant_direction": imaginary_direction,
        "real_rms": real_rms,
        "imaginary_rms": imaginary_rms,
        "imaginary_ratio":
            imaginary_rms / denominator,
        "real_max_abs": max(
            value["real_max_abs"]
            for value in component_values.values()
        ),
        "imaginary_max_abs": max(
            value["imaginary_max_abs"]
            for value in component_values.values()
        ),
        "ratio_denominator": denominator,
        "denominator_uses_floor":
            real_rms <= RESIDUAL_FLOOR,
        "components": component_values,
    }


def derivative_pair(
    field: np.ndarray,
    kx: np.ndarray,
    ky: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    field_hat = np.fft.fft2(
        np.asarray(field, dtype=np.float64)
    )
    return (
        np.fft.ifft2(1j * kx * field_hat),
        np.fft.ifft2(1j * ky * field_hat),
    )


def build_real_compatible_wavenumbers(
    solver: object,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    kx = np.asarray(solver.kx)
    ky = np.asarray(solver.ky)
    nyquist = -N / 2

    x_nyquist_mask = np.asarray(kx == nyquist)
    y_nyquist_mask = np.asarray(ky == nyquist)

    if (
        not x_nyquist_mask.any()
        or not y_nyquist_mask.any()
    ):
        raise IntegrityFailure(
            "nyquist_location",
            "solver wavenumbers do not contain -N/2",
        )

    kx_real_compatible = np.array(
        kx,
        dtype=np.float64,
        copy=True,
    )
    ky_real_compatible = np.array(
        ky,
        dtype=np.float64,
        copy=True,
    )
    kx_real_compatible[x_nyquist_mask] = 0.0
    ky_real_compatible[y_nyquist_mask] = 0.0

    if np.shares_memory(kx_real_compatible, kx):
        raise IntegrityFailure(
            "kx_copy",
            "real-compatible kx shares memory with solver.kx",
        )
    if np.shares_memory(ky_real_compatible, ky):
        raise IntegrityFailure(
            "ky_copy",
            "real-compatible ky shares memory with solver.ky",
        )

    return (
        kx_real_compatible,
        ky_real_compatible,
        x_nyquist_mask,
        y_nyquist_mask,
    )


def project_complex(
    field: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    return np.fft.ifft2(
        np.fft.fft2(
            np.asarray(field, dtype=np.float64)
        )
        * mask
    )


def hermitian_residual(
    spectrum: np.ndarray,
) -> float:
    array = np.asarray(
        spectrum,
        dtype=np.complex128,
    )
    indices = (
        -np.arange(array.shape[0])
    ) % array.shape[0]
    partner = np.conj(
        array[np.ix_(indices, indices)]
    )
    difference = complex_rms(array - partner)
    return difference / max(
        complex_rms(array),
        RESIDUAL_FLOOR,
    )


def spectral_power_fraction(
    field: np.ndarray,
    mask: np.ndarray,
) -> float:
    spectrum = np.fft.fft2(
        np.asarray(field, dtype=np.float64)
    )
    total = float(
        np.sum(np.abs(spectrum) ** 2)
    )
    selected = float(
        np.sum(np.abs(spectrum[mask]) ** 2)
    )
    return selected / max(
        total,
        SPECTRAL_POWER_FLOOR,
    )


def build_route_diagnostics(
    solver: object,
    state: np.ndarray,
    psi: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    *,
    stage: int,
    route: str,
    kx_route: np.ndarray,
    ky_route: np.ndarray,
) -> dict[str, object]:
    deal = np.asarray(solver.deal)

    omega_x, omega_y = derivative_pair(
        state,
        kx_route,
        ky_route,
    )
    omega_measurement = complex_measurement(
        "omega_gradient_imaginary_ratio",
        {
            "x": omega_x,
            "y": omega_y,
        },
    )

    omega_x_centered, omega_y_centered = (
        centered_gradients(
            state,
            float(solver.dx),
        )
    )
    baseline_transport = (
        u * omega_x_centered
        + v * omega_y_centered
    )
    projected_baseline_complex = project_complex(
        baseline_transport,
        deal,
    )
    projected_baseline_measurement = (
        complex_measurement(
            "projected_baseline_transport_imaginary_ratio",
            {"projection": projected_baseline_complex},
        )
    )

    pseudo_raw_transport = (
        u * omega_x.real
        + v * omega_y.real
    )
    projected_pseudo_complex = project_complex(
        pseudo_raw_transport,
        deal,
    )
    projected_pseudo_measurement = (
        complex_measurement(
            "projected_pseudo_transport_imaginary_ratio",
            {"projection": projected_pseudo_complex},
        )
    )

    u_x, u_y = derivative_pair(
        u,
        kx_route,
        ky_route,
    )
    u_measurement = complex_measurement(
        "u_x_gradient_imaginary_ratio",
        {
            "x": u_x,
            "y_auxiliary": u_y,
        },
    )

    v_x, v_y = derivative_pair(
        v,
        kx_route,
        ky_route,
    )
    v_measurement = complex_measurement(
        "v_y_gradient_imaginary_ratio",
        {
            "x_auxiliary": v_x,
            "y": v_y,
        },
    )

    measurements = (
        omega_measurement,
        projected_baseline_measurement,
        projected_pseudo_measurement,
        u_measurement,
        v_measurement,
    )
    if tuple(
        str(item["quantity_id"])
        for item in measurements
    ) != QUANTITY_IDS:
        raise IntegrityFailure(
            "quantity_registry",
            "five-quantity order differs",
            stage=stage,
        )

    arrays = (
        omega_x,
        omega_y,
        projected_baseline_complex,
        pseudo_raw_transport,
        projected_pseudo_complex,
        u_x,
        u_y,
        v_x,
        v_y,
    )
    if not all(
        np.isfinite(value).all()
        for value in arrays
    ):
        raise IntegrityFailure(
            "route_arrays_finite",
            f"{route} route produced nonfinite values",
            stage=stage,
        )

    return {
        "route": route,
        "stage": stage,
        "state": state,
        "state_sha256": sha256_array(state),
        "psi": psi,
        "u": u,
        "v": v,
        "measurements": measurements,
        "measurement_by_id": {
            str(item["quantity_id"]): item
            for item in measurements
        },
        "maximum_ratio": max(
            float(item["imaginary_ratio"])
            for item in measurements
        ),
        "baseline_transport": baseline_transport,
        "projected_baseline_transport":
            projected_baseline_complex.real,
        "pseudo_raw_transport":
            pseudo_raw_transport,
        "projected_pseudo_transport":
            projected_pseudo_complex.real,
        "omega_x": omega_x,
        "omega_y": omega_y,
        "u_x": u_x,
        "u_y": u_y,
        "v_x": v_x,
        "v_y": v_y,
    }


def quantity_real_fields(
    diagnostics: Mapping[str, object],
) -> dict[str, np.ndarray]:
    return {
        "omega_gradient_imaginary_ratio":
            np.stack(
                (
                    np.asarray(
                        diagnostics["omega_x"]
                    ).real,
                    np.asarray(
                        diagnostics["omega_y"]
                    ).real,
                ),
                axis=0,
            ),
        "projected_baseline_transport_imaginary_ratio":
            np.asarray(
                diagnostics[
                    "projected_baseline_transport"
                ],
                dtype=np.float64,
            ),
        "projected_pseudo_transport_imaginary_ratio":
            np.asarray(
                diagnostics[
                    "projected_pseudo_transport"
                ],
                dtype=np.float64,
            ),
        "u_x_gradient_imaginary_ratio":
            np.stack(
                (
                    np.asarray(
                        diagnostics["u_x"]
                    ).real,
                    np.asarray(
                        diagnostics["u_y"]
                    ).real,
                ),
                axis=0,
            ),
        "v_y_gradient_imaginary_ratio":
            np.stack(
                (
                    np.asarray(
                        diagnostics["v_x"]
                    ).real,
                    np.asarray(
                        diagnostics["v_y"]
                    ).real,
                ),
                axis=0,
            ),
    }


def raw_and_real_compatible_trace_rows(
    solver: object,
    baseline: Mapping[str, object],
    raw_diagnostics: Mapping[str, object],
    real_compatible_diagnostics: Mapping[str, object],
    *,
    stage: int,
    x_nyquist_mask: np.ndarray,
    y_nyquist_mask: np.ndarray,
    kx_real_compatible: np.ndarray,
    ky_real_compatible: np.ndarray,
) -> list[dict[str, object]]:
    loop_index = int(baseline["loop_index"])
    physical_time = float(
        baseline["physical_time"]
    )
    state = np.asarray(
        raw_diagnostics["state"],
        dtype=np.float64,
    )

    raw_fields = quantity_real_fields(
        raw_diagnostics
    )
    real_compatible_fields = quantity_real_fields(
        real_compatible_diagnostics
    )

    raw_by_id = raw_diagnostics[
        "measurement_by_id"
    ]
    rc_by_id = real_compatible_diagnostics[
        "measurement_by_id"
    ]

    field_map = {
        "omega_gradient_imaginary_ratio": state,
        "projected_baseline_transport_imaginary_ratio":
            np.asarray(
                raw_diagnostics[
                    "baseline_transport"
                ],
                dtype=np.float64,
            ),
        "projected_pseudo_transport_imaginary_ratio":
            np.asarray(
                raw_diagnostics[
                    "pseudo_raw_transport"
                ],
                dtype=np.float64,
            ),
        "u_x_gradient_imaginary_ratio":
            np.asarray(
                raw_diagnostics["u"],
                dtype=np.float64,
            ),
        "v_y_gradient_imaginary_ratio":
            np.asarray(
                raw_diagnostics["v"],
                dtype=np.float64,
            ),
    }

    rows: list[dict[str, object]] = []

    for quantity_id in QUANTITY_IDS:
        raw_measurement = raw_by_id[quantity_id]
        rc_measurement = rc_by_id[quantity_id]
        raw_field = np.asarray(
            raw_fields[quantity_id],
            dtype=np.float64,
        )
        rc_field = np.asarray(
            real_compatible_fields[quantity_id],
            dtype=np.float64,
        )
        difference = rc_field - raw_field
        difference_rms = field_rms(difference)
        raw_field_rms = field_rms(raw_field)
        rc_field_rms = field_rms(rc_field)
        difference_relative = (
            difference_rms
            / max(
                raw_field_rms,
                rc_field_rms,
                RESIDUAL_FLOOR,
            )
        )

        direction = str(
            raw_measurement["dominant_direction"]
        )
        relevant_mask = (
            x_nyquist_mask
            if direction.startswith("x")
            else y_nyquist_mask
        )
        relevant_multiplier_raw = (
            np.asarray(solver.kx)
            if direction.startswith("x")
            else np.asarray(solver.ky)
        )
        relevant_multiplier_rc = (
            kx_real_compatible
            if direction.startswith("x")
            else ky_real_compatible
        )
        source_field = field_map[quantity_id]
        source_spectrum = np.fft.fft2(
            np.asarray(source_field, dtype=np.float64)
        )
        raw_derivative_spectrum = (
            1j
            * relevant_multiplier_raw
            * source_spectrum
        )
        rc_derivative_spectrum = (
            1j
            * relevant_multiplier_rc
            * source_spectrum
        )
        nyquist_fraction = spectral_power_fraction(
            source_field,
            relevant_mask,
        )
        raw_hermitian = hermitian_residual(
            raw_derivative_spectrum
        )
        rc_hermitian = hermitian_residual(
            rc_derivative_spectrum
        )

        for route, measurement in (
            ("raw", raw_measurement),
            ("real_compatible", rc_measurement),
        ):
            row = {
                "loop_index": loop_index,
                "completed_steps": loop_index + 1,
                "physical_time": physical_time,
                "stage": stage,
                "route": route,
                "quantity_id": quantity_id,
                "dominant_direction": str(
                    measurement[
                        "dominant_direction"
                    ]
                ),
                "real_rms": float(
                    measurement["real_rms"]
                ),
                "imaginary_rms": float(
                    measurement["imaginary_rms"]
                ),
                "imaginary_ratio": float(
                    measurement["imaginary_ratio"]
                ),
                "real_max_abs": float(
                    measurement["real_max_abs"]
                ),
                "imaginary_max_abs": float(
                    measurement[
                        "imaginary_max_abs"
                    ]
                ),
                "ratio_denominator": float(
                    measurement[
                        "ratio_denominator"
                    ]
                ),
                "denominator_uses_floor": bool(
                    measurement[
                        "denominator_uses_floor"
                    ]
                ),
                "threshold": IMAGINARY_RATIO_LIMIT,
                "threshold_pass": (
                    float(
                        measurement[
                            "imaginary_ratio"
                        ]
                    )
                    <= IMAGINARY_RATIO_LIMIT
                ),
                "is_historical_failure": (
                    loop_index == STOP_LOOP_INDEX
                    and stage
                    == EXPECTED_FAILURE_STAGE
                    and route == "raw"
                    and quantity_id
                    == EXPECTED_FAILURE_QUANTITY
                ),
                "raw_to_real_compatible_real_difference_rms":
                    difference_rms,
                "raw_to_real_compatible_real_difference_max_abs":
                    max_abs(difference),
                "raw_to_real_compatible_real_difference_relative":
                    difference_relative,
                "raw_to_real_compatible_real_cosine_similarity":
                    cosine_similarity(
                        raw_field,
                        rc_field,
                    ),
                "relevant_nyquist_power_fraction":
                    nyquist_fraction,
                "raw_hermitian_residual":
                    raw_hermitian,
                "real_compatible_hermitian_residual":
                    rc_hermitian,
                "state_sha256": str(
                    raw_diagnostics[
                        "state_sha256"
                    ]
                ),
            }
            if not all_numeric_values_finite(row):
                raise IntegrityFailure(
                    "trace_row_finite",
                    "trace row contains nonfinite data",
                    quantity_id=quantity_id,
                    stage=stage,
                )
            rows.append(row)

    return rows


# ============================================================================
# Work comparison and historical operator reproduction
# ============================================================================

def historical_operator_works(
    solver: object,
    baseline: Mapping[str, object],
    raw_stage1: Mapping[str, object],
    raw_stage2: Mapping[str, object],
    *,
    jacobian_arakawa_periodic:
        Callable[..., np.ndarray],
) -> dict[str, float]:
    stage_work: dict[
        tuple[int, str],
        float,
    ] = {}

    for stage_number, diagnostics, state, psi, u, v in (
        (
            1,
            raw_stage1,
            np.asarray(baseline["current"]),
            np.asarray(baseline["psi_1"]),
            np.asarray(baseline["u_1"]),
            np.asarray(baseline["v_1"]),
        ),
        (
            2,
            raw_stage2,
            np.asarray(baseline["stage"]),
            np.asarray(baseline["psi_2"]),
            np.asarray(baseline["u_2"]),
            np.asarray(baseline["v_2"]),
        ),
    ):
        baseline_transport = np.asarray(
            diagnostics["baseline_transport"],
            dtype=np.float64,
        )
        projected_baseline = np.asarray(
            diagnostics[
                "projected_baseline_transport"
            ],
            dtype=np.float64,
        )
        dx_uomega, _ = centered_gradients(
            u * state,
            float(solver.dx),
        )
        _, dy_vomega = centered_gradients(
            v * state,
            float(solver.dx),
        )
        conservative_transport = (
            dx_uomega + dy_vomega
        )
        skew_transport = 0.5 * (
            baseline_transport
            + conservative_transport
        )
        pseudo_raw = np.asarray(
            diagnostics["pseudo_raw_transport"],
            dtype=np.float64,
        )
        pseudo_projected = np.asarray(
            diagnostics[
                "projected_pseudo_transport"
            ],
            dtype=np.float64,
        )
        arakawa_transport = -np.asarray(
            jacobian_arakawa_periodic(
                psi,
                state,
                float(solver.dx),
            ),
            dtype=np.float64,
        )

        transports = {
            "BASE_FD_ADVECTIVE_V1":
                baseline_transport,
            "SHADOW_FD_ADVECTIVE_PROJECTED_V1":
                projected_baseline,
            "SHADOW_FD_CONSERVATIVE_V1":
                conservative_transport,
            "SHADOW_FD_SKEW_V1":
                skew_transport,
            "SHADOW_PS_ADVECTIVE_RAW_V1":
                pseudo_raw,
            "SHADOW_PS_ADVECTIVE_PROJECTED_V1":
                pseudo_projected,
            "SHADOW_ARAKAWA_V1":
                arakawa_transport,
        }
        if tuple(transports) != OPERATOR_IDS:
            raise IntegrityFailure(
                "operator_registry",
                "historical operator order differs",
                stage=stage_number,
            )
        for operator_id, transport in (
            transports.items()
        ):
            stage_work[
                (stage_number, operator_id)
            ] = mean_product(
                state,
                -transport,
            )

    return {
        operator_id: 0.5 * (
            stage_work[(1, operator_id)]
            + stage_work[(2, operator_id)]
        )
        for operator_id in OPERATOR_IDS
    }


def work_comparison_rows(
    baseline: Mapping[str, object],
    raw_stage1: Mapping[str, object],
    raw_stage2: Mapping[str, object],
    rc_stage1: Mapping[str, object],
    rc_stage2: Mapping[str, object],
) -> list[dict[str, object]]:
    loop_index = int(baseline["loop_index"])
    physical_time = float(
        baseline["physical_time"]
    )

    stage_rows: list[dict[str, object]] = []
    stage_data: dict[
        tuple[int, str],
        tuple[
            np.ndarray,
            np.ndarray,
            float,
            float,
        ],
    ] = {}

    for stage_number, raw, rc in (
        (1, raw_stage1, rc_stage1),
        (2, raw_stage2, rc_stage2),
    ):
        state = np.asarray(
            raw["state"],
            dtype=np.float64,
        )
        for operator_id, key in (
            (
                "SHADOW_PS_ADVECTIVE_RAW_V1",
                "pseudo_raw_transport",
            ),
            (
                "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
                "projected_pseudo_transport",
            ),
        ):
            raw_transport = np.asarray(
                raw[key],
                dtype=np.float64,
            )
            rc_transport = np.asarray(
                rc[key],
                dtype=np.float64,
            )
            raw_work = mean_product(
                state,
                -raw_transport,
            )
            rc_work = mean_product(
                state,
                -rc_transport,
            )
            stage_data[
                (stage_number, operator_id)
            ] = (
                raw_transport,
                rc_transport,
                raw_work,
                rc_work,
            )
            stage_rows.append(
                build_work_row(
                    loop_index=loop_index,
                    physical_time=physical_time,
                    stage=stage_number,
                    operator_id=operator_id,
                    raw_transport=raw_transport,
                    rc_transport=rc_transport,
                    raw_work=raw_work,
                    rc_work=rc_work,
                )
            )

    for operator_id in PSEUDO_OPERATOR_IDS:
        raw_transport = 0.5 * (
            stage_data[(1, operator_id)][0]
            + stage_data[(2, operator_id)][0]
        )
        rc_transport = 0.5 * (
            stage_data[(1, operator_id)][1]
            + stage_data[(2, operator_id)][1]
        )
        raw_work = 0.5 * (
            stage_data[(1, operator_id)][2]
            + stage_data[(2, operator_id)][2]
        )
        rc_work = 0.5 * (
            stage_data[(1, operator_id)][3]
            + stage_data[(2, operator_id)][3]
        )
        stage_rows.append(
            build_work_row(
                loop_index=loop_index,
                physical_time=physical_time,
                stage="stage_weighted",
                operator_id=operator_id,
                raw_transport=raw_transport,
                rc_transport=rc_transport,
                raw_work=raw_work,
                rc_work=rc_work,
            )
        )

    if len(stage_rows) != 6:
        raise IntegrityFailure(
            "work_row_count",
            f"work rows={len(stage_rows)}, expected=6",
        )
    return stage_rows


def build_work_row(
    *,
    loop_index: int,
    physical_time: float,
    stage: int | str,
    operator_id: str,
    raw_transport: np.ndarray,
    rc_transport: np.ndarray,
    raw_work: float,
    rc_work: float,
) -> dict[str, object]:
    difference = rc_transport - raw_transport
    raw_rms = field_rms(raw_transport)
    rc_rms = field_rms(rc_transport)
    difference_rms = field_rms(difference)
    difference_relative = (
        difference_rms
        / max(
            raw_rms,
            rc_rms,
            RESIDUAL_FLOOR,
        )
    )
    work_absolute = abs(rc_work - raw_work)
    work_relative = relative_difference(
        rc_work,
        raw_work,
    )
    raw_nonzero = (
        abs(raw_work) > WORK_ABSOLUTE_LIMIT
    )
    rc_nonzero = (
        abs(rc_work) > WORK_ABSOLUTE_LIMIT
    )
    sign_changed = (
        raw_nonzero
        and rc_nonzero
        and math.copysign(1.0, raw_work)
        != math.copysign(1.0, rc_work)
    )
    near_zero_changed = (
        raw_nonzero != rc_nonzero
    )
    material = (
        difference_relative
        > REAL_TRANSPORT_RELATIVE_LIMIT
        or (
            work_absolute > WORK_ABSOLUTE_LIMIT
            and work_relative
            > WORK_RELATIVE_LIMIT
        )
        or sign_changed
        or near_zero_changed
    )

    row = {
        "loop_index": loop_index,
        "completed_steps": loop_index + 1,
        "physical_time": physical_time,
        "stage": stage,
        "operator_id": operator_id,
        "raw_transport_rms": raw_rms,
        "real_compatible_transport_rms":
            rc_rms,
        "transport_difference_rms":
            difference_rms,
        "transport_difference_max_abs":
            max_abs(difference),
        "transport_difference_relative":
            difference_relative,
        "transport_cosine_similarity":
            cosine_similarity(
                raw_transport,
                rc_transport,
            ),
        "raw_work": raw_work,
        "real_compatible_work": rc_work,
        "work_absolute_difference":
            work_absolute,
        "work_relative_difference":
            work_relative,
        "work_sign_changed": sign_changed,
        "near_zero_character_changed":
            near_zero_changed,
        "material_real_work_change":
            material,
    }
    if not all_numeric_values_finite(row):
        raise IntegrityFailure(
            "work_row_finite",
            "work row contains nonfinite data",
        )
    return row


# ============================================================================
# Archived evidence comparison
# ============================================================================

def load_partial_references(
    repo: Path,
) -> tuple[
    list[dict[str, str]],
    dict[str, dict[str, str]],
]:
    directory = repo / PARTIAL_STAGE_C_DIRECTORY
    state_rows = read_csv_rows(
        directory / "shadow_state_reference.csv"
    )
    shadow_rows = read_csv_rows(
        directory / "shadow_advection_per_step.csv"
    )
    if len(state_rows) != EXPECTED_PARTIAL_ROWS:
        raise RuntimeError(
            f"partial state rows={len(state_rows)}, "
            f"expected={EXPECTED_PARTIAL_ROWS}"
        )
    last_shadow = {
        str(row["operator_id"]): row
        for row in shadow_rows
        if int(row["loop_index"])
        == LAST_PASSING_LOOP_INDEX
    }
    if tuple(last_shadow) != OPERATOR_IDS:
        raise RuntimeError(
            "last-passing partial operator order differs"
        )
    return state_rows, last_shadow


def open_stage_b_ledger(
    repo: Path,
) -> tuple[Any, csv.DictReader]:
    path = repo / STAGE_B_LEDGER_PATH
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


def compare_stage_b_row(
    baseline: Mapping[str, object],
    archived: Mapping[str, str],
) -> None:
    integer_fields = (
        "loop_index",
        "completed_steps",
    )
    for name in integer_fields:
        if int(baseline[name]) != int(archived[name]):
            raise IntegrityFailure(
                "stage_b_integer_reproduction",
                f"{name} mismatch at "
                f"loop_index={baseline['loop_index']}",
            )

    fields = (
        "physical_time",
        "z_current",
        "z_stage",
        "z_unfiltered",
        "z_filtered",
        "stage1_advection_work_rate",
        "stage2_advection_work_rate",
        "rk2_advection_rate",
    )
    for name in fields:
        if not scalar_matches(
            float(baseline[name]),
            float(archived[name]),
        ):
            raise IntegrityFailure(
                "stage_b_scalar_reproduction",
                f"{name} mismatch at "
                f"loop_index={baseline['loop_index']}: "
                f"observed={baseline[name]}, "
                f"archived={archived[name]}",
            )


def compare_partial_state_row(
    baseline: Mapping[str, object],
    raw_stage1: Mapping[str, object],
    raw_stage2: Mapping[str, object],
    archived: Mapping[str, str],
) -> None:
    fields = (
        (
            float(baseline["physical_time"]),
            float(archived["physical_time"]),
            "physical_time",
        ),
        (
            float(baseline["z_filtered"]),
            float(archived["z_filtered"]),
            "z_filtered",
        ),
        (
            float(baseline["rk2_advection_rate"]),
            float(
                archived[
                    "baseline_rk2_work_replay"
                ]
            ),
            "baseline_rk2_work",
        ),
        (
            float(raw_stage1["maximum_ratio"]),
            float(
                archived[
                    "stage1_maximum_imaginary_ratio"
                ]
            ),
            "stage1_maximum_ratio",
        ),
        (
            float(raw_stage2["maximum_ratio"]),
            float(
                archived[
                    "stage2_maximum_imaginary_ratio"
                ]
            ),
            "stage2_maximum_ratio",
        ),
    )
    for observed, expected, name in fields:
        if not scalar_matches(
            observed,
            expected,
        ):
            raise IntegrityFailure(
                "partial_state_reproduction",
                f"{name} mismatch at "
                f"loop_index={baseline['loop_index']}: "
                f"observed={observed}, "
                f"archived={expected}",
            )


# ============================================================================
# Conclusion and report helpers
# ============================================================================

def determine_conclusions(
    *,
    raw_failure_reproduced: bool,
    real_compatible_passed: bool,
    hermitian_improved: bool,
    nyquist_content_present: bool,
    denominator_floor: bool,
    all_derivatives_preserved: bool,
    all_work_preserved: bool,
    all_state_identities_passed: bool,
) -> tuple[str, str]:
    if (
        raw_failure_reproduced
        and real_compatible_passed
        and hermitian_improved
        and nyquist_content_present
        and not denominator_floor
        and all_derivatives_preserved
        and all_work_preserved
        and all_state_identities_passed
    ):
        primary = (
            "SHADOW NYQUIST REMEDIATION "
            "CONSISTENT WITH LOCALIZATION"
        )
        effect = (
            "REAL SHADOW WORK PRESERVED "
            "UNDER REMEDIATION"
        )
    elif (
        raw_failure_reproduced
        and (
            not real_compatible_passed
            or not hermitian_improved
            or not nyquist_content_present
            or not all_derivatives_preserved
            or not all_work_preserved
            or not all_state_identities_passed
        )
    ):
        primary = (
            "SHADOW NYQUIST REMEDIATION "
            "NOT CONSISTENT WITH LOCALIZATION"
        )
        effect = (
            "REAL SHADOW WORK MATERIALLY "
            "CHANGED UNDER REMEDIATION"
            if not all_work_preserved
            else "REAL SHADOW WORK EFFECT INCONCLUSIVE"
        )
    else:
        primary = (
            "SHADOW NYQUIST REMEDIATION INCONCLUSIVE"
        )
        effect = (
            "REAL SHADOW WORK EFFECT INCONCLUSIVE"
        )

    if primary not in PRIMARY_CONCLUSIONS:
        raise RuntimeError(
            f"unsupported primary conclusion: {primary}"
        )
    if effect not in EFFECT_CONCLUSIONS:
        raise RuntimeError(
            f"unsupported effect conclusion: {effect}"
        )
    return primary, effect


def render_report(
    summary: Mapping[str, object],
) -> str:
    failure = summary["historical_failure"]
    controls = summary["controls"]
    lines = [
        "# Stage C Shadow Nyquist Remediation Verification Report",
        "",
        "## Decision",
        "",
        f"> **{summary['primary_conclusion']}**",
        "",
        f"> **{summary['effect_conclusion']}**",
        "",
        (
            "This is a focused shadow-diagnostic remediation "
            "verification through loop index 3059 only."
        ),
        "",
        "## Historical failure reproduction",
        "",
        f"- Loop index: `{failure['loop_index']}`",
        f"- Stage: `{failure['stage']}`",
        f"- Quantity: `{failure['quantity_id']}`",
        f"- Raw ratio: `{failure['raw_ratio']}`",
        (
            "- Real-compatible ratio: "
            f"`{failure['real_compatible_ratio']}`"
        ),
        f"- Historical threshold: `{IMAGINARY_RATIO_LIMIT}`",
        "",
        "## Controls",
        "",
        (
            "- Stage B rows reproduced: "
            f"`{controls['stage_b_rows_reproduced']}`"
        ),
        (
            "- Partial Stage C rows reproduced: "
            f"`{controls['partial_rows_reproduced']}`"
        ),
        (
            "- Last-passing seven-operator values reproduced: "
            f"`{controls['last_passing_operator_values_reproduced']}`"
        ),
        (
            "- Baseline current-state identity preserved: "
            f"`{controls['current_state_identity_preserved']}`"
        ),
        (
            "- Baseline RK2 stage identity preserved: "
            f"`{controls['stage_state_identity_preserved']}`"
        ),
        (
            "- Accepted filtered-state identity preserved: "
            f"`{controls['filtered_state_identity_preserved']}`"
        ),
        (
            "- Solver wavenumber arrays preserved: "
            f"`{controls['solver_wavenumbers_preserved']}`"
        ),
        "- Protected baseline update modified: `False`",
        "- Alternate trajectories executed: `False`",
        "- Full Stage C rerun performed: `False`",
        "- Full Stage C rerun authorized: `False`",
        (
            "- Stage C operator-form-specificity "
            "classification produced: `False`"
        ),
        "",
        "## Interpretation boundary",
        "",
        (
            "The result applies only to the shadow spectral "
            "derivative convention at the original failure point."
        ),
        "",
        (
            "It does not establish a full Stage C result, "
            "method superiority, convergence, physical validation, "
            "turbulence, a cascade, an inertial range, or a `k^-3` law."
        ),
        "",
    ]
    return "\n".join(lines)


def write_inventory(
    directory: Path,
    inventory_path: Path,
    paths: Sequence[Path],
) -> str:
    rows: list[dict[str, object]] = []
    for path in paths:
        if not path.is_file():
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
                "self-hash omitted to avoid circular "
                "self-reference"
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
# Controlled focused execution
# ============================================================================

def execute_remediation(
    repo: Path,
) -> int:
    runner = Path(__file__).resolve()
    execution_commit = verify_runner_commit_shape(
        repo,
        runner,
    )
    source_identities_before = (
        verify_source_identities(repo)
    )
    assert_all_output_headers_unique()

    output_root = repo / OUTPUT_ROOT
    existing = (
        sorted(output_root.glob(f"{RUN_PREFIX}*"))
        if output_root.is_dir()
        else []
    )
    if existing:
        raise RuntimeError(
            "a focused remediation output already "
            "exists; no rerun is allowed: "
            + ", ".join(str(path) for path in existing)
        )

    created = utc_now()
    run_id = (
        f"{RUN_PREFIX}"
        f"{created.strftime('%Y%m%dT%H%M%SZ')}_"
        f"{execution_commit[:7]}"
    )
    run_directory = output_root / run_id
    if not path_is_git_ignored(repo, run_directory):
        raise RuntimeError(
            "planned focused remediation output is "
            "not Git-ignored: "
            f"{run_directory.relative_to(repo)}"
        )
    run_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    metadata_path = (
        run_directory / "run_metadata.json"
    )
    trace_path = (
        run_directory
        / "raw_and_real_compatible_trace.csv"
    )
    work_path = (
        run_directory
        / "real_work_comparison.csv"
    )
    summary_path = (
        run_directory / "remediation_summary.json"
    )
    report_path = (
        run_directory
        / "STAGE_C_SHADOW_NYQUIST_REMEDIATION_VERIFICATION_REPORT.md"
    )
    inventory_path = (
        run_directory / "file_inventory.csv"
    )

    inventory_hash: str | None = None
    failed_gate: str | None = None
    failed_quantity: str | None = None
    failed_stage: int | None = None
    last_replayed_loop: int | None = None

    metadata: dict[str, object] = {
        "schema_id": (
            "STAGE_C_SHADOW_NYQUIST_"
            "REMEDIATION_METADATA_V1"
        ),
        "run_id": run_id,
        "status": "running",
        "primary_conclusion": None,
        "effect_conclusion": None,
        "created_utc": utc_text(created),
        "completed_utc": None,
        "repository": {
            "name": "Raj-Sanghera-Project",
            "branch": "phase4_validation",
            "design_commit":
                AUTHORIZED_DESIGN_COMMIT,
            "execution_commit": execution_commit,
            "runner_path": runner.name,
            "runner_sha256": sha256_file(runner),
            "source_identities":
                source_identities_before,
        },
        "environment": {
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "operating_system":
                platform.platform(),
            "floating_dtype": "float64",
            "machine_epsilon": float(
                np.finfo(np.float64).eps
            ),
        },
        "configuration": {
            "grid": [N, N],
            "Re": RE,
            "nu": NU,
            "dt": DT,
            "full_stage_c_steps":
                FULL_STAGE_C_STEPS,
            "focused_stop_loop_index":
                STOP_LOOP_INDEX,
            "expected_replay_rows":
                EXPECTED_REPLAY_ROWS,
            "historical_imaginary_ratio_limit":
                IMAGINARY_RATIO_LIMIT,
            "accepted_trajectory":
                "baseline centered-advection only",
            "raw_route": "historical ik",
            "real_compatible_route":
                "local Nyquist-zeroed ik",
            "alternate_trajectories_executed":
                False,
            "full_stage_c_rerun": False,
        },
        "progress": {
            "last_replayed_loop_index": None,
            "stage_b_rows_reproduced": 0,
            "partial_rows_reproduced": 0,
        },
        "claims": {
            "stage_c_specificity_classification":
                False,
            "method_superiority": False,
            "formal_temporal_convergence": False,
            "formal_spatial_convergence": False,
            "physical_validation": False,
            "turbulence": False,
            "cascade": False,
            "inertial_range": False,
            "k_minus_3": False,
            "production_readiness": False,
        },
        "output_files": {
            "run_metadata": metadata_path.name,
            "trace": trace_path.name,
            "real_work_comparison":
                work_path.name,
            "remediation_summary":
                summary_path.name,
            "report": report_path.name,
            "file_inventory":
                inventory_path.name,
        },
    }
    atomic_write_json(metadata_path, metadata)

    ledger_handle: Any | None = None

    try:
        from project.solver.advection_operators import (
            jacobian_arakawa_periodic,
        )
        from project.solver.spectral_solver import (
            SpectralSolver,
        )

        partial_state_rows, last_partial_shadow = (
            load_partial_references(repo)
        )
        ledger_handle, ledger_reader = (
            open_stage_b_ledger(repo)
        )

        solver = SpectralSolver(
            nx=N,
            ny=N,
            Re=RE,
            run_path=run_directory,
            dt=DT,
            steps=FULL_STAGE_C_STEPS,
        )
        if not np.array_equal(
            np.asarray(solver.w),
            np.zeros_like(np.asarray(solver.w)),
        ):
            raise IntegrityFailure(
                "initial_state",
                "solver did not initialize with zero vorticity",
            )

        forcing, forcing_statistics = (
            build_rms_matched_multimode_forcing(solver)
        )
        forcing_hash = str(
            forcing_statistics["forcing_sha256"]
        )
        metadata["forcing"] = forcing_statistics
        atomic_write_json(metadata_path, metadata)

        kx_original_hash = sha256_array(solver.kx)
        ky_original_hash = sha256_array(solver.ky)
        (
            kx_real_compatible,
            ky_real_compatible,
            x_nyquist_mask,
            y_nyquist_mask,
        ) = build_real_compatible_wavenumbers(
            solver
        )

        baseline_omega = np.zeros(
            (N, N),
            dtype=np.float64,
        )
        stage_b_rows_reproduced = 0
        partial_rows_reproduced = 0
        last_passing_operator_values_reproduced = (
            False
        )

        trace_rows: list[dict[str, object]] = []
        work_rows: list[dict[str, object]] = []

        failure_baseline: dict[str, object] | None = None
        failure_raw_stage1: dict[str, object] | None = None
        failure_raw_stage2: dict[str, object] | None = None
        failure_rc_stage1: dict[str, object] | None = None
        failure_rc_stage2: dict[str, object] | None = None

        current_identity_preserved = True
        stage_identity_preserved = True
        filtered_identity_preserved = True

        for loop_index in range(STOP_LOOP_INDEX + 1):
            try:
                archived_stage_b_row = next(
                    ledger_reader
                )
            except StopIteration as error:
                raise IntegrityFailure(
                    "stage_b_ledger_length",
                    "Stage B ledger ended early",
                ) from error

            baseline = baseline_step(
                solver,
                baseline_omega,
                forcing,
                loop_index=loop_index,
            )
            compare_stage_b_row(
                baseline,
                archived_stage_b_row,
            )
            stage_b_rows_reproduced += 1

            current_hash_before = sha256_array(
                baseline["current"]
            )
            stage_hash_before = sha256_array(
                baseline["stage"]
            )
            filtered_hash_before = sha256_array(
                baseline["filtered"]
            )

            raw_stage1 = build_route_diagnostics(
                solver,
                np.asarray(baseline["current"]),
                np.asarray(baseline["psi_1"]),
                np.asarray(baseline["u_1"]),
                np.asarray(baseline["v_1"]),
                stage=1,
                route="raw",
                kx_route=np.asarray(solver.kx),
                ky_route=np.asarray(solver.ky),
            )
            raw_stage2 = build_route_diagnostics(
                solver,
                np.asarray(baseline["stage"]),
                np.asarray(baseline["psi_2"]),
                np.asarray(baseline["u_2"]),
                np.asarray(baseline["v_2"]),
                stage=2,
                route="raw",
                kx_route=np.asarray(solver.kx),
                ky_route=np.asarray(solver.ky),
            )
            rc_stage1 = build_route_diagnostics(
                solver,
                np.asarray(baseline["current"]),
                np.asarray(baseline["psi_1"]),
                np.asarray(baseline["u_1"]),
                np.asarray(baseline["v_1"]),
                stage=1,
                route="real_compatible",
                kx_route=kx_real_compatible,
                ky_route=ky_real_compatible,
            )
            rc_stage2 = build_route_diagnostics(
                solver,
                np.asarray(baseline["stage"]),
                np.asarray(baseline["psi_2"]),
                np.asarray(baseline["u_2"]),
                np.asarray(baseline["v_2"]),
                stage=2,
                route="real_compatible",
                kx_route=kx_real_compatible,
                ky_route=ky_real_compatible,
            )

            current_hash_after = sha256_array(
                baseline["current"]
            )
            stage_hash_after = sha256_array(
                baseline["stage"]
            )
            filtered_hash_after = sha256_array(
                baseline["filtered"]
            )
            current_identity_preserved = (
                current_identity_preserved
                and current_hash_before
                == current_hash_after
            )
            stage_identity_preserved = (
                stage_identity_preserved
                and stage_hash_before
                == stage_hash_after
            )
            filtered_identity_preserved = (
                filtered_identity_preserved
                and filtered_hash_before
                == filtered_hash_after
            )
            if not (
                current_identity_preserved
                and stage_identity_preserved
                and filtered_identity_preserved
            ):
                raise IntegrityFailure(
                    "state_mutation",
                    f"shadow route changed baseline arrays "
                    f"at loop_index={loop_index}",
                )

            if loop_index <= LAST_PASSING_LOOP_INDEX:
                compare_partial_state_row(
                    baseline,
                    raw_stage1,
                    raw_stage2,
                    partial_state_rows[loop_index],
                )
                partial_rows_reproduced += 1

            if loop_index == LAST_PASSING_LOOP_INDEX:
                if not scalar_matches(
                    float(baseline["physical_time"]),
                    EXPECTED_LAST_PASSING_TIME,
                ):
                    raise IntegrityFailure(
                        "last_passing_time",
                        "last passing time differs",
                    )
                if not scalar_matches(
                    float(baseline["z_filtered"]),
                    EXPECTED_LAST_PASSING_Z,
                ):
                    raise IntegrityFailure(
                        "last_passing_z",
                        "last passing enstrophy differs",
                    )
                if not scalar_matches(
                    float(
                        baseline[
                            "rk2_advection_rate"
                        ]
                    ),
                    EXPECTED_LAST_PASSING_BASELINE_WORK,
                ):
                    raise IntegrityFailure(
                        "last_passing_work",
                        "last passing baseline work differs",
                    )
                if not scalar_matches(
                    float(raw_stage1["maximum_ratio"]),
                    EXPECTED_LAST_PASSING_STAGE1_RATIO,
                ):
                    raise IntegrityFailure(
                        "last_passing_stage1_ratio",
                        "last passing stage-1 ratio differs",
                    )
                if not scalar_matches(
                    float(raw_stage2["maximum_ratio"]),
                    EXPECTED_LAST_PASSING_STAGE2_RATIO,
                ):
                    raise IntegrityFailure(
                        "last_passing_stage2_ratio",
                        "last passing stage-2 ratio differs",
                    )
                observed_works = historical_operator_works(
                    solver,
                    baseline,
                    raw_stage1,
                    raw_stage2,
                    jacobian_arakawa_periodic=(
                        jacobian_arakawa_periodic
                    ),
                )
                for operator_id in OPERATOR_IDS:
                    archived_work = float(
                        last_partial_shadow[
                            operator_id
                        ][
                            "stage_weighted_rhs_work"
                        ]
                    )
                    if not scalar_matches(
                        observed_works[operator_id],
                        archived_work,
                    ):
                        raise IntegrityFailure(
                            "last_passing_operator_work",
                            f"{operator_id} mismatch",
                        )
                last_passing_operator_values_reproduced = (
                    True
                )

            if loop_index in (
                LAST_PASSING_LOOP_INDEX,
                STOP_LOOP_INDEX,
            ):
                trace_rows.extend(
                    raw_and_real_compatible_trace_rows(
                        solver,
                        baseline,
                        raw_stage1,
                        rc_stage1,
                        stage=1,
                        x_nyquist_mask=
                            x_nyquist_mask,
                        y_nyquist_mask=
                            y_nyquist_mask,
                        kx_real_compatible=
                            kx_real_compatible,
                        ky_real_compatible=
                            ky_real_compatible,
                    )
                )
                trace_rows.extend(
                    raw_and_real_compatible_trace_rows(
                        solver,
                        baseline,
                        raw_stage2,
                        rc_stage2,
                        stage=2,
                        x_nyquist_mask=
                            x_nyquist_mask,
                        y_nyquist_mask=
                            y_nyquist_mask,
                        kx_real_compatible=
                            kx_real_compatible,
                        ky_real_compatible=
                            ky_real_compatible,
                    )
                )

            last_replayed_loop = loop_index
            metadata["progress"] = {
                "last_replayed_loop_index":
                    loop_index,
                "stage_b_rows_reproduced":
                    stage_b_rows_reproduced,
                "partial_rows_reproduced":
                    partial_rows_reproduced,
            }
            if loop_index % 250 == 0:
                atomic_write_json(
                    metadata_path,
                    metadata,
                )

            if loop_index == STOP_LOOP_INDEX:
                failure_baseline = baseline
                failure_raw_stage1 = raw_stage1
                failure_raw_stage2 = raw_stage2
                failure_rc_stage1 = rc_stage1
                failure_rc_stage2 = rc_stage2
                break

            baseline_omega = np.array(
                baseline["filtered"],
                dtype=np.float64,
                copy=True,
                order="C",
            )

        if last_replayed_loop != STOP_LOOP_INDEX:
            raise IntegrityFailure(
                "stop_index",
                f"last replayed loop={last_replayed_loop}, "
                f"expected={STOP_LOOP_INDEX}",
            )
        if stage_b_rows_reproduced != (
            EXPECTED_STAGE_B_ROWS_COMPARED
        ):
            raise IntegrityFailure(
                "stage_b_row_count",
                f"rows={stage_b_rows_reproduced}, "
                f"expected={EXPECTED_STAGE_B_ROWS_COMPARED}",
            )
        if partial_rows_reproduced != (
            EXPECTED_PARTIAL_ROWS
        ):
            raise IntegrityFailure(
                "partial_row_count",
                f"rows={partial_rows_reproduced}, "
                f"expected={EXPECTED_PARTIAL_ROWS}",
            )
        if not (
            last_passing_operator_values_reproduced
        ):
            raise IntegrityFailure(
                "last_passing_operator_values",
                "seven operator values were not reproduced",
            )
        if any(
            value is None
            for value in (
                failure_baseline,
                failure_raw_stage1,
                failure_raw_stage2,
                failure_rc_stage1,
                failure_rc_stage2,
            )
        ):
            raise IntegrityFailure(
                "failure_context",
                "focused failure context is incomplete",
            )

        assert failure_baseline is not None
        assert failure_raw_stage1 is not None
        assert failure_raw_stage2 is not None
        assert failure_rc_stage1 is not None
        assert failure_rc_stage2 is not None

        raw_failure_measurement = (
            failure_raw_stage2[
                "measurement_by_id"
            ][EXPECTED_FAILURE_QUANTITY]
        )
        rc_failure_measurement = (
            failure_rc_stage2[
                "measurement_by_id"
            ][EXPECTED_FAILURE_QUANTITY]
        )
        raw_failure_ratio = float(
            raw_failure_measurement[
                "imaginary_ratio"
            ]
        )
        rc_failure_ratio = float(
            rc_failure_measurement[
                "imaginary_ratio"
            ]
        )

        raw_failure_reproduced = (
            raw_failure_ratio
            > IMAGINARY_RATIO_LIMIT
            and scalar_matches(
                raw_failure_ratio,
                EXPECTED_RAW_FAILURE_RATIO,
                relative=(
                    RAW_RATIO_REPRODUCTION_RELATIVE_TOLERANCE
                ),
                absolute=(
                    RAW_RATIO_REPRODUCTION_ABSOLUTE_TOLERANCE
                ),
            )
        )
        if not raw_failure_reproduced:
            raise IntegrityFailure(
                "raw_failure_reproduction",
                f"raw ratio={raw_failure_ratio}, "
                f"expected={EXPECTED_RAW_FAILURE_RATIO}",
                quantity_id=EXPECTED_FAILURE_QUANTITY,
                stage=EXPECTED_FAILURE_STAGE,
            )

        real_compatible_reference_reproduced = scalar_matches(
            rc_failure_ratio,
            EXPECTED_REAL_COMPATIBLE_RATIO,
            relative=RAW_RATIO_REPRODUCTION_RELATIVE_TOLERANCE,
            absolute=RAW_RATIO_REPRODUCTION_ABSOLUTE_TOLERANCE,
        )
        real_compatible_passed = (
            rc_failure_ratio <= IMAGINARY_RATIO_LIMIT
            and real_compatible_reference_reproduced
        )
        if not real_compatible_passed:
            raise IntegrityFailure(
                "real_compatible_ratio",
                f"real-compatible ratio={rc_failure_ratio}, "
                f"expected localized reference="
                f"{EXPECTED_REAL_COMPATIBLE_RATIO}, "
                f"threshold={IMAGINARY_RATIO_LIMIT}",
                quantity_id=EXPECTED_FAILURE_QUANTITY,
                stage=EXPECTED_FAILURE_STAGE,
            )

        raw_failure_trace = next(
            row
            for row in trace_rows
            if (
                int(row["loop_index"])
                == STOP_LOOP_INDEX
                and int(row["stage"])
                == EXPECTED_FAILURE_STAGE
                and row["route"] == "raw"
                and row["quantity_id"]
                == EXPECTED_FAILURE_QUANTITY
            )
        )
        rc_failure_trace = next(
            row
            for row in trace_rows
            if (
                int(row["loop_index"])
                == STOP_LOOP_INDEX
                and int(row["stage"])
                == EXPECTED_FAILURE_STAGE
                and row["route"]
                == "real_compatible"
                and row["quantity_id"]
                == EXPECTED_FAILURE_QUANTITY
            )
        )

        denominator_floor = bool(
            raw_failure_trace[
                "denominator_uses_floor"
            ]
        )
        nyquist_content_present = (
            float(
                raw_failure_trace[
                    "relevant_nyquist_power_fraction"
                ]
            )
            > 0.0
        )
        hermitian_improved = (
            float(
                rc_failure_trace[
                    "real_compatible_hermitian_residual"
                ]
            )
            < float(
                raw_failure_trace[
                    "raw_hermitian_residual"
                ]
            )
        )

        derivative_comparison_rows = [
            row
            for row in trace_rows
            if (
                int(row["loop_index"])
                == STOP_LOOP_INDEX
                and row["route"]
                == "real_compatible"
            )
        ]
        all_derivatives_preserved = all(
            float(
                row[
                    "raw_to_real_compatible_real_difference_relative"
                ]
            )
            <= REAL_DERIVATIVE_RELATIVE_LIMIT
            for row in derivative_comparison_rows
        )

        work_rows = work_comparison_rows(
            failure_baseline,
            failure_raw_stage1,
            failure_raw_stage2,
            failure_rc_stage1,
            failure_rc_stage2,
        )
        all_work_preserved = not any(
            bool(
                row["material_real_work_change"]
            )
            for row in work_rows
        )

        solver_wavenumbers_preserved = (
            sha256_array(solver.kx)
            == kx_original_hash
            and sha256_array(solver.ky)
            == ky_original_hash
        )
        forcing_preserved = (
            sha256_array(forcing) == forcing_hash
        )
        all_state_identities_passed = (
            current_identity_preserved
            and stage_identity_preserved
            and filtered_identity_preserved
            and solver_wavenumbers_preserved
            and forcing_preserved
        )
        if not all_state_identities_passed:
            raise IntegrityFailure(
                "identity_preservation",
                "one or more protected identities changed",
            )

        source_identities_after = (
            verify_source_identities(repo)
        )
        if (
            source_identities_after
            != source_identities_before
        ):
            raise IntegrityFailure(
                "source_identity_change",
                "source or evidence identities changed",
            )

        primary, effect = determine_conclusions(
            raw_failure_reproduced=
                raw_failure_reproduced,
            real_compatible_passed=
                real_compatible_passed,
            hermitian_improved=
                hermitian_improved,
            nyquist_content_present=
                nyquist_content_present,
            denominator_floor=
                denominator_floor,
            all_derivatives_preserved=
                all_derivatives_preserved,
            all_work_preserved=
                all_work_preserved,
            all_state_identities_passed=
                all_state_identities_passed,
        )

        write_csv_table(
            trace_path,
            TRACE_FIELDNAMES,
            trace_rows,
        )
        write_csv_table(
            work_path,
            WORK_FIELDNAMES,
            work_rows,
        )

        completed_utc = utc_text()
        summary = {
            "schema_id": (
                "STAGE_C_SHADOW_NYQUIST_"
                "REMEDIATION_SUMMARY_V1"
            ),
            "run_id": run_id,
            "primary_conclusion": primary,
            "effect_conclusion": effect,
            "created_utc":
                metadata["created_utc"],
            "completed_utc": completed_utc,
            "repository":
                metadata["repository"],
            "configuration":
                metadata["configuration"],
            "forcing": forcing_statistics,
            "historical_failure": {
                "loop_index": STOP_LOOP_INDEX,
                "completed_steps":
                    STOP_LOOP_INDEX + 1,
                "physical_time": float(
                    failure_baseline[
                        "physical_time"
                    ]
                ),
                "stage":
                    EXPECTED_FAILURE_STAGE,
                "quantity_id":
                    EXPECTED_FAILURE_QUANTITY,
                "raw_ratio":
                    raw_failure_ratio,
                "expected_raw_ratio":
                    EXPECTED_RAW_FAILURE_RATIO,
                "real_compatible_ratio":
                    rc_failure_ratio,
                "localized_real_compatible_reference":
                    EXPECTED_REAL_COMPATIBLE_RATIO,
                "threshold":
                    IMAGINARY_RATIO_LIMIT,
                "raw_failure_reproduced":
                    raw_failure_reproduced,
                "real_compatible_passed":
                    real_compatible_passed,
                "real_compatible_reference_reproduced":
                    real_compatible_reference_reproduced,
                "denominator_uses_floor":
                    denominator_floor,
                "relevant_nyquist_power_fraction":
                    float(
                        raw_failure_trace[
                            "relevant_nyquist_power_fraction"
                        ]
                    ),
                "raw_hermitian_residual":
                    float(
                        raw_failure_trace[
                            "raw_hermitian_residual"
                        ]
                    ),
                "real_compatible_hermitian_residual":
                    float(
                        rc_failure_trace[
                            "real_compatible_hermitian_residual"
                        ]
                    ),
                "current_state_sha256":
                    sha256_array(
                        failure_baseline[
                            "current"
                        ]
                    ),
                "stage_state_sha256":
                    sha256_array(
                        failure_baseline[
                            "stage"
                        ]
                    ),
                "filtered_state_sha256":
                    sha256_array(
                        failure_baseline[
                            "filtered"
                        ]
                    ),
            },
            "controls": {
                "stage_b_rows_reproduced":
                    stage_b_rows_reproduced,
                "partial_rows_reproduced":
                    partial_rows_reproduced,
                "last_passing_operator_values_reproduced":
                    last_passing_operator_values_reproduced,
                "current_state_identity_preserved":
                    current_identity_preserved,
                "stage_state_identity_preserved":
                    stage_identity_preserved,
                "filtered_state_identity_preserved":
                    filtered_identity_preserved,
                "solver_wavenumbers_preserved":
                    solver_wavenumbers_preserved,
                "forcing_preserved":
                    forcing_preserved,
                "source_and_evidence_identities_preserved":
                    True,
                "all_derivatives_preserved":
                    all_derivatives_preserved,
                "all_real_shadow_work_preserved":
                    all_work_preserved,
            },
            "counts": {
                "replay_rows":
                    EXPECTED_REPLAY_ROWS,
                "trace_rows": len(trace_rows),
                "work_rows": len(work_rows),
            },
            "real_work_comparison":
                work_rows,
            "preservation": {
                "protected_solver_modified":
                    False,
                "accepted_baseline_update_modified":
                    False,
                "original_stage_c_runner_modified":
                    False,
                "localization_runner_modified":
                    False,
                "preserved_partial_evidence_modified":
                    False,
                "focused_localization_evidence_modified":
                    False,
                "alternate_trajectories_executed":
                    False,
                "full_stage_c_rerun_performed":
                    False,
                "full_stage_c_rerun_authorized":
                    False,
                "stage_c_specificity_classification_produced":
                    False,
            },
            "limitations": {
                "focused_loop_3059_verification_only":
                    True,
                "full_stage_c_completion":
                    False,
                "method_superiority":
                    False,
                "formal_convergence":
                    False,
                "physical_validation":
                    False,
                "alternate_trajectory_behavior":
                    False,
                "turbulence": False,
                "cascade": False,
                "inertial_range": False,
                "k_minus_3": False,
                "production_readiness":
                    False,
            },
            "outputs":
                metadata["output_files"],
        }
        atomic_write_json(
            summary_path,
            summary,
        )
        atomic_write_text(
            report_path,
            render_report(summary),
        )

        metadata["status"] = "completed"
        metadata["primary_conclusion"] = primary
        metadata["effect_conclusion"] = effect
        metadata["completed_utc"] = completed_utc
        metadata["progress"] = {
            "last_replayed_loop_index":
                last_replayed_loop,
            "stage_b_rows_reproduced":
                stage_b_rows_reproduced,
            "partial_rows_reproduced":
                partial_rows_reproduced,
        }
        metadata["historical_failure"] = {
            "loop_index": STOP_LOOP_INDEX,
            "stage": EXPECTED_FAILURE_STAGE,
            "quantity_id":
                EXPECTED_FAILURE_QUANTITY,
            "raw_ratio": raw_failure_ratio,
            "real_compatible_ratio":
                rc_failure_ratio,
        }
        atomic_write_json(
            metadata_path,
            metadata,
        )

        inventory_hash = write_inventory(
            run_directory,
            inventory_path,
            (
                metadata_path,
                trace_path,
                work_path,
                summary_path,
                report_path,
            ),
        )

        observed_files = sorted(
            path.name
            for path in run_directory.iterdir()
            if path.is_file()
        )
        if observed_files != sorted(
            OUTPUT_FILENAMES
        ):
            raise IntegrityFailure(
                "output_file_set",
                f"observed={observed_files}, "
                f"expected={sorted(OUTPUT_FILENAMES)}",
            )

        print()
        print("=" * 72)
        print(
            "STAGE C SHADOW NYQUIST REMEDIATION "
            "VERIFICATION: COMPLETE"
        )
        print("=" * 72)
        print("Last replayed loop index:", last_replayed_loop)
        print(
            "Stage B rows reproduced:",
            stage_b_rows_reproduced,
        )
        print(
            "Partial Stage C rows reproduced:",
            partial_rows_reproduced,
        )
        print(
            "Historical raw failure loop:",
            STOP_LOOP_INDEX,
        )
        print(
            "Historical raw failure stage:",
            EXPECTED_FAILURE_STAGE,
        )
        print(
            "Historical raw failure quantity:",
            EXPECTED_FAILURE_QUANTITY,
        )
        print("Raw imaginary ratio:", raw_failure_ratio)
        print(
            "Real-compatible imaginary ratio:",
            rc_failure_ratio,
        )
        print("Primary conclusion:", primary)
        print("Effect conclusion:", effect)
        print("Protected baseline update modified: NO")
        print("Alternate trajectories executed: NO")
        print("Full Stage C rerun performed: NO")
        print("Full Stage C rerun authorized: NO")
        print(
            "Stage C specificity classification produced: NO"
        )
        print("Run directory:", run_directory)
        print(
            "File inventory SHA256:",
            inventory_hash,
        )
        return 0

    except BaseException as error:
        if isinstance(error, IntegrityFailure):
            failed_gate = error.gate
            failed_quantity = error.quantity_id
            failed_stage = error.stage
        else:
            failed_gate = type(error).__name__

        if ledger_handle is not None:
            try:
                ledger_handle.close()
            except Exception:
                pass

        metadata["status"] = "failed"
        metadata["primary_conclusion"] = (
            "NUMERICAL INTEGRITY FAILURE"
        )
        metadata["effect_conclusion"] = (
            "REAL SHADOW WORK EFFECT INCONCLUSIVE"
        )
        metadata["completed_utc"] = utc_text()
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = str(error)
        metadata["failed_gate"] = failed_gate
        metadata["failed_quantity"] = failed_quantity
        metadata["failed_stage"] = failed_stage
        metadata["progress"] = {
            "last_replayed_loop_index":
                last_replayed_loop,
        }
        try:
            atomic_write_json(
                metadata_path,
                metadata,
            )
        except Exception:
            pass
        try:
            inventory_hash = write_inventory(
                run_directory,
                inventory_path,
                (
                    metadata_path,
                    trace_path,
                    work_path,
                    summary_path,
                    report_path,
                ),
            )
        except Exception:
            inventory_hash = None

        print()
        print(
            "STAGE C SHADOW NYQUIST "
            "REMEDIATION VERIFICATION: FAILED"
        )
        print("Failed gate:", failed_gate)
        if failed_quantity is not None:
            print(
                "Failed quantity:",
                failed_quantity,
            )
        if failed_stage is not None:
            print("Failed stage:", failed_stage)
        print(
            "Partial focused evidence preserved at:",
            run_directory,
        )
        print("Full Stage C rerun authorized: NO")
        if inventory_hash is not None:
            print(
                "Partial inventory SHA256:",
                inventory_hash,
            )
        raise
    finally:
        if ledger_handle is not None:
            try:
                ledger_handle.close()
            except Exception:
                pass


# ============================================================================
# Command line
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the controlled "
            "Stage C shadow-only Nyquist remediation "
            "verification."
        )
    )
    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help=(
            "inspect source without numerical execution, "
            "or run the single focused verification"
        ),
    )
    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent

    if arguments.mode == "inspect":
        return inspect_runner(repo)
    if arguments.mode == "run":
        return execute_remediation(repo)

    raise RuntimeError(
        f"unsupported mode: {arguments.mode!r}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
