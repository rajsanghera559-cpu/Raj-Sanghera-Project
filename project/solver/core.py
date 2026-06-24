# Core solver interface (stable API layer)
# This does NOT implement physics.
# It only routes calls to the legacy solver.

from .legacy_solver import run_simulation


def run(u0, dt, steps, **kwargs):
    """
    Stable public API for all experiments.

    Future rule:
    - experiments ONLY call this function
    - never call legacy_solver directly
    """
    return run_simulation(u0, dt, steps, **kwargs)