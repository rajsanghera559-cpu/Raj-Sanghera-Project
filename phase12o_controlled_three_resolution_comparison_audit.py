from pathlib import Path
import math
import subprocess

import numpy as np
import pandas as pd


METHODS = ("fd_centered", "pseudo_spectral", "arakawa")

PAIRS = (
    "pseudo_spectral vs fd_centered",
    "arakawa vs fd_centered",
    "arakawa vs pseudo_spectral",
)

METHOD_FILES = {
    64: Path("PHASE11S_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_AUDIT.csv"),
    128: Path("PHASE11V_N128_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_AUDIT.csv"),
    256: Path("PHASE12L_N256_FULL_FINAL_TIME_1_0_FEASIBILITY_AUDIT.csv"),
}

PAIRWISE_FILES = {
    64: Path("PHASE11S_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_PAIRWISE.csv"),
    128: Path("PHASE11V_N128_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_PAIRWISE.csv"),
    256: Path("PHASE12L_N256_FULL_FINAL_TIME_1_0_FEASIBILITY_PAIRWISE.csv"),
}

FINAL_STATE_FILES = {
    64: {
        "fd_centered": Path("experiments/selectable_diagnostics/phase11S_fd_centered/selectable_final_state.npy"),
        "pseudo_spectral": Path("experiments/selectable_diagnostics/phase11S_pseudo_spectral/selectable_final_state.npy"),
        "arakawa": Path("experiments/selectable_diagnostics/phase11S_arakawa/selectable_final_state.npy"),
    },
    128: {
        "fd_centered": Path("experiments/selectable_diagnostics/phase11V_N128_fd_centered/selectable_final_state.npy"),
        "pseudo_spectral": Path("experiments/selectable_diagnostics/phase11V_N128_pseudo_spectral/selectable_final_state.npy"),
        "arakawa": Path("experiments/selectable_diagnostics/phase11V_N128_arakawa/selectable_final_state.npy"),
    },
    256: {
        "fd_centered": Path("experiments/selectable_diagnostics/phase12L_N256_fd_centered/selectable_final_state.npy"),
        "pseudo_spectral": Path("experiments/selectable_diagnostics/phase12L_N256_pseudo_spectral/selectable_final_state.npy"),
        "arakawa": Path("experiments/selectable_diagnostics/phase12L_N256_arakawa/selectable_final_state.npy"),
    },
}

OUT_METHOD_CSV = Path("PHASE12O_CONTROLLED_THREE_RESOLUTION_METHOD_SUMMARY.csv")
OUT_PAIRWISE_CSV = Path("PHASE12O_CONTROLLED_THREE_RESOLUTION_PAIRWISE_TRENDS.csv")
OUT_FIELD_CSV = Path("PHASE12O_CONTROLLED_THREE_RESOLUTION_FIELD_RESTRICTION.csv")

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


def available_unavailable(condition):
    return "AVAILABLE" if bool(condition) else "UNAVAILABLE"


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return float("nan")


def finite_number(value):
    try:
        return bool(np.isfinite(float(value)))
    except Exception:
        return False


def status_is_pass(value):
    return str(value).strip().upper() == "PASS"


def rms(field):
    arr = np.asarray(field, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def max_abs(field):
    arr = np.asarray(field, dtype=float)
    return float(np.max(np.abs(arr)))


def rel_diff(a, b):
    a = safe_float(a)
    b = safe_float(b)
    return float(abs(a - b) / max(abs(b), 1e-300))


def reduction_ratio(coarse_value, fine_value):
    coarse_value = safe_float(coarse_value)
    fine_value = safe_float(fine_value)

    if not np.isfinite(coarse_value) or not np.isfinite(fine_value):
        return float("nan")

    if abs(fine_value) <= 1e-300:
        return float("inf")

    return float(coarse_value / fine_value)


def observed_order(coarse_value, fine_value):
    ratio_value = reduction_ratio(coarse_value, fine_value)

    if not np.isfinite(ratio_value):
        return float("nan")

    if ratio_value <= 0:
        return float("nan")

    return float(math.log(ratio_value) / math.log(2.0))


def monotone_decrease(v64, v128, v256):
    v64 = safe_float(v64)
    v128 = safe_float(v128)
    v256 = safe_float(v256)

    if not all(finite_number(v) for v in [v64, v128, v256]):
        return False

    return bool(v64 > v128 > v256)


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
    if not path.exists():
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


def load_all_csvs():
    method_dfs = {}
    pairwise_dfs = {}

    for resolution, path in METHOD_FILES.items():
        method_dfs[resolution] = read_csv_checked(path, METHOD_REQUIRED_COLUMNS)

    for resolution, path in PAIRWISE_FILES.items():
        pairwise_dfs[resolution] = read_csv_checked(path, PAIRWISE_REQUIRED_COLUMNS)

    return method_dfs, pairwise_dfs


def all_source_results_pass(method_dfs, pairwise_dfs):
    checks = []

    for resolution in (64, 128, 256):
        checks.append(method_dfs[resolution]["method_result"].astype(str).str.strip().str.upper().eq("PASS").all())
        checks.append(pairwise_dfs[resolution]["pairwise_result"].astype(str).str.strip().str.upper().eq("PASS").all())

    return bool(all(checks))


def expected_methods_present(method_dfs):
    for resolution in (64, 128, 256):
        methods = tuple(sorted(method_dfs[resolution]["method"].astype(str).tolist()))
        if methods != tuple(sorted(METHODS)):
            return False

    return True


def expected_pairs_present(pairwise_dfs):
    for resolution in (64, 128, 256):
        pairs = tuple(sorted(pairwise_dfs[resolution]["pair"].astype(str).tolist()))
        if pairs != tuple(sorted(PAIRS)):
            return False

    return True


def method_summary_row(method, method_dfs):
    rows = {
        64: get_single_row(method_dfs[64], "method", method),
        128: get_single_row(method_dfs[128], "method", method),
        256: get_single_row(method_dfs[256], "method", method),
    }

    final_rms = {n: safe_float(rows[n]["final_rms"]) for n in rows}
    final_energy = {n: safe_float(rows[n]["final_energy"]) for n in rows}
    final_enstrophy = {n: safe_float(rows[n]["final_enstrophy"]) for n in rows}

    dominant_shell = {n: safe_float(rows[n]["dominant_shell"]) for n in rows}
    low_k = {n: safe_float(rows[n]["low_k_fraction_k_le_4"]) for n in rows}
    high_k = {n: safe_float(rows[n]["high_k_fraction_k_ge_10"]) for n in rows}
    spectrum_error = {n: safe_float(rows[n]["spectrum_direct_relative_error"]) for n in rows}

    source_pass = all(status_is_pass(rows[n]["method_result"]) for n in rows)
    dominant_shell_all_same = dominant_shell[64] == dominant_shell[128] == dominant_shell[256]

    numeric_values = (
        list(final_rms.values())
        + list(final_energy.values())
        + list(final_enstrophy.values())
        + list(dominant_shell.values())
        + list(low_k.values())
        + list(high_k.values())
        + list(spectrum_error.values())
    )

    numeric_finite = all(finite_number(v) for v in numeric_values)

    summary_result = all(
        [
            source_pass,
            dominant_shell_all_same,
            numeric_finite,
        ]
    )

    return {
        "phase": "12O",
        "test_type": "method_three_resolution_summary",
        "method": method,
        "N64_method_result": rows[64]["method_result"],
        "N128_method_result": rows[128]["method_result"],
        "N256_method_result": rows[256]["method_result"],
        "source_method_results_pass": pass_fail(source_pass),
        "N64_final_rms": final_rms[64],
        "N128_final_rms": final_rms[128],
        "N256_final_rms": final_rms[256],
        "N64_N128_final_rms_relative_difference": rel_diff(final_rms[64], final_rms[128]),
        "N128_N256_final_rms_relative_difference": rel_diff(final_rms[128], final_rms[256]),
        "N64_final_energy": final_energy[64],
        "N128_final_energy": final_energy[128],
        "N256_final_energy": final_energy[256],
        "N64_N128_final_energy_relative_difference": rel_diff(final_energy[64], final_energy[128]),
        "N128_N256_final_energy_relative_difference": rel_diff(final_energy[128], final_energy[256]),
        "N64_final_enstrophy": final_enstrophy[64],
        "N128_final_enstrophy": final_enstrophy[128],
        "N256_final_enstrophy": final_enstrophy[256],
        "N64_N128_final_enstrophy_relative_difference": rel_diff(final_enstrophy[64], final_enstrophy[128]),
        "N128_N256_final_enstrophy_relative_difference": rel_diff(final_enstrophy[128], final_enstrophy[256]),
        "N64_dominant_shell": dominant_shell[64],
        "N128_dominant_shell": dominant_shell[128],
        "N256_dominant_shell": dominant_shell[256],
        "dominant_shell_all_same": pass_fail(dominant_shell_all_same),
        "N64_low_k_fraction_k_le_4": low_k[64],
        "N128_low_k_fraction_k_le_4": low_k[128],
        "N256_low_k_fraction_k_le_4": low_k[256],
        "N64_high_k_fraction_k_ge_10": high_k[64],
        "N128_high_k_fraction_k_ge_10": high_k[128],
        "N256_high_k_fraction_k_ge_10": high_k[256],
        "N64_spectrum_direct_relative_error": spectrum_error[64],
        "N128_spectrum_direct_relative_error": spectrum_error[128],
        "N256_spectrum_direct_relative_error": spectrum_error[256],
        "numeric_finite": pass_fail(numeric_finite),
        "method_summary_result": pass_fail(summary_result),
    }


def pairwise_trend_row(pair, pairwise_dfs):
    rows = {
        64: get_single_row(pairwise_dfs[64], "pair", pair),
        128: get_single_row(pairwise_dfs[128], "pair", pair),
        256: get_single_row(pairwise_dfs[256], "pair", pair),
    }

    metric_names = [
        "field_relative_l2_difference",
        "energy_relative_difference",
        "enstrophy_relative_difference",
        "rms_relative_difference",
        "spectrum_relative_l2_difference",
    ]

    values = {
        metric: {
            64: safe_float(rows[64][metric]),
            128: safe_float(rows[128][metric]),
            256: safe_float(rows[256][metric]),
        }
        for metric in metric_names
    }

    cosine = {
        64: safe_float(rows[64]["spectrum_cosine_similarity"]),
        128: safe_float(rows[128]["spectrum_cosine_similarity"]),
        256: safe_float(rows[256]["spectrum_cosine_similarity"]),
    }

    source_pass = all(status_is_pass(rows[n]["pairwise_result"]) for n in rows)
    dominant_shell_match_all = all(status_is_pass(rows[n]["dominant_shell_matches"]) for n in rows)

    numeric_values = []

    for metric in metric_names:
        numeric_values.extend(values[metric].values())

    numeric_values.extend(cosine.values())

    numeric_finite = all(finite_number(v) for v in numeric_values)

    pairwise_result = all(
        [
            source_pass,
            dominant_shell_match_all,
            numeric_finite,
        ]
    )

    out = {
        "phase": "12O",
        "test_type": "pairwise_three_resolution_trend",
        "pair": pair,
        "N64_pairwise_result": rows[64]["pairwise_result"],
        "N128_pairwise_result": rows[128]["pairwise_result"],
        "N256_pairwise_result": rows[256]["pairwise_result"],
        "source_pairwise_results_pass": pass_fail(source_pass),
        "dominant_shell_match_all": pass_fail(dominant_shell_match_all),
        "numeric_finite": pass_fail(numeric_finite),
        "pairwise_trend_result": pass_fail(pairwise_result),
    }

    for metric in metric_names:
        v64 = values[metric][64]
        v128 = values[metric][128]
        v256 = values[metric][256]

        out[f"N64_{metric}"] = v64
        out[f"N128_{metric}"] = v128
        out[f"N256_{metric}"] = v256
        out[f"{metric}_N64_over_N128_reduction_ratio"] = reduction_ratio(v64, v128)
        out[f"{metric}_N128_over_N256_reduction_ratio"] = reduction_ratio(v128, v256)
        out[f"{metric}_observed_order_64_to_128"] = observed_order(v64, v128)
        out[f"{metric}_observed_order_128_to_256"] = observed_order(v128, v256)
        out[f"{metric}_monotone_decrease"] = pass_fail(monotone_decrease(v64, v128, v256))

    out["N64_spectrum_cosine_similarity"] = cosine[64]
    out["N128_spectrum_cosine_similarity"] = cosine[128]
    out["N256_spectrum_cosine_similarity"] = cosine[256]

    return out


def field_restriction_row(method):
    paths = {
        64: FINAL_STATE_FILES[64][method],
        128: FINAL_STATE_FILES[128][method],
        256: FINAL_STATE_FILES[256][method],
    }

    files_exist = all(path.exists() for path in paths.values())

    base = {
        "phase": "12O",
        "test_type": "field_restriction",
        "method": method,
        "N64_path": str(paths[64]),
        "N128_path": str(paths[128]),
        "N256_path": str(paths[256]),
        "field_restriction_available": available_unavailable(files_exist),
    }

    if not files_exist:
        base.update(
            {
                "N64_N128_restricted_max_abs_difference": np.nan,
                "N64_N128_restricted_rms_difference": np.nan,
                "N64_N128_restricted_relative_rms_difference": np.nan,
                "N128_N256_restricted_max_abs_difference": np.nan,
                "N128_N256_restricted_rms_difference": np.nan,
                "N128_N256_restricted_relative_rms_difference": np.nan,
                "restricted_field_observed_order": np.nan,
                "field_restriction_result": "UNAVAILABLE",
            }
        )
        return base

    w64 = np.load(paths[64])
    w128 = np.load(paths[128])
    w256 = np.load(paths[256])

    shapes_ok = w64.shape == (64, 64) and w128.shape == (128, 128) and w256.shape == (256, 256)

    if not shapes_ok:
        base.update(
            {
                "N64_shape": str(w64.shape),
                "N128_shape": str(w128.shape),
                "N256_shape": str(w256.shape),
                "N64_N128_restricted_max_abs_difference": np.nan,
                "N64_N128_restricted_rms_difference": np.nan,
                "N64_N128_restricted_relative_rms_difference": np.nan,
                "N128_N256_restricted_max_abs_difference": np.nan,
                "N128_N256_restricted_rms_difference": np.nan,
                "N128_N256_restricted_relative_rms_difference": np.nan,
                "restricted_field_observed_order": np.nan,
                "field_restriction_result": "FAIL",
            }
        )
        return base

    w128_to_64 = w128[::2, ::2]
    w256_to_128 = w256[::2, ::2]

    diff_64_128 = w64 - w128_to_64
    diff_128_256 = w128 - w256_to_128

    rms_64_128 = rms(diff_64_128)
    rms_128_256 = rms(diff_128_256)

    rel_64_128 = rms_64_128 / max(rms(w128_to_64), 1e-300)
    rel_128_256 = rms_128_256 / max(rms(w256_to_128), 1e-300)

    finite_real_ok = all(
        [
            np.isfinite(w64).all(),
            np.isfinite(w128).all(),
            np.isfinite(w256).all(),
            np.isrealobj(w64),
            np.isrealobj(w128),
            np.isrealobj(w256),
            finite_number(rel_64_128),
            finite_number(rel_128_256),
        ]
    )

    restricted_order = observed_order(rel_64_128, rel_128_256)

    field_result = finite_real_ok and shapes_ok

    base.update(
        {
            "N64_shape": str(w64.shape),
            "N128_shape": str(w128.shape),
            "N256_shape": str(w256.shape),
            "shapes_ok": pass_fail(shapes_ok),
            "finite_real_ok": pass_fail(finite_real_ok),
            "N64_N128_restricted_max_abs_difference": max_abs(diff_64_128),
            "N64_N128_restricted_rms_difference": rms_64_128,
            "N64_N128_restricted_relative_rms_difference": rel_64_128,
            "N128_N256_restricted_max_abs_difference": max_abs(diff_128_256),
            "N128_N256_restricted_rms_difference": rms_128_256,
            "N128_N256_restricted_relative_rms_difference": rel_128_256,
            "restricted_field_reduction_ratio_N64N128_over_N128N256": reduction_ratio(rel_64_128, rel_128_256),
            "restricted_field_observed_order": restricted_order,
            "field_restriction_result": pass_fail(field_result),
        }
    )

    return base


print("\n=== PHASE 12O CONTROLLED THREE-RESOLUTION COMPARISON AUDIT ===")
print("Purpose: compare existing N64, N128, and N256 controlled diagnostic outputs.")
print("This reads existing CSV outputs and optional final-state files.")
print("This does not run a new simulation.")
print("This does not modify solver source code.")
print("This does not prove convergence, turbulence, k^-3 scaling, or method superiority.")

print("\n=== REQUIRED FILE CHECKS ===")

all_files_exist = True

for resolution in (64, 128, 256):
    method_exists = METHOD_FILES[resolution].exists()
    pairwise_exists = PAIRWISE_FILES[resolution].exists()

    all_files_exist = all_files_exist and method_exists and pairwise_exists

    print(f"N{resolution} method CSV exists: {pass_fail(method_exists)}")
    print(f"N{resolution} pairwise CSV exists: {pass_fail(pairwise_exists)}")

method_dfs, pairwise_dfs = load_all_csvs()

spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
advection_operators_no_diff = git_file_has_no_diff("project/solver/advection_operators.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")

source_results_pass = all_source_results_pass(method_dfs, pairwise_dfs)
methods_present = expected_methods_present(method_dfs)
pairs_present = expected_pairs_present(pairwise_dfs)

global_checks_pass = all(
    [
        all_files_exist,
        spectral_solver_no_diff,
        advection_operators_no_diff,
        selectable_solver_no_diff,
        source_results_pass,
        methods_present,
        pairs_present,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"selectable_advection_solver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"All source method/pairwise results PASS: {pass_fail(source_results_pass)}")
print(f"Expected methods present: {pass_fail(methods_present)}")
print(f"Expected pairs present: {pass_fail(pairs_present)}")
print(f"Global checks: {pass_fail(global_checks_pass)}")

print("\n=== METHOD THREE-RESOLUTION SUMMARY ===")

method_rows = []

for method in METHODS:
    row = method_summary_row(method, method_dfs)
    method_rows.append(row)

    print(f"\nMethod: {method}")
    print(f"N64 final RMS: {row['N64_final_rms']:.12e}")
    print(f"N128 final RMS: {row['N128_final_rms']:.12e}")
    print(f"N256 final RMS: {row['N256_final_rms']:.12e}")
    print(f"N64 final energy: {row['N64_final_energy']:.12e}")
    print(f"N128 final energy: {row['N128_final_energy']:.12e}")
    print(f"N256 final energy: {row['N256_final_energy']:.12e}")
    print(f"dominant shell all same: {row['dominant_shell_all_same']}")
    print(f"method summary result: {row['method_summary_result']}")

print("\n=== PAIRWISE THREE-RESOLUTION TRENDS ===")

pairwise_rows = []

for pair in PAIRS:
    row = pairwise_trend_row(pair, pairwise_dfs)
    pairwise_rows.append(row)

    print(f"\nPair: {pair}")
    print(f"N64 field relative L2: {row['N64_field_relative_l2_difference']:.12e}")
    print(f"N128 field relative L2: {row['N128_field_relative_l2_difference']:.12e}")
    print(f"N256 field relative L2: {row['N256_field_relative_l2_difference']:.12e}")
    print(
        "field observed order 64->128: "
        f"{row['field_relative_l2_difference_observed_order_64_to_128']:.12e}"
    )
    print(
        "field observed order 128->256: "
        f"{row['field_relative_l2_difference_observed_order_128_to_256']:.12e}"
    )
    print(f"N64 spectrum relative L2: {row['N64_spectrum_relative_l2_difference']:.12e}")
    print(f"N128 spectrum relative L2: {row['N128_spectrum_relative_l2_difference']:.12e}")
    print(f"N256 spectrum relative L2: {row['N256_spectrum_relative_l2_difference']:.12e}")
    print(
        "spectrum observed order 64->128: "
        f"{row['spectrum_relative_l2_difference_observed_order_64_to_128']:.12e}"
    )
    print(
        "spectrum observed order 128->256: "
        f"{row['spectrum_relative_l2_difference_observed_order_128_to_256']:.12e}"
    )
    print(f"field monotone decrease: {row['field_relative_l2_difference_monotone_decrease']}")
    print(f"spectrum monotone decrease: {row['spectrum_relative_l2_difference_monotone_decrease']}")
    print(f"pairwise trend result: {row['pairwise_trend_result']}")

print("\n=== OPTIONAL FIELD-RESTRICTION COMPARISONS ===")

field_rows = []

for method in METHODS:
    row = field_restriction_row(method)
    field_rows.append(row)

    print(f"\nMethod: {method}")
    print(f"field restriction available: {row['field_restriction_available']}")
    print(f"field restriction result: {row['field_restriction_result']}")

    if row["field_restriction_available"] == "AVAILABLE":
        print(
            "N64 vs restricted N128 relative RMS difference: "
            f"{row['N64_N128_restricted_relative_rms_difference']:.12e}"
        )
        print(
            "N128 vs restricted N256 relative RMS difference: "
            f"{row['N128_N256_restricted_relative_rms_difference']:.12e}"
        )
        print(
            "restricted field observed order: "
            f"{row['restricted_field_observed_order']:.12e}"
        )

method_df = pd.DataFrame(method_rows)
pairwise_df = pd.DataFrame(pairwise_rows)
field_df = pd.DataFrame(field_rows)

method_df.to_csv(OUT_METHOD_CSV, index=False)
pairwise_df.to_csv(OUT_PAIRWISE_CSV, index=False)
field_df.to_csv(OUT_FIELD_CSV, index=False)

method_rows_pass = (method_df["method_summary_result"] == "PASS").all()
pairwise_rows_pass = (pairwise_df["pairwise_trend_result"] == "PASS").all()

field_available_any = (field_df["field_restriction_available"] == "AVAILABLE").any()

if field_available_any:
    field_rows_pass = field_df["field_restriction_result"].isin(["PASS", "UNAVAILABLE"]).all()
else:
    field_rows_pass = True

overall_pass = all(
    [
        global_checks_pass,
        method_rows_pass,
        pairwise_rows_pass,
        field_rows_pass,
    ]
)

print("\n=== FINAL CHECKS ===")
print(f"Method three-resolution summary rows pass: {pass_fail(method_rows_pass)}")
print(f"Pairwise three-resolution trend rows pass: {pass_fail(pairwise_rows_pass)}")
print(f"Field restriction rows acceptable: {pass_fail(field_rows_pass)}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 12O controlled three-resolution comparison audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_METHOD_CSV}")
print(f"Wrote: {OUT_PAIRWISE_CSV}")
print(f"Wrote: {OUT_FIELD_CSV}")

print("\n=== SCIENTIFIC BOUNDARY ===")
print("This audit reports structured three-resolution diagnostic comparison metrics.")
print("This audit does not prove convergence.")
print("This audit does not prove turbulence.")
print("This audit does not prove k^-3 scaling.")
print("This audit does not prove method superiority.")
print("Phase 12O audit complete.")