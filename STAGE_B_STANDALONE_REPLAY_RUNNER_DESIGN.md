# Stage B Standalone Replay-Runner Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Source checkpoint:
  `6207be18147606f0a437e8d0ffa5cb5466d06325`
- Parent exact-ledger design:
  `STAGE_B_EXACT_OPERATOR_LEDGER_DESIGN_REVIEW.md`
- Parent exact-ledger design SHA-256:
  `584A94C8A857D4869A95CC01BE31108CDFBC201C0BF56C03A0A8F9860D083B4C`
- Parent separation design checkpoint:
  `f3f517578b0c9541d56dfb6968681f5884cc09a5`
- Stage A runner checkpoint:
  `9a7fea8441f6e3fcdb63dcfc578e3008359f1ecc`
- Stage A evidence checkpoint:
  `fb07d10891f2e950f2c6c7fc7e8de07c3f9cd118`
- Created UTC: `2026-07-20T05:19:28+00:00`
- Document type: prospective standalone-runner design
- Runner source created by this document: no
- Numerical replay authorized by this document: no
- Protected source modification authorized: no
- Existing evidence modification authorized: no
- Automatic rerun authorized: no

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

---

## 1. Purpose

This document freezes the architecture and behavior of one future standalone
Stage B replay runner.

The runner will reproduce the archived `N=64` multimode trajectory while
calculating the exact per-step enstrophy ledger defined at checkpoint
`6207be1`.

The future runner must answer:

> Within the implemented discrete RK2-plus-mask update, what scalar
> contributions did discrete advection, viscosity, forcing, the exact RK2
> quadratic remainder, and the post-step mask make to each accepted-step
> enstrophy change?

The runner will not modify the protected solver and will never call the
protected solver's `run()` method.

---

## 2. Required future runner identity

The future executable filename is frozen as:

```text
run_stage_b_exact_operator_ledger_replay.py
```

It shall support exactly two positional modes:

```powershell
python -B .\run_stage_b_exact_operator_ledger_replay.py inspect
python -B .\run_stage_b_exact_operator_ledger_replay.py run
```

No additional numerical mode is authorized.

The `inspect` path must be non-numerical.

The `run` path must execute at most one replay.

---

## 3. Protected and archived identities

The future runner shall freeze and verify the following SHA-256 values.

### 3.1 Protected sources

| File | SHA-256 |
|---|---|
| `project/solver/spectral_solver.py` | `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1` |
| `forcing_budget_diagnostic.py` | `A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B` |

### 3.2 Stage B designs

| File | SHA-256 |
|---|---|
| `STAGE_B_EXACT_OPERATOR_LEDGER_DESIGN_REVIEW.md` | `584A94C8A857D4869A95CC01BE31108CDFBC201C0BF56C03A0A8F9860D083B4C` |
| `STAGE_B_STANDALONE_REPLAY_RUNNER_DESIGN.md` | determined when this document is archived |

### 3.3 Archived longer-run evidence

Source directory:

```text
experiments/forcing_budget_stationarity/
forcing_budget_stationarity_20260719T083403Z_9a9f2e0/
```

Required source hashes:

| File | SHA-256 |
|---|---|
| `run_metadata.json` | `57640568F657C26E47F495B1BE7C4C23F54EF0ACB882250ECB596A426F504ED9` |
| `forcing_budget.csv` | `38D01CE7278979EB4D7433414C849F65820C729DC5928A964FFED1EB3E4F482F` |
| `forcing_spectra.csv` | `62235ED6A5C9BD17D4FF21D22A1F830EE637FC22F26ABD43B483359B5873275A` |
| `stationarity_window.csv` | `FD1C5017DC24C6BF9F12F3BB56E44631491BA8178B174968743175976C06ED9A` |
| `stationarity_summary.json` | `3573F19100A4BD817B97C603B3C13D0137AD56D1F52FD05D602DFFC6400DBE1E` |
| `file_inventory.csv` | `3745C4E279E304A1A04CA14CEFE04BAA0FABD1A6072BB2E4C407FAB78CA1A028` |

The archived files are read-only replay references.

---

## 4. Frozen numerical configuration

The replay shall use exactly:

| Parameter | Frozen value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Completed updates | `20001` |
| Final physical time | `100.005` |
| Initial vorticity | exact zero |
| Time integrator | external mirror of protected RK2 |
| Protected solver `run()` | not called |
| Dealiasing mask | inherited protected Boolean two-thirds mask |
| Ledger cadence | every timestep |
| High-cadence budget interval | 10 loop indices |
| High-cadence budget time spacing | `0.05` |
| Progress print interval | 500 loop indices |
| Progress print time spacing | `2.5` |

No parameter may change after execution begins.

---

## 5. Expected record counts

The future runner must enforce:

| Output | Expected records |
|---|---:|
| Exact per-step ledger | `20001` |
| High-cadence budget snapshots | `2001` |
| Final-window per-step ledger | `4001` |
| Time-block summary rows | `6` |

The high-cadence loop indices are

\[
0,10,20,\ldots,20000.
\]

The corresponding physical times are

\[
0.005,0.055,0.105,\ldots,100.005.
\]

The final-window ledger includes

\[
80.005\le t\le100.005.
\]

---

## 6. Frozen forcing

The future runner shall construct the same deterministic multimode vorticity
source:

\[
f_\omega(x,y)
=
c\Big[
\sin(2x)\cos(2y)
+
0.75\sin(3x)\cos(y)
+
0.50\sin(x)\cos(4y)
+
0.35\cos(4x-2y)
\Big].
\]

The raw field shall have its numerical mean subtracted.

The normalization coefficient shall be calculated once so that

\[
\sqrt{\langle f_\omega^2\rangle}=0.005.
\]

The expected forcing-array SHA-256 is:

```text
504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB
```

The array shall be:

- `float64`;
- C contiguous;
- finite;
- real;
- shape `(64,64)`;
- set nonwriteable after construction.

Its SHA-256 must be checked at every high-cadence output.

---

## 7. Exact update mirror

For every timestep, the runner shall reproduce the protected update without
calling `solver.run()`.

### 7.1 Current state

\[
\omega_n=\text{accepted state before the update}.
\]

### 7.2 Stage 1

Calculate spectral streamfunction and velocity from \(\omega_n\).

Use the existing centered periodic derivatives:

\[
D_x\omega_n
=
\frac{
\operatorname{roll}(\omega_n,-1,x)
-
\operatorname{roll}(\omega_n,+1,x)
}{
2\Delta x
},
\]

\[
D_y\omega_n
=
\frac{
\operatorname{roll}(\omega_n,-1,y)
-
\operatorname{roll}(\omega_n,+1,y)
}{
2\Delta x
}.
\]

Define:

\[
A_1
=
-\left(
u_nD_x\omega_n+v_nD_y\omega_n
\right),
\]

\[
V_1
=
\text{solver.laplacian\_spectral}(\omega_n),
\]

\[
F_1=f_\omega,
\]

\[
N_1=A_1+V_1+F_1.
\]

### 7.3 Stage state

\[
\omega_s
=
\omega_n+\Delta tN_1.
\]

### 7.4 Stage 2

Repeat the same velocity and centered-derivative procedure at \(\omega_s\).

Define:

\[
A_2
=
-\left(
u_sD_x\omega_s+v_sD_y\omega_s
\right),
\]

\[
V_2
=
\text{solver.laplacian\_spectral}(\omega_s),
\]

\[
F_2=f_\omega,
\]

\[
N_2=A_2+V_2+F_2.
\]

### 7.5 Unfiltered state

\[
\omega_u
=
\omega_n
+
\frac{\Delta t}{2}(N_1+N_2).
\]

### 7.6 Accepted state

\[
\widehat{\omega}_u=\mathcal{F}(\omega_u),
\]

\[
\widehat{\omega}_f=P\widehat{\omega}_u,
\]

\[
\omega_{n+1}
=
\operatorname{Re}
\left[
\mathcal{F}^{-1}(\widehat{\omega}_f)
\right].
\]

The complex inverse transform must be retained temporarily so its imaginary
RMS can be checked before selecting the real part.

---

## 8. Exact per-step enstrophy ledger

For

\[
Z(\omega)=\frac{1}{2}\langle\omega^2\rangle,
\]

record:

\[
Z_n=Z(\omega_n),
\]

\[
Z_s=Z(\omega_s),
\]

\[
Z_u=Z(\omega_u),
\]

\[
Z_f=Z(\omega_{n+1}).
\]

### 8.1 Component work rates

\[
R_A
=
\frac{1}{2}
\left[
\langle\omega_nA_1\rangle
+
\langle\omega_sA_2\rangle
\right],
\]

\[
R_V
=
\frac{1}{2}
\left[
\langle\omega_nV_1\rangle
+
\langle\omega_sV_2\rangle
\right],
\]

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

Define positive viscous dissipation:

\[
D_Z^{RK2}=-R_V.
\]

### 8.2 Exact RK2 remainder

\[
R_{\mathrm{RK2}}
=
\frac{\Delta t}{8}
\left\langle
(N_2-N_1)^2
\right\rangle.
\]

Also calculate the expanded cross-check:

\[
R_{\mathrm{RK2}}^{\mathrm{expanded}}
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

### 8.3 Exact mask terms

\[
\Delta Z_P=Z_f-Z_u,
\]

\[
R_P=\frac{\Delta Z_P}{\Delta t},
\]

\[
L_P=Z_u-Z_f,
\]

\[
D_{Z,P}=\frac{L_P}{\Delta t}=-R_P.
\]

The spectral loss is

\[
L_P^{spectral}
=
\frac{1}{2N^4}
\sum_{P(\boldsymbol{k})=0}
|\widehat{\omega}_u(\boldsymbol{k})|^2.
\]

### 8.4 Observed rates

\[
R_{Z,obs}^{u}
=
\frac{Z_u-Z_n}{\Delta t},
\]

\[
R_{Z,obs}^{f}
=
\frac{Z_f-Z_n}{\Delta t}.
\]

### 8.5 Reconstructed rates

\[
R_{Z,ledger}^{u}
=
R_A+R_V+R_F+R_{\mathrm{RK2}},
\]

\[
R_{Z,ledger}^{f}
=
R_A+R_V+R_F+R_{\mathrm{RK2}}+R_P.
\]

### 8.6 Closure residuals

\[
C_u
=
R_{Z,obs}^{u}
-
R_{Z,ledger}^{u},
\]

\[
C_f
=
R_{Z,obs}^{f}
-
R_{Z,ledger}^{f},
\]

\[
C_P
=
R_{Z,obs}^{f}
-
R_{Z,obs}^{u}
-
R_P.
\]

---

## 9. Normalization and tolerances

Define:

\[
S_Z
=
\max
\left(
|R_{Z,obs}^{f}|,
|R_A|+|R_V|+|R_F|+R_{\mathrm{RK2}}+|R_P|,
10^{-30}
\right).
\]

Normalized closure values are:

\[
\widehat C_u=\frac{|C_u|}{S_Z},
\]

\[
\widehat C_f=\frac{|C_f|}{S_Z},
\]

\[
\widehat C_P=\frac{|C_P|}{S_Z}.
\]

Mask-loss normalization:

\[
S_P
=
\max
\left(
L_P,
L_P^{spectral},
10^{-30}
\right),
\]

\[
\widehat C_{P,spectral}
=
\frac{
|L_P-L_P^{spectral}|
}{
S_P
}.
\]

Frozen limits:

| Integrity check | Limit |
|---|---:|
| Normalized unfiltered ledger closure | `1e-10` |
| Normalized filtered ledger closure | `1e-10` |
| Normalized filter bookkeeping closure | `1e-10` |
| Normalized physical/spectral mask-loss mismatch | `1e-10` |
| Normalized viscous identity mismatch | `1e-10` |
| Normalized forcing identity mismatch | `1e-12` |
| Normalized state reconstruction RMS | `1e-13` |
| Inverse-FFT imaginary/real RMS | `1e-13` |

Sign gates:

\[
R_{\mathrm{RK2}}\ge-10^{-14}S_Z,
\]

\[
R_P\le10^{-14}S_Z.
\]

A violation is a numerical-integrity failure.

---

## 10. Viscous and forcing cross-checks

At both stages, calculate:

\[
D_{Z,i}^{L}
=
-\langle\omega_iV_i\rangle,
\]

and independently:

\[
D_{Z,i}^{\nabla}
=
\nu
\langle
|\nabla\omega_i|^2
\rangle,
\]

using spectral gradients.

Record their signed and normalized differences.

At both stages, calculate the direct forcing work:

\[
\eta_{F,i}
=
\langle\omega_i f_\omega\rangle.
\]

Compare it with the enstrophy-injection value returned by the standalone
forcing-budget diagnostic at the same state.

The exact ledger uses the directly implemented arrays.

---

## 11. State and array reconstruction checks

The future runner must independently verify:

\[
N_1=A_1+V_1+F_1,
\]

\[
N_2=A_2+V_2+F_2,
\]

\[
\omega_s=\omega_n+\Delta tN_1,
\]

\[
\omega_u=\omega_n+\frac{\Delta t}{2}(N_1+N_2),
\]

\[
\omega_{n+1}
=
\operatorname{Re}
\left[
\mathcal{F}^{-1}
(P\mathcal{F}(\omega_u))
\right].
\]

For each reconstruction, calculate RMS difference and normalize by:

\[
\max(
\operatorname{RMS}(\text{reference state}),
10^{-30}
).
\]

All arrays and scalar outputs must be finite.

---

## 12. High-cadence budget table

Every 10 loop indices, calculate one accepted-state forcing-budget snapshot.

The table shall contain:

- loop index;
- completed steps;
- physical time;
- energy;
- enstrophy;
- forcing RMS;
- energy injection;
- enstrophy injection;
- viscous energy dissipation;
- viscous enstrophy dissipation;
- continuous energy RHS;
- continuous enstrophy RHS;
- interval duration;
- observed energy rate;
- trapezoidal mean continuous energy RHS;
- energy interval residual;
- normalized energy interval residual;
- observed enstrophy rate;
- trapezoidal mean continuous enstrophy RHS;
- enstrophy interval residual;
- normalized enstrophy interval residual;
- forcing SHA-256;
- all-values-finite flag.

The first high-cadence row has no prior-interval values.

---

## 13. Archived trajectory equivalence

At loop indices divisible by 100, the replay shall compare accepted-state
budget quantities with the 201 archived `0.5`-cadence snapshots.

Required comparison quantities:

- physical time;
- energy;
- enstrophy;
- forcing RMS;
- energy injection;
- enstrophy injection;
- viscous energy dissipation;
- viscous enstrophy dissipation;
- continuous energy RHS;
- continuous enstrophy RHS.

For each quantity define:

\[
\Delta q=q_{replay}-q_{archive},
\]

and

\[
\delta q
=
\frac{
|\Delta q|
}{
\max(
|q_{archive}|,
10^{-30}
)
}.
\]

Frozen replay-equivalence tolerances:

| Comparison | Limit |
|---|---:|
| Absolute physical-time difference | `1e-14` |
| Absolute forcing-RMS difference | `1e-14` |
| Relative state/budget difference | `1e-11` |
| Absolute state/budget floor | `1e-14` |

A comparison passes when either the relative or absolute tolerance passes.

All 201 archived matching times must be present.

A replay-equivalence failure is preserved and stops the replay.

---

## 14. Per-step ledger CSV schema

The future `operator_ledger_per_step.csv` shall include, in fixed order:

### Identity and time

- `loop_index`;
- `completed_steps`;
- `physical_time`;
- `dt`;
- `forcing_sha256`.

### State enstrophies

- `z_current`;
- `z_stage`;
- `z_unfiltered`;
- `z_filtered`.

### Stage-1 terms

- `stage1_advection_work_rate`;
- `stage1_viscous_work_rate`;
- `stage1_forcing_work_rate`;
- `stage1_total_work_rate`;
- `stage1_advection_rms`;
- `stage1_viscous_rms`;
- `stage1_total_rhs_rms`.

### Stage-2 terms

- `stage2_advection_work_rate`;
- `stage2_viscous_work_rate`;
- `stage2_forcing_work_rate`;
- `stage2_total_work_rate`;
- `stage2_advection_rms`;
- `stage2_viscous_rms`;
- `stage2_total_rhs_rms`.

### Stage-weighted terms

- `rk2_advection_rate`;
- `rk2_viscous_rate`;
- `rk2_viscous_dissipation_rate`;
- `rk2_forcing_rate`;
- `rk2_quadratic_remainder_rate`;
- `rk2_quadratic_remainder_expanded`;
- `rk2_remainder_crosscheck_residual`.

### Mask terms

- `mask_field_removal_rms`;
- `mask_enstrophy_change`;
- `mask_enstrophy_change_rate`;
- `mask_enstrophy_loss`;
- `mask_enstrophy_loss_rate`;
- `mask_enstrophy_loss_spectral`;
- `mask_enstrophy_loss_crosscheck_residual`;
- `normalized_mask_enstrophy_loss_crosscheck_residual`.

### Observed and reconstructed rates

- `observed_unfiltered_enstrophy_rate`;
- `unfiltered_ledger_rate`;
- `unfiltered_closure_residual`;
- `normalized_unfiltered_closure_residual`;
- `observed_filtered_enstrophy_rate`;
- `filtered_ledger_rate`;
- `filtered_closure_residual`;
- `normalized_filtered_closure_residual`;
- `filter_bookkeeping_residual`;
- `normalized_filter_bookkeeping_residual`.

### Viscous and forcing cross-checks

- `stage1_viscous_dissipation_actual`;
- `stage1_viscous_dissipation_gradient`;
- `stage1_viscous_identity_residual`;
- `normalized_stage1_viscous_identity_residual`;
- `stage2_viscous_dissipation_actual`;
- `stage2_viscous_dissipation_gradient`;
- `stage2_viscous_identity_residual`;
- `normalized_stage2_viscous_identity_residual`;
- `stage1_forcing_identity_residual`;
- `normalized_stage1_forcing_identity_residual`;
- `stage2_forcing_identity_residual`;
- `normalized_stage2_forcing_identity_residual`.

### Reconstruction and integrity

- `stage_reconstruction_rms`;
- `normalized_stage_reconstruction_rms`;
- `unfiltered_reconstruction_rms`;
- `normalized_unfiltered_reconstruction_rms`;
- `filtered_reconstruction_rms`;
- `normalized_filtered_reconstruction_rms`;
- `inverse_fft_imaginary_rms`;
- `normalized_inverse_fft_imaginary_rms`;
- `all_numeric_values_finite`;
- `rk2_remainder_sign_pass`;
- `mask_rate_sign_pass`;
- `all_integrity_gates_pass`.

---

## 15. Time blocks

The runner shall aggregate the exact ledger over:

1. `0.005 <= t <= 20.005`;
2. `20.005 < t <= 40.005`;
3. `40.005 < t <= 60.005`;
4. `60.005 < t <= 80.005`;
5. `80.005 < t <= 100.005`;
6. full run: `0.005 <= t <= 100.005`.

Expected timestep counts:

| Block | Count |
|---|---:|
| Block 1 | `4001` |
| Block 2 | `4000` |
| Block 3 | `4000` |
| Block 4 | `4000` |
| Block 5 | `4000` |
| Full run | `20001` |

---

## 16. Aggregate component statistics

For each block and each component

\[
X\in\{A,V,F,\mathrm{RK2},P,\mathrm{NFV},obs\},
\]

record:

- mean signed rate;
- median signed rate;
- mean absolute rate;
- maximum absolute rate;
- time-integrated signed contribution;
- time-integrated absolute activity;
- positive sign count;
- negative sign count;
- zero sign count.

Define:

\[
R_{\mathrm{NFV}}
=
R_A+R_{\mathrm{RK2}}+R_P.
\]

The observed component is the accepted-step observed enstrophy rate.

Also record closure statistics:

- median normalized unfiltered closure;
- maximum normalized unfiltered closure;
- median normalized filtered closure;
- maximum normalized filtered closure;
- median normalized mask cross-check mismatch;
- maximum normalized mask cross-check mismatch;
- failed integrity-gate count.

---

## 17. Attribution activity shares

For the three non-forcing/non-viscous components:

\[
X\in\{A,\mathrm{RK2},P\},
\]

define per-window absolute activity:

\[
A_X
=
\sum_{n\in W}
\Delta t|R_{X,n}|.
\]

Define:

\[
S_X
=
\frac{
A_X
}{
A_A+A_{\mathrm{RK2}}+A_P
}.
\]

Also define signed integrated contribution:

\[
I_X
=
\sum_{n\in W}
\Delta tR_{X,n}.
\]

Define:

\[
I_{\mathrm{NFV}}
=
I_A+I_{\mathrm{RK2}}+I_P.
\]

---

## 18. Frozen dominance tests

For component \(X\in\{A,\mathrm{RK2},P\}\), calculate:

### 18.1 Activity-share gate

\[
S_X\ge0.70.
\]

### 18.2 Sign-consistency gate

\[
\operatorname{sign}(I_X)
=
\operatorname{sign}(I_{\mathrm{NFV}}),
\]

with neither value treated as nonzero unless its magnitude exceeds
`1e-30`.

### 18.3 Integrated-reduction gate

\[
Q_X
=
1-
\frac{
|I_{\mathrm{NFV}}-I_X|
}{
\max(
|I_{\mathrm{NFV}}|,
10^{-30}
)
}.
\]

Require:

\[
Q_X\ge0.70.
\]

### 18.4 Concentration gate

Order the per-step values

\[
\Delta t|R_{X,n}|
\]

from largest to smallest.

Record the minimum number of steps required to account for 90% of the
component's total absolute activity.

Require:

\[
n_{90,X}\ge5.
\]

A leading-contributor classification requires all four gates.

---

## 19. Frozen attribution classifications

For each block, return exactly one of:

- `LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION`;
- `LEADING LEDGER CONTRIBUTOR: RK2 REMAINDER`;
- `LEADING LEDGER CONTRIBUTOR: MASK`;
- `MULTIPLE LEDGER CONTRIBUTORS`;
- `CANCELLING LEDGER CONTRIBUTORS`;
- `LEDGER ATTRIBUTION INCONCLUSIVE`;
- `NUMERICAL INTEGRITY FAILURE`.

Decision order:

1. any failed integrity gate:
   `NUMERICAL INTEGRITY FAILURE`;
2. exactly one component passes all dominance gates:
   corresponding `LEADING` classification;
3. more than one component passes all dominance gates:
   `MULTIPLE LEDGER CONTRIBUTORS`;
4. define cancellation ratio
   \[
   C=
   \frac{
   |I_{\mathrm{NFV}}|
   }{
   |I_A|+|I_{\mathrm{RK2}}|+|I_P|+10^{-30}
   };
   \]
   if `C <= 0.20`:
   `CANCELLING LEDGER CONTRIBUTORS`;
5. if at least two activity shares are `>=0.20`:
   `MULTIPLE LEDGER CONTRIBUTORS`;
6. otherwise:
   `LEDGER ATTRIBUTION INCONCLUSIVE`.

These are implemented-ledger classifications, not physical-causation claims.

The final-window classification is the primary Stage B result.

The full-run classification is secondary context.

---

## 20. Required output bundle

The future replay shall create one new immutable Git-ignored directory under:

```text
experiments/forcing_budget_stage_b_ledger/
```

Run-directory prefix:

```text
stage_b_exact_operator_ledger_
```

Required files:

1. `run_metadata.json`;
2. `operator_ledger_per_step.csv`;
3. `high_cadence_budget.csv`;
4. `operator_ledger_time_blocks.csv`;
5. `operator_ledger_final_window.csv`;
6. `operator_ledger_summary.json`;
7. `file_inventory.csv`.

No checkpoint arrays are included.

No shadow-test results are included.

---

## 21. Metadata requirements

`run_metadata.json` shall record:

- run ID;
- status;
- classification;
- UTC start and completion;
- Git branch;
- design commit;
- execution commit;
- runner path and SHA-256;
- both Stage B design hashes;
- protected source hashes;
- archived source hashes;
- Python version;
- NumPy version;
- operating system;
- float dtype;
- machine epsilon;
- frozen numerical configuration;
- forcing construction and SHA-256;
- output schema IDs;
- integrity tolerances;
- attribution thresholds;
- explicit claim boundaries;
- error type and message after failure.

---

## 22. Summary requirements

`operator_ledger_summary.json` shall include:

- all expected and observed record counts;
- all source identities;
- replay-equivalence results;
- maximum archived replay differences;
- all six time-block summaries;
- final-window attribution;
- full-run attribution;
- maximum closure residuals;
- maximum cross-check residuals;
- maximum imaginary RMS ratio;
- count and location of failed integrity gates;
- global maxima of advection, mask, and RK2 activity;
- final accepted-state budget snapshot;
- explicit limitations;
- explicit no-causal-attribution statement.

---

## 23. File inventory

`file_inventory.csv` shall record, for each non-inventory output:

- relative path;
- byte count;
- SHA-256;
- inventory note.

The inventory's own internal SHA-256 is omitted to avoid circular
self-reference.

The runner shall print the external inventory-file SHA-256 at completion.

---

## 24. Write and memory policy

The runner shall:

- write CSV rows incrementally;
- flush and `fsync` at controlled intervals;
- avoid retaining all 20,001 full rows in memory;
- retain only scalar accumulators needed for time-block summaries;
- write high-cadence rows incrementally;
- write final-window ledger rows incrementally;
- use temporary filenames and atomic replacement for JSON summaries;
- preserve completed rows after failure.

The full vorticity fields exist only as current-step temporary arrays.

---

## 25. Progress output

Every 500 loop indices, print:

- physical time;
- current enstrophy;
- observed accepted-step enstrophy rate;
- `R_A`;
- `R_V`;
- `R_F`;
- `R_RK2`;
- `R_P`;
- normalized filtered closure;
- current final-window status when applicable.

Progress output is descriptive only.

---

## 26. Failure-preservation policy

After output-directory creation, any failure must preserve:

- metadata with failure type and message;
- every completed per-step ledger row;
- every completed high-cadence budget row;
- every completed final-window row;
- the last completed loop index;
- the failed integrity-gate name;
- source hashes;
- partial inventory where possible.

The runner shall print:

```text
STAGE B NUMERICAL INTEGRITY FAILURE
Partial evidence preserved at: <path>
```

No automatic rerun is allowed.

---

## 27. Pre-execution repository gates

The future run path shall require:

- active branch `phase4_validation`;
- clean working tree;
- runner committed;
- runner commit parent equals the archived runner-design commit;
- runner commit changes exactly one file: the runner;
- working runner bytes equal committed runner bytes;
- all design and source hashes match;
- no prior Stage B output directory exists;
- planned output directory is Git ignored.

A failed preflight shall create no output directory.

---

## 28. Static inspection requirements

The future `inspect` mode shall:

- parse and compile the runner source;
- require LF-only runner bytes;
- verify exact filename;
- verify active branch;
- verify HEAD equals the archived runner-design checkpoint;
- require Git status to contain only the untracked runner;
- verify both Stage B design files and hashes;
- verify protected source hashes;
- verify archived evidence hashes;
- inspect AST without importing project modules;
- confirm project imports occur only inside the run function;
- reject any actual `solver.run()` call;
- reject dynamic `eval` or `exec`;
- reject `polyfit`, `curve_fit`, or spectral-slope fitting;
- verify all frozen constants;
- verify required output schemas;
- verify all exact-ledger formulas are represented;
- write no files;
- construct no solver;
- execute no numerical step;
- perform no Git mutation.

Inspection output must explicitly end with:

```text
Numerical replay authorized by inspection: NO
```

---

## 29. Runner archival workflow

After static inspection passes:

1. stage only `run_stage_b_exact_operator_ledger_replay.py`;
2. commit it as the sole child of the runner-design checkpoint;
3. push `phase4_validation`;
4. confirm a clean working tree;
5. stop.

The replay is not executed in the same command block that archives the runner.

A separate explicit user instruction is required to run it.

---

## 30. Expected inspection summary

The future runner inspection should report:

```text
STAGE B EXACT OPERATOR-LEDGER RUNNER INSPECTION: PASS
Configuration: N64, Re1000, dt0.005, steps20001
Ledger cadence: every step
High-cadence budget: every 10 steps / 0.05 time units
Expected ledger rows: 20001
Expected high-cadence rows: 2001
Expected final-window rows: 4001
Exact RK2 remainder formula: PRESENT
Exact physical/spectral mask-loss cross-check: PRESENT
Archived replay-equivalence gate: PRESENT
Protected source hashes: PASS
Project modules imported: NO
Solver constructed: NO
Numerical steps executed: NO
Files written: NO
Git mutations: NONE
Numerical replay authorized by inspection: NO
```

---

## 31. Scientific interpretation boundary

A completed Stage B replay may identify a leading **implemented ledger
contributor**.

It cannot by itself establish:

- why a different numerical method would behave differently;
- formal timestep convergence;
- formal resolution convergence;
- physical correctness;
- turbulence;
- a cascade;
- spectral-law validity;
- production readiness.

The existing longer-run classification remains unchanged unless a separately
designed stationarity test is performed.

---

## 32. Current decision

The standalone replay-runner architecture is now prospectively frozen.

> No executable replay runner is created or authorized by this document.

The next controlled task is to archive this runner design. After that, one
standalone runner may be created, statically inspected, committed, and stopped
before numerical execution.
