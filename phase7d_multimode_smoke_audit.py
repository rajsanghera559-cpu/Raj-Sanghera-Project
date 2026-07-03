import json
from pathlib import Path

import numpy as np
import pandas as pd


RUN = Path(r"experiments\runs\run_2026-07-02_21-57-26")
METADATA_PATH = RUN / "metadata.json"
DIAG_PATH = RUN / "diagnostics.csv"
SPEC_PATH = RUN / "spectrum.csv"

OUT_CSV = Path("PHASE7D_MULTIMODE_SMOKE_AUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def relative_error(a, b):
    denom = max(abs(float(a)), abs(float(b)), 1e-300)
    return abs(float(a) - float(b)) / denom


print("\n=== PHASE 7D MULTIMODE SMOKE AUDIT ===")
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
nx = config.get("nx")
ny = config.get("ny")
dt = config.get("dt")
steps = config.get("steps")
forcing = config.get("forcing")
expected_steps = config.get("expected_diagnostic_steps", [])

forcing_type = config.get("forcing_type")
base_single_mode_rms = config.get("base_single_mode_rms")
matched_multimode_rms = config.get("matched_multimode_rms")
forcing_terms = config.get("forcing_terms", [])

metadata_status_completed = status == "completed"
metadata_dirty_false = git_dirty is False
metadata_commit_expected = str(git_commit).startswith("4173531")
metadata_mode_expected = mode == "phase7D_multimode_smoke"
metadata_config_expected = (
    re_value == 1000
    and nx == 64
    and ny == 64
    and abs(float(dt) - 0.005) < 1e-15
    and steps == 1001
    and forcing == "phase6D_rms_matched_deterministic_low_k_multimode"
)
forcing_stats_expected = (
    forcing_type == "rms_matched_deterministic_low_k_multimode"
    and abs(float(base_single_mode_rms) - 0.005) < 1e-15
    and abs(float(matched_multimode_rms) - 0.005) < 1e-15
    and len(forcing_terms) == 4
)

diag_values = diag[required_diag].to_numpy(dtype=float)
diag_finite = np.isfinite(diag_values).all()
diag_nonnegative_energy = (diag["energy"] >= 0).all()
diag_nonnegative_enstrophy = (diag["enstrophy"] >= 0).all()
diag_nonnegative_E_k4 = (diag["E_k4"] >= 0).all()

actual_steps = diag["step"].astype(int).tolist()
expected_steps_match = actual_steps == expected_steps
steps_increasing = diag["step"].is_monotonic_increasing and diag["step"].is_unique

spec_values = spec[required_spec].to_numpy(dtype=float)
spec_finite = np.isfinite(spec_values).all()
spec_nonnegative = (spec["E(k)"] >= 0).all()
mode_counts_positive = (spec["mode_count"] > 0).all()

last_energy = float(diag["energy"].iloc[-1])
last_enstrophy = float(diag["enstrophy"].iloc[-1])
last_E_k4_diag = float(diag["E_k4"].iloc[-1])

sum_spectrum = float(spec["E(k)"].sum())
energy_spectrum_rel_error = relative_error(last_energy, sum_spectrum)
energy_spectrum_consistent = energy_spectrum_rel_error < 1e-9

k4_row = spec[spec["k"] == 4]
if len(k4_row) == 1:
    E_k4_spec = float(k4_row["E(k)"].iloc[0])
    E_k4_rel_error = relative_error(last_E_k4_diag, E_k4_spec)
    E_k4_consistent = E_k4_rel_error < 1e-9
else:
    E_k4_spec = np.nan
    E_k4_rel_error = np.nan
    E_k4_consistent = False

peak_index = int(spec["E(k)"].idxmax())
peak_k = int(spec.loc[peak_index, "k"])
peak_E = float(spec.loc[peak_index, "E(k)"])
peak_fraction = peak_E / sum_spectrum if sum_spectrum > 0 else np.nan

k3_fraction = float(spec.loc[spec["k"] == 3, "E(k)"].sum()) / sum_spectrum
k4_fraction = float(spec.loc[spec["k"] == 4, "E(k)"].sum()) / sum_spectrum
kge5_fraction = float(spec.loc[spec["k"] >= 5, "E(k)"].sum()) / sum_spectrum

peak_k_expected = peak_k == 3
k4_meaningful = k4_fraction > 0.01
single_shell_broken = peak_fraction < 0.999999
low_k_broadening_reproduced = peak_k_expected and k4_meaningful and single_shell_broken

overall_pass = all(
    [
        metadata_status_completed,
        metadata_dirty_false,
        metadata_commit_expected,
        metadata_mode_expected,
        metadata_config_expected,
        forcing_stats_expected,
        diag_finite,
        diag_nonnegative_energy,
        diag_nonnegative_enstrophy,
        diag_nonnegative_E_k4,
        expected_steps_match,
        steps_increasing,
        spec_finite,
        spec_nonnegative,
        mode_counts_positive,
        energy_spectrum_consistent,
        E_k4_consistent,
        low_k_broadening_reproduced,
    ]
)

print("\n=== METADATA CHECKS ===")
print(f"Run ID: {run_id}")
print(f"Status completed: {pass_fail(metadata_status_completed)}")
print(f"Git commit starts with 4173531: {pass_fail(metadata_commit_expected)}")
print(f"Git dirty false: {pass_fail(metadata_dirty_false)}")
print(f"Mode expected: {pass_fail(metadata_mode_expected)}")
print(f"Config expected: {pass_fail(metadata_config_expected)}")
print(f"Forcing stats expected: {pass_fail(forcing_stats_expected)}")

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

print("\n=== SPECTRUM CHECKS ===")
print(f"Spectrum rows: {len(spec)}")
print(f"Spectrum finite: {pass_fail(spec_finite)}")
print(f"Spectrum nonnegative: {pass_fail(spec_nonnegative)}")
print(f"Mode counts positive: {pass_fail(mode_counts_positive)}")

print("\n=== ENERGY CONSISTENCY ===")
print(f"Final diagnostics energy: {last_energy:.12e}")
print(f"Sum spectrum E(k):        {sum_spectrum:.12e}")
print(f"Relative error:           {energy_spectrum_rel_error:.12e}")
print(f"Energy-spectrum check:    {pass_fail(energy_spectrum_consistent)}")

print("\n=== E(k=4) CONSISTENCY ===")
print(f"Diagnostics E_k4:         {last_E_k4_diag:.12e}")
print(f"Spectrum E(k=4):          {E_k4_spec:.12e}")
print(f"Relative error:           {E_k4_rel_error:.12e}")
print(f"E(k=4) check:             {pass_fail(E_k4_consistent)}")

print("\n=== MULTIMODE BROADENING CHECK ===")
print(f"Peak k:                   {peak_k}")
print(f"Peak fraction:            {peak_fraction:.12e}")
print(f"k=3 fraction:             {k3_fraction:.12e}")
print(f"k=4 fraction:             {k4_fraction:.12e}")
print(f"k>=5 fraction:            {kge5_fraction:.12e}")
print(f"Peak k expected:          {pass_fail(peak_k_expected)}")
print(f"k=4 meaningful >1%:       {pass_fail(k4_meaningful)}")
print(f"Single-shell broken:      {pass_fail(single_shell_broken)}")
print(f"Low-k broadening result:  {pass_fail(low_k_broadening_reproduced)}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 7D multimode smoke audit: {pass_fail(overall_pass)}")

summary = {
    "run_id": run_id,
    "run_folder": str(RUN),
    "status": status,
    "git_commit": git_commit,
    "git_dirty": git_dirty,
    "mode": mode,
    "Re": re_value,
    "nx": nx,
    "ny": ny,
    "dt": dt,
    "steps": steps,
    "forcing": forcing,
    "forcing_type": forcing_type,
    "base_single_mode_rms": base_single_mode_rms,
    "matched_multimode_rms": matched_multimode_rms,
    "diagnostic_rows": len(diag),
    "actual_diagnostic_steps": str(actual_steps),
    "expected_diagnostic_steps": str(expected_steps),
    "expected_steps_match": pass_fail(expected_steps_match),
    "diagnostics_finite": pass_fail(diag_finite),
    "energy_nonnegative": pass_fail(diag_nonnegative_energy),
    "enstrophy_nonnegative": pass_fail(diag_nonnegative_enstrophy),
    "E_k4_nonnegative": pass_fail(diag_nonnegative_E_k4),
    "spectrum_rows": len(spec),
    "spectrum_finite": pass_fail(spec_finite),
    "spectrum_nonnegative": pass_fail(spec_nonnegative),
    "mode_counts_positive": pass_fail(mode_counts_positive),
    "final_energy": last_energy,
    "final_enstrophy": last_enstrophy,
    "final_E_k4_diag": last_E_k4_diag,
    "sum_spectrum_Ek": sum_spectrum,
    "energy_spectrum_relative_error": energy_spectrum_rel_error,
    "energy_spectrum_check": pass_fail(energy_spectrum_consistent),
    "spectrum_E_k4": E_k4_spec,
    "E_k4_relative_error": E_k4_rel_error,
    "E_k4_check": pass_fail(E_k4_consistent),
    "peak_k": peak_k,
    "peak_fraction": peak_fraction,
    "k3_fraction": k3_fraction,
    "k4_fraction": k4_fraction,
    "kge5_fraction": kge5_fraction,
    "peak_k_expected": pass_fail(peak_k_expected),
    "k4_meaningful_gt_1pct": pass_fail(k4_meaningful),
    "single_shell_broken": pass_fail(single_shell_broken),
    "low_k_broadening_reproduced": pass_fail(low_k_broadening_reproduced),
    "overall_result": pass_fail(overall_pass),
}

pd.DataFrame([summary]).to_csv(OUT_CSV, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 7D multimode smoke audit complete.")