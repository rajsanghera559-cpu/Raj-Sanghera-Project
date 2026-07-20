# Stage B Exact Operator-Ledger Design Review

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Source checkpoint:
  `fb07d10891f2e950f2c6c7fc7e8de07c3f9cd118`
- Stage A runner checkpoint:
  `9a7fea8441f6e3fcdb63dcfc578e3008359f1ecc`
- Stage A evidence checkpoint:
  `fb07d10891f2e950f2c6c7fc7e8de07c3f9cd118`
- Parent separation design checkpoint:
  `f3f517578b0c9541d56dfb6968681f5884cc09a5`
- Created UTC: `2026-07-20T05:07:56+00:00`
- Document type: design review only
- New numerical execution authorized: no
- Replay runner creation authorized by this document: no
- Existing evidence modification authorized: no
- Protected solver modification authorized: no
- Protected solver `run()` call authorized: no

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

---

## 1. Purpose

This design review freezes an exact scalar enstrophy ledger for the existing
two-stage RK2 update and post-step spectral mask.

The ledger is intended to separate, without changing the numerical method:

1. discrete-advection enstrophy work;
2. viscous enstrophy work;
3. forcing enstrophy work;
4. the exact quadratic RK2 remainder;
5. exact pre-mask to post-mask enstrophy change;
6. total discrete-step enstrophy change.

The central requirement is an exact algebraic decomposition, to floating-point
roundoff, of every accepted timestep.

The design must be frozen before creating any replay runner.

---

## 2. Stage A result motivating Stage B

The archived Stage A result was:

> `ARCHIVED DATA SUPPORTS OPERATOR CORRELATION`

Stage A found:

- no support for residual growth under offline cadence coarsening;
- very strong full-run correlation between normalized enstrophy residual and
  `mask_removal_rms`;
- very strong correlations with stage advection RMS;
- very strong correlations with viscous enstrophy dissipation;
- very strong correlations with spectral-tail growth.

Those are descriptive associations only.

Stage A could not calculate:

- exact discrete-advection enstrophy work;
- exact enstrophy removed by the mask;
- exact RK2 algebraic remainder;
- local timestep sensitivity.

Stage B addresses the first three quantities.

---

## 3. Existing update that must be mirrored exactly

Let the accepted state before a step be

\[
\omega_n.
\]

The existing solver uses centered physical-space vorticity derivatives for
advection, spectral velocity, spectral diffusion, explicit two-stage RK2, and
a post-step two-thirds spectral mask.

### 3.1 Stage-1 transport field

Define the positive transport expression

\[
T_1
=
u_n D_x\omega_n
+
v_n D_y\omega_n,
\]

where `D_x` and `D_y` are the same centered periodic differences used by the
existing implementation.

The vorticity-RHS advection component is

\[
A_1=-T_1.
\]

This sign convention is frozen.

The ledger must never label `T_1` itself as the RHS advection component.

### 3.2 Stage-1 diffusion and forcing

Define

\[
V_1
=
\nu\nabla_h^2\omega_n,
\]

using the existing spectral diffusion function, and

\[
F_1=f_\omega.
\]

The stage-1 total RHS is

\[
N_1=A_1+V_1+F_1.
\]

### 3.3 RK2 stage state

The stage state is

\[
\omega_s
=
\omega_n+\Delta t\,N_1.
\]

### 3.4 Stage-2 components

Using the stage state, define

\[
T_2
=
u_s D_x\omega_s
+
v_s D_y\omega_s,
\]

\[
A_2=-T_2,
\]

\[
V_2
=
\nu\nabla_h^2\omega_s,
\]

\[
F_2=f_\omega,
\]

and

\[
N_2=A_2+V_2+F_2.
\]

The forcing is time independent, so

\[
F_1=F_2.
\]

### 3.5 Unfiltered RK2 state

The pre-mask RK2 state is

\[
\omega_u
=
\omega_n
+
\frac{\Delta t}{2}(N_1+N_2).
\]

### 3.6 Filtered accepted state

Let `P` denote the existing Boolean Fourier mask.

The accepted state is

\[
\omega_{n+1}
=
\operatorname{Re}
\left[
\mathcal{F}^{-1}
\left(
P\mathcal{F}(\omega_u)
\right)
\right].
\]

No alternate filter, derivative, advection form, or timestep rule is
authorized.

---

## 4. Discrete enstrophy definition

For any real grid field \(\omega\), define

\[
Z(\omega)
=
\frac{1}{2}
\langle \omega^2\rangle,
\]

where the brackets denote the arithmetic mean over all grid points.

The following states must each have a recorded enstrophy:

- `z_current = Z(omega_n)`;
- `z_stage = Z(omega_s)`;
- `z_unfiltered = Z(omega_u)`;
- `z_filtered = Z(omega_{n+1})`.

---

## 5. Exact pre-mask RK2 enstrophy identity

Define

\[
G
=
\frac{1}{2}(N_1+N_2),
\]

so that

\[
\omega_u=\omega_n+\Delta t\,G.
\]

Direct expansion gives

\[
\frac{Z(\omega_u)-Z(\omega_n)}{\Delta t}
=
\langle \omega_nG\rangle
+
\frac{\Delta t}{2}\langle G^2\rangle.
\]

For the explicit trapezoidal RK2 stage construction, the same rate can be
written exactly as

\[
R_Z^{u}
=
\frac{1}{2}
\left[
\langle\omega_nN_1\rangle
+
\langle\omega_sN_2\rangle
\right]
+
R_{\mathrm{RK2}},
\]

where

\[
R_{\mathrm{RK2}}
=
\frac{\Delta t}{8}
\left\langle
(N_2-N_1)^2
\right\rangle.
\]

This is an exact algebraic identity, subject only to floating-point roundoff.

The RK2 remainder satisfies

\[
R_{\mathrm{RK2}}\ge0
\]

in exact arithmetic.

It is not an empirical fit and not an observed-order estimate.

---

## 6. Exact stage-weighted component rates

Because

\[
N_i=A_i+V_i+F_i,
\]

the stage-weighted part decomposes linearly.

### 6.1 Advection rate

Define

\[
R_A
=
\frac{1}{2}
\left[
\langle\omega_nA_1\rangle
+
\langle\omega_sA_2\rangle
\right].
\]

This is the exact stage-weighted discrete-advection contribution appearing in
the RK2 enstrophy identity.

In continuous periodic incompressible flow, the corresponding ideal
advection contribution is zero.

The implemented centered advective form is not assumed to satisfy an exact
discrete zero-work identity.

The sign of `R_A` is descriptive:

- positive: discrete advection contributes net enstrophy during the step;
- negative: discrete advection removes net enstrophy during the step;
- near zero: approximate discrete enstrophy neutrality.

### 6.2 Viscous rate

Define

\[
R_V
=
\frac{1}{2}
\left[
\langle\omega_nV_1\rangle
+
\langle\omega_sV_2\rangle
\right].
\]

For a correctly resolved periodic spectral Laplacian and zero mean mode, this
is expected to be nonpositive.

Define the positive stage-weighted viscous dissipation

\[
D_Z^{\mathrm{RK2}}
=
-R_V.
\]

The ledger must record both the signed work `R_V` and the positive dissipation
`D_Z_RK2`.

### 6.3 Forcing rate

Define

\[
R_F
=
\frac{1}{2}
\left[
\langle\omega_nF_1\rangle
+
\langle\omega_sF_2\rangle
\right].
\]

Because the forcing is fixed,

\[
R_F
=
\left\langle
\frac{\omega_n+\omega_s}{2}
f_\omega
\right\rangle.
\]

This is the stage-weighted forcing contribution in the exact RK2 identity.

It must not be confused with a trapezoidal average of forcing injection
computed from two accepted output states separated by multiple timesteps.

---

## 7. Exact unfiltered ledger

The exact pre-mask rate is

\[
R_Z^{u}
=
R_A+R_V+R_F+R_{\mathrm{RK2}}.
\]

The directly observed pre-mask rate is

\[
R_{Z,\mathrm{obs}}^{u}
=
\frac{
Z(\omega_u)-Z(\omega_n)
}{
\Delta t
}.
\]

Define the unfiltered closure residual

\[
C_u
=
R_{Z,\mathrm{obs}}^{u}
-
\left(
R_A+R_V+R_F+R_{\mathrm{RK2}}
\right).
\]

The design requires

\[
C_u\approx0
\]

to the prospective floating-point closure tolerance.

---

## 8. Exact mask contribution

Define the signed mask enstrophy change

\[
\Delta Z_P
=
Z(\omega_{n+1})
-
Z(\omega_u).
\]

Define the signed mask rate

\[
R_P
=
\frac{\Delta Z_P}{\Delta t}.
\]

For the existing Boolean projection mask, the expected sign is

\[
R_P\le0
\]

up to roundoff.

For readability, also define the positive mask-loss quantities

\[
L_P
=
Z(\omega_u)
-
Z(\omega_{n+1}),
\]

\[
D_{Z,P}
=
\frac{L_P}{\Delta t}
=
-R_P.
\]

The exact ledger uses the signed quantity `R_P`.

The output must record both signed change and positive loss.

The existing `mask_removal_rms` remains useful but is only a field-difference
magnitude. It is not the exact enstrophy loss.

---

## 9. Spectral mask-loss cross-check

Let

\[
\widehat{\omega}_u
=
\mathcal{F}(\omega_u).
\]

For an `N x N` grid using NumPy's FFT normalization, Parseval gives

\[
Z(\omega_u)
=
\frac{1}{2N^4}
\sum_{\boldsymbol{k}}
\left|
\widehat{\omega}_u(\boldsymbol{k})
\right|^2.
\]

Because the mask is Boolean, the spectral enstrophy removed is

\[
L_P^{\mathrm{spectral}}
=
\frac{1}{2N^4}
\sum_{P(\boldsymbol{k})=0}
\left|
\widehat{\omega}_u(\boldsymbol{k})
\right|^2.
\]

The physical-space and spectral-space loss calculations must agree:

\[
L_P
\approx
L_P^{\mathrm{spectral}}.
\]

Record:

- `mask_enstrophy_loss_physical`;
- `mask_enstrophy_loss_spectral`;
- `mask_enstrophy_loss_crosscheck_residual`;
- normalized cross-check residual.

A mismatch beyond tolerance is a numerical-integrity failure.

---

## 10. Exact filtered-step ledger

The observed accepted-step rate is

\[
R_{Z,\mathrm{obs}}
=
\frac{
Z(\omega_{n+1})-Z(\omega_n)
}{
\Delta t
}.
\]

The complete exact ledger is

\[
R_{Z,\mathrm{ledger}}
=
R_A
+
R_V
+
R_F
+
R_{\mathrm{RK2}}
+
R_P.
\]

Define the accepted-step closure residual

\[
C_f
=
R_{Z,\mathrm{obs}}
-
R_{Z,\mathrm{ledger}}.
\]

The design requires

\[
C_f\approx0
\]

to the prospective floating-point closure tolerance.

This identity is the primary Stage B gate.

---

## 11. Exact relation between filtered and unfiltered rates

The implementation must verify

\[
R_{Z,\mathrm{obs}}
=
R_{Z,\mathrm{obs}}^{u}
+
R_P.
\]

Define

\[
C_P
=
R_{Z,\mathrm{obs}}
-
R_{Z,\mathrm{obs}}^{u}
-
R_P.
\]

The design requires

\[
C_P\approx0.
\]

This check isolates state bookkeeping from operator decomposition.

---

## 12. RK2 remainder checks

The runner must record

\[
R_{\mathrm{RK2}}
=
\frac{\Delta t}{8}
\langle(N_2-N_1)^2\rangle.
\]

Required checks:

1. `rk2_remainder_rate` is finite;
2. `rk2_remainder_rate >= -sign_tolerance`;
3. direct formula and expanded-form formula agree;
4. adding the remainder closes the unfiltered RK2 identity;
5. no observed-order interpretation is attached to the remainder.

An optional expanded-form cross-check is

\[
R_{\mathrm{RK2}}
=
\frac{\Delta t}{8}
\left[
\langle N_1^2\rangle
-
2\langle N_1N_2\rangle
+
\langle N_2^2\rangle
\right].
\]

---

## 13. Viscous identity cross-check

At each stage, calculate the standalone spectral-gradient dissipation:

\[
D_{Z,1}^{\nabla}
=
\nu
\left\langle
|\nabla\omega_n|^2
\right\rangle,
\]

\[
D_{Z,2}^{\nabla}
=
\nu
\left\langle
|\nabla\omega_s|^2
\right\rangle.
\]

Compare with the actual solver diffusion work:

\[
D_{Z,1}^{L}
=
-\langle\omega_nV_1\rangle,
\]

\[
D_{Z,2}^{L}
=
-\langle\omega_sV_2\rangle.
\]

Record

\[
C_{V,1}
=
D_{Z,1}^{L}-D_{Z,1}^{\nabla},
\]

\[
C_{V,2}
=
D_{Z,2}^{L}-D_{Z,2}^{\nabla}.
\]

These checks verify consistency between the solver's actual diffusion array and
the diagnostic spectral-gradient formula.

The exact ledger always uses the actual diffusion-array work.

---

## 14. Forcing identity cross-check

At each stage, calculate:

\[
\eta_{F,1}
=
\langle\omega_n f_\omega\rangle,
\]

\[
\eta_{F,2}
=
\langle\omega_s f_\omega\rangle.
\]

Verify that these match direct calls to the forcing-budget formula at the same
states.

The stage-weighted forcing rate is

\[
R_F
=
\frac{1}{2}
(\eta_{F,1}+\eta_{F,2}).
\]

The forcing-array SHA-256 must remain unchanged throughout the replay.

---

## 15. State reconstruction checks

For every timestep, verify the following identities.

### 15.1 RHS composition

\[
N_1=A_1+V_1+F_1,
\]

\[
N_2=A_2+V_2+F_2.
\]

### 15.2 Stage reconstruction

\[
\omega_s
=
\omega_n+\Delta tN_1.
\]

### 15.3 Unfiltered reconstruction

\[
\omega_u
=
\omega_n
+
\frac{\Delta t}{2}(N_1+N_2).
\]

### 15.4 Filter reconstruction

\[
\omega_{n+1}
=
\operatorname{Re}
\left[
\mathcal{F}^{-1}
\left(
P\mathcal{F}(\omega_u)
\right)
\right].
\]

### 15.5 Imaginary-part check

Before discarding the imaginary part of the inverse transform, record its RMS.

A material imaginary component is a numerical-integrity failure.

---

## 16. Prospective normalization

Define the exact-ledger rate scale

\[
S_Z
=
\max
\left(
|R_{Z,\mathrm{obs}}|,
|R_A|+|R_V|+|R_F|+R_{\mathrm{RK2}}+|R_P|,
10^{-30}
\right).
\]

Define normalized closure quantities

\[
\widehat{C}_u
=
\frac{|C_u|}{S_Z},
\]

\[
\widehat{C}_f
=
\frac{|C_f|}{S_Z},
\]

\[
\widehat{C}_P
=
\frac{|C_P|}{S_Z}.
\]

Define the mask cross-check scale

\[
S_P
=
\max
\left(
L_P,
L_P^{\mathrm{spectral}},
10^{-30}
\right),
\]

and

\[
\widehat{C}_{P,\mathrm{spectral}}
=
\frac{
|L_P-L_P^{\mathrm{spectral}}|
}{
S_P
}.
\]

---

## 17. Prospective integrity tolerances

The future runner must freeze these tolerances before execution.

| Check | Limit |
|---|---:|
| Normalized unfiltered ledger closure | `<= 1e-10` |
| Normalized filtered ledger closure | `<= 1e-10` |
| Normalized filter bookkeeping closure | `<= 1e-10` |
| Normalized physical/spectral mask-loss cross-check | `<= 1e-10` |
| Normalized viscous identity residual at each stage | `<= 1e-10` |
| Normalized forcing identity residual at each stage | `<= 1e-12` |
| Normalized state reconstruction RMS | `<= 1e-13` |
| Inverse-FFT imaginary RMS relative to real RMS | `<= 1e-13` |

Sign tolerances:

\[
R_{\mathrm{RK2}}
\ge
-10^{-14}S_Z,
\]

\[
R_P
\le
10^{-14}S_Z.
\]

These are integrity thresholds, not convergence tolerances.

---

## 18. Required per-step scalar schema

A future replay shall calculate the exact ledger every timestep.

The required scalar row includes:

### Identity and time

- `loop_index`;
- `completed_steps`;
- `physical_time`;
- `dt`;
- forcing SHA-256;
- protected solver SHA-256;
- runner SHA-256.

### State enstrophies

- `z_current`;
- `z_stage`;
- `z_unfiltered`;
- `z_filtered`.

### Stage-1 work

- `stage1_advection_work_rate`;
- `stage1_viscous_work_rate`;
- `stage1_forcing_work_rate`;
- `stage1_total_work_rate`.

### Stage-2 work

- `stage2_advection_work_rate`;
- `stage2_viscous_work_rate`;
- `stage2_forcing_work_rate`;
- `stage2_total_work_rate`.

### Stage-weighted rates

- `rk2_advection_rate`;
- `rk2_viscous_rate`;
- `rk2_viscous_dissipation_rate`;
- `rk2_forcing_rate`;
- `rk2_quadratic_remainder_rate`.

### Mask terms

- `mask_field_removal_rms`;
- `mask_enstrophy_change`;
- `mask_enstrophy_change_rate`;
- `mask_enstrophy_loss`;
- `mask_enstrophy_loss_rate`;
- `mask_enstrophy_loss_spectral`;
- `mask_enstrophy_loss_crosscheck_residual`;
- normalized mask cross-check residual.

### Observed and reconstructed rates

- `observed_unfiltered_enstrophy_rate`;
- `unfiltered_ledger_rate`;
- `unfiltered_closure_residual`;
- normalized unfiltered closure residual;
- `observed_filtered_enstrophy_rate`;
- `filtered_ledger_rate`;
- `filtered_closure_residual`;
- normalized filtered closure residual;
- `filter_bookkeeping_residual`;
- normalized filter bookkeeping residual.

### Cross-checks

- stage-1 viscous identity residual;
- stage-2 viscous identity residual;
- stage-1 forcing identity residual;
- stage-2 forcing identity residual;
- stage reconstruction residual;
- unfiltered reconstruction residual;
- filtered reconstruction residual;
- inverse-FFT imaginary RMS;
- all-values-finite flag;
- all-integrity-gates-pass flag.

---

## 19. Required aggregate summaries

Although every step is recorded, aggregate summaries must be produced for:

1. `0 < t <= 20.005`;
2. `20.005 < t <= 40.005`;
3. `40.005 < t <= 60.005`;
4. `60.005 < t <= 80.005`;
5. `80.005 < t <= 100.005`;
6. the full run.

For each component

\[
X\in
\{A,V,F,\mathrm{RK2},P\},
\]

report:

- mean signed rate;
- median signed rate;
- mean absolute rate;
- maximum absolute rate;
- time-integrated signed contribution;
- time-integrated absolute activity;
- positive, negative, and zero sign counts.

Also report all closure statistics and integrity-gate counts.

---

## 20. Attribution quantities

Define the exact non-forcing/non-viscous contribution

\[
R_{\mathrm{NFV}}
=
R_A
+
R_{\mathrm{RK2}}
+
R_P.
\]

The exact accepted-step identity becomes

\[
R_{Z,\mathrm{obs}}
=
R_F
+
R_V
+
R_{\mathrm{NFV}}.
\]

Over a window \(W\), define signed integrated contributions

\[
I_X
=
\sum_{n\in W}
\Delta t\,R_{X,n}.
\]

For the three non-forcing/non-viscous components, define absolute activity

\[
A_X
=
\sum_{n\in W}
\Delta t\,|R_{X,n}|.
\]

Define activity shares

\[
S_X
=
\frac{A_X}
{A_A+A_{\mathrm{RK2}}+A_P},
\]

when the denominator is nonzero.

These shares describe component activity, not unique causal percentages.

---

## 21. Dominance rule

A component may be classified as a **leading ledger contributor** within a
fixed window only when:

1. its absolute activity share is at least `0.70`;
2. its signed integrated contribution has the same sign as the net
   non-forcing/non-viscous contribution;
3. removing that component from the reconstructed non-forcing/non-viscous
   contribution reduces the absolute integrated discrepancy by at least
   `0.70`;
4. the result is not driven solely by fewer than five isolated steps;
5. all exact-ledger integrity checks pass.

Otherwise classify the window as:

- `MULTIPLE LEDGER CONTRIBUTORS`;
- `CANCELLING LEDGER CONTRIBUTORS`;
- or `LEDGER ATTRIBUTION INCONCLUSIVE`.

This rule does not establish physical causation.

---

## 22. Relationship to the archived interval residual

The archived residual used accepted-state snapshots separated by `0.5` time
units and a trapezoidal forcing-plus-viscosity RHS.

The exact per-step ledger will answer a different, more precise question:

> What scalar contribution did each implemented discrete component make to the
> accepted-step enstrophy change?

The future analysis must compare:

1. archived `0.5`-interval residual;
2. reconstructed `0.5` residual from high-cadence accepted states;
3. exact sum of per-step ledger components across the same interval.

This comparison separates interval quadrature from implemented discrete
operator contributions.

---

## 23. Required secondary controls

The future replay must also record:

- existing stage-1 and stage-2 advection RMS;
- existing mask-removal RMS;
- enstrophy;
- vorticity RMS;
- tail fraction above shell 4 at spectrum times;
- high-wave-number fraction at `k>=10` at spectrum times.

These preserve continuity with Stage A correlation results.

The exact ledger values, not the RMS proxies, are authoritative for Stage B.

---

## 24. Output architecture for a later replay

A later authorized replay should write a new immutable Git-ignored directory
containing at minimum:

1. `run_metadata.json`;
2. `operator_ledger_per_step.csv`;
3. `high_cadence_budget.csv`;
4. `operator_ledger_time_blocks.csv`;
5. `operator_ledger_final_window.csv`;
6. `operator_ledger_summary.json`;
7. `file_inventory.csv`.

Checkpoint arrays and shadow-test outputs are not part of Stage B.

They belong to a later separately authorized stage.

---

## 25. Failure-preservation policy

If a future replay fails after output-directory creation:

- preserve every completed scalar row;
- preserve metadata with failure type and message;
- preserve source hashes;
- preserve the last completed step;
- preserve the failed integrity-gate name;
- do not delete the output directory;
- do not rerun automatically.

A failed exact-ledger check is evidence and must not be silently bypassed.

---

## 26. Static inspection requirements for a later runner

Before execution, a standalone runner must pass static inspection confirming:

- exact source checkpoint and parent commit;
- exact design SHA-256;
- exact protected solver SHA-256;
- exact forcing-budget diagnostic SHA-256;
- no protected source modification;
- no `solver.run()` call;
- no alternate advection derivative;
- no alternate diffusion operator;
- no alternate filter;
- no alternate forcing;
- no spectral-slope fit;
- all required ledger formulas present;
- all required output fields present;
- no numerical execution during inspection;
- no files written during inspection.

---

## 27. Design-review conclusions

This review freezes the following exact decomposition:

\[
\boxed{
\frac{
Z(\omega_{n+1})-Z(\omega_n)
}{
\Delta t
}
=
R_A
+
R_V
+
R_F
+
R_{\mathrm{RK2}}
+
R_P
}
\]

with

\[
R_{\mathrm{RK2}}
=
\frac{\Delta t}{8}
\left\langle
(N_2-N_1)^2
\right\rangle,
\]

and

\[
R_P
=
\frac{
Z(\omega_{n+1})-Z(\omega_u)
}{
\Delta t
}.
\]

This formulation replaces qualitative proxy attribution with an exact
implemented-step ledger.

Stage A's strong correlations remain useful motivation, but they do not
determine the outcome in advance.

---

## 28. Current decision

The Stage B exact operator-ledger design review is complete.

> No numerical replay is authorized by this document.

The next controlled task is to archive this design review and then create one
standalone replay-runner design that implements these frozen identities
without modifying the protected solver.
