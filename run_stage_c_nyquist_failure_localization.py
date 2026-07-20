"""
Controlled Stage C Nyquist imaginary-ratio failure localization.

Usage:
    python -B run_stage_c_nyquist_failure_localization.py inspect
    python -B run_stage_c_nyquist_failure_localization.py run

The inspection path performs source and repository checks without importing
project modules, constructing a solver, writing files, or executing numerical
timesteps.

The run path reproduces one baseline centered-advection trajectory only until
the first original Stage C imaginary-ratio failure. It reports the five parent
gate quantities separately, measures even-grid Nyquist content, compares raw
ik differentiation against a Nyquist-zeroed real-compatible diagnostic route,
and then stops. It does not resume the full Stage C audit and produces no
operator-form-specificity classification.
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

RUNNER_NAME = "run_stage_c_nyquist_failure_localization.py"

AUTHORIZED_DESIGN_COMMIT = (
    "e1950232e85a5376cab850fbcde13619b0628610"
)

LOCALIZATION_DESIGN_PATH = Path(
    "STAGE_C_NYQUIST_IMAGINARY_RATIO_FAILURE_LOCALIZATION_AND_REMEDIATION_DESIGN.md"
)
EXPECTED_LOCALIZATION_DESIGN_SHA256 = (
    "809196A724D4CD94C936A6A96BB7A6B39717A6667EB57D932ED023C6469EC1A2"
)

STAGE_C_RUNNER_PATH = Path(
    "run_stage_c_same_state_advection_shadow_audit.py"
)
EXPECTED_STAGE_C_RUNNER_SHA256 = (
    "5E13CF350DF5356E1E8E44F0D921A7C92FFDD6830978466DFA5B6648818F4BC1"
)

STAGE_C_DESIGN_PATH = Path(
    "STAGE_C_SAME_STATE_ADVECTION_FORM_SHADOW_AUDIT_DESIGN.md"
)
EXPECTED_STAGE_C_DESIGN_SHA256 = (
    "4C14EEA8E492CC5824686C3540D9ABF96EA3413C5F4B9B9A8E1D5EDD470D7D0C"
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

STAGE_B_EVIDENCE_DIRECTORY = (
    Path("experiments")
    / "forcing_budget_stage_b_ledger"
    / "stage_b_exact_operator_ledger_20260720T063420Z_5c464c2"
)
STAGE_B_LEDGER_SHA256 = (
    "5EABDFB33B932089910B61C119A223EED83D4EF9247593C3B02DA68B1D74B115"
)

EXPECTED_FORCING_SHA256 = (
    "504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB"
)


# ============================================================================
# Frozen numerical configuration and localization policy
# ============================================================================

N = 64
RE = 1000
NU = 1.0 / RE
DT = 0.005
FULL_STAGE_C_STEPS = 20001

LAST_KNOWN_PASSING_LOOP_INDEX = 3058
EXPECTED_FIRST_FAILING_LOOP_INDEX = 3059
HARD_STOP_LOOP_INDEX = 3100

EXPECTED_PARTIAL_STATE_ROWS = 3059
EXPECTED_PARTIAL_SHADOW_ROWS = 21413
EXPECTED_LAST_PASSING_PHYSICAL_TIME = 15.295
EXPECTED_LAST_PASSING_Z = 0.00247703643047042
EXPECTED_LAST_PASSING_BASELINE_WORK = 1.7413851867416074e-07
EXPECTED_LAST_PASSING_STAGE1_RATIO = 3.2467038768288357e-15
EXPECTED_LAST_PASSING_STAGE2_RATIO = 9.955198638157299e-14

IMAGINARY_RATIO_LIMIT = 1.0e-13
RESIDUAL_FLOOR = 1.0e-30
SPECTRAL_POWER_FLOOR = 1.0e-300

BASELINE_COMPARE_RELATIVE_TOLERANCE = 1.0e-12
BASELINE_COMPARE_ABSOLUTE_TOLERANCE = 1.0e-18

REAL_DERIVATIVE_RELATIVE_LIMIT = 1.0e-10
REAL_TRANSPORT_RELATIVE_LIMIT = 1.0e-10
WORK_ABSOLUTE_LIMIT = 1.0e-14
WORK_RELATIVE_LIMIT = 1.0e-6

FORCING_TARGET_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14

OUTPUT_ROOT = (
    Path("experiments")
    / "advection_form_shadow_audit_localization"
)
RUN_PREFIX = "stage_c_nyquist_failure_localization_"

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

PRIMARY_CONCLUSIONS = (
    "FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION",
    "FAILURE NOT EXPLAINED BY NYQUIST DERIVATIVE CONVENTION",
    "LOCALIZATION INCONCLUSIVE",
    "NUMERICAL INTEGRITY FAILURE",
)

EFFECT_CONCLUSIONS = (
    "NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT",
    "NYQUIST TREATMENT ALSO CHANGES REAL SHADOW WORK",
    "NYQUIST REAL-WORK EFFECT INCONCLUSIVE",
)


# ============================================================================
# Output schemas
# ============================================================================

TRACE_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "stage",
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
    "is_maximum_for_stage",
    "is_first_failing_quantity",
    "state_sha256",
)

NYQUIST_FIELDNAMES = (
    "loop_index",
    "physical_time",
    "stage",
    "field_id",
    "total_power",
    "x_nyquist_power",
    "y_nyquist_power",
    "nyquist_corner_power",
    "x_nyquist_fraction",
    "y_nyquist_fraction",
    "nyquist_corner_fraction",
    "input_hermitian_residual",
    "raw_x_derivative_hermitian_residual",
    "raw_y_derivative_hermitian_residual",
    "nyquist_zeroed_x_derivative_hermitian_residual",
    "nyquist_zeroed_y_derivative_hermitian_residual",
)

RAW_VS_NYQUIST_FIELDNAMES = (
    "loop_index",
    "physical_time",
    "stage",
    "field_id",
    "derivative_direction",
    "raw_real_rms",
    "raw_imaginary_rms",
    "raw_imaginary_ratio",
    "nyquist_zeroed_real_rms",
    "nyquist_zeroed_imaginary_rms",
    "nyquist_zeroed_imaginary_ratio",
    "real_part_difference_rms",
    "real_part_difference_max_abs",
    "real_part_difference_relative",
    "real_part_cosine_similarity",
    "derivative_power_removed",
    "derivative_power_removed_fraction",
    "operator_id",
    "raw_operator_work",
    "nyquist_zeroed_operator_work",
    "operator_work_absolute_difference",
    "operator_work_relative_difference",
    "operator_work_sign_changed",
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
    "imaginary_ratio_trace.csv",
    "nyquist_spectral_content.csv",
    "raw_vs_nyquist_zeroed.csv",
    "localization_summary.json",
    "STAGE_C_NYQUIST_FAILURE_LOCALIZATION_REPORT.md",
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
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    return sha256_bytes(array.tobytes(order="C"))


def field_rms(value: object) -> float:
    array = np.asarray(value, dtype=np.float64)
    return float(np.sqrt(np.mean(array * array)))


def complex_rms(value: object) -> float:
    array = np.asarray(value, dtype=np.complex128)
    return float(np.sqrt(np.mean(np.abs(array) ** 2)))


def max_abs(value: object) -> float:
    return float(np.max(np.abs(np.asarray(value))))


def mean_product(first: object, second: object) -> float:
    return float(
        np.mean(
            np.asarray(first, dtype=np.float64)
            * np.asarray(second, dtype=np.float64)
        )
    )


def enstrophy(value: object) -> float:
    array = np.asarray(value, dtype=np.float64)
    return 0.5 * float(np.mean(array * array))


def cosine_similarity(first: object, second: object) -> float:
    first_array = np.asarray(first, dtype=np.float64).ravel()
    second_array = np.asarray(second, dtype=np.float64).ravel()
    denominator = float(
        np.linalg.norm(first_array) * np.linalg.norm(second_array)
    )
    if denominator <= RESIDUAL_FLOOR:
        return 1.0 if np.array_equal(first_array, second_array) else 0.0
    return float(np.dot(first_array, second_array) / denominator)


def relative_difference(
    first: float,
    second: float,
    *,
    floor: float = RESIDUAL_FLOOR,
) -> float:
    return abs(first - second) / max(abs(first), abs(second), floor)


def scalar_matches(observed: float, expected: float) -> bool:
    absolute = abs(observed - expected)
    relative = absolute / max(abs(expected), BASELINE_COMPARE_ABSOLUTE_TOLERANCE)
    return (
        absolute <= BASELINE_COMPARE_ABSOLUTE_TOLERANCE
        or relative <= BASELINE_COMPARE_RELATIVE_TOLERANCE
    )


def assert_unique_headers(name: str, fieldnames: Sequence[str]) -> None:
    observed = tuple(fieldnames)
    if len(observed) != len(set(observed)):
        duplicates = sorted(
            value
            for value in set(observed)
            if observed.count(value) > 1
        )
        raise RuntimeError(f"duplicate headers in {name}: {duplicates}")


def assert_all_output_headers_unique() -> None:
    assert_unique_headers("imaginary_ratio_trace.csv", TRACE_FIELDNAMES)
    assert_unique_headers("nyquist_spectral_content.csv", NYQUIST_FIELDNAMES)
    assert_unique_headers("raw_vs_nyquist_zeroed.csv", RAW_VS_NYQUIST_FIELDNAMES)
    assert_unique_headers("file_inventory.csv", INVENTORY_FIELDNAMES)


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
        reader = csv.DictReader(handle)
        assert_unique_headers(path.name, tuple(reader.fieldnames or ()))
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


class IncrementalCsvWriter:
    def __init__(
        self,
        path: Path,
        fieldnames: Sequence[str],
        *,
        flush_interval: int = 250,
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
        if set(row) != set(self.fieldnames):
            raise RuntimeError(
                f"CSV row schema mismatch for {self.path.name}: "
                f"missing={sorted(set(self.fieldnames) - set(row))}, "
                f"extra={sorted(set(row) - set(self.fieldnames))}"
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
# Git and source identity helpers
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


def git_read(repo: Path, *args: str) -> str:
    return str(git_process(repo, *args).stdout).strip()


def git_bytes(repo: Path, *args: str) -> bytes:
    return bytes(git_process(repo, *args, text=False).stdout)


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
    working = git_read(
        repo,
        "hash-object",
        f"--path={relative}",
        "--",
        relative,
    )
    committed = git_read(repo, "rev-parse", f"HEAD:{relative}")
    if working != expected_blob or committed != expected_blob:
        raise RuntimeError(
            f"Git blob mismatch for {relative}: "
            f"working={working}, committed={committed}, expected={expected_blob}"
        )
    return working


def verify_partial_evidence(repo: Path) -> dict[str, str]:
    directory = repo / PARTIAL_STAGE_C_DIRECTORY
    if not directory.is_dir():
        raise RuntimeError(
            f"preserved partial Stage C directory is missing: {directory}"
        )
    observed: dict[str, str] = {}
    for name, expected in PARTIAL_STAGE_C_HASHES.items():
        path = directory / name
        if not path.is_file():
            raise RuntimeError(f"preserved partial file is missing: {path}")
        value = sha256_file(path)
        if value != expected:
            raise RuntimeError(
                f"preserved partial SHA256 mismatch for {path}: "
                f"observed={value}, expected={expected}"
            )
        observed[name] = value
    actual_files = sorted(path.name for path in directory.iterdir() if path.is_file())
    expected_files = sorted(PARTIAL_STAGE_C_HASHES)
    if actual_files != expected_files:
        raise RuntimeError(
            f"preserved partial file set changed: "
            f"observed={actual_files}, expected={expected_files}"
        )
    return observed


def verify_source_identities(repo: Path) -> dict[str, str]:
    identities = {
        "localization_design": verify_file_hash(
            repo,
            LOCALIZATION_DESIGN_PATH,
            EXPECTED_LOCALIZATION_DESIGN_SHA256,
        ),
        "stage_c_runner": verify_file_hash(
            repo,
            STAGE_C_RUNNER_PATH,
            EXPECTED_STAGE_C_RUNNER_SHA256,
        ),
        "stage_c_design": verify_file_hash(
            repo,
            STAGE_C_DESIGN_PATH,
            EXPECTED_STAGE_C_DESIGN_SHA256,
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
    }
    ledger_path = (
        repo
        / STAGE_B_EVIDENCE_DIRECTORY
        / "operator_ledger_per_step.csv"
    )
    if sha256_file(ledger_path) != STAGE_B_LEDGER_SHA256:
        raise RuntimeError("Stage B per-step ledger identity mismatch")
    identities["stage_b_ledger"] = STAGE_B_LEDGER_SHA256
    for name, value in verify_partial_evidence(repo).items():
        identities[f"partial/{name}"] = value
    return identities


def verify_inspection_repository_state(repo: Path, runner: Path) -> None:
    branch = git_read(repo, "branch", "--show-current")
    if branch != "phase4_validation":
        fail(f"active branch is {branch!r}, expected 'phase4_validation'")
    head = git_read(repo, "rev-parse", "HEAD")
    if head != AUTHORIZED_DESIGN_COMMIT:
        fail(
            f"HEAD is {head}, expected localization design checkpoint "
            f"{AUTHORIZED_DESIGN_COMMIT}"
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
        fail(f"Git status is {status!r}, expected {expected!r}")


def verify_runner_commit_shape(repo: Path, runner: Path) -> str:
    branch = git_read(repo, "branch", "--show-current")
    if branch != "phase4_validation":
        raise RuntimeError("active branch is not phase4_validation")
    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise RuntimeError(f"working tree is not clean: {status}")
    head = git_read(repo, "rev-parse", "HEAD")
    parent = git_read(repo, "rev-parse", "HEAD^")
    if parent != AUTHORIZED_DESIGN_COMMIT:
        raise RuntimeError(
            f"runner commit parent is {parent}, expected {AUTHORIZED_DESIGN_COMMIT}"
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
            f"runner commit must change exactly one file; observed={changed!r}"
        )
    if git_bytes(repo, "show", f"HEAD:{runner.name}") != runner.read_bytes():
        raise RuntimeError("working runner bytes differ from committed bytes")
    remote = git_read(repo, "rev-parse", "origin/phase4_validation")
    if remote != head:
        raise RuntimeError(
            f"remote branch is {remote}, expected execution commit {head}"
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


def inspect_ast(source: str) -> dict[str, object]:
    tree = ast.parse(source, filename=RUNNER_NAME)
    parent: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    project_imports: list[str] = []
    constructor_calls = 0
    forbidden_calls: list[str] = []
    run_calls: list[str] = []

    def containing_function(node: ast.AST) -> str | None:
        current = parent.get(node)
        while current is not None:
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return current.name
            current = parent.get(current)
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("project."):
                if containing_function(node) != "execute_localization":
                    raise RuntimeError(
                        f"project import outside run path: {module}"
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
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "subprocess"
                    ):
                        run_calls.append("run")

    if constructor_calls != 1:
        raise RuntimeError(
            f"SpectralSolver constructor calls={constructor_calls}, expected=1"
        )
    if forbidden_calls:
        raise RuntimeError(f"forbidden selectable calls: {forbidden_calls}")
    if run_calls:
        raise RuntimeError("protected or selectable run() call is present")

    for text in FORBIDDEN_CLASSIFICATION_STRINGS:
        if text in source:
            raise RuntimeError(
                f"full Stage C classification string present: {text}"
            )

    if "HARD_STOP_LOOP_INDEX" not in source:
        raise RuntimeError("hard localization stop is missing")
    if "break" not in source:
        raise RuntimeError("stop-at-first-failure control is missing")

    return {
        "project_imports": project_imports,
        "spectral_solver_constructor_calls": constructor_calls,
        "forbidden_calls": forbidden_calls,
        "run_calls": run_calls,
    }


def inspect_runner(repo: Path) -> int:
    runner = Path(__file__).resolve()
    if runner.name != RUNNER_NAME:
        fail(f"runner filename is {runner.name!r}, expected {RUNNER_NAME!r}")
    raw = runner.read_bytes()
    if b"\r" in raw:
        fail("runner bytes are not LF-only")
    try:
        source = raw.decode("utf-8")
        compile(source, str(runner), "exec")
    except (UnicodeDecodeError, SyntaxError) as error:
        fail(f"runner source is invalid: {error}")

    verify_inspection_repository_state(repo, runner)
    identities = verify_source_identities(repo)
    assert_all_output_headers_unique()
    ast_summary = inspect_ast(source)

    if IMAGINARY_RATIO_LIMIT != 1.0e-13:
        fail("historical imaginary-ratio threshold was changed")
    if LAST_KNOWN_PASSING_LOOP_INDEX != 3058:
        fail("last known passing index differs from frozen design")
    if EXPECTED_FIRST_FAILING_LOOP_INDEX != 3059:
        fail("expected first failing index differs from frozen design")
    if HARD_STOP_LOOP_INDEX > 3100:
        fail("hard stop permits an excessive localization range")
    if QUANTITY_IDS != (
        "omega_gradient_imaginary_ratio",
        "projected_baseline_transport_imaginary_ratio",
        "projected_pseudo_transport_imaginary_ratio",
        "u_x_gradient_imaginary_ratio",
        "v_y_gradient_imaginary_ratio",
    ):
        fail("five-quantity registry differs from frozen design")

    print()
    print("=" * 72)
    print("STAGE C NYQUIST FAILURE-LOCALIZATION RUNNER INSPECTION: PASS")
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", sha256_bytes(raw))
    print("Design commit:", AUTHORIZED_DESIGN_COMMIT)
    print("Localization design SHA256:", identities["localization_design"])
    print("Configuration: N64, Re1000, dt0.005")
    print("Last known passing loop index: 3058")
    print("Expected first failing loop index: 3059")
    print("Hard localization stop: loop index 3100")
    print("Five imaginary-ratio quantities: PRESENT")
    print("Absolute real/imaginary RMS reporting: PRESENT")
    print("Nyquist-line spectral power diagnostics: PRESENT")
    print("Hermitian-symmetry diagnostics: PRESENT")
    print("Raw-ik derivative route: PRESENT")
    print("Nyquist-zeroed derivative route: PRESENT")
    print("Real shadow-work comparison: PRESENT")
    print("Stop-at-first-failure policy: PRESENT")
    print("Preserved partial evidence identities: PASS")
    print("All output header lists unique: PASS")
    print("Historical threshold unchanged: PASS")
    print(
        "SpectralSolver constructor calls:",
        ast_summary["spectral_solver_constructor_calls"],
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
    print("Full Stage C rerun authorized: NO")
    print("Focused localization execution authorized by inspection: NO")
    return 0


# ============================================================================
# Baseline and forcing
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
    base = 0.01 * np.sin(2.0 * x) * np.cos(2.0 * y)
    raw = (
        1.00 * np.sin(2.0 * x) * np.cos(2.0 * y)
        + 0.75 * np.sin(3.0 * x) * np.cos(y)
        + 0.50 * np.sin(x) * np.cos(4.0 * y)
        + 0.35 * np.cos(4.0 * x - 2.0 * y)
    )
    raw = np.asarray(raw, dtype=np.float64)
    raw = raw - np.mean(raw)
    raw_rms = field_rms(raw)
    base_rms = field_rms(base)
    coefficient = base_rms / raw_rms
    forcing = np.ascontiguousarray(coefficient * raw, dtype=np.float64)
    forcing_hash = sha256_array(forcing)
    if forcing_hash != EXPECTED_FORCING_SHA256:
        raise IntegrityFailure(
            "forcing_sha256",
            f"forcing SHA256={forcing_hash}, expected={EXPECTED_FORCING_SHA256}",
        )
    if not math.isclose(
        field_rms(forcing),
        FORCING_TARGET_RMS,
        rel_tol=0.0,
        abs_tol=FORCING_RMS_TOLERANCE,
    ):
        raise IntegrityFailure("forcing_rms", "forcing RMS differs from 0.005")
    forcing.setflags(write=False)
    return forcing, {
        "forcing_sha256": forcing_hash,
        "forcing_terms": list(FORCING_TERMS),
        "target_rms": FORCING_TARGET_RMS,
        "normalized_rms": field_rms(forcing),
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
    current = np.asarray(baseline_omega, dtype=np.float64)

    psi_1 = solver.streamfunction(current)
    u_1, v_1 = solver.velocity(psi_1)
    omega_x_1, omega_y_1 = centered_gradients(current, float(solver.dx))
    transport_1 = u_1 * omega_x_1 + v_1 * omega_y_1
    advection_1 = -transport_1
    viscous_1 = solver.laplacian_spectral(current)
    total_1 = advection_1 + viscous_1 + forcing
    stage = current + float(solver.dt) * total_1

    psi_2 = solver.streamfunction(stage)
    u_2, v_2 = solver.velocity(psi_2)
    omega_x_2, omega_y_2 = centered_gradients(stage, float(solver.dx))
    transport_2 = u_2 * omega_x_2 + v_2 * omega_y_2
    advection_2 = -transport_2
    viscous_2 = solver.laplacian_spectral(stage)
    total_2 = advection_2 + viscous_2 + forcing

    unfiltered = (
        current
        + 0.5 * float(solver.dt) * (total_1 + total_2)
    )
    filtered_complex = np.fft.ifft2(
        np.fft.fft2(unfiltered) * np.asarray(solver.deal)
    )
    filtered = filtered_complex.real

    if not all(
        np.isfinite(value).all()
        for value in (current, stage, unfiltered, filtered)
    ):
        raise IntegrityFailure(
            "baseline_finite",
            f"baseline state is nonfinite at loop_index={loop_index}",
        )

    stage1_work = mean_product(current, advection_1)
    stage2_work = mean_product(stage, advection_2)

    return {
        "loop_index": loop_index,
        "completed_steps": loop_index + 1,
        "physical_time": (loop_index + 1) * float(solver.dt),
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
        "z_filtered": enstrophy(filtered),
        "stage1_work": stage1_work,
        "stage2_work": stage2_work,
        "rk2_work": 0.5 * (stage1_work + stage2_work),
    }


# ============================================================================
# Complex measurements and Nyquist diagnostics
# ============================================================================

def complex_measurement(
    quantity_id: str,
    components: Mapping[str, np.ndarray],
) -> dict[str, object]:
    if not components:
        raise ValueError("components must not be empty")

    component_values: dict[str, dict[str, float]] = {}
    for direction, value in components.items():
        array = np.asarray(value, dtype=np.complex128)
        component_values[direction] = {
            "real_rms": field_rms(array.real),
            "imaginary_rms": field_rms(array.imag),
            "real_max_abs": max_abs(array.real),
            "imaginary_max_abs": max_abs(array.imag),
        }

    real_direction = max(
        component_values,
        key=lambda key: component_values[key]["real_rms"],
    )
    imaginary_direction = max(
        component_values,
        key=lambda key: component_values[key]["imaginary_rms"],
    )

    real_rms = component_values[real_direction]["real_rms"]
    imaginary_rms = component_values[imaginary_direction]["imaginary_rms"]
    denominator = max(real_rms, RESIDUAL_FLOOR)

    return {
        "quantity_id": quantity_id,
        "dominant_direction": imaginary_direction,
        "real_rms": real_rms,
        "imaginary_rms": imaginary_rms,
        "imaginary_ratio": imaginary_rms / denominator,
        "real_max_abs": max(
            value["real_max_abs"]
            for value in component_values.values()
        ),
        "imaginary_max_abs": max(
            value["imaginary_max_abs"]
            for value in component_values.values()
        ),
        "ratio_denominator": denominator,
        "denominator_uses_floor": real_rms <= RESIDUAL_FLOOR,
        "components": component_values,
    }


def raw_derivative_pair(
    field: np.ndarray,
    kx: np.ndarray,
    ky: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    field_hat = np.fft.fft2(np.asarray(field, dtype=np.float64))
    return (
        np.fft.ifft2(1j * kx * field_hat),
        np.fft.ifft2(1j * ky * field_hat),
    )


def nyquist_zeroed_wavenumbers(
    kx: np.ndarray,
    ky: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    nyquist_value = -N / 2
    x_mask = np.asarray(kx == nyquist_value)
    y_mask = np.asarray(ky == nyquist_value)

    if not x_mask.any() or not y_mask.any():
        raise IntegrityFailure(
            "nyquist_location",
            "actual solver wavenumbers do not contain -N/2",
        )

    kx_zeroed = np.array(kx, dtype=np.float64, copy=True)
    ky_zeroed = np.array(ky, dtype=np.float64, copy=True)
    kx_zeroed[x_mask] = 0.0
    ky_zeroed[y_mask] = 0.0

    return kx_zeroed, ky_zeroed, x_mask, y_mask


def project_complex(field: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return np.fft.ifft2(
        np.fft.fft2(np.asarray(field, dtype=np.float64)) * mask
    )


def build_stage_diagnostics(
    solver: object,
    state: np.ndarray,
    psi: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    *,
    stage: int,
) -> dict[str, object]:
    kx = np.asarray(solver.kx)
    ky = np.asarray(solver.ky)
    deal = np.asarray(solver.deal)

    omega_x_raw, omega_y_raw = raw_derivative_pair(state, kx, ky)
    omega_measure = complex_measurement(
        "omega_gradient_imaginary_ratio",
        {"x": omega_x_raw, "y": omega_y_raw},
    )

    baseline_x, baseline_y = centered_gradients(state, float(solver.dx))
    baseline_transport = u * baseline_x + v * baseline_y
    projected_baseline_complex = project_complex(
        baseline_transport,
        deal,
    )
    projected_baseline_measure = complex_measurement(
        "projected_baseline_transport_imaginary_ratio",
        {"projection": projected_baseline_complex},
    )

    pseudo_raw_transport = (
        u * omega_x_raw.real
        + v * omega_y_raw.real
    )
    projected_pseudo_complex = project_complex(
        pseudo_raw_transport,
        deal,
    )
    projected_pseudo_measure = complex_measurement(
        "projected_pseudo_transport_imaginary_ratio",
        {"projection": projected_pseudo_complex},
    )

    u_x_raw, u_y_raw = raw_derivative_pair(u, kx, ky)
    u_measure = complex_measurement(
        "u_x_gradient_imaginary_ratio",
        {"x": u_x_raw, "y_auxiliary": u_y_raw},
    )

    v_x_raw, v_y_raw = raw_derivative_pair(v, kx, ky)
    v_measure = complex_measurement(
        "v_y_gradient_imaginary_ratio",
        {"x_auxiliary": v_x_raw, "y": v_y_raw},
    )

    measurements = [
        omega_measure,
        projected_baseline_measure,
        projected_pseudo_measure,
        u_measure,
        v_measure,
    ]

    if tuple(
        str(item["quantity_id"])
        for item in measurements
    ) != QUANTITY_IDS:
        raise IntegrityFailure(
            "quantity_registry",
            "five-quantity order differs from frozen design",
            stage=stage,
        )

    maximum_ratio = max(
        float(item["imaginary_ratio"])
        for item in measurements
    )
    failing = [
        item
        for item in measurements
        if float(item["imaginary_ratio"]) > IMAGINARY_RATIO_LIMIT
    ]

    return {
        "stage": stage,
        "state": state,
        "state_sha256": sha256_array(state),
        "psi": psi,
        "u": u,
        "v": v,
        "measurements": measurements,
        "maximum_ratio": maximum_ratio,
        "failing_measurements": failing,
        "baseline_transport": baseline_transport,
        "projected_baseline_transport": projected_baseline_complex.real,
        "pseudo_raw_transport": pseudo_raw_transport,
        "projected_pseudo_transport": projected_pseudo_complex.real,
        "omega_x_raw": omega_x_raw,
        "omega_y_raw": omega_y_raw,
        "u_x_raw": u_x_raw,
        "u_y_raw": u_y_raw,
        "v_x_raw": v_x_raw,
        "v_y_raw": v_y_raw,
    }


def trace_rows_for_stage(
    diagnostics: Mapping[str, object],
    *,
    loop_index: int,
    physical_time: float,
    first_failure: bool,
) -> list[dict[str, object]]:
    measurements = list(diagnostics["measurements"])
    maximum = max(
        float(item["imaginary_ratio"])
        for item in measurements
    )
    failing_maximum = [
        item
        for item in measurements
        if (
            float(item["imaginary_ratio"]) > IMAGINARY_RATIO_LIMIT
            and float(item["imaginary_ratio"]) == maximum
        )
    ]
    rows: list[dict[str, object]] = []

    for item in measurements:
        ratio = float(item["imaginary_ratio"])
        row = {
            "loop_index": loop_index,
            "completed_steps": loop_index + 1,
            "physical_time": physical_time,
            "stage": int(diagnostics["stage"]),
            "quantity_id": str(item["quantity_id"]),
            "dominant_direction": str(item["dominant_direction"]),
            "real_rms": float(item["real_rms"]),
            "imaginary_rms": float(item["imaginary_rms"]),
            "imaginary_ratio": ratio,
            "real_max_abs": float(item["real_max_abs"]),
            "imaginary_max_abs": float(item["imaginary_max_abs"]),
            "ratio_denominator": float(item["ratio_denominator"]),
            "denominator_uses_floor": bool(
                item["denominator_uses_floor"]
            ),
            "threshold": IMAGINARY_RATIO_LIMIT,
            "threshold_pass": ratio <= IMAGINARY_RATIO_LIMIT,
            "is_maximum_for_stage": ratio == maximum,
            "is_first_failing_quantity": (
                first_failure and item in failing_maximum
            ),
            "state_sha256": str(diagnostics["state_sha256"]),
        }
        if not all_numeric_values_finite(row):
            raise IntegrityFailure(
                "trace_row_finite",
                "trace row contains a nonfinite scalar",
                quantity_id=str(item["quantity_id"]),
                stage=int(diagnostics["stage"]),
            )
        rows.append(row)

    return rows


def hermitian_residual(spectrum: np.ndarray) -> float:
    array = np.asarray(spectrum, dtype=np.complex128)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError("Hermitian diagnostic requires a square 2D spectrum")
    indices = (-np.arange(array.shape[0])) % array.shape[0]
    partner = np.conj(array[np.ix_(indices, indices)])
    difference = complex_rms(array - partner)
    return difference / max(complex_rms(array), RESIDUAL_FLOOR)


def nyquist_content_row(
    field: np.ndarray,
    *,
    loop_index: int,
    physical_time: float,
    stage: int,
    field_id: str,
    kx: np.ndarray,
    ky: np.ndarray,
    x_mask: np.ndarray,
    y_mask: np.ndarray,
    kx_zeroed: np.ndarray,
    ky_zeroed: np.ndarray,
) -> dict[str, object]:
    spectrum = np.fft.fft2(np.asarray(field, dtype=np.float64))
    total = float(np.sum(np.abs(spectrum) ** 2))
    x_power = float(np.sum(np.abs(spectrum[x_mask]) ** 2))
    y_power = float(np.sum(np.abs(spectrum[y_mask]) ** 2))
    corner_mask = x_mask & y_mask
    corner = float(np.sum(np.abs(spectrum[corner_mask]) ** 2))

    raw_x = 1j * kx * spectrum
    raw_y = 1j * ky * spectrum
    zeroed_x = 1j * kx_zeroed * spectrum
    zeroed_y = 1j * ky_zeroed * spectrum

    row = {
        "loop_index": loop_index,
        "physical_time": physical_time,
        "stage": stage,
        "field_id": field_id,
        "total_power": total,
        "x_nyquist_power": x_power,
        "y_nyquist_power": y_power,
        "nyquist_corner_power": corner,
        "x_nyquist_fraction": x_power / max(total, SPECTRAL_POWER_FLOOR),
        "y_nyquist_fraction": y_power / max(total, SPECTRAL_POWER_FLOOR),
        "nyquist_corner_fraction": corner / max(total, SPECTRAL_POWER_FLOOR),
        "input_hermitian_residual": hermitian_residual(spectrum),
        "raw_x_derivative_hermitian_residual": hermitian_residual(raw_x),
        "raw_y_derivative_hermitian_residual": hermitian_residual(raw_y),
        "nyquist_zeroed_x_derivative_hermitian_residual": (
            hermitian_residual(zeroed_x)
        ),
        "nyquist_zeroed_y_derivative_hermitian_residual": (
            hermitian_residual(zeroed_y)
        ),
    }
    if not all_numeric_values_finite(row):
        raise IntegrityFailure(
            "nyquist_row_finite",
            f"nonfinite Nyquist row for {field_id}",
            stage=stage,
        )
    return row


def derivative_comparison_row(
    field: np.ndarray,
    *,
    loop_index: int,
    physical_time: float,
    stage: int | str,
    field_id: str,
    direction: str,
    raw_multiplier: np.ndarray,
    zeroed_multiplier: np.ndarray,
) -> dict[str, object]:
    spectrum = np.fft.fft2(np.asarray(field, dtype=np.float64))
    raw_spectrum = 1j * raw_multiplier * spectrum
    zeroed_spectrum = 1j * zeroed_multiplier * spectrum
    raw_complex = np.fft.ifft2(raw_spectrum)
    zeroed_complex = np.fft.ifft2(zeroed_spectrum)

    raw_real_rms = field_rms(raw_complex.real)
    raw_imaginary_rms = field_rms(raw_complex.imag)
    zeroed_real_rms = field_rms(zeroed_complex.real)
    zeroed_imaginary_rms = field_rms(zeroed_complex.imag)
    difference = zeroed_complex.real - raw_complex.real
    difference_rms = field_rms(difference)
    difference_relative = difference_rms / max(
        raw_real_rms,
        zeroed_real_rms,
        RESIDUAL_FLOOR,
    )

    raw_power = float(np.sum(np.abs(raw_spectrum) ** 2))
    zeroed_power = float(np.sum(np.abs(zeroed_spectrum) ** 2))
    removed = max(raw_power - zeroed_power, 0.0)

    return {
        "loop_index": loop_index,
        "physical_time": physical_time,
        "stage": stage,
        "field_id": field_id,
        "derivative_direction": direction,
        "raw_real_rms": raw_real_rms,
        "raw_imaginary_rms": raw_imaginary_rms,
        "raw_imaginary_ratio": (
            raw_imaginary_rms / max(raw_real_rms, RESIDUAL_FLOOR)
        ),
        "nyquist_zeroed_real_rms": zeroed_real_rms,
        "nyquist_zeroed_imaginary_rms": zeroed_imaginary_rms,
        "nyquist_zeroed_imaginary_ratio": (
            zeroed_imaginary_rms
            / max(zeroed_real_rms, RESIDUAL_FLOOR)
        ),
        "real_part_difference_rms": difference_rms,
        "real_part_difference_max_abs": max_abs(difference),
        "real_part_difference_relative": difference_relative,
        "real_part_cosine_similarity": cosine_similarity(
            raw_complex.real,
            zeroed_complex.real,
        ),
        "derivative_power_removed": removed,
        "derivative_power_removed_fraction": (
            removed / max(raw_power, SPECTRAL_POWER_FLOOR)
        ),
        "operator_id": "",
        "raw_operator_work": "",
        "nyquist_zeroed_operator_work": "",
        "operator_work_absolute_difference": "",
        "operator_work_relative_difference": "",
        "operator_work_sign_changed": "",
        "material_real_work_change": (
            difference_relative > REAL_DERIVATIVE_RELATIVE_LIMIT
        ),
    }


def operator_comparison_row(
    state: np.ndarray | None,
    raw_transport: np.ndarray,
    zeroed_transport: np.ndarray,
    *,
    loop_index: int,
    physical_time: float,
    stage: int | str,
    operator_id: str,
    raw_work: float,
    zeroed_work: float,
) -> dict[str, object]:
    difference = zeroed_transport - raw_transport
    raw_rms = field_rms(raw_transport)
    zeroed_rms = field_rms(zeroed_transport)
    difference_rms = field_rms(difference)
    difference_relative = difference_rms / max(
        raw_rms,
        zeroed_rms,
        RESIDUAL_FLOOR,
    )
    work_absolute = abs(zeroed_work - raw_work)
    work_relative = relative_difference(
        zeroed_work,
        raw_work,
        floor=RESIDUAL_FLOOR,
    )
    raw_nonzero = abs(raw_work) > WORK_ABSOLUTE_LIMIT
    zeroed_nonzero = abs(zeroed_work) > WORK_ABSOLUTE_LIMIT
    sign_changed = (
        raw_nonzero
        and zeroed_nonzero
        and math.copysign(1.0, raw_work)
        != math.copysign(1.0, zeroed_work)
    )
    near_zero_character_changed = raw_nonzero != zeroed_nonzero
    material = (
        difference_relative > REAL_TRANSPORT_RELATIVE_LIMIT
        or (
            work_absolute > WORK_ABSOLUTE_LIMIT
            and work_relative > WORK_RELATIVE_LIMIT
        )
        or sign_changed
        or near_zero_character_changed
    )

    return {
        "loop_index": loop_index,
        "physical_time": physical_time,
        "stage": stage,
        "field_id": "pseudo_transport",
        "derivative_direction": "transport",
        "raw_real_rms": raw_rms,
        "raw_imaginary_rms": 0.0,
        "raw_imaginary_ratio": 0.0,
        "nyquist_zeroed_real_rms": zeroed_rms,
        "nyquist_zeroed_imaginary_rms": 0.0,
        "nyquist_zeroed_imaginary_ratio": 0.0,
        "real_part_difference_rms": difference_rms,
        "real_part_difference_max_abs": max_abs(difference),
        "real_part_difference_relative": difference_relative,
        "real_part_cosine_similarity": cosine_similarity(
            raw_transport,
            zeroed_transport,
        ),
        "derivative_power_removed": "",
        "derivative_power_removed_fraction": "",
        "operator_id": operator_id,
        "raw_operator_work": raw_work,
        "nyquist_zeroed_operator_work": zeroed_work,
        "operator_work_absolute_difference": work_absolute,
        "operator_work_relative_difference": work_relative,
        "operator_work_sign_changed": sign_changed,
        "material_real_work_change": material,
    }


def raw_vs_zeroed_at_failure(
    solver: object,
    baseline: Mapping[str, object],
    stage1: Mapping[str, object],
    stage2: Mapping[str, object],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
]:
    loop_index = int(baseline["loop_index"])
    physical_time = float(baseline["physical_time"])
    kx = np.asarray(solver.kx)
    ky = np.asarray(solver.ky)
    deal = np.asarray(solver.deal)
    kx_zeroed, ky_zeroed, x_mask, y_mask = (
        nyquist_zeroed_wavenumbers(kx, ky)
    )

    nyquist_rows: list[dict[str, object]] = []
    comparison_rows: list[dict[str, object]] = []
    stage_operator_data: dict[int, dict[str, object]] = {}

    for stage_number, diagnostics in (
        (1, stage1),
        (2, stage2),
    ):
        state = np.asarray(diagnostics["state"], dtype=np.float64)
        u = np.asarray(diagnostics["u"], dtype=np.float64)
        v = np.asarray(diagnostics["v"], dtype=np.float64)
        baseline_transport = np.asarray(
            diagnostics["baseline_transport"],
            dtype=np.float64,
        )
        pseudo_raw_transport = np.asarray(
            diagnostics["pseudo_raw_transport"],
            dtype=np.float64,
        )

        fields = {
            "vorticity": state,
            "u_velocity": u,
            "v_velocity": v,
            "centered_transport": baseline_transport,
            "pseudo_raw_transport": pseudo_raw_transport,
        }

        for field_id, field in fields.items():
            nyquist_rows.append(
                nyquist_content_row(
                    field,
                    loop_index=loop_index,
                    physical_time=physical_time,
                    stage=stage_number,
                    field_id=field_id,
                    kx=kx,
                    ky=ky,
                    x_mask=x_mask,
                    y_mask=y_mask,
                    kx_zeroed=kx_zeroed,
                    ky_zeroed=ky_zeroed,
                )
            )

        for field_id, field in (
            ("vorticity", state),
            ("u_velocity", u),
            ("v_velocity", v),
        ):
            comparison_rows.append(
                derivative_comparison_row(
                    field,
                    loop_index=loop_index,
                    physical_time=physical_time,
                    stage=stage_number,
                    field_id=field_id,
                    direction="x",
                    raw_multiplier=kx,
                    zeroed_multiplier=kx_zeroed,
                )
            )
            comparison_rows.append(
                derivative_comparison_row(
                    field,
                    loop_index=loop_index,
                    physical_time=physical_time,
                    stage=stage_number,
                    field_id=field_id,
                    direction="y",
                    raw_multiplier=ky,
                    zeroed_multiplier=ky_zeroed,
                )
            )

        state_hat = np.fft.fft2(state)
        omega_x_zeroed = np.fft.ifft2(
            1j * kx_zeroed * state_hat
        ).real
        omega_y_zeroed = np.fft.ifft2(
            1j * ky_zeroed * state_hat
        ).real
        pseudo_zeroed_raw = (
            u * omega_x_zeroed
            + v * omega_y_zeroed
        )
        pseudo_zeroed_projected = np.fft.ifft2(
            np.fft.fft2(pseudo_zeroed_raw) * deal
        ).real

        raw_pseudo = np.asarray(
            diagnostics["pseudo_raw_transport"],
            dtype=np.float64,
        )
        raw_projected = np.asarray(
            diagnostics["projected_pseudo_transport"],
            dtype=np.float64,
        )

        raw_raw_work = mean_product(state, -raw_pseudo)
        zeroed_raw_work = mean_product(state, -pseudo_zeroed_raw)
        raw_projected_work = mean_product(state, -raw_projected)
        zeroed_projected_work = mean_product(
            state,
            -pseudo_zeroed_projected,
        )

        comparison_rows.append(
            operator_comparison_row(
                state,
                raw_pseudo,
                pseudo_zeroed_raw,
                loop_index=loop_index,
                physical_time=physical_time,
                stage=stage_number,
                operator_id="SHADOW_PS_ADVECTIVE_RAW_V1",
                raw_work=raw_raw_work,
                zeroed_work=zeroed_raw_work,
            )
        )
        comparison_rows.append(
            operator_comparison_row(
                state,
                raw_projected,
                pseudo_zeroed_projected,
                loop_index=loop_index,
                physical_time=physical_time,
                stage=stage_number,
                operator_id="SHADOW_PS_ADVECTIVE_PROJECTED_V1",
                raw_work=raw_projected_work,
                zeroed_work=zeroed_projected_work,
            )
        )

        stage_operator_data[stage_number] = {
            "raw_pseudo": raw_pseudo,
            "zeroed_pseudo": pseudo_zeroed_raw,
            "raw_projected": raw_projected,
            "zeroed_projected": pseudo_zeroed_projected,
            "raw_pseudo_work": raw_raw_work,
            "zeroed_pseudo_work": zeroed_raw_work,
            "raw_projected_work": raw_projected_work,
            "zeroed_projected_work": zeroed_projected_work,
        }

    for operator_id, transport_key, work_key in (
        (
            "SHADOW_PS_ADVECTIVE_RAW_V1",
            ("raw_pseudo", "zeroed_pseudo"),
            ("raw_pseudo_work", "zeroed_pseudo_work"),
        ),
        (
            "SHADOW_PS_ADVECTIVE_PROJECTED_V1",
            ("raw_projected", "zeroed_projected"),
            ("raw_projected_work", "zeroed_projected_work"),
        ),
    ):
        raw_stage_weighted = 0.5 * (
            float(stage_operator_data[1][work_key[0]])
            + float(stage_operator_data[2][work_key[0]])
        )
        zeroed_stage_weighted = 0.5 * (
            float(stage_operator_data[1][work_key[1]])
            + float(stage_operator_data[2][work_key[1]])
        )
        raw_transport_average = 0.5 * (
            np.asarray(stage_operator_data[1][transport_key[0]])
            + np.asarray(stage_operator_data[2][transport_key[0]])
        )
        zeroed_transport_average = 0.5 * (
            np.asarray(stage_operator_data[1][transport_key[1]])
            + np.asarray(stage_operator_data[2][transport_key[1]])
        )
        comparison_rows.append(
            operator_comparison_row(
                None,
                raw_transport_average,
                zeroed_transport_average,
                loop_index=loop_index,
                physical_time=physical_time,
                stage="stage_weighted",
                operator_id=operator_id,
                raw_work=raw_stage_weighted,
                zeroed_work=zeroed_stage_weighted,
            )
        )

    for row in comparison_rows:
        if not all_numeric_values_finite(row):
            raise IntegrityFailure(
                "raw_vs_zeroed_row_finite",
                "raw-versus-zeroed output contains nonfinite data",
            )

    material_rows = [
        row
        for row in comparison_rows
        if bool(row["material_real_work_change"])
    ]

    context = {
        "kx_zeroed": kx_zeroed,
        "ky_zeroed": ky_zeroed,
        "x_nyquist_mask": x_mask,
        "y_nyquist_mask": y_mask,
        "material_real_work_change": bool(material_rows),
        "material_rows": material_rows,
        "stage_operator_data": stage_operator_data,
    }
    return nyquist_rows, comparison_rows, context


def nyquist_zeroed_measurements(
    solver: object,
    diagnostics: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    state = np.asarray(diagnostics["state"], dtype=np.float64)
    u = np.asarray(diagnostics["u"], dtype=np.float64)
    v = np.asarray(diagnostics["v"], dtype=np.float64)
    kx = np.asarray(solver.kx)
    ky = np.asarray(solver.ky)
    deal = np.asarray(solver.deal)
    kx_zeroed, ky_zeroed, _, _ = nyquist_zeroed_wavenumbers(kx, ky)

    omega_x, omega_y = raw_derivative_pair(
        state,
        kx_zeroed,
        ky_zeroed,
    )
    omega_measure = complex_measurement(
        "omega_gradient_imaginary_ratio",
        {"x": omega_x, "y": omega_y},
    )

    baseline_projection = project_complex(
        np.asarray(diagnostics["baseline_transport"]),
        deal,
    )
    baseline_measure = complex_measurement(
        "projected_baseline_transport_imaginary_ratio",
        {"projection": baseline_projection},
    )

    pseudo_zeroed = u * omega_x.real + v * omega_y.real
    pseudo_projection = project_complex(pseudo_zeroed, deal)
    pseudo_measure = complex_measurement(
        "projected_pseudo_transport_imaginary_ratio",
        {"projection": pseudo_projection},
    )

    u_x, u_y = raw_derivative_pair(u, kx_zeroed, ky_zeroed)
    u_measure = complex_measurement(
        "u_x_gradient_imaginary_ratio",
        {"x": u_x, "y_auxiliary": u_y},
    )

    v_x, v_y = raw_derivative_pair(v, kx_zeroed, ky_zeroed)
    v_measure = complex_measurement(
        "v_y_gradient_imaginary_ratio",
        {"x_auxiliary": v_x, "y": v_y},
    )

    return {
        str(item["quantity_id"]): item
        for item in (
            omega_measure,
            baseline_measure,
            pseudo_measure,
            u_measure,
            v_measure,
        )
    }


# ============================================================================
# Preserved evidence comparison
# ============================================================================

def load_partial_references(
    repo: Path,
) -> tuple[
    list[dict[str, str]],
    dict[str, dict[str, str]],
    dict[str, object],
]:
    directory = repo / PARTIAL_STAGE_C_DIRECTORY
    metadata = read_json(directory / "run_metadata.json")
    if metadata.get("status") != "failed":
        raise RuntimeError("partial Stage C metadata does not report failed")
    progress = metadata.get("progress", {})
    if int(progress.get("last_completed_loop_index", -1)) != 3058:
        raise RuntimeError("partial Stage C last completed index changed")
    if int(progress.get("state_reference_rows", -1)) != 3059:
        raise RuntimeError("partial Stage C state-row count changed")
    if int(progress.get("shadow_rows", -1)) != 21413:
        raise RuntimeError("partial Stage C shadow-row count changed")

    state_rows = read_csv_rows(
        directory / "shadow_state_reference.csv"
    )
    shadow_rows = read_csv_rows(
        directory / "shadow_advection_per_step.csv"
    )
    if len(state_rows) != EXPECTED_PARTIAL_STATE_ROWS:
        raise RuntimeError(
            f"partial state rows={len(state_rows)}, "
            f"expected={EXPECTED_PARTIAL_STATE_ROWS}"
        )
    if len(shadow_rows) != EXPECTED_PARTIAL_SHADOW_ROWS:
        raise RuntimeError(
            f"partial shadow rows={len(shadow_rows)}, "
            f"expected={EXPECTED_PARTIAL_SHADOW_ROWS}"
        )

    last_shadow = {
        str(row["operator_id"]): row
        for row in shadow_rows
        if int(row["loop_index"]) == LAST_KNOWN_PASSING_LOOP_INDEX
    }
    if len(last_shadow) != 7:
        raise RuntimeError(
            f"last passing operator rows={len(last_shadow)}, expected=7"
        )
    return state_rows, last_shadow, metadata


def compare_partial_state_row(
    observed: Mapping[str, object],
    archived: Mapping[str, str],
) -> None:
    exact_integer_fields = (
        "loop_index",
        "completed_steps",
    )
    for name in exact_integer_fields:
        if int(observed[name]) != int(archived[name]):
            raise IntegrityFailure(
                "partial_row_integer_reproduction",
                f"{name} mismatch at loop_index={observed['loop_index']}",
            )

    pairs = (
        ("physical_time", "physical_time"),
        ("z_filtered", "z_filtered"),
        ("rk2_work", "baseline_rk2_work_replay"),
        ("stage1_ratio", "stage1_maximum_imaginary_ratio"),
        ("stage2_ratio", "stage2_maximum_imaginary_ratio"),
    )
    for observed_name, archived_name in pairs:
        first = float(observed[observed_name])
        second = float(archived[archived_name])
        if not scalar_matches(first, second):
            raise IntegrityFailure(
                "partial_state_reproduction",
                f"{observed_name} mismatch at "
                f"loop_index={observed['loop_index']}: "
                f"observed={first}, archived={second}",
            )


def last_passing_operator_works(
    solver: object,
    baseline: Mapping[str, object],
    stage1: Mapping[str, object],
    stage2: Mapping[str, object],
    *,
    jacobian_arakawa_periodic: Any,
) -> dict[str, float]:
    result: dict[str, float] = {}

    for stage_number, diagnostics, state, psi, u, v in (
        (
            1,
            stage1,
            np.asarray(baseline["current"]),
            np.asarray(baseline["psi_1"]),
            np.asarray(baseline["u_1"]),
            np.asarray(baseline["v_1"]),
        ),
        (
            2,
            stage2,
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
            diagnostics["projected_baseline_transport"],
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
        conservative = dx_uomega + dy_vomega
        skew = 0.5 * (baseline_transport + conservative)
        pseudo_raw = np.asarray(
            diagnostics["pseudo_raw_transport"],
            dtype=np.float64,
        )
        pseudo_projected = np.asarray(
            diagnostics["projected_pseudo_transport"],
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
            "BASE_FD_ADVECTIVE_V1": baseline_transport,
            "SHADOW_FD_ADVECTIVE_PROJECTED_V1": projected_baseline,
            "SHADOW_FD_CONSERVATIVE_V1": conservative,
            "SHADOW_FD_SKEW_V1": skew,
            "SHADOW_PS_ADVECTIVE_RAW_V1": pseudo_raw,
            "SHADOW_PS_ADVECTIVE_PROJECTED_V1": pseudo_projected,
            "SHADOW_ARAKAWA_V1": arakawa_transport,
        }

        for operator_id, transport in transports.items():
            work = mean_product(state, -transport)
            key = f"{stage_number}:{operator_id}"
            result[key] = work

    stage_weighted: dict[str, float] = {}
    operator_ids = sorted(
        key.split(":", 1)[1]
        for key in result
        if key.startswith("1:")
    )
    for operator_id in operator_ids:
        stage_weighted[operator_id] = 0.5 * (
            result[f"1:{operator_id}"]
            + result[f"2:{operator_id}"]
        )
    return stage_weighted


# ============================================================================
# Conclusions and reporting
# ============================================================================

def determine_conclusions(
    *,
    failing_quantity: str,
    raw_ratio: float,
    zeroed_ratio: float,
    relevant_nyquist_fraction: float,
    raw_hermitian: float,
    zeroed_hermitian: float,
    baseline_reproduction_passed: bool,
    material_real_work_change: bool,
    denominator_uses_floor: bool,
) -> tuple[str, str]:
    if denominator_uses_floor:
        primary = "LOCALIZATION INCONCLUSIVE"
    elif (
        failing_quantity
        in {
            "omega_gradient_imaginary_ratio",
            "u_x_gradient_imaginary_ratio",
            "v_y_gradient_imaginary_ratio",
            "projected_pseudo_transport_imaginary_ratio",
        }
        and relevant_nyquist_fraction > 0.0
        and raw_ratio > IMAGINARY_RATIO_LIMIT
        and zeroed_ratio <= IMAGINARY_RATIO_LIMIT
        and zeroed_hermitian < raw_hermitian
        and baseline_reproduction_passed
    ):
        primary = (
            "FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION"
        )
    elif (
        relevant_nyquist_fraction <= 0.0
        or zeroed_ratio >= raw_ratio
        or not baseline_reproduction_passed
    ):
        primary = (
            "FAILURE NOT EXPLAINED BY NYQUIST DERIVATIVE CONVENTION"
        )
    else:
        primary = "LOCALIZATION INCONCLUSIVE"

    effect = (
        "NYQUIST TREATMENT ALSO CHANGES REAL SHADOW WORK"
        if material_real_work_change
        else "NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT"
    )

    if primary == "LOCALIZATION INCONCLUSIVE":
        effect = "NYQUIST REAL-WORK EFFECT INCONCLUSIVE"

    if primary not in PRIMARY_CONCLUSIONS:
        raise RuntimeError(f"unsupported primary conclusion: {primary}")
    if effect not in EFFECT_CONCLUSIONS:
        raise RuntimeError(f"unsupported effect conclusion: {effect}")
    return primary, effect


def render_report(summary: Mapping[str, object]) -> str:
    failure = summary["failure"]
    raw_values = failure["raw_stage_values"]
    zeroed_values = failure["nyquist_zeroed_stage_values"]
    lines = [
        "# Stage C Nyquist Failure Localization Report",
        "",
        "## Decision",
        "",
        f"> **{summary['primary_conclusion']}**",
        "",
        f"> **{summary['effect_conclusion']}**",
        "",
        "This is a focused implementation-level failure localization.",
        "It is not a Stage C operator-form-specificity classification.",
        "",
        "## Failure location",
        "",
        f"- Loop index: `{failure['loop_index']}`",
        f"- Completed steps: `{failure['completed_steps']}`",
        f"- Physical time: `{failure['physical_time']}`",
        f"- Stage: `{failure['stage']}`",
        f"- Quantity: `{failure['quantity_id']}`",
        f"- Raw imaginary ratio: `{failure['raw_ratio']}`",
        f"- Nyquist-zeroed imaginary ratio: `{failure['zeroed_ratio']}`",
        f"- Historical threshold: `{IMAGINARY_RATIO_LIMIT}`",
        "",
        "## Five raw ratios at the failing stage",
        "",
        "| Quantity | Raw ratio | Pass | Nyquist-zeroed ratio |",
        "|---|---:|---|---:|",
    ]
    for quantity_id in QUANTITY_IDS:
        raw = raw_values[quantity_id]
        zeroed = zeroed_values[quantity_id]
        lines.append(
            f"| `{quantity_id}` | `{raw['imaginary_ratio']}` | "
            f"`{raw['imaginary_ratio'] <= IMAGINARY_RATIO_LIMIT}` | "
            f"`{zeroed['imaginary_ratio']}` |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            f"- Last passing loop reproduced: "
            f"`{summary['baseline_reproduction']['last_passing_loop_reproduced']}`",
            f"- Preserved partial rows compared: "
            f"`{summary['baseline_reproduction']['partial_rows_compared']}`",
            "- Preserved partial evidence modified: `False`",
            "- Full Stage C rerun performed: `False`",
            "- Full Stage C rerun authorized: `False`",
            "- Stage C specificity classification produced: `False`",
            "- Protected solver modified: `False`",
            "",
            "## Limitations",
            "",
            "- No full Stage C trajectory was completed.",
            "- No alternate trajectory was executed.",
            "- No method-superiority conclusion is authorized.",
            "- The result applies to the localized spectral-reality gate.",
            "",
        ]
    )
    return "\n".join(lines)


def write_inventory(
    directory: Path,
    inventory_path: Path,
    paths: Sequence[Path],
) -> str:
    rows = []
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
                "self-hash omitted to avoid circular self-reference"
            ),
        }
    )
    write_csv_table(inventory_path, INVENTORY_FIELDNAMES, rows)
    return sha256_file(inventory_path)


# ============================================================================
# Controlled focused execution
# ============================================================================

def execute_localization(repo: Path) -> int:
    runner = Path(__file__).resolve()
    execution_commit = verify_runner_commit_shape(repo, runner)
    source_identities = verify_source_identities(repo)
    assert_all_output_headers_unique()

    output_root = repo / OUTPUT_ROOT
    existing = (
        sorted(output_root.glob(f"{RUN_PREFIX}*"))
        if output_root.is_dir()
        else []
    )
    if existing:
        raise RuntimeError(
            "a focused localization output already exists; no rerun is "
            "allowed: "
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
            f"planned focused output is not Git-ignored: "
            f"{run_directory.relative_to(repo)}"
        )
    run_directory.mkdir(parents=True, exist_ok=False)

    metadata_path = run_directory / "run_metadata.json"
    trace_path = run_directory / "imaginary_ratio_trace.csv"
    nyquist_path = run_directory / "nyquist_spectral_content.csv"
    comparison_path = run_directory / "raw_vs_nyquist_zeroed.csv"
    summary_path = run_directory / "localization_summary.json"
    report_path = (
        run_directory
        / "STAGE_C_NYQUIST_FAILURE_LOCALIZATION_REPORT.md"
    )
    inventory_path = run_directory / "file_inventory.csv"

    trace_writer: IncrementalCsvWriter | None = None
    inventory_hash: str | None = None
    last_reconstructed_loop: int | None = None
    failed_gate: str | None = None
    failed_quantity: str | None = None
    failed_stage: int | None = None

    metadata: dict[str, object] = {
        "schema_id": "STAGE_C_NYQUIST_FAILURE_LOCALIZATION_METADATA_V1",
        "run_id": run_id,
        "status": "running",
        "primary_conclusion": None,
        "effect_conclusion": None,
        "created_utc": utc_text(created),
        "completed_utc": None,
        "repository": {
            "name": "Raj-Sanghera-Project",
            "branch": "phase4_validation",
            "design_commit": AUTHORIZED_DESIGN_COMMIT,
            "execution_commit": execution_commit,
            "runner_path": runner.name,
            "runner_sha256": sha256_file(runner),
            "source_identities": source_identities,
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
            "full_stage_c_steps": FULL_STAGE_C_STEPS,
            "last_known_passing_loop_index": LAST_KNOWN_PASSING_LOOP_INDEX,
            "expected_first_failing_loop_index": (
                EXPECTED_FIRST_FAILING_LOOP_INDEX
            ),
            "hard_stop_loop_index": HARD_STOP_LOOP_INDEX,
            "historical_imaginary_ratio_limit": IMAGINARY_RATIO_LIMIT,
            "accepted_trajectory": "baseline centered-advection only",
            "alternate_trajectories_executed": False,
            "full_stage_c_rerun": False,
        },
        "progress": {
            "last_reconstructed_loop_index": None,
            "trace_rows": 0,
        },
        "claims": {
            "stage_c_specificity_classification": False,
            "method_superiority": False,
            "formal_temporal_convergence": False,
            "formal_spatial_convergence": False,
            "physical_validation": False,
            "turbulence": False,
            "cascade": False,
            "k_minus_3": False,
            "production_readiness": False,
        },
        "output_files": {
            "run_metadata": metadata_path.name,
            "imaginary_ratio_trace": trace_path.name,
            "nyquist_spectral_content": nyquist_path.name,
            "raw_vs_nyquist_zeroed": comparison_path.name,
            "localization_summary": summary_path.name,
            "report": report_path.name,
            "file_inventory": inventory_path.name,
        },
    }
    atomic_write_json(metadata_path, metadata)

    try:
        from project.solver.advection_operators import (
            jacobian_arakawa_periodic,
        )
        from project.solver.spectral_solver import SpectralSolver

        partial_state_rows, last_partial_shadow, _ = (
            load_partial_references(repo)
        )

        solver = SpectralSolver(
            nx=N,
            ny=N,
            Re=RE,
            run_path=run_directory,
            dt=DT,
            steps=FULL_STAGE_C_STEPS,
        )
        forcing, forcing_statistics = (
            build_rms_matched_multimode_forcing(solver)
        )
        forcing_hash = str(forcing_statistics["forcing_sha256"])
        metadata["forcing"] = forcing_statistics
        atomic_write_json(metadata_path, metadata)

        baseline_omega = np.zeros((N, N), dtype=np.float64)
        trace_writer = IncrementalCsvWriter(
            trace_path,
            TRACE_FIELDNAMES,
        )

        first_failure: dict[str, object] | None = None
        failure_stage_diagnostics: dict[str, object] | None = None
        failure_baseline: dict[str, object] | None = None
        partial_rows_compared = 0
        last_passing_shadow_reproduced = False

        for loop_index in range(HARD_STOP_LOOP_INDEX + 1):
            baseline = baseline_step(
                solver,
                baseline_omega,
                forcing,
                loop_index=loop_index,
            )
            stage1 = build_stage_diagnostics(
                solver,
                np.asarray(baseline["current"]),
                np.asarray(baseline["psi_1"]),
                np.asarray(baseline["u_1"]),
                np.asarray(baseline["v_1"]),
                stage=1,
            )
            stage2 = build_stage_diagnostics(
                solver,
                np.asarray(baseline["stage"]),
                np.asarray(baseline["psi_2"]),
                np.asarray(baseline["u_2"]),
                np.asarray(baseline["v_2"]),
                stage=2,
            )

            stage1_failed = bool(stage1["failing_measurements"])
            stage2_failed = bool(stage2["failing_measurements"])
            this_is_failure = stage1_failed or stage2_failed

            for row in trace_rows_for_stage(
                stage1,
                loop_index=loop_index,
                physical_time=float(baseline["physical_time"]),
                first_failure=this_is_failure and stage1_failed,
            ):
                trace_writer.write(row)
            for row in trace_rows_for_stage(
                stage2,
                loop_index=loop_index,
                physical_time=float(baseline["physical_time"]),
                first_failure=(
                    this_is_failure and not stage1_failed and stage2_failed
                ),
            ):
                trace_writer.write(row)

            if loop_index <= LAST_KNOWN_PASSING_LOOP_INDEX:
                observed = {
                    "loop_index": loop_index,
                    "completed_steps": loop_index + 1,
                    "physical_time": float(baseline["physical_time"]),
                    "z_filtered": float(baseline["z_filtered"]),
                    "rk2_work": float(baseline["rk2_work"]),
                    "stage1_ratio": float(stage1["maximum_ratio"]),
                    "stage2_ratio": float(stage2["maximum_ratio"]),
                }
                compare_partial_state_row(
                    observed,
                    partial_state_rows[loop_index],
                )
                partial_rows_compared += 1

            if loop_index == LAST_KNOWN_PASSING_LOOP_INDEX:
                if not scalar_matches(
                    float(baseline["physical_time"]),
                    EXPECTED_LAST_PASSING_PHYSICAL_TIME,
                ):
                    raise IntegrityFailure(
                        "last_passing_time",
                        "last passing physical time does not match",
                    )
                if not scalar_matches(
                    float(baseline["z_filtered"]),
                    EXPECTED_LAST_PASSING_Z,
                ):
                    raise IntegrityFailure(
                        "last_passing_z",
                        "last passing enstrophy does not match",
                    )
                if not scalar_matches(
                    float(baseline["rk2_work"]),
                    EXPECTED_LAST_PASSING_BASELINE_WORK,
                ):
                    raise IntegrityFailure(
                        "last_passing_work",
                        "last passing baseline work does not match",
                    )
                if not scalar_matches(
                    float(stage1["maximum_ratio"]),
                    EXPECTED_LAST_PASSING_STAGE1_RATIO,
                ):
                    raise IntegrityFailure(
                        "last_passing_stage1_ratio",
                        "last passing stage-1 ratio does not match",
                    )
                if not scalar_matches(
                    float(stage2["maximum_ratio"]),
                    EXPECTED_LAST_PASSING_STAGE2_RATIO,
                ):
                    raise IntegrityFailure(
                        "last_passing_stage2_ratio",
                        "last passing stage-2 ratio does not match",
                    )

                reproduced_works = last_passing_operator_works(
                    solver,
                    baseline,
                    stage1,
                    stage2,
                    jacobian_arakawa_periodic=(
                        jacobian_arakawa_periodic
                    ),
                )
                for operator_id, archived in last_partial_shadow.items():
                    observed_work = reproduced_works[operator_id]
                    archived_work = float(archived["stage_weighted_rhs_work"])
                    if not scalar_matches(observed_work, archived_work):
                        raise IntegrityFailure(
                            "last_passing_shadow_work",
                            f"{operator_id} work mismatch: "
                            f"observed={observed_work}, "
                            f"archived={archived_work}",
                        )
                last_passing_shadow_reproduced = True

            last_reconstructed_loop = loop_index
            metadata["progress"] = {
                "last_reconstructed_loop_index": loop_index,
                "trace_rows": trace_writer.count,
            }
            if loop_index % 250 == 0:
                atomic_write_json(metadata_path, metadata)

            if this_is_failure:
                failing_stage_number = 1 if stage1_failed else 2
                failure_stage_diagnostics = (
                    stage1 if stage1_failed else stage2
                )
                candidates = list(
                    failure_stage_diagnostics["failing_measurements"]
                )
                maximum_ratio = max(
                    float(item["imaginary_ratio"])
                    for item in candidates
                )
                maximum_candidates = [
                    item
                    for item in candidates
                    if float(item["imaginary_ratio"]) == maximum_ratio
                ]
                first_item = maximum_candidates[0]
                first_failure = {
                    "loop_index": loop_index,
                    "completed_steps": loop_index + 1,
                    "physical_time": float(baseline["physical_time"]),
                    "stage": failing_stage_number,
                    "quantity_id": str(first_item["quantity_id"]),
                    "tied_quantity_ids": [
                        str(item["quantity_id"])
                        for item in maximum_candidates
                    ],
                    "raw_ratio": float(first_item["imaginary_ratio"]),
                    "real_rms": float(first_item["real_rms"]),
                    "imaginary_rms": float(first_item["imaginary_rms"]),
                    "ratio_denominator": float(
                        first_item["ratio_denominator"]
                    ),
                    "denominator_uses_floor": bool(
                        first_item["denominator_uses_floor"]
                    ),
                    "amount_above_threshold": (
                        float(first_item["imaginary_ratio"])
                        - IMAGINARY_RATIO_LIMIT
                    ),
                    "relative_amount_above_threshold": (
                        float(first_item["imaginary_ratio"])
                        / IMAGINARY_RATIO_LIMIT
                        - 1.0
                    ),
                    "current_state_sha256": sha256_array(
                        baseline["current"]
                    ),
                    "stage_state_sha256": sha256_array(
                        baseline["stage"]
                    ),
                    "forcing_sha256": forcing_hash,
                }
                failure_baseline = baseline
                break

            baseline_omega = np.array(
                baseline["filtered"],
                dtype=np.float64,
                copy=True,
                order="C",
            )

        if first_failure is None:
            raise IntegrityFailure(
                "failure_not_reproduced",
                f"no original raw-route failure through "
                f"loop_index={HARD_STOP_LOOP_INDEX}",
            )
        if int(first_failure["loop_index"]) <= LAST_KNOWN_PASSING_LOOP_INDEX:
            raise IntegrityFailure(
                "failure_too_early",
                f"first failure occurred at "
                f"loop_index={first_failure['loop_index']}",
            )
        if partial_rows_compared != EXPECTED_PARTIAL_STATE_ROWS:
            raise IntegrityFailure(
                "partial_row_compare_count",
                f"compared={partial_rows_compared}, "
                f"expected={EXPECTED_PARTIAL_STATE_ROWS}",
            )
        if not last_passing_shadow_reproduced:
            raise IntegrityFailure(
                "last_passing_shadow_reproduction",
                "last passing shadow values were not reproduced",
            )
        if failure_stage_diagnostics is None or failure_baseline is None:
            raise IntegrityFailure(
                "failure_context",
                "failure context is incomplete",
            )

        trace_writer.close()
        trace_writer = None

        stage1_failure = build_stage_diagnostics(
            solver,
            np.asarray(failure_baseline["current"]),
            np.asarray(failure_baseline["psi_1"]),
            np.asarray(failure_baseline["u_1"]),
            np.asarray(failure_baseline["v_1"]),
            stage=1,
        )
        stage2_failure = build_stage_diagnostics(
            solver,
            np.asarray(failure_baseline["stage"]),
            np.asarray(failure_baseline["psi_2"]),
            np.asarray(failure_baseline["u_2"]),
            np.asarray(failure_baseline["v_2"]),
            stage=2,
        )

        nyquist_rows, comparison_rows, comparison_context = (
            raw_vs_zeroed_at_failure(
                solver,
                failure_baseline,
                stage1_failure,
                stage2_failure,
            )
        )
        write_csv_table(
            nyquist_path,
            NYQUIST_FIELDNAMES,
            nyquist_rows,
        )
        write_csv_table(
            comparison_path,
            RAW_VS_NYQUIST_FIELDNAMES,
            comparison_rows,
        )

        failure_stage = int(first_failure["stage"])
        failure_diagnostics = (
            stage1_failure if failure_stage == 1 else stage2_failure
        )
        raw_values = {
            str(item["quantity_id"]): item
            for item in failure_diagnostics["measurements"]
        }
        zeroed_values = nyquist_zeroed_measurements(
            solver,
            failure_diagnostics,
        )
        failing_quantity_id = str(first_failure["quantity_id"])
        zeroed_ratio = float(
            zeroed_values[failing_quantity_id]["imaginary_ratio"]
        )
        first_failure["zeroed_ratio"] = zeroed_ratio
        first_failure["raw_stage_values"] = raw_values
        first_failure["nyquist_zeroed_stage_values"] = zeroed_values

        relevant_direction = str(
            raw_values[failing_quantity_id]["dominant_direction"]
        )
        relevant_field_map = {
            "omega_gradient_imaginary_ratio": "vorticity",
            "projected_baseline_transport_imaginary_ratio":
                "centered_transport",
            "projected_pseudo_transport_imaginary_ratio":
                "pseudo_raw_transport",
            "u_x_gradient_imaginary_ratio": "u_velocity",
            "v_y_gradient_imaginary_ratio": "v_velocity",
        }
        relevant_field_id = relevant_field_map[failing_quantity_id]
        relevant_row = next(
            row
            for row in nyquist_rows
            if (
                int(row["stage"]) == failure_stage
                and str(row["field_id"]) == relevant_field_id
            )
        )
        if relevant_direction.startswith("x"):
            relevant_nyquist_fraction = float(
                relevant_row["x_nyquist_fraction"]
            )
            raw_hermitian = float(
                relevant_row["raw_x_derivative_hermitian_residual"]
            )
            zeroed_hermitian = float(
                relevant_row[
                    "nyquist_zeroed_x_derivative_hermitian_residual"
                ]
            )
        else:
            relevant_nyquist_fraction = float(
                relevant_row["y_nyquist_fraction"]
            )
            raw_hermitian = float(
                relevant_row["raw_y_derivative_hermitian_residual"]
            )
            zeroed_hermitian = float(
                relevant_row[
                    "nyquist_zeroed_y_derivative_hermitian_residual"
                ]
            )

        primary, effect = determine_conclusions(
            failing_quantity=failing_quantity_id,
            raw_ratio=float(first_failure["raw_ratio"]),
            zeroed_ratio=zeroed_ratio,
            relevant_nyquist_fraction=relevant_nyquist_fraction,
            raw_hermitian=raw_hermitian,
            zeroed_hermitian=zeroed_hermitian,
            baseline_reproduction_passed=True,
            material_real_work_change=bool(
                comparison_context["material_real_work_change"]
            ),
            denominator_uses_floor=bool(
                first_failure["denominator_uses_floor"]
            ),
        )

        partial_hashes_after = verify_partial_evidence(repo)
        summary = {
            "schema_id": (
                "STAGE_C_NYQUIST_FAILURE_LOCALIZATION_SUMMARY_V1"
            ),
            "run_id": run_id,
            "primary_conclusion": primary,
            "effect_conclusion": effect,
            "created_utc": metadata["created_utc"],
            "completed_utc": utc_text(),
            "repository": metadata["repository"],
            "configuration": metadata["configuration"],
            "forcing": forcing_statistics,
            "failure": first_failure,
            "nyquist_context": {
                "relevant_field_id": relevant_field_id,
                "relevant_direction": relevant_direction,
                "relevant_nyquist_fraction": (
                    relevant_nyquist_fraction
                ),
                "raw_derivative_hermitian_residual": raw_hermitian,
                "nyquist_zeroed_derivative_hermitian_residual": (
                    zeroed_hermitian
                ),
            },
            "baseline_reproduction": {
                "last_passing_loop_reproduced": (
                    LAST_KNOWN_PASSING_LOOP_INDEX
                ),
                "partial_rows_compared": partial_rows_compared,
                "last_passing_shadow_values_reproduced": (
                    last_passing_shadow_reproduced
                ),
                "first_failure_loop_index": int(
                    first_failure["loop_index"]
                ),
            },
            "real_work_effect": {
                "material_real_work_change": bool(
                    comparison_context["material_real_work_change"]
                ),
                "material_rows": comparison_context["material_rows"],
            },
            "integrity": {
                "all_gates_passed": True,
                "failed_gate_count": 0,
                "last_reconstructed_loop_index": (
                    last_reconstructed_loop
                ),
            },
            "preservation": {
                "partial_hashes_before": {
                    name: source_identities[f"partial/{name}"]
                    for name in PARTIAL_STAGE_C_HASHES
                },
                "partial_hashes_after": partial_hashes_after,
                "preserved_partial_evidence_modified": False,
                "full_stage_c_rerun_performed": False,
                "full_stage_c_rerun_authorized": False,
                "stage_c_specificity_classification_produced": False,
            },
            "limitations": {
                "focused_failure_localization_only": True,
                "full_stage_c_completion": False,
                "method_superiority": False,
                "formal_convergence": False,
                "physical_validation": False,
                "alternate_trajectory_behavior": False,
                "turbulence": False,
                "cascade": False,
                "k_minus_3": False,
                "production_readiness": False,
            },
            "outputs": metadata["output_files"],
        }
        atomic_write_json(summary_path, summary)
        atomic_write_text(report_path, render_report(summary))

        metadata["status"] = "completed"
        metadata["primary_conclusion"] = primary
        metadata["effect_conclusion"] = effect
        metadata["completed_utc"] = summary["completed_utc"]
        metadata["failure_location"] = {
            "loop_index": first_failure["loop_index"],
            "stage": first_failure["stage"],
            "quantity_id": first_failure["quantity_id"],
        }
        metadata["progress"] = {
            "last_reconstructed_loop_index": last_reconstructed_loop,
            "trace_rows": len(read_csv_rows(trace_path)),
        }
        atomic_write_json(metadata_path, metadata)

        inventory_hash = write_inventory(
            run_directory,
            inventory_path,
            (
                metadata_path,
                trace_path,
                nyquist_path,
                comparison_path,
                summary_path,
                report_path,
            ),
        )

        observed_files = sorted(
            path.name
            for path in run_directory.iterdir()
            if path.is_file()
        )
        if observed_files != sorted(OUTPUT_FILENAMES):
            raise IntegrityFailure(
                "output_file_set",
                f"observed={observed_files}, "
                f"expected={sorted(OUTPUT_FILENAMES)}",
            )

        print()
        print("=" * 72)
        print("STAGE C NYQUIST FAILURE LOCALIZATION: COMPLETE")
        print("=" * 72)
        print(
            "Last reproduced passing loop index:",
            LAST_KNOWN_PASSING_LOOP_INDEX,
        )
        print(
            "First reproduced failing loop index:",
            first_failure["loop_index"],
        )
        print("First failing stage:", first_failure["stage"])
        print(
            "First failing quantity:",
            first_failure["quantity_id"],
        )
        print("Raw imaginary ratio:", first_failure["raw_ratio"])
        print(
            "Nyquist-zeroed imaginary ratio:",
            first_failure["zeroed_ratio"],
        )
        print("Primary conclusion:", primary)
        print("Effect conclusion:", effect)
        print("Preserved partial evidence modified: NO")
        print("Full Stage C rerun performed: NO")
        print("Full Stage C rerun authorized: NO")
        print("Stage C specificity classification produced: NO")
        print("Run directory:", run_directory)
        print("File inventory SHA256:", inventory_hash)
        return 0

    except BaseException as error:
        if isinstance(error, IntegrityFailure):
            failed_gate = error.gate
            failed_quantity = error.quantity_id
            failed_stage = error.stage
        else:
            failed_gate = type(error).__name__

        if trace_writer is not None:
            try:
                trace_writer.close()
            except Exception:
                pass

        metadata["status"] = "failed"
        metadata["primary_conclusion"] = "NUMERICAL INTEGRITY FAILURE"
        metadata["effect_conclusion"] = (
            "NYQUIST REAL-WORK EFFECT INCONCLUSIVE"
        )
        metadata["completed_utc"] = utc_text()
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = str(error)
        metadata["failed_gate"] = failed_gate
        metadata["failed_quantity"] = failed_quantity
        metadata["failed_stage"] = failed_stage
        metadata["progress"] = {
            "last_reconstructed_loop_index": last_reconstructed_loop,
            "trace_rows": (
                trace_writer.count
                if trace_writer is not None
                else metadata.get("progress", {}).get("trace_rows", 0)
            ),
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
                    trace_path,
                    nyquist_path,
                    comparison_path,
                    summary_path,
                    report_path,
                ),
            )
        except Exception:
            inventory_hash = None

        print()
        print("STAGE C NYQUIST FAILURE LOCALIZATION: FAILED")
        print("Failed gate:", failed_gate)
        if failed_quantity is not None:
            print("Failed quantity:", failed_quantity)
        if failed_stage is not None:
            print("Failed stage:", failed_stage)
        print("Partial focused evidence preserved at:", run_directory)
        print("Full Stage C rerun authorized: NO")
        if inventory_hash is not None:
            print("Partial inventory SHA256:", inventory_hash)
        raise


# ============================================================================
# Command line
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the controlled Stage C Nyquist "
            "failure-localization diagnostic."
        )
    )
    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help=(
            "inspect source without numerical execution, or run the "
            "single focused localization"
        ),
    )
    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent

    if arguments.mode == "inspect":
        return inspect_runner(repo)
    if arguments.mode == "run":
        return execute_localization(repo)

    raise RuntimeError(f"unsupported mode: {arguments.mode!r}")


if __name__ == "__main__":
    raise SystemExit(main())
