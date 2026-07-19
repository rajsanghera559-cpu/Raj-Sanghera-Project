# Phase 13 Exploratory Numerical Results and Closure

## Document control

- **Project:** Raj-Sanghera-Project
- **Document purpose:** Interpret the preserved Phase 13G.3 exploratory calibration summaries and close Phase 13 without restarting the audit chain.
- **Document type:** Descriptive numerical-results note and project closure decision
- **Preserved run:** `phase13G_calibration_20260718T083709Z_fa72085`
- **Authorized commit recorded by the run:** `fa720851bb23f43e9a69f0eb33775f04bd9a3130`
- **Authorized tag recorded by the run:** `v0.5.62-phase13G3B-calibration-runner-signature-remediation`
- **Runner SHA-256:** `2558DBB7B22BD5AA340916EAFE4C6FF61E077404F02D59AB96584D4DF494497D`
- **Analysis source:** the three uploaded root summary CSV files
- **Solver rerun:** no
- **Project file modified:** no
- **Full 390-file independent audit performed here:** no
- **Observed-order logarithm calculated:** no
- **Error-decay model fitted:** no
- **Formal convergence claim:** no
- **Method-superiority claim:** no
- **Physical-validation claim:** no
- **Phase 13H authorization:** no

---

## 1. Executive decision

The three uploaded summary tables are complete and internally suitable for descriptive interpretation:

- 77 unique case-summary rows;
- all 77 primary results marked finite;
- track counts of 9 O1, 15 O2, 5 L, and 48 M cases;
- aggregate totals of 850 RK2 steps, 1,632 advection calls, 1,700 diffusion calls, 1,608 Track M source evaluations, zero inherited forcing calls, and 850 post-step masks;
- 85 isolation-metric rows, all available and carrying no null reason;
- 140 floor-observation rows, consisting of 77 case observations and 63 adjacent-pair observations.

The numerical patterns are coherent and scientifically useful at the exploratory level:

1. `fd_centered` and `arakawa` show regular error reduction under grid refinement in O1, O2, and Track M.
2. O1 pseudo-spectral results are already at floating-point scale.
3. O2 pseudo-spectral error falls from `5.393724e-09` at N16 to floating-point scale at N32 and remains floor-dominated thereafter.
4. Track L remains at floating-point scale and is not a useful rate-estimation sequence.
5. Track M cleanly separates the dominant errors:
   - `fd_centered` and `arakawa` are spatial-error dominated over the tested fine-timestep sequences;
   - `pseudo_spectral` is temporal-error dominated over the tested N128/N256 sequences.

### Closure decision

> **Close Phase 13 at the exploratory code-verification and calibration-evidence level.**

The existing evidence should be retained and interpreted descriptively. The incomplete full independent audit of all 390 files and arrays is deferred. Phase 13G.4 and Phase 13H should not begin now.

---

## 2. Source-table identities

The uploaded files were identified by their column schemas rather than their temporary upload names.

| Role | Rows | Columns | SHA-256 |
|---|---|---|---|
| `calibration_case_summary.csv` | 77 | 21 | 8267C8690C6126CE82BFE73E6D40F124F80B9C9864AD607F2061412B2B06A81E |
| `calibration_isolation_metrics.csv` | 85 | 10 | D4675CBC6EEB4DB2634266EF882030A9269DC05984395C690FA29E184309939F |
| `calibration_floor_observations.csv` | 140 | 17 | 8F125F6CAC4B202169AC70FA96F152AB8C004D78D0904E45DB3CC8A991FEA6AF |

These hashes identify the uploaded copies used to create this report.

---

## 3. Interpretation boundary

This document uses the following deliberately limited language:

- **error reduction factor:** `E_coarse / E_fine`;
- **decrease observed:** the finer case has a smaller recorded error;
- **plateau-like:** the predeclared calibration label for adjacent positive errors with a ratio no greater than two;
- **floor-like:** the predeclared calibration label `R_eps <= 1e4`.

This report does **not**:

- calculate logarithmic observed order;
- select an asymptotic range;
- fit algebraic, spectral, or exponential models;
- create Richardson or Grid Convergence Index estimates;
- rank the three methods;
- treat exploratory Phase 13G.3 cases as formal Phase 13H evidence.

A regular fourfold reduction is reported as an observation. It is not converted into a formal order claim.

---

## 4. Dataset overview

| Track | Role | Cases |
|---|---|---|
| O1 | Resolved, band-limited nonlinear operator benchmark | 9 |
| O2 | Smooth analytic broad-spectrum operator benchmark | 15 |
| L | Exact linear viscous-decay evolution | 5 |
| M | Nonlinear manufactured full-evolution benchmark | 48 |
| **Total** |  | **77** |

### Aggregate runtime evidence

| Quantity | Recorded total |
|---|---|
| External RK2 steps | 850 |
| Advection calls | 1,632 |
| Diffusion calls | 1,700 |
| Track M source evaluations | 1,608 |
| Inherited forcing calls | 0 |
| Post-step mask applications | 850 |

All 77 case-summary rows report finite primary and secondary numerical quantities.

---

## 5. O1 resolved two-mode operator results

### 5.1 Recorded L2 errors

| Method | N16 | N32 | N64 | Relative L2 at N64 |
|---|---|---|---|---|
| fd_centered | 6.898904e-02 | 1.768397e-02 | 4.448674e-03 | 8.663606e-03 |
| pseudo_spectral | 1.091107e-15 | 2.448220e-15 | 6.071125e-15 | 1.182326e-14 |
| arakawa | 8.955452e-02 | 2.369994e-02 | 6.010247e-03 | 1.170470e-02 |

### 5.2 Adjacent grid-doubling reduction factors

| Method | N16/N32 | N32/N64 |
|---|---|---|
| fd_centered | 3.90122 | 3.97511 |
| pseudo_spectral | 0.445674 | 0.403256 |
| arakawa | 3.77868 | 3.94326 |

### 5.3 Interpretation

- `fd_centered` reductions are approximately `3.901` and `3.975`.
- `arakawa` reductions are approximately `3.779` and `3.943`.
- Both finite-difference-based sequences show regular error decrease under grid doubling.
- The pseudo-spectral errors are between `1.091107e-15` and `6.071125e-15`.
- All three pseudo-spectral O1 cases are classified as floor-like.
- The pseudo-spectral error increases slightly with N because the sequence is already controlled by floating-point effects rather than unresolved O1 modes.

**O1 conclusion:** O1 is useful for resolved-mode correctness and for showing regular finite-difference operator-error reduction. It cannot supply a useful pseudo-spectral decay sequence.

---

## 6. O2 analytic broad-spectrum operator results

### 6.1 Recorded L2 errors

| Method | N16 | N32 | N64 | N128 | N256 |
|---|---|---|---|---|---|
| fd_centered | 1.399159e-02 | 3.640892e-03 | 9.194415e-04 | 2.304410e-04 | 5.764662e-05 |
| pseudo_spectral | 5.393724e-09 | 7.811569e-16 | 1.682700e-15 | 3.829500e-15 | 7.006252e-15 |
| arakawa | 1.053152e-02 | 2.767056e-03 | 7.004859e-04 | 1.756720e-04 | 4.395249e-05 |

### 6.2 Adjacent grid-doubling reduction factors

| Method | 16/32 | 32/64 | 64/128 | 128/256 |
|---|---|---|---|---|
| fd_centered | 3.8429 | 3.9599 | 3.98992 | 3.99748 |
| pseudo_spectral | 6.905e+06 | 0.464228 | 0.439405 | 0.546583 |
| arakawa | 3.80604 | 3.9502 | 3.98746 | 3.99686 |

### 6.3 Compatibility projection

The largest absolute removed discrete mean across all 15 O2 cases is:

`6.591949e-17`

This is a floating-point-scale compatibility adjustment.

### 6.4 Interpretation

- `fd_centered` reduction factors progress from `3.843` to `3.997`.
- `arakawa` reduction factors progress from `3.806` to `3.997`.
- Those sequences become increasingly regular as N increases.
- The pseudo-spectral error drops by approximately `6.905e+06` between N16 and N32.
- Pseudo-spectral N32, N64, N128, and N256 are all classified as floor-like.
- The increase from N32 through N256 is a floating-point-floor effect, not a meaningful loss of continuum accuracy.

**O2 conclusion:** O2 provides the clearest operator-refinement evidence in the exploratory dataset. It shows regular grid-error reduction for `fd_centered` and `arakawa`, while the pseudo-spectral operator resolves the analytic field to floating-point scale by N32.

---

## 7. Track L exact viscous-decay results

| N | dt | Steps | L2 error | Relative L2 |
|---|---|---|---|---|
| 32 | 0.0005 | 16 | 1.120397e-15 | 1.120478e-15 |
| 64 | 0.004 | 2 | 1.586483e-14 | 1.586598e-14 |
| 64 | 0.002 | 4 | 4.478700e-15 | 4.479023e-15 |
| 64 | 0.001 | 8 | 2.313396e-15 | 2.313563e-15 |
| 64 | 0.0005 | 16 | 2.744506e-15 | 2.744704e-15 |

### 7.1 Isolation observations

| Metric | Comparison | Recorded value |
|---|---|---|
| `Delta_dt` | N64: dt .004 versus .002 | 1.138613e-14 |
| `Delta_dt` | N64: dt .002 versus .001 | 2.165304e-15 |
| `Delta_dt` | N64: dt .001 versus .0005 | 4.311099e-16 |
| `Delta_N` | N32 versus N64 at dt .0005 | 1.624109e-15 |

### 7.2 Interpretation

- Every Track L case is classified as floor-like.
- `R_eps` ranges only from approximately `5.05` to `71.45`.
- The error decreases from dt `.004` through `.001`, then rises slightly at dt `.0005`.
- That fine-level reversal is normal for a sequence already dominated by floating-point effects.
- The N32/N64 difference at dt `.0005` is also floating-point scale.

**Track L conclusion:** the linear diffusion/RK2 path and exact represented mode are reproduced at near-roundoff scale. Track L should be retained as a correctness and numerical-floor benchmark, not used for a formal rate estimate.

---

## 8. Track M nonlinear manufactured-evolution results

## 8.1 Spatial sequences at dt = 0.0005

| Method | N16 | N32 | N64 | N128 | N256 |
|---|---|---|---|---|---|
| fd_centered | 5.453124e-04 | 1.397805e-04 | 3.516478e-05 | 8.805796e-06 | 2.203188e-06 |
| pseudo_spectral | 1.519701e-09 | 1.519701e-09 | 1.519701e-09 | 1.519700e-09 | 1.519701e-09 |
| arakawa | 7.078834e-04 | 1.873367e-04 | 4.750903e-05 | 1.192073e-05 | 2.983784e-06 |

### Adjacent grid-doubling reduction factors

| Method | 16/32 | 32/64 | 64/128 | 128/256 |
|---|---|---|---|---|
| fd_centered | 3.90121 | 3.97501 | 3.99337 | 3.99684 |
| pseudo_spectral | 1 | 1 | 1 | 0.999999 |
| arakawa | 3.77867 | 3.94318 | 3.98541 | 3.99517 |

## 8.2 Spatial sequences at dt = 0.00025

| Method | N16 | N32 | N64 | N128 | N256 |
|---|---|---|---|---|---|
| fd_centered | 5.453115e-04 | 1.397796e-04 | 3.516390e-05 | 8.804916e-06 | 2.202308e-06 |
| pseudo_spectral | 3.799457e-10 | 3.799460e-10 | 3.799447e-10 | 3.799430e-10 | 3.799456e-10 |
| arakawa | 7.078825e-04 | 1.873357e-04 | 4.750810e-05 | 1.191980e-05 | 2.982849e-06 |

### Adjacent grid-doubling reduction factors

| Method | 16/32 | 32/64 | 64/128 | 128/256 |
|---|---|---|---|---|
| fd_centered | 3.90122 | 3.97509 | 3.99367 | 3.99804 |
| pseudo_spectral | 0.999999 | 1 | 1 | 0.999993 |
| arakawa | 3.77868 | 3.94324 | 3.98565 | 3.99611 |

### Spatial interpretation

- At both fine timesteps, `fd_centered` reduction factors progress from about `3.901` to almost `4.000`.
- At both fine timesteps, `arakawa` reduction factors progress from about `3.779` to almost `4.000`.
- The two timestep sequences are nearly indistinguishable for each finite-difference-based method.
- Pseudo-spectral error is nearly constant across N at each fixed timestep:
  - about `1.519700e-09` at dt `.0005`;
  - about `3.79945e-10` at dt `.00025`.
- The pseudo-spectral spatial differences are approximately `1e-15`, while the errors themselves are approximately `1e-9` or `1e-10`.

**Spatial conclusion:** the finite-difference and Arakawa sequences are spatially controlled over the tested fine timesteps. The pseudo-spectral sequence is not limited by spatial resolution over these grids.

---

## 8.3 Temporal sequences at N = 128

| Method | dt .004 | .002 | .001 | .0005 | .00025 |
|---|---|---|---|---|---|
| fd_centered | 8.879780e-06 | 8.823394e-06 | 8.809316e-06 | 8.805796e-06 | 8.804916e-06 |
| pseudo_spectral | 9.718300e-08 | 2.430690e-08 | 6.078113e-09 | 1.519700e-09 | 3.799430e-10 |
| arakawa | 1.199923e-05 | 1.193942e-05 | 1.192447e-05 | 1.192073e-05 | 1.191980e-05 |

### Adjacent timestep-halving reduction factors

| Method | .004/.002 | .002/.001 | .001/.0005 | .0005/.00025 |
|---|---|---|---|---|
| fd_centered | 1.00639 | 1.0016 | 1.0004 | 1.0001 |
| pseudo_spectral | 3.99816 | 3.99909 | 3.99955 | 3.99981 |
| arakawa | 1.00501 | 1.00125 | 1.00031 | 1.00008 |

## 8.4 Temporal sequences at N = 256

| Method | dt .004 | .002 | .001 | .0005 | .00025 |
|---|---|---|---|---|---|
| fd_centered | 2.277819e-06 | 2.220832e-06 | 2.206711e-06 | 2.203188e-06 | 2.202308e-06 |
| pseudo_spectral | 9.718300e-08 | 2.430690e-08 | 6.078113e-09 | 1.519701e-09 | 3.799456e-10 |
| arakawa | 3.062681e-06 | 3.002502e-06 | 2.987525e-06 | 2.983784e-06 | 2.982849e-06 |

### Adjacent timestep-halving reduction factors

| Method | .004/.002 | .002/.001 | .001/.0005 | .0005/.00025 |
|---|---|---|---|---|
| fd_centered | 1.02566 | 1.0064 | 1.0016 | 1.0004 |
| pseudo_spectral | 3.99816 | 3.99909 | 3.99955 | 3.99979 |
| arakawa | 1.02004 | 1.00501 | 1.00125 | 1.00031 |

### Temporal interpretation

- At N128 and N256, the pseudo-spectral error decreases almost exactly fourfold whenever dt is halved.
- The pseudo-spectral N128 and N256 errors are effectively identical at each dt.
- `fd_centered` and `arakawa` errors decrease only slightly when dt is halved and approach clear plateaus.
- Those plateaus are far above the arithmetic floor, so they are best interpreted as spatial-error plateaus rather than floating-point floors.

**Temporal conclusion:** the pseudo-spectral high-resolution sequence is temporally controlled over the tested range. The finite-difference and Arakawa high-resolution temporal sequences are spatial-error dominated.

---

## 8.5 Direct spatial/temporal isolation metrics

The design recorded:

- `C_t = Delta_t / Delta_h` for the fine spatial sequence;
- `C_h = Delta_N / Delta_dt` for the high-resolution temporal sequence.

### C_t at dt = 0.0005

| Method | N32 | N64 | N128 | N256 |
|---|---|---|---|---|
| fd_centered | 2.154198e-06 | 8.401098e-06 | 3.338800e-05 | 1.333561e-04 |
| pseudo_spectral | 2.365695e+06 | 1.870621e+06 | 1.276824e+06 | 9.981180e+05 |
| arakawa | 1.781253e-06 | 6.676208e-06 | 2.626915e-05 | 1.046532e-04 |

Interpretation:

- `fd_centered`: `C_t` remains below `1.34e-04`.
- `arakawa`: `C_t` remains below `1.05e-04`.
- For those two methods, changing dt from `.0005` to `.00025` changes the error by only a tiny fraction of the adjacent grid difference.
- Pseudo-spectral `C_t` is approximately `1e6` because the adjacent spatial differences are near floating-point scale while the timestep difference remains measurable.

### C_h at N = 256

| Method | dt .004 | .002 | .001 |
|---|---|---|---|
| fd_centered | 1.158495e+02 | 4.675879e+02 | 1.874066e+03 |
| pseudo_spectral | 1.137814e-09 | 1.606247e-08 | 1.471291e-07 |
| arakawa | 1.485013e+02 | 5.967029e+02 | 2.388763e+03 |

Interpretation:

- For `fd_centered`, `C_h` rises from approximately `116` to `1,874`.
- For `arakawa`, `C_h` rises from approximately `149` to `2,389`.
- Their N128/N256 difference is therefore much larger than the adjacent timestep difference.
- Pseudo-spectral `C_h` remains between approximately `1.14e-09` and `1.47e-07`.
- Its adjacent timestep difference is therefore overwhelmingly larger than the N128/N256 difference.

These two metric families independently support the same descriptive separation:

| Method | Dominant tested error |
|---|---|
| `fd_centered` | Spatial |
| `arakawa` | Spatial |
| `pseudo_spectral` | Temporal |

This statement is limited to the declared smooth Track M benchmark and tested ranges.

---

## 8.6 Finest declared Track M observations

At N256 and dt `.00025`:

| Method | L1 mean | L2 RMS | Linf | Relative L2 |
|---|---|---|---|---|
| fd_centered | 1.562611e-06 | 2.202308e-06 | 5.517808e-06 | 1.886764e-06 |
| pseudo_spectral | 3.134690e-10 | 3.799456e-10 | 9.115190e-10 | 3.255075e-10 |
| arakawa | 2.445726e-06 | 2.982849e-06 | 6.784404e-06 | 2.555471e-06 |

The pseudo-spectral error is much smaller on this smooth periodic manufactured benchmark. That is a benchmark-specific observation, not a general method ranking.

---

## 9. Numerical-floor and plateau map

## 9.1 Case-level floor-like classifications

| Track | Method | Floor-like cases | Minimum R_eps | Maximum R_eps |
|---|---|---|---|---|
| O1 | fd_centered | 0/3 | 2.003505e+13 | 3.106990e+14 |
| O1 | pseudo_spectral | 3/3 | 4.913908e+00 | 2.734191e+01 |
| O1 | arakawa | 0/3 | 2.706775e+13 | 4.033177e+14 |
| O2 | fd_centered | 0/5 | 2.596173e+11 | 6.301252e+13 |
| O2 | pseudo_spectral | 4/5 | 3.518018e+00 | 2.429117e+07 |
| O2 | arakawa | 0/5 | 1.979444e+11 | 4.742976e+13 |
| L | none | 5/5 | 5.045820e+00 | 7.144886e+01 |
| M | fd_centered | 0/16 | 8.497231e+09 | 2.103995e+12 |
| M | pseudo_spectral | 0/16 | 1.465946e+06 | 3.749642e+08 |
| M | arakawa | 0/16 | 1.150882e+10 | 2.731248e+12 |

Key points:

- All O1 pseudo-spectral cases are floor-like.
- O2 pseudo-spectral N32 through N256 are floor-like; N16 is not.
- All Track L cases are floor-like.
- No Track M case is arithmetic-floor-like under the exploratory `R_eps <= 1e4` label.
- The Track M pseudo-spectral errors remain above the arithmetic floor even when their spatial differences are near roundoff.

## 9.2 Adjacent-pair direction and plateau labels

| Track | Method | Plateau-like pairs | Decreases | Equals | Increases |
|---|---|---|---|---|---|
| O1 | fd_centered | 0/2 | 2 | 0 | 0 |
| O1 | pseudo_spectral | 0/2 | 0 | 0 | 2 |
| O1 | arakawa | 0/2 | 2 | 0 | 0 |
| O2 | fd_centered | 0/4 | 4 | 0 | 0 |
| O2 | pseudo_spectral | 1/4 | 1 | 0 | 3 |
| O2 | arakawa | 0/4 | 4 | 0 | 0 |
| L | none | 2/3 | 2 | 0 | 1 |
| M | fd_centered | 6/14 | 14 | 0 | 0 |
| M | pseudo_spectral | 8/14 | 10 | 0 | 4 |
| M | arakawa | 6/14 | 14 | 0 | 0 |

The plateau label must be interpreted with the source of the plateau:

- Track L plateaus are floating-point-floor effects.
- Track M `fd_centered` and `arakawa` temporal plateaus are spatial-error effects.
- Track M pseudo-spectral spatial plateaus are timestep-error effects.
- O1/O2 pseudo-spectral irregular directions beyond the floor are not evidence of deterioration.

---

## 10. Cross-track scientific synthesis

| Track | fd_centered | pseudo_spectral | arakawa | Primary interpretation |
|---|---|---|---|---|
| O1 | Regular grid-error decrease | Floating-point scale on all grids | Regular grid-error decrease | Resolved-mode operator correctness |
| O2 | Regular grid-error decrease | N16 truncation; floor by N32 | Regular grid-error decrease | Broad-spectrum operator refinement |
| L | Not method-specific | Not method-specific | Not method-specific | Near-roundoff diffusion/RK2 correctness |
| M spatial | Spatially controlled | Temporal plateau across N | Spatially controlled | Competing-error isolation |
| M temporal | Spatial plateau across dt | Regular fourfold dt reduction | Spatial plateau across dt | Competing-error isolation |

The most important result of Phase 13G.3 is not a universal method ranking. It is that the exploratory matrix successfully separated three regimes:

1. **arithmetic-floor regimes** — O1 pseudo-spectral, O2 pseudo-spectral after N32, and Track L;
2. **spatial-error-dominated regimes** — Track M `fd_centered` and `arakawa` at fine dt;
3. **temporal-error-dominated regimes** — high-resolution Track M pseudo-spectral cases.

That was the scientific purpose of the exploratory calibration.

---

## 11. Statements supported by the data

The following statements are supported:

1. All 77 declared exploratory cases completed with finite recorded errors.
2. The recorded aggregate solver-operation counts match the declared matrix.
3. No inherited forcing call occurred.
4. `fd_centered` and `arakawa` show regular error decrease under grid refinement on O1, O2, and Track M.
5. O1 pseudo-spectral and O2 pseudo-spectral from N32 onward operate at floating-point scale.
6. Track L operates at floating-point scale and is not a useful rate sequence.
7. Track M `fd_centered` and `arakawa` are spatial-error dominated over the tested fine-timestep sequences.
8. Track M pseudo-spectral is temporal-error dominated over the tested N128/N256 sequences.
9. Pseudo-spectral Track M error decreases almost fourfold under each timestep halving over the tested range.
10. These findings are benchmark-specific exploratory code-verification observations.

---

## 12. Statements not supported

This evidence does not establish:

- a formal spatial-convergence claim;
- a formal temporal-convergence claim;
- an observed numerical order;
- an asymptotic range;
- an uncertainty estimate;
- universal solver verification;
- method superiority;
- physical validation;
- turbulence;
- an inertial range;
- an enstrophy or inverse-energy cascade;
- a verified `k^-3` law;
- production readiness.

---

## 13. Relationship to the unfinished independent audit

This report analyzes only the three uploaded root summary tables.

It does not verify:

- every one of the 390 preserved file hashes;
- every case JSON record;
- every `fields.npz` archive;
- every array hash and statistic against its field manifest.

The two unsuccessful independent-audit scripts stopped because of incorrect assumptions about the emitted schema and Boolean semantics. They did not demonstrate a numerical failure.

The honest status remains:

> The 77-case numerical execution and root summary evidence are complete and descriptively interpretable. The full independent file-and-array audit is deferred.

---

## 14. Phase 13 closure decision

### Completed evidence

Phase 13 produced:

- a formal claim-language design;
- frozen benchmark equations and sign conventions;
- independently audited exact and manufactured references;
- an external verification-harness design;
- implemented verification modules;
- a successful independently audited 10-case runtime pilot;
- a completed 77-case exploratory calibration matrix;
- a recovered exact 390-path physical/Git inventory;
- the descriptive numerical interpretation recorded here.

### Deferred work

The following are deferred:

- a successful full independent audit of all 390 files and arrays;
- formal threshold freezing;
- formal pre-registration;
- formal refinement runs;
- formal observed-order calculation;
- formal convergence claims;
- physical validation.

### Final decision

> **Phase 13 closes at the exploratory verification and calibration-evidence level.**

Phase 13G.4 is not begun. Phase 13H is not authorized. No additional calibration rerun is needed.

---

## 15. Return to the broader research question

The verification program has now done enough to support continued research without becoming the research itself.

The broader project can return to:

> Can a controlled two-dimensional spectral-vorticity simulation produce a residual `k^-3`-like spectral shape, and can resolution, timestep, forcing, drag, stationarity-window, shell-support, peak-masking, and fitting-window tests distinguish a robust result from a numerical or analytical artifact?

Phase 13 improves confidence in the benchmarked numerical pathways. It does not answer the turbulence or spectral-law question by itself.

Future work should be organized around one scientific question and one decision at a time. Repository controls should support that work, not generate an indefinite chain of audits.

---

## 16. Final project status

- **Phase 12:** complete.
- **Phase 13A–13F:** complete within their declared scopes.
- **Phase 13G.1–13G.2:** complete as gap review and exploratory design.
- **Phase 13G.3 numerical execution:** complete.
- **Phase 13G.3 summary analysis:** complete in this document.
- **Phase 13G.3 full independent file/array audit:** deferred.
- **Phase 13G.4:** not begun.
- **Phase 13H:** not authorized.
- **Formal convergence:** not claimed.
- **Physical validation:** not performed.
- **Project recovery:** complete.
- **Next direction:** return to the broader research question under a simplified workflow.
