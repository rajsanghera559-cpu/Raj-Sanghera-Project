# Research Checkpoint Report

## Current Project Status

The project has moved from isolated spectral plotting into a structured validation pipeline for candidate residual spectral scaling. The current evidence supports residual-spectrum shape validation in selected windows, while preserving the central caveat that the full system remains low-k dominated and not globally stationary.

Run 004 remains the cleanest no-drag residual reference. Run 013 is the current best balanced combined-strategy case among the validated comparison set.

## Current Best Case by Objective

| Objective | Best current case | Reason |
|---|---|---|
| Cleanest residual spectral validation | Run 004 | Highest-quality residual reference; strongest validated no-drag k^-3-like window |
| Cleanest m=3 no-drag forcing case | Run 009 | Good residual quality without drag intervention |
| Strongest stationarity control | Run 011 | Lowest best-window energy growth among combined cases |
| Best balanced compromise | Run 013 | Intermediate stationarity improvement while preserving a residual k^-3-like shape |

These are residual-spectrum validation results, not evidence of a fully stationary enstrophy cascade. Peak domination remains severe, and the residual k^-3-like shape should be interpreted separately from full-system stationarity.

## Main Caveat

The main caveat remains unchanged: the validated spectral behavior is a residual-shape result, not a full-system stationarity result. Peak/low-k energy dominates the full spectrum, and total/peak energy growth has not been eliminated.

No fully stationary enstrophy cascade is claimed.

## Validation Chain Summary

The Run 004 validation chain established the core diagnostic standard used for later candidates:

| Diagnostic stage | Role in the chain |
|---|---|
| Initial slope fit | Identified Run 004 as a strong residual-slope candidate. |
| Time-stability analysis | Tested whether the candidate slope persisted across saved spectra. |
| Energy and peak-mode time series | Showed that total and peak energy continued growing. |
| Energy partition fractions | Identified severe low-k/peak domination. |
| Peak-masked residual spectrum | Checked whether the k^-3-like slope survived after masking the dominant peak band. |
| Compensated k^3 E(k) analysis | Tested for plateau-like residual behavior. |
| Stationarity-window analysis | Isolated the strongest quasi-stationary residual-shape window. |
| Window-local residual budget | Separated shape stability from energy stationarity. |
| Window sensitivity | Checked sensitivity to nearby time windows and fit ranges. |
| Residual exponent uncertainty | Reported an uncertainty band rather than a single exact exponent. |
| Signal-floor analysis | Verified that the fitted residual range was above numerical floor estimates. |
| Shell-support analysis | Checked radial shell population adequacy. |
| Leave-one-shell-out analysis | Checked that no individual shell controlled the fitted slope. |

This chain supports careful residual k^-3-like wording while avoiding stronger cascade claims.

## Forcing and Drag Findings

Run 004, with forcing amplitude 0.01, forcing mode 2, and no drag, produced the cleanest original residual validation:

- best window: saved indices 38:43, steps 38000:43000
- validated residual slope near k^-3
- strong R^2 and compensated-spectrum support
- severe low-k domination and nonstationary peak growth remain the limiting caveats

Low-k selective drag improved stationarity and peak-energy control but degraded residual spectral quality relative to Run 004. Among the combined m=3 drag cases, Run 011 gave the strongest stationarity control, but with weaker residual-shape metrics.

Forcing-mode redesign showed that Run 009, using forcing mode 3 with no drag, preserved residual spectral quality well and was cleaner than the lower-forcing m=2 redesign case. However, Run 009 only modestly improved stationarity.

The combined m=3 plus low-k drag strategy showed a real tradeoff:

- Run 010, alpha=0.10 and kmax=4, was effectively a null result because kmax=4 likely missed the shifted m=3 forcing reservoir.
- Run 011, alpha=0.10 and kmax=5, improved stationarity strongly but degraded residual spectral quality.
- Run 012, alpha=0.05 and kmax=5, preserved residual quality better than Run 011 but controlled stationarity less strongly.
- Run 013, alpha=0.075 and kmax=5, is currently the best balanced combined-strategy case.

Further alpha-only tuning is not immediately justified based on the current documentation. Speculative values 0.068, 0.065, and 0.072 remain speculative only unless a later review identifies a concrete unresolved bracket.

## Current Comparative Interpretation

| Case | Current interpretation |
|---|---|
| Run 004 | Cleanest residual reference; strongest no-drag validation, but poor stationarity and severe low-k domination. |
| Run 009 | Cleanest m=3 no-drag forcing case; good residual quality, but only modest stationarity improvement. |
| Run 011 | Strongest stationarity-control combined case; residual k^-3-like shape survives, but spectral quality is degraded. |
| Run 012 | Previous best balanced combined-strategy case before Run 013. |
| Run 013 | Current best balanced combined-strategy case; intermediate stationarity improvement with residual k^-3-like preservation. |

The project has not produced evidence for a fully stationary enstrophy cascade. It has produced a documented set of residual-shape validation results and a comparison framework for stationarity/residual-quality tradeoffs.

## Comparison Tool References

The validated-run consolidation checkpoint is captured by:

- `compare_validated_runs.py`
- `validated_run_comparison.csv`
- `validated_run_comparison.md`
- `validated_run_tradeoff_plot.png`

These artifacts compare Run 004, Run 009, Run 011, Run 012, and Run 013 using the documented metrics and caveats.

## Recommended Next Step

Pause new simulations and use the comparison checkpoint before deciding the next phase. The next phase should be chosen deliberately from the current documented tradeoff:

- longer integration of a selected case
- a stationarity-focused design change
- a forcing/drag strategy revision
- analysis architecture cleanup and reproducibility consolidation

Do not start another run until the comparison checkpoint has been reviewed and the next scientific question is explicit.

## Explicit Non-Claims

No Navier-Stokes proof is being made.

No fully stationary enstrophy cascade is being claimed.

No general turbulence law is being claimed.

The strongest supported result remains residual-spectrum validation: Run 004 shows a robust peak-masked residual k^-3-like spectral shape over steps 38000-43000, and Run 013 is the current best balanced combined-strategy case among the documented comparisons.
