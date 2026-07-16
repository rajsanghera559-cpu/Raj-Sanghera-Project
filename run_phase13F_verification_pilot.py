"""
Controlled Phase 13F single-grid verification pilot runner.

This file is implemented and statically audited in Phase 13F.2. It must not
be executed until a later Phase 13F.3 execution gate supplies the exact
external authorization environment variables.

Runtime boundary:
- one grid only: N = 16;
- Re = 1000, dt = 0.001, t_0 = 0.0;
- six operator cases;
- one two-step Track L case;
- three two-step Track M cases;
- no refinement sequence;
- no observed order, fitting, ranking, or convergence claim.
"""
from __future__ import annotations

from copy import deepcopy
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
from types import ModuleType
from typing import Any, Callable, Mapping

import numpy as np


RUNNER_VERSION = "PHASE13F_CONTROLLED_PILOT_RUNNER_V1"

EXECUTION_TOKEN = (
    "PHASE13F_EXECUTE_AUTHORIZED_SINGLE_GRID_PILOT_V1"
)

EXPECTED_BRANCH = "phase4_validation"
EXPECTED_RUNNER_TAG_PREFIX = "v0.5.54-phase13F2"

N = 16
RE = 1000.0
NU = 0.001
DT = 0.001
T0 = 0.0
EVOLUTION_STEPS = 2
EVOLUTION_FINAL_TIME = 0.002
CONSTRUCTOR_STEPS = 0
PRODUCT_DEALIASING = False

O1_ID = "O1_BANDLIMITED_TWO_MODE_V1"
O2_ID = "O2_ANALYTIC_BROAD_SPECTRUM_V1"
L_ID = "L_EQUAL_EIGENVALUE_DECAY_V1"
M_ID = "M_TWO_RATE_NONLINEAR_MMS_V1"

METHODS = (
    "fd_centered",
    "pseudo_spectral",
    "arakawa",
)

REPO_ROOT = Path(__file__).resolve().parent

OUTPUT_ROOT = (
    REPO_ROOT
    / "experiments"
    / "verification"
    / "phase13"
)

RUNNER_PATH = (
    REPO_ROOT
    / "run_phase13F_verification_pilot.py"
)

PINNED_HASHES: Mapping[str, str] = {
    (
        "PHASE13B_BENCHMARK_AND_CONTINUOUS_"
        "EQUATION_SPECIFICATION.md"
    ): (
        "6FC0685AC0225F542C181174ECC5940C"
        "E1C1163F2CE90B15301AEF46D5CE7875"
    ),
    (
        "PHASE13C_REFERENCE_SOLUTION_AND_"
        "SOURCE_TERM_AUDIT_REPORT.md"
    ): (
        "ABEF31DF4F67913EB418C816DBB66553"
        "1C5F2C854EB4E300B68CF9F45CA5A306"
    ),
    (
        "PHASE13D_EXTERNAL_VERIFICATION_"
        "HARNESS_DESIGN.md"
    ): (
        "2F014D33623C5D7184F65EBF4E3CA34"
        "F4BAD13501BED0A66DC72D33FB1A90A5E"
    ),
    (
        "PHASE13E_EXTERNAL_VERIFICATION_HARNESS_"
        "IMPLEMENTATION_AND_STATIC_INTERFACE_"
        "AUDIT_REPORT.md"
    ): (
        "35B84F64CB089E8B0AF5525709EFEDEE"
        "3447D92AE9BDA8059C9EC7B29CB7247D"
    ),
    (
        "PHASE13F_CONTROLLED_SINGLE_GRID_"
        "VERIFICATION_PILOT_DESIGN_AND_"
        "AUTHORIZATION.md"
    ): (
        "AFA552CDF8983966F1C8C7CA7E21038"
        "270D58D26570D65131B00A9B811E037DD"
    ),
    "project/solver/spectral_solver.py": (
        "1195AF013057C31FC227FECD05DBCB27"
        "7553D340096C0348F53DFE79A7A483C1"
    ),
    (
        "project/solver/"
        "selectable_advection_solver.py"
    ): (
        "5EDA93A2E9358D81927BD9EE247F305"
        "E6DBC94367B351801913FFEAA2D7C5891"
    ),
    "project/solver/advection_operators.py": (
        "2C86465570DDF095D5B0A9B7F67E6E"
        "78A89D14F82933FA983D91156DD0F76409"
    ),
    (
        "project/verification/"
        "phase13_exact_references.py"
    ): (
        "6904C78E54948D07C92173C8B313844"
        "B28C92209B4F61CE447FFC29E15DA4EED"
    ),
    (
        "project/verification/"
        "phase13_external_harness.py"
    ): (
        "CDB6DBC249EA2DFF27E729AF0CF3D5C"
        "545C48BE57624CC59842B3222DAA752A2"
    ),
    (
        "project/verification/"
        "phase13_output_schema.py"
    ): (
        "6899C611C56E8154435BB6C042B520A"
        "13B466CD10042DE5325C7F9EF634FB11F"
    ),
}

PROTECTED_SOLVER_HASHES: Mapping[str, str] = {
    path: PINNED_HASHES[path]
    for path in (
        "project/solver/spectral_solver.py",
        (
            "project/solver/"
            "selectable_advection_solver.py"
        ),
        "project/solver/advection_operators.py",
    )
}

VERIFICATION_MODULE_HASHES: Mapping[str, str] = {
    path: PINNED_HASHES[path]
    for path in (
        (
            "project/verification/"
            "phase13_exact_references.py"
        ),
        (
            "project/verification/"
            "phase13_external_harness.py"
        ),
        (
            "project/verification/"
            "phase13_output_schema.py"
        ),
    )
}

EXPECTED_VERIFICATION_FILES = tuple(
    sorted(
        VERIFICATION_MODULE_HASHES
    )
)

ALLOWED_GIT_COMMANDS = {
    (
        "rev-parse",
        "HEAD",
    ),
    (
        "branch",
        "--show-current",
    ),
    (
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ),
    (
        "tag",
        "--points-at",
        "HEAD",
    ),
}

RUN_ID_RE = re.compile(
    r"^phase13F_pilot_"
    r"(\d{8}T\d{6}Z)_"
    r"([0-9a-f]{7})$"
)

SHA256_RE = re.compile(
    r"^[0-9A-F]{64}$"
)

COMMIT_RE = re.compile(
    r"^[0-9a-f]{40}$"
)


@dataclass(
    frozen=True,
    slots=True,
)
class PilotCase:
    benchmark_id: str
    track: str
    method: str | None
    n_steps: int
    requested_final_time: float


PILOT_CASES = (
    PilotCase(
        O1_ID,
        "O1",
        "fd_centered",
        0,
        0.0,
    ),
    PilotCase(
        O1_ID,
        "O1",
        "pseudo_spectral",
        0,
        0.0,
    ),
    PilotCase(
        O1_ID,
        "O1",
        "arakawa",
        0,
        0.0,
    ),
    PilotCase(
        O2_ID,
        "O2",
        "fd_centered",
        0,
        0.0,
    ),
    PilotCase(
        O2_ID,
        "O2",
        "pseudo_spectral",
        0,
        0.0,
    ),
    PilotCase(
        O2_ID,
        "O2",
        "arakawa",
        0,
        0.0,
    ),
    PilotCase(
        L_ID,
        "L",
        None,
        EVOLUTION_STEPS,
        EVOLUTION_FINAL_TIME,
    ),
    PilotCase(
        M_ID,
        "M",
        "fd_centered",
        EVOLUTION_STEPS,
        EVOLUTION_FINAL_TIME,
    ),
    PilotCase(
        M_ID,
        "M",
        "pseudo_spectral",
        EVOLUTION_STEPS,
        EVOLUTION_FINAL_TIME,
    ),
    PilotCase(
        M_ID,
        "M",
        "arakawa",
        EVOLUTION_STEPS,
        EVOLUTION_FINAL_TIME,
    ),
)


@dataclass(
    frozen=True,
    slots=True,
)
class PreflightContext:
    head: str
    branch: str
    tag: str
    run_id: str
    run_directory: Path
    runner_sha256: str
    environment_timestamp: str


@dataclass(
    frozen=True,
    slots=True,
)
class LoadedModules:
    exact: ModuleType
    harness: ModuleType
    schema: ModuleType


@dataclass(slots=True)
class CallCounter:
    advection: int = 0
    diffusion: int = 0
    forcing: int = 0
    prohibited: int = 0


@dataclass(
    frozen=True,
    slots=True,
)
class PilotExecution:
    case_results: tuple[Any, ...]
    case_records: tuple[
        Mapping[str, object],
        ...,
    ]
    run_write_result: Any
    total_advection_calls: int
    total_diffusion_calls: int
    total_source_evaluations: int
    total_forcing_calls: int
    total_mask_applications: int
    total_rk2_steps: int
    scaffold_root: Path


def _sha256_file(
    path: Path,
) -> str:
    digest = sha256()

    with path.open(
        "rb"
    ) as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return (
        digest
        .hexdigest()
        .upper()
    )


def _git(
    *arguments: str,
) -> str:
    command = tuple(arguments)

    if command not in ALLOWED_GIT_COMMANDS:
        raise RuntimeError(
            "Unauthorized Git command: "
            f"{command!r}"
        )

    completed = subprocess.run(
        [
            "git",
            *arguments,
        ],
        cwd=REPO_ROOT,
        shell=False,
        check=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="strict",
    )

    return completed.stdout.rstrip(
        "\r\n"
    )


def _require_environment(
    name: str,
) -> str:
    value = os.environ.get(name)

    if (
        value is None
        or not value.strip()
    ):
        raise RuntimeError(
            "Required environment variable "
            f"is absent: {name}"
        )

    return value.strip()


def _verify_pinned_hashes() -> None:
    for (
        relative_path,
        expected,
    ) in PINNED_HASHES.items():
        path = (
            REPO_ROOT
            / relative_path
        )

        if not path.is_file():
            raise RuntimeError(
                "Required pinned file "
                f"is absent: {relative_path}"
            )

        observed = _sha256_file(
            path
        )

        if observed != expected:
            raise RuntimeError(
                "Pinned SHA-256 mismatch for "
                f"{relative_path}: "
                f"expected {expected}, "
                f"observed {observed}"
            )


def _verify_verification_boundary() -> None:
    verification_root = (
        REPO_ROOT
        / "project"
        / "verification"
    )

    physical = tuple(
        sorted(
            path
            .relative_to(REPO_ROOT)
            .as_posix()
            for path in (
                verification_root.rglob("*")
            )
            if path.is_file()
        )
    )

    if (
        physical
        != EXPECTED_VERIFICATION_FILES
    ):
        raise RuntimeError(
            "Verification-file boundary "
            "mismatch: "
            f"expected "
            f"{EXPECTED_VERIFICATION_FILES!r}, "
            f"observed {physical!r}"
        )


def _active_git_operation(
) -> str | None:
    git_dir = (
        REPO_ROOT
        / ".git"
    )

    candidates = {
        "merge": (
            git_dir
            / "MERGE_HEAD"
        ),
        "cherry-pick": (
            git_dir
            / "CHERRY_PICK_HEAD"
        ),
        "revert": (
            git_dir
            / "REVERT_HEAD"
        ),
        "rebase-merge": (
            git_dir
            / "rebase-merge"
        ),
        "rebase-apply": (
            git_dir
            / "rebase-apply"
        ),
    }

    for (
        name,
        path,
    ) in candidates.items():
        if path.exists():
            return name

    return None


def _validate_run_id(
    run_id: str,
    head: str,
) -> None:
    match = RUN_ID_RE.fullmatch(
        run_id
    )

    if match is None:
        raise RuntimeError(
            "PHASE13F_RUN_ID must match "
            "phase13F_pilot_"
            "YYYYMMDDTHHMMSSZ_"
            "<7-character-commit>"
        )

    (
        timestamp,
        short_commit,
    ) = match.groups()

    try:
        parsed = datetime.strptime(
            timestamp,
            "%Y%m%dT%H%M%SZ",
        ).replace(
            tzinfo=timezone.utc
        )

    except ValueError as exc:
        raise RuntimeError(
            "Run identifier contains "
            "an invalid UTC timestamp"
        ) from exc

    if (
        parsed.utcoffset()
        != timezone.utc.utcoffset(
            parsed
        )
    ):
        raise RuntimeError(
            "Run identifier timestamp "
            "is not UTC"
        )

    if short_commit != head[:7]:
        raise RuntimeError(
            "Run identifier short commit "
            "does not match HEAD"
        )


def _preflight(
) -> PreflightContext:
    token = _require_environment(
        "PHASE13F_EXECUTION_TOKEN"
    )

    if token != EXECUTION_TOKEN:
        raise RuntimeError(
            "Phase 13F execution token "
            "is incorrect"
        )

    if not bool(
        sys.flags.isolated
    ):
        raise RuntimeError(
            "Phase 13F requires "
            "Python isolated mode (-I)"
        )

    if not bool(
        sys.dont_write_bytecode
    ):
        raise RuntimeError(
            "Phase 13F requires "
            "bytecode writing disabled (-B)"
        )

    if (
        Path.cwd().resolve()
        != REPO_ROOT
    ):
        raise RuntimeError(
            "Current directory must be "
            "repository root: "
            f"{REPO_ROOT}"
        )

    head = (
        _git(
            "rev-parse",
            "HEAD",
        )
        .strip()
        .lower()
    )

    branch = _git(
        "branch",
        "--show-current",
    ).strip()

    status = _git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )

    tags = tuple(
        line.strip()
        for line in _git(
            "tag",
            "--points-at",
            "HEAD",
        ).splitlines()
        if line.strip()
    )

    authorized_commit = (
        _require_environment(
            "PHASE13F_AUTHORIZED_COMMIT"
        )
        .lower()
    )

    authorized_tag = (
        _require_environment(
            "PHASE13F_AUTHORIZED_TAG"
        )
    )

    expected_runner_hash = (
        _require_environment(
            "PHASE13F_RUNNER_SHA256"
        )
        .upper()
    )

    run_id = _require_environment(
        "PHASE13F_RUN_ID"
    )

    if COMMIT_RE.fullmatch(
        authorized_commit
    ) is None:
        raise RuntimeError(
            "Authorized commit is not "
            "a full 40-character commit"
        )

    if SHA256_RE.fullmatch(
        expected_runner_hash
    ) is None:
        raise RuntimeError(
            "Authorized runner SHA-256 "
            "is invalid"
        )

    if head != authorized_commit:
        raise RuntimeError(
            "HEAD does not match the "
            "authorized runner commit: "
            f"{head}"
        )

    if branch != EXPECTED_BRANCH:
        raise RuntimeError(
            f"Unexpected branch: {branch}"
        )

    if status:
        raise RuntimeError(
            "Repository is not clean "
            "before execution:\n"
            f"{status}"
        )

    if authorized_tag not in tags:
        raise RuntimeError(
            "Authorized annotated tag "
            "is not present at HEAD"
        )

    if not authorized_tag.startswith(
        EXPECTED_RUNNER_TAG_PREFIX
    ):
        raise RuntimeError(
            "Authorized tag does not "
            "identify the Phase 13F.2 "
            "runner checkpoint"
        )

    active_operation = (
        _active_git_operation()
    )

    if active_operation is not None:
        raise RuntimeError(
            "Active Git operation detected: "
            f"{active_operation}"
        )

    _verify_pinned_hashes()
    _verify_verification_boundary()

    runner_hash = _sha256_file(
        RUNNER_PATH
    )

    if (
        runner_hash
        != expected_runner_hash
    ):
        raise RuntimeError(
            "Runner SHA-256 mismatch: "
            f"expected {expected_runner_hash}, "
            f"observed {runner_hash}"
        )

    _validate_run_id(
        run_id,
        head,
    )

    run_directory = (
        OUTPUT_ROOT
        / run_id
    )

    if run_directory.exists():
        raise RuntimeError(
            "Selected run directory "
            "already exists: "
            f"{run_directory}"
        )

    return PreflightContext(
        head=head,
        branch=branch,
        tag=authorized_tag,
        run_id=run_id,
        run_directory=run_directory,
        runner_sha256=runner_hash,
        environment_timestamp=(
            datetime.now(
                timezone.utc
            )
            .isoformat(
                timespec="seconds"
            )
            .replace(
                "+00:00",
                "Z",
            )
        ),
    )


# END CHUNK 1

def _load_modules(
    context: PreflightContext,
) -> LoadedModules:
    result_existed_before = (
        context.run_directory.exists()
    )

    repo_text = str(REPO_ROOT)

    if repo_text not in sys.path:
        sys.path.insert(
            0,
            repo_text,
        )

    from project.verification import (
        phase13_exact_references as exact,
    )

    from project.verification import (
        phase13_external_harness as harness,
    )

    from project.verification import (
        phase13_output_schema as schema,
    )

    if (
        context.run_directory.exists()
        != result_existed_before
    ):
        raise RuntimeError(
            "Import created the selected "
            "result directory"
        )

    harness_contract = (
        harness.implementation_contract()
    )

    schema_contract = (
        schema.implementation_contract()
    )

    if (
        harness_contract[
            "pilot_authorized"
        ]
        is not False
    ):
        raise RuntimeError(
            "Harness implementation "
            "contract unexpectedly "
            "authorizes a pilot"
        )

    if (
        schema_contract[
            "pilot_authorized"
        ]
        is not False
    ):
        raise RuntimeError(
            "Schema implementation "
            "contract unexpectedly "
            "authorizes a pilot"
        )

    if (
        harness_contract[
            "convergence_claim"
        ]
        is not False
    ):
        raise RuntimeError(
            "Harness implementation "
            "contract contains a "
            "convergence claim"
        )

    if (
        schema_contract[
            "convergence_claim"
        ]
        is not False
    ):
        raise RuntimeError(
            "Schema implementation "
            "contract contains a "
            "convergence claim"
        )

    return LoadedModules(
        exact=exact,
        harness=harness,
        schema=schema,
    )


def _reference_arrays(
    reference: Any,
) -> tuple[np.ndarray, ...]:
    values = [
        reference.psi,
        reference.omega_raw,
        reference.omega_input,
        reference.u,
        reference.v,
        reference.adv,
    ]

    for value in (
        reference.laplacian_omega,
        reference.partial_t_omega,
        reference.source,
    ):
        if value is not None:
            values.append(value)

    return tuple(values)


def _exact_reference_smoke(
    modules: LoadedModules,
) -> Mapping[str, object]:
    exact = modules.exact

    grid = exact.construct_native_grid(
        N
    )

    results: dict[
        str,
        object,
    ] = {}

    for benchmark_id in (
        O1_ID,
        O2_ID,
        L_ID,
        M_ID,
    ):
        reference = (
            exact.evaluate_reference(
                benchmark_id,
                grid.X,
                grid.Y,
                T0,
                NU,
            )
        )

        validation = (
            exact.validate_reference_fields(
                reference
            )
        )

        arrays = _reference_arrays(
            reference
        )

        if (
            reference.psi.shape
            != (N, N)
        ):
            raise RuntimeError(
                "Unexpected reference "
                f"shape for {benchmark_id}"
            )

        for array in arrays:
            if array.dtype != np.float64:
                raise RuntimeError(
                    "Unexpected dtype for "
                    f"{benchmark_id}"
                )

            if (
                not np.isrealobj(array)
                or not np.isfinite(
                    array
                ).all()
            ):
                raise RuntimeError(
                    "Nonfinite or complex "
                    "reference for "
                    f"{benchmark_id}"
                )

            if array.flags.writeable:
                raise RuntimeError(
                    "Writable reference "
                    "array for "
                    f"{benchmark_id}"
                )

        for (
            index,
            left,
        ) in enumerate(arrays):
            for right in arrays[
                index + 1 :
            ]:
                if np.shares_memory(
                    left,
                    right,
                ):
                    raise RuntimeError(
                        "Shared reference "
                        "memory for "
                        f"{benchmark_id}"
                    )

        if benchmark_id == O2_ID:
            discrete_mean = float(
                np.mean(
                    reference.omega_input,
                    dtype=np.float64,
                )
            )

            tolerance = (
                64.0
                * np.finfo(
                    np.float64
                ).eps
            )

            if (
                abs(discrete_mean)
                > tolerance
            ):
                raise RuntimeError(
                    "O2 discrete compatibility "
                    "mean is not near zero"
                )

        if benchmark_id == L_ID:
            if np.count_nonzero(
                reference.adv
            ):
                raise RuntimeError(
                    "Track L exact advection "
                    "is not zero"
                )

            if (
                reference.source is None
                or np.count_nonzero(
                    reference.source
                )
            ):
                raise RuntimeError(
                    "Track L exact source "
                    "is not zero"
                )

        if (
            benchmark_id == M_ID
            and reference.source is None
        ):
            raise RuntimeError(
                "Track M exact source "
                "is absent"
            )

        results[
            benchmark_id
        ] = dict(validation)

    return results


def _expect_failure(
    name: str,
    callback: Callable[
        [],
        object,
    ],
) -> str:
    try:
        callback()

    except Exception as exc:
        return (
            f"{name}: "
            f"{type(exc).__name__}"
        )

    raise RuntimeError(
        "Expected fail-closed rejection "
        f"did not occur: {name}"
    )


def _configuration_rejection_tests(
    modules: LoadedModules,
    temporary_root: Path,
) -> tuple[str, ...]:
    harness = modules.harness

    scaffold = (
        temporary_root
        / "_solver_scaffold"
    )

    def config(
        *,
        benchmark_id: str = O1_ID,
        grid_size: int = N,
        reynolds: float = RE,
        timestep: float = DT,
        steps: int = 0,
        method: str | None = (
            "fd_centered"
        ),
        requested: float | None = 0.0,
        product_dealiasing: bool = False,
        mask_policy: str | None = None,
        scaffold_path: Path = scaffold,
    ) -> Any:
        return harness.VerificationConfig(
            benchmark_id=benchmark_id,
            N=grid_size,
            Re=reynolds,
            dt=timestep,
            n_steps=steps,
            t_0=T0,
            advection_method=method,
            scaffold_path=scaffold_path,
            requested_final_time=requested,
            product_dealiasing=(
                product_dealiasing
            ),
            post_step_mask_policy=(
                mask_policy
            ),
        )

    tests: list[
        tuple[
            str,
            Callable[
                [],
                object,
            ],
        ]
    ] = [
        (
            "unknown benchmark",
            lambda: (
                harness.validate_config(
                    config(
                        benchmark_id="UNKNOWN"
                    )
                )
            ),
        ),
        (
            "lowercase benchmark alias",
            lambda: (
                harness.validate_config(
                    config(
                        benchmark_id=(
                            O1_ID.lower()
                        )
                    )
                )
            ),
        ),
        (
            "unknown advection method",
            lambda: (
                harness.validate_config(
                    config(
                        method="unknown"
                    )
                )
            ),
        ),
        (
            "odd grid",
            lambda: (
                harness.validate_config(
                    config(
                        grid_size=15
                    )
                )
            ),
        ),
        (
            "disallowed pilot grid",
            lambda: (
                harness
                .validate_phase13f_pilot_boundary(
                    config(
                        grid_size=32
                    )
                )
            ),
        ),
        (
            "zero Reynolds number",
            lambda: (
                harness.validate_config(
                    config(
                        reynolds=0.0
                    )
                )
            ),
        ),
        (
            "negative Reynolds number",
            lambda: (
                harness.validate_config(
                    config(
                        reynolds=-1.0
                    )
                )
            ),
        ),
        (
            "zero timestep",
            lambda: (
                harness.validate_config(
                    config(
                        timestep=0.0
                    )
                )
            ),
        ),
        (
            "negative timestep",
            lambda: (
                harness.validate_config(
                    config(
                        timestep=-DT
                    )
                )
            ),
        ),
        (
            "negative step count",
            lambda: (
                harness.validate_config(
                    config(
                        steps=-1
                    )
                )
            ),
        ),
        (
            "evolution with zero steps",
            lambda: (
                harness.validate_config(
                    config(
                        benchmark_id=L_ID,
                        steps=0,
                        method=None,
                        requested=0.0,
                    )
                )
            ),
        ),
        (
            "operator with one step",
            lambda: (
                harness.validate_config(
                    config(
                        steps=1,
                        requested=DT,
                    )
                )
            ),
        ),
        (
            (
                "pilot evolution over "
                "two-step maximum"
            ),
            lambda: (
                harness
                .validate_phase13f_pilot_boundary(
                    config(
                        benchmark_id=L_ID,
                        steps=3,
                        method=None,
                        requested=(
                            3.0
                            * DT
                        ),
                    )
                )
            ),
        ),
        (
            "Track L with advection method",
            lambda: (
                harness.validate_config(
                    config(
                        benchmark_id=L_ID,
                        steps=2,
                        method="fd_centered",
                        requested=(
                            EVOLUTION_FINAL_TIME
                        ),
                    )
                )
            ),
        ),
        (
            "O1 without method",
            lambda: (
                harness.validate_config(
                    config(
                        method=None
                    )
                )
            ),
        ),
        (
            "O2 without method",
            lambda: (
                harness.validate_config(
                    config(
                        benchmark_id=O2_ID,
                        method=None,
                    )
                )
            ),
        ),
        (
            "Track M without method",
            lambda: (
                harness.validate_config(
                    config(
                        benchmark_id=M_ID,
                        steps=2,
                        method=None,
                        requested=(
                            EVOLUTION_FINAL_TIME
                        ),
                    )
                )
            ),
        ),
        (
            "product dealiasing enabled",
            lambda: (
                harness.validate_config(
                    config(
                        product_dealiasing=True
                    )
                )
            ),
        ),
        (
            "incorrect mask policy",
            lambda: (
                harness.validate_config(
                    config(
                        mask_policy=(
                            "WRONG_POLICY"
                        )
                    )
                )
            ),
        ),
        (
            (
                "inconsistent requested "
                "final time"
            ),
            lambda: (
                harness.validate_config(
                    config(
                        requested=DT
                    )
                )
            ),
        ),
        (
            "invalid scaffold suffix",
            lambda: (
                harness.validate_config(
                    config(
                        scaffold_path=(
                            temporary_root
                            / (
                                "wrong_"
                                "scaffold_name"
                            )
                        )
                    )
                )
            ),
        ),
    ]

    return tuple(
        _expect_failure(
            name,
            callback,
        )
        for (
            name,
            callback,
        ) in tests
    )


class _GuardTestDouble:
    def __init__(
        self,
        mode: str,
    ) -> None:
        self.mode = mode
        self.N = 4
        self.w = np.zeros(
            (4, 4),
            dtype=np.float64,
        )

    def compute_advection(
        self,
        value: np.ndarray,
    ) -> np.ndarray:
        if (
            self.mode
            == "input_mutation"
        ):
            value[0, 0] = 1.0

            return np.array(
                value,
                copy=True,
            )

        if (
            self.mode
            == "solver_mutation"
        ):
            self.w[0, 0] = 1.0

            return np.array(
                value,
                copy=True,
            )

        if (
            self.mode
            == "share_input"
        ):
            return value

        if (
            self.mode
            == "share_solver"
        ):
            return self.w

        return np.array(
            value + 1.0,
            copy=True,
        )

    def laplacian_spectral(
        self,
        value: np.ndarray,
    ) -> np.ndarray:
        return np.array(
            -value,
            copy=True,
        )


def _mutation_guard_tests(
    modules: LoadedModules,
) -> tuple[str, ...]:
    harness = modules.harness

    field = np.zeros(
        (4, 4),
        dtype=np.float64,
    )

    results = []

    for mode in (
        "input_mutation",
        "solver_mutation",
        "share_input",
        "share_solver",
    ):
        results.append(
            _expect_failure(
                (
                    "mutation guard "
                    f"{mode}"
                ),
                lambda selected=mode: (
                    harness.guarded_advection(
                        _GuardTestDouble(
                            selected
                        ),
                        field,
                    )
                ),
            )
        )

    good = _GuardTestDouble(
        "good"
    )

    advection = (
        harness.guarded_advection(
            good,
            field,
        )
    )

    diffusion = (
        harness.guarded_diffusion(
            good,
            field,
        )
    )

    if not (
        advection
        .mutation_guard
        .input_unchanged
    ):
        raise RuntimeError(
            "Non-mutating advection "
            "test double failed"
        )

    if not (
        diffusion
        .mutation_guard
        .solver_state_unchanged
    ):
        raise RuntimeError(
            "Non-mutating diffusion "
            "test double failed"
        )

    results.extend(
        (
            (
                "non-mutating "
                "advection: PASS"
            ),
            (
                "non-mutating "
                "diffusion: PASS"
            ),
        )
    )

    return tuple(results)


# END CHUNK 2

def _repository_record(
    context: PreflightContext,
) -> Mapping[str, object]:
    return {
        "name": REPO_ROOT.name,
        "branch": context.branch,
        "commit": context.head,
        "dirty": False,
        (
            "phase13b_"
            "specification_sha256"
        ): PINNED_HASHES[
            (
                "PHASE13B_BENCHMARK_AND_"
                "CONTINUOUS_EQUATION_"
                "SPECIFICATION.md"
            )
        ],
        (
            "phase13c_"
            "audit_report_sha256"
        ): PINNED_HASHES[
            (
                "PHASE13C_REFERENCE_"
                "SOLUTION_AND_SOURCE_TERM_"
                "AUDIT_REPORT.md"
            )
        ],
        (
            "protected_solver_sha256"
        ): dict(
            PROTECTED_SOLVER_HASHES
        ),
        (
            "exact_reference_"
            "module_sha256"
        ): VERIFICATION_MODULE_HASHES[
            (
                "project/verification/"
                "phase13_exact_references.py"
            )
        ],
        (
            "harness_module_sha256"
        ): VERIFICATION_MODULE_HASHES[
            (
                "project/verification/"
                "phase13_external_harness.py"
            )
        ],
        (
            "output_schema_"
            "module_sha256"
        ): VERIFICATION_MODULE_HASHES[
            (
                "project/verification/"
                "phase13_output_schema.py"
            )
        ],
    }


def _baseline_schema_metadata(
    modules: LoadedModules,
    context: PreflightContext,
    environment: Mapping[
        str,
        object,
    ],
) -> dict[str, object]:
    schema = modules.schema

    case_id = (
        schema.deterministic_case_id(
            benchmark_id=O1_ID,
            N=N,
            Re=RE,
            dt=DT,
            n_steps=0,
            t_0=T0,
            advection_method=(
                "fd_centered"
            ),
        )
    )

    zero_summary = {
        "L1_mean": 0.0,
        "L2_rms": 0.0,
        "Linf": 0.0,
        "exact_L2_rms": 1.0,
        (
            "numerical_L2_rms"
        ): 1.0,
        "relative_L2": 0.0,
        "finite": True,
    }

    return {
        "schema_id": (
            schema.METADATA_SCHEMA_ID
        ),
        "repository": dict(
            _repository_record(
                context
            )
        ),
        "environment": dict(
            environment
        ),
        "benchmark": {
            "benchmark_id": O1_ID,
            "track": "O1",
            (
                "reference_version"
            ): "PHASE13_REFERENCE_V1",
            (
                "compatibility_policy"
            ): "NONE",
            (
                "source_policy"
            ): (
                "OPERATOR_ONLY_"
                "NO_SOURCE_V1"
            ),
            (
                "advection_method"
            ): "fd_centered",
            (
                "product_dealiasing"
            ): False,
            (
                "post_step_mask_policy"
            ): (
                "NO_POST_STEP_MASK_"
                "OPERATOR_ONLY_V1"
            ),
        },
        "numerical": {
            "N": N,
            "L": float(
                2.0
                * np.pi
            ),
            "dx": float(
                2.0
                * np.pi
                / N
            ),
            "Re": RE,
            "nu": NU,
            "dt": DT,
            "n_steps": 0,
            "t_0": T0,
            (
                "t_final_actual"
            ): T0,
            (
                "t_final_requested"
            ): T0,
            (
                "final_time_aligned"
            ): True,
            (
                "constructor_steps"
            ): 0,
        },
        "execution": {
            (
                "solver_class"
            ): (
                "SelectableAdvectionSolver"
            ),
            (
                "allowed_methods_called"
            ): [
                "compute_advection",
            ],
            (
                "prohibited_methods_called"
            ): [],
            (
                "forcing_call_count"
            ): 0,
            (
                "mask_application_count"
            ): 0,
            "input_unchanged": True,
            (
                "solver_state_unchanged"
            ): True,
        },
        "result": {
            "case_id": case_id,
            "case_status": "PASS",
            (
                "output_filenames"
            ): dict(
                schema.CASE_OUTPUT_FILENAMES
            ),
            "output_sha256": {},
            (
                "error_summary"
            ): zero_summary,
            (
                "failure_messages"
            ): [],
        },
    }


def _schema_rejection_tests(
    modules: LoadedModules,
    context: PreflightContext,
    environment: Mapping[
        str,
        object,
    ],
) -> tuple[str, ...]:
    schema = modules.schema

    baseline = (
        _baseline_schema_metadata(
            modules,
            context,
            environment,
        )
    )

    outcomes: list[str] = []

    def reject_metadata(
        name: str,
        mutator: Callable[
            [
                dict[
                    str,
                    object,
                ]
            ],
            None,
        ],
    ) -> None:
        candidate = deepcopy(
            baseline
        )

        mutator(candidate)

        outcomes.append(
            _expect_failure(
                name,
                lambda: (
                    schema
                    .validate_case_metadata(
                        candidate,
                        allow_unwritten_outputs=(
                            True
                        ),
                    )
                ),
            )
        )

    for section in (
        "repository",
        "environment",
        "benchmark",
        "numerical",
        "execution",
        "result",
    ):
        reject_metadata(
            (
                "missing metadata "
                f"section {section}"
            ),
            lambda data, key=section: (
                data.pop(key)
            ),
        )

    reject_metadata(
        "invalid SHA-256",
        lambda data: (
            data["repository"]
            .__setitem__(
                (
                    "exact_reference_"
                    "module_sha256"
                ),
                "BAD",
            )
        ),
    )

    reject_metadata(
        (
            "incomplete protected "
            "hash set"
        ),
        lambda data: (
            data["repository"][
                "protected_solver_sha256"
            ].pop(
                (
                    "project/solver/"
                    "advection_operators.py"
                )
            )
        ),
    )

    reject_metadata(
        "inconsistent viscosity",
        lambda data: (
            data["numerical"]
            .__setitem__(
                "nu",
                0.002,
            )
        ),
    )

    reject_metadata(
        (
            "inconsistent grid "
            "spacing"
        ),
        lambda data: (
            data["numerical"]
            .__setitem__(
                "dx",
                1.0,
            )
        ),
    )

    reject_metadata(
        (
            "inconsistent final "
            "time"
        ),
        lambda data: (
            data["numerical"]
            .__setitem__(
                "t_final_actual",
                DT,
            )
        ),
    )

    reject_metadata(
        (
            "invalid deterministic "
            "case id"
        ),
        lambda data: (
            data["result"]
            .__setitem__(
                "case_id",
                "WRONG",
            )
        ),
    )

    reject_metadata(
        "nonzero forcing count",
        lambda data: (
            data["execution"]
            .__setitem__(
                "forcing_call_count",
                1,
            )
        ),
    )

    reject_metadata(
        "incorrect mask count",
        lambda data: (
            data["execution"]
            .__setitem__(
                "mask_application_count",
                1,
            )
        ),
    )

    reject_metadata(
        (
            "passing case with "
            "failure message"
        ),
        lambda data: (
            data["result"]
            .__setitem__(
                "failure_messages",
                [
                    "failure",
                ],
            )
        ),
    )

    def failed_without_message(
        data: dict[
            str,
            object,
        ],
    ) -> None:
        data["result"][
            "case_status"
        ] = "FAIL"

        data["result"][
            "failure_messages"
        ] = []

    reject_metadata(
        (
            "failed case without "
            "message"
        ),
        failed_without_message,
    )

    reject_metadata(
        (
            "nonfinite error "
            "summary"
        ),
        lambda data: (
            data["result"][
                "error_summary"
            ].__setitem__(
                "L2_rms",
                float("inf"),
            )
        ),
    )

    valid_arrays = {
        name: np.zeros(
            (N, N),
            dtype=np.float64,
        )
        for name in (
            schema.OPERATOR_ARRAY_NAMES
        )
    }

    outcomes.append(
        _expect_failure(
            (
                "missing required "
                "array"
            ),
            lambda: (
                schema.prepare_case_arrays(
                    "O1",
                    {
                        key: value
                        for (
                            key,
                            value,
                        ) in (
                            valid_arrays.items()
                        )
                        if (
                            key
                            != "error_adv"
                        )
                    },
                )
            ),
        )
    )

    outcomes.append(
        _expect_failure(
            "unexpected array",
            lambda: (
                schema.prepare_case_arrays(
                    "O1",
                    {
                        **valid_arrays,
                        "unexpected": (
                            np.zeros(
                                (N, N)
                            )
                        ),
                    },
                )
            ),
        )
    )

    outcomes.append(
        _expect_failure(
            "nonsquare array",
            lambda: (
                schema.prepare_case_arrays(
                    "O1",
                    {
                        **valid_arrays,
                        "omega_raw": (
                            np.zeros(
                                (
                                    N,
                                    N - 1,
                                )
                            )
                        ),
                    },
                )
            ),
        )
    )

    outcomes.append(
        _expect_failure(
            "complex array",
            lambda: (
                schema.prepare_case_arrays(
                    "O1",
                    {
                        **valid_arrays,
                        "omega_raw": (
                            np.zeros(
                                (N, N),
                                dtype=complex,
                            )
                        ),
                    },
                )
            ),
        )
    )

    nonfinite = np.zeros(
        (N, N),
        dtype=np.float64,
    )

    nonfinite[
        0,
        0,
    ] = np.nan

    outcomes.append(
        _expect_failure(
            "nonfinite array",
            lambda: (
                schema.prepare_case_arrays(
                    "O1",
                    {
                        **valid_arrays,
                        "omega_raw": (
                            nonfinite
                        ),
                    },
                )
            ),
        )
    )

    outcomes.append(
        _expect_failure(
            (
                "inconsistent array "
                "shape"
            ),
            lambda: (
                schema.prepare_case_arrays(
                    "O1",
                    {
                        **valid_arrays,
                        "omega_raw": (
                            np.zeros(
                                (8, 8)
                            )
                        ),
                    },
                )
            ),
        )
    )

    outcomes.append(
        _expect_failure(
            (
                "unsafe run "
                "identifier"
            ),
            lambda: (
                schema.build_run_manifest(
                    run_id="../unsafe",
                    run_status="PASS",
                    created_utc=str(
                        environment[
                            "timestamp_utc"
                        ]
                    ),
                    repository=(
                        _repository_record(
                            context
                        )
                    ),
                    environment=(
                        environment
                    ),
                    cases=(),
                )
            ),
        )
    )

    with tempfile.TemporaryDirectory(
        prefix=(
            "phase13F_"
            "schema_reject_"
        )
    ) as temporary:
        root = Path(temporary)

        case_id = str(
            baseline["result"][
                "case_id"
            ]
        )

        schema.atomic_write_json(
            (
                root
                / case_id
                / "sentinel.json"
            ),
            {
                "sentinel": True,
            },
        )

        outcomes.append(
            _expect_failure(
                (
                    "nonempty pre-existing "
                    "case directory"
                ),
                lambda: (
                    schema.write_case_bundle(
                        output_root=root,
                        metadata=baseline,
                        checks={
                            "smoke": True,
                        },
                        error_summary=(
                            baseline["result"][
                                "error_summary"
                            ]
                        ),
                        arrays=valid_arrays,
                    )
                ),
            )
        )

    with tempfile.TemporaryDirectory(
        prefix=(
            "phase13F_"
            "run_reject_"
        )
    ) as temporary:
        run_id = (
            "phase13F_test_run"
        )

        run_directory = (
            Path(temporary)
            / run_id
        )

        schema.atomic_write_json(
            (
                run_directory
                / (
                    schema
                    .RUN_MANIFEST_FILENAME
                )
            ),
            {
                "sentinel": True,
            },
        )

        outcomes.append(
            _expect_failure(
                (
                    "pre-existing "
                    "run manifest"
                ),
                lambda: (
                    schema.write_run_manifest(
                        run_directory=(
                            run_directory
                        ),
                        run_id=run_id,
                        run_status="PASS",
                        created_utc=str(
                            environment[
                                "timestamp_utc"
                            ]
                        ),
                        repository=(
                            _repository_record(
                                context
                            )
                        ),
                        environment=(
                            environment
                        ),
                        cases=(),
                    )
                ),
            )
        )

    return tuple(outcomes)


def _atomic_writer_smoke(
    modules: LoadedModules,
) -> Mapping[str, object]:
    schema = modules.schema

    temporary_path: (
        Path
        | None
    ) = None

    with tempfile.TemporaryDirectory(
        prefix=(
            "phase13F_"
            "atomic_smoke_"
        )
    ) as temporary:
        temporary_path = Path(
            temporary
        )

        json_path = (
            temporary_path
            / "sample.json"
        )

        csv_path = (
            temporary_path
            / "sample.csv"
        )

        npz_path = (
            temporary_path
            / "sample.npz"
        )

        json_value = {
            "alpha": 1,
            "beta": [
                2,
                3,
            ],
        }

        summary = {
            "L1_mean": 0.0,
            "L2_rms": 0.0,
            "Linf": 0.0,
            "exact_L2_rms": 1.0,
            (
                "numerical_L2_rms"
            ): 1.0,
            "relative_L2": 0.0,
            "finite": True,
        }

        arrays = {
            "field": (
                np.arange(
                    16,
                    dtype=np.float64,
                ).reshape(
                    4,
                    4,
                )
            )
        }

        schema.atomic_write_json(
            json_path,
            json_value,
        )

        schema.atomic_write_error_summary_csv(
            csv_path,
            summary,
        )

        schema.atomic_write_npz(
            npz_path,
            arrays,
        )

        if (
            json.loads(
                json_path.read_text(
                    encoding="utf-8"
                )
            )
            != json_value
        ):
            raise RuntimeError(
                "Atomic JSON smoke-test "
                "content mismatch"
            )

        with csv_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            reader = csv.DictReader(
                handle
            )

            rows = list(reader)

        if (
            tuple(
                reader.fieldnames
                or ()
            )
            != tuple(
                schema
                .ERROR_SUMMARY_COLUMNS
            )
        ):
            raise RuntimeError(
                "Atomic CSV smoke-test "
                "columns mismatch"
            )

        if len(rows) != 1:
            raise RuntimeError(
                "Atomic CSV smoke-test "
                "row count mismatch"
            )

        with np.load(
            npz_path,
            allow_pickle=False,
        ) as archive:
            if set(
                archive.files
            ) != {
                "field",
            }:
                raise RuntimeError(
                    "Atomic NPZ smoke-test "
                    "field set mismatch"
                )

            if not np.array_equal(
                archive["field"],
                arrays["field"],
            ):
                raise RuntimeError(
                    "Atomic NPZ smoke-test "
                    "array mismatch"
                )

        remaining_tmp = tuple(
            temporary_path.rglob(
                "*.tmp"
            )
        )

        if remaining_tmp:
            raise RuntimeError(
                "Temporary writer files "
                "remain: "
                f"{remaining_tmp!r}"
            )

        hashes = {
            "json": (
                schema.sha256_file(
                    json_path
                )
            ),
            "csv": (
                schema.sha256_file(
                    csv_path
                )
            ),
            "npz": (
                schema.sha256_file(
                    npz_path
                )
            ),
        }

    if (
        temporary_path is None
        or temporary_path.exists()
    ):
        raise RuntimeError(
            "Atomic-writer temporary "
            "directory cleanup failed"
        )

    return hashes


def _config_for_case(
    harness: ModuleType,
    case: PilotCase,
    scaffold: Path,
) -> Any:
    return harness.VerificationConfig(
        benchmark_id=case.benchmark_id,
        N=N,
        Re=RE,
        dt=DT,
        n_steps=case.n_steps,
        t_0=T0,
        advection_method=case.method,
        scaffold_path=scaffold,
        requested_final_time=(
            case.requested_final_time
        ),
        product_dealiasing=(
            PRODUCT_DEALIASING
        ),
        post_step_mask_policy=None,
    )


def _solver_construction_smoke(
    modules: LoadedModules,
) -> tuple[
    Mapping[
        str,
        object,
    ],
    ...,
]:
    harness = modules.harness

    records = []

    temporary_path: (
        Path
        | None
    ) = None

    smoke_cases = (
        PilotCase(
            O1_ID,
            "O1",
            "fd_centered",
            0,
            0.0,
        ),
        PilotCase(
            O1_ID,
            "O1",
            "pseudo_spectral",
            0,
            0.0,
        ),
        PilotCase(
            O1_ID,
            "O1",
            "arakawa",
            0,
            0.0,
        ),
        PilotCase(
            L_ID,
            "L",
            None,
            EVOLUTION_STEPS,
            EVOLUTION_FINAL_TIME,
        ),
    )

    with tempfile.TemporaryDirectory(
        prefix=(
            "phase13F_"
            "solver_smoke_"
        )
    ) as temporary:
        temporary_path = Path(
            temporary
        )

        for (
            index,
            case,
        ) in enumerate(
            smoke_cases
        ):
            scaffold = (
                temporary_path
                / f"case_{index:02d}"
                / "_solver_scaffold"
            )

            config = _config_for_case(
                harness,
                case,
                scaffold,
            )

            boundary = (
                harness
                .validate_phase13f_pilot_boundary(
                    config
                )
            )

            if (
                boundary[
                    "pilot_boundary_valid"
                ]
                is not True
            ):
                raise RuntimeError(
                    "Pilot boundary "
                    "did not validate"
                )

            (
                solver,
                contract,
            ) = (
                harness
                .construct_guarded_solver(
                    config
                )
            )

            if (
                type(solver).__name__
                != (
                    "SelectableAdvectionSolver"
                )
            ):
                raise RuntimeError(
                    "Unexpected solver class"
                )

            if not scaffold.is_dir():
                raise RuntimeError(
                    "Solver scaffold "
                    "was not created"
                )

            if any(
                scaffold.iterdir()
            ):
                raise RuntimeError(
                    "Solver construction "
                    "wrote an unexpected "
                    "scaffold file"
                )

            records.append(
                asdict(contract)
            )

    if (
        temporary_path is None
        or temporary_path.exists()
    ):
        raise RuntimeError(
            "Solver-construction "
            "temporary cleanup failed"
        )

    return tuple(records)


# END CHUNK 3

def _instrument_solver(
    solver: Any,
) -> CallCounter:
    counter = CallCounter()

    original_advection = (
        solver.compute_advection
    )

    original_diffusion = (
        solver.laplacian_spectral
    )

    def counted_advection(
        value: np.ndarray,
    ) -> np.ndarray:
        counter.advection += 1

        return original_advection(
            value
        )

    def counted_diffusion(
        value: np.ndarray,
    ) -> np.ndarray:
        counter.diffusion += 1

        return original_diffusion(
            value
        )

    def prohibited_forcing(
        *_args: object,
        **_kwargs: object,
    ) -> np.ndarray:
        counter.forcing += 1

        raise RuntimeError(
            "Inherited forcing was called "
            "during Phase 13F"
        )

    solver.compute_advection = (
        counted_advection
    )

    solver.laplacian_spectral = (
        counted_diffusion
    )

    solver.forcing = (
        prohibited_forcing
    )

    for name in (
        "compute_rhs_selectable",
        "step_once_selectable",
        "run_selectable_diagnostic",
        "run",
    ):
        if hasattr(
            solver,
            name,
        ):
            def denied(
                *_args: object,
                _name: str = name,
                **_kwargs: object,
            ) -> None:
                counter.prohibited += 1

                raise RuntimeError(
                    "Prohibited solver "
                    "interface called: "
                    f"{_name}"
                )

            setattr(
                solver,
                name,
                denied,
            )

    return counter


def _case_error_summary(
    result: Any,
) -> Mapping[str, object]:
    return asdict(
        result.error_norms
    )


def _case_arrays(
    result: Any,
) -> Mapping[
    str,
    np.ndarray,
]:
    if result.track in (
        "O1",
        "O2",
    ):
        return {
            "omega_raw": (
                result.omega_raw
            ),
            "omega_input": (
                result.omega_input
            ),
            "computed_adv": (
                result.computed_adv
            ),
            "exact_adv": (
                result.exact_adv
            ),
            "error_adv": (
                result.error_adv
            ),
        }

    return {
        "initial_omega": (
            result.initial_omega
        ),
        "numerical_omega": (
            result.numerical_omega
        ),
        "exact_omega": (
            result.exact_omega
        ),
        "error_omega": (
            result.error_omega
        ),
    }


def _case_metadata(
    modules: LoadedModules,
    context: PreflightContext,
    environment: Mapping[
        str,
        object,
    ],
    case: PilotCase,
    result: Any,
    counter: CallCounter,
) -> Mapping[str, object]:
    exact = modules.exact
    schema = modules.schema

    definition = (
        exact.get_benchmark_definition(
            case.benchmark_id
        )
    )

    contract = result.metadata[
        "solver_contract"
    ]

    if case.track in (
        "O1",
        "O2",
    ):
        input_unchanged = bool(
            result
            .mutation_guard
            .input_unchanged
        )

        solver_state_unchanged = bool(
            result
            .mutation_guard
            .solver_state_unchanged
        )

        mask_count = int(
            result
            .mask_application_count
        )

        allowed_methods = (
            "compute_advection",
        )

        final_time = T0

    else:
        input_unchanged = all(
            bool(
                step.input_unchanged
            )
            for step in result.steps
        )

        solver_state_unchanged = all(
            bool(
                step
                .solver_state_unchanged
            )
            for step in result.steps
        )

        mask_count = int(
            result
            .total_mask_applications
        )

        allowed_methods = (
            (
                "laplacian_spectral",
            )
            if case.track == "L"
            else (
                "compute_advection",
                "laplacian_spectral",
            )
        )

        final_time = float(
            result.final_time
        )

    return {
        "schema_id": (
            schema.METADATA_SCHEMA_ID
        ),
        "repository": dict(
            _repository_record(
                context
            )
        ),
        "environment": dict(
            environment
        ),
        "benchmark": {
            (
                "benchmark_id"
            ): case.benchmark_id,
            "track": case.track,
            (
                "reference_version"
            ): (
                definition
                .reference_version
            ),
            (
                "compatibility_policy"
            ): (
                definition
                .compatibility_policy
            ),
            (
                "source_policy"
            ): (
                definition
                .source_policy
            ),
            (
                "advection_method"
            ): case.method,
            (
                "product_dealiasing"
            ): False,
            (
                "post_step_mask_policy"
            ): (
                definition
                .post_step_mask_policy
            ),
        },
        "numerical": {
            "N": int(
                contract.N
            ),
            "L": float(
                contract.L
            ),
            "dx": float(
                contract.dx
            ),
            "Re": float(
                contract.Re
            ),
            "nu": float(
                contract.nu
            ),
            "dt": float(
                contract.dt
            ),
            (
                "n_steps"
            ): case.n_steps,
            "t_0": T0,
            (
                "t_final_actual"
            ): final_time,
            (
                "t_final_requested"
            ): (
                case
                .requested_final_time
            ),
            (
                "final_time_aligned"
            ): True,
            (
                "constructor_steps"
            ): int(
                contract
                .constructor_steps
            ),
        },
        "execution": {
            (
                "solver_class"
            ): (
                contract
                .solver_class
            ),
            (
                "allowed_methods_called"
            ): list(
                allowed_methods
            ),
            (
                "prohibited_methods_called"
            ): [],
            (
                "forcing_call_count"
            ): int(
                counter.forcing
            ),
            (
                "mask_application_count"
            ): mask_count,
            (
                "input_unchanged"
            ): input_unchanged,
            (
                "solver_state_unchanged"
            ): solver_state_unchanged,
        },
        "result": {
            "case_id": (
                result.case_id
            ),
            (
                "case_status"
            ): "PASS",
            (
                "output_filenames"
            ): dict(
                schema
                .CASE_OUTPUT_FILENAMES
            ),
            (
                "output_sha256"
            ): {},
            (
                "error_summary"
            ): dict(
                _case_error_summary(
                    result
                )
            ),
            (
                "failure_messages"
            ): [],
        },
    }


def _case_checks(
    context: PreflightContext,
    case: PilotCase,
    result: Any,
    counter: CallCounter,
    source_evaluations: int,
) -> Mapping[str, object]:
    if case.track in (
        "O1",
        "O2",
    ):
        input_unchanged = bool(
            result
            .mutation_guard
            .input_unchanged
        )

        solver_state_unchanged = bool(
            result
            .mutation_guard
            .solver_state_unchanged
        )

        output_input_independent = (
            not bool(
                result
                .mutation_guard
                .output_shares_input_memory
            )
        )

        output_state_independent = (
            not bool(
                result
                .mutation_guard
                .output_shares_solver_state_memory
            )
        )

        mask_count = int(
            result
            .mask_application_count
        )

        final_time = T0

        stage_times: list[
            Mapping[
                str,
                object,
            ]
        ] = []

    else:
        input_unchanged = all(
            bool(
                step.input_unchanged
            )
            for step in result.steps
        )

        solver_state_unchanged = all(
            bool(
                step
                .solver_state_unchanged
            )
            for step in result.steps
        )

        output_input_independent = True
        output_state_independent = True

        mask_count = int(
            result
            .total_mask_applications
        )

        final_time = float(
            result.final_time
        )

        stage_times = [
            {
                "t_n": float(
                    step.t_n
                ),
                (
                    "t_stage_1"
                ): float(
                    step.t_stage_1
                ),
                (
                    "t_stage_2"
                ): float(
                    step.t_stage_2
                ),
                "t_next": float(
                    step.t_next
                ),
                (
                    "stage_1_"
                    "source_sha256"
                ): (
                    step
                    .stage_1_source_sha256
                ),
                (
                    "stage_2_"
                    "source_sha256"
                ): (
                    step
                    .stage_2_source_sha256
                ),
            }
            for step in result.steps
        ]

    return {
        "runner_version": (
            RUNNER_VERSION
        ),
        "phase": "13F",
        "run_id": context.run_id,
        (
            "authorized_commit"
        ): context.head,
        (
            "authorized_tag"
        ): context.tag,
        (
            "runner_sha256"
        ): context.runner_sha256,
        (
            "design_sha256"
        ): PINNED_HASHES[
            (
                "PHASE13F_CONTROLLED_"
                "SINGLE_GRID_VERIFICATION_"
                "PILOT_DESIGN_AND_"
                "AUTHORIZATION.md"
            )
        ],
        (
            "benchmark_id"
        ): case.benchmark_id,
        "track": case.track,
        (
            "advection_method"
        ): case.method,
        (
            "pilot_boundary_valid"
        ): True,
        (
            "module_hash_gate"
        ): True,
        (
            "protected_source_hash_gate"
        ): True,
        (
            "solver_grid_agreement"
        ): True,
        (
            "solver_mask_agreement"
        ): True,
        (
            "viscosity_agreement"
        ): True,
        (
            "timestep_agreement"
        ): True,
        (
            "constructor_steps_agreement"
        ): True,
        (
            "product_dealiasing"
        ): False,
        (
            "forcing_call_count"
        ): counter.forcing,
        (
            "advection_call_count"
        ): counter.advection,
        (
            "diffusion_call_count"
        ): counter.diffusion,
        (
            "analytic_source_"
            "evaluation_count"
        ): source_evaluations,
        (
            "prohibited_interface_"
            "call_count"
        ): counter.prohibited,
        (
            "input_unchanged"
        ): input_unchanged,
        (
            "solver_state_unchanged"
        ): solver_state_unchanged,
        (
            "output_input_"
            "memory_independent"
        ): output_input_independent,
        (
            "output_solver_state_"
            "memory_independent"
        ): output_state_independent,
        (
            "mask_application_count"
        ): mask_count,
        (
            "initial_time"
        ): T0,
        (
            "final_time"
        ): final_time,
        (
            "final_time_aligned"
        ): bool(
            np.isclose(
                final_time,
                case
                .requested_final_time,
                rtol=0.0,
                atol=1e-15,
            )
        ),
        (
            "primary_error_finite"
        ): bool(
            result
            .error_norms
            .finite
        ),
        (
            "stage_records"
        ): stage_times,
        (
            "case_status"
        ): "PASS",
        (
            "convergence_claim"
        ): False,
        (
            "physical_validation_claim"
        ): False,
    }


def _verify_case_runtime_counts(
    case: PilotCase,
    result: Any,
    counter: CallCounter,
) -> int:
    if (
        counter.forcing != 0
        or counter.prohibited != 0
    ):
        raise RuntimeError(
            "Prohibited solver pathway "
            "was called"
        )

    if case.track in (
        "O1",
        "O2",
    ):
        expected_advection = 1
        expected_diffusion = 0
        expected_masks = 0
        expected_steps = 0
        source_evaluations = 0

    elif case.track == "L":
        expected_advection = 0
        expected_diffusion = 4
        expected_masks = 2
        expected_steps = 2
        source_evaluations = 0

    else:
        expected_advection = 4
        expected_diffusion = 4
        expected_masks = 2
        expected_steps = 2

        source_evaluations = sum(
            int(
                step
                .stage_1_source_sha256
                is not None
            )
            + int(
                step
                .stage_2_source_sha256
                is not None
            )
            for step in result.steps
        )

        if source_evaluations != 4:
            raise RuntimeError(
                "Track M source-stage "
                "count mismatch"
            )

        for step in result.steps:
            if not (
                step.t_stage_2
                > step.t_stage_1
            ):
                raise RuntimeError(
                    "Track M stage times "
                    "are not distinct"
                )

    observed_masks = (
        int(
            result
            .mask_application_count
        )
        if case.track in (
            "O1",
            "O2",
        )
        else int(
            result
            .total_mask_applications
        )
    )

    observed_steps = (
        0
        if case.track in (
            "O1",
            "O2",
        )
        else len(
            result.steps
        )
    )

    if (
        counter.advection
        != expected_advection
    ):
        raise RuntimeError(
            "Advection call-count mismatch "
            f"for {result.case_id}: "
            f"expected {expected_advection}, "
            f"observed {counter.advection}"
        )

    if (
        counter.diffusion
        != expected_diffusion
    ):
        raise RuntimeError(
            "Diffusion call-count mismatch "
            f"for {result.case_id}: "
            f"expected {expected_diffusion}, "
            f"observed {counter.diffusion}"
        )

    if (
        observed_masks
        != expected_masks
    ):
        raise RuntimeError(
            "Mask-count mismatch "
            f"for {result.case_id}: "
            f"expected {expected_masks}, "
            f"observed {observed_masks}"
        )

    if (
        observed_steps
        != expected_steps
    ):
        raise RuntimeError(
            "Step-count mismatch "
            f"for {result.case_id}: "
            f"expected {expected_steps}, "
            f"observed {observed_steps}"
        )

    if not bool(
        result.error_norms.finite
    ):
        raise RuntimeError(
            "Nonfinite primary error "
            f"for {result.case_id}"
        )

    return source_evaluations


def _run_numerical_pilot(
    modules: LoadedModules,
    context: PreflightContext,
    environment: Mapping[
        str,
        object,
    ],
) -> PilotExecution:
    harness = modules.harness
    schema = modules.schema

    if len(PILOT_CASES) != 10:
        raise RuntimeError(
            "Pilot matrix does not "
            "contain exactly ten cases"
        )

    case_write_results: list[
        Any
    ] = []

    case_records: list[
        Mapping[
            str,
            object,
        ]
    ] = []

    total_advection = 0
    total_diffusion = 0
    total_source = 0
    total_forcing = 0
    total_masks = 0
    total_steps = 0

    scaffold_root_path: (
        Path
        | None
    ) = None

    with tempfile.TemporaryDirectory(
        prefix=(
            "phase13F_"
            "pilot_scaffolds_"
        )
    ) as temporary:
        scaffold_root_path = Path(
            temporary
        )

        for (
            index,
            case,
        ) in enumerate(
            PILOT_CASES,
            start=1,
        ):
            scaffold = (
                scaffold_root_path
                / f"case_{index:02d}"
                / "_solver_scaffold"
            )

            config = _config_for_case(
                harness,
                case,
                scaffold,
            )

            boundary = (
                harness
                .validate_phase13f_pilot_boundary(
                    config
                )
            )

            if (
                boundary[
                    "pilot_boundary_valid"
                ]
                is not True
            ):
                raise RuntimeError(
                    "Case failed the "
                    "pilot-boundary validator"
                )

            if (
                boundary[
                    "pilot_authorized"
                ]
                is not False
            ):
                raise RuntimeError(
                    "Harness module "
                    "unexpectedly "
                    "self-authorized "
                    "the pilot"
                )

            (
                solver,
                _contract,
            ) = (
                harness
                .construct_guarded_solver(
                    config
                )
            )

            counter = (
                _instrument_solver(
                    solver
                )
            )

            print(
                f"CASE {index:02d}/10 "
                f"START: "
                f"{case.benchmark_id} | "
                f"{case.method}"
            )

            if case.track in (
                "O1",
                "O2",
            ):
                result = (
                    harness
                    .run_operator_case(
                        solver,
                        config,
                    )
                )

            else:
                result = (
                    harness
                    .run_evolution_case(
                        solver,
                        config,
                    )
                )

            source_evaluations = (
                _verify_case_runtime_counts(
                    case,
                    result,
                    counter,
                )
            )

            if any(
                scaffold.iterdir()
            ):
                raise RuntimeError(
                    "Unexpected solver-"
                    "scaffold file for "
                    f"{result.case_id}"
                )

            metadata = _case_metadata(
                modules,
                context,
                environment,
                case,
                result,
                counter,
            )

            checks = _case_checks(
                context,
                case,
                result,
                counter,
                source_evaluations,
            )

            arrays = _case_arrays(
                result
            )

            error_summary = (
                _case_error_summary(
                    result
                )
            )

            write_result = (
                schema.write_case_bundle(
                    output_root=(
                        context
                        .run_directory
                    ),
                    metadata=metadata,
                    checks=checks,
                    error_summary=(
                        error_summary
                    ),
                    arrays=arrays,
                )
            )

            case_write_results.append(
                write_result
            )

            case_record = {
                "case_id": (
                    result.case_id
                ),
                "track": case.track,
                "method": case.method,
                (
                    "error_summary"
                ): dict(
                    error_summary
                ),
                (
                    "advection_calls"
                ): counter.advection,
                (
                    "diffusion_calls"
                ): counter.diffusion,
                (
                    "source_evaluations"
                ): source_evaluations,
                (
                    "forcing_calls"
                ): counter.forcing,
                (
                    "mask_applications"
                ): (
                    result
                    .mask_application_count
                    if case.track in (
                        "O1",
                        "O2",
                    )
                    else (
                        result
                        .total_mask_applications
                    )
                ),
            }

            case_records.append(
                case_record
            )

            total_advection += (
                counter.advection
            )

            total_diffusion += (
                counter.diffusion
            )

            total_source += (
                source_evaluations
            )

            total_forcing += (
                counter.forcing
            )

            total_masks += int(
                case_record[
                    "mask_applications"
                ]
            )

            total_steps += (
                0
                if case.track in (
                    "O1",
                    "O2",
                )
                else len(
                    result.steps
                )
            )

            print(
                f"CASE {index:02d}/10 "
                f"PASS: "
                f"{result.case_id} | "
                f"adv={counter.advection} | "
                f"diff={counter.diffusion} | "
                f"masks="
                f"{case_record['mask_applications']} | "
                f"L2="
                f"{result.error_norms.L2_rms:.6e}"
            )

    if (
        scaffold_root_path is None
        or scaffold_root_path.exists()
    ):
        raise RuntimeError(
            "Pilot solver-scaffold "
            "cleanup failed"
        )

    expected_totals = {
        "advection": 18,
        "diffusion": 16,
        "source": 12,
        "forcing": 0,
        "masks": 8,
        "steps": 8,
    }

    observed_totals = {
        "advection": (
            total_advection
        ),
        "diffusion": (
            total_diffusion
        ),
        "source": total_source,
        "forcing": total_forcing,
        "masks": total_masks,
        "steps": total_steps,
    }

    if (
        observed_totals
        != expected_totals
    ):
        raise RuntimeError(
            "Aggregate call-count "
            "mismatch: "
            f"expected {expected_totals}, "
            f"observed {observed_totals}"
        )

    run_write_result = (
        schema.write_run_manifest(
            run_directory=(
                context.run_directory
            ),
            run_id=context.run_id,
            run_status="PASS",
            created_utc=str(
                environment[
                    "timestamp_utc"
                ]
            ),
            repository=(
                _repository_record(
                    context
                )
            ),
            environment=environment,
            cases=tuple(
                case_write_results
            ),
        )
    )

    return PilotExecution(
        case_results=tuple(
            case_write_results
        ),
        case_records=tuple(
            case_records
        ),
        run_write_result=(
            run_write_result
        ),
        total_advection_calls=(
            total_advection
        ),
        total_diffusion_calls=(
            total_diffusion
        ),
        total_source_evaluations=(
            total_source
        ),
        total_forcing_calls=(
            total_forcing
        ),
        total_mask_applications=(
            total_masks
        ),
        total_rk2_steps=(
            total_steps
        ),
        scaffold_root=(
            scaffold_root_path
        ),
    )


# END CHUNK 4

def _post_run_audit(
    modules: LoadedModules,
    context: PreflightContext,
    execution: PilotExecution,
) -> Mapping[str, object]:
    schema = modules.schema

    run_directory = (
        context.run_directory
    )

    if not run_directory.is_dir():
        raise RuntimeError(
            "Persistent run directory "
            "is absent"
        )

    run_manifest_path = (
        run_directory
        / schema.RUN_MANIFEST_FILENAME
    )

    if not run_manifest_path.is_file():
        raise RuntimeError(
            "Run manifest is absent"
        )

    expected_case_ids = {
        str(
            record["case_id"]
        )
        for record in (
            execution.case_records
        )
    }

    observed_case_dirs = {
        path.name
        for path in (
            run_directory.iterdir()
        )
        if path.is_dir()
    }

    if (
        observed_case_dirs
        != expected_case_ids
    ):
        raise RuntimeError(
            "Persistent case-directory "
            "set mismatch"
        )

    expected_case_files = set(
        schema
        .CASE_OUTPUT_FILENAMES
        .values()
    )

    persistent_file_count = 1

    for (
        write_result,
        case_record,
    ) in zip(
        execution.case_results,
        execution.case_records,
        strict=True,
    ):
        case_id = str(
            case_record[
                "case_id"
            ]
        )

        case_directory = (
            run_directory
            / case_id
        )

        observed_files = {
            path.name
            for path in (
                case_directory.iterdir()
            )
            if path.is_file()
        }

        if (
            observed_files
            != expected_case_files
        ):
            raise RuntimeError(
                "Case file set mismatch "
                f"for {case_id}"
            )

        persistent_file_count += len(
            observed_files
        )

        for (
            logical_name,
            record,
        ) in (
            write_result
            .files
            .items()
        ):
            path = (
                case_directory
                / record.filename
            )

            observed_hash = (
                schema.sha256_file(
                    path
                )
            )

            if (
                observed_hash
                != record.sha256
            ):
                raise RuntimeError(
                    "Physical hash mismatch "
                    f"for {case_id}/"
                    f"{logical_name}"
                )

        metadata = json.loads(
            (
                case_directory
                / (
                    schema
                    .CASE_METADATA_FILENAME
                )
            ).read_text(
                encoding="utf-8"
            )
        )

        checks = json.loads(
            (
                case_directory
                / schema.CHECKS_FILENAME
            ).read_text(
                encoding="utf-8"
            )
        )

        field_manifest = json.loads(
            (
                case_directory
                / (
                    schema
                    .FIELD_MANIFEST_FILENAME
                )
            ).read_text(
                encoding="utf-8"
            )
        )

        if (
            metadata["result"][
                "case_status"
            ]
            != "PASS"
        ):
            raise RuntimeError(
                "Case metadata is not "
                f"PASS: {case_id}"
            )

        if (
            checks["case_status"]
            != "PASS"
        ):
            raise RuntimeError(
                "Checks record is not "
                f"PASS: {case_id}"
            )

        with (
            case_directory
            / (
                schema
                .ERROR_SUMMARY_FILENAME
            )
        ).open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            reader = csv.DictReader(
                handle
            )

            rows = list(reader)

        if (
            tuple(
                reader.fieldnames
                or ()
            )
            != tuple(
                schema
                .ERROR_SUMMARY_COLUMNS
            )
        ):
            raise RuntimeError(
                "Error-summary columns "
                f"mismatch: {case_id}"
            )

        if len(rows) != 1:
            raise RuntimeError(
                "Error-summary row count "
                f"mismatch: {case_id}"
            )

        track = str(
            case_record[
                "track"
            ]
        )

        expected_arrays = (
            set(
                schema
                .OPERATOR_ARRAY_NAMES
            )
            if track in (
                "O1",
                "O2",
            )
            else set(
                schema
                .EVOLUTION_ARRAY_NAMES
            )
        )

        with np.load(
            (
                case_directory
                / schema.FIELDS_FILENAME
            ),
            allow_pickle=False,
        ) as archive:
            if (
                set(archive.files)
                != expected_arrays
            ):
                raise RuntimeError(
                    "NPZ array set mismatch: "
                    f"{case_id}"
                )

            if (
                field_manifest[
                    "array_count"
                ]
                != len(
                    expected_arrays
                )
            ):
                raise RuntimeError(
                    "Field-manifest count "
                    f"mismatch: {case_id}"
                )

            for name in archive.files:
                array = archive[name]

                if array.shape != (
                    N,
                    N,
                ):
                    raise RuntimeError(
                        "Stored array shape "
                        "mismatch: "
                        f"{case_id}/{name}"
                    )

                if (
                    not np.isrealobj(
                        array
                    )
                    or not np.isfinite(
                        array
                    ).all()
                ):
                    raise RuntimeError(
                        "Stored array invalid: "
                        f"{case_id}/{name}"
                    )

                manifest_entry = (
                    field_manifest[
                        "arrays"
                    ][name]
                )

                if (
                    manifest_entry[
                        "sha256"
                    ]
                    != schema.hash_array(
                        array
                    )
                ):
                    raise RuntimeError(
                        "Array hash mismatch: "
                        f"{case_id}/{name}"
                    )

        recorded_hashes = (
            metadata["result"][
                "output_sha256"
            ]
        )

        for logical_name in (
            "checks",
            "error_summary",
            "fields",
            "field_manifest",
        ):
            physical = (
                case_directory
                / (
                    schema
                    .CASE_OUTPUT_FILENAMES[
                        logical_name
                    ]
                )
            )

            if (
                recorded_hashes[
                    logical_name
                ]
                != schema.sha256_file(
                    physical
                )
            ):
                raise RuntimeError(
                    "Metadata output hash "
                    "mismatch: "
                    f"{case_id}/"
                    f"{logical_name}"
                )

    run_manifest = json.loads(
        run_manifest_path.read_text(
            encoding="utf-8"
        )
    )

    if (
        run_manifest[
            "run_status"
        ]
        != "PASS"
    ):
        raise RuntimeError(
            "Run manifest status "
            "is not PASS"
        )

    if (
        run_manifest[
            "case_count"
        ]
        != 10
    ):
        raise RuntimeError(
            "Run manifest case count "
            "is not ten"
        )

    if (
        set(
            execution
            .run_write_result
            .case_ids
        )
        != expected_case_ids
    ):
        raise RuntimeError(
            "Run-write result "
            "case IDs mismatch"
        )

    if persistent_file_count != 51:
        raise RuntimeError(
            "Persistent output count "
            "mismatch: expected 51, "
            f"observed "
            f"{persistent_file_count}"
        )

    remaining_temporary_files = tuple(
        run_directory.rglob(
            "*.tmp"
        )
    )

    if remaining_temporary_files:
        raise RuntimeError(
            "Persistent temporary "
            "files remain: "
            f"{remaining_temporary_files!r}"
        )

    if (
        execution
        .scaffold_root
        .exists()
    ):
        raise RuntimeError(
            "Solver scaffold root "
            "remains after execution"
        )

    _verify_pinned_hashes()
    _verify_verification_boundary()

    if (
        _sha256_file(
            RUNNER_PATH
        )
        != context.runner_sha256
    ):
        raise RuntimeError(
            "Runner source changed "
            "during execution"
        )

    status = _git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )

    expected_prefix = (
        "?? experiments/verification/"
        f"phase13/{context.run_id}/"
    )

    status_lines = tuple(
        line
        for line in (
            status.splitlines()
        )
        if line
    )

    if not status_lines:
        raise RuntimeError(
            "Git status does not "
            "contain the authorized "
            "result files"
        )

    if any(
        not line.startswith(
            expected_prefix
        )
        for line in status_lines
    ):
        raise RuntimeError(
            "Repository status contains "
            "a path outside the "
            "authorized run directory"
        )

    return {
        "run_directory": str(
            run_directory
        ),
        (
            "case_directories"
        ): len(
            observed_case_dirs
        ),
        (
            "persistent_files"
        ): persistent_file_count,
        (
            "temporary_files"
        ): len(
            remaining_temporary_files
        ),
        (
            "status_entries"
        ): len(
            status_lines
        ),
        (
            "run_manifest_sha256"
        ): schema.sha256_file(
            run_manifest_path
        ),
    }


def _print_heading(
    title: str,
) -> None:
    print("")
    print(
        "=" * 72
    )
    print(title)
    print(
        "=" * 72
    )


def main() -> int:
    try:
        _print_heading(
            (
                "PHASE 13F CONTROLLED "
                "SINGLE-GRID "
                "VERIFICATION PILOT"
            )
        )

        context = _preflight()

        print(
            "Authorized commit: "
            f"{context.head}"
        )

        print(
            "Authorized tag:    "
            f"{context.tag}"
        )

        print(
            "Run identifier:    "
            f"{context.run_id}"
        )

        print(
            "Python executable: "
            f"{sys.executable}"
        )

        print(
            "Working directory: "
            f"{Path.cwd()}"
        )

        print(
            "Preflight:         PASS"
        )

        modules = _load_modules(
            context
        )

        print(
            "Import smoke:      PASS"
        )

        environment = (
            modules
            .schema
            .environment_record()
        )

        exact_smoke = (
            _exact_reference_smoke(
                modules
            )
        )

        print(
            "Exact references:  "
            f"{len(exact_smoke)}/4 "
            "PASS"
        )

        with tempfile.TemporaryDirectory(
            prefix=(
                "phase13F_"
                "rejections_"
            )
        ) as temporary:
            rejection_results = (
                _configuration_rejection_tests(
                    modules,
                    Path(temporary),
                )
            )

        print(
            "Config rejections: "
            f"{len(rejection_results)} "
            "PASS"
        )

        mutation_results = (
            _mutation_guard_tests(
                modules
            )
        )

        print(
            "Mutation guards:   "
            f"{len(mutation_results)} "
            "PASS"
        )

        schema_rejections = (
            _schema_rejection_tests(
                modules,
                context,
                environment,
            )
        )

        print(
            "Schema rejections: "
            f"{len(schema_rejections)} "
            "PASS"
        )

        atomic_hashes = (
            _atomic_writer_smoke(
                modules
            )
        )

        print(
            "Atomic writers:    "
            f"{len(atomic_hashes)}/3 "
            "PASS"
        )

        solver_smoke = (
            _solver_construction_smoke(
                modules
            )
        )

        print(
            "Solver constructs: "
            f"{len(solver_smoke)}/4 "
            "PASS"
        )

        execution = (
            _run_numerical_pilot(
                modules,
                context,
                environment,
            )
        )

        audit = _post_run_audit(
            modules,
            context,
            execution,
        )

        _print_heading(
            "PHASE 13F PILOT SUMMARY"
        )

        print(
            "Preflight:                    PASS"
        )
        print(
            "Import smoke:                 PASS"
        )
        print(
            "Exact-reference smoke:        PASS"
        )
        print(
            "Configuration rejections:     PASS"
        )
        print(
            "Mutation-guard tests:         PASS"
        )
        print(
            "Output-schema rejections:     PASS"
        )
        print(
            "Atomic-writer temporary test: PASS"
        )
        print(
            "Solver-construction smoke:    PASS"
        )
        print(
            "O1 cases:                     3/3 PASS"
        )
        print(
            "O2 cases:                     3/3 PASS"
        )
        print(
            "Track L cases:                1/1 PASS"
        )
        print(
            "Track M cases:                3/3 PASS"
        )
        print(
            "Total numerical cases:        10/10 PASS"
        )
        print(
            "External RK2 steps:           "
            f"{execution.total_rk2_steps}"
        )
        print(
            "Advection calls:              "
            f"{execution.total_advection_calls}"
        )
        print(
            "Diffusion calls:              "
            f"{execution.total_diffusion_calls}"
        )
        print(
            "Track M source evaluations:   "
            f"{execution.total_source_evaluations}"
        )
        print(
            "Forcing calls:                "
            f"{execution.total_forcing_calls}"
        )
        print(
            "Post-step masks:              "
            f"{execution.total_mask_applications}"
        )
        print(
            "Persistent output files:      "
            f"{audit['persistent_files']}"
        )
        print(
            "Output directory:             "
            f"{audit['run_directory']}"
        )
        print(
            "Refinement sequence:          NONE"
        )
        print(
            "Observed order:               NONE"
        )
        print(
            "Convergence claim:            NONE"
        )
        print(
            "Physical-validation claim:    NONE"
        )
        print("")
        print(
            "PHASE 13F CONTROLLED PILOT: PASS"
        )

        return 0

    except Exception as exc:
        _print_heading(
            "PHASE 13F CONTROLLED PILOT: FAIL"
        )

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        traceback.print_exc()

        return 2


if __name__ == "__main__":
    raise SystemExit(
        main()
    )


# END CHUNK 5
