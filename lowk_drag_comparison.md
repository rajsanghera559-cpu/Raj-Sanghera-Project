# Low-K Drag Comparison Checkpoint

## Purpose

Compare the no-drag Run 004 residual-shape validation against the low-k selective drag production cases.

This checkpoint does not claim a validated stationary enstrophy cascade. It records the tradeoff observed so far: low-k selective drag improves stationarity and peak-energy behavior while preserving a residual `k^-3`-like range, but the residual spectral shape is less clean than the no-drag Run 004 case.

## Comparison Table

| Case name | Parameters | Best window | Mean slope | R^2 | Compensated CV | Leave-one-shell-out range | Signal-floor status | Total/peak energy improvement | Best-window energy growth | Strongest advantage | Strongest caveat |
|---|---|---|---:|---:|---:|---|---|---|---:|---|---|
| Run 004 no-drag residual validation | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, no low-k drag | saved indices `38:43`, steps `38000:43000` | `-3.0004` | `0.9668` | `0.2433` | `[-3.0778, -2.9517]` | Fit range safely above numerical floor | Reference case; no low-k energy-control improvement | `+27.92%` | Strongest residual spectral validation | Severe low-k domination and nonstationary peak growth |
| Low-k drag production alpha=0.15 | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.15`, `lowk_drag_kmax=4` | saved indices `36:40`, steps `36000:40000` | `-3.0121` | `0.9459` | `0.2870` | `[-3.1122, -2.9463]` | Safely above tail | Final total/peak energy about `7.07%` of Run 004 | `+3.75%` | Slightly cleaner residual spectral quality than alpha=0.20 | Improvement over alpha=0.20 is marginal; weaker low-k control than alpha=0.20 |
| Low-k drag production alpha=0.20, kmax=4 | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.20`, `lowk_drag_kmax=4` | saved indices `36:40`, steps `36000:40000` | `-3.0177` | `0.9434` | `0.2877` | `[-3.1203, -2.9461]` | Safely above tail; final fit/tail ratio `1.93e13` | Final total/peak energy about `4.13%` of Run 004 | `+1.85%` | Much better low-k energy control | Residual spectral validation is less clean than Run 004 |
| Low-k drag cutoff tuning alpha=0.20, kmax=3 | `N=256`, `dt=0.0005`, `nu=5e-05`, `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.20`, `lowk_drag_kmax=3` | saved indices `36:40`, steps `36000:40000` | `-3.0176` | `0.94335` | `0.28769` | `[-3.1203, -2.9461]` | Safely above tail; final fit/tail ratio about `1.93e13` | Final total/peak energy about `4.13%` of Run 004 | `+1.85%` | Still improves stationarity versus Run 004 | Effectively equivalent to alpha=0.20, kmax=4; does not improve residual spectral quality |

## Interpretation

Low-k selective drag improves stationarity/peak-energy behavior while preserving a residual `k^-3`-like range, but introduces a tradeoff: the residual spectral shape is less clean than the no-drag Run 004 case.

Run 004 remains the cleaner residual-shape validation case. Alpha=0.15 preserves residual spectral quality slightly better than alpha=0.20, but the improvement over alpha=0.20 is marginal. Alpha=0.20 remains the stronger stationarity/peak-control case. Alpha=0.20, kmax=3 is effectively equivalent to alpha=0.20, kmax=4 in measured validation metrics. Low-k drag alpha/cutoff tuning has reached diminishing returns, immediate kmax=5 testing is not recommended, and the next scientific direction should be forcing redesign planning rather than another drag-parameter run.

## Source Artifacts

- `experiment_log.md`
- `evidence_summary.md`
- `project_state.md`
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
- Run 004 validation artifacts listed in `evidence_summary.md`

## Current Non-Claim

None of these cases validates a full stationary enstrophy cascade. The supported claim is limited to residual spectral-shape behavior under the documented diagnostics.
