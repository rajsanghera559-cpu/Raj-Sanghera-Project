# Phase 4 Manuscript Figure Selection

## Status and scope

- Controlling documentation checkpoint: `e9d1172bffd8425aa945ae8afd14d14a5ed9e6dd`.
- Purpose: freeze the smallest figure set that communicates the completed
  Phase 4 evidence without strengthening the scientific claims.
- Numerical simulations, solver imports, new fits, and new scientific
  classifications performed during selection: none.
- Current bitmap files are evidence sources and layout references. They are not
  all manuscript-grade final artwork.

## Frozen main-text selection

Three main figures are sufficient. The older seven-figure outline is reduced by
combining closely related panels and moving robustness controls to supplementary
material.

| Figure | Scientific job | Placement | Final-art status |
|---|---|---|---|
| 1. Run 004 residual spectral diagnostics | Show the selected-window residual shape, fitted interval, numerical-floor separation, and corresponding compensation. | After manuscript Section 4.1 | Compose the two existing high-resolution PNG panels; do not regenerate spectral curves from summary statistics. |
| 2. Production limitation and tradeoff | Show continued selected-window energy growth/peak domination alongside the five-case stationarity-versus-shape comparison. | After manuscript Section 4.2 | Re-render as two panels from archived production evidence. |
| 3. Stage E grid contraction and resolution test | Show all ten pairwise separations contracting with grid refinement while remaining unresolved against the declared uncertainty rule. | In manuscript Section 6.5, after the resolution bullets | New two-panel rendering from the archived Stage E CSV/JSON evidence only. |

No validation-chain schematic is needed in the main text; the methodology table
already performs that role more precisely.

## Figure 1: Run 004 residual spectral diagnostics

### Panel specification

- **(a) Residual spectrum and floor check.** Window-mean Run 004 spectrum for
  saved indices `38:43` (steps `38,000:43,000`), with the forcing band `k=2:4`
  visibly excluded, fitted shells `k=9:41` identified, the fitted exponent near
  `-3` shown, and the recorded numerical-floor estimates retained.
- **(b) Compensated spectrum.** The corresponding `k^3 E(k)` spectrum over the
  same selected window and fitted interval. The presentation may emphasize the
  fitted interval, but it must not imply a broad plateau outside that interval.

### Archived sources

| Source | Identity / role |
|---|---|
| `residual_signal_floor_spectrum.png` | `1785x1054`; SHA-256 `0B79C5F3871C3DB41512C8D3F4CC58FD5117F99C7F5CCDACBB1692C390B4065A`; selected final panel and floor-reference source. |
| `stationarity_window_compensated.png` | `1600x960`; SHA-256 `F68285DE9135A2064559207A6E9BB97C07A9381A2C38E2EA29653CD441C26652`; selected final compensated-spectrum panel. |
| `stationarity_window_summary.csv` | Selected-window metrics and energy fractions. |
| `residual_exponent_uncertainty.csv` | Supporting exponent range; supplementary rather than an additional main panel. |

### Draft caption

> **Figure 1. Selected-window residual spectral diagnostics for Run 004.**
> (a) Peak-masked window-mean spectrum over saved indices 38--43 (steps
> 38,000--43,000). Markers identify the fitted shells `k=9:41`, the reference
> line shows the fitted exponent near `-3`, and the recorded floor estimates
> remain well below the fitted values. The forcing-scale band `k=2:4` is
> excluded. (b) The corresponding `k^3 E(k)` compensation shows limited
> plateau-like behavior over the same interval. These panels establish a
> residual spectral resemblance in a selected window; they do not establish
> stationarity, an inertial range, or an enstrophy cascade.

## Figure 2: Production limitation and tradeoff

### Panel specification

- **(a) Selected-window energy behavior.** Re-render the Run 004 total,
  forcing-band peak, and residual energy histories over indices `38:43`, using
  beginning-of-window normalization where needed for legibility. Annotate the
  approximately `+27.92%` total/peak growth and the near-unity peak fraction.
  The panel must make the residual/peak scale separation explicit.
- **(b) Five-case tradeoff.** Plot compensated coefficient of variation against
  selected-window total-energy growth for Runs 004, 009, 011, 012, and 013.
  Use direct, readable labels. Lower values on both axes are descriptively
  favorable, but no optimum or ranking is inferred.

### Archived sources

| Source | Identity / role |
|---|---|
| `window_local_residual_budget.png` | `1760x2080`; SHA-256 `DE5145F370A7CEA0C90EEADDF4868F33E566E764D9A51BAD1EBB13CDD1254C4D`; evidence/layout source, not final artwork. |
| `window_local_residual_budget.csv` | Selected-window total, peak, residual, midrange, and high-wavenumber histories. |
| `validated_run_tradeoff_plot.png` | `1000x700`; SHA-256 `3ECDF8C490FECCA04D51F50511D59C50D4EB119828E46BED81EDF2E49A313962`; comparison reference requiring re-render because of small labels and excess whitespace. |
| `validated_run_comparison.csv` | Authoritative five-case values and interpretation labels. |

### Draft caption

> **Figure 2. Physical limitation and stationarity--shape tradeoff in the
> archived production comparison.** (a) Run 004 total and forcing-band energy
> continue to grow through the selected analysis window, while energy outside
> the forcing band remains a very small fraction of the total. (b) Across the
> five documented cases, stronger low-wavenumber control reduces selected-window
> growth but generally increases compensated-spectrum variation. Run 011 gives
> the strongest stationarity control among the listed combined cases, while Run
> 013 is a descriptive compromise. The comparison identifies neither a
> stationary case nor a universally optimal configuration.

## Figure 3: Stage E grid contraction and resolution test

### Panel specification

- **(a) Pairwise grid contraction.** At `T=15.3` and fixed `dt=0.00125`, show
  all ten operator-pair mean-free vorticity separations across `N=64,96,144`,
  normalized pair-by-pair to the `N=64` value. Plot every pair rather than an
  average. At `N=144`, the normalized values lie approximately in
  `0.1987--0.2015`.
- **(b) Resolution decision.** Show the final combined discretization
  uncertainty divided by pair separation for all ten pairs, with the declared
  threshold `0.20`. The observed range is `1.238941--5.154083`; therefore all
  ten pairs remain unresolved.

### Archived sources

The Stage E evidence package contains no existing figure. The final figure must
be rendered from these immutable records:

| Source | SHA-256 / role |
|---|---|
| `within_case_pairwise.csv` | `C1FAF0B7033CC5CD808EEC4B313F81308654E11D800FCD3C7A1BF123BBA13374`; 10 pairwise sequences across the five cases. |
| `stage_e_summary.json` | `EA3DBD9B0A8406ED2AD44E926139CC06895FDFC42155A4E98B1102DB3F47A93E`; frozen pair-resolution decisions and uncertainty/separation ratios. |
| `refinement_comparisons.csv` | `6A0DD36B8E08579FB5A251B8683F2B1CF302CB3B586C4EFEE87996DC91418E5D`; self-refinement context and numerical-floor fields. |

### Draft caption

> **Figure 3. Grid contraction and unresolved operator-pair differences in the
> separate Stage E smooth problem.** (a) Every final-time pairwise separation
> decreases with grid refinement; at `N=144`, the ten separations are
> approximately `0.1987--0.2015` of their `N=64` values. (b) Nevertheless, all
> final uncertainty-to-separation ratios exceed the frozen resolution threshold
> of `0.20` (`1.239--5.154` observed), so none of the ten pairs is resolved. The
> finite-grid differences are measurable, but these results establish neither
> distinct nor identical continuum limits and do not rank the methods. Stage E
> uses a separate smooth, L-shaped refinement problem and is not a refinement
> test of Runs 004--013.

## Supplementary disposition

| Existing evidence | Disposition |
|---|---|
| `residual_exponent_uncertainty.png` | Supplementary robustness figure. |
| `shell_mode_counts.png` and `shell_sum_vs_shell_mean_spectrum.png` | Supplementary shell-support figure or table. |
| `leave_one_shell_out_slope_change.png` and `leave_one_shell_out_r2_change.png` | Supplementary influence diagnostic. |
| `residual_signal_floor_ratios.png` | Supplementary floor-margin diagnostic. |
| `stationarity_window_diagnostics.png` | Retain as an evidence diagnostic; do not use unchanged in the main text because it is tall, label-dense, and partly redundant with Figures 1--2. |
| Stage E temporal/spatial observed orders | Keep the compact numerical table in the main text; an additional order figure would be redundant. |
| Integrity, ownership, hash, and projection-control records | Reproducibility text, tables, or supplementary evidence; not main scientific figures. |

`peak_masked_normalized_spectra.png`, `stationarity_window_spectrum.png`, and
`residual_signal_floor_spectrum.png` must not all appear as separate manuscript
figures because they repeat the same spectral story. `chi_collapse.png` and
`test.png` are not selected.

## Production-figure provenance limitation

The selected production PNGs and corresponding summary CSVs are Git-tracked,
but the raw Run 004 spectral directory and dedicated generators for several
root diagnostic PNGs are absent from the present repository snapshot. The
files first appear in the available history at commit `6ee8cfb`, whose commit
message does not document their generation. Therefore:

- Figure 1 must use the identified PNG panels directly, with only lossless
  composition, cropping, panel lettering, and captioning;
- its spectral curves must not be reconstructed from aggregate summary values;
- the caption and manifest carry the panel identities and evidence boundary;
  and
- any later full replot requires recovery of the original spectral arrays and
  should be treated as a separate provenance task, not silently approximated.

Figure 2 can be re-rendered faithfully from the preserved root CSV files, and
Figure 3 can be rendered from the archived Stage E CSV/JSON evidence.

## Rendering rules for the next task

- Read archived CSV/JSON evidence only; do not import or construct the solver.
- Do not run timesteps, refit spectral exponents, change windows, change the
  Stage E uncertainty rule, or create new scientific classifications.
- Replace internal trajectory IDs with short labels: `FD-A`, `FD-C`, `FD-S`,
  `PS-A`, and `Arakawa`, defined in the caption or legend.
- Replace “stationarity window” in artwork with “selected analysis window.”
- Use consistent panel lettering, a color-vision-safe palette, distinguishable
  markers, and fonts readable at final manuscript width.
- Produce vector PDF or SVG plus a high-resolution PNG for each final figure.
- Preserve the full-precision source data; formatting and normalization may be
  used only as transparent presentation transformations.
- For Figure 1, retain the archived bitmap panels without curve reconstruction;
  the vector container may embed those raster panels.

## Next controlled task

Create one read-only figure-assembly/plotting script that composes Figure 1 from
the identified PNGs and renders Figures 2--3 from the named archived evidence.
Statically inspect it, then run it once to produce the manuscript artwork. This
is a documentation/visualization task, not a new numerical investigation.
