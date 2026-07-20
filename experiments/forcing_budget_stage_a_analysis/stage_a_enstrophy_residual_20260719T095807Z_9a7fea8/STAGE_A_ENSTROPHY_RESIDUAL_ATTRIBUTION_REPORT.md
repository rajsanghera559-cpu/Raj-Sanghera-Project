# Stage A Enstrophy-Residual Archived-Evidence Analysis

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Stage A execution commit: `9a7fea8441f6e3fcdb63dcfc578e3008359f1ecc`
- Design commit: `f3f517578b0c9541d56dfb6968681f5884cc09a5`
- Created UTC: `2026-07-19T09:58:07+00:00`
- Analysis type: read-only analysis of archived CSV and JSON files
- Solver execution: none
- Numerical timestep execution: none
- Archived evidence modification: none
- Causal attribution claim: none

---

## 1. Stage A decision

> **ARCHIVED DATA SUPPORTS OPERATOR CORRELATION**

This is a descriptive archived-data classification. It does not causally identify the residual source.

The archived longer-run classification remains:

> **NOT STATIONARY WITHIN TESTED DURATION**

---

## 2. Source identities

| Archived file | SHA-256 |
|---|---|
| `run_metadata.json` | `57640568F657C26E47F495B1BE7C4C23F54EF0ACB882250ECB596A426F504ED9` |
| `forcing_budget.csv` | `38D01CE7278979EB4D7433414C849F65820C729DC5928A964FFED1EB3E4F482F` |
| `forcing_spectra.csv` | `62235ED6A5C9BD17D4FF21D22A1F830EE637FC22F26ABD43B483359B5873275A` |
| `stationarity_window.csv` | `FD1C5017DC24C6BF9F12F3BB56E44631491BA8178B174968743175976C06ED9A` |
| `stationarity_summary.json` | `3573F19100A4BD817B97C603B3C13D0137AD56D1F52FD05D602DFFC6400DBE1E` |
| `file_inventory.csv` | `3745C4E279E304A1A04CA14CEFE04BAA0FABD1A6072BB2E4C407FAB78CA1A028` |

---

## 3. Baseline that remains established

Independent of residual closure, the final-window enstrophy drift and injection-dissipation balance failed.

| Metric | Observed |
|---|---:|
| Enstrophy normalized drift | `0.18316303915302523` |
| Enstrophy balance metric | `0.3580633279251752` |
| Mean enstrophy injection | `0.0004056060526304712` |
| Mean enstrophy dissipation | `0.0006318474551695239` |

Therefore, improved residual closure would not by itself convert the archived result into a stationarity candidate.

---

## 4. Five-block residual statistics

| Block | Intervals | Median normalized Z residual | Maximum normalized Z residual | P90 | Mean max-stage advection RMS | Mean mask-removal RMS |
|---|---:|---:|---:|---:|---:|---:|
| 0.005 <= t <= 20.005 | 40 | 2.789087203069e-04 | 2.700022149106e-03 | 9.814021752291e-04 | 6.628695427082e-04 | 6.151237732597e-11 |
| 20.005 < t <= 40.005 | 40 | 4.888876394473e-03 | 9.912130778447e-03 | 8.908161925087e-03 | 3.258849186243e-03 | 1.311054732925e-07 |
| 40.005 < t <= 60.005 | 40 | 1.440422290564e-02 | 2.023276890965e-02 | 1.844136082239e-02 | 6.551067318627e-03 | 1.184460335485e-06 |
| 60.005 < t <= 80.005 | 40 | 4.092611197561e-02 | 5.853516373841e-02 | 5.848641595900e-02 | 1.364362790981e-02 | 2.964030433881e-06 |
| 80.005 < t <= 100.005 | 40 | 5.107587377270e-02 | 5.843424054746e-02 | 5.807526936974e-02 | 1.708971888483e-02 | 4.396942222349e-06 |

---

## 5. Strongest archived budget correlations

Target: `normalized_enstrophy_budget_residual`.

| Scope | Predictor | n | Pearson | Spearman | Largest absolute coefficient | Strength |
|---|---|---:|---:|---:|---:|---|
| all_budget_intervals | `viscous_enstrophy_dissipation_rate` | 200 | 9.411928619578e-01 | 9.919537988450e-01 | 9.919537988450e-01 | very strong |
| all_budget_intervals | `mean_viscous_enstrophy_dissipation_rate` | 200 | 9.423319696038e-01 | 9.915157878947e-01 | 9.915157878947e-01 | very strong |
| all_budget_intervals | `mask_removal_rms` | 200 | 9.771425932496e-01 | 9.871896797420e-01 | 9.871896797420e-01 | very strong |
| all_budget_intervals | `stage1_advection_rms` | 200 | 9.795878234418e-01 | 9.652156303908e-01 | 9.795878234418e-01 | very strong |
| all_budget_intervals | `max_stage_advection_rms` | 200 | 9.795826620460e-01 | 9.652156303908e-01 | 9.795826620460e-01 | very strong |
| all_budget_intervals | `stage2_advection_rms` | 200 | 9.795820370224e-01 | 9.652156303908e-01 | 9.795820370224e-01 | very strong |
| all_budget_intervals | `enstrophy` | 200 | 8.732093902283e-01 | 9.676951923798e-01 | 9.676951923798e-01 | very strong |
| all_budget_intervals | `vorticity_rms` | 200 | 8.034237480188e-01 | 9.676951923798e-01 | 9.676951923798e-01 | very strong |
| all_budget_intervals | `maximum_absolute_vorticity` | 200 | 7.813073944862e-01 | 9.099182479562e-01 | 9.099182479562e-01 | very strong |
| all_budget_intervals | `mean_continuous_enstrophy_rhs` | 200 | -7.864378735036e-01 | -5.088712217805e-01 | 7.864378735036e-01 | strong |

Correlation is descriptive. Advection RMS and mask-removal RMS are magnitudes, not exact enstrophy-work or mask-loss terms.

---

## 6. Spectral-tail correlations at exact matching times

| Scope | Predictor | n | Pearson | Spearman | Largest absolute coefficient | Strength |
|---|---|---:|---:|---:|---:|---|
| all_spectrum_matched_intervals | `tail_fraction_k_gt_4` | 40 | 9.572086115905e-01 | 9.692307692308e-01 | 9.692307692308e-01 | very strong |
| all_spectrum_matched_intervals | `low_k_fraction_k_le_4` | 40 | -9.572086115905e-01 | -9.692307692308e-01 | 9.692307692308e-01 | very strong |
| all_spectrum_matched_intervals | `middle_k_fraction_5_le_k_le_9` | 40 | 9.561153657732e-01 | 9.690431519700e-01 | 9.690431519700e-01 | very strong |
| all_spectrum_matched_intervals | `high_k_fraction_k_ge_10` | 40 | 9.341765413751e-01 | 9.658536585366e-01 | 9.658536585366e-01 | very strong |
| final_window_spectrum_matched_intervals | `high_k_fraction_k_ge_10` | 8 | 9.335473714543e-01 | 9.285714285714e-01 | 9.335473714543e-01 | very strong |
| final_window_spectrum_matched_intervals | `dominant_shell` | 8 | 7.574494643447e-01 | 7.559289460185e-01 | 7.574494643447e-01 | strong |
| all_spectrum_matched_intervals | `dominant_shell` | 40 | -4.896949733708e-01 | -4.124394700411e-01 | 4.896949733708e-01 | moderate |
| final_window_spectrum_matched_intervals | `middle_k_fraction_5_le_k_le_9` | 8 | -4.439818035333e-01 | -4.761904761905e-01 | 4.761904761905e-01 | moderate |
| final_window_spectrum_matched_intervals | `tail_fraction_k_gt_4` | 8 | -3.958020803010e-01 | -4.285714285714e-01 | 4.285714285714e-01 | moderate |
| final_window_spectrum_matched_intervals | `low_k_fraction_k_le_4` | 8 | 3.958020803010e-01 | 4.285714285714e-01 | 4.285714285714e-01 | moderate |

---

## 7. Offline cadence coarsening

All rows use the same archived trajectory. Only interval endpoint spacing changes.

| Cadence | Final-window intervals | Median normalized E residual | Maximum normalized E residual | Median normalized Z residual | Maximum normalized Z residual | Z median gate | Z max gate |
|---:|---:|---:|---:|---:|---:|---|---|
| 0.5 | 40 | 6.975630021169e-03 | 1.079090227795e-02 | 5.107587377270e-02 | 5.843424054746e-02 | FAIL | FAIL |
| 1.0 | 20 | 7.019499033126e-03 | 1.035811259799e-02 | 5.086705774076e-02 | 5.815445047309e-02 | FAIL | FAIL |
| 2.0 | 10 | 6.991089088174e-03 | 9.700398962356e-03 | 5.004046448508e-02 | 5.699742550686e-02 | FAIL | FAIL |
| 2.5 | 8 | 6.970483975053e-03 | 9.484656033755e-03 | 4.942944963444e-02 | 5.608938594352e-02 | FAIL | FAIL |
| 5.0 | 4 | 7.302787286196e-03 | 9.726550712215e-03 | 4.498671900393e-02 | 4.783416992652e-02 | FAIL | PASS |

This coarsening test can show whether residuals worsen when diagnostic intervals become wider. It cannot determine the sub-0.5 limit because no finer archived states exist.

---

## 8. Stage A support tests

### 8.1 Cadence sensitivity

- Supported: `False`
- Successive median increases: `0` of required `3`
- Coarsest/base final-window median factor: `0.8807821713267525` with required factor `1.25`

### 8.2 Operator-magnitude correlation

- Supported: `True`
- Correlation support threshold: `0.6`
- Strongest scope/predictor: `all_budget_intervals` / `mask_removal_rms`
- Largest absolute Pearson/Spearman coefficient: `0.9871896797419936`

---

## 9. What Stage A can and cannot resolve

Stage A can identify time dependence, coarsening sensitivity, and descriptive associations.

Stage A cannot directly calculate:

- discrete advection enstrophy work;
- exact pre-mask to post-mask enstrophy loss;
- RK2 local temporal error;
- residual behavior below the archived 0.5 cadence.

Those require the operator-ledger replay and same-state shadow tests defined in the archived design.

---

## 10. Final interpretation

The Stage A classification is **ARCHIVED DATA SUPPORTS OPERATOR CORRELATION**.

Regardless of that descriptive classification, the archived evidence already establishes genuine continuing modeled enstrophy evolution over the final window: enstrophy declined and mean dissipation exceeded mean injection.

No new numerical execution was performed.

---

## 11. Claim boundaries

This analysis does not establish:

- formal temporal convergence;
- formal spatial convergence;
- causal operator attribution;
- physical validation;
- turbulence;
- a cascade;
- an inertial range;
- a `k^-3` law;
- method superiority.

The next permitted task is design review for the exact operator ledger. No replay is authorized by this report.
