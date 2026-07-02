import pandas as pd
import numpy as np
from pathlib import Path

RUN = Path(r"experiments\runs\run_2026-07-01_01-53-34")
SPEC_PATH = RUN / "spectrum.csv"

print("\n=== PHASE 6E SPECTRUM AUDIT ===")
print(f"Run folder: {RUN}")
print(f"Spectrum file: {SPEC_PATH}")

if not SPEC_PATH.exists():
    raise FileNotFoundError(f"Could not find spectrum.csv at: {SPEC_PATH}")

spec = pd.read_csv(SPEC_PATH)
spec.columns = [c.strip() for c in spec.columns]

required = ["k", "E(k)"]
for col in required:
    if col not in spec.columns:
        raise ValueError(f"Missing required column: {col}. Found columns: {list(spec.columns)}")

spec["k"] = pd.to_numeric(spec["k"])
spec["E(k)"] = pd.to_numeric(spec["E(k)"])

total = spec["E(k)"].sum()
spec["fraction"] = spec["E(k)"] / total

print(f"\nTotal sum E(k): {total:.12e}")

print("\n=== FIRST 20 SPECTRAL SHELLS ===")
for _, row in spec.head(20).iterrows():
    k = int(row["k"])
    e = float(row["E(k)"])
    f = float(row["fraction"])
    print(f"k={k:2d}  E(k)={e:.12e}  fraction={f:.6%}")

frac_k3 = spec.loc[spec["k"] == 3, "fraction"].sum()
frac_k4 = spec.loc[spec["k"] == 4, "fraction"].sum()
frac_kge5 = spec.loc[spec["k"] >= 5, "fraction"].sum()

active_1pct = spec[spec["fraction"] > 0.01]
active_01pct = spec[spec["fraction"] > 0.001]

print("\n=== SUMMARY ===")
print(f"k=3 fraction:  {frac_k3:.6%}")
print(f"k=4 fraction:  {frac_k4:.6%}")
print(f"k>=5 fraction: {frac_kge5:.6%}")
print(f"Active shells >1%:   {len(active_1pct)} -> {active_1pct['k'].astype(int).tolist()}")
print(f"Active shells >0.1%: {len(active_01pct)} -> {active_01pct['k'].astype(int).tolist()}")

print("\n=== PROVISIONAL LOG-LOG SLOPE CHECK ===")
print("These are diagnostic fits only. They are not turbulence-scaling claims.")

def fit_range(kmin, kmax):
    d = spec[(spec["k"] >= kmin) & (spec["k"] <= kmax) & (spec["E(k)"] > 0)].copy()

    if len(d) < 3:
        print(f"k={kmin}-{kmax}: not enough points")
        return

    x = np.log(d["k"].astype(float).to_numpy())
    y = np.log(d["E(k)"].astype(float).to_numpy())

    slope, intercept = np.polyfit(x, y, 1)
    yhat = slope * x + intercept

    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    print(f"k={kmin:2d}-{kmax:2d}: slope={slope: .4f}, R^2={r2:.4f}, points={len(d)}")

for kmin, kmax in [(3, 8), (4, 10), (5, 10), (5, 15), (5, 20), (8, 20)]:
    fit_range(kmin, kmax)

out_path = Path("PHASE6E_SPECTRUM_AUDIT_SUMMARY.csv")
spec.to_csv(out_path, index=False)

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {out_path}")
print("\nPhase 6E audit complete.")