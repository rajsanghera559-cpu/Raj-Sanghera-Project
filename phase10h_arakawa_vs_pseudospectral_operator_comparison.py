from pathlib import Path

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.advection_operators import (
    advection_fd_centered,
    advection_pseudo_spectral,
    advection_arakawa,
    l2_norm,
    max_abs,
)


OUT_CSV = Path("PHASE10H_ARAKAWA_VS_PSEUDOSPECTRAL_OPERATOR_COMPARISON.csv")
OUT_RESOLUTION_CSV = Path("PHASE10H_ARAKAWA_RESOLUTION_SUMMARY.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    return float(np.sqrt(np.mean(np.asarray(field) ** 2)))


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
    run_path = Path("experiments") / "method_diagnostics" / f"phase10H_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    w = np.asarray(field_info["field"])
    w_before = w.copy()
    solver_w_before = solver.w.copy()

    fd_adv = advection_fd_centered(solver, w)
    ps_adv = advection_pseudo_spectral(solver, w, dealias_product=False)
    ar_adv = advection_arakawa(solver, w)

    fd_l2 = l2_norm(fd_adv)
    ps_l2 = l2_norm(ps_adv)
    ar_l2 = l2_norm(ar_adv)

    fd_ps_diff_l2 = l2_norm(fd_adv - ps_adv)
    ar_ps_diff_l2 = l2_norm(ar_adv - ps_adv)
    ar_fd_diff_l2 = l2_norm(ar_adv - fd_adv)

    fd_ps_rel_error = relative_error(fd_ps_diff_l2, ps_l2)
    ar_ps_rel_error = relative_error(ar_ps_diff_l2, ps_l2)
    ar_fd_rel_error = relative_error(ar_fd_diff_l2, fd_l2)

    fd_ps_cosine = cosine_similarity(fd_adv, ps_adv)
    ar_ps_cosine = cosine_similarity(ar_adv, ps_adv)
    ar_fd_cosine = cosine_similarity(ar_adv, fd_adv)

    finite_all = (
        np.isfinite(w).all()
        and np.isfinite(fd_adv).all()
        and np.isfinite(ps_adv).all()
        and np.isfinite(ar_adv).all()
    )

    real_all = (
        np.isrealobj(fd_adv)
        and np.isrealobj(ps_adv)
        and np.isrealobj(ar_adv)
    )

    input_w_unchanged = np.allclose(w, w_before, rtol=0.0, atol=0.0)
    solver_w_unchanged = np.allclose(solver.w, solver_w_before, rtol=0.0, atol=0.0)

    nonzero_operator = ps_l2 > 1e-18 if field_info["primary_evidence"] else True

    if field_info["primary_evidence"]:
        sign_ok = ar_ps_cosine > 0.99
        fd_sign_ok = fd_ps_cosine > 0.99
    else:
        sign_ok = True
        fd_sign_ok = True

    arakawa_not_worse_than_fd_by_large_factor = (
        ar_ps_rel_error <= 1.25 * fd_ps_rel_error
        if field_info["primary_evidence"]
        else True
    )

    case_pass = all(
        [
            finite_all,
            real_all,
            input_w_unchanged,
            solver_w_unchanged,
            nonzero_operator,
            sign_ok,
            fd_sign_ok,
            arakawa_not_worse_than_fd_by_large_factor,
        ]
    )

    if field_info["primary_evidence"]:
        if ar_ps_rel_error < fd_ps_rel_error:
            arakawa_vs_fd_quality = "BETTER_THAN_FD"
        elif ar_ps_rel_error <= 1.25 * fd_ps_rel_error:
            arakawa_vs_fd_quality = "COMPARABLE_TO_FD"
        else:
            arakawa_vs_fd_quality = "WORSE_THAN_FD_REVIEW"
    else:
        arakawa_vs_fd_quality = "NEAR_NULL_REVIEW"

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
        "fd_max_abs": max_abs(fd_adv),
        "pseudo_spectral_max_abs": max_abs(ps_adv),
        "arakawa_max_abs": max_abs(ar_adv),
        "nonzero_operator": pass_fail(nonzero_operator),
        "fd_sign_ok": pass_fail(fd_sign_ok),
        "arakawa_sign_ok": pass_fail(sign_ok),
        "arakawa_not_worse_than_fd_by_large_factor": pass_fail(arakawa_not_worse_than_fd_by_large_factor),
        "arakawa_vs_fd_quality": arakawa_vs_fd_quality,
        "overall_case_result": pass_fail(case_pass),
    }


print("\n=== PHASE 10H ARAKAWA VS PSEUDO-SPECTRAL OPERATOR COMPARISON ===")
print("Purpose: compare Arakawa, finite-difference, and pseudo-spectral advection operators.")
print("This does not modify SpectralSolver.")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")

rows = []

for N in [64, 128]:
    print(f"\n=== N={N} ===")

    run_path = Path("experiments") / "method_diagnostics" / f"phase10H_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    fields = build_test_fields(solver)

    for field_name, field_info in fields.items():
        result = audit_case(N, field_name, field_info)
        rows.append(result)

        print(f"\nField: {field_name}")
        print(f"classification: {result['classification']}")
        print(f"primary_evidence: {result['primary_evidence']}")
        print(f"fd_vs_ps_rel_error: {result['fd_vs_pseudo_spectral_relative_error']:.12e}")
        print(f"arakawa_vs_ps_rel_error: {result['arakawa_vs_pseudo_spectral_relative_error']:.12e}")
        print(f"arakawa_vs_fd_rel_error: {result['arakawa_vs_fd_relative_error']:.12e}")
        print(f"fd_vs_ps_cosine: {result['fd_vs_pseudo_spectral_cosine']:.12e}")
        print(f"arakawa_vs_ps_cosine: {result['arakawa_vs_pseudo_spectral_cosine']:.12e}")
        print(f"arakawa_vs_fd_cosine: {result['arakawa_vs_fd_cosine']:.12e}")
        print(f"arakawa_vs_fd_quality: {result['arakawa_vs_fd_quality']}")
        print(f"overall_case_result: {result['overall_case_result']}")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

resolution_rows = []

for field_name in sorted(df["field_name"].unique()):
    row64 = df[(df["N"] == 64) & (df["field_name"] == field_name)].iloc[0]
    row128 = df[(df["N"] == 128) & (df["field_name"] == field_name)].iloc[0]

    fd_err64 = float(row64["fd_vs_pseudo_spectral_relative_error"])
    fd_err128 = float(row128["fd_vs_pseudo_spectral_relative_error"])
    ar_err64 = float(row64["arakawa_vs_pseudo_spectral_relative_error"])
    ar_err128 = float(row128["arakawa_vs_pseudo_spectral_relative_error"])

    fd_ratio = fd_err128 / fd_err64 if fd_err64 > 0 else np.nan
    ar_ratio = ar_err128 / ar_err64 if ar_err64 > 0 else np.nan

    primary = bool(row64["primary_evidence"])

    fd_improved = fd_err128 < fd_err64
    ar_improved = ar_err128 < ar_err64

    if primary:
        fd_second_order_window = 0.15 <= fd_ratio <= 0.40
        ar_second_order_window = 0.15 <= ar_ratio <= 0.40
        resolution_result = fd_improved and ar_improved and ar_second_order_window
    else:
        fd_second_order_window = False
        ar_second_order_window = False
        resolution_result = True

    resolution_rows.append(
        {
            "field_name": field_name,
            "classification": row64["classification"],
            "primary_evidence": primary,
            "fd_N64_error": fd_err64,
            "fd_N128_error": fd_err128,
            "fd_N128_over_N64_error_ratio": fd_ratio,
            "fd_improved_at_N128": pass_fail(fd_improved),
            "fd_second_order_window": pass_fail(fd_second_order_window),
            "arakawa_N64_error": ar_err64,
            "arakawa_N128_error": ar_err128,
            "arakawa_N128_over_N64_error_ratio": ar_ratio,
            "arakawa_improved_at_N128": pass_fail(ar_improved),
            "arakawa_second_order_window": pass_fail(ar_second_order_window),
            "resolution_result": pass_fail(resolution_result),
        }
    )

resolution_df = pd.DataFrame(resolution_rows)
resolution_df.to_csv(OUT_RESOLUTION_CSV, index=False)

print("\n=== RESOLUTION SUMMARY ===")

for _, row in resolution_df.iterrows():
    print(f"\nField: {row['field_name']}")
    print(f"classification: {row['classification']}")
    print(f"primary_evidence: {row['primary_evidence']}")
    print(f"FD N64 error: {row['fd_N64_error']:.12e}")
    print(f"FD N128 error: {row['fd_N128_error']:.12e}")
    print(f"FD N128/N64 ratio: {row['fd_N128_over_N64_error_ratio']:.12e}")
    print(f"Arakawa N64 error: {row['arakawa_N64_error']:.12e}")
    print(f"Arakawa N128 error: {row['arakawa_N128_error']:.12e}")
    print(f"Arakawa N128/N64 ratio: {row['arakawa_N128_over_N64_error_ratio']:.12e}")
    print(f"resolution_result: {row['resolution_result']}")

primary_cases = df[df["primary_evidence"] == True]
primary_case_pass = (primary_cases["overall_case_result"] == "PASS").all()

primary_resolution = resolution_df[resolution_df["primary_evidence"] == True]
primary_resolution_pass = (primary_resolution["resolution_result"] == "PASS").all()

near_null_retained = (df["primary_evidence"] == False).any()

overall_pass = bool(primary_case_pass and primary_resolution_pass and near_null_retained)

print("\n=== OVERALL RESULT ===")
print(f"Primary operator cases pass: {pass_fail(primary_case_pass)}")
print(f"Primary resolution behavior pass: {pass_fail(primary_resolution_pass)}")
print(f"Near-null reference retained: {pass_fail(near_null_retained)}")
print(f"Phase 10H Arakawa comparison audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print(f"Wrote: {OUT_RESOLUTION_CSV}")
print("Phase 10H Arakawa vs pseudo-spectral operator comparison complete.")