# Forcing Redesign Comparison Checkpoint

## Purpose

Compare the forcing-redesign no-drag production cases against Run 004 and the low-k drag stationarity-control cases.

This checkpoint does not claim a validated stationary enstrophy cascade. It records the observed tradeoff: forcing redesign can preserve residual spectral quality well, but peak domination and global stationarity remain limiting caveats.

## Lower-Forcing Case

| Field | Value |
|---|---|
| run folder | `outputs_forcing_redesign/f_0.006_m2_nodrag` |
| analysis folder | `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag` |
| summary artifact | `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_validation_summary.csv` |
| forcing amplitude | `0.006` |
| forcing mode | `2` |
| drag | none |
| best window | saved indices `36:40`, steps `36000:40000` |
| slope | `-2.9823` |
| R^2 | `0.9505` |
| compensated CV | `0.2828` |
| final total/peak energy | about `36.0%` of Run 004 |
| final peak fraction | `0.9999999964` |
| best-window total energy growth | `+23.36%` |

## Forcing-Mode 3 Case

| Field | Value |
|---|---|
| run folder | `outputs_forcing_redesign/f_0.01_m3_nodrag` |
| analysis folder | `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag` |
| summary artifact | `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_validation_summary.csv` |
| forcing amplitude | `0.01` |
| forcing mode | `3` |
| drag | none |
| peak location | shifted to `k=4` |
| mask used | `k=3:5` |
| best window | saved indices `40:44`, steps `40000:44000` |
| slope | `-3.0116` |
| R^2 | `0.9619` |
| compensated CV | `0.2366` |
| leave-one-shell-out range | `[-3.1034, -2.9560]` |
| signal-floor final fit/tail ratio | `4.47e14` |
| shell support min count | `56` |
| final total/peak amplitude | about `43.9%` of Run 004 |
| final peak fraction | `0.9999999964` |
| best-window total energy growth | `+20.78%` |

## Combined m=3 Low-K Drag Case

| Field | Value |
|---|---|
| run folder | `outputs_combined_strategy/f_0.01_m3_lowkdrag_0.10_k4` |
| analysis folder | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4` |
| summary artifact | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_validation_summary.csv` |
| forcing amplitude | `0.01` |
| forcing mode | `3` |
| low-k drag alpha | `0.10` |
| low-k drag kmax | `4` |
| best window | saved indices `40:44`, steps `40000:44000` |
| slope | `-3.0120` |
| R^2 | `0.9620` |
| compensated CV | `0.2365` |
| leave-one-shell-out range | `[-3.1033, -2.9564]` |
| signal-floor final fit/tail ratio | `4.47e14` |
| final total energy ratio to Run 009 | `1.0000` |
| best-window total energy growth | `+20.78%` |
| final peak fraction | `0.9999999989` |

## Combined m=3 Low-K Drag kmax=5 Case

| Field | Value |
|---|---|
| run folder | `outputs_combined_strategy/f_0.01_m3_lowkdrag_0.10_k5` |
| analysis folder | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5` |
| summary artifact | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_validation_summary.csv` |
| forcing amplitude | `0.01` |
| forcing mode | `3` |
| low-k drag alpha | `0.10` |
| low-k drag kmax | `5` |
| best window | saved indices `37:41`, steps `37000:41000` |
| slope | `-3.0004` |
| R^2 | `0.9448` |
| compensated CV | `0.3022` |
| leave-one-shell-out range | `[-3.0694, -2.9244]` |
| signal-floor final fit/tail ratio | `5.40e14` |
| final total energy | `14.0%` of Run 009 and `6.16%` of Run 004 |
| final peak fraction | `0.9999999919` |
| best-window total energy growth | `+6.80%` |

## Combined m=3 Low-K Drag alpha=0.05, kmax=5 Case

| Field | Value |
|---|---|
| run folder | `outputs_combined_strategy/f_0.01_m3_lowkdrag_0.05_k5` |
| analysis folder | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5` |
| summary artifact | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_validation_summary.csv` |
| forcing amplitude | `0.01` |
| forcing mode | `3` |
| low-k drag alpha | `0.05` |
| low-k drag kmax | `5` |
| best window | saved indices `38:42`, steps `38000:42000` |
| slope | `-3.0217` |
| R^2 | `0.9504` |
| compensated CV | `0.2860` |
| leave-one-shell-out range | `[-3.0992, -2.9695]` |
| signal-floor final fit/tail ratio | `4.77e14` |
| final total energy | `33.4%` of Run 009 and `14.7%` of Run 004 |
| final peak fraction | `0.9999999961` |
| best-window total energy growth | `+12.23%` |

## Combined m=3 Low-K Drag alpha=0.075, kmax=5 Case

| Field | Value |
|---|---|
| run folder | `outputs_combined_strategy/f_0.01_m3_lowkdrag_0.075_k5` |
| analysis folder | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5` |
| summary artifact | `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_validation_summary.csv` |
| forcing amplitude | `0.01` |
| forcing mode | `3` |
| low-k drag alpha | `0.075` |
| low-k drag kmax | `5` |
| best window | saved indices `37:41`, steps `37000:41000` |
| slope | `-2.9916` |
| R^2 | `0.9466` |
| compensated CV | `0.2962` |
| leave-one-shell-out range | `[-3.0624, -2.9277]` |
| minimum leave-one-out R^2 | `0.9441` |
| signal-floor final fit/tail ratio | `4.91e14` |
| final total energy | `21.07%` of Run 009 and `9.25%` of Run 004 |
| final total energy versus alpha=0.05/kmax=5 | `63.12%` |
| final total energy versus alpha=0.10/kmax=5 | `150.26%` |
| final peak fraction | `0.9999999945` |
| best-window total energy growth | `+9.38%` |

## Comparison Table

| Case name | Parameters | Best window | Mean slope | R^2 | Compensated CV | Final total/peak energy vs Run 004 | Final peak fraction | Best-window energy growth | Strongest advantage | Strongest caveat |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| Run 004 no-drag residual validation | `forcing_amplitude=0.01`, `forcing_mode=2`, no drag | saved indices `38:43`, steps `38000:43000` | `-3.0004` | `0.9668` | `0.2433` | reference | `0.9999999988` | `+27.92%` | Cleanest residual spectral validation | Severe low-k domination and nonstationary peak growth |
| Lower forcing no-drag | `forcing_amplitude=0.006`, `forcing_mode=2`, no drag | saved indices `36:40`, steps `36000:40000` | `-2.9823` | `0.9505` | `0.2828` | about `36.0%` | `0.9999999964` | `+23.36%` | Reduces total/peak amplitude while preserving residual spectral quality reasonably well | Does not sufficiently improve stationarity or peak domination |
| Forcing-mode 3 no-drag | `forcing_amplitude=0.01`, `forcing_mode=3`, no drag; peak `k=4`, mask `k=3:5` | saved indices `40:44`, steps `40000:44000` | `-3.0116` | `0.9619` | `0.2366` | about `43.9%` | `0.9999999964` | `+20.78%` | Cleanest forcing-redesign residual-shape result so far | Only modest stationarity improvement; peak domination remains severe |
| Run 010 combined m=3 low-k drag alpha=0.10, kmax=4 | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.10`, `lowk_drag_kmax=4` | saved indices `40:44`, steps `40000:44000` | `-3.0120` | `0.9620` | `0.2365` | about `43.9%`; final total energy ratio to Run 009 `1.0000` | `0.9999999989` | `+20.78%` | Preserves Run 009 residual metrics because it is effectively identical | Null combined-strategy result; kmax=4 likely misses the m=3 forced reservoir near `|k|=4.24` |
| Run 011 combined m=3 low-k drag alpha=0.10, kmax=5 | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.10`, `lowk_drag_kmax=5` | saved indices `37:41`, steps `37000:41000` | `-3.0004` | `0.9448` | `0.3022` | about `6.16%`; final total energy ratio to Run 009 `14.0%` | `0.9999999919` | `+6.80%` | Actually changes m=3 dynamics and substantially improves stationarity | Residual spectral quality worsens compared with Run 009 |
| Run 012 combined m=3 low-k drag alpha=0.05, kmax=5 | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.05`, `lowk_drag_kmax=5` | saved indices `38:42`, steps `38000:42000` | `-3.0217` | `0.9504` | `0.2860` | about `14.7%`; final total energy ratio to Run 009 `33.4%` | `0.9999999961` | `+12.23%` | Previous best balanced combined-strategy case before Run 013; improves stationarity while preserving residual quality better than alpha=0.10/kmax=5 | Peak domination remains severe and stationarity control is weaker than alpha=0.10/kmax=5 |
| Run 013 combined m=3 low-k drag alpha=0.075, kmax=5 | `forcing_amplitude=0.01`, `forcing_mode=3`, `lowk_drag_alpha=0.075`, `lowk_drag_kmax=5` | saved indices `37:41`, steps `37000:41000` | `-2.9916` | `0.9466` | `0.2962` | about `9.25%`; final total energy ratio to Run 009 `21.07%` | `0.9999999945` | `+9.38%` | Current best balanced combined-strategy case; improves stationarity versus alpha=0.05/kmax=5 and preserves residual quality slightly better than alpha=0.10/kmax=5 | Peak domination remains severe and further alpha-only tuning is not immediately justified |
| Low-k drag alpha=0.15, kmax=4 | `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.15`, `lowk_drag_kmax=4` | saved indices `36:40`, steps `36000:40000` | `-3.0121` | `0.9459` | `0.2870` | about `7.07%` | `0.9999999921` | `+3.75%` | Better stationarity control than lower forcing | Residual spectral validation is less clean than Run 004 |
| Low-k drag alpha=0.20, kmax=4 | `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.20`, `lowk_drag_kmax=4` | saved indices `36:40`, steps `36000:40000` | `-3.0177` | `0.9434` | `0.2877` | about `4.13%` | `0.9999999865` | `+1.85%` | Strongest low-k/peak-energy control among documented cases | Residual spectral validation is less clean than Run 004 |
| Low-k drag alpha=0.20, kmax=3 | `forcing_amplitude=0.01`, `forcing_mode=2`, `lowk_drag_alpha=0.20`, `lowk_drag_kmax=3` | saved indices `36:40`, steps `36000:40000` | `-3.0176` | `0.94335` | `0.28769` | about `4.13%` | `0.9999999864` | `+1.85%` | Confirms kmax=3 is effectively equivalent to kmax=4 in measured metrics | Does not improve residual spectral quality versus kmax=4 |

## Interpretation

Forcing_mode=3 preserves residual `k^-3`-like spectral quality well and is cleaner than the lower-forcing `f=0.006` case and cleaner than low-k drag by residual-shape metrics.

Forcing_mode=3 only modestly improves stationarity. Low-k drag alpha=0.20 remains stronger for peak-energy control, while Run 004 remains the reference no-drag residual-shape validation case.

The combined m=3, alpha=0.10, kmax=4 case is a null result. It is effectively identical to Run 009. The likely reason is that `forcing_mode=3` injects near `|k|=sqrt(3^2+3^2) ~= 4.24`, while `lowk_drag_kmax=4` does not include that forced peak. Therefore this run did not meaningfully test low-k drag on the shifted m=3 forcing reservoir.

The combined m=3, alpha=0.10, kmax=5 case actually changes the m=3 dynamics. Stationarity improves substantially versus Run 009 and the residual `k^-3` slope survives, but residual spectral quality worsens compared with Run 009. This is a real but imperfect combined compromise.

The combined m=3, alpha=0.05, kmax=5 case improves stationarity versus Run 009 and preserves residual spectral quality better than alpha=0.10/kmax=5, while still retaining the major caveat that peak domination remains severe.

The combined m=3, alpha=0.075, kmax=5 case improves stationarity versus alpha=0.05/kmax=5 and preserves residual spectral quality slightly better than alpha=0.10/kmax=5. It is currently the best balanced combined-strategy case. Further alpha-only tuning is not immediately justified. User-suggested speculative future refinement values are `0.068`, `0.065`, and `0.072`, but these should remain speculative unless a later documentation review identifies a concrete unresolved bracket.

## Source Artifacts

- `experiment_log.md`
- `evidence_summary.md`
- `project_state.md`
- `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_validation_summary.csv`
- `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_time_series.csv`
- `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_energy.png`
- `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_partitions.png`
- `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_residual_slopes.png`
- `outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_compensated.png`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_validation_summary.csv`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_time_series.csv`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_energy.png`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_partitions.png`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_residual_slopes.png`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_compensated.png`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_leave_one_shell_out.csv`
- `outputs_forcing_redesign/analysis_f_0.01_m3_nodrag/forcing_m3_signal_floor.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_time_series.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_energy.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_partitions.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_residual_slopes.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4/combined_compensated.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_time_series.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_energy.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_partitions.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_residual_slopes.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5/combined_compensated.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_time_series.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_energy.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_partitions.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_residual_slopes.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5/combined_compensated.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_validation_summary.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_time_series.csv`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_energy.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_partitions.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_residual_slopes.png`
- `outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_compensated.png`
- `outputs_lowk_drag_production/analysis/lowk_production_validation_summary.csv`
- `outputs_lowk_drag_production/analysis_alpha_0.15_k4/alpha015_validation_summary.csv`
- `outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_validation_summary.csv`
- Run 004 validation artifacts listed in `evidence_summary.md`

## Current Non-Claim

This result does not validate a full stationary enstrophy cascade. The supported claim remains limited to documented residual spectral-shape behavior under the validation diagnostics.
