import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PRIMARY_SUMMARY = Path(
    "outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/"
    "combined_validation_summary.csv"
)
RUN004_SIGNAL_FLOOR = Path("residual_signal_floor_summary.csv")
RUN004_LEAVE_ONE_OUT = Path("leave_one_shell_out_summary.csv")

CSV_OUTPUT = Path("validated_run_comparison.csv")
MD_OUTPUT = Path("validated_run_comparison.md")
PLOT_OUTPUT = Path("validated_run_tradeoff_plot.png")


CASES = [
    {
        "run_label": "Run 004",
        "summary_column": "run004",
        "parameters": "N=256, dt=0.0005, nu=5e-05, f=0.01, m=2, no drag",
        "output_folder": "outputs_spectra_refined/nu_5e-05_f_0.01_m_2",
        "analysis_folder": "root validation artifacts",
        "interpretation_label": "Cleanest residual reference; severe low-k domination.",
    },
    {
        "run_label": "Run 009",
        "summary_column": "forcing_m3_nodrag",
        "parameters": "N=256, dt=0.0005, nu=5e-05, f=0.01, m=3, no drag",
        "output_folder": "outputs_forcing_redesign/f_0.01_m3_nodrag",
        "analysis_folder": "outputs_forcing_redesign/analysis_f_0.01_m3_nodrag",
        "interpretation_label": "Clean m=3 residual shape; weak stationarity.",
    },
    {
        "run_label": "Run 011",
        "summary_column": "combined_m3_lowkdrag010_k5",
        "parameters": (
            "N=256, dt=0.0005, nu=5e-05, f=0.01, m=3, "
            "lowk_drag_alpha=0.10, lowk_drag_kmax=5"
        ),
        "output_folder": "outputs_combined_strategy/f_0.01_m3_lowkdrag_0.10_k5",
        "analysis_folder": "outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5",
        "interpretation_label": (
            "Strongest stationarity control among listed combined cases; "
            "residual quality degraded."
        ),
    },
    {
        "run_label": "Run 012",
        "summary_column": "combined_m3_lowkdrag005_k5",
        "parameters": (
            "N=256, dt=0.0005, nu=5e-05, f=0.01, m=3, "
            "lowk_drag_alpha=0.05, lowk_drag_kmax=5"
        ),
        "output_folder": "outputs_combined_strategy/f_0.01_m3_lowkdrag_0.05_k5",
        "analysis_folder": "outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5",
        "interpretation_label": "Previous best balanced combined-strategy case before Run 013.",
    },
    {
        "run_label": "Run 013",
        "summary_column": "combined_m3_lowkdrag0075_k5",
        "parameters": (
            "N=256, dt=0.0005, nu=5e-05, f=0.01, m=3, "
            "lowk_drag_alpha=0.075, lowk_drag_kmax=5"
        ),
        "output_folder": "outputs_combined_strategy/f_0.01_m3_lowkdrag_0.075_k5",
        "analysis_folder": "outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5",
        "interpretation_label": "Current best balanced combined-strategy case.",
    },
]


METRICS = [
    "final_total_energy",
    "final_peak_fraction",
    "best_window_start_index",
    "best_window_end_index",
    "best_window_mean_slope",
    "best_window_mean_r_squared",
    "best_window_mean_cv",
    "best_window_total_energy_pct_change",
    "signal_floor_final_fit_to_tail",
    "loo_slope_min",
    "loo_slope_max",
    "loo_min_r_squared",
]


def read_metric_table(path):
    table = {}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            metric = row.get("metric")
            if metric:
                table[metric] = row
    return table


def as_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def fmt(value, digits=4):
    number = as_float(value)
    if number is None:
        return ""
    if number == 0:
        return "0"
    if abs(number) >= 1e4 or abs(number) < 1e-3:
        return f"{number:.{digits}e}"
    return f"{number:.{digits}f}"


def get_metric(table, column, metric):
    row = table.get(metric, {})
    return row.get(column, "")


def run004_signal_floor_fallback():
    if not RUN004_SIGNAL_FLOOR.exists():
        return "", False
    best = None
    with RUN004_SIGNAL_FLOOR.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            step = as_float(row.get("step"))
            ratio = row.get("fit_over_tail_median_ratio")
            if step is None or ratio in (None, ""):
                continue
            if best is None or step > best[0]:
                best = (step, ratio)
    if best is None:
        return "", False
    return best[1], True


def run004_loo_min_r2_fallback():
    if not RUN004_LEAVE_ONE_OUT.exists():
        return "", False
    candidates = []
    with RUN004_LEAVE_ONE_OUT.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            value = as_float(row.get("loo_r_squared"))
            if value is not None:
                candidates.append(value)
            summary_value = as_float(row.get("loo_r_squared_min"))
            if summary_value is not None:
                candidates.append(summary_value)
    if not candidates:
        return "", False
    return str(min(candidates)), True


def build_rows():
    primary = read_metric_table(PRIMARY_SUMMARY)
    run004_signal_floor, signal_fallback_used = run004_signal_floor_fallback()
    run004_loo_min_r2, loo_fallback_used = run004_loo_min_r2_fallback()

    run004_total = as_float(get_metric(primary, "run004", "final_total_energy"))
    run009_total = as_float(get_metric(primary, "forcing_m3_nodrag", "final_total_energy"))

    rows = []
    missing = {}
    manual_fields = ["run_label", "parameters", "output_folder", "analysis_folder", "interpretation_label"]

    for case in CASES:
        column = case["summary_column"]
        row = {
            "run_label": case["run_label"],
            "parameters": case["parameters"],
            "output_folder": case["output_folder"],
            "analysis_folder": case["analysis_folder"],
            "interpretation_label": case["interpretation_label"],
        }
        case_missing = []

        for metric in METRICS:
            value = get_metric(primary, column, metric)
            if case["run_label"] == "Run 004" and metric == "signal_floor_final_fit_to_tail" and not value:
                value = run004_signal_floor
            if case["run_label"] == "Run 004" and metric == "loo_min_r_squared" and not value:
                value = run004_loo_min_r2
            row[metric] = value
            if value in (None, ""):
                case_missing.append(metric)

        final_total = as_float(row["final_total_energy"])
        row["final_total_energy_relative_to_run004"] = (
            final_total / run004_total if final_total is not None and run004_total else ""
        )
        row["final_total_energy_relative_to_run009"] = (
            final_total / run009_total if final_total is not None and run009_total else ""
        )

        start = row["best_window_start_index"]
        end = row["best_window_end_index"]
        row["best_window"] = f"{start}:{end}" if start and end else ""
        lo = row["loo_slope_min"]
        hi = row["loo_slope_max"]
        row["leave_one_shell_out_range"] = f"[{fmt(lo)}, {fmt(hi)}]" if lo and hi else ""
        row["missing_fields"] = "; ".join(case_missing)
        if case_missing:
            missing[case["run_label"]] = case_missing
        rows.append(row)

    return rows, missing, signal_fallback_used, loo_fallback_used, manual_fields


def write_comparison_csv(rows):
    fieldnames = [
        "run_label",
        "parameters",
        "output_folder",
        "analysis_folder",
        "best_window",
        "best_window_mean_slope",
        "best_window_mean_r_squared",
        "best_window_mean_cv",
        "best_window_total_energy_pct_change",
        "final_total_energy",
        "final_total_energy_relative_to_run004",
        "final_total_energy_relative_to_run009",
        "final_peak_fraction",
        "leave_one_shell_out_range",
        "loo_min_r_squared",
        "signal_floor_final_fit_to_tail",
        "interpretation_label",
        "missing_fields",
    ]
    with CSV_OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows):
    headers = [
        "Run",
        "Best window",
        "Slope",
        "R^2",
        "CV",
        "Growth %",
        "Final E / Run004",
        "Final E / Run009",
        "Peak fraction",
        "LOO range",
        "Signal floor",
        "Interpretation",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for row in rows:
        values = [
            row["run_label"],
            row["best_window"],
            fmt(row["best_window_mean_slope"]),
            fmt(row["best_window_mean_r_squared"]),
            fmt(row["best_window_mean_cv"]),
            fmt(row["best_window_total_energy_pct_change"], 2),
            fmt(row["final_total_energy_relative_to_run004"]),
            fmt(row["final_total_energy_relative_to_run009"]),
            fmt(row["final_peak_fraction"], 10),
            row["leave_one_shell_out_range"],
            fmt(row["signal_floor_final_fit_to_tail"], 3),
            row["interpretation_label"],
        ]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(rows, missing, signal_fallback_used, manual_fields):
    text = [
        "# Validated Run Comparison",
        "",
        "This file is generated by `compare_validated_runs.py` from existing validation artifacts.",
        "It consolidates documented comparison metrics and does not change scientific claims.",
        "",
        markdown_table(rows),
        "",
        "## Summary",
        "",
        "- Current best balanced case: Run 013.",
        "- Cleanest residual reference: Run 004.",
        "- Strongest stationarity control among listed combined cases: Run 011.",
        "- Caveat: no fully stationary enstrophy cascade is claimed; peak domination remains severe.",
        "- Residual `k^-3`-like shape is not the same as full-system stationarity.",
        "",
        "## Source Files",
        "",
        f"- `{PRIMARY_SUMMARY}`",
        f"- `{RUN004_SIGNAL_FLOOR}` for Run 004 signal-floor fallback",
        f"- `{RUN004_LEAVE_ONE_OUT}` for Run 004 leave-one-out fallback",
        "",
        "## Manual Fields",
        "",
        "The following registry fields are manually defined in the script:",
        "",
        "- " + ", ".join(manual_fields),
        "",
        "Numeric diagnostic values are read from CSV artifacts where available.",
        "",
        "## Missing Fields",
        "",
    ]
    if missing:
        for run_label, fields in missing.items():
            text.append(f"- {run_label}: {', '.join(fields)}")
    else:
        text.append("- None.")
    text.extend(
        [
            "",
            f"Run 004 signal-floor ratio filled from fallback: {'yes' if signal_fallback_used else 'no'}",
        ]
    )
    MD_OUTPUT.write_text("\n".join(text) + "\n")


def draw_tradeoff_plot(rows):
    width, height = 1000, 700
    margin_l, margin_r, margin_t, margin_b = 90, 60, 70, 90
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    points = []
    for row in rows:
        x = as_float(row["best_window_total_energy_pct_change"])
        y = as_float(row["best_window_mean_cv"])
        r2 = as_float(row["best_window_mean_r_squared"])
        if x is not None and y is not None:
            points.append((row["run_label"], x, y, r2))

    if not points:
        draw.text((20, 20), "No plottable data", fill="black", font=font)
        img.save(PLOT_OUTPUT)
        return

    xmin = min(p[1] for p in points)
    xmax = max(p[1] for p in points)
    ymin = min(p[2] for p in points)
    ymax = max(p[2] for p in points)
    xpad = 0.12 * (xmax - xmin if xmax != xmin else 1.0)
    ypad = 0.16 * (ymax - ymin if ymax != ymin else 1.0)
    xmin -= xpad
    xmax += xpad
    ymin -= ypad
    ymax += ypad

    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    def to_xy(x, y):
        px = margin_l + (x - xmin) / (xmax - xmin) * plot_w
        py = margin_t + (ymax - y) / (ymax - ymin) * plot_h
        return px, py

    draw.rectangle([margin_l, margin_t, width - margin_r, height - margin_b], outline="black")
    draw.text((margin_l, 25), "Validated run tradeoff: stationarity growth vs compensated CV", fill="black", font=font)
    draw.text((width // 2 - 110, height - 40), "Best-window total energy growth (%)", fill="black", font=font)
    draw.text((15, height // 2), "Compensated CV", fill="black", font=font)
    draw.text((margin_l, height - margin_b + 10), f"{xmin:.1f}", fill="black", font=font)
    draw.text((width - margin_r - 35, height - margin_b + 10), f"{xmax:.1f}", fill="black", font=font)
    draw.text((25, margin_t), f"{ymax:.3f}", fill="black", font=font)
    draw.text((25, height - margin_b - 8), f"{ymin:.3f}", fill="black", font=font)

    colors = {
        "Run 004": (31, 119, 180),
        "Run 009": (44, 160, 44),
        "Run 011": (214, 39, 40),
        "Run 012": (255, 127, 14),
        "Run 013": (148, 103, 189),
    }
    for label, x, y, r2 in points:
        color = colors.get(label, (80, 80, 80))
        px, py = to_xy(x, y)
        draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=color, outline="black")
        annotation = f"{label} R2={r2:.3f}" if r2 is not None else label
        draw.text((px + 8, py - 8), annotation, fill=color, font=font)

    img.save(PLOT_OUTPUT)


def main():
    if not PRIMARY_SUMMARY.exists():
        raise FileNotFoundError(PRIMARY_SUMMARY)
    rows, missing, signal_fallback_used, loo_fallback_used, manual_fields = build_rows()
    write_comparison_csv(rows)
    write_markdown(rows, missing, signal_fallback_used, manual_fields)
    draw_tradeoff_plot(rows)

    print("Created:")
    print(f"- {CSV_OUTPUT}")
    print(f"- {MD_OUTPUT}")
    print(f"- {PLOT_OUTPUT}")
    print("Missing fields:")
    if missing:
        for run_label, fields in missing.items():
            print(f"- {run_label}: {', '.join(fields)}")
    else:
        print("- none")
    print(f"Run 004 signal-floor ratio filled from fallback: {'yes' if signal_fallback_used else 'no'}")
    print(f"Run 004 leave-one-out min R^2 filled from fallback: {'yes' if loo_fallback_used else 'no'}")
    print("Manual-entry fields: " + ", ".join(manual_fields))


if __name__ == "__main__":
    main()
