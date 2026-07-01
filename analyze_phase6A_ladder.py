import argparse
import csv
import json
import math
from collections import defaultdict
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
    if not rows:
        return None
    return rows[-1]


def read_spectrum(path):
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return rows

        if "E(k)" in reader.fieldnames:
            e_col = "E(k)"
        elif "Ek" in reader.fieldnames:
            e_col = "Ek"
        else:
            raise ValueError(f"No E(k) or Ek column in {path}")

        for row in reader:
            rows.append(
                {
                    "k": to_float(row.get("k")),
                    "Ek": to_float(row.get(e_col)),
                    "mode_count": to_float(row.get("mode_count")),
                }
            )

    return rows


def load_phase6a_runs(base):
    base = Path(base)

    runs = []

    for run_path in base.iterdir():
        if not run_path.is_dir() or not run_path.name.startswith("run_"):
            continue

        metadata_path = run_path / "metadata.json"
        diagnostics_path = run_path / "diagnostics.csv"
        spectrum_path = run_path / "spectrum.csv"

        if not metadata_path.exists():
            continue

        try:
            metadata = read_json(metadata_path)
        except Exception:
            continue

        config = metadata.get("config", {})
        if not isinstance(config, dict):
            continue

        if config.get("mode") != "phase6A_re_ladder":
            continue

        if not diagnostics_path.exists() or not spectrum_path.exists():
            continue

        diag = read_last_csv_row(diagnostics_path)
        spectrum = read_spectrum(spectrum_path)

        if diag is None or not spectrum:
            continue

        energy = to_float(diag.get("energy"))
        enstrophy = to_float(diag.get("enstrophy"))
        step = to_float(diag.get("step"))
        sum_ek = sum(row["Ek"] for row in spectrum if math.isfinite(row["Ek"]))

        rel_err = math.nan
        if math.isfinite(energy) and abs(energy) > 0:
            rel_err = abs(sum_ek - energy) / abs(energy)

        peak = max(spectrum, key=lambda row: row["Ek"] if math.isfinite(row["Ek"]) else -1.0)
        peak_k = peak["k"]
        peak_ek = peak["Ek"]
        peak_fraction = peak_ek / sum_ek if sum_ek > 0 else math.nan

        active_shells_1pct = sum(
            1 for row in spectrum
            if math.isfinite(row["Ek"]) and sum_ek > 0 and row["Ek"] >= 0.01 * sum_ek
        )

        high_k_fraction = sum(
            row["Ek"] for row in spectrum
            if math.isfinite(row["Ek"]) and math.isfinite(row["k"]) and row["k"] >= 5
        ) / sum_ek if sum_ek > 0 else math.nan

        if peak_fraction > 0.95 and active_shells_1pct <= 2:
            spectrum_shape = "single_shell_dominated"
        else:
            spectrum_shape = "broad_or_multishell"

        runs.append(
            {
                "run_id": run_path.name,
                "Re": config.get("Re"),
                "nx": config.get("nx"),
                "ny": config.get("ny"),
                "dt": config.get("dt"),
                "steps": config.get("steps"),
                "status": metadata.get("status"),
                "commit": str(metadata.get("git_commit", ""))[:7],
                "dirty": metadata.get("git_dirty"),
                "step": step,
                "energy": energy,
                "enstrophy": enstrophy,
                "sum_Ek": sum_ek,
                "rel_err": rel_err,
                "peak_k": peak_k,
                "peak_Ek": peak_ek,
                "peak_fraction": peak_fraction,
                "active_shells_1pct": active_shells_1pct,
                "high_k_fraction": high_k_fraction,
                "spectrum_shape": spectrum_shape,
                "mtime": run_path.stat().st_mtime,
            }
        )

    runs.sort(key=lambda row: row["mtime"], reverse=True)
    return runs


def fmt(value):
    if isinstance(value, float):
        if math.isfinite(value):
            return f"{value:.6e}"
        return "nan"
    return str(value)


def print_run_table(runs):
    headers = [
        "run_id",
        "Re",
        "status",
        "commit",
        "dirty",
        "energy",
        "sum_Ek",
        "rel_err",
        "peak_k",
        "peak_frac",
        "active>1%",
        "hi_k_frac",
        "shape",
    ]

    rows = []
    for r in runs:
        rows.append(
            [
                r["run_id"],
                r["Re"],
                r["status"],
                r["commit"],
                r["dirty"],
                fmt(r["energy"]),
                fmt(r["sum_Ek"]),
                fmt(r["rel_err"]),
                fmt(r["peak_k"]),
                fmt(r["peak_fraction"]),
                r["active_shells_1pct"],
                fmt(r["high_k_fraction"]),
                r["spectrum_shape"],
            ]
        )

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * w for w in widths))

    for row in rows:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))


def print_group_summary(runs):
    groups = defaultdict(list)
    for r in runs:
        groups[r["Re"]].append(r)

    print()
    print("Grouped duplicate-run summary by Re")
    print("----------------------------------")

    headers = [
        "Re",
        "n",
        "mean_energy",
        "energy_rel_spread",
        "mean_enstrophy",
        "peak_k_values",
        "shape_values",
    ]

    rows = []

    for re_value in sorted(groups, key=lambda x: float(x)):
        group = groups[re_value]

        energies = [r["energy"] for r in group if math.isfinite(r["energy"])]
        enstrophies = [r["enstrophy"] for r in group if math.isfinite(r["enstrophy"])]

        mean_energy = sum(energies) / len(energies) if energies else math.nan
        mean_enstrophy = sum(enstrophies) / len(enstrophies) if enstrophies else math.nan

        if energies and mean_energy != 0:
            energy_rel_spread = (max(energies) - min(energies)) / abs(mean_energy)
        else:
            energy_rel_spread = math.nan

        peak_k_values = sorted(set(r["peak_k"] for r in group))
        shape_values = sorted(set(r["spectrum_shape"] for r in group))

        rows.append(
            [
                re_value,
                len(group),
                fmt(mean_energy),
                fmt(energy_rel_spread),
                fmt(mean_enstrophy),
                ",".join(fmt(v) for v in peak_k_values),
                ",".join(shape_values),
            ]
        )

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * w for w in widths))

    for row in rows:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers))))

    print()
    print("Interpretation guardrail")
    print("------------------------")

    all_single_shell = all(r["spectrum_shape"] == "single_shell_dominated" for r in runs)
    all_peak_k3 = all(abs(float(r["peak_k"]) - 3.0) < 1e-12 for r in runs)

    if all_single_shell and all_peak_k3:
        print("Result: The Phase 6A spectra are dominated by one shell near k=3.")
        print("Meaning: This validates the run pipeline, but it does NOT establish a k^-3 inertial-range spectrum.")
        print("Next physics step: run longer and inspect time-averaged spectra before claiming scaling.")
    else:
        print("Result: Spectra are not purely single-shell dominated.")
        print("Meaning: inspect the saved spectra carefully before making any scaling claim.")


def main():
    parser = argparse.ArgumentParser(description="Analyze Phase 6A Reynolds ladder runs.")
    parser.add_argument("--base", default="experiments/runs")
    parser.add_argument("--latest", type=int, default=8)
    args = parser.parse_args()

    runs = load_phase6a_runs(args.base)

    if args.latest:
        runs = runs[: args.latest]

    if not runs:
        raise SystemExit("No Phase 6A ladder runs found.")

    print()
    print(f"Loaded Phase 6A runs: {len(runs)}")
    print()

    print_run_table(runs)
    print_group_summary(runs)


if __name__ == "__main__":
    main()