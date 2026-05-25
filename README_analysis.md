# Analysis Comparison Tool README

## 1. Purpose

`compare_validated_runs.py` consolidates already-generated validation metrics for the current validated comparison set:

- Run 004
- Run 009
- Run 011
- Run 012
- Run 013

The script reads existing validation artifacts and produces a compact comparison table and tradeoff plot. It does not run simulations and does not change scientific claims.

## 2. How To Run

Expected working directory: project root.

Run:

```bash
python compare_validated_runs.py
```

The script assumes root-relative paths. Run it from the project root unless the script is later refactored for configurable paths.

## 3. Required Source Files

Primary source file:

- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_validation_summary.csv`

Run 004 fallback/source files used by the script:

- `residual_signal_floor_summary.csv`
- `leave_one_shell_out_summary.csv`

The primary combined validation summary contains the comparison metrics for Runs 004, 009, 011, 012, and 013 where available. The fallback files fill Run 004 signal-floor and leave-one-shell-out values when those values are not present in the primary table.

## 4. Outputs Generated

Running `compare_validated_runs.py` writes:

- `validated_run_comparison.csv`
- `validated_run_comparison.md`
- `validated_run_tradeoff_plot.png`

These are curated comparison artifacts for the current checkpoint.

## 5. Tradeoff Plot Interpretation

`validated_run_tradeoff_plot.png` compares stationarity behavior against residual spectral shape quality.

| Plot element | Meaning |
|---|---|
| x-axis | Best-window total energy growth |
| y-axis | Compensated CV |
| Lower x | Better stationarity behavior in the selected window |
| Lower y | Flatter compensated spectrum |
| Run labels | Case identifiers for the validated comparison set |
| R^2 annotations | Fit-quality reference values for each point |

The plot is a comparison aid, not a standalone physical conclusion.

## 6. Scientific Caveats

This tool summarizes residual-spectrum validation artifacts.

It does not prove a fully stationary enstrophy cascade.

Peak domination remains severe in the documented cases.

The residual `k^-3`-like shape should be interpreted separately from full-system stationarity.

## 7. Current Interpretation

| Case | Current interpretation |
|---|---|
| Run 004 | Cleanest residual spectral reference. |
| Run 009 | Cleanest `m=3` no-drag forcing case. |
| Run 011 | Strongest stationarity-control combined case. |
| Run 013 | Current best balanced combined-strategy case. |

These interpretations are checkpoint summaries based on existing validation artifacts and should not be strengthened beyond the documented evidence.

## 8. Git / Artifact Policy

The comparison script and curated comparison outputs are intended to be tracked:

- `compare_validated_runs.py`
- `validated_run_comparison.csv`
- `validated_run_comparison.md`
- `validated_run_tradeoff_plot.png`

Raw `outputs_*` folders are ignored and should not be committed as normal Git files.

Broad root diagnostic CSV/PNG dumps are local/generated artifacts unless specifically curated in a later analysis-output package.

Future cleanup should preserve existing report links until path changes are deliberately planned and verified.
