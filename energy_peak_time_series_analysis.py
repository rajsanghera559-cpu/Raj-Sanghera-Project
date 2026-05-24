import csv
import glob
import os

import matplotlib.pyplot as plt
import numpy as np


RUNS = [
    {
        "run": "nu_7.5e-05_f_0.003_m_2",
        "output_dir": "outputs_spectra_refined/nu_7.5e-05_f_0.003_m_2",
        "mid_kmin": 6,
        "mid_kmax": 40,
    },
    {
        "run": "nu_7.5e-05_f_0.006_m_2",
        "output_dir": "outputs_spectra_refined/nu_7.5e-05_f_0.006_m_2",
        "mid_kmin": 9,
        "mid_kmax": 35,
    },
    {
        "run": "nu_5e-05_f_0.01_m_2",
        "output_dir": "outputs_spectra_refined/nu_5e-05_f_0.01_m_2",
        "mid_kmin": 9,
        "mid_kmax": 41,
    },
]


def load_run(config):
    k_bins = np.load(os.path.join(config["output_dir"], "spectrum_bins.npy"))
    files = sorted(glob.glob(os.path.join(config["output_dir"], "spectrum_k_*.npy")))
    spectra = np.array([np.load(path) for path in files])
    late_mean = np.mean(spectra[len(spectra) // 2 :], axis=0)

    low_k_mask = (k_bins >= 1) & (k_bins <= 6)
    low_k_bins = k_bins[low_k_mask]
    low_k_energy = late_mean[low_k_mask]
    peak_k = float(low_k_bins[int(np.argmax(low_k_energy))])

    return k_bins, files, spectra, peak_k


def analyze_run(config):
    k_bins, files, spectra, peak_k = load_run(config)
    peak_mask = (k_bins >= peak_k - 1) & (k_bins <= peak_k + 1)
    mid_mask = (k_bins >= config["mid_kmin"]) & (k_bins <= config["mid_kmax"])
    high_mask = k_bins >= 40

    rows = []
    for saved_index, path in enumerate(files):
        spectrum = spectra[saved_index]
        step = int(os.path.basename(path).replace("spectrum_k_", "").replace(".npy", ""))
        rows.append(
            {
                "run": config["run"],
                "output_dir": config["output_dir"],
                "saved_index": saved_index,
                "step": step,
                "peak_k": peak_k,
                "peak_kmin": peak_k - 1,
                "peak_kmax": peak_k + 1,
                "mid_kmin": config["mid_kmin"],
                "mid_kmax": config["mid_kmax"],
                "total_energy": float(np.sum(spectrum)),
                "peak_mode_energy": float(np.sum(spectrum[peak_mask])),
                "midrange_energy": float(np.sum(spectrum[mid_mask])),
                "high_k_energy": float(np.sum(spectrum[high_mask])),
            }
        )

    return rows


def write_csv(path, rows):
    fieldnames = [
        "run",
        "output_dir",
        "saved_index",
        "step",
        "peak_k",
        "peak_kmin",
        "peak_kmax",
        "mid_kmin",
        "mid_kmax",
        "total_energy",
        "peak_mode_energy",
        "midrange_energy",
        "high_k_energy",
    ]

    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_metric(rows, metric, ylabel, path, log_y=True):
    plt.figure(figsize=(10, 6))

    for config in RUNS:
        run_rows = [row for row in rows if row["run"] == config["run"]]
        x = [row["saved_index"] for row in run_rows]
        y = [row[metric] for row in run_rows]
        plt.plot(x, y, marker="o", linewidth=1.8, markersize=3.5, label=config["run"])

    plt.xlabel("Saved spectrum index")
    plt.ylabel(ylabel)
    plt.title(ylabel + " vs saved spectrum index")
    if log_y:
        plt.yscale("log")
    plt.grid(True, alpha=0.3, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def trend_summary(rows):
    by_run = {}
    for row in rows:
        by_run.setdefault(row["run"], []).append(row)

    summaries = []
    for run, run_rows in by_run.items():
        run_rows = sorted(run_rows, key=lambda item: item["saved_index"])
        late_rows = run_rows[len(run_rows) // 2 :]
        last10 = run_rows[-10:]

        item = {"run": run}
        for metric in [
            "total_energy",
            "peak_mode_energy",
            "midrange_energy",
            "high_k_energy",
        ]:
            values = np.array([row[metric] for row in run_rows], dtype=float)
            late_values = np.array([row[metric] for row in late_rows], dtype=float)
            last10_values = np.array([row[metric] for row in last10], dtype=float)
            item[f"{metric}_initial"] = float(values[0])
            item[f"{metric}_final"] = float(values[-1])
            item[f"{metric}_growth_factor"] = float(values[-1] / values[0]) if values[0] > 0 else np.nan
            item[f"{metric}_late_growth_factor"] = (
                float(late_values[-1] / late_values[0]) if late_values[0] > 0 else np.nan
            )
            item[f"{metric}_last10_growth_factor"] = (
                float(last10_values[-1] / last10_values[0]) if last10_values[0] > 0 else np.nan
            )

        summaries.append(item)

    return summaries


def main():
    rows = []
    for config in RUNS:
        rows.extend(analyze_run(config))

    write_csv("energy_peak_time_series_summary.csv", rows)
    plot_metric(rows, "total_energy", "Total spectral energy proxy", "energy_total_vs_time.png")
    plot_metric(rows, "peak_mode_energy", "Peak-mode energy proxy", "peak_mode_energy_vs_time.png")
    plot_metric(rows, "midrange_energy", "Midrange energy proxy", "midrange_energy_vs_time.png")
    plot_metric(rows, "high_k_energy", "High-k energy proxy", "high_k_energy_vs_time.png")

    print("Energy/peak time-series summary")
    print("================================")
    for item in trend_summary(rows):
        print(item["run"])
        for metric in [
            "total_energy",
            "peak_mode_energy",
            "midrange_energy",
            "high_k_energy",
        ]:
            print(
                f"  {metric}: "
                f"final={item[f'{metric}_final']:.6e}, "
                f"full_growth={item[f'{metric}_growth_factor']:.6e}, "
                f"late_growth={item[f'{metric}_late_growth_factor']:.6e}, "
                f"last10_growth={item[f'{metric}_last10_growth_factor']:.6e}"
            )


if __name__ == "__main__":
    main()
