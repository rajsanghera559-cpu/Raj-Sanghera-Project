from pathlib import Path

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.advection_operators import (
    advection_fd_centered,
    advection_pseudo_spectral,
    advection_arakawa,
    jacobian_arakawa_periodic,
    l2_norm,
    max_abs,
)


OUT_CSV = Path("PHASE10G_ARAKAWA_OPERATOR_SANITY_AUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    return float(np.sqrt(np.mean(np.asarray(field) ** 2)))


def safe_relative_error(a, b):
    denom = max(abs(float(b)), 1e-300)
    return abs(float(a)) / denom


def cosine_similarity(a, b):
    a_flat = np.asarray(a).ravel()
    b_flat = np.asarray(b).ravel()

    denom = np.linalg.norm(a_flat) * np.linalg.norm(b_flat)

    if denom <= 0:
        return np.nan

    return float(np.dot(a_flat, b_flat) / denom)


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
            "classification": "near_null_reference",
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


def audit_case(N, field_name, field_info):
    run_path = Path("experiments") / "method_diagnostics" / f"phase10G_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    w = np.asarray(field_info["field"])
    w_before = w.copy()
    solver_w_before = solver.w.copy()

    psi = solver.streamfunction(w)
    psi_before = psi.copy()

    fd_adv = advection_fd_centered(solver, w)
    ps_adv = advection_pseudo_spectral(solver, w, dealias_product=False)
    ar_adv = advection_arakawa(solver, w)
    ar_jacobian = jacobian_arakawa_periodic(psi, w, solver.dx)

    finite_all = (
        np.isfinite(w).all()
        and np.isfinite(psi).all()
        and np.isfinite(fd_adv).all()
        and np.isfinite(ps_adv).all()
        and np.isfinite(ar_adv).all()
        and np.isfinite(ar_jacobian).all()
    )

    real_all = (
        np.isrealobj(fd_adv)
        and np.isrealobj(ps_adv)
        and np.isrealobj(ar_adv)
        and np.isrealobj(ar_jacobian)
    )

    input_w_unchanged = np.allclose(w, w_before, rtol=0.0, atol=0.0)
    input_psi_unchanged = np.allclose(psi, psi_before, rtol=0.0, atol=0.0)
    solver_w_unchanged = np.allclose(solver.w, solver_w_before, rtol=0.0, atol=0.0)

    fd_l2 = l2_norm(fd_adv)
    ps_l2 = l2_norm(ps_adv)
    ar_l2 = l2_norm(ar_adv)

    ar_minus_ps = ar_adv - ps_adv
    ar_minus_fd = ar_adv - fd_adv
    fd_minus_ps = fd_adv - ps_adv

    ar_ps_diff_l2 = l2_norm(ar_minus_ps)
    ar_fd_diff_l2 = l2_norm(ar_minus_fd)
    fd_ps_diff_l2 = l2_norm(fd_minus_ps)

    ar_ps_rel_error = safe_relative_error(ar_ps_diff_l2, ps_l2)
    ar_fd_rel_error = safe_relative_error(ar_fd_diff_l2, fd_l2)
    fd_ps_rel_error = safe_relative_error(fd_ps_diff_l2, ps_l2)

    ar_ps_cosine = cosine_similarity(ar_adv, ps_adv)
    ar_fd_cosine = cosine_similarity(ar_adv, fd_adv)
    fd_ps_cosine = cosine_similarity(fd_adv, ps_adv)

    nonzero_primary_operator = ps_l2 > 1e-18 if field_info["primary_evidence"] else True

    sign_matches_pseudo_spectral = (
        ar_ps_cosine > 0.90 if field_info["primary_evidence"] else True
    )

    sign_not_flipped = (
        ar_ps_cosine > 0.0 if np.isfinite(ar_ps_cosine) else field_info["primary_evidence"] is False
    )

    primary_quality = (
        finite_all
        and real_all
        and input_w_unchanged
        and input_psi_unchanged
        and solver_w_unchanged
        and nonzero_primary_operator
        and sign_matches_pseudo_spectral
        and sign_not_flipped
    )

    overall_case_result = primary_quality if field_info["primary_evidence"] else (
        finite_all
        and real_all
        and input_w_unchanged
        and input_psi_unchanged
        and solver_w_unchanged
    )

    return {
        "N": N,
        "field_name": field_name,
        "classification": field_info["classification"],
        "primary_evidence": bool(field_info["primary_evidence"]),
        "field_rms": rms(w),
        "field_max_abs": max_abs(w),
        "finite_all": pass_fail(finite_all),
        "real_all": pass_fail(real_all),
        "input_w_unchanged": pass_fail(input_w_unchanged),
        "input_psi_unchanged": pass_fail(input_psi_unchanged),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "fd_l2": fd_l2,
        "pseudo_spectral_l2": ps_l2,
        "arakawa_l2": ar_l2,
        "fd_vs_pseudo_spectral_diff_l2": fd_ps_diff_l2,
        "arakawa_vs_pseudo_spectral_diff_l2": ar_ps_diff_l2,
        "arakawa_vs_fd_diff_l2": ar_fd_diff_l2,
        "fd_vs_pseudo_spectral_relative_error": fd_ps_rel_error,
        "arakawa_vs_pseudo_spectral_relative_error": ar_ps_rel_error,
        "arakawa_vs_fd_relative_error": ar_fd_rel_error,
        "fd_vs_pseudo_spectral_cosine": fd_ps_cosine,
        "arakawa_vs_pseudo_spectral_cosine": ar_ps_cosine,
        "arakawa_vs_fd_cosine": ar_fd_cosine,
        "arakawa_max_abs": max_abs(ar_adv),
        "pseudo_spectral_max_abs": max_abs(ps_adv),
        "fd_max_abs": max_abs(fd_adv),
        "nonzero_primary_operator": pass_fail(nonzero_primary_operator),
        "sign_matches_pseudo_spectral": pass_fail(sign_matches_pseudo_spectral),
        "sign_not_flipped": pass_fail(sign_not_flipped),
        "overall_case_result": pass_fail(overall_case_result),
    }


print("\n=== PHASE 10G ARAKAWA OPERATOR SANITY AUDIT ===")
print("Purpose: sanity-check standalone Arakawa operator implementation.")
print("This does not modify SpectralSolver.")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")

rows = []

for N in [64, 128]:
    print(f"\n=== N={N} ===")

    run_path = Path("experiments") / "method_diagnostics" / f"phase10G_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    fields = build_test_fields(solver)

    for field_name, field_info in fields.items():
        result = audit_case(N, field_name, field_info)
        rows.append(result)

        print(f"\nField: {field_name}")
        print(f"classification: {result['classification']}")
        print(f"primary_evidence: {result['primary_evidence']}")
        print(f"finite_all: {result['finite_all']}")
        print(f"real_all: {result['real_all']}")
        print(f"input_w_unchanged: {result['input_w_unchanged']}")
        print(f"input_psi_unchanged: {result['input_psi_unchanged']}")
        print(f"solver_w_unchanged: {result['solver_w_unchanged']}")
        print(f"fd_l2: {result['fd_l2']:.12e}")
        print(f"pseudo_spectral_l2: {result['pseudo_spectral_l2']:.12e}")
        print(f"arakawa_l2: {result['arakawa_l2']:.12e}")
        print(f"arakawa_vs_pseudo_spectral_relative_error: {result['arakawa_vs_pseudo_spectral_relative_error']:.12e}")
        print(f"arakawa_vs_pseudo_spectral_cosine: {result['arakawa_vs_pseudo_spectral_cosine']:.12e}")
        print(f"arakawa_vs_fd_cosine: {result['arakawa_vs_fd_cosine']:.12e}")
        print(f"sign_matches_pseudo_spectral: {result['sign_matches_pseudo_spectral']}")
        print(f"sign_not_flipped: {result['sign_not_flipped']}")
        print(f"overall_case_result: {result['overall_case_result']}")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

primary_df = df[df["primary_evidence"] == True]
near_null_df = df[df["primary_evidence"] == False]

primary_pass = (primary_df["overall_case_result"] == "PASS").all()
near_null_review_retained = len(near_null_df) > 0

overall_pass = bool(primary_pass and near_null_review_retained)

print("\n=== OVERALL RESULT ===")
print(f"Primary nonlinear fields pass: {pass_fail(primary_pass)}")
print(f"Near-null single-mode reference retained: {pass_fail(near_null_review_retained)}")
print(f"Phase 10G Arakawa operator sanity audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print("Wrote: PHASE10G_ARAKAWA_OPERATOR_SANITY_AUDIT.csv")
print("Phase 10G Arakawa operator sanity audit complete.")