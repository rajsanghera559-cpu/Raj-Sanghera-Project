import json
from pathlib import Path

import numpy as np
import pandas as pd


RUN = Path(r"experiments\runs\run_2026-07-01_01-53-34")
DIAG_PATH = RUN / "diagnostics.csv"
SPEC_PATH = RUN / "spectrum.csv"

SOLVER_PATH = Path(r"project\solver\spectral_solver.py")
SPECTRUM_TOOL_PATH = Path(r"src\spectral2d\diagnostics\spectrum_tools.py")

OUT_CSV = Path("PHASE7A_SOLVER_SANITY_AUDIT.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def relative_error(a, b):
    denom = max(abs(float(a)), abs(float(b)), 1e-300)
    return abs(float(a) - float(b)) / denom


print("\n=== PHASE 7A SOLVER SANITY AUDIT ===")
print(f"Run folder: {RUN}")
print(f"Diagnostics: {DIAG_PATH}")
print(f"Spectrum: {SPEC_PATH}")
print(f"Solver: {SOLVER_PATH}")
print(f"Spectrum tool: {SPECTRUM_TOOL_PATH}")

for path in [DIAG_PATH, SPEC_PATH, SOLVER_PATH, SPECTRUM_TOOL_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

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

diag_numeric = diag[required_diag].to_numpy(dtype=float)
spec_numeric = spec[required_spec].to_numpy(dtype=float)

finite_diag = np.isfinite(diag_numeric).all()
finite_spec = np.isfinite(spec_numeric).all()

nonnegative_energy = (diag["energy"] >= 0).all()
nonnegative_enstrophy = (diag["enstrophy"] >= 0).all()
nonnegative_spectrum = (spec["E(k)"] >= 0).all()
positive_mode_counts = (spec["mode_count"] > 0).all()

steps_strictly_increasing = diag["step"].is_monotonic_increasing and diag["step"].is_unique

step_diffs = diag["step"].diff().dropna()
cadence_consistent = len(step_diffs) == 0 or (step_diffs == step_diffs.iloc[0]).all()
cadence_value = int(step_diffs.iloc[0]) if len(step_diffs) else None

last_diag = diag.iloc[-1]
last_energy = float(last_diag["energy"])
last_enstrophy = float(last_diag["enstrophy"])
last_E_k4_diag = float(last_diag["E_k4"])

sum_spectrum = float(spec["E(k)"].sum())
energy_spectrum_rel_error = relative_error(last_energy, sum_spectrum)

k4_rows = spec[spec["k"] == 4]
if len(k4_rows) == 1:
    E_k4_spec = float(k4_rows["E(k)"].iloc[0])
    E_k4_rel_error = relative_error(last_E_k4_diag, E_k4_spec)
    k4_consistency = E_k4_rel_error < 1e-9
else:
    E_k4_spec = np.nan
    E_k4_rel_error = np.nan
    k4_consistency = False

spectrum_total_positive = sum_spectrum > 0
energy_positive = last_energy > 0
enstrophy_positive = last_enstrophy > 0

solver_text = SOLVER_PATH.read_text(encoding="utf-8")
spectrum_tool_text = SPECTRUM_TOOL_PATH.read_text(encoding="utf-8")

has_dealias_mask = "self.deal" in solver_text
applies_dealiasing = "W *= self.deal" in solver_text
uses_roll_advection = "np.roll" in solver_text
uses_spectral_diffusion = "laplacian_spectral" in solver_text and "np.fft.fft2" in solver_text
uses_spectral_streamfunction = "def streamfunction" in solver_text and "np.fft.fft2" in solver_text
uses_spectrum_tool = "compute_kinetic_energy_spectrum_from_vorticity" in solver_text
spectrum_excludes_zero_mode = "nonzero = k_sq > 0" in spectrum_tool_text
spectrum_uses_vorticity_energy_formula = "0.5" in spectrum_tool_text and "/ k_sq" in spectrum_tool_text

energy_spectrum_consistency = energy_spectrum_rel_error < 1e-6

overall_pass = all(
    [
        finite_diag,
        finite_spec,
        nonnegative_energy,
        nonnegative_enstrophy,
        nonnegative_spectrum,
        positive_mode_counts,
        steps_strictly_increasing,
        cadence_consistent,
        spectrum_total_positive,
        energy_positive,
        enstrophy_positive,
        energy_spectrum_consistency,
        k4_consistency,
        has_dealias_mask,
        applies_dealiasing,
        uses_spectral_diffusion,
        uses_spectral_streamfunction,
        uses_spectrum_tool,
        spectrum_excludes_zero_mode,
        spectrum_uses_vorticity_energy_formula,
    ]
)

print("\n=== FILE SHAPE CHECKS ===")
print(f"Diagnostics rows: {len(diag)}")
print(f"Spectrum rows: {len(spec)}")
print(f"First diagnostic step: {int(diag['step'].iloc[0])}")
print(f"Last diagnostic step: {int(diag['step'].iloc[-1])}")
print(f"Diagnostic cadence: {cadence_value}")

print("\n=== FINITE / NONNEGATIVE CHECKS ===")
print(f"Diagnostics finite: {pass_fail(finite_diag)}")
print(f"Spectrum finite: {pass_fail(finite_spec)}")
print(f"Energy nonnegative: {pass_fail(nonnegative_energy)}")
print(f"Enstrophy nonnegative: {pass_fail(nonnegative_enstrophy)}")
print(f"Spectrum E(k) nonnegative: {pass_fail(nonnegative_spectrum)}")
print(f"Mode counts positive: {pass_fail(positive_mode_counts)}")

print("\n=== ENERGY / SPECTRUM CONSISTENCY ===")
print(f"Last diagnostics energy: {last_energy:.12e}")
print(f"Sum spectrum E(k):       {sum_spectrum:.12e}")
print(f"Relative error:          {energy_spectrum_rel_error:.12e}")
print(f"Energy-spectrum check:   {pass_fail(energy_spectrum_consistency)}")

print("\n=== E(k=4) CONSISTENCY ===")
print(f"Diagnostics E_k4:        {last_E_k4_diag:.12e}")
print(f"Spectrum E(k=4):         {E_k4_spec:.12e}")
print(f"Relative error:          {E_k4_rel_error:.12e}")
print(f"E(k=4) check:            {pass_fail(k4_consistency)}")

print("\n=== SOLVER FEATURE CHECKS ===")
print(f"Dealias mask present:        {pass_fail(has_dealias_mask)}")
print(f"Dealiasing applied:          {pass_fail(applies_dealiasing)}")
print(f"Finite-difference advection: {pass_fail(uses_roll_advection)}")
print(f"Spectral diffusion present:  {pass_fail(uses_spectral_diffusion)}")
print(f"Spectral streamfunction:     {pass_fail(uses_spectral_streamfunction)}")
print(f"Spectrum tool used:          {pass_fail(uses_spectrum_tool)}")
print(f"Zero mode excluded:          {pass_fail(spectrum_excludes_zero_mode)}")
print(f"Vorticity energy formula:    {pass_fail(spectrum_uses_vorticity_energy_formula)}")

print("\n=== NUMERICAL METHOD CLASSIFICATION ===")
if uses_roll_advection and uses_spectral_diffusion and uses_spectral_streamfunction:
    method_classification = "mixed_spectral_finite_difference"
else:
    method_classification = "unclear"

print(f"Method classification: {method_classification}")
print("Interpretation: spectral streamfunction/diffusion with finite-difference advection and post-step dealiasing.")

print("\n=== OVERALL RESULT ===")
print(f"Phase 7A sanity audit: {pass_fail(overall_pass)}")

summary = {
    "run_folder": str(RUN),
    "diagnostics_rows": len(diag),
    "spectrum_rows": len(spec),
    "first_step": int(diag["step"].iloc[0]),
    "last_step": int(diag["step"].iloc[-1]),
    "diagnostic_cadence": cadence_value,
    "last_energy": last_energy,
    "last_enstrophy": last_enstrophy,
    "sum_spectrum_Ek": sum_spectrum,
    "energy_spectrum_relative_error": energy_spectrum_rel_error,
    "energy_spectrum_check": pass_fail(energy_spectrum_consistency),
    "diagnostics_E_k4": last_E_k4_diag,
    "spectrum_E_k4": E_k4_spec,
    "E_k4_relative_error": E_k4_rel_error,
    "E_k4_check": pass_fail(k4_consistency),
    "finite_diagnostics": pass_fail(finite_diag),
    "finite_spectrum": pass_fail(finite_spec),
    "nonnegative_energy": pass_fail(nonnegative_energy),
    "nonnegative_enstrophy": pass_fail(nonnegative_enstrophy),
    "nonnegative_spectrum": pass_fail(nonnegative_spectrum),
    "positive_mode_counts": pass_fail(positive_mode_counts),
    "steps_strictly_increasing": pass_fail(steps_strictly_increasing),
    "cadence_consistent": pass_fail(cadence_consistent),
    "has_dealias_mask": pass_fail(has_dealias_mask),
    "applies_dealiasing": pass_fail(applies_dealiasing),
    "uses_roll_advection": pass_fail(uses_roll_advection),
    "uses_spectral_diffusion": pass_fail(uses_spectral_diffusion),
    "uses_spectral_streamfunction": pass_fail(uses_spectral_streamfunction),
    "uses_spectrum_tool": pass_fail(uses_spectrum_tool),
    "spectrum_excludes_zero_mode": pass_fail(spectrum_excludes_zero_mode),
    "spectrum_uses_vorticity_energy_formula": pass_fail(spectrum_uses_vorticity_energy_formula),
    "method_classification": method_classification,
    "overall_result": pass_fail(overall_pass),
}

pd.DataFrame([summary]).to_csv(OUT_CSV, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 7A existing-run sanity audit complete.")