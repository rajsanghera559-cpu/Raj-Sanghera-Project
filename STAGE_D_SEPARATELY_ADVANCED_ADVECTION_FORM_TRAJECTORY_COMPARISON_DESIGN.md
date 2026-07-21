
# Stage D Separately Advanced Advection-Form Trajectory Comparison Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Current archive checkpoint:
  `44178fba82c2e1c6279f8bcd2350796f9871457d`
- Current archive commit message:
  `Archive Stage C remediated full same-state shadow audit evidence`
- Stage C remediated full completion report:
  `STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_COMPLETION_REPORT.md`
- Stage C remediated full completion-report SHA-256:
  `ABB2F348A678C59A5CDEAB9D6CDC8640870C998C3945CC883662AD2E36DCFB05`
- Stage C remediated full evidence inventory SHA-256:
  `142B74CF928AEE7E25407D434E29624129B64870619108BE9AAD6964264657A2`
- Stage C remediated full execution design:
  `STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_EXECUTION_DESIGN.md`
- Stage C remediated full execution-design SHA-256:
  `3FB9902A463E6C11F9E12E29F754131FB2B280DAABF180985030472701FDDA75`
- Stage C remediated full runner:
  `run_stage_c_remediated_full_same_state_shadow_audit.py`
- Stage C remediated full runner SHA-256:
  `9CD4551E52C5CF385E94ED2DB7356D5D9ED641ADB19377E9F97B1F1FB8FA9431`
- Focused remediation completion report:
  `STAGE_C_SHADOW_NYQUIST_REMEDIATION_VERIFICATION_COMPLETION_REPORT.md`
- Focused remediation completion-report SHA-256:
  `B3BB4E6B7442035975DF7C2774DCFF1720E51953DA0A3E37C81415AAFB618AAD`
- Stage B exact-ledger evidence report:
  `STAGE_B_EXACT_OPERATOR_LEDGER_EVIDENCE_REPORT.md`
- Stage B exact-ledger evidence-report SHA-256:
  `5419765B72A757A4C048761CDBC55B1AAD8ED2A0414E3D9E79CC118A64D40DE4`
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
  `2026-07-21T02:02:06+00:00`
- Document type:
  design only
- Stage D pilot runner created by this document:
  no
- Stage D full runner created by this document:
  no
- Numerical execution authorized now:
  no
- Protected source modification authorized:
  no
- Stage C evidence modification authorized:
  no
- Method ranking authorized:
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
- Lyapunov exponent: not authorized
- Predictability horizon: not authorized
- Method superiority: not authorized
- Production readiness: not authorized
- Unique physical causation: not authorized
- Baseline replacement: not authorized
- Generalization beyond the frozen initial condition and forcing: not authorized

---

## 1. Purpose

Stage C established the same-state result:

> **REMEDIATED SHADOW RESPONSE IS FORM-DEPENDENT AND MIXED**

On the exact same baseline current and RK2 stage states:

- the centered conservative form retained the baseline advection-work magnitude
  with the opposite sign;
- the centered skew-symmetric form was near-neutral;
- both verified real-compatible pseudo-spectral forms were near-neutral;
- the Arakawa form was near-neutral;
- the projected centered baseline mechanism check remained close to the
  baseline.

Stage C did not advance the alternate operators on their own states.

Stage D addresses the next distinct question:

> When each frozen advection form advances its own vorticity trajectory from
> the same initial condition under the same forcing, viscosity, timestep, RK2
> structure, and post-step mask, how do the resulting states, scalar budgets,
> spectra, and pairwise differences evolve over the tested horizon?

Stage D is not a method-selection experiment.

Stage D is not a convergence study.

Stage D does not assume that pointwise trajectory separation implies error.

Stage D distinguishes:

1. phase-sensitive state divergence;
2. scalar-budget divergence;
3. spectral-amplitude divergence;
4. numerical-integrity failure.

---

## 2. Scientific transition from Stage C to Stage D

### 2.1 Stage C same-state question

Stage C evaluated:

\[
A_m(\omega_n^{base}),
\qquad
A_m(\omega_s^{base}),
\]

for every operator \(m\), while only the baseline operator advanced the
trajectory.

This isolated operator-form dependence at identical states.

### 2.2 Stage D separate-trajectory question

Stage D evaluates:

\[
A_m(\omega_n^m),
\qquad
A_m(\omega_s^m),
\]

where every trajectory \(m\) has its own:

- accepted current state;
- RK2 stage state;
- streamfunction;
- velocity;
- nonlinear transport;
- unfiltered update;
- filtered accepted state.

Therefore:

\[
\omega_n^m
\neq
\omega_n^{base}
\]

is permitted and expected after trajectory separation begins.

### 2.3 Interpretation constraint

A growing state difference can arise from deterministic path dependence.

It does not by itself show that one method is more accurate.

Stage D must report phase-sensitive and phase-insensitive diagnostics
separately.

---

## 3. Stage D execution structure

Stage D shall be split into two separately archived phases.

### 3.1 Stage D1: short separate-trajectory pilot

Frozen pilot range:

```text
loop index 0 through 3059
completed updates 3060
final physical time 15.300
```

The pilot verifies:

- all seven independent trajectories are implemented correctly;
- all seven remain finite under the frozen configuration;
- the baseline trajectory reproduces the archive exactly;
- no trajectory shares state memory with another trajectory;
- evaluation order does not change any accepted state;
- real-compatible pseudo-spectral derivatives remain numerically real;
- exact discrete-budget ledgers close for every trajectory;
- output volume and runtime are controlled.

The pilot produces no long-horizon scientific classification.

### 3.2 Stage D2: full separate-trajectory comparison

Frozen full range:

```text
loop index 0 through 20000
completed updates 20001
final physical time 100.005
```

The full comparison may be designed and authorized only after:

1. the Stage D1 design is archived;
2. the Stage D1 runner is archived;
3. Stage D1 static inspection passes;
4. one Stage D1 pilot is executed;
5. Stage D1 evidence is audited and archived;
6. a separate Stage D2 execution authorization is archived.

### 3.3 Current authorization

This document authorizes only the future creation and static inspection of the
Stage D1 pilot runner after this design is committed.

It does not authorize Stage D1 numerical execution.

It does not authorize Stage D2 runner creation or execution.

---

## 4. Prospective runner identities

### 4.1 Stage D1 pilot runner

Prospective filename:

```text
run_stage_d_separate_trajectory_pilot.py
```

Required modes:

```powershell
python -B .\run_stage_d_separate_trajectory_pilot.py inspect
python -B .\run_stage_d_separate_trajectory_pilot.py run
```

### 4.2 Stage D2 full runner

Reserved future filename:

```text
run_stage_d_separate_trajectory_comparison.py
```

This design does not authorize creation of the Stage D2 runner.

---

## 5. Frozen numerical configuration

| Parameter | Value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Initial vorticity | exact zero |
| Forcing target RMS | `0.005` |
| Forcing SHA-256 | `504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB` |
| Integrator | explicit RK2 |
| Post-step operation | existing spectral mask |
| Pilot updates | `3060` |
| Pilot final time | `15.300` |
| Full updates | `20001` |
| Full final time | `100.005` |
| Adaptive timestep | prohibited |
| Spectral-slope fitting | prohibited |
| Random perturbations | prohibited |
| Ensemble members | `1` deterministic member |

The full horizon remains a transient comparison.

The baseline stationarity test did not establish full enstrophy stationarity by
`t = 100.005`.

Stage D shall not call the final window stationary.

---

## 6. Frozen trajectory registry

Stage D shall advance exactly seven independent trajectory IDs.

### 6.1 Baseline centered advective trajectory

```text
TRAJ_BASE_FD_ADVECTIVE_V1
```

Stage C operator source:

```text
BASE_FD_ADVECTIVE_V1
```

Transport:

\[
T_{BA}
=
uD_x^c\omega
+
vD_y^c\omega.
\]

Advection RHS:

\[
A_{BA}
=
-T_{BA}.
\]

Role:

- archived baseline replay;
- primary comparison reference.

---

### 6.2 Projected centered advective trajectory

```text
TRAJ_FD_ADVECTIVE_PROJECTED_V1
```

Stage C operator source:

```text
SHADOW_FD_ADVECTIVE_PROJECTED_V1
```

Transport:

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

Advection RHS:

\[
A_{BAP}
=
-T_{BAP}.
\]

Role:

- projection mechanism trajectory;
- secondary comparison;
- excluded from family-count rules unless explicitly stated.

---

### 6.3 Centered conservative trajectory

```text
TRAJ_FD_CONSERVATIVE_V1
```

Stage C operator source:

```text
SHADOW_FD_CONSERVATIVE_V1
```

Transport:

\[
T_{FC}
=
D_x^c(u\omega)
+
D_y^c(v\omega).
\]

Advection RHS:

\[
A_{FC}
=
-T_{FC}.
\]

Role:

- primary separately advanced trajectory.

---

### 6.4 Centered skew-symmetric trajectory

```text
TRAJ_FD_SKEW_V1
```

Stage C operator source:

```text
SHADOW_FD_SKEW_V1
```

Transport:

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

Advection RHS:

\[
A_{FS}
=
-T_{FS}.
\]

Role:

- primary separately advanced trajectory.

---

### 6.5 Real-compatible unprojected pseudo-spectral trajectory

```text
TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2
```

Stage C operator source:

```text
SHADOW_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2
```

Transport:

\[
T_{PSR}^{RC}
=
uD_x^{RC}\omega
+
vD_y^{RC}\omega.
\]

The nonlinear product is not projected before insertion into the RK2 RHS.

Advection RHS:

\[
A_{PSR}^{RC}
=
-T_{PSR}^{RC}.
\]

Role:

- primary separately advanced trajectory.

---

### 6.6 Real-compatible projected pseudo-spectral trajectory

```text
TRAJ_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2
```

Stage C operator source:

```text
SHADOW_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2
```

Transport:

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

Advection RHS:

\[
A_{PSP}^{RC}
=
-T_{PSP}^{RC}.
\]

Role:

- primary separately advanced trajectory.

---

### 6.7 Arakawa trajectory

```text
TRAJ_ARAKAWA_V1
```

Stage C operator source:

```text
SHADOW_ARAKAWA_V1
```

Existing project sign convention:

\[
T_A
=
-J_A(\psi,\omega),
\]

\[
A_A
=
J_A(\psi,\omega).
\]

Role:

- primary separately advanced trajectory.

---

## 7. Primary families

Primary trajectory families:

```text
CENTERED_ALGEBRAIC
PSEUDO_SPECTRAL_RC_NYQUIST
ARAKAWA
```

Mappings:

| Trajectory | Family |
|---|---|
| `TRAJ_FD_CONSERVATIVE_V1` | `CENTERED_ALGEBRAIC` |
| `TRAJ_FD_SKEW_V1` | `CENTERED_ALGEBRAIC` |
| `TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2` | `PSEUDO_SPECTRAL_RC_NYQUIST` |
| `TRAJ_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2` | `PSEUDO_SPECTRAL_RC_NYQUIST` |
| `TRAJ_ARAKAWA_V1` | `ARAKAWA` |

The projected centered advective trajectory is a secondary mechanism check.

---

## 8. Independent trajectory policy

For each trajectory \(m\), retain an independent accepted state:

\[
\omega_n^m.
\]

Every trajectory shall calculate its own:

\[
\psi_n^m,
\quad
u_n^m,
\quad
v_n^m,
\quad
A_{1,m},
\quad
\omega_{s,m},
\quad
A_{2,m},
\quad
\omega_{u,m},
\quad
\omega_{n+1,m}.
\]

No trajectory may use:

- another trajectory's vorticity;
- another trajectory's stage state;
- another trajectory's velocity;
- another trajectory's nonlinear transport;
- another trajectory's accepted next state.

The common objects are limited to immutable numerical configuration:

- grid;
- wavenumbers;
- viscosity;
- timestep;
- mask;
- forcing.

---

## 9. Per-trajectory RK2 update

For trajectory \(m\):

\[
\psi_{1,m}
=
\operatorname{streamfunction}(\omega_{n,m}),
\]

\[
(u_{1,m},v_{1,m})
=
\operatorname{velocity}(\psi_{1,m}),
\]

\[
A_{1,m}
=
A_m(
\omega_{n,m},
u_{1,m},
v_{1,m},
\psi_{1,m}
),
\]

\[
V_{1,m}
=
\nu\nabla^2\omega_{n,m},
\]

\[
N_{1,m}
=
A_{1,m}
+
V_{1,m}
+
F,
\]

\[
\omega_{s,m}
=
\omega_{n,m}
+
\Delta tN_{1,m},
\]

\[
\psi_{2,m}
=
\operatorname{streamfunction}(\omega_{s,m}),
\]

\[
(u_{2,m},v_{2,m})
=
\operatorname{velocity}(\psi_{2,m}),
\]

\[
A_{2,m}
=
A_m(
\omega_{s,m},
u_{2,m},
v_{2,m},
\psi_{2,m}
),
\]

\[
V_{2,m}
=
\nu\nabla^2\omega_{s,m},
\]

\[
N_{2,m}
=
A_{2,m}
+
V_{2,m}
+
F,
\]

\[
\omega_{u,m}
=
\omega_{n,m}
+
\frac{\Delta t}{2}
\left(
N_{1,m}
+
N_{2,m}
\right),
\]

\[
\omega_{n+1,m}
=
\operatorname{Re}
\left[
\mathcal F^{-1}
\left(
P\mathcal F(\omega_{u,m})
\right)
\right].
\]

The same forcing array is used for every trajectory and both RK2 stages.

---

## 10. Real-compatible pseudo-spectral derivative

Define local copied derivative wavenumbers:

\[
k_x^{RC}
=
\begin{cases}
0,&k_x=-N/2,\\
k_x,&\text{otherwise},
\end{cases}
\]

\[
k_y^{RC}
=
\begin{cases}
0,&k_y=-N/2,\\
k_y,&\text{otherwise}.
\end{cases}
\]

Requirements:

- derive the Nyquist location from the actual solver arrays;
- copy the solver wavenumber arrays;
- verify no shared memory;
- never assign to `solver.kx` or `solver.ky`;
- hash solver and local arrays before and after execution;
- retain complex inverse transforms for imaginary-ratio diagnostics;
- use the real part in the accepted pseudo-spectral trajectory RHS;
- require every accepted pseudo-spectral derivative ratio to be
  `<= 1e-13`.

The historical raw-\(ik\) derivative may be evaluated diagnostically at the
baseline checkpoint.

It may not enter either pseudo-spectral accepted trajectory.

---

## 11. Baseline replay gate

The baseline trajectory must reproduce the archived Stage B trajectory.

### Stage D1 pilot

Compare loop indices `0` through `3059` against the Stage B per-step ledger.

Required result:

```text
3060 / 3060 PASS
```

At loop `3059`, require the archived baseline hashes:

```text
current state:
7534D7C24F2666993BBD5B7B79E03B82B8F7F15665B41C30453351A18196E852

RK2 stage state:
01F5C093F544119D75C4903FBEBC8B809224CABEF12CE125FB94C6AA509BD2B7

filtered accepted state:
1A95D9BF2065E88B47E2E578B8862DB83B47D804288354C32299EF44809EE61E
```

### Stage D2 full comparison

Require:

```text
20001 / 20001 per-step Stage B ledger rows PASS
201 / 201 archived cadence comparisons PASS
```

A baseline mismatch stops the complete Stage D calculation.

---

## 12. Operator implementation cross-check

Stage D shall prove that its operator helpers reproduce Stage C on frozen
baseline states.

### Stage D1 cross-check loops

```text
0
3058
3059
```

### Stage D2 cross-check loops

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

At each cross-check loop:

1. read or stream the archived Stage C baseline-state operator rows;
2. evaluate every Stage D operator helper on the baseline state;
3. compare stage-1 work;
4. compare stage-2 work;
5. compare stage-weighted work;
6. compare imaginary-ratio diagnostics;
7. compare operator identity residuals.

These diagnostic cross-checks do not enter any accepted trajectory.

---

## 13. Memory-isolation gates

At initialization:

- every trajectory state must own its data;
- no two trajectory arrays may share memory;
- no trajectory state may share memory with forcing;
- no trajectory state may share memory with local wavenumber copies;
- no accepted and stage-state arrays may alias.

After every update:

- accepted state hashes for all other trajectories must remain unchanged;
- writeability flags must remain unchanged;
- the forcing hash must remain unchanged;
- solver-grid hashes must remain unchanged.

Any shared-state mutation is a numerical-integrity failure.

---

## 14. Evaluation-order invariance

Trajectory updates may be computed sequentially in software, but the accepted
mathematical update must be independent of evaluation order.

Frozen pilot sentinels:

```text
0
3058
3059
```

Frozen full-run sentinels:

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

1. clone all seven current states;
2. preview all seven accepted next states in forward registry order;
3. preview all seven accepted next states in reverse registry order;
4. require exact array equality or the frozen normalized tolerance;
5. require identical scalar ledgers;
6. accept the canonical forward-order result only after the comparison passes.

This gate detects hidden shared-state or order-dependent contamination.

---

## 15. Exact discrete enstrophy ledger per trajectory

For every accepted update and trajectory \(m\), calculate:

\[
\frac{
Z(\omega_{n+1,m})
-
Z(\omega_{n,m})
}{
\Delta t
}
=
R_{A,m}
+
R_{V,m}
+
R_{F,m}
+
R_{RK2,m}
+
R_{P,m}.
\]

Where:

- \(R_{A,m}\) is the exact RK2 advection contribution;
- \(R_{V,m}\) is the exact RK2 viscous contribution;
- \(R_{F,m}\) is the exact RK2 forcing contribution;
- \(R_{RK2,m}\) is the quadratic RK2 remainder;
- \(R_{P,m}\) is the exact post-step mask contribution.

Required checks:

- unfiltered closure;
- filtered closure;
- physical/spectral mask-loss cross-check;
- finite scalar values;
- exact sign convention;
- no omitted term.

The ledger is a numerical-integrity diagnostic.

It does not establish physical correctness.

---

## 16. Scalar trajectory diagnostics

For each trajectory and sampled time, record:

- energy;
- enstrophy;
- vorticity RMS;
- velocity RMS;
- energy injection;
- enstrophy injection;
- viscous energy dissipation;
- viscous enstrophy dissipation;
- advection enstrophy work;
- exact RK2 remainder;
- mask enstrophy change;
- normalized ledger closure;
- dominant spectral shell;
- low-\(k\) fraction `k <= 4`;
- tail fraction `k > 4`;
- high-\(k\) fraction `k >= 10`;
- maximum real-compatible imaginary ratio where applicable;
- finite-value status.

---

## 17. Pairwise trajectory metrics

There are:

\[
\binom{7}{2}
=
21
\]

trajectory pairs.

For pair \((a,b)\), calculate:

### 17.1 Phase-sensitive vorticity difference

\[
D_\omega(a,b)
=
\frac{
\operatorname{RMS}(
\omega_a-\omega_b
)
}{
\max(
\operatorname{RMS}(\omega_a),
\operatorname{RMS}(\omega_b),
10^{-30}
)
}.
\]

### 17.2 Velocity difference

\[
D_u(a,b)
=
\frac{
\sqrt{
\operatorname{RMS}(u_a-u_b)^2
+
\operatorname{RMS}(v_a-v_b)^2
}
}{
\max(
U_{rms,a},
U_{rms,b},
10^{-30}
)
}.
\]

### 17.3 State cosine similarity

\[
C_\omega(a,b)
=
\frac{
\langle\omega_a,\omega_b\rangle
}{
\max(
\|\omega_a\|_2
\|\omega_b\|_2,
10^{-30}
)
}.
\]

### 17.4 Scalar relative differences

Record symmetric relative differences for:

- energy;
- enstrophy;
- energy injection;
- enstrophy injection;
- viscous energy dissipation;
- viscous enstrophy dissipation.

### 17.5 Spectrum-amplitude distance

For nonnegative shell energies \(E_a(k)\) and \(E_b(k)\), normalize:

\[
p_a(k)
=
\frac{
E_a(k)
}{
\max(
\sum_j E_a(j),
10^{-30}
)
},
\]

and similarly for \(p_b\).

Record:

\[
D_{spec,L1}
=
\frac{1}{2}
\sum_k
|p_a(k)-p_b(k)|.
\]

Also record the Hellinger distance:

\[
D_H
=
\frac{1}{\sqrt{2}}
\left[
\sum_k
\left(
\sqrt{p_a(k)}
-
\sqrt{p_b(k)}
\right)^2
\right]^{1/2}.
\]

### 17.6 Shell-summary differences

Record differences in:

- dominant shell;
- `k <= 4` fraction;
- `k > 4` fraction;
- `k >= 10` fraction.

---

## 18. Phase-sensitive versus phase-insensitive interpretation

A large \(D_\omega\) with small scalar and spectral-amplitude differences shall
be described as:

```text
PHASE-SENSITIVE STATE SEPARATION WITH SCALAR AGREEMENT
```

It shall not be described as physical failure.

A large \(D_\omega\) with large scalar or spectral-amplitude differences shall
be described as:

```text
STATE AND SCALAR TRAJECTORY SEPARATION
```

Neither phrase ranks methods.

---

## 19. Divergence-onset records

For every pair, record the first sampled time at which:

\[
D_\omega
\ge
10^{-6},
\]

\[
D_\omega
\ge
10^{-4},
\]

\[
D_\omega
\ge
10^{-2},
\]

\[
D_\omega
\ge
10^{-1},
\]

and:

\[
D_\omega
\ge
0.5.
\]

Also record first sampled time for:

- energy relative difference `>= 0.01`;
- enstrophy relative difference `>= 0.01`;
- spectrum L1 distance `>= 0.05`;
- spectrum L1 distance `>= 0.10`.

These are operational threshold-crossing times.

They are not Lyapunov exponents.

They are not formal predictability horizons.

---

## 20. Sampling cadences

### 20.1 Trajectory diagnostic cadence

```text
every 10 loop indices
```

Full-run sampled loop set:

```text
0, 10, 20, ..., 20000
```

Expected samples per trajectory:

```text
2001
```

Expected full diagnostic rows:

\[
2001
\times
7
=
14007.
\]

### 20.2 Pairwise divergence cadence

Use the same 2,001 sampled loop indices.

Expected full pairwise rows:

\[
2001
\times
21
=
42021.
\]

### 20.3 Spectrum cadence

```text
every 500 loop indices
```

Full sampled loop set:

```text
0, 500, 1000, ..., 20000
```

Expected spectrum times:

```text
41
```

Expected finite shells per trajectory:

```text
45
```

Expected long-format spectrum rows:

\[
41
\times
7
\times
45
=
12915.
\]

---

## 21. Stage D1 pilot sampling counts

Pilot diagnostic loop set:

```text
0, 10, 20, ..., 3050, 3059
```

Expected pilot samples:

```text
307
```

Expected pilot trajectory diagnostic rows:

\[
307
\times
7
=
2149.
\]

Expected pilot pairwise rows:

\[
307
\times
21
=
6447.
\]

Expected pilot per-step integrity rows:

\[
3060
\times
7
=
21420.
\]

Expected pilot sentinel cross-check rows:

\[
3
\times
7
=
21.
\]

---

## 22. Stage D2 block structure

Use the existing six time blocks:

| Block | Time range | Expected updates |
|---:|---|---:|
| 1 | `0.005 <= t <= 20.005` | `4001` |
| 2 | `20.005 < t <= 40.005` | `4000` |
| 3 | `40.005 < t <= 60.005` | `4000` |
| 4 | `60.005 < t <= 80.005` | `4000` |
| 5 | `80.005 < t <= 100.005` | `4000` |
| 6 | full run | `20001` |

Block 5 is called the final comparison window.

It is not called a stationary window.

---

## 23. Snapshot policy

Stage D2 shall archive compressed vorticity snapshots at:

```text
loop index 0
loop index 3059
loop index 4000
loop index 8000
loop index 12000
loop index 16000
loop index 20000
```

For seven trajectories:

```text
49 vorticity arrays
```

Prospective file:

```text
trajectory_snapshots.npz
```

Required properties:

- NumPy compressed archive;
- no pickle;
- float64;
- one deterministic key per trajectory and loop;
- array shape `64 x 64`;
- snapshot manifest with SHA-256 per uncompressed array;
- total file size expected well below the GitHub 50 MB recommendation.

No full per-step fields are archived.

---

## 24. Evidence-size policy

The Stage C archive produced an approximately 85 MB CSV and triggered a
GitHub large-file warning.

Stage D shall avoid repeating that pattern.

Requirements:

- no uncompressed evidence file may exceed `40 MB`;
- no file may be committed if projected size exceeds `50 MB`;
- full per-step field arrays are prohibited;
- high-cadence outputs shall contain scalar diagnostics only;
- snapshots shall be compressed;
- evidence format shall be frozen before execution;
- Git LFS shall not be introduced after evidence generation;
- if projected output exceeds the limit, execution preflight must stop before
  creating the run directory.

---

## 25. Stage D1 pilot integrity limits

| Gate | Limit |
|---|---:|
| Baseline archive relative difference | `1e-11` |
| Baseline absolute floor | `1e-14` |
| Per-trajectory normalized filtered ledger closure | `1e-10` |
| Per-trajectory normalized unfiltered ledger closure | `1e-10` |
| Mask physical/spectral cross-check | `1e-12` |
| Centered skew identity | `1e-15` |
| Centered advective/conservative identity | `1e-12` |
| Arakawa sign identity | `1e-12` |
| Pseudo-spectral projection identity | `1e-12` |
| RC imaginary ratio | `1e-13` |
| State memory aliasing | none |
| State mutation | exact zero |
| Order-invariance normalized difference | `1e-15` |
| Nonfinite arrays or scalars | none |

These are implementation integrity limits.

They are not formal discretization-error estimates.

---

## 26. Stage D1 pilot pass rule

Return:

```text
STAGE D SEPARATE-TRAJECTORY PILOT: PASS
```

only when:

1. all seven trajectories complete 3,060 updates;
2. the baseline reproduces 3,060 Stage B rows;
3. baseline checkpoint hashes match;
4. all trajectory arrays remain finite;
5. all seven exact ledgers pass;
6. every RC imaginary-ratio gate passes;
7. every sentinel order-invariance check passes;
8. no state arrays share memory;
9. no source or evidence identities change;
10. the output file set and row counts are exact.

The pilot does not classify trajectory agreement.

---

## 27. Stage D1 pilot failure rule

Return:

```text
STAGE D SEPARATE-TRAJECTORY PILOT: NUMERICAL INTEGRITY FAILURE
```

when any mandatory gate fails.

Record:

- failed trajectory;
- failed gate;
- loop index;
- RK2 stage;
- last completed updates by trajectory;
- partial output inventory;
- source identities.

Do not convert a numerical-integrity failure into a method ranking.

---

## 28. Operational Stage D2 per-trajectory categories

These categories compare each trajectory to the baseline in block 5 and block
6.

### 28.1 Close in state and scalars

```text
TRAJECTORY CLOSE TO BASELINE UNDER FROZEN HORIZON
```

only if:

- median \(D_\omega \le 0.01\);
- 95th-percentile \(D_\omega \le 0.05\);
- median energy relative difference `<= 0.01`;
- median enstrophy relative difference `<= 0.01`;
- median spectrum L1 distance `<= 0.05`;
- all integrity gates pass.

### 28.2 State separated, scalar diagnostics close

```text
PHASE-SENSITIVE STATE SEPARATION WITH SCALAR AGREEMENT
```

only if:

- median \(D_\omega \ge 0.10\);
- median energy relative difference `<= 0.05`;
- median enstrophy relative difference `<= 0.05`;
- median spectrum L1 distance `<= 0.10`;
- all integrity gates pass.

### 28.3 State and scalar separation

```text
STATE AND SCALAR TRAJECTORY SEPARATION
```

only if:

- median \(D_\omega \ge 0.10\);
- at least one of:
  - median energy relative difference `> 0.10`;
  - median enstrophy relative difference `> 0.10`;
  - median spectrum L1 distance `> 0.10`;
- all integrity gates pass.

### 28.4 Intermediate separation

```text
INTERMEDIATE TRAJECTORY SEPARATION
```

when no prior operational rule applies and all integrity gates pass.

### 28.5 Unavailable under frozen configuration

```text
TRAJECTORY UNAVAILABLE UNDER FROZEN CONFIGURATION
```

only when a trajectory stops through a finite-value or integrity gate.

This does not state that the method is generally unstable.

---

## 29. Operational global Stage D2 classifications

A successful Stage D2 result may return one global classification.

### 29.1 Clustered response

```text
SEPARATELY ADVANCED TRAJECTORIES REMAIN CLUSTERED
```

when every primary alternate is close to the baseline in block 5 and block 6.

### 29.2 Phase separation with scalar clustering

```text
SEPARATELY ADVANCED TRAJECTORIES SHOW PHASE SEPARATION WITH SCALAR CLUSTERING
```

when:

- at least three primary alternates are phase-separated;
- no primary alternate has state-and-scalar separation;
- scalar and spectral differences remain within the frozen close limits.

### 29.3 Family-dependent response

```text
SEPARATELY ADVANCED TRAJECTORIES SHOW FAMILY-DEPENDENT RESPONSE
```

when:

- at least one primary family is close or scalar-close;
- at least one distinct primary family has state-and-scalar separation or
  intermediate separation;
- all integrity gates pass.

### 29.4 Broad state and scalar separation

```text
SEPARATELY ADVANCED TRAJECTORIES DIVERGE IN STATE AND SCALAR DIAGNOSTICS
```

when state-and-scalar separation occurs in at least two distinct primary
families in both block 5 and block 6.

### 29.5 Inconclusive

```text
SEPARATE-TRAJECTORY COMPARISON INCONCLUSIVE
```

when:

- required data are missing;
- baseline reproduction fails;
- denominators are unstable;
- a complete frozen classification cannot be formed.

### 29.6 Numerical integrity failure

```text
NUMERICAL INTEGRITY FAILURE
```

when a mandatory implementation gate fails.

---

## 30. Classification limitations

The Stage D2 categories are operational labels.

They do not establish:

- accuracy relative to an exact solution;
- method superiority;
- physical fidelity;
- asymptotic convergence;
- long-time invariant measures;
- stochastic robustness;
- ensemble behavior.

A trajectory close to the baseline is not necessarily more accurate.

A trajectory far from the baseline is not necessarily less accurate.

---

## 31. Stage D1 prospective output directory

Root:

```text
experiments/advection_form_trajectory_pilot/
```

Run prefix:

```text
stage_d_separate_trajectory_pilot_
```

No prior directory with that prefix may exist.

---

## 32. Stage D1 prospective output bundle

Required files:

1. `run_metadata.json`;
2. `trajectory_pilot_diagnostics.csv`;
3. `trajectory_pilot_pairwise_divergence.csv`;
4. `trajectory_pilot_integrity_per_step.csv`;
5. `trajectory_pilot_sentinel_crosscheck.csv`;
6. `trajectory_pilot_summary.json`;
7. `STAGE_D_SEPARATE_TRAJECTORY_PILOT_REPORT.md`;
8. `file_inventory.csv`.

No scientific trajectory category is produced by the pilot.

---

## 33. Stage D1 diagnostic schema

`trajectory_pilot_diagnostics.csv` expected rows:

```text
2149
```

Required fields:

- loop index;
- completed steps;
- physical time;
- trajectory ID;
- operator family;
- energy;
- enstrophy;
- vorticity RMS;
- velocity RMS;
- energy injection;
- enstrophy injection;
- viscous energy dissipation;
- viscous enstrophy dissipation;
- advection enstrophy work;
- RK2 remainder;
- mask enstrophy change;
- normalized filtered closure;
- dominant shell;
- low-\(k\) fraction;
- tail fraction;
- high-\(k\) fraction;
- maximum imaginary ratio;
- accepted-state SHA-256;
- finite status.

All headers must be unique.

---

## 34. Stage D1 pairwise schema

`trajectory_pilot_pairwise_divergence.csv` expected rows:

```text
6447
```

Required fields:

- loop index;
- completed steps;
- physical time;
- trajectory A;
- trajectory B;
- normalized vorticity RMS difference;
- normalized velocity difference;
- vorticity cosine similarity;
- energy relative difference;
- enstrophy relative difference;
- dominant-shell difference;
- low-\(k\)-fraction difference;
- tail-fraction difference;
- high-\(k\)-fraction difference;
- finite status.

Pilot spectra need not be archived at every pairwise sample.

---

## 35. Stage D1 integrity schema

`trajectory_pilot_integrity_per_step.csv` expected rows:

```text
21420
```

Required fields:

- loop index;
- completed steps;
- physical time;
- trajectory ID;
- unfiltered closure residual;
- filtered closure residual;
- normalized unfiltered closure;
- normalized filtered closure;
- mask cross-check residual;
- maximum imaginary ratio;
- state mutation count;
- state alias count;
- update finite;
- integrity pass.

---

## 36. Stage D1 sentinel schema

`trajectory_pilot_sentinel_crosscheck.csv` expected rows:

```text
21
```

Required fields:

- loop index;
- trajectory ID;
- forward accepted-state SHA-256;
- reverse accepted-state SHA-256;
- normalized accepted-state difference;
- ledger scalar difference;
- Stage C baseline-state operator-work reference;
- Stage D helper operator-work value;
- helper/reference difference;
- order-invariance pass;
- helper cross-check pass.

---

## 37. Stage D2 prospective output directory

Reserved root:

```text
experiments/advection_form_trajectory_comparison/
```

Reserved run prefix:

```text
stage_d_separate_trajectory_comparison_
```

No Stage D2 output directory may be created by the Stage D1 runner.

---

## 38. Stage D2 prospective output bundle

A future Stage D2 design should require:

1. `run_metadata.json`;
2. `trajectory_diagnostics.csv`;
3. `pairwise_trajectory_divergence.csv`;
4. `trajectory_spectra.csv`;
5. `trajectory_budget_blocks.csv`;
6. `pairwise_block_summary.csv`;
7. `divergence_threshold_crossings.csv`;
8. `trajectory_snapshots.npz`;
9. `snapshot_manifest.csv`;
10. `sentinel_operator_crosscheck.csv`;
11. `stage_d_summary.json`;
12. `STAGE_D_SEPARATELY_ADVANCED_TRAJECTORY_COMPARISON_REPORT.md`;
13. `file_inventory.csv`.

This file set is reserved, not currently authorized.

---

## 39. Stage D1 static inspection requirements

The future pilot runner `inspect` mode shall:

- parse and compile the source;
- require the exact pilot filename;
- require LF-only UTF-8;
- verify branch `phase4_validation`;
- require this archived design checkpoint as `HEAD`;
- require only the pilot runner to be untracked;
- verify all protected source and evidence identities;
- verify exactly seven trajectory IDs;
- verify independent state variables;
- verify no state aliasing pathways;
- verify one immutable forcing array;
- verify local RC wavenumber copies;
- verify no assignment to `solver.kx` or `solver.ky`;
- verify exactly one solver construction in the run path;
- reject protected or selectable `run()` calls;
- reject use of the Stage C same-state runner's accepted update;
- verify each method creates its own RK2 stage;
- verify the pilot stop index `3059`;
- verify all output headers are unique;
- verify exact pilot row counts;
- verify no Stage D2 classification strings;
- verify no spectral-slope fitting;
- verify no Lyapunov fitting;
- verify no convergence calculation;
- write no files;
- construct no solver;
- execute no timestep;
- mutate no Git state.

Inspection shall conclude:

```text
Stage D pilot numerical execution authorized by inspection: NO
Stage D full comparison authorized: NO
```

---

## 40. Stage D1 execution preflight

A future pilot `run` path shall require:

- clean working tree;
- exact branch;
- pilot runner committed and pushed;
- runner commit parent equals this design commit;
- runner commit changes exactly one file;
- working bytes equal committed bytes;
- remote branch equals local `HEAD`;
- all protected source hashes unchanged;
- Stage B evidence unchanged;
- Stage C evidence unchanged;
- no prior Stage D pilot output;
- output path Git-ignored;
- predicted output files each below `40 MB`;
- no Stage D2 output path creation.

A failed preflight creates no run directory.

---

## 41. Stage D1 progress reporting

Recommended progress every 250 loop indices:

```text
progress
t=<time>
E_base=<value>
Z_base=<value>
D_cons=<normalized vorticity difference from baseline>
D_skew=<normalized vorticity difference from baseline>
D_ps_rc=<normalized vorticity difference from baseline>
D_psp_rc=<normalized vorticity difference from baseline>
D_arakawa=<normalized vorticity difference from baseline>
max_closure=<maximum normalized ledger closure>
max_imag=<maximum RC imaginary ratio>
```

Progress values are descriptive only.

---

## 42. Stage D1 successful console summary

A successful pilot should report:

```text
STAGE D SEPARATE-TRAJECTORY PILOT: PASS
Pilot updates per trajectory: 3060
Trajectories: 7
Baseline Stage B rows reproduced: 3060 / 3060
Trajectory diagnostic rows: 2149
Pairwise rows: 6447
Integrity rows: 21420
Sentinel cross-check rows: 21
Finite trajectories: 7 / 7
Shared-memory violations: 0
Order-invariance failures: 0
Failed integrity gates: 0
Scientific trajectory classification produced: NO
Stage D full comparison authorized: NO
```

---

## 43. Failure preservation

After a pilot output directory exists, any failure must preserve:

- metadata;
- completed diagnostic rows;
- completed pairwise rows;
- completed integrity rows;
- last completed update by trajectory;
- failed trajectory;
- failed gate;
- failed stage;
- source identities;
- partial file inventory.

The runner shall print:

```text
STAGE D SEPARATE-TRAJECTORY PILOT: FAILED
Failed trajectory: <trajectory>
Failed gate: <gate>
Partial evidence preserved at: <path>
Do not rerun automatically.
```

---

## 44. One-execution policy

Only one Stage D1 pilot may be authorized.

After pilot completion or failure:

- do not rerun automatically;
- do not delete partial evidence;
- do not modify Stage B or Stage C evidence;
- do not modify protected source;
- do not relax thresholds;
- audit and archive the pilot before considering Stage D2.

---

## 45. Large-file and archive policy

Before numerical execution, the pilot runner shall estimate output size.

It must stop before execution when any projected file exceeds `40 MB`.

Future Stage D2 evidence shall use:

- cadence-limited scalar CSVs;
- compressed NPZ snapshots;
- deterministic manifests;
- no full per-step field archive.

The repository history shall not be rewritten to add LFS after evidence is
committed.

---

## 46. Scientific limitations

Even a successful Stage D2 comparison cannot establish:

- which trajectory is closest to an unknown exact solution;
- which operator is physically correct;
- which operator should replace the baseline;
- formal convergence;
- long-time invariant statistics;
- ensemble robustness;
- turbulence;
- cascade behavior;
- an inertial range;
- a spectral law.

It can establish only how the frozen separately advanced implementations differ
over the tested deterministic horizon.

---

## 47. Permitted Stage D reporting language

Permitted:

- trajectories remain close;
- trajectories separate;
- phase-sensitive difference grows;
- scalar diagnostics remain close;
- spectra remain close or separate;
- response is family-dependent;
- a trajectory is unavailable under the frozen configuration;
- numerical integrity gates pass or fail.

Prohibited:

- superior;
- best;
- preferred;
- most accurate;
- physically correct;
- validated replacement;
- production-ready.

---

## 48. Current decision

The Stage D separately advanced advection-form trajectory comparison is now
specified at the design level.

The first required implementation is a short, controlled Stage D1 pilot.

No Stage D runner has been created.

No Stage D numerical timestep has been executed.

No full Stage D comparison has been authorized.

The protected solver remains unchanged.

All Stage B and Stage C evidence remains unchanged.

The next controlled task is to archive this design before creating and
statically inspecting:

```text
run_stage_d_separate_trajectory_pilot.py
```
