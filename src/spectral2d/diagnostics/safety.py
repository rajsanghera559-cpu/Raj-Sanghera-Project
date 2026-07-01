from __future__ import annotations
import numpy as np

def assert_finite(name: str, array: np.ndarray, step: int) -> None:
    """Tripwire: Raises FloatingPointError if array contains NaN or Inf."""
    if not np.all(np.isfinite(array)):
        bad_count = int(np.size(array) - np.count_nonzero(np.isfinite(array)))
        raise FloatingPointError(
            f"{name} contains non-finite values at step={step}. "
            f"bad_count={bad_count}"
        )

def guard_solver_state(
    *,
    step: int,
    omega: np.ndarray,
    energy: float | None = None,
    cfl: float | None = None,
    cfl_limit: float = 1.0,
) -> None:
    """General guard to check solver health at any given step."""
    assert_finite("omega", omega, step)

    if energy is not None and not np.isfinite(energy):
        raise FloatingPointError(f"Energy is non-finite at step={step}")

    if cfl is not None:
        if not np.isfinite(cfl) or cfl > cfl_limit:
            raise FloatingPointError(
                f"CFL limit exceeded or non-finite at step={step}: cfl={cfl}"
            )