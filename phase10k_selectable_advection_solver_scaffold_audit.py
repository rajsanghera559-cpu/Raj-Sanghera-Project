from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver
from project.solver.advection_operators import (
    advection_fd_centered,
    advection_pseudo_spectral,
    advection_arakawa,
    l2_norm,
    max_abs,
)


OUT_CSV = Path("PHASE10K1_SELECTABLE_ADVECTION_SOLVER_SCAFFOLD_AUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    return float(np.sqrt(np.mean(np.asarray(field) ** 2)))


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


def build_test_field(solver):
    X = solver.X
    Y = solver.Y

    raw = (
        np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(Y)
        + 0.50 * np.sin(X) * np.cos(4 * Y)
        + 0.35 * np.cos(4 * X - 2 * Y)
    )

    field_rms = rms(raw)

    if field_rms == 0:
        raise ValueError("Cannot rescale zero-RMS field.")

    return raw * (0.01 / field_rms)


def expected_operator_output(solver, w, method):
    if method == "fd_centered":
        return advection_fd_centered(solver, w)

    if method == "pseudo_spectral":
        return advection_pseudo_spectral(solver, w, dealias_product=False)

    if method == "arakawa":
        return advection_arakawa(solver, w)

    raise ValueError(f"Unexpected method: {method}")


def audit_method(method):
    run_path = Path("experiments") / "method_diagnostics" / f"phase10K1_{method}"
    solver = SelectableAdvectionSolver(
        nx=64,
        ny=64,
        Re=1000,
        run_path=run_path,
        dt=0.005,
        steps=1,
        advection_method=method,
    )

    w = build_test_field(solver)
    w_before = w.copy()
    solver_w_before = solver.w.copy()

    selected_adv = solver.compute_advection(w)
    expected_adv = expected_operator_output(solver, w, method)

    diff = selected_adv - expected_adv

    finite_output = np.isfinite(selected_adv).all()
    real_output = np.isrealobj(selected_adv)
    input_w_unchanged = np.allclose(w, w_before, rtol=0.0, atol=0.0)
    solver_w_unchanged = np.allclose(solver.w, solver_w_before, rtol=0.0, atol=0.0)
    matches_direct_operator = np.allclose(selected_adv, expected_adv, rtol=0.0, atol=0.0)

    metadata = solver.selectable_advection_metadata()

    metadata_has_solver_variant = metadata.get("solver_variant") == "selectable_advection"
    metadata_has_solver_class = metadata.get("solver_class") == "SelectableAdvectionSolver"
    metadata_has_baseline_class = metadata.get("baseline_solver_class") == "SpectralSolver"
    metadata_has_method = metadata.get("advection_method") == method
    metadata_baseline_unmodified = metadata.get("production_baseline_modified") is False
    metadata_no_turbulence_claim = metadata.get("turbulence_claim") is False
    metadata_no_k_minus_3_claim = metadata.get("k_minus_3_claim") is False

    try:
        solver.run()
        run_disabled = False
    except NotImplementedError:
        run_disabled = True

    overall = all(
        [
            solver.advection_method == method,
            finite_output,
            real_output,
            input_w_unchanged,
            solver_w_unchanged,
            matches_direct_operator,
            metadata_has_solver_variant,
            metadata_has_solver_class,
            metadata_has_baseline_class,
            metadata_has_method,
            metadata_baseline_unmodified,
            metadata_no_turbulence_claim,
            metadata_no_k_minus_3_claim,
            run_disabled,
        ]
    )

    return {
        "test_type": "method_audit",
        "method": method,
        "constructor_accepts_method": pass_fail(solver.advection_method == method),
        "finite_output": pass_fail(finite_output),
        "real_output": pass_fail(real_output),
        "input_w_unchanged": pass_fail(input_w_unchanged),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "matches_direct_operator": pass_fail(matches_direct_operator),
        "selected_adv_l2": l2_norm(selected_adv),
        "expected_adv_l2": l2_norm(expected_adv),
        "diff_l2": l2_norm(diff),
        "diff_max_abs": max_abs(diff),
        "cosine_similarity_vs_direct_operator": cosine_similarity(selected_adv, expected_adv),
        "metadata_has_solver_variant": pass_fail(metadata_has_solver_variant),
        "metadata_has_solver_class": pass_fail(metadata_has_solver_class),
        "metadata_has_baseline_class": pass_fail(metadata_has_baseline_class),
        "metadata_has_method": pass_fail(metadata_has_method),
        "metadata_baseline_unmodified": pass_fail(metadata_baseline_unmodified),
        "metadata_no_turbulence_claim": pass_fail(metadata_no_turbulence_claim),
        "metadata_no_k_minus_3_claim": pass_fail(metadata_no_k_minus_3_claim),
        "run_disabled": pass_fail(run_disabled),
        "overall_result": pass_fail(overall),
    }


def audit_invalid_method():
    try:
        SelectableAdvectionSolver(
            nx=64,
            ny=64,
            Re=1000,
            run_path=Path("experiments") / "method_diagnostics" / "phase10K1_invalid",
            dt=0.005,
            steps=1,
            advection_method="invalid_method",
        )
        rejected_invalid_method = False
    except ValueError:
        rejected_invalid_method = True

    return {
        "test_type": "invalid_method_audit",
        "method": "invalid_method",
        "constructor_accepts_method": "N/A",
        "finite_output": "N/A",
        "real_output": "N/A",
        "input_w_unchanged": "N/A",
        "solver_w_unchanged": "N/A",
        "matches_direct_operator": "N/A",
        "selected_adv_l2": np.nan,
        "expected_adv_l2": np.nan,
        "diff_l2": np.nan,
        "diff_max_abs": np.nan,
        "cosine_similarity_vs_direct_operator": np.nan,
        "metadata_has_solver_variant": "N/A",
        "metadata_has_solver_class": "N/A",
        "metadata_has_baseline_class": "N/A",
        "metadata_has_method": "N/A",
        "metadata_baseline_unmodified": "N/A",
        "metadata_no_turbulence_claim": "N/A",
        "metadata_no_k_minus_3_claim": "N/A",
        "run_disabled": "N/A",
        "overall_result": pass_fail(rejected_invalid_method),
    }


print("\n=== PHASE 10K.1 SELECTABLE-ADVECTION SOLVER SCAFFOLD AUDIT ===")
print("Purpose: audit scaffold imports, method selection, metadata, run disabling, and baseline preservation.")
print("This does not modify SpectralSolver.")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")

rows = []

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods = SelectableAdvectionSolver.supported_advection_methods()
supported_methods_ok = supported_methods == ("fd_centered", "pseudo_spectral", "arakawa")
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")

print("\n=== IMPORT AND BASELINE CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"Supported methods: {supported_methods}")
print(f"Supported methods check: {pass_fail(supported_methods_ok)}")
print(f"Default method is fd_centered: {pass_fail(default_method_ok)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")

rows.append(
    {
        "test_type": "global_audit",
        "method": "global",
        "constructor_accepts_method": "N/A",
        "finite_output": "N/A",
        "real_output": "N/A",
        "input_w_unchanged": "N/A",
        "solver_w_unchanged": "N/A",
        "matches_direct_operator": "N/A",
        "selected_adv_l2": np.nan,
        "expected_adv_l2": np.nan,
        "diff_l2": np.nan,
        "diff_max_abs": np.nan,
        "cosine_similarity_vs_direct_operator": np.nan,
        "metadata_has_solver_variant": "N/A",
        "metadata_has_solver_class": "N/A",
        "metadata_has_baseline_class": "N/A",
        "metadata_has_method": "N/A",
        "metadata_baseline_unmodified": pass_fail(spectral_solver_no_diff),
        "metadata_no_turbulence_claim": "N/A",
        "metadata_no_k_minus_3_claim": "N/A",
        "run_disabled": "N/A",
        "overall_result": pass_fail(
            baseline_import_ok
            and selectable_import_ok
            and supported_methods_ok
            and default_method_ok
            and spectral_solver_no_diff
        ),
    }
)

for method in supported_methods:
    print(f"\n=== METHOD AUDIT: {method} ===")
    result = audit_method(method)
    rows.append(result)

    print(f"constructor_accepts_method: {result['constructor_accepts_method']}")
    print(f"finite_output: {result['finite_output']}")
    print(f"real_output: {result['real_output']}")
    print(f"input_w_unchanged: {result['input_w_unchanged']}")
    print(f"solver_w_unchanged: {result['solver_w_unchanged']}")
    print(f"matches_direct_operator: {result['matches_direct_operator']}")
    print(f"selected_adv_l2: {result['selected_adv_l2']:.12e}")
    print(f"expected_adv_l2: {result['expected_adv_l2']:.12e}")
    print(f"diff_l2: {result['diff_l2']:.12e}")
    print(f"diff_max_abs: {result['diff_max_abs']:.12e}")
    print(f"cosine_similarity_vs_direct_operator: {result['cosine_similarity_vs_direct_operator']:.12e}")
    print(f"metadata_has_solver_variant: {result['metadata_has_solver_variant']}")
    print(f"metadata_has_solver_class: {result['metadata_has_solver_class']}")
    print(f"metadata_has_baseline_class: {result['metadata_has_baseline_class']}")
    print(f"metadata_has_method: {result['metadata_has_method']}")
    print(f"metadata_baseline_unmodified: {result['metadata_baseline_unmodified']}")
    print(f"metadata_no_turbulence_claim: {result['metadata_no_turbulence_claim']}")
    print(f"metadata_no_k_minus_3_claim: {result['metadata_no_k_minus_3_claim']}")
    print(f"run_disabled: {result['run_disabled']}")
    print(f"overall_result: {result['overall_result']}")

print("\n=== INVALID METHOD AUDIT ===")
invalid_result = audit_invalid_method()
rows.append(invalid_result)
print(f"invalid method rejected: {invalid_result['overall_result']}")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

all_pass = (df["overall_result"] == "PASS").all()

print("\n=== OVERALL RESULT ===")
print(f"Phase 10K.1 selectable-advection solver scaffold audit: {pass_fail(all_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 10K.1 scaffold audit complete.")