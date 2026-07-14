from pathlib import Path
import subprocess

import numpy as np
import pandas as pd


METHODS = ("fd_centered", "pseudo_spectral", "arakawa")

PAIRS = (
    "pseudo_spectral vs fd_centered",
    "arakawa vs fd_centered",
    "arakawa vs pseudo_spectral",
)

N64_METHOD_CSV = Path("PHASE11S_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_AUDIT.csv")
N64_PAIRWISE_CSV = Path("PHASE11S_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_PAIRWISE.csv")

N128_METHOD_CSV = Path("PHASE11V_N128_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_AUDIT.csv")
N128_PAIRWISE_CSV = Path("PHASE11V_N128_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_PAIRWISE.csv")

OUT_METHOD_CSV = Path("PHASE12A_CONTROLLED_RESOLUTION_CONSISTENCY_AUDIT.csv")
OUT_PAIRWISE_CSV = Path("PHASE12A_CONTROLLED_RESOLUTION_CONSISTENCY_PAIRWISE_TRENDS.csv")


METHOD_REQUIRED_COLUMNS = {
    "method",
    "N",
    "Re",
    "dt",
    "steps",
    "final_time",
    "final_rms",
    "final_energy",
    "final_enstrophy",
    "rms_ratio",
    "energy_ratio",
    "enstrophy_ratio",
    "dominant_shell",
    "low_k_fraction_k_le_4",
    "high_k_fraction_k_ge_10",
    "spectrum_direct_relative_error",
    "method_result",
}

PAIRWISE_REQUIRED_COLUMNS = {
    "pair",
    "N",
    "Re",
    "dt",
    "steps",
    "final_time",
    "field_relative_l2_difference",
    "energy_relative_difference",
    "enstrophy_relative_difference",
    "rms_relative_difference",
    "spectrum_relative_l2_difference",
    "spectrum_cosine_similarity",
    "dominant_shell_matches",
    "pairwise_result",
}


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def finite_number(value):
    try:
        return bool(np.isfinite(float(value)))
    except Exception:
        return False


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return float("nan")


def safe_relative_difference(a, b):
    a = safe_float(a)
    b = safe_float(b)
    return float(abs(a - b) / max(abs(b), 1e-300))


def safe_reduction_ratio(n64_value, n128_value):
    n64_value = safe_float(n64_value)
    n128_value = safe_float(n128_value)

    if not np.isfinite(n64_value) or not np.isfinite(n128_value):
        return float("nan")

    if abs(n128_value) <= 1e-300:
        return float("inf")

    return float(n64_value / n128_value)


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


def read_csv_checked(path, required_columns):
    if not Path(path).exists():
        raise FileNotFoundError(f"Required file missing: {path}")

    df = pd.read_csv(path)

    missing = sorted(required_columns.difference(set(df.columns)))

    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")

    return df


def get_single_row(df, column, value):
    rows = df[df[column] == value]

    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row where {column}={value!r}; found {len(rows)}")

    return rows.iloc[0]


def status_is_pass(value):
    return str(value).strip().upper() == "PASS"


def check_all_pass(df, column):
    return bool(df[column].astype(str).str.strip().str.upper().eq("PASS").all())


def method_comparison_row(method, n64_row, n128_row):
    final_rms_n64 = safe_float(n64_row["final_rms"])
    final_rms_n128 = safe_float(n128_row["final_rms"])

    final_energy_n64 = safe_float(n64_row["final_energy"])
    final_energy_n128 = safe_float(n128_row["final_energy"])

    final_enstrophy_n64 = safe_float(n64_row["final_enstrophy"])
    final_enstrophy_n128 = safe_float(n128_row["final_enstrophy"])

    low_k_n64 = safe_float(n64_row["low_k_fraction_k_le_4"])
    low_k_n128 = safe_float(n128_row["low_k_fraction_k_le_4"])

    high_k_n64 = safe_float(n64_row["high_k_fraction_k_ge_10"])
    high_k_n128 = safe_float(n128_row["high_k_fraction_k_ge_10"])

    spectrum_error_n64 = safe_float(n64_row["spectrum_direct_relative_error"])
    spectrum_error_n128 = safe_float(n128_row["spectrum_direct_relative_error"])

    dominant_shell_n64 = safe_float(n64_row["dominant_shell"])
    dominant_shell_n128 = safe_float(n128_row["dominant_shell"])

    final_rms_relative_difference = safe_relative_difference(final_rms_n64, final_rms_n128)
    final_energy_relative_difference = safe_relative_difference(final_energy_n64, final_energy_n128)
    final_enstrophy_relative_difference = safe_relative_difference(final_enstrophy_n64, final_enstrophy_n128)
    low_k_absolute_difference = float(abs(low_k_n64 - low_k_n128))
    high_k_absolute_difference = float(abs(high_k_n64 - high_k_n128))
    spectrum_error_absolute_difference = float(abs(spectrum_error_n64 - spectrum_error_n128))

    dominant_shell_same = dominant_shell_n64 == dominant_shell_n128
    both_method_results_pass = status_is_pass(n64_row["method_result"]) and status_is_pass(n128_row["method_result"])

    numeric_values = [
        final_rms_n64,
        final_rms_n128,
        final_energy_n64,
        final_energy_n128,
        final_enstrophy_n64,
        final_enstrophy_n128,
        low_k_n64,
        low_k_n128,
        high_k_n64,
        high_k_n128,
        spectrum_error_n64,
        spectrum_error_n128,
        final_rms_relative_difference,
        final_energy_relative_difference,
        final_enstrophy_relative_difference,
        low_k_absolute_difference,
        high_k_absolute_difference,
        spectrum_error_absolute_difference,
    ]

    numeric_finite = all(finite_number(value) for value in numeric_values)

    consistency_result = all(
        [
            both_method_results_pass,
            numeric_finite,
            dominant_shell_same,
        ]
    )

    return {
        "phase": "12A",
        "test_type": "method_resolution_consistency",
        "method": method,
        "N64_result": str(n64_row["method_result"]),
        "N128_result": str(n128_row["method_result"]),
        "both_method_results_pass": pass_fail(both_method_results_pass),
        "N64_final_rms": final_rms_n64,
        "N128_final_rms": final_rms_n128,
        "final_rms_relative_difference": final_rms_relative_difference,
        "N64_final_energy": final_energy_n64,
        "N128_final_energy": final_energy_n128,
        "final_energy_relative_difference": final_energy_relative_difference,
        "N64_final_enstrophy": final_enstrophy_n64,
        "N128_final_enstrophy": final_enstrophy_n128,
        "final_enstrophy_relative_difference": final_enstrophy_relative_difference,
        "N64_dominant_shell": dominant_shell_n64,
        "N128_dominant_shell": dominant_shell_n128,
        "dominant_shell_same": pass_fail(dominant_shell_same),
        "N64_low_k_fraction_k_le_4": low_k_n64,
        "N128_low_k_fraction_k_le_4": low_k_n128,
        "low_k_absolute_difference": low_k_absolute_difference,
        "N64_high_k_fraction_k_ge_10": high_k_n64,
        "N128_high_k_fraction_k_ge_10": high_k_n128,
        "high_k_absolute_difference": high_k_absolute_difference,
        "N64_spectrum_direct_relative_error": spectrum_error_n64,
        "N128_spectrum_direct_relative_error": spectrum_error_n128,
        "spectrum_error_absolute_difference": spectrum_error_absolute_difference,
        "numeric_finite": pass_fail(numeric_finite),
        "consistency_result": pass_fail(consistency_result),
    }


def pairwise_trend_row(pair, n64_row, n128_row):
    field_n64 = safe_float(n64_row["field_relative_l2_difference"])
    field_n128 = safe_float(n128_row["field_relative_l2_difference"])

    energy_n64 = safe_float(n64_row["energy_relative_difference"])
    energy_n128 = safe_float(n128_row["energy_relative_difference"])

    enstrophy_n64 = safe_float(n64_row["enstrophy_relative_difference"])
    enstrophy_n128 = safe_float(n128_row["enstrophy_relative_difference"])

    rms_n64 = safe_float(n64_row["rms_relative_difference"])
    rms_n128 = safe_float(n128_row["rms_relative_difference"])

    spectrum_n64 = safe_float(n64_row["spectrum_relative_l2_difference"])
    spectrum_n128 = safe_float(n128_row["spectrum_relative_l2_difference"])

    cosine_n64 = safe_float(n64_row["spectrum_cosine_similarity"])
    cosine_n128 = safe_float(n128_row["spectrum_cosine_similarity"])

    field_reduction_ratio = safe_reduction_ratio(field_n64, field_n128)
    energy_reduction_ratio = safe_reduction_ratio(energy_n64, energy_n128)
    enstrophy_reduction_ratio = safe_reduction_ratio(enstrophy_n64, enstrophy_n128)
    rms_reduction_ratio = safe_reduction_ratio(rms_n64, rms_n128)
    spectrum_reduction_ratio = safe_reduction_ratio(spectrum_n64, spectrum_n128)

    field_difference_decreased = field_n128 < field_n64
    spectrum_difference_decreased = spectrum_n128 < spectrum_n64

    both_pairwise_results_pass = status_is_pass(n64_row["pairwise_result"]) and status_is_pass(n128_row["pairwise_result"])
    dominant_shell_match_both = status_is_pass(n64_row["dominant_shell_matches"]) and status_is_pass(n128_row["dominant_shell_matches"])

    numeric_values = [
        field_n64,
        field_n128,
        energy_n64,
        energy_n128,
        enstrophy_n64,
        enstrophy_n128,
        rms_n64,
        rms_n128,
        spectrum_n64,
        spectrum_n128,
        cosine_n64,
        cosine_n128,
        field_reduction_ratio,
        energy_reduction_ratio,
        enstrophy_reduction_ratio,
        rms_reduction_ratio,
        spectrum_reduction_ratio,
    ]

    numeric_finite = all(finite_number(value) for value in numeric_values)

    pairwise_trend_result = all(
        [
            both_pairwise_results_pass,
            dominant_shell_match_both,
            numeric_finite,
        ]
    )

    return {
        "phase": "12A",
        "test_type": "pairwise_resolution_trend",
        "pair": pair,
        "N64_result": str(n64_row["pairwise_result"]),
        "N128_result": str(n128_row["pairwise_result"]),
        "both_pairwise_results_pass": pass_fail(both_pairwise_results_pass),
        "dominant_shell_match_both": pass_fail(dominant_shell_match_both),
        "N64_field_relative_l2_difference": field_n64,
        "N128_field_relative_l2_difference": field_n128,
        "field_reduction_ratio_N64_over_N128": field_reduction_ratio,
        "field_difference_decreased": pass_fail(field_difference_decreased),
        "N64_energy_relative_difference": energy_n64,
        "N128_energy_relative_difference": energy_n128,
        "energy_reduction_ratio_N64_over_N128": energy_reduction_ratio,
        "N64_enstrophy_relative_difference": enstrophy_n64,
        "N128_enstrophy_relative_difference": enstrophy_n128,
        "enstrophy_reduction_ratio_N64_over_N128": enstrophy_reduction_ratio,
        "N64_rms_relative_difference": rms_n64,
        "N128_rms_relative_difference": rms_n128,
        "rms_reduction_ratio_N64_over_N128": rms_reduction_ratio,
        "N64_spectrum_relative_l2_difference": spectrum_n64,
        "N128_spectrum_relative_l2_difference": spectrum_n128,
        "spectrum_reduction_ratio_N64_over_N128": spectrum_reduction_ratio,
        "spectrum_difference_decreased": pass_fail(spectrum_difference_decreased),
        "N64_spectrum_cosine_similarity": cosine_n64,
        "N128_spectrum_cosine_similarity": cosine_n128,
        "numeric_finite": pass_fail(numeric_finite),
        "pairwise_trend_result": pass_fail(pairwise_trend_result),
    }


print("\n=== PHASE 12A CONTROLLED RESOLUTION-CONSISTENCY AUDIT ===")
print("Purpose: compare existing N64 and N128 controlled selectable diagnostic results.")
print("This reads existing Phase 11S and Phase 11V CSV outputs.")
print("This does not run a new simulation.")
print("This does not modify solver source code.")
print("This does not prove convergence, turbulence, k^-3 scaling, or method superiority.")

required_files = [
    N64_METHOD_CSV,
    N64_PAIRWISE_CSV,
    N128_METHOD_CSV,
    N128_PAIRWISE_CSV,
]

files_exist = all(path.exists() for path in required_files)

print("\n=== FILE CHECKS ===")
for path in required_files:
    print(f"{path}: {pass_fail(path.exists())}")

n64_method_df = read_csv_checked(N64_METHOD_CSV, METHOD_REQUIRED_COLUMNS)
n64_pairwise_df = read_csv_checked(N64_PAIRWISE_CSV, PAIRWISE_REQUIRED_COLUMNS)
n128_method_df = read_csv_checked(N128_METHOD_CSV, METHOD_REQUIRED_COLUMNS)
n128_pairwise_df = read_csv_checked(N128_PAIRWISE_CSV, PAIRWISE_REQUIRED_COLUMNS)

spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
advection_operators_no_diff = git_file_has_no_diff("project/solver/advection_operators.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")

n64_methods_pass = check_all_pass(n64_method_df, "method_result")
n128_methods_pass = check_all_pass(n128_method_df, "method_result")
n64_pairwise_pass = check_all_pass(n64_pairwise_df, "pairwise_result")
n128_pairwise_pass = check_all_pass(n128_pairwise_df, "pairwise_result")

n64_methods_present = sorted(n64_method_df["method"].tolist()) == sorted(METHODS)
n128_methods_present = sorted(n128_method_df["method"].tolist()) == sorted(METHODS)
n64_pairs_present = sorted(n64_pairwise_df["pair"].tolist()) == sorted(PAIRS)
n128_pairs_present = sorted(n128_pairwise_df["pair"].tolist()) == sorted(PAIRS)

n64_resolution_ok = set(n64_method_df["N"].astype(int).tolist()) == {64}
n128_resolution_ok = set(n128_method_df["N"].astype(int).tolist()) == {128}

global_checks_pass = all(
    [
        files_exist,
        spectral_solver_no_diff,
        advection_operators_no_diff,
        selectable_solver_no_diff,
        n64_methods_pass,
        n128_methods_pass,
        n64_pairwise_pass,
        n128_pairwise_pass,
        n64_methods_present,
        n128_methods_present,
        n64_pairs_present,
        n128_pairs_present,
        n64_resolution_ok,
        n128_resolution_ok,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"selectable_advection_solver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"N64 method results PASS: {pass_fail(n64_methods_pass)}")
print(f"N128 method results PASS: {pass_fail(n128_methods_pass)}")
print(f"N64 pairwise results PASS: {pass_fail(n64_pairwise_pass)}")
print(f"N128 pairwise results PASS: {pass_fail(n128_pairwise_pass)}")
print(f"N64 methods present: {pass_fail(n64_methods_present)}")
print(f"N128 methods present: {pass_fail(n128_methods_present)}")
print(f"N64 pairs present: {pass_fail(n64_pairs_present)}")
print(f"N128 pairs present: {pass_fail(n128_pairs_present)}")
print(f"N64 resolution check: {pass_fail(n64_resolution_ok)}")
print(f"N128 resolution check: {pass_fail(n128_resolution_ok)}")
print(f"Global checks: {pass_fail(global_checks_pass)}")

method_rows = []

print("\n=== METHOD RESOLUTION-CONSISTENCY RESULTS ===")

for method in METHODS:
    n64_row = get_single_row(n64_method_df, "method", method)
    n128_row = get_single_row(n128_method_df, "method", method)

    row = method_comparison_row(method, n64_row, n128_row)
    method_rows.append(row)

    print(f"\nMethod: {method}")
    print(f"N64 final RMS: {row['N64_final_rms']:.12e}")
    print(f"N128 final RMS: {row['N128_final_rms']:.12e}")
    print(f"final RMS relative difference: {row['final_rms_relative_difference']:.12e}")
    print(f"N64 final energy: {row['N64_final_energy']:.12e}")
    print(f"N128 final energy: {row['N128_final_energy']:.12e}")
    print(f"final energy relative difference: {row['final_energy_relative_difference']:.12e}")
    print(f"N64 final enstrophy: {row['N64_final_enstrophy']:.12e}")
    print(f"N128 final enstrophy: {row['N128_final_enstrophy']:.12e}")
    print(f"final enstrophy relative difference: {row['final_enstrophy_relative_difference']:.12e}")
    print(f"dominant shell same: {row['dominant_shell_same']}")
    print(f"consistency result: {row['consistency_result']}")

pairwise_rows = []

print("\n=== PAIRWISE RESOLUTION-TREND RESULTS ===")

for pair in PAIRS:
    n64_row = get_single_row(n64_pairwise_df, "pair", pair)
    n128_row = get_single_row(n128_pairwise_df, "pair", pair)

    row = pairwise_trend_row(pair, n64_row, n128_row)
    pairwise_rows.append(row)

    print(f"\nPair: {pair}")
    print(f"N64 field relative L2 difference: {row['N64_field_relative_l2_difference']:.12e}")
    print(f"N128 field relative L2 difference: {row['N128_field_relative_l2_difference']:.12e}")
    print(f"field reduction ratio N64/N128: {row['field_reduction_ratio_N64_over_N128']:.12e}")
    print(f"N64 spectrum relative L2 difference: {row['N64_spectrum_relative_l2_difference']:.12e}")
    print(f"N128 spectrum relative L2 difference: {row['N128_spectrum_relative_l2_difference']:.12e}")
    print(f"spectrum reduction ratio N64/N128: {row['spectrum_reduction_ratio_N64_over_N128']:.12e}")
    print(f"dominant shell match both: {row['dominant_shell_match_both']}")
    print(f"pairwise trend result: {row['pairwise_trend_result']}")

method_df = pd.DataFrame(method_rows)
pairwise_df = pd.DataFrame(pairwise_rows)

method_df.to_csv(OUT_METHOD_CSV, index=False)
pairwise_df.to_csv(OUT_PAIRWISE_CSV, index=False)

method_consistency_pass = (method_df["consistency_result"] == "PASS").all()
pairwise_trends_pass = (pairwise_df["pairwise_trend_result"] == "PASS").all()

overall_pass = all(
    [
        global_checks_pass,
        method_consistency_pass,
        pairwise_trends_pass,
    ]
)

print("\n=== FINAL CHECKS ===")
print(f"Method consistency rows pass: {pass_fail(method_consistency_pass)}")
print(f"Pairwise trend rows pass: {pass_fail(pairwise_trends_pass)}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 12A controlled resolution-consistency audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_METHOD_CSV}")
print(f"Wrote: {OUT_PAIRWISE_CSV}")

print("\n=== SCIENTIFIC BOUNDARY ===")
print("This audit reports controlled N64/N128 resolution-consistency metrics only.")
print("This audit does not prove convergence.")
print("This audit does not prove turbulence.")
print("This audit does not prove k^-3 scaling.")
print("This audit does not prove method superiority.")
print("Phase 12A audit complete.")