from pathlib import Path

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.advection_operators import (
    advection_fd_centered,
    advection_pseudo_spectral,
    compare_advection_operators,
    l2_norm,
    max_abs,
)


OUT_CSV = Path("PHASE10D_ADVECTION_OPERATOR_COMPARISON_AUDIT.csv")
OUT_COMPARISON_CSV = Path("PHASE10D_ADVECTION_OPERATOR_RESOLUTION_COMPARISON.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    return float(np.sqrt(np.mean(np.asarray(field) ** 2)))


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


def audit_case(N, field_name, field_info, dealias_pseudo_spectral):
    run_path = Path("experiments") / "method_diagnostics" / f"phase10D_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    w = field_info["field"]

    fd_adv = advection_fd_centered(solver, w)
    ps_adv = advection_pseudo_spectral(
        solver,
        w,
        dealias_product=dealias_pseudo_spectral,
    )

    comparison = compare_advection_operators(
        solver,
        w,
        dealias_pseudo_spectral=dealias_pseudo_spectral,
    )

    fd_l2 = float(comparison["fd_adv_l2"])
    ps_l2 = float(comparison["pseudo_spectral_adv_l2"])
    diff_l2 = float(comparison["diff_l2"])
    rel_error = float(comparison["relative_l2_error_vs_pseudo_spectral"])
    cosine = float(comparison["cosine_similarity"])

    finite_all = comparison["finite_all"] == "PASS"
    nonzero_operator = ps_l2 > 1e-18

    if field_info["primary_evidence"]:
        primary_field_quality = (
            finite_all
            and nonzero_operator
            and np.isfinite(rel_error)
            and cosine > 0.99
        )
    else:
        primary_field_quality = finite_all

    return {
        "N": N,
        "field_name": field_name,
        "classification": field_info["classification"],
        "primary_evidence": field_info["primary_evidence"],
        "dealias_pseudo_spectral_product": bool(dealias_pseudo_spectral),
        "field_rms": rms(w),
        "field_max_abs": max_abs(w),
        "finite_all": pass_fail(finite_all),
        "nonzero_operator": pass_fail(nonzero_operator),
        "fd_adv_l2": fd_l2,
        "pseudo_spectral_adv_l2": ps_l2,
        "diff_l2": diff_l2,
        "relative_l2_error_vs_pseudo_spectral": rel_error,
        "fd_adv_max_abs": float(comparison["fd_adv_max_abs"]),
        "pseudo_spectral_adv_max_abs": float(comparison["pseudo_spectral_adv_max_abs"]),
        "diff_max_abs": float(comparison["diff_max_abs"]),
        "cosine_similarity": cosine,
        "primary_field_quality": pass_fail(primary_field_quality),
    }


print("\n=== PHASE 10D ADVECTION OPERATOR COMPARISON AUDIT ===")
print("Purpose: formal comparison of finite-difference and pseudo-spectral advection diagnostics.")
print("This does not modify SpectralSolver.")
print("This does not implement Arakawa.")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")

rows = []

for dealias_pseudo_spectral in [False, True]:
    print(f"\n=== PSEUDO-SPECTRAL PRODUCT DEALIASING: {dealias_pseudo_spectral} ===")

    for N in [64, 128]:
        print(f"\n=== N={N} ===")

        run_path = Path("experiments") / "method_diagnostics" / f"phase10D_N{N}"
        solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

        fields = build_test_fields(solver)

        for field_name, field_info in fields.items():
            result = audit_case(N, field_name, field_info, dealias_pseudo_spectral)
            rows.append(result)

            print(f"\nField: {field_name}")
            print(f"classification: {result['classification']}")
            print(f"primary_evidence: {result['primary_evidence']}")
            print(f"finite_all: {result['finite_all']}")
            print(f"nonzero_operator: {result['nonzero_operator']}")
            print(f"fd_adv_l2: {result['fd_adv_l2']:.12e}")
            print(f"pseudo_spectral_adv_l2: {result['pseudo_spectral_adv_l2']:.12e}")
            print(f"diff_l2: {result['diff_l2']:.12e}")
            print(f"relative_l2_error_vs_pseudo_spectral: {result['relative_l2_error_vs_pseudo_spectral']:.12e}")
            print(f"cosine_similarity: {result['cosine_similarity']:.12e}")
            print(f"primary_field_quality: {result['primary_field_quality']}")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

comparison_rows = []

for dealias_pseudo_spectral in [False, True]:
    subset = df[df["dealias_pseudo_spectral_product"] == dealias_pseudo_spectral]

    for field_name in sorted(subset["field_name"].unique()):
        row64 = subset[(subset["N"] == 64) & (subset["field_name"] == field_name)].iloc[0]
        row128 = subset[(subset["N"] == 128) & (subset["field_name"] == field_name)].iloc[0]

        err64 = float(row64["relative_l2_error_vs_pseudo_spectral"])
        err128 = float(row128["relative_l2_error_vs_pseudo_spectral"])

        if err64 > 0:
            error_ratio = err128 / err64
        else:
            error_ratio = np.nan

        improved = bool(err128 < err64)

        primary = bool(row64["primary_evidence"])

        if primary:
            approximately_second_order = bool(0.15 <= error_ratio <= 0.40)
            comparison_result = improved and approximately_second_order
        else:
            approximately_second_order = False
            comparison_result = improved

        comparison_rows.append(
            {
                "dealias_pseudo_spectral_product": bool(dealias_pseudo_spectral),
                "field_name": field_name,
                "classification": row64["classification"],
                "primary_evidence": primary,
                "N64_relative_error": err64,
                "N128_relative_error": err128,
                "N128_over_N64_error_ratio": error_ratio,
                "improved_at_N128": pass_fail(improved),
                "approximately_second_order_window": pass_fail(approximately_second_order),
                "comparison_result": pass_fail(comparison_result),
            }
        )

comparison_df = pd.DataFrame(comparison_rows)
comparison_df.to_csv(OUT_COMPARISON_CSV, index=False)

print("\n=== RESOLUTION COMPARISON SUMMARY ===")

for _, row in comparison_df.iterrows():
    print(f"\nField: {row['field_name']}")
    print(f"dealias_pseudo_spectral_product: {row['dealias_pseudo_spectral_product']}")
    print(f"classification: {row['classification']}")
    print(f"primary_evidence: {row['primary_evidence']}")
    print(f"N64 relative error: {row['N64_relative_error']:.12e}")
    print(f"N128 relative error: {row['N128_relative_error']:.12e}")
    print(f"N128/N64 error ratio: {row['N128_over_N64_error_ratio']:.12e}")
    print(f"improved_at_N128: {row['improved_at_N128']}")
    print(f"approximately_second_order_window: {row['approximately_second_order_window']}")
    print(f"comparison_result: {row['comparison_result']}")

primary_rows = df[df["primary_evidence"] == True]
primary_quality_pass = (primary_rows["primary_field_quality"] == "PASS").all()

primary_comparisons = comparison_df[comparison_df["primary_evidence"] == True]
primary_resolution_pass = (primary_comparisons["comparison_result"] == "PASS").all()

single_mode_rows = comparison_df[comparison_df["field_name"] == "single_mode_k2_2"]
single_mode_review = len(single_mode_rows) > 0

overall_pass = bool(primary_quality_pass and primary_resolution_pass and single_mode_review)

print("\n=== OVERALL RESULT ===")
print(f"Primary field quality: {pass_fail(primary_quality_pass)}")
print(f"Primary field resolution behavior: {pass_fail(primary_resolution_pass)}")
print(f"Single-mode near-null case retained as review reference: {pass_fail(single_mode_review)}")
print(f"Phase 10D advection operator comparison audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print(f"Wrote: {OUT_COMPARISON_CSV}")
print("Phase 10D advection operator comparison audit complete.")