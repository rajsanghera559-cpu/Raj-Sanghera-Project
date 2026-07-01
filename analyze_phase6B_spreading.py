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
        rows = []

        if "E(k)" in reader.fieldnames:
            e_col = "E(k)"
        elif "Ek" in reader.fieldnames:
            e_col = "Ek"
        else:
            raise ValueError(f"No E(k) column in {path}")

        for row in reader:
            rows.append({
                "k": to_float(row.get("k")),
                "Ek": to_float(row.get(e_col)),
                "mode_count": to_float(row.get("mode_count")),
            })

    return rows


def load_phase6b_runs(base="experiments/runs"):
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

        if config.get("mode") != "phase6B_spreading_test":
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
            1 for row in spectrum
            if math.isfinite(row["Ek"]) and sum_ek > 0 and row["Ek"] >= 0.01 * sum_ek
        )

        active_shells_0p1pct = sum(
            1 for row in spectrum
            if math.isfinite(row["Ek"]) and sum_ek > 0 and row["Ek"] >= 0.001 * sum_ek
        )

        high_k_fraction = sum(
            row["Ek"] for row in spectrum
            if math.isfinite(row["Ek"]) and math.isfinite(row["k"]) and row["k"] >= 5
        ) / sum_ek if sum_ek > 0 else math.nan

        runs.append({
            "run_id": run_path.name,
            "steps": config.get("steps"),
            "Re": config.get("Re"),
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
            "mtime": run_path.stat().st_mtime,
        })

    runs.sort(key=lambda r: int(r["steps"]))
    return runs


def fmt(x):
    if isinstance(x, float):
        if math.isfinite(x):
            return f"{x:.6e}"
        return "nan"
    return str(x)


def print_table(runs):
    headers = [
        "run_id",
        "steps",
        "Re",
        "energy",
        "enstrophy",
        "sum_Ek",
        "peak_k",
        "peak_frac",
        "active>1%",
        "active>0.1%",
        "hi_k_frac",
        "status",
        "commit",
        "dirty",
    ]

    rows = []
    for r in runs:
        rows.append([
            r["run_id"],
            r["steps"],
            r["Re"],
            fmt(r["energy"]),
            fmt(r["enstrophy"]),
            fmt(r["sum_Ek"]),
            fmt(r["peak_k"]),
            fmt(r["peak_fraction"]),
            r["active_shells_1pct"],
            r["active_shells_0p1pct"],
            fmt(r["high_k_fraction"]),
            r["status"],
            r["commit"],
            r["dirty"],
        ])

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * w for w in widths))

    for row in rows:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))


def print_interpretation(runs):
    print()
    print("Interpretation")
    print("--------------")

    if not runs:
        print("No Phase 6B runs found.")
        return

    first = runs[0]
    last = runs[-1]

    energy_growth = last["energy"] / first["energy"] if first["energy"] > 0 else math.nan
    high_k_growth = (
        last["high_k_fraction"] / first["high_k_fraction"]
        if first["high_k_fraction"] > 0
        else math.nan
    )

    print(f"Energy growth from first to last run: {fmt(energy_growth)}")
    print(f"Peak fraction at final run: {fmt(last['peak_fraction'])}")
    print(f"Active shells >1% at final run: {last['active_shells_1pct']}")
    print(f"Active shells >0.1% at final run: {last['active_shells_0p1pct']}")
    print(f"High-k fraction k>=5 at final run: {fmt(last['high_k_fraction'])}")

    if last["peak_fraction"] > 0.95 and last["active_shells_1pct"] <= 2:
        print()
        print("Result: Spectrum is still single-shell dominated.")
        print("Meaning: Longer runtime increased energy, but did not create a broad cascade.")
        print("Conclusion: Do not claim k^-3 scaling from Phase 6B.")
    else:
        print()
        print("Result: Spectrum shows some spreading beyond the forced shell.")
        print("Meaning: inspect the spectrum carefully before any scaling claim.")


def main():
    runs = load_phase6b_runs()

    print()
    print(f"Loaded Phase 6B spreading runs: {len(runs)}")
    print()

    print_table(runs)
    print_interpretation(runs)


if __name__ == "__main__":
    main()