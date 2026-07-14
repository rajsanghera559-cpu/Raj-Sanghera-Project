from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


OUT_METHOD_CSV = Path("PHASE10Q1_SELECTABLE_ONE_STEP_OPERATOR_COMPARISON_AUDIT.csv")
OUT_PAIRWISE_CSV = Path("PHASE10Q1_SELECTABLE_ONE_STEP_PAIRWISE_SUMMARY.csv")

METHODS = ("fd_centered", "pseudo_spectral", "arakawa")

PAIRS = (
    ("pseudo_spectral", "fd_centered"),
    ("arakawa", "fd_centered"),
    ("arakawa", "pseudo_spectral"),
)


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    arr = np.asarray(field)
    return float(np.sqrt(np.mean(arr * arr)))


def l2_norm(field):
    arr = np.asarray(field)
    return float(np.sqrt(np.mean(arr * arr)))


def max_abs(field):
    return float(np.max(np.abs(np.asarray(field))))


def relative_error(diff_norm, reference_norm):
    denom = max(abs(float(reference_norm)), 1e-300)
    return float(diff_norm) / denom


def cosine_similarity(a, b):
    a_flat = np.asarray(a).ravel()
    b_flat = np.asarray(b).ravel()

    denom = np.linalg.norm(a_flat) * np.linalg.norm(b_flat)

    if denom <= 0:
        return np.nan

    return float(np.dot(a_flat, b_flat) / denom)


def git_file_has_no_diff(path):
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet", "--", path],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def rescale_to_rms(field, target_rms):
    field_rms = rms(field)

    if field_rms == 0:
        raise ValueError("Cannot rescale zero-RMS field.")

    return field * (target_rms / field_rms)


def kinetic_energy_from_vorticity(solver, w):
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)
    return float(0.5 * np.mean(u * u + v * v))


def enstrophy_from_vorticity(w):
    arr = np.asarray(w)
    return float(0.5 * np.mean(arr * arr))


def build_test_fields(solver):
    X = solver.X
    Y = solver.Y

    single_mode = 0.01 * np.sin(2 * X) * np.cos(2 * Y)

    low_mode_pair = 0.01 * (
        np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(Y)
    )

    phase6d_like_raw = (
        np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(Y)
        + 0.50 * np.sin(X) * np.cos(4 * Y)
        + 0.35 * np.cos(4 * X - 2 * Y)
    )
    phase6d_like = rescale_to_rms(phase6d_like_raw, 0.01)

    higher_smooth_raw = (
        np.sin(5 * X) * np.cos(3 * Y)
        + 0.50 * np.sin(7 * X - 2 * Y)
        + 0.25 * np.cos(4 * X + 6 * Y)
    )
    higher_smooth = rescale_to_rms(higher_smooth_raw, 0.01)

    return {
        "single_mode_k2_2": {
            "field": single_mode,
            "classification": "controlled_single_mode_reference",
            "primary_evidence": False,
        },
        "low_mode_pair": {
            "field": low_mode_pair,
            "classification": "low_k_nonlinear",
            "primary_evidence": True,
        },
        "phase6d_like_multimode": {
            "field": phase6d_like,
            "classification": "phase6d_like_low_k_nonlinear",
            "primary_evidence": True,
        },
        "higher_smooth_multimode": {
            "field": higher_smooth,
            "classification": "higher_smooth_nonlinear",
            "primary_evidence": True,
        },
    }


def audit_invalid_method():
    try:
        SelectableAdvectionSolver(
            nx=64,
            ny=64,
            Re=1000,
            run_path=Path("experiments") / "method_diagnostics" / "phase10Q1_invalid",
            dt=0.005,
            steps=1,
            advection_method="invalid_method",
        )
        return False
    except ValueError:
        return True


def audit_method_output(N, field_name, field_info, method):
    run_path = (
        Path("experiments")
        / "method_diagnostics"
        / f"phase10Q1_N{N}_{field_name}_{method}"
    )

    solver = SelectableAdvectionSolver(
        nx=N,
        ny=N,
        Re=1000,
        run_path=run_path,
        dt=0.005,
        steps=1,
        advection_method=method,
    )

    w = np.asarray(field_info["field"])
    w_before = w.copy()
    solver_w_before = solver.w.copy()

    output = solver.step_once_selectable(w)

    finite_output = np.isfinite(output).all()
    real_output = np.isrealobj(output)
    input_w_unchanged = np.allclose(w, w_before, rtol=0.0, atol=0.0)
    solver_w_unchanged = np.allclose(
        solver.w,
        solver_w_before,
        rtol=0.0,
        atol=0.0,
    )

    metadata = solver.selectable_advection_metadata()

    metadata_method_ok = metadata.get("advection_method") == method
    metadata_rhs_method_ok = metadata.get("rhs_method") == "compute_rhs_selectable"
    metadata_step_method_ok = metadata.get("step_method") == "step_once_selectable"
    metadata_step_status_ok = metadata.get("step_status") == "diagnostic_scaffold"
    metadata_variant_ok = metadata.get("solver_variant") == "selectable_advection"
    metadata_baseline_ok = metadata.get("production_baseline_modified") is False
    metadata_run_disabled_ok = metadata.get("run_enabled") is False
    metadata_no_turbulence_claim = metadata.get("turbulence_claim") is False
    metadata_no_k_minus_3_claim = metadata.get("k_minus_3_claim") is False

    try:
        solver.run()
        run_disabled = False
    except NotImplementedError:
        run_disabled = True

    input_l2 = l2_norm(w)
    output_l2 = l2_norm(output)
    output_to_input_l2_ratio = output_l2 / max(input_l2, 1e-300)

    no_explosive_one_step_growth = output_to_input_l2_ratio < 2.0

    overall = all(
        [
            solver.advection_method == method,
            finite_output,
            real_output,
            input_w_unchanged,
            solver_w_unchanged,
            metadata_method_ok,
            metadata_rhs_method_ok,
            metadata_step_method_ok,
            metadata_step_status_ok,
            metadata_variant_ok,
            metadata_baseline_ok,
            metadata_run_disabled_ok,
            metadata_no_turbulence_claim,
            metadata_no_k_minus_3_claim,
            run_disabled,
            no_explosive_one_step_growth,
        ]
    )

    energy = kinetic_energy_from_vorticity(solver, output)
    enstrophy = enstrophy_from_vorticity(output)

    return {
        "N": N,
        "field_name": field_name,
        "classification": field_info["classification"],
        "primary_evidence": bool(field_info["primary_evidence"]),
        "method": method,
        "input_l2": input_l2,
        "output_l2": output_l2,
        "output_to_input_l2_ratio": output_to_input_l2_ratio,
        "output_max_abs": max_abs(output),
        "output_energy": energy,
        "output_enstrophy": enstrophy,
        "finite_output": pass_fail(finite_output),
        "real_output": pass_fail(real_output),
        "input_w_unchanged": pass_fail(input_w_unchanged),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "metadata_method_ok": pass_fail(metadata_method_ok),
        "metadata_rhs_method_ok": pass_fail(metadata_rhs_method_ok),
        "metadata_step_method_ok": pass_fail(metadata_step_method_ok),
        "metadata_step_status_ok": pass_fail(metadata_step_status_ok),
        "metadata_variant_ok": pass_fail(metadata_variant_ok),
        "metadata_baseline_ok": pass_fail(metadata_baseline_ok),
        "metadata_run_disabled_ok": pass_fail(metadata_run_disabled_ok),
        "metadata_no_turbulence_claim": pass_fail(metadata_no_turbulence_claim),
        "metadata_no_k_minus_3_claim": pass_fail(metadata_no_k_minus_3_claim),
        "run_disabled": pass_fail(run_disabled),
        "no_explosive_one_step_growth": pass_fail(no_explosive_one_step_growth),
        "overall_result": pass_fail(overall),
        "_output": output,
        "_solver": solver,
    }


def pairwise_summary(N, field_name, field_info, method_results, method_a, method_b):
    out_a = method_results[method_a]["_output"]
    out_b = method_results[method_b]["_output"]
    solver_a = method_results[method_a]["_solver"]
    solver_b = method_results[method_b]["_solver"]

    diff = out_a - out_b

    a_l2 = l2_norm(out_a)
    b_l2 = l2_norm(out_b)
    diff_l2 = l2_norm(diff)
    diff_max = max_abs(diff)
    rel_error = relative_error(diff_l2, b_l2)
    cosine = cosine_similarity(out_a, out_b)

    a_energy = kinetic_energy_from_vorticity(solver_a, out_a)
    b_energy = kinetic_energy_from_vorticity(solver_b, out_b)
    energy_diff = float(a_energy - b_energy)
    energy_abs_diff = abs(energy_diff)

    a_enstrophy = enstrophy_from_vorticity(out_a)
    b_enstrophy = enstrophy_from_vorticity(out_b)
    enstrophy_diff = float(a_enstrophy - b_enstrophy)
    enstrophy_abs_diff = abs(enstrophy_diff)

    if field_info["primary_evidence"]:
        positive_alignment = cosine > 0.99
    else:
        positive_alignment = np.isfinite(cosine) and cosine > 0.0

    no_large_pairwise_disagreement = rel_error < 0.25

    pairwise_result = positive_alignment and no_large_pairwise_disagreement

    return {
        "N": N,
        "field_name": field_name,
        "classification": field_info["classification"],
        "primary_evidence": bool(field_info["primary_evidence"]),
        "method_a": method_a,
        "method_b_reference": method_b,
        "method_a_l2": a_l2,
        "method_b_l2": b_l2,
        "diff_l2": diff_l2,
        "diff_max_abs": diff_max,
        "relative_error_vs_method_b": rel_error,
        "cosine_similarity": cosine,
        "method_a_energy": a_energy,
        "method_b_energy": b_energy,
        "energy_diff_a_minus_b": energy_diff,
        "energy_abs_diff": energy_abs_diff,
        "method_a_enstrophy": a_enstrophy,
        "method_b_enstrophy": b_enstrophy,
        "enstrophy_diff_a_minus_b": enstrophy_diff,
        "enstrophy_abs_diff": enstrophy_abs_diff,
        "positive_alignment": pass_fail(positive_alignment),
        "no_large_pairwise_disagreement": pass_fail(no_large_pairwise_disagreement),
        "pairwise_result": pass_fail(pairwise_result),
    }


print("\n=== PHASE 10Q.1 SELECTABLE ONE-STEP OPERATOR COMPARISON AUDIT ===")
print("Purpose: compare one-step outputs across fd_centered, pseudo_spectral, and arakawa.")
print("This does not modify SpectralSolver.")
print("This does not enable SelectableAdvectionSolver.run().")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")

method_rows = []
pairwise_rows = []

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods_ok = SelectableAdvectionSolver.supported_advection_methods() == METHODS
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
rhs_method_exists = hasattr(SelectableAdvectionSolver, "compute_rhs_selectable")
step_method_exists = hasattr(SelectableAdvectionSolver, "step_once_selectable")
spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")
invalid_method_rejected = audit_invalid_method()

global_pass = all(
    [
        baseline_import_ok,
        selectable_import_ok,
        supported_methods_ok,
        default_method_ok,
        rhs_method_exists,
        step_method_exists,
        spectral_solver_no_diff,
        selectable_solver_no_diff,
        invalid_method_rejected,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"Supported methods check: {pass_fail(supported_methods_ok)}")
print(f"Default method fd_centered: {pass_fail(default_method_ok)}")
print(f"compute_rhs_selectable exists: {pass_fail(rhs_method_exists)}")
print(f"step_once_selectable exists: {pass_fail(step_method_exists)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"SelectableAdvectionSolver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"Invalid method rejected: {pass_fail(invalid_method_rejected)}")
print(f"Global checks: {pass_fail(global_pass)}")

method_rows.append(
    {
        "N": np.nan,
        "field_name": "global",
        "classification": "global",
        "primary_evidence": False,
        "method": "global",
        "input_l2": np.nan,
        "output_l2": np.nan,
        "output_to_input_l2_ratio": np.nan,
        "output_max_abs": np.nan,
        "output_energy": np.nan,
        "output_enstrophy": np.nan,
        "finite_output": "N/A",
        "real_output": "N/A",
        "input_w_unchanged": "N/A",
        "solver_w_unchanged": "N/A",
        "metadata_method_ok": "N/A",
        "metadata_rhs_method_ok": "N/A",
        "metadata_step_method_ok": "N/A",
        "metadata_step_status_ok": "N/A",
        "metadata_variant_ok": "N/A",
        "metadata_baseline_ok": pass_fail(spectral_solver_no_diff),
        "metadata_run_disabled_ok": "N/A",
        "metadata_no_turbulence_claim": "N/A",
        "metadata_no_k_minus_3_claim": "N/A",
        "run_disabled": "N/A",
        "no_explosive_one_step_growth": "N/A",
        "overall_result": pass_fail(global_pass),
    }
)

for N in [64, 128]:
    print(f"\n=== N={N} ===")

    field_solver = SpectralSolver(
        nx=N,
        ny=N,
        Re=1000,
        run_path=Path("experiments") / "method_diagnostics" / f"phase10Q1_field_builder_N{N}",
        dt=0.005,
        steps=1,
    )

    fields = build_test_fields(field_solver)

    for field_name, field_info in fields.items():
        print(f"\nField: {field_name}")
        print(f"classification: {field_info['classification']}")
        print(f"primary_evidence: {field_info['primary_evidence']}")

        method_results = {}

        for method in METHODS:
            result = audit_method_output(N, field_name, field_info, method)
            method_results[method] = result

            public_result = {
                key: value
                for key, value in result.items()
                if key not in ["_output", "_solver"]
            }
            method_rows.append(public_result)

            print(f"\nMethod: {method}")
            print(f"output_l2: {result['output_l2']:.12e}")
            print(f"output_energy: {result['output_energy']:.12e}")
            print(f"output_enstrophy: {result['output_enstrophy']:.12e}")
            print(f"finite_output: {result['finite_output']}")
            print(f"real_output: {result['real_output']}")
            print(f"input_w_unchanged: {result['input_w_unchanged']}")
            print(f"solver_w_unchanged: {result['solver_w_unchanged']}")
            print(f"run_disabled: {result['run_disabled']}")
            print(f"metadata_method_ok: {result['metadata_method_ok']}")
            print(f"metadata_no_turbulence_claim: {result['metadata_no_turbulence_claim']}")
            print(f"metadata_no_k_minus_3_claim: {result['metadata_no_k_minus_3_claim']}")
            print(f"overall_result: {result['overall_result']}")

        print("\nPairwise comparisons:")

        for method_a, method_b in PAIRS:
            pair = pairwise_summary(
                N,
                field_name,
                field_info,
                method_results,
                method_a,
                method_b,
            )
            pairwise_rows.append(pair)

            print(f"\n{method_a} vs {method_b}")
            print(f"diff_l2: {pair['diff_l2']:.12e}")
            print(f"diff_max_abs: {pair['diff_max_abs']:.12e}")
            print(f"relative_error_vs_{method_b}: {pair['relative_error_vs_method_b']:.12e}")
            print(f"cosine_similarity: {pair['cosine_similarity']:.12e}")
            print(f"energy_abs_diff: {pair['energy_abs_diff']:.12e}")
            print(f"enstrophy_abs_diff: {pair['enstrophy_abs_diff']:.12e}")
            print(f"positive_alignment: {pair['positive_alignment']}")
            print(f"no_large_pairwise_disagreement: {pair['no_large_pairwise_disagreement']}")
            print(f"pairwise_result: {pair['pairwise_result']}")

method_df = pd.DataFrame(method_rows)
pairwise_df = pd.DataFrame(pairwise_rows)

method_df.to_csv(OUT_METHOD_CSV, index=False)
pairwise_df.to_csv(OUT_PAIRWISE_CSV, index=False)

method_pass = (method_df["overall_result"] == "PASS").all()

primary_pairwise = pairwise_df[pairwise_df["primary_evidence"] == True]
primary_pairwise_pass = (primary_pairwise["pairwise_result"] == "PASS").all()

near_null_retained = (pairwise_df["primary_evidence"] == False).any()

overall_pass = bool(method_pass and primary_pairwise_pass and near_null_retained)

print("\n=== OVERALL RESULT ===")
print(f"Method output checks pass: {pass_fail(method_pass)}")
print(f"Primary pairwise comparisons pass: {pass_fail(primary_pairwise_pass)}")
print(f"Near-null/reference case retained: {pass_fail(near_null_retained)}")
print(f"Phase 10Q.1 selectable one-step operator comparison audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_METHOD_CSV}")
print(f"Wrote: {OUT_PAIRWISE_CSV}")
print("Phase 10Q.1 selectable one-step operator comparison audit complete.")