# Project State

## Current Strongest Supported Result

Run 004 shows a robust peak-masked residual `k^-3`-like spectral shape over steps `38000-43000`.

This result is supported by the documented validation chain: peak masking, compensated spectra, stationarity-window analysis, residual budget checks, window sensitivity, exponent uncertainty, signal-floor analysis, shell-support analysis, and leave-one-shell-out influence testing.

## Current Strongest Caveat

This is not yet evidence of a validated stationary enstrophy cascade. The full system remains low-k dominated, and total/peak energy continues to grow.

The validated result is a residual spectral-shape result, not a full-system stationarity result.

## Run 004 Parameters

| Field | Value |
|---|---|
| Run | 004 |
| N | 256 |
| dt | 0.0005 |
| nu | 5e-05 |
| forcing f | 0.01 |
| steps | 50000 |
| output folder | `outputs_spectra_refined/nu_5e-05_f_0.01_m_2` |
| initial auto-fit slope | -2.791 |

The initial auto-fit slope is not the final validation checkpoint. The stronger documented checkpoint is the validated window result below.

## Validated Window Details

| Field | Value |
|---|---|
| saved indices | 38:43 |
| steps | 38000:43000 |
| fit range | k=9:41 |
| peak mask | k=2:4 |
| validated window slope | -3.0004 |
| R^2 | 0.9668 |
| residual exponent uncertainty | -3.00 +/- 0.15 |
| leave-one-shell-out slope range | [-3.0778, -2.9517] |
| minimum leave-one-shell-out R^2 | 0.9631 |
| shell support | adequate; min shell count 56, median 160 |
| signal-floor result | fit range safely above numerical floor |

## Low-K Drag Comparison State

Low-k selective drag improves stationarity and peak-energy behavior while preserving a residual `k^-3`-like range, but the residual spectral shape is less clean than the no-drag Run 004 case.

| Case | Best window | Mean slope | R^2 | Compensated CV | Best-window energy growth | Final total/peak energy vs Run 004 | Main read |
|---|---|---:|---:|---:|---:|---:|---|
| Run 004 no-drag | saved indices 38:43, steps 38000:43000 | -3.0004 | 0.9668 | 0.2433 | +27.92% | reference | Cleanest residual spectral validation, but severe low-k domination. |
| low-k drag alpha=0.15, kmax=4 | saved indices 36:40, steps 36000:40000 | -3.0121 | 0.9459 | 0.2870 | +3.75% | 7.07% | Slightly cleaner residual spectral quality than alpha=0.20, but the improvement is marginal. |
| low-k drag alpha=0.20, kmax=4 | saved indices 36:40, steps 36000:40000 | -3.0177 | 0.9434 | 0.2877 | +1.85% | 4.13% | Stronger low-k/peak-energy control than alpha=0.15. |
| low-k drag alpha=0.20, kmax=3 | saved indices 36:40, steps 36000:40000 | -3.0176 | 0.94335 | 0.28769 | +1.85% | 4.13% | Effectively equivalent to alpha=0.20, kmax=4; no residual-quality improvement. |

Low-k drag alpha/cutoff tuning shows diminishing returns and does not justify another immediate drag-parameter run. Immediate kmax=5 testing is not recommended.

## Forcing Redesign State

Lower forcing amplitude and forcing-mode shift were tested as no-drag forcing-redesign candidates.

| Case | Best window | Mean slope | R^2 | Compensated CV | Best-window energy growth | Final total/peak energy vs Run 004 | Final peak fraction | Main read |
|---|---|---:|---:|---:|---:|---:|---:|---|
| lower forcing f=0.006, mode=2, no drag | saved indices 36:40, steps 36000:40000 | -2.9823 | 0.9505 | 0.2828 | +23.36% | 36.0% | 0.9999999964 | Reduces total/peak amplitude versus Run 004 and preserves residual spectral quality reasonably well, but does not sufficiently improve stationarity or peak domination. |
| forcing mode=3, f=0.01, no drag | saved indices 40:44, steps 40000:44000 | -3.0116 | 0.9619 | 0.2366 | +20.78% | 43.9% | 0.9999999964 | Preserves residual `k^-3`-like spectral quality well and is cleaner than lower forcing and low-k drag by residual-shape metrics, but only modestly improves stationarity. |

Forcing_mode=3 shifted the peak to `k=4`; the validation used mask `k=3:5`. It has leave-one-shell-out range `[-3.1034, -2.9560]`, signal-floor final fit/tail ratio `4.47e14`, and shell support min count `56`.

Forcing_mode=3 is cleaner than the lower-forcing f=0.006 case and cleaner than low-k drag by residual-shape metrics. Low-k drag alpha=0.20 remains stronger for peak-energy control.

The next direction should be combined strategy planning, not another pure forcing-only run.

## Combined Strategy State

The combined forcing-plus-drag tests use `forcing_mode=3`, `forcing_amplitude=0.01`, and low-k selective drag.

| Case | Best window | Mean slope | R^2 | Compensated CV | Best-window energy growth | Final total energy vs Run 009 | Final peak fraction | Main read |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Run 010 m=3, alpha=0.10, kmax=4 | saved indices 40:44, steps 40000:44000 | -3.0120 | 0.9620 | 0.2365 | +20.78% | 1.0000 | 0.9999999989 | Null combined-strategy result; effectively identical to Run 009. |
| Run 011 m=3, alpha=0.10, kmax=5 | saved indices 37:41, steps 37000:41000 | -3.0004 | 0.9448 | 0.3022 | +6.80% | 14.0% | 0.9999999919 | Real but imperfect combined compromise; stationarity improves and the residual slope survives, but residual spectral quality worsens. |
| Run 012 m=3, alpha=0.05, kmax=5 | saved indices 38:42, steps 38000:42000 | -3.0217 | 0.9504 | 0.2860 | +12.23% | 33.4% | 0.9999999961 | Previous best balanced combined-strategy case before Run 013; stationarity improves versus Run 009 while residual quality is better than alpha=0.10/kmax=5. |
| Run 013 m=3, alpha=0.075, kmax=5 | saved indices 37:41, steps 37000:41000 | -2.9916 | 0.9466 | 0.2962 | +9.38% | 21.07% | 0.9999999945 | Current best balanced combined-strategy case; improves stationarity versus alpha=0.05/kmax=5 while residual quality is slightly better than alpha=0.10/kmax=5. |

The kmax=4 run did not meaningfully test low-k drag on the shifted m=3 forcing reservoir. The likely reason is that `forcing_mode=3` injects near `|k|=sqrt(3^2+3^2) ~= 4.24`, while `lowk_drag_kmax=4` does not include that forced peak.

The alpha=0.10, kmax=5 run actually changes the m=3 dynamics. Final total energy is `14.0%` of Run 009 and `6.16%` of Run 004, and best-window total energy growth drops to `+6.80%`. The residual `k^-3` slope survives, but R^2 and compensated CV worsen compared with Run 009.

The Run 012 alpha=0.05, kmax=5 run is a gentler combined strategy. Final total energy is `33.4%` of Run 009 and `14.7%` of Run 004, and best-window total energy growth is `+12.23%`. It preserves residual spectral quality better than alpha=0.10/kmax=5 while still improving stationarity versus Run 009. It was the previous best balanced combined-strategy case before Run 013.

The Run 013 alpha=0.075, kmax=5 run is the midpoint combined strategy. Final total energy is `21.07%` of Run 009 and `9.25%` of Run 004, `63.12%` of alpha=0.05/kmax=5, and `150.26%` of alpha=0.10/kmax=5. Best-window total energy growth is `+9.38%`. It improves stationarity versus alpha=0.05/kmax=5 and preserves residual spectral quality slightly better than alpha=0.10/kmax=5. It is currently the best balanced combined-strategy case.

Further alpha-only tuning is not immediately justified. User-suggested speculative future refinement values are `0.068`, `0.065`, and `0.072`, but these should remain speculative unless a later documentation review identifies a concrete unresolved bracket.

## Evidence Chain Summary

| Step | Summary |
|---|---|
| Initial slope fit | Identified Run 004 as a strong residual-slope candidate. |
| Time-stability analysis | Run 004 had the best late-time slope stability among candidates, but slopes still drifted over the full run. |
| Energy/peak time series | Total and peak energy continued growing. |
| Energy partition fractions | Peak/total approached nearly 1, while midrange and high-k fractions were tiny. |
| Peak-masked residual spectrum | The residual slope survived masking the dominant low-k peak band. |
| Compensated `k^3 E(k)` | Run 004 had the strongest plateau-like residual behavior among tested candidates. |
| Stationarity-window analysis | Best quasi-stationary window was saved indices 38:43, steps 38000:43000. |
| Window-local residual budget | Residual shape remained stable while residual amplitude decayed and total/peak energy grew. |
| Window-sensitivity analysis | The result was robust across nearby time windows and moderately sensitive to fit-range choice. |
| Residual exponent uncertainty | Accepted ensemble supported reporting a residual exponent near `-3.00 +/- 0.15`. |
| Signal-floor analysis | The fit range was safely above numerical floor estimates. |
| Shell-support analysis | Fitted shells were adequately populated. |
| Leave-one-shell-out analysis | No individual shell controlled the slope. |

## Remaining Uncertainties

- The full system is still low-k dominated.
- Total and peak energy continue to grow.
- Residual energy is tiny relative to peak energy.
- The validated result is quasi-stationary over a selected window, not over the full run.
- Fit-range choice still affects the exact exponent.
- The current evidence supports a residual `k^-3`-like shape, not a fully validated stationary cascade.
- Low-k drag improves peak-energy control but does not yet produce a cleaner residual spectral validation than Run 004.
- Alpha=0.20, kmax=3 is effectively equivalent to alpha=0.20, kmax=4 in measured validation metrics.
- Lower forcing f=0.006 reduces total/peak amplitude versus Run 004 but does not sufficiently improve stationarity or peak domination.
- Forcing_mode=3 preserves residual spectral quality well, but only modestly improves stationarity and does not solve peak domination.
- Combined m=3 alpha=0.10, kmax=4 is a null result because it is effectively identical to Run 009 and likely misses the shifted forced reservoir.
- Combined m=3 alpha=0.10, kmax=5 is a real but imperfect compromise: better stationarity, surviving residual slope, worse residual spectral quality.
- Combined m=3 alpha=0.05, kmax=5 improves stationarity versus Run 009 and preserves residual spectral quality better than alpha=0.10/kmax=5, but peak domination remains severe and full stationarity is still not established.
- Combined m=3 alpha=0.075, kmax=5 is currently the best balanced combined-strategy case, but peak domination remains severe and further alpha-only tuning is not immediately justified.

## Recommended Next Options

1. Improve stationarity.
   Focus on whether total/peak energy can reach a less transient regime.

2. Redesign forcing.
   Pause pure forcing-only runs; use the forcing_mode=3 result when planning a combined stationarity/residual-quality strategy.

3. Combined strategy.
   Review the alpha=0.075/kmax=5 checkpoint before any further simulations. Speculative alpha-only refinements `0.068`, `0.065`, and `0.072` should remain unrun unless review identifies a concrete unresolved bracket.

4. Stop immediate m=2 low-k drag alpha/cutoff tuning.
   Current m=2 alpha and cutoff tuning shows diminishing returns; do not prioritize immediate m=2 kmax=5 testing.

5. Extend runs.
   Continue or repeat targeted cases only after deciding that longer integration is scientifically justified.

6. Clean analysis architecture.
   Organize analysis scripts, outputs, and source-artifact references so the validation chain remains reproducible.

## Explicit Non-Claims

No Navier-Stokes proof is being made.

No full stationary enstrophy cascade claim is being made.

No general turbulence law is being claimed.

The current strongest claim is limited to Run 004 showing a robust peak-masked residual `k^-3`-like spectral shape over steps `38000-43000`.
