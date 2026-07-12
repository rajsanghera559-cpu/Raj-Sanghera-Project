import json
from pathlib import Path

import numpy as np
import pandas as pd


RUN = Path(r"experiments\runs\run_2026-07-03_23-57-36")
METADATA_PATH = RUN / "metadata.json"
DIAG_PATH = RUN / "diagnostics.csv"
SPEC_PATH = RUN / "spectrum.csv"

OUT_CSV = Path("PHASE8A_NO_FORCING_DECAY_AUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def relative_error(a, b):
    denom = max(abs(float(a)), abs(float(b)), 1e-300)
    return abs(float(a) - float(b)) / denom


print("\n=== PHASE 8A NO-FORCING DECAY AUDIT ===")
print(f"Run folder: {RUN}")
print(f"Metadata: {METADATA_PATH}")
print(f"Diagnostics: {DIAG_PATH}")
print(f"Spectrum: {SPEC_PATH}")

for path in [METADATA_PATH, DIAG_PATH, SPEC_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

diag = pd.read_csv(DIAG_PATH)
spec = pd.read_csv(SPEC_PATH)

diag.columns = [c.strip() for c in diag.columns]
spec.columns = [c.strip() for c in spec.columns]

required_diag = ["step", "energy", "enstrophy", "E_k4"]
required_spec = ["k", "E(k)", "mode_count"]

for col in required_diag:
    if col not in diag.columns:
        raise ValueError(f"Missing diagnostics column: {col}. Found: {list(diag.columns)}")

for col in required_spec:
    if col not in spec.columns:
        raise ValueError(f"Missing spectrum column: {col}. Found: {list(spec.columns)}")

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
mode_kx = int(config.get("mode_kx"))
mode_ky = int(config.get("mode_ky"))
k_squared = float(config.get("k_squared"))
expected_steps = config.get("expected_diagnostic_steps", [])
expected_logged_ratio_metadata = float(config.get("expected_logged_energy_ratio_step1000_over_step0"))

expected_logged_ratio_computed = float(np.exp(-2.0 * nu * k_squared * (1000 * dt)))
expected_ratio_consistency = relative_error(expected_logged_ratio_metadata, expected_logged_ratio_computed) < 1e-14

metadata_status_completed = status == "completed"
metadata_dirty_false = git_dirty is False
metadata_commit_expected = str(git_commit).startswith("5e981f4")
metadata_mode_expected = mode == "phase8A_no_forcing_single_mode_decay"
metadata_config_expected = (
    re_value == 1000
    and nx == 64
    and ny == 64
    and abs(nu - 0.001) < 1e-15
    and abs(dt - 0.005) < 1e-15
    and steps == 1001
    and forcing == "zero_forcing_override"
    and initial_condition == "single_fourier_mode"
    and mode_kx == 2
    and mode_ky == 2
    and abs(k_squared - 8.0) < 1e-15
)

diag_values = diag[required_diag].to_numpy(dtype=float)
diag_finite = np.isfinite(diag_values).all()
diag_nonnegative_energy = (diag["energy"] >= 0).all()
diag_nonnegative_enstrophy = (diag["enstrophy"] >= 0).all()
diag_nonnegative_E_k4 = (diag["E_k4"] >= 0).all()

actual_steps = diag["step"].astype(int).tolist()
expected_steps_match = actual_steps == expected_steps
steps_increasing = diag["step"].is_monotonic_increasing and diag["step"].is_unique

energy_decreases = diag["energy"].is_monotonic_decreasing
enstrophy_decreases = diag["enstrophy"].is_monotonic_decreasing

spec_values = spec[required_spec].to_numpy(dtype=float)
spec_finite = np.isfinite(spec_values).all()
spec_nonnegative = (spec["E(k)"] >= 0).all()
mode_counts_positive = (spec["mode_count"] > 0).all()

energy0 = float(diag["energy"].iloc[0])
energy_final = float(diag["energy"].iloc[-1])
enstrophy0 = float(diag["enstrophy"].iloc[0])
enstrophy_final = float(diag["enstrophy"].iloc[-1])
E_k4_final = float(diag["E_k4"].iloc[-1])

measured_energy_ratio = energy_final / energy0
measured_enstrophy_ratio = enstrophy_final / enstrophy0

energy_ratio_rel_error = relative_error(measured_energy_ratio, expected_logged_ratio_computed)
enstrophy_ratio_rel_error = relative_error(measured_enstrophy_ratio, expected_logged_ratio_computed)

energy_decay_matches_theory = energy_ratio_rel_error < 1e-8
enstrophy_decay_matches_theory = enstrophy_ratio_rel_error < 1e-8

sum_spectrum = float(spec["E(k)"].sum())
energy_spectrum_rel_error = relative_error(energy_final, sum_spectrum)
energy_spectrum_consistent = energy_spectrum_rel_error < 1e-9

peak_index = int(spec["E(k)"].idxmax())
peak_k = int(spec.loc[peak_index, "k"])
peak_E = float(spec.loc[peak_index, "E(k)"])
peak_fraction = peak_E / sum_spectrum if sum_spectrum > 0 else np.nan

k3_fraction = float(spec.loc[spec["k"] == 3, "E(k)"].sum()) / sum_spectrum
k4_fraction = float(spec.loc[spec["k"] == 4, "E(k)"].sum()) / sum_spectrum
kge4_fraction = float(spec.loc[spec["k"] >= 4, "E(k)"].sum()) / sum_spectrum

peak_k_expected = peak_k == 3
single_shell_preserved = k3_fraction > 0.999999
non_target_shells_small = kge4_fraction < 1e-20

enstrophy_energy_ratio_initial = enstrophy0 / energy0
enstrophy_energy_ratio_final = enstrophy_final / energy_final

enstrophy_energy_relation_initial_error = relative_error(enstrophy_energy_ratio_initial, k_squared)
enstrophy_energy_relation_final_error = relative_error(enstrophy_energy_ratio_final, k_squared)

enstrophy_energy_relation_ok = (
    enstrophy_energy_relation_initial_error < 1e-8
    and enstrophy_energy_relation_final_error < 1e-8
)

overall_pass = all(
    [
        metadata_status_completed,
        metadata_dirty_false,
        metadata_commit_expected,
        metadata_mode_expected,
        metadata_config_expected,
        expected_ratio_consistency,
        diag_finite,
        diag_nonnegative_energy,
        diag_nonnegative_enstrophy,
        diag_nonnegative_E_k4,
        expected_steps_match,
        steps_increasing,
        energy_decreases,
        enstrophy_decreases,
        spec_finite,
        spec_nonnegative,
        mode_counts_positive,
        energy_decay_matches_theory,
        enstrophy_decay_matches_theory,
        energy_spectrum_consistent,
        peak_k_expected,
        single_shell_preserved,
        enstrophy_energy_relation_ok,
    ]
)

print("\n=== METADATA CHECKS ===")
print(f"Run ID: {run_id}")
print(f"Status completed: {pass_fail(metadata_status_completed)}")
print(f"Git commit starts with 5e981f4: {pass_fail(metadata_commit_expected)}")
print(f"Git dirty false: {pass_fail(metadata_dirty_false)}")
print(f"Mode expected: {pass_fail(metadata_mode_expected)}")
print(f"Config expected: {pass_fail(metadata_config_expected)}")

print("\n=== THEORETICAL DECAY CHECK ===")
print(f"nu: {nu:.12e}")
print(f"k_squared: {k_squared:.12e}")
print(f"dt: {dt:.12e}")
print(f"Expected ratio from metadata: {expected_logged_ratio_metadata:.12e}")
print(f"Expected ratio recomputed:    {expected_logged_ratio_computed:.12e}")
print(f"Expected ratio consistency:   {pass_fail(expected_ratio_consistency)}")

print("\n=== DIAGNOSTICS CHECKS ===")
print(f"Rows: {len(diag)}")
print(f"Actual steps: {actual_steps}")
print(f"Expected steps: {expected_steps}")
print(f"Expected steps match: {pass_fail(expected_steps_match)}")
print(f"Steps increasing: {pass_fail(steps_increasing)}")
print(f"Diagnostics finite: {pass_fail(diag_finite)}")
print(f"Energy nonnegative: {pass_fail(diag_nonnegative_energy)}")
print(f"Enstrophy nonnegative: {pass_fail(diag_nonnegative_enstrophy)}")
print(f"E_k4 nonnegative: {pass_fail(diag_nonnegative_E_k4)}")

print("\n=== DECAY RESULTS ===")
print(f"Initial energy: {energy0:.12e}")
print(f"Final energy:   {energy_final:.12e}")
print(f"Measured energy ratio:   {measured_energy_ratio:.12e}")
print(f"Energy ratio rel error:  {energy_ratio_rel_error:.12e}")
print(f"Energy decreases:        {pass_fail(energy_decreases)}")
print(f"Energy decay theory:     {pass_fail(energy_decay_matches_theory)}")

print(f"Initial enstrophy: {enstrophy0:.12e}")
print(f"Final enstrophy:   {enstrophy_final:.12e}")
print(f"Measured enstrophy ratio:  {measured_enstrophy_ratio:.12e}")
print(f"Enstrophy ratio rel error: {enstrophy_ratio_rel_error:.12e}")
print(f"Enstrophy decreases:       {pass_fail(enstrophy_decreases)}")
print(f"Enstrophy decay theory:    {pass_fail(enstrophy_decay_matches_theory)}")

print("\n=== ENERGY / SPECTRUM CONSISTENCY ===")
print(f"Final diagnostics energy: {energy_final:.12e}")
print(f"Sum spectrum E(k):        {sum_spectrum:.12e}")
print(f"Relative error:           {energy_spectrum_rel_error:.12e}")
print(f"Energy-spectrum check:    {pass_fail(energy_spectrum_consistent)}")

print("\n=== SINGLE-MODE SPECTRAL SHAPE ===")
print(f"Peak k:                   {peak_k}")
print(f"Peak fraction:            {peak_fraction:.12e}")
print(f"k=3 fraction:             {k3_fraction:.12e}")
print(f"k=4 fraction:             {k4_fraction:.12e}")
print(f"k>=4 fraction:            {kge4_fraction:.12e}")
print(f"Peak k expected:          {pass_fail(peak_k_expected)}")
print(f"Single-shell preserved:   {pass_fail(single_shell_preserved)}")
print(f"Non-target shells small:  {pass_fail(non_target_shells_small)}")

print("\n=== ENSTROPHY / ENERGY RELATION ===")
print(f"Initial Z/E: {enstrophy_energy_ratio_initial:.12e}")
print(f"Final Z/E:   {enstrophy_energy_ratio_final:.12e}")
print(f"Expected k^2: {k_squared:.12e}")
print(f"Initial relation rel error: {enstrophy_energy_relation_initial_error:.12e}")
print(f"Final relation rel error:   {enstrophy_energy_relation_final_error:.12e}")
print(f"Z/E relation check:         {pass_fail(enstrophy_energy_relation_ok)}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 8A no-forcing decay audit: {pass_fail(overall_pass)}")

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
    "mode_kx": mode_kx,
    "mode_ky": mode_ky,
    "k_squared": k_squared,
    "diagnostic_rows": len(diag),
    "actual_diagnostic_steps": str(actual_steps),
    "expected_diagnostic_steps": str(expected_steps),
    "expected_steps_match": pass_fail(expected_steps_match),
    "initial_energy": energy0,
    "final_energy": energy_final,
    "measured_energy_ratio": measured_energy_ratio,
    "expected_energy_ratio": expected_logged_ratio_computed,
    "energy_ratio_relative_error": energy_ratio_rel_error,
    "energy_decreases": pass_fail(energy_decreases),
    "energy_decay_matches_theory": pass_fail(energy_decay_matches_theory),
    "initial_enstrophy": enstrophy0,
    "final_enstrophy": enstrophy_final,
    "measured_enstrophy_ratio": measured_enstrophy_ratio,
    "expected_enstrophy_ratio": expected_logged_ratio_computed,
    "enstrophy_ratio_relative_error": enstrophy_ratio_rel_error,
    "enstrophy_decreases": pass_fail(enstrophy_decreases),
    "enstrophy_decay_matches_theory": pass_fail(enstrophy_decay_matches_theory),
    "sum_spectrum_Ek": sum_spectrum,
    "energy_spectrum_relative_error": energy_spectrum_rel_error,
    "energy_spectrum_check": pass_fail(energy_spectrum_consistent),
    "peak_k": peak_k,
    "peak_fraction": peak_fraction,
    "k3_fraction": k3_fraction,
    "k4_fraction": k4_fraction,
    "kge4_fraction": kge4_fraction,
    "peak_k_expected": pass_fail(peak_k_expected),
    "single_shell_preserved": pass_fail(single_shell_preserved),
    "initial_Z_over_E": enstrophy_energy_ratio_initial,
    "final_Z_over_E": enstrophy_energy_ratio_final,
    "Z_over_E_expected": k_squared,
    "Z_over_E_relation_check": pass_fail(enstrophy_energy_relation_ok),
    "overall_result": pass_fail(overall_pass),
}

pd.DataFrame([summary]).to_csv(OUT_CSV, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 8A no-forcing decay audit complete.")