import csv
import json
import math
from pathlib import Path


def to_float(value):
    try:
        return float(value)
    except Exception:
        return math.nan


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def read_last_csv_row(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows[-1] if rows else None


def read_spectrum(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if "E(k)" in reader.fieldnames:
            e_col = "E(k)"
        elif "Ek" in reader.fieldnames:
            e_col = "Ek"
        else:
            raise ValueError(f"No E(k) column in {path}")

        rows = []
        for row in reader:
            rows.append(
                {
                    "k": to_float(row.get("k")),
                    "Ek": to_float(row.get(e_col)),
                    "mode_count": to_float(row.get("mode_count")),
                }
            )

    return rows


def load_runs(mode, base="experiments/runs"):
    base = Path(base)
    runs = []

    for run_path in base.iterdir():
        if not run_path.is_dir() or not run_path.name.startswith("run_"):
            continue

        metadata_path = run_path / "metadata.json"
        diagnostics_path = run_path / "diagnostics.csv"
        spectrum_path = run_path / "spectrum.csv"

        if not metadata_path.exists() or not diagnostics_path.exists() or not spectrum_path.exists():
            continue

        metadata = read_json(metadata_path)
        config = metadata.get("config", {})

        if not isinstance(config, dict):
            continue

        if config.get("mode") != mode:
            continue

        diag = read_last_csv_row(diagnostics_path)
        spectrum = read_spectrum(spectrum_path)

        energy = to_float(diag.get("energy"))
        enstrophy = to_float(diag.get("enstrophy"))
        sum_ek = sum(row["Ek"] for row in spectrum if math.isfinite(row["Ek"]))

        peak = max(spectrum, key=lambda row: row["Ek"] if math.isfinite(row["Ek"]) else -1.0)

        peak_k = peak["k"]
        peak_ek = peak["Ek"]
        peak_fraction = peak_ek / sum_ek if sum_ek > 0 else math.nan

        active_shells_1pct = sum(
            1
            for row in spectrum
            if math.isfinite(row["Ek"]) and sum_ek > 0 and row["Ek"] >= 0.01 * sum_ek
        )

        active_shells_0p1pct = sum(
            1
            for row in spectrum
            if math.isfinite(row["Ek"]) and sum_ek > 0 and row["Ek"] >= 0.001 * sum_ek
        )

        high_k_fraction = (
            sum(
                row["Ek"]
                for row in spectrum
                if math.isfinite(row["Ek"]) and math.isfinite(row["k"]) and row["k"] >= 5
            )
            / sum_ek
            if sum_ek > 0
            else math.nan
        )

        ek4 = next((row["Ek"] for row in spectrum if int(row["k"]) == 4), math.nan)
        ek5plus = sum(
            row["Ek"]
            for row in spectrum
            if math.isfinite(row["Ek"]) and math.isfinite(row["k"]) and row["k"] >= 5
        )

        runs.append(
            {
                "run_id": run_path.name,
                "mode": mode,
                "steps": config.get("steps"),
                "Re": config.get("Re"),
                "amplitude": config.get("perturbation_amplitude", 0.0),
                "status": metadata.get("status"),
                "commit": str(metadata.get("git_commit", ""))[:7],
                "dirty": metadata.get("git_dirty"),
                "energy": energy,
                "enstrophy": enstrophy,
                "sum_Ek": sum_ek,
                "peak_k": peak_k,
                "peak_fraction": peak_fraction,
                "active_shells_1pct": active_shells_1pct,
                "active_shells_0p1pct": active_shells_0p1pct,
                "high_k_fraction": high_k_fraction,
                "E_k4": ek4,
                "E_k4_fraction": ek4 / sum_ek if sum_ek > 0 else math.nan,
                "E_k5plus": ek5plus,
                "E_k5plus_fraction": ek5plus / sum_ek if sum_ek > 0 else math.nan,
                "mtime": run_path.stat().st_mtime,
            }
        )

    runs.sort(key=lambda r: (to_float(r["amplitude"]), int(r["steps"] or 0), r["mtime"]))
    return runs


def fmt(x):
    if isinstance(x, float):
        if math.isfinite(x):
            return f"{x:.6e}"
        return "nan"
    return str(x)


def print_table(rows):
    headers = [
        "run_id",
        "amp",
        "steps",
        "Re",
        "energy",
        "peak_k",
        "peak_frac",
        "active>1%",
        "active>0.1%",
        "E_k4_frac",
        "k>=5_frac",
        "status",
        "commit",
        "dirty",
    ]

    table = []
    for r in rows:
        table.append(
            [
                r["run_id"],
                fmt(float(r["amplitude"])),
                r["steps"],
                r["Re"],
                fmt(r["energy"]),
                fmt(r["peak_k"]),
                fmt(r["peak_fraction"]),
                r["active_shells_1pct"],
                r["active_shells_0p1pct"],
                fmt(r["E_k4_fraction"]),
                fmt(r["E_k5plus_fraction"]),
                r["status"],
                r["commit"],
                r["dirty"],
            ]
        )

    widths = [len(h) for h in headers]
    for row in table:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * w for w in widths))

    for row in table:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))


def main():
    phase6c = load_runs("phase6C_perturbed_ic")
    phase6b = load_runs("phase6B_spreading_test")

    # Keep only the final 10000-step Phase 6B baseline if present.
    baseline = [r for r in phase6b if int(r["steps"]) == 10000]
    baseline = sorted(baseline, key=lambda r: r["mtime"], reverse=True)[:1]

    rows = baseline + phase6c

    print()
    print(f"Loaded Phase 6C perturbed-IC runs: {len(phase6c)}")
    print(f"Loaded Phase 6B 10000-step baseline rows: {len(baseline)}")
    print()

    print_table(rows)

    print()
    print("Interpretation")
    print("--------------")

    if not phase6c:
        print("No Phase 6C runs found.")
        return

    for r in phase6c:
        print(
            f"amp={fmt(float(r['amplitude']))}: "
            f"peak_frac={fmt(r['peak_fraction'])}, "
            f"active>1%={r['active_shells_1pct']}, "
            f"active>0.1%={r['active_shells_0p1pct']}, "
            f"E_k4_frac={fmt(r['E_k4_fraction'])}, "
            f"k>=5_frac={fmt(r['E_k5plus_fraction'])}"
        )

    final_runs = phase6c

    any_broad = any(
        r["peak_fraction"] < 0.95 or r["active_shells_1pct"] > 2
        for r in final_runs
    )

    print()

    if any_broad:
        print("Result: At least one perturbed run shows measurable spectral spreading.")
        print("Meaning: inspect the spectrum before making any scaling claim.")
    else:
        print("Result: Perturbed initial conditions did not break the single-shell dominance.")
        print("Meaning: forcing/initialization still fails to produce a broad cascade.")
        print("Conclusion: Do not claim k^-3 scaling from Phase 6C.")


if __name__ == "__main__":
    main()