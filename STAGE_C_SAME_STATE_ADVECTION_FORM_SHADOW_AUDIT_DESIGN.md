
# Stage C Same-State Advection-Form Shadow Audit Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Source checkpoint:
  `a5c200b25b17a9cc4ce709dae3695ceca8e63aba`
- Parent Stage B execution commit:
  `5c464c21f61e917f26e00c73c5ec691fadc2bed9`
- Parent Stage B evidence commit:
  `a5c200b25b17a9cc4ce709dae3695ceca8e63aba`
- Stage B evidence report:
  `STAGE_B_EXACT_OPERATOR_LEDGER_EVIDENCE_REPORT.md`
- Stage B evidence report SHA-256:
  `5419765B72A757A4C048761CDBC55B1AAD8ED2A0414E3D9E79CC118A64D40DE4`
- Stage B runner:
  `run_stage_b_exact_operator_ledger_replay.py`
- Stage B runner SHA-256:
  `970AE47D4DF69819FA6D831557FC2679D843B860D901CF367361A3A34126E246`
- Protected baseline solver:
  `project/solver/spectral_solver.py`
- Protected baseline solver SHA-256:
  `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1`
- Existing standalone advection operators:
  `project/solver/advection_operators.py`
- Current Git blob identity for standalone advection operators:
  `849b3d5c95c955a7db73313d8680c942fd32c571`
- Existing selectable-advection scaffold:
  `project/solver/selectable_advection_solver.py`
- Current Git blob identity for selectable-advection scaffold:
  `cc3b757e327a5b1a0b6cea2287c672adebd77c15`
- Created UTC:
  `2026-07-20T07:03:27+00:00`
- Document type:
  design only
- New numerical execution authorized:
  no
- Shadow runner creation authorized:
  no
- Alternate trajectory execution authorized:
  no
- Protected solver modification authorized:
  no
- Existing Stage B evidence modification authorized:
  no
- Production solver selection authorized:
  no

### Claim boundaries

- Formal temporal convergence: not authorized
- Formal spatial convergence: not authorized
- Physical validation: not authorized
- Turbulence: not authorized
- Cascade: not authorized
- Inertial range: not authorized
- `k^-3` law: not authorized
- Method superiority: not authorized
- Production readiness: not authorized
- Unique physical causation: not authorized
- Replacement of the baseline method: not authorized
- Alternate-method trajectory claims: not authorized

---

## 1. Purpose

Stage B established that the previously omitted
non-forcing/non-viscous enstrophy-ledger activity is dominated by the
implemented discrete-advection work.

Stage C is designed to test a narrower question:

> When several alternative advection operators are evaluated on exactly the
> same baseline RK2 states, does the nonzero stage-weighted enstrophy work
> remain, diminish, change sign, or approach numerical neutrality?

The purpose is not to choose a better solver.

The purpose is not to advance multiple trajectories.

The purpose is to determine whether the Stage B nonzero work is specific to
the current centered advective form within a frozen shadow-operator set.

---

## 2. Stage B basis

The archived Stage B result is:

> `LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION`

For the final window:

```text
80.005 < t <= 100.005
```

the baseline discrete-advection contribution was:

| Quantity | Stage B value |
|---|---:|
| Mean signed rate | `+3.2414560868477325e-05` |
| Integrated signed contribution | `+0.0006482912173695466` |
| Maximum absolute rate | `3.9338892670361616e-05` |
| Positive steps | `4000` |
| Negative steps | `0` |

For the full run:

| Quantity | Stage B value |
|---|---:|
| Integrated signed contribution | `+0.0015368528716236765` |
| Integrated absolute activity | `0.0015368528716236765` |
| Positive steps | `20000` |
| Negative steps | `1` |

The Stage B exact ledger closed with maximum normalized filtered residual:

```text
2.645205267472769e-12
```

All 201 archived replay comparisons passed.

These values are frozen baseline references for any future Stage C runner.

---

## 3. Question being tested

The primary question is:

> Is the nonzero stage-weighted advection work substantially reduced for all
> frozen alternative advection forms when each is evaluated on the same
> baseline current state and the same baseline RK2 stage state?

The secondary questions are:

1. Does changing only the centered algebraic form alter the work?
2. Does spectral differentiation alter the work?
3. Does projecting the nonlinear product alter the work?
4. Does the Arakawa Jacobian produce near-neutral enstrophy work on the same
   states?
5. Is any difference attributable to operator form rather than trajectory
   divergence?
6. Does the answer remain consistent across the five Stage B time blocks and
   the full run?

---

## 4. Current baseline update

The protected baseline computes:

\[
T^{base}
=
uD_x^c\omega
+
vD_y^c\omega,
\]

where \(D_x^c\) and \(D_y^c\) are centered periodic finite differences.

The advection component of the vorticity right-hand side is:

\[
A^{base}
=
-T^{base}.
\]

At each RK2 step:

\[
N_1
=
A_1^{base}+V_1+F_1,
\]

\[
\omega_s
=
\omega_n+\Delta tN_1,
\]

\[
N_2
=
A_2^{base}+V_2+F_2,
\]

\[
\omega_u
=
\omega_n+\frac{\Delta t}{2}(N_1+N_2),
\]

\[
\omega_{n+1}
=
\operatorname{Re}
\left[
\mathcal F^{-1}
\left(
P\mathcal F(\omega_u)
\right)
\right].
\]

Only this baseline update is permitted to advance the replayed state.

---

## 5. Meaning of same-state shadow evaluation

For each timestep, every advection operator shall be evaluated at:

1. the exact baseline accepted state \(\omega_n\);
2. the exact baseline RK2 stage state \(\omega_s\).

The stage state is always:

\[
\omega_s
=
\omega_n+\Delta t
\left(
A_1^{base}+V_1+F_1
\right).
\]

No shadow operator may define its own stage state.

No shadow operator may define its own unfiltered state.

No shadow operator may define its own accepted state.

No shadow result may be fed into:

- `N1`;
- `N2`;
- `omega_stage`;
- `omega_unfiltered`;
- `omega_filtered`;
- the next timestep.

This produces operator comparisons on one common trajectory.

It does not produce alternate-method simulations.

---

## 6. Frozen trajectory

The future Stage C execution, if separately authorized, shall replay exactly:

| Parameter | Value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Updates | `20001` |
| Final time | `100.005` |
| Initial vorticity | exact zero |
| Forcing | archived RMS-matched multimode field |
| Forcing RMS | `0.005` |
| Forcing SHA-256 | `504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB` |
| Accepted update | baseline centered advective RK2 plus mask |

The future execution must reproduce the Stage B trajectory before any shadow
classification is valid.

---

## 7. Sign convention

All transport operators are defined as:

\[
T_m
=
u\omega_x+v\omega_y
\]

or their discrete analogues.

Every vorticity-RHS advection component is:

\[
A_m=-T_m.
\]

Every shadow enstrophy-work calculation uses \(A_m\), not \(T_m\).

The future runner shall record both:

- `transport_work = <omega * T>`;
- `rhs_advection_work = <omega * A>`.

They must satisfy:

\[
\langle\omega A_m\rangle
=
-\langle\omega T_m\rangle
\]

to roundoff.

A sign-convention mismatch is a numerical-integrity failure.

---

## 8. Frozen operator registry

The future audit shall evaluate exactly seven operator IDs.

### 8.1 Baseline operator

```text
BASE_FD_ADVECTIVE_V1
```

Definition:

\[
T_{BA}
=
uD_x^c\omega
+
vD_y^c\omega.
\]

Purpose:

- reproduce the active protected solver;
- anchor all ratios;
- verify the standalone helper against the embedded formula.

Classification role:

- baseline only.

---

### 8.2 Projected baseline transport

```text
SHADOW_FD_ADVECTIVE_PROJECTED_V1
```

Definition:

\[
T_{BAP}
=
P
\left(
uD_x^c\omega
+
vD_y^c\omega
\right).
\]

Here \(P\) means transform the completed physical nonlinear product, apply the
existing Boolean two-thirds mask, and transform back.

Purpose:

- isolate the effect of projecting the baseline nonlinear product;
- test whether stage-2 unfiltered content changes the baseline work.

Classification role:

- mechanism check only;
- excluded from the primary specificity decision.

---

### 8.3 Centered conservative form

```text
SHADOW_FD_CONSERVATIVE_V1
```

Definition:

\[
T_{FC}
=
D_x^c(u\omega)
+
D_y^c(v\omega).
\]

Purpose:

- change the algebraic advection form;
- keep the same centered derivative operator;
- keep the same velocity and same state.

Classification family:

```text
CENTERED_ALGEBRAIC
```

---

### 8.4 Centered skew-symmetric form

```text
SHADOW_FD_SKEW_V1
```

Definition:

\[
T_{FS}
=
\frac{1}{2}
\left[
T_{BA}
+
T_{FC}
\right].
\]

Purpose:

- test the arithmetic midpoint of centered advective and conservative forms;
- isolate algebraic-form sensitivity without changing the derivative stencil.

Frozen identity:

\[
T_{FS}
-
\frac{1}{2}(T_{BA}+T_{FC})
=
0.
\]

Classification family:

```text
CENTERED_ALGEBRAIC
```

---

### 8.5 Pseudo-spectral advective form without product projection

```text
SHADOW_PS_ADVECTIVE_RAW_V1
```

Definition:

\[
T_{PSR}
=
uD_x^s\omega
+
vD_y^s\omega,
\]

where \(D_x^s,D_y^s\) are FFT derivatives.

The final nonlinear product is not projected.

Purpose:

- change the vorticity-gradient representation;
- retain the advective product form;
- expose raw pseudo-spectral product behavior.

Classification family:

```text
PSEUDO_SPECTRAL
```

---

### 8.6 Pseudo-spectral advective form with product projection

```text
SHADOW_PS_ADVECTIVE_PROJECTED_V1
```

Definition:

\[
T_{PSP}
=
P
\left(
uD_x^s\omega
+
vD_y^s\omega
\right).
\]

Purpose:

- separate spectral-gradient effects from nonlinear-product projection;
- use the existing solver mask without changing the accepted trajectory.

Classification family:

```text
PSEUDO_SPECTRAL
```

---

### 8.7 Arakawa form

```text
SHADOW_ARAKAWA_V1
```

The existing helper calculates the project-convention transport:

\[
T_A=-J_A(\psi,\omega),
\]

where \(J_A\) is the periodic Arakawa Jacobian.

Therefore:

\[
A_A=J_A(\psi,\omega).
\]

Purpose:

- evaluate a structurally distinct Jacobian stencil;
- test same-state discrete enstrophy-work behavior;
- do so without advancing an Arakawa trajectory.

Classification family:

```text
ARAKAWA
```

---

## 9. Primary and secondary operators

The primary alternate set is:

```text
SHADOW_FD_CONSERVATIVE_V1
SHADOW_FD_SKEW_V1
SHADOW_PS_ADVECTIVE_RAW_V1
SHADOW_PS_ADVECTIVE_PROJECTED_V1
SHADOW_ARAKAWA_V1
```

The secondary mechanism-check operator is:

```text
SHADOW_FD_ADVECTIVE_PROJECTED_V1
```

The secondary operator may explain a mechanism.

It cannot independently determine specificity.

---

## 10. Velocity consistency

For each state \(\omega\), calculate one baseline streamfunction:

\[
\psi
=
\operatorname{streamfunction}(\omega).
\]

Calculate one baseline velocity:

\[
u=\partial_y^s\psi,
\]

\[
v=-\partial_x^s\psi.
\]

The same numerical \(u,v,\psi\) arrays shall be supplied to all applicable
shadow calculations at that state.

An operator may not recompute velocity using an alternate Poisson solve,
alternate sign convention, alternate wavenumber array, or alternate mask.

For existing helper functions that internally calculate velocity, the returned
velocity-dependent result must match an equivalent calculation using the
frozen shared velocity arrays.

---

## 11. Stage-specific shadow work

For method \(m\), define stage-1 work:

\[
W_{1,m}
=
\langle
\omega_nA_{1,m}
\rangle.
\]

Define stage-2 work:

\[
W_{2,m}
=
\langle
\omega_sA_{2,m}
\rangle.
\]

Define Stage B-compatible stage-weighted work:

\[
R_{A,m}^{shadow}
=
\frac{1}{2}
\left(
W_{1,m}
+
W_{2,m}
\right).
\]

This is the primary scalar comparison.

It uses the same stage weights as the Stage B baseline ledger.

---

## 12. Work-alignment diagnostics

For a state \(\omega\) and RHS field \(A_m\), define:

\[
\rho_m
=
\frac{
\langle\omega A_m\rangle
}{
\max(
\operatorname{RMS}(\omega)
\operatorname{RMS}(A_m),
10^{-30}
)
}.
\]

This is a normalized field-work alignment.

It lies within approximately \([-1,1]\), subject to floating-point error.

Record separately:

- stage-1 alignment;
- stage-2 alignment.

A large advection-field RMS with near-zero alignment can yield near-zero
enstrophy work.

This distinction is central to interpreting Stage A advection-RMS
correlations.

---

## 13. Field-difference diagnostics

For each shadow method \(m\), define:

\[
\Delta A_{1,m}
=
A_{1,m}-A_{1,base},
\]

\[
\Delta A_{2,m}
=
A_{2,m}-A_{2,base}.
\]

Record:

- RMS of each baseline and shadow field;
- RMS of each difference;
- maximum absolute difference;
- normalized RMS difference;
- cosine similarity with the baseline;
- mean of each RHS field;
- maximum imaginary contamination before selecting real parts.

The normalized difference is:

\[
D_{i,m}
=
\frac{
\operatorname{RMS}(\Delta A_{i,m})
}{
\max(
\operatorname{RMS}(A_{i,base}),
10^{-30}
)
}.
\]

Field similarity does not imply equal work.

Work similarity does not imply field similarity.

Both must be reported.

---

## 14. Centered product-rule diagnostics

For each baseline state, define the centered velocity-divergence field:

\[
\delta_h
=
D_x^cu
+
D_y^cv.
\]

Define the centered product-rule defect:

\[
Q_h
=
D_x^c(u\omega)
+
D_y^c(v\omega)
-
uD_x^c\omega
-
vD_y^c\omega
-
\omega\delta_h.
\]

Then the exact constructed identity is:

\[
T_{FC}-T_{BA}
=
\omega\delta_h+Q_h.
\]

The future runner must verify this identity numerically.

Record:

- `centered_velocity_divergence_rms`;
- `centered_velocity_divergence_max_abs`;
- `centered_product_rule_defect_rms`;
- `centered_product_rule_defect_max_abs`;
- `centered_form_identity_residual_rms`;
- normalized identity residual.

Also record the work decomposition:

\[
\langle\omega(T_{FC}-T_{BA})\rangle
=
\langle\omega^2\delta_h\rangle
+
\langle\omega Q_h\rangle.
\]

This diagnostic tests whether centered-form differences align more strongly
with:

- centered divergence mismatch;
- discrete product-rule defect;
- both.

It does not assign physical causation.

---

## 15. Pseudo-spectral diagnostics

For each state, calculate spectral velocity divergence:

\[
\delta_s
=
D_x^su
+
D_y^sv.
\]

Record its RMS and maximum absolute value.

Define the raw-to-projected nonlinear-product difference:

\[
H_{PS}
=
T_{PSR}-T_{PSP}.
\]

Record:

- RMS of `H_PS`;
- maximum absolute value;
- work removed by product projection;
- fractional reduction in absolute work;
- fraction of raw product spectral norm outside the retained mask.

At stage 1, the accepted state is already mask projected.

At stage 2, the baseline stage state is not assumed to be mask projected.

The two stages must therefore be reported separately.

---

## 16. Arakawa identity diagnostics

For each state, calculate:

\[
J_A(\psi,\omega).
\]

Verify the sign relation:

\[
T_A=-J_A,
\]

\[
A_A=J_A.
\]

Record:

- \(\langle\omega A_A\rangle\);
- normalized enstrophy-work alignment;
- \(\langle\psi A_A\rangle\) as a secondary energy-work identity diagnostic;
- sign-relation residual;
- finite-value and shape checks.

The energy-work diagnostic is secondary.

It does not enter the Stage C specificity classification.

No statement that Arakawa is superior is authorized.

---

## 17. Baseline replay requirements

The future runner must reproduce Stage B before interpreting any shadow result.

### 17.1 Source identities

It shall verify all archived Stage B hashes, including:

- `operator_ledger_per_step.csv`;
- `operator_ledger_summary.json`;
- `run_metadata.json`;
- Stage B inventory;
- Stage B runner;
- Stage B evidence report.

### 17.2 Per-step scalar equivalence

For all 20,001 rows, compare the replayed baseline values against the Stage B
per-step ledger:

- loop index;
- completed steps;
- physical time;
- `z_current`;
- `z_stage`;
- `z_unfiltered`;
- `z_filtered`;
- baseline stage-1 advection work;
- baseline stage-2 advection work;
- baseline stage-weighted advection rate;
- baseline viscous rate;
- baseline forcing rate;
- RK2 remainder;
- mask contribution;
- observed filtered enstrophy rate.

### 17.3 Archived trajectory equivalence

At all 201 archived cadence points, reproduce the longer forcing-budget
trajectory comparison.

All 201 points must pass.

### 17.4 Baseline classification reference

The reproduced final-window baseline advection integrated signed contribution
must match:

```text
0.0006482912173695466
```

The reproduced full-run baseline advection integrated signed contribution
must match:

```text
0.0015368528716236765
```

---

## 18. Baseline helper equivalence

The future runner shall calculate the baseline centered advective transport by
two routes:

### Route E: embedded mirror

\[
T_{BA,E}
=
uD_x^c\omega
+
vD_y^c\omega.
\]

### Route H: existing helper

```python
advection_fd_centered(solver, omega)
```

Require:

\[
T_{BA,E}
\approx
T_{BA,H}.
\]

Record exact array equality and normalized RMS difference.

A mismatch beyond tolerance is a numerical-integrity failure.

---

## 19. Shadow non-mutation gates

For every state and every method:

1. hash the state array before evaluation;
2. evaluate the shadow operator;
3. hash the state array after evaluation;
4. require exact equality;
5. require the state writeability flag to remain unchanged;
6. require solver grid arrays to remain unchanged;
7. require forcing bytes to remain unchanged.

The future runner must also verify that shadow evaluation order does not
matter at frozen sentinel steps.

Required sentinel loop indices:

```text
0
4000
8000
12000
16000
20000
```

At each sentinel, evaluate the method registry:

- forward order;
- reverse order.

All corresponding shadow arrays and scalar results must match.

---

## 20. Same-trajectory enforcement

The future runner shall retain exactly one evolving vorticity state:

```text
baseline_omega
```

No variable named or used as an evolving alternate trajectory is authorized.

Forbidden patterns include:

- `omega_arakawa_next`;
- `omega_pseudo_next`;
- `omega_conservative_next`;
- separate shadow timestep loops;
- calls to `step_once_selectable`;
- calls to `run_selectable_diagnostic`;
- calls to any protected or selectable `run()` method.

Shadow operators may return fields only.

They may not return accepted states.

---

## 21. Time blocks

Use the same six blocks as Stage B:

| Block | Time range | Expected baseline steps |
|---:|---|---:|
| 1 | `0.005 <= t <= 20.005` | `4001` |
| 2 | `20.005 < t <= 40.005` | `4000` |
| 3 | `40.005 < t <= 60.005` | `4000` |
| 4 | `60.005 < t <= 80.005` | `4000` |
| 5 | `80.005 < t <= 100.005` | `4000` |
| 6 | full run | `20001` |

Block 5 is the primary decision window.

Block 6 is the secondary decision window.

Blocks 1 through 4 describe time dependence.

---

## 22. Aggregate work metrics

For each operator \(m\) and window \(W\), calculate:

### 22.1 Integrated signed work

\[
I_{m,W}
=
\sum_{n\in W}
\Delta t
R_{A,m,n}^{shadow}.
\]

### 22.2 Integrated absolute activity

\[
B_{m,W}
=
\sum_{n\in W}
\Delta t
\left|
R_{A,m,n}^{shadow}
\right|.
\]

### 22.3 Mean and median

Record:

- mean signed rate;
- median signed rate;
- mean absolute rate;
- maximum absolute rate.

### 22.4 Sign counts

Record:

- positive count;
- negative count;
- zero count;
- sign agreement fraction with baseline.

### 22.5 Concentration

Record the minimum number of steps accounting for 90% of total absolute
activity:

\[
n_{90,m,W}.
\]

---

## 23. Baseline-normalized shadow ratios

For each primary alternate \(m\), define:

### 23.1 Absolute-activity ratio

\[
Q_{m,W}
=
\frac{
B_{m,W}
}{
\max(
B_{base,W},
10^{-30}
)
}.
\]

### 23.2 Signed-integral magnitude ratio

\[
S_{m,W}
=
\frac{
|I_{m,W}|
}{
\max(
|I_{base,W}|,
10^{-30}
)
}.
\]

### 23.3 Maximum-rate ratio

\[
M_{m,W}
=
\frac{
\max_{n\in W}|R_{A,m,n}^{shadow}|
}{
\max(
\max_{n\in W}|R_{A,base,n}^{shadow}|,
10^{-30}
)
}.
\]

### 23.4 Signed-integral ratio

Also record:

\[
G_{m,W}
=
\frac{
I_{m,W}
}{
I_{base,W}
}.
\]

This signed value shows direction reversal.

It is not used alone for classification.

---

## 24. Frozen near-neutral test

An alternate method \(m\) is classified as `NEAR_NEUTRAL_RELATIVE_TO_BASELINE`
in window \(W\) only when all conditions pass:

\[
Q_{m,W}\le0.10,
\]

\[
S_{m,W}\le0.10,
\]

\[
M_{m,W}\le0.25,
\]

\[
n_{90,m,W}\ge5,
\]

and all method integrity gates pass.

These thresholds indicate a strong reduction.

They do not mean exact conservation.

---

## 25. Frozen persistence test

An alternate method \(m\) is classified as
`NONZERO_WORK_PERSISTS_RELATIVE_TO_BASELINE` in window \(W\) only when:

\[
Q_{m,W}\ge0.50,
\]

\[
S_{m,W}\ge0.50,
\]

\[
M_{m,W}\ge0.25,
\]

and all method integrity gates pass.

The alternate work may have the same or opposite sign.

Persistence refers to nonzero magnitude, not physical correctness.

---

## 26. Frozen family-level decision rules

The primary families are:

```text
CENTERED_ALGEBRAIC
PSEUDO_SPECTRAL
ARAKAWA
```

### 26.1 Support for current-form specificity

Return:

```text
SHADOW SET SUPPORTS CURRENT-FORM SPECIFICITY
```

only when:

1. every one of the five primary alternate methods is near-neutral in the
   final window;
2. every one of the five primary alternate methods is near-neutral over the
   full run;
3. baseline Stage B reproduction passes;
4. all shadow integrity gates pass.

This is deliberately strict.

It means support only within the frozen shadow set.

### 26.2 Persistence across multiple forms

Return:

```text
NONZERO WORK PERSISTS ACROSS MULTIPLE FORMS
```

when:

1. the persistence test passes for at least one alternate method in at least
   two structurally distinct families;
2. it passes in both the final window and full run;
3. baseline reproduction and integrity gates pass.

### 26.3 Mixed response

Return:

```text
SHADOW RESPONSE IS FORM-DEPENDENT AND MIXED
```

when:

- neither specificity nor multi-family persistence criteria pass;
- at least one alternate is near-neutral;
- at least one alternate is persistent or intermediate.

### 26.4 No strong separation

Return:

```text
SHADOW SET DOES NOT SHOW STRONG FORM SEPARATION
```

when:

- no alternate is near-neutral;
- multi-family persistence does not meet its full decision rule;
- integrity gates pass.

### 26.5 Inconclusive

Return:

```text
SAME-STATE SHADOW AUDIT INCONCLUSIVE
```

when:

- baseline ratios are unstable;
- required rows are missing;
- source identities are incomplete;
- the baseline reference cannot be reproduced.

### 26.6 Integrity failure

Return:

```text
NUMERICAL INTEGRITY FAILURE
```

when any mandatory integrity gate fails.

---

## 27. Method superiority prohibition

The audit shall not use language such as:

- better;
- more accurate;
- superior;
- preferred;
- correct replacement;
- production method;
- recommended solver.

A method with smaller same-state enstrophy work is not automatically more
accurate.

A method with nonzero work is not automatically invalid.

A method with near-zero work may differ in:

- truncation error;
- phase error;
- dispersion;
- dissipation;
- stability;
- computational cost;
- long-time trajectory.

Those questions are outside Stage C.

---

## 28. Primary interpretation matrix

The final report shall interpret patterns as follows.

| Observed pattern | Permitted interpretation |
|---|---|
| All primary shadows near-neutral | Support for current-form specificity within frozen set |
| Centered alternatives remain large, Arakawa near-zero | Work depends on more than one centered form; Arakawa differs |
| Raw pseudo-spectral large, projected pseudo-spectral small | Product projection strongly affects same-state work |
| Conservative and advective opposite, skew near-zero | Algebraic averaging cancels same-state work |
| All families retain substantial work | Nonzero work is not specific to current centered form |
| Mixed ratios and signs | Form-dependent mixed response |
| Baseline replay mismatch | No scientific interpretation |

---

## 29. Per-step state-reference schema

A future `shadow_state_reference.csv` shall contain unique headers only.

Required columns:

- `loop_index`;
- `completed_steps`;
- `physical_time`;
- `forcing_sha256`;
- `omega_current_sha256`;
- `omega_stage_sha256`;
- `omega_filtered_sha256`;
- `z_current`;
- `z_stage`;
- `z_filtered`;
- `baseline_stage1_work_replay`;
- `baseline_stage1_work_archived`;
- `baseline_stage1_work_difference`;
- `baseline_stage2_work_replay`;
- `baseline_stage2_work_archived`;
- `baseline_stage2_work_difference`;
- `baseline_rk2_work_replay`;
- `baseline_rk2_work_archived`;
- `baseline_rk2_work_difference`;
- `baseline_scalar_equivalence_pass`;
- `all_shadow_state_hashes_unchanged`;
- `all_shadow_arrays_finite`;
- `all_integrity_gates_pass`.

Expected rows:

```text
20001
```

---

## 30. Long-format shadow schema

A future `shadow_advection_per_step.csv` shall use long format.

Each baseline timestep contributes seven rows.

Expected rows:

\[
20001\times7=140007.
\]

Required unique columns:

### Identity

- `loop_index`;
- `completed_steps`;
- `physical_time`;
- `operator_id`;
- `operator_family`;
- `classification_role`;
- `stage_state_policy`.

### Stage-1 values

- `stage1_transport_work`;
- `stage1_rhs_work`;
- `stage1_rhs_rms`;
- `stage1_rhs_max_abs`;
- `stage1_work_alignment`;
- `stage1_difference_from_baseline_rms`;
- `stage1_normalized_difference_from_baseline`;
- `stage1_cosine_similarity_with_baseline`;
- `stage1_rhs_mean`.

### Stage-2 values

- `stage2_transport_work`;
- `stage2_rhs_work`;
- `stage2_rhs_rms`;
- `stage2_rhs_max_abs`;
- `stage2_work_alignment`;
- `stage2_difference_from_baseline_rms`;
- `stage2_normalized_difference_from_baseline`;
- `stage2_cosine_similarity_with_baseline`;
- `stage2_rhs_mean`.

### Stage-weighted values

- `stage_weighted_rhs_work`;
- `difference_from_baseline_stage_weighted_work`;
- `ratio_to_baseline_stage_weighted_work`;
- `absolute_ratio_to_baseline_stage_weighted_work`;
- `sign_agreement_with_baseline`.

### Method integrity

- `input_state_unchanged`;
- `operator_output_finite`;
- `transport_rhs_sign_identity_residual`;
- `operator_specific_identity_residual`;
- `operator_integrity_pass`.

---

## 31. Mechanism-diagnostic schema

The future state-reference output or a dedicated internal accumulator shall
also preserve:

- centered velocity-divergence RMS;
- centered product-rule defect RMS;
- centered form-identity residual;
- centered divergence work term;
- centered product-rule work term;
- spectral velocity-divergence RMS;
- pseudo-spectral product-removed RMS;
- pseudo-spectral product-removed work;
- Arakawa sign-identity residual;
- Arakawa secondary energy-work value.

No duplicate CSV headers are permitted.

The future runner must explicitly assert header uniqueness before writing.

---

## 32. Time-block summary schema

A future `shadow_advection_time_blocks.csv` shall contain:

\[
6\times7=42
\]

rows.

Required columns:

- `block_id`;
- `block_label`;
- `operator_id`;
- `operator_family`;
- `classification_role`;
- `step_count`;
- `integrated_signed_work`;
- `integrated_absolute_activity`;
- `mean_signed_rate`;
- `median_signed_rate`;
- `mean_absolute_rate`;
- `maximum_absolute_rate`;
- `positive_count`;
- `negative_count`;
- `zero_count`;
- `sign_agreement_fraction_with_baseline`;
- `n90_steps`;
- `absolute_activity_ratio_to_baseline`;
- `signed_integral_magnitude_ratio_to_baseline`;
- `maximum_rate_ratio_to_baseline`;
- `signed_integral_ratio_to_baseline`;
- `near_neutral_pass`;
- `persistence_pass`;
- `integrity_failure_count`.

Every header must be unique.

---

## 33. Summary requirements

A future `shadow_advection_summary.json` shall contain:

- run identity;
- source identities;
- frozen configuration;
- method registry;
- primary and secondary method sets;
- same-state policy;
- exact baseline reproduction results;
- 201-point trajectory equivalence results;
- all six block summaries;
- all method ratios;
- family-level classification;
- final-window classification;
- full-run classification;
- centered product-rule diagnostics;
- pseudo-spectral projection diagnostics;
- Arakawa identity diagnostics;
- maximum source and state mutation residuals;
- count and location of failed gates;
- limitations and claim boundaries.

---

## 34. Prospective output bundle

A future authorized audit shall create one immutable Git-ignored directory
under:

```text
experiments/advection_form_shadow_audit/
```

Run-directory prefix:

```text
stage_c_same_state_advection_shadow_
```

Required files:

1. `run_metadata.json`;
2. `shadow_state_reference.csv`;
3. `shadow_advection_per_step.csv`;
4. `shadow_advection_time_blocks.csv`;
5. `shadow_advection_summary.json`;
6. `STAGE_C_SAME_STATE_ADVECTION_FORM_SHADOW_AUDIT_REPORT.md`;
7. `file_inventory.csv`.

No state arrays are archived.

No alternate trajectories are archived.

No plots are required.

---

## 35. Future runner identity

The prospective runner filename is:

```text
run_stage_c_same_state_advection_shadow_audit.py
```

It shall support:

```powershell
python -B .\run_stage_c_same_state_advection_shadow_audit.py inspect
python -B .\run_stage_c_same_state_advection_shadow_audit.py run
```

The design does not create or authorize that runner.

---

## 36. Future inspection mode

The future `inspect` mode shall:

- parse and compile the runner;
- verify exact filename;
- require LF-only runner bytes;
- verify active branch;
- require the runner-design checkpoint as HEAD;
- require only the untracked runner in Git status;
- verify all design and Stage B evidence identities;
- inspect AST without importing project modules;
- confirm project imports occur only inside the run path;
- reject protected solver `run()` calls;
- reject selectable `run()` calls;
- reject `step_once_selectable`;
- reject `run_selectable_diagnostic`;
- reject multiple evolving trajectory variables;
- reject convergence and spectral-slope fitting;
- verify all seven operator IDs;
- verify all output header lists are unique;
- verify all classification thresholds;
- write no files;
- construct no solver;
- execute no timestep;
- mutate no Git state.

Inspection must end with:

```text
Numerical shadow audit authorized by inspection: NO
```

---

## 37. Future execution preflight

A future run path shall require:

- branch `phase4_validation`;
- clean working tree;
- runner committed and pushed;
- runner commit has the archived design commit as its parent;
- runner commit changes exactly one file;
- working runner bytes equal committed bytes;
- protected solver hash matches;
- advection-operator source identity matches;
- Stage B evidence hashes match;
- no prior Stage C output directory exists;
- output directory is Git ignored;
- forcing hash matches;
- no alternate trajectory code path exists.

A failed preflight creates no output directory.

---

## 38. Runtime tolerances

Prospective tolerances:

| Check | Limit |
|---|---:|
| Baseline archived scalar relative difference | `1e-11` |
| Baseline archived scalar absolute floor | `1e-14` |
| Baseline helper normalized field difference | `1e-15` |
| Shadow state hash mutation | exact zero |
| Centered form-identity normalized residual | `1e-12` |
| Skew identity normalized residual | `1e-15` |
| Pseudo-spectral projection identity residual | `1e-12` |
| Arakawa sign-identity normalized residual | `1e-12` |
| Transport/RHS sign residual | `1e-14` |
| Spectral velocity-divergence normalized RMS | `1e-12` |
| Imaginary/real RMS ratio | `1e-13` |
| Nonfinite values | none permitted |
| Archived trajectory matches | `201 / 201` |

These are integrity tolerances.

They are not accuracy claims.

---

## 39. Failure preservation

After a future output directory is created, any failure must preserve:

- metadata;
- completed state-reference rows;
- completed shadow rows;
- last completed loop index;
- failed gate;
- method being evaluated;
- stage being evaluated;
- source identities;
- partial inventory where possible.

The runner shall print:

```text
STAGE C SAME-STATE SHADOW AUDIT FAILURE
Partial evidence preserved at: <path>
Do not rerun automatically.
```

---

## 40. No-rerun policy

Only one controlled Stage C execution may be authorized.

After either completion or failure:

- do not rerun automatically;
- do not delete partial evidence;
- do not modify Stage B evidence;
- localize any schema or implementation defect before deciding further work.

The Stage B experience with duplicate CSV headers requires a prospective
header-uniqueness gate before the first Stage C write.

---

## 41. Expected successful console summary

A future successful execution should report:

```text
STAGE C SAME-STATE ADVECTION-FORM SHADOW AUDIT: COMPLETE
Baseline trajectory replay: PASS
Baseline per-step ledger reproduction: PASS
Archived comparison points: 201 / 201 PASS
Baseline steps: 20001
Shadow methods: 7
Shadow rows: 140007
Time-block rows: 42
Accepted trajectory changed by shadows: NO
Alternate trajectories executed: NO
Protected solver run loop called: NO
Method superiority authorized: NO
Classification: <one frozen classification>
```

---

## 42. Scientific limitations

Even a clean Stage C result cannot establish:

- which method is more accurate;
- which method should replace the baseline;
- formal consistency order;
- formal convergence;
- long-time stability;
- physical correctness;
- conservation under a separately advanced trajectory;
- equivalence of alternate trajectories;
- turbulence;
- a cascade;
- an inertial range;
- a spectral law;
- production readiness.

Same-state shadow work is a local operator diagnostic.

It is not a solver-selection experiment.

---

## 43. Permitted conclusions

Depending on the evidence, the future report may state:

- the frozen shadow set supports current-form specificity;
- nonzero work persists across multiple forms;
- the response is form-dependent and mixed;
- the shadow set does not show strong separation;
- the audit is inconclusive;
- numerical integrity failed.

It may quantify:

- work reductions;
- sign reversals;
- operator-field differences;
- projection effects;
- product-rule defects;
- divergence defects;
- time dependence.

It may not state that a method is superior.

---

## 44. Current decision

The Stage C same-state advection-form shadow audit is now designed.

No runner has been created.

No solver has been constructed.

No numerical step has been executed.

No accepted trajectory has been changed.

No alternate trajectory has been authorized.

The next controlled task is to archive this design before creating any
standalone Stage C runner.
