import json
from pathlib import Path

import numpy as np
import pandas as pd


RUN = Path(r"experiments\runs\run_2026-07-12_00-45-24")
REF_RUN = Path(r"experiments\runs\run_2026-07-12_00-38-33")

METADATA_PATH = RUN / "metadata.json"
INITIAL_PATH = RUN / "initial_invariants.csv"
DIAG_PATH = RUN / "diagnostics.csv"
SPEC_PATH = RUN / "spectrum.csv"

REF_9A3_CSV = Path("PHASE9A3_NONLINEAR_DRIFT_AUDIT.csv")
STRICT_9A4_CSV = Path("PHASE9A4_HALF_DT_NONLINEAR_DRIFT_AUDIT.csv")

OUT_CSV = Path("PHASE9A4R_TOLERANCE_ROBUST_NONLINEAR_DRIFT_REAUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def relative_error(a, b):
    denom = max(abs(float(a)), abs(float(b)), 1e-300)
    return abs(float(a) - float(b)) / denom


def relative_change(final, initial):
    denom = max(abs(float(initial)), 1e-300)
    return (float(final) - float(initial)) / denom


print("\n=== PHASE 9A.4R TOLERANCE-ROBUST NONLINEAR DRIFT RE-AUDIT ===")
print(f"Phase 9A.4 run folder: {RUN}")
print(f"Phase 9A.3 reference run folder: {REF_RUN}")
print(f"Strict Phase 9A.4 audit CSV: {STRICT_9A4_CSV}")
print(f"Phase 9A.3 reference CSV: {REF_9A3_CSV}")

for path in [METADATA_PATH, INITIAL_PATH, DIAG_PATH, SPEC_PATH, REF_9A3_CSV, STRICT_9A4_CSV]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

initial = pd.read_csv(INITIAL_PATH)
diag = pd.read_csv(DIAG_PATH)
spec = pd.read_csv(SPEC_PATH)
ref9a3 = pd.read_csv(REF_9A3_CSV)
strict9a4 = pd.read_csv(STRICT_9A4_CSV)

initial.columns = [c.strip() for c in initial.columns]
diag.columns = [c.strip() for c in diag.columns]
spec.columns = [c.strip() for c in spec.columns]
ref9a3.columns = [c.strip() for c in ref9a3.columns]
strict9a4.columns = [c.strip() for c in strict9a4.columns]

for col in ["energy", "enstrophy", "sum_spectrum", "peak_k", "peak_fraction", "field_rms"]:
    initial[col] = pd.to_numeric(initial[col], errors="raise")

for col in ["step", "energy", "enstrophy", "E_k4"]:
    diag[col] = pd.to_numeric(diag[col], errors="raise")

for col in ["k", "E(k)", "mode_count"]:
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
comparison_time = float(config.get("comparison_time"))
expected_steps = config.get("expected_diagnostic_steps", [])

metadata_ok = (
    status == "completed"
    and git_dirty is False
    and str(git_commit).startswith("1c1cd19")
    and mode == "phase9A4_nonlinear_no_forcing_drift_dt_half"
    and re_value == 1_000_000
    and nx == 64
    and ny == 64
    and abs(nu - 1.0e-6) < 1e-18
    and abs(dt - 0.0005) < 1e-18
    and steps == 2001
    and forcing == "zero_forcing_override"
    and abs(comparison_time - 1.0) < 1e-15
)

actual_steps = diag["step"].astype(int).tolist()
steps_ok = actual_steps == expected_steps and diag["step"].is_monotonic_increasing and diag["step"].is_unique

finite_ok = (
    np.isfinite(initial[["energy", "enstrophy", "sum_spectrum", "peak_k", "peak_fraction", "field_rms"]].to_numpy(dtype=float)).all()
    and np.isfinite(diag[["step", "energy", "enstrophy", "E_k4"]].to_numpy(dtype=float)).all()
    and np.isfinite(spec[["k", "E(k)", "mode_count"]].to_numpy(dtype=float)).all()
)

nonnegative_ok = (
    (diag["energy"] >= 0).all()
    and (diag["enstrophy"] >= 0).all()
    and (diag["E_k4"] >= 0).all()
    and (spec["E(k)"] >= 0).all()
    and (spec["mode_count"] > 0).all()
)

initial_energy = float(initial["energy"].iloc[0])
initial_enstrophy = float(initial["enstrophy"].iloc[0])
initial_sum_spectrum = float(initial["sum_spectrum"].iloc[0])
initial_field_rms = float(initial["field_rms"].iloc[0])

final_energy = float(diag["energy"].iloc[-1])
final_enstrophy = float(diag["enstrophy"].iloc[-1])
final_E_k4 = float(diag["E_k4"].iloc[-1])

sum_spectrum = float(spec["E(k)"].sum())
final_energy_spectrum_error = relative_error(final_energy, sum_spectrum)
initial_energy_spectrum_error = relative_error(initial_energy, initial_sum_spectrum)

energy_spectrum_ok = (
    initial_energy_spectrum_error < 1e-9
    and final_energy_spectrum_error < 1e-9
)

energy_change = relative_change(final_energy, initial_energy)
enstrophy_change = relative_change(final_enstrophy, initial_enstrophy)

drift_small_ok = (
    abs(energy_change) < 1e-3
    and abs(enstrophy_change) < 1e-3
    and final_energy <= initial_energy * (1.0 + 1e-3)
    and final_enstrophy <= initial_enstrophy * (1.0 + 1e-3)
    and diag["energy"].is_monotonic_decreasing
    and diag["enstrophy"].is_monotonic_decreasing
)

peak_index = int(spec["E(k)"].idxmax())
final_peak_k = int(spec.loc[peak_index, "k"])
final_peak_fraction = float(spec.loc[peak_index, "E(k)"] / sum_spectrum)

k3_fraction = float(spec.loc[spec["k"] == 3, "E(k)"].sum()) / sum_spectrum
k4_fraction = float(spec.loc[spec["k"] == 4, "E(k)"].sum()) / sum_spectrum
kge5_fraction = float(spec.loc[spec["k"] >= 5, "E(k)"].sum()) / sum_spectrum

spectrum_shape_ok = (
    final_peak_k == 3
    and 0.85 < k3_fraction < 0.90
    and 0.10 < k4_fraction < 0.15
    and kge5_fraction < 1e-5
)

ref_final_energy = float(ref9a3["final_energy"].iloc[0])
ref_final_enstrophy = float(ref9a3["final_enstrophy"].iloc[0])
ref_final_E_k4 = float(ref9a3["final_E_k4"].iloc[0])
ref_energy_change = float(ref9a3["energy_change_initial_to_final"].iloc[0])
ref_enstrophy_change = float(ref9a3["enstrophy_change_initial_to_final"].iloc[0])
ref_k3_fraction = float(ref9a3["k3_fraction"].iloc[0])
ref_k4_fraction = float(ref9a3["k4_fraction"].iloc[0])
ref_kge5_fraction = float(ref9a3["kge5_fraction"].iloc[0])

energy_rel_diff_vs_9a3 = relative_error(final_energy, ref_final_energy)
enstrophy_rel_diff_vs_9a3 = relative_error(final_enstrophy, ref_final_enstrophy)
E_k4_rel_diff_vs_9a3 = relative_error(final_E_k4, ref_final_E_k4)

energy_drift_abs_diff = abs(energy_change - ref_energy_change)
enstrophy_drift_abs_diff = abs(enstrophy_change - ref_enstrophy_change)

k3_fraction_abs_diff = abs(k3_fraction - ref_k3_fraction)
k4_fraction_abs_diff = abs(k4_fraction - ref_k4_fraction)
kge5_fraction_abs_diff = abs(kge5_fraction - ref_kge5_fraction)

matches_9a3_robust_ok = (
    energy_rel_diff_vs_9a3 < 1e-6
    and enstrophy_rel_diff_vs_9a3 < 1e-6
    and E_k4_rel_diff_vs_9a3 < 1e-5
    and energy_drift_abs_diff < 1e-7
    and enstrophy_drift_abs_diff < 1e-7
    and k3_fraction_abs_diff < 1e-6
    and k4_fraction_abs_diff < 1e-6
    and kge5_fraction_abs_diff < 1e-6
)

strict_original_result = str(strict9a4["overall_result"].iloc[0])
strict_failure_preserved = strict_original_result == "FAIL"

overall_pass = all(
    [
        metadata_ok,
        steps_ok,
        finite_ok,
        nonnegative_ok,
        energy_spectrum_ok,
        drift_small_ok,
        spectrum_shape_ok,
        matches_9a3_robust_ok,
        strict_failure_preserved,
    ]
)

print("\n=== ORIGINAL STRICT AUDIT ===")
print(f"Strict Phase 9A.4 original result: {strict_original_result}")
print(f"Strict failure preserved: {pass_fail(strict_failure_preserved)}")

print("\n=== METADATA / STRUCTURE ===")
print(f"Run ID: {run_id}")
print(f"Metadata OK: {pass_fail(metadata_ok)}")
print(f"Actual steps: {actual_steps}")
print(f"Expected steps: {expected_steps}")
print(f"Steps OK: {pass_fail(steps_ok)}")
print(f"Finite OK: {pass_fail(finite_ok)}")
print(f"Nonnegative OK: {pass_fail(nonnegative_ok)}")

print("\n=== ENERGY / SPECTRUM ===")
print(f"Initial energy: {initial_energy:.12e}")
print(f"Final energy: {final_energy:.12e}")
print(f"Initial E/spectrum relative error: {initial_energy_spectrum_error:.12e}")
print(f"Final E/spectrum relative error: {final_energy_spectrum_error:.12e}")
print(f"Energy/spectrum OK: {pass_fail(energy_spectrum_ok)}")

print("\n=== DRIFT ===")
print(f"Energy change: {energy_change:.12e}")
print(f"Enstrophy change: {enstrophy_change:.12e}")
print(f"Drift small OK: {pass_fail(drift_small_ok)}")

print("\n=== SPECTRAL SHAPE ===")
print(f"Peak k: {final_peak_k}")
print(f"Peak fraction: {final_peak_fraction:.12e}")
print(f"k=3 fraction: {k3_fraction:.12e}")
print(f"k=4 fraction: {k4_fraction:.12e}")
print(f"k>=5 fraction: {kge5_fraction:.12e}")
print(f"Spectrum shape OK: {pass_fail(spectrum_shape_ok)}")

print("\n=== ROBUST COMPARISON TO PHASE 9A.3 ===")
print(f"Final energy relative diff vs 9A.3: {energy_rel_diff_vs_9a3:.12e}")
print(f"Final enstrophy relative diff vs 9A.3: {enstrophy_rel_diff_vs_9a3:.12e}")
print(f"Final E_k4 relative diff vs 9A.3: {E_k4_rel_diff_vs_9a3:.12e}")
print(f"Energy drift absolute diff: {energy_drift_abs_diff:.12e}")
print(f"Enstrophy drift absolute diff: {enstrophy_drift_abs_diff:.12e}")
print(f"k=3 fraction absolute diff: {k3_fraction_abs_diff:.12e}")
print(f"k=4 fraction absolute diff: {k4_fraction_abs_diff:.12e}")
print(f"k>=5 fraction absolute diff: {kge5_fraction_abs_diff:.12e}")
print(f"Robust 9A.3 comparison OK: {pass_fail(matches_9a3_robust_ok)}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 9A.4R tolerance-robust re-audit: {pass_fail(overall_pass)}")

summary = {
    "run_id": run_id,
    "run_folder": str(RUN),
    "reference_run_folder": str(REF_RUN),
    "strict_phase9A4_original_result": strict_original_result,
    "strict_failure_preserved": pass_fail(strict_failure_preserved),
    "metadata_ok": pass_fail(metadata_ok),
    "steps_ok": pass_fail(steps_ok),
    "finite_ok": pass_fail(finite_ok),
    "nonnegative_ok": pass_fail(nonnegative_ok),
    "initial_energy": initial_energy,
    "final_energy": final_energy,
    "initial_enstrophy": initial_enstrophy,
    "final_enstrophy": final_enstrophy,
    "final_E_k4": final_E_k4,
    "initial_energy_spectrum_relative_error": initial_energy_spectrum_error,
    "final_energy_spectrum_relative_error": final_energy_spectrum_error,
    "energy_spectrum_ok": pass_fail(energy_spectrum_ok),
    "energy_change": energy_change,
    "enstrophy_change": enstrophy_change,
    "drift_small_ok": pass_fail(drift_small_ok),
    "peak_k": final_peak_k,
    "peak_fraction": final_peak_fraction,
    "k3_fraction": k3_fraction,
    "k4_fraction": k4_fraction,
    "kge5_fraction": kge5_fraction,
    "spectrum_shape_ok": pass_fail(spectrum_shape_ok),
    "final_energy_relative_diff_vs_9A3": energy_rel_diff_vs_9a3,
    "final_enstrophy_relative_diff_vs_9A3": enstrophy_rel_diff_vs_9a3,
    "final_E_k4_relative_diff_vs_9A3": E_k4_rel_diff_vs_9a3,
    "energy_drift_abs_diff_vs_9A3": energy_drift_abs_diff,
    "enstrophy_drift_abs_diff_vs_9A3": enstrophy_drift_abs_diff,
    "k3_fraction_abs_diff_vs_9A3": k3_fraction_abs_diff,
    "k4_fraction_abs_diff_vs_9A3": k4_fraction_abs_diff,
    "kge5_fraction_abs_diff_vs_9A3": kge5_fraction_abs_diff,
    "robust_9A3_comparison_ok": pass_fail(matches_9a3_robust_ok),
    "overall_result": pass_fail(overall_pass),
}

pd.DataFrame([summary]).to_csv(OUT_CSV, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 9A.4R tolerance-robust nonlinear drift re-audit complete.")