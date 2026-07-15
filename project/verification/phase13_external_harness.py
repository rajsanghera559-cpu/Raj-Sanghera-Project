"""
External in-memory verification harness for Phase 13.

Phase 13E.2 implementation boundary:
- no top-level project solver import;
- no top-level numerical execution;
- no result-file writing;
- no production run-loop call;
- no Phase 13F pilot authorization;
- no convergence or physical-validation claim.

The functions in this module implement the Phase 13D interfaces. They remain
dormant until a later phase explicitly imports and calls them.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol
import numpy as np

HARNESS_VERSION = 'PHASE13_EXTERNAL_HARNESS_V1'
SUPPORTED_ADVECTION_METHODS = ('fd_centered', 'pseudo_spectral', 'arakawa')
TRACK_L_CONSTRUCTOR_METHOD = 'fd_centered'

O1_BENCHMARK_ID = 'O1_BANDLIMITED_TWO_MODE_V1'
O2_BENCHMARK_ID = 'O2_ANALYTIC_BROAD_SPECTRUM_V1'
L_BENCHMARK_ID = 'L_EQUAL_EIGENVALUE_DECAY_V1'
M_BENCHMARK_ID = 'M_TWO_RATE_NONLINEAR_MMS_V1'

OPERATOR_TRACKS = ('O1', 'O2')
EVOLUTION_TRACKS = ('L', 'M')

O2_COMPATIBILITY_POLICY = 'O2_DISCRETE_MEAN_SUBTRACTION_V1'
M_SOURCE_POLICY = 'M_ANALYTIC_SOURCE_REPLACES_BASELINE_V1'
L_SOURCE_POLICY = 'L_ZERO_SOURCE_V1'

NO_POST_STEP_MASK = 'NO_POST_STEP_MASK_OPERATOR_ONLY_V1'
POST_STEP_MASK_POLICY = 'POST_STEP_STRICT_COORDINATE_TWO_THIRDS_ONCE_V1'

PRODUCT_DEALIASING_ENABLED = False
CONSTRUCTOR_STEPS = 0

PROHIBITED_SOLVER_INTERFACES = (
    'forcing',
    'compute_rhs_selectable',
    'step_once_selectable',
    'run_selectable_diagnostic',
    'run',
)


class SolverProtocol(Protocol):
    """Structural interface required from the selectable solver."""

    N: int
    L: float
    dx: float
    nu: float
    dt: float
    steps: int
    x: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    kx: np.ndarray
    ky: np.ndarray
    deal: np.ndarray
    w: np.ndarray
    advection_method: str

    def compute_advection(self, w: np.ndarray) -> np.ndarray:
        """Return project-convention nonlinear advection."""
        ...

    def laplacian_spectral(self, w: np.ndarray) -> np.ndarray:
        """Return viscosity-weighted spectral diffusion."""
        ...


@dataclass(frozen=True, slots=True)
class VerificationConfig:
    """Frozen configuration for one in-memory verification case."""

    benchmark_id: str
    N: int
    Re: float
    dt: float
    n_steps: int
    t_0: float
    advection_method: str | None
    scaffold_path: Path
    requested_final_time: float | None = None
    product_dealiasing: bool = PRODUCT_DEALIASING_ENABLED
    post_step_mask_policy: str | None = None


@dataclass(frozen=True, slots=True)
class SolverContract:
    """Audited solver attributes for one constructed adapter."""

    solver_class: str
    N: int
    L: float
    dx: float
    Re: float
    nu: float
    dt: float
    constructor_steps: int
    requested_advection_method: str | None
    constructor_advection_method: str
    mask_shape: tuple[int, int]
    retained_mode_count: int
    removed_mode_count: int
    scaffold_path: str


@dataclass(frozen=True, slots=True)
class MutationGuard:
    """Mutation and memory-independence result for one allowed call."""

    input_unchanged: bool
    solver_state_unchanged: bool
    output_shares_input_memory: bool
    output_shares_solver_state_memory: bool


@dataclass(frozen=True, slots=True)
class GuardedFieldCall:
    """Result from one allowed solver-field call."""

    operation: str
    field: np.ndarray
    mutation_guard: MutationGuard


@dataclass(frozen=True, slots=True)
class ErrorNorms:
    """Native-grid error norms."""

    L1_mean: float
    L2_rms: float
    Linf: float
    exact_L2_rms: float
    numerical_L2_rms: float
    relative_L2: float | None
    finite: bool


@dataclass(frozen=True, slots=True)
class RHSResult:
    """One external RHS evaluation."""

    track: str
    time: float
    value: np.ndarray
    advection: np.ndarray | None
    diffusion: np.ndarray
    source: np.ndarray | None
    source_sha256: str | None
    allowed_methods_called: tuple[str, ...]
    forcing_call_count: int
    input_unchanged: bool
    solver_state_unchanged: bool


@dataclass(frozen=True, slots=True)
class StepResult:
    """One external RK2-style step."""

    track: str
    t_n: float
    t_stage_1: float
    t_stage_2: float
    t_next: float
    dt: float
    w_n: np.ndarray
    k1: np.ndarray
    predictor: np.ndarray
    k2: np.ndarray
    provisional: np.ndarray
    w_next: np.ndarray
    stage_1_source_sha256: str | None
    stage_2_source_sha256: str | None
    mask_application_count: int
    mask_policy: str
    pre_mask_L2_rms: float
    post_mask_L2_rms: float
    maximum_imaginary_residue: float
    input_unchanged: bool
    solver_state_unchanged: bool


@dataclass(frozen=True, slots=True)
class OperatorCaseResult:
    """In-memory result for one O1 or O2 operator case."""

    case_id: str
    benchmark_id: str
    track: str
    advection_method: str
    compatibility_policy: str
    discrete_mean_removed: float
    omega_raw: np.ndarray
    omega_input: np.ndarray
    computed_adv: np.ndarray
    exact_adv: np.ndarray
    error_adv: np.ndarray
    error_norms: ErrorNorms
    mutation_guard: MutationGuard
    mask_application_count: int
    forcing_call_count: int
    metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class EvolutionCaseResult:
    """In-memory result for one Track L or Track M evolution case."""

    case_id: str
    benchmark_id: str
    track: str
    advection_method: str | None
    initial_time: float
    final_time: float
    dt: float
    n_steps: int
    initial_omega: np.ndarray
    numerical_omega: np.ndarray
    exact_omega: np.ndarray
    error_omega: np.ndarray
    error_norms: ErrorNorms
    steps: tuple[StepResult, ...]
    total_mask_applications: int
    forcing_call_count: int
    metadata: Mapping[str, object]


def _exact_module() -> Any:
    """
    Import the independent exact-reference module only when a harness function
    is explicitly called.
    """

    from project.verification import phase13_exact_references

    return phase13_exact_references


def _selectable_solver_class() -> type[Any]:
    """
    Import the selectable solver class only when guarded construction is
    explicitly requested.
    """

    from project.solver.selectable_advection_solver import (
        SelectableAdvectionSolver,
    )

    return SelectableAdvectionSolver


def _as_finite_float(
    value: object,
    *,
    name: str,
    positive: bool = False,
) -> float:
    """Normalize one finite scalar."""

    if isinstance(value, bool) or not np.isscalar(value):
        raise TypeError(f'{name} must be a real scalar')

    result = float(value)

    if not np.isfinite(result):
        raise ValueError(f'{name} must be finite')

    if positive and result <= 0.0:
        raise ValueError(f'{name} must be strictly positive')

    return result


def _as_nonnegative_integer(
    value: object,
    *,
    name: str,
) -> int:
    """Normalize one nonnegative integer."""

    if isinstance(value, bool) or not isinstance(
        value,
        (int, np.integer),
    ):
        raise TypeError(f'{name} must be an integer')

    result = int(value)

    if result < 0:
        raise ValueError(f'{name} must be nonnegative')

    return result


def _normalize_method(method: object) -> str:
    """Validate one exact selectable-advection method identifier."""

    if not isinstance(method, str):
        raise TypeError('advection_method must be a string')

    normalized = method.strip().lower()

    if normalized not in SUPPORTED_ADVECTION_METHODS:
        allowed = ', '.join(SUPPORTED_ADVECTION_METHODS)

        raise ValueError(
            f'Unknown advection_method={method!r}. '
            f'Allowed values: {allowed}'
        )

    return normalized


def _benchmark_definition(benchmark_id: str) -> Any:
    """Return the independent frozen benchmark definition."""

    return _exact_module().get_benchmark_definition(benchmark_id)


def validate_config(
    config: VerificationConfig,
) -> Mapping[str, object]:
    """Validate one case without constructing or calling a solver."""

    if not isinstance(config, VerificationConfig):
        raise TypeError(
            'config must be a VerificationConfig instance'
        )

    definition = _benchmark_definition(config.benchmark_id)

    if isinstance(config.N, bool) or not isinstance(
        config.N,
        (int, np.integer),
    ):
        raise TypeError('N must be an integer')

    N = int(config.N)

    if N < 2 or N % 2:
        raise ValueError(
            'N must be an even integer of at least 2'
        )

    Re = _as_finite_float(
        config.Re,
        name='Re',
        positive=True,
    )

    dt = _as_finite_float(
        config.dt,
        name='dt',
        positive=True,
    )

    n_steps = _as_nonnegative_integer(
        config.n_steps,
        name='n_steps',
    )

    t_0 = _as_finite_float(
        config.t_0,
        name='t_0',
    )

    if not isinstance(config.scaffold_path, Path):
        raise TypeError(
            'scaffold_path must be a pathlib.Path'
        )

    if config.scaffold_path.name != '_solver_scaffold':
        raise ValueError(
            'scaffold_path must end with _solver_scaffold'
        )

    if config.product_dealiasing is not False:
        raise ValueError(
            'Phase 13 uses product_dealiasing=False'
        )

    expected_mask_policy = (
        NO_POST_STEP_MASK
        if definition.track in OPERATOR_TRACKS
        else POST_STEP_MASK_POLICY
    )

    mask_policy = (
        expected_mask_policy
        if config.post_step_mask_policy is None
        else str(config.post_step_mask_policy)
    )

    if mask_policy != expected_mask_policy:
        raise ValueError(
            'Unexpected post-step mask policy for this track'
        )

    method: str | None

    if definition.requires_advection_method:
        method = _normalize_method(config.advection_method)
    else:
        if config.advection_method is not None:
            raise ValueError(
                'Primary Track L evolution must not receive '
                'an advection method'
            )

        method = None

    if definition.track in OPERATOR_TRACKS:
        if n_steps != 0:
            raise ValueError(
                'Operator cases require n_steps=0'
            )

    elif definition.track in EVOLUTION_TRACKS:
        if n_steps <= 0:
            raise ValueError(
                'Evolution cases require n_steps>0'
            )

    else:
        raise ValueError(
            f'Unsupported benchmark track={definition.track!r}'
        )

    actual_final_time = t_0 + n_steps * dt
    requested_final_time = config.requested_final_time

    if requested_final_time is not None:
        requested = _as_finite_float(
            requested_final_time,
            name='requested_final_time',
        )

        tolerance = (
            32.0
            * np.finfo(np.float64).eps
            * max(
                1.0,
                abs(requested),
                abs(actual_final_time),
            )
        )

        if abs(requested - actual_final_time) > tolerance:
            raise ValueError(
                'Requested and actual final times do not align'
            )

    return MappingProxyType(
        {
            'benchmark_id': definition.benchmark_id,
            'track': definition.track,
            'N': N,
            'Re': Re,
            'nu': 1.0 / Re,
            'dt': dt,
            'n_steps': n_steps,
            't_0': t_0,
            't_final_actual': actual_final_time,
            'advection_method': method,
            'product_dealiasing': False,
            'post_step_mask_policy': mask_policy,
        }
    )


def validate_phase13f_pilot_boundary(
    config: VerificationConfig,
) -> Mapping[str, object]:
    """
    Validate the maximum Phase 13D pilot boundary.

    Calling this validator does not authorize or execute a pilot.
    """

    normalized = validate_config(config)

    if normalized['N'] != 16:
        raise ValueError(
            'The first Phase 13F pilot boundary requires N=16'
        )

    track = str(normalized['track'])
    n_steps = int(normalized['n_steps'])

    if track in OPERATOR_TRACKS and n_steps != 0:
        raise ValueError(
            'Operator pilot cases require n_steps=0'
        )

    if track in EVOLUTION_TRACKS and n_steps > 2:
        raise ValueError(
            'Evolution pilot cases may not exceed two steps'
        )

    return MappingProxyType(
        {
            **dict(normalized),
            'pilot_boundary_valid': True,
            'pilot_authorized': False,
        }
    )


def case_id_from_config(config: VerificationConfig) -> str:
    """Create a deterministic in-memory case identifier."""

    normalized = validate_config(config)
    method = normalized['advection_method']
    method_token = 'none' if method is None else str(method)

    return (
        f"{normalized['benchmark_id']}"
        f"__N{normalized['N']}"
        f"__Re{float(normalized['Re']):.12g}"
        f"__dt{float(normalized['dt']):.12g}"
        f"__steps{normalized['n_steps']}"
        f"__t0{float(normalized['t_0']):.12g}"
        f"__method_{method_token}"
    )


def reconstruct_strict_two_thirds_mask(
    N: int,
    L: float,
) -> np.ndarray:
    """Independently reconstruct the audited coordinate-wise mask."""

    if isinstance(N, bool) or not isinstance(
        N,
        (int, np.integer),
    ):
        raise TypeError('N must be an integer')

    size = int(N)

    if size < 2 or size % 2:
        raise ValueError(
            'N must be an even integer of at least 2'
        )

    domain_length = _as_finite_float(
        L,
        name='L',
        positive=True,
    )

    dx = domain_length / size

    k = (
        np.fft.fftfreq(
            size,
            d=dx,
        )
        * 2.0
        * np.pi
    )

    kx, ky = np.meshgrid(
        k,
        k,
        indexing='xy',
    )

    kmax = float(
        np.max(
            np.abs(k)
        )
    )

    mask = (
        np.abs(kx) < (2.0 / 3.0) * kmax
    ) & (
        np.abs(ky) < (2.0 / 3.0) * kmax
    )

    result = np.array(
        mask,
        dtype=bool,
        copy=True,
    )

    result.setflags(write=False)

    return result


def _finite_real_array(
    value: object,
    *,
    shape: tuple[int, int],
    name: str,
    read_only: bool,
) -> np.ndarray:
    """Return one independent finite real float64 field."""

    raw = np.asarray(value)

    if raw.shape != shape:
        raise ValueError(
            f'{name} has shape {raw.shape}; expected {shape}'
        )

    if not np.isrealobj(raw):
        raise ValueError(
            f'{name} must be real-valued'
        )

    result = np.array(
        raw,
        dtype=np.float64,
        copy=True,
    )

    if not np.isfinite(result).all():
        raise ValueError(
            f'{name} must be finite'
        )

    if read_only:
        result.setflags(write=False)

    return result


def _freeze_mapping(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    """Return one shallow immutable metadata mapping."""

    return MappingProxyType(dict(value))


def hash_array(value: object) -> str:
    """Hash one array with shape and dtype included."""

    array = np.ascontiguousarray(np.asarray(value))
    digest = sha256()

    digest.update(
        str(array.dtype).encode('utf-8')
    )

    digest.update(b'\x00')

    digest.update(
        repr(array.shape).encode('ascii')
    )

    digest.update(b'\x00')
    digest.update(array.tobytes(order='C'))

    return digest.hexdigest().upper()


def _solver_state_copy(
    solver: SolverProtocol,
) -> np.ndarray:
    """Copy the solver state for an exact mutation check."""

    return np.array(
        solver.w,
        copy=True,
    )


def _guarded_solver_call(
    solver: SolverProtocol,
    input_field: object,
    *,
    operation: str,
    callback: Callable[[np.ndarray], object],
) -> GuardedFieldCall:
    """Call one authorized solver interface with mutation guards."""

    shape = (
        int(solver.N),
        int(solver.N),
    )

    call_input = _finite_real_array(
        input_field,
        shape=shape,
        name='input_field',
        read_only=False,
    )

    input_before = np.array(
        call_input,
        copy=True,
    )

    solver_before = _solver_state_copy(solver)

    output_raw = callback(call_input)

    input_unchanged = bool(
        np.array_equal(
            input_before,
            call_input,
        )
    )

    solver_state_unchanged = bool(
        np.array_equal(
            solver_before,
            solver.w,
        )
    )

    output_shares_input_memory = bool(
        np.shares_memory(
            np.asarray(output_raw),
            call_input,
        )
    )

    output_shares_solver_state_memory = bool(
        np.shares_memory(
            np.asarray(output_raw),
            solver.w,
        )
    )

    if not input_unchanged:
        raise RuntimeError(
            f'{operation} mutated its input field'
        )

    if not solver_state_unchanged:
        raise RuntimeError(
            f'{operation} mutated solver.w'
        )

    if output_shares_input_memory:
        raise RuntimeError(
            f'{operation} returned memory shared with its input'
        )

    if output_shares_solver_state_memory:
        raise RuntimeError(
            f'{operation} returned memory shared with solver.w'
        )

    output = _finite_real_array(
        output_raw,
        shape=shape,
        name=f'{operation}_output',
        read_only=True,
    )

    return GuardedFieldCall(
        operation=operation,
        field=output,
        mutation_guard=MutationGuard(
            input_unchanged=input_unchanged,
            solver_state_unchanged=solver_state_unchanged,
            output_shares_input_memory=(
                output_shares_input_memory
            ),
            output_shares_solver_state_memory=(
                output_shares_solver_state_memory
            ),
        ),
    )


def guarded_advection(
    solver: SolverProtocol,
    w: object,
) -> GuardedFieldCall:
    """Call only the audited selectable-advection interface."""

    return _guarded_solver_call(
        solver,
        w,
        operation='compute_advection',
        callback=solver.compute_advection,
    )


def guarded_diffusion(
    solver: SolverProtocol,
    w: object,
) -> GuardedFieldCall:
    """
    Call the viscosity-weighted spectral diffusion interface.

    The returned field already contains viscosity. This harness does not
    multiply it by nu again.
    """

    return _guarded_solver_call(
        solver,
        w,
        operation='laplacian_spectral',
        callback=solver.laplacian_spectral,
    )


def validate_solver_contract(
    solver: SolverProtocol,
    config: VerificationConfig,
) -> SolverContract:
    """Verify solver grid, viscosity, constructor, method, and mask."""

    normalized = validate_config(config)

    N = int(normalized['N'])
    Re = float(normalized['Re'])
    nu = float(normalized['nu'])
    dt = float(normalized['dt'])
    method = normalized['advection_method']

    if int(solver.N) != N:
        raise ValueError(
            'solver.N does not match configuration'
        )

    if int(solver.steps) != CONSTRUCTOR_STEPS:
        raise ValueError(
            'solver.steps must equal zero'
        )

    tolerance = (
        32.0
        * np.finfo(np.float64).eps
    )

    if not np.isclose(
        float(solver.nu),
        nu,
        rtol=tolerance,
        atol=0.0,
    ):
        raise ValueError(
            'solver.nu does not equal 1/Re'
        )

    if not np.isclose(
        float(solver.dt),
        dt,
        rtol=tolerance,
        atol=0.0,
    ):
        raise ValueError(
            'solver.dt does not match configuration'
        )

    if not np.isclose(
        float(solver.L),
        2.0 * np.pi,
        rtol=tolerance,
        atol=0.0,
    ):
        raise ValueError(
            'solver.L does not match 2*pi'
        )

    expected_dx = float(solver.L) / N

    if not np.isclose(
        float(solver.dx),
        expected_dx,
        rtol=tolerance,
        atol=0.0,
    ):
        raise ValueError(
            'solver.dx is inconsistent'
        )

    exact = _exact_module()
    independent_grid = exact.construct_native_grid(N)

    for name, observed, expected in (
        ('solver.x', solver.x, independent_grid.x),
        ('solver.X', solver.X, independent_grid.X),
        ('solver.Y', solver.Y, independent_grid.Y),
    ):
        observed_array = np.asarray(
            observed,
            dtype=np.float64,
        )

        expected_array = np.asarray(
            expected,
            dtype=np.float64,
        )

        grid_tolerance = (
            16.0
            * np.finfo(np.float64).eps
            * max(
                1.0,
                float(solver.L),
            )
        )

        if not np.allclose(
            observed_array,
            expected_array,
            rtol=0.0,
            atol=grid_tolerance,
        ):
            raise ValueError(
                f'{name} differs from the independent grid'
            )

    expected_mask = reconstruct_strict_two_thirds_mask(
        N,
        float(solver.L),
    )

    observed_mask = np.asarray(
        solver.deal,
        dtype=bool,
    )

    if observed_mask.shape != expected_mask.shape:
        raise ValueError(
            'solver.deal has an unexpected shape'
        )

    if not np.array_equal(
        observed_mask,
        expected_mask,
    ):
        raise ValueError(
            'solver.deal differs from the independent mask'
        )

    solver_state = np.asarray(solver.w)

    if solver_state.shape != (N, N):
        raise ValueError(
            'solver.w has an unexpected shape'
        )

    if not np.isrealobj(solver_state):
        raise ValueError(
            'solver.w must be real-valued'
        )

    if not np.isfinite(solver_state).all():
        raise ValueError(
            'solver.w must be finite'
        )

    if np.count_nonzero(solver_state):
        raise ValueError(
            'solver.w must be initially zero'
        )

    constructor_method = str(
        solver.advection_method
    )

    if method is None:
        if constructor_method != TRACK_L_CONSTRUCTOR_METHOD:
            raise ValueError(
                'Track L constructor method differs from its '
                'frozen unused default'
            )

    elif constructor_method != method:
        raise ValueError(
            'solver.advection_method does not match configuration'
        )

    retained_mode_count = int(
        np.count_nonzero(expected_mask)
    )

    return SolverContract(
        solver_class=type(solver).__name__,
        N=N,
        L=float(solver.L),
        dx=float(solver.dx),
        Re=Re,
        nu=float(solver.nu),
        dt=float(solver.dt),
        constructor_steps=int(solver.steps),
        requested_advection_method=(
            None
            if method is None
            else str(method)
        ),
        constructor_advection_method=constructor_method,
        mask_shape=expected_mask.shape,
        retained_mode_count=retained_mode_count,
        removed_mode_count=int(
            expected_mask.size
            - retained_mode_count
        ),
        scaffold_path=str(config.scaffold_path),
    )


def construct_guarded_solver(
    config: VerificationConfig,
) -> tuple[SolverProtocol, SolverContract]:
    """
    Construct the selectable solver with steps=0 and verify its contract.

    This function is dormant until explicitly called by an authorized phase.
    """

    normalized = validate_config(config)
    solver_class = _selectable_solver_class()
    method = normalized['advection_method']

    common_arguments = {
        'nx': int(normalized['N']),
        'ny': int(normalized['N']),
        'Re': float(normalized['Re']),
        'run_path': Path(config.scaffold_path),
        'dt': float(normalized['dt']),
        'steps': CONSTRUCTOR_STEPS,
    }

    if method is None:
        solver = solver_class(
            **common_arguments
        )
    else:
        solver = solver_class(
            **common_arguments,
            advection_method=str(method),
        )

    contract = validate_solver_contract(
        solver,
        config,
    )

    return solver, contract


def compute_error_norms(
    numerical: object,
    exact: object,
) -> tuple[np.ndarray, ErrorNorms]:
    """Compute native-grid absolute error fields and norms."""

    numerical_array = np.asarray(numerical)
    exact_array = np.asarray(exact)

    if numerical_array.shape != exact_array.shape:
        raise ValueError(
            'Numerical and exact fields have different shapes'
        )

    if (
        not np.isrealobj(numerical_array)
        or not np.isrealobj(exact_array)
    ):
        raise ValueError(
            'Numerical and exact fields must be real'
        )

    if (
        not np.isfinite(numerical_array).all()
        or not np.isfinite(exact_array).all()
    ):
        raise ValueError(
            'Numerical and exact fields must be finite'
        )

    error = np.array(
        numerical_array - exact_array,
        dtype=np.float64,
        copy=True,
    )

    absolute_error = np.abs(error)

    L1_mean = float(
        np.mean(
            absolute_error,
            dtype=np.float64,
        )
    )

    L2_rms = float(
        np.sqrt(
            np.mean(
                error * error,
                dtype=np.float64,
            )
        )
    )

    Linf = float(
        np.max(absolute_error)
    )

    exact_L2_rms = float(
        np.sqrt(
            np.mean(
                exact_array * exact_array,
                dtype=np.float64,
            )
        )
    )

    numerical_L2_rms = float(
        np.sqrt(
            np.mean(
                numerical_array * numerical_array,
                dtype=np.float64,
            )
        )
    )

    relative_L2: float | None

    if (
        np.isfinite(exact_L2_rms)
        and exact_L2_rms > 0.0
    ):
        relative_L2 = (
            L2_rms
            / exact_L2_rms
        )
    else:
        relative_L2 = None

    finite = bool(
        np.isfinite(
            (
                L1_mean,
                L2_rms,
                Linf,
                exact_L2_rms,
                numerical_L2_rms,
            )
        ).all()
        and (
            relative_L2 is None
            or np.isfinite(relative_L2)
        )
    )

    if not finite:
        raise ValueError(
            'One or more primary error quantities are nonfinite'
        )

    error.setflags(write=False)

    return (
        error,
        ErrorNorms(
            L1_mean=L1_mean,
            L2_rms=L2_rms,
            Linf=Linf,
            exact_L2_rms=exact_L2_rms,
            numerical_L2_rms=numerical_L2_rms,
            relative_L2=relative_L2,
            finite=finite,
        ),
    )


def evaluate_exact_reference(
    config: VerificationConfig,
    solver: SolverProtocol,
    *,
    time: float,
) -> Any:
    """Evaluate an independent exact reference on the native solver grid."""

    validate_solver_contract(
        solver,
        config,
    )

    exact = _exact_module()

    reference = exact.evaluate_reference(
        config.benchmark_id,
        solver.X,
        solver.Y,
        time,
        float(solver.nu),
    )

    exact.validate_reference_fields(reference)

    return reference


def run_operator_case(
    solver: SolverProtocol,
    config: VerificationConfig,
) -> OperatorCaseResult:
    """Run one isolated O1 or O2 advection-operator evaluation."""

    normalized = validate_config(config)
    track = str(normalized['track'])

    if track not in OPERATOR_TRACKS:
        raise ValueError(
            'run_operator_case requires O1 or O2'
        )

    contract = validate_solver_contract(
        solver,
        config,
    )

    reference = evaluate_exact_reference(
        config,
        solver,
        time=float(normalized['t_0']),
    )

    call = guarded_advection(
        solver,
        reference.omega_input,
    )

    error, norms = compute_error_norms(
        call.field,
        reference.adv,
    )

    case_id = case_id_from_config(config)

    metadata = _freeze_mapping(
        {
            'harness_version': HARNESS_VERSION,
            'case_id': case_id,
            'benchmark_id': config.benchmark_id,
            'track': track,
            'advection_method': str(
                normalized['advection_method']
            ),
            'product_dealiasing': False,
            'post_step_mask_policy': NO_POST_STEP_MASK,
            'mask_application_count': 0,
            'forcing_call_count': 0,
            'solver_contract': contract,
            'allowed_methods_called': (
                'compute_advection',
            ),
            'prohibited_methods_called': (),
        }
    )

    return OperatorCaseResult(
        case_id=case_id,
        benchmark_id=config.benchmark_id,
        track=track,
        advection_method=str(
            normalized['advection_method']
        ),
        compatibility_policy=(
            reference.compatibility_policy
        ),
        discrete_mean_removed=float(
            reference.discrete_mean_removed
        ),
        omega_raw=reference.omega_raw,
        omega_input=reference.omega_input,
        computed_adv=call.field,
        exact_adv=reference.adv,
        error_adv=error,
        error_norms=norms,
        mutation_guard=call.mutation_guard,
        mask_application_count=0,
        forcing_call_count=0,
        metadata=metadata,
    )


def track_l_rhs(
    solver: SolverProtocol,
    w: object,
    time: float,
    config: VerificationConfig,
) -> RHSResult:
    """Evaluate the external linear Track L RHS."""

    normalized = validate_config(config)

    if normalized['track'] != 'L':
        raise ValueError(
            'track_l_rhs requires the Track L benchmark'
        )

    validate_solver_contract(
        solver,
        config,
    )

    time_value = _as_finite_float(
        time,
        name='time',
    )

    diffusion = guarded_diffusion(
        solver,
        w,
    )

    return RHSResult(
        track='L',
        time=time_value,
        value=diffusion.field,
        advection=None,
        diffusion=diffusion.field,
        source=None,
        source_sha256=None,
        allowed_methods_called=(
            'laplacian_spectral',
        ),
        forcing_call_count=0,
        input_unchanged=(
            diffusion.mutation_guard.input_unchanged
        ),
        solver_state_unchanged=(
            diffusion.mutation_guard.solver_state_unchanged
        ),
    )


def track_m_rhs(
    solver: SolverProtocol,
    w: object,
    time: float,
    config: VerificationConfig,
) -> RHSResult:
    """Evaluate the external source-aware Track M RHS."""

    normalized = validate_config(config)

    if normalized['track'] != 'M':
        raise ValueError(
            'track_m_rhs requires the Track M benchmark'
        )

    validate_solver_contract(
        solver,
        config,
    )

    time_value = _as_finite_float(
        time,
        name='time',
    )

    advection = guarded_advection(
        solver,
        w,
    )

    diffusion = guarded_diffusion(
        solver,
        w,
    )

    reference = evaluate_exact_reference(
        config,
        solver,
        time=time_value,
    )

    if reference.source is None:
        raise RuntimeError(
            'Track M exact source is absent'
        )

    shape = (
        int(solver.N),
        int(solver.N),
    )

    source = _finite_real_array(
        reference.source,
        shape=shape,
        name='track_m_source',
        read_only=True,
    )

    rhs = _finite_real_array(
        (
            -advection.field
            + diffusion.field
            + source
        ),
        shape=shape,
        name='track_m_rhs',
        read_only=True,
    )

    input_unchanged = bool(
        advection.mutation_guard.input_unchanged
        and diffusion.mutation_guard.input_unchanged
    )

    solver_state_unchanged = bool(
        advection.mutation_guard.solver_state_unchanged
        and diffusion.mutation_guard.solver_state_unchanged
    )

    return RHSResult(
        track='M',
        time=time_value,
        value=rhs,
        advection=advection.field,
        diffusion=diffusion.field,
        source=source,
        source_sha256=hash_array(source),
        allowed_methods_called=(
            'compute_advection',
            'laplacian_spectral',
        ),
        forcing_call_count=0,
        input_unchanged=input_unchanged,
        solver_state_unchanged=solver_state_unchanged,
    )


def apply_post_step_mask_once(
    solver: SolverProtocol,
    provisional: object,
    config: VerificationConfig,
) -> tuple[np.ndarray, float, float, float]:
    """Apply the independently verified post-step mask exactly once."""

    normalized = validate_config(config)

    if normalized['track'] not in EVOLUTION_TRACKS:
        raise ValueError(
            'The post-step mask is prohibited for operator cases'
        )

    validate_solver_contract(
        solver,
        config,
    )

    shape = (
        int(solver.N),
        int(solver.N),
    )

    provisional_array = _finite_real_array(
        provisional,
        shape=shape,
        name='provisional',
        read_only=False,
    )

    mask = reconstruct_strict_two_thirds_mask(
        int(solver.N),
        float(solver.L),
    )

    spectrum = np.fft.fft2(provisional_array)
    masked_spectrum = spectrum * mask
    physical_complex = np.fft.ifft2(masked_spectrum)

    maximum_imaginary_residue = float(
        np.max(
            np.abs(
                physical_complex.imag
            )
        )
    )

    result = _finite_real_array(
        physical_complex.real,
        shape=shape,
        name='post_step_mask_result',
        read_only=True,
    )

    pre_mask_L2_rms = float(
        np.sqrt(
            np.mean(
                provisional_array * provisional_array,
                dtype=np.float64,
            )
        )
    )

    post_mask_L2_rms = float(
        np.sqrt(
            np.mean(
                result * result,
                dtype=np.float64,
            )
        )
    )

    return (
        result,
        pre_mask_L2_rms,
        post_mask_L2_rms,
        maximum_imaginary_residue,
    )


def _rhs_callback(
    solver: SolverProtocol,
    config: VerificationConfig,
) -> Callable[[object, float], RHSResult]:
    """Select exactly one external RHS."""

    track = str(
        validate_config(config)['track']
    )

    if track == 'L':
        return lambda w, t: track_l_rhs(
            solver,
            w,
            t,
            config,
        )

    if track == 'M':
        return lambda w, t: track_m_rhs(
            solver,
            w,
            t,
            config,
        )

    raise ValueError(
        'External RK2 requires Track L or Track M'
    )


def external_rk2_step(
    solver: SolverProtocol,
    config: VerificationConfig,
    w_n: object,
    t_n: float,
) -> StepResult:
    """Perform one external RK2-style step and one post-step mask."""

    normalized = validate_config(config)
    track = str(normalized['track'])

    if track not in EVOLUTION_TRACKS:
        raise ValueError(
            'external_rk2_step requires Track L or Track M'
        )

    validate_solver_contract(
        solver,
        config,
    )

    shape = (
        int(solver.N),
        int(solver.N),
    )

    state = _finite_real_array(
        w_n,
        shape=shape,
        name='w_n',
        read_only=False,
    )

    state_before = np.array(
        state,
        copy=True,
    )

    solver_before = _solver_state_copy(solver)

    time_value = _as_finite_float(
        t_n,
        name='t_n',
    )

    dt = float(normalized['dt'])
    rhs = _rhs_callback(solver, config)

    stage_1 = rhs(
        state,
        time_value,
    )

    predictor = _finite_real_array(
        (
            state
            + dt * stage_1.value
        ),
        shape=shape,
        name='predictor',
        read_only=True,
    )

    stage_2_time = time_value + dt

    stage_2 = rhs(
        predictor,
        stage_2_time,
    )

    provisional = _finite_real_array(
        (
            state
            + 0.5
            * dt
            * (
                stage_1.value
                + stage_2.value
            )
        ),
        shape=shape,
        name='provisional',
        read_only=True,
    )

    (
        w_next,
        pre_mask_L2_rms,
        post_mask_L2_rms,
        maximum_imaginary_residue,
    ) = apply_post_step_mask_once(
        solver,
        provisional,
        config,
    )

    input_unchanged = bool(
        np.array_equal(
            state_before,
            state,
        )
        and stage_1.input_unchanged
        and stage_2.input_unchanged
    )

    solver_state_unchanged = bool(
        np.array_equal(
            solver_before,
            solver.w,
        )
        and stage_1.solver_state_unchanged
        and stage_2.solver_state_unchanged
    )

    if not input_unchanged:
        raise RuntimeError(
            'external_rk2_step mutated its input'
        )

    if not solver_state_unchanged:
        raise RuntimeError(
            'external_rk2_step mutated solver.w'
        )

    if track == 'M':
        if stage_1.source_sha256 is None:
            raise RuntimeError(
                'Track M stage 1 source hash is absent'
            )

        if stage_2.source_sha256 is None:
            raise RuntimeError(
                'Track M stage 2 source hash is absent'
            )

        if stage_1.time == stage_2.time:
            raise RuntimeError(
                'Track M source stages used the same time'
            )

    elif (
        stage_1.source_sha256 is not None
        or stage_2.source_sha256 is not None
    ):
        raise RuntimeError(
            'Track L unexpectedly contains source hashes'
        )

    frozen_state = _finite_real_array(
        state_before,
        shape=shape,
        name='w_n_snapshot',
        read_only=True,
    )

    return StepResult(
        track=track,
        t_n=time_value,
        t_stage_1=time_value,
        t_stage_2=stage_2_time,
        t_next=stage_2_time,
        dt=dt,
        w_n=frozen_state,
        k1=stage_1.value,
        predictor=predictor,
        k2=stage_2.value,
        provisional=provisional,
        w_next=w_next,
        stage_1_source_sha256=(
            stage_1.source_sha256
        ),
        stage_2_source_sha256=(
            stage_2.source_sha256
        ),
        mask_application_count=1,
        mask_policy=POST_STEP_MASK_POLICY,
        pre_mask_L2_rms=pre_mask_L2_rms,
        post_mask_L2_rms=post_mask_L2_rms,
        maximum_imaginary_residue=(
            maximum_imaginary_residue
        ),
        input_unchanged=input_unchanged,
        solver_state_unchanged=solver_state_unchanged,
    )


def run_evolution_case(
    solver: SolverProtocol,
    config: VerificationConfig,
) -> EvolutionCaseResult:
    """Run one in-memory Track L or Track M external evolution case."""

    normalized = validate_config(config)
    track = str(normalized['track'])

    if track not in EVOLUTION_TRACKS:
        raise ValueError(
            'run_evolution_case requires Track L or Track M'
        )

    contract = validate_solver_contract(
        solver,
        config,
    )

    t_0 = float(normalized['t_0'])
    n_steps = int(normalized['n_steps'])

    initial_reference = evaluate_exact_reference(
        config,
        solver,
        time=t_0,
    )

    shape = (
        int(solver.N),
        int(solver.N),
    )

    state = _finite_real_array(
        initial_reference.omega_input,
        shape=shape,
        name='initial_omega',
        read_only=True,
    )

    initial_omega = state
    step_results: list[StepResult] = []
    time_value = t_0

    for _ in range(n_steps):
        step = external_rk2_step(
            solver,
            config,
            state,
            time_value,
        )

        step_results.append(step)
        state = step.w_next
        time_value = step.t_next

    expected_final_time = float(
        normalized['t_final_actual']
    )

    tolerance = (
        32.0
        * np.finfo(np.float64).eps
        * max(
            1.0,
            abs(time_value),
            abs(expected_final_time),
        )
    )

    if abs(time_value - expected_final_time) > tolerance:
        raise RuntimeError(
            'Actual final time differs from the validated final time'
        )

    final_reference = evaluate_exact_reference(
        config,
        solver,
        time=time_value,
    )

    error, norms = compute_error_norms(
        state,
        final_reference.omega_input,
    )

    total_mask_applications = sum(
        step.mask_application_count
        for step in step_results
    )

    if total_mask_applications != n_steps:
        raise RuntimeError(
            'The post-step mask count is not exactly one per step'
        )

    forcing_call_count = 0
    case_id = case_id_from_config(config)

    metadata = _freeze_mapping(
        {
            'harness_version': HARNESS_VERSION,
            'case_id': case_id,
            'benchmark_id': config.benchmark_id,
            'track': track,
            'advection_method': normalized[
                'advection_method'
            ],
            'source_policy': (
                L_SOURCE_POLICY
                if track == 'L'
                else M_SOURCE_POLICY
            ),
            'product_dealiasing': False,
            'post_step_mask_policy': POST_STEP_MASK_POLICY,
            'mask_application_count': (
                total_mask_applications
            ),
            'forcing_call_count': forcing_call_count,
            't_0': t_0,
            'dt': float(normalized['dt']),
            'n_steps': n_steps,
            't_final_actual': time_value,
            'solver_contract': contract,
            'prohibited_methods_called': (),
        }
    )

    return EvolutionCaseResult(
        case_id=case_id,
        benchmark_id=config.benchmark_id,
        track=track,
        advection_method=(
            None
            if normalized['advection_method'] is None
            else str(normalized['advection_method'])
        ),
        initial_time=t_0,
        final_time=time_value,
        dt=float(normalized['dt']),
        n_steps=n_steps,
        initial_omega=initial_omega,
        numerical_omega=state,
        exact_omega=final_reference.omega_input,
        error_omega=error,
        error_norms=norms,
        steps=tuple(step_results),
        total_mask_applications=(
            total_mask_applications
        ),
        forcing_call_count=forcing_call_count,
        metadata=metadata,
    )


def implementation_contract() -> Mapping[str, object]:
    """Return immutable static harness-boundary metadata."""

    return MappingProxyType(
        {
            'harness_version': HARNESS_VERSION,
            'supported_advection_methods': (
                SUPPORTED_ADVECTION_METHODS
            ),
            'constructor_steps': CONSTRUCTOR_STEPS,
            'product_dealiasing': False,
            'post_step_mask_policy': POST_STEP_MASK_POLICY,
            'prohibited_solver_interfaces': (
                PROHIBITED_SOLVER_INTERFACES
            ),
            'result_writing_implemented': False,
            'pilot_authorized': False,
            'convergence_claim': False,
            'physical_validation_claim': False,
        }
    )


__all__ = (
    'SolverProtocol',
    'VerificationConfig',
    'SolverContract',
    'MutationGuard',
    'GuardedFieldCall',
    'ErrorNorms',
    'RHSResult',
    'StepResult',
    'OperatorCaseResult',
    'EvolutionCaseResult',
    'HARNESS_VERSION',
    'SUPPORTED_ADVECTION_METHODS',
    'TRACK_L_CONSTRUCTOR_METHOD',
    'O1_BENCHMARK_ID',
    'O2_BENCHMARK_ID',
    'L_BENCHMARK_ID',
    'M_BENCHMARK_ID',
    'O2_COMPATIBILITY_POLICY',
    'M_SOURCE_POLICY',
    'L_SOURCE_POLICY',
    'NO_POST_STEP_MASK',
    'POST_STEP_MASK_POLICY',
    'PRODUCT_DEALIASING_ENABLED',
    'CONSTRUCTOR_STEPS',
    'PROHIBITED_SOLVER_INTERFACES',
    'validate_config',
    'validate_phase13f_pilot_boundary',
    'case_id_from_config',
    'reconstruct_strict_two_thirds_mask',
    'hash_array',
    'guarded_advection',
    'guarded_diffusion',
    'validate_solver_contract',
    'construct_guarded_solver',
    'compute_error_norms',
    'evaluate_exact_reference',
    'run_operator_case',
    'track_l_rhs',
    'track_m_rhs',
    'apply_post_step_mask_once',
    'external_rk2_step',
    'run_evolution_case',
    'implementation_contract',
)