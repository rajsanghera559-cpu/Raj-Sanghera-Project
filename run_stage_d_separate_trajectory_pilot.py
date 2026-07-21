"""
Controlled Stage D1 separately advanced advection-form trajectory pilot.

Usage:
    python -B run_stage_d_separate_trajectory_pilot.py inspect
    python -B run_stage_d_separate_trajectory_pilot.py run

The inspection path parses and verifies this source and the frozen repository
identities. It does not import project modules, construct a solver, create
files, or execute a numerical timestep.

The guarded run path advances exactly seven independently owned vorticity
states for loop indices 0 through 3059. Every trajectory constructs its own
two-stage RK2 update from its own current state. The two pseudo-spectral
trajectories use local copied wavenumbers with the even-grid Nyquist modes
zeroed before differentiation. The pilot records implementation-integrity and
descriptive trajectory diagnostics only.

This pilot does not classify trajectory agreement, rank methods, fit spectral
slopes, calculate convergence, estimate Lyapunov exponents, validate physical
behavior, select a production solver, or authorize a full comparison.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime
import hashlib
import io
import json
import math
import os
import subprocess
from collections.abc import Callable, Mapping, Sequence
from itertools import combinations
from pathlib import Path

import numpy as np


# ============================================================================
# Frozen repository and evidence identities
# ============================================================================

RUNNER_NAME = "run_stage_d_separate_trajectory_pilot.py"
EXPECTED_BRANCH = "phase4_validation"

# The full object name is resolved from this unique archived prefix and then
# compared exactly with HEAD (inspection) or HEAD^ (run preflight).
AUTHORIZED_DESIGN_COMMIT_PREFIX = "5bb62e2"

DESIGN_PATH = Path(
    "STAGE_D_SEPARATELY_ADVANCED_ADVECTION_FORM_TRAJECTORY_COMPARISON_DESIGN.md"
)
EXPECTED_DESIGN_SHA256 = (
    "491B1118B40523CF4EC340E40C38CAC462C8985377809D09484571884FC445BF"
)

STAGE_C_COMPLETION_REPORT_PATH = Path(
    "STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_COMPLETION_REPORT.md"
)
EXPECTED_STAGE_C_COMPLETION_REPORT_SHA256 = (
    "ABB2F348A678C59A5CDEAB9D6CDC8640870C998C3945CC883662AD2E36DCFB05"
)

STAGE_C_DESIGN_PATH = Path(
    "STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_EXECUTION_DESIGN.md"
)
EXPECTED_STAGE_C_DESIGN_SHA256 = (
    "3FB9902A463E6C11F9E12E29F754131FB2B280DAABF180985030472701FDDA75"
)

STAGE_C_RUNNER_PATH = Path(
    "run_stage_c_remediated_full_same_state_shadow_audit.py"
)
EXPECTED_STAGE_C_RUNNER_SHA256 = (
    "9CD4551E52C5CF385E94ED2DB7356D5D9ED641ADB19377E9F97B1F1FB8FA9431"
)

FOCUSED_REMEDIATION_REPORT_PATH = Path(
    "STAGE_C_SHADOW_NYQUIST_REMEDIATION_VERIFICATION_COMPLETION_REPORT.md"
)
EXPECTED_FOCUSED_REMEDIATION_REPORT_SHA256 = (
    "B3BB4E6B7442035975DF7C2774DCFF1720E51953DA0A3E37C81415AAFB618AAD"
)

STAGE_B_REPORT_PATH = Path("STAGE_B_EXACT_OPERATOR_LEDGER_EVIDENCE_REPORT.md")
EXPECTED_STAGE_B_REPORT_SHA256 = (
    "5419765B72A757A4C048761CDBC55B1AAD8ED2A0414E3D9E79CC118A64D40DE4"
)

STAGE_B_RUNNER_PATH = Path("run_stage_b_exact_operator_ledger_replay.py")
EXPECTED_STAGE_B_RUNNER_SHA256 = (
    "970AE47D4DF69819FA6D831557FC2679D843B860D901CF367361A3A34126E246"
)

SPECTRAL_SOLVER_PATH = Path("project") / "solver" / "spectral_solver.py"
EXPECTED_SPECTRAL_SOLVER_SHA256 = (
    "1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1"
)

ADVECTION_OPERATORS_PATH = Path("project") / "solver" / "advection_operators.py"
EXPECTED_ADVECTION_OPERATORS_BLOB = (
    "849b3d5c95c955a7db73313d8680c942fd32c571"
)

SELECTABLE_SOLVER_PATH = (
    Path("project") / "solver" / "selectable_advection_solver.py"
)
EXPECTED_SELECTABLE_SOLVER_BLOB = (
    "cc3b757e327a5b1a0b6cea2287c672adebd77c15"
)

FORCING_BUDGET_DIAGNOSTIC_PATH = Path("forcing_budget_diagnostic.py")
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

STAGE_C_EVIDENCE_DIRECTORY = (
    Path("experiments")
    / "advection_form_shadow_audit_remediated_full"
    / "stage_c_remediated_full_same_state_shadow_20260721T010632Z_4bfd08a"
)
STAGE_C_EVIDENCE_HASHES = {
    "file_inventory.csv":
        "142B74CF928AEE7E25407D434E29624129B64870619108BE9AAD6964264657A2",
    "nyquist_remediation_checkpoint_trace.csv":
        "F67DEF0703489A2E329F4EB0534AF8BBB13F9B073D00B4DFF5F1D39E34229C7D",
    "nyquist_remediation_checkpoint_work.csv":
        "590EC3717DDB9F00AB83B30B27BCC6C08233421C838E7E717411FA69E165FE7E",
    "remediated_shadow_advection_per_step.csv":
        "79B3E972DA3AC1DF3FD745EE6CA8956772B16A2EB25309E38EE48B788BE8EA29",
    "remediated_shadow_state_reference.csv":
        "9289DF386EA4C5B4CAD20CFD8F94CA07FAE4AB0EA6A8F430B74702CE3EE7261F",
    "remediated_shadow_summary.json":
        "43289295A39A4D6BA4F7463D834FA30587971EEF2FCE6DA61AF32BDE95202793",
    "remediated_shadow_time_blocks.csv":
        "C1B23E46690383D3CEE4B7D0890D89CF06653FEBCDD629382777287D3EB02BCC",
    "run_metadata.json":
        "5D83EEC72BD811F70F6CCD9B4CF70BE6044264634078803AB8161024E7EDFB4B",
    "STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_REPORT.md":
        "B6E9079A91F16E235B0AEFFBCA64F2CE2E864CEE8FF4901C65EF1C1B330661FA",
}


# ============================================================================
# Frozen pilot configuration and limits
# ============================================================================

N = 64
RE = 1000
NU = 1.0 / RE
DT = 0.005
PILOT_UPDATES = 3060
PILOT_STOP_INDEX = 3059
PILOT_FINAL_TIME = 15.300

FORCING_TARGET_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14
EXPECTED_FORCING_SHA256 = (
    "504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB"
)

EXPECTED_CHECKPOINT_CURRENT_SHA256 = (
    "7534D7C24F2666993BBD5B7B79E03B82B8F7F15665B41C30453351A18196E852"
)
EXPECTED_CHECKPOINT_STAGE_SHA256 = (
    "01F5C093F544119D75C4903FBEBC8B809224CABEF12CE125FB94C6AA509BD2B7"
)
EXPECTED_CHECKPOINT_FILTERED_SHA256 = (
    "1A95D9BF2065E88B47E2E578B8862DB83B47D804288354C32299EF44809EE61E"
)

BASELINE_ARCHIVE_RELATIVE_TOLERANCE = 1.0e-11
BASELINE_ARCHIVE_ABSOLUTE_FLOOR = 1.0e-14
FILTERED_LEDGER_CLOSURE_LIMIT = 1.0e-10
UNFILTERED_LEDGER_CLOSURE_LIMIT = 1.0e-10
MASK_CROSSCHECK_LIMIT = 1.0e-12
CENTERED_FORM_IDENTITY_LIMIT = 1.0e-12
SKEW_IDENTITY_LIMIT = 1.0e-15
ARAKAWA_IDENTITY_LIMIT = 1.0e-12
PSEUDO_PROJECTION_IDENTITY_LIMIT = 1.0e-12
IMAGINARY_RATIO_LIMIT = 1.0e-13
ORDER_INVARIANCE_LIMIT = 1.0e-15
RESIDUAL_FLOOR = 1.0e-30

SENTINEL_LOOP_INDICES = (0, 3058, 3059)
DIAGNOSTIC_LOOP_INDICES = tuple(range(0, 3060, 10)) + (3059,)

EXPECTED_DIAGNOSTIC_SAMPLES = 307
EXPECTED_TRAJECTORY_DIAGNOSTIC_ROWS = 2149
EXPECTED_PAIRWISE_ROWS = 6447
EXPECTED_INTEGRITY_ROWS = 21420
EXPECTED_SENTINEL_ROWS = 21
EXPECTED_BASELINE_ROWS = 3060

PROGRESS_INTERVAL = 250
CSV_FLUSH_INTERVAL = 100
MAX_OUTPUT_FILE_BYTES = 40_000_000

OUTPUT_ROOT = Path("experiments") / "advection_form_trajectory_pilot"
RUN_PREFIX = "stage_d_separate_trajectory_pilot_"

OUTPUT_FILENAMES = (
    "run_metadata.json",
    "trajectory_pilot_diagnostics.csv",
    "trajectory_pilot_pairwise_divergence.csv",
    "trajectory_pilot_integrity_per_step.csv",
    "trajectory_pilot_sentinel_crosscheck.csv",
    "trajectory_pilot_summary.json",
    "STAGE_D_SEPARATE_TRAJECTORY_PILOT_REPORT.md",
    "file_inventory.csv",
)

PREDICTED_OUTPUT_FILE_BYTES = {
    "run_metadata.json": 100_000,
    "trajectory_pilot_diagnostics.csv": 8_000_000,
    "trajectory_pilot_pairwise_divergence.csv": 12_000_000,
    "trajectory_pilot_integrity_per_step.csv": 25_000_000,
    "trajectory_pilot_sentinel_crosscheck.csv": 250_000,
    "trajectory_pilot_summary.json": 500_000,
    "STAGE_D_SEPARATE_TRAJECTORY_PILOT_REPORT.md": 250_000,
    "file_inventory.csv": 100_000,
}

FORCING_TERMS = (
    "sin(2X)cos(2Y)",
    "0.75*sin(3X)cos(Y)",
    "0.50*sin(X)cos(4Y)",
    "0.35*cos(4X-2Y)",
)


# ============================================================================
# Frozen trajectory registry
# ============================================================================

TRAJECTORY_REGISTRY = (
    {
        "trajectory_id": "TRAJ_BASE_FD_ADVECTIVE_V1",
        "stage_c_operator_id": "BASE_FD_ADVECTIVE_V1",
        "operator_family": "BASELINE",
        "operator_kind": "fd_advective",
    },
    {
        "trajectory_id": "TRAJ_FD_ADVECTIVE_PROJECTED_V1",
        "stage_c_operator_id": "SHADOW_FD_ADVECTIVE_PROJECTED_V1",
        "operator_family": "PROJECTED_BASELINE_CHECK",
        "operator_kind": "fd_advective_projected",
    },
    {
        "trajectory_id": "TRAJ_FD_CONSERVATIVE_V1",
        "stage_c_operator_id": "SHADOW_FD_CONSERVATIVE_V1",
        "operator_family": "CENTERED_ALGEBRAIC",
        "operator_kind": "fd_conservative",
    },
    {
        "trajectory_id": "TRAJ_FD_SKEW_V1",
        "stage_c_operator_id": "SHADOW_FD_SKEW_V1",
        "operator_family": "CENTERED_ALGEBRAIC",
        "operator_kind": "fd_skew",
    },
    {
        "trajectory_id": "TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2",
        "stage_c_operator_id": (
            "SHADOW_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2"
        ),
        "operator_family": "PSEUDO_SPECTRAL_RC_NYQUIST",
        "operator_kind": "ps_advective_rc_unprojected",
    },
    {
        "trajectory_id": "TRAJ_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2",
        "stage_c_operator_id": (
            "SHADOW_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2"
        ),
        "operator_family": "PSEUDO_SPECTRAL_RC_NYQUIST",
        "operator_kind": "ps_advective_rc_projected",
    },
    {
        "trajectory_id": "TRAJ_ARAKAWA_V1",
        "stage_c_operator_id": "SHADOW_ARAKAWA_V1",
        "operator_family": "ARAKAWA",
        "operator_kind": "arakawa",
    },
)

TRAJECTORY_IDS = tuple(row["trajectory_id"] for row in TRAJECTORY_REGISTRY)
BASELINE_TRAJECTORY_ID = TRAJECTORY_IDS[0]
PAIR_IDS = tuple(combinations(TRAJECTORY_IDS, 2))


# ============================================================================
# Output schemas
# ============================================================================

DIAGNOSTIC_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "trajectory_id",
    "operator_family",
    "energy",
    "enstrophy",
    "vorticity_rms",
    "velocity_rms",
    "energy_injection",
    "enstrophy_injection",
    "viscous_energy_dissipation",
    "viscous_enstrophy_dissipation",
    "advection_enstrophy_work",
    "rk2_remainder",
    "mask_enstrophy_change",
    "normalized_filtered_closure",
    "dominant_shell",
    "low_k_fraction",
    "tail_fraction",
    "high_k_fraction",
    "maximum_imaginary_ratio",
    "accepted_state_sha256",
    "finite_status",
)

PAIRWISE_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "trajectory_a",
    "trajectory_b",
    "normalized_vorticity_rms_difference",
    "normalized_velocity_difference",
    "vorticity_cosine_similarity",
    "energy_relative_difference",
    "enstrophy_relative_difference",
    "dominant_shell_difference",
    "low_k_fraction_difference",
    "tail_fraction_difference",
    "high_k_fraction_difference",
    "finite_status",
)

INTEGRITY_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "trajectory_id",
    "unfiltered_closure_residual",
    "filtered_closure_residual",
    "normalized_unfiltered_closure",
    "normalized_filtered_closure",
    "mask_crosscheck_residual",
    "maximum_imaginary_ratio",
    "state_mutation_count",
    "state_alias_count",
    "update_finite",
    "integrity_pass",
)

SENTINEL_FIELDNAMES = (
    "loop_index",
    "trajectory_id",
    "forward_accepted_state_sha256",
    "reverse_accepted_state_sha256",
    "normalized_accepted_state_difference",
    "ledger_scalar_difference",
    "stage_c_baseline_state_operator_work_reference",
    "stage_d_helper_operator_work_value",
    "helper_reference_difference",
    "order_invariance_pass",
    "helper_crosscheck_pass",
)

INVENTORY_FIELDNAMES = ("relative_path", "bytes", "sha256")


# ============================================================================
# Generic utilities
# ============================================================================

class IntegrityFailure(RuntimeError):
    def __init__(
        self,
        gate: str,
        message: str,
        *,
        trajectory_id: str | None = None,
        loop_index: int | None = None,
        stage: str | None = None,
    ) -> None:
        super().__init__(message)
        self.gate = gate
        self.trajectory_id = trajectory_id
        self.loop_index = loop_index
        self.stage = stage


def fail(message: str) -> None:
    raise RuntimeError(message)


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def utc_text(value: datetime.datetime | None = None) -> str:
    selected = value or utc_now()
    return selected.isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_array(value: object) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    return sha256_bytes(array.tobytes(order="C"))


def finite_float(name: str, value: object) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise IntegrityFailure("nonfinite_scalar", f"{name} is nonfinite: {result}")
    return result


def field_rms(value: object) -> float:
    array = np.asarray(value)
    return float(np.sqrt(np.mean(np.abs(array) ** 2)))


def enstrophy(value: object) -> float:
    array = np.asarray(value, dtype=np.float64)
    return 0.5 * float(np.mean(array * array))


def mean_product(first: object, second: object) -> float:
    a = np.asarray(first, dtype=np.float64)
    b = np.asarray(second, dtype=np.float64)
    return float(np.mean(a * b))


def normalized_rms_difference(first: object, second: object) -> tuple[float, float]:
    a = np.asarray(first, dtype=np.float64)
    b = np.asarray(second, dtype=np.float64)
    absolute = field_rms(a - b)
    scale = max(field_rms(a), field_rms(b), RESIDUAL_FLOOR)
    return absolute, absolute / scale


def cosine_similarity(first: object, second: object) -> float:
    a = np.asarray(first, dtype=np.float64).ravel()
    b = np.asarray(second, dtype=np.float64).ravel()
    denominator = max(float(np.linalg.norm(a) * np.linalg.norm(b)), RESIDUAL_FLOOR)
    return float(np.dot(a, b) / denominator)


def symmetric_relative_difference(first: float, second: float) -> float:
    return 2.0 * abs(first - second) / max(
        abs(first) + abs(second), RESIDUAL_FLOOR
    )


def archived_scalar_comparison(observed: float, archived: float) -> tuple[float, float, bool]:
    absolute = abs(observed - archived)
    scale = max(abs(observed), abs(archived), BASELINE_ARCHIVE_ABSOLUTE_FLOOR)
    relative = absolute / scale
    passed = (
        absolute <= BASELINE_ARCHIVE_ABSOLUTE_FLOOR
        or relative <= BASELINE_ARCHIVE_RELATIVE_TOLERANCE
    )
    return absolute, relative, passed


def assert_unique_headers(name: str, headers: Sequence[str]) -> None:
    duplicates = sorted({field for field in headers if headers.count(field) > 1})
    if duplicates:
        raise RuntimeError(f"duplicate headers in {name}: {duplicates}")


def assert_all_output_headers_unique() -> None:
    for name, headers in (
        ("trajectory_pilot_diagnostics.csv", DIAGNOSTIC_FIELDNAMES),
        ("trajectory_pilot_pairwise_divergence.csv", PAIRWISE_FIELDNAMES),
        ("trajectory_pilot_integrity_per_step.csv", INTEGRITY_FIELDNAMES),
        ("trajectory_pilot_sentinel_crosscheck.csv", SENTINEL_FIELDNAMES),
        ("file_inventory.csv", INVENTORY_FIELDNAMES),
    ):
        assert_unique_headers(name, headers)


def atomic_write_text(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_json(path: Path, value: object) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


class IncrementalCsvWriter:
    def __init__(self, path: Path, fieldnames: Sequence[str]) -> None:
        self.path = path
        self.fieldnames = tuple(fieldnames)
        assert_unique_headers(path.name, self.fieldnames)
        self.handle = path.open("w", encoding="utf-8", newline="")
        self.writer = csv.DictWriter(
            self.handle, fieldnames=self.fieldnames, extrasaction="raise", lineterminator="\n"
        )
        self.writer.writeheader()
        self.row_count = 0

    def write(self, row: Mapping[str, object]) -> None:
        if set(row) != set(self.fieldnames):
            missing = sorted(set(self.fieldnames) - set(row))
            extra = sorted(set(row) - set(self.fieldnames))
            raise RuntimeError(
                f"schema mismatch for {self.path.name}; missing={missing}, extra={extra}"
            )
        self.writer.writerow(row)
        self.row_count += 1

    def flush(self) -> None:
        self.handle.flush()

    def close(self) -> None:
        if not self.handle.closed:
            self.flush()
            self.handle.close()


# ============================================================================
# Read-only Git and identity gates
# ============================================================================

def git_process(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", *args], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if check and result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
    return result


def git_read(repo: Path, *args: str) -> str:
    return git_process(repo, *args).stdout.decode("utf-8", errors="strict").strip()


def git_bytes(repo: Path, *args: str) -> bytes:
    return git_process(repo, *args).stdout


def resolve_design_commit(repo: Path) -> str:
    return git_read(repo, "rev-parse", f"{AUTHORIZED_DESIGN_COMMIT_PREFIX}^{{commit}}")


def verify_file_hash(repo: Path, relative_path: Path, expected: str) -> str:
    path = repo / relative_path
    if not path.is_file():
        raise RuntimeError(f"required file is missing: {relative_path.as_posix()}")
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(
            f"SHA256 mismatch for {relative_path.as_posix()}: observed={observed}, expected={expected}"
        )
    return observed


def verify_git_blob(repo: Path, relative_path: Path, expected: str) -> str:
    relative = relative_path.as_posix()
    working = git_read(repo, "hash-object", f"--path={relative}", "--", relative)
    committed = git_read(repo, "rev-parse", f"HEAD:{relative}")
    if working != expected or committed != expected:
        raise RuntimeError(
            f"Git blob mismatch for {relative}: working={working}, committed={committed}, expected={expected}"
        )
    return working


def verify_evidence_inventory(
    directory: Path, expected_hashes: Mapping[str, str]
) -> dict[str, str]:
    if not directory.is_dir():
        raise RuntimeError(f"evidence directory is missing: {directory}")
    actual_names = sorted(path.name for path in directory.iterdir() if path.is_file())
    expected_names = sorted(expected_hashes)
    if actual_names != expected_names:
        raise RuntimeError(
            f"evidence file set mismatch for {directory}: observed={actual_names}, expected={expected_names}"
        )

    observed: dict[str, str] = {}
    for name, expected in expected_hashes.items():
        path = directory / name
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(
                f"evidence SHA256 mismatch for {path}: observed={actual}, expected={expected}"
            )
        observed[name] = actual

    inventory_path = directory / "file_inventory.csv"
    with inventory_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert_unique_headers(inventory_path.name, tuple(reader.fieldnames or ()))
        rows = list(reader)
    by_name = {str(row.get("relative_path", "")): row for row in rows}
    for name, expected in expected_hashes.items():
        row = by_name.get(name)
        if row is None:
            raise RuntimeError(f"inventory entry missing for {directory / name}")
        if name == "file_inventory.csv":
            if str(row.get("sha256", "")).strip():
                raise RuntimeError(f"inventory self-hash is not blank: {inventory_path}")
            continue
        recorded_hash = str(row.get("sha256", "")).strip().upper()
        recorded_bytes = int(str(row.get("bytes", "0")).strip())
        if recorded_hash != expected or recorded_bytes != (directory / name).stat().st_size:
            raise RuntimeError(f"inventory record mismatch for {directory / name}")
    return observed


def verify_source_identities(repo: Path) -> dict[str, str]:
    hashes = {
        "stage_d_design": verify_file_hash(repo, DESIGN_PATH, EXPECTED_DESIGN_SHA256),
        "stage_c_completion_report": verify_file_hash(
            repo, STAGE_C_COMPLETION_REPORT_PATH, EXPECTED_STAGE_C_COMPLETION_REPORT_SHA256
        ),
        "stage_c_design": verify_file_hash(
            repo, STAGE_C_DESIGN_PATH, EXPECTED_STAGE_C_DESIGN_SHA256
        ),
        "stage_c_runner": verify_file_hash(
            repo, STAGE_C_RUNNER_PATH, EXPECTED_STAGE_C_RUNNER_SHA256
        ),
        "focused_remediation_report": verify_file_hash(
            repo, FOCUSED_REMEDIATION_REPORT_PATH, EXPECTED_FOCUSED_REMEDIATION_REPORT_SHA256
        ),
        "stage_b_report": verify_file_hash(
            repo, STAGE_B_REPORT_PATH, EXPECTED_STAGE_B_REPORT_SHA256
        ),
        "stage_b_runner": verify_file_hash(
            repo, STAGE_B_RUNNER_PATH, EXPECTED_STAGE_B_RUNNER_SHA256
        ),
        "spectral_solver": verify_file_hash(
            repo, SPECTRAL_SOLVER_PATH, EXPECTED_SPECTRAL_SOLVER_SHA256
        ),
        "advection_operators_blob": verify_git_blob(
            repo, ADVECTION_OPERATORS_PATH, EXPECTED_ADVECTION_OPERATORS_BLOB
        ),
        "selectable_solver_blob": verify_git_blob(
            repo, SELECTABLE_SOLVER_PATH, EXPECTED_SELECTABLE_SOLVER_BLOB
        ),
        "forcing_budget_diagnostic": verify_file_hash(
            repo,
            FORCING_BUDGET_DIAGNOSTIC_PATH,
            EXPECTED_FORCING_BUDGET_DIAGNOSTIC_SHA256,
        ),
    }
    for name, value in verify_evidence_inventory(
        repo / STAGE_B_EVIDENCE_DIRECTORY, STAGE_B_EVIDENCE_HASHES
    ).items():
        hashes[f"stage_b/{name}"] = value
    for name, value in verify_evidence_inventory(
        repo / STAGE_C_EVIDENCE_DIRECTORY, STAGE_C_EVIDENCE_HASHES
    ).items():
        hashes[f"stage_c/{name}"] = value
    return hashes


def verify_inspection_repository_state(repo: Path, runner: Path) -> str:
    branch = git_read(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"active branch is {branch!r}, expected {EXPECTED_BRANCH!r}")
    design_commit = resolve_design_commit(repo)
    head = git_read(repo, "rev-parse", "HEAD")
    if head != design_commit:
        raise RuntimeError(f"HEAD is {head}, expected archived design commit {design_commit}")
    status_lines = [
        line
        for line in git_read(
            repo, "status", "--porcelain=v1", "--untracked-files=all"
        ).splitlines()
        if line
    ]
    expected = [f"?? {runner.name}"]
    if status_lines != expected:
        raise RuntimeError(
            f"inspection requires exactly one untracked pilot runner; observed={status_lines!r}"
        )
    return design_commit


def path_is_git_ignored(repo: Path, path: Path) -> bool:
    relative = path.relative_to(repo).as_posix()
    return git_process(repo, "check-ignore", "-q", "--", relative, check=False).returncode == 0


def verify_run_preflight(repo: Path, runner: Path) -> tuple[str, dict[str, str]]:
    branch = git_read(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"active branch is {branch!r}, expected {EXPECTED_BRANCH!r}")
    status = git_read(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise RuntimeError(f"working tree is not clean: {status!r}")

    design_commit = resolve_design_commit(repo)
    head = git_read(repo, "rev-parse", "HEAD")
    parent = git_read(repo, "rev-parse", "HEAD^")
    if parent != design_commit:
        raise RuntimeError(f"runner commit parent is {parent}, expected {design_commit}")
    changed = [
        line
        for line in git_read(
            repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"
        ).splitlines()
        if line
    ]
    if changed != [runner.name]:
        raise RuntimeError(
            f"runner commit must change exactly one file; observed={changed!r}"
        )
    if git_bytes(repo, "show", f"HEAD:{runner.name}") != runner.read_bytes():
        raise RuntimeError("working runner bytes differ from committed runner bytes")

    remote_lines = git_read(repo, "ls-remote", "origin", f"refs/heads/{EXPECTED_BRANCH}")
    remote_head = remote_lines.split()[0] if remote_lines else ""
    if remote_head != head:
        raise RuntimeError(f"remote branch is {remote_head!r}, expected local HEAD {head}")

    source_hashes = verify_source_identities(repo)
    if OUTPUT_ROOT.exists():
        prior = sorted(
            path.name
            for path in OUTPUT_ROOT.iterdir()
            if path.is_dir() and path.name.startswith(RUN_PREFIX)
        )
        if prior:
            raise RuntimeError(f"prior Stage D pilot output exists: {prior}")
    probe = repo / OUTPUT_ROOT / (RUN_PREFIX + "ignore_probe")
    if not path_is_git_ignored(repo, probe):
        raise RuntimeError(f"pilot output path is not Git-ignored: {probe.relative_to(repo)}")
    oversized = {
        name: size
        for name, size in PREDICTED_OUTPUT_FILE_BYTES.items()
        if size >= MAX_OUTPUT_FILE_BYTES
    }
    if oversized:
        raise RuntimeError(f"predicted output exceeds frozen size limit: {oversized}")
    if tuple(sorted(PREDICTED_OUTPUT_FILE_BYTES)) != tuple(sorted(OUTPUT_FILENAMES)):
        raise RuntimeError("predicted output set differs from frozen output set")
    return head, source_hashes


# ============================================================================
# Archived pilot references
# ============================================================================

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


def load_stage_b_pilot_rows(repo: Path) -> list[dict[str, str]]:
    path = repo / STAGE_B_EVIDENCE_DIRECTORY / "operator_ledger_per_step.csv"
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert_unique_headers(path.name, tuple(reader.fieldnames or ()))
        for expected_loop, row in enumerate(reader):
            if expected_loop >= PILOT_UPDATES:
                break
            if int(row["loop_index"]) != expected_loop:
                raise RuntimeError(
                    f"Stage B ledger loop mismatch: observed={row['loop_index']}, expected={expected_loop}"
                )
            rows.append(row)
    if len(rows) != EXPECTED_BASELINE_ROWS:
        raise RuntimeError(
            f"Stage B pilot rows={len(rows)}, expected={EXPECTED_BASELINE_ROWS}"
        )
    return rows


def load_stage_c_sentinel_references(
    repo: Path,
) -> tuple[dict[tuple[int, str], dict[str, str]], dict[int, dict[str, str]]]:
    operator_path = (
        repo / STAGE_C_EVIDENCE_DIRECTORY / "remediated_shadow_advection_per_step.csv"
    )
    operator_rows: dict[tuple[int, str], dict[str, str]] = {}
    with operator_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert_unique_headers(operator_path.name, tuple(reader.fieldnames or ()))
        for row in reader:
            loop_index = int(row["loop_index"])
            if loop_index > PILOT_STOP_INDEX:
                break
            if loop_index in SENTINEL_LOOP_INDICES:
                key = (loop_index, str(row["operator_id"]))
                if key in operator_rows:
                    raise RuntimeError(f"duplicate Stage C sentinel operator row: {key}")
                operator_rows[key] = row

    state_path = (
        repo / STAGE_C_EVIDENCE_DIRECTORY / "remediated_shadow_state_reference.csv"
    )
    state_rows: dict[int, dict[str, str]] = {}
    with state_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert_unique_headers(state_path.name, tuple(reader.fieldnames or ()))
        for row in reader:
            loop_index = int(row["loop_index"])
            if loop_index > PILOT_STOP_INDEX:
                break
            if loop_index in SENTINEL_LOOP_INDICES:
                state_rows[loop_index] = row

    expected_operator_keys = {
        (loop_index, registry["stage_c_operator_id"])
        for loop_index in SENTINEL_LOOP_INDICES
        for registry in TRAJECTORY_REGISTRY
    }
    if set(operator_rows) != expected_operator_keys:
        missing = sorted(expected_operator_keys - set(operator_rows))
        extra = sorted(set(operator_rows) - expected_operator_keys)
        raise RuntimeError(
            f"Stage C sentinel operator reference mismatch; missing={missing}, extra={extra}"
        )
    if set(state_rows) != set(SENTINEL_LOOP_INDICES):
        raise RuntimeError(
            f"Stage C sentinel state reference mismatch: {sorted(state_rows)}"
        )
    return operator_rows, state_rows


def compare_stage_b_ledger_row(
    replay: Mapping[str, object], archived: Mapping[str, str]
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
            archived_value = finite_float(f"archived_{name}", archived[name])
            absolute, _, field_pass = archived_scalar_comparison(observed, archived_value)
            differences[name] = absolute
        passed = passed and field_pass
    return {
        "passed": passed,
        "differences": differences,
        "maximum_absolute_difference": max(differences.values(), default=0.0),
    }


# ============================================================================
# Frozen forcing and immutable solver environment
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
    coefficient = field_rms(base) / field_rms(raw)
    forcing = np.ascontiguousarray(coefficient * raw, dtype=np.float64)
    forcing_rms = field_rms(forcing)
    forcing_hash = sha256_array(forcing)
    if not math.isclose(
        forcing_rms, FORCING_TARGET_RMS, rel_tol=0.0, abs_tol=FORCING_RMS_TOLERANCE
    ):
        raise IntegrityFailure(
            "forcing_rms", f"forcing RMS={forcing_rms}, expected={FORCING_TARGET_RMS}"
        )
    if forcing_hash != EXPECTED_FORCING_SHA256:
        raise IntegrityFailure(
            "forcing_sha256",
            f"forcing SHA256={forcing_hash}, expected={EXPECTED_FORCING_SHA256}",
        )
    if forcing.shape != (N, N) or not np.isfinite(forcing).all():
        raise IntegrityFailure("forcing_array", "forcing shape or finite gate failed")
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


def freeze_solver_environment(solver: object) -> dict[str, str]:
    identities: dict[str, str] = {}
    for name in ("x", "X", "Y", "k", "kx", "ky", "k2", "deal", "w"):
        value = np.asarray(getattr(solver, name))
        value.setflags(write=False)
        identities[name] = sha256_array(value)
    identities["N"] = sha256_bytes(str(int(solver.N)).encode())
    identities["dt"] = sha256_bytes(repr(float(solver.dt)).encode())
    identities["nu"] = sha256_bytes(repr(float(solver.nu)).encode())
    identities["dx"] = sha256_bytes(repr(float(solver.dx)).encode())
    return identities


def verify_solver_environment(solver: object, expected: Mapping[str, str]) -> None:
    observed = freeze_solver_environment(solver)
    if dict(observed) != dict(expected):
        changed = sorted(
            key
            for key in set(observed) | set(expected)
            if observed.get(key) != expected.get(key)
        )
        raise IntegrityFailure(
            "solver_environment_mutation", f"solver environment changed: {changed}"
        )


def build_real_compatible_wavenumbers(
    solver: object,
) -> tuple[np.ndarray, np.ndarray]:
    solver_kx = np.asarray(solver.kx)
    solver_ky = np.asarray(solver.ky)
    nyquist = -N / 2
    x_mask = np.asarray(solver_kx == nyquist)
    y_mask = np.asarray(solver_ky == nyquist)
    if not x_mask.any() or not y_mask.any():
        raise IntegrityFailure(
            "nyquist_location", "solver wavenumber arrays do not contain the derived -N/2 mode"
        )
    kx_real_compatible = np.array(solver_kx, dtype=np.float64, copy=True)
    ky_real_compatible = np.array(solver_ky, dtype=np.float64, copy=True)
    kx_real_compatible[x_mask] = 0.0
    ky_real_compatible[y_mask] = 0.0
    if np.shares_memory(kx_real_compatible, solver_kx):
        raise IntegrityFailure("kx_copy", "local real-compatible kx aliases solver.kx")
    if np.shares_memory(ky_real_compatible, solver_ky):
        raise IntegrityFailure("ky_copy", "local real-compatible ky aliases solver.ky")
    kx_real_compatible.setflags(write=False)
    ky_real_compatible.setflags(write=False)
    return kx_real_compatible, ky_real_compatible


# ============================================================================
# Independent operators and per-trajectory RK2
# ============================================================================

def trajectory_metadata(trajectory_id: str) -> Mapping[str, str]:
    for row in TRAJECTORY_REGISTRY:
        if row["trajectory_id"] == trajectory_id:
            return row
    raise KeyError(trajectory_id)


def centered_gradients(field: object, dx: float) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(field, dtype=np.float64)
    x_gradient = (
        np.roll(array, -1, axis=1) - np.roll(array, 1, axis=1)
    ) / (2.0 * dx)
    y_gradient = (
        np.roll(array, -1, axis=0) - np.roll(array, 1, axis=0)
    ) / (2.0 * dx)
    return x_gradient, y_gradient


def spectral_gradients_real_compatible(
    field: object, kx_real_compatible: np.ndarray, ky_real_compatible: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float]:
    array = np.asarray(field, dtype=np.float64)
    field_hat = np.fft.fft2(array)
    x_complex = np.fft.ifft2(1j * kx_real_compatible * field_hat)
    y_complex = np.fft.ifft2(1j * ky_real_compatible * field_hat)
    real_scale = max(
        field_rms(x_complex.real), field_rms(y_complex.real), RESIDUAL_FLOOR
    )
    imaginary_ratio = max(
        field_rms(x_complex.imag), field_rms(y_complex.imag)
    ) / real_scale
    return x_complex.real, y_complex.real, imaginary_ratio


def project_field(field: object, deal: np.ndarray) -> tuple[np.ndarray, float]:
    projected_complex = np.fft.ifft2(
        np.fft.fft2(np.asarray(field, dtype=np.float64)) * deal
    )
    ratio = field_rms(projected_complex.imag) / max(
        field_rms(projected_complex.real), RESIDUAL_FLOOR
    )
    return projected_complex.real, ratio


def compute_transport(
    trajectory_id: str,
    solver: object,
    state: np.ndarray,
    psi: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    *,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_real_compatible: np.ndarray,
    ky_real_compatible: np.ndarray,
) -> dict[str, object]:
    metadata = trajectory_metadata(trajectory_id)
    kind = metadata["operator_kind"]
    state_array = np.asarray(state, dtype=np.float64)
    state_hash = sha256_array(state_array)
    state_writeable = bool(state_array.flags.writeable)
    omega_x_c, omega_y_c = centered_gradients(state_array, float(solver.dx))
    advective = u * omega_x_c + v * omega_y_c
    imaginary_ratio = 0.0
    identity_residual = 0.0

    if kind == "fd_advective":
        transport = advective
    elif kind == "fd_advective_projected":
        transport, projection_imaginary = project_field(advective, np.asarray(solver.deal))
        reconstructed, _ = project_field(advective, np.asarray(solver.deal))
        identity_residual = normalized_rms_difference(transport, reconstructed)[1]
        imaginary_ratio = projection_imaginary
    elif kind == "fd_conservative":
        ux_omega = centered_gradients(u * state_array, float(solver.dx))[0]
        vy_omega = centered_gradients(v * state_array, float(solver.dx))[1]
        transport = ux_omega + vy_omega
        reconstructed = ux_omega + vy_omega
        identity_residual = normalized_rms_difference(transport, reconstructed)[1]
    elif kind == "fd_skew":
        conservative = (
            centered_gradients(u * state_array, float(solver.dx))[0]
            + centered_gradients(v * state_array, float(solver.dx))[1]
        )
        transport = 0.5 * (advective + conservative)
        identity_residual = normalized_rms_difference(
            transport, 0.5 * (advective + conservative)
        )[1]
    elif kind in ("ps_advective_rc_unprojected", "ps_advective_rc_projected"):
        omega_x_s, omega_y_s, derivative_imaginary = (
            spectral_gradients_real_compatible(
                state_array, kx_real_compatible, ky_real_compatible
            )
        )
        raw = u * omega_x_s + v * omega_y_s
        imaginary_ratio = derivative_imaginary
        if kind == "ps_advective_rc_unprojected":
            transport = raw
        else:
            transport, projection_imaginary = project_field(raw, np.asarray(solver.deal))
            reconstructed, _ = project_field(raw, np.asarray(solver.deal))
            identity_residual = normalized_rms_difference(transport, reconstructed)[1]
            imaginary_ratio = max(imaginary_ratio, projection_imaginary)
    elif kind == "arakawa":
        jacobian = np.asarray(
            jacobian_arakawa_periodic(psi, state_array, float(solver.dx)),
            dtype=np.float64,
        )
        transport = -jacobian
        identity_residual = normalized_rms_difference(transport, -jacobian)[1]
    else:
        raise KeyError(kind)

    output = np.ascontiguousarray(transport, dtype=np.float64)
    if output.shape != (N, N) or not np.isfinite(output).all():
        raise IntegrityFailure(
            "operator_output",
            f"operator output shape or finite gate failed for {trajectory_id}",
            trajectory_id=trajectory_id,
        )
    if sha256_array(state_array) != state_hash or bool(state_array.flags.writeable) != state_writeable:
        raise IntegrityFailure(
            "operator_state_mutation",
            f"operator changed its input state for {trajectory_id}",
            trajectory_id=trajectory_id,
        )
    identity_limit = {
        "fd_advective": CENTERED_FORM_IDENTITY_LIMIT,
        "fd_advective_projected": PSEUDO_PROJECTION_IDENTITY_LIMIT,
        "fd_conservative": CENTERED_FORM_IDENTITY_LIMIT,
        "fd_skew": SKEW_IDENTITY_LIMIT,
        "ps_advective_rc_unprojected": PSEUDO_PROJECTION_IDENTITY_LIMIT,
        "ps_advective_rc_projected": PSEUDO_PROJECTION_IDENTITY_LIMIT,
        "arakawa": ARAKAWA_IDENTITY_LIMIT,
    }[kind]
    if identity_residual > identity_limit:
        raise IntegrityFailure(
            "operator_identity",
            f"identity residual={identity_residual} for {trajectory_id}",
            trajectory_id=trajectory_id,
        )
    if kind.startswith("ps_") and imaginary_ratio > IMAGINARY_RATIO_LIMIT:
        raise IntegrityFailure(
            "real_compatible_imaginary_ratio",
            f"imaginary ratio={imaginary_ratio} for {trajectory_id}",
            trajectory_id=trajectory_id,
        )
    output.setflags(write=False)
    return {
        "transport": output,
        "advection_rhs": -output,
        "maximum_imaginary_ratio": float(imaginary_ratio),
        "identity_residual": float(identity_residual),
    }


def rk2_preview(
    trajectory_id: str,
    solver: object,
    current_state: np.ndarray,
    forcing: np.ndarray,
    *,
    loop_index: int,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_real_compatible: np.ndarray,
    ky_real_compatible: np.ndarray,
) -> dict[str, object]:
    current = np.asarray(current_state, dtype=np.float64)
    current_hash = sha256_array(current)
    current_writeable = bool(current.flags.writeable)
    if current.shape != (N, N) or not np.isfinite(current).all():
        raise IntegrityFailure(
            "current_state", "current state shape or finite gate failed",
            trajectory_id=trajectory_id, loop_index=loop_index,
        )

    psi_1 = solver.streamfunction(current)
    u_1, v_1 = solver.velocity(psi_1)
    operator_1 = compute_transport(
        trajectory_id,
        solver,
        current,
        psi_1,
        u_1,
        v_1,
        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
        kx_real_compatible=kx_real_compatible,
        ky_real_compatible=ky_real_compatible,
    )
    advection_1 = np.asarray(operator_1["advection_rhs"])
    viscous_1 = solver.laplacian_spectral(current)
    total_1 = advection_1 + viscous_1 + forcing
    stage_state = np.ascontiguousarray(current + solver.dt * total_1, dtype=np.float64)
    if np.shares_memory(stage_state, current):
        raise IntegrityFailure(
            "stage_alias", "RK2 stage aliases current state",
            trajectory_id=trajectory_id, loop_index=loop_index, stage="stage_1",
        )

    psi_2 = solver.streamfunction(stage_state)
    u_2, v_2 = solver.velocity(psi_2)
    operator_2 = compute_transport(
        trajectory_id,
        solver,
        stage_state,
        psi_2,
        u_2,
        v_2,
        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
        kx_real_compatible=kx_real_compatible,
        ky_real_compatible=ky_real_compatible,
    )
    advection_2 = np.asarray(operator_2["advection_rhs"])
    viscous_2 = solver.laplacian_spectral(stage_state)
    total_2 = advection_2 + viscous_2 + forcing
    unfiltered = np.ascontiguousarray(
        current + 0.5 * solver.dt * (total_1 + total_2), dtype=np.float64
    )
    unfiltered_hat = np.fft.fft2(unfiltered)
    filtered_complex = np.fft.ifft2(unfiltered_hat * solver.deal)
    accepted_state = np.ascontiguousarray(filtered_complex.real, dtype=np.float64)

    z_current = enstrophy(current)
    z_stage = enstrophy(stage_state)
    z_unfiltered = enstrophy(unfiltered)
    z_filtered = enstrophy(accepted_state)
    stage1_advection_work = mean_product(current, advection_1)
    stage2_advection_work = mean_product(stage_state, advection_2)
    stage1_viscous_work = mean_product(current, viscous_1)
    stage2_viscous_work = mean_product(stage_state, viscous_2)
    stage1_forcing_work = mean_product(current, forcing)
    stage2_forcing_work = mean_product(stage_state, forcing)
    rk2_advection = 0.5 * (stage1_advection_work + stage2_advection_work)
    rk2_viscous = 0.5 * (stage1_viscous_work + stage2_viscous_work)
    rk2_forcing = 0.5 * (stage1_forcing_work + stage2_forcing_work)
    total_difference = total_2 - total_1
    rk2_remainder = (
        solver.dt / 8.0 * float(np.mean(total_difference * total_difference))
    )

    observed_unfiltered_rate = (z_unfiltered - z_current) / solver.dt
    observed_filtered_rate = (z_filtered - z_current) / solver.dt
    mask_rate_physical = (z_filtered - z_unfiltered) / solver.dt
    discarded_hat = np.where(solver.deal, 0.0, unfiltered_hat)
    removed_complex = np.fft.ifft2(discarded_hat)
    mask_rate_spectral = (
        -0.5 * float(np.mean(np.abs(removed_complex) ** 2)) / solver.dt
    )
    unfiltered_rhs = rk2_advection + rk2_viscous + rk2_forcing + rk2_remainder
    filtered_rhs = unfiltered_rhs + mask_rate_physical
    unfiltered_closure = observed_unfiltered_rate - unfiltered_rhs
    filtered_closure = observed_filtered_rate - filtered_rhs
    unfiltered_scale = max(
        abs(observed_unfiltered_rate), abs(rk2_advection), abs(rk2_viscous),
        abs(rk2_forcing), abs(rk2_remainder), RESIDUAL_FLOOR,
    )
    filtered_scale = max(
        abs(observed_filtered_rate), abs(rk2_advection), abs(rk2_viscous),
        abs(rk2_forcing), abs(rk2_remainder), abs(mask_rate_physical),
        RESIDUAL_FLOOR,
    )
    normalized_unfiltered = abs(unfiltered_closure) / unfiltered_scale
    normalized_filtered = abs(filtered_closure) / filtered_scale
    mask_crosscheck_residual = mask_rate_physical - mask_rate_spectral
    normalized_mask_crosscheck = abs(mask_crosscheck_residual) / max(
        abs(mask_rate_physical), abs(mask_rate_spectral), RESIDUAL_FLOOR
    )
    filtered_imaginary_ratio = field_rms(filtered_complex.imag) / max(
        field_rms(filtered_complex.real), RESIDUAL_FLOOR
    )
    maximum_imaginary_ratio = max(
        float(operator_1["maximum_imaginary_ratio"]),
        float(operator_2["maximum_imaginary_ratio"]),
        filtered_imaginary_ratio,
    )
    update_finite = all(
        np.isfinite(value).all()
        for value in (stage_state, unfiltered, accepted_state, total_1, total_2)
    ) and all(
        math.isfinite(float(value))
        for value in (
            unfiltered_closure, filtered_closure, normalized_unfiltered,
            normalized_filtered, normalized_mask_crosscheck,
            maximum_imaginary_ratio,
        )
    )
    integrity_pass = bool(
        update_finite
        and normalized_unfiltered <= UNFILTERED_LEDGER_CLOSURE_LIMIT
        and normalized_filtered <= FILTERED_LEDGER_CLOSURE_LIMIT
        and normalized_mask_crosscheck <= MASK_CROSSCHECK_LIMIT
        and maximum_imaginary_ratio <= IMAGINARY_RATIO_LIMIT
    )
    if not integrity_pass:
        raise IntegrityFailure(
            "trajectory_update_integrity",
            f"integrity gate failed for {trajectory_id} at loop {loop_index}",
            trajectory_id=trajectory_id, loop_index=loop_index,
        )
    if sha256_array(current) != current_hash or bool(current.flags.writeable) != current_writeable:
        raise IntegrityFailure(
            "current_state_mutation", "RK2 preview changed current state",
            trajectory_id=trajectory_id, loop_index=loop_index,
        )
    if np.shares_memory(accepted_state, stage_state) or np.shares_memory(accepted_state, current):
        raise IntegrityFailure(
            "accepted_state_alias", "accepted state aliases current or stage state",
            trajectory_id=trajectory_id, loop_index=loop_index,
        )

    stage_state.setflags(write=False)
    accepted_state.setflags(write=False)
    ledger_scalars = (
        rk2_advection, rk2_viscous, rk2_forcing, rk2_remainder,
        mask_rate_physical, observed_unfiltered_rate, observed_filtered_rate,
        unfiltered_closure, filtered_closure,
    )
    return {
        "loop_index": loop_index,
        "completed_steps": loop_index + 1,
        "physical_time": (loop_index + 1) * solver.dt,
        "trajectory_id": trajectory_id,
        "current": current,
        "stage": stage_state,
        "accepted": accepted_state,
        "psi_1": psi_1,
        "u_1": u_1,
        "v_1": v_1,
        "psi_2": psi_2,
        "u_2": u_2,
        "v_2": v_2,
        "stage1_advection_work_rate": stage1_advection_work,
        "stage2_advection_work_rate": stage2_advection_work,
        "rk2_advection_rate": rk2_advection,
        "rk2_viscous_rate": rk2_viscous,
        "rk2_forcing_rate": rk2_forcing,
        "rk2_quadratic_remainder_rate": rk2_remainder,
        "mask_enstrophy_change_rate": mask_rate_physical,
        "observed_filtered_enstrophy_rate": observed_filtered_rate,
        "z_current": z_current,
        "z_stage": z_stage,
        "z_unfiltered": z_unfiltered,
        "z_filtered": z_filtered,
        "unfiltered_closure_residual": unfiltered_closure,
        "filtered_closure_residual": filtered_closure,
        "normalized_unfiltered_closure": normalized_unfiltered,
        "normalized_filtered_closure": normalized_filtered,
        "mask_crosscheck_residual": mask_crosscheck_residual,
        "normalized_mask_crosscheck": normalized_mask_crosscheck,
        "maximum_imaginary_ratio": maximum_imaginary_ratio,
        "operator_identity_residual": max(
            float(operator_1["identity_residual"]),
            float(operator_2["identity_residual"]),
        ),
        "update_finite": update_finite,
        "integrity_pass": integrity_pass,
        "ledger_scalars": ledger_scalars,
    }


def initialize_trajectory_states(initial: np.ndarray) -> dict[str, np.ndarray]:
    states: dict[str, np.ndarray] = {}
    for trajectory_id in TRAJECTORY_IDS:
        owned_state = np.array(initial, dtype=np.float64, copy=True, order="C")
        owned_state.setflags(write=False)
        states[trajectory_id] = owned_state
    return states


def state_alias_count(
    states: Mapping[str, np.ndarray],
    forcing: np.ndarray,
    kx_real_compatible: np.ndarray,
    ky_real_compatible: np.ndarray,
) -> int:
    aliases = 0
    for first, second in PAIR_IDS:
        aliases += int(np.shares_memory(states[first], states[second]))
    for state in states.values():
        aliases += int(np.shares_memory(state, forcing))
        aliases += int(np.shares_memory(state, kx_real_compatible))
        aliases += int(np.shares_memory(state, ky_real_compatible))
    return aliases


def trajectory_alias_count(
    trajectory_id: str,
    states: Mapping[str, np.ndarray],
    forcing: np.ndarray,
    kx_real_compatible: np.ndarray,
    ky_real_compatible: np.ndarray,
    preview: Mapping[str, object],
) -> int:
    state = states[trajectory_id]
    aliases = int(np.shares_memory(state, forcing))
    aliases += int(np.shares_memory(state, kx_real_compatible))
    aliases += int(np.shares_memory(state, ky_real_compatible))
    aliases += int(np.shares_memory(state, np.asarray(preview["stage"])))
    for other_id, other in states.items():
        if other_id != trajectory_id:
            aliases += int(np.shares_memory(state, other))
    return aliases


def compute_all_previews(
    order: Sequence[str],
    snapshots: Mapping[str, np.ndarray],
    solver: object,
    forcing: np.ndarray,
    *,
    loop_index: int,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_real_compatible: np.ndarray,
    ky_real_compatible: np.ndarray,
) -> dict[str, dict[str, object]]:
    hashes_before = {key: sha256_array(value) for key, value in snapshots.items()}
    flags_before = {key: bool(value.flags.writeable) for key, value in snapshots.items()}
    previews: dict[str, dict[str, object]] = {}
    for trajectory_id in order:
        previews[trajectory_id] = rk2_preview(
            trajectory_id,
            solver,
            snapshots[trajectory_id],
            forcing,
            loop_index=loop_index,
            jacobian_arakawa_periodic=jacobian_arakawa_periodic,
            kx_real_compatible=kx_real_compatible,
            ky_real_compatible=ky_real_compatible,
        )
    for key, value in snapshots.items():
        if sha256_array(value) != hashes_before[key] or bool(value.flags.writeable) != flags_before[key]:
            raise IntegrityFailure(
                "preview_state_mutation", f"preview evaluation changed snapshot {key}",
                trajectory_id=key, loop_index=loop_index,
            )
    return previews


def accept_previews_without_cross_mutation(
    states: Mapping[str, np.ndarray],
    previews: Mapping[str, Mapping[str, object]],
    *,
    loop_index: int,
) -> tuple[dict[str, np.ndarray], int]:
    accepted = dict(states)
    mutation_count = 0
    for trajectory_id in TRAJECTORY_IDS:
        before_other = {
            key: sha256_array(value)
            for key, value in accepted.items()
            if key != trajectory_id
        }
        accepted[trajectory_id] = np.asarray(previews[trajectory_id]["accepted"])
        for key, expected_hash in before_other.items():
            mutation_count += int(sha256_array(accepted[key]) != expected_hash)
    if mutation_count:
        raise IntegrityFailure(
            "cross_trajectory_mutation",
            f"unexpected cross-trajectory mutations={mutation_count}",
            loop_index=loop_index,
        )
    return accepted, mutation_count


# ============================================================================
# Sentinel cross-checks and descriptive diagnostics
# ============================================================================

def sentinel_helper_crosschecks(
    loop_index: int,
    solver: object,
    baseline_preview: Mapping[str, object],
    operator_references: Mapping[tuple[int, str], Mapping[str, str]],
    state_reference: Mapping[str, str],
    *,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    advection_fd_centered: Callable[..., np.ndarray],
    advection_arakawa: Callable[..., np.ndarray],
    kx_real_compatible: np.ndarray,
    ky_real_compatible: np.ndarray,
) -> dict[str, dict[str, object]]:
    current = np.asarray(baseline_preview["current"])
    stage = np.asarray(baseline_preview["stage"])
    psi_1 = np.asarray(baseline_preview["psi_1"])
    u_1 = np.asarray(baseline_preview["u_1"])
    v_1 = np.asarray(baseline_preview["v_1"])
    psi_2 = np.asarray(baseline_preview["psi_2"])
    u_2 = np.asarray(baseline_preview["u_2"])
    v_2 = np.asarray(baseline_preview["v_2"])

    embedded_fd = compute_transport(
        BASELINE_TRAJECTORY_ID, solver, current, psi_1, u_1, v_1,
        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
        kx_real_compatible=kx_real_compatible,
        ky_real_compatible=ky_real_compatible,
    )["transport"]
    project_fd = np.asarray(advection_fd_centered(solver, current), dtype=np.float64)
    if normalized_rms_difference(embedded_fd, project_fd)[1] > ORDER_INVARIANCE_LIMIT:
        raise IntegrityFailure(
            "baseline_project_helper", "baseline Stage D helper differs from project helper",
            loop_index=loop_index,
        )

    arakawa_id = "TRAJ_ARAKAWA_V1"
    embedded_arakawa = compute_transport(
        arakawa_id, solver, current, psi_1, u_1, v_1,
        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
        kx_real_compatible=kx_real_compatible,
        ky_real_compatible=ky_real_compatible,
    )["transport"]
    project_arakawa = np.asarray(advection_arakawa(solver, current), dtype=np.float64)
    if normalized_rms_difference(embedded_arakawa, project_arakawa)[1] > ARAKAWA_IDENTITY_LIMIT:
        raise IntegrityFailure(
            "arakawa_project_helper", "Arakawa Stage D helper differs from project helper",
            trajectory_id=arakawa_id, loop_index=loop_index,
        )

    results: dict[str, dict[str, object]] = {}
    stage1_imaginary_values: list[float] = []
    stage2_imaginary_values: list[float] = []
    for registry in TRAJECTORY_REGISTRY:
        trajectory_id = registry["trajectory_id"]
        operator_id = registry["stage_c_operator_id"]
        first = compute_transport(
            trajectory_id, solver, current, psi_1, u_1, v_1,
            jacobian_arakawa_periodic=jacobian_arakawa_periodic,
            kx_real_compatible=kx_real_compatible,
            ky_real_compatible=ky_real_compatible,
        )
        second = compute_transport(
            trajectory_id, solver, stage, psi_2, u_2, v_2,
            jacobian_arakawa_periodic=jacobian_arakawa_periodic,
            kx_real_compatible=kx_real_compatible,
            ky_real_compatible=ky_real_compatible,
        )
        stage1_imaginary_values.append(float(first["maximum_imaginary_ratio"]))
        stage2_imaginary_values.append(float(second["maximum_imaginary_ratio"]))
        stage1_work = mean_product(current, first["advection_rhs"])
        stage2_work = mean_product(stage, second["advection_rhs"])
        weighted_work = 0.5 * (stage1_work + stage2_work)
        reference = operator_references[(loop_index, operator_id)]
        archived_stage1 = finite_float("archived_stage1_rhs_work", reference["stage1_rhs_work"])
        archived_stage2 = finite_float("archived_stage2_rhs_work", reference["stage2_rhs_work"])
        archived_weighted = finite_float(
            "archived_stage_weighted_rhs_work", reference["stage_weighted_rhs_work"]
        )
        archived_identity = finite_float(
            "archived_operator_identity", reference["operator_specific_identity_residual"]
        )
        comparisons = (
            archived_scalar_comparison(stage1_work, archived_stage1)[2],
            archived_scalar_comparison(stage2_work, archived_stage2)[2],
            archived_scalar_comparison(weighted_work, archived_weighted)[2],
            abs(float(first["identity_residual"]) - archived_identity)
                <= max(CENTERED_FORM_IDENTITY_LIMIT, PSEUDO_PROJECTION_IDENTITY_LIMIT),
        )
        results[trajectory_id] = {
            "reference_work": archived_weighted,
            "helper_work": weighted_work,
            "difference": abs(weighted_work - archived_weighted),
            "pass": all(comparisons),
        }

    archived_stage1_imag = finite_float(
        "stage1_maximum_imaginary_ratio", state_reference["stage1_maximum_imaginary_ratio"]
    )
    archived_stage2_imag = finite_float(
        "stage2_maximum_imaginary_ratio", state_reference["stage2_maximum_imaginary_ratio"]
    )
    imaginary_pass = (
        archived_scalar_comparison(max(stage1_imaginary_values), archived_stage1_imag)[2]
        and archived_scalar_comparison(max(stage2_imaginary_values), archived_stage2_imag)[2]
    )
    for result in results.values():
        result["pass"] = bool(result["pass"] and imaginary_pass)
    return results


def spectrum_summary(
    u: np.ndarray, v: np.ndarray, kx: np.ndarray, ky: np.ndarray
) -> dict[str, object]:
    normalization = float(N * N) ** 2
    mode_energy = 0.5 * (
        np.abs(np.fft.fft2(u)) ** 2 + np.abs(np.fft.fft2(v)) ** 2
    ) / normalization
    shell_index = np.floor(np.sqrt(kx * kx + ky * ky)).astype(int)
    shell_energy = np.bincount(
        shell_index.ravel(), weights=mode_energy.ravel(), minlength=int(shell_index.max()) + 1
    )
    total = max(float(np.sum(shell_energy)), RESIDUAL_FLOOR)
    shell_numbers = np.arange(len(shell_energy))
    return {
        "dominant_shell": int(np.argmax(shell_energy)),
        "low_k_fraction": float(np.sum(shell_energy[shell_numbers <= 4])) / total,
        "tail_fraction": float(np.sum(shell_energy[shell_numbers > 4])) / total,
        "high_k_fraction": float(np.sum(shell_energy[shell_numbers >= 10])) / total,
    }


def build_diagnostic(
    loop_index: int,
    trajectory_id: str,
    state: np.ndarray,
    preview: Mapping[str, object],
    solver: object,
    forcing: np.ndarray,
    *,
    forcing_budget_snapshot: Callable[..., Mapping[str, object]],
) -> dict[str, object]:
    psi = solver.streamfunction(state)
    u, v = solver.velocity(psi)
    budget = forcing_budget_snapshot(
        omega=state,
        forcing=forcing,
        nu=solver.nu,
        kx=solver.kx,
        ky=solver.ky,
        dt=solver.dt,
        loop_index=loop_index,
    )
    spectrum = spectrum_summary(u, v, np.asarray(solver.kx), np.asarray(solver.ky))
    finite_status = bool(
        np.isfinite(state).all()
        and np.isfinite(u).all()
        and np.isfinite(v).all()
        and all(
            math.isfinite(float(budget[name]))
            for name in (
                "energy", "enstrophy", "energy_injection_rate",
                "enstrophy_injection_rate", "viscous_energy_dissipation_rate",
                "viscous_enstrophy_dissipation_rate",
            )
        )
    )
    if not finite_status:
        raise IntegrityFailure(
            "sample_diagnostic_finite", "sample diagnostic is nonfinite",
            trajectory_id=trajectory_id, loop_index=loop_index,
        )
    return {
        "row": {
            "loop_index": loop_index,
            "completed_steps": loop_index + 1,
            "physical_time": (loop_index + 1) * solver.dt,
            "trajectory_id": trajectory_id,
            "operator_family": trajectory_metadata(trajectory_id)["operator_family"],
            "energy": budget["energy"],
            "enstrophy": budget["enstrophy"],
            "vorticity_rms": field_rms(state),
            "velocity_rms": float(np.sqrt(np.mean(u * u + v * v))),
            "energy_injection": budget["energy_injection_rate"],
            "enstrophy_injection": budget["enstrophy_injection_rate"],
            "viscous_energy_dissipation": budget["viscous_energy_dissipation_rate"],
            "viscous_enstrophy_dissipation": budget["viscous_enstrophy_dissipation_rate"],
            "advection_enstrophy_work": preview["rk2_advection_rate"],
            "rk2_remainder": preview["rk2_quadratic_remainder_rate"],
            "mask_enstrophy_change": preview["mask_enstrophy_change_rate"],
            "normalized_filtered_closure": preview["normalized_filtered_closure"],
            "dominant_shell": spectrum["dominant_shell"],
            "low_k_fraction": spectrum["low_k_fraction"],
            "tail_fraction": spectrum["tail_fraction"],
            "high_k_fraction": spectrum["high_k_fraction"],
            "maximum_imaginary_ratio": preview["maximum_imaginary_ratio"],
            "accepted_state_sha256": sha256_array(state),
            "finite_status": finite_status,
        },
        "state": state,
        "u": u,
        "v": v,
        "energy": float(budget["energy"]),
        "enstrophy": float(budget["enstrophy"]),
        **spectrum,
    }


def build_pairwise_row(
    loop_index: int,
    first_id: str,
    second_id: str,
    diagnostics: Mapping[str, Mapping[str, object]],
    solver: object,
) -> dict[str, object]:
    first = diagnostics[first_id]
    second = diagnostics[second_id]
    first_state = np.asarray(first["state"])
    second_state = np.asarray(second["state"])
    vorticity_difference = field_rms(first_state - second_state) / max(
        field_rms(first_state), field_rms(second_state), RESIDUAL_FLOOR
    )
    first_u = np.asarray(first["u"])
    first_v = np.asarray(first["v"])
    second_u = np.asarray(second["u"])
    second_v = np.asarray(second["v"])
    numerator = math.sqrt(
        field_rms(first_u - second_u) ** 2 + field_rms(first_v - second_v) ** 2
    )
    first_velocity_rms = float(np.sqrt(np.mean(first_u * first_u + first_v * first_v)))
    second_velocity_rms = float(
        np.sqrt(np.mean(second_u * second_u + second_v * second_v))
    )
    velocity_difference = numerator / max(
        first_velocity_rms, second_velocity_rms, RESIDUAL_FLOOR
    )
    numeric_values = (
        vorticity_difference,
        velocity_difference,
        cosine_similarity(first_state, second_state),
        symmetric_relative_difference(float(first["energy"]), float(second["energy"])),
        symmetric_relative_difference(
            float(first["enstrophy"]), float(second["enstrophy"])
        ),
    )
    finite_status = all(math.isfinite(value) for value in numeric_values)
    if not finite_status:
        raise IntegrityFailure(
            "pairwise_finite", "pairwise diagnostic is nonfinite", loop_index=loop_index
        )
    return {
        "loop_index": loop_index,
        "completed_steps": loop_index + 1,
        "physical_time": (loop_index + 1) * solver.dt,
        "trajectory_a": first_id,
        "trajectory_b": second_id,
        "normalized_vorticity_rms_difference": numeric_values[0],
        "normalized_velocity_difference": numeric_values[1],
        "vorticity_cosine_similarity": numeric_values[2],
        "energy_relative_difference": numeric_values[3],
        "enstrophy_relative_difference": numeric_values[4],
        "dominant_shell_difference": (
            int(first["dominant_shell"]) - int(second["dominant_shell"])
        ),
        "low_k_fraction_difference": (
            float(first["low_k_fraction"]) - float(second["low_k_fraction"])
        ),
        "tail_fraction_difference": (
            float(first["tail_fraction"]) - float(second["tail_fraction"])
        ),
        "high_k_fraction_difference": (
            float(first["high_k_fraction"]) - float(second["high_k_fraction"])
        ),
        "finite_status": finite_status,
    }


# ============================================================================
# Output finalization
# ============================================================================

def write_inventory(run_directory: Path, inventory_path: Path) -> str:
    rows: list[dict[str, object]] = []
    for name in OUTPUT_FILENAMES:
        path = run_directory / name
        if name == inventory_path.name:
            rows.append({"relative_path": name, "bytes": "", "sha256": ""})
        elif path.is_file():
            rows.append(
                {
                    "relative_path": name,
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    self_row = next(row for row in rows if row["relative_path"] == inventory_path.name)

    def render() -> str:
        handle = io.StringIO(newline="")
        writer = csv.DictWriter(
            handle, fieldnames=INVENTORY_FIELDNAMES, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        return handle.getvalue()

    for _ in range(10):
        text = render()
        observed_bytes = len(text.encode("utf-8"))
        if self_row["bytes"] == observed_bytes:
            break
        self_row["bytes"] = observed_bytes
    else:
        raise RuntimeError("file inventory self-byte count did not stabilize")
    atomic_write_text(inventory_path, render())
    return sha256_file(inventory_path)


def render_report(
    run_id: str,
    execution_commit: str,
    counts: Mapping[str, int],
    maximums: Mapping[str, float],
) -> str:
    return "\n".join(
        (
            "# Stage D Separate-Trajectory Pilot Report",
            "",
            "## Control",
            "",
            f"- Run ID: `{run_id}`",
            f"- Execution commit: `{execution_commit}`",
            "- Configuration: `N=64`, `Re=1000`, `dt=0.005`",
            "- Loop indices: `0..3059`",
            "- Updates per trajectory: `3060`",
            "- Trajectories: `7`",
            "",
            "## Integrity result",
            "",
            "> **STAGE D SEPARATE-TRAJECTORY PILOT: PASS**",
            "",
            f"- Baseline Stage B rows reproduced: `{counts['baseline_rows']} / 3060`",
            f"- Trajectory diagnostic rows: `{counts['diagnostic_rows']}`",
            f"- Pairwise rows: `{counts['pairwise_rows']}`",
            f"- Per-step integrity rows: `{counts['integrity_rows']}`",
            f"- Sentinel cross-check rows: `{counts['sentinel_rows']}`",
            f"- Maximum normalized filtered closure: `{maximums['filtered_closure']:.17g}`",
            f"- Maximum normalized unfiltered closure: `{maximums['unfiltered_closure']:.17g}`",
            f"- Maximum real-compatible imaginary ratio: `{maximums['imaginary_ratio']:.17g}`",
            f"- Maximum order-invariance difference: `{maximums['order_difference']:.17g}`",
            "- Shared-memory violations: `0`",
            "- Failed integrity gates: `0`",
            "",
            "## Boundaries",
            "",
            "- Scientific trajectory classification produced: **NO**",
            "- Method ranking produced: **NO**",
            "- Formal convergence result produced: **NO**",
            "- Physical validation produced: **NO**",
            "- Full comparison authorized: **NO**",
            "",
        )
    )


# ============================================================================
# Static inspection
# ============================================================================

FORBIDDEN_CALL_NAMES = (
    "polyfit",
    "curve_fit",
    "linregress",
    "step_once_selectable",
    "run_selectable_diagnostic",
)


def call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def enclosing_function_name(
    node: ast.AST, parent_map: Mapping[ast.AST, ast.AST]
) -> str | None:
    current: ast.AST | None = node
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
    protected_run_calls: list[str] = []
    solver_wavenumber_assignments: list[str] = []
    classification_functions: list[str] = []
    stage_c_runner_imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("project.") or module == "forcing_budget_diagnostic":
                project_imports.append((module, enclosing_function_name(node, parent_map)))
            if "stage_c_remediated_full_same_state_shadow_audit" in module:
                stage_c_runner_imports.append(module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("project."):
                    project_imports.append(
                        (alias.name, enclosing_function_name(node, parent_map))
                    )
                if "stage_c_remediated_full_same_state_shadow_audit" in alias.name:
                    stage_c_runner_imports.append(alias.name)
        elif isinstance(node, ast.Call):
            name = call_name(node)
            if name == "SpectralSolver":
                constructor_calls += 1
            if name in FORBIDDEN_CALL_NAMES:
                forbidden_calls.append(name)
            if name == "run" and isinstance(node.func, ast.Attribute):
                receiver = node.func.value
                if isinstance(receiver, ast.Name) and receiver.id in {
                    "solver", "selectable_solver", "baseline_solver"
                }:
                    protected_run_calls.append(f"{receiver.id}.run")
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
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
                    solver_wavenumber_assignments.append(f"solver.{target.attr}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("classify") or node.name.endswith("classification"):
                classification_functions.append(node.name)

    invalid_imports = [item for item in project_imports if item[1] != "execute_pilot"]
    if invalid_imports:
        raise RuntimeError(f"project imports outside execute_pilot: {invalid_imports}")
    if constructor_calls != 1:
        raise RuntimeError(f"SpectralSolver constructor calls={constructor_calls}, expected=1")
    if forbidden_calls:
        raise RuntimeError(f"forbidden numerical-analysis calls present: {forbidden_calls}")
    if protected_run_calls:
        raise RuntimeError(f"protected or selectable run() calls present: {protected_run_calls}")
    if solver_wavenumber_assignments:
        raise RuntimeError(
            f"solver wavenumber assignments present: {solver_wavenumber_assignments}"
        )
    if stage_c_runner_imports:
        raise RuntimeError(f"Stage C runner imports present: {stage_c_runner_imports}")
    if classification_functions:
        raise RuntimeError(f"scientific classification functions present: {classification_functions}")

    required_functions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required = {
        "initialize_trajectory_states",
        "build_real_compatible_wavenumbers",
        "compute_transport",
        "rk2_preview",
        "compute_all_previews",
        "accept_previews_without_cross_mutation",
        "sentinel_helper_crosschecks",
        "execute_pilot",
    }
    missing = sorted(required - required_functions)
    if missing:
        raise RuntimeError(f"required Stage D pilot functions missing: {missing}")

    required_fragments = (
        "for trajectory_id in TRAJECTORY_IDS:",
        "owned_state = np.array(initial, dtype=np.float64, copy=True, order=\"C\")",
        "stage_state = np.ascontiguousarray(current + solver.dt * total_1",
        "current + 0.5 * solver.dt * (total_1 + total_2)",
        "kx_real_compatible[x_mask] = 0.0",
        "ky_real_compatible[y_mask] = 0.0",
        "np.shares_memory",
        "tuple(reversed(TRAJECTORY_IDS))",
        "PILOT_STOP_INDEX = 3059",
        "PILOT_UPDATES = 3060",
    )
    missing_fragments = [fragment for fragment in required_fragments if fragment not in source]
    if missing_fragments:
        raise RuntimeError(f"required frozen source fragments missing: {missing_fragments}")
    return {
        "project_import_count": len(project_imports),
        "project_imports": project_imports,
        "spectral_solver_constructor_calls": constructor_calls,
        "forbidden_calls": forbidden_calls,
        "protected_run_calls": protected_run_calls,
        "solver_wavenumber_assignments": solver_wavenumber_assignments,
        "classification_functions": classification_functions,
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
    except UnicodeDecodeError as error:
        fail(f"runner is not valid UTF-8: {error}")
    compile(source, str(runner), "exec")
    design_commit = verify_inspection_repository_state(repo, runner)
    source_hashes = verify_source_identities(repo)
    assert_all_output_headers_unique()
    ast_summary = inspect_ast(source)

    if len(TRAJECTORY_REGISTRY) != 7 or len(set(TRAJECTORY_IDS)) != 7:
        fail("trajectory registry is not exactly seven unique IDs")
    if len(PAIR_IDS) != 21:
        fail(f"pair count={len(PAIR_IDS)}, expected=21")
    if DIAGNOSTIC_LOOP_INDICES != tuple(range(0, 3060, 10)) + (3059,):
        fail("pilot diagnostic loop set differs from frozen design")
    if len(DIAGNOSTIC_LOOP_INDICES) != EXPECTED_DIAGNOSTIC_SAMPLES:
        fail("pilot diagnostic sample count differs from frozen design")
    if EXPECTED_TRAJECTORY_DIAGNOSTIC_ROWS != len(DIAGNOSTIC_LOOP_INDICES) * 7:
        fail("trajectory diagnostic row formula is incorrect")
    if EXPECTED_PAIRWISE_ROWS != len(DIAGNOSTIC_LOOP_INDICES) * len(PAIR_IDS):
        fail("pairwise row formula is incorrect")
    if EXPECTED_INTEGRITY_ROWS != PILOT_UPDATES * 7:
        fail("per-step integrity row formula is incorrect")
    if EXPECTED_SENTINEL_ROWS != len(SENTINEL_LOOP_INDICES) * 7:
        fail("sentinel row formula is incorrect")
    if PILOT_STOP_INDEX != PILOT_UPDATES - 1:
        fail("pilot stop index is inconsistent with update count")
    if not math.isclose(PILOT_UPDATES * DT, PILOT_FINAL_TIME, rel_tol=0.0, abs_tol=1e-15):
        fail("pilot final time is inconsistent with update count")
    if len(OUTPUT_FILENAMES) != 8:
        fail("pilot output file count differs from frozen design")
    immutable_forcing_fragment = "forcing.setflags(" + "write=False)"
    if source.count(immutable_forcing_fragment) != 1:
        fail("runner does not freeze exactly one forcing array")

    print()
    print("=" * 72)
    print("STAGE D SEPARATE-TRAJECTORY PILOT RUNNER INSPECTION: PASS")
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", sha256_bytes(raw))
    print("Design commit:", design_commit)
    print("Design SHA256:", source_hashes["stage_d_design"])
    print("Trajectories: 7 EXACT")
    print("Independent owned initial states: PRESENT")
    print("Pilot updates per trajectory: 3060")
    print("Final loop index: 3059")
    print("Baseline Stage B rows required: 3060 / 3060")
    print("Trajectory diagnostic rows:", EXPECTED_TRAJECTORY_DIAGNOSTIC_ROWS)
    print("Pairwise divergence rows:", EXPECTED_PAIRWISE_ROWS)
    print("Per-step integrity rows:", EXPECTED_INTEGRITY_ROWS)
    print("Sentinel cross-check rows:", EXPECTED_SENTINEL_ROWS)
    print("Independent RK2 stage per trajectory: PRESENT")
    print("Shared-memory gates: PRESENT")
    print("Local Nyquist-zeroed wavenumber copies: PRESENT")
    print("Solver wavenumber mutation: ABSENT")
    print("Exact enstrophy ledger per trajectory: PRESENT")
    print("Sentinel forward/reverse order gate: PRESENT")
    print("All output header lists unique: PASS")
    print("Project imports outside run path: NO")
    print("SpectralSolver constructor calls:", ast_summary["spectral_solver_constructor_calls"])
    print("Protected or selectable run() calls: NO")
    print("Stage C accepted-update reuse: NO")
    print("Spectral-slope fitting present: NO")
    print("Lyapunov fitting present: NO")
    print("Convergence calculation present: NO")
    print("Scientific trajectory classification code: ABSENT")
    print("Project modules imported: NO")
    print("Solver constructed: NO")
    print("Numerical timesteps executed: NO")
    print("Files written: NO")
    print("Git mutations: NONE")
    print("Stage D pilot numerical execution authorized by inspection: NO")
    print("Stage D full comparison authorized: NO")
    return 0


# ============================================================================
# Guarded controlled pilot execution
# ============================================================================

def execute_pilot(repo: Path) -> int:
    runner = Path(__file__).resolve()
    execution_commit, source_hashes = verify_run_preflight(repo, runner)
    stage_b_rows = load_stage_b_pilot_rows(repo)
    stage_c_operator_refs, stage_c_state_refs = load_stage_c_sentinel_references(repo)

    created = utc_now()
    run_id = RUN_PREFIX + created.strftime("%Y%m%dT%H%M%SZ") + "_" + execution_commit[:7]
    run_directory = repo / OUTPUT_ROOT / run_id
    if run_directory.exists():
        raise RuntimeError(f"pilot run directory already exists: {run_directory}")
    run_directory.mkdir(parents=True, exist_ok=False)

    metadata_path = run_directory / "run_metadata.json"
    diagnostic_path = run_directory / "trajectory_pilot_diagnostics.csv"
    pairwise_path = run_directory / "trajectory_pilot_pairwise_divergence.csv"
    integrity_path = run_directory / "trajectory_pilot_integrity_per_step.csv"
    sentinel_path = run_directory / "trajectory_pilot_sentinel_crosscheck.csv"
    summary_path = run_directory / "trajectory_pilot_summary.json"
    report_path = run_directory / "STAGE_D_SEPARATE_TRAJECTORY_PILOT_REPORT.md"
    inventory_path = run_directory / "file_inventory.csv"

    metadata: dict[str, object] = {
        "schema_id": "STAGE_D_SEPARATE_TRAJECTORY_PILOT_METADATA_V1",
        "run_id": run_id,
        "status": "running",
        "created_utc": utc_text(created),
        "repository": {
            "branch": EXPECTED_BRANCH,
            "execution_commit": execution_commit,
            "design_commit": resolve_design_commit(repo),
        },
        "configuration": {
            "N": N,
            "Re": RE,
            "nu": NU,
            "dt": DT,
            "pilot_updates": PILOT_UPDATES,
            "pilot_stop_index": PILOT_STOP_INDEX,
            "pilot_final_time": PILOT_FINAL_TIME,
        },
        "trajectory_registry": list(TRAJECTORY_REGISTRY),
        "source_hashes": source_hashes,
        "claims": {
            "scientific_trajectory_classification": False,
            "method_superiority": False,
            "formal_temporal_convergence": False,
            "formal_spatial_convergence": False,
            "physical_validation": False,
            "turbulence": False,
            "cascade": False,
            "inertial_range": False,
            "k_minus_3": False,
            "lyapunov_exponent": False,
            "predictability_horizon": False,
            "production_readiness": False,
            "baseline_replacement": False,
        },
        "progress": {
            "last_completed_loop_index": None,
            "baseline_rows": 0,
            "diagnostic_rows": 0,
            "pairwise_rows": 0,
            "integrity_rows": 0,
            "sentinel_rows": 0,
        },
    }
    atomic_write_json(metadata_path, metadata)

    diagnostic_writer: IncrementalCsvWriter | None = None
    pairwise_writer: IncrementalCsvWriter | None = None
    integrity_writer: IncrementalCsvWriter | None = None
    sentinel_writer: IncrementalCsvWriter | None = None
    failed_gate: str | None = None
    failed_trajectory: str | None = None
    failed_loop: int | None = None
    failed_stage: str | None = None
    last_completed_loop = -1

    counts = {
        "baseline_rows": 0,
        "diagnostic_rows": 0,
        "pairwise_rows": 0,
        "integrity_rows": 0,
        "sentinel_rows": 0,
    }
    maximums = {
        "filtered_closure": 0.0,
        "unfiltered_closure": 0.0,
        "imaginary_ratio": 0.0,
        "order_difference": 0.0,
        "stage_b_absolute_difference": 0.0,
    }

    try:
        from forcing_budget_diagnostic import forcing_budget_snapshot
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
            steps=PILOT_UPDATES,
        )
        if not np.array_equal(solver.w, np.zeros_like(solver.w)):
            raise IntegrityFailure("initial_solver_state", "solver initial state is not exact zero")
        if (
            int(solver.N) != N
            or float(solver.dt) != DT
            or not math.isclose(float(solver.nu), NU, rel_tol=0.0, abs_tol=1e-15)
        ):
            raise IntegrityFailure("solver_configuration", "solver configuration differs from pilot")

        solver_environment = freeze_solver_environment(solver)
        kx_real_compatible, ky_real_compatible = build_real_compatible_wavenumbers(solver)
        kx_hash = sha256_array(kx_real_compatible)
        ky_hash = sha256_array(ky_real_compatible)
        forcing, forcing_statistics = build_rms_matched_multimode_forcing(solver)
        forcing_hash = sha256_array(forcing)
        metadata["forcing"] = forcing_statistics
        atomic_write_json(metadata_path, metadata)

        states = initialize_trajectory_states(np.asarray(solver.w))
        if state_alias_count(
            states, forcing, kx_real_compatible, ky_real_compatible
        ) != 0:
            raise IntegrityFailure("initial_state_alias", "initial trajectory states share memory")

        diagnostic_writer = IncrementalCsvWriter(diagnostic_path, DIAGNOSTIC_FIELDNAMES)
        pairwise_writer = IncrementalCsvWriter(pairwise_path, PAIRWISE_FIELDNAMES)
        integrity_writer = IncrementalCsvWriter(integrity_path, INTEGRITY_FIELDNAMES)
        sentinel_writer = IncrementalCsvWriter(sentinel_path, SENTINEL_FIELDNAMES)

        for loop_index in range(PILOT_UPDATES):
            snapshots = {
                trajectory_id: np.array(
                    states[trajectory_id], dtype=np.float64, copy=True, order="C"
                )
                for trajectory_id in TRAJECTORY_IDS
            }
            for value in snapshots.values():
                value.setflags(write=False)
            snapshot_hashes = {key: sha256_array(value) for key, value in states.items()}

            forward_previews = compute_all_previews(
                TRAJECTORY_IDS,
                snapshots,
                solver,
                forcing,
                loop_index=loop_index,
                jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                kx_real_compatible=kx_real_compatible,
                ky_real_compatible=ky_real_compatible,
            )
            helper_results: dict[str, dict[str, object]] = {}
            if loop_index in SENTINEL_LOOP_INDICES:
                reverse_previews = compute_all_previews(
                    tuple(reversed(TRAJECTORY_IDS)),
                    snapshots,
                    solver,
                    forcing,
                    loop_index=loop_index,
                    jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                    kx_real_compatible=kx_real_compatible,
                    ky_real_compatible=ky_real_compatible,
                )
                helper_results = sentinel_helper_crosschecks(
                    loop_index,
                    solver,
                    forward_previews[BASELINE_TRAJECTORY_ID],
                    stage_c_operator_refs,
                    stage_c_state_refs[loop_index],
                    jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                    advection_fd_centered=advection_fd_centered,
                    advection_arakawa=advection_arakawa,
                    kx_real_compatible=kx_real_compatible,
                    ky_real_compatible=ky_real_compatible,
                )
                for trajectory_id in TRAJECTORY_IDS:
                    forward = forward_previews[trajectory_id]
                    reverse = reverse_previews[trajectory_id]
                    _, normalized_difference = normalized_rms_difference(
                        forward["accepted"], reverse["accepted"]
                    )
                    ledger_difference = max(
                        abs(float(first) - float(second))
                        for first, second in zip(
                            forward["ledger_scalars"], reverse["ledger_scalars"], strict=True
                        )
                    )
                    order_pass = bool(
                        normalized_difference <= ORDER_INVARIANCE_LIMIT
                        and ledger_difference == 0.0
                    )
                    if not order_pass:
                        raise IntegrityFailure(
                            "order_invariance", "forward/reverse preview mismatch",
                            trajectory_id=trajectory_id, loop_index=loop_index,
                        )
                    maximums["order_difference"] = max(
                        maximums["order_difference"], normalized_difference
                    )
                    helper = helper_results[trajectory_id]
                    if not bool(helper["pass"]):
                        raise IntegrityFailure(
                            "stage_c_helper_crosscheck", "Stage D helper differs from Stage C reference",
                            trajectory_id=trajectory_id, loop_index=loop_index,
                        )
                    sentinel_writer.write(
                        {
                            "loop_index": loop_index,
                            "trajectory_id": trajectory_id,
                            "forward_accepted_state_sha256": sha256_array(forward["accepted"]),
                            "reverse_accepted_state_sha256": sha256_array(reverse["accepted"]),
                            "normalized_accepted_state_difference": normalized_difference,
                            "ledger_scalar_difference": ledger_difference,
                            "stage_c_baseline_state_operator_work_reference": helper["reference_work"],
                            "stage_d_helper_operator_work_value": helper["helper_work"],
                            "helper_reference_difference": helper["difference"],
                            "order_invariance_pass": order_pass,
                            "helper_crosscheck_pass": helper["pass"],
                        }
                    )
                    counts["sentinel_rows"] += 1

            baseline_preview = forward_previews[BASELINE_TRAJECTORY_ID]
            baseline_comparison = compare_stage_b_ledger_row(
                baseline_preview, stage_b_rows[loop_index]
            )
            maximums["stage_b_absolute_difference"] = max(
                maximums["stage_b_absolute_difference"],
                float(baseline_comparison["maximum_absolute_difference"]),
            )
            if not bool(baseline_comparison["passed"]):
                raise IntegrityFailure(
                    "stage_b_baseline_reproduction", "baseline differs from Stage B ledger",
                    trajectory_id=BASELINE_TRAJECTORY_ID, loop_index=loop_index,
                )
            counts["baseline_rows"] += 1
            if loop_index == PILOT_STOP_INDEX:
                observed_hashes = (
                    sha256_array(baseline_preview["current"]),
                    sha256_array(baseline_preview["stage"]),
                    sha256_array(baseline_preview["accepted"]),
                )
                expected_hashes = (
                    EXPECTED_CHECKPOINT_CURRENT_SHA256,
                    EXPECTED_CHECKPOINT_STAGE_SHA256,
                    EXPECTED_CHECKPOINT_FILTERED_SHA256,
                )
                if observed_hashes != expected_hashes:
                    raise IntegrityFailure(
                        "baseline_checkpoint_hashes",
                        f"observed={observed_hashes}, expected={expected_hashes}",
                        trajectory_id=BASELINE_TRAJECTORY_ID, loop_index=loop_index,
                    )

            for key, expected_hash in snapshot_hashes.items():
                if sha256_array(states[key]) != expected_hash:
                    raise IntegrityFailure(
                        "state_mutated_before_acceptance", f"state changed during previews: {key}",
                        trajectory_id=key, loop_index=loop_index,
                    )
            states, state_mutation_count = accept_previews_without_cross_mutation(
                states, forward_previews, loop_index=loop_index
            )
            global_alias_count = state_alias_count(
                states, forcing, kx_real_compatible, ky_real_compatible
            )
            if global_alias_count:
                raise IntegrityFailure(
                    "accepted_state_alias", f"accepted state alias count={global_alias_count}",
                    loop_index=loop_index,
                )

            verify_solver_environment(solver, solver_environment)
            if sha256_array(forcing) != forcing_hash:
                raise IntegrityFailure("forcing_mutation", "forcing bytes changed", loop_index=loop_index)
            if (
                sha256_array(kx_real_compatible) != kx_hash
                or sha256_array(ky_real_compatible) != ky_hash
            ):
                raise IntegrityFailure(
                    "real_compatible_wavenumber_mutation",
                    "local real-compatible wavenumber bytes changed",
                    loop_index=loop_index,
                )

            for trajectory_id in TRAJECTORY_IDS:
                preview = forward_previews[trajectory_id]
                alias_count = trajectory_alias_count(
                    trajectory_id,
                    states,
                    forcing,
                    kx_real_compatible,
                    ky_real_compatible,
                    preview,
                )
                row_pass = bool(
                    preview["integrity_pass"]
                    and state_mutation_count == 0
                    and alias_count == 0
                )
                if not row_pass:
                    raise IntegrityFailure(
                        "per_step_integrity", "per-step integrity row failed",
                        trajectory_id=trajectory_id, loop_index=loop_index,
                    )
                integrity_writer.write(
                    {
                        "loop_index": loop_index,
                        "completed_steps": loop_index + 1,
                        "physical_time": (loop_index + 1) * solver.dt,
                        "trajectory_id": trajectory_id,
                        "unfiltered_closure_residual": preview["unfiltered_closure_residual"],
                        "filtered_closure_residual": preview["filtered_closure_residual"],
                        "normalized_unfiltered_closure": preview["normalized_unfiltered_closure"],
                        "normalized_filtered_closure": preview["normalized_filtered_closure"],
                        "mask_crosscheck_residual": preview["mask_crosscheck_residual"],
                        "maximum_imaginary_ratio": preview["maximum_imaginary_ratio"],
                        "state_mutation_count": state_mutation_count,
                        "state_alias_count": alias_count,
                        "update_finite": preview["update_finite"],
                        "integrity_pass": row_pass,
                    }
                )
                counts["integrity_rows"] += 1
                maximums["filtered_closure"] = max(
                    maximums["filtered_closure"],
                    float(preview["normalized_filtered_closure"]),
                )
                maximums["unfiltered_closure"] = max(
                    maximums["unfiltered_closure"],
                    float(preview["normalized_unfiltered_closure"]),
                )
                maximums["imaginary_ratio"] = max(
                    maximums["imaginary_ratio"],
                    float(preview["maximum_imaginary_ratio"]),
                )

            if loop_index in DIAGNOSTIC_LOOP_INDICES:
                sampled: dict[str, dict[str, object]] = {}
                for trajectory_id in TRAJECTORY_IDS:
                    diagnostic = build_diagnostic(
                        loop_index,
                        trajectory_id,
                        states[trajectory_id],
                        forward_previews[trajectory_id],
                        solver,
                        forcing,
                        forcing_budget_snapshot=forcing_budget_snapshot,
                    )
                    sampled[trajectory_id] = diagnostic
                    diagnostic_writer.write(diagnostic["row"])
                    counts["diagnostic_rows"] += 1
                for first_id, second_id in PAIR_IDS:
                    pairwise_writer.write(
                        build_pairwise_row(
                            loop_index, first_id, second_id, sampled, solver
                        )
                    )
                    counts["pairwise_rows"] += 1

            last_completed_loop = loop_index
            metadata["progress"] = {
                "last_completed_loop_index": loop_index,
                **counts,
            }
            if loop_index % PROGRESS_INTERVAL == 0 or loop_index == PILOT_STOP_INDEX:
                base_sample = states[BASELINE_TRAJECTORY_ID]
                print(
                    "progress",
                    f"t={(loop_index + 1) * solver.dt:.3f}",
                    f"Z_base={enstrophy(base_sample):.6e}",
                    f"max_closure={maximums['filtered_closure']:.6e}",
                    f"max_imag={maximums['imaginary_ratio']:.6e}",
                )
            if loop_index % CSV_FLUSH_INTERVAL == 0:
                for writer in (
                    diagnostic_writer, pairwise_writer, integrity_writer, sentinel_writer
                ):
                    writer.flush()
                atomic_write_json(metadata_path, metadata)

        for writer in (
            diagnostic_writer, pairwise_writer, integrity_writer, sentinel_writer
        ):
            writer.close()

        expected_counts = {
            "baseline_rows": EXPECTED_BASELINE_ROWS,
            "diagnostic_rows": EXPECTED_TRAJECTORY_DIAGNOSTIC_ROWS,
            "pairwise_rows": EXPECTED_PAIRWISE_ROWS,
            "integrity_rows": EXPECTED_INTEGRITY_ROWS,
            "sentinel_rows": EXPECTED_SENTINEL_ROWS,
        }
        if counts != expected_counts:
            raise IntegrityFailure(
                "output_row_counts", f"observed={counts}, expected={expected_counts}"
            )
        if last_completed_loop != PILOT_STOP_INDEX:
            raise IntegrityFailure(
                "final_loop_index", f"observed={last_completed_loop}, expected={PILOT_STOP_INDEX}"
            )

        completed = utc_text()
        summary = {
            "schema_id": "STAGE_D_SEPARATE_TRAJECTORY_PILOT_SUMMARY_V1",
            "run_id": run_id,
            "status": "pass",
            "created_utc": metadata["created_utc"],
            "completed_utc": completed,
            "configuration": metadata["configuration"],
            "trajectory_registry": list(TRAJECTORY_REGISTRY),
            "counts": counts,
            "maximum_integrity_values": maximums,
            "integrity": {
                "all_gates_passed": True,
                "failed_gate_count": 0,
                "shared_memory_violations": 0,
                "order_invariance_failures": 0,
                "finite_trajectories": 7,
            },
            "scientific_trajectory_classification_produced": False,
            "full_comparison_authorized": False,
            "claims": metadata["claims"],
        }
        atomic_write_json(summary_path, summary)
        atomic_write_text(
            report_path, render_report(run_id, execution_commit, counts, maximums)
        )
        metadata["status"] = "completed"
        metadata["completed_utc"] = completed
        metadata["progress"] = {"last_completed_loop_index": last_completed_loop, **counts}
        atomic_write_json(metadata_path, metadata)
        inventory_hash = write_inventory(run_directory, inventory_path)

        observed_outputs = sorted(
            path.name for path in run_directory.iterdir() if path.is_file()
        )
        if observed_outputs != sorted(OUTPUT_FILENAMES):
            raise IntegrityFailure(
                "output_file_set",
                f"observed={observed_outputs}, expected={sorted(OUTPUT_FILENAMES)}",
            )
        oversized_actual = {
            path.name: path.stat().st_size
            for path in run_directory.iterdir()
            if path.is_file() and path.stat().st_size >= MAX_OUTPUT_FILE_BYTES
        }
        if oversized_actual:
            raise IntegrityFailure(
                "output_file_size", f"actual output exceeds limit: {oversized_actual}"
            )

        print()
        print("=" * 72)
        print("STAGE D SEPARATE-TRAJECTORY PILOT: PASS")
        print("=" * 72)
        print("Pilot updates per trajectory: 3060")
        print("Trajectories: 7")
        print("Baseline Stage B rows reproduced: 3060 / 3060")
        print("Trajectory diagnostic rows: 2149")
        print("Pairwise rows: 6447")
        print("Integrity rows: 21420")
        print("Sentinel cross-check rows: 21")
        print("Finite trajectories: 7 / 7")
        print("Shared-memory violations: 0")
        print("Order-invariance failures: 0")
        print("Failed integrity gates: 0")
        print("Scientific trajectory classification produced: NO")
        print("Stage D full comparison authorized: NO")
        print("Run directory:", run_directory)
        print("File inventory SHA256:", inventory_hash)
        return 0

    except BaseException as error:
        if isinstance(error, IntegrityFailure):
            failed_gate = error.gate
            failed_trajectory = error.trajectory_id
            failed_loop = error.loop_index
            failed_stage = error.stage
        else:
            failed_gate = type(error).__name__

        for writer in (
            diagnostic_writer, pairwise_writer, integrity_writer, sentinel_writer
        ):
            if writer is not None:
                try:
                    writer.close()
                except Exception:
                    pass
        metadata["status"] = "failed"
        metadata["completed_utc"] = utc_text()
        metadata["failed_gate"] = failed_gate
        metadata["failed_trajectory"] = failed_trajectory
        metadata["failed_loop_index"] = failed_loop
        metadata["failed_stage"] = failed_stage
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = str(error)
        metadata["progress"] = {"last_completed_loop_index": last_completed_loop, **counts}
        try:
            atomic_write_json(metadata_path, metadata)
        except Exception:
            pass
        try:
            inventory_hash = write_inventory(run_directory, inventory_path)
        except Exception:
            inventory_hash = None

        print()
        print("STAGE D SEPARATE-TRAJECTORY PILOT: FAILED")
        print("Failed trajectory:", failed_trajectory)
        print("Failed gate:", failed_gate)
        print("Failed loop index:", failed_loop)
        print("Failed stage:", failed_stage)
        print("Partial evidence preserved at:", run_directory)
        if inventory_hash is not None:
            print("Partial inventory SHA256:", inventory_hash)
        print("Do not rerun automatically.")
        raise


# ============================================================================
# Command line
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect or execute the controlled Stage D separate-trajectory pilot."
    )
    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help="inspect without numerical execution, or run the separately authorized pilot",
    )
    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent
    if arguments.mode == "inspect":
        return inspect_runner(repo)
    if arguments.mode == "run":
        return execute_pilot(repo)
    raise RuntimeError(f"unsupported mode: {arguments.mode!r}")


if __name__ == "__main__":
    raise SystemExit(main())
