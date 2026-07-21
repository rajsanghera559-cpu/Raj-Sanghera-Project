"""
Controlled Stage E focused resolution and timestep refinement study.

Usage:
    python -B run_stage_e_focused_refinement_study.py inspect
    python -B run_stage_e_focused_refinement_study.py run

The inspection path parses this source and verifies the frozen repository
interfaces. It does not import project modules, construct a solver, create an
output directory, or execute a numerical timestep.

The separately authorized run path advances five independently owned
trajectories over a crossed five-case resolution/timestep matrix. Projected
operator variants are evaluated only as non-advancing same-state controls.
There is no reference-candidate execution path in this runner.
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
import time
from collections.abc import Callable, Mapping, Sequence
from itertools import combinations
from pathlib import Path

import numpy as np


# ============================================================================
# Frozen repository identities
# ============================================================================

RUNNER_NAME = "run_stage_e_focused_refinement_study.py"
EXPECTED_BRANCH = "phase4_validation"
AUTHORIZED_DESIGN_COMMIT = "778606a9b54f5d0a2b1b1117ec805573278d4d1d"

DESIGN_PATH = Path(
    "STAGE_E_FOCUSED_RESOLUTION_TIMESTEP_REFERENCE_STUDY_DESIGN.md"
)
EXPECTED_DESIGN_SHA256 = (
    "75AE9F88326026BF015104D83861CD456584351252522F0CBD34323A5B07A825"
)

STAGE_D1R_RUNNER_PATH = Path("run_stage_d_separate_trajectory_pilot_remediated.py")
EXPECTED_STAGE_D1R_RUNNER_SHA256 = (
    "21A7E2D1168C5A6D33C563B7A278006E5A047AD18025B42F2BFE4BB65BDD3BC3"
)
STAGE_D1R_COMPLETION_REPORT_PATH = Path(
    "STAGE_D1_REMEDIATED_SEPARATE_TRAJECTORY_PILOT_COMPLETION_REPORT.md"
)
EXPECTED_STAGE_D1R_COMPLETION_REPORT_SHA256 = (
    "C5BDCDE3D97EDB1568B2A6C959CF98A94DE0207415772DAAE181144C0E2850BA"
)

SPECTRAL_SOLVER_PATH = Path("project/solver/spectral_solver.py")
ADVECTION_OPERATORS_PATH = Path("project/solver/advection_operators.py")
FORCING_BUDGET_PATH = Path("forcing_budget_diagnostic.py")
EXPECTED_SPECTRAL_SOLVER_BLOB = "09cb2d04b0f229c1f605bf883ce08dfd2cab51d5"
EXPECTED_ADVECTION_OPERATORS_BLOB = "849b3d5c95c955a7db73313d8680c942fd32c571"
EXPECTED_FORCING_BUDGET_BLOB = "393c5a25d5461d7d34c979dd1b19dd9d5ba9fb77"
EXPECTED_FORCING_BUDGET_SHA256 = (
    "A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B"
)

STAGE_D1R_EVIDENCE_DIRECTORY = (
    Path("experiments")
    / "advection_form_trajectory_pilot_remediated"
    / "stage_d_separate_trajectory_pilot_remediated_20260721T055827Z_b3612a0"
)
STAGE_D1R_EVIDENCE_HASHES = {
    "run_metadata.json":
        "15E47994F59DE68B7692A9CCD46923567CE7EFB5E4252994E9A90AB1D1A677CA",
    "trajectory_pilot_diagnostics.csv":
        "91F25F8ACCF9985177070EE0B030476C9412C159FBA309DBBE28E8BE92784A39",
    "trajectory_pilot_pairwise_divergence.csv":
        "8943CEE0283276AD8A3759E303A6A41BD01A1A567EA7BFA0916923CED1B7C822",
    "trajectory_pilot_integrity_per_step.csv":
        "CDF70CE26DC6C36F546A63DD3E2B6E52D352E2BBB57C9F95EAD3AEF9BEB21A8D",
    "trajectory_pilot_sentinel_crosscheck.csv":
        "1C0EBB09E1DB65B32B63F07B3B1DD79F0654E3620CC364B8A86773AF0E61FC8D",
    "trajectory_pilot_summary.json":
        "17460F60CF3CE05A256FF48DC192BB93DCDA4BE1978110EB18760A833A78ACC5",
    "STAGE_D_REMEDIATED_SEPARATE_TRAJECTORY_PILOT_REPORT.md":
        "C139FB3E6D565F8B26427D9FACE50C90538AD56A2D154F58B50FBC9556C4E054",
    "file_inventory.csv":
        "B71EF5D9313B1C3FAE007726C92F77F7C0CD17B26D2A27F7841F073BECD8BE20",
}


# ============================================================================
# Frozen scientific matrix and limits
# ============================================================================

RE = 1000
NU = 1.0 / RE
FINAL_TIME = 15.3
FORCING_TARGET_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14
EXPECTED_C0_FORCING_SHA256 = (
    "504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB"
)

CASE_REGISTRY = (
    {"case_id": "C0_N64_DT00500", "N": 64, "dt": 0.005, "updates": 3060},
    {"case_id": "C1_N64_DT00250", "N": 64, "dt": 0.0025, "updates": 6120},
    {"case_id": "C2_N64_DT00125", "N": 64, "dt": 0.00125, "updates": 12240},
    {"case_id": "C3_N96_DT00125", "N": 96, "dt": 0.00125, "updates": 12240},
    {"case_id": "C4_N144_DT00125", "N": 144, "dt": 0.00125, "updates": 12240},
)
CASE_IDS = tuple(str(row["case_id"]) for row in CASE_REGISTRY)
CASE_BY_ID = {str(row["case_id"]): row for row in CASE_REGISTRY}

TRAJECTORY_REGISTRY = (
    {
        "trajectory_id": "TRAJ_BASE_FD_ADVECTIVE_V1",
        "operator_family": "BASELINE",
        "operator_kind": "fd_advective",
    },
    {
        "trajectory_id": "TRAJ_FD_CONSERVATIVE_V1",
        "operator_family": "CENTERED_ALGEBRAIC",
        "operator_kind": "fd_conservative",
    },
    {
        "trajectory_id": "TRAJ_FD_SKEW_V1",
        "operator_family": "CENTERED_ALGEBRAIC",
        "operator_kind": "fd_skew",
    },
    {
        "trajectory_id": "TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2",
        "operator_family": "PSEUDO_SPECTRAL_RC_NYQUIST",
        "operator_kind": "ps_advective_rc_unprojected",
    },
    {
        "trajectory_id": "TRAJ_ARAKAWA_V1",
        "operator_family": "ARAKAWA",
        "operator_kind": "arakawa",
    },
)
TRAJECTORY_IDS = tuple(str(row["trajectory_id"]) for row in TRAJECTORY_REGISTRY)
TRAJECTORY_BY_ID = {str(row["trajectory_id"]): row for row in TRAJECTORY_REGISTRY}
PRIMARY_PAIRS = tuple(combinations(TRAJECTORY_IDS, 2))

PROJECTION_CONTROLS = (
    {
        "control_id": "FD_ADVECTIVE_PROJECTED_CONTROL",
        "trajectory_id": "TRAJ_BASE_FD_ADVECTIVE_V1",
        "canonical_kind": "fd_advective",
        "control_kind": "fd_advective_projected",
    },
    {
        "control_id": "PS_ADVECTIVE_PROJECTED_CONTROL",
        "trajectory_id": "TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2",
        "canonical_kind": "ps_advective_rc_unprojected",
        "control_kind": "ps_advective_rc_projected",
    },
)

COMMON_SAMPLE_TICKS = tuple(range(307))
COMMON_SAMPLE_TIMES = tuple(tick * 0.05 for tick in COMMON_SAMPLE_TICKS)
ANCHOR_TICKS = (0, 51, 102, 153, 204, 255, 306)
ANCHOR_TIMES = tuple(tick * 0.05 for tick in ANCHOR_TICKS)

D1R_SAMPLE_COMPLETED_STEPS = tuple(range(1, 3052, 10)) + (3060,)
D1R_PRIMARY_EXPECTED_ROWS = 5 * 307

D1R_DIAGNOSTIC_FIELDNAMES = (
    "loop_index", "completed_steps", "physical_time", "trajectory_id",
    "operator_family", "energy", "enstrophy", "vorticity_rms",
    "velocity_rms", "energy_injection", "enstrophy_injection",
    "viscous_energy_dissipation", "viscous_enstrophy_dissipation",
    "advection_enstrophy_work", "rk2_remainder", "mask_enstrophy_change",
    "normalized_filtered_closure", "dominant_shell", "low_k_fraction",
    "tail_fraction", "high_k_fraction", "maximum_imaginary_ratio",
    "accepted_state_sha256", "finite_status",
)
D1R_INTEGER_FIELDS = ("loop_index", "completed_steps", "dominant_shell")
D1R_FLOAT_FIELDS = (
    "physical_time", "energy", "enstrophy", "vorticity_rms", "velocity_rms",
    "energy_injection", "enstrophy_injection", "viscous_energy_dissipation",
    "viscous_enstrophy_dissipation", "advection_enstrophy_work",
    "rk2_remainder", "mask_enstrophy_change", "normalized_filtered_closure",
    "low_k_fraction", "tail_fraction", "high_k_fraction",
    "maximum_imaginary_ratio",
)
D1R_STRING_FIELDS = ("trajectory_id", "operator_family")

EXPECTED_C0_FINAL_ACCEPTED_SHA256 = {
    "TRAJ_BASE_FD_ADVECTIVE_V1":
        "1A95D9BF2065E88B47E2E578B8862DB83B47D804288354C32299EF44809EE61E",
    "TRAJ_FD_CONSERVATIVE_V1":
        "C3C161F0FFE7B1807498CDCDA866B8C6D56D8FA56D6C0D8E28B9713957F8C9BF",
    "TRAJ_FD_SKEW_V1":
        "7662442A0A7D27E766DA1815B1301A7942AB1BB27E00F7608FEDE1D6D393270D",
    "TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2":
        "CDBADDCF8D56321CD4F254D5906F1FD692201AF4FC79624D26D32C43E67AF818",
    "TRAJ_ARAKAWA_V1":
        "FCE132855C77EBFC7A8CFC060A744B476B2FB9F923D949BD65B332AB7FC6249B",
}
EXPECTED_C0_FINAL_BASELINE_CURRENT_SHA256 = (
    "7534D7C24F2666993BBD5B7B79E03B82B8F7F15665B41C30453351A18196E852"
)
EXPECTED_C0_FINAL_BASELINE_STAGE_SHA256 = (
    "01F5C093F544119D75C4903FBEBC8B809224CABEF12CE125FB94C6AA509BD2B7"
)
EXPECTED_C0_FINAL_BASELINE_ACCEPTED_SHA256 = (
    "1A95D9BF2065E88B47E2E578B8862DB83B47D804288354C32299EF44809EE61E"
)

TEMPORAL_ADJACENCIES = (
    ("C0_N64_DT00500", "C1_N64_DT00250"),
    ("C1_N64_DT00250", "C2_N64_DT00125"),
)
SPATIAL_ADJACENCIES = (
    ("C2_N64_DT00125", "C3_N96_DT00125"),
    ("C3_N96_DT00125", "C4_N144_DT00125"),
)

EXPECTED_PRIMARY_UPDATES = 229_500
EXPECTED_CASE_DIAGNOSTIC_ROWS = 7_675
EXPECTED_WITHIN_PAIRWISE_ROWS = 15_350
EXPECTED_REFINEMENT_ROWS = 140
EXPECTED_PROJECTION_CONTROL_ROWS = 70
EXPECTED_INTEGRITY_SUMMARY_ROWS = 25
EXPECTED_ANCHOR_SPECTRA_ROWS = 10_780
EXPECTED_STATE_ARRAYS = 175
EXPECTED_DEAL_ACTIVE_MODE_COUNTS = {64: 1_849, 96: 3_969, 144: 9_025}

FILTERED_LEDGER_CLOSURE_LIMIT = 1.0e-10
UNFILTERED_LEDGER_CLOSURE_LIMIT = 1.0e-10
MASK_CROSSCHECK_LIMIT = 1.0e-12
IMAGINARY_RATIO_LIMIT = 1.0e-13
ORDER_INVARIANCE_LIMIT = 1.0e-15
PROJECTION_ABSOLUTE_LIMIT = 1.0e-8
PROJECTION_RELATIVE_FRACTION = 0.01
FLOOR_SAFETY_MULTIPLIER = 64.0
RESIDUAL_FLOOR = 1.0e-30

BASELINE_ARCHIVE_RELATIVE_TOLERANCE = 1.0e-11
BASELINE_ARCHIVE_ABSOLUTE_FLOOR = 1.0e-14

PROGRESS_INTERVAL_SECONDS = 1.0
MAX_OUTPUT_FILE_BYTES = 40_000_000

OUTPUT_ROOT = Path("experiments") / "focused_refinement_study"
RUN_PREFIX = "stage_e_focused_refinement_"
OUTPUT_FILENAMES = (
    "run_metadata.json",
    "case_diagnostics.csv",
    "within_case_pairwise.csv",
    "refinement_comparisons.csv",
    "projection_controls.csv",
    "integrity_summary.csv",
    "anchor_spectra.csv",
    "state_checkpoints.npz",
    "stage_e_summary.json",
    "file_inventory.csv",
)
PREDICTED_OUTPUT_FILE_BYTES = {
    "run_metadata.json": 250_000,
    "case_diagnostics.csv": 8_000_000,
    "within_case_pairwise.csv": 12_000_000,
    "refinement_comparisons.csv": 1_000_000,
    "projection_controls.csv": 500_000,
    "integrity_summary.csv": 250_000,
    "anchor_spectra.csv": 8_000_000,
    "state_checkpoints.npz": 25_000_000,
    "stage_e_summary.json": 500_000,
    "file_inventory.csv": 100_000,
}

FORCING_TERMS = (
    "sin(2X)cos(2Y)",
    "0.75*sin(3X)cos(Y)",
    "0.50*sin(X)cos(4Y)",
    "0.35*cos(4X-2Y)",
)


# ============================================================================
# Output schemas
# ============================================================================

CASE_DIAGNOSTIC_FIELDNAMES = (
    "case_id", "N", "dt", "step", "physical_time", "is_initial",
    "trajectory_id", "operator_family", "mean_vorticity", "energy",
    "enstrophy", "vorticity_rms", "mean_free_vorticity_rms", "velocity_rms",
    "energy_injection", "enstrophy_injection", "viscous_energy_dissipation",
    "viscous_enstrophy_dissipation", "advection_enstrophy_work",
    "rk2_remainder", "mask_enstrophy_change", "normalized_filtered_closure",
    "dominant_shell", "low_k_fraction", "tail_fraction", "high_k_fraction",
    "maximum_imaginary_ratio", "maximum_speed", "cfl", "state_sha256",
    "finite_status",
)

WITHIN_PAIRWISE_FIELDNAMES = (
    "case_id", "N", "dt", "step", "physical_time", "trajectory_a",
    "trajectory_b", "absolute_vorticity_rms_difference",
    "normalized_vorticity_rms_difference",
    "absolute_mean_free_vorticity_rms_difference",
    "normalized_mean_free_vorticity_rms_difference", "mean_vorticity_difference",
    "normalized_velocity_difference", "vorticity_cosine_similarity",
    "energy_relative_difference", "enstrophy_relative_difference",
    "dominant_shell_difference", "low_k_fraction_difference",
    "tail_fraction_difference", "high_k_fraction_difference", "finite_status",
)

REFINEMENT_FIELDNAMES = (
    "axis", "adjacency_index", "coarse_case_id", "fine_case_id",
    "trajectory_id", "anchor_index", "anchor_time", "increment_role",
    "coarse_N", "fine_N", "coarse_dt", "fine_dt", "comparison_grid_N",
    "comparison_representation", "absolute_vorticity_rms_difference",
    "normalized_vorticity_rms_difference",
    "absolute_mean_free_vorticity_rms_difference",
    "normalized_mean_free_vorticity_rms_difference", "mean_vorticity_difference",
    "normalized_velocity_difference", "vorticity_cosine_similarity",
    "energy_relative_difference", "enstrophy_relative_difference",
    "dominant_shell_difference", "low_k_fraction_difference",
    "tail_fraction_difference", "high_k_fraction_difference",
    "discarded_band_applicable",
    "coarse_discarded_band_energy", "fine_discarded_band_energy",
    "coarse_discarded_band_enstrophy", "fine_discarded_band_enstrophy",
    "coarse_error_for_order", "fine_error_for_order", "refinement_ratio",
    "observed_order", "order_reportable", "order_eligible",
    "roundtrip_floor", "restriction_imaginary_floor", "absolute_guard_floor",
    "numerical_floor", "comparison_error_to_floor_ratio",
    "numerical_floor_status", "finite_status",
)

PROJECTION_CONTROL_FIELDNAMES = (
    "case_id", "N", "dt", "anchor_time", "control_id", "trajectory_id",
    "comparison_type", "preview_performed", "normalized_transport_difference",
    "normalized_accepted_update_difference", "selected_control_defect",
    "smallest_noncontrol_operator_separation", "absolute_limit",
    "relative_fraction_limit", "absolute_limit_pass",
    "relative_limit_applicable", "control_to_operator_separation_ratio",
    "relative_limit_pass", "transport_limit_pass",
    "accepted_update_limit_pass", "transport_status",
    "accepted_update_status", "descriptively_negligible",
    "maximum_imaginary_ratio", "finite_status",
)

INTEGRITY_SUMMARY_FIELDNAMES = (
    "case_id", "N", "dt", "trajectory_id", "expected_updates",
    "accepted_updates", "state_ownership_check_count", "failure_count",
    "finite_failure_count", "unfiltered_closure_failure_count",
    "filtered_closure_failure_count", "mask_crosscheck_failure_count",
    "imaginary_ratio_failure_count", "physical_loss_sign_failure_count",
    "spectral_loss_sign_failure_count",
    "corrected_mask_change_sign_failure_count", "state_mutation_count",
    "state_alias_count", "forcing_mutation_count",
    "wavenumber_mutation_count", "maximum_normalized_unfiltered_closure",
    "maximum_normalized_filtered_closure", "maximum_normalized_mask_crosscheck",
    "maximum_normalized_filter_bookkeeping", "maximum_imaginary_ratio",
    "minimum_mask_loss_physical", "minimum_mask_loss_spectral",
    "maximum_corrected_mask_enstrophy_change", "maximum_cfl",
    "solver_environment_unchanged", "forcing_unchanged",
    "local_wavenumbers_unchanged", "all_updates_finite", "integrity_pass",
)

ANCHOR_SPECTRA_FIELDNAMES = (
    "case_id", "N", "dt", "anchor_time", "trajectory_id", "shell",
    "shell_energy", "mode_count", "dealiased_mode_count", "finite_status",
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
        case_id: str | None = None,
        trajectory_id: str | None = None,
        step: int | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.gate = gate
        self.case_id = case_id
        self.trajectory_id = trajectory_id
        self.step = step
        self.details = dict(details or {})


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def utc_text(value: datetime.datetime | None = None) -> str:
    return (value or utc_now()).isoformat(timespec="seconds")


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


def field_rms(value: object) -> float:
    array = np.asarray(value)
    return float(np.sqrt(np.mean(np.abs(array) ** 2)))


def mean_free(value: object) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    return array - float(np.mean(array))


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


def finite_float(name: str, value: object) -> float:
    selected = float(value)
    if not math.isfinite(selected):
        raise IntegrityFailure("nonfinite_scalar", f"{name} is nonfinite: {selected}")
    return selected


def json_safe(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        selected = float(value)
        if math.isnan(selected):
            return "NaN"
        if math.isinf(selected):
            return "+Infinity" if selected > 0.0 else "-Infinity"
        return selected
    if value is None or isinstance(value, str):
        return value
    return str(value)


def atomic_write_text(path: Path, value: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_json(path: Path, value: object) -> None:
    atomic_write_text(
        path,
        json.dumps(json_safe(value), indent=2, sort_keys=True, allow_nan=False) + "\n",
    )


def assert_unique_headers(name: str, headers: Sequence[str]) -> None:
    values = tuple(headers)
    duplicates = sorted({field for field in values if values.count(field) > 1})
    if duplicates:
        raise RuntimeError(f"duplicate headers in {name}: {duplicates}")


def assert_all_headers_unique() -> None:
    for name, headers in (
        ("case_diagnostics.csv", CASE_DIAGNOSTIC_FIELDNAMES),
        ("within_case_pairwise.csv", WITHIN_PAIRWISE_FIELDNAMES),
        ("refinement_comparisons.csv", REFINEMENT_FIELDNAMES),
        ("projection_controls.csv", PROJECTION_CONTROL_FIELDNAMES),
        ("integrity_summary.csv", INTEGRITY_SUMMARY_FIELDNAMES),
        ("anchor_spectra.csv", ANCHOR_SPECTRA_FIELDNAMES),
        ("file_inventory.csv", INVENTORY_FIELDNAMES),
    ):
        assert_unique_headers(name, headers)


class IncrementalCsvWriter:
    def __init__(self, path: Path, fieldnames: Sequence[str]) -> None:
        self.path = path
        self.fieldnames = tuple(fieldnames)
        assert_unique_headers(path.name, self.fieldnames)
        self.handle = path.open("w", encoding="utf-8", newline="")
        self.writer = csv.DictWriter(
            self.handle,
            fieldnames=self.fieldnames,
            extrasaction="raise",
            lineterminator="\n",
        )
        self.writer.writeheader()

    def write(self, row: Mapping[str, object]) -> None:
        if set(row) != set(self.fieldnames):
            missing = sorted(set(self.fieldnames) - set(row))
            extra = sorted(set(row) - set(self.fieldnames))
            raise RuntimeError(
                f"CSV row mismatch for {self.path.name}: missing={missing}, extra={extra}"
            )
        self.writer.writerow(dict(row))

    def flush(self) -> None:
        self.handle.flush()
        os.fsync(self.handle.fileno())

    def close(self) -> None:
        if not self.handle.closed:
            self.flush()
            self.handle.close()


def git_process(
    repo: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
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
    observed = git_read(repo, "rev-parse", f"{AUTHORIZED_DESIGN_COMMIT}^{{commit}}")
    if observed != AUTHORIZED_DESIGN_COMMIT:
        raise RuntimeError(
            f"design commit resolved to {observed}, expected={AUTHORIZED_DESIGN_COMMIT}"
        )
    return observed


def verify_file_hash(repo: Path, path: Path, expected: str) -> str:
    selected = repo / path
    if not selected.is_file():
        raise RuntimeError(f"required file is missing: {path.as_posix()}")
    observed = sha256_file(selected)
    if observed != expected:
        raise RuntimeError(
            f"SHA256 mismatch for {path.as_posix()}: observed={observed}, expected={expected}"
        )
    return observed


def verify_git_blob(repo: Path, path: Path, expected: str) -> str:
    relative = path.as_posix()
    working = git_read(repo, "hash-object", f"--path={relative}", "--", relative)
    committed = git_read(repo, "rev-parse", f"HEAD:{relative}")
    if working != expected or committed != expected:
        raise RuntimeError(
            f"Git blob mismatch for {relative}: working={working}, "
            f"committed={committed}, expected={expected}"
        )
    return working


def verify_frozen_sources(repo: Path) -> dict[str, str]:
    return {
        "design": verify_file_hash(repo, DESIGN_PATH, EXPECTED_DESIGN_SHA256),
        "stage_d1r_runner": verify_file_hash(
            repo, STAGE_D1R_RUNNER_PATH, EXPECTED_STAGE_D1R_RUNNER_SHA256
        ),
        "stage_d1r_completion_report": verify_file_hash(
            repo,
            STAGE_D1R_COMPLETION_REPORT_PATH,
            EXPECTED_STAGE_D1R_COMPLETION_REPORT_SHA256,
        ),
        "spectral_solver_blob": verify_git_blob(
            repo, SPECTRAL_SOLVER_PATH, EXPECTED_SPECTRAL_SOLVER_BLOB
        ),
        "advection_operators_blob": verify_git_blob(
            repo, ADVECTION_OPERATORS_PATH, EXPECTED_ADVECTION_OPERATORS_BLOB
        ),
        "forcing_budget_sha256": verify_file_hash(
            repo, FORCING_BUDGET_PATH, EXPECTED_FORCING_BUDGET_SHA256
        ),
        "forcing_budget_blob": verify_git_blob(
            repo, FORCING_BUDGET_PATH, EXPECTED_FORCING_BUDGET_BLOB
        ),
    }


def verify_stage_d1r_evidence(repo: Path) -> dict[str, str]:
    directory = repo / STAGE_D1R_EVIDENCE_DIRECTORY
    if not directory.is_dir():
        raise RuntimeError(f"Stage D1R evidence directory is missing: {directory}")
    observed_names = sorted(path.name for path in directory.iterdir() if path.is_file())
    expected_names = sorted(STAGE_D1R_EVIDENCE_HASHES)
    if observed_names != expected_names:
        raise RuntimeError(
            f"Stage D1R evidence file set mismatch: observed={observed_names}"
        )
    observed: dict[str, str] = {}
    for name, expected in STAGE_D1R_EVIDENCE_HASHES.items():
        actual = sha256_file(directory / name)
        if actual != expected:
            raise RuntimeError(
                f"Stage D1R evidence hash mismatch for {name}: {actual}"
            )
        observed[name] = actual
    return observed


def parse_archived_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise RuntimeError(f"invalid archived boolean: {value!r}")


def load_d1r_diagnostic_rows(
    repo: Path,
) -> dict[tuple[int, str], dict[str, str]]:
    path = (
        repo
        / STAGE_D1R_EVIDENCE_DIRECTORY
        / "trajectory_pilot_diagnostics.csv"
    )
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != D1R_DIAGNOSTIC_FIELDNAMES:
            raise RuntimeError(
                "archived D1R diagnostic header differs from the frozen schema"
            )
        all_rows = list(reader)
    if len(all_rows) != 2_149:
        raise RuntimeError(f"archived D1R diagnostic rows={len(all_rows)}, expected=2149")
    selected: dict[tuple[int, str], dict[str, str]] = {}
    permitted_steps = set(D1R_SAMPLE_COMPLETED_STEPS)
    permitted_ids = set(TRAJECTORY_IDS)
    for row in all_rows:
        step = int(row["completed_steps"])
        trajectory_id = row["trajectory_id"]
        if step not in permitted_steps or trajectory_id not in permitted_ids:
            continue
        key = (step, trajectory_id)
        if key in selected:
            raise RuntimeError(f"duplicate archived D1R diagnostic key: {key}")
        if not parse_archived_bool(row["finite_status"]):
            raise RuntimeError(f"archived D1R diagnostic is nonfinite: {key}")
        selected[key] = row
    expected_keys = {
        (step, trajectory_id)
        for step in D1R_SAMPLE_COMPLETED_STEPS
        for trajectory_id in TRAJECTORY_IDS
    }
    if set(selected) != expected_keys or len(selected) != D1R_PRIMARY_EXPECTED_ROWS:
        missing = sorted(expected_keys - set(selected))
        raise RuntimeError(
            f"D1R retained diagnostic key mismatch: rows={len(selected)}, "
            f"missing={missing[:5]}"
        )
    return selected


def archived_scalar_comparison(
    observed: float, archived: float
) -> tuple[float, float, bool]:
    absolute = abs(observed - archived)
    scale = max(abs(observed), abs(archived), BASELINE_ARCHIVE_ABSOLUTE_FLOOR)
    relative = absolute / scale
    passed = (
        absolute <= BASELINE_ARCHIVE_ABSOLUTE_FLOOR
        or relative <= BASELINE_ARCHIVE_RELATIVE_TOLERANCE
    )
    return absolute, relative, passed


def compare_d1r_diagnostic_row(
    observed: Mapping[str, object], archived: Mapping[str, str]
) -> dict[str, object]:
    failures: list[str] = []
    maximum_absolute = 0.0
    maximum_relative = 0.0
    for name in D1R_INTEGER_FIELDS:
        if int(observed[name]) != int(archived[name]):
            failures.append(name)
    for name in D1R_STRING_FIELDS:
        if str(observed[name]) != archived[name]:
            failures.append(name)
    for name in D1R_FLOAT_FIELDS:
        absolute, relative, passed = archived_scalar_comparison(
            float(observed[name]), float(archived[name])
        )
        maximum_absolute = max(maximum_absolute, absolute)
        maximum_relative = max(maximum_relative, relative)
        if not passed:
            failures.append(name)
    if bool(observed["finite_status"]) != parse_archived_bool(
        archived["finite_status"]
    ):
        failures.append("finite_status")
    if str(observed["accepted_state_sha256"]) != archived[
        "accepted_state_sha256"
    ]:
        failures.append("accepted_state_sha256")
    return {
        "passed": not failures,
        "failed_fields": failures,
        "maximum_absolute_difference": maximum_absolute,
        "maximum_relative_difference": maximum_relative,
    }


def path_is_ignored(repo: Path, path: Path) -> bool:
    relative = path.relative_to(repo).as_posix()
    return git_process(repo, "check-ignore", "-q", "--", relative, check=False).returncode == 0


def verify_inspection_repository_state(repo: Path) -> str:
    branch = git_read(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"active branch={branch!r}, expected={EXPECTED_BRANCH!r}")
    design_commit = resolve_design_commit(repo)
    head = git_read(repo, "rev-parse", "HEAD")
    if head != design_commit:
        raise RuntimeError(f"HEAD={head}, expected design commit={design_commit}")
    status = [
        line
        for line in git_read(
            repo, "status", "--porcelain=v1", "--untracked-files=all"
        ).splitlines()
        if line
    ]
    expected = [f"?? {RUNNER_NAME}"]
    if status != expected:
        raise RuntimeError(
            f"inspection requires exactly one untracked runner: observed={status!r}"
        )
    return design_commit


def verify_run_preflight(
    repo: Path,
) -> tuple[str, dict[str, str], dict[str, str]]:
    branch = git_read(repo, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"active branch={branch!r}, expected={EXPECTED_BRANCH!r}")
    status = git_read(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise RuntimeError(f"working tree is not clean: {status!r}")
    design_commit = resolve_design_commit(repo)
    head = git_read(repo, "rev-parse", "HEAD")
    parent = git_read(repo, "rev-parse", "HEAD^")
    if parent != design_commit:
        raise RuntimeError(f"runner parent={parent}, expected design={design_commit}")
    changed = [
        line
        for line in git_read(
            repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"
        ).splitlines()
        if line
    ]
    if changed != [RUNNER_NAME]:
        raise RuntimeError(f"runner commit changed unexpected files: {changed!r}")
    runner = repo / RUNNER_NAME
    if git_bytes(repo, "show", f"HEAD:{RUNNER_NAME}") != runner.read_bytes():
        raise RuntimeError("working runner differs from committed runner")
    source_hashes = verify_frozen_sources(repo)
    evidence_hashes = verify_stage_d1r_evidence(repo)
    if (repo / OUTPUT_ROOT).exists():
        prior = sorted(
            path.name
            for path in (repo / OUTPUT_ROOT).iterdir()
            if path.is_dir() and path.name.startswith(RUN_PREFIX)
        ) if (repo / OUTPUT_ROOT).is_dir() else []
        if prior:
            raise RuntimeError(f"prior Stage E output exists: {prior}")
    probe = repo / OUTPUT_ROOT / (RUN_PREFIX + "ignore_probe")
    if not path_is_ignored(repo, probe):
        raise RuntimeError(f"output path is not Git-ignored: {probe.relative_to(repo)}")
    if tuple(sorted(PREDICTED_OUTPUT_FILE_BYTES)) != tuple(sorted(OUTPUT_FILENAMES)):
        raise RuntimeError("predicted output file set differs from output contract")
    oversized = {
        name: size
        for name, size in PREDICTED_OUTPUT_FILE_BYTES.items()
        if size >= MAX_OUTPUT_FILE_BYTES
    }
    if oversized:
        raise RuntimeError(f"predicted output exceeds 40 MB: {oversized}")
    return head, source_hashes, evidence_hashes


# ============================================================================
# Case construction and numerical kernels
# ============================================================================

def case_sample_steps(case: Mapping[str, object]) -> tuple[int, ...]:
    dt = float(case["dt"])
    updates = int(case["updates"])
    steps = tuple(int(round(time_value / dt)) for time_value in COMMON_SAMPLE_TIMES)
    if len(steps) != 307 or steps[0] != 0 or steps[-1] != updates:
        raise RuntimeError(f"invalid common sample schedule for {case['case_id']}")
    for step, time_value in zip(steps, COMMON_SAMPLE_TIMES, strict=True):
        if not math.isclose(step * dt, time_value, rel_tol=0.0, abs_tol=2.0e-14):
            raise RuntimeError(f"sample time is not representable for {case['case_id']}")
    return steps


def case_anchor_steps(case: Mapping[str, object]) -> tuple[int, ...]:
    dt = float(case["dt"])
    steps = tuple(int(round(time_value / dt)) for time_value in ANCHOR_TIMES)
    for step, time_value in zip(steps, ANCHOR_TIMES, strict=True):
        if not math.isclose(step * dt, time_value, rel_tol=0.0, abs_tol=2.0e-14):
            raise RuntimeError(f"anchor time is not representable for {case['case_id']}")
    return steps


def validate_frozen_matrix() -> None:
    if len(CASE_REGISTRY) != 5 or len(TRAJECTORY_REGISTRY) != 5:
        raise RuntimeError("Stage E requires exactly five cases and five trajectories")
    if len(PRIMARY_PAIRS) != 10 or len(PROJECTION_CONTROLS) != 2:
        raise RuntimeError("pair or projection-control registry is inconsistent")
    observed_updates = sum(
        int(case["updates"]) * len(TRAJECTORY_IDS) for case in CASE_REGISTRY
    )
    if observed_updates != EXPECTED_PRIMARY_UPDATES:
        raise RuntimeError(
            f"primary update count={observed_updates}, expected={EXPECTED_PRIMARY_UPDATES}"
        )
    for case in CASE_REGISTRY:
        n = int(case["N"])
        dt = float(case["dt"])
        updates = int(case["updates"])
        if n % 2 or n < 4:
            raise RuntimeError(f"case grid must be even: {case}")
        if not math.isclose(updates * dt, FINAL_TIME, rel_tol=0.0, abs_tol=2.0e-14):
            raise RuntimeError(f"case final time is inconsistent: {case}")
        case_sample_steps(case)
        case_anchor_steps(case)


def build_rms_matched_multimode_forcing(
    solver: object, case_id: str
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
        forcing_rms,
        FORCING_TARGET_RMS,
        rel_tol=0.0,
        abs_tol=FORCING_RMS_TOLERANCE,
    ):
        raise IntegrityFailure(
            "forcing_rms",
            f"forcing RMS={forcing_rms}, expected={FORCING_TARGET_RMS}",
            case_id=case_id,
        )
    if case_id == "C0_N64_DT00500" and forcing_hash != EXPECTED_C0_FORCING_SHA256:
        raise IntegrityFailure(
            "forcing_sha256",
            f"C0 forcing SHA256={forcing_hash}",
            case_id=case_id,
        )
    if forcing.shape != (int(solver.N), int(solver.N)):
        raise IntegrityFailure("forcing_shape", "forcing shape mismatch", case_id=case_id)
    if not np.isfinite(forcing).all() or not np.isrealobj(forcing):
        raise IntegrityFailure("forcing_finite", "forcing is not finite real", case_id=case_id)
    forcing.setflags(write=False)
    normalized_hat = np.fft.fft2(forcing) / float(int(solver.N) ** 2)
    nonzero_modes = []
    k_values = np.rint(np.asarray(solver.k)).astype(int)
    for iy, ky in enumerate(k_values):
        for ix, kx in enumerate(k_values):
            value = complex(normalized_hat[iy, ix])
            if abs(value) > 1.0e-14:
                nonzero_modes.append(
                    {"kx": int(kx), "ky": int(ky), "real": value.real, "imag": value.imag}
                )
    return forcing, {
        "case_id": case_id,
        "forcing_sha256": forcing_hash,
        "forcing_terms": list(FORCING_TERMS),
        "target_rms": FORCING_TARGET_RMS,
        "normalized_rms": forcing_rms,
        "mean": float(np.mean(forcing)),
        "normalization_coefficient": coefficient,
        "shape": list(forcing.shape),
        "dtype": str(forcing.dtype),
        "writeable": bool(forcing.flags.writeable),
        "normalized_nonzero_fourier_modes": nonzero_modes,
    }


def freeze_solver_environment(solver: object) -> dict[str, str]:
    identities: dict[str, str] = {}
    for name in ("x", "X", "Y", "k", "kx", "ky", "k2", "deal", "w"):
        value = np.asarray(getattr(solver, name))
        value.setflags(write=False)
        identities[name] = sha256_array(value)
    identities["N"] = sha256_bytes(str(int(solver.N)).encode("utf-8"))
    identities["dt"] = sha256_bytes(repr(float(solver.dt)).encode("utf-8"))
    identities["nu"] = sha256_bytes(repr(float(solver.nu)).encode("utf-8"))
    identities["dx"] = sha256_bytes(repr(float(solver.dx)).encode("utf-8"))
    return identities


def initialize_trajectory_states(initial: object) -> dict[str, np.ndarray]:
    source = np.asarray(initial, dtype=np.float64)
    states: dict[str, np.ndarray] = {}
    for trajectory_id in TRAJECTORY_IDS:
        state = np.array(source, dtype=np.float64, copy=True, order="C")
        state.setflags(write=False)
        states[trajectory_id] = state
    return states


def state_alias_count(
    states: Mapping[str, np.ndarray],
    forcing: np.ndarray,
    kx_rc: np.ndarray,
    ky_rc: np.ndarray,
) -> int:
    arrays = [np.asarray(states[key]) for key in TRAJECTORY_IDS]
    auxiliary = (np.asarray(forcing), np.asarray(kx_rc), np.asarray(ky_rc))
    count = 0
    for first_index, first in enumerate(arrays):
        if first.flags.writeable or not first.flags.c_contiguous:
            count += 1
        for second in arrays[first_index + 1:]:
            count += int(np.shares_memory(first, second))
        for other in auxiliary:
            count += int(np.shares_memory(first, other))
    return count


def preview_alias_count(
    states: Mapping[str, np.ndarray],
    previews: Mapping[str, Mapping[str, object]],
    forcing: np.ndarray,
    kx_rc: np.ndarray,
    ky_rc: np.ndarray,
) -> int:
    arrays: list[np.ndarray] = []
    for trajectory_id in TRAJECTORY_IDS:
        preview = previews[trajectory_id]
        arrays.extend(
            [
                np.asarray(preview["stage"]),
                np.asarray(preview["accepted"]),
            ]
        )
    protected = [
        *(np.asarray(states[key]) for key in TRAJECTORY_IDS),
        np.asarray(forcing), np.asarray(kx_rc), np.asarray(ky_rc),
    ]
    count = 0
    for first_index, first in enumerate(arrays):
        for second in arrays[first_index + 1:]:
            count += int(np.shares_memory(first, second))
        for other in protected:
            count += int(np.shares_memory(first, other))
    return count


def accept_independent_previews(
    previews: Mapping[str, Mapping[str, object]]
) -> dict[str, np.ndarray]:
    accepted: dict[str, np.ndarray] = {}
    for trajectory_id in TRAJECTORY_IDS:
        value = np.array(
            previews[trajectory_id]["accepted"],
            dtype=np.float64,
            copy=True,
            order="C",
        )
        value.setflags(write=False)
        accepted[trajectory_id] = value
    return accepted


def build_real_compatible_wavenumbers(
    solver: object, case_id: str
) -> tuple[np.ndarray, np.ndarray]:
    n = int(solver.N)
    solver_kx = np.asarray(solver.kx)
    solver_ky = np.asarray(solver.ky)
    nyquist = -n / 2
    x_mask = np.asarray(solver_kx == nyquist)
    y_mask = np.asarray(solver_ky == nyquist)
    if not x_mask.any() or not y_mask.any():
        raise IntegrityFailure(
            "nyquist_location", "derived Nyquist mode is absent", case_id=case_id
        )
    kx_rc = np.array(solver_kx, dtype=np.float64, copy=True)
    ky_rc = np.array(solver_ky, dtype=np.float64, copy=True)
    kx_rc[x_mask] = 0.0
    ky_rc[y_mask] = 0.0
    if np.shares_memory(kx_rc, solver_kx) or np.shares_memory(ky_rc, solver_ky):
        raise IntegrityFailure(
            "wavenumber_alias", "real-compatible wavenumbers alias solver arrays",
            case_id=case_id,
        )
    kx_rc.setflags(write=False)
    ky_rc.setflags(write=False)
    return kx_rc, ky_rc


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
    field: object, kx_rc: np.ndarray, ky_rc: np.ndarray
) -> tuple[np.ndarray, np.ndarray, float]:
    array = np.asarray(field, dtype=np.float64)
    field_hat = np.fft.fft2(array)
    x_complex = np.fft.ifft2(1j * kx_rc * field_hat)
    y_complex = np.fft.ifft2(1j * ky_rc * field_hat)
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
    return np.ascontiguousarray(projected_complex.real, dtype=np.float64), ratio


def compute_transport(
    operator_kind: str,
    solver: object,
    state: np.ndarray,
    psi: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    *,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_rc: np.ndarray,
    ky_rc: np.ndarray,
    case_id: str,
    trajectory_id: str,
    step: int,
) -> dict[str, object]:
    state_array = np.asarray(state, dtype=np.float64)
    imaginary_ratio = 0.0
    if operator_kind in ("fd_advective", "fd_advective_projected", "fd_skew"):
        omega_x, omega_y = centered_gradients(state_array, float(solver.dx))
        advective = u * omega_x + v * omega_y
    if operator_kind in ("fd_conservative", "fd_skew"):
        conservative = (
            centered_gradients(u * state_array, float(solver.dx))[0]
            + centered_gradients(v * state_array, float(solver.dx))[1]
        )

    if operator_kind == "fd_advective":
        transport = advective
    elif operator_kind == "fd_advective_projected":
        transport, imaginary_ratio = project_field(advective, np.asarray(solver.deal))
    elif operator_kind == "fd_conservative":
        transport = conservative
    elif operator_kind == "fd_skew":
        transport = 0.5 * (advective + conservative)
    elif operator_kind in (
        "ps_advective_rc_unprojected", "ps_advective_rc_projected"
    ):
        omega_x, omega_y, derivative_imaginary = spectral_gradients_real_compatible(
            state_array, kx_rc, ky_rc
        )
        raw = u * omega_x + v * omega_y
        imaginary_ratio = derivative_imaginary
        if operator_kind == "ps_advective_rc_unprojected":
            transport = raw
        else:
            transport, projection_imaginary = project_field(raw, np.asarray(solver.deal))
            imaginary_ratio = max(imaginary_ratio, projection_imaginary)
    elif operator_kind == "arakawa":
        jacobian = np.asarray(
            jacobian_arakawa_periodic(psi, state_array, float(solver.dx)),
            dtype=np.float64,
        )
        transport = -jacobian
    else:
        raise KeyError(operator_kind)

    output = np.ascontiguousarray(transport, dtype=np.float64)
    expected_shape = (int(solver.N), int(solver.N))
    if output.shape != expected_shape or not np.isfinite(output).all():
        raise IntegrityFailure(
            "operator_output",
            f"invalid operator output for {operator_kind}",
            case_id=case_id,
            trajectory_id=trajectory_id,
            step=step,
        )
    if operator_kind.startswith("ps_") and imaginary_ratio > IMAGINARY_RATIO_LIMIT:
        raise IntegrityFailure(
            "real_compatible_imaginary_ratio",
            f"imaginary ratio={imaginary_ratio}",
            case_id=case_id,
            trajectory_id=trajectory_id,
            step=step,
        )
    output.setflags(write=False)
    return {
        "transport": output,
        "advection_rhs": -output,
        "maximum_imaginary_ratio": float(imaginary_ratio),
    }


def rk2_preview(
    operator_kind: str,
    solver: object,
    current_state: np.ndarray,
    forcing: np.ndarray,
    *,
    step: int,
    case_id: str,
    trajectory_id: str,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_rc: np.ndarray,
    ky_rc: np.ndarray,
) -> dict[str, object]:
    current = np.asarray(current_state, dtype=np.float64)
    current_hash = sha256_array(current)
    expected_shape = (int(solver.N), int(solver.N))
    if current.shape != expected_shape or not np.isfinite(current).all():
        raise IntegrityFailure(
            "current_state", "invalid current state", case_id=case_id,
            trajectory_id=trajectory_id, step=step,
        )
    if current.flags.writeable:
        raise IntegrityFailure(
            "current_state_writeable", "current state is unexpectedly writeable",
            case_id=case_id, trajectory_id=trajectory_id, step=step,
        )

    psi_1 = solver.streamfunction(current)
    u_1, v_1 = solver.velocity(psi_1)
    operator_1 = compute_transport(
        operator_kind, solver, current, psi_1, u_1, v_1,
        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
        kx_rc=kx_rc, ky_rc=ky_rc, case_id=case_id,
        trajectory_id=trajectory_id, step=step,
    )
    advection_1 = np.asarray(operator_1["advection_rhs"])
    viscous_1 = solver.laplacian_spectral(current)
    total_1 = advection_1 + viscous_1 + forcing
    stage_state = np.ascontiguousarray(current + solver.dt * total_1, dtype=np.float64)

    psi_2 = solver.streamfunction(stage_state)
    u_2, v_2 = solver.velocity(psi_2)
    operator_2 = compute_transport(
        operator_kind, solver, stage_state, psi_2, u_2, v_2,
        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
        kx_rc=kx_rc, ky_rc=ky_rc, case_id=case_id,
        trajectory_id=trajectory_id, step=step,
    )
    advection_2 = np.asarray(operator_2["advection_rhs"])
    viscous_2 = solver.laplacian_spectral(stage_state)
    total_2 = advection_2 + viscous_2 + forcing
    unfiltered = np.ascontiguousarray(
        current + 0.5 * solver.dt * (total_1 + total_2), dtype=np.float64
    )
    unfiltered_hat = np.fft.fft2(unfiltered)
    filtered_complex = np.fft.ifft2(unfiltered_hat * solver.deal)
    accepted = np.ascontiguousarray(filtered_complex.real, dtype=np.float64)

    z_current = enstrophy(current)
    z_stage = enstrophy(stage_state)
    z_unfiltered = enstrophy(unfiltered)
    z_filtered = enstrophy(accepted)
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
    rk2_remainder = solver.dt / 8.0 * float(np.mean(total_difference * total_difference))

    observed_unfiltered_rate = (z_unfiltered - z_current) / solver.dt
    observed_filtered_rate = (z_filtered - z_current) / solver.dt
    observed_mask_change_rate = (z_filtered - z_unfiltered) / solver.dt
    discarded_hat = np.where(solver.deal, 0.0, unfiltered_hat)
    removed_physical_complex = np.fft.ifft2(discarded_hat)
    mask_loss_physical = 0.5 * float(np.mean(np.abs(removed_physical_complex) ** 2))
    n = int(solver.N)
    mask_loss_spectral = float(
        np.sum(np.abs(discarded_hat) ** 2) / (2.0 * float(n ** 4))
    )
    mask_change = -mask_loss_physical / solver.dt
    filter_bookkeeping = observed_mask_change_rate - mask_change
    unfiltered_rhs = rk2_advection + rk2_viscous + rk2_forcing + rk2_remainder
    filtered_rhs = unfiltered_rhs + mask_change
    unfiltered_closure = observed_unfiltered_rate - unfiltered_rhs
    filtered_closure = observed_filtered_rate - filtered_rhs
    unfiltered_scale = max(
        abs(observed_unfiltered_rate), abs(rk2_advection), abs(rk2_viscous),
        abs(rk2_forcing), abs(rk2_remainder), RESIDUAL_FLOOR,
    )
    filtered_scale = max(
        abs(observed_filtered_rate), abs(rk2_advection), abs(rk2_viscous),
        abs(rk2_forcing), abs(rk2_remainder), abs(mask_change), RESIDUAL_FLOOR,
    )
    normalized_unfiltered = abs(unfiltered_closure) / unfiltered_scale
    normalized_filtered = abs(filtered_closure) / filtered_scale
    normalized_filter_bookkeeping = abs(filter_bookkeeping) / filtered_scale
    mask_residual = mask_loss_physical - mask_loss_spectral
    normalized_mask = abs(mask_residual) / max(
        abs(mask_loss_physical), abs(mask_loss_spectral), RESIDUAL_FLOOR
    )
    filtered_imaginary = field_rms(filtered_complex.imag) / max(
        field_rms(filtered_complex.real), RESIDUAL_FLOOR
    )
    maximum_imaginary = max(
        float(operator_1["maximum_imaginary_ratio"]),
        float(operator_2["maximum_imaginary_ratio"]),
        filtered_imaginary,
    )
    maximum_speed = float(np.max(np.sqrt(u_1 * u_1 + v_1 * v_1)))
    cfl = maximum_speed * float(solver.dt) / float(solver.dx)

    arrays = (stage_state, unfiltered, accepted, total_1, total_2)
    scalars = (
        normalized_unfiltered, normalized_filtered, normalized_mask,
        normalized_filter_bookkeeping, maximum_imaginary, mask_loss_physical,
        mask_loss_spectral, mask_change, cfl,
    )
    update_finite = all(np.isfinite(value).all() for value in arrays) and all(
        math.isfinite(float(value)) for value in scalars
    )
    failures = []
    if not update_finite:
        failures.append("update_finite")
    if normalized_unfiltered > UNFILTERED_LEDGER_CLOSURE_LIMIT:
        failures.append("unfiltered_ledger_closure")
    if normalized_filtered > FILTERED_LEDGER_CLOSURE_LIMIT:
        failures.append("filtered_ledger_closure")
    if normalized_mask > MASK_CROSSCHECK_LIMIT:
        failures.append("mask_parseval_crosscheck")
    if maximum_imaginary > IMAGINARY_RATIO_LIMIT:
        failures.append("real_compatible_imaginary_ratio")
    if mask_loss_physical < 0.0:
        failures.append("physical_loss_sign")
    if mask_loss_spectral < 0.0:
        failures.append("spectral_loss_sign")
    if mask_change > 0.0:
        failures.append("corrected_mask_change_sign")
    if sha256_array(current) != current_hash:
        failures.append("state_mutation")
    if np.shares_memory(stage_state, current) or np.shares_memory(accepted, current):
        failures.append("state_alias")
    if np.shares_memory(accepted, stage_state):
        failures.append("stage_accepted_alias")
    if failures:
        details = {
            "failures": failures,
            "normalized_unfiltered_closure": normalized_unfiltered,
            "normalized_filtered_closure": normalized_filtered,
            "normalized_mask_crosscheck": normalized_mask,
            "maximum_imaginary_ratio": maximum_imaginary,
            "mask_loss_physical": mask_loss_physical,
            "mask_loss_spectral": mask_loss_spectral,
            "mask_enstrophy_change_rate": mask_change,
            "state_hashes": {
                "current": sha256_array(current),
                "stage": sha256_array(stage_state),
                "accepted": sha256_array(accepted),
            },
        }
        raise IntegrityFailure(
            failures[0], "RK2 integrity gate failed", case_id=case_id,
            trajectory_id=trajectory_id, step=step, details=details,
        )

    stage_state.setflags(write=False)
    accepted.setflags(write=False)
    return {
        "step": step,
        "current": current,
        "stage": stage_state,
        "accepted": accepted,
        "rk2_advection_rate": rk2_advection,
        "rk2_viscous_rate": rk2_viscous,
        "rk2_forcing_rate": rk2_forcing,
        "rk2_quadratic_remainder_rate": rk2_remainder,
        "mask_enstrophy_change_rate": mask_change,
        "normalized_unfiltered_closure": normalized_unfiltered,
        "normalized_filtered_closure": normalized_filtered,
        "normalized_mask_crosscheck": normalized_mask,
        "normalized_filter_bookkeeping": normalized_filter_bookkeeping,
        "maximum_imaginary_ratio": maximum_imaginary,
        "mask_loss_physical": mask_loss_physical,
        "mask_loss_spectral": mask_loss_spectral,
        "maximum_speed": maximum_speed,
        "cfl": cfl,
        "ledger_scalars": (
            rk2_advection, rk2_viscous, rk2_forcing, rk2_remainder,
            mask_change, observed_unfiltered_rate, observed_filtered_rate,
            unfiltered_closure, filtered_closure,
        ),
    }


# ============================================================================
# Diagnostics, controls, and cross-grid comparison
# ============================================================================

def spectrum_details(
    u: np.ndarray, v: np.ndarray, kx: np.ndarray, ky: np.ndarray
) -> dict[str, object]:
    n = int(u.shape[0])
    normalization = float(n * n) ** 2
    mode_energy = 0.5 * (
        np.abs(np.fft.fft2(u)) ** 2 + np.abs(np.fft.fft2(v)) ** 2
    ) / normalization
    shell_index = np.floor(np.sqrt(kx * kx + ky * ky)).astype(int)
    minlength = int(shell_index.max()) + 1
    shell_energy = np.bincount(
        shell_index.ravel(), weights=mode_energy.ravel(), minlength=minlength
    )
    mode_count = np.bincount(shell_index.ravel(), minlength=minlength)
    total = max(float(np.sum(shell_energy)), RESIDUAL_FLOOR)
    shell_numbers = np.arange(len(shell_energy))
    return {
        "dominant_shell": int(np.argmax(shell_energy)),
        "low_k_fraction": float(np.sum(shell_energy[shell_numbers <= 4])) / total,
        "tail_fraction": float(np.sum(shell_energy[shell_numbers > 4])) / total,
        "high_k_fraction": float(np.sum(shell_energy[shell_numbers >= 10])) / total,
        "shell_energy": shell_energy,
        "mode_count": mode_count,
    }


def build_diagnostic(
    case: Mapping[str, object],
    trajectory_id: str,
    state: np.ndarray,
    preview: Mapping[str, object] | None,
    solver: object,
    forcing: np.ndarray,
    *,
    step: int,
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
        loop_index=step - 1,
    )
    spectrum = spectrum_details(u, v, np.asarray(solver.kx), np.asarray(solver.ky))
    maximum_speed = float(np.max(np.sqrt(u * u + v * v)))
    cfl = maximum_speed * float(solver.dt) / float(solver.dx)
    if preview is None:
        advection_work = 0.0
        rk2_remainder = 0.0
        mask_change = 0.0
        filtered_closure = 0.0
        maximum_imaginary = 0.0
    else:
        advection_work = float(preview["rk2_advection_rate"])
        rk2_remainder = float(preview["rk2_quadratic_remainder_rate"])
        mask_change = float(preview["mask_enstrophy_change_rate"])
        filtered_closure = float(preview["normalized_filtered_closure"])
        maximum_imaginary = float(preview["maximum_imaginary_ratio"])
    state_array = np.asarray(state, dtype=np.float64)
    mean_value = float(np.mean(state_array))
    numeric_values = (
        mean_value,
        float(budget["energy"]),
        float(budget["enstrophy"]),
        field_rms(state_array),
        field_rms(mean_free(state_array)),
        float(np.sqrt(np.mean(u * u + v * v))),
        maximum_speed,
        cfl,
        advection_work,
        rk2_remainder,
        mask_change,
        filtered_closure,
        maximum_imaginary,
    )
    finite_status = bool(
        np.isfinite(state_array).all()
        and np.isfinite(u).all()
        and np.isfinite(v).all()
        and all(math.isfinite(value) for value in numeric_values)
    )
    if not finite_status:
        raise IntegrityFailure(
            "sample_diagnostic_finite",
            "sample diagnostic is nonfinite",
            case_id=str(case["case_id"]),
            trajectory_id=trajectory_id,
            step=step,
        )
    physical_time = step * float(case["dt"])
    metadata = TRAJECTORY_BY_ID[trajectory_id]
    row = {
        "case_id": case["case_id"],
        "N": case["N"],
        "dt": case["dt"],
        "step": step,
        "physical_time": physical_time,
        "is_initial": step == 0,
        "trajectory_id": trajectory_id,
        "operator_family": metadata["operator_family"],
        "mean_vorticity": mean_value,
        "energy": budget["energy"],
        "enstrophy": budget["enstrophy"],
        "vorticity_rms": field_rms(state_array),
        "mean_free_vorticity_rms": field_rms(mean_free(state_array)),
        "velocity_rms": float(np.sqrt(np.mean(u * u + v * v))),
        "energy_injection": budget["energy_injection_rate"],
        "enstrophy_injection": budget["enstrophy_injection_rate"],
        "viscous_energy_dissipation": budget["viscous_energy_dissipation_rate"],
        "viscous_enstrophy_dissipation": budget["viscous_enstrophy_dissipation_rate"],
        "advection_enstrophy_work": advection_work,
        "rk2_remainder": rk2_remainder,
        "mask_enstrophy_change": mask_change,
        "normalized_filtered_closure": filtered_closure,
        "dominant_shell": spectrum["dominant_shell"],
        "low_k_fraction": spectrum["low_k_fraction"],
        "tail_fraction": spectrum["tail_fraction"],
        "high_k_fraction": spectrum["high_k_fraction"],
        "maximum_imaginary_ratio": maximum_imaginary,
        "maximum_speed": maximum_speed,
        "cfl": cfl,
        "state_sha256": sha256_array(state_array),
        "finite_status": finite_status,
    }
    legacy_row = {
        "loop_index": step - 1,
        "completed_steps": step,
        "physical_time": physical_time,
        "trajectory_id": trajectory_id,
        "operator_family": metadata["operator_family"],
        "energy": budget["energy"],
        "enstrophy": budget["enstrophy"],
        "vorticity_rms": field_rms(state_array),
        "velocity_rms": float(np.sqrt(np.mean(u * u + v * v))),
        "energy_injection": budget["energy_injection_rate"],
        "enstrophy_injection": budget["enstrophy_injection_rate"],
        "viscous_energy_dissipation": budget["viscous_energy_dissipation_rate"],
        "viscous_enstrophy_dissipation": budget["viscous_enstrophy_dissipation_rate"],
        "advection_enstrophy_work": advection_work,
        "rk2_remainder": rk2_remainder,
        "mask_enstrophy_change": mask_change,
        "normalized_filtered_closure": filtered_closure,
        "dominant_shell": spectrum["dominant_shell"],
        "low_k_fraction": spectrum["low_k_fraction"],
        "tail_fraction": spectrum["tail_fraction"],
        "high_k_fraction": spectrum["high_k_fraction"],
        "maximum_imaginary_ratio": maximum_imaginary,
        "accepted_state_sha256": sha256_array(state_array),
        "finite_status": finite_status,
    }
    return {
        "row": row,
        "legacy_row": legacy_row,
        "state": state_array,
        "u": np.asarray(u),
        "v": np.asarray(v),
        "energy": float(budget["energy"]),
        "enstrophy": float(budget["enstrophy"]),
        **spectrum,
    }


def pairwise_metrics(
    first: Mapping[str, object], second: Mapping[str, object]
) -> dict[str, object]:
    first_state = np.asarray(first["state"], dtype=np.float64)
    second_state = np.asarray(second["state"], dtype=np.float64)
    absolute, normalized = normalized_rms_difference(first_state, second_state)
    first_mean_free = mean_free(first_state)
    second_mean_free = mean_free(second_state)
    mf_absolute, mf_normalized = normalized_rms_difference(
        first_mean_free, second_mean_free
    )
    first_u = np.asarray(first["u"], dtype=np.float64)
    first_v = np.asarray(first["v"], dtype=np.float64)
    second_u = np.asarray(second["u"], dtype=np.float64)
    second_v = np.asarray(second["v"], dtype=np.float64)
    velocity_numerator = math.sqrt(
        field_rms(first_u - second_u) ** 2 + field_rms(first_v - second_v) ** 2
    )
    first_velocity = float(np.sqrt(np.mean(first_u * first_u + first_v * first_v)))
    second_velocity = float(
        np.sqrt(np.mean(second_u * second_u + second_v * second_v))
    )
    velocity_difference = velocity_numerator / max(
        first_velocity, second_velocity, RESIDUAL_FLOOR
    )
    if field_rms(first_state) <= RESIDUAL_FLOOR and field_rms(second_state) <= RESIDUAL_FLOOR:
        cosine = 1.0
    else:
        cosine = cosine_similarity(first_state, second_state)
    result = {
        "absolute_vorticity_rms_difference": absolute,
        "normalized_vorticity_rms_difference": normalized,
        "absolute_mean_free_vorticity_rms_difference": mf_absolute,
        "normalized_mean_free_vorticity_rms_difference": mf_normalized,
        "mean_vorticity_difference": float(np.mean(first_state) - np.mean(second_state)),
        "normalized_velocity_difference": velocity_difference,
        "vorticity_cosine_similarity": cosine,
        "energy_relative_difference": symmetric_relative_difference(
            float(first["energy"]), float(second["energy"])
        ),
        "enstrophy_relative_difference": symmetric_relative_difference(
            float(first["enstrophy"]), float(second["enstrophy"])
        ),
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
    }
    result["finite_status"] = all(
        math.isfinite(float(value)) for value in result.values()
    )
    return result


def build_within_pairwise_row(
    case: Mapping[str, object],
    step: int,
    first_id: str,
    second_id: str,
    diagnostics: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    metrics = pairwise_metrics(diagnostics[first_id], diagnostics[second_id])
    if not bool(metrics["finite_status"]):
        raise IntegrityFailure(
            "pairwise_finite", "pairwise metric is nonfinite",
            case_id=str(case["case_id"]), step=step,
        )
    return {
        "case_id": case["case_id"], "N": case["N"], "dt": case["dt"],
        "step": step, "physical_time": step * float(case["dt"]),
        "trajectory_a": first_id, "trajectory_b": second_id, **metrics,
    }


def write_anchor_spectra(
    writer: IncrementalCsvWriter,
    case: Mapping[str, object],
    anchor_time: float,
    trajectory_id: str,
    diagnostic: Mapping[str, object],
    deal: np.ndarray,
) -> int:
    shell_energy = np.asarray(diagnostic["shell_energy"], dtype=np.float64)
    mode_count = np.asarray(diagnostic["mode_count"], dtype=np.int64)
    if len(shell_energy) != len(mode_count):
        raise RuntimeError("spectrum energy/count length mismatch")
    n = int(case["N"])
    dx = 2.0 * np.pi / n
    modes = np.fft.fftfreq(n, d=dx) * 2.0 * np.pi
    kx, ky = np.meshgrid(modes, modes)
    shell_index = np.floor(np.sqrt(kx * kx + ky * ky)).astype(int)
    dealiased_count = np.bincount(
        shell_index.ravel(),
        weights=np.asarray(deal, dtype=np.int64).ravel(),
        minlength=len(shell_energy),
    ).astype(np.int64)
    for shell, (energy_value, count_value) in enumerate(
        zip(shell_energy, mode_count, strict=True)
    ):
        writer.write(
            {
                "case_id": case["case_id"], "N": case["N"], "dt": case["dt"],
                "anchor_time": anchor_time, "trajectory_id": trajectory_id,
                "shell": shell, "shell_energy": float(energy_value),
                "mode_count": int(count_value),
                "dealiased_mode_count": int(dealiased_count[shell]),
                "finite_status": math.isfinite(float(energy_value)),
            }
        )
    return len(shell_energy)


def state_checkpoint_key(
    case_id: str, trajectory_id: str, anchor_index: int
) -> str:
    return f"{case_id}__{trajectory_id}__A{anchor_index:02d}"


def velocity_from_vorticity(field: object) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(field, dtype=np.float64)
    n = int(array.shape[0])
    dx = 2.0 * np.pi / n
    k = np.fft.fftfreq(n, d=dx) * 2.0 * np.pi
    kx, ky = np.meshgrid(k, k)
    k2 = kx * kx + ky * ky
    safe_k2 = np.where(k2 == 0.0, 1.0, k2)
    psi_hat = -np.fft.fft2(array) / safe_k2
    psi_hat[0, 0] = 0.0
    u = np.fft.ifft2(1j * ky * psi_hat).real
    v = np.fft.ifft2(-1j * kx * psi_hat).real
    return u, v


def diagnostic_from_field(field: object) -> dict[str, object]:
    state = np.ascontiguousarray(np.asarray(field, dtype=np.float64))
    u, v = velocity_from_vorticity(state)
    n = int(state.shape[0])
    dx = 2.0 * np.pi / n
    k = np.fft.fftfreq(n, d=dx) * 2.0 * np.pi
    kx, ky = np.meshgrid(k, k)
    spectrum = spectrum_details(u, v, kx, ky)
    return {
        "state": state,
        "u": u,
        "v": v,
        "energy": 0.5 * float(np.mean(u * u + v * v)),
        "enstrophy": enstrophy(state),
        **spectrum,
    }


def fourier_restrict(field: object, target_n: int) -> dict[str, object]:
    source = np.asarray(field, dtype=np.float64)
    source_n = int(source.shape[0])
    if source.shape != (source_n, source_n) or target_n > source_n or target_n % 2:
        raise ValueError("invalid Fourier restriction shapes")
    source_coefficients = np.fft.fft2(source) / float(source_n ** 2)
    source_modes = np.rint(np.fft.fftfreq(source_n) * source_n).astype(int)
    target_modes = np.rint(np.fft.fftfreq(target_n) * target_n).astype(int)
    source_index = {int(mode): index for index, mode in enumerate(source_modes)}
    target_coefficients = np.zeros((target_n, target_n), dtype=np.complex128)
    retained_source = np.zeros_like(source_coefficients, dtype=bool)
    half = target_n // 2
    for target_y, ky in enumerate(target_modes):
        if abs(int(ky)) >= half:
            continue
        source_y = source_index[int(ky)]
        for target_x, kx in enumerate(target_modes):
            if abs(int(kx)) >= half:
                continue
            source_x = source_index[int(kx)]
            target_coefficients[target_y, target_x] = source_coefficients[
                source_y, source_x
            ]
            retained_source[source_y, source_x] = True
    target_complex = np.fft.ifft2(target_coefficients * float(target_n ** 2))
    restricted = np.ascontiguousarray(target_complex.real, dtype=np.float64)
    imaginary_rms = field_rms(target_complex.imag)

    source_kx, source_ky = np.meshgrid(source_modes, source_modes)
    k2 = source_kx * source_kx + source_ky * source_ky
    coefficient_power = np.abs(source_coefficients) ** 2
    energy_weights = np.zeros_like(coefficient_power, dtype=np.float64)
    nonzero = k2 > 0
    energy_weights[nonzero] = 0.5 * coefficient_power[nonzero] / k2[nonzero]
    outside = ~retained_source
    discarded_enstrophy = 0.5 * float(np.sum(coefficient_power[outside]))
    discarded_energy = float(np.sum(energy_weights[outside]))
    parseval_residual = abs(
        float(np.mean(source * source)) - float(np.sum(coefficient_power))
    )
    return {
        "field": restricted,
        "discarded_band_energy": discarded_energy,
        "discarded_band_enstrophy": discarded_enstrophy,
        "imaginary_rms": imaginary_rms,
        "retained_mode_count": int(np.count_nonzero(retained_source)),
        "parseval_residual": parseval_residual,
    }


def comparison_floor(
    first: np.ndarray,
    second: np.ndarray,
    restriction_imaginary_floor: float,
    measured_study_floor: float,
) -> tuple[float, float, float]:
    first_roundtrip = np.fft.ifft2(np.fft.fft2(first)).real
    second_roundtrip = np.fft.ifft2(np.fft.fft2(second)).real
    roundtrip_floor = max(
        field_rms(first_roundtrip - first), field_rms(second_roundtrip - second)
    )
    absolute_guard = FLOOR_SAFETY_MULTIPLIER * np.finfo(np.float64).eps * max(
        field_rms(mean_free(first)), field_rms(mean_free(second)),
        np.finfo(np.float64).tiny,
    )
    measured = max(
        float(measured_study_floor),
        roundtrip_floor,
        float(restriction_imaginary_floor),
        absolute_guard,
    )
    return roundtrip_floor, absolute_guard, measured


def smallest_noncontrol_separation(states: Mapping[str, np.ndarray]) -> float:
    values = []
    for first_id, second_id in PRIMARY_PAIRS:
        values.append(
            normalized_rms_difference(
                mean_free(states[first_id]), mean_free(states[second_id])
            )[1]
        )
    return min(values, default=0.0)


def build_projection_control_rows(
    case: Mapping[str, object],
    anchor_index: int,
    anchor_time: float,
    states: Mapping[str, np.ndarray],
    solver: object,
    forcing: np.ndarray,
    *,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_rc: np.ndarray,
    ky_rc: np.ndarray,
) -> list[dict[str, object]]:
    case_id = str(case["case_id"])
    step = int(round(anchor_time / float(case["dt"])))
    smallest_separation = smallest_noncontrol_separation(states)
    rows = []
    for control in PROJECTION_CONTROLS:
        trajectory_id = str(control["trajectory_id"])
        canonical_state = np.array(
            states[trajectory_id], dtype=np.float64, copy=True, order="C"
        )
        control_state = np.array(
            states[trajectory_id], dtype=np.float64, copy=True, order="C"
        )
        canonical_state.setflags(write=False)
        control_state.setflags(write=False)
        if (
            np.shares_memory(canonical_state, control_state)
            or sha256_array(canonical_state) != sha256_array(control_state)
        ):
            raise IntegrityFailure(
                "projection_control_state_ownership",
                "canonical/control copies are aliased or unequal",
                case_id=case_id,
                trajectory_id=trajectory_id,
                step=step,
            )
        psi = solver.streamfunction(canonical_state)
        u, v = solver.velocity(psi)
        canonical_transport = compute_transport(
            str(control["canonical_kind"]), solver, canonical_state, psi, u, v,
            jacobian_arakawa_periodic=jacobian_arakawa_periodic,
            kx_rc=kx_rc, ky_rc=ky_rc, case_id=case_id,
            trajectory_id=trajectory_id, step=step,
        )
        control_psi = solver.streamfunction(control_state)
        control_u, control_v = solver.velocity(control_psi)
        projected_transport = compute_transport(
            str(control["control_kind"]), solver, control_state,
            control_psi, control_u, control_v,
            jacobian_arakawa_periodic=jacobian_arakawa_periodic,
            kx_rc=kx_rc, ky_rc=ky_rc, case_id=case_id,
            trajectory_id=trajectory_id, step=step,
        )
        transport_difference = normalized_rms_difference(
            canonical_transport["transport"], projected_transport["transport"]
        )[1]
        maximum_imaginary = max(
            float(canonical_transport["maximum_imaginary_ratio"]),
            float(projected_transport["maximum_imaginary_ratio"]),
        )
        preview_performed = anchor_index < len(ANCHOR_TIMES) - 1
        if preview_performed:
            canonical_preview = rk2_preview(
                str(control["canonical_kind"]), solver, canonical_state, forcing,
                step=step + 1, case_id=case_id, trajectory_id=trajectory_id,
                jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                kx_rc=kx_rc, ky_rc=ky_rc,
            )
            projected_preview = rk2_preview(
                str(control["control_kind"]), solver, control_state, forcing,
                step=step + 1, case_id=case_id, trajectory_id=trajectory_id,
                jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                kx_rc=kx_rc, ky_rc=ky_rc,
            )
            accepted_difference = normalized_rms_difference(
                canonical_preview["accepted"], projected_preview["accepted"]
            )[1]
            selected_defect = max(transport_difference, accepted_difference)
            comparison_type = "one_step_preview"
            accepted_status = (
                "PASS" if accepted_difference <= PROJECTION_ABSOLUTE_LIMIT else "FAIL"
            )
            accepted_limit_pass: object = accepted_difference <= PROJECTION_ABSOLUTE_LIMIT
            maximum_imaginary = max(
                maximum_imaginary,
                float(canonical_preview["maximum_imaginary_ratio"]),
                float(projected_preview["maximum_imaginary_ratio"]),
            )
        else:
            accepted_difference = ""
            selected_defect = transport_difference
            comparison_type = "endpoint_transport_only"
            accepted_status = "NOT_EVALUATED"
            accepted_limit_pass = ""
        expected_control_hash = sha256_array(states[trajectory_id])
        if (
            sha256_array(canonical_state) != expected_control_hash
            or sha256_array(control_state) != expected_control_hash
        ):
            raise IntegrityFailure(
                "projection_control_state_mutation",
                "projection control evaluation changed an input copy",
                case_id=case_id,
                trajectory_id=trajectory_id,
                step=step,
            )
        absolute_pass = selected_defect <= PROJECTION_ABSOLUTE_LIMIT
        relative_applicable = smallest_separation > PROJECTION_ABSOLUTE_LIMIT
        separation_ratio: object = (
            selected_defect / smallest_separation
            if relative_applicable
            else ""
        )
        relative_pass = (
            True
            if not relative_applicable
            else selected_defect <= PROJECTION_RELATIVE_FRACTION * smallest_separation
        )
        transport_pass = transport_difference <= PROJECTION_ABSOLUTE_LIMIT
        numeric_values = (
            transport_difference, selected_defect, smallest_separation,
            maximum_imaginary,
        )
        finite_status = all(math.isfinite(float(value)) for value in numeric_values)
        rows.append(
            {
                "case_id": case_id, "N": case["N"], "dt": case["dt"],
                "anchor_time": anchor_time, "control_id": control["control_id"],
                "trajectory_id": trajectory_id, "comparison_type": comparison_type,
                "preview_performed": preview_performed,
                "normalized_transport_difference": transport_difference,
                "normalized_accepted_update_difference": accepted_difference,
                "selected_control_defect": selected_defect,
                "smallest_noncontrol_operator_separation": smallest_separation,
                "absolute_limit": PROJECTION_ABSOLUTE_LIMIT,
                "relative_fraction_limit": PROJECTION_RELATIVE_FRACTION,
                "absolute_limit_pass": absolute_pass,
                "relative_limit_applicable": relative_applicable,
                "control_to_operator_separation_ratio": separation_ratio,
                "relative_limit_pass": relative_pass,
                "transport_limit_pass": transport_pass,
                "accepted_update_limit_pass": accepted_limit_pass,
                "transport_status": "PASS" if transport_pass else "FAIL",
                "accepted_update_status": accepted_status,
                "descriptively_negligible": bool(absolute_pass and relative_pass),
                "maximum_imaginary_ratio": maximum_imaginary,
                "finite_status": finite_status,
            }
        )
    return rows


# ============================================================================
# Execution-only validation and aggregate integrity
# ============================================================================

def validate_fourier_restriction_harness() -> dict[str, object]:
    maximum_supported_error = 0.0
    maximum_removed_error = 0.0
    maximum_imaginary_rms = 0.0
    maximum_parseval_residual = 0.0
    cases_tested = 0
    for source_n in (64, 96, 144):
        source_axis = 2.0 * np.pi * np.arange(source_n, dtype=np.float64) / source_n
        source_x, source_y = np.meshgrid(source_axis, source_axis)
        supported = (
            0.25
            + 0.70 * np.sin(3.0 * source_x + 5.0 * source_y)
            + 0.40 * np.cos(7.0 * source_x - 2.0 * source_y)
            + 0.15 * np.sin(11.0 * source_y)
        )
        result = fourier_restrict(supported, 64)
        target_axis = 2.0 * np.pi * np.arange(64, dtype=np.float64) / 64
        target_x, target_y = np.meshgrid(target_axis, target_axis)
        expected = (
            0.25
            + 0.70 * np.sin(3.0 * target_x + 5.0 * target_y)
            + 0.40 * np.cos(7.0 * target_x - 2.0 * target_y)
            + 0.15 * np.sin(11.0 * target_y)
        )
        supported_error = field_rms(np.asarray(result["field"]) - expected)
        maximum_supported_error = max(maximum_supported_error, supported_error)
        maximum_imaginary_rms = max(
            maximum_imaginary_rms, float(result["imaginary_rms"])
        )
        maximum_parseval_residual = max(
            maximum_parseval_residual, float(result["parseval_residual"])
        )
        cases_tested += 1
        if source_n > 64:
            unsupported = (
                np.cos(32.0 * source_x)
                + 0.5 * np.sin(32.0 * source_y)
                + 0.25 * np.cos(40.0 * source_x + source_y)
            )
            removed = fourier_restrict(unsupported, 64)
            removed_error = field_rms(removed["field"])
            maximum_removed_error = max(maximum_removed_error, removed_error)
            maximum_imaginary_rms = max(
                maximum_imaginary_rms, float(removed["imaginary_rms"])
            )
            maximum_parseval_residual = max(
                maximum_parseval_residual, float(removed["parseval_residual"])
            )
            cases_tested += 1
    limit = 5.0e-13
    if (
        maximum_supported_error > limit
        or maximum_removed_error > limit
        or maximum_imaginary_rms > limit
        or maximum_parseval_residual > limit
    ):
        raise IntegrityFailure(
            "fourier_restriction_harness",
            "known-field Fourier restriction tests failed",
            details={
                "maximum_supported_error": maximum_supported_error,
                "maximum_removed_error": maximum_removed_error,
                "maximum_imaginary_rms": maximum_imaginary_rms,
                "maximum_parseval_residual": maximum_parseval_residual,
                "limit": limit,
            },
        )
    return {
        "status": "PASS",
        "cases_tested": cases_tested,
        "maximum_supported_error": maximum_supported_error,
        "maximum_removed_error": maximum_removed_error,
        "maximum_imaginary_rms": maximum_imaginary_rms,
        "maximum_parseval_residual": maximum_parseval_residual,
        "limit": limit,
    }


def verify_forcing_cross_grid_equivalence(
    records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    if len(records) != len(CASE_REGISTRY):
        raise IntegrityFailure(
            "forcing_cross_grid_count", "forcing record count is incomplete"
        )
    coefficient_maps: list[dict[tuple[int, int], complex]] = []
    for record in records:
        selected: dict[tuple[int, int], complex] = {}
        for mode in record["normalized_nonzero_fourier_modes"]:
            item = dict(mode)
            key = (int(item["kx"]), int(item["ky"]))
            selected[key] = complex(float(item["real"]), float(item["imag"]))
        coefficient_maps.append(selected)
    expected_modes = set(coefficient_maps[0])
    maximum_difference = 0.0
    for selected in coefficient_maps[1:]:
        if set(selected) != expected_modes:
            raise IntegrityFailure(
                "forcing_cross_grid_modes",
                "normalized forcing mode support differs across grids",
            )
        for key in sorted(expected_modes):
            maximum_difference = max(
                maximum_difference,
                abs(selected[key] - coefficient_maps[0][key]),
            )
    coefficient_values = [float(record["normalization_coefficient"]) for record in records]
    coefficient_difference = max(coefficient_values) - min(coefficient_values)
    limit = 2.0e-15
    if maximum_difference > limit or abs(coefficient_difference) > limit:
        raise IntegrityFailure(
            "forcing_cross_grid_coefficients",
            "normalized forcing coefficients differ across grids",
            details={
                "maximum_mode_difference": maximum_difference,
                "normalization_coefficient_range": coefficient_difference,
                "limit": limit,
            },
        )
    return {
        "status": "PASS",
        "mode_count": len(expected_modes),
        "maximum_normalized_mode_difference": maximum_difference,
        "normalization_coefficient_range": coefficient_difference,
        "limit": limit,
    }


def new_integrity_accumulator(
    case: Mapping[str, object], trajectory_id: str
) -> dict[str, object]:
    return {
        "case_id": str(case["case_id"]),
        "N": int(case["N"]),
        "dt": float(case["dt"]),
        "trajectory_id": trajectory_id,
        "expected_updates": int(case["updates"]),
        "accepted_updates": 0,
        "state_ownership_check_count": 1,
        "failure_count": 0,
        "finite_failure_count": 0,
        "unfiltered_closure_failure_count": 0,
        "filtered_closure_failure_count": 0,
        "mask_crosscheck_failure_count": 0,
        "imaginary_ratio_failure_count": 0,
        "physical_loss_sign_failure_count": 0,
        "spectral_loss_sign_failure_count": 0,
        "corrected_mask_change_sign_failure_count": 0,
        "state_mutation_count": 0,
        "state_alias_count": 0,
        "forcing_mutation_count": 0,
        "wavenumber_mutation_count": 0,
        "maximum_normalized_unfiltered_closure": 0.0,
        "maximum_normalized_filtered_closure": 0.0,
        "maximum_normalized_mask_crosscheck": 0.0,
        "maximum_normalized_filter_bookkeeping": 0.0,
        "maximum_imaginary_ratio": 0.0,
        "minimum_mask_loss_physical": math.inf,
        "minimum_mask_loss_spectral": math.inf,
        "maximum_corrected_mask_enstrophy_change": -math.inf,
        "maximum_cfl": 0.0,
    }


def update_integrity_accumulator(
    accumulator: dict[str, object],
    preview: Mapping[str, object],
    *,
    ownership_checks: int = 1,
) -> None:
    accumulator["accepted_updates"] = int(accumulator["accepted_updates"]) + 1
    accumulator["state_ownership_check_count"] = (
        int(accumulator["state_ownership_check_count"]) + ownership_checks
    )
    accumulator["maximum_normalized_unfiltered_closure"] = max(
        float(accumulator["maximum_normalized_unfiltered_closure"]),
        float(preview["normalized_unfiltered_closure"]),
    )
    accumulator["maximum_normalized_filtered_closure"] = max(
        float(accumulator["maximum_normalized_filtered_closure"]),
        float(preview["normalized_filtered_closure"]),
    )
    accumulator["maximum_normalized_mask_crosscheck"] = max(
        float(accumulator["maximum_normalized_mask_crosscheck"]),
        float(preview["normalized_mask_crosscheck"]),
    )
    accumulator["maximum_normalized_filter_bookkeeping"] = max(
        float(accumulator["maximum_normalized_filter_bookkeeping"]),
        float(preview["normalized_filter_bookkeeping"]),
    )
    accumulator["maximum_imaginary_ratio"] = max(
        float(accumulator["maximum_imaginary_ratio"]),
        float(preview["maximum_imaginary_ratio"]),
    )
    accumulator["minimum_mask_loss_physical"] = min(
        float(accumulator["minimum_mask_loss_physical"]),
        float(preview["mask_loss_physical"]),
    )
    accumulator["minimum_mask_loss_spectral"] = min(
        float(accumulator["minimum_mask_loss_spectral"]),
        float(preview["mask_loss_spectral"]),
    )
    accumulator["maximum_corrected_mask_enstrophy_change"] = max(
        float(accumulator["maximum_corrected_mask_enstrophy_change"]),
        float(preview["mask_enstrophy_change_rate"]),
    )
    accumulator["maximum_cfl"] = max(
        float(accumulator["maximum_cfl"]), float(preview["cfl"])
    )


def mark_integrity_failure(
    accumulator: dict[str, object], gate: str
) -> None:
    mapping = {
        "update_finite": "finite_failure_count",
        "unfiltered_ledger_closure": "unfiltered_closure_failure_count",
        "filtered_ledger_closure": "filtered_closure_failure_count",
        "mask_parseval_crosscheck": "mask_crosscheck_failure_count",
        "real_compatible_imaginary_ratio": "imaginary_ratio_failure_count",
        "physical_loss_sign": "physical_loss_sign_failure_count",
        "spectral_loss_sign": "spectral_loss_sign_failure_count",
        "corrected_mask_change_sign": "corrected_mask_change_sign_failure_count",
        "state_mutation": "state_mutation_count",
        "state_alias": "state_alias_count",
        "accepted_state_alias": "state_alias_count",
        "forcing_mutation": "forcing_mutation_count",
        "real_compatible_wavenumber_mutation": "wavenumber_mutation_count",
    }
    accumulator["failure_count"] = int(accumulator["failure_count"]) + 1
    field = mapping.get(gate)
    if field is not None:
        accumulator[field] = int(accumulator[field]) + 1


def build_integrity_summary_row(
    accumulator: Mapping[str, object],
    *,
    solver_environment_unchanged: bool,
    forcing_unchanged: bool,
    local_wavenumbers_unchanged: bool,
) -> dict[str, object]:
    row = dict(accumulator)
    for name in ("minimum_mask_loss_physical", "minimum_mask_loss_spectral"):
        if not math.isfinite(float(row[name])):
            row[name] = ""
    if not math.isfinite(float(row["maximum_corrected_mask_enstrophy_change"])):
        row["maximum_corrected_mask_enstrophy_change"] = ""
    row["solver_environment_unchanged"] = solver_environment_unchanged
    row["forcing_unchanged"] = forcing_unchanged
    row["local_wavenumbers_unchanged"] = local_wavenumbers_unchanged
    row["all_updates_finite"] = int(row["finite_failure_count"]) == 0
    row["integrity_pass"] = bool(
        int(row["accepted_updates"]) == int(row["expected_updates"])
        and int(row["failure_count"]) == 0
        and solver_environment_unchanged
        and forcing_unchanged
        and local_wavenumbers_unchanged
    )
    return row


# ============================================================================
# Cross-case refinement and resolution summaries
# ============================================================================

def build_refinement_increment(
    axis: str,
    adjacency_index: int,
    coarse_case_id: str,
    fine_case_id: str,
    trajectory_id: str,
    anchor_index: int,
    checkpoints: Mapping[tuple[str, str, int], np.ndarray],
    measured_study_floor: float,
) -> dict[str, object]:
    coarse_native = checkpoints[(coarse_case_id, trajectory_id, anchor_index)]
    fine_native = checkpoints[(fine_case_id, trajectory_id, anchor_index)]
    if axis == "temporal":
        coarse_field = np.asarray(coarse_native)
        fine_field = np.asarray(fine_native)
        coarse_discarded_energy: object = ""
        fine_discarded_energy: object = ""
        coarse_discarded_enstrophy: object = ""
        fine_discarded_enstrophy: object = ""
        restriction_imaginary = 0.0
        discarded_applicable = False
        representation = "native_n64"
    elif axis == "spatial":
        coarse_restriction = fourier_restrict(coarse_native, 64)
        fine_restriction = fourier_restrict(fine_native, 64)
        coarse_field = np.asarray(coarse_restriction["field"])
        fine_field = np.asarray(fine_restriction["field"])
        coarse_discarded_energy = coarse_restriction["discarded_band_energy"]
        fine_discarded_energy = fine_restriction["discarded_band_energy"]
        coarse_discarded_enstrophy = coarse_restriction[
            "discarded_band_enstrophy"
        ]
        fine_discarded_enstrophy = fine_restriction["discarded_band_enstrophy"]
        restriction_imaginary = max(
            float(coarse_restriction["imaginary_rms"]),
            float(fine_restriction["imaginary_rms"]),
        )
        discarded_applicable = True
        representation = "fourier_common_n64"
    else:
        raise KeyError(axis)
    coarse_diagnostic = diagnostic_from_field(coarse_field)
    fine_diagnostic = diagnostic_from_field(fine_field)
    metrics = pairwise_metrics(coarse_diagnostic, fine_diagnostic)
    roundtrip_floor, absolute_guard, numerical_floor = comparison_floor(
        coarse_field,
        fine_field,
        restriction_imaginary,
        measured_study_floor,
    )
    return {
        "axis": axis,
        "adjacency_index": adjacency_index,
        "coarse_case_id": coarse_case_id,
        "fine_case_id": fine_case_id,
        "trajectory_id": trajectory_id,
        "anchor_index": anchor_index,
        "anchor_time": ANCHOR_TIMES[anchor_index],
        "coarse_N": int(CASE_BY_ID[coarse_case_id]["N"]),
        "fine_N": int(CASE_BY_ID[fine_case_id]["N"]),
        "coarse_dt": float(CASE_BY_ID[coarse_case_id]["dt"]),
        "fine_dt": float(CASE_BY_ID[fine_case_id]["dt"]),
        "comparison_grid_N": 64,
        "comparison_representation": representation,
        "discarded_band_applicable": discarded_applicable,
        "coarse_discarded_band_energy": coarse_discarded_energy,
        "fine_discarded_band_energy": fine_discarded_energy,
        "coarse_discarded_band_enstrophy": coarse_discarded_enstrophy,
        "fine_discarded_band_enstrophy": fine_discarded_enstrophy,
        "roundtrip_floor": roundtrip_floor,
        "restriction_imaginary_floor": restriction_imaginary,
        "absolute_guard_floor": absolute_guard,
        "numerical_floor": numerical_floor,
        "metrics": metrics,
    }


def build_refinement_rows_and_groups(
    checkpoints: Mapping[tuple[str, str, int], np.ndarray],
    measured_study_floor: float,
) -> tuple[list[dict[str, object]], dict[tuple[str, str, int], dict[str, object]]]:
    rows: list[dict[str, object]] = []
    groups: dict[tuple[str, str, int], dict[str, object]] = {}
    for axis, adjacencies, ratio in (
        ("temporal", TEMPORAL_ADJACENCIES, 2.0),
        ("spatial", SPATIAL_ADJACENCIES, 1.5),
    ):
        for trajectory_id in TRAJECTORY_IDS:
            for anchor_index in range(len(ANCHOR_TIMES)):
                increments = [
                    build_refinement_increment(
                        axis,
                        adjacency_index,
                        coarse_case_id,
                        fine_case_id,
                        trajectory_id,
                        anchor_index,
                        checkpoints,
                        measured_study_floor,
                    )
                    for adjacency_index, (coarse_case_id, fine_case_id) in enumerate(
                        adjacencies
                    )
                ]
                coarse_error = float(
                    increments[0]["metrics"][
                        "absolute_mean_free_vorticity_rms_difference"
                    ]
                )
                fine_error = float(
                    increments[1]["metrics"][
                        "absolute_mean_free_vorticity_rms_difference"
                    ]
                )
                group_floor = max(
                    float(increments[0]["numerical_floor"]),
                    float(increments[1]["numerical_floor"]),
                )
                order_reportable = bool(
                    math.isfinite(coarse_error)
                    and math.isfinite(fine_error)
                    and coarse_error > group_floor
                    and fine_error > group_floor
                )
                order_eligible = bool(
                    order_reportable
                    and coarse_error >= 100.0 * group_floor
                    and fine_error >= 100.0 * group_floor
                )
                observed_order: object = (
                    math.log(coarse_error / fine_error) / math.log(ratio)
                    if order_reportable
                    else ""
                )
                if order_eligible:
                    floor_status = "ABOVE_100X_FLOOR"
                elif order_reportable:
                    floor_status = "ABOVE_FLOOR_NOT_100X"
                else:
                    floor_status = "INDETERMINATE_NEAR_FLOOR"
                groups[(axis, trajectory_id, anchor_index)] = {
                    "axis": axis,
                    "trajectory_id": trajectory_id,
                    "anchor_index": anchor_index,
                    "anchor_time": ANCHOR_TIMES[anchor_index],
                    "coarse_error": coarse_error,
                    "fine_error": fine_error,
                    "refinement_ratio": ratio,
                    "observed_order": observed_order,
                    "order_reportable": order_reportable,
                    "order_eligible": order_eligible,
                    "numerical_floor": group_floor,
                    "numerical_floor_status": floor_status,
                }
                for increment_index, increment in enumerate(increments):
                    metrics = dict(increment["metrics"])
                    comparison_error = float(
                        metrics["absolute_mean_free_vorticity_rms_difference"]
                    )
                    row = {
                        key: value
                        for key, value in increment.items()
                        if key != "metrics"
                    }
                    row.update(metrics)
                    row.update(
                        {
                            "increment_role": (
                                "coarse_increment"
                                if increment_index == 0
                                else "fine_increment"
                            ),
                            "coarse_error_for_order": coarse_error,
                            "fine_error_for_order": fine_error,
                            "refinement_ratio": ratio,
                            "observed_order": observed_order,
                            "order_reportable": order_reportable,
                            "order_eligible": order_eligible,
                            "comparison_error_to_floor_ratio": (
                                comparison_error
                                / max(float(increment["numerical_floor"]), RESIDUAL_FLOOR)
                            ),
                            "numerical_floor_status": floor_status,
                            "finite_status": bool(metrics["finite_status"]),
                        }
                    )
                    if set(row) != set(REFINEMENT_FIELDNAMES):
                        missing = sorted(set(REFINEMENT_FIELDNAMES) - set(row))
                        extra = sorted(set(row) - set(REFINEMENT_FIELDNAMES))
                        raise RuntimeError(
                            f"refinement row schema mismatch: missing={missing}, extra={extra}"
                        )
                    rows.append(row)
    if len(rows) != EXPECTED_REFINEMENT_ROWS:
        raise IntegrityFailure(
            "refinement_row_count",
            f"refinement rows={len(rows)}, expected={EXPECTED_REFINEMENT_ROWS}",
        )
    return rows, groups


def build_refinement_and_resolution_summary(
    groups: Mapping[tuple[str, str, int], Mapping[str, object]],
    checkpoints: Mapping[tuple[str, str, int], np.ndarray],
    measured_study_floor: float,
) -> dict[str, object]:
    method_records = []
    unresolved_temporal: list[str] = []
    unresolved_spatial: list[str] = []
    for trajectory_id in TRAJECTORY_IDS:
        for axis in ("temporal", "spatial"):
            records = [groups[(axis, trajectory_id, index)] for index in range(7)]
            positive = records[1:]
            final_five = records[2:]
            reduction_flags = [
                float(record["fine_error"]) < float(record["coarse_error"])
                for record in positive
            ]
            refinement_resolved = bool(
                reduction_flags[-1] and sum(reduction_flags) >= 5
            )
            lower, upper = (1.7, 2.3) if axis == "temporal" else (1.5, 2.5)
            order_flags = [
                bool(record["order_eligible"])
                and lower <= float(record["observed_order"]) <= upper
                for record in final_five
            ]
            order_diagnostic = sum(order_flags) >= 4
            if not refinement_resolved:
                (unresolved_temporal if axis == "temporal" else unresolved_spatial).append(
                    trajectory_id
                )
            method_records.append(
                {
                    "trajectory_id": trajectory_id,
                    "axis": axis,
                    "status": "RESOLVED" if refinement_resolved else "UNRESOLVED",
                    "fine_smaller_count_positive_anchors": sum(reduction_flags),
                    "final_anchor_fine_smaller": reduction_flags[-1],
                    "order_range": [lower, upper],
                    "order_range_count_final_five": sum(order_flags),
                    "order_diagnostic_status": (
                        "SUPPORTED" if order_diagnostic else "NOT_SUPPORTED"
                    ),
                    "anchors": [dict(record) for record in records],
                }
            )

    c4_common: dict[tuple[str, int], np.ndarray] = {}
    for trajectory_id in TRAJECTORY_IDS:
        for anchor_index in range(7):
            c4_common[(trajectory_id, anchor_index)] = np.asarray(
                fourier_restrict(
                    checkpoints[("C4_N144_DT00125", trajectory_id, anchor_index)],
                    64,
                )["field"]
            )
    pair_records = []
    for first_id, second_id in PRIMARY_PAIRS:
        anchor_records = []
        for anchor_index, anchor_time in enumerate(ANCHOR_TIMES):
            first_temporal = float(
                groups[("temporal", first_id, anchor_index)]["fine_error"]
            )
            second_temporal = float(
                groups[("temporal", second_id, anchor_index)]["fine_error"]
            )
            first_spatial = float(
                groups[("spatial", first_id, anchor_index)]["fine_error"]
            )
            second_spatial = float(
                groups[("spatial", second_id, anchor_index)]["fine_error"]
            )
            combined = (
                first_temporal + second_temporal + first_spatial + second_spatial
            )
            first_field = c4_common[(first_id, anchor_index)]
            second_field = c4_common[(second_id, anchor_index)]
            separation = field_rms(mean_free(first_field) - mean_free(second_field))
            _, absolute_guard, separation_floor = comparison_floor(
                first_field, second_field, 0.0, measured_study_floor
            )
            separation_above_floor = separation > separation_floor
            resolved_at_anchor = bool(
                separation_above_floor and combined <= 0.20 * separation
            )
            anchor_records.append(
                {
                    "anchor_index": anchor_index,
                    "anchor_time": anchor_time,
                    "fine_temporal_increment_first": first_temporal,
                    "fine_temporal_increment_second": second_temporal,
                    "fine_spatial_increment_first": first_spatial,
                    "fine_spatial_increment_second": second_spatial,
                    "combined_discretization_uncertainty": combined,
                    "c4_common_band_mean_free_separation": separation,
                    "separation_numerical_floor": separation_floor,
                    "separation_absolute_guard_floor": absolute_guard,
                    "separation_above_floor": separation_above_floor,
                    "uncertainty_fraction_of_separation": (
                        combined / separation if separation_above_floor else None
                    ),
                    "criterion_fraction": 0.20,
                    "resolved_at_anchor": resolved_at_anchor,
                }
            )
        final_five = anchor_records[2:]
        resolved_count = sum(
            bool(record["resolved_at_anchor"]) for record in final_five
        )
        final_anchor_resolved = bool(final_five[-1]["resolved_at_anchor"])
        pair_resolved = final_anchor_resolved and resolved_count >= 4
        pair_records.append(
            {
                "trajectory_a": first_id,
                "trajectory_b": second_id,
                "status": "RESOLVED" if pair_resolved else "UNRESOLVED",
                "resolved_count_final_five": resolved_count,
                "final_anchor_resolved": final_anchor_resolved,
                "space_time_interaction_unmeasured": True,
                "anchors": anchor_records,
            }
        )
    possible_escalations = []
    if unresolved_temporal:
        possible_escalations.append(
            {
                "axis": "temporal",
                "affected_trajectories": unresolved_temporal,
                "candidate_only": "N64_dt0.000625",
                "automatic": False,
            }
        )
    if unresolved_spatial:
        possible_escalations.append(
            {
                "axis": "spatial",
                "affected_trajectories": unresolved_spatial,
                "candidate_only": "N216_dt0.00125",
                "automatic": False,
            }
        )
    return {
        "method_refinement": method_records,
        "operator_pair_resolution": pair_records,
        "unresolved_temporal_trajectories": unresolved_temporal,
        "unresolved_spatial_trajectories": unresolved_spatial,
        "possible_escalations": possible_escalations,
        "space_time_interaction_unmeasured": True,
        "reference_candidate_executed": False,
        "validated_reference": False,
        "method_ranking_produced": False,
    }


# ============================================================================
# Output finalization
# ============================================================================

def write_state_checkpoints(
    path: Path,
    checkpoints: Mapping[tuple[str, str, int], np.ndarray],
    checkpoint_hashes: Mapping[tuple[str, str, int], str],
    *,
    require_complete: bool,
) -> int:
    expected_keys = [
        (case_id, trajectory_id, anchor_index)
        for case_id in CASE_IDS
        for trajectory_id in TRAJECTORY_IDS
        for anchor_index in range(len(ANCHOR_TIMES))
    ]
    if require_complete and set(checkpoints) != set(expected_keys):
        raise IntegrityFailure(
            "checkpoint_key_count",
            f"checkpoint arrays={len(checkpoints)}, expected={EXPECTED_STATE_ARRAYS}",
        )
    ordered_arrays: dict[str, np.ndarray] = {}
    for key in expected_keys:
        if key not in checkpoints:
            continue
        case_id, trajectory_id, anchor_index = key
        value = np.asarray(checkpoints[key])
        expected_n = int(CASE_BY_ID[case_id]["N"])
        if (
            value.shape != (expected_n, expected_n)
            or value.dtype != np.dtype(np.float64)
            or not value.flags.c_contiguous
            or not np.isfinite(value).all()
            or sha256_array(value) != checkpoint_hashes[key]
        ):
            raise IntegrityFailure(
                "checkpoint_array_contract",
                f"invalid checkpoint array: {key}",
            )
        ordered_arrays[
            state_checkpoint_key(case_id, trajectory_id, anchor_index)
        ] = np.array(value, dtype=np.float64, copy=True, order="C")
    np.savez_compressed(path, **ordered_arrays)
    with np.load(path, allow_pickle=False) as archive:
        if list(archive.files) != list(ordered_arrays):
            raise IntegrityFailure(
                "checkpoint_archive_keys", "NPZ key order or set differs"
            )
        for archive_key, original in ordered_arrays.items():
            loaded = np.asarray(archive[archive_key])
            if (
                loaded.dtype != np.dtype(np.float64)
                or not loaded.flags.c_contiguous
                or loaded.shape != original.shape
                or not np.isfinite(loaded).all()
                or sha256_array(loaded) != sha256_array(original)
            ):
                raise IntegrityFailure(
                    "checkpoint_archive_reopen",
                    f"NPZ reopen validation failed: {archive_key}",
                )
    return len(ordered_arrays)


def csv_data_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


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
        else:
            raise RuntimeError(f"output missing before inventory: {name}")
    self_row = next(
        row for row in rows if row["relative_path"] == inventory_path.name
    )

    def render() -> str:
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(
            buffer, fieldnames=INVENTORY_FIELDNAMES, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()

    for _ in range(10):
        value = render()
        byte_count = len(value.encode("utf-8"))
        if self_row["bytes"] == byte_count:
            break
        self_row["bytes"] = byte_count
    else:
        raise RuntimeError("inventory self-byte count did not stabilize")
    atomic_write_text(inventory_path, render())
    return sha256_file(inventory_path)


def verify_successful_output_contract(
    run_directory: Path, counts: Mapping[str, int], checkpoint_arrays: int
) -> None:
    expected_counts = {
        "primary_accepted_updates": EXPECTED_PRIMARY_UPDATES,
        "case_diagnostic_rows": EXPECTED_CASE_DIAGNOSTIC_ROWS,
        "within_pairwise_rows": EXPECTED_WITHIN_PAIRWISE_ROWS,
        "refinement_rows": EXPECTED_REFINEMENT_ROWS,
        "projection_control_rows": EXPECTED_PROJECTION_CONTROL_ROWS,
        "integrity_summary_rows": EXPECTED_INTEGRITY_SUMMARY_ROWS,
        "anchor_spectra_rows": EXPECTED_ANCHOR_SPECTRA_ROWS,
        "d1r_reproduction_rows": D1R_PRIMARY_EXPECTED_ROWS,
    }
    for name, expected in expected_counts.items():
        if int(counts.get(name, -1)) != expected:
            raise IntegrityFailure(
                "output_row_counts",
                f"{name}={counts.get(name)}, expected={expected}",
            )
    csv_count_contract = {
        "case_diagnostics.csv": EXPECTED_CASE_DIAGNOSTIC_ROWS,
        "within_case_pairwise.csv": EXPECTED_WITHIN_PAIRWISE_ROWS,
        "refinement_comparisons.csv": EXPECTED_REFINEMENT_ROWS,
        "projection_controls.csv": EXPECTED_PROJECTION_CONTROL_ROWS,
        "integrity_summary.csv": EXPECTED_INTEGRITY_SUMMARY_ROWS,
        "anchor_spectra.csv": EXPECTED_ANCHOR_SPECTRA_ROWS,
        "file_inventory.csv": len(OUTPUT_FILENAMES),
    }
    for name, expected in csv_count_contract.items():
        observed = csv_data_row_count(run_directory / name)
        if observed != expected:
            raise IntegrityFailure(
                "output_csv_row_count",
                f"{name} rows={observed}, expected={expected}",
            )
    if checkpoint_arrays != EXPECTED_STATE_ARRAYS:
        raise IntegrityFailure(
            "checkpoint_array_count",
            f"checkpoint arrays={checkpoint_arrays}, expected={EXPECTED_STATE_ARRAYS}",
        )
    observed_names = tuple(sorted(path.name for path in run_directory.iterdir()))
    expected_names = tuple(sorted(OUTPUT_FILENAMES))
    if observed_names != expected_names:
        raise IntegrityFailure(
            "output_file_set",
            f"observed={observed_names}, expected={expected_names}",
        )
    oversized = {
        path.name: path.stat().st_size
        for path in run_directory.iterdir()
        if path.is_file() and path.stat().st_size >= MAX_OUTPUT_FILE_BYTES
    }
    if oversized:
        raise IntegrityFailure(
            "output_file_size", f"output files at or above 40 MB: {oversized}"
        )


def record_common_sample(
    case: Mapping[str, object],
    step: int,
    states: Mapping[str, np.ndarray],
    previews: Mapping[str, Mapping[str, object]] | None,
    solver: object,
    forcing: np.ndarray,
    diagnostic_writer: IncrementalCsvWriter,
    pairwise_writer: IncrementalCsvWriter,
    *,
    forcing_budget_snapshot: Callable[..., Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    sampled: dict[str, dict[str, object]] = {}
    for trajectory_id in TRAJECTORY_IDS:
        preview = None if previews is None else previews[trajectory_id]
        diagnostic = build_diagnostic(
            case,
            trajectory_id,
            states[trajectory_id],
            preview,
            solver,
            forcing,
            step=step,
            forcing_budget_snapshot=forcing_budget_snapshot,
        )
        sampled[trajectory_id] = diagnostic
        diagnostic_writer.write(diagnostic["row"])
    for first_id, second_id in PRIMARY_PAIRS:
        pairwise_writer.write(
            build_within_pairwise_row(
                case, step, first_id, second_id, sampled
            )
        )
    return sampled


def record_anchor(
    case: Mapping[str, object],
    anchor_index: int,
    states: Mapping[str, np.ndarray],
    sampled: Mapping[str, Mapping[str, object]],
    solver: object,
    forcing: np.ndarray,
    spectra_writer: IncrementalCsvWriter,
    projection_writer: IncrementalCsvWriter,
    checkpoints: dict[tuple[str, str, int], np.ndarray],
    checkpoint_hashes: dict[tuple[str, str, int], str],
    *,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_rc: np.ndarray,
    ky_rc: np.ndarray,
) -> tuple[int, list[dict[str, object]]]:
    case_id = str(case["case_id"])
    anchor_time = ANCHOR_TIMES[anchor_index]
    spectra_rows = 0
    for trajectory_id in TRAJECTORY_IDS:
        key = (case_id, trajectory_id, anchor_index)
        checkpoint = np.array(
            states[trajectory_id], dtype=np.float64, copy=True, order="C"
        )
        checkpoint.setflags(write=False)
        if any(
            np.shares_memory(checkpoint, states[other_id])
            for other_id in TRAJECTORY_IDS
        ):
            raise IntegrityFailure(
                "checkpoint_state_alias",
                f"saved checkpoint aliases a production state: {key}",
                case_id=case_id,
                trajectory_id=trajectory_id,
            )
        checkpoints[key] = checkpoint
        checkpoint_hashes[key] = sha256_array(checkpoint)
        if checkpoint_hashes[key] != str(sampled[trajectory_id]["row"]["state_sha256"]):
            raise IntegrityFailure(
                "checkpoint_diagnostic_hash",
                f"checkpoint differs from anchor diagnostic: {key}",
                case_id=case_id,
                trajectory_id=trajectory_id,
            )
        spectra_rows += write_anchor_spectra(
            spectra_writer,
            case,
            anchor_time,
            trajectory_id,
            sampled[trajectory_id],
            np.asarray(solver.deal),
        )
    control_rows = build_projection_control_rows(
        case,
        anchor_index,
        anchor_time,
        states,
        solver,
        forcing,
        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
        kx_rc=kx_rc,
        ky_rc=ky_rc,
    )
    for row in control_rows:
        projection_writer.write(row)
    return spectra_rows, control_rows


def evaluate_c2_order_canary(
    snapshots: Mapping[str, np.ndarray],
    forward: Mapping[str, Mapping[str, object]],
    solver: object,
    forcing: np.ndarray,
    *,
    step: int,
    jacobian_arakawa_periodic: Callable[..., np.ndarray],
    kx_rc: np.ndarray,
    ky_rc: np.ndarray,
) -> dict[str, object]:
    reverse: dict[str, dict[str, object]] = {}
    for trajectory_id in reversed(TRAJECTORY_IDS):
        reverse[trajectory_id] = rk2_preview(
            str(TRAJECTORY_BY_ID[trajectory_id]["operator_kind"]),
            solver,
            snapshots[trajectory_id],
            forcing,
            step=step,
            case_id="C2_N64_DT00125",
            trajectory_id=trajectory_id,
            jacobian_arakawa_periodic=jacobian_arakawa_periodic,
            kx_rc=kx_rc,
            ky_rc=ky_rc,
        )
    records = []
    maximum_normalized = 0.0
    maximum_absolute_mean_free = 0.0
    maximum_ledger_difference = 0.0
    for trajectory_id in TRAJECTORY_IDS:
        first = forward[trajectory_id]
        second = reverse[trajectory_id]
        absolute_mf, normalized_mf = normalized_rms_difference(
            mean_free(first["accepted"]), mean_free(second["accepted"])
        )
        ledger_difference = max(
            abs(float(a) - float(b))
            for a, b in zip(
                first["ledger_scalars"], second["ledger_scalars"], strict=True
            )
        )
        hash_match = sha256_array(first["accepted"]) == sha256_array(
            second["accepted"]
        )
        passed = bool(
            hash_match
            and normalized_mf <= ORDER_INVARIANCE_LIMIT
            and ledger_difference == 0.0
        )
        if not passed:
            raise IntegrityFailure(
                "order_invariance",
                f"C2 final forward/reverse canary failed: {trajectory_id}",
                case_id="C2_N64_DT00125",
                trajectory_id=trajectory_id,
                step=step,
                details={
                    "hash_match": hash_match,
                    "absolute_mean_free_difference": absolute_mf,
                    "normalized_mean_free_difference": normalized_mf,
                    "ledger_difference": ledger_difference,
                },
            )
        maximum_normalized = max(maximum_normalized, normalized_mf)
        maximum_absolute_mean_free = max(maximum_absolute_mean_free, absolute_mf)
        maximum_ledger_difference = max(
            maximum_ledger_difference, ledger_difference
        )
        records.append(
            {
                "trajectory_id": trajectory_id,
                "accepted_hash_match": hash_match,
                "absolute_mean_free_difference": absolute_mf,
                "normalized_mean_free_difference": normalized_mf,
                "maximum_ledger_scalar_difference": ledger_difference,
                "pass": passed,
            }
        )
    return {
        "status": "PASS",
        "step": step,
        "maximum_normalized_accepted_difference": maximum_normalized,
        "maximum_absolute_mean_free_difference": maximum_absolute_mean_free,
        "maximum_ledger_scalar_difference": maximum_ledger_difference,
        "records": records,
    }


def execute_study(repo: Path) -> int:
    execution_commit, source_hashes, evidence_hashes = verify_run_preflight(repo)
    archived_d1r_rows = load_d1r_diagnostic_rows(repo)
    restriction_harness = validate_fourier_restriction_harness()

    created = utc_now()
    run_id = RUN_PREFIX + created.strftime("%Y%m%dT%H%M%SZ") + "_" + execution_commit[:7]
    run_directory = repo / OUTPUT_ROOT / run_id
    if run_directory.exists():
        raise RuntimeError(f"Stage E run directory already exists: {run_directory}")
    run_directory.mkdir(parents=True, exist_ok=False)

    paths = {name: run_directory / name for name in OUTPUT_FILENAMES}
    counts = {
        "primary_accepted_updates": 0,
        "case_diagnostic_rows": 0,
        "within_pairwise_rows": 0,
        "refinement_rows": 0,
        "projection_control_rows": 0,
        "integrity_summary_rows": 0,
        "anchor_spectra_rows": 0,
        "d1r_reproduction_rows": 0,
        "checkpoint_arrays": 0,
    }
    expected_counts = {
        "primary_accepted_updates": EXPECTED_PRIMARY_UPDATES,
        "case_diagnostic_rows": EXPECTED_CASE_DIAGNOSTIC_ROWS,
        "within_pairwise_rows": EXPECTED_WITHIN_PAIRWISE_ROWS,
        "refinement_rows": EXPECTED_REFINEMENT_ROWS,
        "projection_control_rows": EXPECTED_PROJECTION_CONTROL_ROWS,
        "integrity_summary_rows": EXPECTED_INTEGRITY_SUMMARY_ROWS,
        "anchor_spectra_rows": EXPECTED_ANCHOR_SPECTRA_ROWS,
        "d1r_reproduction_rows": D1R_PRIMARY_EXPECTED_ROWS,
        "checkpoint_arrays": EXPECTED_STATE_ARRAYS,
    }
    metadata: dict[str, object] = {
        "schema_id": "STAGE_E_FOCUSED_REFINEMENT_STUDY_METADATA_V1",
        "run_id": run_id,
        "status": "running",
        "created_utc": utc_text(created),
        "repository": {
            "branch": EXPECTED_BRANCH,
            "execution_commit": execution_commit,
            "design_commit": AUTHORIZED_DESIGN_COMMIT,
            "design_sha256": EXPECTED_DESIGN_SHA256,
            "runner_sha256": sha256_file(repo / RUNNER_NAME),
        },
        "source_hashes": source_hashes,
        "stage_d1r_evidence_hashes": evidence_hashes,
        "configuration": {
            "Re": RE,
            "nu": NU,
            "final_time": FINAL_TIME,
            "case_registry": list(CASE_REGISTRY),
            "trajectory_registry": list(TRAJECTORY_REGISTRY),
            "projection_controls": list(PROJECTION_CONTROLS),
            "common_sample_times": list(COMMON_SAMPLE_TIMES),
            "anchor_times": list(ANCHOR_TIMES),
            "d1r_reproduction_completed_steps": list(D1R_SAMPLE_COMPLETED_STEPS),
            "temporal_adjacencies": list(TEMPORAL_ADJACENCIES),
            "spatial_adjacencies": list(SPATIAL_ADJACENCIES),
        },
        "limits": {
            "filtered_ledger_closure": FILTERED_LEDGER_CLOSURE_LIMIT,
            "unfiltered_ledger_closure": UNFILTERED_LEDGER_CLOSURE_LIMIT,
            "mask_crosscheck": MASK_CROSSCHECK_LIMIT,
            "imaginary_ratio": IMAGINARY_RATIO_LIMIT,
            "order_invariance": ORDER_INVARIANCE_LIMIT,
            "projection_absolute": PROJECTION_ABSOLUTE_LIMIT,
            "projection_relative_fraction": PROJECTION_RELATIVE_FRACTION,
            "baseline_archive_relative": BASELINE_ARCHIVE_RELATIVE_TOLERANCE,
            "baseline_archive_absolute": BASELINE_ARCHIVE_ABSOLUTE_FLOOR,
        },
        "output_contract": {
            "files": list(OUTPUT_FILENAMES),
            "expected_counts": expected_counts,
            "predicted_bytes": PREDICTED_OUTPUT_FILE_BYTES,
            "maximum_file_bytes": MAX_OUTPUT_FILE_BYTES,
        },
        "fourier_restriction_harness": restriction_harness,
        "claims_boundary": {
            "method_ranking": False,
            "best_or_true_method": False,
            "validated_reference_solution": False,
            "reference_candidate_execution": False,
            "general_continuum_convergence": False,
            "turbulence_or_spectral_law": False,
        },
        "progress": {
            "completed_cases": [],
            "active_case": None,
            "last_completed_step": None,
            "counts": counts,
        },
    }
    atomic_write_json(paths["run_metadata.json"], metadata)

    diagnostic_writer: IncrementalCsvWriter | None = None
    pairwise_writer: IncrementalCsvWriter | None = None
    refinement_writer: IncrementalCsvWriter | None = None
    projection_writer: IncrementalCsvWriter | None = None
    integrity_writer: IncrementalCsvWriter | None = None
    spectra_writer: IncrementalCsvWriter | None = None
    writers: list[IncrementalCsvWriter] = []
    checkpoints: dict[tuple[str, str, int], np.ndarray] = {}
    checkpoint_hashes: dict[tuple[str, str, int], str] = {}
    projection_records: list[dict[str, object]] = []
    integrity_rows: list[dict[str, object]] = []
    case_records: list[dict[str, object]] = []
    forcing_records: list[dict[str, object]] = []
    solver_environment_records: list[dict[str, object]] = []
    completed_cases: list[str] = []
    active_case: Mapping[str, object] | None = None
    active_integrity: dict[str, dict[str, object]] | None = None
    integrity_written: set[tuple[str, str]] = set()
    current_step: int | None = None
    c2_canary: dict[str, object] | None = None
    c0_reproduction: dict[str, object] = {
        "selected_rows": 0,
        "accepted_state_hash_matches": 0,
        "float_comparisons": 0,
        "integer_comparisons": 0,
        "string_comparisons": 0,
        "finite_status_comparisons": 0,
        "maximum_absolute_scalar_difference": 0.0,
        "maximum_relative_scalar_difference": 0.0,
        "final_accepted_hashes": {},
        "final_baseline_checkpoint_hashes": {},
        "pass": False,
    }

    try:
        from forcing_budget_diagnostic import forcing_budget_snapshot
        from project.solver.advection_operators import jacobian_arakawa_periodic
        from project.solver.spectral_solver import SpectralSolver

        diagnostic_writer = IncrementalCsvWriter(
            paths["case_diagnostics.csv"], CASE_DIAGNOSTIC_FIELDNAMES
        )
        writers.append(diagnostic_writer)
        pairwise_writer = IncrementalCsvWriter(
            paths["within_case_pairwise.csv"], WITHIN_PAIRWISE_FIELDNAMES
        )
        writers.append(pairwise_writer)
        refinement_writer = IncrementalCsvWriter(
            paths["refinement_comparisons.csv"], REFINEMENT_FIELDNAMES
        )
        writers.append(refinement_writer)
        projection_writer = IncrementalCsvWriter(
            paths["projection_controls.csv"], PROJECTION_CONTROL_FIELDNAMES
        )
        writers.append(projection_writer)
        integrity_writer = IncrementalCsvWriter(
            paths["integrity_summary.csv"], INTEGRITY_SUMMARY_FIELDNAMES
        )
        writers.append(integrity_writer)
        spectra_writer = IncrementalCsvWriter(
            paths["anchor_spectra.csv"], ANCHOR_SPECTRA_FIELDNAMES
        )
        writers.append(spectra_writer)

        for case in CASE_REGISTRY:
            active_case = case
            current_step = 0
            case_id = str(case["case_id"])
            n = int(case["N"])
            dt = float(case["dt"])
            updates = int(case["updates"])
            metadata["progress"] = {
                "completed_cases": list(completed_cases),
                "active_case": case_id,
                "last_completed_step": 0,
                "counts": dict(counts),
            }
            atomic_write_json(paths["run_metadata.json"], metadata)

            solver = SpectralSolver(
                nx=n,
                ny=n,
                Re=RE,
                run_path=run_directory,
                dt=dt,
                steps=updates,
            )
            if (
                int(solver.N) != n
                or float(solver.dt) != dt
                or not math.isclose(float(solver.nu), NU, rel_tol=0.0, abs_tol=1.0e-15)
                or not np.array_equal(solver.w, np.zeros_like(solver.w))
            ):
                raise IntegrityFailure(
                    "solver_configuration",
                    f"solver differs from frozen case {case_id}",
                    case_id=case_id,
                )
            solver_environment_entry = freeze_solver_environment(solver)
            deal_active_modes = int(np.count_nonzero(np.asarray(solver.deal)))
            if deal_active_modes != EXPECTED_DEAL_ACTIVE_MODE_COUNTS[n]:
                raise IntegrityFailure(
                    "dealias_mask_count",
                    f"N={n} active modes={deal_active_modes}",
                    case_id=case_id,
                )
            kx_rc, ky_rc = build_real_compatible_wavenumbers(solver, case_id)
            kx_hash = sha256_array(kx_rc)
            ky_hash = sha256_array(ky_rc)
            forcing, forcing_record = build_rms_matched_multimode_forcing(
                solver, case_id
            )
            forcing_hash = sha256_array(forcing)
            forcing_records.append(forcing_record)
            states = initialize_trajectory_states(np.asarray(solver.w))
            initial_aliases = state_alias_count(states, forcing, kx_rc, ky_rc)
            if initial_aliases:
                raise IntegrityFailure(
                    "initial_state_alias",
                    f"initial state alias count={initial_aliases}",
                    case_id=case_id,
                )
            active_integrity = {
                trajectory_id: new_integrity_accumulator(case, trajectory_id)
                for trajectory_id in TRAJECTORY_IDS
            }
            sample_steps = set(case_sample_steps(case))
            anchor_step_to_index = {
                step: index for index, step in enumerate(case_anchor_steps(case))
            }

            initial_sample = record_common_sample(
                case,
                0,
                states,
                None,
                solver,
                forcing,
                diagnostic_writer,
                pairwise_writer,
                forcing_budget_snapshot=forcing_budget_snapshot,
            )
            counts["case_diagnostic_rows"] += len(TRAJECTORY_IDS)
            counts["within_pairwise_rows"] += len(PRIMARY_PAIRS)
            initial_spectra, initial_control_rows = record_anchor(
                case,
                0,
                states,
                initial_sample,
                solver,
                forcing,
                spectra_writer,
                projection_writer,
                checkpoints,
                checkpoint_hashes,
                jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                kx_rc=kx_rc,
                ky_rc=ky_rc,
            )
            counts["anchor_spectra_rows"] += initial_spectra
            counts["projection_control_rows"] += len(initial_control_rows)
            projection_records.extend(initial_control_rows)
            for accumulator in active_integrity.values():
                accumulator["state_ownership_check_count"] = (
                    int(accumulator["state_ownership_check_count"]) + 1
                )

            progress_stride = max(updates // 10, 1)
            last_progress = time.monotonic()
            for step in range(1, updates + 1):
                current_step = step
                state_hashes = {
                    trajectory_id: sha256_array(states[trajectory_id])
                    for trajectory_id in TRAJECTORY_IDS
                }
                snapshots = {
                    trajectory_id: np.array(
                        states[trajectory_id], dtype=np.float64, copy=True, order="C"
                    )
                    for trajectory_id in TRAJECTORY_IDS
                }
                for snapshot in snapshots.values():
                    snapshot.setflags(write=False)
                if state_alias_count(snapshots, forcing, kx_rc, ky_rc):
                    raise IntegrityFailure(
                        "snapshot_state_alias",
                        "immutable snapshots share memory",
                        case_id=case_id,
                        step=step,
                    )
                previews: dict[str, dict[str, object]] = {}
                for trajectory_id in TRAJECTORY_IDS:
                    previews[trajectory_id] = rk2_preview(
                        str(TRAJECTORY_BY_ID[trajectory_id]["operator_kind"]),
                        solver,
                        snapshots[trajectory_id],
                        forcing,
                        step=step,
                        case_id=case_id,
                        trajectory_id=trajectory_id,
                        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                        kx_rc=kx_rc,
                        ky_rc=ky_rc,
                    )
                cross_aliases = preview_alias_count(
                    snapshots, previews, forcing, kx_rc, ky_rc
                )
                if cross_aliases:
                    for accumulator in active_integrity.values():
                        accumulator["state_alias_count"] = (
                            int(accumulator["state_alias_count"]) + cross_aliases
                        )
                    raise IntegrityFailure(
                        "accepted_state_alias",
                        f"cross-trajectory preview alias count={cross_aliases}",
                        case_id=case_id,
                        step=step,
                    )
                for trajectory_id in TRAJECTORY_IDS:
                    if sha256_array(states[trajectory_id]) != state_hashes[trajectory_id]:
                        active_integrity[trajectory_id]["state_mutation_count"] = (
                            int(active_integrity[trajectory_id]["state_mutation_count"]) + 1
                        )
                        raise IntegrityFailure(
                            "state_mutation",
                            "production state changed before simultaneous acceptance",
                            case_id=case_id,
                            trajectory_id=trajectory_id,
                            step=step,
                        )

                if case_id == "C2_N64_DT00125" and step == updates:
                    c2_canary = evaluate_c2_order_canary(
                        snapshots,
                        previews,
                        solver,
                        forcing,
                        step=step,
                        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                        kx_rc=kx_rc,
                        ky_rc=ky_rc,
                    )
                if case_id == "C0_N64_DT00500" and step == updates:
                    baseline = previews["TRAJ_BASE_FD_ADVECTIVE_V1"]
                    observed_checkpoint_hashes = {
                        "current": sha256_array(baseline["current"]),
                        "stage": sha256_array(baseline["stage"]),
                        "accepted": sha256_array(baseline["accepted"]),
                    }
                    expected_checkpoint_hashes = {
                        "current": EXPECTED_C0_FINAL_BASELINE_CURRENT_SHA256,
                        "stage": EXPECTED_C0_FINAL_BASELINE_STAGE_SHA256,
                        "accepted": EXPECTED_C0_FINAL_BASELINE_ACCEPTED_SHA256,
                    }
                    if observed_checkpoint_hashes != expected_checkpoint_hashes:
                        raise IntegrityFailure(
                            "c0_final_baseline_checkpoint_hashes",
                            "C0 final baseline preview hashes differ from Stage D1R",
                            case_id=case_id,
                            trajectory_id="TRAJ_BASE_FD_ADVECTIVE_V1",
                            step=step,
                            details={
                                "observed": observed_checkpoint_hashes,
                                "expected": expected_checkpoint_hashes,
                            },
                        )
                    c0_reproduction["final_baseline_checkpoint_hashes"] = (
                        observed_checkpoint_hashes
                    )

                states = accept_independent_previews(previews)
                accepted_aliases = state_alias_count(states, forcing, kx_rc, ky_rc)
                if accepted_aliases:
                    for accumulator in active_integrity.values():
                        accumulator["state_alias_count"] = (
                            int(accumulator["state_alias_count"]) + accepted_aliases
                        )
                    raise IntegrityFailure(
                        "accepted_state_alias",
                        f"accepted state alias count={accepted_aliases}",
                        case_id=case_id,
                        step=step,
                    )
                for trajectory_id in TRAJECTORY_IDS:
                    update_integrity_accumulator(
                        active_integrity[trajectory_id], previews[trajectory_id]
                    )
                counts["primary_accepted_updates"] += len(TRAJECTORY_IDS)

                if case_id == "C0_N64_DT00500" and step in D1R_SAMPLE_COMPLETED_STEPS:
                    for trajectory_id in TRAJECTORY_IDS:
                        reproduction_diagnostic = build_diagnostic(
                            case,
                            trajectory_id,
                            states[trajectory_id],
                            previews[trajectory_id],
                            solver,
                            forcing,
                            step=step,
                            forcing_budget_snapshot=forcing_budget_snapshot,
                        )
                        observed_legacy = reproduction_diagnostic["legacy_row"]
                        archived = archived_d1r_rows[(step, trajectory_id)]
                        comparison = compare_d1r_diagnostic_row(
                            observed_legacy, archived
                        )
                        if not bool(comparison["passed"]):
                            raise IntegrityFailure(
                                "c0_d1r_reproduction",
                                "C0 retained trajectory differs from archived D1R",
                                case_id=case_id,
                                trajectory_id=trajectory_id,
                                step=step,
                                details=comparison,
                            )
                        c0_reproduction["selected_rows"] = (
                            int(c0_reproduction["selected_rows"]) + 1
                        )
                        c0_reproduction["accepted_state_hash_matches"] = (
                            int(c0_reproduction["accepted_state_hash_matches"]) + 1
                        )
                        c0_reproduction["float_comparisons"] = (
                            int(c0_reproduction["float_comparisons"])
                            + len(D1R_FLOAT_FIELDS)
                        )
                        c0_reproduction["integer_comparisons"] = (
                            int(c0_reproduction["integer_comparisons"])
                            + len(D1R_INTEGER_FIELDS)
                        )
                        c0_reproduction["string_comparisons"] = (
                            int(c0_reproduction["string_comparisons"])
                            + len(D1R_STRING_FIELDS)
                        )
                        c0_reproduction["finite_status_comparisons"] = (
                            int(c0_reproduction["finite_status_comparisons"]) + 1
                        )
                        c0_reproduction["maximum_absolute_scalar_difference"] = max(
                            float(c0_reproduction["maximum_absolute_scalar_difference"]),
                            float(comparison["maximum_absolute_difference"]),
                        )
                        c0_reproduction["maximum_relative_scalar_difference"] = max(
                            float(c0_reproduction["maximum_relative_scalar_difference"]),
                            float(comparison["maximum_relative_difference"]),
                        )
                    counts["d1r_reproduction_rows"] += len(TRAJECTORY_IDS)

                sampled: dict[str, dict[str, object]] | None = None
                if step in sample_steps:
                    sampled = record_common_sample(
                        case,
                        step,
                        states,
                        previews,
                        solver,
                        forcing,
                        diagnostic_writer,
                        pairwise_writer,
                        forcing_budget_snapshot=forcing_budget_snapshot,
                    )
                    counts["case_diagnostic_rows"] += len(TRAJECTORY_IDS)
                    counts["within_pairwise_rows"] += len(PRIMARY_PAIRS)
                if step in anchor_step_to_index:
                    if sampled is None:
                        raise RuntimeError("anchor step is absent from common sample schedule")
                    anchor_index = anchor_step_to_index[step]
                    anchor_aliases = state_alias_count(states, forcing, kx_rc, ky_rc)
                    if anchor_aliases:
                        raise IntegrityFailure(
                            "anchor_state_alias",
                            f"anchor state alias count={anchor_aliases}",
                            case_id=case_id,
                            step=step,
                        )
                    spectra_rows, control_rows = record_anchor(
                        case,
                        anchor_index,
                        states,
                        sampled,
                        solver,
                        forcing,
                        spectra_writer,
                        projection_writer,
                        checkpoints,
                        checkpoint_hashes,
                        jacobian_arakawa_periodic=jacobian_arakawa_periodic,
                        kx_rc=kx_rc,
                        ky_rc=ky_rc,
                    )
                    counts["anchor_spectra_rows"] += spectra_rows
                    counts["projection_control_rows"] += len(control_rows)
                    projection_records.extend(control_rows)
                    for accumulator in active_integrity.values():
                        accumulator["state_ownership_check_count"] = (
                            int(accumulator["state_ownership_check_count"]) + 1
                        )
                    for writer in writers:
                        writer.flush()
                    metadata["progress"] = {
                        "completed_cases": list(completed_cases),
                        "active_case": case_id,
                        "last_completed_step": step,
                        "counts": dict(counts),
                    }
                    atomic_write_json(paths["run_metadata.json"], metadata)

                now = time.monotonic()
                if (
                    step == updates
                    or (step % progress_stride == 0 and now - last_progress >= PROGRESS_INTERVAL_SECONDS)
                ):
                    print(
                        "progress",
                        f"case={case_id}",
                        f"step={step}/{updates}",
                        f"t={step * dt:.5f}",
                        f"Z_base={enstrophy(states[TRAJECTORY_IDS[0]]):.6e}",
                    )
                    last_progress = now

            solver_environment_exit = freeze_solver_environment(solver)
            environment_unchanged = (
                solver_environment_exit == solver_environment_entry
            )
            forcing_unchanged = sha256_array(forcing) == forcing_hash
            wavenumbers_unchanged = (
                sha256_array(kx_rc) == kx_hash and sha256_array(ky_rc) == ky_hash
            )
            if not environment_unchanged:
                raise IntegrityFailure(
                    "solver_environment_mutation",
                    "solver environment changed during case",
                    case_id=case_id,
                )
            if not forcing_unchanged:
                raise IntegrityFailure(
                    "forcing_mutation", "forcing bytes changed", case_id=case_id
                )
            if not wavenumbers_unchanged:
                raise IntegrityFailure(
                    "real_compatible_wavenumber_mutation",
                    "local real-compatible wavenumbers changed",
                    case_id=case_id,
                )
            for trajectory_id in TRAJECTORY_IDS:
                row = build_integrity_summary_row(
                    active_integrity[trajectory_id],
                    solver_environment_unchanged=environment_unchanged,
                    forcing_unchanged=forcing_unchanged,
                    local_wavenumbers_unchanged=wavenumbers_unchanged,
                )
                if not bool(row["integrity_pass"]):
                    raise IntegrityFailure(
                        "integrity_summary",
                        f"aggregate integrity failed: {case_id}/{trajectory_id}",
                        case_id=case_id,
                        trajectory_id=trajectory_id,
                    )
                integrity_writer.write(row)
                integrity_rows.append(row)
                integrity_written.add((case_id, trajectory_id))
                counts["integrity_summary_rows"] += 1
            solver_environment_records.append(
                {
                    "case_id": case_id,
                    "entry_hashes": solver_environment_entry,
                    "exit_hashes": solver_environment_exit,
                    "unchanged": environment_unchanged,
                    "dealias_mask_sha256": sha256_array(np.asarray(solver.deal)),
                    "dealias_active_mode_count": deal_active_modes,
                    "real_compatible_kx_sha256": kx_hash,
                    "real_compatible_ky_sha256": ky_hash,
                }
            )
            case_records.append(
                {
                    "case_id": case_id,
                    "N": n,
                    "dt": dt,
                    "updates": updates,
                    "status": "PASS",
                    "final_state_hashes": {
                        trajectory_id: sha256_array(states[trajectory_id])
                        for trajectory_id in TRAJECTORY_IDS
                    },
                }
            )
            if case_id == "C0_N64_DT00500":
                final_hashes = {
                    trajectory_id: sha256_array(states[trajectory_id])
                    for trajectory_id in TRAJECTORY_IDS
                }
                if final_hashes != EXPECTED_C0_FINAL_ACCEPTED_SHA256:
                    raise IntegrityFailure(
                        "c0_final_accepted_hashes",
                        "C0 final accepted hashes differ from Stage D1R",
                        case_id=case_id,
                        details={
                            "observed": final_hashes,
                            "expected": EXPECTED_C0_FINAL_ACCEPTED_SHA256,
                        },
                    )
                c0_reproduction["final_accepted_hashes"] = final_hashes
                c0_reproduction["pass"] = bool(
                    int(c0_reproduction["selected_rows"])
                    == D1R_PRIMARY_EXPECTED_ROWS
                    and int(c0_reproduction["accepted_state_hash_matches"])
                    == D1R_PRIMARY_EXPECTED_ROWS
                    and int(c0_reproduction["float_comparisons"])
                    == D1R_PRIMARY_EXPECTED_ROWS * len(D1R_FLOAT_FIELDS)
                )
                if not bool(c0_reproduction["pass"]):
                    raise IntegrityFailure(
                        "c0_reproduction_count",
                        "C0 reproduction comparison counts are incomplete",
                        case_id=case_id,
                    )
            completed_cases.append(case_id)
            metadata["progress"] = {
                "completed_cases": list(completed_cases),
                "active_case": None,
                "last_completed_step": updates,
                "counts": dict(counts),
            }
            atomic_write_json(paths["run_metadata.json"], metadata)
            active_integrity = None
            active_case = None
            current_step = None

        forcing_cross_grid = verify_forcing_cross_grid_equivalence(forcing_records)
        if c2_canary is None:
            raise IntegrityFailure("order_canary_missing", "C2 final canary is absent")
        if len(checkpoints) != EXPECTED_STATE_ARRAYS:
            raise IntegrityFailure(
                "checkpoint_count",
                f"checkpoints={len(checkpoints)}, expected={EXPECTED_STATE_ARRAYS}",
            )
        maximum_checkpoint_mean_free_rms = max(
            field_rms(mean_free(value)) for value in checkpoints.values()
        )
        roundoff_guard = (
            FLOOR_SAFETY_MULTIPLIER
            * np.finfo(np.float64).eps
            * max(maximum_checkpoint_mean_free_rms, np.finfo(np.float64).tiny)
        )
        measured_floor = max(
            float(restriction_harness["maximum_supported_error"]),
            float(restriction_harness["maximum_removed_error"]),
            float(restriction_harness["maximum_imaginary_rms"]),
            float(c2_canary["maximum_absolute_mean_free_difference"]),
            roundoff_guard,
        )
        numerical_floor = {
            "restriction_supported_component": restriction_harness[
                "maximum_supported_error"
            ],
            "restriction_removed_component": restriction_harness[
                "maximum_removed_error"
            ],
            "restriction_imaginary_component": restriction_harness[
                "maximum_imaginary_rms"
            ],
            "order_canary_repeatability_component": c2_canary[
                "maximum_absolute_mean_free_difference"
            ],
            "roundoff_guard_component": roundoff_guard,
            "maximum_checkpoint_mean_free_vorticity_rms": (
                maximum_checkpoint_mean_free_rms
            ),
            "measured_absolute_floor": measured_floor,
        }
        refinement_rows, refinement_groups = build_refinement_rows_and_groups(
            checkpoints, measured_floor
        )
        for row in refinement_rows:
            refinement_writer.write(row)
        counts["refinement_rows"] = len(refinement_rows)
        refinement_summary = build_refinement_and_resolution_summary(
            refinement_groups, checkpoints, measured_floor
        )
        checkpoint_arrays = write_state_checkpoints(
            paths["state_checkpoints.npz"],
            checkpoints,
            checkpoint_hashes,
            require_complete=True,
        )
        counts["checkpoint_arrays"] = checkpoint_arrays
        for writer in writers:
            writer.close()

        projection_summary = []
        for control in PROJECTION_CONTROLS:
            control_id = str(control["control_id"])
            selected = [
                row for row in projection_records if row["control_id"] == control_id
            ]
            projection_summary.append(
                {
                    "control_id": control_id,
                    "rows": len(selected),
                    "transport_failures": sum(
                        row["transport_status"] == "FAIL" for row in selected
                    ),
                    "accepted_update_failures": sum(
                        row["accepted_update_status"] == "FAIL" for row in selected
                    ),
                    "descriptively_negligible_rows": sum(
                        bool(row["descriptively_negligible"]) for row in selected
                    ),
                    "transport_and_accepted_update_interpreted_separately": True,
                }
            )
        maximum_integrity = {
            "maximum_normalized_unfiltered_closure": max(
                float(row["maximum_normalized_unfiltered_closure"])
                for row in integrity_rows
            ),
            "maximum_normalized_filtered_closure": max(
                float(row["maximum_normalized_filtered_closure"])
                for row in integrity_rows
            ),
            "maximum_normalized_mask_crosscheck": max(
                float(row["maximum_normalized_mask_crosscheck"])
                for row in integrity_rows
            ),
            "maximum_imaginary_ratio": max(
                float(row["maximum_imaginary_ratio"]) for row in integrity_rows
            ),
            "failure_count": sum(int(row["failure_count"]) for row in integrity_rows),
        }
        completed = utc_text()
        summary = {
            "schema_id": "STAGE_E_FOCUSED_REFINEMENT_STUDY_SUMMARY_V1",
            "run_id": run_id,
            "status": "PASS",
            "created_utc": metadata["created_utc"],
            "completed_utc": completed,
            "expected_counts": expected_counts,
            "observed_counts": counts,
            "case_completion": case_records,
            "global_integrity": maximum_integrity,
            "c0_d1r_reproduction": c0_reproduction,
            "c2_order_canary": c2_canary,
            "numerical_floor": numerical_floor,
            "refinement_and_resolution": refinement_summary,
            "projection_controls": projection_summary,
            "projection_transport_is_not_trajectory_importance": True,
            "reference_candidate_executed": False,
            "validated_reference": False,
            "method_ranking_produced": False,
            "automatic_escalation": False,
        }
        atomic_write_json(paths["stage_e_summary.json"], summary)
        metadata.update(
            {
                "status": "completed",
                "completed_utc": completed,
                "forcing_records": forcing_records,
                "forcing_cross_grid_equivalence": forcing_cross_grid,
                "solver_environments": solver_environment_records,
                "c0_d1r_reproduction": c0_reproduction,
                "c2_order_canary": c2_canary,
                "numerical_floor": numerical_floor,
                "observed_counts": counts,
                "progress": {
                    "completed_cases": list(completed_cases),
                    "active_case": None,
                    "last_completed_step": None,
                    "counts": dict(counts),
                },
            }
        )
        atomic_write_json(paths["run_metadata.json"], metadata)
        inventory_sha256 = write_inventory(
            run_directory, paths["file_inventory.csv"]
        )
        verify_successful_output_contract(
            run_directory, counts, checkpoint_arrays
        )
        print()
        print("=" * 72)
        print("STAGE E FOCUSED RESOLUTION/TIMESTEP STUDY: PASS")
        print("=" * 72)
        print(f"Cases: {len(completed_cases)} / {len(CASE_REGISTRY)}")
        print(f"Primary accepted updates: {counts['primary_accepted_updates']}")
        print(f"C0 D1R rows reproduced: {counts['d1r_reproduction_rows']}")
        print(f"Diagnostics / pairwise: {counts['case_diagnostic_rows']} / {counts['within_pairwise_rows']}")
        print(f"Refinement / projection: {counts['refinement_rows']} / {counts['projection_control_rows']}")
        print(f"Integrity / spectra: {counts['integrity_summary_rows']} / {counts['anchor_spectra_rows']}")
        print(f"Checkpoint arrays: {checkpoint_arrays}")
        print(f"Run directory: {run_directory}")
        print(f"File inventory SHA256: {inventory_sha256}")
        print("Reference-candidate execution: NO")
        print("Automatic escalation: NO")
        return 0
    except Exception as error:
        if isinstance(error, IntegrityFailure):
            failed_gate = error.gate
            failed_case = error.case_id or (
                str(active_case["case_id"]) if active_case is not None else None
            )
            failed_trajectory = error.trajectory_id
            failed_step = error.step if error.step is not None else current_step
            details = error.details
            if (
                active_integrity is not None
                and failed_trajectory in active_integrity
            ):
                mark_integrity_failure(
                    active_integrity[str(failed_trajectory)], failed_gate
                )
        else:
            failed_gate = "unexpected_exception"
            failed_case = (
                str(active_case["case_id"]) if active_case is not None else None
            )
            failed_trajectory = None
            failed_step = current_step
            details = {}
        failure_snapshot = {
            "error_type": type(error).__name__,
            "message": str(error),
            "failed_gate": failed_gate,
            "failed_case": failed_case,
            "failed_trajectory": failed_trajectory,
            "failed_step": failed_step,
            "details": details,
            "completed_cases": list(completed_cases),
            "partial_counts": dict(counts),
            "partial_checkpoint_arrays": len(checkpoints),
            "automatic_retry": False,
        }
        if integrity_writer is not None and active_integrity is not None and active_case is not None:
            active_case_id = str(active_case["case_id"])
            for trajectory_id in TRAJECTORY_IDS:
                key = (active_case_id, trajectory_id)
                if key in integrity_written:
                    continue
                row = build_integrity_summary_row(
                    active_integrity[trajectory_id],
                    solver_environment_unchanged=False,
                    forcing_unchanged=False,
                    local_wavenumbers_unchanged=False,
                )
                integrity_writer.write(row)
                integrity_written.add(key)
                counts["integrity_summary_rows"] += 1
        for writer in writers:
            try:
                writer.close()
            except Exception:
                pass
        csv_contracts = {
            "case_diagnostics.csv": CASE_DIAGNOSTIC_FIELDNAMES,
            "within_case_pairwise.csv": WITHIN_PAIRWISE_FIELDNAMES,
            "refinement_comparisons.csv": REFINEMENT_FIELDNAMES,
            "projection_controls.csv": PROJECTION_CONTROL_FIELDNAMES,
            "integrity_summary.csv": INTEGRITY_SUMMARY_FIELDNAMES,
            "anchor_spectra.csv": ANCHOR_SPECTRA_FIELDNAMES,
        }
        for name, fieldnames in csv_contracts.items():
            if not paths[name].exists():
                fallback_writer = IncrementalCsvWriter(paths[name], fieldnames)
                fallback_writer.close()
        partial_csv_count_keys = {
            "case_diagnostics.csv": "case_diagnostic_rows",
            "within_case_pairwise.csv": "within_pairwise_rows",
            "refinement_comparisons.csv": "refinement_rows",
            "projection_controls.csv": "projection_control_rows",
            "integrity_summary.csv": "integrity_summary_rows",
            "anchor_spectra.csv": "anchor_spectra_rows",
        }
        for name, count_key in partial_csv_count_keys.items():
            counts[count_key] = csv_data_row_count(paths[name])
        try:
            counts["checkpoint_arrays"] = write_state_checkpoints(
                paths["state_checkpoints.npz"],
                checkpoints,
                checkpoint_hashes,
                require_complete=False,
            )
        except Exception as checkpoint_error:
            np.savez_compressed(paths["state_checkpoints.npz"])
            failure_snapshot["checkpoint_preservation_error"] = str(checkpoint_error)
            counts["checkpoint_arrays"] = 0
        failed_summary = {
            "schema_id": "STAGE_E_FOCUSED_REFINEMENT_STUDY_SUMMARY_V1",
            "run_id": run_id,
            "status": "FAILED",
            "created_utc": metadata["created_utc"],
            "failed_utc": utc_text(),
            "expected_counts": expected_counts,
            "observed_counts": counts,
            "failure_snapshot": failure_snapshot,
            "reference_candidate_executed": False,
            "method_ranking_produced": False,
            "automatic_retry": False,
        }
        atomic_write_json(paths["stage_e_summary.json"], failed_summary)
        metadata.update(
            {
                "status": "failed",
                "failed_utc": failed_summary["failed_utc"],
                "failure_snapshot": failure_snapshot,
                "forcing_records": forcing_records,
                "solver_environments": solver_environment_records,
                "observed_counts": counts,
                "progress": {
                    "completed_cases": list(completed_cases),
                    "active_case": failed_case,
                    "last_completed_step": failed_step,
                    "counts": dict(counts),
                },
            }
        )
        atomic_write_json(paths["run_metadata.json"], metadata)
        try:
            inventory_sha256 = write_inventory(
                run_directory, paths["file_inventory.csv"]
            )
        except Exception as inventory_error:
            inventory_sha256 = "UNAVAILABLE"
            print(f"inventory preservation error: {inventory_error}")
        print()
        print("STAGE E FOCUSED RESOLUTION/TIMESTEP STUDY: FAILED")
        print(f"Failed gate: {failed_gate}")
        print(f"Failed case: {failed_case}")
        print(f"Failed trajectory: {failed_trajectory}")
        print(f"Failed step: {failed_step}")
        print(f"Partial evidence: {run_directory}")
        print(f"Partial inventory SHA256: {inventory_sha256}")
        print("Do not rerun automatically.")
        return 1


# ============================================================================
# Read-only static inspection and CLI
# ============================================================================

def containing_function(
    node: ast.AST, parent_by_node: Mapping[ast.AST, ast.AST]
) -> str | None:
    current: ast.AST | None = node
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
        current = parent_by_node.get(current)
    return None


def root_name(node: ast.AST) -> str | None:
    current = node
    while isinstance(current, ast.Attribute):
        current = current.value
    return current.id if isinstance(current, ast.Name) else None


def inspect_source_tree(tree: ast.Module, source: str) -> dict[str, object]:
    parent_by_node: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parent_by_node[child] = parent

    allowed_top_level = (
        ast.Expr,
        ast.Import,
        ast.ImportFrom,
        ast.Assign,
        ast.AnnAssign,
        ast.FunctionDef,
        ast.ClassDef,
        ast.If,
    )
    unexpected_top_level = [
        type(node).__name__
        for node in tree.body
        if not isinstance(node, allowed_top_level)
    ]
    if unexpected_top_level:
        raise RuntimeError(f"unexpected top-level nodes: {unexpected_top_level}")

    project_imports: list[tuple[str, str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "forcing_budget_diagnostic" or module.startswith("project"):
                project_imports.append(
                    (module, containing_function(node, parent_by_node))
                )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "forcing_budget_diagnostic" or alias.name.startswith(
                    "project"
                ):
                    project_imports.append(
                        (alias.name, containing_function(node, parent_by_node))
                    )
    expected_import_modules = {
        "forcing_budget_diagnostic",
        "project.solver.advection_operators",
        "project.solver.spectral_solver",
    }
    if (
        {module for module, _ in project_imports} != expected_import_modules
        or any(function != "execute_study" for _, function in project_imports)
    ):
        raise RuntimeError(f"project import boundary failed: {project_imports}")

    solver_constructor_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "SpectralSolver"
    ]
    if (
        len(solver_constructor_calls) != 1
        or containing_function(solver_constructor_calls[0], parent_by_node)
        != "execute_study"
    ):
        raise RuntimeError(
            f"SpectralSolver constructor sites={len(solver_constructor_calls)}, expected=1"
        )
    solver_run_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "run"
        and root_name(node.func.value) == "solver"
    ]
    if solver_run_calls:
        raise RuntimeError("protected solver.run() call is present")
    if any(
        isinstance(node, ast.Name) and node.id == "SelectableAdvectionSolver"
        for node in ast.walk(tree)
    ):
        raise RuntimeError("SelectableAdvectionSolver symbol is present")
    for node in ast.walk(tree):
        targets: list[ast.AST] = []
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            else:
                targets = [node.target]
        for target in targets:
            for selected in ast.walk(target):
                if (
                    isinstance(selected, ast.Attribute)
                    and selected.attr in {"kx", "ky"}
                    and root_name(selected.value) == "solver"
                ):
                    raise RuntimeError("assignment to solver kx/ky is present")

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required_functions = {
        "execute_study",
        "rk2_preview",
        "fourier_restrict",
        "validate_fourier_restriction_harness",
        "load_d1r_diagnostic_rows",
        "compare_d1r_diagnostic_row",
        "build_refinement_rows_and_groups",
        "build_projection_control_rows",
        "state_alias_count",
        "write_state_checkpoints",
        "write_inventory",
        "inspect_runner",
        "main",
    }
    missing_functions = sorted(required_functions - set(functions))
    if missing_functions:
        raise RuntimeError(f"required functions missing: {missing_functions}")
    reference_execution_functions = sorted(
        name
        for name in functions
        if "reference_candidate" in name.lower()
        or name.lower().startswith("execute_reference")
    )
    if reference_execution_functions:
        raise RuntimeError(
            f"reference-candidate execution functions present: {reference_execution_functions}"
        )

    rk2_node = functions["rk2_preview"]
    transport_calls = [
        node
        for node in ast.walk(rk2_node)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "compute_transport"
    ]
    if len(transport_calls) != 2:
        raise RuntimeError(
            f"RK2 compute_transport calls={len(transport_calls)}, expected=2"
        )
    rk2_source = ast.unparse(rk2_node)
    required_rk2_fragments = (
        "current + solver.dt * total_1",
        "current + 0.5 * solver.dt * (total_1 + total_2)",
        "np.fft.ifft2(unfiltered_hat * solver.deal)",
        "n ** 4",
        "-mask_loss_physical / solver.dt",
    )
    missing_rk2 = [item for item in required_rk2_fragments if item not in rk2_source]
    if missing_rk2:
        raise RuntimeError(f"RK2 contract fragments missing: {missing_rk2}")

    nyquist_source = ast.unparse(functions["build_real_compatible_wavenumbers"])
    if (
        nyquist_source.count("copy=True") < 2
        or "kx_rc[x_mask] = 0.0" not in nyquist_source
        or "ky_rc[y_mask] = 0.0" not in nyquist_source
    ):
        raise RuntimeError("local Nyquist-zeroed copy contract is incomplete")
    restriction_source = ast.unparse(functions["fourier_restrict"])
    required_restriction_fragments = (
        "np.fft.fft2(source) / float(source_n ** 2)",
        "target_coefficients * float(target_n ** 2)",
        "abs(int(ky)) >= half",
        "abs(int(kx)) >= half",
        "outside = ~retained_source",
    )
    missing_restriction = [
        item for item in required_restriction_fragments
        if item not in restriction_source
    ]
    if missing_restriction:
        raise RuntimeError(
            f"Fourier restriction contract fragments missing: {missing_restriction}"
        )
    execution_source = ast.unparse(functions["execute_study"])
    if execution_source.count("state_alias_count(") < 4:
        raise RuntimeError("state ownership is not checked at all required boundaries")
    if "evaluate_c2_order_canary(" not in execution_source:
        raise RuntimeError("C2 final forward/reverse canary is not invoked")
    if "validate_fourier_restriction_harness()" not in execution_source:
        raise RuntimeError("restriction harness is not invoked in run preflight")

    local_calls: dict[str, set[str]] = {}
    for name, function in functions.items():
        local_calls[name] = {
            node.func.id
            for node in ast.walk(function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in functions
        }
    reachable = {"inspect_runner"}
    frontier = ["inspect_runner"]
    while frontier:
        selected = frontier.pop()
        for called in local_calls.get(selected, set()):
            if called not in reachable:
                reachable.add(called)
                frontier.append(called)
    forbidden_from_inspection = {
        "execute_study",
        "IncrementalCsvWriter",
        "atomic_write_text",
        "atomic_write_json",
        "build_rms_matched_multimode_forcing",
        "compute_transport",
        "rk2_preview",
        "fourier_restrict",
        "validate_fourier_restriction_harness",
        "build_projection_control_rows",
        "write_state_checkpoints",
        "write_inventory",
    }
    reached_forbidden = sorted(reachable & forbidden_from_inspection)
    if reached_forbidden:
        raise RuntimeError(
            f"inspection call graph reaches execution/writes: {reached_forbidden}"
        )
    return {
        "project_imports": len(project_imports),
        "solver_constructor_sites": len(solver_constructor_calls),
        "solver_run_calls": len(solver_run_calls),
        "inspection_reachable_functions": len(reachable),
        "rk2_transport_calls": len(transport_calls),
    }


def inspect_runner(repo: Path) -> int:
    runner_path = repo / RUNNER_NAME
    source_bytes = runner_path.read_bytes()
    if b"\r\n" in source_bytes:
        raise RuntimeError("runner must use LF line endings during inspection")
    source = source_bytes.decode("utf-8")
    tree = ast.parse(source, filename=RUNNER_NAME)
    compile(tree, RUNNER_NAME, "exec")

    design_commit = verify_inspection_repository_state(repo)
    source_identities = verify_frozen_sources(repo)
    validate_frozen_matrix()
    assert_all_headers_unique()
    ast_results = inspect_source_tree(tree, source)

    if tuple(case_sample_steps(CASE_REGISTRY[0])) != tuple(range(0, 3061, 10)):
        raise RuntimeError("C0 common schedule mismatch")
    if tuple(case_sample_steps(CASE_REGISTRY[1])) != tuple(range(0, 6121, 20)):
        raise RuntimeError("C1 common schedule mismatch")
    for case in CASE_REGISTRY[2:]:
        if tuple(case_sample_steps(case)) != tuple(range(0, 12241, 40)):
            raise RuntimeError(f"fine common schedule mismatch: {case['case_id']}")
    if D1R_SAMPLE_COMPLETED_STEPS != tuple(range(1, 3052, 10)) + (3060,):
        raise RuntimeError("D1R offset reproduction schedule mismatch")
    if any(
        control["control_kind"]
        in {trajectory["operator_kind"] for trajectory in TRAJECTORY_REGISTRY}
        for control in PROJECTION_CONTROLS
    ):
        raise RuntimeError("projected sparse controls appear in primary registry")
    derived_spectrum_rows = sum(
        (
            int(math.floor(math.sqrt(2.0 * (int(case["N"]) // 2) ** 2)))
            + 1
        )
        * len(TRAJECTORY_IDS)
        * len(ANCHOR_TIMES)
        for case in CASE_REGISTRY
    )
    if derived_spectrum_rows != EXPECTED_ANCHOR_SPECTRA_ROWS:
        raise RuntimeError(
            f"derived spectrum rows={derived_spectrum_rows}, "
            f"expected={EXPECTED_ANCHOR_SPECTRA_ROWS}"
        )
    derived_counts = {
        "primary_updates": sum(
            int(case["updates"]) * len(TRAJECTORY_IDS) for case in CASE_REGISTRY
        ),
        "diagnostics": len(CASE_REGISTRY) * len(TRAJECTORY_IDS) * 307,
        "pairwise": len(CASE_REGISTRY) * len(PRIMARY_PAIRS) * 307,
        "refinement": 2 * 2 * len(TRAJECTORY_IDS) * len(ANCHOR_TIMES),
        "projection": len(CASE_REGISTRY) * len(PROJECTION_CONTROLS) * len(ANCHOR_TIMES),
        "integrity": len(CASE_REGISTRY) * len(TRAJECTORY_IDS),
        "spectra": derived_spectrum_rows,
        "checkpoints": len(CASE_REGISTRY) * len(TRAJECTORY_IDS) * len(ANCHOR_TIMES),
    }
    expected_derived = {
        "primary_updates": EXPECTED_PRIMARY_UPDATES,
        "diagnostics": EXPECTED_CASE_DIAGNOSTIC_ROWS,
        "pairwise": EXPECTED_WITHIN_PAIRWISE_ROWS,
        "refinement": EXPECTED_REFINEMENT_ROWS,
        "projection": EXPECTED_PROJECTION_CONTROL_ROWS,
        "integrity": EXPECTED_INTEGRITY_SUMMARY_ROWS,
        "spectra": EXPECTED_ANCHOR_SPECTRA_ROWS,
        "checkpoints": EXPECTED_STATE_ARRAYS,
    }
    if derived_counts != expected_derived:
        raise RuntimeError(
            f"derived count mismatch: observed={derived_counts}, expected={expected_derived}"
        )
    if tuple(sorted(PREDICTED_OUTPUT_FILE_BYTES)) != tuple(sorted(OUTPUT_FILENAMES)):
        raise RuntimeError("predicted/output file sets differ")
    if any(
        size >= MAX_OUTPUT_FILE_BYTES
        for size in PREDICTED_OUTPUT_FILE_BYTES.values()
    ):
        raise RuntimeError("a predicted output is not below 40 MB")

    runner_hash = sha256_bytes(source_bytes)
    line_count = len(source.splitlines())
    print()
    print("=" * 72)
    print("STAGE E FOCUSED REFINEMENT RUNNER STATIC INSPECTION: PASS")
    print("=" * 72)
    print(f"File: {RUNNER_NAME}")
    print(f"Lines / bytes: {line_count} / {len(source_bytes)}")
    print(f"SHA256: {runner_hash}")
    print(f"Design commit: {design_commit}")
    print(f"Frozen source identities: {len(source_identities)} VERIFIED")
    print("Matrix: 5 cases / 5 primary trajectories / 2 sparse controls")
    print(
        "Counts: "
        f"{EXPECTED_PRIMARY_UPDATES} updates; "
        f"{EXPECTED_CASE_DIAGNOSTIC_ROWS} diagnostics; "
        f"{EXPECTED_WITHIN_PAIRWISE_ROWS} pairwise; "
        f"{EXPECTED_REFINEMENT_ROWS} refinement"
    )
    print(
        "Evidence: "
        f"{EXPECTED_PROJECTION_CONTROL_ROWS} controls; "
        f"{EXPECTED_INTEGRITY_SUMMARY_ROWS} integrity; "
        f"{EXPECTED_ANCHOR_SPECTRA_ROWS} spectra; "
        f"{EXPECTED_STATE_ARRAYS} checkpoints"
    )
    print(
        "AST: project imports run-local; "
        f"{ast_results['solver_constructor_sites']} solver constructor site; "
        "no solver.run()"
    )
    print("Outputs: 10 EXACT; each predicted below 40 MB")
    print("Reference-candidate execution path: ABSENT")
    print("Project modules imported: NO")
    print("Solver constructed / numerical timesteps / files written: NO / NO / NO")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Controlled Stage E focused refinement study"
    )
    parser.add_argument("command", choices=("inspect", "run"))
    arguments = parser.parse_args(argv)
    repo = Path(__file__).resolve().parent
    if arguments.command == "inspect":
        return inspect_runner(repo)
    return execute_study(repo)


if __name__ == "__main__":
    raise SystemExit(main())
