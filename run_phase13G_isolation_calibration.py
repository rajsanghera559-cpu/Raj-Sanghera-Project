"""Controlled Phase 13G.3 exploratory isolation-calibration runner.

Implemented and statically audited under the archived Phase 13G.2 design.
This file must not execute until a separate Phase 13G.3 gate supplies every
exact authorization variable. It creates exploratory calibration evidence only.
It calculates no observed order and makes no convergence or physical claim.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import traceback
from types import ModuleType, SimpleNamespace
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


RUNNER_VERSION = "PHASE13G_ISOLATION_CALIBRATION_RUNNER_V1"
EXECUTION_TOKEN = "PHASE13G_EXECUTE_AUTHORIZED_ISOLATION_CALIBRATION_V1"
EXPECTED_BRANCH = "phase4_validation"
EXPECTED_TAG_PREFIX = "v0.5.62-phase13G3B-calibration-runner-signature-remediation"

REPO_ROOT = Path(__file__).resolve().parent
RUNNER_PATH = REPO_ROOT / "run_phase13G_isolation_calibration.py"
OUTPUT_ROOT = REPO_ROOT / "experiments" / "verification" / "phase13"

RE = 1000.0
NU = 0.001
T0 = 0.0
FINAL_TIME = 0.008
METHODS = ("fd_centered", "pseudo_spectral", "arakawa")
O1_ID = "O1_BANDLIMITED_TWO_MODE_V1"
O2_ID = "O2_ANALYTIC_BROAD_SPECTRUM_V1"
L_ID = "L_EQUAL_EIGENVALUE_DECAY_V1"
M_ID = "M_TWO_RATE_NONLINEAR_MMS_V1"

EXPECTED_CASES = 77
EXPECTED_STEPS = 850
EXPECTED_ADVECTION = 1632
EXPECTED_DIFFUSION = 1700
EXPECTED_SOURCE = 1608
EXPECTED_FORCING = 0
EXPECTED_MASKS = 850
EXPECTED_FILES = 390

RUN_ID_RE = re.compile(
    r"^phase13G_calibration_(\d{8}T\d{6}Z)_([0-9a-f]{7})$"
)
SHA256_RE = re.compile(r"^[0-9A-F]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

PINNED_HASHES: Mapping[str, str] = {
    "PHASE13G2_EXPLORATORY_ISOLATION_CALIBRATION_DESIGN_AND_AUTHORIZATION.md":
        "688B4FDAEF4776CD87EB8EF1FBCD4F09D5BF639B40B0F23BB0A0AF205A3E8F13",
    "PHASE13G1_PHASE13F_CALIBRATION_GAP_REVIEW.md":
        "170258780D8EDA00E5E3FA08351C9E203F5E27BEAE92C5D0C00D0CF777689028",
    "PHASE13B_BENCHMARK_AND_CONTINUOUS_EQUATION_SPECIFICATION.md":
        "6FC0685AC0225F542C181174ECC5940CE1C1163F2CE90B15301AEF46D5CE7875",
    "PHASE13C_REFERENCE_SOLUTION_AND_SOURCE_TERM_AUDIT_REPORT.md":
        "ABEF31DF4F67913EB418C816DBB665531C5F2C854EB4E300B68CF9F45CA5A306",
    "PHASE13D_EXTERNAL_VERIFICATION_HARNESS_DESIGN.md":
        "2F014D33623C5D7184F65EBF4E3CA34F4BAD13501BED0A66DC72D33FB1A90A5E",
    "run_phase13F_verification_pilot.py":
        "DB9396579912AC8A02E756B92050E60884259EF78791E47DA3B6A10A24F862FA",
    "project/solver/spectral_solver.py":
        "1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1",
    "project/solver/selectable_advection_solver.py":
        "5EDA93A2E9358D81927BD9EE247F305E6DBC94367B351801913FFEAA2D7C5891",
    "project/solver/advection_operators.py":
        "2C86465570DDF095D5B0A9B7F67E6E78A89D14F82933FA983D91156DD0F76409",
    "project/verification/phase13_exact_references.py":
        "6904C78E54948D07C92173C8B313844B28C92209B4F61CE447FFC29E15DA4EED",
    "project/verification/phase13_external_harness.py":
        "CDB6DBC249EA2DFF27E729AF0CF3D5C545C48BE57624CC59842B3222DAA752A2",
    "project/verification/phase13_output_schema.py":
        "6899C611C56E8154435BB6C042B520A13B466CD10042DE5325C7F9EF634FB11F",
}

AUTHORIZATION_VARIABLES = (
    "PHASE13G_EXECUTION_TOKEN",
    "PHASE13G_AUTHORIZED_COMMIT",
    "PHASE13G_AUTHORIZED_TAG",
    "PHASE13G_RUNNER_SHA256",
    "PHASE13G_RUN_ID",
)


@dataclass(frozen=True, slots=True)
class CalibrationCase:
    benchmark_id: str
    track: str
    N: int
    dt: float
    n_steps: int
    method: str | None
    requested_final_time: float

    @property
    def key(self) -> tuple[str, int, float, int, str | None]:
        return (self.track, self.N, self.dt, self.n_steps, self.method)


@dataclass(frozen=True, slots=True)
class PreflightContext:
    head: str
    branch: str
    tag: str
    run_id: str
    run_directory: Path
    runner_sha256: str
    timestamp_utc: str


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    case_writes: tuple[Any, ...]
    records: tuple[Mapping[str, object], ...]
    advection: int
    diffusion: int
    source: int
    forcing: int
    masks: int
    steps: int


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True, shell=False,
        text=True, capture_output=True, encoding="utf-8", errors="strict"
    ).stdout.rstrip("\r\n")


def _require_environment(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Required environment variable is absent: {name}")
    return value.strip()


def _active_git_operation() -> str | None:
    git_dir = REPO_ROOT / ".git"
    checks = {
        "merge": git_dir / "MERGE_HEAD",
        "cherry-pick": git_dir / "CHERRY_PICK_HEAD",
        "revert": git_dir / "REVERT_HEAD",
        "rebase-merge": git_dir / "rebase-merge",
        "rebase-apply": git_dir / "rebase-apply",
    }
    return next((name for name, path in checks.items() if path.exists()), None)


def _verify_pinned_hashes() -> None:
    for relative, expected in PINNED_HASHES.items():
        path = REPO_ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"Pinned file is absent: {relative}")
        observed = _sha256_file(path)
        if observed != expected:
            raise RuntimeError(
                f"Pinned SHA-256 mismatch for {relative}: "
                f"expected {expected}, observed {observed}"
            )


def _verify_authorization_variable_boundary() -> None:
    allowed = set(AUTHORIZATION_VARIABLES)
    unexpected = sorted(
        name for name in os.environ
        if name.upper().startswith("PHASE13")
        and ("AUTH" in name.upper() or "EXECUTION" in name.upper())
        and name not in allowed
    )
    if unexpected:
        raise RuntimeError(f"Unexpected Phase 13 authorization variables: {unexpected}")


def _validate_run_id(run_id: str, head: str) -> None:
    match = RUN_ID_RE.fullmatch(run_id)
    if match is None:
        raise RuntimeError(
            "PHASE13G_RUN_ID must match "
            "phase13G_calibration_YYYYMMDDTHHMMSSZ_<commit7>"
        )
    timestamp, short_commit = match.groups()
    parsed = datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ").replace(
        tzinfo=timezone.utc
    )
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise RuntimeError("Run identifier timestamp is not UTC")
    if short_commit != head[:7]:
        raise RuntimeError("Run identifier short commit does not match HEAD")


def _preflight() -> PreflightContext:
    token = _require_environment("PHASE13G_EXECUTION_TOKEN")
    if token != EXECUTION_TOKEN:
        raise RuntimeError("Phase 13G execution token is incorrect")
    _verify_authorization_variable_boundary()
    if not sys.flags.isolated:
        raise RuntimeError("Phase 13G requires Python isolated mode (-I)")
    if not sys.dont_write_bytecode:
        raise RuntimeError("Phase 13G requires bytecode writing disabled (-B)")
    if Path.cwd().resolve() != REPO_ROOT:
        raise RuntimeError(f"Current directory must be repository root: {REPO_ROOT}")

    head = _git("rev-parse", "HEAD").strip().lower()
    branch = _git("branch", "--show-current").strip()
    status = _git("status", "--porcelain=v1", "--untracked-files=all")
    authorized_commit = _require_environment("PHASE13G_AUTHORIZED_COMMIT").lower()
    authorized_tag = _require_environment("PHASE13G_AUTHORIZED_TAG")
    expected_runner_hash = _require_environment("PHASE13G_RUNNER_SHA256").upper()
    run_id = _require_environment("PHASE13G_RUN_ID")

    if COMMIT_RE.fullmatch(authorized_commit) is None:
        raise RuntimeError("Authorized commit is not a full commit")
    if SHA256_RE.fullmatch(expected_runner_hash) is None:
        raise RuntimeError("Authorized runner SHA-256 is invalid")
    if head != authorized_commit:
        raise RuntimeError("HEAD does not match authorized runner commit")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"Unexpected branch: {branch}")
    if status:
        raise RuntimeError(f"Repository is not clean before execution:\n{status}")
    if not authorized_tag.startswith(EXPECTED_TAG_PREFIX):
        raise RuntimeError("Authorized tag does not identify the Phase 13G runner")
    if _git("cat-file", "-t", f"refs/tags/{authorized_tag}") != "tag":
        raise RuntimeError("Authorized tag is not annotated")
    if _git("rev-parse", f"{authorized_tag}^{{}}") != head:
        raise RuntimeError("Authorized tag does not resolve to HEAD")
    active = _active_git_operation()
    if active is not None:
        raise RuntimeError(f"Active Git operation detected: {active}")

    _verify_pinned_hashes()
    runner_hash = _sha256_file(RUNNER_PATH)
    if runner_hash != expected_runner_hash:
        raise RuntimeError(
            f"Runner SHA-256 mismatch: expected {expected_runner_hash}, "
            f"observed {runner_hash}"
        )
    _validate_run_id(run_id, head)
    run_directory = OUTPUT_ROOT / run_id
    if run_directory.exists():
        raise RuntimeError(f"Selected run directory already exists: {run_directory}")

    return PreflightContext(
        head=head, branch=branch, tag=authorized_tag, run_id=run_id,
        run_directory=run_directory, runner_sha256=runner_hash,
        timestamp_utc=datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
    )


def _clear_process_authorization() -> None:
    for name in AUTHORIZATION_VARIABLES:
        os.environ.pop(name, None)


def _build_cases() -> tuple[CalibrationCase, ...]:
    cases: dict[tuple[str, int, float, int, str | None], CalibrationCase] = {}

    def add(case: CalibrationCase) -> None:
        if case.key in cases:
            if cases[case.key] != case:
                raise RuntimeError(f"Conflicting duplicate case: {case.key}")
            return
        cases[case.key] = case

    for method in METHODS:
        for n in (16, 32, 64):
            add(CalibrationCase(O1_ID, "O1", n, 0.001, 0, method, 0.0))
        for n in (16, 32, 64, 128, 256):
            add(CalibrationCase(O2_ID, "O2", n, 0.001, 0, method, 0.0))

    for dt, steps in ((0.004, 2), (0.002, 4), (0.001, 8), (0.0005, 16)):
        add(CalibrationCase(L_ID, "L", 64, dt, steps, None, FINAL_TIME))
    add(CalibrationCase(L_ID, "L", 32, 0.0005, 16, None, FINAL_TIME))

    for method in METHODS:
        for n in (16, 32, 64, 128, 256):
            for dt, steps in ((0.0005, 16), (0.00025, 32)):
                add(CalibrationCase(M_ID, "M", n, dt, steps, method, FINAL_TIME))
        for n in (128, 256):
            for dt, steps in ((0.004, 2), (0.002, 4), (0.001, 8), (0.0005, 16)):
                add(CalibrationCase(M_ID, "M", n, dt, steps, method, FINAL_TIME))

    track_rank = {"O1": 0, "O2": 1, "L": 2, "M": 3}
    method_rank = {None: 0, "fd_centered": 1, "pseudo_spectral": 2, "arakawa": 3}
    ordered = tuple(sorted(
        cases.values(),
        key=lambda c: (track_rank[c.track], method_rank[c.method], c.N, -c.dt),
    ))
    if len(ordered) != EXPECTED_CASES:
        raise RuntimeError("Calibration matrix does not contain exactly 77 cases")
    if sum(case.n_steps for case in ordered) != EXPECTED_STEPS:
        raise RuntimeError("Calibration matrix does not contain exactly 850 RK2 steps")
    return ordered


CALIBRATION_CASES = _build_cases()
CALIBRATION_KEYS = frozenset(case.key for case in CALIBRATION_CASES)


def _load_modules(context: PreflightContext) -> SimpleNamespace:
    existed = context.run_directory.exists()
    repo_text = str(REPO_ROOT)
    if repo_text not in sys.path:
        sys.path.insert(0, repo_text)

    import run_phase13F_verification_pilot as base
    from project.verification import phase13_exact_references as exact
    from project.verification import phase13_external_harness as harness
    from project.verification import phase13_output_schema as schema

    if context.run_directory.exists() != existed:
        raise RuntimeError("Import created the selected result directory")
    for contract in (harness.implementation_contract(), schema.implementation_contract()):
        if contract["pilot_authorized"] is not False:
            raise RuntimeError("Dormant Phase 13 module unexpectedly authorizes a pilot")
        if contract["convergence_claim"] is not False:
            raise RuntimeError("Dormant Phase 13 module contains a convergence claim")
    return SimpleNamespace(base=base, exact=exact, harness=harness, schema=schema)


def _environment_record(context: PreflightContext) -> Mapping[str, object]:
    return {
        "timestamp_utc": context.timestamp_utc,
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "operating_system": __import__("platform").platform(),
        "floating_dtype": "float64",
        "machine_epsilon": float(np.finfo(np.float64).eps),
    }


def _base_context(modules: SimpleNamespace, context: PreflightContext) -> Any:
    return modules.base.PreflightContext(
        head=context.head, branch=context.branch, tag=context.tag,
        run_id=context.run_id, run_directory=context.run_directory,
        runner_sha256=context.runner_sha256,
        environment_timestamp=context.timestamp_utc,
    )


def _config(modules: SimpleNamespace, case: CalibrationCase, scaffold: Path) -> Any:
    return modules.harness.VerificationConfig(
        benchmark_id=case.benchmark_id, N=case.N, Re=RE, dt=case.dt,
        n_steps=case.n_steps, t_0=T0, advection_method=case.method,
        scaffold_path=scaffold, requested_final_time=case.requested_final_time,
        product_dealiasing=False, post_step_mask_policy=None,
    )


def _validate_calibration_boundary(modules: SimpleNamespace, case: CalibrationCase, config: Any) -> None:
    normalized = modules.harness.validate_config(config)
    observed = (
        str(normalized["track"]), int(normalized["N"]), float(normalized["dt"]),
        int(normalized["n_steps"]), normalized["advection_method"],
    )
    if observed not in CALIBRATION_KEYS or observed != case.key:
        raise RuntimeError(f"Unauthorized calibration configuration: {observed}")
    actual = float(normalized["t_final_actual"])
    if not np.isclose(actual, case.requested_final_time, rtol=0.0, atol=1e-15):
        raise RuntimeError("Calibration final-time boundary mismatch")


def _configuration_rejection_smoke(modules: SimpleNamespace) -> tuple[str, ...]:
    valid = CALIBRATION_CASES[0]
    invalid = (
        (valid.track, 12, valid.dt, valid.n_steps, valid.method),
        (valid.track, valid.N, 0.003, valid.n_steps, valid.method),
        ("M", 64, 0.0005, 15, "fd_centered"),
        ("M", 64, 0.0005, 16, "unknown"),
        ("S", 64, 0.0005, 16, "fd_centered"),
    )
    for key in invalid:
        if key in CALIBRATION_KEYS:
            raise RuntimeError(f"Invalid calibration key was accepted: {key}")
    if valid.key not in CALIBRATION_KEYS:
        raise RuntimeError("Valid calibration key was rejected")
    return tuple(f"rejection_{index}: PASS" for index in range(1, len(invalid) + 1))


def _solver_construction_smoke(modules: SimpleNamespace) -> tuple[Mapping[str, object], ...]:
    smoke = (
        next(c for c in CALIBRATION_CASES if c.track == "O1" and c.N == 16 and c.method == "fd_centered"),
        next(c for c in CALIBRATION_CASES if c.track == "O2" and c.N == 256 and c.method == "pseudo_spectral"),
        next(c for c in CALIBRATION_CASES if c.track == "L" and c.N == 64 and c.dt == 0.004),
    )
    records: list[Mapping[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="phase13G_solver_smoke_") as temporary:
        root = Path(temporary)
        for index, case in enumerate(smoke):
            scaffold = root / f"case_{index:02d}" / "_solver_scaffold"
            config = _config(modules, case, scaffold)
            _validate_calibration_boundary(modules, case, config)
            solver, contract = modules.harness.construct_guarded_solver(config)
            if type(solver).__name__ != "SelectableAdvectionSolver":
                raise RuntimeError("Unexpected solver class in construction smoke")
            if not scaffold.is_dir() or any(scaffold.iterdir()):
                raise RuntimeError("Solver construction wrote an unexpected file")
            records.append(asdict(contract))
    return tuple(records)


def _case_runtime_counts(case: CalibrationCase, result: Any, counter: Any) -> int:
    if counter.forcing != 0 or counter.prohibited != 0:
        raise RuntimeError("Prohibited solver pathway was called")
    if case.track in ("O1", "O2"):
        expected_advection, expected_diffusion, expected_masks = 1, 0, 0
        observed_steps, source = 0, 0
    elif case.track == "L":
        expected_advection, expected_diffusion = 0, 2 * case.n_steps
        expected_masks, observed_steps, source = case.n_steps, len(result.steps), 0
    else:
        expected_advection = expected_diffusion = 2 * case.n_steps
        expected_masks, observed_steps = case.n_steps, len(result.steps)
        source = sum(
            int(step.stage_1_source_sha256 is not None)
            + int(step.stage_2_source_sha256 is not None)
            for step in result.steps
        )
        if source != 2 * case.n_steps:
            raise RuntimeError("Track M source-stage count mismatch")
        if any(step.t_stage_2 <= step.t_stage_1 for step in result.steps):
            raise RuntimeError("Track M source stage times are not distinct")

    masks = (
        int(result.mask_application_count)
        if case.track in ("O1", "O2")
        else int(result.total_mask_applications)
    )
    if counter.advection != expected_advection:
        raise RuntimeError(f"Advection call mismatch for {result.case_id}")
    if counter.diffusion != expected_diffusion:
        raise RuntimeError(f"Diffusion call mismatch for {result.case_id}")
    if masks != expected_masks:
        raise RuntimeError(f"Mask call mismatch for {result.case_id}")
    if observed_steps != case.n_steps:
        raise RuntimeError(f"Step count mismatch for {result.case_id}")
    if not result.error_norms.finite:
        raise RuntimeError(f"Nonfinite error for {result.case_id}")
    return source


def _checks(
    modules: SimpleNamespace, context: PreflightContext, case: CalibrationCase,
    result: Any, counter: Any, source: int,
) -> Mapping[str, object]:
    base_case = modules.base.PilotCase(
        case.benchmark_id, case.track, case.method, case.n_steps,
        case.requested_final_time,
    )
    raw = dict(modules.base._case_checks(
        _base_context(modules, context), base_case, result, counter, source
    ))
    raw.update({
        "runner_version": RUNNER_VERSION,
        "phase": "13G.3",
        "design_sha256": PINNED_HASHES[
            "PHASE13G2_EXPLORATORY_ISOLATION_CALIBRATION_DESIGN_AND_AUTHORIZATION.md"
        ],
        "pilot_boundary_valid": False,
        "calibration_boundary_valid": True,
        "exploratory_calibration": True,
        "observed_order_calculated": False,
        "error_decay_model_fitted": False,
        "method_ranking": False,
        "convergence_claim": False,
        "physical_validation_claim": False,
    })
    return raw


def _metadata(
    modules: SimpleNamespace, context: PreflightContext,
    environment: Mapping[str, object], case: CalibrationCase,
    result: Any, counter: Any,
) -> Mapping[str, object]:
    base_case = modules.base.PilotCase(
        case.benchmark_id, case.track, case.method, case.n_steps,
        case.requested_final_time,
    )
    return modules.base._case_metadata(
        modules, _base_context(modules, context), environment,
        base_case, result, counter,
    )


def _case_record(case: CalibrationCase, result: Any, counter: Any, source: int) -> Mapping[str, object]:
    norms = asdict(result.error_norms)
    masks = (
        int(result.mask_application_count)
        if case.track in ("O1", "O2")
        else int(result.total_mask_applications)
    )
    return {
        "case_id": result.case_id, "benchmark_id": case.benchmark_id,
        "track": case.track, "method": case.method, "N": case.N,
        "dt": case.dt, "n_steps": case.n_steps,
        "t_final": case.requested_final_time,
        **norms,
        "discrete_mean_removed": (
            float(result.discrete_mean_removed) if case.track in ("O1", "O2") else 0.0
        ),
        "advection_calls": int(counter.advection),
        "diffusion_calls": int(counter.diffusion),
        "source_evaluations": int(source),
        "forcing_calls": int(counter.forcing),
        "mask_applications": masks,
    }


def _plan(context: PreflightContext) -> Mapping[str, object]:
    return {
        "schema_id": "PHASE13G_CALIBRATION_PLAN_V1",
        "runner_version": RUNNER_VERSION,
        "run_id": context.run_id,
        "authorized_commit": context.head,
        "authorized_tag": context.tag,
        "runner_sha256": context.runner_sha256,
        "design_sha256": PINNED_HASHES[
            "PHASE13G2_EXPLORATORY_ISOLATION_CALIBRATION_DESIGN_AND_AUTHORIZATION.md"
        ],
        "continuous_configuration": {
            "L": 2.0 * np.pi, "Re": RE, "nu": NU, "t_0": T0,
            "evolution_final_time": FINAL_TIME, "floating_dtype": "float64",
            "product_dealiasing": False, "inherited_forcing": False,
        },
        "expected": {
            "cases": EXPECTED_CASES, "rk2_steps": EXPECTED_STEPS,
            "advection_calls": EXPECTED_ADVECTION,
            "diffusion_calls": EXPECTED_DIFFUSION,
            "source_evaluations": EXPECTED_SOURCE,
            "forcing_calls": EXPECTED_FORCING,
            "post_step_masks": EXPECTED_MASKS,
            "persistent_files": EXPECTED_FILES,
        },
        "cases": [asdict(case) for case in CALIBRATION_CASES],
        "claims": {
            "observed_order": False, "convergence": False,
            "physical_validation": False, "method_superiority": False,
            "turbulence": False, "cascade": False, "k_minus_3": False,
        },
    }


def _atomic_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key) for key in fieldnames})
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _execute(
    modules: SimpleNamespace, context: PreflightContext,
    environment: Mapping[str, object],
) -> ExecutionResult:
    schema, harness, base = modules.schema, modules.harness, modules.base
    context.run_directory.mkdir(parents=True, exist_ok=False)
    schema.atomic_write_json(context.run_directory / "calibration_plan.json", _plan(context))

    writes: list[Any] = []
    records: list[Mapping[str, object]] = []
    totals = {"advection": 0, "diffusion": 0, "source": 0, "forcing": 0, "masks": 0, "steps": 0}

    with tempfile.TemporaryDirectory(prefix="phase13G_calibration_scaffolds_") as temporary:
        scaffold_root = Path(temporary)
        for index, case in enumerate(CALIBRATION_CASES, start=1):
            scaffold = scaffold_root / f"case_{index:03d}" / "_solver_scaffold"
            config = _config(modules, case, scaffold)
            _validate_calibration_boundary(modules, case, config)
            solver, _contract = harness.construct_guarded_solver(config)
            counter = base._instrument_solver(solver)
            print(
                f"CASE {index:03d}/{EXPECTED_CASES} START | {case.track} | "
                f"{case.method} | N={case.N} | dt={case.dt:.8g} | steps={case.n_steps}"
            )
            result = (
                harness.run_operator_case(solver, config)
                if case.track in ("O1", "O2")
                else harness.run_evolution_case(solver, config)
            )
            source = _case_runtime_counts(case, result, counter)
            if any(scaffold.iterdir()):
                raise RuntimeError(f"Unexpected solver-scaffold file for {result.case_id}")

            metadata = _metadata(modules, context, environment, case, result, counter)
            checks = _checks(modules, context, case, result, counter, source)
            error_summary = base._case_error_summary(result)
            write = schema.write_case_bundle(
                output_root=context.run_directory, metadata=metadata, checks=checks,
                error_summary=error_summary, arrays=base._case_arrays(result),
            )
            writes.append(write)
            record = _case_record(case, result, counter, source)
            records.append(record)
            totals["advection"] += int(counter.advection)
            totals["diffusion"] += int(counter.diffusion)
            totals["source"] += int(source)
            totals["forcing"] += int(counter.forcing)
            totals["masks"] += int(record["mask_applications"])
            totals["steps"] += case.n_steps
            print(
                f"CASE {index:03d}/{EXPECTED_CASES} PASS | {result.case_id} | "
                f"L2={result.error_norms.L2_rms:.12e}"
            )

    expected = {
        "advection": EXPECTED_ADVECTION, "diffusion": EXPECTED_DIFFUSION,
        "source": EXPECTED_SOURCE, "forcing": EXPECTED_FORCING,
        "masks": EXPECTED_MASKS, "steps": EXPECTED_STEPS,
    }
    if totals != expected:
        raise RuntimeError(f"Aggregate call-count mismatch: expected {expected}, observed {totals}")
    if len(writes) != EXPECTED_CASES or len(records) != EXPECTED_CASES:
        raise RuntimeError("Case execution inventory mismatch")
    return ExecutionResult(
        case_writes=tuple(writes), records=tuple(records),
        advection=totals["advection"], diffusion=totals["diffusion"],
        source=totals["source"], forcing=totals["forcing"],
        masks=totals["masks"], steps=totals["steps"],
    )


def _record_index(records: Sequence[Mapping[str, object]]) -> Mapping[tuple[str, int, float, str | None], Mapping[str, object]]:
    return {
        (str(row["track"]), int(row["N"]), float(row["dt"]), row["method"]): row
        for row in records
    }


def _difference(a: float, b: float) -> float:
    return abs(float(a) - float(b))


def _isolation_rows(records: Sequence[Mapping[str, object]]) -> list[Mapping[str, object]]:
    index = _record_index(records)
    rows: list[Mapping[str, object]] = []

    def add(kind: str, track: str, method: str | None, n: int | None, dt: float | None,
            numerator: float | None, denominator: float | None = None) -> None:
        value = numerator if denominator is None else (
            None if denominator == 0.0 else numerator / denominator
        )
        rows.append({
            "metric": kind, "track": track, "method": method,
            "N": n, "dt": dt, "numerator": numerator,
            "denominator": denominator, "value": value,
            "available": value is not None and np.isfinite(value),
            "null_reason": "ZERO_DENOMINATOR" if denominator == 0.0 else "",
        })

    for method in METHODS:
        for dt in (0.0005, 0.00025):
            for n in (32, 64, 128, 256):
                delta_h = _difference(
                    index[("M", n // 2, dt, method)]["L2_rms"],
                    index[("M", n, dt, method)]["L2_rms"],
                )
                add("Delta_h", "M", method, n, dt, delta_h)
        for n in (16, 32, 64, 128, 256):
            delta_t = _difference(
                index[("M", n, 0.0005, method)]["L2_rms"],
                index[("M", n, 0.00025, method)]["L2_rms"],
            )
            add("Delta_t", "M", method, n, None, delta_t)
            if n > 16:
                delta_h = _difference(
                    index[("M", n // 2, 0.0005, method)]["L2_rms"],
                    index[("M", n, 0.0005, method)]["L2_rms"],
                )
                add("C_t", "M", method, n, 0.0005, delta_t, delta_h)

        for dt in (0.004, 0.002, 0.001, 0.0005):
            delta_n = _difference(
                index[("M", 128, dt, method)]["L2_rms"],
                index[("M", 256, dt, method)]["L2_rms"],
            )
            add("Delta_N", "M", method, 256, dt, delta_n)
        for dt, fine_dt in ((0.004, 0.002), (0.002, 0.001), (0.001, 0.0005)):
            delta_dt = _difference(
                index[("M", 256, dt, method)]["L2_rms"],
                index[("M", 256, fine_dt, method)]["L2_rms"],
            )
            delta_n = _difference(
                index[("M", 128, dt, method)]["L2_rms"],
                index[("M", 256, dt, method)]["L2_rms"],
            )
            add("Delta_dt", "M", method, 256, dt, delta_dt)
            add("C_h", "M", method, 256, dt, delta_n, delta_dt)

    for dt, fine_dt in ((0.004, 0.002), (0.002, 0.001), (0.001, 0.0005)):
        add(
            "Delta_dt", "L", None, 64, dt,
            _difference(index[("L", 64, dt, None)]["L2_rms"],
                        index[("L", 64, fine_dt, None)]["L2_rms"]),
        )
    add(
        "Delta_N", "L", None, 64, 0.0005,
        _difference(index[("L", 32, 0.0005, None)]["L2_rms"],
                    index[("L", 64, 0.0005, None)]["L2_rms"]),
    )
    return rows


def _floor_rows(records: Sequence[Mapping[str, object]]) -> list[Mapping[str, object]]:
    eps = float(np.finfo(np.float64).eps)
    rows: list[Mapping[str, object]] = []
    index = _record_index(records)
    for row in records:
        exact = float(row["exact_L2_rms"])
        error = float(row["L2_rms"])
        scale = max(1.0, exact)
        floor = eps * scale
        ratio = error / floor
        rows.append({
            "observation_kind": "CASE", "case_id": row["case_id"],
            "track": row["track"], "method": row["method"],
            "N": row["N"], "dt": row["dt"], "machine_epsilon": eps,
            "characteristic_scale": scale, "F_eps": floor, "E": error,
            "R_eps": ratio, "exact_zero": error == 0.0,
            "floor_like": ratio <= 1.0e4,
            "adjacent_case_id": "", "adjacent_ratio": None,
            "direction": "", "plateau_like": "",
        })

    def pair(coarse: Mapping[str, object], fine: Mapping[str, object]) -> None:
        coarse_error = float(coarse["L2_rms"])
        fine_error = float(fine["L2_rms"])
        if coarse_error == 0.0 or fine_error == 0.0:
            adjacent_ratio: float | None = None
        else:
            adjacent_ratio = max(coarse_error, fine_error) / min(coarse_error, fine_error)
        direction = (
            "DECREASE OBSERVED" if fine_error < coarse_error
            else "INCREASE OBSERVED" if fine_error > coarse_error
            else "EQUAL OBSERVED"
        )
        exact = float(fine["exact_L2_rms"])
        scale = max(1.0, exact)
        floor = eps * scale
        ratio = fine_error / floor
        rows.append({
            "observation_kind": "ADJACENT", "case_id": coarse["case_id"],
            "track": fine["track"], "method": fine["method"],
            "N": fine["N"], "dt": fine["dt"], "machine_epsilon": eps,
            "characteristic_scale": scale, "F_eps": floor, "E": fine_error,
            "R_eps": ratio, "exact_zero": coarse_error == 0.0 or fine_error == 0.0,
            "floor_like": ratio <= 1.0e4,
            "adjacent_case_id": fine["case_id"], "adjacent_ratio": adjacent_ratio,
            "direction": direction,
            "plateau_like": adjacent_ratio is not None and adjacent_ratio <= 2.0,
        })

    for track, grids in (("O1", (16, 32, 64)), ("O2", (16, 32, 64, 128, 256))):
        for method in METHODS:
            for coarse_n, fine_n in zip(grids, grids[1:]):
                pair(index[(track, coarse_n, 0.001, method)],
                     index[(track, fine_n, 0.001, method)])

    for coarse_dt, fine_dt in ((0.004, 0.002), (0.002, 0.001), (0.001, 0.0005)):
        pair(index[("L", 64, coarse_dt, None)], index[("L", 64, fine_dt, None)])

    for method in METHODS:
        for dt in (0.0005, 0.00025):
            for coarse_n, fine_n in zip((16, 32, 64, 128), (32, 64, 128, 256)):
                pair(index[("M", coarse_n, dt, method)],
                     index[("M", fine_n, dt, method)])
        for n in (128, 256):
            for coarse_dt, fine_dt in ((0.004, 0.002), (0.002, 0.001), (0.001, 0.0005)):
                pair(index[("M", n, coarse_dt, method)],
                     index[("M", n, fine_dt, method)])
    return rows


def _write_summaries(
    modules: SimpleNamespace, context: PreflightContext, execution: ExecutionResult,
) -> None:
    records = list(execution.records)
    case_fields = (
        "case_id", "benchmark_id", "track", "method", "N", "dt", "n_steps",
        "t_final", "L1_mean", "L2_rms", "Linf", "exact_L2_rms",
        "numerical_L2_rms", "relative_L2", "finite", "discrete_mean_removed",
        "advection_calls", "diffusion_calls", "source_evaluations",
        "forcing_calls", "mask_applications",
    )
    _atomic_csv(context.run_directory / "calibration_case_summary.csv", case_fields, records)
    isolation = _isolation_rows(records)
    _atomic_csv(
        context.run_directory / "calibration_isolation_metrics.csv",
        ("metric", "track", "method", "N", "dt", "numerator", "denominator",
         "value", "available", "null_reason"), isolation,
    )
    floors = _floor_rows(records)
    _atomic_csv(
        context.run_directory / "calibration_floor_observations.csv",
        ("observation_kind", "case_id", "track", "method", "N", "dt",
         "machine_epsilon", "characteristic_scale", "F_eps", "E", "R_eps",
         "exact_zero", "floor_like", "adjacent_case_id", "adjacent_ratio",
         "direction", "plateau_like"), floors,
    )


def _inventory(run_directory: Path, exclude_manifest: bool = False) -> list[Mapping[str, object]]:
    records = []
    for path in sorted(p for p in run_directory.rglob("*") if p.is_file()):
        relative = path.relative_to(run_directory).as_posix()
        if exclude_manifest and relative == "run_manifest.json":
            continue
        records.append({
            "path": relative, "size_bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        })
    return records


def _write_manifest(
    modules: SimpleNamespace, context: PreflightContext,
    environment: Mapping[str, object], execution: ExecutionResult,
) -> str:
    schema = modules.schema
    before = _inventory(context.run_directory, exclude_manifest=True)
    if len(before) != EXPECTED_FILES - 1:
        raise RuntimeError(
            f"Pre-manifest file count mismatch: expected {EXPECTED_FILES - 1}, "
            f"observed {len(before)}"
        )
    base_manifest = schema.build_run_manifest(
        run_id=context.run_id, run_status="PASS", created_utc=context.timestamp_utc,
        repository=modules.base._repository_record(_base_context(modules, context)),
        environment=environment, cases=execution.case_writes,
    )
    manifest = json.loads(schema.canonical_json_bytes(base_manifest).decode("utf-8"))
    manifest["calibration_schema_id"] = "PHASE13G_CALIBRATION_RUN_MANIFEST_V1"
    manifest["runner_version"] = RUNNER_VERSION
    manifest["design_sha256"] = PINNED_HASHES[
        "PHASE13G2_EXPLORATORY_ISOLATION_CALIBRATION_DESIGN_AND_AUTHORIZATION.md"
    ]
    manifest["aggregate_counts"] = {
        "cases": EXPECTED_CASES, "rk2_steps": execution.steps,
        "advection_calls": execution.advection,
        "diffusion_calls": execution.diffusion,
        "source_evaluations": execution.source,
        "forcing_calls": execution.forcing,
        "post_step_masks": execution.masks,
        "persistent_files": EXPECTED_FILES,
    }
    manifest["persistent_inventory_excluding_manifest"] = before
    manifest["claims"] = {
        "observed_order": False, "convergence": False,
        "physical_validation": False, "method_superiority": False,
        "turbulence": False, "cascade": False, "k_minus_3": False,
    }
    schema.atomic_write_json(context.run_directory / "run_manifest.json", manifest)
    final = _inventory(context.run_directory)
    if len(final) != EXPECTED_FILES:
        raise RuntimeError(
            f"Final file count mismatch: expected {EXPECTED_FILES}, observed {len(final)}"
        )
    canonical = "".join(
        f"{row['path']}\0{row['size_bytes']}\0{row['sha256']}\n" for row in final
    ).encode("utf-8")
    return _sha256_bytes(canonical)


def _write_failure(context: PreflightContext | None, exc: BaseException) -> None:
    if context is None or not context.run_directory.exists():
        return
    path = context.run_directory / "calibration_failure.json"
    if path.exists():
        return
    payload = {
        "schema_id": "PHASE13G_CALIBRATION_FAILURE_V1",
        "run_id": context.run_id, "status": "CALIBRATION INCOMPLETE",
        "exception_type": type(exc).__name__, "message": str(exc),
        "traceback": traceback.format_exc(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "claims": {"convergence": False, "physical_validation": False},
    }
    data = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)


def main() -> int:
    context: PreflightContext | None = None
    try:
        context = _preflight()
        _clear_process_authorization()
        cases = _build_cases()
        if cases != CALIBRATION_CASES:
            raise RuntimeError("Calibration matrix changed after preflight")
        modules = _load_modules(context)
        environment = _environment_record(context)

        configuration_rejections = _configuration_rejection_smoke(modules)
        mutation_tests = modules.base._mutation_guard_tests(modules)
        schema_rejections = modules.base._schema_rejection_tests(
            modules, _base_context(modules, context), environment
        )
        atomic_smoke = modules.base._atomic_writer_smoke(modules)
        construction_smoke = _solver_construction_smoke(modules)

        print("PHASE 13G.3 PREFLIGHT: PASS")
        print(f"Configuration rejections: {len(configuration_rejections)} PASS")
        print(f"Mutation guards:          {len(mutation_tests)} PASS")
        print(f"Schema rejections:        {len(schema_rejections)} PASS")
        print(f"Atomic writers:           {len(atomic_smoke)} PASS")
        print(f"Solver constructions:     {len(construction_smoke)} PASS")

        execution = _execute(modules, context, environment)
        _write_summaries(modules, context, execution)
        inventory_hash = _write_manifest(modules, context, environment, execution)

        status = _git("status", "--porcelain=v1", "--untracked-files=all")
        if status:
            raise RuntimeError(f"Visible Git status changed during execution:\n{status}")
        if tuple(context.run_directory.rglob("*.tmp")):
            raise RuntimeError("Temporary output files remain")

        print("\n" + "=" * 72)
        print("PHASE 13G.3 EXPLORATORY ISOLATION CALIBRATION: PASS")
        print("=" * 72 + "\n")
        print(f"Run identifier:           {context.run_id}")
        print(f"Authorized commit:        {context.head}")
        print(f"Runner SHA256:            {context.runner_sha256}")
        print(f"Unique cases:             {EXPECTED_CASES}/77 PASS")
        print(f"External RK2 steps:       {execution.steps}")
        print(f"Advection calls:          {execution.advection}")
        print(f"Diffusion calls:          {execution.diffusion}")
        print(f"Track M source calls:     {execution.source}")
        print(f"Forcing calls:            {execution.forcing}")
        print(f"Post-step masks:          {execution.masks}")
        print(f"Persistent files:         {EXPECTED_FILES}")
        print(f"Inventory SHA256:         {inventory_hash}")
        print(f"Output directory:         {context.run_directory}")
        print("Classification:           CALIBRATION COMPLETE")
        print("Observed order:           NONE")
        print("Convergence claim:        NONE")
        print("Physical-validation claim: NONE")
        print("Phase 13H authorization:  NO")
        print("Authorization variables:  CLEARED IN PROCESS")
        return 0
    except BaseException as exc:
        _clear_process_authorization()
        _write_failure(context, exc)
        print("\nPHASE 13G.3 EXPLORATORY ISOLATION CALIBRATION: FAIL", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
