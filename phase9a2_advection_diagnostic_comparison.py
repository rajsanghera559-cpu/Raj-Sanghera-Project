from pathlib import Path

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver


OUT_CSV = Path("PHASE9A2_ADVECTION_DIAGNOSTIC_COMPARISON.csv")


def l2_norm(a):
    return float(np.sqrt(np.mean(np.asarray(a) ** 2)))


def max_abs(a):
    return float(np.max(np.abs(np.asarray(a))))


def safe_relative_error(numerator, denominator):
    denominator = max(float(denominator), 1e-300)
    return float(numerator) / denominator


def rms(a):
    return float(np.sqrt(np.mean(np.asarray(a) ** 2)))


def rescale_to_rms(field, target_rms):
    field_rms = rms(field)
    if field_rms == 0:
        raise ValueError("Cannot rescale a zero-RMS field.")
    return field * (target_rms / field_rms)


def finite_difference_advection(solver, w):
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)

    wx = (np.roll(w, -1, 1) - np.roll(w, 1, 1)) / (2 * solver.dx)
    wy = (np.roll(w, -1, 0) - np.roll(w, 1, 0)) / (2 * solver.dx)

    return u * wx + v * wy


def spectral_advection(solver, w):
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)

    w_hat = np.fft.fft2(w)
    wx = np.fft.ifft2(1j * solver.kx * w_hat).real
    wy = np.fft.ifft2(1j * solver.ky * w_hat).real

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


def analyze_case(N, field_name, w):
    run_path = Path("experiments") / "method_diagnostics" / f"phase9A2_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)

    fd_adv = finite_difference_advection(solver, w)
    spec_adv = spectral_advection(solver, w)

    diff = fd_adv - spec_adv

    fd_l2 = l2_norm(fd_adv)
    spec_l2 = l2_norm(spec_adv)
    diff_l2 = l2_norm(diff)
    rel_l2 = safe_relative_error(diff_l2, spec_l2)

    fd_max = max_abs(fd_adv)
    spec_max = max_abs(spec_adv)
    diff_max = max_abs(diff)

    finite_all = (
        np.isfinite(w).all()
        and np.isfinite(fd_adv).all()
        and np.isfinite(spec_adv).all()
        and np.isfinite(diff).all()
    )

    fd_flat = fd_adv.ravel()
    spec_flat = spec_adv.ravel()
    denom = np.linalg.norm(fd_flat) * np.linalg.norm(spec_flat)
    cosine_similarity = float(np.dot(fd_flat, spec_flat) / denom) if denom > 0 else np.nan

    return {
        "N": N,
        "field_name": field_name,
        "field_rms": rms(w),
        "field_max_abs": max_abs(w),
        "finite_all": "PASS" if finite_all else "FAIL",
        "fd_adv_l2": fd_l2,
        "spectral_adv_l2": spec_l2,
        "diff_l2": diff_l2,
        "relative_l2_error_vs_spectral": rel_l2,
        "fd_adv_max_abs": fd_max,
        "spectral_adv_max_abs": spec_max,
        "diff_max_abs": diff_max,
        "cosine_similarity": cosine_similarity,
    }


print("\n=== PHASE 9A.2 ADVECTION DIAGNOSTIC COMPARISON ===")
print("Purpose: compare current finite-difference advection against spectral-derivative advection.")
print("This does not modify the solver.")
print("This does not prove turbulence or k^-3 scaling.")

rows = []

for N in [64, 128]:
    run_path = Path("experiments") / "method_diagnostics" / f"phase9A2_N{N}"
    solver = SpectralSolver(nx=N, ny=N, Re=1000, run_path=run_path, dt=0.005, steps=1)
    fields = build_test_fields(solver)

    print(f"\n=== N={N} ===")

    for field_name, w in fields.items():
        result = analyze_case(N, field_name, w)
        rows.append(result)

        print(f"\nField: {field_name}")
        print(f"finite_all: {result['finite_all']}")
        print(f"fd_adv_l2: {result['fd_adv_l2']:.12e}")
        print(f"spectral_adv_l2: {result['spectral_adv_l2']:.12e}")
        print(f"diff_l2: {result['diff_l2']:.12e}")
        print(f"relative_l2_error_vs_spectral: {result['relative_l2_error_vs_spectral']:.12e}")
        print(f"cosine_similarity: {result['cosine_similarity']:.12e}")

df = pd.DataFrame(rows)

print("\n=== RESOLUTION COMPARISON N=64 TO N=128 ===")

comparison_rows = []

for field_name in sorted(df["field_name"].unique()):
    row64 = df[(df["N"] == 64) & (df["field_name"] == field_name)].iloc[0]
    row128 = df[(df["N"] == 128) & (df["field_name"] == field_name)].iloc[0]

    err64 = float(row64["relative_l2_error_vs_spectral"])
    err128 = float(row128["relative_l2_error_vs_spectral"])

    if err64 > 0:
        error_ratio_128_over_64 = err128 / err64
    else:
        error_ratio_128_over_64 = np.nan

    improved = bool(err128 < err64)

    comparison_rows.append(
        {
            "field_name": field_name,
            "N64_relative_l2_error": err64,
            "N128_relative_l2_error": err128,
            "N128_over_N64_error_ratio": error_ratio_128_over_64,
            "improved_at_N128": "PASS" if improved else "FAIL",
        }
    )

    print(f"\nField: {field_name}")
    print(f"N=64 relative error:  {err64:.12e}")
    print(f"N=128 relative error: {err128:.12e}")
    print(f"N128/N64 error ratio: {error_ratio_128_over_64:.12e}")
    print(f"improved_at_N128: {'PASS' if improved else 'FAIL'}")

comparison_df = pd.DataFrame(comparison_rows)

finite_pass = (df["finite_all"] == "PASS").all()

nonlinear_fields = [
    "low_mode_pair",
    "phase6d_like_multimode",
    "higher_smooth_multimode",
]

nonlinear_improvement_pass = (
    comparison_df[comparison_df["field_name"].isin(nonlinear_fields)]["improved_at_N128"] == "PASS"
).all()

overall_result = "PASS" if finite_pass and nonlinear_improvement_pass else "REVIEW"

print("\n=== OVERALL RESULT ===")
print(f"finite checks: {'PASS' if finite_pass else 'FAIL'}")
print(f"nonlinear error improves at N=128: {'PASS' if nonlinear_improvement_pass else 'REVIEW'}")
print(f"Phase 9A.2 diagnostic comparison: {overall_result}")

df.to_csv(OUT_CSV, index=False)

comparison_out = Path("PHASE9A2_ADVECTION_DIAGNOSTIC_RESOLUTION_COMPARISON.csv")
comparison_df.to_csv(comparison_out, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print(f"Wrote: {comparison_out}")
print("Phase 9A.2 advection diagnostic comparison complete.")