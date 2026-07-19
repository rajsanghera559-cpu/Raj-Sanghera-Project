"""
Standalone forcing-budget diagnostics for periodic 2-D vorticity fields.

This module does not import or modify the project solver and performs no
time stepping.

Project sign convention
-----------------------
    Laplacian(psi) = omega
    u = d(psi)/dy
    v = -d(psi)/dx

Continuous quantities
---------------------
    E = 0.5 * <u^2 + v^2>
    Z = 0.5 * <omega^2>

    energy forcing rate:
        epsilon_f = -<psi * f_omega>

    enstrophy forcing rate:
        eta_f = <omega * f_omega>

    viscous energy dissipation:
        D_E = nu * <omega^2>

    viscous enstrophy dissipation:
        D_Z = nu * <|grad omega|^2>

Angle brackets denote the periodic spatial mean.

The continuous forcing-plus-viscosity right-hand sides do not automatically
include discrete advection error, filtering error, or time-integration error.
Those effects can be estimated later through interval residuals.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping

import numpy as np


def _real_finite_array(name: str, value: object) -> np.ndarray:
    array = np.asarray(value)

    if array.ndim != 2:
        raise ValueError(f"{name} must be a two-dimensional array")

    if not np.isrealobj(array):
        raise ValueError(f"{name} must be real-valued")

    result = np.asarray(array, dtype=np.float64)

    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite values")

    return result


def _finite_scalar(name: str, value: object) -> float:
    result = float(value)

    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")

    return result


def forcing_budget_snapshot(
    *,
    omega: object,
    forcing: object,
    nu: float,
    kx: object,
    ky: object,
    dt: float,
    loop_index: int,
) -> dict[str, float | int]:
    """
    Calculate one instantaneous forcing-budget snapshot.

    The loop-index convention follows the existing solver:

        loop_index = -1  -> initial state, zero completed steps
        loop_index = 0   -> state after one completed update
        loop_index = n   -> state after n + 1 completed updates
    """
    omega_array = _real_finite_array("omega", omega)
    forcing_array = _real_finite_array("forcing", forcing)
    kx_array = _real_finite_array("kx", kx)
    ky_array = _real_finite_array("ky", ky)

    expected_shape = omega_array.shape

    for name, array in (
        ("forcing", forcing_array),
        ("kx", kx_array),
        ("ky", ky_array),
    ):
        if array.shape != expected_shape:
            raise ValueError(
                f"{name} shape {array.shape} does not match "
                f"omega shape {expected_shape}"
            )

    nu_value = _finite_scalar("nu", nu)
    dt_value = _finite_scalar("dt", dt)

    if nu_value < 0.0:
        raise ValueError("nu must be nonnegative")

    if dt_value <= 0.0:
        raise ValueError("dt must be positive")

    if (
        not isinstance(loop_index, (int, np.integer))
        or isinstance(loop_index, bool)
        or int(loop_index) < -1
    ):
        raise ValueError("loop_index must be an integer greater than or equal to -1")

    loop_index_value = int(loop_index)
    completed_steps = loop_index_value + 1
    physical_time = completed_steps * dt_value

    omega_hat = np.fft.fft2(omega_array)

    k_squared = kx_array * kx_array + ky_array * ky_array
    safe_k_squared = np.where(k_squared == 0.0, 1.0, k_squared)

    psi_hat = -omega_hat / safe_k_squared
    psi_hat[0, 0] = 0.0

    psi = np.fft.ifft2(psi_hat).real

    u = np.fft.ifft2(1j * ky_array * psi_hat).real
    v = np.fft.ifft2(-1j * kx_array * psi_hat).real

    omega_x = np.fft.ifft2(1j * kx_array * omega_hat).real
    omega_y = np.fft.ifft2(1j * ky_array * omega_hat).real

    energy = 0.5 * float(np.mean(u * u + v * v))
    enstrophy = 0.5 * float(np.mean(omega_array * omega_array))

    forcing_rms = float(np.sqrt(np.mean(forcing_array * forcing_array)))

    energy_injection_rate = -float(np.mean(psi * forcing_array))
    enstrophy_injection_rate = float(
        np.mean(omega_array * forcing_array)
    )

    viscous_energy_dissipation_rate = nu_value * float(
        np.mean(omega_array * omega_array)
    )

    viscous_enstrophy_dissipation_rate = nu_value * float(
        np.mean(omega_x * omega_x + omega_y * omega_y)
    )

    continuous_energy_rhs = (
        energy_injection_rate
        - viscous_energy_dissipation_rate
    )

    continuous_enstrophy_rhs = (
        enstrophy_injection_rate
        - viscous_enstrophy_dissipation_rate
    )

    result: dict[str, float | int] = {
        "loop_index": loop_index_value,
        "completed_steps": completed_steps,
        "physical_time": physical_time,
        "energy": energy,
        "enstrophy": enstrophy,
        "forcing_rms": forcing_rms,
        "energy_injection_rate": energy_injection_rate,
        "enstrophy_injection_rate": enstrophy_injection_rate,
        "viscous_energy_dissipation_rate": (
            viscous_energy_dissipation_rate
        ),
        "viscous_enstrophy_dissipation_rate": (
            viscous_enstrophy_dissipation_rate
        ),
        "continuous_energy_rhs": continuous_energy_rhs,
        "continuous_enstrophy_rhs": continuous_enstrophy_rhs,
    }

    if not all(
        math.isfinite(float(value))
        for value in result.values()
    ):
        raise RuntimeError("forcing-budget snapshot contains a nonfinite value")

    return result


def forcing_budget_interval(
    previous: Mapping[str, float | int],
    current: Mapping[str, float | int],
) -> dict[str, float]:
    """
    Compare two snapshots and calculate observed budget residuals.

    A nonzero residual can contain discrete-advection effects, filtering,
    time-integration error, or insufficient temporal sampling.
    """
    required = (
        "physical_time",
        "energy",
        "enstrophy",
        "continuous_energy_rhs",
        "continuous_enstrophy_rhs",
    )

    for name in required:
        if name not in previous:
            raise KeyError(f"previous snapshot is missing {name!r}")

        if name not in current:
            raise KeyError(f"current snapshot is missing {name!r}")

    previous_time = _finite_scalar(
        "previous physical_time",
        previous["physical_time"],
    )

    current_time = _finite_scalar(
        "current physical_time",
        current["physical_time"],
    )

    interval = current_time - previous_time

    if interval <= 0.0:
        raise ValueError("current physical_time must exceed previous physical_time")

    observed_energy_rate = (
        _finite_scalar("current energy", current["energy"])
        - _finite_scalar("previous energy", previous["energy"])
    ) / interval

    observed_enstrophy_rate = (
        _finite_scalar("current enstrophy", current["enstrophy"])
        - _finite_scalar("previous enstrophy", previous["enstrophy"])
    ) / interval

    mean_continuous_energy_rhs = 0.5 * (
        _finite_scalar(
            "previous continuous_energy_rhs",
            previous["continuous_energy_rhs"],
        )
        + _finite_scalar(
            "current continuous_energy_rhs",
            current["continuous_energy_rhs"],
        )
    )

    mean_continuous_enstrophy_rhs = 0.5 * (
        _finite_scalar(
            "previous continuous_enstrophy_rhs",
            previous["continuous_enstrophy_rhs"],
        )
        + _finite_scalar(
            "current continuous_enstrophy_rhs",
            current["continuous_enstrophy_rhs"],
        )
    )

    return {
        "interval_duration": interval,
        "observed_energy_rate": observed_energy_rate,
        "mean_continuous_energy_rhs": mean_continuous_energy_rhs,
        "energy_budget_residual": (
            observed_energy_rate
            - mean_continuous_energy_rhs
        ),
        "observed_enstrophy_rate": observed_enstrophy_rate,
        "mean_continuous_enstrophy_rhs": (
            mean_continuous_enstrophy_rhs
        ),
        "enstrophy_budget_residual": (
            observed_enstrophy_rate
            - mean_continuous_enstrophy_rhs
        ),
    }


def _self_test() -> None:
    """
    Verify the formulas against the analytic default single-mode solution.
    """
    size = 64
    length = 2.0 * np.pi
    dx = length / size

    coordinates = np.linspace(
        0.0,
        length,
        size,
        endpoint=False,
    )

    x, y = np.meshgrid(coordinates, coordinates)

    wave_numbers = np.fft.fftfreq(size, d=dx) * 2.0 * np.pi
    kx, ky = np.meshgrid(wave_numbers, wave_numbers)

    nu = 0.001
    dt = 0.005
    loop_index = 9500
    physical_time = (loop_index + 1) * dt

    forcing_amplitude = 0.01
    eigenvalue = 8.0

    mode = np.sin(2.0 * x) * np.cos(2.0 * y)

    amplitude = (
        forcing_amplitude
        / (eigenvalue * nu)
        * (
            1.0
            - np.exp(-eigenvalue * nu * physical_time)
        )
    )

    omega = amplitude * mode
    forcing = forcing_amplitude * mode

    observed = forcing_budget_snapshot(
        omega=omega,
        forcing=forcing,
        nu=nu,
        kx=kx,
        ky=ky,
        dt=dt,
        loop_index=loop_index,
    )

    expected = {
        "completed_steps": 9501,
        "physical_time": 47.505,
        "energy": amplitude * amplitude / 64.0,
        "enstrophy": amplitude * amplitude / 8.0,
        "forcing_rms": 0.005,
        "energy_injection_rate": (
            amplitude * forcing_amplitude / 32.0
        ),
        "enstrophy_injection_rate": (
            amplitude * forcing_amplitude / 4.0
        ),
        "viscous_energy_dissipation_rate": (
            nu * amplitude * amplitude / 4.0
        ),
        "viscous_enstrophy_dissipation_rate": (
            2.0 * nu * amplitude * amplitude
        ),
    }

    failures: list[str] = []

    for name, expected_value in expected.items():
        observed_value = observed[name]

        if not np.isclose(
            float(observed_value),
            float(expected_value),
            rtol=1.0e-12,
            atol=1.0e-14,
        ):
            failures.append(
                f"{name}: observed={observed_value!r}, "
                f"expected={expected_value!r}"
            )

    if failures:
        raise SystemExit(
            "FORCING BUDGET DIAGNOSTIC SELF-TEST: FAIL\n"
            + "\n".join(failures)
        )

    print("FORCING BUDGET DIAGNOSTIC SELF-TEST: PASS")
    print("Solver imported: NO")
    print("Solver executed: NO")
    print("Files written by self-test: NO")
    print(json.dumps(observed, indent=2, sort_keys=True))


if __name__ == "__main__":
    _self_test()
