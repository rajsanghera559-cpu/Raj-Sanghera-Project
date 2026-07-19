"""
Controlled short RMS-matched multimode forcing-budget pilot.

Usage:
    python -B run_forcing_budget_multimode_pilot.py --inspect
    python -B run_forcing_budget_multimode_pilot.py --run

The inspection path parses this file and verifies source identities without
importing project modules, constructing a solver, or writing result files.

The run path mirrors the protected solver's RK2 update externally. It does not
call the protected solver run loop and does not modify protected source files.

This is a descriptive forcing-budget pilot, not a convergence, turbulence,
cascade, spectral-law, method-superiority, or physical-validation experiment.
"""

from __future__ import annotations

import argparse
import ast
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

EXPECTED_FORCING_RMS = 0.005
FORCING_RMS_TOLERANCE = 1.0e-14

EXPECTED_SOLVER_SHA256 = (
    "1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1"
)

EXPECTED_BUDGET_SHA256 = (
    "A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B"
)

OUTPUT_ROOT = Path("experiments") / "forcing_budget_pilot"
RUN_PREFIX = "forcing_budget_multimode_"

FORCING_TERMS = (
    "sin(2X)cos(2Y)",
    "0.75*sin(3X)cos(Y)",
    "0.50*sin(X)cos(4Y)",
    "0.35*cos(4X-2Y)",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


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


def build_rms_matched_multimode_forcing(
    solver: object,
) -> tuple[np.ndarray, dict[str, float | tuple[str, ...]]]:
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

    forcing = raw * (base_rms / raw_rms)

    matched_rms = float(np.sqrt(np.mean(forcing * forcing)))
    mean_value = float(np.mean(forcing))
    max_abs = float(np.max(np.abs(forcing)))

    if not np.isfinite(forcing).all():
        raise RuntimeError("multimode forcing contains a nonfinite value")

    if abs(matched_rms - EXPECTED_FORCING_RMS) > FORCING_RMS_TOLERANCE:
        raise RuntimeError(
            f"unexpected matched forcing RMS: {matched_rms}"
        )

    return forcing, {
        "base_single_mode_rms": base_rms,
        "raw_multimode_rms": raw_rms,
        "matched_multimode_rms": matched_rms,
        "forcing_mean": mean_value,
        "forcing_max_abs": max_abs,
        "forcing_terms": FORCING_TERMS,
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
        "vorticity_rms": float(
            np.sqrt(np.mean(filtered * filtered))
        ),
    }


def spectrum_summary(
    solver: object,
    omega: np.ndarray,
) -> dict[str, float | int]:
    k_bins, energy_spectrum, mode_counts = solver.energy_spectrum(omega)

    k_bins = np.asarray(k_bins)
    energy_spectrum = np.asarray(energy_spectrum)
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

    if not np.isfinite(energy_spectrum).all():
        raise RuntimeError("nonfinite energy spectrum")

    total = float(np.sum(energy_spectrum))

    if total <= 0.0:
        raise RuntimeError("nonpositive spectrum energy sum")

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

    tail_energy = sum(
        value
        for k, value in shell_map.items()
        if k > 4
    )

    high_k_energy = sum(
        value
        for k, value in shell_map.items()
        if k >= 10
    )

    return {
        "spectrum_energy_sum": total,
        "dominant_shell": dominant_shell,
        "dominant_shell_energy": shell_map[dominant_shell],
        "k1_energy": shell_map.get(1, 0.0),
        "k2_energy": shell_map.get(2, 0.0),
        "k3_energy": shell_map.get(3, 0.0),
        "k4_energy": shell_map.get(4, 0.0),
        "low_k_fraction_k_le_4": low_k_energy / total,
        "tail_fraction_k_gt_4": tail_energy / total,
        "high_k_fraction_k_ge_10": high_k_energy / total,
        "finite_shell_count": int(np.isfinite(energy_spectrum).sum()),
        "nonzero_shell_count": int((energy_spectrum > 0.0).sum()),
    }


def inspect_runner(repo: Path) -> int:
    runner = Path(__file__).resolve()
    raw = runner.read_bytes()

    if b"\r" in raw:
        fail("runner is not LF-only")

    source = raw.decode("utf-8", errors="strict")
    tree = ast.parse(source, filename=str(runner))
    compile(tree, str(runner), "exec", dont_inherit=True)

    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        fail("active branch is not phase4_validation")

    status = git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ).splitlines()

    expected_status = [f"?? {runner.name}"]

    if status != expected_status:
        fail(f"unexpected Git status: {status!r}")

    expected_hashes = {
        repo / "project" / "solver" / "spectral_solver.py":
            EXPECTED_SOLVER_SHA256,
        repo / "forcing_budget_diagnostic.py":
            EXPECTED_BUDGET_SHA256,
    }

    for path, expected in expected_hashes.items():
        if not path.is_file():
            fail(f"protected file is missing: {path}")

        observed = sha256_file(path)

        if observed != expected:
            fail(
                f"protected hash changed for {path.name}: {observed}"
            )

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
        "STEPS": 1001,
        "OUTPUT_INTERVAL": 100,
        "EXPECTED_FORCING_RMS": 0.005,
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
        "git_read",
        "write_json",
        "write_csv",
        "build_rms_matched_multimode_forcing",
        "external_rk2_step",
        "spectrum_summary",
        "inspect_runner",
        "execute_pilot",
        "main",
    }

    observed_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    missing = required_functions - observed_functions

    if missing:
        fail(f"missing functions: {sorted(missing)}")

    parents: dict[ast.AST, ast.AST] = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def enclosing_function(node: ast.AST) -> str | None:
        current = node

        while current in parents:
            current = parents[current]

            if isinstance(current, ast.FunctionDef):
                return current.name

        return None

    actual_solver_run_lines: list[int] = []
    project_import_scopes: list[tuple[str, str | None]] = []
    call_counts = {
        "SpectralSolver": 0,
        "forcing_budget_snapshot": 0,
        "forcing_budget_interval": 0,
    }

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

        if isinstance(node.func, ast.Attribute):
            owner = node.func.value

            if (
                node.func.attr == "run"
                and isinstance(owner, ast.Name)
                and owner.id == "solver"
            ):
                actual_solver_run_lines.append(node.lineno)

    if actual_solver_run_lines:
        fail(
            f"actual solver.run calls found at {actual_solver_run_lines}"
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
        if item[1] != "execute_pilot"
    ]

    if bad_import_scopes:
        fail(
            "project imports are not confined to execute_pilot: "
            f"{bad_import_scopes!r}"
        )

    required_fragments = (
        'for loop_index in range(STEPS):',
        'loop_index=loop_index,',
        'loop_index % OUTPUT_INTERVAL == 0',
        'loop_index == STEPS - 1',
        'RUN_PREFIX = "forcing_budget_multimode_"',
        '"forcing_type": "rms_matched_deterministic_low_k_multimode"',
        '"convergence": False',
        '"physical_validation": False',
        '"turbulence": False',
        '"cascade": False',
        '"k_minus_3": False',
        'if arguments.mode == "inspect":',
        'if arguments.mode == "run":',
    )

    for fragment in required_fragments:
        if fragment not in source:
            fail(f"required fragment absent: {fragment}")

    print()
    print("=" * 72)
    print("MULTIMODE FORCING-BUDGET RUNNER INSPECTION: PASS")
    print("=" * 72)
    print("File:", runner.name)
    print("Lines:", len(source.splitlines()))
    print("Bytes:", len(raw))
    print("SHA256:", hashlib.sha256(raw).hexdigest().upper())
    print("Configuration: N64, Re1000, dt0.005, steps1001")
    print("Output interval: 100")
    print("Expected snapshots: 11")
    print("Forcing: RMS-matched deterministic low-k multimode")
    print("Protected source hashes: PASS")
    print("Runner imported project modules: NO")
    print("Runner executed numerical steps: NO")
    print("Solver constructed: NO")
    print("Actual solver.run call present: NO")
    print("Files written: NO")
    print("Git mutations: NONE")
    print("Numerical execution authorized by inspection: NO")

    return 0


def execute_pilot(repo: Path) -> int:
    if git_read(repo, "branch", "--show-current") != "phase4_validation":
        raise RuntimeError("active branch is not phase4_validation")

    if git_read(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ):
        raise RuntimeError("working tree is not clean")

    solver_path = (
        repo / "project" / "solver" / "spectral_solver.py"
    )

    budget_path = repo / "forcing_budget_diagnostic.py"

    if sha256_file(solver_path) != EXPECTED_SOLVER_SHA256:
        raise RuntimeError("protected spectral solver hash changed")

    if sha256_file(budget_path) != EXPECTED_BUDGET_SHA256:
        raise RuntimeError("forcing-budget diagnostic hash changed")

    output_root = repo / OUTPUT_ROOT

    existing_runs = (
        sorted(output_root.glob(f"{RUN_PREFIX}*"))
        if output_root.is_dir()
        else []
    )

    if existing_runs:
        raise RuntimeError(
            "a multimode forcing-budget pilot output already exists: "
            + ", ".join(str(path) for path in existing_runs)
        )

    head = git_read(repo, "rev-parse", "HEAD")

    from forcing_budget_diagnostic import (
        forcing_budget_interval,
        forcing_budget_snapshot,
    )

    from project.solver.spectral_solver import SpectralSolver

    created = datetime.datetime.now(datetime.timezone.utc)
    created_utc = created.replace(microsecond=0).isoformat()
    stamp = created.strftime("%Y%m%dT%H%M%SZ")

    run_id = f"{RUN_PREFIX}{stamp}_{head[:7]}"
    run_directory = output_root / run_id
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
            "forcing_type": (
                "rms_matched_deterministic_low_k_multimode"
            ),
            "forcing_terms": FORCING_TERMS,
            "target_forcing_rms": EXPECTED_FORCING_RMS,
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
            "stationarity": False,
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

        forcing, forcing_stats = (
            build_rms_matched_multimode_forcing(solver)
        )

        metadata["configuration"]["forcing_statistics"] = (
            forcing_stats
        )

        rows: list[dict[str, object]] = []
        previous_snapshot: dict[str, float | int] | None = None

        max_advection_rms_all_steps = 0.0
        max_mask_removal_rms_all_steps = 0.0

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

            spectral = spectrum_summary(
                solver,
                np.asarray(solver.w),
            )

            row: dict[str, object] = {
                **snapshot,
                **step_metrics,
                **spectral,
                "energy_injection_to_dissipation_ratio": (
                    float(snapshot["energy_injection_rate"])
                    / float(
                        snapshot[
                            "viscous_energy_dissipation_rate"
                        ]
                    )
                    if float(
                        snapshot[
                            "viscous_energy_dissipation_rate"
                        ]
                    ) != 0.0
                    else None
                ),
                "enstrophy_injection_to_dissipation_ratio": (
                    float(snapshot["enstrophy_injection_rate"])
                    / float(
                        snapshot[
                            "viscous_enstrophy_dissipation_rate"
                        ]
                    )
                    if float(
                        snapshot[
                            "viscous_enstrophy_dissipation_rate"
                        ]
                    ) != 0.0
                    else None
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

        final = rows[-1]

        numeric_values: list[float] = []

        for row in rows:
            for value in row.values():
                if value is None:
                    continue

                if isinstance(value, (int, float, np.integer, np.floating)):
                    numeric_values.append(float(value))

        all_numeric_finite = all(
            math.isfinite(value)
            for value in numeric_values
        )

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
            "forcing_rms_matches": (
                abs(
                    float(final["forcing_rms"])
                    - EXPECTED_FORCING_RMS
                ) <= FORCING_RMS_TOLERANCE
            ),
            "all_numeric_values_are_finite": all_numeric_finite,
            "final_energy_is_positive": (
                float(final["energy"]) > 0.0
            ),
            "final_enstrophy_is_positive": (
                float(final["enstrophy"]) > 0.0
            ),
            "final_spectrum_energy_is_positive": (
                float(final["spectrum_energy_sum"]) > 0.0
            ),
            "interval_residuals_are_recorded": all(
                row["energy_budget_residual"] is not None
                and row["enstrophy_budget_residual"] is not None
                for row in rows[1:]
            ),
        }

        passed = all(checks.values())

        maximum_energy_residual = max(
            abs(float(row["energy_budget_residual"]))
            for row in rows[1:]
        )

        maximum_enstrophy_residual = max(
            abs(float(row["enstrophy_budget_residual"]))
            for row in rows[1:]
        )

        summary = {
            "run_id": run_id,
            "classification": (
                "MULTIMODE FORCING-BUDGET PILOT PASS"
                if passed
                else "MULTIMODE FORCING-BUDGET PILOT FAIL"
            ),
            "checks": checks,
            "snapshot_count": len(rows),
            "forcing_statistics": forcing_stats,
            "max_advection_rms_all_steps": (
                max_advection_rms_all_steps
            ),
            "max_mask_removal_rms_all_steps": (
                max_mask_removal_rms_all_steps
            ),
            "max_abs_energy_budget_residual": (
                maximum_energy_residual
            ),
            "max_abs_enstrophy_budget_residual": (
                maximum_enstrophy_residual
            ),
            "final_snapshot": final,
            "files": {
                "metadata": metadata_path.name,
                "table": table_path.name,
                "summary": summary_path.name,
            },
            "scientific_boundary": {
                "short_descriptive_pilot_only": True,
                "convergence_claim": False,
                "physical_validation_claim": False,
                "turbulence_claim": False,
                "cascade_claim": False,
                "k_minus_3_claim": False,
                "stationarity_claim": False,
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
            "Forcing RMS:",
            f"{float(final['forcing_rms']):.12e}",
        )
        print(
            "Final energy injection rate:",
            f"{float(final['energy_injection_rate']):.12e}",
        )
        print(
            "Final viscous energy dissipation rate:",
            f"{float(final['viscous_energy_dissipation_rate']):.12e}",
        )
        print(
            "Final enstrophy injection rate:",
            f"{float(final['enstrophy_injection_rate']):.12e}",
        )
        print(
            "Final viscous enstrophy dissipation rate:",
            f"{float(final['viscous_enstrophy_dissipation_rate']):.12e}",
        )
        print(
            "Maximum advection RMS:",
            f"{max_advection_rms_all_steps:.12e}",
        )
        print(
            "Final dominant shell:",
            final["dominant_shell"],
        )
        print(
            "Final tail fraction k>4:",
            f"{float(final['tail_fraction_k_gt_4']):.12e}",
        )
        print(
            "Final high-k fraction k>=10:",
            f"{float(final['high_k_fraction_k_ge_10']):.12e}",
        )
        print(
            "Maximum absolute energy-budget residual:",
            f"{maximum_energy_residual:.12e}",
        )
        print(
            "Maximum absolute enstrophy-budget residual:",
            f"{maximum_enstrophy_residual:.12e}",
        )
        print("Protected solver run loop called: NO")
        print("Formal claims authorized: NO")

        if not passed:
            raise RuntimeError(
                "multimode forcing-budget pilot checks failed"
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or execute the controlled short RMS-matched "
            "multimode forcing-budget pilot."
        )
    )

    parser.add_argument(
        "mode",
        choices=("inspect", "run"),
        help="inspect source without execution, or run the pilot once",
    )

    arguments = parser.parse_args()
    repo = Path(__file__).resolve().parent

    if arguments.mode == "inspect":
        return inspect_runner(repo)

    if arguments.mode == "run":
        return execute_pilot(repo)

    raise AssertionError("unreachable mode")


if __name__ == "__main__":
    raise SystemExit(main())
