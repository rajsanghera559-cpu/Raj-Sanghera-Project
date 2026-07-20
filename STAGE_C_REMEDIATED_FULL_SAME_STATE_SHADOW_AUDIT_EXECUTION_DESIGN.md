
# Stage C Remediated Full Same-State Shadow Audit Execution Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Current source checkpoint:
  `d482936f42dcf4f529f934957d4fdf34c081ac88`
- Parent focused-remediation runner checkpoint:
  `9a27e66f2838768df5cf218d48a601824386f9ea`
- Parent focused-remediation evidence commit:
  `d482936f42dcf4f529f934957d4fdf34c081ac88`
- Original Stage C design:
  `STAGE_C_SAME_STATE_ADVECTION_FORM_SHADOW_AUDIT_DESIGN.md`
- Original Stage C design SHA-256:
  `4C14EEA8E492CC5824686C3540D9ABF96EA3413C5F4B9B9A8E1D5EDD470D7D0C`
- Original Stage C runner:
  `run_stage_c_same_state_advection_shadow_audit.py`
- Original Stage C runner SHA-256:
  `5E13CF350DF5356E1E8E44F0D921A7C92FFDD6830978466DFA5B6648818F4BC1`
- Nyquist failure-localization design:
  `STAGE_C_NYQUIST_IMAGINARY_RATIO_FAILURE_LOCALIZATION_AND_REMEDIATION_DESIGN.md`
- Nyquist failure-localization design SHA-256:
  `809196A724D4CD94C936A6A96BB7A6B39717A6667EB57D932ED023C6469EC1A2`
- Nyquist failure-localization runner:
  `run_stage_c_nyquist_failure_localization.py`
- Nyquist failure-localization runner SHA-256:
  `945CD7D940CBAA823A15AC6A3E5885F97ED4E46AFE4919C40181F3FCA6B9BFA0`
- Nyquist failure-localization evidence report:
  `STAGE_C_NYQUIST_FAILURE_LOCALIZATION_EVIDENCE_REPORT.md`
- Nyquist failure-localization evidence-report SHA-256:
  `EEFB82BFBC74C5E2EEC75C816D0A8F4C56601921E3EAEFD1D5B820B5F74BBE7D`
- Shadow-diagnostic Nyquist remediation design:
  `STAGE_C_SHADOW_DIAGNOSTIC_NYQUIST_REMEDIATION_DESIGN.md`
- Shadow-diagnostic Nyquist remediation-design SHA-256:
  `62F4B615F7CB9DC65402FD99FC8F72634F27177222CCCA3BD3FCD121991F0787`
- Focused remediation-verification runner:
  `run_stage_c_shadow_nyquist_remediation_verification.py`
- Focused remediation-verification runner SHA-256:
  `DB43FCEC5EFD0BEC9A9F1C09661A8660CC9E39FCE107D55A757A870DE66A2F6A`
- Focused remediation-verification completion report:
  `STAGE_C_SHADOW_NYQUIST_REMEDIATION_VERIFICATION_COMPLETION_REPORT.md`
- Focused remediation-verification completion-report SHA-256:
  `B3BB4E6B7442035975DF7C2774DCFF1720E51953DA0A3E37C81415AAFB618AAD`
- Focused remediation evidence inventory SHA-256:
  `3478343159B6A7909480C1434E179B2970CF36977D90561B90C4F4900DA38282`
- Protected baseline solver:
  `project/solver/spectral_solver.py`
- Protected baseline solver SHA-256:
  `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1`
- Standalone advection operators:
  `project/solver/advection_operators.py`
- Frozen advection-operator Git blob:
  `849b3d5c95c955a7db73313d8680c942fd32c571`
- Selectable-advection scaffold:
  `project/solver/selectable_advection_solver.py`
- Frozen selectable-solver Git blob:
  `cc3b757e327a5b1a0b6cea2287c672adebd77c15`
- Created UTC:
  `2026-07-20T23:17:27+00:00`
- Document type:
  design only
- New full-run runner created by this document:
  no
- Static inspection performed by this document:
  no
- Numerical execution authorized now:
  no
- Protected baseline solver modification authorized:
  no
- Accepted baseline-update modification authorized:
  no
- Existing runner modification authorized:
  no
- Advection-operator source modification authorized:
  no
- Alternate trajectory execution authorized:
  no
- Method-superiority claim authorized:
  no
- Spectral-slope fitting authorized:
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
- Baseline replacement: not authorized
- Alternate-method trajectory claims: not authorized
- Production-solver selection: not authorized

---

## 1. Purpose

Stage B established that the leading omitted
non-forcing/non-viscous contribution in the implemented enstrophy ledger was
the centered finite-difference advection work.

The first Stage C same-state audit was intended to determine whether that work
was specific to the current centered advective form. It stopped at loop index
`3059`, RK2 stage 2, because the raw pseudo-spectral vorticity-gradient
diagnostic exceeded the frozen imaginary-ratio threshold.

The focused localization and remediation verification established that:

```text
historical raw ratio:
1.0021037272233111e-13

real-compatible Nyquist-zeroed ratio:
7.983551748537457e-16
```

and that the real-compatible shadow route preserved real derivatives,
transports, and shadow work at roundoff-scale differences.

This document defines a new full same-state audit using the verified
real-compatible derivative convention only in the affected shadow diagnostic
paths.

The purpose remains:

> Determine whether the nonzero discrete-advection work measured for the
> baseline centered advective form is specific to that form within a frozen
> seven-operator same-state shadow set.

The purpose is not to rank methods.

The purpose is not to advance alternate trajectories.

The purpose is not to modify the protected solver.

---

## 2. Evidence basis

### 2.1 Stage B exact-ledger result

The archived Stage B classification is:

> **LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION**

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

All 20,001 exact-ledger rows passed their integrity gates.

All 201 archived baseline comparisons passed.

---

### 2.2 Partial original Stage C pattern

At physical time `15.295`, the original Stage C partial evidence recorded:

| Operator | Stage-weighted RHS work |
|---|---:|
| Baseline centered advective | `+1.7413851867416074e-07` |
| Projected centered advective | `+1.7413851867408504e-07` |
| Centered conservative | `-1.7413851867416e-07` |
| Centered skew-symmetric | `+1.0587911840678754e-22` |
| Raw pseudo-spectral | `+6.352747104407253e-22` |
| Projected pseudo-spectral | `-1.3923104070492562e-19` |
| Arakawa | `+1.0587911840678754e-22` |

This was a strong partial pattern.

It was not a complete Stage C classification.

---

### 2.3 Focused localization result

The original failure was localized to:

```text
loop index: 3059
completed steps: 3060
physical time: 15.3
stage: 2
quantity: omega_gradient_imaginary_ratio
```

The focused conclusion was:

> **FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION**

> **NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT**

---

### 2.4 Focused remediation-verification result

The focused remediation verification reproduced:

- `3060 / 3060` Stage B rows;
- `3059 / 3059` preserved partial Stage C rows;
- all seven last-passing operator-work values;
- the exact historical raw failure;
- the exact localized real-compatible ratio.

Maximum observed differences were:

| Quantity | Maximum |
|---|---:|
| Real-derivative relative difference | `3.755608831459645e-16` |
| Transport relative difference | `5.305126715227565e-16` |
| Work absolute difference | `6.352747104407253e-22` |

The focused remediation conclusions were:

> **SHADOW NYQUIST REMEDIATION CONSISTENT WITH LOCALIZATION**

> **REAL SHADOW WORK PRESERVED UNDER REMEDIATION**

These results justify designing a new full shadow audit.

They do not themselves authorize its execution.

---

## 3. Remediated full-run question

The primary question is:

> Across the complete frozen baseline trajectory, are all five primary
> alternate advection forms near-neutral relative to the baseline centered
> advective work under the frozen Stage C thresholds?

Secondary questions are:

1. Does the centered conservative form remain approximately opposite to the
   centered advective form?
2. Does the centered skew-symmetric form remain near-neutral?
3. Do the real-compatible pseudo-spectral forms remain near-neutral?
4. Does the Arakawa form remain near-neutral?
5. Does projecting the centered baseline nonlinear product materially change
   its same-state work?
6. Does projecting the real-compatible pseudo-spectral nonlinear product
   materially change its same-state work?
7. Are these patterns stable across the five Stage B time blocks?
8. Do any forms show substantial nonzero work in the final window or full run?
9. Can the result be obtained without changing the accepted baseline
   trajectory?

---

## 4. New runner identity

The prospective full-run runner filename is:

```text
run_stage_c_remediated_full_same_state_shadow_audit.py
```

It shall support exactly:

```powershell
python -B .\run_stage_c_remediated_full_same_state_shadow_audit.py inspect
python -B .\run_stage_c_remediated_full_same_state_shadow_audit.py run
```

This design does not create that runner.

This design does not authorize `run` mode.

The new runner must be a new file.

It may not replace or edit:

```text
run_stage_c_same_state_advection_shadow_audit.py
run_stage_c_nyquist_failure_localization.py
run_stage_c_shadow_nyquist_remediation_verification.py
```

---

## 5. Frozen numerical configuration

| Parameter | Value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Baseline updates | `20001` |
| Final physical time | `100.005` |
| Initial vorticity | exact zero |
| Forcing target RMS | `0.005` |
| Forcing SHA-256 | `504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB` |
| Accepted advection | centered finite-difference advective form |
| Accepted integrator | existing explicit RK2 |
| Accepted post-step operation | existing spectral mask |
| Alternate trajectories | none |

---

## 6. Accepted baseline update

The accepted baseline transport is:

\[
T^{base}
=
uD_x^c\omega
+
vD_y^c\omega.
\]

The accepted advection RHS is:

\[
A^{base}
=
-T^{base}.
\]

The baseline RK2 update remains:

\[
N_1
=
A_1^{base}
+
V_1
+
F_1,
\]

\[
\omega_s
=
\omega_n
+
\Delta tN_1,
\]

\[
N_2
=
A_2^{base}
+
V_2
+
F_2,
\]

\[
\omega_u
=
\omega_n
+
\frac{\Delta t}{2}
\left(
N_1+N_2
\right),
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

Only this update advances the state.

No shadow transport enters:

- `N1`;
- `omega_stage`;
- `N2`;
- `omega_unfiltered`;
- `omega_filtered`;
- the next timestep.

---

## 7. Same-state policy

Every shadow operator shall be evaluated at:

1. the exact baseline accepted current state \(\omega_n\);
2. the exact baseline RK2 stage state \(\omega_s\).

The stage state is always generated by the baseline centered-advection update.

A shadow operator may not:

- create its own stage state;
- create its own accepted state;
- update the baseline state;
- retain an evolving alternate state;
- call a selectable stepping routine;
- call a protected or selectable `run()` method.

The future runner shall retain one evolving state variable only:

```text
baseline_omega
```

---

## 8. Sign convention

All transport fields are defined as positive transport:

\[
T_m.
\]

Every shadow advection RHS is:

\[
A_m=-T_m.
\]

Every enstrophy-work calculation uses:

\[
W_m
=
\langle
\omega A_m
\rangle.
\]

The future runner shall record both:

- transport work;
- RHS advection work.

It shall verify:

\[
\langle\omega A_m\rangle
=
-\langle\omega T_m\rangle
\]

within the frozen sign-identity tolerance.

---

## 9. Frozen remediated operator registry

The future audit shall evaluate exactly seven operator IDs.

### 9.1 Baseline centered advective form

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

Role:

- accepted baseline trajectory;
- baseline work reference;
- primary denominator for all comparison ratios.

Family:

```text
BASELINE
```

---

### 9.2 Projected centered advective form

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

Role:

- secondary mechanism check;
- excluded from the primary specificity decision.

Family:

```text
PROJECTED_BASELINE_CHECK
```

---

### 9.3 Centered conservative form

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

Role:

- primary alternate.

Family:

```text
CENTERED_ALGEBRAIC
```

---

### 9.4 Centered skew-symmetric form

```text
SHADOW_FD_SKEW_V1
```

Definition:

\[
T_{FS}
=
\frac{1}{2}
\left(
T_{BA}
+
T_{FC}
\right).
\]

Role:

- primary alternate.

Family:

```text
CENTERED_ALGEBRAIC
```

Frozen identity:

\[
T_{FS}
-
\frac{1}{2}
\left(
T_{BA}
+
T_{FC}
\right)
=
0.
\]

---

### 9.5 Real-compatible unprojected pseudo-spectral form

```text
SHADOW_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2
```

Definition:

\[
T_{PSR}^{RC}
=
uD_x^{RC}\omega
+
vD_y^{RC}\omega.
\]

The nonlinear product is not projected.

Role:

- primary alternate.

Family:

```text
PSEUDO_SPECTRAL_RC_NYQUIST
```

The new `V2` ID distinguishes this verified derivative convention from the
historical raw-`ik` Stage C implementation.

---

### 9.6 Real-compatible projected pseudo-spectral form

```text
SHADOW_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2
```

Definition:

\[
T_{PSP}^{RC}
=
P
\left(
uD_x^{RC}\omega
+
vD_y^{RC}\omega
\right).
\]

Role:

- primary alternate.

Family:

```text
PSEUDO_SPECTRAL_RC_NYQUIST
```

---

### 9.7 Arakawa form

```text
SHADOW_ARAKAWA_V1
```

The existing project-convention transport remains:

\[
T_A
=
-J_A(\psi,\omega).
\]

Therefore:

\[
A_A
=
J_A(\psi,\omega).
\]

Role:

- primary alternate.

Family:

```text
ARAKAWA
```

---

## 10. Primary and secondary sets

Primary alternate operator IDs:

```text
SHADOW_FD_CONSERVATIVE_V1
SHADOW_FD_SKEW_V1
SHADOW_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2
SHADOW_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2
SHADOW_ARAKAWA_V1
```

Secondary mechanism-check operator:

```text
SHADOW_FD_ADVECTIVE_PROJECTED_V1
```

The secondary operator may explain projection sensitivity.

It may not independently determine the primary classification.

---

## 11. Real-compatible derivative convention

For the even grid, define local copied derivative wavenumbers:

\[
k_x^{RC}
=
\begin{cases}
0,& k_x=-N/2,\\
k_x,& \text{otherwise},
\end{cases}
\]

\[
k_y^{RC}
=
\begin{cases}
0,& k_y=-N/2,\\
k_y,& \text{otherwise}.
\end{cases}
\]

Then:

\[
\widehat{D_x^{RC}q}
=
ik_x^{RC}\widehat q,
\]

\[
\widehat{D_y^{RC}q}
=
ik_y^{RC}\widehat q.
\]

Requirements:

- derive the Nyquist value from `N`;
- verify that the actual solver arrays contain `-N/2`;
- copy `solver.kx` and `solver.ky`;
- zero only the relevant local copied Nyquist entries;
- verify the copies do not share memory with the solver arrays;
- hash `solver.kx` and `solver.ky` before and after the audit;
- never assign to `solver.kx` or `solver.ky`;
- retain complex inverse transforms until real and imaginary diagnostics are
  measured;
- use only the real part in the pseudo-spectral shadow transport;
- apply the convention only to shadow spectral derivatives and shadow spectral
  divergence diagnostics.

---

## 12. Historical raw-route checkpoint

The historical raw route is:

\[
\widehat{D_x^{raw}q}
=
ik_x\widehat q,
\]

\[
\widehat{D_y^{raw}q}
=
ik_y\widehat q.
\]

The raw route shall not be used for the full-run pseudo-spectral operator
classification.

It shall be evaluated only at the frozen remediation checkpoints:

```text
loop index 3058
loop index 3059
```

At loop `3059`, stage 2, the future runner must reproduce:

```text
quantity:
omega_gradient_imaginary_ratio

raw ratio:
1.0021037272233111e-13

real-compatible ratio:
7.983551748537457e-16
```

The raw route must fail the historical `1e-13` threshold.

The real-compatible route must pass it.

This expected raw failure is a historical reproduction gate.

It is not a reason to stop the new remediated full run when reproduced
correctly.

A mismatch is an integrity failure.

---

## 13. Historical checkpoint interpretation

The future runner shall distinguish:

```text
EXPECTED HISTORICAL RAW FAILURE REPRODUCED
```

from:

```text
UNEXPECTED REMEDIATED ROUTE FAILURE
```

Rules:

1. The raw route is evaluated only at the frozen checkpoint.
2. The raw failure must match the archived ratio within the frozen comparison
   tolerance.
3. The raw result is never relabeled as passing.
4. The real-compatible route must pass at the same state.
5. The baseline accepted state must remain unchanged.
6. All focused remediation identities must match.
7. The future run may continue only after all seven conditions pass.

---

## 14. Imaginary-ratio diagnostics

At every timestep and both RK2 stages, the remediated route shall report or
accumulate:

1. real-compatible vorticity spectral-gradient ratio;
2. projected centered-baseline transport ratio;
3. projected real-compatible pseudo-spectral transport ratio;
4. real-compatible spectral `u_x` ratio;
5. real-compatible spectral `v_y` ratio.

For each quantity:

\[
\rho
=
\frac{
\operatorname{RMS}(\operatorname{Im}q)
}{
\max(
\operatorname{RMS}(\operatorname{Re}q),
10^{-30}
)
}.
\]

Frozen gate:

```text
rho <= 1.0e-13
```

No denominator-floor classification is allowed.

The maximum ratio and the maximum-producing quantity shall be recorded for
each stage.

---

## 15. Velocity consistency

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

The same numerical \(\psi,u,v\) arrays shall be supplied to all applicable
shadow operators.

No shadow operator may use:

- an alternate Poisson solve;
- an alternate velocity sign;
- alternate accepted-state filtering;
- a separately advanced velocity;
- a modified baseline wavenumber array.

---

## 16. Stage-specific shadow work

For method \(m\), define:

\[
W_{1,m}
=
\langle
\omega_nA_{1,m}
\rangle,
\]

\[
W_{2,m}
=
\langle
\omega_sA_{2,m}
\rangle.
\]

The stage-weighted work is:

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

This is the primary per-step scalar used for time-block attribution.

---

## 17. Work-alignment diagnostics

For each state and shadow RHS:

\[
\rho_m^{work}
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

Record separately:

- stage-1 alignment;
- stage-2 alignment.

The audit shall distinguish:

- operator-field magnitude;
- state-to-operator alignment;
- scalar enstrophy work.

---

## 18. Field-difference diagnostics

For every alternate operator \(m\):

\[
\Delta A_{i,m}
=
A_{i,m}
-
A_{i,base},
\qquad
i\in\{1,2\}.
\]

Record:

- baseline RHS RMS;
- shadow RHS RMS;
- difference RMS;
- maximum absolute difference;
- normalized difference;
- cosine similarity;
- RHS mean;
- finite-value status.

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

---

## 19. Centered product-rule diagnostics

Define:

\[
\delta_h
=
D_x^cu
+
D_y^cv,
\]

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

Verify:

\[
T_{FC}
-
T_{BA}
=
\omega\delta_h
+
Q_h.
\]

Record:

- centered velocity-divergence RMS;
- centered velocity-divergence maximum;
- centered product-rule defect RMS;
- centered product-rule defect maximum;
- centered form-identity residual;
- normalized identity residual;
- centered divergence work term;
- centered product-rule work term;
- work-identity residual.

These diagnostics are descriptive.

They do not establish unique physical causation.

---

## 20. Real-compatible pseudo-spectral diagnostics

For each state, calculate:

\[
\delta_s^{RC}
=
D_x^{RC}u
+
D_y^{RC}v.
\]

Record:

- real-compatible spectral divergence RMS;
- real-compatible spectral divergence maximum;
- normalized divergence;
- real-compatible gradient imaginary ratios;
- projected-product imaginary ratio.

Define:

\[
H_{PS}^{RC}
=
T_{PSR}^{RC}
-
T_{PSP}^{RC}.
\]

Record:

- RMS of \(H_{PS}^{RC}\);
- maximum absolute value;
- work removed by projection;
- fractional work reduction;
- fraction of unprojected product spectral power outside the retained mask.

---

## 21. Arakawa diagnostics

For each state:

\[
J_A(\psi,\omega)
\]

must satisfy the frozen project sign convention:

\[
T_A=-J_A,
\]

\[
A_A=J_A.
\]

Record:

- enstrophy work;
- work alignment;
- secondary energy-work diagnostic;
- sign-identity residual;
- finite-value status.

The secondary energy-work value does not enter the primary classification.

---

## 22. Non-mutation gates

For every shadow evaluation:

1. hash the baseline input state;
2. record the writeability flag;
3. evaluate all shadows;
4. rehash the state;
5. compare the writeability flag;
6. verify the forcing hash;
7. verify solver-grid hashes;
8. verify local derivative arrays did not change.

Any mutation is an integrity failure.

---

## 23. Evaluation-order sentinels

Required sentinel loop indices:

```text
0
3058
3059
4000
8000
12000
16000
20000
```

At each sentinel:

- evaluate the remediated seven-operator registry in forward order;
- evaluate it in reverse order;
- compare every transport array;
- compare every scalar work value;
- compare every imaginary-ratio value;
- compare every state hash;
- require order-independent results.

At `3058` and `3059`, also evaluate the historical raw checkpoint route.

---

## 24. Baseline replay requirements

The future runner shall reproduce the complete Stage B baseline.

### 24.1 Per-step exact-ledger scalar reproduction

Compare all 20,001 rows against the archived Stage B ledger for:

- loop index;
- completed steps;
- physical time;
- `z_current`;
- `z_stage`;
- `z_unfiltered`;
- `z_filtered`;
- stage-1 advection work;
- stage-2 advection work;
- stage-weighted advection work;
- viscous work;
- forcing work;
- RK2 remainder;
- mask contribution;
- observed filtered rate.

### 24.2 Archived trajectory comparisons

At all 201 archived cadence points, reproduce the archived forcing-budget
trajectory.

Required result:

```text
201 / 201 PASS
```

### 24.3 Integrated baseline references

Final-window baseline integrated signed work:

```text
0.0006482912173695466
```

Full-run baseline integrated signed work:

```text
0.0015368528716236765
```

### 24.4 Focused remediation checkpoint

At loop `3059`, reproduce:

- current-state SHA-256:
  `7534D7C24F2666993BBD5B7B79E03B82B8F7F15665B41C30453351A18196E852`;
- stage-state SHA-256:
  `01F5C093F544119D75C4903FBEBC8B809224CABEF12CE125FB94C6AA509BD2B7`;
- filtered-state SHA-256:
  `1A95D9BF2065E88B47E2E578B8862DB83B47D804288354C32299EF44809EE61E`.

---

## 25. Time blocks

Use the frozen Stage B blocks:

| Block | Time range | Expected steps |
|---:|---|---:|
| 1 | `0.005 <= t <= 20.005` | `4001` |
| 2 | `20.005 < t <= 40.005` | `4000` |
| 3 | `40.005 < t <= 60.005` | `4000` |
| 4 | `60.005 < t <= 80.005` | `4000` |
| 5 | `80.005 < t <= 100.005` | `4000` |
| 6 | full run | `20001` |

Block 5 is the primary decision window.

Block 6 is the secondary decision window.

Blocks 1 through 4 report time dependence.

---

## 26. Aggregate work metrics

For operator \(m\) and window \(W\):

### 26.1 Integrated signed work

\[
I_{m,W}
=
\sum_{n\in W}
\Delta t
R_{A,m,n}^{shadow}.
\]

### 26.2 Integrated absolute activity

\[
B_{m,W}
=
\sum_{n\in W}
\Delta t
\left|
R_{A,m,n}^{shadow}
\right|.
\]

### 26.3 Distribution metrics

Record:

- mean signed rate;
- median signed rate;
- mean absolute rate;
- maximum absolute rate;
- positive count;
- negative count;
- zero count;
- sign agreement with baseline.

### 26.4 Concentration

Record the minimum number of steps accounting for 90% of absolute activity:

\[
n_{90,m,W}.
\]

---

## 27. Baseline-normalized ratios

For every primary alternate \(m\):

### 27.1 Absolute-activity ratio

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

### 27.2 Signed-integral magnitude ratio

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

### 27.3 Maximum-rate ratio

\[
M_{m,W}
=
\frac{
\max|R_{A,m}^{shadow}|
}{
\max(
\max|R_{A,base}^{shadow}|,
10^{-30}
)
}.
\]

### 27.4 Signed-integral ratio

\[
G_{m,W}
=
\frac{
I_{m,W}
}{
I_{base,W}
}.
\]

---

## 28. Frozen near-neutral rule

An alternate method \(m\) is:

```text
NEAR_NEUTRAL_RELATIVE_TO_BASELINE
```

in window \(W\) only if:

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

and all integrity gates pass.

This indicates strong reduction relative to the baseline.

It does not establish exact conservation.

---

## 29. Frozen persistence rule

An alternate method \(m\) is:

```text
NONZERO_WORK_PERSISTS_RELATIVE_TO_BASELINE
```

in window \(W\) only if:

\[
Q_{m,W}\ge0.50,
\]

\[
S_{m,W}\ge0.50,
\]

\[
M_{m,W}\ge0.25,
\]

and all integrity gates pass.

Persistence concerns magnitude.

The sign may agree with or oppose the baseline.

---

## 30. Frozen full-run classifications

The future successful run may return exactly one scientific classification.

### 30.1 Support for current-form specificity

```text
REMEDIATED SHADOW SET SUPPORTS CURRENT-FORM SPECIFICITY
```

only when:

1. every one of the five primary alternates is near-neutral in block 5;
2. every one of the five primary alternates is near-neutral in block 6;
3. baseline replay passes;
4. the historical raw checkpoint passes;
5. the real-compatible checkpoint passes;
6. every integrity gate passes.

This means support only within the frozen remediated shadow set.

---

### 30.2 Persistence across multiple families

```text
NONZERO WORK PERSISTS ACROSS MULTIPLE REMEDIATED SHADOW FAMILIES
```

when:

1. persistence passes for at least one alternate in at least two structurally
   distinct primary families;
2. persistence passes in both block 5 and block 6;
3. all integrity gates pass.

---

### 30.3 Mixed response

```text
REMEDIATED SHADOW RESPONSE IS FORM-DEPENDENT AND MIXED
```

when:

- neither specificity nor multi-family persistence passes;
- at least one alternate is near-neutral;
- at least one alternate is persistent or intermediate;
- all integrity gates pass.

---

### 30.4 No strong separation

```text
REMEDIATED SHADOW SET DOES NOT SHOW STRONG FORM SEPARATION
```

when:

- no primary alternate is near-neutral;
- multi-family persistence does not satisfy its complete rule;
- all integrity gates pass.

---

### 30.5 Inconclusive

```text
REMEDIATED SAME-STATE SHADOW AUDIT INCONCLUSIVE
```

when:

- baseline denominators are unstable;
- required rows are missing;
- the historical checkpoint cannot be reproduced;
- the remediated checkpoint cannot be reproduced;
- source identities are incomplete;
- a classification cannot be formed without violating a frozen rule.

---

### 30.6 Integrity failure

```text
NUMERICAL INTEGRITY FAILURE
```

when any mandatory integrity gate fails.

---

## 31. Method-superiority prohibition

The report shall not use:

- better;
- superior;
- preferred;
- more accurate;
- correct replacement;
- recommended production method;
- validated solver replacement.

Near-neutral same-state work does not establish greater accuracy.

Persistent same-state work does not establish invalidity.

The audit compares one scalar property on one frozen trajectory.

---

## 32. Interpretation matrix

| Pattern | Permitted interpretation |
|---|---|
| All primary alternates near-neutral | Support for current-form specificity within frozen remediated set |
| Conservative opposite and skew near-zero | Centered algebraic averaging cancels same-state work |
| Unprojected and projected RC pseudo-spectral near-zero | Spectral shadow work is near-neutral under verified RC convention |
| Unprojected RC large, projected RC small | Nonlinear-product projection materially affects same-state work |
| Arakawa near-zero while centered alternatives remain large | Arakawa differs, but current-form specificity is not fully supported |
| Multiple families retain substantial work | Nonzero work is not specific to the current centered form |
| Mixed signs and magnitudes | Form-dependent mixed response |
| Baseline or remediation checkpoint mismatch | No scientific classification |

---

## 33. Prospective output directory

A future authorized execution shall create one immutable Git-ignored directory
under:

```text
experiments/advection_form_shadow_audit_remediated_full/
```

Run-directory prefix:

```text
stage_c_remediated_full_same_state_shadow_
```

No prior directory with that prefix may exist.

No automatic rerun is allowed.

---

## 34. Prospective output bundle

Required files:

1. `run_metadata.json`;
2. `remediated_shadow_state_reference.csv`;
3. `remediated_shadow_advection_per_step.csv`;
4. `remediated_shadow_time_blocks.csv`;
5. `nyquist_remediation_checkpoint_trace.csv`;
6. `nyquist_remediation_checkpoint_work.csv`;
7. `remediated_shadow_summary.json`;
8. `STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_REPORT.md`;
9. `file_inventory.csv`.

No state arrays are archived.

No plots are required.

No spectral slopes are fitted.

---

## 35. Expected record counts

| Output | Expected rows |
|---|---:|
| Baseline state-reference rows | `20001` |
| Long-format shadow rows | `140007` |
| Time-block rows | `42` |
| Nyquist checkpoint trace rows | `40` |
| Nyquist checkpoint work rows | `6` |
| Archived baseline matches | `201` |

The 40 checkpoint trace rows are:

\[
2\ \text{loop indices}
\times
2\ \text{stages}
\times
2\ \text{routes}
\times
5\ \text{quantities}
=
40.
\]

The six checkpoint work rows are:

\[
2\ \text{pseudo-spectral operators}
\times
3\ \text{stage labels}
=
6.
\]

---

## 36. State-reference schema

`remediated_shadow_state_reference.csv` shall contain unique headers.

Required fields include:

### Identity

- `loop_index`;
- `completed_steps`;
- `physical_time`;
- `forcing_sha256`;
- `omega_current_sha256`;
- `omega_stage_sha256`;
- `omega_filtered_sha256`.

### Baseline values

- `z_current`;
- `z_stage`;
- `z_unfiltered`;
- `z_filtered`;
- `baseline_stage1_work_replay`;
- `baseline_stage1_work_archived`;
- `baseline_stage1_work_difference`;
- `baseline_stage2_work_replay`;
- `baseline_stage2_work_archived`;
- `baseline_stage2_work_difference`;
- `baseline_rk2_work_replay`;
- `baseline_rk2_work_archived`;
- `baseline_rk2_work_difference`.

### Remediated mechanism diagnostics

For both stages:

- maximum remediated imaginary ratio;
- maximum-producing quantity;
- centered divergence RMS;
- centered product-rule defect RMS;
- centered form-identity residual;
- remediated spectral divergence RMS;
- remediated pseudo-product removed RMS;
- remediated projection work reduction;
- Arakawa sign residual;
- maximum imaginary ratio.

### Integrity

- `baseline_scalar_equivalence_pass`;
- `all_shadow_state_hashes_unchanged`;
- `all_shadow_arrays_finite`;
- `all_integrity_gates_pass`.

Expected rows:

```text
20001
```

---

## 37. Long-format shadow schema

`remediated_shadow_advection_per_step.csv` shall contain one row per operator
per baseline update.

Expected rows:

```text
140007
```

Required fields:

### Identity

- loop index;
- completed steps;
- physical time;
- operator ID;
- operator family;
- classification role;
- stage-state policy;
- derivative convention.

### Stage 1

- transport work;
- RHS work;
- RHS RMS;
- maximum absolute RHS;
- work alignment;
- difference from baseline RMS;
- normalized difference;
- cosine similarity;
- RHS mean.

### Stage 2

- same fields as stage 1.

### Stage weighted

- stage-weighted RHS work;
- difference from baseline;
- signed ratio to baseline;
- absolute ratio to baseline;
- sign agreement.

### Integrity

- input state unchanged;
- output finite;
- sign identity residual;
- operator-specific identity residual;
- imaginary-ratio pass;
- operator integrity pass.

All headers must be unique.

---

## 38. Time-block schema

`remediated_shadow_time_blocks.csv` shall contain:

```text
42 rows
```

Required fields:

- block ID;
- block label;
- operator ID;
- operator family;
- classification role;
- step count;
- integrated signed work;
- integrated absolute activity;
- mean signed rate;
- median signed rate;
- mean absolute rate;
- maximum absolute rate;
- positive count;
- negative count;
- zero count;
- sign agreement fraction;
- `n90_steps`;
- absolute-activity ratio;
- signed-integral magnitude ratio;
- maximum-rate ratio;
- signed-integral ratio;
- near-neutral pass;
- persistence pass;
- integrity-failure count.

Every header must be unique.

---

## 39. Nyquist checkpoint trace schema

`nyquist_remediation_checkpoint_trace.csv` shall contain the exact 40-row
checkpoint set.

Required fields:

- loop index;
- completed steps;
- physical time;
- stage;
- route;
- quantity ID;
- dominant direction;
- real RMS;
- imaginary RMS;
- imaginary ratio;
- threshold;
- threshold pass;
- historical-failure marker;
- raw-to-RC real difference RMS;
- raw-to-RC relative difference;
- cosine similarity;
- relevant Nyquist power fraction;
- raw Hermitian residual;
- RC Hermitian residual;
- state SHA-256.

The raw route is present only in this checkpoint output.

---

## 40. Nyquist checkpoint work schema

`nyquist_remediation_checkpoint_work.csv` shall contain six rows.

Required fields:

- loop index;
- physical time;
- stage label;
- remediated pseudo-spectral operator ID;
- historical raw transport RMS;
- RC transport RMS;
- transport difference RMS;
- transport relative difference;
- cosine similarity;
- historical raw work;
- RC work;
- work absolute difference;
- work relative difference;
- sign changed;
- near-zero character changed;
- material real-work change.

---

## 41. Summary requirements

`remediated_shadow_summary.json` shall contain:

- run identity;
- all source identities;
- complete operator registry;
- frozen configuration;
- baseline reproduction results;
- 201-point archive-equivalence results;
- remediation-checkpoint reproduction results;
- time-block summaries;
- final-window result;
- full-run result;
- classification;
- centered mechanism diagnostics;
- RC pseudo-spectral diagnostics;
- Arakawa diagnostics;
- state-mutation results;
- evaluation-order sentinel results;
- maximum imaginary ratios;
- failed-gate count;
- limitations;
- claim boundaries;
- exact output filenames.

---

## 42. Report requirements

The final report shall state:

1. the complete frozen configuration;
2. that one baseline trajectory was advanced;
3. that no alternate trajectory was advanced;
4. the complete baseline replay result;
5. the raw historical checkpoint result;
6. the RC checkpoint result;
7. all five primary alternate final-window ratios;
8. all five primary alternate full-run ratios;
9. all six time-block classifications;
10. the centered algebraic relationship;
11. the RC projection relationship;
12. the Arakawa result;
13. the final frozen classification;
14. all claim boundaries;
15. that method superiority is not authorized.

---

## 43. Prospective runner inspection mode

The new runner `inspect` mode shall:

- parse and compile the source;
- require the exact filename;
- require LF-only UTF-8;
- verify branch `phase4_validation`;
- require the archived design checkpoint as `HEAD`;
- require only the new runner to be untracked;
- verify all source and evidence hashes;
- verify the nine output filenames;
- verify every CSV header list is unique;
- verify all expected row counts;
- verify the seven remediated operator IDs;
- verify the five primary alternate IDs;
- verify all classification thresholds;
- verify all integrity tolerances;
- verify exactly one `SpectralSolver` construction;
- verify project imports occur only in the run path;
- reject protected or selectable `run()` calls;
- reject selectable step calls;
- reject alternate-trajectory variables;
- reject solver `kx` or `ky` assignments;
- verify local RC wavenumber copies;
- verify raw route confinement to checkpoint logic;
- verify no raw route enters the full-run pseudo-spectral shadow;
- verify no spectral-slope fitting;
- verify no convergence calculation;
- write no files;
- construct no solver;
- execute no timestep;
- mutate no Git state.

Inspection shall end with:

```text
Remediated full Stage C numerical execution authorized by inspection: NO
```

---

## 44. Prospective execution preflight

A future `run` path shall require:

- branch `phase4_validation`;
- clean working tree;
- new runner committed and pushed;
- runner commit parent equals this design commit;
- runner commit changes exactly one file;
- working runner bytes equal committed bytes;
- remote branch equals local `HEAD`;
- protected solver hash unchanged;
- advection-operator blob unchanged;
- selectable-solver blob unchanged;
- all Stage B evidence identities unchanged;
- original partial Stage C evidence unchanged;
- localization evidence unchanged;
- focused remediation evidence unchanged;
- output directory Git-ignored;
- no prior remediated full-run directory;
- forcing hash unchanged;
- no full-run raw-derivative pseudo-spectral route.

A failed preflight creates no output directory.

---

## 45. Runtime integrity tolerances

| Check | Limit |
|---|---:|
| Baseline archive relative difference | `1e-11` |
| Baseline absolute floor | `1e-14` |
| Baseline helper normalized difference | `1e-15` |
| State mutation | exact zero |
| Centered form identity | `1e-12` |
| Skew identity | `1e-15` |
| RC pseudo projection identity | `1e-12` |
| Arakawa sign identity | `1e-12` |
| Transport/RHS sign identity | `1e-14` |
| RC spectral divergence | `1e-12` |
| RC imaginary ratio | `1e-13` |
| Raw checkpoint ratio reproduction relative tolerance | `1e-12` |
| Raw checkpoint ratio reproduction absolute tolerance | `1e-18` |
| RC checkpoint ratio reproduction relative tolerance | `1e-12` |
| RC checkpoint ratio reproduction absolute tolerance | `1e-18` |
| Checkpoint real derivative relative difference | `1e-10` |
| Checkpoint transport relative difference | `1e-10` |
| Checkpoint work absolute difference | `1e-14` |
| Checkpoint work relative difference | `1e-6` |
| Archived trajectory comparisons | `201 / 201` |
| Nonfinite values | none |

These are integrity tolerances.

They are not formal error estimates.

---

## 46. Progress reporting

The future runner should print progress every 500 loop indices:

```text
progress
t=<time>
Z=<enstrophy>
Rbase=<baseline work>
Rcons=<conservative work>
Rskew=<skew work>
Rps_rc=<RC unprojected work>
Rpsp_rc=<RC projected work>
Rarakawa=<Arakawa work>
max_imag=<maximum RC imaginary ratio>
```

At loop `3059`, it shall additionally print:

```text
historical raw checkpoint: PASS
real-compatible checkpoint: PASS
continuing remediated same-state audit
```

---

## 47. Successful console summary

A successful run should report:

```text
STAGE C REMEDIATED FULL SAME-STATE SHADOW AUDIT: COMPLETE
Baseline trajectory replay: PASS
Baseline per-step ledger reproduction: PASS
Archived comparison points: 201 / 201 PASS
Historical raw checkpoint: PASS
Real-compatible checkpoint: PASS
Baseline steps: 20001
Shadow methods: 7
Shadow rows: 140007
Time-block rows: 42
Nyquist checkpoint trace rows: 40
Nyquist checkpoint work rows: 6
Accepted trajectory changed by shadows: NO
Alternate trajectories executed: NO
Protected solver run loop called: NO
Method superiority authorized: NO
Classification: <one frozen classification>
```

---

## 48. Failure preservation

After the output directory is created, any failure must preserve:

- metadata;
- completed state-reference rows;
- completed shadow rows;
- completed checkpoint rows;
- last completed loop index;
- failed gate;
- failed operator;
- failed stage;
- source identities;
- partial inventory.

The runner shall print:

```text
STAGE C REMEDIATED FULL SAME-STATE SHADOW AUDIT: FAILED
Failed gate: <gate>
Partial evidence preserved at: <path>
Do not rerun automatically.
```

---

## 49. One-execution policy

Only one controlled remediated full-run execution may be authorized.

After completion or failure:

- do not rerun automatically;
- do not delete partial evidence;
- do not modify existing Stage C evidence;
- do not modify focused remediation evidence;
- do not alter the protected solver;
- do not relax a threshold;
- do not regenerate evidence silently;
- archive the result before considering further work.

---

## 50. Scientific limitations

Even a successful run cannot establish:

- formal temporal convergence;
- formal spatial convergence;
- physical correctness;
- long-time behavior of separately advanced alternate methods;
- method superiority;
- production-solver selection;
- turbulence;
- a cascade;
- an inertial range;
- a spectral law;
- production readiness.

It can establish only the same-state scalar-work behavior of the frozen
remediated operator set on one frozen baseline trajectory.

---

## 51. Permitted conclusions

A future successful report may state one of the six frozen classifications.

It may quantify:

- work reductions;
- sign reversals;
- block dependence;
- projection effects;
- centered product-rule defects;
- remediated pseudo-spectral work;
- Arakawa work;
- checkpoint reproduction.

It may not state that an alternate method should replace the baseline.

---

## 52. Current decision

The remediated full same-state Stage C audit is now specified at the design
level.

No new full-run runner has been created.

No new full-run static inspection has been performed.

No remediated 20,001-step execution has been authorized.

The protected baseline solver remains unchanged.

The accepted baseline update remains unchanged.

The historical raw failure remains preserved.

The focused remediation evidence remains preserved.

The next controlled task is to archive this design before creating the new
full-run runner.
