from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


OUT_CSV = Path("PHASE10N1_FD_CENTERED_RHS_EQUIVALENCE_AUDIT.csv")


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
        },
        "low_mode_pair": {
            "field": low_mode_pair,
            "classification": "low_k_nonlinear",
        },
        "phase6d_like_multimode": {
            "field": phase6d_like,
            "classification": "phase6d_like_low_k_nonlinear",
        },
        "higher_smooth_multimode": {
            "field": higher_smooth,
            "classification": "higher_smooth_nonlinear",
        },
    }


def baseline_fd_centered_rhs(solver, w):
    """
    Direct transcription of SpectralSolver.run() stage-RHS logic.

    This intentionally does not call SelectableAdvectionSolver.

    Baseline convention:

        rhs = -adv + laplacian_spectral(w) + forcing()

    where:

        adv = u * omega_x + v * omega_y
    """
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)

    wx = (np.roll(w, -1, 1) - np.roll(w, 1, 1)) / (2 * solver.dx)
    wy = (np.roll(w, -1, 0) - np.roll(w, 1, 0)) / (2 * solver.dx)

    adv = u * wx + v * wy

    return -adv + solver.laplacian_spectral(w) + solver.forcing()


def audit_shape_mismatch_rejection():
    solver = SelectableAdvectionSolver(
        nx=64,
        ny=64,
        Re=1000,
        run_path=Path("experiments") / "method_diagnostics" / "phase10N1_shape_mismatch",
        dt=0.005,
        steps=1,
        advection_method="fd_centered",
    )

    bad_field = np.zeros((65, 64))

    try:
        solver.compute_rhs_selectable(bad_field)
        rejected = False
    except ValueError:
        rejected = True

    return rejected


def audit_case(N, field_name, field_info):
    baseline_path = Path("experiments") / "method_diagnostics" / f"phase10N1_baseline_N{N}_{field_name}"
    selectable_path = Path("experiments") / "method_diagnostics" / f"phase10N1_selectable_N{N}_{field_name}"

    baseline_solver = SpectralSolver(
        nx=N,
        ny=N,
        Re=1000,
        run_path=baseline_path,
        dt=0.005,
        steps=1,
    )

    selectable_solver = SelectableAdvectionSolver(
        nx=N,
        ny=N,
        Re=1000,
        run_path=selectable_path,
        dt=0.005,
        steps=1,
        advection_method="fd_centered",
    )

    w = np.asarray(field_info["field"])
    w_before = w.copy()
    baseline_w_before = baseline_solver.w.copy()
    selectable_w_before = selectable_solver.w.copy()

    baseline_rhs = baseline_fd_centered_rhs(baseline_solver, w)
    selectable_rhs = selectable_solver.compute_rhs_selectable(w)

    diff = selectable_rhs - baseline_rhs

    baseline_rhs_l2 = l2_norm(baseline_rhs)
    selectable_rhs_l2 = l2_norm(selectable_rhs)
    diff_l2 = l2_norm(diff)
    diff_max = max_abs(diff)
    rel_error = relative_error(diff_l2, baseline_rhs_l2)
    cosine = cosine_similarity(selectable_rhs, baseline_rhs)

    finite_all = (
        np.isfinite(w).all()
        and np.isfinite(baseline_rhs).all()
        and np.isfinite(selectable_rhs).all()
        and np.isfinite(diff).all()
    )

    real_all = (
        np.isrealobj(baseline_rhs)
        and np.isrealobj(selectable_rhs)
        and np.isrealobj(diff)
    )

    input_w_unchanged = np.allclose(w, w_before, rtol=0.0, atol=0.0)
    baseline_solver_w_unchanged = np.allclose(
        baseline_solver.w,
        baseline_w_before,
        rtol=0.0,
        atol=0.0,
    )
    selectable_solver_w_unchanged = np.allclose(
        selectable_solver.w,
        selectable_w_before,
        rtol=0.0,
        atol=0.0,
    )

    exact_match = np.allclose(selectable_rhs, baseline_rhs, rtol=0.0, atol=0.0)
    strict_equivalence = exact_match or (rel_error <= 1e-12 and diff_max <= 1e-14)

    metadata = selectable_solver.selectable_advection_metadata()

    metadata_method_ok = metadata.get("advection_method") == "fd_centered"
    metadata_rhs_method_ok = metadata.get("rhs_method") == "compute_rhs_selectable"
    metadata_variant_ok = metadata.get("solver_variant") == "selectable_advection"
    metadata_baseline_ok = metadata.get("production_baseline_modified") is False
    metadata_run_disabled_ok = metadata.get("run_enabled") is False
    metadata_no_turbulence_claim = metadata.get("turbulence_claim") is False
    metadata_no_k_minus_3_claim = metadata.get("k_minus_3_claim") is False

    try:
        selectable_solver.run()
        run_disabled = False
    except NotImplementedError:
        run_disabled = True

    overall = all(
        [
            selectable_solver.advection_method == "fd_centered",
            finite_all,
            real_all,
            input_w_unchanged,
            baseline_solver_w_unchanged,
            selectable_solver_w_unchanged,
            strict_equivalence,
            metadata_method_ok,
            metadata_rhs_method_ok,
            metadata_variant_ok,
            metadata_baseline_ok,
            metadata_run_disabled_ok,
            metadata_no_turbulence_claim,
            metadata_no_k_minus_3_claim,
            run_disabled,
        ]
    )

    return {
        "test_type": "fd_centered_rhs_equivalence",
        "N": N,
        "field_name": field_name,
        "classification": field_info["classification"],
        "advection_method": selectable_solver.advection_method,
        "field_rms": rms(w),
        "field_max_abs": max_abs(w),
        "baseline_rhs_l2": baseline_rhs_l2,
        "selectable_rhs_l2": selectable_rhs_l2,
        "diff_l2": diff_l2,
        "diff_max_abs": diff_max,
        "relative_error": rel_error,
        "cosine_similarity": cosine,
        "finite_all": pass_fail(finite_all),
        "real_all": pass_fail(real_all),
        "input_w_unchanged": pass_fail(input_w_unchanged),
        "baseline_solver_w_unchanged": pass_fail(baseline_solver_w_unchanged),
        "selectable_solver_w_unchanged": pass_fail(selectable_solver_w_unchanged),
        "exact_match": pass_fail(exact_match),
        "strict_equivalence": pass_fail(strict_equivalence),
        "metadata_method_ok": pass_fail(metadata_method_ok),
        "metadata_rhs_method_ok": pass_fail(metadata_rhs_method_ok),
        "metadata_variant_ok": pass_fail(metadata_variant_ok),
        "metadata_baseline_ok": pass_fail(metadata_baseline_ok),
        "metadata_run_disabled_ok": pass_fail(metadata_run_disabled_ok),
        "metadata_no_turbulence_claim": pass_fail(metadata_no_turbulence_claim),
        "metadata_no_k_minus_3_claim": pass_fail(metadata_no_k_minus_3_claim),
        "run_disabled": pass_fail(run_disabled),
        "overall_result": pass_fail(overall),
    }


print("\n=== PHASE 10N.1 FD_CENTERED RHS EQUIVALENCE AUDIT ===")
print("Purpose: compare direct baseline RHS logic to selectable fd_centered RHS.")
print("This does not modify SpectralSolver.")
print("This does not enable SelectableAdvectionSolver.run().")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")

rows = []

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods_ok = SelectableAdvectionSolver.supported_advection_methods() == (
    "fd_centered",
    "pseudo_spectral",
    "arakawa",
)
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")
shape_mismatch_rejected = audit_shape_mismatch_rejection()

global_pass = all(
    [
        baseline_import_ok,
        selectable_import_ok,
        supported_methods_ok,
        default_method_ok,
        spectral_solver_no_diff,
        selectable_solver_no_diff,
        shape_mismatch_rejected,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"Supported methods check: {pass_fail(supported_methods_ok)}")
print(f"Default method fd_centered: {pass_fail(default_method_ok)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"SelectableAdvectionSolver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"Shape mismatch rejected: {pass_fail(shape_mismatch_rejected)}")
print(f"Global checks: {pass_fail(global_pass)}")

rows.append(
    {
        "test_type": "global_checks",
        "N": np.nan,
        "field_name": "global",
        "classification": "global",
        "advection_method": "fd_centered",
        "field_rms": np.nan,
        "field_max_abs": np.nan,
        "baseline_rhs_l2": np.nan,
        "selectable_rhs_l2": np.nan,
        "diff_l2": np.nan,
        "diff_max_abs": np.nan,
        "relative_error": np.nan,
        "cosine_similarity": np.nan,
        "finite_all": "N/A",
        "real_all": "N/A",
        "input_w_unchanged": "N/A",
        "baseline_solver_w_unchanged": "N/A",
        "selectable_solver_w_unchanged": "N/A",
        "exact_match": "N/A",
        "strict_equivalence": "N/A",
        "metadata_method_ok": "N/A",
        "metadata_rhs_method_ok": "N/A",
        "metadata_variant_ok": "N/A",
        "metadata_baseline_ok": pass_fail(spectral_solver_no_diff),
        "metadata_run_disabled_ok": "N/A",
        "metadata_no_turbulence_claim": "N/A",
        "metadata_no_k_minus_3_claim": "N/A",
        "run_disabled": "N/A",
        "overall_result": pass_fail(global_pass),
    }
)

for N in [64, 128]:
    print(f"\n=== N={N} ===")

    field_solver = SpectralSolver(
        nx=N,
        ny=N,
        Re=1000,
        run_path=Path("experiments") / "method_diagnostics" / f"phase10N1_field_builder_N{N}",
        dt=0.005,
        steps=1,
    )

    fields = build_test_fields(field_solver)

    for field_name, field_info in fields.items():
        result = audit_case(N, field_name, field_info)
        rows.append(result)

        print(f"\nField: {field_name}")
        print(f"classification: {result['classification']}")
        print(f"baseline_rhs_l2: {result['baseline_rhs_l2']:.12e}")
        print(f"selectable_rhs_l2: {result['selectable_rhs_l2']:.12e}")
        print(f"diff_l2: {result['diff_l2']:.12e}")
        print(f"diff_max_abs: {result['diff_max_abs']:.12e}")
        print(f"relative_error: {result['relative_error']:.12e}")
        print(f"cosine_similarity: {result['cosine_similarity']:.12e}")
        print(f"finite_all: {result['finite_all']}")
        print(f"real_all: {result['real_all']}")
        print(f"input_w_unchanged: {result['input_w_unchanged']}")
        print(f"baseline_solver_w_unchanged: {result['baseline_solver_w_unchanged']}")
        print(f"selectable_solver_w_unchanged: {result['selectable_solver_w_unchanged']}")
        print(f"exact_match: {result['exact_match']}")
        print(f"strict_equivalence: {result['strict_equivalence']}")
        print(f"metadata_method_ok: {result['metadata_method_ok']}")
        print(f"metadata_rhs_method_ok: {result['metadata_rhs_method_ok']}")
        print(f"metadata_variant_ok: {result['metadata_variant_ok']}")
        print(f"metadata_baseline_ok: {result['metadata_baseline_ok']}")
        print(f"metadata_run_disabled_ok: {result['metadata_run_disabled_ok']}")
        print(f"metadata_no_turbulence_claim: {result['metadata_no_turbulence_claim']}")
        print(f"metadata_no_k_minus_3_claim: {result['metadata_no_k_minus_3_claim']}")
        print(f"run_disabled: {result['run_disabled']}")
        print(f"overall_result: {result['overall_result']}")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

all_pass = (df["overall_result"] == "PASS").all()

print("\n=== OVERALL RESULT ===")
print(f"Phase 10N.1 fd_centered RHS equivalence audit: {pass_fail(all_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 10N.1 fd_centered RHS equivalence audit complete.")