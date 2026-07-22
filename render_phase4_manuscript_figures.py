#!/usr/bin/env python3
"""Assemble the three frozen Phase 4 manuscript figures.

``inspect`` is a read-only, standard-library-only repository-bound inspection.
``render`` reads archived PNG/CSV/JSON evidence and writes presentation artwork.
It never imports project modules, constructs a solver, advances a state, refits
an exponent, or changes a scientific decision.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


CHECKPOINT = "9b1b4eb981982178815bf6387e9edd2e8a1182b5"
MANIFEST = "MANUSCRIPT_FIGURE_SELECTION.md"
MANIFEST_SHA256 = "8A31CD71EC459EEDB000E1C7E31D03332B5BF9F2F1E490C90D69C7B6E6BE1338"
DEFAULT_STAGE_E = Path(
    "experiments/focused_refinement_study/"
    "stage_e_focused_refinement_20260721T074126Z_8ab70dc"
)
DEFAULT_OUTPUT = Path("manuscript_figures/phase4_checkpoint_9b1b4eb_qa_revision1")

ROOT_INPUTS = {
    "residual_signal_floor_spectrum.png":
        "0B79C5F3871C3DB41512C8D3F4CC58FD5117F99C7F5CCDACBB1692C390B4065A",
    "stationarity_window_compensated.png":
        "F68285DE9135A2064559207A6E9BB97C07A9381A2C38E2EA29653CD441C26652",
    "window_local_residual_budget.csv":
        "D8E6ABF36EE1CD3EADE7AEAF6FF701875041B354D2C80795C34AD654EC6E5CA9",
    "validated_run_comparison.csv":
        "12417EDBB4F4F7AE02795061270766A98A584EDD80FBE84618E742617F955D64",
}

STAGE_E_INPUTS = {
    "within_case_pairwise.csv":
        "C1FAF0B7033CC5CD808EEC4B313F81308654E11D800FCD3C7A1BF123BBA13374",
    "stage_e_summary.json":
        "EA3DBD9B0A8406ED2AD44E926139CC06895FDFC42155A4E98B1102DB3F47A93E",
}

FIGURE_BASENAMES = (
    "figure_1_run004_residual_spectral_diagnostics",
    "figure_2_production_limitation_and_tradeoff",
    "figure_3_stage_e_grid_contraction_and_resolution",
)

OUTPUT_NAMES = tuple(
    f"{base}.{suffix}"
    for base in FIGURE_BASENAMES
    for suffix in ("png", "pdf")
) + (
    "manuscript_figure_captions.md",
    "manuscript_figure_inventory.csv",
)

TRAJECTORY_LABELS = {
    "TRAJ_BASE_FD_ADVECTIVE_V1": "FD-A",
    "TRAJ_FD_CONSERVATIVE_V1": "FD-C",
    "TRAJ_FD_SKEW_V1": "FD-S",
    "TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2": "PS-A",
    "TRAJ_ARAKAWA_V1": "Arakawa",
}

CAPTIONS = """# Phase 4 manuscript figure captions

Source checkpoint: `9b1b4eb981982178815bf6387e9edd2e8a1182b5`.

## Figure 1

**Selected-window residual spectral diagnostics for Run 004.** (a)
Peak-masked window-mean spectrum over saved indices 38--43 (steps
38,000--43,000). Markers identify the fitted shells `k=9:41`, the reference
line shows the fitted exponent near `-3`, and the recorded floor estimates
remain well below the fitted values. The forcing-scale band `k=2:4` is
excluded. (b) The corresponding normalized compensation, `k^3 E_norm(k)`,
shows limited plateau-like behavior over the same interval. These panels
establish a residual spectral resemblance in a selected window; they do not
establish stationarity, an inertial range, or an enstrophy cascade.

## Figure 2

**Physical limitation and growth--shape tradeoff in the archived production
comparison.** (a) Independently normalized Run 004 total and masked peak-band
energies continue to grow through the selected analysis window, while the
residual decreases slightly. The annotation, rather than vertical separation
of the normalized curves, records the near-unity peak-band fraction at step
43,000. (b)
Across the five documented cases, stronger low-wavenumber control reduces
selected-window growth but generally increases compensated-spectrum
variation. Run 011 has the lowest selected-window growth among the listed
combined cases, while Run 013 is a descriptive compromise. The comparison
identifies neither a stationary case nor a universally optimal configuration.

## Figure 3

**Grid contraction and unresolved operator-pair differences in the separate
Stage E smooth problem.** (a) Every final-time pairwise separation decreases
with grid refinement; at `N=144`, the ten separations are approximately
`0.1987--0.2015` of their `N=64` values. (b) Nevertheless, all final
uncertainty-to-separation ratios exceed the frozen resolution threshold of
`0.20` (`1.239--5.154` observed), so none of the ten pairs is resolved. The
finite-grid differences are measurable, but these results establish neither
distinct nor identical continuum limits and do not rank the methods. Stage E
uses a separate smooth, L-shaped refinement problem and is not a refinement
test of Runs 004--013.

Trajectory abbreviations: FD-A, finite-difference advective; FD-C,
finite-difference conservative; FD-S, finite-difference skew-symmetric; PS-A,
pseudo-spectral advective; Arakawa, Arakawa Jacobian trajectory.
"""


class FigureAssemblyError(RuntimeError):
    """Raised when a frozen evidence or presentation gate fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def sha256_canonical_text(path: Path) -> str:
    """Hash text with Git-style LF normalization for Windows portability."""
    content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def require_file(path: Path, expected_sha256: str) -> None:
    if not path.is_file():
        raise FigureAssemblyError(f"required evidence file is missing: {path}")
    observed = sha256_file(path)
    if observed != expected_sha256:
        raise FigureAssemblyError(
            f"evidence identity mismatch for {path.name}: {observed}"
        )


def require_text_file(path: Path, expected_sha256: str) -> None:
    if not path.is_file():
        raise FigureAssemblyError(f"required evidence file is missing: {path}")
    observed = sha256_canonical_text(path)
    if observed != expected_sha256:
        raise FigureAssemblyError(
            f"canonical text identity mismatch for {path.name}: {observed}"
        )


def resolve_paths(
    repo: Path,
    stage_e_argument: Path | None,
    output_argument: Path | None,
) -> tuple[Path, Path, Path]:
    repo = repo.resolve()
    stage_e = stage_e_argument or DEFAULT_STAGE_E
    output = output_argument or DEFAULT_OUTPUT
    if not stage_e.is_absolute():
        stage_e = repo / stage_e
    if not output.is_absolute():
        output = repo / output
    return repo, stage_e.resolve(), output.resolve()


def verify_frozen_inputs(repo: Path, stage_e: Path) -> None:
    require_text_file(repo / MANIFEST, MANIFEST_SHA256)
    for name, expected in ROOT_INPUTS.items():
        if Path(name).suffix == ".csv":
            require_text_file(repo / name, expected)
        else:
            require_file(repo / name, expected)
    for name, expected in STAGE_E_INPUTS.items():
        require_file(stage_e / name, expected)


def inspect_source(source_path: Path) -> None:
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=source_path.name)

    standard_roots = {
        "__future__", "argparse", "ast", "csv", "hashlib", "json", "math",
        "sys", "pathlib", "typing",
    }
    render_roots = {"matplotlib", "PIL"}
    imported_roots: set[str] = set()
    external_import_lines: list[int] = []
    parent: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    for node in ast.walk(tree):
        roots: list[str] = []
        if isinstance(node, ast.Import):
            roots = [alias.name.split(".", 1)[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots = [node.module.split(".", 1)[0]]
        if not roots:
            continue
        imported_roots.update(roots)
        unknown = set(roots) - standard_roots - render_roots
        if unknown:
            raise FigureAssemblyError(
                f"unapproved import(s) at line {node.lineno}: {sorted(unknown)}"
            )
        if set(roots) & render_roots:
            cursor: ast.AST | None = node
            while cursor is not None and not isinstance(
                cursor, (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                cursor = parent.get(cursor)
            if cursor is None:
                external_import_lines.append(node.lineno)

    if external_import_lines:
        raise FigureAssemblyError(
            "plotting/image imports must remain inside render functions: "
            f"{external_import_lines}"
        )
    if imported_roots & {"project", "solver", "numpy", "scipy"}:
        raise FigureAssemblyError("project or numerical-solver import detected")

    assignments = {
        target.id: node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    if "OUTPUT_NAMES" not in assignments:
        raise FigureAssemblyError("frozen output registry is absent")
    if len(OUTPUT_NAMES) != 8 or len(set(OUTPUT_NAMES)) != 8:
        raise FigureAssemblyError("expected exactly eight unique outputs")

    banned_tokens = (
        "Spectral" + "Solver",
        "solver" + ".run",
        "execute_" + "pilot",
        "solve_" + "ivp",
        "curve_" + "fit",
        "poly" + "fit",
    )
    present = [token for token in banned_tokens if token in source]
    if present:
        raise FigureAssemblyError(f"banned execution/fitting token(s): {present}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def finite_float(text: str, field: str) -> float:
    try:
        value = float(text)
    except (TypeError, ValueError) as exc:
        raise FigureAssemblyError(f"invalid numeric field {field}: {text!r}") from exc
    if not math.isfinite(value):
        raise FigureAssemblyError(f"non-finite numeric field {field}: {text!r}")
    return value


def read_production_evidence(
    repo: Path,
) -> tuple[list[dict[str, float]], list[dict[str, float | str]]]:
    budget_raw = read_csv(repo / "window_local_residual_budget.csv")
    budget: list[dict[str, float]] = []
    for row in budget_raw:
        if not row["saved_index"].isdigit():
            continue
        budget.append({
            "saved_index": finite_float(row["saved_index"], "saved_index"),
            "step": finite_float(row["step"], "step"),
            "total": finite_float(row["total_energy"], "total_energy"),
            "peak": finite_float(row["peak_energy"], "peak_energy"),
            "residual": finite_float(row["residual_energy"], "residual_energy"),
        })
    if [int(row["saved_index"]) for row in budget] != list(range(38, 44)):
        raise FigureAssemblyError("Run 004 budget must contain indices 38--43")
    if any(
        row[field] <= 0.0
        for row in budget
        for field in ("total", "peak", "residual")
    ):
        raise FigureAssemblyError("Run 004 plotted energy fields must be positive")

    comparison_raw = read_csv(repo / "validated_run_comparison.csv")
    comparison: list[dict[str, float | str]] = []
    for row in comparison_raw:
        comparison.append({
            "run": row["run_label"],
            "growth": finite_float(
                row["best_window_total_energy_pct_change"], "energy growth"
            ),
            "cv": finite_float(row["best_window_mean_cv"], "compensated CV"),
            "r2": finite_float(row["best_window_mean_r_squared"], "mean R2"),
        })
    expected_runs = ["Run 004", "Run 009", "Run 011", "Run 012", "Run 013"]
    if [row["run"] for row in comparison] != expected_runs:
        raise FigureAssemblyError("five-case production registry mismatch")

    growth = (budget[-1]["total"] / budget[0]["total"] - 1.0) * 100.0
    if abs(growth - 27.91848234316073) > 1.0e-10:
        raise FigureAssemblyError("Run 004 selected-window growth mismatch")
    return budget, comparison


def pair_key(trajectory_a: str, trajectory_b: str) -> tuple[str, str]:
    return trajectory_a, trajectory_b


def pair_label(key: tuple[str, str]) -> str:
    try:
        return f"{TRAJECTORY_LABELS[key[0]]}-{TRAJECTORY_LABELS[key[1]]}"
    except KeyError as exc:
        raise FigureAssemblyError(f"unknown trajectory identifier: {exc.args[0]}")


def read_stage_e_evidence(
    stage_e: Path,
) -> tuple[list[tuple[tuple[str, str], list[float]]], list[tuple[tuple[str, str], float]], float]:
    rows = read_csv(stage_e / "within_case_pairwise.csv")
    case_by_n = {64: "C2_N64_DT00125", 96: "C3_N96_DT00125", 144: "C4_N144_DT00125"}
    values: dict[tuple[str, str], dict[int, float]] = {}
    selected_slots: set[tuple[tuple[str, str], int]] = set()
    for row in rows:
        n_value = finite_float(row["N"], "N")
        if not n_value.is_integer():
            raise FigureAssemblyError(f"non-integral Stage E grid size: {n_value}")
        n = int(n_value)
        if n not in case_by_n or row["case_id"] != case_by_n[n]:
            continue
        time = finite_float(row["physical_time"], "physical_time")
        if abs(time - 15.3) > 1.0e-12:
            continue
        if abs(finite_float(row["dt"], "dt") - 0.00125) > 1.0e-15:
            raise FigureAssemblyError("Stage E final pairwise dt mismatch")
        if row["finite_status"].strip().lower() != "true":
            raise FigureAssemblyError("non-finite Stage E final pairwise record")
        key = pair_key(row["trajectory_a"], row["trajectory_b"])
        slot = (key, n)
        if slot in selected_slots:
            raise FigureAssemblyError(
                f"duplicate Stage E pair/grid record: {pair_label(key)}, N={n}"
            )
        selected_slots.add(slot)
        values.setdefault(key, {})[n] = finite_float(
            row["absolute_mean_free_vorticity_rms_difference"],
            "absolute mean-free vorticity separation",
        )
    if len(values) != 10 or any(set(by_n) != {64, 96, 144} for by_n in values.values()):
        raise FigureAssemblyError("Stage E final pairwise registry must be 10 x 3")

    contraction: list[tuple[tuple[str, str], list[float]]] = []
    for key, by_n in values.items():
        base = by_n[64]
        if base <= 0.0:
            raise FigureAssemblyError(f"non-positive N=64 separation for {pair_label(key)}")
        normalized = [by_n[n] / base for n in (64, 96, 144)]
        if not (normalized[0] > normalized[1] > normalized[2] > 0.0):
            raise FigureAssemblyError(f"non-contracting sequence for {pair_label(key)}")
        contraction.append((key, normalized))

    with (stage_e / "stage_e_summary.json").open("r", encoding="utf-8") as handle:
        summary = json.load(handle)
    records = summary["refinement_and_resolution"]["operator_pair_resolution"]
    if len(records) != 10:
        raise FigureAssemblyError("Stage E summary must contain ten pair decisions")
    ratios: list[tuple[tuple[str, str], float]] = []
    criteria: set[float] = set()
    ratio_keys: set[tuple[str, str]] = set()
    for record in records:
        anchors = [
            candidate
            for candidate in record["anchors"]
            if int(candidate["anchor_index"]) == 6
        ]
        if len(anchors) != 1:
            raise FigureAssemblyError("Stage E final anchor_index=6 is not unique")
        anchor = anchors[0]
        if abs(float(anchor["anchor_time"]) - 15.3) > 1.0e-12:
            raise FigureAssemblyError("Stage E final resolution anchor is not T=15.3")
        if (
            bool(anchor["resolved_at_anchor"])
            or bool(record["final_anchor_resolved"])
            or record["status"] != "UNRESOLVED"
        ):
            raise FigureAssemblyError("frozen Stage E decision unexpectedly resolved")
        key = pair_key(record["trajectory_a"], record["trajectory_b"])
        if key in ratio_keys:
            raise FigureAssemblyError(f"duplicate Stage E resolution pair: {pair_label(key)}")
        ratio_keys.add(key)
        ratio = float(anchor["uncertainty_fraction_of_separation"])
        if not math.isfinite(ratio):
            raise FigureAssemblyError(f"invalid final ratio for {pair_label(key)}")
        separation = float(anchor["c4_common_band_mean_free_separation"])
        uncertainty = float(anchor["combined_discretization_uncertainty"])
        if separation <= 0.0 or not math.isclose(
            ratio, uncertainty / separation, rel_tol=1.0e-12, abs_tol=1.0e-15
        ):
            raise FigureAssemblyError(f"resolution-ratio identity failed for {pair_label(key)}")
        criterion = float(anchor["criterion_fraction"])
        if ratio <= criterion:
            raise FigureAssemblyError(f"unexpected resolved ratio for {pair_label(key)}")
        ratios.append((key, ratio))
        criteria.add(criterion)
    if criteria != {0.2}:
        raise FigureAssemblyError(f"unexpected Stage E resolution criterion: {criteria}")
    if {key for key, _ in contraction} != {key for key, _ in ratios}:
        raise FigureAssemblyError("Stage E pair registries disagree")

    n144 = [sequence[-1] for _, sequence in contraction]
    ratio_values = [ratio for _, ratio in ratios]
    if abs(min(n144) - 0.19865830761464834) > 1.0e-12 or abs(
        max(n144) - 0.20145669695949972
    ) > 1.0e-12:
        raise FigureAssemblyError("Stage E N=144 contraction range changed")
    if abs(min(ratio_values) - 1.2389411016228298) > 1.0e-12 or abs(
        max(ratio_values) - 5.1540831115035255
    ) > 1.0e-12:
        raise FigureAssemblyError("Stage E final uncertainty-ratio range changed")
    return contraction, ratios, 0.2


def configure_matplotlib() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 12.0,
        "axes.labelsize": 13.0,
        "axes.titlesize": 14.0,
        "legend.fontsize": 10.5,
        "xtick.labelsize": 11.5,
        "ytick.labelsize": 11.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    return plt


def save_figure(fig: Any, png: Path, pdf: Path) -> None:
    metadata = {
        "Title": png.stem,
        "Author": "Phase 4 evidence renderer",
        "Subject": f"Archived evidence at checkpoint {CHECKPOINT}",
        "Creator": "render_phase4_manuscript_figures.py",
    }
    fig.savefig(
        png,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Phase 4 evidence renderer"},
    )
    fig.savefig(pdf, bbox_inches="tight", facecolor="white", metadata=metadata)


def add_panel_label(ax: Any, label: str) -> None:
    ax.text(
        -0.16, 1.04, label,
        transform=ax.transAxes,
        ha="left", va="bottom",
        fontsize=15, fontweight="bold",
    )


def render_figure_1(repo: Path, output: Path) -> None:
    from matplotlib import font_manager
    from PIL import Image, ImageDraw, ImageFont

    first = Image.open(repo / "residual_signal_floor_spectrum.png").convert("RGB")
    second = Image.open(repo / "stationarity_window_compensated.png").convert("RGB")
    if first.size != (1785, 1054) or second.size != (1600, 960):
        raise FigureAssemblyError(
            f"Figure 1 source dimensions changed: {first.size}, {second.size}"
        )
    regular_font_path = font_manager.findfont(
        font_manager.FontProperties(family="DejaVu Sans"),
        fallback_to_default=True,
    )
    title_font = ImageFont.truetype(regular_font_path, 30)
    legend_font = ImageFont.truetype(regular_font_path, 22)
    second_draw = ImageDraw.Draw(second)
    second_draw.rectangle((0, 0, second.width, 58), fill="white")
    replacement_title = "Selected analysis window: compensated spectrum"
    title_box = second_draw.textbbox((0, 0), replacement_title, font=title_font)
    title_x = (second.width - (title_box[2] - title_box[0])) // 2
    second_draw.text((title_x, 12), replacement_title, fill="black", font=title_font)
    second_draw.rectangle((208, 748, 630, 784), fill="white")
    second_draw.text(
        (214, 749), "Run 004, indices 38:43", fill="black", font=legend_font
    )

    gap = 28
    width = max(first.width, second.width)
    height = first.height + gap + second.height
    canvas = Image.new("RGB", (width, height), "white")
    first_x = (width - first.width) // 2
    second_x = (width - second.width) // 2
    canvas.paste(first, (first_x, 0))
    canvas.paste(second, (second_x, first.height + gap))

    font_path = font_manager.findfont(
        font_manager.FontProperties(family="DejaVu Sans", weight="bold"),
        fallback_to_default=True,
    )
    font = ImageFont.truetype(font_path, 44)
    draw = ImageDraw.Draw(canvas)
    for label, x, y in (
        ("(a)", first_x + 14, 12),
        ("(b)", second_x + 14, first.height + gap + 12),
    ):
        box = draw.textbbox((x, y), label, font=font)
        draw.rectangle((box[0] - 6, box[1] - 4, box[2] + 6, box[3] + 4), fill="white")
        draw.text((x, y), label, fill="black", font=font)

    base = output / FIGURE_BASENAMES[0]
    canvas.save(base.with_suffix(".png"), format="PNG", optimize=True, dpi=(300, 300))
    plt = configure_matplotlib()
    fig = plt.figure(figsize=(width / 300.0, height / 300.0), dpi=300)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.imshow(canvas)
    ax.axis("off")
    fig.savefig(
        base.with_suffix(".pdf"),
        dpi=300,
        facecolor="white",
        metadata={
            "Title": base.name,
            "Author": "Phase 4 evidence renderer",
            "Subject": f"Archived evidence at checkpoint {CHECKPOINT}",
            "Creator": "render_phase4_manuscript_figures.py",
        },
    )
    plt.close(fig)


def render_figure_2(
    repo: Path,
    output: Path,
    budget: Sequence[dict[str, float]],
    comparison: Sequence[dict[str, float | str]],
) -> None:
    plt = configure_matplotlib()
    palette = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9"]
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12.2, 4.65))

    steps = [row["step"] / 1000.0 for row in budget]
    total0, peak0, residual0 = (
        budget[0]["total"], budget[0]["peak"], budget[0]["residual"]
    )
    ax_a.plot(
        steps, [row["total"] / total0 for row in budget],
        color=palette[0], linewidth=2.8, marker="o", markersize=5,
        label="Total",
    )
    ax_a.plot(
        steps, [row["peak"] / peak0 for row in budget],
        color=palette[1], linewidth=1.8, linestyle="--", marker="s",
        markersize=4, markerfacecolor="white",
        label="Peak band (k=2:4)",
    )
    ax_a.plot(
        steps, [row["residual"] / residual0 for row in budget],
        color=palette[2], linewidth=2.0, marker="^", markersize=5,
        label="Residual",
    )
    ax_a.axhline(1.0, color="0.65", linewidth=0.9, linestyle=":")
    total_growth = (budget[-1]["total"] / total0 - 1.0) * 100.0
    residual_growth = (budget[-1]["residual"] / residual0 - 1.0) * 100.0
    peak_fraction = budget[-1]["peak"] / budget[-1]["total"]
    ax_a.text(
        0.03, 0.74,
        f"Window: total +{total_growth:.2f}%; residual {residual_growth:.2f}%\n"
        f"Peak/total at step 43,000: {peak_fraction:.9f}",
        transform=ax_a.transAxes, fontsize=9.0, va="top",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "0.8"},
    )
    ax_a.set_xlabel("Step (thousands)")
    ax_a.set_ylabel("Energy / value at step 38,000")
    ax_a.set_title("Run 004 selected analysis window")
    ax_a.set_ylim(0.94, 1.30)
    ax_a.grid(True, linewidth=0.5, alpha=0.25)
    ax_a.legend(loc="upper left", frameon=False, fontsize=10.0)
    add_panel_label(ax_a, "(a)")

    offsets = {
        "Run 004": (-30, 8),
        "Run 009": (7, 8),
        "Run 011": (7, 6),
        "Run 012": (7, -13),
        "Run 013": (7, 6),
    }
    for index, row in enumerate(comparison):
        run = str(row["run"])
        growth = float(row["growth"])
        cv = float(row["cv"])
        ax_b.scatter(
            growth, cv, s=58, color=palette[index],
            edgecolor="black", linewidth=0.55, zorder=3,
        )
        ax_b.annotate(
            run, (growth, cv), xytext=offsets[run], textcoords="offset points",
            fontsize=10.5,
        )
    ax_b.annotate(
        "lower growth and lower variation",
        xy=(7.2, 0.239), xytext=(14.0, 0.264),
        arrowprops={"arrowstyle": "->", "color": "0.35", "linewidth": 1.0},
        color="0.30", fontsize=10.0, ha="center",
    )
    ax_b.set_xlabel("Selected-window total-energy growth (%)")
    ax_b.set_ylabel("Compensated-spectrum CV")
    ax_b.set_title("Five-case growth-shape tradeoff")
    ax_b.set_ylim(0.232, 0.306)
    ax_b.grid(True, linewidth=0.5, alpha=0.25)
    add_panel_label(ax_b, "(b)")

    fig.subplots_adjust(wspace=0.30)
    base = output / FIGURE_BASENAMES[1]
    save_figure(fig, base.with_suffix(".png"), base.with_suffix(".pdf"))
    plt.close(fig)


def render_figure_3(
    output: Path,
    contraction: Sequence[tuple[tuple[str, str], list[float]]],
    ratios: Sequence[tuple[tuple[str, str], float]],
    criterion: float,
) -> None:
    plt = configure_matplotlib()
    palette = [
        "#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9",
        "#D55E00", "#332288", "#88CCEE", "#117733", "#AA4499",
    ]
    markers = ["o", "s", "^", "D", "v", "P", "X", "<", ">", "h"]
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(13.0, 5.2), gridspec_kw={"width_ratios": [1.06, 1.0]}
    )

    ordered = sorted(contraction, key=lambda item: pair_label(item[0]))
    for index, (key, normalized) in enumerate(ordered):
        ax_a.plot(
            [64, 96, 144], normalized,
            label=pair_label(key), color=palette[index], linewidth=1.7,
            marker=markers[index], markersize=5.5,
        )
    ax_a.set_xticks([64, 96, 144])
    ax_a.set_xlabel("Grid size N (fixed dt = 0.00125)")
    ax_a.set_ylabel("Mean-free separation / N=64 value")
    ax_a.set_title("Final-time pairwise grid contraction (T = 15.3)")
    ax_a.set_ylim(0.14, 1.06)
    ax_a.grid(True, linewidth=0.5, alpha=0.25)
    ax_a.text(
        0.98, 0.91, "All 10 pair sequences shown",
        transform=ax_a.transAxes, ha="right", va="top", fontsize=10.5,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "0.8"},
    )
    add_panel_label(ax_a, "(a)")

    ratio_map = dict(ratios)
    labels = [pair_label(key) for key, _ in ordered]
    ratio_values = [ratio_map[key] for key, _ in ordered]
    positions = list(range(len(labels)))
    ax_b.barh(
        positions, ratio_values,
        color=[palette[index] for index in range(len(labels))],
        edgecolor="black", linewidth=0.4,
    )
    ax_b.axvline(
        criterion, color="#D55E00", linestyle="--", linewidth=1.7,
        label=f"Resolution threshold = {criterion:.2f}",
    )
    for y, value in zip(positions, ratio_values):
        ax_b.text(value + 0.07, y, f"{value:.3f}", va="center", fontsize=10.0)
    ax_b.set_yticks(positions, labels)
    ax_b.invert_yaxis()
    ax_b.set_xlim(0.0, max(ratio_values) * 1.14)
    ax_b.set_xlabel("Combined discretization uncertainty / separation")
    ax_b.set_title("Frozen final resolution decision: 0 of 10 resolved")
    ax_b.grid(True, axis="x", linewidth=0.5, alpha=0.25)
    ax_b.legend(loc="lower right", frameon=False)
    add_panel_label(ax_b, "(b)")

    fig.subplots_adjust(wspace=0.40, bottom=0.15)
    base = output / FIGURE_BASENAMES[2]
    save_figure(fig, base.with_suffix(".png"), base.with_suffix(".pdf"))
    plt.close(fig)


def write_inventory(output: Path, sources: Iterable[Path]) -> None:
    source_summary = ";".join(
        f"{path.name}:{sha256_file(path)}" for path in sources
    )
    inventory_path = output / "manuscript_figure_inventory.csv"
    with inventory_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow((
            "file", "bytes", "sha256", "source_checkpoint", "source_identities"
        ))
        for name in OUTPUT_NAMES:
            if name == inventory_path.name:
                continue
            path = output / name
            writer.writerow((
                name, path.stat().st_size, sha256_file(path), CHECKPOINT, source_summary
            ))


def render_all(repo: Path, stage_e: Path, output: Path) -> None:
    if output.exists():
        raise FigureAssemblyError(
            f"output path already exists; automatic overwrite is disabled: {output}"
        )
    verify_frozen_inputs(repo, stage_e)
    budget, comparison = read_production_evidence(repo)
    contraction, ratios, criterion = read_stage_e_evidence(stage_e)

    output.mkdir(parents=True, exist_ok=False)
    render_figure_1(repo, output)
    render_figure_2(repo, output, budget, comparison)
    render_figure_3(output, contraction, ratios, criterion)
    (output / "manuscript_figure_captions.md").write_text(CAPTIONS, encoding="utf-8")

    sources = [repo / MANIFEST]
    sources.extend(repo / name for name in ROOT_INPUTS)
    sources.extend(stage_e / name for name in STAGE_E_INPUTS)
    write_inventory(output, sources)

    observed = {path.name for path in output.iterdir() if path.is_file()}
    if observed != set(OUTPUT_NAMES):
        raise FigureAssemblyError(
            f"output inventory mismatch: observed {sorted(observed)}"
        )
    print("\nPHASE 4 MANUSCRIPT FIGURE ASSEMBLY: PASS")
    print(f"Source checkpoint: {CHECKPOINT}")
    print("Figures: 3 PNG + 3 PDF")
    print(f"Captions / inventory: 1 / 1")
    print(f"Output directory: {output}")
    print("Numerical execution: NO")


def run_inspection(repo: Path, stage_e: Path) -> None:
    inspect_source(Path(__file__).resolve())
    verify_frozen_inputs(repo, stage_e)
    budget, comparison = read_production_evidence(repo)
    contraction, ratios, criterion = read_stage_e_evidence(stage_e)
    if len(budget) != 6 or len(comparison) != 5:
        raise FigureAssemblyError("production evidence row contract failed")
    if len(contraction) != 10 or len(ratios) != 10 or criterion != 0.2:
        raise FigureAssemblyError("Stage E evidence contract failed")

    print("\n" + "=" * 72)
    print("PHASE 4 MANUSCRIPT FIGURE RENDERER STATIC INSPECTION: PASS")
    print("=" * 72)
    print(f"File: {Path(__file__).name}")
    print(f"SHA256: {sha256_file(Path(__file__).resolve())}")
    print(f"Figure-selection checkpoint: {CHECKPOINT}")
    print("Frozen evidence identities: 7 VERIFIED")
    print("Figures / outputs: 3 / 8 EXACT")
    print("Production rows: 6 budget / 5 comparison")
    print("Stage E pairs: 10 contraction / 10 resolution")
    print("Plotting/image imports during inspection: NO")
    print("Project imports / solver construction: NO / NO")
    print("Figure rendering / numerical execution / files written: NO / NO / NO")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inspect", "render"))
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).resolve().parent,
        help="repository root (default: renderer directory)",
    )
    parser.add_argument(
        "--stage-e-dir", type=Path,
        help=f"Stage E evidence directory (default: {DEFAULT_STAGE_E})",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        help=f"render destination (default: {DEFAULT_OUTPUT})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo, stage_e, output = resolve_paths(args.repo, args.stage_e_dir, args.output_dir)
    try:
        if args.mode == "inspect":
            run_inspection(repo, stage_e)
        else:
            render_all(repo, stage_e, output)
    except (
        FigureAssemblyError,
        ImportError,
        KeyError,
        OSError,
        ValueError,
        ZeroDivisionError,
    ) as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
