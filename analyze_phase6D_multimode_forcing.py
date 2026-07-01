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

        def shell_energy(k_value):
            return sum(
                row["Ek"]
                for row in spectrum
                if math.isfinite(row["Ek"]) and int(row["k"]) == k_value
            )

        e_k3 = shell_energy(3)
        e_k4 = shell_energy(4)

        forced_band_energy = e_k3 + e_k4

        high_k_energy = sum(
            row["Ek"]
            for row in spectrum
            if math.isfinite(row["Ek"]) and math.isfinite(row["k"]) and row["k"] >= 5
        )

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

        runs.append(
            {
                "run_id": run_path.name,
                "mode": mode,
                "steps": config.get("steps"),
                "Re": config.get("Re"),
                "status": metadata.get("status"),
                "commit": str(metadata.get("git_commit", ""))[:7],
                "dirty": metadata.get("git_dirty"),
                "energy": energy,
                "enstrophy": enstrophy,
                "sum_Ek": sum_ek,
                "peak_k": peak["k"],
                "peak_fraction": peak["Ek"] / sum_ek if sum_ek > 0 else math.nan,
                "E_k3_fraction": e_k3 / sum_ek if sum_ek > 0 else math.nan,
                "E_k4_fraction": e_k4 / sum_ek if sum_ek > 0 else math.nan,
                "forced_band_fraction_k3_k4": forced_band_energy / sum_ek if sum_ek > 0 else math.nan,
                "high_k_fraction_k5plus": high_k_energy / sum_ek if sum_ek > 0 else math.nan,
                "active_shells_1pct": active_shells_1pct,
                "active_shells_0p1pct": active_shells_0p1pct,
                "mtime": run_path.stat().st_mtime,
            }
        )

    runs.sort(key=lambda row: row["mtime"], reverse=True)
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
        "mode",
        "steps",
        "Re",
        "energy",
        "peak_k",
        "peak_frac",
        "E3_frac",
        "E4_frac",
        "E3+E4_frac",
        "k>=5_frac",
        "active>1%",
        "active>0.1%",
        "status",
        "commit",
        "dirty",
    ]

    table = []

    for r in rows:
        table.append(
            [
                r["run_id"],
                r["mode"],
                r["steps"],
                r["Re"],
                fmt(r["energy"]),
                fmt(r["peak_k"]),
                fmt(r["peak_fraction"]),
                fmt(r["E_k3_fraction"]),
                fmt(r["E_k4_fraction"]),
                fmt(r["forced_band_fraction_k3_k4"]),
                fmt(r["high_k_fraction_k5plus"]),
                r["active_shells_1pct"],
                r["active_shells_0p1pct"],
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
    baseline = load_runs("phase6B_spreading_test")
    baseline = [r for r in baseline if int(r["steps"]) == 10000]
    baseline = sorted(baseline, key=lambda r: r["mtime"], reverse=True)[:1]

    phase6d = load_runs("phase6D_multimode_forcing")

    rows = baseline + phase6d

    print()
    print(f"Loaded Phase 6B baseline rows: {len(baseline)}")
    print(f"Loaded Phase 6D multimode-forcing runs: {len(phase6d)}")
    print()

    print_table(rows)

    print()
    print("Interpretation")
    print("--------------")

    if not phase6d:
        print("No Phase 6D runs found.")
        return

    latest = phase6d[0]

    print(f"Phase 6D peak fraction: {fmt(latest['peak_fraction'])}")
    print(f"Phase 6D E(k=3) fraction: {fmt(latest['E_k3_fraction'])}")
    print(f"Phase 6D E(k=4) fraction: {fmt(latest['E_k4_fraction'])}")
    print(f"Phase 6D E(k>=5) fraction: {fmt(latest['high_k_fraction_k5plus'])}")
    print(f"Phase 6D active shells >1%: {latest['active_shells_1pct']}")
    print(f"Phase 6D active shells >0.1%: {latest['active_shells_0p1pct']}")

    print()

    if latest["active_shells_1pct"] > 1 and latest["E_k4_fraction"] > 0.01:
        print("Result: Multimode forcing broke the pure k=3 single-shell lock.")
        print("Meaning: energy is now distributed across more than one low-k shell.")
    else:
        print("Result: Multimode forcing did not materially broaden the spectrum.")

    if latest["high_k_fraction_k5plus"] < 0.01:
        print("However: energy beyond k>=5 remains small.")
        print("Conclusion: this is low-k multimode support, not evidence of an inertial-range cascade.")
        print("Do not claim k^-3 scaling from Phase 6D.")
    else:
        print("Energy beyond k>=5 is non-negligible. Inspect spectrum and slopes before making any claim.")


if __name__ == "__main__":
    main()