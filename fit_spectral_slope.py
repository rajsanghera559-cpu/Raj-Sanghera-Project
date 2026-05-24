import argparse
import csv
import glob
import os

import matplotlib.pyplot as plt
import numpy as np


DEFAULT_OUTPUT_DIR = "outputs_nu_0.001"
DEFAULT_RANGES = [(4, 8), (8, 40), (10, 80)]
DEFAULT_AUTO_KMIN = 5
DEFAULT_AUTO_KMAX = 80
DEFAULT_AUTO_MIN_POINTS = 10
DEFAULT_AUTO_TOP_N = 3
DEFAULT_AUTO_MIN_SLOPE = -5.0
DEFAULT_AUTO_MAX_SLOPE = -0.5
DEFAULT_AUTO_MIN_R2 = 0.8


def parse_fit_ranges(values):
    ranges = []

    for value in values:
        try:
            left, right = value.split(":", 1)
            kmin = float(left)
            kmax = float(right)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"Fit range must look like kmin:kmax, got {value!r}"
            ) from exc

        if kmin >= kmax:
            raise argparse.ArgumentTypeError(
                f"Fit range must satisfy kmin < kmax, got {value!r}"
            )

        ranges.append((kmin, kmax))

    return ranges


def load_spectra(output_dir):
    files = sorted(glob.glob(os.path.join(output_dir, "spectrum_k_*.npy")))
    bins_path = os.path.join(output_dir, "spectrum_bins.npy")

    if not files:
        raise FileNotFoundError(f"No spectrum files found in {output_dir!r}")

    if not os.path.exists(bins_path):
        raise FileNotFoundError(f"Missing spectrum bins file: {bins_path}")

    spectra = np.array([np.load(path) for path in files])
    k_bins = np.load(bins_path)

    if spectra.ndim != 2:
        raise ValueError(f"Expected 2D spectra array, got shape {spectra.shape}")

    if spectra.shape[1] != len(k_bins):
        raise ValueError(
            f"Spectrum length {spectra.shape[1]} does not match {len(k_bins)} bins"
        )

    return files, k_bins, spectra


def fit_power_law(k_bins, spectrum, kmin, kmax):
    mask = (k_bins >= kmin) & (k_bins <= kmax) & np.isfinite(spectrum) & (spectrum > 0)
    k_fit = k_bins[mask]
    e_fit = spectrum[mask]

    if len(k_fit) < 3:
        return None

    logk = np.log10(k_fit)
    loge = np.log10(e_fit)

    slope, intercept = np.polyfit(logk, loge, 1)
    predicted = slope * logk + intercept

    residual = loge - predicted
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((loge - np.mean(loge)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    return {
        "kmin": kmin,
        "kmax": kmax,
        "points": len(k_fit),
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_squared),
        "fit_k": k_fit,
        "fit_e": 10**intercept * k_fit**slope,
    }


def score_auto_fit(fit, target_slope=None):
    log_width = np.log10(fit["kmax"]) - np.log10(fit["kmin"])
    score = fit["r_squared"] + 0.12 * log_width

    if target_slope is not None:
        score -= 0.08 * abs(fit["slope"] - target_slope)

    return float(score)


def find_auto_windows(
    k_bins,
    spectrum,
    kmin,
    kmax,
    min_points,
    top_n,
    min_slope,
    max_slope,
    min_r2,
    target_slope=None,
):
    valid = (
        (k_bins >= kmin)
        & (k_bins <= kmax)
        & np.isfinite(spectrum)
        & (spectrum > 0)
    )
    candidates = np.where(valid)[0]
    fits = []

    for start_pos in range(0, len(candidates)):
        for end_pos in range(start_pos + min_points - 1, len(candidates)):
            window_indices = candidates[start_pos : end_pos + 1]
            left = float(k_bins[window_indices[0]])
            right = float(k_bins[window_indices[-1]])
            fit = fit_power_law(k_bins, spectrum, left, right)

            if fit is None:
                continue

            if not min_slope <= fit["slope"] <= max_slope:
                continue

            if fit["r_squared"] < min_r2:
                continue

            fit["auto_score"] = score_auto_fit(fit, target_slope)
            fit["kind"] = "auto"
            fits.append(fit)

    fits.sort(key=lambda item: item["auto_score"], reverse=True)

    selected = []
    used_ranges = []

    for fit in fits:
        overlap = False
        fit_width = fit["kmax"] - fit["kmin"]

        for used_kmin, used_kmax in used_ranges:
            overlap_left = max(fit["kmin"], used_kmin)
            overlap_right = min(fit["kmax"], used_kmax)
            overlap_width = max(0, overlap_right - overlap_left)

            if fit_width > 0 and overlap_width / fit_width > 0.6:
                overlap = True
                break

        if overlap:
            continue

        selected.append(fit)
        used_ranges.append((fit["kmin"], fit["kmax"]))

        if len(selected) >= top_n:
            break

    return selected


def describe_peak(k_bins, spectrum):
    peak_index = int(np.nanargmax(spectrum))
    return k_bins[peak_index], spectrum[peak_index]


def analyze_output_dir(output_dir, skip_fraction, fit_ranges, auto_options):
    files, k_bins, spectra = load_spectra(output_dir)
    start_index = int(len(files) * skip_fraction)
    selected = spectra[start_index:]

    if len(selected) == 0:
        raise ValueError(f"No spectra remain for {output_dir!r} after --skip-fraction")

    mean_spectrum = np.mean(selected, axis=0)
    final_spectrum = spectra[-1]
    peak_k, peak_e = describe_peak(k_bins, final_spectrum)
    fits = []

    for kmin, kmax in fit_ranges:
        fit = fit_power_law(k_bins, mean_spectrum, kmin, kmax)
        if fit is not None:
            fit["kind"] = "fixed"
            fits.append(fit)

    auto_fits = []
    if auto_options["enabled"]:
        auto_fits = find_auto_windows(
            k_bins,
            mean_spectrum,
            auto_options["kmin"],
            auto_options["kmax"],
            auto_options["min_points"],
            auto_options["top_n"],
            auto_options["min_slope"],
            auto_options["max_slope"],
            auto_options["min_r2"],
            auto_options["target_slope"],
        )

    return {
        "output_dir": output_dir,
        "files": files,
        "k_bins": k_bins,
        "spectra": spectra,
        "start_index": start_index,
        "selected": selected,
        "mean_spectrum": mean_spectrum,
        "final_spectrum": final_spectrum,
        "peak_k": peak_k,
        "peak_e": peak_e,
        "fits": fits,
        "auto_fits": auto_fits,
    }


def print_run_report(run):
    k_bins = run["k_bins"]
    final_spectrum = run["final_spectrum"]

    print("\nSpectral analysis")
    print("=================")
    print(f"output_dir       = {run['output_dir']}")
    print(f"spectra_loaded   = {len(run['files'])}")
    print(f"spectra_averaged = {len(run['selected'])}")
    print(f"skipped_initial  = {run['start_index']}")
    print(f"final_peak       = k={run['peak_k']:g}, E={run['peak_e']:.6e}")
    print(
        f"final_E_k4       = {final_spectrum[k_bins == 4][0]:.6e}"
        if np.any(k_bins == 4)
        else "final_E_k4       = unavailable"
    )

    print("\nPower-law fits on late-time mean spectrum")
    print("-----------------------------------------")

    for fit in run["fits"]:
        print(
            f"k={fit['kmin']:g}:{fit['kmax']:g}  "
            f"slope={fit['slope']:.6f}  "
            f"R^2={fit['r_squared']:.4f}  "
            f"points={fit['points']}"
        )

    if run["auto_fits"]:
        print("\nAutomatic candidate windows")
        print("---------------------------")

        for fit in run["auto_fits"]:
            print(
                f"k={fit['kmin']:g}:{fit['kmax']:g}  "
                f"slope={fit['slope']:.6f}  "
                f"R^2={fit['r_squared']:.4f}  "
                f"points={fit['points']}  "
                f"score={fit['auto_score']:.4f}"
            )


def save_single_run_plot(run, save_path):
    plt.figure(figsize=(9, 6))
    plt.loglog(run["k_bins"], run["final_spectrum"], alpha=0.45, label="Final spectrum")
    plt.loglog(
        run["k_bins"],
        run["mean_spectrum"],
        linewidth=2,
        label="Late-time mean spectrum",
    )

    for fit in run["fits"] + run["auto_fits"][:1]:
        linestyle = ":" if fit.get("kind") == "auto" else "--"
        prefix = "auto " if fit.get("kind") == "auto" else ""
        plt.loglog(
            fit["fit_k"],
            fit["fit_e"],
            linestyle,
            label=(
                f"{prefix}k={fit['kmin']:g}:{fit['kmax']:g}, "
                f"slope={fit['slope']:.2f}, R^2={fit['r_squared']:.2f}"
            ),
        )

    plt.xlabel("Wavenumber k")
    plt.ylabel("E(k)")
    plt.title(f"Spectral slope fits: {run['output_dir']}")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=160)


def save_comparison_plot(runs, save_path):
    plt.figure(figsize=(10, 6))

    for run in runs:
        label = os.path.basename(os.path.normpath(run["output_dir"])) or run["output_dir"]
        plt.loglog(
            run["k_bins"],
            run["mean_spectrum"],
            linewidth=2,
            label=f"{label} late-time mean",
        )

    plt.xlabel("Wavenumber k")
    plt.ylabel("E(k)")
    plt.title("Late-time mean spectrum comparison")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=160)


def print_comparison_report(runs):
    print("\nComparison summary")
    print("==================")
    print("run                 peak_k     peak_E          slope_8:40     best_auto")
    print("------------------  ---------  --------------  -------------  ----------------")

    for run in runs:
        name = os.path.basename(os.path.normpath(run["output_dir"])) or run["output_dir"]
        fit_by_range = {
            (fit["kmin"], fit["kmax"]): fit
            for fit in run["fits"]
        }
        fit_4_8 = fit_by_range.get((4, 8))
        fit_8_40 = fit_by_range.get((8, 40))
        slope_8_40 = f"{fit_8_40['slope']:.6f}" if fit_8_40 else "n/a"
        best_auto = run["auto_fits"][0] if run["auto_fits"] else None
        auto_label = (
            f"{best_auto['slope']:.3f} @ {best_auto['kmin']:g}:{best_auto['kmax']:g}"
            if best_auto
            else "n/a"
        )

        print(
            f"{name:<18}  "
            f"{run['peak_k']:<9g}  "
            f"{run['peak_e']:<14.6e}  "
            f"{slope_8_40:<13}  "
            f"{auto_label:<16}"
        )


def write_summary_csv(runs, path):
    rows = []

    for run in runs:
        for fit in run["fits"] + run["auto_fits"]:
            rows.append(
                {
                    "output_dir": run["output_dir"],
                    "run": os.path.basename(os.path.normpath(run["output_dir"])),
                    "spectra_loaded": len(run["files"]),
                    "spectra_averaged": len(run["selected"]),
                    "skipped_initial": run["start_index"],
                    "peak_k": run["peak_k"],
                    "peak_E": run["peak_e"],
                    "fit_kmin": fit["kmin"],
                    "fit_kmax": fit["kmax"],
                    "fit_points": fit["points"],
                    "slope": fit["slope"],
                    "r_squared": fit["r_squared"],
                    "fit_kind": fit.get("kind", "fixed"),
                    "auto_score": fit.get("auto_score", ""),
                }
            )

    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "output_dir",
                "run",
                "spectra_loaded",
                "spectra_averaged",
                "skipped_initial",
                "peak_k",
                "peak_E",
                "fit_kmin",
                "fit_kmax",
                "fit_points",
                "slope",
                "r_squared",
                "fit_kind",
                "auto_score",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def discover_spectrum_dirs(root):
    matches = []

    for current_root, _, files in os.walk(root):
        if "spectrum_bins.npy" in files:
            matches.append(current_root)

    return sorted(matches)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Analyze saved spectra and fit candidate power-law ranges."
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory containing spectrum_*.npy files. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--compare-dir",
        action="append",
        help="Additional spectrum output directory to compare against. May be repeated.",
    )
    parser.add_argument(
        "--compare-root",
        help="Discover and compare every spectrum directory below this root.",
    )
    parser.add_argument(
        "--skip-fraction",
        type=float,
        default=0.5,
        help="Fraction of early spectra to discard before time averaging. Default: 0.5",
    )
    parser.add_argument(
        "--fit-range",
        action="append",
        help="Fit range in kmin:kmax form. May be repeated. Default: 4:8, 8:40, 10:80",
    )
    parser.add_argument(
        "--save",
        default=None,
        help="Output plot path. Default: <output-dir>/spectral_slope_fit.png",
    )
    parser.add_argument(
        "--summary-csv",
        default=None,
        help="Write a CSV summary of all fit results.",
    )
    parser.add_argument(
        "--no-auto-window",
        action="store_true",
        help="Disable automatic power-law window detection.",
    )
    parser.add_argument(
        "--auto-kmin",
        type=float,
        default=DEFAULT_AUTO_KMIN,
        help=f"Minimum k for automatic window search. Default: {DEFAULT_AUTO_KMIN}",
    )
    parser.add_argument(
        "--auto-kmax",
        type=float,
        default=DEFAULT_AUTO_KMAX,
        help=f"Maximum k for automatic window search. Default: {DEFAULT_AUTO_KMAX}",
    )
    parser.add_argument(
        "--auto-min-points",
        type=int,
        default=DEFAULT_AUTO_MIN_POINTS,
        help=f"Minimum points in each automatic window. Default: {DEFAULT_AUTO_MIN_POINTS}",
    )
    parser.add_argument(
        "--auto-top-n",
        type=int,
        default=DEFAULT_AUTO_TOP_N,
        help=f"Number of automatic windows to keep per run. Default: {DEFAULT_AUTO_TOP_N}",
    )
    parser.add_argument(
        "--auto-target-slope",
        type=float,
        default=None,
        help="Optional slope target used as a soft ranking preference.",
    )
    parser.add_argument(
        "--auto-min-slope",
        type=float,
        default=DEFAULT_AUTO_MIN_SLOPE,
        help=f"Steepest slope allowed in automatic windows. Default: {DEFAULT_AUTO_MIN_SLOPE}",
    )
    parser.add_argument(
        "--auto-max-slope",
        type=float,
        default=DEFAULT_AUTO_MAX_SLOPE,
        help=f"Shallowest slope allowed in automatic windows. Default: {DEFAULT_AUTO_MAX_SLOPE}",
    )
    parser.add_argument(
        "--auto-min-r2",
        type=float,
        default=DEFAULT_AUTO_MIN_R2,
        help=f"Minimum R^2 allowed in automatic windows. Default: {DEFAULT_AUTO_MIN_R2}",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the matplotlib window after saving the plot.",
    )
    return parser


def main():
    args = build_parser().parse_args()

    if not 0 <= args.skip_fraction < 1:
        raise ValueError("--skip-fraction must be in [0, 1)")

    fit_ranges = (
        parse_fit_ranges(args.fit_range)
        if args.fit_range
        else DEFAULT_RANGES
    )

    if args.auto_kmin >= args.auto_kmax:
        raise ValueError("--auto-kmin must be less than --auto-kmax")

    if args.auto_min_points < 3:
        raise ValueError("--auto-min-points must be at least 3")

    if args.auto_min_slope >= args.auto_max_slope:
        raise ValueError("--auto-min-slope must be less than --auto-max-slope")

    if not 0 <= args.auto_min_r2 <= 1:
        raise ValueError("--auto-min-r2 must be in [0, 1]")

    auto_options = {
        "enabled": not args.no_auto_window,
        "kmin": args.auto_kmin,
        "kmax": args.auto_kmax,
        "min_points": args.auto_min_points,
        "top_n": args.auto_top_n,
        "min_slope": args.auto_min_slope,
        "max_slope": args.auto_max_slope,
        "min_r2": args.auto_min_r2,
        "target_slope": args.auto_target_slope,
    }

    output_dirs = [args.output_dir] + (args.compare_dir or [])

    if args.compare_root:
        for path in discover_spectrum_dirs(args.compare_root):
            if path not in output_dirs:
                output_dirs.append(path)

    runs = [
        analyze_output_dir(path, args.skip_fraction, fit_ranges, auto_options)
        for path in output_dirs
    ]

    for run in runs:
        print_run_report(run)

    print("\nReference theoretical slopes")
    print("----------------------------")
    print("2D inverse energy cascade:   -5/3 ~= -1.667")
    print("2D enstrophy cascade:        -3")

    save_path = args.save or os.path.join(args.output_dir, "spectral_slope_fit.png")

    if len(runs) > 1:
        print_comparison_report(runs)
        save_comparison_plot(runs, save_path)
    else:
        save_single_run_plot(runs[0], save_path)

    print(f"\nSaved plot: {save_path}")

    if args.summary_csv:
        write_summary_csv(runs, args.summary_csv)
        print(f"Saved summary CSV: {args.summary_csv}")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
