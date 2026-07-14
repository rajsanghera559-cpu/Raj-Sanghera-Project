from pathlib import Path

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.advection_operators import (
    advection_fd_centered,
    advection_pseudo_spectral,
    advection_arakawa,
    apply_dealias_mask,
    compare_advection_operators,
    ensure_real_array,
    jacobian_arakawa_periodic,
    l2_norm,
    max_abs,
    velocity_from_vorticity,
    vorticity_grad_fd_centered,
    vorticity_grad_pseudo_spectral,
)


OUT_CSV = Path("PHASE10C1_ADVECTION_OPERATOR_SCAFFOLD_AUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    return float(np.sqrt(np.mean(np.asarray(field) ** 2)))


def rescale_to_rms(field, target_rms):
    field_rms = rms(field)
    if field_rms == 0:
        raise ValueError("Cannot rescale zero-RMS field.")
    return field * (target_rms / field_rms)


def embedded_solver_fd_advection(solver, w):
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)

    wx = (np.roll(w, -1, 1) - np.roll(w, 1, 1)) / (2 * solver.dx)
    wy = (np.roll(w, -1, 0) - np.roll(w, 1, 0)) / (2 * solver.dx)

    return u * wx + v * wy


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
        "single_mode_k2_2": single_mode,
        "low_mode_pair": low_mode_pair,
        "phase6d_like_multimode": phase6d_like,
        "higher_smooth_multimode": higher_smooth,
    }


def arakawa_placeholder_check(solver, w):
    psi = solver.streamfunction(w)

    jacobian_raised = False
    advection_raised = False

    try:
        jacobian_arakawa_periodic(psi, w, solver.dx)
    except NotImplementedError:
        jacobian_raised = True

    try:
        advection_arakawa(solver, w)
    except NotImplementedError:
        advection_raised = True

    return jacobian_raised and advection_raised


def run_case(N, field_name, w):
    run_path = Path("experiments") / "method_diagnostics" / f"phase10C1_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    w_before = w.copy()
    solver_w_before = solver.w.copy()

    arr = ensure_real_array(w)

    u, v = velocity_from_vorticity(solver, arr)
    wx_fd, wy_fd = vorticity_grad_fd_centered(solver, arr)
    wx_ps, wy_ps = vorticity_grad_pseudo_spectral(solver, arr)

    fd_from_scaffold = advection_fd_centered(solver, arr)
    fd_from_embedded_logic = embedded_solver_fd_advection(solver, arr)

    fd_match_diff = fd_from_scaffold - fd_from_embedded_logic
    fd_match_l2 = l2_norm(fd_match_diff)
    fd_match_max = max_abs(fd_match_diff)

    ps_no_dealias = advection_pseudo_spectral(solver, arr, dealias_product=False)
    ps_dealias = advection_pseudo_spectral(solver, arr, dealias_product=True)

    direct_dealias = apply_dealias_mask(solver, ps_no_dealias)
    dealias_match_l2 = l2_norm(ps_dealias - direct_dealias)

    comparison = compare_advection_operators(
        solver,
        arr,
        dealias_pseudo_spectral=False,
    )

    arakawa_placeholders_ok = arakawa_placeholder_check(solver, arr)

    w_unchanged = np.allclose(w, w_before, rtol=0.0, atol=0.0)
    solver_w_unchanged = np.allclose(solver.w, solver_w_before, rtol=0.0, atol=0.0)

    finite_all = (
        np.isfinite(arr).all()
        and np.isfinite(u).all()
        and np.isfinite(v).all()
        and np.isfinite(wx_fd).all()
        and np.isfinite(wy_fd).all()
        and np.isfinite(wx_ps).all()
        and np.isfinite(wy_ps).all()
        and np.isfinite(fd_from_scaffold).all()
        and np.isfinite(fd_from_embedded_logic).all()
        and np.isfinite(ps_no_dealias).all()
        and np.isfinite(ps_dealias).all()
    )

    fd_matches_embedded = fd_match_l2 < 1e-14 and fd_match_max < 1e-14
    dealias_consistent = dealias_match_l2 < 1e-14

    overall_case_pass = all(
        [
            finite_all,
            fd_matches_embedded,
            dealias_consistent,
            arakawa_placeholders_ok,
            w_unchanged,
            solver_w_unchanged,
            comparison["finite_all"] == "PASS",
        ]
    )

    return {
        "N": N,
        "field_name": field_name,
        "field_rms": rms(arr),
        "field_max_abs": max_abs(arr),
        "finite_all": pass_fail(finite_all),
        "fd_matches_embedded": pass_fail(fd_matches_embedded),
        "fd_match_l2": fd_match_l2,
        "fd_match_max_abs": fd_match_max,
        "pseudo_spectral_dealias_consistent": pass_fail(dealias_consistent),
        "dealias_match_l2": dealias_match_l2,
        "arakawa_placeholders_raise_NotImplementedError": pass_fail(arakawa_placeholders_ok),
        "input_field_unchanged": pass_fail(w_unchanged),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "fd_adv_l2": comparison["fd_adv_l2"],
        "pseudo_spectral_adv_l2": comparison["pseudo_spectral_adv_l2"],
        "diff_l2": comparison["diff_l2"],
        "relative_l2_error_vs_pseudo_spectral": comparison["relative_l2_error_vs_pseudo_spectral"],
        "cosine_similarity": comparison["cosine_similarity"],
        "overall_case_result": pass_fail(overall_case_pass),
    }


print("\n=== PHASE 10C.1 ADVECTION OPERATOR SCAFFOLD AUDIT ===")
print("Purpose: import and sanity-check project/solver/advection_operators.py")
print("This does not modify SpectralSolver.")
print("This does not run a production simulation.")
print("This does not implement Arakawa yet.")

rows = []

for N in [64, 128]:
    print(f"\n=== N={N} ===")

    run_path = Path("experiments") / "method_diagnostics" / f"phase10C1_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    fields = build_test_fields(solver)

    for field_name, w in fields.items():
        result = run_case(N, field_name, w)
        rows.append(result)

        print(f"\nField: {field_name}")
        print(f"finite_all: {result['finite_all']}")
        print(f"fd_matches_embedded: {result['fd_matches_embedded']}")
        print(f"fd_match_l2: {result['fd_match_l2']:.12e}")
        print(f"pseudo_spectral_dealias_consistent: {result['pseudo_spectral_dealias_consistent']}")
        print(f"arakawa_placeholders_raise_NotImplementedError: {result['arakawa_placeholders_raise_NotImplementedError']}")
        print(f"input_field_unchanged: {result['input_field_unchanged']}")
        print(f"solver_w_unchanged: {result['solver_w_unchanged']}")
        print(f"relative_l2_error_vs_pseudo_spectral: {result['relative_l2_error_vs_pseudo_spectral']:.12e}")
        print(f"cosine_similarity: {result['cosine_similarity']:.12e}")
        print(f"overall_case_result: {result['overall_case_result']}")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

overall_pass = (df["overall_case_result"] == "PASS").all()

print("\n=== OVERALL RESULT ===")
print(f"Phase 10C.1 scaffold audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 10C.1 advection operator scaffold audit complete.")