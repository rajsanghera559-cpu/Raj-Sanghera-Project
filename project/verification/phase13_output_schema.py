"""
Deterministic Phase 13 output schema and atomic result writer.

Phase 13E.3 boundary:
- standard library and NumPy only;
- no project or solver imports;
- no solver construction or numerical evaluation;
- no top-level file output;
- no plotting, rate fitting, pilot authorization, or convergence claim.

The functions remain dormant until explicitly called by a later authorized
runner.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from hashlib import sha256
from io import StringIO
import csv
import json
import os
from pathlib import Path
import platform
import re
import tempfile
from types import MappingProxyType
from typing import Mapping, Sequence

import numpy as np


METADATA_SCHEMA_ID = "PHASE13_VERIFICATION_METADATA_V1"
OUTPUT_SCHEMA_ID = "PHASE13_VERIFICATION_OUTPUT_V1"
FIELD_MANIFEST_SCHEMA_ID = "PHASE13_FIELD_MANIFEST_V1"
RUN_MANIFEST_SCHEMA_ID = "PHASE13_RUN_MANIFEST_V1"

OUTPUT_ROOT = Path(
    "experiments/verification/phase13"
)

RUN_MANIFEST_FILENAME = "run_manifest.json"
CASE_METADATA_FILENAME = "case_metadata.json"
CHECKS_FILENAME = "checks.json"
ERROR_SUMMARY_FILENAME = "error_summary.csv"
FIELDS_FILENAME = "fields.npz"
FIELD_MANIFEST_FILENAME = "field_manifest.json"

CASE_OUTPUT_FILENAMES: Mapping[str, str] = (
    MappingProxyType(
        {
            "case_metadata": (
                CASE_METADATA_FILENAME
            ),
            "checks": CHECKS_FILENAME,
            "error_summary": (
                ERROR_SUMMARY_FILENAME
            ),
            "fields": FIELDS_FILENAME,
            "field_manifest": (
                FIELD_MANIFEST_FILENAME
            ),
        }
    )
)

CASE_STATUSES = (
    "INCOMPLETE",
    "PASS",
    "FAIL",
)

RUN_STATUSES = (
    "INCOMPLETE",
    "PASS",
    "FAIL",
)

SUPPORTED_ADVECTION_METHODS = (
    "fd_centered",
    "pseudo_spectral",
    "arakawa",
)

BENCHMARK_TRACKS: Mapping[str, str] = (
    MappingProxyType(
        {
            "O1_BANDLIMITED_TWO_MODE_V1": (
                "O1"
            ),
            "O2_ANALYTIC_BROAD_SPECTRUM_V1": (
                "O2"
            ),
            "L_EQUAL_EIGENVALUE_DECAY_V1": (
                "L"
            ),
            "M_TWO_RATE_NONLINEAR_MMS_V1": (
                "M"
            ),
        }
    )
)

PROTECTED_SOLVER_PATHS = (
    "project/solver/spectral_solver.py",
    (
        "project/solver/"
        "selectable_advection_solver.py"
    ),
    "project/solver/advection_operators.py",
)

OPERATOR_ARRAY_NAMES = (
    "omega_raw",
    "omega_input",
    "computed_adv",
    "exact_adv",
    "error_adv",
)

EVOLUTION_ARRAY_NAMES = (
    "initial_omega",
    "numerical_omega",
    "exact_omega",
    "error_omega",
)

TRACK_M_OPTIONAL_ARRAY_PREFIXES = (
    "stage_1_source_",
    "stage_2_source_",
    "source_stage_",
)

ERROR_SUMMARY_COLUMNS = (
    "L1_mean",
    "L2_rms",
    "Linf",
    "exact_L2_rms",
    "numerical_L2_rms",
    "relative_L2",
    "finite",
)

_SHA256_RE = re.compile(
    r"^[0-9A-F]{64}$"
)

_COMMIT_RE = re.compile(
    r"^[0-9A-Fa-f]{40}$"
)

_SAFE_TOKEN_RE = re.compile(
    r"^[A-Za-z0-9_.-]+$"
)


class SchemaValidationError(ValueError):
    """Raised when schema content is invalid."""


@dataclass(
    frozen=True,
    slots=True,
)
class FileHashRecord:
    """Identity record for one written file."""

    logical_name: str
    filename: str
    sha256: str
    size_bytes: int


@dataclass(
    frozen=True,
    slots=True,
)
class ArrayManifestEntry:
    """Manifest entry for one stored array."""

    name: str
    shape: tuple[int, ...]
    dtype: str
    nbytes: int
    sha256: str
    finite: bool
    real_valued: bool
    writeable: bool
    minimum: float
    maximum: float
    L2_rms: float


@dataclass(
    frozen=True,
    slots=True,
)
class CaseWriteResult:
    """Result identity for one case bundle."""

    case_id: str
    case_directory: str
    case_status: str
    files: Mapping[
        str,
        FileHashRecord,
    ]
    array_manifest: Mapping[
        str,
        ArrayManifestEntry,
    ]


@dataclass(
    frozen=True,
    slots=True,
)
class RunWriteResult:
    """Result identity for one run manifest."""

    run_id: str
    run_directory: str
    run_status: str
    manifest: FileHashRecord
    case_ids: tuple[str, ...]


def utc_timestamp() -> str:
    """Return a canonical UTC timestamp."""

    return (
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
    )


def environment_record(
) -> Mapping[str, object]:
    """Return immutable environment metadata."""

    return MappingProxyType(
        {
            "timestamp_utc": (
                utc_timestamp()
            ),
            "operating_system": (
                platform.platform()
            ),
            "python_version": (
                platform.python_version()
            ),
            "numpy_version": (
                np.__version__
            ),
            "floating_dtype": (
                "float64"
            ),
            "machine_epsilon": float(
                np.finfo(
                    np.float64
                ).eps
            ),
        }
    )


def _mapping(
    value: object,
    name: str,
) -> Mapping[str, object]:
    """Normalize one string-keyed mapping."""

    if not isinstance(
        value,
        Mapping,
    ):
        raise SchemaValidationError(
            f"{name} must be a mapping"
        )

    result: dict[
        str,
        object,
    ] = {}

    for key, item in value.items():
        if not isinstance(
            key,
            str,
        ):
            raise SchemaValidationError(
                f"{name} requires "
                "string keys"
            )

        result[key] = item

    return MappingProxyType(
        result
    )


def _sequence(
    value: object,
    name: str,
) -> tuple[object, ...]:
    """Normalize one non-string sequence."""

    if isinstance(
        value,
        (
            str,
            bytes,
            bytearray,
        ),
    ):
        raise SchemaValidationError(
            f"{name} must not be "
            "a string"
        )

    if not isinstance(
        value,
        Sequence,
    ):
        raise SchemaValidationError(
            f"{name} must be a sequence"
        )

    return tuple(value)


def _required(
    mapping: Mapping[
        str,
        object,
    ],
    key: str,
    section: str,
) -> object:
    """Return one required field."""

    if key not in mapping:
        raise SchemaValidationError(
            "Missing required metadata "
            f"field: {section}.{key}"
        )

    return mapping[key]


def _nonempty_string(
    value: object,
    name: str,
) -> str:
    """Normalize one nonempty string."""

    if (
        not isinstance(
            value,
            str,
        )
        or not value.strip()
    ):
        raise SchemaValidationError(
            f"{name} must be a "
            "nonempty string"
        )

    return value.strip()


def _finite_float(
    value: object,
    name: str,
    *,
    positive: bool = False,
    nonnegative: bool = False,
) -> float:
    """Normalize one finite real scalar."""

    if (
        isinstance(
            value,
            bool,
        )
        or not np.isscalar(value)
    ):
        raise SchemaValidationError(
            f"{name} must be a real scalar"
        )

    result = float(value)

    if not np.isfinite(result):
        raise SchemaValidationError(
            f"{name} must be finite"
        )

    if (
        positive
        and result <= 0.0
    ):
        raise SchemaValidationError(
            f"{name} must be "
            "strictly positive"
        )

    if (
        nonnegative
        and result < 0.0
    ):
        raise SchemaValidationError(
            f"{name} must be nonnegative"
        )

    return result


def _nonnegative_int(
    value: object,
    name: str,
) -> int:
    """Normalize one nonnegative integer."""

    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            (
                int,
                np.integer,
            ),
        )
    ):
        raise SchemaValidationError(
            f"{name} must be an integer"
        )

    result = int(value)

    if result < 0:
        raise SchemaValidationError(
            f"{name} must be nonnegative"
        )

    return result


def _sha256(
    value: object,
    name: str,
) -> str:
    """Normalize one SHA-256 digest."""

    if not isinstance(
        value,
        str,
    ):
        raise SchemaValidationError(
            f"{name} must be a "
            "SHA-256 string"
        )

    digest = (
        value
        .strip()
        .upper()
    )

    if not _SHA256_RE.fullmatch(
        digest
    ):
        raise SchemaValidationError(
            f"{name} is not a "
            "SHA-256 digest"
        )

    return digest


def _safe_token(
    value: object,
    name: str,
) -> str:
    """Validate one path-safe token."""

    if not isinstance(
        value,
        str,
    ):
        raise SchemaValidationError(
            f"{name} must be a string"
        )

    token = value.strip()

    if (
        not token
        or not _SAFE_TOKEN_RE.fullmatch(
            token
        )
    ):
        raise SchemaValidationError(
            f"{name} is not a "
            "safe path token"
        )

    if token in {
        ".",
        "..",
    }:
        raise SchemaValidationError(
            f"{name} is not allowed"
        )

    return token


def json_safe(
    value: object,
) -> object:
    """
    Recursively convert metadata to strict
    JSON-safe built-in values.
    """

    if (
        is_dataclass(value)
        and not isinstance(
            value,
            type,
        )
    ):
        return json_safe(
            asdict(value)
        )

    if isinstance(
        value,
        Path,
    ):
        return str(value)

    if isinstance(
        value,
        Mapping,
    ):
        result: dict[
            str,
            object,
        ] = {}

        for key, item in value.items():
            if not isinstance(
                key,
                str,
            ):
                raise SchemaValidationError(
                    "JSON mappings require "
                    "string keys"
                )

            result[key] = json_safe(
                item
            )

        return result

    if isinstance(
        value,
        np.ndarray,
    ):
        if (
            not np.isrealobj(value)
            or not np.isfinite(
                value
            ).all()
        ):
            raise SchemaValidationError(
                "JSON arrays must be "
                "finite and real"
            )

        return value.tolist()

    if isinstance(
        value,
        (
            tuple,
            list,
        ),
    ):
        return [
            json_safe(item)
            for item in value
        ]

    if (
        value is None
        or isinstance(
            value,
            (
                str,
                bool,
                int,
            ),
        )
    ):
        return value

    if isinstance(
        value,
        np.integer,
    ):
        return int(value)

    if isinstance(
        value,
        (
            float,
            np.floating,
        ),
    ):
        result = float(value)

        if not np.isfinite(result):
            raise SchemaValidationError(
                "JSON does not allow "
                "NaN or infinity"
            )

        return result

    raise SchemaValidationError(
        "Unsupported JSON type: "
        f"{type(value).__name__}"
    )


def canonical_json_bytes(
    value: object,
) -> bytes:
    """Return deterministic UTF-8 JSON."""

    text = json.dumps(
        json_safe(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        indent=2,
        separators=(
            ",",
            ": ",
        ),
    )

    return (
        text
        + "\n"
    ).encode(
        "utf-8"
    )


def sha256_bytes(
    value: bytes,
) -> str:
    """Hash one byte sequence."""

    return (
        sha256(value)
        .hexdigest()
        .upper()
    )


def sha256_file(
    path: Path,
) -> str:
    """Hash one regular file."""

    file_path = Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(
            file_path
        )

    digest = sha256()

    with file_path.open(
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


def hash_array(
    value: object,
) -> str:
    """
    Hash one array with dtype and shape
    included in the digest.
    """

    array = np.ascontiguousarray(
        np.asarray(value)
    )

    digest = sha256()

    digest.update(
        str(
            array.dtype
        ).encode(
            "utf-8"
        )
    )

    digest.update(
        b"\x00"
    )

    digest.update(
        repr(
            array.shape
        ).encode(
            "ascii"
        )
    )

    digest.update(
        b"\x00"
    )

    digest.update(
        array.tobytes(
            order="C"
        )
    )

    return (
        digest
        .hexdigest()
        .upper()
    )


def deterministic_case_id(
    *,
    benchmark_id: str,
    N: int,
    Re: float,
    dt: float,
    n_steps: int,
    t_0: float,
    advection_method: (
        str
        | None
    ),
) -> str:
    """
    Create the frozen deterministic
    Phase 13 case identifier.
    """

    if benchmark_id not in (
        BENCHMARK_TRACKS
    ):
        raise SchemaValidationError(
            "Unknown benchmark_id="
            f"{benchmark_id!r}"
        )

    if (
        isinstance(
            N,
            bool,
        )
        or not isinstance(
            N,
            (
                int,
                np.integer,
            ),
        )
    ):
        raise SchemaValidationError(
            "N must be an integer"
        )

    size = int(N)

    if (
        size < 2
        or size % 2
    ):
        raise SchemaValidationError(
            "N must be even and "
            "at least 2"
        )

    reynolds = _finite_float(
        Re,
        "Re",
        positive=True,
    )

    time_step = _finite_float(
        dt,
        "dt",
        positive=True,
    )

    steps = _nonnegative_int(
        n_steps,
        "n_steps",
    )

    initial_time = _finite_float(
        t_0,
        "t_0",
    )

    track = BENCHMARK_TRACKS[
        benchmark_id
    ]

    if track == "L":
        if advection_method is not None:
            raise SchemaValidationError(
                "Primary Track L must use "
                "advection_method=None"
            )

        method = "none"

    else:
        if not isinstance(
            advection_method,
            str,
        ):
            raise SchemaValidationError(
                "An advection method "
                "is required"
            )

        method = (
            advection_method
            .strip()
            .lower()
        )

        if method not in (
            SUPPORTED_ADVECTION_METHODS
        ):
            raise SchemaValidationError(
                "Unknown advection method"
            )

    return (
        f"{benchmark_id}"
        f"__N{size}"
        f"__Re{reynolds:.12g}"
        f"__dt{time_step:.12g}"
        f"__steps{steps}"
        f"__t0{initial_time:.12g}"
        f"__method_{method}"
    )


def normalize_error_summary(
    value: object,
) -> Mapping[str, object]:
    """Validate frozen error fields."""

    raw = (
        asdict(value)
        if is_dataclass(value)
        else _mapping(
            value,
            "error_summary",
        )
    )

    missing = [
        key
        for key in (
            ERROR_SUMMARY_COLUMNS
        )
        if key not in raw
    ]

    if missing:
        raise SchemaValidationError(
            "Missing error-summary "
            "fields: "
            + ", ".join(missing)
        )

    result: dict[
        str,
        object,
    ] = {}

    for key in (
        ERROR_SUMMARY_COLUMNS[:5]
    ):
        result[key] = _finite_float(
            raw[key],
            (
                "error_summary."
                f"{key}"
            ),
            nonnegative=True,
        )

    relative = raw[
        "relative_L2"
    ]

    result["relative_L2"] = (
        None
        if relative is None
        else _finite_float(
            relative,
            (
                "error_summary."
                "relative_L2"
            ),
            nonnegative=True,
        )
    )

    if raw["finite"] is not True:
        raise SchemaValidationError(
            "Primary error quantities "
            "must be finite"
        )

    result["finite"] = True

    return MappingProxyType(
        result
    )


def _validate_repository(
    value: object,
) -> Mapping[str, object]:
    """Validate repository metadata."""

    section = _mapping(
        value,
        "repository",
    )

    name = _nonempty_string(
        _required(
            section,
            "name",
            "repository",
        ),
        "repository.name",
    )

    branch = _nonempty_string(
        _required(
            section,
            "branch",
            "repository",
        ),
        "repository.branch",
    )

    commit_raw = _required(
        section,
        "commit",
        "repository",
    )

    dirty = _required(
        section,
        "dirty",
        "repository",
    )

    if (
        not isinstance(
            commit_raw,
            str,
        )
        or not _COMMIT_RE.fullmatch(
            commit_raw.strip()
        )
    ):
        raise SchemaValidationError(
            "repository.commit must "
            "be a full commit"
        )

    if not isinstance(
        dirty,
        bool,
    ):
        raise SchemaValidationError(
            "repository.dirty must "
            "be Boolean"
        )

    protected = _mapping(
        _required(
            section,
            (
                "protected_solver_"
                "sha256"
            ),
            "repository",
        ),
        (
            "repository."
            "protected_solver_sha256"
        ),
    )

    if set(protected) != set(
        PROTECTED_SOLVER_PATHS
    ):
        raise SchemaValidationError(
            "Protected-solver hash set "
            "is incorrect"
        )

    result = {
        "name": name,
        "branch": branch,
        "commit": (
            commit_raw
            .strip()
            .lower()
        ),
        "dirty": dirty,
        (
            "phase13b_"
            "specification_sha256"
        ): _sha256(
            _required(
                section,
                (
                    "phase13b_"
                    "specification_sha256"
                ),
                "repository",
            ),
            (
                "repository."
                "phase13b_"
                "specification_sha256"
            ),
        ),
        (
            "phase13c_"
            "audit_report_sha256"
        ): _sha256(
            _required(
                section,
                (
                    "phase13c_"
                    "audit_report_sha256"
                ),
                "repository",
            ),
            (
                "repository."
                "phase13c_"
                "audit_report_sha256"
            ),
        ),
        (
            "protected_solver_sha256"
        ): MappingProxyType(
            {
                path: _sha256(
                    protected[path],
                    (
                        "protected"
                        f"[{path}]"
                    ),
                )
                for path in (
                    PROTECTED_SOLVER_PATHS
                )
            }
        ),
        (
            "exact_reference_"
            "module_sha256"
        ): _sha256(
            _required(
                section,
                (
                    "exact_reference_"
                    "module_sha256"
                ),
                "repository",
            ),
            (
                "repository."
                "exact_reference_"
                "module_sha256"
            ),
        ),
        (
            "harness_module_sha256"
        ): _sha256(
            _required(
                section,
                (
                    "harness_"
                    "module_sha256"
                ),
                "repository",
            ),
            (
                "repository."
                "harness_module_sha256"
            ),
        ),
        (
            "output_schema_"
            "module_sha256"
        ): _sha256(
            _required(
                section,
                (
                    "output_schema_"
                    "module_sha256"
                ),
                "repository",
            ),
            (
                "repository."
                "output_schema_"
                "module_sha256"
            ),
        ),
    }

    return MappingProxyType(
        result
    )


def _validate_environment(
    value: object,
) -> Mapping[str, object]:
    """Validate environment metadata."""

    section = _mapping(
        value,
        "environment",
    )

    timestamp = _required(
        section,
        "timestamp_utc",
        "environment",
    )

    if (
        not isinstance(
            timestamp,
            str,
        )
        or not timestamp.endswith(
            "Z"
        )
    ):
        raise SchemaValidationError(
            "timestamp_utc must be "
            "a UTC Z timestamp"
        )

    try:
        parsed = (
            datetime.fromisoformat(
                timestamp.replace(
                    "Z",
                    "+00:00",
                )
            )
        )

    except ValueError as exc:
        raise SchemaValidationError(
            "timestamp_utc is invalid"
        ) from exc

    if (
        parsed.utcoffset()
        != timezone.utc.utcoffset(
            parsed
        )
    ):
        raise SchemaValidationError(
            "timestamp_utc must "
            "represent UTC"
        )

    result: dict[
        str,
        object,
    ] = {
        "timestamp_utc": timestamp,
    }

    for key in (
        "operating_system",
        "python_version",
        "numpy_version",
        "floating_dtype",
    ):
        result[key] = (
            _nonempty_string(
                _required(
                    section,
                    key,
                    "environment",
                ),
                f"environment.{key}",
            )
        )

    if (
        result["floating_dtype"]
        != "float64"
    ):
        raise SchemaValidationError(
            "floating_dtype must "
            "be float64"
        )

    epsilon = _finite_float(
        _required(
            section,
            "machine_epsilon",
            "environment",
        ),
        (
            "environment."
            "machine_epsilon"
        ),
        positive=True,
    )

    expected_epsilon = float(
        np.finfo(
            np.float64
        ).eps
    )

    if epsilon != expected_epsilon:
        raise SchemaValidationError(
            "machine_epsilon is not "
            "float64 epsilon"
        )

    result[
        "machine_epsilon"
    ] = epsilon

    return MappingProxyType(
        result
    )


def validate_case_metadata(
    metadata: object,
    *,
    allow_unwritten_outputs: (
        bool
    ) = False,
) -> Mapping[str, object]:
    """
    Validate and normalize complete
    Phase 13 case metadata.
    """

    root = _mapping(
        metadata,
        "metadata",
    )

    if (
        _required(
            root,
            "schema_id",
            "metadata",
        )
        != METADATA_SCHEMA_ID
    ):
        raise SchemaValidationError(
            "metadata.schema_id "
            "is incorrect"
        )

    repository = _validate_repository(
        _required(
            root,
            "repository",
            "metadata",
        )
    )

    environment = _validate_environment(
        _required(
            root,
            "environment",
            "metadata",
        )
    )

    benchmark = _mapping(
        _required(
            root,
            "benchmark",
            "metadata",
        ),
        "benchmark",
    )

    numerical = _mapping(
        _required(
            root,
            "numerical",
            "metadata",
        ),
        "numerical",
    )

    execution = _mapping(
        _required(
            root,
            "execution",
            "metadata",
        ),
        "execution",
    )

    result = _mapping(
        _required(
            root,
            "result",
            "metadata",
        ),
        "result",
    )

    benchmark_id = _required(
        benchmark,
        "benchmark_id",
        "benchmark",
    )

    if benchmark_id not in (
        BENCHMARK_TRACKS
    ):
        raise SchemaValidationError(
            "Unknown benchmark identifier"
        )

    track = _required(
        benchmark,
        "track",
        "benchmark",
    )

    if (
        track
        != BENCHMARK_TRACKS[
            benchmark_id
        ]
    ):
        raise SchemaValidationError(
            "benchmark.track does not "
            "match benchmark_id"
        )

    benchmark_strings: dict[
        str,
        str,
    ] = {}

    for key in (
        "reference_version",
        "compatibility_policy",
        "source_policy",
        "post_step_mask_policy",
    ):
        benchmark_strings[key] = (
            _nonempty_string(
                _required(
                    benchmark,
                    key,
                    "benchmark",
                ),
                f"benchmark.{key}",
            )
        )

    if (
        _required(
            benchmark,
            "product_dealiasing",
            "benchmark",
        )
        is not False
    ):
        raise SchemaValidationError(
            "product_dealiasing must "
            "be false"
        )

    method = _required(
        benchmark,
        "advection_method",
        "benchmark",
    )

    if track == "L":
        if method is not None:
            raise SchemaValidationError(
                "Track L "
                "advection_method "
                "must be null"
            )

        normalized_method = None

    else:
        if not isinstance(
            method,
            str,
        ):
            raise SchemaValidationError(
                "An advection method "
                "is required"
            )

        normalized_method = (
            method
            .strip()
            .lower()
        )

        if normalized_method not in (
            SUPPORTED_ADVECTION_METHODS
        ):
            raise SchemaValidationError(
                "Unknown advection method"
            )

    N_raw = _required(
        numerical,
        "N",
        "numerical",
    )

    if (
        isinstance(
            N_raw,
            bool,
        )
        or not isinstance(
            N_raw,
            (
                int,
                np.integer,
            ),
        )
    ):
        raise SchemaValidationError(
            "numerical.N must "
            "be an integer"
        )

    N = int(N_raw)

    if (
        N < 2
        or N % 2
    ):
        raise SchemaValidationError(
            "numerical.N must be "
            "even and at least 2"
        )

    L = _finite_float(
        _required(
            numerical,
            "L",
            "numerical",
        ),
        "numerical.L",
        positive=True,
    )

    dx = _finite_float(
        _required(
            numerical,
            "dx",
            "numerical",
        ),
        "numerical.dx",
        positive=True,
    )

    Re = _finite_float(
        _required(
            numerical,
            "Re",
            "numerical",
        ),
        "numerical.Re",
        positive=True,
    )

    nu = _finite_float(
        _required(
            numerical,
            "nu",
            "numerical",
        ),
        "numerical.nu",
        positive=True,
    )

    dt = _finite_float(
        _required(
            numerical,
            "dt",
            "numerical",
        ),
        "numerical.dt",
        positive=True,
    )

    n_steps = _nonnegative_int(
        _required(
            numerical,
            "n_steps",
            "numerical",
        ),
        "numerical.n_steps",
    )

    t_0 = _finite_float(
        _required(
            numerical,
            "t_0",
            "numerical",
        ),
        "numerical.t_0",
    )

    t_final_actual = _finite_float(
        _required(
            numerical,
            "t_final_actual",
            "numerical",
        ),
        (
            "numerical."
            "t_final_actual"
        ),
    )

    requested_raw = _required(
        numerical,
        "t_final_requested",
        "numerical",
    )

    t_final_requested = (
        None
        if requested_raw is None
        else _finite_float(
            requested_raw,
            (
                "numerical."
                "t_final_requested"
            ),
        )
    )

    constructor_steps = (
        _nonnegative_int(
            _required(
                numerical,
                "constructor_steps",
                "numerical",
            ),
            (
                "numerical."
                "constructor_steps"
            ),
        )
    )

    if constructor_steps != 0:
        raise SchemaValidationError(
            "constructor_steps must "
            "equal zero"
        )

    if (
        track in {
            "O1",
            "O2",
        }
        and n_steps != 0
    ):
        raise SchemaValidationError(
            "Operator tracks require "
            "n_steps=0"
        )

    if (
        track in {
            "L",
            "M",
        }
        and n_steps <= 0
    ):
        raise SchemaValidationError(
            "Evolution tracks require "
            "n_steps>0"
        )

    L_tolerance = (
        64.0
        * np.finfo(
            np.float64
        ).eps
    )

    if not np.isclose(
        L,
        2.0 * np.pi,
        rtol=0.0,
        atol=L_tolerance,
    ):
        raise SchemaValidationError(
            "L must equal 2*pi"
        )

    expected_dx = L / N

    dx_tolerance = (
        64.0
        * np.finfo(
            np.float64
        ).eps
        * max(
            1.0,
            abs(dx),
            abs(expected_dx),
        )
    )

    if not np.isclose(
        dx,
        expected_dx,
        rtol=0.0,
        atol=dx_tolerance,
    ):
        raise SchemaValidationError(
            "dx is inconsistent "
            "with L/N"
        )

    expected_nu = 1.0 / Re

    nu_tolerance = (
        64.0
        * np.finfo(
            np.float64
        ).eps
        * max(
            1.0,
            abs(nu),
            abs(expected_nu),
        )
    )

    if not np.isclose(
        nu,
        expected_nu,
        rtol=0.0,
        atol=nu_tolerance,
    ):
        raise SchemaValidationError(
            "nu is inconsistent "
            "with 1/Re"
        )

    expected_final = (
        t_0
        + n_steps * dt
    )

    time_tolerance = (
        64.0
        * np.finfo(
            np.float64
        ).eps
        * max(
            1.0,
            abs(expected_final),
            abs(t_final_actual),
        )
    )

    if not np.isclose(
        t_final_actual,
        expected_final,
        rtol=0.0,
        atol=time_tolerance,
    ):
        raise SchemaValidationError(
            "t_final_actual "
            "is inconsistent"
        )

    aligned = (
        t_final_requested is None
        or np.isclose(
            t_final_requested,
            t_final_actual,
            rtol=0.0,
            atol=time_tolerance,
        )
    )

    declared_aligned = _required(
        numerical,
        "final_time_aligned",
        "numerical",
    )

    if (
        not isinstance(
            declared_aligned,
            bool,
        )
        or declared_aligned
        is not bool(aligned)
    ):
        raise SchemaValidationError(
            "final_time_aligned "
            "is incorrect"
        )

    if not aligned:
        raise SchemaValidationError(
            "Requested and actual "
            "final times differ"
        )

    status_raw = _required(
        result,
        "case_status",
        "result",
    )

    if not isinstance(
        status_raw,
        str,
    ):
        raise SchemaValidationError(
            "case_status must "
            "be a string"
        )

    case_status = (
        status_raw
        .strip()
        .upper()
    )

    if case_status not in (
        CASE_STATUSES
    ):
        raise SchemaValidationError(
            "Unknown case status"
        )

    if (
        case_status
        == "INCOMPLETE"
        and not allow_unwritten_outputs
    ):
        raise SchemaValidationError(
            "INCOMPLETE is not "
            "a final case status"
        )

    case_id = deterministic_case_id(
        benchmark_id=str(
            benchmark_id
        ),
        N=N,
        Re=Re,
        dt=dt,
        n_steps=n_steps,
        t_0=t_0,
        advection_method=(
            normalized_method
        ),
    )

    if (
        _required(
            result,
            "case_id",
            "result",
        )
        != case_id
    ):
        raise SchemaValidationError(
            "case_id is not deterministic"
        )

    filenames = _mapping(
        _required(
            result,
            "output_filenames",
            "result",
        ),
        (
            "result."
            "output_filenames"
        ),
    )

    if dict(filenames) != dict(
        CASE_OUTPUT_FILENAMES
    ):
        raise SchemaValidationError(
            "output_filenames differs "
            "from the schema"
        )

    hashes = _mapping(
        _required(
            result,
            "output_sha256",
            "result",
        ),
        "result.output_sha256",
    )

    required_hashes = {
        "checks",
        "error_summary",
        "fields",
        "field_manifest",
    }

    if hashes:
        if set(hashes) != (
            required_hashes
        ):
            raise SchemaValidationError(
                "output_sha256 has "
                "the wrong file set"
            )

        normalized_hashes = (
            MappingProxyType(
                {
                    key: _sha256(
                        hashes[key],
                        (
                            "output_sha256."
                            f"{key}"
                        ),
                    )
                    for key in sorted(
                        hashes
                    )
                }
            )
        )

    elif allow_unwritten_outputs:
        normalized_hashes = (
            MappingProxyType({})
        )

    else:
        raise SchemaValidationError(
            "Final metadata requires "
            "output hashes"
        )

    error_summary = (
        normalize_error_summary(
            _required(
                result,
                "error_summary",
                "result",
            )
        )
    )

    failure_messages = tuple(
        str(item)
        for item in _sequence(
            _required(
                result,
                "failure_messages",
                "result",
            ),
            (
                "result."
                "failure_messages"
            ),
        )
        if str(item)
    )

    if (
        case_status == "PASS"
        and failure_messages
    ):
        raise SchemaValidationError(
            "A passing case cannot "
            "contain failures"
        )

    if (
        case_status == "FAIL"
        and not failure_messages
    ):
        raise SchemaValidationError(
            "A failed case requires "
            "a failure message"
        )

    solver_class = (
        _nonempty_string(
            _required(
                execution,
                "solver_class",
                "execution",
            ),
            (
                "execution."
                "solver_class"
            ),
        )
    )

    allowed_methods = tuple(
        str(item)
        for item in _sequence(
            _required(
                execution,
                "allowed_methods_called",
                "execution",
            ),
            (
                "execution."
                "allowed_methods_called"
            ),
        )
    )

    prohibited_methods = tuple(
        str(item)
        for item in _sequence(
            _required(
                execution,
                (
                    "prohibited_"
                    "methods_called"
                ),
                "execution",
            ),
            (
                "execution."
                "prohibited_methods_called"
            ),
        )
    )

    if prohibited_methods:
        raise SchemaValidationError(
            "No prohibited method "
            "may be recorded"
        )

    forcing_count = _nonnegative_int(
        _required(
            execution,
            "forcing_call_count",
            "execution",
        ),
        (
            "execution."
            "forcing_call_count"
        ),
    )

    if forcing_count != 0:
        raise SchemaValidationError(
            "forcing_call_count "
            "must equal zero"
        )

    mask_count = _nonnegative_int(
        _required(
            execution,
            (
                "mask_application_"
                "count"
            ),
            "execution",
        ),
        (
            "execution."
            "mask_application_count"
        ),
    )

    expected_masks = (
        0
        if track in {
            "O1",
            "O2",
        }
        else n_steps
    )

    if mask_count != expected_masks:
        raise SchemaValidationError(
            "mask_application_count "
            "is incorrect"
        )

    input_unchanged = _required(
        execution,
        "input_unchanged",
        "execution",
    )

    state_unchanged = _required(
        execution,
        "solver_state_unchanged",
        "execution",
    )

    if (
        not isinstance(
            input_unchanged,
            bool,
        )
        or not isinstance(
            state_unchanged,
            bool,
        )
    ):
        raise SchemaValidationError(
            "Mutation fields must "
            "be Boolean"
        )

    if (
        case_status == "PASS"
        and not (
            input_unchanged
            and state_unchanged
        )
    ):
        raise SchemaValidationError(
            "A passing case must "
            "preserve all state"
        )

    normalized = {
        "schema_id": (
            METADATA_SCHEMA_ID
        ),
        "repository": repository,
        "environment": environment,
        "benchmark": (
            MappingProxyType(
                {
                    "benchmark_id": (
                        benchmark_id
                    ),
                    "track": track,
                    **benchmark_strings,
                    (
                        "advection_method"
                    ): normalized_method,
                    (
                        "product_dealiasing"
                    ): False,
                }
            )
        ),
        "numerical": (
            MappingProxyType(
                {
                    "N": N,
                    "L": L,
                    "dx": dx,
                    "Re": Re,
                    "nu": nu,
                    "dt": dt,
                    "n_steps": n_steps,
                    "t_0": t_0,
                    (
                        "t_final_actual"
                    ): t_final_actual,
                    (
                        "t_final_requested"
                    ): t_final_requested,
                    (
                        "final_time_aligned"
                    ): True,
                    (
                        "constructor_steps"
                    ): 0,
                }
            )
        ),
        "execution": (
            MappingProxyType(
                {
                    (
                        "solver_class"
                    ): solver_class,
                    (
                        "allowed_methods_called"
                    ): allowed_methods,
                    (
                        "prohibited_methods_called"
                    ): prohibited_methods,
                    (
                        "forcing_call_count"
                    ): forcing_count,
                    (
                        "mask_application_count"
                    ): mask_count,
                    (
                        "input_unchanged"
                    ): input_unchanged,
                    (
                        "solver_state_unchanged"
                    ): state_unchanged,
                }
            )
        ),
        "result": (
            MappingProxyType(
                {
                    "case_id": case_id,
                    (
                        "case_status"
                    ): case_status,
                    (
                        "output_filenames"
                    ): CASE_OUTPUT_FILENAMES,
                    (
                        "output_sha256"
                    ): normalized_hashes,
                    (
                        "error_summary"
                    ): error_summary,
                    (
                        "failure_messages"
                    ): failure_messages,
                }
            )
        ),
    }

    json_safe(normalized)

    return MappingProxyType(
        normalized
    )


def _array_entry(
    name: str,
    value: object,
) -> tuple[
    np.ndarray,
    ArrayManifestEntry,
]:
    """Normalize one case array."""

    raw = np.asarray(value)

    if (
        raw.ndim != 2
        or raw.shape[0]
        != raw.shape[1]
    ):
        raise SchemaValidationError(
            f"Array {name!r} must "
            "be square and 2-D"
        )

    if not np.isrealobj(raw):
        raise SchemaValidationError(
            f"Array {name!r} "
            "must be real"
        )

    array = np.array(
        raw,
        dtype=np.float64,
        copy=True,
        order="C",
    )

    if not np.isfinite(
        array
    ).all():
        raise SchemaValidationError(
            f"Array {name!r} "
            "must be finite"
        )

    minimum = float(
        np.min(array)
    )

    maximum = float(
        np.max(array)
    )

    L2_rms = float(
        np.sqrt(
            np.mean(
                array * array,
                dtype=np.float64,
            )
        )
    )

    array.setflags(
        write=False
    )

    entry = ArrayManifestEntry(
        name=name,
        shape=tuple(
            int(item)
            for item in array.shape
        ),
        dtype=str(array.dtype),
        nbytes=int(array.nbytes),
        sha256=hash_array(array),
        finite=True,
        real_valued=True,
        writeable=bool(
            array.flags.writeable
        ),
        minimum=minimum,
        maximum=maximum,
        L2_rms=L2_rms,
    )

    return array, entry


def prepare_case_arrays(
    track: str,
    arrays: Mapping[
        str,
        object,
    ],
) -> tuple[
    Mapping[
        str,
        np.ndarray,
    ],
    Mapping[
        str,
        ArrayManifestEntry,
    ],
]:
    """
    Validate one track-specific array set
    and construct its manifest.
    """

    source = _mapping(
        arrays,
        "arrays",
    )

    if track in {
        "O1",
        "O2",
    }:
        required = set(
            OPERATOR_ARRAY_NAMES
        )

        allowed = required

    elif track == "L":
        required = set(
            EVOLUTION_ARRAY_NAMES
        )

        allowed = required

    elif track == "M":
        required = set(
            EVOLUTION_ARRAY_NAMES
        )

        optional = {
            name
            for name in source
            if any(
                name.startswith(
                    prefix
                )
                for prefix in (
                    TRACK_M_OPTIONAL_ARRAY_PREFIXES
                )
            )
        }

        allowed = (
            required
            | optional
        )

    else:
        raise SchemaValidationError(
            "Unknown track"
        )

    observed = set(source)

    missing = (
        required
        - observed
    )

    unexpected = (
        observed
        - allowed
    )

    if missing:
        raise SchemaValidationError(
            "Missing arrays: "
            + ", ".join(
                sorted(missing)
            )
        )

    if unexpected:
        raise SchemaValidationError(
            "Unexpected arrays: "
            + ", ".join(
                sorted(unexpected)
            )
        )

    prepared: dict[
        str,
        np.ndarray,
    ] = {}

    entries: dict[
        str,
        ArrayManifestEntry,
    ] = {}

    shape: (
        tuple[int, int]
        | None
    ) = None

    for name in sorted(
        observed
    ):
        array, entry = (
            _array_entry(
                name,
                source[name],
            )
        )

        if shape is None:
            shape = array.shape

        elif array.shape != shape:
            raise SchemaValidationError(
                "All case arrays must "
                "share one shape"
            )

        prepared[name] = array
        entries[name] = entry

    return (
        MappingProxyType(
            prepared
        ),
        MappingProxyType(
            entries
        ),
    )


def build_field_manifest(
    *,
    case_id: str,
    track: str,
    entries: Mapping[
        str,
        ArrayManifestEntry,
    ],
) -> Mapping[str, object]:
    """Build field-manifest content."""

    token = _safe_token(
        case_id,
        "case_id",
    )

    if track not in {
        "O1",
        "O2",
        "L",
        "M",
    }:
        raise SchemaValidationError(
            "Unknown track"
        )

    arrays = {
        name: json_safe(entry)
        for name, entry in sorted(
            entries.items()
        )
    }

    return MappingProxyType(
        {
            "schema_id": (
                FIELD_MANIFEST_SCHEMA_ID
            ),
            "case_id": token,
            "track": track,
            "archive_filename": (
                FIELDS_FILENAME
            ),
            "array_count": len(
                arrays
            ),
            "arrays": arrays,
        }
    )


def validate_checks(
    checks: object,
) -> Mapping[str, object]:
    """Validate one checks mapping."""

    safe = json_safe(
        _mapping(
            checks,
            "checks",
        )
    )

    if (
        not isinstance(
            safe,
            dict,
        )
        or not safe
    ):
        raise SchemaValidationError(
            "checks must be a "
            "nonempty mapping"
        )

    return MappingProxyType(
        safe
    )


def _atomic_bytes(
    path: Path,
    payload: bytes,
) -> None:
    """
    Write temporary bytes and atomically
    replace the destination.
    """

    destination = Path(path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        descriptor,
        temporary_name,
    ) = tempfile.mkstemp(
        dir=destination.parent,
        prefix=(
            f".{destination.name}."
        ),
        suffix=".tmp",
    )

    temporary = Path(
        temporary_name
    )

    try:
        with os.fdopen(
            descriptor,
            "wb",
        ) as handle:
            handle.write(
                payload
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary,
            destination,
        )

    except BaseException:
        temporary.unlink(
            missing_ok=True
        )

        raise


def atomic_write_json(
    path: Path,
    value: object,
) -> None:
    """Atomically write deterministic JSON."""

    _atomic_bytes(
        Path(path),
        canonical_json_bytes(
            value
        ),
    )


def atomic_write_error_summary_csv(
    path: Path,
    summary: Mapping[
        str,
        object,
    ],
) -> None:
    """Atomically write error_summary.csv."""

    normalized = (
        normalize_error_summary(
            summary
        )
    )

    buffer = StringIO(
        newline=""
    )

    writer = csv.DictWriter(
        buffer,
        fieldnames=list(
            ERROR_SUMMARY_COLUMNS
        ),
        lineterminator="\n",
    )

    writer.writeheader()

    writer.writerow(
        {
            key: (
                ""
                if normalized[key]
                is None
                else normalized[key]
            )
            for key in (
                ERROR_SUMMARY_COLUMNS
            )
        }
    )

    _atomic_bytes(
        Path(path),
        buffer.getvalue().encode(
            "utf-8"
        ),
    )


def atomic_write_npz(
    path: Path,
    arrays: Mapping[
        str,
        np.ndarray,
    ],
) -> None:
    """Atomically write a compressed NPZ."""

    destination = Path(path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        descriptor,
        temporary_name,
    ) = tempfile.mkstemp(
        dir=destination.parent,
        prefix=(
            f".{destination.name}."
        ),
        suffix=".tmp",
    )

    temporary = Path(
        temporary_name
    )

    try:
        with os.fdopen(
            descriptor,
            "wb",
        ) as handle:
            np.savez_compressed(
                handle,
                **{
                    name: np.asarray(
                        value
                    )
                    for name, value
                    in arrays.items()
                },
            )

            handle.flush()

            os.fsync(
                handle.fileno()
            )

        os.replace(
            temporary,
            destination,
        )

    except BaseException:
        temporary.unlink(
            missing_ok=True
        )

        raise


def _file_record(
    logical_name: str,
    path: Path,
) -> FileHashRecord:
    """Build one file identity record."""

    file_path = Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(
            file_path
        )

    return FileHashRecord(
        logical_name=logical_name,
        filename=file_path.name,
        sha256=sha256_file(
            file_path
        ),
        size_bytes=int(
            file_path.stat().st_size
        ),
    )


def _mutable_json_mapping(
    value: object,
) -> dict[str, object]:
    """Return one mutable JSON mapping."""

    safe = json_safe(value)

    if not isinstance(
        safe,
        dict,
    ):
        raise SchemaValidationError(
            "Expected a JSON mapping"
        )

    return safe


def _case_directory(
    output_root: Path,
    case_id: str,
) -> Path:
    """
    Resolve a case directory without
    permitting path escape.
    """

    root = Path(
        output_root
    ).resolve()

    candidate = (
        root
        / _safe_token(
            case_id,
            "case_id",
        )
    ).resolve()

    try:
        candidate.relative_to(
            root
        )

    except ValueError as exc:
        raise SchemaValidationError(
            "case_id escapes "
            "the output root"
        ) from exc

    return candidate


def write_case_bundle(
    *,
    output_root: Path,
    metadata: Mapping[
        str,
        object,
    ],
    checks: Mapping[
        str,
        object,
    ],
    error_summary: Mapping[
        str,
        object,
    ],
    arrays: Mapping[
        str,
        object,
    ],
) -> CaseWriteResult:
    """
    Atomically write one fail-closed
    Phase 13 case bundle.
    """

    normalized = (
        validate_case_metadata(
            metadata,
            allow_unwritten_outputs=(
                True
            ),
        )
    )

    benchmark = _mapping(
        normalized["benchmark"],
        "benchmark",
    )

    numerical = _mapping(
        normalized["numerical"],
        "numerical",
    )

    result = _mapping(
        normalized["result"],
        "result",
    )

    case_id = str(
        result["case_id"]
    )

    case_status = str(
        result["case_status"]
    )

    track = str(
        benchmark["track"]
    )

    (
        prepared_arrays,
        entries,
    ) = prepare_case_arrays(
        track,
        arrays,
    )

    expected_shape = (
        int(
            numerical["N"]
        ),
        int(
            numerical["N"]
        ),
    )

    for (
        name,
        array,
    ) in prepared_arrays.items():
        if array.shape != (
            expected_shape
        ):
            raise SchemaValidationError(
                f"Array {name!r} shape "
                "does not match metadata N"
            )

    normalized_checks = (
        validate_checks(
            checks
        )
    )

    normalized_error = (
        normalize_error_summary(
            error_summary
        )
    )

    if dict(
        normalized_error
    ) != dict(
        _mapping(
            result[
                "error_summary"
            ],
            "error_summary",
        )
    ):
        raise SchemaValidationError(
            "error_summary differs "
            "from metadata"
        )

    field_manifest = (
        build_field_manifest(
            case_id=case_id,
            track=track,
            entries=entries,
        )
    )

    case_directory = (
        _case_directory(
            Path(output_root),
            case_id,
        )
    )

    if case_directory.exists():
        if not case_directory.is_dir():
            raise FileExistsError(
                "Case path is not "
                "a directory: "
                f"{case_directory}"
            )

        if any(
            case_directory.iterdir()
        ):
            raise FileExistsError(
                "Case directory is "
                "not empty: "
                f"{case_directory}"
            )

    case_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = {
        key: (
            case_directory
            / filename
        )
        for key, filename in (
            CASE_OUTPUT_FILENAMES.items()
        )
    }

    incomplete = (
        _mutable_json_mapping(
            normalized
        )
    )

    incomplete_result = _mapping(
        incomplete["result"],
        "result",
    )

    incomplete["result"] = {
        **dict(
            incomplete_result
        ),
        "case_status": "INCOMPLETE",
        "output_sha256": {},
    }

    validate_case_metadata(
        incomplete,
        allow_unwritten_outputs=True,
    )

    atomic_write_json(
        paths["case_metadata"],
        incomplete,
    )

    atomic_write_json(
        paths["checks"],
        normalized_checks,
    )

    atomic_write_error_summary_csv(
        paths["error_summary"],
        normalized_error,
    )

    atomic_write_npz(
        paths["fields"],
        prepared_arrays,
    )

    atomic_write_json(
        paths["field_manifest"],
        field_manifest,
    )

    records = {
        key: _file_record(
            key,
            paths[key],
        )
        for key in (
            "checks",
            "error_summary",
            "fields",
            "field_manifest",
        )
    }

    final_metadata = (
        _mutable_json_mapping(
            normalized
        )
    )

    final_result = _mapping(
        final_metadata["result"],
        "result",
    )

    final_metadata["result"] = {
        **dict(final_result),
        "output_sha256": {
            key: record.sha256
            for key, record
            in records.items()
        },
    }

    completed = (
        validate_case_metadata(
            final_metadata,
            allow_unwritten_outputs=(
                False
            ),
        )
    )

    atomic_write_json(
        paths["case_metadata"],
        completed,
    )

    records = {
        "case_metadata": (
            _file_record(
                "case_metadata",
                paths[
                    "case_metadata"
                ],
            )
        ),
        **records,
    }

    return CaseWriteResult(
        case_id=case_id,
        case_directory=str(
            case_directory
        ),
        case_status=case_status,
        files=MappingProxyType(
            records
        ),
        array_manifest=entries,
    )


def build_run_manifest(
    *,
    run_id: str,
    run_status: str,
    created_utc: str,
    repository: Mapping[
        str,
        object,
    ],
    environment: Mapping[
        str,
        object,
    ],
    cases: Sequence[
        CaseWriteResult
    ],
) -> Mapping[str, object]:
    """Build deterministic run metadata."""

    token = _safe_token(
        run_id,
        "run_id",
    )

    status = (
        str(run_status)
        .strip()
        .upper()
    )

    if status not in RUN_STATUSES:
        raise SchemaValidationError(
            "Unknown run status"
        )

    repository_record = (
        _validate_repository(
            repository
        )
    )

    environment_data = (
        _validate_environment(
            environment
        )
    )

    if (
        created_utc
        != environment_data[
            "timestamp_utc"
        ]
    ):
        raise SchemaValidationError(
            "created_utc must match "
            "environment"
        )

    if not cases:
        raise SchemaValidationError(
            "A run manifest requires "
            "at least one case"
        )

    case_ids: set[str] = set()

    case_records: list[
        dict[str, object]
    ] = []

    for case in cases:
        if not isinstance(
            case,
            CaseWriteResult,
        ):
            raise SchemaValidationError(
                "cases must contain "
                "CaseWriteResult"
            )

        if case.case_id in case_ids:
            raise SchemaValidationError(
                "Duplicate case identifier"
            )

        case_ids.add(
            case.case_id
        )

        case_records.append(
            {
                "case_id": case.case_id,
                (
                    "case_directory"
                ): case.case_directory,
                (
                    "case_status"
                ): case.case_status,
                "files": {
                    name: {
                        (
                            "filename"
                        ): record.filename,
                        (
                            "sha256"
                        ): record.sha256,
                        (
                            "size_bytes"
                        ): record.size_bytes,
                    }
                    for name, record
                    in sorted(
                        case.files.items()
                    )
                },
            }
        )

    if (
        status == "PASS"
        and any(
            case.case_status
            != "PASS"
            for case in cases
        )
    ):
        raise SchemaValidationError(
            "A passing run may "
            "contain only passing cases"
        )

    if (
        status == "FAIL"
        and all(
            case.case_status
            == "PASS"
            for case in cases
        )
    ):
        raise SchemaValidationError(
            "A failed run requires "
            "a failed case"
        )

    return MappingProxyType(
        {
            "schema_id": (
                RUN_MANIFEST_SCHEMA_ID
            ),
            "output_schema_id": (
                OUTPUT_SCHEMA_ID
            ),
            "run_id": token,
            "run_status": status,
            "created_utc": (
                created_utc
            ),
            "repository": (
                repository_record
            ),
            "environment": (
                environment_data
            ),
            "case_count": len(
                case_records
            ),
            "cases": tuple(
                case_records
            ),
        }
    )


def write_run_manifest(
    *,
    run_directory: Path,
    run_id: str,
    run_status: str,
    created_utc: str,
    repository: Mapping[
        str,
        object,
    ],
    environment: Mapping[
        str,
        object,
    ],
    cases: Sequence[
        CaseWriteResult
    ],
) -> RunWriteResult:
    """Atomically write run_manifest.json."""

    token = _safe_token(
        run_id,
        "run_id",
    )

    directory = Path(
        run_directory
    )

    if directory.name != token:
        raise SchemaValidationError(
            "run_directory name must "
            "equal run_id"
        )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        directory
        / RUN_MANIFEST_FILENAME
    )

    if path.exists():
        raise FileExistsError(
            path
        )

    manifest = build_run_manifest(
        run_id=token,
        run_status=run_status,
        created_utc=created_utc,
        repository=repository,
        environment=environment,
        cases=cases,
    )

    atomic_write_json(
        path,
        manifest,
    )

    return RunWriteResult(
        run_id=token,
        run_directory=str(
            directory.resolve()
        ),
        run_status=(
            str(run_status)
            .strip()
            .upper()
        ),
        manifest=_file_record(
            "run_manifest",
            path,
        ),
        case_ids=tuple(
            case.case_id
            for case in cases
        ),
    )


def implementation_contract(
) -> Mapping[str, object]:
    """Return static schema metadata."""

    return MappingProxyType(
        {
            "metadata_schema_id": (
                METADATA_SCHEMA_ID
            ),
            "output_schema_id": (
                OUTPUT_SCHEMA_ID
            ),
            (
                "field_manifest_schema_id"
            ): FIELD_MANIFEST_SCHEMA_ID,
            (
                "run_manifest_schema_id"
            ): RUN_MANIFEST_SCHEMA_ID,
            "output_root": str(
                OUTPUT_ROOT
            ),
            (
                "case_output_filenames"
            ): CASE_OUTPUT_FILENAMES,
            (
                "atomic_json_writing"
            ): True,
            (
                "atomic_csv_writing"
            ): True,
            (
                "atomic_npz_writing"
            ): True,
            (
                "initial_case_status"
            ): "INCOMPLETE",
            (
                "result_writing_implemented"
            ): True,
            (
                "top_level_writing"
            ): False,
            (
                "plotting_implemented"
            ): False,
            (
                "observed_order_implemented"
            ): False,
            (
                "rate_fitting_implemented"
            ): False,
            "pilot_authorized": False,
            "convergence_claim": False,
            (
                "physical_validation_claim"
            ): False,
        }
    )


__all__ = (
    "SchemaValidationError",
    "FileHashRecord",
    "ArrayManifestEntry",
    "CaseWriteResult",
    "RunWriteResult",
    "METADATA_SCHEMA_ID",
    "OUTPUT_SCHEMA_ID",
    "FIELD_MANIFEST_SCHEMA_ID",
    "RUN_MANIFEST_SCHEMA_ID",
    "OUTPUT_ROOT",
    "RUN_MANIFEST_FILENAME",
    "CASE_METADATA_FILENAME",
    "CHECKS_FILENAME",
    "ERROR_SUMMARY_FILENAME",
    "FIELDS_FILENAME",
    "FIELD_MANIFEST_FILENAME",
    "CASE_OUTPUT_FILENAMES",
    "CASE_STATUSES",
    "RUN_STATUSES",
    "BENCHMARK_TRACKS",
    "SUPPORTED_ADVECTION_METHODS",
    "PROTECTED_SOLVER_PATHS",
    "OPERATOR_ARRAY_NAMES",
    "EVOLUTION_ARRAY_NAMES",
    "ERROR_SUMMARY_COLUMNS",
    "utc_timestamp",
    "environment_record",
    "json_safe",
    "canonical_json_bytes",
    "sha256_bytes",
    "sha256_file",
    "hash_array",
    "deterministic_case_id",
    "normalize_error_summary",
    "validate_case_metadata",
    "prepare_case_arrays",
    "build_field_manifest",
    "validate_checks",
    "atomic_write_json",
    "atomic_write_error_summary_csv",
    "atomic_write_npz",
    "write_case_bundle",
    "build_run_manifest",
    "write_run_manifest",
    "implementation_contract",
)