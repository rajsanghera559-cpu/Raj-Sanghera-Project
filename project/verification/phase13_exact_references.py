"""
Independent analytic references for Phase 13 verification.

Phase 13E.1 boundary:
- standard library and NumPy only;
- no project solver imports;
- no solver construction or solver calls;
- no file output;
- no pilot, refinement sequence, or convergence claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

import numpy as np


REFERENCE_VERSION = "PHASE13_REFERENCE_V1"

O1_BENCHMARK_ID = "O1_BANDLIMITED_TWO_MODE_V1"
O2_BENCHMARK_ID = "O2_ANALYTIC_BROAD_SPECTRUM_V1"
L_BENCHMARK_ID = "L_EQUAL_EIGENVALUE_DECAY_V1"
M_BENCHMARK_ID = "M_TWO_RATE_NONLINEAR_MMS_V1"

NO_COMPATIBILITY_PROJECTION = "NONE"
O2_COMPATIBILITY_POLICY = "O2_DISCRETE_MEAN_SUBTRACTION_V1"

OPERATOR_SOURCE_POLICY = "OPERATOR_ONLY_NO_SOURCE_V1"
L_SOURCE_POLICY = "L_ZERO_SOURCE_V1"
M_SOURCE_POLICY = "M_ANALYTIC_SOURCE_REPLACES_BASELINE_V1"

NO_POST_STEP_MASK = "NO_POST_STEP_MASK_OPERATOR_ONLY_V1"
POST_STEP_MASK_POLICY = "POST_STEP_STRICT_COORDINATE_TWO_THIRDS_ONCE_V1"


@dataclass(frozen=True, slots=True)
class BenchmarkDefinition:
    """Immutable benchmark-registry entry."""

    benchmark_id: str
    track: str
    reference_version: str
    supports_operator_evaluation: bool
    supports_time_evolution: bool
    requires_advection_method: bool
    source_policy: str
    compatibility_policy: str
    post_step_mask_policy: str


@dataclass(frozen=True, slots=True)
class NativeGrid:
    """Independent periodic native grid."""

    N: int
    L: float
    dx: float
    x: np.ndarray
    X: np.ndarray
    Y: np.ndarray


@dataclass(frozen=True, slots=True)
class ReferenceFields:
    """Immutable container for one exact benchmark evaluation."""

    benchmark_id: str
    track: str
    reference_version: str
    time: float
    nu: float
    psi: np.ndarray
    omega_raw: np.ndarray
    omega_input: np.ndarray
    u: np.ndarray
    v: np.ndarray
    adv: np.ndarray
    laplacian_omega: np.ndarray | None
    partial_t_omega: np.ndarray | None
    source: np.ndarray | None
    discrete_mean_removed: float
    compatibility_policy: str
    fourier_support: Mapping[str, tuple[tuple[int, int], ...]]
    checks: Mapping[str, object]


_BENCHMARK_REGISTRY: Mapping[str, BenchmarkDefinition] = MappingProxyType(
    {
        O1_BENCHMARK_ID: BenchmarkDefinition(
            benchmark_id=O1_BENCHMARK_ID,
            track="O1",
            reference_version=REFERENCE_VERSION,
            supports_operator_evaluation=True,
            supports_time_evolution=False,
            requires_advection_method=True,
            source_policy=OPERATOR_SOURCE_POLICY,
            compatibility_policy=NO_COMPATIBILITY_PROJECTION,
            post_step_mask_policy=NO_POST_STEP_MASK,
        ),
        O2_BENCHMARK_ID: BenchmarkDefinition(
            benchmark_id=O2_BENCHMARK_ID,
            track="O2",
            reference_version=REFERENCE_VERSION,
            supports_operator_evaluation=True,
            supports_time_evolution=False,
            requires_advection_method=True,
            source_policy=OPERATOR_SOURCE_POLICY,
            compatibility_policy=O2_COMPATIBILITY_POLICY,
            post_step_mask_policy=NO_POST_STEP_MASK,
        ),
        L_BENCHMARK_ID: BenchmarkDefinition(
            benchmark_id=L_BENCHMARK_ID,
            track="L",
            reference_version=REFERENCE_VERSION,
            supports_operator_evaluation=False,
            supports_time_evolution=True,
            requires_advection_method=False,
            source_policy=L_SOURCE_POLICY,
            compatibility_policy=NO_COMPATIBILITY_PROJECTION,
            post_step_mask_policy=POST_STEP_MASK_POLICY,
        ),
        M_BENCHMARK_ID: BenchmarkDefinition(
            benchmark_id=M_BENCHMARK_ID,
            track="M",
            reference_version=REFERENCE_VERSION,
            supports_operator_evaluation=False,
            supports_time_evolution=True,
            requires_advection_method=True,
            source_policy=M_SOURCE_POLICY,
            compatibility_policy=NO_COMPATIBILITY_PROJECTION,
            post_step_mask_policy=POST_STEP_MASK_POLICY,
        ),
    }
)


_SUPPORT: Mapping[
    str,
    Mapping[str, tuple[tuple[int, int], ...]],
] = MappingProxyType(
    {
        O1_BENCHMARK_ID: MappingProxyType(
            {
                "omega": (
                    (1, 1),
                    (2, 1),
                ),
                "adv": (
                    (1, 0),
                    (1, 2),
                    (3, 0),
                    (3, 2),
                ),
            }
        ),
        O2_BENCHMARK_ID: MappingProxyType(
            {
                "omega": (),
                "adv": (),
            }
        ),
        L_BENCHMARK_ID: MappingProxyType(
            {
                "omega": (
                    (0, 3),
                    (3, 0),
                ),
                "adv": (),
                "source": (),
            }
        ),
        M_BENCHMARK_ID: MappingProxyType(
            {
                "omega": (
                    (1, 1),
                    (2, 1),
                ),
                "adv": (
                    (1, 0),
                    (1, 2),
                    (3, 0),
                    (3, 2),
                ),
                "source": (
                    (1, 0),
                    (1, 1),
                    (1, 2),
                    (2, 1),
                    (3, 0),
                    (3, 2),
                ),
            }
        ),
    }
)


def benchmark_registry() -> Mapping[str, BenchmarkDefinition]:
    """Return the immutable version-1 benchmark registry."""

    return _BENCHMARK_REGISTRY


def get_benchmark_definition(
    benchmark_id: str,
) -> BenchmarkDefinition:
    """Return one exact, case-sensitive registry entry."""

    if not isinstance(benchmark_id, str):
        raise TypeError("benchmark_id must be a string")

    try:
        return _BENCHMARK_REGISTRY[benchmark_id]
    except KeyError as exc:
        allowed = ", ".join(_BENCHMARK_REGISTRY)

        raise ValueError(
            f"Unknown benchmark_id={benchmark_id!r}. "
            f"Allowed values: {allowed}"
        ) from exc


def _validate_even_grid_size(N: int) -> int:
    """Validate an independent native-grid size."""

    if isinstance(N, bool) or not isinstance(
        N,
        (int, np.integer),
    ):
        raise TypeError("N must be an integer")

    value = int(N)

    if value < 2:
        raise ValueError("N must be at least 2")

    if value % 2:
        raise ValueError("N must be even")

    return value


def _freeze_array(
    value: object,
    *,
    shape: tuple[int, ...],
    name: str,
) -> np.ndarray:
    """Copy a finite real array and mark it read-only."""

    raw = np.asarray(value)

    if raw.shape != shape:
        raise ValueError(
            f"{name} has shape {raw.shape}; expected {shape}"
        )

    if not np.isrealobj(raw):
        raise ValueError(f"{name} must be real-valued")

    array = np.array(
        raw,
        dtype=np.float64,
        copy=True,
    )

    if not np.isfinite(array).all():
        raise ValueError(f"{name} must be finite")

    array.setflags(write=False)

    return array


def _freeze_optional(
    value: object | None,
    *,
    shape: tuple[int, int],
    name: str,
) -> np.ndarray | None:
    """Freeze an optional exact field."""

    if value is None:
        return None

    return _freeze_array(
        value,
        shape=shape,
        name=name,
    )


def _freeze_support(
    support: Mapping[str, tuple[tuple[int, int], ...]],
) -> Mapping[str, tuple[tuple[int, int], ...]]:
    """Return immutable normalized absolute Fourier support."""

    normalized = {
        key: tuple(
            sorted(
                {
                    (
                        abs(int(kx)),
                        abs(int(ky)),
                    )
                    for kx, ky in modes
                }
            )
        )
        for key, modes in support.items()
    }

    return MappingProxyType(normalized)


def construct_native_grid(N: int) -> NativeGrid:
    """
    Construct the independent periodic native grid.

    The repeated endpoint is excluded. NumPy's ``xy`` convention is used,
    so axis 1 is x and axis 0 is y.
    """

    size = _validate_even_grid_size(N)

    L = float(2.0 * np.pi)
    dx = L / size

    x = (
        np.arange(
            size,
            dtype=np.float64,
        )
        * dx
    )

    X, Y = np.meshgrid(
        x,
        x,
        indexing="xy",
    )

    return NativeGrid(
        N=size,
        L=L,
        dx=dx,
        x=_freeze_array(
            x,
            shape=(size,),
            name="x",
        ),
        X=_freeze_array(
            X,
            shape=(size, size),
            name="X",
        ),
        Y=_freeze_array(
            Y,
            shape=(size, size),
            name="Y",
        ),
    )


def _validate_coordinates(
    X: object,
    Y: object,
) -> tuple[
    np.ndarray,
    np.ndarray,
    tuple[int, int],
]:
    """Validate independent square coordinate arrays."""

    x_array = np.asarray(X)
    y_array = np.asarray(Y)

    if x_array.ndim != 2 or y_array.ndim != 2:
        raise ValueError(
            "X and Y must both be two-dimensional"
        )

    if x_array.shape != y_array.shape:
        raise ValueError(
            "X and Y must have the same shape"
        )

    if x_array.shape[0] != x_array.shape[1]:
        raise ValueError(
            "X and Y must describe a square grid"
        )

    if x_array.shape[0] % 2:
        raise ValueError(
            "The inferred grid size must be even"
        )

    if (
        not np.isrealobj(x_array)
        or not np.isrealobj(y_array)
    ):
        raise ValueError(
            "X and Y must be real-valued"
        )

    if (
        not np.isfinite(x_array).all()
        or not np.isfinite(y_array).all()
    ):
        raise ValueError(
            "X and Y must be finite"
        )

    return (
        np.asarray(
            x_array,
            dtype=np.float64,
        ),
        np.asarray(
            y_array,
            dtype=np.float64,
        ),
        x_array.shape,
    )


def _validate_scalars(
    t: object,
    nu: object,
) -> tuple[float, float]:
    """Validate exact-reference scalar parameters."""

    if isinstance(t, bool) or not np.isscalar(t):
        raise TypeError("t must be a real scalar")

    if isinstance(nu, bool) or not np.isscalar(nu):
        raise TypeError("nu must be a real scalar")

    time_value = float(t)
    viscosity = float(nu)

    if not np.isfinite(time_value):
        raise ValueError("t must be finite")

    if (
        not np.isfinite(viscosity)
        or viscosity <= 0.0
    ):
        raise ValueError(
            "nu must be finite and strictly positive"
        )

    return time_value, viscosity


def _common_spatial(
    X: np.ndarray,
    Y: np.ndarray,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    """Return the shared f, g, and F_O1 analytic fields."""

    f = np.sin(X) * np.sin(Y)

    g = (
        np.cos(2.0 * X)
        * np.cos(Y)
    )

    F_o1 = (
        np.cos(X)
        + 3.0
        * np.cos(X)
        * np.cos(2.0 * Y)
        - 3.0
        * np.cos(3.0 * X)
        - np.cos(3.0 * X)
        * np.cos(2.0 * Y)
    )

    return f, g, F_o1


def _o1_fields(
    X: np.ndarray,
    Y: np.ndarray,
) -> dict[str, object]:
    """Evaluate the direct analytic O1 fields."""

    f, g, F_o1 = _common_spatial(X, Y)

    omega = (
        -2.0 * f
        - 1.25 * g
    )

    return {
        "psi": f + 0.25 * g,
        "omega_raw": omega,
        "omega_input": np.array(
            omega,
            copy=True,
        ),
        "u": (
            np.sin(X) * np.cos(Y)
            - 0.25
            * np.cos(2.0 * X)
            * np.sin(Y)
        ),
        "v": (
            -np.cos(X) * np.sin(Y)
            + 0.5
            * np.sin(2.0 * X)
            * np.cos(Y)
        ),
        "adv": (
            (3.0 / 16.0)
            * F_o1
        ),
        "laplacian_omega": None,
        "partial_t_omega": None,
        "source": None,
        "discrete_mean_removed": 0.0,
        "compatibility_policy": (
            NO_COMPATIBILITY_PROJECTION
        ),
        "checks": {
            "continuous_zero_mean_expected": True,
            "nonlinear_term_expected_nonzero": True,
            "operator_only": True,
        },
    }


def _o2_fields(
    X: np.ndarray,
    Y: np.ndarray,
) -> dict[str, object]:
    """Evaluate analytic O2 and apply its frozen mean rule."""

    a = 0.5
    b = 1.0 / 3.0

    q = (
        a * np.cos(X)
        + b * np.cos(Y)
    )

    exp_q = np.exp(q)

    gauge_constant = float(
        np.i0(a)
        * np.i0(b)
    )

    H = (
        a * a * np.sin(X) ** 2
        - a * np.cos(X)
        + b * b * np.sin(Y) ** 2
        - b * np.cos(Y)
    )

    omega_raw = exp_q * H

    removed_mean = float(
        np.mean(
            omega_raw,
            dtype=np.float64,
        )
    )

    omega_input = (
        omega_raw
        - removed_mean
    )

    return {
        "psi": exp_q - gauge_constant,
        "omega_raw": omega_raw,
        "omega_input": omega_input,
        "u": (
            -b
            * np.sin(Y)
            * exp_q
        ),
        "v": (
            a
            * np.sin(X)
            * exp_q
        ),
        "adv": (
            -2.0
            * a
            * b
            * (
                a * np.cos(X)
                - b * np.cos(Y)
            )
            * np.exp(2.0 * q)
            * np.sin(X)
            * np.sin(Y)
        ),
        "laplacian_omega": None,
        "partial_t_omega": None,
        "source": None,
        "discrete_mean_removed": removed_mean,
        "compatibility_policy": (
            O2_COMPATIBILITY_POLICY
        ),
        "checks": {
            "continuous_zero_mean_expected": True,
            "nonlinear_term_expected_nonzero": True,
            "analytic_non_band_limited": True,
            "operator_only": True,
            "gauge_constant": gauge_constant,
        },
    }


def _l_fields(
    X: np.ndarray,
    Y: np.ndarray,
    *,
    t: float,
    nu: float,
) -> dict[str, object]:
    """Evaluate the exact Track L fields."""

    phi = (
        np.sin(3.0 * X)
        + np.cos(3.0 * Y)
    )

    decay = np.exp(
        -9.0 * nu * t
    )

    omega = decay * phi

    return {
        "psi": (
            -(1.0 / 9.0)
            * omega
        ),
        "omega_raw": omega,
        "omega_input": np.array(
            omega,
            copy=True,
        ),
        "u": (
            (1.0 / 3.0)
            * decay
            * np.sin(3.0 * Y)
        ),
        "v": (
            (1.0 / 3.0)
            * decay
            * np.cos(3.0 * X)
        ),
        "adv": np.zeros(
            X.shape,
            dtype=np.float64,
        ),
        "laplacian_omega": (
            -9.0
            * omega
        ),
        "partial_t_omega": (
            -9.0
            * nu
            * omega
        ),
        "source": np.zeros(
            X.shape,
            dtype=np.float64,
        ),
        "discrete_mean_removed": 0.0,
        "compatibility_policy": (
            NO_COMPATIBILITY_PROJECTION
        ),
        "checks": {
            "continuous_zero_mean_expected": True,
            "nonlinear_term_exactly_zero": True,
            "source_exactly_zero": True,
            "laplacian_eigenvalue": -9,
        },
    }


def _m_fields(
    X: np.ndarray,
    Y: np.ndarray,
    *,
    t: float,
    nu: float,
) -> dict[str, object]:
    """Evaluate the direct analytic Track M fields."""

    f, g, F_o1 = _common_spatial(X, Y)

    A = np.exp(-t)

    B = (
        0.25
        * np.exp(-2.0 * t)
    )

    omega = (
        -2.0 * A * f
        - 5.0 * B * g
    )

    return {
        "psi": (
            A * f
            + B * g
        ),
        "omega_raw": omega,
        "omega_input": np.array(
            omega,
            copy=True,
        ),
        "u": (
            A
            * np.sin(X)
            * np.cos(Y)
            - B
            * np.cos(2.0 * X)
            * np.sin(Y)
        ),
        "v": (
            -A
            * np.cos(X)
            * np.sin(Y)
            + 2.0
            * B
            * np.sin(2.0 * X)
            * np.cos(Y)
        ),
        "adv": (
            (3.0 / 4.0)
            * A
            * B
            * F_o1
        ),
        "laplacian_omega": (
            4.0 * A * f
            + 25.0 * B * g
        ),
        "partial_t_omega": (
            2.0 * A * f
            + 10.0 * B * g
        ),
        "source": (
            (2.0 - 4.0 * nu)
            * A
            * f
            + (10.0 - 25.0 * nu)
            * B
            * g
            + (3.0 / 4.0)
            * A
            * B
            * F_o1
        ),
        "discrete_mean_removed": 0.0,
        "compatibility_policy": (
            NO_COMPATIBILITY_PROJECTION
        ),
        "checks": {
            "continuous_zero_mean_expected": True,
            "nonlinear_term_expected_nonzero": True,
            "manufactured_source_present": True,
            "source_replaces_baseline": True,
        },
    }


def _assemble_reference(
    definition: BenchmarkDefinition,
    *,
    t: float,
    nu: float,
    shape: tuple[int, int],
    values: Mapping[str, object],
) -> ReferenceFields:
    """Freeze and validate one complete reference result."""

    arrays = {
        "psi": _freeze_array(
            values["psi"],
            shape=shape,
            name="psi",
        ),
        "omega_raw": _freeze_array(
            values["omega_raw"],
            shape=shape,
            name="omega_raw",
        ),
        "omega_input": _freeze_array(
            values["omega_input"],
            shape=shape,
            name="omega_input",
        ),
        "u": _freeze_array(
            values["u"],
            shape=shape,
            name="u",
        ),
        "v": _freeze_array(
            values["v"],
            shape=shape,
            name="v",
        ),
        "adv": _freeze_array(
            values["adv"],
            shape=shape,
            name="adv",
        ),
    }

    laplacian_omega = _freeze_optional(
        values["laplacian_omega"],
        shape=shape,
        name="laplacian_omega",
    )

    partial_t_omega = _freeze_optional(
        values["partial_t_omega"],
        shape=shape,
        name="partial_t_omega",
    )

    source = _freeze_optional(
        values["source"],
        shape=shape,
        name="source",
    )

    removed_mean = float(
        values["discrete_mean_removed"]
    )

    if not np.isfinite(removed_mean):
        raise ValueError(
            "discrete_mean_removed must be finite"
        )

    policy = str(
        values["compatibility_policy"]
    )

    if policy != definition.compatibility_policy:
        raise ValueError(
            "Compatibility policy does not match the registry"
        )

    all_arrays = list(
        arrays.values()
    )

    all_arrays.extend(
        item
        for item in (
            laplacian_omega,
            partial_t_omega,
            source,
        )
        if item is not None
    )

    checks = dict(
        values["checks"]
    )

    checks.update(
        {
            "shape": shape,
            "all_arrays_real": all(
                np.isrealobj(item)
                for item in all_arrays
            ),
            "all_arrays_finite": all(
                np.isfinite(item).all()
                for item in all_arrays
            ),
            "all_arrays_read_only": all(
                not item.flags.writeable
                for item in all_arrays
            ),
            "omega_raw_discrete_mean": float(
                np.mean(
                    arrays["omega_raw"],
                    dtype=np.float64,
                )
            ),
            "omega_input_discrete_mean": float(
                np.mean(
                    arrays["omega_input"],
                    dtype=np.float64,
                )
            ),
        }
    )

    return ReferenceFields(
        benchmark_id=definition.benchmark_id,
        track=definition.track,
        reference_version=definition.reference_version,
        time=t,
        nu=nu,
        psi=arrays["psi"],
        omega_raw=arrays["omega_raw"],
        omega_input=arrays["omega_input"],
        u=arrays["u"],
        v=arrays["v"],
        adv=arrays["adv"],
        laplacian_omega=laplacian_omega,
        partial_t_omega=partial_t_omega,
        source=source,
        discrete_mean_removed=removed_mean,
        compatibility_policy=policy,
        fourier_support=_freeze_support(
            _SUPPORT[definition.benchmark_id]
        ),
        checks=MappingProxyType(checks),
    )


def evaluate_reference(
    benchmark_id: str,
    X: object,
    Y: object,
    t: object,
    nu: object,
) -> ReferenceFields:
    """
    Evaluate direct analytic fields without numerical derivatives or solver code.
    """

    definition = get_benchmark_definition(
        benchmark_id
    )

    x_array, y_array, shape = (
        _validate_coordinates(
            X,
            Y,
        )
    )

    time_value, viscosity = (
        _validate_scalars(
            t,
            nu,
        )
    )

    if benchmark_id == O1_BENCHMARK_ID:
        values = _o1_fields(
            x_array,
            y_array,
        )
    elif benchmark_id == O2_BENCHMARK_ID:
        values = _o2_fields(
            x_array,
            y_array,
        )
    elif benchmark_id == L_BENCHMARK_ID:
        values = _l_fields(
            x_array,
            y_array,
            t=time_value,
            nu=viscosity,
        )
    elif benchmark_id == M_BENCHMARK_ID:
        values = _m_fields(
            x_array,
            y_array,
            t=time_value,
            nu=viscosity,
        )
    else:
        raise RuntimeError(
            "Validated benchmark was not dispatched"
        )

    return _assemble_reference(
        definition,
        t=time_value,
        nu=viscosity,
        shape=shape,
        values=values,
    )


def validate_reference_fields(
    reference: ReferenceFields,
) -> Mapping[str, object]:
    """Validate shape, finiteness, immutability, and track contracts."""

    if not isinstance(
        reference,
        ReferenceFields,
    ):
        raise TypeError(
            "reference must be a ReferenceFields instance"
        )

    definition = get_benchmark_definition(
        reference.benchmark_id
    )

    if reference.track != definition.track:
        raise ValueError(
            "Reference track does not match registry"
        )

    if (
        reference.reference_version
        != definition.reference_version
    ):
        raise ValueError(
            "Reference version does not match registry"
        )

    if (
        reference.compatibility_policy
        != definition.compatibility_policy
    ):
        raise ValueError(
            "Compatibility policy does not match registry"
        )

    arrays: list[
        tuple[str, np.ndarray]
    ] = [
        ("psi", reference.psi),
        ("omega_raw", reference.omega_raw),
        ("omega_input", reference.omega_input),
        ("u", reference.u),
        ("v", reference.v),
        ("adv", reference.adv),
    ]

    for name, value in (
        (
            "laplacian_omega",
            reference.laplacian_omega,
        ),
        (
            "partial_t_omega",
            reference.partial_t_omega,
        ),
        (
            "source",
            reference.source,
        ),
    ):
        if value is not None:
            arrays.append(
                (name, value)
            )

    shape = reference.psi.shape

    for name, array in arrays:
        if array.shape != shape:
            raise ValueError(
                f"{name} has an inconsistent shape"
            )

        if not np.isrealobj(array):
            raise ValueError(
                f"{name} is not real-valued"
            )

        if not np.isfinite(array).all():
            raise ValueError(
                f"{name} is not finite"
            )

        if array.flags.writeable:
            raise ValueError(
                f"{name} is not read-only"
            )

    for index, (
        left_name,
        left_array,
    ) in enumerate(arrays):
        for (
            right_name,
            right_array,
        ) in arrays[index + 1 :]:
            if np.shares_memory(
                left_array,
                right_array,
            ):
                raise ValueError(
                    f"{left_name} and "
                    f"{right_name} share memory"
                )

    if reference.track in (
        "O1",
        "O2",
    ):
        if any(
            value is not None
            for value in (
                reference.laplacian_omega,
                reference.partial_t_omega,
                reference.source,
            )
        ):
            raise ValueError(
                "Operator-only reference "
                "contains evolution fields"
            )

    if reference.track == "L":
        if any(
            value is None
            for value in (
                reference.laplacian_omega,
                reference.partial_t_omega,
                reference.source,
            )
        ):
            raise ValueError(
                "Track L lacks required evolution fields"
            )

        if np.count_nonzero(
            reference.adv
        ):
            raise ValueError(
                "Track L advection is not exactly zero"
            )

        if np.count_nonzero(
            reference.source
        ):
            raise ValueError(
                "Track L source is not exactly zero"
            )

    if reference.track == "M":
        if any(
            value is None
            for value in (
                reference.laplacian_omega,
                reference.partial_t_omega,
                reference.source,
            )
        ):
            raise ValueError(
                "Track M lacks required evolution fields"
            )

    if reference.track == "O2":
        if (
            reference.compatibility_policy
            != O2_COMPATIBILITY_POLICY
        ):
            raise ValueError(
                "Track O2 compatibility policy is incorrect"
            )

    return MappingProxyType(
        {
            "benchmark_id": reference.benchmark_id,
            "track": reference.track,
            "shape": shape,
            "array_count": len(arrays),
            "all_arrays_read_only": True,
            "all_arrays_independent": True,
            "registry_match": True,
            "compatibility_policy_match": True,
        }
    )


__all__ = (
    "BenchmarkDefinition",
    "NativeGrid",
    "ReferenceFields",
    "REFERENCE_VERSION",
    "O1_BENCHMARK_ID",
    "O2_BENCHMARK_ID",
    "L_BENCHMARK_ID",
    "M_BENCHMARK_ID",
    "NO_COMPATIBILITY_PROJECTION",
    "O2_COMPATIBILITY_POLICY",
    "OPERATOR_SOURCE_POLICY",
    "L_SOURCE_POLICY",
    "M_SOURCE_POLICY",
    "NO_POST_STEP_MASK",
    "POST_STEP_MASK_POLICY",
    "benchmark_registry",
    "get_benchmark_definition",
    "construct_native_grid",
    "evaluate_reference",
    "validate_reference_fields",
)