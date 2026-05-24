import csv
import glob
import os

import matplotlib.pyplot as plt
import numpy as np


RUNS = [
    {
        "run": "nu_7.5e-05_f_0.003_m_2",
        "output_dir": "outputs_spectra_refined/nu_7.5e-05_f_0.003_m_2",
        "kmin": 6,
        "kmax": 40,
    },
    {
        "run": "nu_7.5e-05_f_0.006_m_2",
        "output_dir": "outputs_spectra_refined/nu_7.5e-05_f_0.006_m_2",
        "kmin": 9,
        "kmax": 35,
    },
    {
        "run": "nu_5e-05_f_0.01_m_2",
        "output_dir": "outputs_spectra_refined/nu_5e-05_f_0.01_m_2",
        "kmin": 9,
        "kmax": 41,
    },
]


def fit_slope(k_bins, spectrum, kmin, kmax):
    mask = (
        (k_bins >= kmin)
        & (k_bins <= kmax)
        & np.isfinite(spectrum)
        & (spectrum > 0)
    )
    k_fit = k_bins[mask]
    e_fit = spectrum[mask]

    if len(k_fit) < 3:
        return np.nan, np.nan, len(k_fit)

    logk = np.log10(k_fit)
    loge = np.log10(e_fit)
    slope, intercept = np.polyfit(logk, loge, 1)
    predicted = slope * logk + intercept
    residual = loge - predicted
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((loge - np.mean(loge)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    return float(slope), float(r_squared), len(k_fit)


def analyze_run(config):
    k_bins = np.load(os.path.join(config["output_dir"], "spectrum_bins.npy"))
    files = sorted(glob.glob(os.path.join(config["output_dir"], "spectrum_k_*.npy")))
    rows = []

    for saved_index, path in enumerate(files):
        spectrum = np.load(path)
        slope, r_squared, fit_points = fit_slope(
            k_bins,
            spectrum,
            config["kmin"],
            config["kmax"],
        )
        step = int(os.path.basename(path).replace("spectrum_k_", "").replace(".npy", ""))
        rows.append(
            {
                "run": config["run"],
                "output_dir": config["output_dir"],
                "saved_index": saved_index,
                "step": step,
                "fit_kmin": config["kmin"],
                "fit_kmax": config["kmax"],
                "fit_points": fit_points,
                "slope": slope,
                "r_squared": r_squared,
            }
        )

    return rows


def summarize(rows):
    by_run = {}

    for row in rows:
        by_run.setdefault(row["run"], []).append(row)

    summary = []
    for run, run_rows in by_run.items():
        slopes = np.array([row["slope"] for row in run_rows], dtype=float)
        r2 = np.array([row["r_squared"] for row in run_rows], dtype=float)
        late_count = max(1, len(run_rows) // 2)
        late_slopes = slopes[-late_count:]
        late_r2 = r2[-late_count:]
        final_window_count = min(10, len(run_rows))
        final_slopes = slopes[-final_window_count:]

        summary.append(
            {
                "run": run,
                "n_spectra": len(run_rows),
                "mean_slope": float(np.nanmean(slopes)),
                "late_mean_slope": float(np.nanmean(late_slopes)),
                "late_std_slope": float(np.nanstd(late_slopes)),
                "last10_mean_slope": float(np.nanmean(final_slopes)),
                "last10_std_slope": float(np.nanstd(final_slopes)),
                "final_slope": float(slopes[-1]),
                "late_mean_r2": float(np.nanmean(late_r2)),
                "final_r2": float(r2[-1]),
                "distance_to_minus3": float(abs(np.nanmean(late_slopes) + 3)),
            }
        )

    return summary


def write_csv(path, rows):
    fieldnames = [
        "run",
        "output_dir",
        "saved_index",
        "step",
        "fit_kmin",
        "fit_kmax",
        "fit_points",
        "slope",
        "r_squared",
    ]

    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_metric(rows, metric, ylabel, path):
    plt.figure(figsize=(10, 6))

    for config in RUNS:
        run_rows = [row for row in rows if row["run"] == config["run"]]
        x = [row["saved_index"] for row in run_rows]
        y = [row[metric] for row in run_rows]
        plt.plot(x, y, marker="o", linewidth=1.8, markersize=3.5, label=config["run"])

    if metric == "slope":
        plt.axhline(-3, color="black", linestyle="--", linewidth=1, label="slope = -3")

    plt.xlabel("Saved spectrum index")
    plt.ylabel(ylabel)
    plt.title(ylabel + " vs saved spectrum index")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def main():
    rows = []

    for config in RUNS:
        rows.extend(analyze_run(config))

    write_csv("time_stability_summary.csv", rows)
    plot_metric(rows, "slope", "Log-log slope", "time_stability_slopes.png")
    plot_metric(rows, "r_squared", "Fit R^2", "time_stability_r2.png")

    print("Time-stability summary")
    print("======================")
    for item in summarize(rows):
        print(
            f"{item['run']}: "
            f"late_mean_slope={item['late_mean_slope']:.4f}, "
            f"late_std={item['late_std_slope']:.4f}, "
            f"last10_mean={item['last10_mean_slope']:.4f}, "
            f"last10_std={item['last10_std_slope']:.4f}, "
            f"final_slope={item['final_slope']:.4f}, "
            f"late_mean_r2={item['late_mean_r2']:.4f}, "
            f"final_r2={item['final_r2']:.4f}"
        )


if __name__ == "__main__":
    main()
