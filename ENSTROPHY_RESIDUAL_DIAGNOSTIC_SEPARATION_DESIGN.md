# Enstrophy-Residual Diagnostic Separation Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Source checkpoint: `866ad40`
- Evidence archive checkpoint: `2ce245b`
- Longer-test design checkpoint: `3af047b`
- Longer-test runner checkpoint: `9a9f2e0`
- Run ID:
  `forcing_budget_stationarity_20260719T083403Z_9a9f2e0`
- Created UTC: `2026-07-19T08:57:55+00:00`
- Document type: design only
- New numerical execution authorized: no
- Existing run modification authorized: no
- Existing evidence replacement authorized: no
- Automatic rerun authorized: no
- Formal convergence claim: none
- Physical-validation claim: none
- Turbulence claim: none
- Cascade claim: none
- Inertial-range claim: none
- `k^-3` claim: none
- Method-superiority claim: none

---

## 1. Purpose

This document defines a controlled investigation of why the longer
forcing-budget test failed the prospectively specified enstrophy-residual
gates.

The investigation separates five possible contributors:

1. budget sampling cadence and interval quadrature;
2. discrete advection nonconservation;
3. dealiasing-mask removal;
4. RK2 temporal-discretization error;
5. genuine continuing enstrophy evolution.

The design distinguishes two different scientific questions:

### Question A — residual attribution

Why does

\[
\frac{dZ}{dt}
-
\left(
\eta_f-D_Z
\right)
\]

remain nonzero in the stored interval diagnostic?

### Question B — stationarity attribution

Why did the flow fail the enstrophy drift and injection-dissipation balance
criteria over the fixed final window?

Genuine continuing evolution can explain Question B without necessarily
explaining the numerical residual in Question A.

This distinction must be preserved throughout the investigation.

---

## 2. Archived baseline result

The completed longer run used:

| Parameter | Value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Completed updates | `20001` |
| Final time | `100.005` |
| Budget sampling interval | `0.5` |
| Spectrum sampling interval | `2.5` |
| Stationarity window | `80.005` through `100.005` |

The archived classification was:

> `NOT STATIONARY WITHIN TESTED DURATION`

The energy residual gates passed:

| Metric | Observed | Limit |
|---|---:|---:|
| Median normalized energy residual | `0.006975630021169467` | `0.01` |
| Maximum normalized energy residual | `0.010790902277951337` | `0.05` |

The enstrophy residual gates failed:

| Metric | Observed | Limit |
|---|---:|---:|
| Median normalized enstrophy residual | `0.05107587377269546` | `0.01` |
| Maximum normalized enstrophy residual | `0.05843424054745961` | `0.05` |

Independent enstrophy stationarity gates also failed:

| Metric | Observed | Limit |
|---|---:|---:|
| Enstrophy normalized drift | `0.18316303915302523` | `0.05` |
| Enstrophy balance metric | `0.3580633279251752` | `0.10` |

The numerical-integrity gates passed.

---

## 3. Baseline interpretation that must not be lost

The enstrophy-residual failure is not the sole reason the run was classified
as nonstationary.

Even if the residual gates had passed, the following would still have failed:

- enstrophy normalized drift;
- enstrophy injection-dissipation balance.

The final-window means were:

\[
\overline{\eta_f}
=
0.0004056060526304712,
\]

\[
\overline{D_Z}
=
0.0006318474551695239,
\]

so

\[
\overline{\eta_f-D_Z}
=
-0.00022624140253905267.
\]

The fitted enstrophy slope was

\[
b_Z
=
-0.00020722204413126485.
\]

Their difference was approximately

\[
1.90194\times10^{-5},
\]

which is about `3.01%` of the larger mean injection/dissipation scale.

This shows two simultaneous facts:

1. the enstrophy was genuinely declining;
2. the stored discrete interval balance did not close to the prospective
   residual tolerance.

The investigation must quantify both facts separately.

---

## 4. Competing hypotheses

### H1 — sampling-cadence and quadrature hypothesis

The `0.5` time-unit output spacing is too coarse for the trapezoidal estimate
of the mean continuous RHS.

Expected signature:

- residual decreases systematically when computed from finer diagnostic
  sampling on the same numerical trajectory;
- state evolution is unchanged;
- discrete operator-ledger terms do not account for most of the discrepancy.

### H2 — discrete-advection hypothesis

The centered-difference advection operator is not exactly
enstrophy-conserving under the solver's discrete inner product.

Expected signature:

- the stage-based discrete advection enstrophy work is nonzero;
- its magnitude and sign correlate with the residual;
- removing the advection contribution from the ledger materially improves
  closure.

### H3 — dealiasing-mask hypothesis

The post-step spectral mask removes a measurable amount of enstrophy that is
not included in the continuous forcing-plus-viscosity RHS.

Expected signature:

- the exact pre-mask to post-mask enstrophy change is non-negligible;
- adding that exact mask-loss term materially reduces the residual;
- mask loss grows as higher-wave-number content develops.

### H4 — RK2 temporal-error hypothesis

The residual contains finite-timestep error from the two-stage update and
nonlinear operator coupling.

Expected signature:

- matched local shadow integrations from the same stored state show residual
  reduction as `dt` is halved;
- the reduction persists after accounting for advection work and mask loss;
- the residual approaches a smaller limiting value with fixed physical
  diagnostic interval.

### H5 — genuine-evolution hypothesis

The enstrophy channel is still physically and numerically evolving under the
tested model, independent of residual closure.

Expected signature:

- the mean continuous enstrophy RHS remains materially negative;
- enstrophy trends remain negative under finer diagnostic sampling;
- injection remains below dissipation;
- residual closure may improve while drift and imbalance still fail.

H5 concerns nonstationarity. H1 through H4 concern residual attribution.

---

## 5. Investigation strategy

The investigation shall proceed in the following order:

1. read-only analysis of the archived evidence;
2. design of an operator-resolved diagnostic ledger;
3. one prospective high-cadence replay design;
4. local same-state timestep shadow tests;
5. attribution decision.

No new execution is authorized by this document.

Each later execution requires a separate runner, static inspection, archive
checkpoint, and explicit authorization.

---

## 6. Stage A — read-only archived-evidence analysis

### 6.1 Objective

Extract every conclusion available from the existing six-file evidence bundle
without rerunning the solver.

### 6.2 Required inputs

- `forcing_budget.csv`;
- `forcing_spectra.csv`;
- `stationarity_window.csv`;
- `stationarity_summary.json`;
- `run_metadata.json`;
- `file_inventory.csv`.

### 6.3 Required residual time-series analysis

For all 200 noninitial budget intervals, calculate and plot or tabulate:

- absolute enstrophy residual;
- normalized enstrophy residual;
- absolute energy residual;
- normalized energy residual;
- observed enstrophy rate;
- mean continuous enstrophy RHS;
- enstrophy injection;
- enstrophy dissipation;
- stage-1 advection RMS;
- stage-2 advection RMS;
- mask-removal RMS;
- physical time.

### 6.4 Required correlations

Calculate Pearson and rank correlations between normalized enstrophy residual
and:

- stage-1 advection RMS;
- stage-2 advection RMS;
- mask-removal RMS;
- enstrophy;
- absolute observed enstrophy rate;
- absolute mean continuous enstrophy RHS;
- enstrophy injection;
- enstrophy dissipation;
- high-wave-number energy fraction;
- tail fraction at `k>4`.

Spectral values may be joined only at matching spectrum times.

Correlation is descriptive and does not prove causation.

### 6.5 Required window splits

Report residual statistics over:

1. `0.005 <= t <= 20.005`;
2. `20.005 < t <= 40.005`;
3. `40.005 < t <= 60.005`;
4. `60.005 < t <= 80.005`;
5. `80.005 < t <= 100.005`.

For each interval report:

- median;
- mean;
- maximum;
- 90th percentile;
- sign distribution;
- corresponding mean advection RMS;
- corresponding mean mask-removal RMS.

### 6.6 Coarsening study from archived data

Starting from the stored `0.5` cadence, recompute interval residuals using
coarsened spacings:

- `1.0`;
- `2.0`;
- `2.5`;
- `5.0`.

Use exact endpoint alignment.

This test can show whether residuals worsen under coarsening.

It cannot establish the fine-cadence limit because no spacing below `0.5`
exists in the archive.

### 6.7 Stage-A decision

Stage A shall end with one of:

- `ARCHIVED DATA SUPPORTS CADENCE SENSITIVITY`;
- `ARCHIVED DATA SUPPORTS OPERATOR CORRELATION`;
- `ARCHIVED DATA INCONCLUSIVE`;
- `ARCHIVED DATA SHOWS MULTIPLE CONTRIBUTORS`.

No causal attribution is authorized from Stage A alone.

---

## 7. Stage B — exact discrete operator ledger design

### 7.1 Objective

Separate the enstrophy change produced by:

- forcing;
- viscosity;
- discrete advection;
- RK2 coupling;
- post-step spectral masking.

### 7.2 Per-step states

For each selected diagnostic step, retain:

- current state `w_n`;
- RK2 stage state `w_stage`;
- unfiltered RK2 state `w_unfiltered`;
- filtered accepted state `w_{n+1}`.

These arrays are diagnostic temporaries and need not all be written to disk.

### 7.3 Stage operator components

At stage 1 record:

\[
A_1=-u_n\partial_xw_n-v_n\partial_yw_n,
\]

\[
V_1=\nu\nabla^2w_n,
\]

\[
F_1=f_\omega.
\]

At stage 2 record:

\[
A_2=-u_s\partial_xw_s-v_s\partial_yw_s,
\]

\[
V_2=\nu\nabla^2w_s,
\]

\[
F_2=f_\omega.
\]

The current implementation uses time-independent forcing, so `F_1=F_2`.

### 7.4 Stage-based enstrophy-work estimates

Record:

\[
W_{A,1}=\langle w_nA_1\rangle,
\qquad
W_{A,2}=\langle w_sA_2\rangle,
\]

\[
W_{V,1}=\langle w_nV_1\rangle,
\qquad
W_{V,2}=\langle w_sV_2\rangle,
\]

\[
W_{F,1}=\langle w_nF_1\rangle,
\qquad
W_{F,2}=\langle w_sF_2\rangle.
\]

Define RK2 stage-weighted estimates:

\[
W_A^{RK2}
=
\frac{1}{2}(W_{A,1}+W_{A,2}),
\]

\[
W_V^{RK2}
=
\frac{1}{2}(W_{V,1}+W_{V,2}),
\]

\[
W_F^{RK2}
=
\frac{1}{2}(W_{F,1}+W_{F,2}).
\]

These are diagnostic ledger terms, not an assumption of exact additive
decomposition.

### 7.5 Exact mask contribution

Calculate the exact post-update mask contribution:

\[
\Delta Z_{\mathrm{mask}}
=
Z(w_{n+1})-Z(w_{\mathrm{unfiltered}}).
\]

Define its rate:

\[
R_{\mathrm{mask}}
=
\frac{\Delta Z_{\mathrm{mask}}}{dt}.
\]

For a dissipative mask, this term is expected to be nonpositive.

Also record exact energy mask loss.

### 7.6 Exact discrete step change

Calculate:

\[
R_Z^{\mathrm{step}}
=
\frac{Z(w_{n+1})-Z(w_n)}{dt}.
\]

Calculate the unfiltered step rate:

\[
R_Z^{\mathrm{unfiltered}}
=
\frac{Z(w_{\mathrm{unfiltered}})-Z(w_n)}{dt}.
\]

Then verify exactly, to roundoff:

\[
R_Z^{\mathrm{step}}
=
R_Z^{\mathrm{unfiltered}}
+
R_{\mathrm{mask}}.
\]

### 7.7 Operator-ledger residuals

Define:

\[
R_{\mathrm{ledger,unfiltered}}
=
R_Z^{\mathrm{unfiltered}}
-
\left(
W_A^{RK2}+W_V^{RK2}+W_F^{RK2}
\right),
\]

and

\[
R_{\mathrm{ledger,filtered}}
=
R_Z^{\mathrm{step}}
-
\left(
W_A^{RK2}+W_V^{RK2}+W_F^{RK2}
+R_{\mathrm{mask}}
\right).
\]

These terms measure remaining RK2/nonlinear cross-term effects and any ledger
approximation error.

### 7.8 Discrete-advection attribution metric

Define:

\[
C_A
=
\frac{|W_A^{RK2}|}
{\max(
|R_Z^{\mathrm{step}}|,
|W_F^{RK2}|,
|W_V^{RK2}|,
10^{-30}
)}.
\]

Also calculate the fraction of the original residual removed after adding
the advection ledger term.

### 7.9 Mask attribution metric

Define:

\[
C_M
=
\frac{|R_{\mathrm{mask}}|}
{\max(
|R_Z^{\mathrm{step}}|,
|W_F^{RK2}|,
|W_V^{RK2}|,
10^{-30}
)}.
\]

Also calculate the fraction of the original residual removed after adding
the exact mask term.

---

## 8. Stage C — high-cadence same-trajectory replay design

### 8.1 Objective

Test whether the `0.5` output cadence is responsible for a substantial part
of the stored interval residual.

### 8.2 Frozen numerical trajectory

Use the same:

- grid;
- Reynolds number;
- viscosity;
- timestep;
- step count;
- initial condition;
- forcing field;
- forcing normalization;
- RK2 update;
- dealiasing mask;
- protected source hashes.

Only diagnostic cadence and operator-ledger recording may change.

### 8.3 High-cadence budget output

Record budget and operator-ledger diagnostics every 10 loop indices:

\[
\Delta t_{\mathrm{diag}}=0.05.
\]

This yields 2,001 budget snapshots including the final step.

### 8.4 Offline cadence reconstruction

From the same high-cadence trajectory, construct aligned interval datasets at:

- `0.05`;
- `0.10`;
- `0.25`;
- `0.50`;
- `1.00`;
- `2.50`.

All cadence comparisons must use the same underlying numerical states.

### 8.5 Cadence scaling metrics

For each cadence calculate:

- median normalized energy residual;
- maximum normalized energy residual;
- median normalized enstrophy residual;
- maximum normalized enstrophy residual;
- mean signed residual;
- residual RMS;
- final-window metrics;
- full-run metrics.

### 8.6 Sampling attribution rule

Sampling cadence is classified as a **material contributor** when:

1. the median normalized enstrophy residual decreases monotonically over at
   least three successive cadence refinements;
2. the `0.05` result is at least 50% smaller than the `0.50` result;
3. operator-ledger terms do not explain most of that reduction.

Sampling cadence is classified as a **dominant contributor** only when the
`0.05` median and maximum both pass the original residual thresholds without
changing the numerical timestep.

---

## 9. Stage D — local same-state RK2 shadow tests

### 9.1 Objective

Separate finite-timestep RK2 error from long-trajectory divergence.

### 9.2 Required checkpoint states

A prospective replay shall save exact vorticity checkpoints at:

- `t=20.005`;
- `t=40.005`;
- `t=60.005`;
- `t=80.005`;
- `t=90.005`;
- `t=100.005`.

Each checkpoint shall include:

- array shape;
- dtype;
- SHA-256;
- physical time;
- loop index;
- forcing SHA-256;
- source hashes.

### 9.3 Local shadow intervals

From each checkpoint, independently integrate over a fixed local duration:

\[
\Delta T_{\mathrm{shadow}}=0.5.
\]

Use:

- `dt=0.005`;
- `dt=0.0025`;
- `dt=0.00125`.

All shadows begin from the exact same checkpoint state.

The forcing and spatial operators remain fixed.

### 9.4 Comparison quantities

For each checkpoint and timestep, calculate:

- final energy;
- final enstrophy;
- integrated forcing contribution;
- integrated viscous contribution;
- integrated discrete-advection contribution;
- integrated exact mask contribution;
- ledger residual;
- difference from the finest-timestep shadow.

### 9.5 RK2 attribution rule

RK2 temporal error is a **material contributor** when:

- the operator-resolved residual decreases consistently under timestep
  halving;
- the decrease is visible at most checkpoint states;
- the finest-timestep residual remains above the roundoff/operator-ledger
  floor.

A formal observed order shall not be claimed from this diagnostic alone.

---

## 10. Stage E — genuine continuing evolution analysis

### 10.1 Objective

Determine whether the enstrophy channel remains dynamically nonstationary
after numerical residual contributors are accounted for.

### 10.2 Required indicators

Over the fixed final window calculate, using the finest available diagnostic
cadence:

- enstrophy OLS slope;
- normalized enstrophy drift;
- mean injection;
- mean dissipation;
- mean operator-resolved advection contribution;
- mean exact mask contribution;
- mean corrected RHS;
- four subwindow means;
- sign persistence of corrected RHS.

### 10.3 Corrected modeled balance

Define an operator-resolved discrete RHS:

\[
R_Z^{\mathrm{corrected}}
=
W_F^{RK2}
+
W_V^{RK2}
+
W_A^{RK2}
+
R_{\mathrm{mask}}.
\]

Compare this with the observed discrete step rate.

### 10.4 Genuine-evolution rule

Genuine continuing evolution is confirmed when:

- the corrected mean enstrophy RHS remains materially nonzero;
- the enstrophy drift remains above `0.05`;
- injection-dissipation imbalance remains above `0.10`, or the corrected
  operator balance remains materially nonzero;
- these results persist under finer diagnostic cadence;
- numerical integrity remains intact.

This classification concerns the tested numerical model, not physical
validation.

---

## 11. Attribution decision matrix

### A. Predominantly sampling-cadence limited

Use when:

- high-cadence residuals pass;
- operator-ledger corrections are small;
- timestep shadow effects are small;
- genuine enstrophy drift may still persist.

### B. Predominantly discrete-advection limited

Use when:

- `W_A^{RK2}` accounts for most of the residual;
- correlation with advection activity is strong;
- cadence refinement alone does not close the budget.

### C. Predominantly mask-loss limited

Use when:

- exact `R_mask` accounts for most of the residual;
- the contribution grows with spectral tail development;
- post-mask ledger closure is substantially improved.

### D. Predominantly RK2 limited

Use when:

- timestep halving reduces the operator-resolved residual consistently;
- cadence and mask corrections are insufficient;
- local same-state shadows show clear temporal sensitivity.

### E. Genuine evolution with acceptable discrete closure

Use when:

- corrected residuals pass;
- enstrophy drift and imbalance still fail;
- the mean corrected RHS remains negative.

### F. Multiple contributors

Use when no single contributor explains at least 70% of the residual magnitude
or when different contributors dominate at different times.

### G. Inconclusive

Use when diagnostics are insufficient, inconsistent, or fail integrity gates.

---

## 12. Quantitative attribution fractions

For each interval, define the original enstrophy residual:

\[
R_0
=
R_Z^{\mathrm{observed}}
-
(\eta_f-D_Z).
\]

Define sequential corrected residuals:

\[
R_1
=
R_0-W_A^{RK2},
\]

\[
R_2
=
R_1-R_{\mathrm{mask}},
\]

\[
R_3
=
R_{\mathrm{ledger,filtered}}.
\]

Report reduction fractions:

\[
F_A
=
1-\frac{|R_1|}{\max(|R_0|,10^{-30})},
\]

\[
F_M
=
1-\frac{|R_2|}{\max(|R_1|,10^{-30})},
\]

and the remaining fraction:

\[
F_R
=
\frac{|R_3|}{\max(|R_0|,10^{-30})}.
\]

Because sequential attribution can depend on ordering, also report the reverse
order:

1. mask first;
2. advection second.

No unique causal percentage shall be claimed when ordering materially changes
the result.

---

## 13. Required plots and tables

A later analysis package shall produce:

1. normalized enstrophy residual versus time;
2. energy and enstrophy residuals on the same normalized scale;
3. residual versus advection RMS;
4. residual versus mask-removal RMS;
5. exact enstrophy mask-loss rate versus time;
6. discrete advection enstrophy work versus time;
7. cadence versus residual statistics;
8. local timestep-shadow residuals;
9. observed enstrophy rate versus corrected discrete RHS;
10. enstrophy injection and dissipation over the final window;
11. residual attribution table by five time blocks;
12. final attribution decision table.

Plots are descriptive evidence. The numerical tables remain authoritative.

---

## 14. Required future output bundle

A future authorized investigation should produce one immutable directory
containing:

1. `investigation_metadata.json`;
2. `high_cadence_budget.csv`;
3. `operator_ledger.csv`;
4. `cadence_reconstruction.csv`;
5. `checkpoint_inventory.csv`;
6. `shadow_test_results.csv`;
7. `attribution_summary.json`;
8. `file_inventory.csv`.

Optional visualizations may be included separately.

No file may overwrite the archived longer stationarity evidence.

---

## 15. Numerical-integrity gates

Any future execution must stop and preserve partial outputs if:

- a source hash changes;
- the forcing identity changes;
- a state becomes nonfinite;
- an operator-ledger value becomes nonfinite;
- exact step decomposition fails beyond `1e-12` relative tolerance;
- a checkpoint hash changes after writing;
- an expected cadence endpoint is missing;
- a same-state shadow does not begin from the recorded checkpoint bytes;
- an output schema or atomic write fails;
- Git state is not clean before execution.

No automatic rerun is allowed.

---

## 16. Interpretation guardrails

The investigation may support statements about:

- diagnostic sampling sensitivity;
- discrete operator budget closure;
- mask-associated enstrophy removal;
- local timestep sensitivity;
- continuing modeled enstrophy evolution.

It may not establish:

- formal timestep convergence;
- formal spatial convergence;
- physical truth;
- turbulence;
- cascade direction;
- inertial-range scaling;
- a `k^-3` law;
- superiority of one numerical method;
- production readiness.

---

## 17. Minimal execution sequence

The recommended sequence is:

### Step 1

Complete Stage A using existing archived CSV and JSON files only.

### Step 2

Create one operator-ledger design review and confirm the exact formulas.

### Step 3

Create one combined high-cadence replay runner that:

- preserves the original trajectory configuration;
- records the operator ledger;
- writes required checkpoint states;
- performs no shadow tests during the main trajectory.

### Step 4

Archive and inspect the high-cadence replay evidence.

### Step 5

Create a separate local shadow-test runner using the archived checkpoint files.

This ordering avoids mixing long-run trajectory generation with local timestep
experiments.

---

## 18. Current decision

The archived `t=100.005` run remains valid and unchanged.

Its classification remains:

> `NOT STATIONARY WITHIN TESTED DURATION`

The current evidence already establishes genuine declining enstrophy over the
fixed final window.

The precise attribution of the residual mismatch among sampling cadence,
discrete advection, dealiasing, and RK2 error remains unresolved.

---

## 19. Execution authorization

This document is design-only.

> No new numerical execution is authorized.

The next permitted task is read-only Stage A analysis of the existing evidence
bundle.
