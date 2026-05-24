import csv
import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


RUN = "forcing_f_0.01_m3_nodrag"
RUN_DIR = Path("outputs_forcing_redesign/f_0.01_m3_nodrag")
ANALYSIS_DIR = Path("outputs_forcing_redesign/analysis_f_0.01_m3_nodrag")
FIT_KMIN = 9
FIT_KMAX = 41  # exclusive, matching prior k=9:41 convention
N = 256
SAVE_EVERY = 1000


COLORS = [
    (31, 119, 180),
    (214, 39, 40),
    (44, 160, 44),
    (255, 127, 14),
    (148, 103, 189),
    (140, 86, 75),
]


def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def read_metric_csv(path, value_column=None):
    data = {}
    if not path.exists():
        return data
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            key = row.get("metric")
            if not key:
                continue
            if value_column and value_column in row:
                data[key] = row[value_column]
            else:
                for col, value in row.items():
                    if col != "metric" and value not in (None, ""):
                        data[key] = value
                        break
    return data


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_spectra(run_dir):
    bins = np.load(run_dir / "spectrum_bins.npy")
    files = sorted(run_dir.glob("spectrum_k_*.npy"))
    records = []
    for file_path in files:
        step = int(file_path.stem.split("_")[-1])
        records.append(
            {
                "file": file_path.name,
                "step": step,
                "saved_index": step // SAVE_EVERY,
                "spectrum": np.load(file_path),
            }
        )
    return bins.astype(float), records


def shell_counts(n):
    L = 2.0 * np.pi
    dx = L / n
    k = np.fft.fftfreq(n, d=dx) * 2.0 * np.pi
    kx, ky = np.meshgrid(k, k)
    kmag = np.sqrt(kx**2 + ky**2).ravel()
    bins = np.arange(1, n // 2)
    rows = []
    for kb in bins:
        count = int(np.count_nonzero((kmag >= kb - 0.5) & (kmag < kb + 0.5)))
        rows.append({"k": int(kb), "mode_count": count})
    return rows


def fit_loglog(k, y):
    k = np.asarray(k, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = (k > 0.0) & (y > 0.0) & np.isfinite(y)
    if np.count_nonzero(mask) < 3:
        return np.nan, np.nan, 0
    x = np.log(k[mask])
    yy = np.log(y[mask])
    slope, intercept = np.polyfit(x, yy, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((yy - pred) ** 2))
    ss_tot = float(np.sum((yy - np.mean(yy)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else np.nan
    return float(slope), float(r2), int(np.count_nonzero(mask))


def pct_change(start, end):
    if start == 0 or not np.isfinite(start) or not np.isfinite(end):
        return np.nan
    return 100.0 * (end - start) / start


def normalized_residual_spectrum(spectrum, peak_mask):
    residual = spectrum.astype(float).copy()
    residual[peak_mask] = 0.0
    denom = float(np.sum(residual))
    if denom <= 0.0:
        return residual * np.nan, denom
    return residual / denom, denom


def compensated_cv(bins, norm_spectrum, fit_mask):
    comp = (bins[fit_mask] ** 3) * norm_spectrum[fit_mask]
    comp = comp[np.isfinite(comp) & (comp > 0.0)]
    if len(comp) == 0:
        return np.nan, np.nan, np.nan, 0
    mean = float(np.mean(comp))
    std = float(np.std(comp))
    cv = std / mean if mean != 0.0 else np.nan
    return mean, std, cv, int(len(comp))


def linear_regression(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(mask) < 2:
        return np.nan
    slope, _ = np.polyfit(x[mask], y[mask], 1)
    return float(slope)


def draw_plot(path, series, title, xlabel, ylabel, logy=False, hlines=None):
    width, height = 1000, 620
    margin_l, margin_r, margin_t, margin_b = 90, 40, 55, 80
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    values_x = []
    values_y = []
    clean_series = []
    for name, x, y in series:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        if logy:
            mask &= y > 0.0
        x = x[mask]
        y = y[mask]
        if len(x) == 0:
            continue
        clean_series.append((name, x, y))
        values_x.extend(x.tolist())
        values_y.extend((np.log10(y) if logy else y).tolist())

    if not values_x or not values_y:
        draw.text((20, 20), f"{title}: no plottable data", fill="black", font=font)
        img.save(path)
        return

    xmin, xmax = min(values_x), max(values_x)
    ymin, ymax = min(values_y), max(values_y)
    if xmin == xmax:
        xmin -= 1.0
        xmax += 1.0
    if ymin == ymax:
        ymin -= 1.0
        ymax += 1.0
    pad_y = 0.05 * (ymax - ymin)
    ymin -= pad_y
    ymax += pad_y

    def to_xy(xv, yv):
        yv = math.log10(yv) if logy else yv
        px = margin_l + (xv - xmin) / (xmax - xmin) * plot_w
        py = margin_t + (ymax - yv) / (ymax - ymin) * plot_h
        return px, py

    draw.rectangle([margin_l, margin_t, width - margin_r, height - margin_b], outline=(0, 0, 0))
    draw.text((margin_l, 18), title, fill="black", font=font)
    draw.text((width // 2 - 40, height - 35), xlabel, fill="black", font=font)
    draw.text((15, height // 2), ylabel, fill="black", font=font)
    draw.text((margin_l, height - margin_b + 10), f"{xmin:g}", fill="black", font=font)
    draw.text((width - margin_r - 60, height - margin_b + 10), f"{xmax:g}", fill="black", font=font)
    draw.text((20, margin_t), f"{(10 ** ymax if logy else ymax):.3g}", fill="black", font=font)
    draw.text((20, height - margin_b - 10), f"{(10 ** ymin if logy else ymin):.3g}", fill="black", font=font)

    if hlines:
        for value, label, color in hlines:
            if logy and value <= 0:
                continue
            _, py = to_xy(xmin, value)
            draw.line([margin_l, py, width - margin_r, py], fill=color, width=1)
            draw.text((width - margin_r - 120, py - 12), label, fill=color, font=font)

    for idx, (name, x, y) in enumerate(clean_series):
        color = COLORS[idx % len(COLORS)]
        pts = [to_xy(float(a), float(b)) for a, b in zip(x, y)]
        if len(pts) > 1:
            draw.line(pts, fill=color, width=2)
        for px, py in pts:
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=color)
        draw.text((margin_l + 20, margin_t + 20 + 16 * idx), name, fill=color, font=font)

    img.save(path)


def draw_heatmap(path, rows, row_key, col_key, value_key, title):
    row_vals = sorted({row[row_key] for row in rows})
    col_vals = sorted({row[col_key] for row in rows})
    vals = [float(row[value_key]) for row in rows if row.get(value_key) not in ("", None)]
    width = 110 + 105 * len(col_vals)
    height = 95 + 42 * len(row_vals)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((20, 20), title, fill="black", font=font)
    if not vals:
        img.save(path)
        return
    vmin, vmax = min(vals), max(vals)
    if vmin == vmax:
        vmax = vmin + 1.0
    value_map = {(row[row_key], row[col_key]): float(row[value_key]) for row in rows}
    for j, col in enumerate(col_vals):
        draw.text((110 + j * 105, 58), str(col), fill="black", font=font)
    for i, rv in enumerate(row_vals):
        y = 85 + i * 42
        draw.text((8, y + 10), str(rv), fill="black", font=font)
        for j, col in enumerate(col_vals):
            x = 105 + j * 105
            val = value_map.get((rv, col), np.nan)
            if np.isfinite(val):
                t = (val - vmin) / (vmax - vmin)
                color = (int(255 * t), int(180 * (1 - abs(t - 0.5) * 2)), int(255 * (1 - t)))
                label = f"{val:.3g}"
            else:
                color = (230, 230, 230)
                label = "nan"
            draw.rectangle([x, y, x + 95, y + 34], fill=color, outline=(60, 60, 60))
            draw.text((x + 8, y + 10), label, fill="black", font=font)
    img.save(path)


def main():
    ensure_dir(ANALYSIS_DIR)
    bins, records = load_spectra(RUN_DIR)
    if not records:
        raise RuntimeError(f"No spectra found in {RUN_DIR}")

    low_peak_mask = bins <= 8
    late_mean = np.mean([r["spectrum"] for r in records[-10:]], axis=0)
    peak_k = int(bins[low_peak_mask][np.argmax(late_mean[low_peak_mask])])
    peak_mask = (bins >= peak_k - 1) & (bins <= peak_k + 1)
    fit_mask = (bins >= FIT_KMIN) & (bins < FIT_KMAX)
    high_mask = bins >= 40
    tail_mask = bins >= 100

    time_rows = []
    for rec in records:
        spec = rec["spectrum"].astype(float)
        norm, residual_energy = normalized_residual_spectrum(spec, peak_mask)
        slope, r2, nfit = fit_loglog(bins[fit_mask], norm[fit_mask])
        comp_mean, comp_std, comp_cv, width = compensated_cv(bins, norm, fit_mask)
        total = float(np.sum(spec))
        peak = float(np.sum(spec[peak_mask]))
        mid = float(np.sum(spec[fit_mask]))
        high = float(np.sum(spec[high_mask]))
        fit_vals = spec[fit_mask]
        tail_vals = spec[tail_mask]
        pos = spec[spec > 0.0]
        tail_pos = tail_vals[tail_vals > 0.0]
        fit_pos = fit_vals[fit_vals > 0.0]
        fit_integral = float(np.sum(fit_pos))
        tail_integral = float(np.sum(tail_pos))
        time_rows.append(
            {
                "run": RUN,
                "saved_index": rec["saved_index"],
                "step": rec["step"],
                "total_energy": total,
                "peak_k": peak_k,
                "peak_mask_kmin": peak_k - 1,
                "peak_mask_kmax": peak_k + 1,
                "peak_energy": peak,
                "residual_energy": residual_energy,
                "midrange_energy": mid,
                "high_k_energy": high,
                "peak_fraction": peak / total if total > 0.0 else np.nan,
                "midrange_fraction": mid / total if total > 0.0 else np.nan,
                "high_k_fraction": high / total if total > 0.0 else np.nan,
                "masked_slope": slope,
                "masked_r_squared": r2,
                "fit_points": nfit,
                "compensated_mean": comp_mean,
                "compensated_std": comp_std,
                "compensated_cv": comp_cv,
                "plateau_width": width,
                "fit_min_E": float(np.min(fit_pos)) if len(fit_pos) else np.nan,
                "fit_median_E": float(np.median(fit_pos)) if len(fit_pos) else np.nan,
                "fit_max_E": float(np.max(fit_pos)) if len(fit_pos) else np.nan,
                "tail_median_E": float(np.median(tail_pos)) if len(tail_pos) else np.nan,
                "min_positive_E": float(np.min(pos)) if len(pos) else np.nan,
                "fit_to_tail_median_ratio": (
                    float(np.median(fit_pos) / np.median(tail_pos))
                    if len(fit_pos) and len(tail_pos) and np.median(tail_pos) > 0.0
                    else np.nan
                ),
                "fit_to_min_positive_ratio": (
                    float(np.median(fit_pos) / np.min(pos)) if len(fit_pos) and len(pos) else np.nan
                ),
                "fit_integrated_to_tail_integrated_ratio": (
                    fit_integral / tail_integral if tail_integral > 0.0 else np.nan
                ),
                "eps_max_E": float(np.finfo(float).eps * np.max(spec)) if len(spec) else np.nan,
            }
        )

    write_csv(
        ANALYSIS_DIR / "forcing_m3_time_series.csv",
        time_rows,
        list(time_rows[0].keys()),
    )

    # Stationarity windows.
    by_index = {row["saved_index"]: row for row in time_rows}
    stationarity_rows = []
    indices = [row["saved_index"] for row in time_rows]
    for length in (5, 6, 7, 8):
        for start in range(min(indices), max(indices) - length + 2):
            idxs = list(range(start, start + length))
            if any(idx not in by_index for idx in idxs):
                continue
            rows = [by_index[idx] for idx in idxs]
            slopes = np.array([r["masked_slope"] for r in rows], dtype=float)
            r2s = np.array([r["masked_r_squared"] for r in rows], dtype=float)
            cvs = np.array([r["compensated_cv"] for r in rows], dtype=float)
            totals = np.array([r["total_energy"] for r in rows], dtype=float)
            residuals = np.array([r["residual_energy"] for r in rows], dtype=float)
            valid = np.isfinite(slopes) & np.isfinite(r2s) & np.isfinite(cvs)
            if np.count_nonzero(valid) < 3:
                continue
            mean_slope = float(np.mean(slopes[valid]))
            slope_std = float(np.std(slopes[valid]))
            mean_r2 = float(np.mean(r2s[valid]))
            mean_cv = float(np.mean(cvs[valid]))
            score = (
                abs(mean_slope + 3.0)
                + 1.25 * slope_std
                + 1.5 * max(0.0, 1.0 - mean_r2)
                + 0.35 * mean_cv
                + 0.02 * abs(pct_change(totals[0], totals[-1]))
            )
            stationarity_rows.append(
                {
                    "run": RUN,
                    "start_index": start,
                    "end_index": start + length - 1,
                    "n_snapshots": length,
                    "start_step": start * SAVE_EVERY,
                    "end_step": (start + length - 1) * SAVE_EVERY,
                    "score": score,
                    "mean_slope": mean_slope,
                    "slope_std": slope_std,
                    "mean_r2": mean_r2,
                    "mean_cv": mean_cv,
                    "cv_std": float(np.std(cvs[valid])),
                    "mean_plateau_width": float(np.mean([r["plateau_width"] for r in rows])),
                    "slope_drift_per_index": linear_regression(idxs, slopes),
                    "cv_drift_per_index": linear_regression(idxs, cvs),
                    "peak_fraction_mean": float(np.mean([r["peak_fraction"] for r in rows])),
                    "midrange_fraction_mean": float(np.mean([r["midrange_fraction"] for r in rows])),
                    "high_k_fraction_mean": float(np.mean([r["high_k_fraction"] for r in rows])),
                    "total_energy_start": float(totals[0]),
                    "total_energy_end": float(totals[-1]),
                    "total_energy_pct_change": pct_change(totals[0], totals[-1]),
                    "residual_energy_start": float(residuals[0]),
                    "residual_energy_end": float(residuals[-1]),
                    "residual_energy_pct_change": pct_change(residuals[0], residuals[-1]),
                }
            )

    stationarity_rows.sort(key=lambda row: row["score"])
    write_csv(
        ANALYSIS_DIR / "forcing_m3_stationarity_windows.csv",
        stationarity_rows,
        list(stationarity_rows[0].keys()),
    )
    best = stationarity_rows[0]
    best_indices = list(range(int(best["start_index"]), int(best["end_index"]) + 1))
    best_records = [records[idx] for idx in best_indices]
    best_mean_spec = np.mean([r["spectrum"] for r in best_records], axis=0)
    best_norm, _ = normalized_residual_spectrum(best_mean_spec, peak_mask)

    budget_rows = [by_index[idx] for idx in best_indices]
    budget_summary = {
        "run": RUN,
        "start_index": best_indices[0],
        "end_index": best_indices[-1],
        "start_step": best_indices[0] * SAVE_EVERY,
        "end_step": best_indices[-1] * SAVE_EVERY,
        "total_energy_pct_change": pct_change(budget_rows[0]["total_energy"], budget_rows[-1]["total_energy"]),
        "peak_energy_pct_change": pct_change(budget_rows[0]["peak_energy"], budget_rows[-1]["peak_energy"]),
        "residual_energy_pct_change": pct_change(
            budget_rows[0]["residual_energy"], budget_rows[-1]["residual_energy"]
        ),
        "midrange_energy_pct_change": pct_change(
            budget_rows[0]["midrange_energy"], budget_rows[-1]["midrange_energy"]
        ),
        "high_k_energy_pct_change": pct_change(budget_rows[0]["high_k_energy"], budget_rows[-1]["high_k_energy"]),
        "mean_slope": best["mean_slope"],
        "slope_std": best["slope_std"],
        "mean_r2": best["mean_r2"],
        "mean_cv": best["mean_cv"],
    }
    write_csv(ANALYSIS_DIR / "forcing_m3_window_budget.csv", [budget_summary], list(budget_summary.keys()))

    # Window sensitivity around the best window.
    fit_ranges = [(8, 40), (9, 41), (10, 42), (9, 35), (12, 40)]
    base_start = int(best["start_index"])
    base_end = int(best["end_index"])
    candidate_windows = []
    for offset in (-2, -1, 0, 1, 2):
        s = base_start + offset
        e = base_end + offset
        if s >= min(indices) and e <= max(indices):
            candidate_windows.append((s, e))
    for s, e in ((base_start - 2, base_end), (base_start - 1, base_end + 1), (base_start, base_end + 2)):
        if s >= min(indices) and e <= max(indices):
            candidate_windows.append((s, e))
    candidate_windows = sorted(set(candidate_windows))

    sens_rows = []
    for s, e in candidate_windows:
        spec = np.mean([records[idx]["spectrum"] for idx in range(s, e + 1)], axis=0)
        norm, _ = normalized_residual_spectrum(spec, peak_mask)
        for kmin, kmax in fit_ranges:
            mask = (bins >= kmin) & (bins < kmax)
            slope, r2, points = fit_loglog(bins[mask], norm[mask])
            _, _, cv, width = compensated_cv(bins, norm, mask)
            sens_rows.append(
                {
                    "window": f"{s}:{e}",
                    "start_index": s,
                    "end_index": e,
                    "window_length": e - s + 1,
                    "fit_range": f"k={kmin}:{kmax}",
                    "fit_kmin": kmin,
                    "fit_kmax": kmax,
                    "fit_width": kmax - kmin,
                    "slope": slope,
                    "r_squared": r2,
                    "compensated_cv": cv,
                    "plateau_width": width,
                    "abs_slope_plus_3": abs(slope + 3.0) if np.isfinite(slope) else np.nan,
                    "fit_points": points,
                }
            )
    write_csv(ANALYSIS_DIR / "forcing_m3_window_sensitivity.csv", sens_rows, list(sens_rows[0].keys()))

    slopes = np.array([r["slope"] for r in sens_rows], dtype=float)
    r2s = np.array([r["r_squared"] for r in sens_rows], dtype=float)
    cvs = np.array([r["compensated_cv"] for r in sens_rows], dtype=float)
    valid = np.isfinite(slopes)
    high_quality = valid & (r2s >= 0.95) & (cvs <= 0.30)
    near_three = valid & (np.abs(slopes + 3.0) <= 0.25)

    def stat_rows(label, mask):
        vals = slopes[mask]
        if len(vals) == 0:
            return {
                "ensemble": label,
                "count": 0,
                "mean": np.nan,
                "median": np.nan,
                "std": np.nan,
                "min": np.nan,
                "max": np.nan,
                "p10": np.nan,
                "p90": np.nan,
            }
        return {
            "ensemble": label,
            "count": int(len(vals)),
            "mean": float(np.mean(vals)),
            "median": float(np.median(vals)),
            "std": float(np.std(vals)),
            "min": float(np.min(vals)),
            "max": float(np.max(vals)),
            "p10": float(np.percentile(vals, 10)),
            "p90": float(np.percentile(vals, 90)),
        }

    uncertainty_rows = [
        stat_rows("all", valid),
        stat_rows("high_quality_r2_ge_0.95_cv_le_0.30", high_quality),
        stat_rows("near_three_abs_le_0.25", near_three),
    ]
    write_csv(
        ANALYSIS_DIR / "forcing_m3_residual_exponent_uncertainty.csv",
        uncertainty_rows,
        list(uncertainty_rows[0].keys()),
    )

    # Shell support and shell mean comparison.
    count_rows = shell_counts(N)
    count_map = {row["k"]: row["mode_count"] for row in count_rows}
    shell_rows = []
    for kb, val in zip(bins, best_mean_spec):
        count = count_map.get(int(kb), 0)
        shell_rows.append(
            {
                "k": int(kb),
                "mode_count": count,
                "shell_sum_E": float(val),
                "shell_mean_E": float(val / count) if count > 0 else np.nan,
                "in_fit_range": bool(FIT_KMIN <= kb < FIT_KMAX),
            }
        )
    fit_counts = [row["mode_count"] for row in shell_rows if row["in_fit_range"]]
    shell_sum_slope, shell_sum_r2, _ = fit_loglog(bins[fit_mask], best_mean_spec[fit_mask])
    shell_mean = np.array([row["shell_mean_E"] for row in shell_rows], dtype=float)
    shell_mean_slope, shell_mean_r2, _ = fit_loglog(bins[fit_mask], shell_mean[fit_mask])
    write_csv(ANALYSIS_DIR / "forcing_m3_shell_support.csv", shell_rows, list(shell_rows[0].keys()))

    # Leave-one-shell-out on window-averaged normalized residual spectrum.
    baseline_slope, baseline_r2, _ = fit_loglog(bins[fit_mask], best_norm[fit_mask])
    loo_rows = []
    fit_ks = bins[fit_mask].astype(int)
    for leave_k in fit_ks:
        loo_mask = fit_mask & (bins != leave_k)
        slope, r2, points = fit_loglog(bins[loo_mask], best_norm[loo_mask])
        loo_rows.append(
            {
                "left_out_k": int(leave_k),
                "baseline_slope": baseline_slope,
                "baseline_r_squared": baseline_r2,
                "loo_slope": slope,
                "loo_r_squared": r2,
                "delta_slope": slope - baseline_slope,
                "delta_r_squared": r2 - baseline_r2,
                "fit_points": points,
                "within_minus3_pm_0.15": bool(-3.15 <= slope <= -2.85),
            }
        )
    write_csv(ANALYSIS_DIR / "forcing_m3_leave_one_shell_out.csv", loo_rows, list(loo_rows[0].keys()))

    # Signal floor separate CSV.
    signal_fields = [
        "run",
        "saved_index",
        "step",
        "fit_min_E",
        "fit_median_E",
        "fit_max_E",
        "tail_median_E",
        "min_positive_E",
        "fit_to_tail_median_ratio",
        "fit_to_min_positive_ratio",
        "fit_integrated_to_tail_integrated_ratio",
        "eps_max_E",
    ]
    write_csv(
        ANALYSIS_DIR / "forcing_m3_signal_floor.csv",
        [{key: row[key] for key in signal_fields} for row in time_rows],
        signal_fields,
    )

    # Comparison summary.
    run004_stationarity = read_metric_csv(Path("stationarity_window_summary.csv"))
    f006 = read_metric_csv(
        Path("outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_validation_summary.csv"),
        "forcing_f006",
    )
    alpha020 = read_metric_csv(
        Path("outputs_lowk_drag_production/analysis/lowk_production_validation_summary.csv"),
        "lowk_drag",
    )
    run004_from_f006 = read_metric_csv(
        Path("outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_validation_summary.csv"),
        "run004",
    )

    final = time_rows[-1]
    final_total = final["total_energy"]
    final_peak = final["peak_energy"]
    run004_total = float(run004_from_f006.get("final_total_energy", "nan"))
    alpha020_total = float(alpha020.get("final_total_energy", "nan"))
    f006_total = float(f006.get("final_total_energy", "nan"))
    loo_slopes = np.array([r["loo_slope"] for r in loo_rows], dtype=float)
    loo_r2s = np.array([r["loo_r_squared"] for r in loo_rows], dtype=float)
    summary_pairs = [
        ("final_total_energy", final_total),
        ("final_peak_energy", final_peak),
        ("final_peak_fraction", final["peak_fraction"]),
        ("final_midrange_fraction", final["midrange_fraction"]),
        ("peak_k", peak_k),
        ("peak_mask_kmin", peak_k - 1),
        ("peak_mask_kmax", peak_k + 1),
        ("best_window_start_index", best["start_index"]),
        ("best_window_end_index", best["end_index"]),
        ("best_window_mean_slope", best["mean_slope"]),
        ("best_window_mean_r_squared", best["mean_r2"]),
        ("best_window_mean_cv", best["mean_cv"]),
        ("best_window_total_energy_pct_change", budget_summary["total_energy_pct_change"]),
        ("sensitivity_mean_slope_all", uncertainty_rows[0]["mean"]),
        ("sensitivity_std_slope_all", uncertainty_rows[0]["std"]),
        ("sensitivity_p10_slope_all", uncertainty_rows[0]["p10"]),
        ("sensitivity_p90_slope_all", uncertainty_rows[0]["p90"]),
        ("signal_floor_final_fit_to_tail", final["fit_to_tail_median_ratio"]),
        ("shell_support_min_count_fit_range", int(np.min(fit_counts))),
        ("shell_support_median_count_fit_range", float(np.median(fit_counts))),
        ("shell_sum_slope_best_window", shell_sum_slope),
        ("shell_sum_r_squared_best_window", shell_sum_r2),
        ("shell_mean_slope_best_window", shell_mean_slope),
        ("shell_mean_r_squared_best_window", shell_mean_r2),
        ("loo_slope_min", float(np.min(loo_slopes))),
        ("loo_slope_max", float(np.max(loo_slopes))),
        ("loo_min_r_squared", float(np.min(loo_r2s))),
        ("loo_max_abs_delta_slope", float(np.max(np.abs(loo_slopes - baseline_slope)))),
    ]

    summary_rows = []
    for metric, value in summary_pairs:
        row = {
            "metric": metric,
            "forcing_m3": value,
            "run004": run004_from_f006.get(metric, ""),
            "forcing_f006": f006.get(metric, ""),
            "alpha020_k4": alpha020.get(metric, ""),
            "ratio_m3_to_run004": "",
            "ratio_m3_to_f006": "",
            "ratio_m3_to_alpha020_k4": "",
        }
        if metric in ("final_total_energy", "final_peak_energy"):
            row["ratio_m3_to_run004"] = value / run004_total if run004_total > 0.0 else ""
            row["ratio_m3_to_f006"] = value / f006_total if f006_total > 0.0 else ""
            row["ratio_m3_to_alpha020_k4"] = value / alpha020_total if alpha020_total > 0.0 else ""
        summary_rows.append(row)
    write_csv(ANALYSIS_DIR / "forcing_m3_validation_summary.csv", summary_rows, list(summary_rows[0].keys()))

    # Plots.
    steps = np.array([row["step"] for row in time_rows], dtype=float)
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_energy.png",
        [
            ("total", steps, [row["total_energy"] for row in time_rows]),
            ("peak", steps, [row["peak_energy"] for row in time_rows]),
            ("residual", steps, [row["residual_energy"] for row in time_rows]),
            ("midrange", steps, [row["midrange_energy"] for row in time_rows]),
            ("high-k", steps, [row["high_k_energy"] for row in time_rows]),
        ],
        "Forcing m=3 energy proxies",
        "step",
        "energy proxy",
        logy=True,
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_partitions.png",
        [
            ("peak/total", steps, [row["peak_fraction"] for row in time_rows]),
            ("midrange/total", steps, [row["midrange_fraction"] for row in time_rows]),
            ("high-k/total", steps, [row["high_k_fraction"] for row in time_rows]),
        ],
        "Forcing m=3 energy fractions",
        "step",
        "fraction",
        logy=True,
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_residual_slopes.png",
        [
            ("slope", steps, [row["masked_slope"] for row in time_rows]),
            ("R^2", steps, [row["masked_r_squared"] for row in time_rows]),
        ],
        "Forcing m=3 residual slope and R^2",
        "step",
        "value",
        hlines=[(-3.0, "-3", (120, 120, 120))],
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_compensated.png",
        [("best-window mean", bins[fit_mask], (bins[fit_mask] ** 3) * best_norm[fit_mask])],
        "Forcing m=3 compensated k^3 E(k)",
        "k",
        "k^3 normalized E(k)",
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_stationarity_window_spectrum.png",
        [("best-window residual", bins[~peak_mask], best_norm[~peak_mask])],
        "Forcing m=3 peak-masked normalized spectrum",
        "k",
        "normalized residual E(k)",
        logy=True,
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_stationarity_window_compensated.png",
        [("best-window compensated", bins[fit_mask], (bins[fit_mask] ** 3) * best_norm[fit_mask])],
        "Forcing m=3 stationarity-window compensated spectrum",
        "k",
        "k^3 normalized E(k)",
    )
    draw_heatmap(
        ANALYSIS_DIR / "forcing_m3_window_sensitivity_slope.png",
        sens_rows,
        "window",
        "fit_range",
        "slope",
        "Window sensitivity: slope",
    )
    draw_heatmap(
        ANALYSIS_DIR / "forcing_m3_window_sensitivity_r2.png",
        sens_rows,
        "window",
        "fit_range",
        "r_squared",
        "Window sensitivity: R^2",
    )
    draw_heatmap(
        ANALYSIS_DIR / "forcing_m3_window_sensitivity_cv.png",
        sens_rows,
        "window",
        "fit_range",
        "compensated_cv",
        "Window sensitivity: compensated CV",
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_residual_exponent_uncertainty.png",
        [("sensitivity slopes", np.arange(len(slopes[valid])), slopes[valid])],
        "Forcing m=3 residual exponent sensitivity ensemble",
        "combination",
        "slope",
        hlines=[(-3.0, "-3", (120, 120, 120))],
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_signal_floor.png",
        [
            ("fit/tail median", steps, [row["fit_to_tail_median_ratio"] for row in time_rows]),
            ("fit/min positive", steps, [row["fit_to_min_positive_ratio"] for row in time_rows]),
        ],
        "Forcing m=3 signal-floor ratios",
        "step",
        "ratio",
        logy=True,
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_shell_support.png",
        [
            ("mode count", [row["k"] for row in shell_rows], [row["mode_count"] for row in shell_rows]),
            ("shell sum E", [row["k"] for row in shell_rows], [row["shell_sum_E"] for row in shell_rows]),
            ("shell mean E", [row["k"] for row in shell_rows], [row["shell_mean_E"] for row in shell_rows]),
        ],
        "Forcing m=3 shell support and spectra",
        "k",
        "count / spectrum",
        logy=True,
    )
    draw_plot(
        ANALYSIS_DIR / "forcing_m3_leave_one_shell_out.png",
        [
            ("delta slope", [row["left_out_k"] for row in loo_rows], [row["delta_slope"] for row in loo_rows]),
            ("delta R^2", [row["left_out_k"] for row in loo_rows], [row["delta_r_squared"] for row in loo_rows]),
        ],
        "Forcing m=3 leave-one-shell-out influence",
        "left-out k",
        "delta",
        hlines=[(0.0, "0", (120, 120, 120))],
    )

    print(
        "Analysis complete: "
        f"peak_k={peak_k}, mask={peak_k - 1}:{peak_k + 1}, "
        f"best_window={best['start_index']}:{best['end_index']}, "
        f"slope={best['mean_slope']:.4f}, r2={best['mean_r2']:.4f}, cv={best['mean_cv']:.4f}, "
        f"final_total_ratio_to_run004={final_total / run004_total:.4f}, "
        f"final_total_ratio_to_f006={final_total / f006_total:.4f}, "
        f"final_total_ratio_to_alpha020={final_total / alpha020_total:.4f}"
    )


if __name__ == "__main__":
    main()
