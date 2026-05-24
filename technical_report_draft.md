# Technical Report Draft: Residual Spectral Validation and Stationarity Tradeoffs

## 1. Title

Residual `k^-3`-Like Spectral Shape Validation in a 2D Numerical Turbulence Experiment: Checkpoint Report for Runs 004, 009, 011, 012, and 013

## 2. Abstract / Executive Summary

This report summarizes the current documented state of the numerical turbulence experiment pipeline. The project has progressed from individual spectral plots to a structured validation workflow for candidate residual spectral scaling. The strongest supported result remains a residual-spectrum result: Run 004 shows a robust peak-masked residual `k^-3`-like spectral shape over steps `38000-43000`.

The main unresolved caveat is also unchanged. The full system remains strongly low-k/peak dominated, and total/peak energy growth has not been eliminated. Therefore, the documented evidence supports residual spectral-shape validation in selected windows, not a fully stationary enstrophy cascade.

Among the current comparison set, Run 004 is the cleanest residual spectral reference. Run 009 is the cleanest `m=3` no-drag forcing case. Run 011 gives the strongest stationarity control among listed combined cases. Run 013 is the current best balanced combined-strategy case because it provides intermediate stationarity improvement while preserving a residual `k^-3`-like shape.

The recommended next step is to pause new simulations and use the comparison checkpoint before deciding the next phase. The immediate priority should be synthesis, reproducibility, and architecture review rather than another parameter run.

## 3. Project Objective

The objective is to build a scientifically interpretable numerical turbulence experiment pipeline that can distinguish:

- a clean fitted spectral slope,
- a robust residual spectral shape,
- a quasi-stationary residual-shape window,
- and a fully stationary cascade claim.

The current work focuses on validating whether residual spectra contain a stable `k^-3`-like structure after masking dominant forcing-scale peaks. The project intentionally separates residual spectral validation from full-system stationarity.

## 4. Numerical Model and Setup

The documented production runs use a 2D numerical vorticity solver with saved spectral outputs. The comparison set uses:

| Parameter | Common value in validated production cases |
|---|---|
| Grid size | `N=256` |
| Time step | `dt=0.0005` |
| Viscosity | `nu=5e-05` |
| Steps | `50000` |
| Saved spectrum cadence | Documented saved-index to step mappings use 1000-step spacing in the validated windows |

The main controlled variations are forcing amplitude, forcing mode, and low-k selective drag:

| Case | Forcing amplitude | Forcing mode | Drag configuration |
|---|---:|---:|---|
| Run 004 | `0.01` | `2` | none |
| Run 009 | `0.01` | `3` | none |
| Run 011 | `0.01` | `3` | `lowk_drag_alpha=0.10`, `lowk_drag_kmax=5` |
| Run 012 | `0.01` | `3` | `lowk_drag_alpha=0.05`, `lowk_drag_kmax=5` |
| Run 013 | `0.01` | `3` | `lowk_drag_alpha=0.075`, `lowk_drag_kmax=5` |

For Run 004, the validated residual analysis used peak mask `k=2:4` and fit range `k=9:41`. For the forcing-mode 3 cases, the forcing peak shifted to approximately `k=4`, and the documented analysis used mask `k=3:5` where appropriate.

## 5. Diagnostic and Validation Methodology

The validation workflow is designed to reduce overinterpretation from slope fitting alone. The core chain is:

| Diagnostic stage | Purpose |
|---|---|
| Initial slope fit | Identify candidate runs with residual slopes near the `-3` reference. |
| Time-stability analysis | Check whether slopes persist across saved spectra. |
| Energy and peak-mode time series | Determine whether total and peak energy are still growing. |
| Energy partition fractions | Quantify whether energy is concentrated at low k or distributed across scales. |
| Peak-masked residual spectrum | Test whether the slope survives after masking the dominant peak band. |
| Compensated `k^3 E(k)` analysis | Check for plateau-like behavior associated with a `k^-3` residual range. |
| Stationarity-window analysis | Identify a non-isolated window where slope, R^2, and compensated CV align. |
| Window-local residual budget | Separate residual shape stability from residual or peak energy stationarity. |
| Window sensitivity | Check whether the result survives small changes in time window and fit range. |
| Residual exponent uncertainty | Report a defensible exponent band instead of a single value. |
| Signal-floor analysis | Confirm the fitted residual range is above numerical floor estimates. |
| Shell-support analysis | Check radial shell population support. |
| Leave-one-shell-out analysis | Check whether any single shell controls the fitted slope. |

This workflow supports cautious residual `k^-3`-like wording while preserving caveats about full-system energy behavior.

## 6. Baseline Result: Run 004

Run 004 is the cleanest residual spectral reference.

| Field | Value |
|---|---|
| Output folder | `outputs_spectra_refined/nu_5e-05_f_0.01_m_2` |
| Parameters | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, no drag |
| Best window | saved indices `38:43`, steps `38000:43000` |
| Fit range | `k=9:41` |
| Peak mask | `k=2:4` |
| Validated shell-summed window fit slope | approximately `-3.0004` |
| Validated shell-summed window fit R^2 | `0.9668` |
| Consolidated best-window mean slope / R^2 | `-3.0036` / `0.9650` |
| Compensated CV | `0.2433` |
| Residual exponent uncertainty | approximately `-3.00 +/- 0.15` |
| Leave-one-shell-out range | `[-3.0778, -2.9517]` |
| Minimum leave-one-out R^2 | `0.9631` |
| Signal-floor status | Fit range safely above numerical floor |
| Shell support | Adequate; min shell count `56`, median `160` |
| Best-window total/peak energy growth | about `+27.92%` |

The supported interpretation is that Run 004 contains a robust peak-masked residual `k^-3`-like spectral shape over the selected window. The main limitation is that this residual validation occurs while the full spectrum remains severely low-k dominated and nonstationary in total/peak energy.

## 7. Forcing Redesign Results

Two no-drag forcing redesign directions were documented: reduced forcing amplitude at mode 2 and shifted forcing mode at amplitude 0.01.

| Case | Best window | Slope | R^2 | Compensated CV | Best-window growth | Main interpretation |
|---|---|---:|---:|---:|---:|---|
| Lower forcing, `f=0.006`, `m=2` | `36:40` | `-2.9823` | `0.9505` | `0.2828` | `+23.36%` | Reduces total/peak amplitude versus Run 004 and preserves residual quality reasonably well, but does not sufficiently improve stationarity or peak domination. |
| Run 009, `f=0.01`, `m=3` | `40:44` | `-3.0116` | `0.9619` | `0.2366` | `+20.78%` | Cleanest `m=3` no-drag forcing case; good residual quality, but only modest stationarity improvement. |

Run 009 shifted the peak to `k=4`, and the analysis used mask `k=3:5`. It preserved residual spectral quality well and is cleaner than the lower-forcing case by residual-shape metrics. However, it did not resolve the peak domination caveat.

## 8. Low-k Drag and Combined Strategy Results

Low-k selective drag was introduced to reduce low-k/peak energy accumulation. The documented results show a tradeoff: low-k drag improves stationarity and peak-energy control, but residual spectral quality generally worsens relative to the cleanest no-drag residual references.

The combined strategy used `forcing_mode=3`, `forcing_amplitude=0.01`, and low-k selective drag:

| Case | Drag | Best window | Slope | R^2 | Compensated CV | Best-window growth | Main interpretation |
|---|---|---|---:|---:|---:|---:|---|
| Run 010 | `alpha=0.10`, `kmax=4` | `40:44` | `-3.0120` | `0.9620` | `0.2365` | `+20.78%` | Null combined-strategy result; effectively identical to Run 009 because `kmax=4` likely missed the shifted forced reservoir. |
| Run 011 | `alpha=0.10`, `kmax=5` | `37:41` | `-3.0004` | `0.9448` | `0.3022` | `+6.80%` | Strongest stationarity control among listed combined cases; residual quality degraded. |
| Run 012 | `alpha=0.05`, `kmax=5` | `38:42` | `-3.0217` | `0.9504` | `0.2860` | `+12.23%` | Previous best balanced combined-strategy case before Run 013. |
| Run 013 | `alpha=0.075`, `kmax=5` | `37:41` | `-2.9916` | `0.9466` | `0.2962` | `+9.38%` | Current best balanced combined-strategy case. |

Run 013 improves stationarity versus Run 012 while preserving residual spectral quality slightly better than Run 011. It does not remove the peak domination caveat, and it does not justify a fully stationary cascade claim.

## 9. Comparative Results Table

### Current Best Case by Objective

| Objective | Best current case | Reason |
|---|---|---|
| Cleanest residual spectral validation | Run 004 | Highest-quality residual reference; strongest validated no-drag k^-3-like window |
| Cleanest m=3 no-drag forcing case | Run 009 | Good residual quality without drag intervention |
| Strongest stationarity control | Run 011 | Lowest best-window energy growth among combined cases |
| Best balanced compromise | Run 013 | Intermediate stationarity improvement while preserving a residual k^-3-like shape |

These are residual-spectrum validation results, not evidence of a fully stationary enstrophy cascade. Peak domination remains severe, and the residual k^-3-like shape should be interpreted separately from full-system stationarity.

### Validated Run Comparison

| Run | Best window | Slope | R^2 | CV | Growth % | Final E / Run004 | Final E / Run009 | Peak fraction | LOO range | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Run 004 | `38:43` | `-3.0036` | `0.9650` | `0.2433` | `27.92` | `1.0000` | `2.2777` | `0.9999999988` | `[-3.0778, -2.9517]` | Cleanest residual reference; severe low-k domination. |
| Run 009 | `40:44` | `-3.0116` | `0.9619` | `0.2366` | `20.78` | `0.4390` | `1.0000` | `0.9999999964` | `[-3.1034, -2.9560]` | Clean `m=3` residual shape; weak stationarity. |
| Run 011 | `37:41` | `-3.0004` | `0.9448` | `0.3022` | `6.80` | `0.0616` | `0.1402` | `0.9999999919` | `[-3.0694, -2.9244]` | Strongest stationarity control among listed combined cases; residual quality degraded. |
| Run 012 | `38:42` | `-3.0217` | `0.9504` | `0.2860` | `12.23` | `0.1466` | `0.3338` | `0.9999999961` | `[-3.0992, -2.9695]` | Previous best balanced combined-strategy case before Run 013. |
| Run 013 | `37:41` | `-2.9916` | `0.9466` | `0.2962` | `9.38` | `0.0925` | `0.2107` | `0.9999999945` | `[-3.0624, -2.9277]` | Current best balanced combined-strategy case. |

The current tradeoff visualization is `validated_run_tradeoff_plot.png`, generated by `compare_validated_runs.py`. It plots best-window total energy growth against compensated CV for the validated comparison set.

## 10. Interpretation

The strongest supported result is not a full turbulence claim. It is a residual-spectrum validation result. Run 004 provides the strongest no-drag residual reference, with a robust peak-masked `k^-3`-like spectral shape over a selected quasi-stationary window.

Run 009 shows that shifting the forcing mode to `m=3` can preserve residual spectral quality without drag intervention, but stationarity remains weak. Run 011 shows that stronger low-k drag can reduce best-window energy growth substantially, but the residual spectral metrics degrade. Run 013 sits between these cases and is currently the best balanced combined strategy.

The comparison supports a clear tradeoff within the current validated comparison set:

- cleaner residual spectral shape tends to occur in cases with weaker stationarity control;
- stronger stationarity control tends to trade off against residual spectral cleanliness;
- Run 013 is the current compromise, not a final resolution.

The current evidence does not justify further immediate alpha-only tuning. It is more appropriate to pause, consolidate the analysis architecture, and decide the next scientific question deliberately.

## 11. Limitations and Caveats

The following limitations remain active:

- No full stationary enstrophy cascade claim is being made.
- The full system remains severely low-k/peak dominated.
- Peak fractions remain very close to 1 in the documented cases.
- Total and peak energy growth have not been eliminated.
- Residual energy remains tiny relative to peak energy.
- The strongest scaling evidence is window-local, not full-run stationary.
- Fit-range selection still affects the exact exponent.
- Low-k drag improves stationarity control but generally reduces residual spectral cleanliness.
- Run 013 is the best balanced combined case so far, but it does not resolve full-system stationarity.
- Further alpha-only tuning is not immediately justified by the current comparison checkpoint.

No Navier-Stokes proof is being made. No general turbulence law is being claimed.

## 12. Recommended Next Work

The recommended next step is to pause new simulations and use the comparison checkpoint before deciding the next phase.

Recommended near-term work:

1. Prepare the analysis artifacts for reproducibility review.
2. Consolidate repeated validation logic into reusable analysis scripts.
3. Use `compare_validated_runs.py`, `validated_run_comparison.csv`, `validated_run_comparison.md`, and `validated_run_tradeoff_plot.png` as the current comparison checkpoint.
4. Decide whether the next scientific question is:
   - longer integration of a selected case,
   - stationarity-focused design changes,
   - forcing/drag architecture redesign,
   - higher-resolution validation,
   - or analysis architecture cleanup.

Do not start another production run until the next scientific question is explicit.

## 13. Artifact Index / Source Files

Primary report sources:

- `research_checkpoint_report.md`
- `validated_run_comparison.md`
- `validated_run_comparison.csv`
- `forcing_redesign_comparison.md`
- `evidence_summary.md`
- `project_state.md`
- `experiment_log.md`

Comparison tool references:

- `compare_validated_runs.py`
- `validated_run_comparison.csv`
- `validated_run_comparison.md`
- `validated_run_tradeoff_plot.png`

Key validation source artifacts include:

- `outputs_spectra_refined/sweep_fit_summary_auto_final.csv`
- `time_stability_summary.csv`
- `energy_peak_time_series_summary.csv`
- `energy_partition_fractions.csv`
- `peak_masked_slope_summary.csv`
- `peak_masked_time_stability.csv`
- `compensated_peak_masked_summary.csv`
- `stationarity_window_summary.csv`
- `window_local_residual_budget.csv`
- `window_sensitivity_summary.csv`
- `residual_exponent_uncertainty.csv`
- `residual_signal_floor_summary.csv`
- `shell_support_summary.csv`
- `leave_one_shell_out_summary.csv`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_validation_summary.csv`
- `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_validation_summary.csv`
- `outputs_lowk_drag_production/analysis/lowk_production_validation_summary.csv`
- `outputs_lowk_drag_production/analysis_alpha_0.15_k4/alpha015_validation_summary.csv`
- `outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_validation_summary.csv`

This draft is a checkpoint document. It summarizes documented evidence and does not introduce new scientific claims.
