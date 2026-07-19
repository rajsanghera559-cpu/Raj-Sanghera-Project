"""
Controlled longer RMS-matched multimode forcing-budget stationarity test.

Usage:
    python -B run_forcing_budget_stationarity_test.py inspect
    python -B run_forcing_budget_stationarity_test.py run

The inspection path parses this file and verifies the frozen design and source
identities without importing project modules, constructing a solver, writing
files, or executing numerical steps.

The run path implements the design archived at commit 3af047b. It mirrors the
protected solver's RK2 update externally, never calls the protected solver run
loop, and writes an immutable, Git-ignored evidence bundle.

This is a stationarity-screening calculation only. It does not authorize or
establish convergence, physical validation, turbulence, a cascade, an inertial
range, a k^-3 law, method superiority, or production readiness.
"""

from __future__ import annotations

import argparse
import ast
import csv
import datetime
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np


# ============================================================================
# Frozen design identity
# ============================================================================

RUNNER_NAME = "run_forcing_budget_stationarity_test.py"

DESIGN_PATH = Path("FORCING_BUDGET_LONGER_STATIONARITY_TEST_DESIGN.md")

AUTHORIZED_DESIGN_COMMIT = (
    "3af047b12429bb75f2b4d8eb4d9437cdca4c3a82"
)

EXPECTED_DESIGN_SHA256 = (
    "91C0ACFDF526CF5C86309ACCB5033892644A36326DA3D3D7F4A01DA6565A46C6"
)

EXPECTED_SOLVER_SHA256 = (
    "1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1"
)

EXPECTED_BUDGET_SHA256 = (
    "A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B"
)


# ============================================================================
# Frozen numerical configuration
# ============================================================================

N = 64
RE = 1000
NU = 1.0 / RE
DT = 0.005
STEPS = 20001
FINAL_PHYSICAL_TIME = 100.005

BUDGET_OUTPUT_INTERVAL = 100
SPECTRUM_OUTPUT_INTERVAL = 500

EXPECTED_BUDGET_SNAPSHOTS = 201
EXPECTED_SPECTRUM_SNAPSHOTS = 41

EXPECTED_FORCING_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14

STATIONARITY_START_TIME = 80.005
STATIONARITY_END_TIME = 100.005
STATIONARITY_DURATION = 20.0
EXPECTED_STATIONARITY_SNAPSHOTS = 41

RESIDUAL_DENOMINATOR_FLOOR = 1.0e-30
ENERGY_SPECTRUM_CONSISTENCY_TOLERANCE = 1.0e-8

ENERGY_DRIFT_LIMIT = 0.05
ENSTROPHY_DRIFT_LIMIT = 0.05
ENERGY_BALANCE_LIMIT = 0.10
ENSTROPHY_BALANCE_LIMIT = 0.10
SUBWINDOW_DEVIATION_LIMIT = 0.10

MEDIAN_NORMALIZED_ENERGY_RESIDUAL_LIMIT = 0.01
MAX_NORMALIZED_ENERGY_RESIDUAL_LIMIT = 0.05
MEDIAN_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT = 0.01
MAX_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT = 0.05

OUTPUT_ROOT = Path("experiments") / "forcing_budget_stationarity"
RUN_PREFIX = "forcing_budget_stationarity_"

FORCING_TERMS = (
    "sin(2X)cos(2Y)",
    "0.75*sin(3X)cos(Y)",
    "0.50*sin(X)cos(4Y)",
    "0.35*cos(4X-2Y)",
)

SUBWINDOWS = (
    {
        "id": 1,
        "lower": 80.005,
        "upper": 85.005,
        "lower_inclusive": True,
        "upper_inclusive": True,
    },
    {
        "id": 2,
        "lower": 85.005,
        "upper": 90.005,
        "lower_inclusive": False,
        "upper_inclusive": True,
    },
    {
        "id": 3,
        "lower": 90.005,
        "upper": 95.005,
        "lower_inclusive": False,
        "upper_inclusive": True,
    },
    {
        "id": 4,
        "lower": 95.005,
        "upper": 100.005,
        "lower_inclusive": False,
        "upper_inclusive": True,
    },
)

CLASSIFICATION_STATIONARITY_CANDIDATE = "STATIONARITY CANDIDATE"
CLASSIFICATION_NOT_STATIONARY = "NOT STATIONARY WITHIN TESTED DURATION"
CLASSIFICATION_INCOMPLETE = "INCOMPLETE"
CLASSIFICATION_NUMERICAL_FAILURE = "NUMERICAL FAILURE"


# ============================================================================
# Output schemas
# ============================================================================

BUDGET_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "energy",
    "enstrophy",
    "forcing_rms",
    "energy_injection_rate",
    "enstrophy_injection_rate",
    "viscous_energy_dissipation_rate",
    "viscous_enstrophy_dissipation_rate",
    "continuous_energy_rhs",
    "continuous_enstrophy_rhs",
    "stage1_advection_rms",
    "stage2_advection_rms",
    "mask_removal_rms",
    "vorticity_rms",
    "maximum_absolute_vorticity",
    "forcing_sha256",
    "forcing_identity_matches",
    "interval_duration",
    "observed_energy_rate",
    "mean_continuous_energy_rhs",
    "energy_budget_residual",
    "mean_energy_injection_rate",
    "mean_viscous_energy_dissipation_rate",
    "normalized_energy_budget_residual",
    "observed_enstrophy_rate",
    "mean_continuous_enstrophy_rhs",
    "enstrophy_budget_residual",
    "mean_enstrophy_injection_rate",
    "mean_viscous_enstrophy_dissipation_rate",
    "normalized_enstrophy_budget_residual",
)

SPECTRUM_FIELDNAMES = (
    "loop_index",
    "completed_steps",
    "physical_time",
    "k",
    "energy",
    "mode_count",
    "direct_energy",
    "spectrum_energy_sum",
    "relative_energy_consistency_error",
    "dominant_shell",
    "dominant_shell_energy",
    "k1_energy",
    "k2_energy",
    "k3_energy",
    "k4_energy",
    "low_k_fraction_k_le_4",
    "middle_k_fraction_5_le_k_le_9",
    "high_k_fraction_k_ge_10",
    "tail_fraction_k_gt_4",
    "finite_shell_count",
    "nonzero_shell_count",
    "minimum_spectral_value",
    "maximum_spectral_value",
)

WINDOW_EXTRA_FIELDNAMES = (
    "stationarity_window_member",
    "subwindow_id",
    "residual_interval_fully_inside_window",
)

WINDOW_FIELDNAMES = BUDGET_FIELDNAMES + WINDOW_EXTRA_FIELDNAMES

INVENTORY_FIELDNAMES = (
    "relative_path",
    "bytes",
    "sha256",
    "inventory_note",
)


# ============================================================================
# Generic utilities
# ============================================================================

def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def utc_text(value: datetime.datetime | None = None) -> str:
    moment = utc_now() if value is None else value
    return moment.replace(microsecond=0).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def sha256_array(value: object) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    return sha256_bytes(array.tobytes(order="C"))


def git_process(
    repo: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        shell=False,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )


def git_read(repo: Path, *args: str) -> str:
    return git_process(repo, *args).stdout.strip()


def path_is_git_ignored(repo: Path, path: Path) -> bool:
    relative = path.relative_to(repo).as_posix()
    result = git_process(
        repo,
        "check-ignore",
        "-q",
        "--no-index",
        "--",
        relative,
        check=False,
    )
    return result.returncode == 0


def atomic_write_text(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")

    try:
        with temporary.open(
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())

        temporary.replace(path)

    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_json(path: Path, value: object) -> None:
    text = json.dumps(
        value,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )
    atomic_write_text(path, text + "\n")


def atomic_write_csv(
    path: Path,
    rows: Sequence[Mapping[str, object]],
    fieldnames: Sequence[str],
) -> None:
    temporary = path.with_name(path.name + ".tmp")

    try:
        with temporary.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=list(fieldnames),
                extrasaction="raise",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())

        temporary.replace(path)

    finally:
        if temporary.exists():
            temporary.unlink()


def finite_float(name: str, value: object) -> float:
    result = float(value)

    if not math.isfinite(result):
        raise RuntimeError(f"{name} is not finite: {value!r}")

    return result


def all_numeric_values_finite(rows: Iterable[Mapping[str, object]]) -> bool:
    for row in rows:
        for value in row.values():
            if value is None:
                continue

            if isinstance(
                value,
                (int, float, np.integer, np.floating),
            ):
                if not math.isfinite(float(value)):
                    return False

    return True


def safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0.0:
        return None

    return numerator / denominator


# ============================================================================
# Frozen forcing and external RK2 mirror
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

    raw = raw - np.mean(raw)

    base_rms = float(np.sqrt(np.mean(base * base)))
    raw_rms = float(np.sqrt(np.mean(raw * raw)))

    if raw_rms == 0.0:
        raise RuntimeError("raw multimode forcing has zero RMS")

    normalization_coefficient = base_rms / raw_rms

    forcing = np.ascontiguousarray(
        raw * normalization_coefficient,
        dtype=np.float64,
    )

    matched_rms = float(np.sqrt(np.mean(forcing * forcing)))
    mean_value = float(np.mean(forcing))
    max_abs = float(np.max(np.abs(forcing)))

    if forcing.shape != (N, N):
        raise RuntimeError(
            f"forcing shape is {forcing.shape}, expected {(N, N)}"
        )

    if not np.isrealobj(forcing):
        raise RuntimeError("multimode forcing is not real-valued")

    if not np.isfinite(forcing).all():
        raise RuntimeError("multimode forcing contains a nonfinite value")

    if abs(matched_rms - EXPECTED_FORCING_RMS) > FORCING_RMS_TOLERANCE:
        raise RuntimeError(
            f"unexpected matched forcing RMS: {matched_rms}"
        )

    forcing_hash = sha256_array(forcing)

    forcing.setflags(write=False)

    return forcing, {
        "forcing_terms": FORCING_TERMS,
        "normalization_coefficient": normalization_coefficient,
        "base_single_mode_rms": base_rms,
        "raw_multimode_rms": raw_rms,
        "normalized_multimode_rms": matched_rms,
        "forcing_mean": mean_value,
        "forcing_max_abs": max_abs,
        "forcing_sha256": forcing_hash,
        "forcing_array_shape": list(forcing.shape),
        "forcing_array_dtype": str(forcing.dtype),
        "forcing_is_finite": bool(np.isfinite(forcing).all()),
        "forcing_is_real": bool(np.isrealobj(forcing)),
        "forcing_is_writeable": bool(forcing.flags.writeable),
    }


def external_rk2_step(
    solver: object,
    forcing: np.ndarray,
) -> dict[str, float]:
    current = np.asarray(solver.w)

    if not np.isfinite(current).all():
        raise RuntimeError("current vorticity contains a nonfinite value")

    psi = solver.streamfunction(current)
    u, v = solver.velocity(psi)

    omega_x = (
        np.roll(current, -1, 1)
        - np.roll(current, 1, 1)
    ) / (2.0 * solver.dx)

    omega_y = (
        np.roll(current, -1, 0)
        - np.roll(current, 1, 0)
    ) / (2.0 * solver.dx)

    advection_1 = u * omega_x + v * omega_y

    k1 = (
        -advection_1
        + solver.laplacian_spectral(current)
        + forcing
    )

    stage = current + solver.dt * k1

    if not np.isfinite(stage).all():
        raise RuntimeError("RK2 stage field contains a nonfinite value")

    psi_stage = solver.streamfunction(stage)
    u_stage, v_stage = solver.velocity(psi_stage)

    omega_x_stage = (
        np.roll(stage, -1, 1)
        - np.roll(stage, 1, 1)
    ) / (2.0 * solver.dx)

    omega_y_stage = (
        np.roll(stage, -1, 0)
        - np.roll(stage, 1, 0)
    ) / (2.0 * solver.dx)

    advection_2 = (
        u_stage * omega_x_stage
        + v_stage * omega_y_stage
    )

    k2 = (
        -advection_2
        + solver.laplacian_spectral(stage)
        + forcing
    )

    unfiltered = current + 0.5 * solver.dt * (k1 + k2)

    transformed = np.fft.fft2(unfiltered)
    transformed *= solver.deal
    filtered = np.fft.ifft2(transformed).real

    if not np.isfinite(filtered).all():
        raise RuntimeError("RK2 update produced a nonfinite field")

    solver.w = filtered

    return {
        "stage1_advection_rms": float(
            np.sqrt(np.mean(advection_1 * advection_1))
        ),
        "stage2_advection_rms": float(
            np.sqrt(np.mean(advection_2 * advection_2))
        ),
        "mask_removal_rms": float(
            np.sqrt(np.mean((unfiltered - filtered) ** 2))
        ),
        "vorticity_rms": float(
            np.sqrt(np.mean(filtered * filtered))
        ),
        "maximum_absolute_vorticity": float(
            np.max(np.abs(filtered))
        ),
    }


# ============================================================================
# Spectrum and stationarity calculations
# ============================================================================

def spectrum_snapshot(
    solver: object,
    omega: np.ndarray,
    *,
    loop_index: int,
    direct_energy: float,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    k_bins, energy_spectrum, mode_counts = solver.energy_spectrum(omega)

    k_bins = np.asarray(k_bins)
    energy_spectrum = np.asarray(energy_spectrum, dtype=np.float64)
    mode_counts = np.asarray(mode_counts)

    if not (
        k_bins.ndim == 1
        and energy_spectrum.ndim == 1
        and mode_counts.ndim == 1
        and len(k_bins) == len(energy_spectrum) == len(mode_counts)
    ):
        raise RuntimeError("unexpected energy-spectrum shape")

    if len(energy_spectrum) == 0:
        raise RuntimeError("empty energy spectrum")

    if not np.isfinite(k_bins).all():
        raise RuntimeError("nonfinite radial shell index")

    if not np.isfinite(energy_spectrum).all():
        raise RuntimeError("nonfinite energy spectrum")

    if not np.isfinite(mode_counts).all():
        raise RuntimeError("nonfinite spectrum mode count")

    total = float(np.sum(energy_spectrum))

    if total <= 0.0:
        raise RuntimeError("nonpositive spectrum energy sum")

    direct = finite_float("direct kinetic energy", direct_energy)

    consistency_error = abs(total - direct) / max(
        abs(direct),
        RESIDUAL_DENOMINATOR_FLOOR,
    )

    if consistency_error > ENERGY_SPECTRUM_CONSISTENCY_TOLERANCE:
        raise RuntimeError(
            "direct and spectral kinetic energy disagree: "
            f"relative error {consistency_error:.12e}"
        )

    dominant_index = int(np.argmax(energy_spectrum))
    dominant_shell = int(k_bins[dominant_index])

    shell_map = {
        int(k): float(value)
        for k, value in zip(k_bins, energy_spectrum)
    }

    low_k_energy = sum(
        value
        for k, value in shell_map.items()
        if k <= 4
    )

    middle_k_energy = sum(
        value
        for k, value in shell_map.items()
        if 5 <= k <= 9
    )

    high_k_energy = sum(
        value
        for k, value in shell_map.items()
        if k >= 10
    )

    tail_energy = sum(
        value
        for k, value in shell_map.items()
        if k > 4
    )

    completed_steps = loop_index + 1
    physical_time = completed_steps * DT

    summary: dict[str, object] = {
        "loop_index": loop_index,
        "completed_steps": completed_steps,
        "physical_time": physical_time,
        "direct_energy": direct,
        "spectrum_energy_sum": total,
        "relative_energy_consistency_error": consistency_error,
        "dominant_shell": dominant_shell,
        "dominant_shell_energy": shell_map[dominant_shell],
        "k1_energy": shell_map.get(1, 0.0),
        "k2_energy": shell_map.get(2, 0.0),
        "k3_energy": shell_map.get(3, 0.0),
        "k4_energy": shell_map.get(4, 0.0),
        "low_k_fraction_k_le_4": low_k_energy / total,
        "middle_k_fraction_5_le_k_le_9": middle_k_energy / total,
        "high_k_fraction_k_ge_10": high_k_energy / total,
        "tail_fraction_k_gt_4": tail_energy / total,
        "finite_shell_count": int(np.isfinite(energy_spectrum).sum()),
        "nonzero_shell_count": int((energy_spectrum > 0.0).sum()),
        "minimum_spectral_value": float(np.min(energy_spectrum)),
        "maximum_spectral_value": float(np.max(energy_spectrum)),
    }

    rows: list[dict[str, object]] = []

    for k, value, count in zip(
        k_bins,
        energy_spectrum,
        mode_counts,
    ):
        rows.append(
            {
                "loop_index": loop_index,
                "completed_steps": completed_steps,
                "physical_time": physical_time,
                "k": int(k),
                "energy": float(value),
                "mode_count": int(count),
                **{
                    key: summary[key]
                    for key in SPECTRUM_FIELDNAMES
                    if key not in {
                        "loop_index",
                        "completed_steps",
                        "physical_time",
                        "k",
                        "energy",
                        "mode_count",
                    }
                },
            }
        )

    if not all_numeric_values_finite(rows):
        raise RuntimeError("spectrum table contains a nonfinite numeric value")

    return rows, summary


def interval_with_normalized_residuals(
    previous_snapshot: Mapping[str, float | int],
    current_snapshot: Mapping[str, float | int],
    forcing_budget_interval: object,
) -> dict[str, float]:
    interval = forcing_budget_interval(
        previous_snapshot,
        current_snapshot,
    )

    mean_energy_injection = 0.5 * (
        float(previous_snapshot["energy_injection_rate"])
        + float(current_snapshot["energy_injection_rate"])
    )

    mean_energy_dissipation = 0.5 * (
        float(previous_snapshot["viscous_energy_dissipation_rate"])
        + float(current_snapshot["viscous_energy_dissipation_rate"])
    )

    mean_enstrophy_injection = 0.5 * (
        float(previous_snapshot["enstrophy_injection_rate"])
        + float(current_snapshot["enstrophy_injection_rate"])
    )

    mean_enstrophy_dissipation = 0.5 * (
        float(previous_snapshot["viscous_enstrophy_dissipation_rate"])
        + float(current_snapshot["viscous_enstrophy_dissipation_rate"])
    )

    normalized_energy_residual = (
        abs(float(interval["energy_budget_residual"]))
        / max(
            abs(mean_energy_injection),
            abs(mean_energy_dissipation),
            RESIDUAL_DENOMINATOR_FLOOR,
        )
    )

    normalized_enstrophy_residual = (
        abs(float(interval["enstrophy_budget_residual"]))
        / max(
            abs(mean_enstrophy_injection),
            abs(mean_enstrophy_dissipation),
            RESIDUAL_DENOMINATOR_FLOOR,
        )
    )

    result = {
        **interval,
        "mean_energy_injection_rate": mean_energy_injection,
        "mean_viscous_energy_dissipation_rate": (
            mean_energy_dissipation
        ),
        "normalized_energy_budget_residual": (
            normalized_energy_residual
        ),
        "mean_enstrophy_injection_rate": mean_enstrophy_injection,
        "mean_viscous_enstrophy_dissipation_rate": (
            mean_enstrophy_dissipation
        ),
        "normalized_enstrophy_budget_residual": (
            normalized_enstrophy_residual
        ),
    }

    if not all(math.isfinite(float(value)) for value in result.values()):
        raise RuntimeError("interval diagnostics contain a nonfinite value")

    return result


def ordinary_least_squares_slope(
    times: Sequence[float],
    values: Sequence[float],
) -> float:
    x = np.asarray(times, dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)

    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y):
        raise ValueError("OLS inputs must be equal-length vectors")

    if len(x) < 2:
        raise ValueError("OLS requires at least two observations")

    centered_x = x - np.mean(x)
    denominator = float(np.dot(centered_x, centered_x))

    if denominator == 0.0:
        raise ValueError("OLS time denominator is zero")

    centered_y = y - np.mean(y)
    slope = float(np.dot(centered_x, centered_y) / denominator)

    if not math.isfinite(slope):
        raise RuntimeError("OLS slope is not finite")

    return slope


def normalized_window_drift(
    times: Sequence[float],
    values: Sequence[float],
) -> dict[str, float]:
    slope = ordinary_least_squares_slope(times, values)
    mean_value = float(np.mean(np.asarray(values, dtype=np.float64)))

    normalized_drift = (
        abs(slope) * STATIONARITY_DURATION
        / max(
            abs(mean_value),
            RESIDUAL_DENOMINATOR_FLOOR,
        )
    )

    return {
        "slope": slope,
        "window_mean": mean_value,
        "normalized_window_drift": normalized_drift,
    }


def time_in_subwindow(value: float, definition: Mapping[str, object]) -> bool:
    lower = float(definition["lower"])
    upper = float(definition["upper"])
    tolerance = 1.0e-12

    lower_ok = (
        value >= lower - tolerance
        if bool(definition["lower_inclusive"])
        else value > lower + tolerance
    )

    upper_ok = (
        value <= upper + tolerance
        if bool(definition["upper_inclusive"])
        else value < upper - tolerance
    )

    return lower_ok and upper_ok


def subwindow_id_for_time(value: float) -> int:
    for definition in SUBWINDOWS:
        if time_in_subwindow(value, definition):
            return int(definition["id"])

    raise RuntimeError(
        f"time {value!r} is not in a frozen stationarity subwindow"
    )


def summarize_stationarity_window(
    window_rows: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    if len(window_rows) != EXPECTED_STATIONARITY_SNAPSHOTS:
        raise RuntimeError(
            "stationarity window has "
            f"{len(window_rows)} snapshots, "
            f"expected {EXPECTED_STATIONARITY_SNAPSHOTS}"
        )

    times = [float(row["physical_time"]) for row in window_rows]

    if not math.isclose(
        times[0],
        STATIONARITY_START_TIME,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise RuntimeError(
            f"stationarity window starts at {times[0]!r}"
        )

    if not math.isclose(
        times[-1],
        STATIONARITY_END_TIME,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise RuntimeError(
            f"stationarity window ends at {times[-1]!r}"
        )

    quantity_fields = (
        "energy",
        "enstrophy",
        "energy_injection_rate",
        "enstrophy_injection_rate",
        "viscous_energy_dissipation_rate",
        "viscous_enstrophy_dissipation_rate",
    )

    trends: dict[str, dict[str, float]] = {}

    for field in quantity_fields:
        values = [float(row[field]) for row in window_rows]
        trends[field] = normalized_window_drift(times, values)

    means = {
        field: float(
            np.mean(
                np.asarray(
                    [float(row[field]) for row in window_rows],
                    dtype=np.float64,
                )
            )
        )
        for field in quantity_fields
    }

    energy_balance = (
        abs(
            means["energy_injection_rate"]
            - means["viscous_energy_dissipation_rate"]
        )
        / max(
            abs(means["energy_injection_rate"]),
            abs(means["viscous_energy_dissipation_rate"]),
            RESIDUAL_DENOMINATOR_FLOOR,
        )
    )

    enstrophy_balance = (
        abs(
            means["enstrophy_injection_rate"]
            - means["viscous_enstrophy_dissipation_rate"]
        )
        / max(
            abs(means["enstrophy_injection_rate"]),
            abs(means["viscous_enstrophy_dissipation_rate"]),
            RESIDUAL_DENOMINATOR_FLOOR,
        )
    )

    subwindow_metrics: list[dict[str, object]] = []

    for definition in SUBWINDOWS:
        selected = [
            row
            for row in window_rows
            if time_in_subwindow(
                float(row["physical_time"]),
                definition,
            )
        ]

        if not selected:
            raise RuntimeError(
                f"subwindow {definition['id']} is empty"
            )

        energy_mean = float(
            np.mean(
                np.asarray(
                    [float(row["energy"]) for row in selected],
                    dtype=np.float64,
                )
            )
        )

        enstrophy_mean = float(
            np.mean(
                np.asarray(
                    [float(row["enstrophy"]) for row in selected],
                    dtype=np.float64,
                )
            )
        )

        energy_deviation = (
            abs(energy_mean - means["energy"])
            / max(
                abs(means["energy"]),
                RESIDUAL_DENOMINATOR_FLOOR,
            )
        )

        enstrophy_deviation = (
            abs(enstrophy_mean - means["enstrophy"])
            / max(
                abs(means["enstrophy"]),
                RESIDUAL_DENOMINATOR_FLOOR,
            )
        )

        subwindow_metrics.append(
            {
                "subwindow_id": int(definition["id"]),
                "lower": float(definition["lower"]),
                "upper": float(definition["upper"]),
                "lower_inclusive": bool(
                    definition["lower_inclusive"]
                ),
                "upper_inclusive": bool(
                    definition["upper_inclusive"]
                ),
                "snapshot_count": len(selected),
                "energy_mean": energy_mean,
                "energy_deviation_from_full_window_mean": (
                    energy_deviation
                ),
                "energy_deviation_pass": (
                    energy_deviation <= SUBWINDOW_DEVIATION_LIMIT
                ),
                "enstrophy_mean": enstrophy_mean,
                "enstrophy_deviation_from_full_window_mean": (
                    enstrophy_deviation
                ),
                "enstrophy_deviation_pass": (
                    enstrophy_deviation
                    <= SUBWINDOW_DEVIATION_LIMIT
                ),
            }
        )

    residual_rows = list(window_rows[1:])

    if len(residual_rows) != EXPECTED_STATIONARITY_SNAPSHOTS - 1:
        raise RuntimeError("unexpected stationarity residual count")

    energy_residuals = np.asarray(
        [
            float(row["normalized_energy_budget_residual"])
            for row in residual_rows
        ],
        dtype=np.float64,
    )

    enstrophy_residuals = np.asarray(
        [
            float(row["normalized_enstrophy_budget_residual"])
            for row in residual_rows
        ],
        dtype=np.float64,
    )

    if not np.isfinite(energy_residuals).all():
        raise RuntimeError("nonfinite normalized energy residual")

    if not np.isfinite(enstrophy_residuals).all():
        raise RuntimeError("nonfinite normalized enstrophy residual")

    residual_metrics = {
        "interval_count": len(residual_rows),
        "median_normalized_energy_residual": float(
            np.median(energy_residuals)
        ),
        "maximum_normalized_energy_residual": float(
            np.max(energy_residuals)
        ),
        "median_normalized_enstrophy_residual": float(
            np.median(enstrophy_residuals)
        ),
        "maximum_normalized_enstrophy_residual": float(
            np.max(enstrophy_residuals)
        ),
    }

    criteria = {
        "full_run_reached_t_100_005": True,
        "numerical_integrity_gates_passed": True,
        "energy_normalized_drift_pass": (
            trends["energy"]["normalized_window_drift"]
            <= ENERGY_DRIFT_LIMIT
        ),
        "enstrophy_normalized_drift_pass": (
            trends["enstrophy"]["normalized_window_drift"]
            <= ENSTROPHY_DRIFT_LIMIT
        ),
        "energy_injection_dissipation_balance_pass": (
            energy_balance <= ENERGY_BALANCE_LIMIT
        ),
        "enstrophy_injection_dissipation_balance_pass": (
            enstrophy_balance <= ENSTROPHY_BALANCE_LIMIT
        ),
        "all_energy_subwindow_deviations_pass": all(
            bool(item["energy_deviation_pass"])
            for item in subwindow_metrics
        ),
        "all_enstrophy_subwindow_deviations_pass": all(
            bool(item["enstrophy_deviation_pass"])
            for item in subwindow_metrics
        ),
        "median_normalized_energy_residual_pass": (
            residual_metrics[
                "median_normalized_energy_residual"
            ]
            <= MEDIAN_NORMALIZED_ENERGY_RESIDUAL_LIMIT
        ),
        "maximum_normalized_energy_residual_pass": (
            residual_metrics[
                "maximum_normalized_energy_residual"
            ]
            <= MAX_NORMALIZED_ENERGY_RESIDUAL_LIMIT
        ),
        "median_normalized_enstrophy_residual_pass": (
            residual_metrics[
                "median_normalized_enstrophy_residual"
            ]
            <= MEDIAN_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
        ),
        "maximum_normalized_enstrophy_residual_pass": (
            residual_metrics[
                "maximum_normalized_enstrophy_residual"
            ]
            <= MAX_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
        ),
    }

    classification = (
        CLASSIFICATION_STATIONARITY_CANDIDATE
        if all(criteria.values())
        else CLASSIFICATION_NOT_STATIONARY
    )

    annotated_rows: list[dict[str, object]] = []

    for index, row in enumerate(window_rows):
        time_value = float(row["physical_time"])

        annotated_rows.append(
            {
                **row,
                "stationarity_window_member": True,
                "subwindow_id": subwindow_id_for_time(time_value),
                "residual_interval_fully_inside_window": index > 0,
            }
        )

    summary = {
        "classification": classification,
        "window": {
            "start_time": STATIONARITY_START_TIME,
            "end_time": STATIONARITY_END_TIME,
            "duration": STATIONARITY_DURATION,
            "snapshot_count": len(window_rows),
            "residual_interval_count": len(residual_rows),
            "subwindows": SUBWINDOWS,
        },
        "thresholds": {
            "energy_normalized_drift_limit": ENERGY_DRIFT_LIMIT,
            "enstrophy_normalized_drift_limit": (
                ENSTROPHY_DRIFT_LIMIT
            ),
            "energy_balance_limit": ENERGY_BALANCE_LIMIT,
            "enstrophy_balance_limit": ENSTROPHY_BALANCE_LIMIT,
            "subwindow_deviation_limit": (
                SUBWINDOW_DEVIATION_LIMIT
            ),
            "median_normalized_energy_residual_limit": (
                MEDIAN_NORMALIZED_ENERGY_RESIDUAL_LIMIT
            ),
            "maximum_normalized_energy_residual_limit": (
                MAX_NORMALIZED_ENERGY_RESIDUAL_LIMIT
            ),
            "median_normalized_enstrophy_residual_limit": (
                MEDIAN_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
            ),
            "maximum_normalized_enstrophy_residual_limit": (
                MAX_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
            ),
            "residual_denominator_floor": (
                RESIDUAL_DENOMINATOR_FLOOR
            ),
        },
        "window_means": means,
        "trends": trends,
        "balance": {
            "energy_balance_metric": energy_balance,
            "enstrophy_balance_metric": enstrophy_balance,
            "mean_energy_injection_to_dissipation_ratio": safe_ratio(
                means["energy_injection_rate"],
                means["viscous_energy_dissipation_rate"],
            ),
            "mean_enstrophy_injection_to_dissipation_ratio": (
                safe_ratio(
                    means["enstrophy_injection_rate"],
                    means[
                        "viscous_enstrophy_dissipation_rate"
                    ],
                )
            ),
        },
        "subwindows": subwindow_metrics,
        "budget_residuals": residual_metrics,
        "criteria": criteria,
    }

    return annotated_rows, summary


# ============================================================================
# Repository and evidence-bundle gates
# ============================================================================

def verify_protected_sources(repo: Path) -> dict[str, str]:
    paths = {
        "design": repo / DESIGN_PATH,
        "spectral_solver": (
            repo / "project" / "solver" / "spectral_solver.py"
        ),
        "forcing_budget_diagnostic": (
            repo / "forcing_budget_diagnostic.py"
        ),
    }

    expected = {
        "design": EXPECTED_DESIGN_SHA256,
        "spectral_solver": EXPECTED_SOLVER_SHA256,
        "forcing_budget_diagnostic": EXPECTED_BUDGET_SHA256,
    }

    observed: dict[str, str] = {}

    for name, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"required file is missing: {path}")

        observed[name] = sha256_file(path)

        if observed[name] != expected[name]:
            raise RuntimeError(
                f"{name} SHA256 changed: {observed[name]}"
            )

    return observed


def verify_runner_commit_shape(
    repo: Path,
    runner: Path,
) -> str:
    head = git_read(repo, "rev-parse", "HEAD")

    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        raise RuntimeError("active branch is not phase4_validation")

    if git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ):
        raise RuntimeError("working tree is not clean")

    ancestor = git_process(
        repo,
        "merge-base",
        "--is-ancestor",
        AUTHORIZED_DESIGN_COMMIT,
        head,
        check=False,
    )

    if ancestor.returncode != 0:
        raise RuntimeError(
            "authorized design commit is not an ancestor of HEAD"
        )

    commit_count = int(
        git_read(
            repo,
            "rev-list",
            "--count",
            f"{AUTHORIZED_DESIGN_COMMIT}..{head}",
        )
    )

    if commit_count != 1:
        raise RuntimeError(
            "execution HEAD must be exactly one commit after "
            "the authorized design commit"
        )

    changed_paths = git_read(
        repo,
        "diff",
        "--name-only",
        f"{AUTHORIZED_DESIGN_COMMIT}..{head}",
    ).splitlines()

    if changed_paths != [runner.name]:
        raise RuntimeError(
            "the runner commit contains unexpected paths: "
            f"{changed_paths!r}"
        )

    tracked = git_process(
        repo,
        "ls-files",
        "--error-unmatch",
        "--",
        runner.name,
        check=False,
    )

    if tracked.returncode != 0:
        raise RuntimeError("runner is not tracked in Git")

    committed_runner = git_process(
        repo,
        "show",
        f"HEAD:{runner.name}",
    ).stdout.encode("utf-8")

    local_runner = runner.read_bytes()

    if sha256_bytes(committed_runner) != sha256_bytes(local_runner):
        raise RuntimeError(
            "working runner bytes do not match committed runner bytes"
        )

    return head


def assert_repository_unchanged(
    repo: Path,
    *,
    authorized_head: str,
) -> None:
    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        raise RuntimeError("active branch changed during execution")

    if git_read(repo, "rev-parse", "HEAD") != authorized_head:
        raise RuntimeError("authorized commit changed during execution")

    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )

    if status:
        raise RuntimeError(
            "working tree became dirty during execution: "
            f"{status!r}"
        )

    verify_protected_sources(repo)


def write_inventory(
    run_directory: Path,
    inventory_path: Path,
    persistent_paths: Sequence[Path],
) -> str:
    rows: list[dict[str, object]] = []

    for path in persistent_paths:
        if not path.is_file():
            continue

        rows.append(
            {
                "relative_path": path.relative_to(
                    run_directory
                ).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "inventory_note": "",
            }
        )

    rows.append(
        {
            "relative_path": inventory_path.name,
            "bytes": "",
            "sha256": "",
            "inventory_note": (
                "self-hash intentionally omitted because a manifest "
                "cannot contain its own final cryptographic hash "
                "without circular self-reference"
            ),
        }
    )

    atomic_write_csv(
        inventory_path,
        rows,
        INVENTORY_FIELDNAMES,
    )

    return sha256_file(inventory_path)


def ensure_bundle_files_exist(
    *,
    budget_path: Path,
    spectrum_path: Path,
    window_path: Path,
    budget_rows: Sequence[Mapping[str, object]],
    spectrum_rows: Sequence[Mapping[str, object]],
    window_rows: Sequence[Mapping[str, object]],
) -> None:
    if not budget_path.exists():
        atomic_write_csv(
            budget_path,
            budget_rows,
            BUDGET_FIELDNAMES,
        )

    if not spectrum_path.exists():
        atomic_write_csv(
            spectrum_path,
            spectrum_rows,
            SPECTRUM_FIELDNAMES,
        )

    if not window_path.exists():
        atomic_write_csv(
            window_path,
            window_rows,
            WINDOW_FIELDNAMES,
        )


# ============================================================================
# Static self-inspection
# ============================================================================

def inspect_runner(repo: Path) -> int:
    runner = Path(__file__).resolve()
    raw = runner.read_bytes()

    if runner.name != RUNNER_NAME:
        fail(
            f"runner filename is {runner.name!r}, "
            f"expected {RUNNER_NAME!r}"
        )

    if b"\r" in raw:
        fail("runner is not LF-only")

    source = raw.decode("utf-8", errors="strict")
    tree = ast.parse(source, filename=str(runner))
    compile(tree, str(runner), "exec", dont_inherit=True)

    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        fail("active branch is not phase4_validation")

    head = git_read(repo, "rev-parse", "HEAD")

    if head != AUTHORIZED_DESIGN_COMMIT:
        fail(
            f"HEAD is {head}, expected design checkpoint "
            f"{AUTHORIZED_DESIGN_COMMIT}"
        )

    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ).splitlines()

    expected_status = [f"?? {runner.name}"]

    if status != expected_status:
        fail(f"unexpected Git status: {status!r}")

    try:
        verify_protected_sources(repo)
    except RuntimeError as error:
        fail(str(error))

    constants: dict[str, object] = {}

    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]

            if isinstance(target, ast.Name):
                try:
                    constants[target.id] = ast.literal_eval(node.value)
                except Exception:
                    pass

    expected_constants = {
        "N": 64,
        "RE": 1000,
        "DT": 0.005,
        "STEPS": 20001,
        "FINAL_PHYSICAL_TIME": 100.005,
        "BUDGET_OUTPUT_INTERVAL": 100,
        "SPECTRUM_OUTPUT_INTERVAL": 500,
        "EXPECTED_BUDGET_SNAPSHOTS": 201,
        "EXPECTED_SPECTRUM_SNAPSHOTS": 41,
        "EXPECTED_FORCING_RMS": 0.005,
        "STATIONARITY_START_TIME": 80.005,
        "STATIONARITY_END_TIME": 100.005,
        "STATIONARITY_DURATION": 20.0,
        "EXPECTED_STATIONARITY_SNAPSHOTS": 41,
        "ENERGY_DRIFT_LIMIT": 0.05,
        "ENSTROPHY_DRIFT_LIMIT": 0.05,
        "ENERGY_BALANCE_LIMIT": 0.10,
        "ENSTROPHY_BALANCE_LIMIT": 0.10,
        "SUBWINDOW_DEVIATION_LIMIT": 0.10,
        "MEDIAN_NORMALIZED_ENERGY_RESIDUAL_LIMIT": 0.01,
        "MAX_NORMALIZED_ENERGY_RESIDUAL_LIMIT": 0.05,
        "MEDIAN_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT": 0.01,
        "MAX_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT": 0.05,
    }

    for name, expected in expected_constants.items():
        if constants.get(name) != expected:
            fail(
                f"{name} is {constants.get(name)!r}, "
                f"expected {expected!r}"
            )

    required_functions = {
        "fail",
        "sha256_file",
        "sha256_array",
        "git_read",
        "atomic_write_json",
        "atomic_write_csv",
        "build_rms_matched_multimode_forcing",
        "external_rk2_step",
        "spectrum_snapshot",
        "interval_with_normalized_residuals",
        "ordinary_least_squares_slope",
        "normalized_window_drift",
        "summarize_stationarity_window",
        "verify_protected_sources",
        "verify_runner_commit_shape",
        "assert_repository_unchanged",
        "write_inventory",
        "inspect_runner",
        "execute_test",
        "main",
    }

    observed_functions = {
        node.name
        for node in tree.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        )
    }

    missing_functions = required_functions - observed_functions

    if missing_functions:
        fail(
            f"missing functions: {sorted(missing_functions)}"
        )

    parents: dict[ast.AST, ast.AST] = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def enclosing_function(node: ast.AST) -> str | None:
        current = node

        while current in parents:
            current = parents[current]

            if isinstance(
                current,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                return current.name

        return None

    actual_solver_run_lines: list[int] = []
    project_import_scopes: list[tuple[str, str | None]] = []

    call_counts = {
        "SpectralSolver": 0,
        "forcing_budget_snapshot": 0,
        "forcing_budget_interval": 0,
    }

    forbidden_power_fit_calls: list[int] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""

            if (
                module.startswith("project")
                or module == "forcing_budget_diagnostic"
            ):
                project_import_scopes.append(
                    (module, enclosing_function(node))
                )

        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            if node.func.id in call_counts:
                call_counts[node.func.id] += 1

            if node.func.id in {"eval", "exec"}:
                fail("dynamic eval or exec call is present")

            if node.func.id in {"polyfit", "curve_fit"}:
                forbidden_power_fit_calls.append(node.lineno)

        if isinstance(node.func, ast.Attribute):
            owner = node.func.value

            if (
                node.func.attr == "run"
                and isinstance(owner, ast.Name)
                and owner.id == "solver"
            ):
                actual_solver_run_lines.append(node.lineno)

            if node.func.attr in {"polyfit", "curve_fit"}:
                forbidden_power_fit_calls.append(node.lineno)

    if actual_solver_run_lines:
        fail(
            "actual solver.run calls found at "
            f"{actual_solver_run_lines}"
        )

    if forbidden_power_fit_calls:
        fail(
            "forbidden generic fit calls found at "
            f"{forbidden_power_fit_calls}"
        )

    expected_call_counts = {
        "SpectralSolver": 1,
        "forcing_budget_snapshot": 1,
        "forcing_budget_interval": 1,
    }

    for name, expected in expected_call_counts.items():
        if call_counts[name] != expected:
            fail(
                f"expected {expected} {name} call, "
                f"found {call_counts[name]}"
            )

    bad_import_scopes = [
        item
        for item in project_import_scopes
        if item[1] != "execute_test"
    ]

    if bad_import_scopes:
        fail(
            "project imports are not confined to execute_test: "
            f"{bad_import_scopes!r}"
        )

    required_fragments = (
        "for loop_index in range(STEPS):",
        "loop_index % BUDGET_OUTPUT_INTERVAL == 0",
        "loop_index % SPECTRUM_OUTPUT_INTERVAL == 0",
        "loop_index == STEPS - 1",
        "80.005",
        "100.005",
        "STATIONARITY CANDIDATE",
        "NOT STATIONARY WITHIN TESTED DURATION",
        "INCOMPLETE",
        "NUMERICAL FAILURE",
        '"convergence": False',
        '"physical_validation": False',
        '"turbulence": False',
        '"cascade": False',
        '"inertial_range": False',
        '"k_minus_3": False',
        '"method_superiority": False',
        '"production_readiness": False',
        'if arguments.mode == "inspect":',
        'if arguments.mode == "run":',
    )

    for fragment in required_fragments:
        if fragment not in source:
            fail(f"required fragment absent: {fragment}")

    print()
    print("=" * 72)
    print("LONGER STATIONARITY RUNNER INSPECTION: PASS")
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", sha256_bytes(raw))
    print("Design commit:", AUTHORIZED_DESIGN_COMMIT)
    print("Design SHA256:", EXPECTED_DESIGN_SHA256)
    print("Configuration: N64, Re1000, dt0.005, steps20001")
    print("Final physical time: 100.005")
    print("Budget interval: 100 loop indices / 0.5 time units")
    print("Spectrum interval: 500 loop indices / 2.5 time units")
    print("Stationarity window: 80.005 through 100.005")
    print("Expected budget snapshots: 201")
    print("Expected spectrum snapshots: 41")
    print("Expected stationarity snapshots: 41")
    print("Forcing: RMS-matched deterministic low-k multimode")
    print("Spectral slope fitting present: NO")
    print("Protected source hashes: PASS")
    print("Runner imported project modules: NO")
    print("Runner executed numerical steps: NO")
    print("Solver constructed: NO")
    print("Actual solver.run call present: NO")
    print("Files written: NO")
    print("Git mutations: NONE")
    print("Numerical execution authorized by inspection: NO")

    return 0


# ============================================================================
# Controlled numerical execution
# ============================================================================

def execute_test(repo: Path) -> int:
    runner = Path(__file__).resolve()

    authorized_head = verify_runner_commit_shape(
        repo,
        runner,
    )

    protected_hashes = verify_protected_sources(repo)

    output_root = repo / OUTPUT_ROOT

    existing_runs = (
        sorted(output_root.glob(f"{RUN_PREFIX}*"))
        if output_root.is_dir()
        else []
    )

    if existing_runs:
        raise RuntimeError(
            "a longer stationarity-test output already exists; "
            "no rerun is allowed: "
            + ", ".join(str(path) for path in existing_runs)
        )

    created = utc_now()
    created_utc = utc_text(created)
    stamp = created.strftime("%Y%m%dT%H%M%SZ")

    run_id = f"{RUN_PREFIX}{stamp}_{authorized_head[:7]}"
    run_directory = output_root / run_id

    if not path_is_git_ignored(repo, run_directory):
        raise RuntimeError(
            "planned result directory is not Git-ignored: "
            f"{run_directory.relative_to(repo)}"
        )

    run_directory.mkdir(parents=True, exist_ok=False)

    metadata_path = run_directory / "run_metadata.json"
    budget_path = run_directory / "forcing_budget.csv"
    spectrum_path = run_directory / "forcing_spectra.csv"
    window_path = run_directory / "stationarity_window.csv"
    summary_path = run_directory / "stationarity_summary.json"
    inventory_path = run_directory / "file_inventory.csv"

    budget_rows: list[dict[str, object]] = []
    spectrum_rows: list[dict[str, object]] = []
    spectrum_summaries: list[dict[str, object]] = []
    stationarity_rows: list[dict[str, object]] = []

    runner_hash = sha256_file(runner)

    metadata: dict[str, object] = {
        "schema_id": "FORCING_BUDGET_STATIONARITY_TEST_V1",
        "run_id": run_id,
        "status": "running",
        "classification": None,
        "created_utc": created_utc,
        "completed_utc": None,
        "repository": {
            "name": "Raj-Sanghera-Project",
            "branch": "phase4_validation",
            "authorized_design_commit": AUTHORIZED_DESIGN_COMMIT,
            "authorized_execution_commit": authorized_head,
            "runner_path": runner.name,
            "runner_sha256": runner_hash,
            "design_path": DESIGN_PATH.as_posix(),
            "design_sha256": protected_hashes["design"],
            "spectral_solver_sha256": (
                protected_hashes["spectral_solver"]
            ),
            "forcing_budget_diagnostic_sha256": (
                protected_hashes["forcing_budget_diagnostic"]
            ),
        },
        "environment": {
            "python_version": sys.version,
            "numpy_version": np.__version__,
            "operating_system": platform.platform(),
            "floating_dtype": "float64",
            "machine_epsilon": float(
                np.finfo(np.float64).eps
            ),
        },
        "configuration": {
            "grid": [N, N],
            "Re": RE,
            "nu": NU,
            "dt": DT,
            "steps": STEPS,
            "final_physical_time": FINAL_PHYSICAL_TIME,
            "initial_vorticity": "exact_zero",
            "time_integrator": "external mirror of protected RK2",
            "protected_solver_run_called": False,
            "dealiasing": "inherited protected two-thirds mask",
            "budget_output_interval_loop_indices": (
                BUDGET_OUTPUT_INTERVAL
            ),
            "budget_sampling_interval_time": (
                BUDGET_OUTPUT_INTERVAL * DT
            ),
            "spectrum_output_interval_loop_indices": (
                SPECTRUM_OUTPUT_INTERVAL
            ),
            "spectrum_sampling_interval_time": (
                SPECTRUM_OUTPUT_INTERVAL * DT
            ),
            "stationarity_window": {
                "start_time": STATIONARITY_START_TIME,
                "end_time": STATIONARITY_END_TIME,
                "duration": STATIONARITY_DURATION,
                "subwindows": SUBWINDOWS,
            },
        },
        "thresholds": {
            "forcing_rms_tolerance": FORCING_RMS_TOLERANCE,
            "energy_spectrum_consistency_tolerance": (
                ENERGY_SPECTRUM_CONSISTENCY_TOLERANCE
            ),
            "energy_normalized_drift_limit": ENERGY_DRIFT_LIMIT,
            "enstrophy_normalized_drift_limit": (
                ENSTROPHY_DRIFT_LIMIT
            ),
            "energy_balance_limit": ENERGY_BALANCE_LIMIT,
            "enstrophy_balance_limit": ENSTROPHY_BALANCE_LIMIT,
            "subwindow_deviation_limit": (
                SUBWINDOW_DEVIATION_LIMIT
            ),
            "median_normalized_energy_residual_limit": (
                MEDIAN_NORMALIZED_ENERGY_RESIDUAL_LIMIT
            ),
            "maximum_normalized_energy_residual_limit": (
                MAX_NORMALIZED_ENERGY_RESIDUAL_LIMIT
            ),
            "median_normalized_enstrophy_residual_limit": (
                MEDIAN_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
            ),
            "maximum_normalized_enstrophy_residual_limit": (
                MAX_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
            ),
            "residual_denominator_floor": (
                RESIDUAL_DENOMINATOR_FLOOR
            ),
        },
        "forcing": None,
        "output_files": {
            "run_metadata": metadata_path.name,
            "forcing_budget": budget_path.name,
            "forcing_spectra": spectrum_path.name,
            "stationarity_window": window_path.name,
            "stationarity_summary": summary_path.name,
            "file_inventory": inventory_path.name,
        },
        "inventory_policy": {
            "all_non_inventory_outputs_hashed": True,
            "inventory_self_hash_in_manifest": False,
            "reason": (
                "a manifest cannot include its own final hash "
                "without circular self-reference"
            ),
        },
        "claims": {
            "stationarity_candidate_limited_to_tested_configuration": False,
            "convergence": False,
            "physical_validation": False,
            "turbulence": False,
            "cascade": False,
            "inertial_range": False,
            "k_minus_3": False,
            "method_superiority": False,
            "production_readiness": False,
        },
    }

    atomic_write_json(metadata_path, metadata)
    atomic_write_csv(budget_path, budget_rows, BUDGET_FIELDNAMES)
    atomic_write_csv(spectrum_path, spectrum_rows, SPECTRUM_FIELDNAMES)
    atomic_write_csv(window_path, stationarity_rows, WINDOW_FIELDNAMES)

    previous_snapshot: dict[str, float | int] | None = None
    max_advection_rms_all_steps = 0.0
    max_mask_removal_rms_all_steps = 0.0
    final_summary: dict[str, object] | None = None

    try:
        from forcing_budget_diagnostic import (
            forcing_budget_interval,
            forcing_budget_snapshot,
        )

        from project.solver.spectral_solver import SpectralSolver

        solver = SpectralSolver(
            nx=N,
            ny=N,
            Re=RE,
            run_path=run_directory,
            dt=DT,
            steps=STEPS,
        )

        if not np.array_equal(
            solver.w,
            np.zeros_like(solver.w),
        ):
            raise RuntimeError(
                "solver did not initialize with exact zero vorticity"
            )

        if not math.isclose(
            float(solver.nu),
            NU,
            rel_tol=0.0,
            abs_tol=1.0e-15,
        ):
            raise RuntimeError(
                f"solver viscosity is {solver.nu!r}, expected {NU!r}"
            )

        forcing, forcing_statistics = (
            build_rms_matched_multimode_forcing(solver)
        )

        expected_forcing_hash = str(
            forcing_statistics["forcing_sha256"]
        )

        metadata["forcing"] = forcing_statistics
        atomic_write_json(metadata_path, metadata)

        for loop_index in range(STEPS):
            step_metrics = external_rk2_step(
                solver,
                forcing,
            )

            max_advection_rms_all_steps = max(
                max_advection_rms_all_steps,
                float(step_metrics["stage1_advection_rms"]),
                float(step_metrics["stage2_advection_rms"]),
            )

            max_mask_removal_rms_all_steps = max(
                max_mask_removal_rms_all_steps,
                float(step_metrics["mask_removal_rms"]),
            )

            budget_due = (
                loop_index % BUDGET_OUTPUT_INTERVAL == 0
                or loop_index == STEPS - 1
            )

            spectrum_due = (
                loop_index % SPECTRUM_OUTPUT_INTERVAL == 0
                or loop_index == STEPS - 1
            )

            if not budget_due and not spectrum_due:
                continue

            observed_forcing_hash = sha256_array(forcing)
            forcing_identity_matches = (
                observed_forcing_hash == expected_forcing_hash
            )

            if not forcing_identity_matches:
                raise RuntimeError(
                    "forcing-field identity changed during execution"
                )

            if not np.isfinite(solver.w).all():
                raise RuntimeError(
                    "vorticity contains a nonfinite value"
                )

            snapshot = forcing_budget_snapshot(
                omega=solver.w,
                forcing=forcing,
                nu=solver.nu,
                kx=solver.kx,
                ky=solver.ky,
                dt=DT,
                loop_index=loop_index,
            )

            row: dict[str, object] = {
                **snapshot,
                **step_metrics,
                "forcing_sha256": observed_forcing_hash,
                "forcing_identity_matches": (
                    forcing_identity_matches
                ),
                "interval_duration": None,
                "observed_energy_rate": None,
                "mean_continuous_energy_rhs": None,
                "energy_budget_residual": None,
                "mean_energy_injection_rate": None,
                "mean_viscous_energy_dissipation_rate": None,
                "normalized_energy_budget_residual": None,
                "observed_enstrophy_rate": None,
                "mean_continuous_enstrophy_rhs": None,
                "enstrophy_budget_residual": None,
                "mean_enstrophy_injection_rate": None,
                "mean_viscous_enstrophy_dissipation_rate": None,
                "normalized_enstrophy_budget_residual": None,
            }

            if previous_snapshot is not None:
                row.update(
                    interval_with_normalized_residuals(
                        previous_snapshot,
                        snapshot,
                        forcing_budget_interval,
                    )
                )

            if budget_due:
                budget_rows.append(row)
                atomic_write_csv(
                    budget_path,
                    budget_rows,
                    BUDGET_FIELDNAMES,
                )
                previous_snapshot = snapshot

            if spectrum_due:
                assert_repository_unchanged(
                    repo,
                    authorized_head=authorized_head,
                )

                new_spectrum_rows, spectrum_summary = (
                    spectrum_snapshot(
                        solver,
                        np.asarray(solver.w),
                        loop_index=loop_index,
                        direct_energy=float(snapshot["energy"]),
                    )
                )

                spectrum_rows.extend(new_spectrum_rows)
                spectrum_summaries.append(spectrum_summary)

                atomic_write_csv(
                    spectrum_path,
                    spectrum_rows,
                    SPECTRUM_FIELDNAMES,
                )

                print(
                    "progress",
                    f"t={float(snapshot['physical_time']):.3f}",
                    f"E={float(snapshot['energy']):.6e}",
                    f"Z={float(snapshot['enstrophy']):.6e}",
                    "Einj/Ediss="
                    f"{safe_ratio(float(snapshot['energy_injection_rate']), float(snapshot['viscous_energy_dissipation_rate']))}",
                    "Zinj/Zdiss="
                    f"{safe_ratio(float(snapshot['enstrophy_injection_rate']), float(snapshot['viscous_enstrophy_dissipation_rate']))}",
                    "dominant_shell="
                    f"{spectrum_summary['dominant_shell']}",
                    "tail_k_gt_4="
                    f"{float(spectrum_summary['tail_fraction_k_gt_4']):.6e}",
                    flush=True,
                )

        if len(budget_rows) != EXPECTED_BUDGET_SNAPSHOTS:
            raise RuntimeError(
                f"budget snapshot count is {len(budget_rows)}, "
                f"expected {EXPECTED_BUDGET_SNAPSHOTS}"
            )

        if len(spectrum_summaries) != EXPECTED_SPECTRUM_SNAPSHOTS:
            raise RuntimeError(
                "spectrum snapshot count is "
                f"{len(spectrum_summaries)}, "
                f"expected {EXPECTED_SPECTRUM_SNAPSHOTS}"
            )

        final_budget = budget_rows[-1]
        final_spectrum = spectrum_summaries[-1]

        if int(final_budget["completed_steps"]) != STEPS:
            raise RuntimeError(
                "final completed-step count does not match design"
            )

        if not math.isclose(
            float(final_budget["physical_time"]),
            FINAL_PHYSICAL_TIME,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            raise RuntimeError(
                "final physical time does not match design"
            )

        if not all_numeric_values_finite(budget_rows):
            raise RuntimeError(
                "forcing-budget table contains a nonfinite numeric value"
            )

        if not all_numeric_values_finite(spectrum_rows):
            raise RuntimeError(
                "forcing-spectrum table contains a nonfinite numeric value"
            )

        raw_window_rows = [
            row
            for row in budget_rows
            if (
                float(row["physical_time"])
                >= STATIONARITY_START_TIME - 1.0e-12
                and float(row["physical_time"])
                <= STATIONARITY_END_TIME + 1.0e-12
            )
        ]

        stationarity_rows, stationarity_analysis = (
            summarize_stationarity_window(raw_window_rows)
        )

        atomic_write_csv(
            window_path,
            stationarity_rows,
            WINDOW_FIELDNAMES,
        )

        classification = str(
            stationarity_analysis["classification"]
        )

        final_summary = {
            "schema_id": "FORCING_BUDGET_STATIONARITY_SUMMARY_V1",
            "run_id": run_id,
            "classification": classification,
            "repository": metadata["repository"],
            "configuration": metadata["configuration"],
            "forcing": forcing_statistics,
            "thresholds": metadata["thresholds"],
            "counts": {
                "budget_snapshots": len(budget_rows),
                "spectrum_snapshots": len(spectrum_summaries),
                "spectrum_rows": len(spectrum_rows),
                "stationarity_window_snapshots": (
                    len(stationarity_rows)
                ),
            },
            "global_integrity_metrics": {
                "max_advection_rms_all_steps": (
                    max_advection_rms_all_steps
                ),
                "max_mask_removal_rms_all_steps": (
                    max_mask_removal_rms_all_steps
                ),
                "maximum_spectrum_energy_consistency_error": max(
                    float(
                        item[
                            "relative_energy_consistency_error"
                        ]
                    )
                    for item in spectrum_summaries
                ),
                "forcing_identity_matches_at_all_outputs": all(
                    bool(row["forcing_identity_matches"])
                    for row in budget_rows
                ),
            },
            "stationarity_analysis": stationarity_analysis,
            "final_budget_snapshot": final_budget,
            "final_spectrum_summary": final_spectrum,
            "scientific_boundary": {
                "stationarity_screening_only": True,
                "stationarity_candidate_limited_to_tested_configuration": (
                    classification
                    == CLASSIFICATION_STATIONARITY_CANDIDATE
                ),
                "convergence": False,
                "physical_validation": False,
                "turbulence": False,
                "cascade": False,
                "inertial_range": False,
                "k_minus_3": False,
                "method_superiority": False,
                "production_readiness": False,
                "spectral_slope_fitted": False,
            },
        }

        atomic_write_json(summary_path, final_summary)

        metadata["status"] = "completed"
        metadata["classification"] = classification
        metadata["completed_utc"] = utc_text()
        metadata["claims"][
            "stationarity_candidate_limited_to_tested_configuration"
        ] = (
            classification
            == CLASSIFICATION_STATIONARITY_CANDIDATE
        )

        atomic_write_json(metadata_path, metadata)

        inventory_hash = write_inventory(
            run_directory,
            inventory_path,
            (
                metadata_path,
                budget_path,
                spectrum_path,
                window_path,
                summary_path,
            ),
        )

        assert_repository_unchanged(
            repo,
            authorized_head=authorized_head,
        )

        print()
        print("=" * 72)
        print(classification)
        print("=" * 72)
        print("Run directory:", run_directory)
        print("Budget snapshots:", len(budget_rows))
        print("Spectrum snapshots:", len(spectrum_summaries))
        print(
            "Stationarity-window snapshots:",
            len(stationarity_rows),
        )
        print(
            "Final completed steps:",
            final_budget["completed_steps"],
        )
        print(
            "Final physical time:",
            final_budget["physical_time"],
        )
        print(
            "Energy normalized drift:",
            f"{float(stationarity_analysis['trends']['energy']['normalized_window_drift']):.12e}",
        )
        print(
            "Enstrophy normalized drift:",
            f"{float(stationarity_analysis['trends']['enstrophy']['normalized_window_drift']):.12e}",
        )
        print(
            "Energy balance metric:",
            f"{float(stationarity_analysis['balance']['energy_balance_metric']):.12e}",
        )
        print(
            "Enstrophy balance metric:",
            f"{float(stationarity_analysis['balance']['enstrophy_balance_metric']):.12e}",
        )
        print(
            "Median normalized energy residual:",
            f"{float(stationarity_analysis['budget_residuals']['median_normalized_energy_residual']):.12e}",
        )
        print(
            "Maximum normalized energy residual:",
            f"{float(stationarity_analysis['budget_residuals']['maximum_normalized_energy_residual']):.12e}",
        )
        print(
            "Median normalized enstrophy residual:",
            f"{float(stationarity_analysis['budget_residuals']['median_normalized_enstrophy_residual']):.12e}",
        )
        print(
            "Maximum normalized enstrophy residual:",
            f"{float(stationarity_analysis['budget_residuals']['maximum_normalized_enstrophy_residual']):.12e}",
        )
        print(
            "Final dominant shell:",
            final_spectrum["dominant_shell"],
        )
        print(
            "Final tail fraction k>4:",
            f"{float(final_spectrum['tail_fraction_k_gt_4']):.12e}",
        )
        print(
            "Final high-k fraction k>=10:",
            f"{float(final_spectrum['high_k_fraction_k_ge_10']):.12e}",
        )
        print("File inventory SHA256:", inventory_hash)
        print("Protected solver run loop called: NO")
        print("Spectral slope fitted: NO")
        print("Formal claims authorized: NO")

        return 0

    except KeyboardInterrupt as error:
        classification = CLASSIFICATION_INCOMPLETE

        failure_summary = {
            "schema_id": "FORCING_BUDGET_STATIONARITY_SUMMARY_V1",
            "run_id": run_id,
            "classification": classification,
            "error_type": type(error).__name__,
            "error_message": "execution interrupted by user",
            "counts": {
                "budget_snapshots": len(budget_rows),
                "spectrum_snapshots": len(spectrum_summaries),
                "spectrum_rows": len(spectrum_rows),
            },
            "scientific_boundary": {
                "stationarity_claim": False,
                "convergence": False,
                "physical_validation": False,
                "turbulence": False,
                "cascade": False,
                "inertial_range": False,
                "k_minus_3": False,
                "method_superiority": False,
                "production_readiness": False,
            },
        }

        atomic_write_json(summary_path, failure_summary)

        metadata["status"] = "incomplete"
        metadata["classification"] = classification
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = "execution interrupted by user"
        metadata["completed_utc"] = utc_text()
        atomic_write_json(metadata_path, metadata)

        ensure_bundle_files_exist(
            budget_path=budget_path,
            spectrum_path=spectrum_path,
            window_path=window_path,
            budget_rows=budget_rows,
            spectrum_rows=spectrum_rows,
            window_rows=stationarity_rows,
        )

        write_inventory(
            run_directory,
            inventory_path,
            (
                metadata_path,
                budget_path,
                spectrum_path,
                window_path,
                summary_path,
            ),
        )

        print()
        print(CLASSIFICATION_INCOMPLETE)
        print("Partial outputs preserved at:", run_directory)
        raise

    except ImportError as error:
        classification = CLASSIFICATION_INCOMPLETE

        failure_summary = {
            "schema_id": "FORCING_BUDGET_STATIONARITY_SUMMARY_V1",
            "run_id": run_id,
            "classification": classification,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "counts": {
                "budget_snapshots": len(budget_rows),
                "spectrum_snapshots": len(spectrum_summaries),
                "spectrum_rows": len(spectrum_rows),
            },
            "scientific_boundary": {
                "stationarity_claim": False,
                "convergence": False,
                "physical_validation": False,
                "turbulence": False,
                "cascade": False,
                "inertial_range": False,
                "k_minus_3": False,
                "method_superiority": False,
                "production_readiness": False,
            },
        }

        atomic_write_json(summary_path, failure_summary)

        metadata["status"] = "incomplete"
        metadata["classification"] = classification
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = str(error)
        metadata["completed_utc"] = utc_text()
        atomic_write_json(metadata_path, metadata)

        ensure_bundle_files_exist(
            budget_path=budget_path,
            spectrum_path=spectrum_path,
            window_path=window_path,
            budget_rows=budget_rows,
            spectrum_rows=spectrum_rows,
            window_rows=stationarity_rows,
        )

        write_inventory(
            run_directory,
            inventory_path,
            (
                metadata_path,
                budget_path,
                spectrum_path,
                window_path,
                summary_path,
            ),
        )

        print()
        print(CLASSIFICATION_INCOMPLETE)
        print("Partial outputs preserved at:", run_directory)
        raise

    except BaseException as error:
        classification = CLASSIFICATION_NUMERICAL_FAILURE

        failure_summary = {
            "schema_id": "FORCING_BUDGET_STATIONARITY_SUMMARY_V1",
            "run_id": run_id,
            "classification": classification,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "counts": {
                "budget_snapshots": len(budget_rows),
                "spectrum_snapshots": len(spectrum_summaries),
                "spectrum_rows": len(spectrum_rows),
            },
            "scientific_boundary": {
                "stationarity_claim": False,
                "convergence": False,
                "physical_validation": False,
                "turbulence": False,
                "cascade": False,
                "inertial_range": False,
                "k_minus_3": False,
                "method_superiority": False,
                "production_readiness": False,
            },
        }

        try:
            atomic_write_json(summary_path, failure_summary)
        except Exception:
            pass

        metadata["status"] = "failed"
        metadata["classification"] = classification
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = str(error)
        metadata["completed_utc"] = utc_text()

        try:
            atomic_write_json(metadata_path, metadata)
        except Exception:
            pass

        try:
            ensure_bundle_files_exist(
                budget_path=budget_path,
                spectrum_path=spectrum_path,
                window_path=window_path,
                budget_rows=budget_rows,
                spectrum_rows=spectrum_rows,
                window_rows=stationarity_rows,
            )
        except Exception:
            pass

        try:
            write_inventory(
                run_directory,
                inventory_path,
                (
                    metadata_path,
                    budget_path,
                    spectrum_path,
                    window_path,
                    summary_path,
                ),
            )
        except Exception:
            pass

        print()
        print(CLASSIFICATION_NUMERICAL_FAILURE)
        print("Partial outputs preserved at:", run_directory)
        raise


# ============================================================================
# Command line
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the controlled longer RMS-matched "
            "multimode forcing-budget stationarity test."
        )
    )

    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help=(
            "inspect source without numerical execution, "
            "or run the single authorized test"
        ),
    )

    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent

    if arguments.mode == "inspect":
        return inspect_runner(repo)

    if arguments.mode == "run":
        return execute_test(repo)

    raise RuntimeError(f"unsupported mode: {arguments.mode!r}")


if __name__ == "__main__":
    raise SystemExit(main())
