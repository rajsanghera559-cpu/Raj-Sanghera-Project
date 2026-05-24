# Evidence Summary

## Run 004 Validation Chain

Candidate: Run 004, `nu=5e-05`, `f=0.01`

Window: saved indices `38:43`, steps `38000:43000`

Fit range: `k=9:41`, peak mask `k=2:4`

| Diagnostic | Question answered | Result | Status | Caveat | Source artifact |
|---|---|---|---|---|---|
| Initial slope fit | Is there a candidate slope near the 2D enstrophy-cascade reference? | Run 004 produced a strong initial candidate near `-3` in the refined sweep. | Candidate identified | Slope fitting alone is not enough to claim a cascade. | `outputs_spectra_refined/sweep_fit_summary_auto_final.csv` |
| Time-stability analysis | Does the candidate slope persist over saved spectra? | Run 004 had the best late-time stability among candidates, but slopes still drifted. | Partially supported | Not fully stationary over the full run. | `time_stability_summary.csv`, `time_stability_slopes.png`, `time_stability_r2.png` |
| Energy/peak time series | Is total energy stationary and broadly distributed? | Total and peak energy continued growing. | Caveat identified | Full system is still transient in total energy. | `energy_peak_time_series_summary.csv`, `energy_total_vs_time.png`, `peak_mode_energy_vs_time.png` |
| Energy partition fractions | Is energy distributed across peak, midrange, and high-k bands? | Peak/total approached nearly 1, while midrange and high-k fractions were tiny. | Major caveat | Full spectrum is overwhelmingly low-k dominated. | `energy_partition_fractions.csv`, `energy_partition_fractions.png` |
| Peak-masked residual spectrum | Does the `-3`-like slope survive after masking the dominant peak band? | The residual slope survived peak masking. | Supported | Residual energy remains tiny relative to the peak. | `peak_masked_slope_summary.csv`, `peak_masked_time_stability.csv`, `peak_masked_normalized_spectra.png`, `peak_masked_slope_vs_time.png` |
| Compensated `k^3 E(k)` | Does compensation show a plateau-like residual range? | Run 004 had the strongest plateau-like behavior, with compensated CV near `0.302` late and `0.2433` in the selected window. | Supported for residual shape | Plateau quality is not proof of full stationarity. | `compensated_peak_masked_summary.csv`, `compensated_peak_masked_late_mean.png`, `compensated_plateau_quality_vs_time.png` |
| Stationarity-window analysis | Is there a quasi-stationary window where slope, R^2, and CV align? | Best window was indices `38:43`, with slope `-3.0036`, R^2 `0.9650`, CV `0.2433`, width `32`. | Strong residual-shape support | Window is quasi-stationary, not a full-run stationary state. | `stationarity_window_summary.csv`, `stationarity_window_spectrum.png`, `stationarity_window_compensated.png`, `stationarity_window_diagnostics.png` |
| Window-local residual budget | Is the shape stable while amplitudes change? | Total/peak energy grew `27.918%`; residual energy fell `4.499%`; midrange fell `9.500%`; high-k fell `16.964%`. | Shape stable, energy not stationary | Residual amplitude is slowly decaying while peak grows. | `window_local_residual_budget.csv`, `window_local_residual_budget.png` |
| Window-sensitivity analysis | Does the result survive nearby time-window and fit-range choices? | `13/40` combinations were within `0.10` of `-3`; `36/40` were within `0.25`; all `k=9:41` windows stayed near `-3`. | Robust across time windows | More sensitive to fit-range choice. | `window_sensitivity_summary.csv`, `window_sensitivity_heatmap_slope.png`, `window_sensitivity_heatmap_r2.png`, `window_sensitivity_heatmap_cv.png` |
| Residual exponent uncertainty | What exponent range is defensible? | Accepted ensemble gave mean slope `-2.995`, std `0.145`, 10-90% band `[-3.162, -2.792]`. | Supports `k^-3`-like wording | Report an uncertainty band, not a single exact exponent. | `residual_exponent_uncertainty.csv`, `residual_exponent_uncertainty.png` |
| Signal-floor analysis | Is the residual fit range above numerical floor? | Fit-range median was about `24.3` orders above median high-k tail and `4.5` orders above `eps * max(E)`. | Supported | Signal is real relative to floor, but still tiny relative to peak energy. | `residual_signal_floor_summary.csv`, `residual_signal_floor_spectrum.png`, `residual_signal_floor_ratios.png` |
| Shell-support analysis | Are fitted shells sufficiently populated? | `k=9:41` shells had min count `56`, median `160`, max `264`; no shells below `32` modes. | Supported | Shell-mean normalization changes the slope, as expected from shell population growth. | `shell_support_summary.csv`, `shell_mode_counts.png`, `shell_sum_vs_shell_mean_spectrum.png` |
| Leave-one-shell-out analysis | Is the slope controlled by one radial bin? | Baseline slope `-3.0004`, R^2 `0.9668`; leave-one-out slope range `[-3.0778, -2.9517]`; min R^2 `0.9631`. | Supported | Does not remove the low-k domination caveat. | `leave_one_shell_out_summary.csv`, `leave_one_shell_out_slope_change.png`, `leave_one_shell_out_r2_change.png` |

## Run 004 vs Low-K Drag Production

| Case name | Parameters | Best window | Mean slope | R^2 | Compensated CV | Leave-one-shell-out range | Signal-floor status | Total/peak energy improvement | Best-window energy growth | Strongest advantage | Strongest caveat |
|---|---|---|---:|---:|---:|---|---|---|---:|---|---|
| Run 004 no-drag residual validation | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, no low-k drag | saved indices `38:43`, steps `38000:43000` | `-3.0004` | `0.9668` | `0.2433` | `[-3.0778, -2.9517]` | Fit range safely above numerical floor | Reference case; no low-k energy-control improvement | `+27.92%` | Strongest residual spectral validation | Severe low-k domination and nonstationary peak growth |
| Low-k drag production alpha=0.15 | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.15`, `lowk_drag_kmax=4` | saved indices `36:40`, steps `36000:40000` | `-3.0121` | `0.9459` | `0.2870` | `[-3.1122, -2.9463]` | Safely above tail | Final total/peak energy about `7.07%` of Run 004 | `+3.75%` | Slightly cleaner residual spectral quality than alpha=0.20 | Improvement over alpha=0.20 is marginal; weaker low-k control than alpha=0.20 |
| Low-k drag production alpha=0.20, kmax=4 | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.20`, `lowk_drag_kmax=4` | saved indices `36:40`, steps `36000:40000` | `-3.0177` | `0.9434` | `0.2877` | `[-3.1203, -2.9461]` | Safely above tail; final fit/tail ratio `1.93e13` | Final total/peak energy about `4.13%` of Run 004 | `+1.85%` | Much better low-k energy control | Residual spectral validation is less clean than Run 004 |
| Low-k drag cutoff tuning alpha=0.20, kmax=3 | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.20`, `lowk_drag_kmax=3` | saved indices `36:40`, steps `36000:40000` | `-3.0176` | `0.94335` | `0.28769` | `[-3.1203, -2.9461]` | Safely above tail; final fit/tail ratio about `1.93e13` | Final total/peak energy about `4.13%` of Run 004 | `+1.85%` | Still improves stationarity versus Run 004 | Effectively equivalent to alpha=0.20, kmax=4; does not improve residual spectral quality |

Low-k selective drag improves stationarity/peak-energy behavior while preserving a residual `k^-3`-like range, but introduces a tradeoff: the residual spectral shape is less clean than the no-drag Run 004 case. Alpha=0.15 preserves residual spectral quality slightly better than alpha=0.20, but the improvement is marginal; alpha=0.20 still has stronger low-k/peak-energy control. Alpha=0.20, kmax=3 is effectively equivalent to alpha=0.20, kmax=4 in measured validation metrics. Low-k drag alpha/cutoff tuning has reached diminishing returns, and immediate kmax=5 testing is not recommended.

Supporting source artifacts:
- `outputs_lowk_drag_production/analysis/lowk_production_validation_summary.csv`
- `outputs_lowk_drag_production/analysis_alpha_0.15_k4/alpha015_validation_summary.csv`
- `outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_validation_summary.csv`
- `outputs_lowk_drag_production/analysis/lowk_production_time_series.csv`
- `outputs_lowk_drag_production/analysis_alpha_0.15_k4/alpha015_time_series.csv`
- `outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_time_series.csv`
- `outputs_lowk_drag_production/analysis/lowk_production_partitions.png`
- `outputs_lowk_drag_production/analysis_alpha_0.15_k4/alpha015_partitions.png`
- `outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_partitions.png`
- `outputs_lowk_drag_production/analysis/lowk_production_residual_slopes.png`
- `outputs_lowk_drag_production/analysis_alpha_0.15_k4/alpha015_residual_slopes.png`
- `outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_residual_slopes.png`
- `outputs_lowk_drag_production/analysis/lowk_production_stationarity_windows.csv`
- `outputs_lowk_drag_production/analysis_alpha_0.15_k4/alpha015_stationarity_windows.csv`
- `outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_stationarity_windows.csv`
- Run 004 artifacts listed in the validation-chain table above

## Forcing Redesign Checkpoint

Lower forcing amplitude and forcing-mode shift were tested as no-drag forcing-redesign candidates.

| Case name | Parameters | Best window | Mean slope | R^2 | Compensated CV | Final total/peak energy vs Run 004 | Final peak fraction | Best-window energy growth | Interpretation | Source artifact |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Run 004 no-drag reference | `forcing_amplitude=0.01`, `forcing_mode=2`, no drag | saved indices `38:43`, steps `38000:43000` | `-3.0004` | `0.9668` | `0.2433` | reference | `0.9999999988` | `+27.92%` | Cleanest residual spectral validation, but severe low-k domination and nonstationary peak growth. | Run 004 artifacts listed above |
| Lower forcing no-drag | `forcing_amplitude=0.006`, `forcing_mode=2`, no drag | saved indices `36:40`, steps `36000:40000` | `-2.9823` | `0.9505` | `0.2828` | about `36.0%` | `0.9999999964` | `+23.36%` | Reduces total/peak amplitude versus Run 004 and preserves residual spectral quality reasonably well, but does not sufficiently improve stationarity or peak domination. | `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_validation_summary.csv` |
| Forcing-mode shift no-drag | `forcing_amplitude=0.01`, `forcing_mode=3`, no drag; peak shifted to `k=4`, mask `k=3:5` | saved indices `40:44`, steps `40000:44000` | `-3.0116` | `0.9619` | `0.2366` | about `43.9%` | `0.9999999964` | `+20.78%` | Preserves residual `k^-3`-like spectral quality well and is cleaner than lower forcing and low-k drag by residual-shape metrics, but only modestly improves stationarity. | `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_validation_summary.csv` |
| Combined m=3 low-k drag | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.10`, `lowk_drag_kmax=4` | saved indices `40:44`, steps `40000:44000` | `-3.0120` | `0.9620` | `0.2365` | about `43.9%`; final total energy ratio to Run 009 `1.0000` | `0.9999999989` | `+20.78%` | Null combined-strategy result: effectively identical to Run 009 because `kmax=4` likely misses the m=3 forced reservoir near `|k|=sqrt(3^2+3^2) ~= 4.24`. | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_validation_summary.csv` |
| Combined m=3 low-k drag kmax=5 | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.10`, `lowk_drag_kmax=5` | saved indices `37:41`, steps `37000:41000` | `-3.0004` | `0.9448` | `0.3022` | `6.16%` of Run 004; `14.0%` of Run 009 | `0.9999999919` | `+6.80%` | Real but imperfect combined compromise: stationarity improves and the residual `k^-3` slope survives, but residual spectral quality worsens compared with Run 009. | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_validation_summary.csv` |
| Run 012 combined m=3 low-k drag alpha=0.05, kmax=5 | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.05`, `lowk_drag_kmax=5` | saved indices `38:42`, steps `38000:42000` | `-3.0217` | `0.9504` | `0.2860` | `14.7%` of Run 004; `33.4%` of Run 009 | `0.9999999961` | `+12.23%` | Previous best balanced combined-strategy case before Run 013: improves stationarity versus Run 009 and preserves residual spectral quality better than alpha=0.10/kmax=5. | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_validation_summary.csv` |
| Run 013 combined m=3 low-k drag alpha=0.075, kmax=5 | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.075`, `lowk_drag_kmax=5` | saved indices `37:41`, steps `37000:41000` | `-2.9916` | `0.9466` | `0.2962` | `9.25%` of Run 004; `21.07%` of Run 009; `63.12%` of alpha=0.05/kmax=5; `150.26%` of alpha=0.10/kmax=5 | `0.9999999945` | `+9.38%` | Current best balanced combined-strategy case: improves stationarity versus alpha=0.05/kmax=5 and preserves residual spectral quality slightly better than alpha=0.10/kmax=5. | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_validation_summary.csv` |
| Low-k drag alpha=0.20, kmax=4 | `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.20`, `lowk_drag_kmax=4` | saved indices `36:40`, steps `36000:40000` | `-3.0177` | `0.9434` | `0.2877` | about `4.13%` | `0.9999999865` | `+1.85%` | Stronger stationarity and peak-energy control than lower forcing, with less clean residual spectral validation than Run 004. | `outputs_lowk_drag_production/analysis/lowk_production_validation_summary.csv` |

Forcing_mode=3 preserves residual `k^-3`-like spectral quality well and is cleaner than the lower-forcing `f=0.006` case and low-k drag by residual-shape metrics. It only modestly improves stationarity. The combined m=3, alpha=0.10, kmax=4 case is a null result because it is effectively identical to Run 009. The combined m=3, alpha=0.10, kmax=5 case actually changes the m=3 dynamics, substantially improves stationarity, and preserves the residual `k^-3` slope, but residual spectral quality worsens compared with Run 009. The combined m=3, alpha=0.05, kmax=5 case improves stationarity versus Run 009 while preserving residual spectral quality better than alpha=0.10/kmax=5. The combined m=3, alpha=0.075, kmax=5 case improves stationarity versus alpha=0.05/kmax=5 while preserving residual spectral quality slightly better than alpha=0.10/kmax=5; it is currently the best balanced combined-strategy case. Further alpha-only tuning is not immediately justified. Speculative future refinement values are `0.068`, `0.065`, and `0.072`, but these should remain speculative unless a later documentation review identifies a concrete unresolved bracket.

## Current Strongest Claim

Run 004 shows a robust peak-masked residual `k^-3`-like spectral shape over steps `38000-43000`.

## Current Strongest Caveat

This is not yet evidence of a validated stationary enstrophy cascade because the full system remains low-k dominated and total/peak energy continues to grow.
