"""
Controlled analytic pilot for the standalone forcing-budget diagnostic.

The runner reproduces the protected solver's RK2 step externally. It does
not call the protected solver run loop and does not modify project source
files.

This is an analytic forced-diffusion pilot, not a turbulence, cascade,
spectral-law, convergence, or physical-validation experiment.
"""

from __future__ import annotations

import csv
import datetime
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np


N = 64
RE = 1000
DT = 0.005
STEPS = 1001
OUTPUT_INTERVAL = 100

FORCING_AMPLITUDE = 0.01
FORCING_EIGENVALUE = 8.0
EXPECTED_FORCING_RMS = 0.005

RELATIVE_ERROR_TOLERANCE = 1.0e-8
ADVECTION_RMS_TOLERANCE = 1.0e-12
MASK_REMOVAL_RMS_TOLERANCE = 1.0e-12
FORCING_RMS_TOLERANCE = 1.0e-14

EXPECTED_SOLVER_SHA256 = (
    "1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1"
)

EXPECTED_BUDGET_SHA256 = (
    "A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B"
)

OUTPUT_ROOT = Path("experiments") / "forcing_budget_pilot"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest().upper()


def git_read(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        shell=False,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    ).stdout.strip()


def write_json(path: Path, value: object) -> None:
    text = json.dumps(
        value,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    )

    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def relative_error(observed: float, expected: float) -> float:
    denominator = max(abs(expected), np.finfo(np.float64).tiny)
    return abs(observed - expected) / denominator


def exact_single_mode_reference(
    *,
    physical_time: float,
    nu: float,
) -> dict[str, float]:
    amplitude = (
        FORCING_AMPLITUDE
        / (FORCING_EIGENVALUE * nu)
        * (
            1.0
            - math.exp(
                -FORCING_EIGENVALUE
                * nu
                * physical_time
            )
        )
    )

    energy = amplitude * amplitude / 64.0
    enstrophy = amplitude * amplitude / 8.0

    energy_injection_rate = (
        amplitude * FORCING_AMPLITUDE / 32.0
    )

    enstrophy_injection_rate = (
        amplitude * FORCING_AMPLITUDE / 4.0
    )

    viscous_energy_dissipation_rate = (
        nu * amplitude * amplitude / 4.0
    )

    viscous_enstrophy_dissipation_rate = (
        2.0 * nu * amplitude * amplitude
    )

    return {
        "exact_amplitude": amplitude,
        "exact_energy": energy,
        "exact_enstrophy": enstrophy,
        "exact_energy_injection_rate": energy_injection_rate,
        "exact_enstrophy_injection_rate": (
            enstrophy_injection_rate
        ),
        "exact_viscous_energy_dissipation_rate": (
            viscous_energy_dissipation_rate
        ),
        "exact_viscous_enstrophy_dissipation_rate": (
            viscous_enstrophy_dissipation_rate
        ),
        "exact_continuous_energy_rhs": (
            energy_injection_rate
            - viscous_energy_dissipation_rate
        ),
        "exact_continuous_enstrophy_rhs": (
            enstrophy_injection_rate
            - viscous_enstrophy_dissipation_rate
        ),
    }


def external_rk2_step(
    solver: object,
    forcing: np.ndarray,
) -> dict[str, float]:
    current = np.asarray(solver.w)

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
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write an empty forcing-budget table")

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    repo = Path(__file__).resolve().parent

    solver_path = (
        repo / "project" / "solver" / "spectral_solver.py"
    )

    budget_path = repo / "forcing_budget_diagnostic.py"

    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        raise RuntimeError("active branch is not phase4_validation")

    if git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ):
        raise RuntimeError("working tree is not clean")

    if sha256_file(solver_path) != EXPECTED_SOLVER_SHA256:
        raise RuntimeError("protected spectral solver hash changed")

    if sha256_file(budget_path) != EXPECTED_BUDGET_SHA256:
        raise RuntimeError("forcing-budget diagnostic hash changed")

    head = git_read(repo, "rev-parse", "HEAD")

    from forcing_budget_diagnostic import (
        forcing_budget_interval,
        forcing_budget_snapshot,
    )

    from project.solver.spectral_solver import SpectralSolver

    created = datetime.datetime.now(datetime.timezone.utc)
    created_utc = created.replace(microsecond=0).isoformat()
    stamp = created.strftime("%Y%m%dT%H%M%SZ")

    run_id = (
        f"forcing_budget_analytic_{stamp}_{head[:7]}"
    )

    run_directory = repo / OUTPUT_ROOT / run_id
    run_directory.mkdir(parents=True, exist_ok=False)

    metadata_path = run_directory / "run_metadata.json"
    table_path = run_directory / "forcing_budget.csv"
    summary_path = run_directory / "summary.json"

    metadata: dict[str, object] = {
        "run_id": run_id,
        "status": "running",
        "created_utc": created_utc,
        "repository": {
            "branch": "phase4_validation",
            "commit": head,
            "runner_sha256": sha256_file(Path(__file__)),
            "spectral_solver_sha256": EXPECTED_SOLVER_SHA256,
            "forcing_budget_diagnostic_sha256": (
                EXPECTED_BUDGET_SHA256
            ),
        },
        "configuration": {
            "grid": N,
            "Re": RE,
            "nu": 1.0 / RE,
            "dt": DT,
            "steps": STEPS,
            "output_interval": OUTPUT_INTERVAL,
            "initial_vorticity": "zero",
            "forcing": "0.01*sin(2X)*cos(2Y)",
            "forcing_rms": EXPECTED_FORCING_RMS,
            "time_integrator": "external mirror of protected RK2",
            "solver_run_called": False,
        },
        "claims": {
            "convergence": False,
            "physical_validation": False,
            "turbulence": False,
            "cascade": False,
            "k_minus_3": False,
            "method_superiority": False,
        },
    }

    write_json(metadata_path, metadata)

    try:
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

        forcing = np.asarray(
            solver.forcing(),
            dtype=np.float64,
        )

        forcing_rms = float(
            np.sqrt(np.mean(forcing * forcing))
        )

        if abs(
            forcing_rms - EXPECTED_FORCING_RMS
        ) > FORCING_RMS_TOLERANCE:
            raise RuntimeError(
                f"unexpected forcing RMS: {forcing_rms}"
            )

        rows: list[dict[str, object]] = []
        previous_snapshot: dict[str, float | int] | None = None

        for loop_index in range(STEPS):
            step_metrics = external_rk2_step(
                solver,
                forcing,
            )

            should_record = (
                loop_index % OUTPUT_INTERVAL == 0
                or loop_index == STEPS - 1
            )

            if not should_record:
                continue

            snapshot = forcing_budget_snapshot(
                omega=solver.w,
                forcing=forcing,
                nu=solver.nu,
                kx=solver.kx,
                ky=solver.ky,
                dt=DT,
                loop_index=loop_index,
            )

            exact = exact_single_mode_reference(
                physical_time=float(snapshot["physical_time"]),
                nu=solver.nu,
            )

            row: dict[str, object] = {
                **snapshot,
                **exact,
                **step_metrics,
                "energy_relative_error": relative_error(
                    float(snapshot["energy"]),
                    exact["exact_energy"],
                ),
                "enstrophy_relative_error": relative_error(
                    float(snapshot["enstrophy"]),
                    exact["exact_enstrophy"],
                ),
                "energy_injection_relative_error": relative_error(
                    float(snapshot["energy_injection_rate"]),
                    exact["exact_energy_injection_rate"],
                ),
                "enstrophy_injection_relative_error": relative_error(
                    float(snapshot["enstrophy_injection_rate"]),
                    exact["exact_enstrophy_injection_rate"],
                ),
                "viscous_energy_dissipation_relative_error": relative_error(
                    float(snapshot["viscous_energy_dissipation_rate"]),
                    exact["exact_viscous_energy_dissipation_rate"],
                ),
                "viscous_enstrophy_dissipation_relative_error": relative_error(
                    float(snapshot["viscous_enstrophy_dissipation_rate"]),
                    exact["exact_viscous_enstrophy_dissipation_rate"],
                ),
                "interval_duration": None,
                "observed_energy_rate": None,
                "mean_continuous_energy_rhs": None,
                "energy_budget_residual": None,
                "observed_enstrophy_rate": None,
                "mean_continuous_enstrophy_rhs": None,
                "enstrophy_budget_residual": None,
            }

            if previous_snapshot is not None:
                row.update(
                    forcing_budget_interval(
                        previous_snapshot,
                        snapshot,
                    )
                )

            rows.append(row)
            previous_snapshot = snapshot

        write_csv(table_path, rows)

        max_energy_error = max(
            float(row["energy_relative_error"])
            for row in rows
        )

        max_enstrophy_error = max(
            float(row["enstrophy_relative_error"])
            for row in rows
        )

        max_energy_injection_error = max(
            float(row["energy_injection_relative_error"])
            for row in rows
        )

        max_enstrophy_injection_error = max(
            float(row["enstrophy_injection_relative_error"])
            for row in rows
        )

        max_viscous_energy_error = max(
            float(row["viscous_energy_dissipation_relative_error"])
            for row in rows
        )

        max_viscous_enstrophy_error = max(
            float(row["viscous_enstrophy_dissipation_relative_error"])
            for row in rows
        )

        max_advection_rms = max(
            max(
                float(row["stage1_advection_rms"]),
                float(row["stage2_advection_rms"]),
            )
            for row in rows
        )

        max_mask_removal_rms = max(
            float(row["mask_removal_rms"])
            for row in rows
        )

        final = rows[-1]

        checks = {
            "snapshot_count_is_11": len(rows) == 11,
            "final_loop_index_is_1000": (
                int(final["loop_index"]) == 1000
            ),
            "final_completed_steps_is_1001": (
                int(final["completed_steps"]) == 1001
            ),
            "final_time_is_5_005": math.isclose(
                float(final["physical_time"]),
                5.005,
                rel_tol=0.0,
                abs_tol=1.0e-15,
            ),
            "energy_matches_analytic_reference": (
                max_energy_error <= RELATIVE_ERROR_TOLERANCE
            ),
            "enstrophy_matches_analytic_reference": (
                max_enstrophy_error
                <= RELATIVE_ERROR_TOLERANCE
            ),
            "energy_injection_matches_reference": (
                max_energy_injection_error
                <= RELATIVE_ERROR_TOLERANCE
            ),
            "enstrophy_injection_matches_reference": (
                max_enstrophy_injection_error
                <= RELATIVE_ERROR_TOLERANCE
            ),
            "viscous_energy_dissipation_matches_reference": (
                max_viscous_energy_error
                <= RELATIVE_ERROR_TOLERANCE
            ),
            "viscous_enstrophy_dissipation_matches_reference": (
                max_viscous_enstrophy_error
                <= RELATIVE_ERROR_TOLERANCE
            ),
            "advection_remains_roundoff_scale": (
                max_advection_rms <= ADVECTION_RMS_TOLERANCE
            ),
            "mask_removal_remains_roundoff_scale": (
                max_mask_removal_rms
                <= MASK_REMOVAL_RMS_TOLERANCE
            ),
            "forcing_rms_matches": (
                abs(
                    forcing_rms - EXPECTED_FORCING_RMS
                ) <= FORCING_RMS_TOLERANCE
            ),
        }

        passed = all(checks.values())

        summary = {
            "run_id": run_id,
            "classification": (
                "ANALYTIC FORCING-BUDGET PILOT PASS"
                if passed
                else "ANALYTIC FORCING-BUDGET PILOT FAIL"
            ),
            "checks": checks,
            "snapshot_count": len(rows),
            "max_energy_relative_error": max_energy_error,
            "max_enstrophy_relative_error": (
                max_enstrophy_error
            ),
            "max_energy_injection_relative_error": (
                max_energy_injection_error
            ),
            "max_enstrophy_injection_relative_error": (
                max_enstrophy_injection_error
            ),
            "max_viscous_energy_dissipation_relative_error": (
                max_viscous_energy_error
            ),
            "max_viscous_enstrophy_dissipation_relative_error": (
                max_viscous_enstrophy_error
            ),
            "max_advection_rms": max_advection_rms,
            "max_mask_removal_rms": max_mask_removal_rms,
            "final_snapshot": final,
            "files": {
                "metadata": metadata_path.name,
                "table": table_path.name,
                "summary": summary_path.name,
            },
            "scientific_boundary": {
                "analytic_pilot_only": True,
                "convergence_claim": False,
                "physical_validation_claim": False,
                "turbulence_claim": False,
                "cascade_claim": False,
                "k_minus_3_claim": False,
            },
        }

        write_json(summary_path, summary)

        metadata["status"] = "passed" if passed else "failed"
        metadata["completed_utc"] = (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        )

        write_json(metadata_path, metadata)

        print()
        print("=" * 72)
        print(summary["classification"])
        print("=" * 72)
        print("Run directory:", run_directory)
        print("Snapshots:", len(rows))
        print("Final completed steps:", final["completed_steps"])
        print("Final physical time:", final["physical_time"])
        print(
            "Maximum energy relative error:",
            f"{max_energy_error:.12e}",
        )
        print(
            "Maximum enstrophy relative error:",
            f"{max_enstrophy_error:.12e}",
        )
        print(
            "Maximum energy-injection relative error:",
            f"{max_energy_injection_error:.12e}",
        )
        print(
            "Maximum enstrophy-injection relative error:",
            f"{max_enstrophy_injection_error:.12e}",
        )
        print(
            "Maximum viscous-energy relative error:",
            f"{max_viscous_energy_error:.12e}",
        )
        print(
            "Maximum viscous-enstrophy relative error:",
            f"{max_viscous_enstrophy_error:.12e}",
        )
        print(
            "Maximum advection RMS:",
            f"{max_advection_rms:.12e}",
        )
        print(
            "Maximum mask-removal RMS:",
            f"{max_mask_removal_rms:.12e}",
        )
        print("Protected solver run loop called: NO")
        print("Formal claims authorized: NO")

        if not passed:
            raise RuntimeError(
                "analytic forcing-budget pilot checks failed"
            )

        return 0

    except BaseException as error:
        metadata["status"] = "failed"
        metadata["error_type"] = type(error).__name__
        metadata["error_message"] = str(error)
        metadata["completed_utc"] = (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        )

        write_json(metadata_path, metadata)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
