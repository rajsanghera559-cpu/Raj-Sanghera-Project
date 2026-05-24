# Experiment Log

| Run | Date | N | dt | nu | forcing f | steps | stable? | slope | output folder | notes |
|---|---|---:|---:|---:|---:|---:|---|---|---|---|
| 001 | 2026-05-20 | 256 | 0.0005 | 0.001 | 0.01 | 50000 | yes | -0.614 | outputs_nu_0.001 | Baseline completed run. Full spectra generated. |
| 002 | planned | 256 | 0.0005 | 0.0007 | 0.01 | 50000 | TBD | TBD | TBD | Planned viscosity sweep. |
| 003 | 2026-05-21 | TBD | TBD | 5e-05 | 0.006 | TBD | yes | TBD | outputs_spectra_refined/nu_5e-05_f_0.006_m_2 | Completed refined sweep run. Full spectra 00000-49000 present. |
| 004 | 2026-05-21 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | initial auto-fit: -2.791 | outputs_spectra_refined/nu_5e-05_f_0.01_m_2 | Missing case recovered and completed. Initial auto fit k=9:41, R^2=0.9665. Validated window result is the stronger checkpoint: slope=-3.0004 over saved indices 38:43, fit k=9:41. |
| 005 | 2026-05-22 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -3.0177 | outputs_lowk_drag_production/alpha_0.20_k4 | Low-k selective drag production candidate with lowk_drag_alpha=0.20, lowk_drag_kmax=4. Best window saved indices 36:40, steps 36000:40000, R^2=0.9434, compensated CV=0.2877. Final total/peak energy about 4.13% of Run 004, but residual spectral validation is less clean than Run 004. |
| 006 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -3.0121 | outputs_lowk_drag_production/alpha_0.15_k4 | Low-k selective drag production candidate with lowk_drag_alpha=0.15, lowk_drag_kmax=4. Best window saved indices 36:40, steps 36000:40000, R^2=0.9459, compensated CV=0.2870. Final total/peak energy about 7.07% of Run 004. Residual spectral quality is slightly better than alpha=0.20, but the improvement is marginal and alpha=0.20 has stronger low-k/peak-energy control. |
| 007 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -3.0176 | outputs_lowk_drag_kmax_tuning/alpha_0.20_k3 | Low-k selective drag cutoff-tuning candidate with lowk_drag_alpha=0.20, lowk_drag_kmax=3. Best window saved indices 36:40, steps 36000:40000, R^2=0.94335, compensated CV=0.28769. Final total/peak energy about 4.13% of Run 004. Effectively equivalent to alpha=0.20, kmax=4 in measured validation metrics. |
| 008 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.006 | 50000 | yes | best window: -2.9823 | outputs_forcing_redesign/f_0.006_m2_nodrag | Lower-forcing no-drag production candidate with forcing_mode=2. Best window saved indices 36:40, steps 36000:40000, R^2=0.9505, compensated CV=0.2828. Final total/peak energy about 36.0% of Run 004; final peak fraction=0.9999999964; best-window total energy growth +23.36%. Lower forcing reduces total/peak amplitude and preserves residual spectral quality reasonably well, but does not sufficiently improve stationarity or peak domination. |
| 009 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -3.0116 | outputs_forcing_redesign/f_0.01_m3_nodrag | Forcing-mode redesign no-drag production candidate with forcing_mode=3. Peak shifted to k=4 and mask k=3:5 was used. Best window saved indices 40:44, steps 40000:44000, R^2=0.9619, compensated CV=0.2366, leave-one-shell-out range [-3.1034, -2.9560]. Final total/peak amplitude about 43.9% of Run 004; final peak fraction=0.9999999964; best-window total energy growth +20.78%. Preserves residual k^-3-like spectral quality well, but only modestly improves stationarity. |
| 010 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -3.0120 | outputs_combined_strategy/f_0.01_m3_lowkdrag_0.10_k4 | Combined m=3 plus low-k drag candidate with lowk_drag_alpha=0.10, lowk_drag_kmax=4. Best window saved indices 40:44, steps 40000:44000, R^2=0.9620, compensated CV=0.2365, leave-one-shell-out range [-3.1033, -2.9564]. Final total energy ratio to Run 009 was 1.0000; best-window total energy growth +20.78%; final peak fraction=0.9999999989. Null combined-strategy result: effectively identical to Run 009 because kmax=4 likely misses the m=3 forced reservoir near |k|=sqrt(3^2+3^2)=4.24. |
| 011 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -3.0004 | outputs_combined_strategy/f_0.01_m3_lowkdrag_0.10_k5 | Combined m=3 plus low-k drag candidate with lowk_drag_alpha=0.10, lowk_drag_kmax=5. Best window saved indices 37:41, steps 37000:41000, R^2=0.9448, compensated CV=0.3022, leave-one-shell-out range [-3.0694, -2.9244]. Final total energy was 14.0% of Run 009 and 6.16% of Run 004; final peak fraction=0.9999999919; best-window total energy growth +6.80%. kmax=5 actually changes the m=3 dynamics and improves stationarity, but residual spectral quality worsens compared with Run 009. |
| 012 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -3.0217 | outputs_combined_strategy/f_0.01_m3_lowkdrag_0.05_k5 | Combined m=3 plus low-k drag candidate with lowk_drag_alpha=0.05, lowk_drag_kmax=5. Best window saved indices 38:42, steps 38000:42000, R^2=0.9504, compensated CV=0.2860, leave-one-shell-out range [-3.0992, -2.9695]. Final total energy was 33.4% of Run 009 and 14.7% of Run 004; final peak fraction=0.9999999961; best-window total energy growth +12.23%. Improves stationarity versus Run 009 while preserving residual spectral quality better than alpha=0.10/kmax=5; previous best balanced combined-strategy case before Run 013. |
| 013 | 2026-05-23 | 256 | 0.0005 | 5e-05 | 0.01 | 50000 | yes | best window: -2.9916 | outputs_combined_strategy/f_0.01_m3_lowkdrag_0.075_k5 | Combined m=3 plus low-k drag midpoint candidate with lowk_drag_alpha=0.075, lowk_drag_kmax=5. Best window saved indices 37:41, steps 37000:41000, R^2=0.9466, compensated CV=0.2962, leave-one-shell-out range [-3.0624, -2.9277], min leave-one-out R^2=0.9441. Final total energy was 21.07% of Run 009 and 9.25% of Run 004; final total energy was 63.12% of alpha=0.05/kmax=5 and 150.26% of alpha=0.10/kmax=5. Signal-floor final fit/tail ratio=4.91e14; best-window total energy growth +9.38%. Improves stationarity versus alpha=0.05/kmax=5, preserves residual spectral quality slightly better than alpha=0.10/kmax=5, and is currently the best balanced combined-strategy case. |

## Questions

### Verification
- Does slope stabilize?
- Does rerun agree?
- Does nu sweep behave smoothly?
- Do outputs organize naturally?
- What artifact could fool us?
- What result would remain unchanged if rerun tomorrow?
- Does the apparent -3 slope survive after masking the dominant peak band?
- Does the residual k^-3-like result survive small changes in time window and fit range?

### Physics
- Is forcing dominating the spectrum?
- Is transfer broadening?
- Is energy accumulating?
- Is there evidence of stationarity?

### Numerical
- Does increasing N change conclusions?
- Is CFL bounded?
- Are spectra reproducible?
- Is this physics or numerical diffusion?

---

## Future

### Diagnostics
- Add convergence tracking
- Add spectrum comparison
- Add parameter sweep summary
- Add uncertainty estimates
- Add peak-masked normalized spectrum analysis
- Add window-sensitivity analysis

### Infrastructure
- Archive completed runs
- Add experiment metadata
- Organize outputs by run
- Separate active vs archived outputs

### Long-term
- Spectral transfer analysis
- Validation workflow
- Statistical averaging
- Reproducibility checks

---

## Definitions

baseline:
Reference run used for comparison

stable:
No NaN, no blow-up, bounded diagnostics

converged:
Result changes minimally under refinement

reproducible:
Independent rerun gives similar result

artifact:
Observed structure caused by numerics, not physics

stationarity:
Statistics stop drifting significantly

validated:
Agreement with expected behavior, independent checks, or controlled comparison

---

## Current Status

Project Phase:
Experimental Infrastructure

Current Goal:
Verify numerical behavior before interpretation

Current Baseline:
Run 001 (N=256, dt=0.0005, nu=0.001)

Current Active Work:
Combined-strategy checkpoint updated with m=3, alpha=0.075, kmax=5 result; maintain review-first posture before any new simulations.

Current Interpretation:
Run 004 shows a robust peak-masked residual k^-3-like spectral shape over steps 38000-43000. Low-k selective drag improves stationarity and peak-energy behavior while preserving a residual k^-3-like range, but the residual spectral shape is less clean than the no-drag Run 004 case. Forcing_mode=3 preserves residual k^-3-like spectral quality well and is cleaner than the lower-forcing f=0.006 case and low-k drag by residual-shape metrics, but it only modestly improves stationarity. The combined m=3, alpha=0.075, kmax=5 case improves stationarity versus alpha=0.05/kmax=5 and preserves residual spectral quality slightly better than alpha=0.10/kmax=5. It is currently the best balanced combined-strategy case. Further alpha-only tuning is not immediately justified. None of these cases is evidence of a validated stationary enstrophy cascade.

Current Best Candidate:
Run 004, nu=5e-05, f=0.01

Current Best Window:
saved indices 38:43, steps 38000:43000

Run 004 Validation Checkpoint:
- Fit range: k=9:41
- Validated window slope: -3.0004 over saved indices 38:43
- Baseline shell-summed slope: -3.0004
- R^2: 0.9668
- Residual exponent uncertainty: -3.00 +/- 0.15
- Leave-one-shell-out slope range: [-3.0778, -2.9517]
- Minimum leave-one-shell-out R^2: 0.9631
- Signal-floor check: fit range safely above numerical floor
- Shell support: adequate, min shell count 56, median 160
- Main caveat: full spectrum remains low-k dominated and nonstationary in total energy

Low-k Drag Production Checkpoint:
- Alpha=0.20 case: output folder outputs_lowk_drag_production/alpha_0.20_k4; analysis folder outputs_lowk_drag_production/analysis
- Alpha=0.20 best window: saved indices 36:40, steps 36000:40000
- Alpha=0.20 mean slope: -3.0177
- Alpha=0.20 mean R^2: 0.9434
- Alpha=0.20 compensated CV: 0.2877
- Alpha=0.20 leave-one-shell-out slope range: [-3.1203, -2.9461]
- Alpha=0.20 signal-floor check: safely above tail; final fit/tail ratio 1.93e13
- Alpha=0.20 final total/peak energy: about 4.13% of Run 004
- Alpha=0.20 best-window total/peak energy growth: +1.85%
- Alpha=0.15 case: output folder outputs_lowk_drag_production/alpha_0.15_k4; analysis folder outputs_lowk_drag_production/analysis_alpha_0.15_k4
- Alpha=0.15 best window: saved indices 36:40, steps 36000:40000
- Alpha=0.15 mean slope: -3.0121
- Alpha=0.15 mean R^2: 0.9459
- Alpha=0.15 compensated CV: 0.2870
- Alpha=0.15 leave-one-shell-out slope range: [-3.1122, -2.9463]
- Alpha=0.15 final total/peak energy: about 7.07% of Run 004
- Alpha=0.15 best-window total/peak energy growth: +3.75%
- Alpha=0.20, kmax=3 case: output folder outputs_lowk_drag_kmax_tuning/alpha_0.20_k3; analysis folder outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3
- Alpha=0.20, kmax=3 summary: outputs_lowk_drag_kmax_tuning/analysis_alpha_0.20_k3/kmax3_validation_summary.csv
- Alpha=0.20, kmax=3 best window: saved indices 36:40, steps 36000:40000
- Alpha=0.20, kmax=3 mean slope: -3.0176
- Alpha=0.20, kmax=3 mean R^2: 0.94335
- Alpha=0.20, kmax=3 compensated CV: 0.28769
- Alpha=0.20, kmax=3 leave-one-shell-out slope range: [-3.1203, -2.9461]
- Alpha=0.20, kmax=3 final total/peak energy: about 4.13% of Run 004
- Alpha=0.20, kmax=3 best-window total/peak energy growth: +1.85%
- Alpha=0.20, kmax=3 interpretation: does not improve residual spectral quality versus kmax=4 and remains effectively equivalent to alpha=0.20, kmax=4
- Low-k drag advantage: better low-k/peak-energy control than Run 004
- Low-k drag caveat: residual spectral validation is less clean than Run 004
- Interpretation: alpha/cutoff tuning shows diminishing returns and does not justify another immediate drag-parameter run. Do not recommend immediate kmax=5.

Forcing Redesign Checkpoint:
- Lower-forcing case: output folder outputs_forcing_redesign/f_0.006_m2_nodrag; analysis folder outputs_forcing_redesign/analysis_f_0.006_m2_nodrag
- Lower-forcing summary: outputs_forcing_redesign/analysis_f_0.006_m2_nodrag/forcing_f006_validation_summary.csv
- Parameters: forcing_amplitude=0.006, forcing_mode=2, no drag
- Best window: saved indices 36:40, steps 36000:40000
- Mean slope: -2.9823
- Mean R^2: 0.9505
- Compensated CV: 0.2828
- Final total/peak energy: about 36.0% of Run 004
- Final peak fraction: 0.9999999964
- Best-window total energy growth: +23.36%
- Interpretation: lower forcing reduces total/peak amplitude versus Run 004 and preserves residual spectral quality reasonably well, but it does not sufficiently improve stationarity or peak domination. Low-k drag remains stronger for stationarity control. The next forcing-redesign test should be forcing_mode=3.
- Forcing_mode=3 case: output folder outputs_forcing_redesign/f_0.01_m3_nodrag; analysis folder outputs_forcing_redesign/analysis_f_0.01_m3_nodrag
- Parameters: forcing_amplitude=0.01, forcing_mode=3, no drag
- Peak shifted to k=4; mask used k=3:5
- Best window: saved indices 40:44, steps 40000:44000
- Mean slope: -3.0116
- Mean R^2: 0.9619
- Compensated CV: 0.2366
- Leave-one-shell-out slope range: [-3.1034, -2.9560]
- Signal-floor final fit/tail ratio: 4.47e14
- Shell support min count: 56
- Final total/peak amplitude: about 43.9% of Run 004
- Final peak fraction: 0.9999999964
- Best-window total energy growth: +20.78%
- Interpretation: forcing_mode=3 preserves residual k^-3-like spectral quality well and is cleaner than lower forcing f=0.006 and low-k drag by residual-shape metrics, but it only modestly improves stationarity. Low-k drag alpha=0.20 remains stronger for peak-energy control. The next direction should be combined strategy planning, not another pure forcing-only run.
- Combined m=3 low-k drag case: output folder outputs_combined_strategy/f_0.01_m3_lowkdrag_0.10_k4; analysis folder outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k4
- Parameters: forcing_amplitude=0.01, forcing_mode=3, lowk_drag_alpha=0.10, lowk_drag_kmax=4
- Best window: saved indices 40:44, steps 40000:44000
- Mean slope: -3.0120
- Mean R^2: 0.9620
- Compensated CV: 0.2365
- Leave-one-shell-out slope range: [-3.1033, -2.9564]
- Signal-floor final fit/tail ratio: 4.47e14
- Final total energy ratio to Run 009: 1.0000
- Best-window total energy growth: +20.78%
- Final peak fraction: 0.9999999989
- Interpretation: this is a null combined-strategy result. It is effectively identical to Run 009. Likely reason: forcing_mode=3 injects near |k|=sqrt(3^2+3^2) ~= 4.24, while lowk_drag_kmax=4 does not include that forced peak. Therefore this run did not meaningfully test low-k drag on the shifted m=3 forcing reservoir. The next valid combined test, if continuing, should use lowk_drag_kmax=5 with alpha=0.10.
- Combined m=3 kmax=5 case: output folder outputs_combined_strategy/f_0.01_m3_lowkdrag_0.10_k5; analysis folder outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.10_k5
- Parameters: forcing_amplitude=0.01, forcing_mode=3, lowk_drag_alpha=0.10, lowk_drag_kmax=5
- Best window: saved indices 37:41, steps 37000:41000
- Mean slope: -3.0004
- Mean R^2: 0.9448
- Compensated CV: 0.3022
- Leave-one-shell-out slope range: [-3.0694, -2.9244]
- Signal-floor final fit/tail ratio: 5.40e14
- Final total energy: 14.0% of Run 009 and 6.16% of Run 004
- Final peak fraction: 0.9999999919
- Best-window total energy growth: +6.80%
- Interpretation: kmax=5 actually changes the m=3 dynamics, unlike kmax=4. Stationarity improves substantially versus Run 009 and the residual k^-3 slope survives, but residual spectral quality worsens compared with Run 009. This is a real but imperfect combined compromise. The gentler alpha=0.05/kmax=5 candidate was later completed as Run 012.
- Combined m=3 alpha=0.05 kmax=5 case: output folder outputs_combined_strategy/f_0.01_m3_lowkdrag_0.05_k5; analysis folder outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.05_k5
- Parameters: forcing_amplitude=0.01, forcing_mode=3, lowk_drag_alpha=0.05, lowk_drag_kmax=5
- Best window: saved indices 38:42, steps 38000:42000
- Mean slope: -3.0217
- Mean R^2: 0.9504
- Compensated CV: 0.2860
- Leave-one-shell-out slope range: [-3.0992, -2.9695]
- Signal-floor final fit/tail ratio: 4.77e14
- Final total energy: 33.4% of Run 009 and 14.7% of Run 004
- Final peak fraction: 0.9999999961
- Best-window total energy growth: +12.23%
- Interpretation: alpha=0.05/kmax=5 improves stationarity versus Run 009 and preserves residual spectral quality better than alpha=0.10/kmax=5. It was the previous best balanced combined-strategy case before Run 013. The alpha=0.075/kmax=5 midpoint candidate has now been completed and documented as Run 013.
- Combined m=3 alpha=0.075 kmax=5 case: output folder outputs_combined_strategy/f_0.01_m3_lowkdrag_0.075_k5; analysis folder outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5
- Summary artifact: outputs_combined_strategy/analysis_f_0.01_m3_lowkdrag_0.075_k5/combined_validation_summary.csv
- Parameters: forcing_amplitude=0.01, forcing_mode=3, lowk_drag_alpha=0.075, lowk_drag_kmax=5
- Best window: saved indices 37:41, steps 37000:41000
- Mean slope: -2.9916
- Mean R^2: 0.9466
- Compensated CV: 0.2962
- Leave-one-shell-out slope range: [-3.0624, -2.9277]
- Minimum leave-one-out R^2: 0.9441
- Signal-floor final fit/tail ratio: 4.91e14
- Final total energy: 21.07% of Run 009 and 9.25% of Run 004
- Final total energy versus alpha=0.05/kmax=5: 63.12%
- Final total energy versus alpha=0.10/kmax=5: 150.26%
- Best-window total energy growth: +9.38%
- Interpretation: alpha=0.075/kmax=5 improves stationarity versus alpha=0.05/kmax=5 and preserves residual spectral quality slightly better than alpha=0.10/kmax=5. It is currently the best balanced combined-strategy case. Further alpha-only tuning is not immediately justified.
- Speculative future alpha-only refinement values: 0.068, 0.065, and 0.072. These should remain speculative unless a later documentation review identifies a concrete unresolved bracket.

Last Confirmed Completed Run:
Run 013

Next Review Trigger:
Review Run 013 documentation before deciding whether any speculative alpha-only refinement is justified.

Current Rule:
Observe -> Verify -> Compare -> Interpret

Decision Priority:
Numerics -> Validation -> Interpretation -> Conclusions

Not Claiming:
- Solved Navier-Stokes
- New turbulence law
- Continuum replacement
- Physical conclusions beyond measured outputs

---

## Review Checklist

Before interpreting a result:

[ ] Run completed

[ ] Outputs saved

[ ] No NaN or blow-up

[ ] Spectra generated

[ ] Comparison available

[ ] Baseline checked

[ ] Notes written

[ ] Question recorded

[ ] Interpretation delayed until review

