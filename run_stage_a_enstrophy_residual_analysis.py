"""
Read-only Stage A analysis of the archived longer forcing-budget evidence.

Usage:
    python -B run_stage_a_enstrophy_residual_analysis.py inspect
    python -B run_stage_a_enstrophy_residual_analysis.py run

The inspection path parses this file and verifies the archived design and
source-data identities without importing project modules, executing solver
steps, or writing analysis outputs.

The run path reads only the archived CSV and JSON evidence files. It performs
descriptive residual statistics, correlations, exact-time spectral joins, and
offline cadence coarsening. It writes a new Git-ignored analysis bundle and
does not modify the archived evidence.

This analysis cannot causally separate discrete advection, dealiasing, RK2
error, or sub-0.5 diagnostic cadence. Those questions require the later
operator-ledger and replay stages defined by the archived design.
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
import shutil
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np


RUNNER_NAME = "run_stage_a_enstrophy_residual_analysis.py"

DESIGN_PATH = Path(
    "ENSTROPHY_RESIDUAL_DIAGNOSTIC_SEPARATION_DESIGN.md"
)

AUTHORIZED_DESIGN_COMMIT = (
    "f3f517578b0c9541d56dfb6968681f5884cc09a5"
)

EXPECTED_DESIGN_SHA256 = (
    "9F1A2CE658545E601ADE0072C0FBBC738754F9D53B2B190BCD71B85CCC529DAA"
)

SOURCE_RUN = (
    Path("experiments")
    / "forcing_budget_stationarity"
    / "forcing_budget_stationarity_20260719T083403Z_9a9f2e0"
)

SOURCE_HASHES = {
    "run_metadata.json":
        "57640568F657C26E47F495B1BE7C4C23F54EF0ACB882250ECB596A426F504ED9",
    "forcing_budget.csv":
        "38D01CE7278979EB4D7433414C849F65820C729DC5928A964FFED1EB3E4F482F",
    "forcing_spectra.csv":
        "62235ED6A5C9BD17D4FF21D22A1F830EE637FC22F26ABD43B483359B5873275A",
    "stationarity_window.csv":
        "FD1C5017DC24C6BF9F12F3BB56E44631491BA8178B174968743175976C06ED9A",
    "stationarity_summary.json":
        "3573F19100A4BD817B97C603B3C13D0137AD56D1F52FD05D602DFFC6400DBE1E",
    "file_inventory.csv":
        "3745C4E279E304A1A04CA14CEFE04BAA0FABD1A6072BB2E4C407FAB78CA1A028",
}

OUTPUT_ROOT = (
    Path("experiments")
    / "forcing_budget_stage_a_analysis"
)

RUN_PREFIX = "stage_a_enstrophy_residual_"

BASE_CADENCE = 0.5
COARSENING_CADENCES = (0.5, 1.0, 2.0, 2.5, 5.0)

STATIONARITY_START_TIME = 80.005
STATIONARITY_END_TIME = 100.005

RESIDUAL_DENOMINATOR_FLOOR = 1.0e-30

MEDIAN_NORMALIZED_ENERGY_RESIDUAL_LIMIT = 0.01
MAX_NORMALIZED_ENERGY_RESIDUAL_LIMIT = 0.05
MEDIAN_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT = 0.01
MAX_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT = 0.05

CORRELATION_SUPPORT_THRESHOLD = 0.60
CADENCE_FACTOR_THRESHOLD = 1.25
CADENCE_REQUIRED_SUCCESSIVE_INCREASES = 3

CLASSIFICATION_CADENCE = (
    "ARCHIVED DATA SUPPORTS CADENCE SENSITIVITY"
)
CLASSIFICATION_OPERATOR = (
    "ARCHIVED DATA SUPPORTS OPERATOR CORRELATION"
)
CLASSIFICATION_INCONCLUSIVE = "ARCHIVED DATA INCONCLUSIVE"
CLASSIFICATION_MULTIPLE = (
    "ARCHIVED DATA SHOWS MULTIPLE CONTRIBUTORS"
)

TIME_BLOCKS = (
    {
        "block_id": 1,
        "label": "0.005 <= t <= 20.005",
        "lower": 0.005,
        "upper": 20.005,
        "lower_inclusive": True,
    },
    {
        "block_id": 2,
        "label": "20.005 < t <= 40.005",
        "lower": 20.005,
        "upper": 40.005,
        "lower_inclusive": False,
    },
    {
        "block_id": 3,
        "label": "40.005 < t <= 60.005",
        "lower": 40.005,
        "upper": 60.005,
        "lower_inclusive": False,
    },
    {
        "block_id": 4,
        "label": "60.005 < t <= 80.005",
        "lower": 60.005,
        "upper": 80.005,
        "lower_inclusive": False,
    },
    {
        "block_id": 5,
        "label": "80.005 < t <= 100.005",
        "lower": 80.005,
        "upper": 100.005,
        "lower_inclusive": False,
    },
)

TIME_SERIES_FIELDNAMES = (
    "block_id",
    "interval_start_time",
    "physical_time",
    "interval_duration",
    "loop_index",
    "completed_steps",
    "energy",
    "enstrophy",
    "observed_energy_rate",
    "mean_continuous_energy_rhs",
    "energy_budget_residual",
    "normalized_energy_budget_residual",
    "observed_enstrophy_rate",
    "absolute_observed_enstrophy_rate",
    "mean_continuous_enstrophy_rhs",
    "absolute_mean_continuous_enstrophy_rhs",
    "enstrophy_budget_residual",
    "normalized_enstrophy_budget_residual",
    "energy_injection_rate",
    "viscous_energy_dissipation_rate",
    "enstrophy_injection_rate",
    "viscous_enstrophy_dissipation_rate",
    "mean_enstrophy_injection_rate",
    "mean_viscous_enstrophy_dissipation_rate",
    "stage1_advection_rms",
    "stage2_advection_rms",
    "max_stage_advection_rms",
    "mask_removal_rms",
    "vorticity_rms",
    "maximum_absolute_vorticity",
    "dominant_shell",
    "tail_fraction_k_gt_4",
    "high_k_fraction_k_ge_10",
    "middle_k_fraction_5_le_k_le_9",
    "low_k_fraction_k_le_4",
)

BLOCK_FIELDNAMES = (
    "block_id",
    "label",
    "interval_count",
    "time_start",
    "time_end",
    "normalized_enstrophy_residual_median",
    "normalized_enstrophy_residual_mean",
    "normalized_enstrophy_residual_maximum",
    "normalized_enstrophy_residual_p90",
    "normalized_energy_residual_median",
    "normalized_energy_residual_mean",
    "normalized_energy_residual_maximum",
    "normalized_energy_residual_p90",
    "signed_enstrophy_residual_mean",
    "signed_enstrophy_residual_rms",
    "positive_enstrophy_residual_count",
    "negative_enstrophy_residual_count",
    "zero_enstrophy_residual_count",
    "positive_enstrophy_residual_fraction",
    "negative_enstrophy_residual_fraction",
    "mean_stage1_advection_rms",
    "mean_stage2_advection_rms",
    "mean_max_stage_advection_rms",
    "mean_mask_removal_rms",
    "mean_enstrophy",
    "mean_absolute_observed_enstrophy_rate",
    "mean_absolute_continuous_enstrophy_rhs",
    "mean_enstrophy_injection_rate",
    "mean_viscous_enstrophy_dissipation_rate",
)

CORRELATION_FIELDNAMES = (
    "scope",
    "target",
    "predictor",
    "sample_count",
    "pearson",
    "spearman",
    "maximum_absolute_coefficient",
    "strength",
    "support_threshold",
    "support_threshold_met",
)

COARSENING_FIELDNAMES = (
    "scope",
    "cadence",
    "cadence_multiple_of_base",
    "interval_count",
    "normalized_energy_residual_median",
    "normalized_energy_residual_mean",
    "normalized_energy_residual_maximum",
    "normalized_energy_residual_p90",
    "normalized_enstrophy_residual_median",
    "normalized_enstrophy_residual_mean",
    "normalized_enstrophy_residual_maximum",
    "normalized_enstrophy_residual_p90",
    "signed_energy_residual_mean",
    "signed_energy_residual_rms",
    "signed_enstrophy_residual_mean",
    "signed_enstrophy_residual_rms",
    "median_energy_gate_pass",
    "maximum_energy_gate_pass",
    "median_enstrophy_gate_pass",
    "maximum_enstrophy_gate_pass",
)

INVENTORY_FIELDNAMES = (
    "relative_path",
    "bytes",
    "sha256",
    "inventory_note",
)


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


def git_process(
    repo: Path,
    *args: str,
    check: bool = True,
    text: bool = True,
) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        shell=False,
        check=check,
        capture_output=True,
        text=text,
        encoding="utf-8" if text else None,
        errors="strict" if text else None,
    )


def git_read(repo: Path, *args: str) -> str:
    return str(git_process(repo, *args).stdout).strip()


def git_bytes(repo: Path, *args: str) -> bytes:
    result = git_process(
        repo,
        *args,
        text=False,
    )

    return bytes(result.stdout)


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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def finite_float(name: str, value: object) -> float:
    result = float(value)

    if not math.isfinite(result):
        raise RuntimeError(f"{name} is nonfinite: {value!r}")

    return result


def optional_float(value: object) -> float | None:
    if value is None:
        return None

    text = str(value).strip()

    if text == "":
        return None

    return finite_float("optional numeric value", text)


def parse_budget_rows(
    raw_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    integer_fields = {
        "loop_index",
        "completed_steps",
    }

    boolean_fields = {
        "forcing_identity_matches",
    }

    rows: list[dict[str, object]] = []

    for raw in raw_rows:
        row: dict[str, object] = {}

        for name, value in raw.items():
            if name in integer_fields:
                row[name] = int(value)

            elif name in boolean_fields:
                if value not in {"True", "False"}:
                    raise RuntimeError(
                        f"invalid Boolean value for {name}: {value!r}"
                    )

                row[name] = value == "True"

            elif name in {
                "forcing_sha256",
            }:
                row[name] = value

            else:
                row[name] = optional_float(value)

        rows.append(row)

    rows.sort(key=lambda item: int(item["loop_index"]))

    return rows


def parse_spectrum_summaries(
    raw_rows: Sequence[Mapping[str, str]],
) -> dict[int, dict[str, object]]:
    summaries: dict[int, dict[str, object]] = {}
    counts: dict[int, int] = {}

    summary_fields = (
        "loop_index",
        "completed_steps",
        "physical_time",
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

    integer_fields = {
        "loop_index",
        "completed_steps",
        "dominant_shell",
        "finite_shell_count",
        "nonzero_shell_count",
    }

    for raw in raw_rows:
        loop_index = int(raw["loop_index"])
        counts[loop_index] = counts.get(loop_index, 0) + 1

        candidate: dict[str, object] = {}

        for name in summary_fields:
            if name in integer_fields:
                candidate[name] = int(raw[name])
            else:
                candidate[name] = finite_float(name, raw[name])

        if loop_index not in summaries:
            summaries[loop_index] = candidate
            continue

        existing = summaries[loop_index]

        for name in summary_fields:
            first = existing[name]
            second = candidate[name]

            if isinstance(first, int):
                if first != second:
                    raise RuntimeError(
                        f"spectrum summary field {name} changes "
                        f"within loop index {loop_index}"
                    )
            else:
                if not math.isclose(
                    float(first),
                    float(second),
                    rel_tol=1.0e-13,
                    abs_tol=1.0e-15,
                ):
                    raise RuntimeError(
                        f"spectrum summary field {name} changes "
                        f"within loop index {loop_index}"
                    )

    if len(summaries) != 41:
        raise RuntimeError(
            f"expected 41 spectrum snapshots, found {len(summaries)}"
        )

    if any(count != 45 for count in counts.values()):
        raise RuntimeError(
            "not every spectrum snapshot contains exactly 45 shell rows"
        )

    return summaries


def percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        raise ValueError("cannot calculate a percentile of no values")

    return float(np.percentile(np.asarray(values, dtype=np.float64), quantile))


def mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot calculate a mean of no values")

    return float(np.mean(np.asarray(values, dtype=np.float64)))


def median(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot calculate a median of no values")

    return float(np.median(np.asarray(values, dtype=np.float64)))


def rms(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot calculate RMS of no values")

    array = np.asarray(values, dtype=np.float64)
    return float(np.sqrt(np.mean(array * array)))


def rank_average(values: Sequence[float]) -> list[float]:
    indexed = sorted(
        enumerate(values),
        key=lambda item: item[1],
    )

    ranks = [0.0] * len(values)
    position = 0

    while position < len(indexed):
        end = position + 1

        while (
            end < len(indexed)
            and indexed[end][1] == indexed[position][1]
        ):
            end += 1

        average_rank = 0.5 * (
            (position + 1)
            + end
        )

        for index in range(position, end):
            original_index = indexed[index][0]
            ranks[original_index] = average_rank

        position = end

    return ranks


def pearson_correlation(
    first: Sequence[float],
    second: Sequence[float],
) -> float | None:
    if len(first) != len(second):
        raise ValueError("correlation arrays have unequal lengths")

    if len(first) < 3:
        return None

    x = np.asarray(first, dtype=np.float64)
    y = np.asarray(second, dtype=np.float64)

    x_centered = x - np.mean(x)
    y_centered = y - np.mean(y)

    denominator = float(
        np.sqrt(
            np.sum(x_centered * x_centered)
            * np.sum(y_centered * y_centered)
        )
    )

    if denominator == 0.0:
        return None

    return float(
        np.sum(x_centered * y_centered)
        / denominator
    )


def spearman_correlation(
    first: Sequence[float],
    second: Sequence[float],
) -> float | None:
    return pearson_correlation(
        rank_average(first),
        rank_average(second),
    )


def correlation_strength(value: float | None) -> str:
    if value is None:
        return "undefined"

    magnitude = abs(value)

    if magnitude >= 0.80:
        return "very strong"

    if magnitude >= 0.60:
        return "strong"

    if magnitude >= 0.40:
        return "moderate"

    if magnitude >= 0.20:
        return "weak"

    return "very weak"


def block_for_time(physical_time: float) -> int:
    tolerance = 1.0e-12

    for block in TIME_BLOCKS:
        lower = float(block["lower"])
        upper = float(block["upper"])
        lower_inclusive = bool(block["lower_inclusive"])

        lower_ok = (
            physical_time >= lower - tolerance
            if lower_inclusive
            else physical_time > lower + tolerance
        )

        upper_ok = physical_time <= upper + tolerance

        if lower_ok and upper_ok:
            return int(block["block_id"])

    raise RuntimeError(
        f"physical time {physical_time} is outside the time blocks"
    )


def residual_from_endpoints(
    previous: Mapping[str, object],
    current: Mapping[str, object],
) -> dict[str, float]:
    start_time = finite_float(
        "previous physical_time",
        previous["physical_time"],
    )

    end_time = finite_float(
        "current physical_time",
        current["physical_time"],
    )

    interval = end_time - start_time

    if interval <= 0.0:
        raise RuntimeError("nonpositive coarsened interval")

    observed_energy_rate = (
        finite_float("current energy", current["energy"])
        - finite_float("previous energy", previous["energy"])
    ) / interval

    observed_enstrophy_rate = (
        finite_float("current enstrophy", current["enstrophy"])
        - finite_float("previous enstrophy", previous["enstrophy"])
    ) / interval

    mean_continuous_energy_rhs = 0.5 * (
        finite_float(
            "previous continuous energy RHS",
            previous["continuous_energy_rhs"],
        )
        + finite_float(
            "current continuous energy RHS",
            current["continuous_energy_rhs"],
        )
    )

    mean_continuous_enstrophy_rhs = 0.5 * (
        finite_float(
            "previous continuous enstrophy RHS",
            previous["continuous_enstrophy_rhs"],
        )
        + finite_float(
            "current continuous enstrophy RHS",
            current["continuous_enstrophy_rhs"],
        )
    )

    energy_residual = (
        observed_energy_rate
        - mean_continuous_energy_rhs
    )

    enstrophy_residual = (
        observed_enstrophy_rate
        - mean_continuous_enstrophy_rhs
    )

    mean_energy_injection = 0.5 * (
        finite_float(
            "previous energy injection",
            previous["energy_injection_rate"],
        )
        + finite_float(
            "current energy injection",
            current["energy_injection_rate"],
        )
    )

    mean_energy_dissipation = 0.5 * (
        finite_float(
            "previous energy dissipation",
            previous["viscous_energy_dissipation_rate"],
        )
        + finite_float(
            "current energy dissipation",
            current["viscous_energy_dissipation_rate"],
        )
    )

    mean_enstrophy_injection = 0.5 * (
        finite_float(
            "previous enstrophy injection",
            previous["enstrophy_injection_rate"],
        )
        + finite_float(
            "current enstrophy injection",
            current["enstrophy_injection_rate"],
        )
    )

    mean_enstrophy_dissipation = 0.5 * (
        finite_float(
            "previous enstrophy dissipation",
            previous["viscous_enstrophy_dissipation_rate"],
        )
        + finite_float(
            "current enstrophy dissipation",
            current["viscous_enstrophy_dissipation_rate"],
        )
    )

    normalized_energy = abs(energy_residual) / max(
        abs(mean_energy_injection),
        abs(mean_energy_dissipation),
        RESIDUAL_DENOMINATOR_FLOOR,
    )

    normalized_enstrophy = abs(enstrophy_residual) / max(
        abs(mean_enstrophy_injection),
        abs(mean_enstrophy_dissipation),
        RESIDUAL_DENOMINATOR_FLOOR,
    )

    return {
        "interval_start_time": start_time,
        "physical_time": end_time,
        "interval_duration": interval,
        "observed_energy_rate": observed_energy_rate,
        "mean_continuous_energy_rhs": mean_continuous_energy_rhs,
        "energy_budget_residual": energy_residual,
        "normalized_energy_budget_residual": normalized_energy,
        "observed_enstrophy_rate": observed_enstrophy_rate,
        "absolute_observed_enstrophy_rate": abs(
            observed_enstrophy_rate
        ),
        "mean_continuous_enstrophy_rhs": (
            mean_continuous_enstrophy_rhs
        ),
        "absolute_mean_continuous_enstrophy_rhs": abs(
            mean_continuous_enstrophy_rhs
        ),
        "enstrophy_budget_residual": enstrophy_residual,
        "normalized_enstrophy_budget_residual": (
            normalized_enstrophy
        ),
    }


def build_time_series(
    budget_rows: Sequence[Mapping[str, object]],
    spectrum_summaries: Mapping[int, Mapping[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for index in range(1, len(budget_rows)):
        previous = budget_rows[index - 1]
        current = budget_rows[index]

        interval = residual_from_endpoints(
            previous,
            current,
        )

        stored_energy = finite_float(
            "stored normalized energy residual",
            current["normalized_energy_budget_residual"],
        )

        stored_enstrophy = finite_float(
            "stored normalized enstrophy residual",
            current["normalized_enstrophy_budget_residual"],
        )

        if not math.isclose(
            interval["normalized_energy_budget_residual"],
            stored_energy,
            rel_tol=1.0e-12,
            abs_tol=1.0e-14,
        ):
            raise RuntimeError(
                "recomputed 0.5-cadence energy residual "
                "does not match the archive"
            )

        if not math.isclose(
            interval["normalized_enstrophy_budget_residual"],
            stored_enstrophy,
            rel_tol=1.0e-12,
            abs_tol=1.0e-14,
        ):
            raise RuntimeError(
                "recomputed 0.5-cadence enstrophy residual "
                "does not match the archive"
            )

        loop_index = int(current["loop_index"])
        spectral = spectrum_summaries.get(loop_index)

        row = {
            "block_id": block_for_time(
                finite_float(
                    "physical time",
                    current["physical_time"],
                )
            ),
            **interval,
            "loop_index": loop_index,
            "completed_steps": int(current["completed_steps"]),
            "energy": finite_float("energy", current["energy"]),
            "enstrophy": finite_float(
                "enstrophy",
                current["enstrophy"],
            ),
            "energy_injection_rate": finite_float(
                "energy injection",
                current["energy_injection_rate"],
            ),
            "viscous_energy_dissipation_rate": finite_float(
                "energy dissipation",
                current["viscous_energy_dissipation_rate"],
            ),
            "enstrophy_injection_rate": finite_float(
                "enstrophy injection",
                current["enstrophy_injection_rate"],
            ),
            "viscous_enstrophy_dissipation_rate": finite_float(
                "enstrophy dissipation",
                current["viscous_enstrophy_dissipation_rate"],
            ),
            "mean_enstrophy_injection_rate": finite_float(
                "mean enstrophy injection",
                current["mean_enstrophy_injection_rate"],
            ),
            "mean_viscous_enstrophy_dissipation_rate": finite_float(
                "mean enstrophy dissipation",
                current[
                    "mean_viscous_enstrophy_dissipation_rate"
                ],
            ),
            "stage1_advection_rms": finite_float(
                "stage-1 advection RMS",
                current["stage1_advection_rms"],
            ),
            "stage2_advection_rms": finite_float(
                "stage-2 advection RMS",
                current["stage2_advection_rms"],
            ),
            "max_stage_advection_rms": max(
                finite_float(
                    "stage-1 advection RMS",
                    current["stage1_advection_rms"],
                ),
                finite_float(
                    "stage-2 advection RMS",
                    current["stage2_advection_rms"],
                ),
            ),
            "mask_removal_rms": finite_float(
                "mask removal RMS",
                current["mask_removal_rms"],
            ),
            "vorticity_rms": finite_float(
                "vorticity RMS",
                current["vorticity_rms"],
            ),
            "maximum_absolute_vorticity": finite_float(
                "maximum absolute vorticity",
                current["maximum_absolute_vorticity"],
            ),
            "dominant_shell": (
                int(spectral["dominant_shell"])
                if spectral is not None
                else None
            ),
            "tail_fraction_k_gt_4": (
                finite_float(
                    "tail fraction",
                    spectral["tail_fraction_k_gt_4"],
                )
                if spectral is not None
                else None
            ),
            "high_k_fraction_k_ge_10": (
                finite_float(
                    "high-k fraction",
                    spectral["high_k_fraction_k_ge_10"],
                )
                if spectral is not None
                else None
            ),
            "middle_k_fraction_5_le_k_le_9": (
                finite_float(
                    "middle-k fraction",
                    spectral[
                        "middle_k_fraction_5_le_k_le_9"
                    ],
                )
                if spectral is not None
                else None
            ),
            "low_k_fraction_k_le_4": (
                finite_float(
                    "low-k fraction",
                    spectral["low_k_fraction_k_le_4"],
                )
                if spectral is not None
                else None
            ),
        }

        rows.append(row)

    if len(rows) != 200:
        raise RuntimeError(
            f"expected 200 interval rows, found {len(rows)}"
        )

    return rows


def build_block_statistics(
    time_series: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []

    for block in TIME_BLOCKS:
        block_id = int(block["block_id"])

        members = [
            row
            for row in time_series
            if int(row["block_id"]) == block_id
        ]

        if not members:
            raise RuntimeError(
                f"time block {block_id} contains no intervals"
            )

        enstrophy_normalized = [
            finite_float(
                "normalized enstrophy residual",
                row["normalized_enstrophy_budget_residual"],
            )
            for row in members
        ]

        energy_normalized = [
            finite_float(
                "normalized energy residual",
                row["normalized_energy_budget_residual"],
            )
            for row in members
        ]

        signed_enstrophy = [
            finite_float(
                "signed enstrophy residual",
                row["enstrophy_budget_residual"],
            )
            for row in members
        ]

        positive = sum(value > 0.0 for value in signed_enstrophy)
        negative = sum(value < 0.0 for value in signed_enstrophy)
        zero = len(signed_enstrophy) - positive - negative

        output.append(
            {
                "block_id": block_id,
                "label": block["label"],
                "interval_count": len(members),
                "time_start": min(
                    finite_float(
                        "block time",
                        row["physical_time"],
                    )
                    for row in members
                ),
                "time_end": max(
                    finite_float(
                        "block time",
                        row["physical_time"],
                    )
                    for row in members
                ),
                "normalized_enstrophy_residual_median": median(
                    enstrophy_normalized
                ),
                "normalized_enstrophy_residual_mean": mean(
                    enstrophy_normalized
                ),
                "normalized_enstrophy_residual_maximum": max(
                    enstrophy_normalized
                ),
                "normalized_enstrophy_residual_p90": percentile(
                    enstrophy_normalized,
                    90.0,
                ),
                "normalized_energy_residual_median": median(
                    energy_normalized
                ),
                "normalized_energy_residual_mean": mean(
                    energy_normalized
                ),
                "normalized_energy_residual_maximum": max(
                    energy_normalized
                ),
                "normalized_energy_residual_p90": percentile(
                    energy_normalized,
                    90.0,
                ),
                "signed_enstrophy_residual_mean": mean(
                    signed_enstrophy
                ),
                "signed_enstrophy_residual_rms": rms(
                    signed_enstrophy
                ),
                "positive_enstrophy_residual_count": positive,
                "negative_enstrophy_residual_count": negative,
                "zero_enstrophy_residual_count": zero,
                "positive_enstrophy_residual_fraction": (
                    positive / len(members)
                ),
                "negative_enstrophy_residual_fraction": (
                    negative / len(members)
                ),
                "mean_stage1_advection_rms": mean(
                    [
                        finite_float(
                            "stage-1 advection RMS",
                            row["stage1_advection_rms"],
                        )
                        for row in members
                    ]
                ),
                "mean_stage2_advection_rms": mean(
                    [
                        finite_float(
                            "stage-2 advection RMS",
                            row["stage2_advection_rms"],
                        )
                        for row in members
                    ]
                ),
                "mean_max_stage_advection_rms": mean(
                    [
                        finite_float(
                            "maximum stage advection RMS",
                            row["max_stage_advection_rms"],
                        )
                        for row in members
                    ]
                ),
                "mean_mask_removal_rms": mean(
                    [
                        finite_float(
                            "mask removal RMS",
                            row["mask_removal_rms"],
                        )
                        for row in members
                    ]
                ),
                "mean_enstrophy": mean(
                    [
                        finite_float(
                            "enstrophy",
                            row["enstrophy"],
                        )
                        for row in members
                    ]
                ),
                "mean_absolute_observed_enstrophy_rate": mean(
                    [
                        abs(
                            finite_float(
                                "observed enstrophy rate",
                                row["observed_enstrophy_rate"],
                            )
                        )
                        for row in members
                    ]
                ),
                "mean_absolute_continuous_enstrophy_rhs": mean(
                    [
                        abs(
                            finite_float(
                                "continuous enstrophy RHS",
                                row[
                                    "mean_continuous_enstrophy_rhs"
                                ],
                            )
                        )
                        for row in members
                    ]
                ),
                "mean_enstrophy_injection_rate": mean(
                    [
                        finite_float(
                            "enstrophy injection",
                            row["enstrophy_injection_rate"],
                        )
                        for row in members
                    ]
                ),
                "mean_viscous_enstrophy_dissipation_rate": mean(
                    [
                        finite_float(
                            "enstrophy dissipation",
                            row[
                                "viscous_enstrophy_dissipation_rate"
                            ],
                        )
                        for row in members
                    ]
                ),
            }
        )

    return output


def correlation_row(
    *,
    scope: str,
    target_name: str,
    predictor_name: str,
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    target_values: list[float] = []
    predictor_values: list[float] = []

    for row in rows:
        target = row.get(target_name)
        predictor = row.get(predictor_name)

        if target is None or predictor is None:
            continue

        target_values.append(
            finite_float(target_name, target)
        )

        predictor_values.append(
            finite_float(predictor_name, predictor)
        )

    pearson = pearson_correlation(
        target_values,
        predictor_values,
    )

    spearman = spearman_correlation(
        target_values,
        predictor_values,
    )

    available = [
        abs(value)
        for value in (pearson, spearman)
        if value is not None
    ]

    maximum_absolute = max(available) if available else None

    return {
        "scope": scope,
        "target": target_name,
        "predictor": predictor_name,
        "sample_count": len(target_values),
        "pearson": pearson,
        "spearman": spearman,
        "maximum_absolute_coefficient": maximum_absolute,
        "strength": correlation_strength(maximum_absolute),
        "support_threshold": CORRELATION_SUPPORT_THRESHOLD,
        "support_threshold_met": (
            maximum_absolute is not None
            and maximum_absolute >= CORRELATION_SUPPORT_THRESHOLD
        ),
    }


def build_correlations(
    time_series: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    budget_predictors = (
        "stage1_advection_rms",
        "stage2_advection_rms",
        "max_stage_advection_rms",
        "mask_removal_rms",
        "enstrophy",
        "vorticity_rms",
        "maximum_absolute_vorticity",
        "observed_enstrophy_rate",
        "absolute_observed_enstrophy_rate",
        "mean_continuous_enstrophy_rhs",
        "absolute_mean_continuous_enstrophy_rhs",
        "enstrophy_injection_rate",
        "viscous_enstrophy_dissipation_rate",
        "mean_enstrophy_injection_rate",
        "mean_viscous_enstrophy_dissipation_rate",
    )

    spectral_predictors = (
        "dominant_shell",
        "tail_fraction_k_gt_4",
        "high_k_fraction_k_ge_10",
        "middle_k_fraction_5_le_k_le_9",
        "low_k_fraction_k_le_4",
    )

    scopes = {
        "all_budget_intervals": list(time_series),
        "final_window_budget_intervals": [
            row
            for row in time_series
            if (
                finite_float(
                    "interval start",
                    row["interval_start_time"],
                )
                >= STATIONARITY_START_TIME - 1.0e-12
                and finite_float(
                    "interval end",
                    row["physical_time"],
                )
                <= STATIONARITY_END_TIME + 1.0e-12
            )
        ],
    }

    output: list[dict[str, object]] = []

    for scope, rows in scopes.items():
        for predictor in budget_predictors:
            output.append(
                correlation_row(
                    scope=scope,
                    target_name=(
                        "normalized_enstrophy_budget_residual"
                    ),
                    predictor_name=predictor,
                    rows=rows,
                )
            )

    spectral_scopes = {
        "all_spectrum_matched_intervals": [
            row
            for row in time_series
            if row["tail_fraction_k_gt_4"] is not None
        ],
        "final_window_spectrum_matched_intervals": [
            row
            for row in time_series
            if (
                row["tail_fraction_k_gt_4"] is not None
                and finite_float(
                    "interval start",
                    row["interval_start_time"],
                )
                >= STATIONARITY_START_TIME - 1.0e-12
                and finite_float(
                    "interval end",
                    row["physical_time"],
                )
                <= STATIONARITY_END_TIME + 1.0e-12
            )
        ],
    }

    for scope, rows in spectral_scopes.items():
        for predictor in spectral_predictors:
            output.append(
                correlation_row(
                    scope=scope,
                    target_name=(
                        "normalized_enstrophy_budget_residual"
                    ),
                    predictor_name=predictor,
                    rows=rows,
                )
            )

    return output


def coarsened_intervals(
    budget_rows: Sequence[Mapping[str, object]],
    cadence: float,
) -> list[dict[str, float]]:
    multiple = cadence / BASE_CADENCE
    step = int(round(multiple))

    if not math.isclose(
        multiple,
        float(step),
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise RuntimeError(
            f"cadence {cadence} is not an exact multiple "
            f"of base cadence {BASE_CADENCE}"
        )

    intervals: list[dict[str, float]] = []

    for current_index in range(step, len(budget_rows), step):
        previous_index = current_index - step

        intervals.append(
            residual_from_endpoints(
                budget_rows[previous_index],
                budget_rows[current_index],
            )
        )

    expected_count = (len(budget_rows) - 1) // step

    if len(intervals) != expected_count:
        raise RuntimeError(
            f"cadence {cadence} produced {len(intervals)} "
            f"intervals, expected {expected_count}"
        )

    return intervals


def summarize_coarsened_scope(
    *,
    scope: str,
    cadence: float,
    intervals: Sequence[Mapping[str, float]],
) -> dict[str, object]:
    if not intervals:
        raise RuntimeError(
            f"coarsening scope {scope} at cadence {cadence} "
            "contains no intervals"
        )

    energy_normalized = [
        finite_float(
            "coarsened normalized energy residual",
            row["normalized_energy_budget_residual"],
        )
        for row in intervals
    ]

    enstrophy_normalized = [
        finite_float(
            "coarsened normalized enstrophy residual",
            row["normalized_enstrophy_budget_residual"],
        )
        for row in intervals
    ]

    energy_signed = [
        finite_float(
            "coarsened signed energy residual",
            row["energy_budget_residual"],
        )
        for row in intervals
    ]

    enstrophy_signed = [
        finite_float(
            "coarsened signed enstrophy residual",
            row["enstrophy_budget_residual"],
        )
        for row in intervals
    ]

    return {
        "scope": scope,
        "cadence": cadence,
        "cadence_multiple_of_base": cadence / BASE_CADENCE,
        "interval_count": len(intervals),
        "normalized_energy_residual_median": median(
            energy_normalized
        ),
        "normalized_energy_residual_mean": mean(
            energy_normalized
        ),
        "normalized_energy_residual_maximum": max(
            energy_normalized
        ),
        "normalized_energy_residual_p90": percentile(
            energy_normalized,
            90.0,
        ),
        "normalized_enstrophy_residual_median": median(
            enstrophy_normalized
        ),
        "normalized_enstrophy_residual_mean": mean(
            enstrophy_normalized
        ),
        "normalized_enstrophy_residual_maximum": max(
            enstrophy_normalized
        ),
        "normalized_enstrophy_residual_p90": percentile(
            enstrophy_normalized,
            90.0,
        ),
        "signed_energy_residual_mean": mean(energy_signed),
        "signed_energy_residual_rms": rms(energy_signed),
        "signed_enstrophy_residual_mean": mean(
            enstrophy_signed
        ),
        "signed_enstrophy_residual_rms": rms(
            enstrophy_signed
        ),
        "median_energy_gate_pass": (
            median(energy_normalized)
            <= MEDIAN_NORMALIZED_ENERGY_RESIDUAL_LIMIT
        ),
        "maximum_energy_gate_pass": (
            max(energy_normalized)
            <= MAX_NORMALIZED_ENERGY_RESIDUAL_LIMIT
        ),
        "median_enstrophy_gate_pass": (
            median(enstrophy_normalized)
            <= MEDIAN_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
        ),
        "maximum_enstrophy_gate_pass": (
            max(enstrophy_normalized)
            <= MAX_NORMALIZED_ENSTROPHY_RESIDUAL_LIMIT
        ),
    }


def build_coarsening(
    budget_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []

    for cadence in COARSENING_CADENCES:
        intervals = coarsened_intervals(
            budget_rows,
            cadence,
        )

        output.append(
            summarize_coarsened_scope(
                scope="full_run",
                cadence=cadence,
                intervals=intervals,
            )
        )

        final_window = [
            row
            for row in intervals
            if (
                finite_float(
                    "coarsened interval start",
                    row["interval_start_time"],
                )
                >= STATIONARITY_START_TIME - 1.0e-12
                and finite_float(
                    "coarsened interval end",
                    row["physical_time"],
                )
                <= STATIONARITY_END_TIME + 1.0e-12
            )
        ]

        output.append(
            summarize_coarsened_scope(
                scope="final_window",
                cadence=cadence,
                intervals=final_window,
            )
        )

    return output


def cadence_support_metrics(
    coarsening_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    final_rows = sorted(
        [
            row
            for row in coarsening_rows
            if row["scope"] == "final_window"
        ],
        key=lambda row: finite_float(
            "cadence",
            row["cadence"],
        ),
    )

    medians = [
        finite_float(
            "final-window median enstrophy residual",
            row["normalized_enstrophy_residual_median"],
        )
        for row in final_rows
    ]

    cadences = [
        finite_float("cadence", row["cadence"])
        for row in final_rows
    ]

    successive_increases = sum(
        second > first * (1.0 + 1.0e-12)
        for first, second in zip(medians, medians[1:])
    )

    baseline = medians[0]
    coarsest = medians[-1]

    factor = (
        coarsest / baseline
        if baseline != 0.0
        else math.inf
    )

    supported = (
        successive_increases
        >= CADENCE_REQUIRED_SUCCESSIVE_INCREASES
        and factor >= CADENCE_FACTOR_THRESHOLD
    )

    return {
        "cadences": cadences,
        "final_window_median_normalized_enstrophy_residuals": (
            medians
        ),
        "successive_increase_count": successive_increases,
        "required_successive_increases": (
            CADENCE_REQUIRED_SUCCESSIVE_INCREASES
        ),
        "coarsest_to_base_median_factor": factor,
        "required_factor": CADENCE_FACTOR_THRESHOLD,
        "supported": supported,
    }


def operator_support_metrics(
    correlations: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    operator_predictors = {
        "stage1_advection_rms",
        "stage2_advection_rms",
        "max_stage_advection_rms",
        "mask_removal_rms",
    }

    candidates = [
        row
        for row in correlations
        if (
            row["predictor"] in operator_predictors
            and row["scope"] in {
                "all_budget_intervals",
                "final_window_budget_intervals",
            }
            and row["maximum_absolute_coefficient"] is not None
        )
    ]

    if not candidates:
        return {
            "supported": False,
            "strongest": None,
            "support_threshold": CORRELATION_SUPPORT_THRESHOLD,
        }

    strongest = max(
        candidates,
        key=lambda row: finite_float(
            "correlation coefficient",
            row["maximum_absolute_coefficient"],
        ),
    )

    maximum = finite_float(
        "maximum operator correlation",
        strongest["maximum_absolute_coefficient"],
    )

    return {
        "supported": maximum >= CORRELATION_SUPPORT_THRESHOLD,
        "strongest": dict(strongest),
        "support_threshold": CORRELATION_SUPPORT_THRESHOLD,
    }


def stage_a_classification(
    cadence_metrics: Mapping[str, object],
    operator_metrics: Mapping[str, object],
) -> str:
    cadence = bool(cadence_metrics["supported"])
    operator = bool(operator_metrics["supported"])

    if cadence and operator:
        return CLASSIFICATION_MULTIPLE

    if cadence:
        return CLASSIFICATION_CADENCE

    if operator:
        return CLASSIFICATION_OPERATOR

    return CLASSIFICATION_INCONCLUSIVE


def markdown_float(value: object) -> str:
    if value is None:
        return "undefined"

    return f"{finite_float('report value', value):.12e}"


def markdown_bool(value: object) -> str:
    return "PASS" if bool(value) else "FAIL"


def build_report(
    *,
    created_utc: str,
    execution_commit: str,
    source_hashes: Mapping[str, str],
    summary_json: Mapping[str, object],
    block_rows: Sequence[Mapping[str, object]],
    correlations: Sequence[Mapping[str, object]],
    coarsening_rows: Sequence[Mapping[str, object]],
    cadence_metrics: Mapping[str, object],
    operator_metrics: Mapping[str, object],
    classification: str,
) -> str:
    final_window_coarsening = sorted(
        [
            row
            for row in coarsening_rows
            if row["scope"] == "final_window"
        ],
        key=lambda row: finite_float(
            "cadence",
            row["cadence"],
        ),
    )

    all_budget_correlations = sorted(
        [
            row
            for row in correlations
            if (
                row["scope"] == "all_budget_intervals"
                and row["maximum_absolute_coefficient"]
                is not None
            )
        ],
        key=lambda row: finite_float(
            "correlation coefficient",
            row["maximum_absolute_coefficient"],
        ),
        reverse=True,
    )

    spectral_correlations = sorted(
        [
            row
            for row in correlations
            if (
                "spectrum_matched" in str(row["scope"])
                and row["maximum_absolute_coefficient"]
                is not None
            )
        ],
        key=lambda row: finite_float(
            "spectral correlation coefficient",
            row["maximum_absolute_coefficient"],
        ),
        reverse=True,
    )

    stationarity = summary_json["stationarity_analysis"]

    lines: list[str] = [
        "# Stage A Enstrophy-Residual Archived-Evidence Analysis",
        "",
        "## 0. Document control",
        "",
        "- Repository: `Raj-Sanghera-Project`",
        "- Branch: `phase4_validation`",
        f"- Stage A execution commit: `{execution_commit}`",
        f"- Design commit: `{AUTHORIZED_DESIGN_COMMIT}`",
        f"- Created UTC: `{created_utc}`",
        "- Analysis type: read-only analysis of archived CSV and JSON files",
        "- Solver execution: none",
        "- Numerical timestep execution: none",
        "- Archived evidence modification: none",
        "- Causal attribution claim: none",
        "",
        "---",
        "",
        "## 1. Stage A decision",
        "",
        f"> **{classification}**",
        "",
        "This is a descriptive archived-data classification. It does not "
        "causally identify the residual source.",
        "",
        "The archived longer-run classification remains:",
        "",
        "> **NOT STATIONARY WITHIN TESTED DURATION**",
        "",
        "---",
        "",
        "## 2. Source identities",
        "",
        "| Archived file | SHA-256 |",
        "|---|---|",
    ]

    for name, digest in source_hashes.items():
        lines.append(f"| `{name}` | `{digest}` |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## 3. Baseline that remains established",
            "",
            "Independent of residual closure, the final-window enstrophy "
            "drift and injection-dissipation balance failed.",
            "",
            "| Metric | Observed |",
            "|---|---:|",
            (
                "| Enstrophy normalized drift | "
                f"`{stationarity['trends']['enstrophy']['normalized_window_drift']}` |"
            ),
            (
                "| Enstrophy balance metric | "
                f"`{stationarity['balance']['enstrophy_balance_metric']}` |"
            ),
            (
                "| Mean enstrophy injection | "
                f"`{stationarity['window_means']['enstrophy_injection_rate']}` |"
            ),
            (
                "| Mean enstrophy dissipation | "
                f"`{stationarity['window_means']['viscous_enstrophy_dissipation_rate']}` |"
            ),
            "",
            "Therefore, improved residual closure would not by itself "
            "convert the archived result into a stationarity candidate.",
            "",
            "---",
            "",
            "## 4. Five-block residual statistics",
            "",
            "| Block | Intervals | Median normalized Z residual | "
            "Maximum normalized Z residual | P90 | "
            "Mean max-stage advection RMS | Mean mask-removal RMS |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for row in block_rows:
        lines.append(
            "| "
            f"{row['label']} | "
            f"{row['interval_count']} | "
            f"{markdown_float(row['normalized_enstrophy_residual_median'])} | "
            f"{markdown_float(row['normalized_enstrophy_residual_maximum'])} | "
            f"{markdown_float(row['normalized_enstrophy_residual_p90'])} | "
            f"{markdown_float(row['mean_max_stage_advection_rms'])} | "
            f"{markdown_float(row['mean_mask_removal_rms'])} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 5. Strongest archived budget correlations",
            "",
            "Target: `normalized_enstrophy_budget_residual`.",
            "",
            "| Scope | Predictor | n | Pearson | Spearman | "
            "Largest absolute coefficient | Strength |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )

    for row in all_budget_correlations[:10]:
        lines.append(
            "| "
            f"{row['scope']} | "
            f"`{row['predictor']}` | "
            f"{row['sample_count']} | "
            f"{markdown_float(row['pearson'])} | "
            f"{markdown_float(row['spearman'])} | "
            f"{markdown_float(row['maximum_absolute_coefficient'])} | "
            f"{row['strength']} |"
        )

    lines.extend(
        [
            "",
            "Correlation is descriptive. Advection RMS and mask-removal "
            "RMS are magnitudes, not exact enstrophy-work or mask-loss "
            "terms.",
            "",
            "---",
            "",
            "## 6. Spectral-tail correlations at exact matching times",
            "",
            "| Scope | Predictor | n | Pearson | Spearman | "
            "Largest absolute coefficient | Strength |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )

    for row in spectral_correlations:
        lines.append(
            "| "
            f"{row['scope']} | "
            f"`{row['predictor']}` | "
            f"{row['sample_count']} | "
            f"{markdown_float(row['pearson'])} | "
            f"{markdown_float(row['spearman'])} | "
            f"{markdown_float(row['maximum_absolute_coefficient'])} | "
            f"{row['strength']} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 7. Offline cadence coarsening",
            "",
            "All rows use the same archived trajectory. Only interval "
            "endpoint spacing changes.",
            "",
            "| Cadence | Final-window intervals | Median normalized E residual | "
            "Maximum normalized E residual | Median normalized Z residual | "
            "Maximum normalized Z residual | Z median gate | Z max gate |",
            "|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )

    for row in final_window_coarsening:
        lines.append(
            "| "
            f"{row['cadence']} | "
            f"{row['interval_count']} | "
            f"{markdown_float(row['normalized_energy_residual_median'])} | "
            f"{markdown_float(row['normalized_energy_residual_maximum'])} | "
            f"{markdown_float(row['normalized_enstrophy_residual_median'])} | "
            f"{markdown_float(row['normalized_enstrophy_residual_maximum'])} | "
            f"{markdown_bool(row['median_enstrophy_gate_pass'])} | "
            f"{markdown_bool(row['maximum_enstrophy_gate_pass'])} |"
        )

    lines.extend(
        [
            "",
            "This coarsening test can show whether residuals worsen when "
            "diagnostic intervals become wider. It cannot determine the "
            "sub-0.5 limit because no finer archived states exist.",
            "",
            "---",
            "",
            "## 8. Stage A support tests",
            "",
            "### 8.1 Cadence sensitivity",
            "",
            f"- Supported: `{cadence_metrics['supported']}`",
            (
                "- Successive median increases: "
                f"`{cadence_metrics['successive_increase_count']}` "
                f"of required `{cadence_metrics['required_successive_increases']}`"
            ),
            (
                "- Coarsest/base final-window median factor: "
                f"`{cadence_metrics['coarsest_to_base_median_factor']}` "
                f"with required factor `{cadence_metrics['required_factor']}`"
            ),
            "",
            "### 8.2 Operator-magnitude correlation",
            "",
            f"- Supported: `{operator_metrics['supported']}`",
            (
                "- Correlation support threshold: "
                f"`{operator_metrics['support_threshold']}`"
            ),
        ]
    )

    strongest = operator_metrics.get("strongest")

    if strongest is None:
        lines.append("- Strongest archived operator-magnitude correlation: undefined")
    else:
        lines.extend(
            [
                (
                    "- Strongest scope/predictor: "
                    f"`{strongest['scope']}` / `{strongest['predictor']}`"
                ),
                (
                    "- Largest absolute Pearson/Spearman coefficient: "
                    f"`{strongest['maximum_absolute_coefficient']}`"
                ),
            ]
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## 9. What Stage A can and cannot resolve",
            "",
            "Stage A can identify time dependence, coarsening sensitivity, "
            "and descriptive associations.",
            "",
            "Stage A cannot directly calculate:",
            "",
            "- discrete advection enstrophy work;",
            "- exact pre-mask to post-mask enstrophy loss;",
            "- RK2 local temporal error;",
            "- residual behavior below the archived 0.5 cadence.",
            "",
            "Those require the operator-ledger replay and same-state shadow "
            "tests defined in the archived design.",
            "",
            "---",
            "",
            "## 10. Final interpretation",
            "",
            f"The Stage A classification is **{classification}**.",
            "",
            "Regardless of that descriptive classification, the archived "
            "evidence already establishes genuine continuing modeled "
            "enstrophy evolution over the final window: enstrophy declined "
            "and mean dissipation exceeded mean injection.",
            "",
            "No new numerical execution was performed.",
            "",
            "---",
            "",
            "## 11. Claim boundaries",
            "",
            "This analysis does not establish:",
            "",
            "- formal temporal convergence;",
            "- formal spatial convergence;",
            "- causal operator attribution;",
            "- physical validation;",
            "- turbulence;",
            "- a cascade;",
            "- an inertial range;",
            "- a `k^-3` law;",
            "- method superiority.",
            "",
            "The next permitted task is design review for the exact "
            "operator ledger. No replay is authorized by this report.",
            "",
        ]
    )

    return "\n".join(lines)


def verify_source_files(
    repo: Path,
) -> dict[str, str]:
    design = repo / DESIGN_PATH

    if not design.is_file():
        raise RuntimeError(
            f"design file is missing: {DESIGN_PATH}"
        )

    observed_design_hash = sha256_file(design)

    if observed_design_hash != EXPECTED_DESIGN_SHA256:
        raise RuntimeError(
            f"design SHA256 is {observed_design_hash}, "
            f"expected {EXPECTED_DESIGN_SHA256}"
        )

    source_directory = repo / SOURCE_RUN
    observed: dict[str, str] = {}

    for name, expected in SOURCE_HASHES.items():
        path = source_directory / name

        if not path.is_file():
            raise RuntimeError(
                f"archived source file is missing: "
                f"{path.relative_to(repo)}"
            )

        digest = sha256_file(path)
        observed[name] = digest

        if digest != expected:
            raise RuntimeError(
                f"source hash mismatch for {name}: {digest}"
            )

    inventory_rows = read_csv_rows(
        source_directory / "file_inventory.csv"
    )

    inventory_map = {
        row["relative_path"]: row["sha256"]
        for row in inventory_rows
        if row["sha256"].strip() != ""
    }

    for name in SOURCE_HASHES:
        if name == "file_inventory.csv":
            continue

        if inventory_map.get(name) != SOURCE_HASHES[name]:
            raise RuntimeError(
                f"archive inventory does not confirm {name}"
            )

    return observed


def verify_runner_commit_shape(
    repo: Path,
    runner: Path,
) -> str:
    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        raise RuntimeError("active branch is not phase4_validation")

    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )

    if status != "":
        raise RuntimeError("working tree is not clean")

    head = git_read(repo, "rev-parse", "HEAD")
    parent = git_read(repo, "rev-parse", "HEAD^")

    if parent != AUTHORIZED_DESIGN_COMMIT:
        raise RuntimeError(
            f"runner commit parent is {parent}, "
            f"expected {AUTHORIZED_DESIGN_COMMIT}"
        )

    changed = git_read(
        repo,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "HEAD",
    ).splitlines()

    if changed != [runner.name]:
        raise RuntimeError(
            f"runner commit changed unexpected files: {changed!r}"
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
        raise RuntimeError("runner is not tracked")

    committed_bytes = git_bytes(
        repo,
        "show",
        f"HEAD:{runner.name}",
    )

    working_bytes = runner.read_bytes()

    if committed_bytes != working_bytes:
        raise RuntimeError(
            "working runner bytes differ from the committed runner"
        )

    return head


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

    if status != [f"?? {runner.name}"]:
        fail(f"unexpected Git status: {status!r}")

    try:
        verify_source_files(repo)
    except RuntimeError as error:
        fail(str(error))

    actual_solver_run_lines: list[int] = []
    project_imports: list[tuple[str, int]] = []
    forbidden_calls: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""

            if (
                module.startswith("project")
                or module == "forcing_budget_diagnostic"
            ):
                project_imports.append((module, node.lineno))

        if not isinstance(node, ast.Call):
            continue

        if isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec"}:
                forbidden_calls.append(
                    (node.func.id, node.lineno)
                )

        if isinstance(node.func, ast.Attribute):
            owner = node.func.value

            if (
                node.func.attr == "run"
                and isinstance(owner, ast.Name)
                and owner.id == "solver"
            ):
                actual_solver_run_lines.append(node.lineno)

    if project_imports:
        fail(f"project imports are present: {project_imports!r}")

    if actual_solver_run_lines:
        fail(
            f"solver.run calls are present: "
            f"{actual_solver_run_lines!r}"
        )

    if forbidden_calls:
        fail(
            f"dynamic execution calls are present: "
            f"{forbidden_calls!r}"
        )

    required_functions = {
        "verify_source_files",
        "verify_runner_commit_shape",
        "parse_budget_rows",
        "parse_spectrum_summaries",
        "build_time_series",
        "build_block_statistics",
        "build_correlations",
        "build_coarsening",
        "build_report",
        "inspect_runner",
        "execute_analysis",
        "main",
    }

    observed_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    missing = required_functions - observed_functions

    if missing:
        fail(f"required functions are missing: {sorted(missing)}")

    required_fragments = (
        "COARSENING_CADENCES = (0.5, 1.0, 2.0, 2.5, 5.0)",
        "normalized_enstrophy_budget_residual",
        "stage1_advection_rms",
        "stage2_advection_rms",
        "mask_removal_rms",
        "enstrophy_injection_rate",
        "viscous_enstrophy_dissipation_rate",
        "tail_fraction_k_gt_4",
        "high_k_fraction_k_ge_10",
        "ARCHIVED DATA SUPPORTS CADENCE SENSITIVITY",
        "ARCHIVED DATA SUPPORTS OPERATOR CORRELATION",
        "ARCHIVED DATA INCONCLUSIVE",
        "ARCHIVED DATA SHOWS MULTIPLE CONTRIBUTORS",
        'if arguments.mode == "inspect":',
        'if arguments.mode == "run":',
    )

    for fragment in required_fragments:
        if fragment not in source:
            fail(f"required fragment is absent: {fragment}")

    print()
    print("=" * 72)
    print("STAGE A READ-ONLY ANALYSIS RUNNER INSPECTION: PASS")
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", sha256_bytes(raw))
    print("Design commit:", AUTHORIZED_DESIGN_COMMIT)
    print("Design SHA256:", EXPECTED_DESIGN_SHA256)
    print("Archived source hashes: PASS")
    print("Budget intervals expected: 200")
    print("Time blocks: 5")
    print("Correlations: Pearson and Spearman")
    print("Spectrum joins: exact loop-index matches only")
    print("Coarsening cadences: 0.5, 1.0, 2.0, 2.5, 5.0")
    print("Project modules imported: NO")
    print("Solver constructed: NO")
    print("Solver executed: NO")
    print("Archived evidence modified: NO")
    print("Analysis outputs written by inspection: NO")
    print("Git mutations: NONE")
    print("Stage A execution authorized by inspection: NO")

    return 0


def write_output_inventory(
    directory: Path,
    inventory_path: Path,
    paths: Sequence[Path],
) -> None:
    rows: list[dict[str, object]] = []

    for path in paths:
        rows.append(
            {
                "relative_path": path.name,
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
                "self-hash omitted to avoid circular self-reference"
            ),
        }
    )

    atomic_write_csv(
        inventory_path,
        rows,
        INVENTORY_FIELDNAMES,
    )


def execute_analysis(repo: Path) -> int:
    runner = Path(__file__).resolve()

    execution_commit = verify_runner_commit_shape(
        repo,
        runner,
    )

    source_hashes = verify_source_files(repo)
    source_directory = repo / SOURCE_RUN

    output_root = repo / OUTPUT_ROOT

    existing = (
        sorted(output_root.glob(f"{RUN_PREFIX}*"))
        if output_root.is_dir()
        else []
    )

    if existing:
        raise RuntimeError(
            "a Stage A analysis output already exists; "
            "do not create a duplicate: "
            + ", ".join(str(path) for path in existing)
        )

    if not path_is_git_ignored(
        repo,
        output_root / f"{RUN_PREFIX}probe",
    ):
        raise RuntimeError(
            "planned Stage A output is not Git-ignored"
        )

    created = utc_now()
    created_utc = utc_text(created)
    stamp = created.strftime("%Y%m%dT%H%M%SZ")

    run_id = (
        f"{RUN_PREFIX}{stamp}_{execution_commit[:7]}"
    )

    final_directory = output_root / run_id
    temporary_directory = output_root / (
        "." + run_id + ".tmp"
    )

    if final_directory.exists() or temporary_directory.exists():
        raise RuntimeError("planned analysis directory already exists")

    output_root.mkdir(parents=True, exist_ok=True)
    temporary_directory.mkdir(parents=False, exist_ok=False)

    try:
        budget_raw = read_csv_rows(
            source_directory / "forcing_budget.csv"
        )

        spectra_raw = read_csv_rows(
            source_directory / "forcing_spectra.csv"
        )

        window_raw = read_csv_rows(
            source_directory / "stationarity_window.csv"
        )

        summary_json = read_json(
            source_directory / "stationarity_summary.json"
        )

        metadata_json = read_json(
            source_directory / "run_metadata.json"
        )

        if len(budget_raw) != 201:
            raise RuntimeError(
                f"expected 201 budget rows, found {len(budget_raw)}"
            )

        if len(spectra_raw) != 1845:
            raise RuntimeError(
                f"expected 1845 spectrum rows, found {len(spectra_raw)}"
            )

        if len(window_raw) != 41:
            raise RuntimeError(
                f"expected 41 stationarity-window rows, "
                f"found {len(window_raw)}"
            )

        if (
            summary_json.get("classification")
            != "NOT STATIONARY WITHIN TESTED DURATION"
        ):
            raise RuntimeError(
                "archived summary classification is unexpected"
            )

        if metadata_json.get("status") != "completed":
            raise RuntimeError(
                "archived run metadata is not completed"
            )

        budget_rows = parse_budget_rows(budget_raw)

        spectrum_summaries = parse_spectrum_summaries(
            spectra_raw
        )

        time_series = build_time_series(
            budget_rows,
            spectrum_summaries,
        )

        block_rows = build_block_statistics(
            time_series
        )

        correlations = build_correlations(
            time_series
        )

        coarsening_rows = build_coarsening(
            budget_rows
        )

        cadence_metrics = cadence_support_metrics(
            coarsening_rows
        )

        operator_metrics = operator_support_metrics(
            correlations
        )

        classification = stage_a_classification(
            cadence_metrics,
            operator_metrics,
        )

        report = build_report(
            created_utc=created_utc,
            execution_commit=execution_commit,
            source_hashes=source_hashes,
            summary_json=summary_json,
            block_rows=block_rows,
            correlations=correlations,
            coarsening_rows=coarsening_rows,
            cadence_metrics=cadence_metrics,
            operator_metrics=operator_metrics,
            classification=classification,
        )

        time_series_path = (
            temporary_directory
            / "stage_a_residual_timeseries.csv"
        )

        block_path = (
            temporary_directory
            / "stage_a_time_block_statistics.csv"
        )

        correlation_path = (
            temporary_directory
            / "stage_a_correlations.csv"
        )

        coarsening_path = (
            temporary_directory
            / "stage_a_coarsening.csv"
        )

        summary_path = (
            temporary_directory
            / "stage_a_summary.json"
        )

        report_path = (
            temporary_directory
            / "STAGE_A_ENSTROPHY_RESIDUAL_ATTRIBUTION_REPORT.md"
        )

        inventory_path = (
            temporary_directory
            / "file_inventory.csv"
        )

        atomic_write_csv(
            time_series_path,
            time_series,
            TIME_SERIES_FIELDNAMES,
        )

        atomic_write_csv(
            block_path,
            block_rows,
            BLOCK_FIELDNAMES,
        )

        atomic_write_csv(
            correlation_path,
            correlations,
            CORRELATION_FIELDNAMES,
        )

        atomic_write_csv(
            coarsening_path,
            coarsening_rows,
            COARSENING_FIELDNAMES,
        )

        summary = {
            "schema_id": "STAGE_A_ENSTROPHY_RESIDUAL_ANALYSIS_V1",
            "run_id": run_id,
            "classification": classification,
            "created_utc": created_utc,
            "completed_utc": utc_text(),
            "repository": {
                "branch": "phase4_validation",
                "execution_commit": execution_commit,
                "runner_path": runner.name,
                "runner_sha256": sha256_file(runner),
                "design_path": DESIGN_PATH.as_posix(),
                "design_commit": AUTHORIZED_DESIGN_COMMIT,
                "design_sha256": EXPECTED_DESIGN_SHA256,
            },
            "source_run": {
                "path": SOURCE_RUN.as_posix(),
                "file_hashes": source_hashes,
                "archived_classification": (
                    summary_json["classification"]
                ),
            },
            "counts": {
                "budget_snapshots": len(budget_rows),
                "budget_intervals": len(time_series),
                "spectrum_rows": len(spectra_raw),
                "spectrum_snapshots": len(spectrum_summaries),
                "stationarity_window_rows": len(window_raw),
                "time_blocks": len(block_rows),
                "correlation_rows": len(correlations),
                "coarsening_rows": len(coarsening_rows),
            },
            "cadence_support": cadence_metrics,
            "operator_correlation_support": operator_metrics,
            "classification_logic": {
                "correlation_support_threshold": (
                    CORRELATION_SUPPORT_THRESHOLD
                ),
                "cadence_factor_threshold": (
                    CADENCE_FACTOR_THRESHOLD
                ),
                "cadence_required_successive_increases": (
                    CADENCE_REQUIRED_SUCCESSIVE_INCREASES
                ),
            },
            "limitations": {
                "sub_0_5_cadence_available": False,
                "exact_advection_enstrophy_work_available": False,
                "exact_mask_enstrophy_loss_available": False,
                "rk2_shadow_tests_available": False,
                "causal_attribution_authorized": False,
                "solver_executed": False,
                "archived_evidence_modified": False,
            },
            "outputs": {
                "residual_timeseries": time_series_path.name,
                "time_block_statistics": block_path.name,
                "correlations": correlation_path.name,
                "coarsening": coarsening_path.name,
                "summary": summary_path.name,
                "report": report_path.name,
                "inventory": inventory_path.name,
            },
        }

        atomic_write_json(
            summary_path,
            summary,
        )

        atomic_write_text(
            report_path,
            report,
        )

        write_output_inventory(
            temporary_directory,
            inventory_path,
            (
                time_series_path,
                block_path,
                correlation_path,
                coarsening_path,
                summary_path,
                report_path,
            ),
        )

        temporary_directory.replace(final_directory)

    except BaseException:
        if temporary_directory.exists():
            shutil.rmtree(temporary_directory)

        raise

    final_summary_path = (
        final_directory
        / "stage_a_summary.json"
    )

    final_summary = read_json(final_summary_path)

    strongest = final_summary[
        "operator_correlation_support"
    ].get("strongest")

    print()
    print("=" * 72)
    print("STAGE A READ-ONLY ARCHIVED-EVIDENCE ANALYSIS: COMPLETE")
    print("=" * 72)
    print("Classification:", final_summary["classification"])
    print("Output directory:", final_directory)
    print("Budget intervals:", len(time_series))
    print("Time blocks:", len(block_rows))
    print("Correlation rows:", len(correlations))
    print("Coarsening rows:", len(coarsening_rows))
    print(
        "Cadence sensitivity supported:",
        cadence_metrics["supported"],
    )
    print(
        "Coarsest/base final-window median factor:",
        f"{float(cadence_metrics['coarsest_to_base_median_factor']):.12e}",
    )
    print(
        "Operator-magnitude correlation supported:",
        operator_metrics["supported"],
    )

    if strongest is not None:
        print(
            "Strongest operator correlation:",
            strongest["scope"],
            "/",
            strongest["predictor"],
            "/",
            f"{float(strongest['maximum_absolute_coefficient']):.12e}",
        )

    print("Solver executed: NO")
    print("Numerical steps executed: 0")
    print("Archived evidence modified: NO")
    print("Causal attribution authorized: NO")
    print("Report:", final_directory / (
        "STAGE_A_ENSTROPHY_RESIDUAL_ATTRIBUTION_REPORT.md"
    ))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the read-only Stage A analysis "
            "of the archived enstrophy-residual evidence."
        )
    )

    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help=(
            "inspect the analysis source without output, "
            "or run the archived-data analysis"
        ),
    )

    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent

    if arguments.mode == "inspect":
        return inspect_runner(repo)

    if arguments.mode == "run":
        return execute_analysis(repo)

    raise RuntimeError(f"unsupported mode: {arguments.mode!r}")


if __name__ == "__main__":
    raise SystemExit(main())
