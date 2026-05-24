import csv
import glob
import os

import matplotlib.pyplot as plt
import numpy as np


RUNS = [
    {
        "run": "nu_7.5e-05_f_0.003_m_2",
        "output_dir": "outputs_spectra_refined/nu_7.5e-05_f_0.003_m_2",
        "fit_kmin": 6,
        "fit_kmax": 40,
    },
    {
        "run": "nu_7.5e-05_f_0.006_m_2",
        "output_dir": "outputs_spectra_refined/nu_7.5e-05_f_0.006_m_2",
        "fit_kmin": 9,
        "fit_kmax": 35,
    },
    {
        "run": "nu_5e-05_f_0.01_m_2",
        "output_dir": "outputs_spectra_refined/nu_5e-05_f_0.01_m_2",
        "fit_kmin": 9,
        "fit_kmax": 41,
    },
]


def fit_power_law(k_bins, spectrum, fit_kmin, fit_kmax, valid_mask):
    mask = (
        valid_mask
        & (k_bins >= fit_kmin)
        & (k_bins <= fit_kmax)
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


def load_run(config):
    k_bins = np.load(os.path.join(config["output_dir"], "spectrum_bins.npy"))
    files = sorted(glob.glob(os.path.join(config["output_dir"], "spectrum_k_*.npy")))
    spectra = np.array([np.load(path) for path in files])
    late_mean = np.mean(spectra[len(spectra) // 2 :], axis=0)

    low_k_mask = (k_bins >= 1) & (k_bins <= 6)
    low_k_bins = k_bins[low_k_mask]
    low_k_energy = late_mean[low_k_mask]
    peak_k = float(low_k_bins[int(np.argmax(low_k_energy))])
    peak_mask = (k_bins >= peak_k - 1) & (k_bins <= peak_k + 1)
    valid_mask = ~peak_mask

    return k_bins, files, spectra, peak_k, peak_mask, valid_mask


def normalized_outside_peak(spectrum, valid_mask):
    residual = np.where(valid_mask, spectrum, np.nan)
    norm = np.nansum(residual)

    if norm <= 0:
        return residual * np.nan, norm

    return residual / norm, norm


def analyze_run(config):
    k_bins, files, spectra, peak_k, peak_mask, valid_mask = load_run(config)
    rows = []
    normalized_spectra = []

    for saved_index, path in enumerate(files):
        spectrum = spectra[saved_index]
        normalized, residual_energy = normalized_outside_peak(spectrum, valid_mask)
        slope, r_squared, fit_points = fit_power_law(
            k_bins,
            normalized,
            config["fit_kmin"],
            config["fit_kmax"],
            valid_mask,
        )
        step = int(os.path.basename(path).replace("spectrum_k_", "").replace(".npy", ""))
        normalized_spectra.append(normalized)
        rows.append(
            {
                "run": config["run"],
                "output_dir": config["output_dir"],
                "saved_index": saved_index,
                "step": step,
                "peak_k": peak_k,
                "masked_kmin": peak_k - 1,
                "masked_kmax": peak_k + 1,
                "fit_kmin": config["fit_kmin"],
                "fit_kmax": config["fit_kmax"],
                "fit_points": fit_points,
                "residual_energy": float(residual_energy),
                "masked_slope": slope,
                "masked_r_squared": r_squared,
            }
        )

    late_mean_normalized = np.nanmean(
        np.array(normalized_spectra[len(normalized_spectra) // 2 :]),
        axis=0,
    )
    late_slope, late_r2, late_points = fit_power_law(
        k_bins,
        late_mean_normalized,
        config["fit_kmin"],
        config["fit_kmax"],
        valid_mask,
    )

    summary = {
        "run": config["run"],
        "output_dir": config["output_dir"],
        "peak_k": peak_k,
        "masked_kmin": peak_k - 1,
        "masked_kmax": peak_k + 1,
        "fit_kmin": config["fit_kmin"],
        "fit_kmax": config["fit_kmax"],
        "late_masked_slope": late_slope,
        "late_masked_r_squared": late_r2,
        "late_fit_points": late_points,
        "late_residual_energy_mean": float(np.mean([row["residual_energy"] for row in rows[len(rows) // 2 :]])),
        "last10_slope_mean": float(np.nanmean([row["masked_slope"] for row in rows[-10:]])),
        "last10_slope_std": float(np.nanstd([row["masked_slope"] for row in rows[-10:]])),
        "final_slope": float(rows[-1]["masked_slope"]),
        "final_r_squared": float(rows[-1]["masked_r_squared"]),
    }

    return rows, summary, k_bins, late_mean_normalized, valid_mask


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_normalized_spectra(results, path):
    plt.figure(figsize=(10, 6))

    for config, k_bins, late_mean_normalized, valid_mask in results:
        plt.loglog(
            k_bins[valid_mask],
            late_mean_normalized[valid_mask],
            linewidth=2,
            label=config["run"],
        )

    plt.xlabel("Wavenumber k")
    plt.ylabel("Normalized E(k) outside peak band")
    plt.title("Peak-masked normalized late-time spectra")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_slope_time(rows, path):
    plt.figure(figsize=(10, 6))

    for config in RUNS:
        run_rows = [row for row in rows if row["run"] == config["run"]]
        run_rows = sorted(run_rows, key=lambda row: row["saved_index"])
        plt.plot(
            [row["saved_index"] for row in run_rows],
            [row["masked_slope"] for row in run_rows],
            marker="o",
            markersize=3.5,
            linewidth=1.8,
            label=config["run"],
        )

    plt.axhline(-3, color="black", linestyle="--", linewidth=1, label="slope = -3")
    plt.xlabel("Saved spectrum index")
    plt.ylabel("Peak-masked slope")
    plt.title("Peak-masked slope vs saved spectrum index")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def main():
    all_rows = []
    summaries = []
    normalized_results = []

    for config in RUNS:
        rows, summary, k_bins, late_mean_normalized, valid_mask = analyze_run(config)
        all_rows.extend(rows)
        summaries.append(summary)
        normalized_results.append((config, k_bins, late_mean_normalized, valid_mask))

    write_csv(
        "peak_masked_time_stability.csv",
        all_rows,
        [
            "run",
            "output_dir",
            "saved_index",
            "step",
            "peak_k",
            "masked_kmin",
            "masked_kmax",
            "fit_kmin",
            "fit_kmax",
            "fit_points",
            "residual_energy",
            "masked_slope",
            "masked_r_squared",
        ],
    )
    write_csv(
        "peak_masked_slope_summary.csv",
        summaries,
        [
            "run",
            "output_dir",
            "peak_k",
            "masked_kmin",
            "masked_kmax",
            "fit_kmin",
            "fit_kmax",
            "late_masked_slope",
            "late_masked_r_squared",
            "late_fit_points",
            "late_residual_energy_mean",
            "last10_slope_mean",
            "last10_slope_std",
            "final_slope",
            "final_r_squared",
        ],
    )
    plot_normalized_spectra(normalized_results, "peak_masked_normalized_spectra.png")
    plot_slope_time(all_rows, "peak_masked_slope_vs_time.png")

    print("Peak-masked spectrum summary")
    print("============================")
    for summary in summaries:
        print(
            f"{summary['run']}: "
            f"mask k={summary['masked_kmin']:g}:{summary['masked_kmax']:g}, "
            f"fit k={summary['fit_kmin']:g}:{summary['fit_kmax']:g}, "
            f"late_slope={summary['late_masked_slope']:.4f}, "
            f"late_R2={summary['late_masked_r_squared']:.4f}, "
            f"last10_mean={summary['last10_slope_mean']:.4f}, "
            f"last10_std={summary['last10_slope_std']:.4f}, "
            f"final_slope={summary['final_slope']:.4f}, "
            f"final_R2={summary['final_r_squared']:.4f}"
        )


if __name__ == "__main__":
    main()
