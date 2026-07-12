import json
from pathlib import Path

import numpy as np
import pandas as pd


RUN = Path(r"experiments\runs\run_2026-07-12_00-38-33")
METADATA_PATH = RUN / "metadata.json"
DIAG_PATH = RUN / "diagnostics.csv"
SPEC_PATH = RUN / "spectrum.csv"
INITIAL_PATH = RUN / "initial_invariants.csv"

OUT_CSV = Path("PHASE9A3_NONLINEAR_DRIFT_AUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def relative_error(a, b):
    denom = max(abs(float(a)), abs(float(b)), 1e-300)
    return abs(float(a) - float(b)) / denom


def relative_change(final, initial):
    denom = max(abs(float(initial)), 1e-300)
    return (float(final) - float(initial)) / denom


print("\n=== PHASE 9A.3 NONLINEAR NO-FORCING DRIFT AUDIT ===")
print(f"Run folder: {RUN}")
print(f"Metadata: {METADATA_PATH}")
print(f"Initial invariants: {INITIAL_PATH}")
print(f"Diagnostics: {DIAG_PATH}")
print(f"Spectrum: {SPEC_PATH}")

for path in [METADATA_PATH, INITIAL_PATH, DIAG_PATH, SPEC_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

initial = pd.read_csv(INITIAL_PATH)
diag = pd.read_csv(DIAG_PATH)
spec = pd.read_csv(SPEC_PATH)

initial.columns = [c.strip() for c in initial.columns]
diag.columns = [c.strip() for c in diag.columns]
spec.columns = [c.strip() for c in spec.columns]

required_initial = [
    "energy",
    "enstrophy",
    "sum_spectrum",
    "peak_k",
    "peak_fraction",
    "field_rms",
]

required_diag = ["step", "energy", "enstrophy", "E_k4"]
required_spec = ["k", "E(k)", "mode_count"]

for col in required_initial:
    if col not in initial.columns:
        raise ValueError(f"Missing initial invariant column: {col}. Found: {list(initial.columns)}")

for col in required_diag:
    if col not in diag.columns:
        raise ValueError(f"Missing diagnostics column: {col}. Found: {list(diag.columns)}")

for col in required_spec:
    if col not in spec.columns:
        raise ValueError(f"Missing spectrum column: {col}. Found: {list(spec.columns)}")

for col in required_initial:
    initial[col] = pd.to_numeric(initial[col], errors="raise")

for col in required_diag:
    diag[col] = pd.to_numeric(diag[col], errors="raise")

for col in required_spec:
    spec[col] = pd.to_numeric(spec[col], errors="raise")

run_id = metadata.get("run_id")
status = metadata.get("status")
git_commit = metadata.get("git_commit", "")
git_dirty = metadata.get("git_dirty")
config = metadata.get("config", {})

mode = config.get("mode")
re_value = config.get("Re")
nu = float(config.get("nu"))
nx = config.get("nx")
ny = config.get("ny")
dt = float(config.get("dt"))
steps = config.get("steps")
forcing = config.get("forcing")
initial_condition = config.get("initial_condition")
target_initial_rms = float(config.get("target_initial_rms"))
comparison_time = float(config.get("comparison_time"))
expected_steps = config.get("expected_diagnostic_steps", [])

metadata_status_completed = status == "completed"
metadata_dirty_false = git_dirty is False
metadata_commit_expected = str(git_commit).startswith("598b7aa")
metadata_mode_expected = mode == "phase9A3_nonlinear_no_forcing_drift"
metadata_config_expected = (
    re_value == 1_000_000
    and nx == 64
    and ny == 64
    and abs(nu - 1.0e-6) < 1e-18
    and abs(dt - 0.001) < 1e-18
    and steps == 1001
    and forcing == "zero_forcing_override"
    and initial_condition == "phase6d_like_multimode_vorticity"
    and abs(target_initial_rms - 0.01) < 1e-15
    and abs(comparison_time - 1.0) < 1e-15
)

initial_values = initial[required_initial].to_numpy(dtype=float)
diag_values = diag[required_diag].to_numpy(dtype=float)
spec_values = spec[required_spec].to_numpy(dtype=float)

initial_finite = np.isfinite(initial_values).all()
diag_finite = np.isfinite(diag_values).all()
spec_finite = np.isfinite(spec_values).all()

diag_nonnegative_energy = (diag["energy"] >= 0).all()
diag_nonnegative_enstrophy = (diag["enstrophy"] >= 0).all()
diag_nonnegative_E_k4 = (diag["E_k4"] >= 0).all()
spec_nonnegative = (spec["E(k)"] >= 0).all()
mode_counts_positive = (spec["mode_count"] > 0).all()

actual_steps = diag["step"].astype(int).tolist()
expected_steps_match = actual_steps == expected_steps
steps_increasing = diag["step"].is_monotonic_increasing and diag["step"].is_unique

initial_energy = float(initial["energy"].iloc[0])
initial_enstrophy = float(initial["enstrophy"].iloc[0])
initial_sum_spectrum = float(initial["sum_spectrum"].iloc[0])
initial_peak_k = int(initial["peak_k"].iloc[0])
initial_peak_fraction = float(initial["peak_fraction"].iloc[0])
initial_field_rms = float(initial["field_rms"].iloc[0])

logged_energy_0 = float(diag["energy"].iloc[0])
logged_enstrophy_0 = float(diag["enstrophy"].iloc[0])

final_energy = float(diag["energy"].iloc[-1])
final_enstrophy = float(diag["enstrophy"].iloc[-1])
final_E_k4 = float(diag["E_k4"].iloc[-1])

energy_change_initial_to_final = relative_change(final_energy, initial_energy)
enstrophy_change_initial_to_final = relative_change(final_enstrophy, initial_enstrophy)

energy_change_logged_to_final = relative_change(final_energy, logged_energy_0)
enstrophy_change_logged_to_final = relative_change(final_enstrophy, logged_enstrophy_0)

energy_abs_drift_small = abs(energy_change_initial_to_final) < 1e-3
enstrophy_abs_drift_small = abs(enstrophy_change_initial_to_final) < 1e-3

energy_not_growing_materially = final_energy <= initial_energy * (1.0 + 1e-3)
enstrophy_not_growing_materially = final_enstrophy <= initial_enstrophy * (1.0 + 1e-3)

energy_monotonic_nonincreasing_logged = diag["energy"].is_monotonic_decreasing
enstrophy_monotonic_nonincreasing_logged = diag["enstrophy"].is_monotonic_decreasing

sum_spectrum = float(spec["E(k)"].sum())
energy_spectrum_rel_error = relative_error(final_energy, sum_spectrum)
energy_spectrum_consistent = energy_spectrum_rel_error < 1e-9

initial_energy_spectrum_rel_error = relative_error(initial_energy, initial_sum_spectrum)
initial_energy_spectrum_consistent = initial_energy_spectrum_rel_error < 1e-9

peak_index = int(spec["E(k)"].idxmax())
final_peak_k = int(spec.loc[peak_index, "k"])
final_peak_E = float(spec.loc[peak_index, "E(k)"])
final_peak_fraction = final_peak_E / sum_spectrum if sum_spectrum > 0 else np.nan

k3_fraction = float(spec.loc[spec["k"] == 3, "E(k)"].sum()) / sum_spectrum
k4_fraction = float(spec.loc[spec["k"] == 4, "E(k)"].sum()) / sum_spectrum
kge5_fraction = float(spec.loc[spec["k"] >= 5, "E(k)"].sum()) / sum_spectrum

field_rms_expected = abs(initial_field_rms - target_initial_rms) < 1e-12
initial_peak_valid = initial_peak_k > 0
final_peak_valid = final_peak_k > 0

overall_pass = all(
    [
        metadata_status_completed,
        metadata_dirty_false,
        metadata_commit_expected,
        metadata_mode_expected,
        metadata_config_expected,
        initial_finite,
        diag_finite,
        spec_finite,
        diag_nonnegative_energy,
        diag_nonnegative_enstrophy,
        diag_nonnegative_E_k4,
        spec_nonnegative,
        mode_counts_positive,
        expected_steps_match,
        steps_increasing,
        initial_energy_spectrum_consistent,
        energy_spectrum_consistent,
        energy_abs_drift_small,
        enstrophy_abs_drift_small,
        energy_not_growing_materially,
        enstrophy_not_growing_materially,
        energy_monotonic_nonincreasing_logged,
        enstrophy_monotonic_nonincreasing_logged,
        field_rms_expected,
        initial_peak_valid,
        final_peak_valid,
    ]
)

print("\n=== METADATA CHECKS ===")
print(f"Run ID: {run_id}")
print(f"Status completed: {pass_fail(metadata_status_completed)}")
print(f"Git commit starts with 598b7aa: {pass_fail(metadata_commit_expected)}")
print(f"Git dirty false: {pass_fail(metadata_dirty_false)}")
print(f"Mode expected: {pass_fail(metadata_mode_expected)}")
print(f"Config expected: {pass_fail(metadata_config_expected)}")

print("\n=== FILE / FINITE CHECKS ===")
print(f"Initial invariants finite: {pass_fail(initial_finite)}")
print(f"Diagnostics finite: {pass_fail(diag_finite)}")
print(f"Spectrum finite: {pass_fail(spec_finite)}")
print(f"Energy nonnegative: {pass_fail(diag_nonnegative_energy)}")
print(f"Enstrophy nonnegative: {pass_fail(diag_nonnegative_enstrophy)}")
print(f"E_k4 nonnegative: {pass_fail(diag_nonnegative_E_k4)}")
print(f"Spectrum nonnegative: {pass_fail(spec_nonnegative)}")
print(f"Mode counts positive: {pass_fail(mode_counts_positive)}")

print("\n=== DIAGNOSTIC STEP CHECKS ===")
print(f"Actual steps: {actual_steps}")
print(f"Expected steps: {expected_steps}")
print(f"Expected steps match: {pass_fail(expected_steps_match)}")
print(f"Steps increasing: {pass_fail(steps_increasing)}")

print("\n=== INITIAL STATE ===")
print(f"Initial field RMS: {initial_field_rms:.12e}")
print(f"Target field RMS:  {target_initial_rms:.12e}")
print(f"Field RMS expected: {pass_fail(field_rms_expected)}")
print(f"Initial energy: {initial_energy:.12e}")
print(f"Initial enstrophy: {initial_enstrophy:.12e}")
print(f"Initial sum spectrum: {initial_sum_spectrum:.12e}")
print(f"Initial E/spectrum rel error: {initial_energy_spectrum_rel_error:.12e}")
print(f"Initial E/spectrum check: {pass_fail(initial_energy_spectrum_consistent)}")
print(f"Initial peak k: {initial_peak_k}")
print(f"Initial peak fraction: {initial_peak_fraction:.12e}")

print("\n=== FINAL STATE ===")
print(f"Final energy: {final_energy:.12e}")
print(f"Final enstrophy: {final_enstrophy:.12e}")
print(f"Final E_k4: {final_E_k4:.12e}")
print(f"Final sum spectrum: {sum_spectrum:.12e}")
print(f"Final E/spectrum rel error: {energy_spectrum_rel_error:.12e}")
print(f"Final E/spectrum check: {pass_fail(energy_spectrum_consistent)}")
print(f"Final peak k: {final_peak_k}")
print(f"Final peak fraction: {final_peak_fraction:.12e}")
print(f"k=3 fraction: {k3_fraction:.12e}")
print(f"k=4 fraction: {k4_fraction:.12e}")
print(f"k>=5 fraction: {kge5_fraction:.12e}")

print("\n=== DRIFT CHECKS ===")
print(f"Energy change initial to final: {energy_change_initial_to_final:.12e}")
print(f"Enstrophy change initial to final: {enstrophy_change_initial_to_final:.12e}")
print(f"Energy change logged step0 to final: {energy_change_logged_to_final:.12e}")
print(f"Enstrophy change logged step0 to final: {enstrophy_change_logged_to_final:.12e}")
print(f"Energy abs drift < 1e-3: {pass_fail(energy_abs_drift_small)}")
print(f"Enstrophy abs drift < 1e-3: {pass_fail(enstrophy_abs_drift_small)}")
print(f"Energy not growing materially: {pass_fail(energy_not_growing_materially)}")
print(f"Enstrophy not growing materially: {pass_fail(enstrophy_not_growing_materially)}")
print(f"Logged energy monotonic nonincreasing: {pass_fail(energy_monotonic_nonincreasing_logged)}")
print(f"Logged enstrophy monotonic nonincreasing: {pass_fail(enstrophy_monotonic_nonincreasing_logged)}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 9A.3 nonlinear drift audit: {pass_fail(overall_pass)}")

summary = {
    "run_id": run_id,
    "run_folder": str(RUN),
    "status": status,
    "git_commit": git_commit,
    "git_dirty": git_dirty,
    "mode": mode,
    "Re": re_value,
    "nu": nu,
    "nx": nx,
    "ny": ny,
    "dt": dt,
    "steps": steps,
    "forcing": forcing,
    "initial_condition": initial_condition,
    "target_initial_rms": target_initial_rms,
    "comparison_time": comparison_time,
    "actual_diagnostic_steps": str(actual_steps),
    "expected_diagnostic_steps": str(expected_steps),
    "initial_energy": initial_energy,
    "initial_enstrophy": initial_enstrophy,
    "initial_sum_spectrum": initial_sum_spectrum,
    "initial_energy_spectrum_relative_error": initial_energy_spectrum_rel_error,
    "initial_peak_k": initial_peak_k,
    "initial_peak_fraction": initial_peak_fraction,
    "initial_field_rms": initial_field_rms,
    "logged_step0_energy": logged_energy_0,
    "logged_step0_enstrophy": logged_enstrophy_0,
    "final_energy": final_energy,
    "final_enstrophy": final_enstrophy,
    "final_E_k4": final_E_k4,
    "final_sum_spectrum": sum_spectrum,
    "final_energy_spectrum_relative_error": energy_spectrum_rel_error,
    "final_peak_k": final_peak_k,
    "final_peak_fraction": final_peak_fraction,
    "k3_fraction": k3_fraction,
    "k4_fraction": k4_fraction,
    "kge5_fraction": kge5_fraction,
    "energy_change_initial_to_final": energy_change_initial_to_final,
    "enstrophy_change_initial_to_final": enstrophy_change_initial_to_final,
    "energy_change_logged_step0_to_final": energy_change_logged_to_final,
    "enstrophy_change_logged_step0_to_final": enstrophy_change_logged_to_final,
    "energy_abs_drift_lt_1e_minus_3": pass_fail(energy_abs_drift_small),
    "enstrophy_abs_drift_lt_1e_minus_3": pass_fail(enstrophy_abs_drift_small),
    "energy_not_growing_materially": pass_fail(energy_not_growing_materially),
    "enstrophy_not_growing_materially": pass_fail(enstrophy_not_growing_materially),
    "logged_energy_monotonic_nonincreasing": pass_fail(energy_monotonic_nonincreasing_logged),
    "logged_enstrophy_monotonic_nonincreasing": pass_fail(enstrophy_monotonic_nonincreasing_logged),
    "overall_result": pass_fail(overall_pass),
}

pd.DataFrame([summary]).to_csv(OUT_CSV, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 9A.3 nonlinear drift audit complete.")