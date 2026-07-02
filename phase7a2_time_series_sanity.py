from pathlib import Path

import numpy as np
import pandas as pd


RUN = Path(r"experiments\runs\run_2026-07-01_01-53-34")
DIAG_PATH = RUN / "diagnostics.csv"
OUT_CSV = Path("PHASE7A2_TIME_SERIES_SANITY.csv")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


print("\n=== PHASE 7A.2 TIME-SERIES SANITY CHECK ===")
print(f"Run folder: {RUN}")
print(f"Diagnostics file: {DIAG_PATH}")

if not DIAG_PATH.exists():
    raise FileNotFoundError(f"Missing diagnostics file: {DIAG_PATH}")

diag = pd.read_csv(DIAG_PATH)
diag.columns = [c.strip() for c in diag.columns]

required = ["step", "energy", "enstrophy", "E_k4"]
for col in required:
    if col not in diag.columns:
        raise ValueError(f"Missing required column: {col}. Found columns: {list(diag.columns)}")

for col in required:
    diag[col] = pd.to_numeric(diag[col], errors="raise")

values = diag[required].to_numpy(dtype=float)

finite_all = np.isfinite(values).all()
nonnegative_energy = (diag["energy"] >= 0).all()
nonnegative_enstrophy = (diag["enstrophy"] >= 0).all()
nonnegative_E_k4 = (diag["E_k4"] >= 0).all()

steps_increasing = diag["step"].is_monotonic_increasing and diag["step"].is_unique
step_diffs = diag["step"].diff().dropna()
cadence_consistent = len(step_diffs) == 0 or (step_diffs == step_diffs.iloc[0]).all()
cadence_value = int(step_diffs.iloc[0]) if len(step_diffs) else None

energy_initial = float(diag["energy"].iloc[0])
energy_final = float(diag["energy"].iloc[-1])
energy_min = float(diag["energy"].min())
energy_max = float(diag["energy"].max())

enstrophy_initial = float(diag["enstrophy"].iloc[0])
enstrophy_final = float(diag["enstrophy"].iloc[-1])
enstrophy_min = float(diag["enstrophy"].min())
enstrophy_max = float(diag["enstrophy"].max())

Ek4_initial = float(diag["E_k4"].iloc[0])
Ek4_final = float(diag["E_k4"].iloc[-1])
Ek4_min = float(diag["E_k4"].min())
Ek4_max = float(diag["E_k4"].max())

energy_range_ok = energy_max < 1.0
enstrophy_range_ok = enstrophy_max < 1.0
Ek4_range_ok = Ek4_max < 1.0

energy_ratio = energy_final / max(energy_initial, 1e-300)
enstrophy_ratio = enstrophy_final / max(enstrophy_initial, 1e-300)
Ek4_ratio = Ek4_final / max(Ek4_initial, 1e-300)

energy_deltas = diag["energy"].diff().dropna()
enstrophy_deltas = diag["enstrophy"].diff().dropna()
Ek4_deltas = diag["E_k4"].diff().dropna()

energy_has_large_negative_jump = (energy_deltas < -0.5 * diag["energy"].shift(1).dropna()).any()
enstrophy_has_large_negative_jump = (enstrophy_deltas < -0.5 * diag["enstrophy"].shift(1).dropna()).any()

overall_pass = all(
    [
        finite_all,
        nonnegative_energy,
        nonnegative_enstrophy,
        nonnegative_E_k4,
        steps_increasing,
        cadence_consistent,
        energy_range_ok,
        enstrophy_range_ok,
        Ek4_range_ok,
        not energy_has_large_negative_jump,
        not enstrophy_has_large_negative_jump,
    ]
)

print("\n=== BASIC CHECKS ===")
print(f"Rows: {len(diag)}")
print(f"First step: {int(diag['step'].iloc[0])}")
print(f"Last step: {int(diag['step'].iloc[-1])}")
print(f"Cadence: {cadence_value}")
print(f"Finite values: {pass_fail(finite_all)}")
print(f"Steps increasing: {pass_fail(steps_increasing)}")
print(f"Cadence consistent: {pass_fail(cadence_consistent)}")

print("\n=== NONNEGATIVE CHECKS ===")
print(f"Energy nonnegative: {pass_fail(nonnegative_energy)}")
print(f"Enstrophy nonnegative: {pass_fail(nonnegative_enstrophy)}")
print(f"E_k4 nonnegative: {pass_fail(nonnegative_E_k4)}")

print("\n=== ENERGY TIME SERIES ===")
print(f"Initial energy: {energy_initial:.12e}")
print(f"Final energy:   {energy_final:.12e}")
print(f"Min energy:     {energy_min:.12e}")
print(f"Max energy:     {energy_max:.12e}")
print(f"Final / initial energy ratio: {energy_ratio:.6e}")
print(f"Large negative energy jump: {pass_fail(not energy_has_large_negative_jump)}")

print("\n=== ENSTROPHY TIME SERIES ===")
print(f"Initial enstrophy: {enstrophy_initial:.12e}")
print(f"Final enstrophy:   {enstrophy_final:.12e}")
print(f"Min enstrophy:     {enstrophy_min:.12e}")
print(f"Max enstrophy:     {enstrophy_max:.12e}")
print(f"Final / initial enstrophy ratio: {enstrophy_ratio:.6e}")
print(f"Large negative enstrophy jump: {pass_fail(not enstrophy_has_large_negative_jump)}")

print("\n=== E(k=4) TIME SERIES ===")
print(f"Initial E_k4: {Ek4_initial:.12e}")
print(f"Final E_k4:   {Ek4_final:.12e}")
print(f"Min E_k4:     {Ek4_min:.12e}")
print(f"Max E_k4:     {Ek4_max:.12e}")
print(f"Final / initial E_k4 ratio: {Ek4_ratio:.6e}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 7A.2 time-series sanity: {pass_fail(overall_pass)}")

summary = {
    "run_folder": str(RUN),
    "rows": len(diag),
    "first_step": int(diag["step"].iloc[0]),
    "last_step": int(diag["step"].iloc[-1]),
    "cadence": cadence_value,
    "finite_values": pass_fail(finite_all),
    "steps_increasing": pass_fail(steps_increasing),
    "cadence_consistent": pass_fail(cadence_consistent),
    "energy_nonnegative": pass_fail(nonnegative_energy),
    "enstrophy_nonnegative": pass_fail(nonnegative_enstrophy),
    "E_k4_nonnegative": pass_fail(nonnegative_E_k4),
    "initial_energy": energy_initial,
    "final_energy": energy_final,
    "min_energy": energy_min,
    "max_energy": energy_max,
    "energy_ratio_final_over_initial": energy_ratio,
    "initial_enstrophy": enstrophy_initial,
    "final_enstrophy": enstrophy_final,
    "min_enstrophy": enstrophy_min,
    "max_enstrophy": enstrophy_max,
    "enstrophy_ratio_final_over_initial": enstrophy_ratio,
    "initial_E_k4": Ek4_initial,
    "final_E_k4": Ek4_final,
    "min_E_k4": Ek4_min,
    "max_E_k4": Ek4_max,
    "E_k4_ratio_final_over_initial": Ek4_ratio,
    "large_negative_energy_jump_check": pass_fail(not energy_has_large_negative_jump),
    "large_negative_enstrophy_jump_check": pass_fail(not enstrophy_has_large_negative_jump),
    "overall_result": pass_fail(overall_pass),
}

pd.DataFrame([summary]).to_csv(OUT_CSV, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 7A.2 time-series sanity check complete.")