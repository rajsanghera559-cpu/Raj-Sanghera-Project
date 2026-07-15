# Phase 13C — Reference-Solution and Source-Term Audit Report

## 0. Document control

- Project: Raj-Sanghera-Project
- Phase: 13C
- Phase title: Reference-Solution and Source-Term Audit
- Starting checkpoint:
  `v0.5.46-phase13B-benchmark-and-continuous-equation-specification`
- Starting commit:
  `2351aeb8cedbd929f5ea5a5eae62de49b3bdc7ae`
- Governing specification:
  `PHASE13B_BENCHMARK_AND_CONTINUOUS_EQUATION_SPECIFICATION.md`
- Phase 13C audit status: pass
- Production solver imports: none
- Solver object instantiations: none
- Solver methods executed: none
- Simulations executed: none
- Numerical time steps executed: none
- Formal refinement sequences executed: none
- Solver source changes: none
- Convergence claims authorized: none
- Physical-validation claims authorized: none

Phase 13C independently audits the exact reference fields, analytic derivatives,
continuous residuals, Fourier support, zero-mean conditions, compatibility
projection, and manufactured source definitions specified in Phase 13B.

Phase 13C does not implement or execute a production verification harness.

No convergence claim is made.

---

## 1. Audit boundary

Phase 13C audited:

- periodicity;
- real-valuedness;
- finiteness;
- streamfunction–vorticity consistency;
- velocity signs and coordinate axes;
- analytic spatial derivatives;
- analytic time derivatives;
- exact nonlinear advection;
- continuous zero-mean conditions;
- finite Fourier support where applicable;
- the O2 sampled discrete-mean issue;
- the O2 compatibility projection;
- the Track L viscous-decay identity;
- the Track M manufactured source;
- the Track M continuous residual;
- the Track M RK2 source-stage times;
- repository and protected-source integrity.

Phase 13C did not:

- import `project`;
- import a project solver module;
- instantiate `SpectralSolver`;
- instantiate `SelectableAdvectionSolver`;
- call `compute_advection()`;
- call `compute_rhs_selectable()`;
- call `step_once_selectable()`;
- call `SelectableAdvectionSolver.run()`;
- execute an RK2 update;
- run a simulation;
- run a spatial refinement sequence;
- run a time-step refinement sequence;
- modify solver source;
- establish numerical convergence.

---

## 2. Independent audit routes

Three complementary audit routes were used.

### Route A — exact symbolic derivation

SymPy exact arithmetic independently derived, from each primitive
streamfunction:

`omega = Laplacian(psi)`

`u = partial_y psi`

`v = -partial_x psi`

`adv = u * partial_x omega + v * partial_y omega`

For Track M, the source was independently derived as:

`s_M = partial_t omega_M + adv_M - nu * Laplacian(omega_M)`

Declared expressions and independently derived expressions were required to
simplify to exact zero difference.

### Route B — independent high-precision differentiation

mpmath used 80 decimal digits and numerical differentiation directly from the
primitive streamfunctions.

The declared expressions were tested at four predeclared points:

| Point | x | y | t | nu |
|---|---|---|---|---|
| P1 | `pi/7` | `pi/11` | `0` | `1/1000` |
| P2 | `2*pi/9` | `5*pi/13` | `1/10` | `1/100` |
| P3 | `7*pi/12` | `4*pi/15` | `7/10` | `1/10` |
| P4 | `13*pi/17` | `9*pi/19` | `3/2` | `1/37` |

The predeclared residual threshold was:

`maximum absolute residual <= 1e-50`

### Route C — Fourier-support and mean analysis

Explicit Fourier expansion was used to audit:

- exact finite support for O1, Track L, and Track M;
- absence of zero Fourier modes;
- candidate-mask retention;
- the O2 sampled discrete mean;
- the O2 compatibility projection.

No error-rate fit was performed.

---

## 3. Audit environment

The read-only audit used:

| Component | Version or setting |
|---|---|
| Python | `3.14.5` |
| SymPy | `1.14.0` |
| mpmath | `1.3.0` |
| NumPy availability check | `2.4.4` |
| Python isolated mode | enabled |
| Python bytecode writing | disabled |
| Decimal precision | 80 digits |
| Residual threshold | `1e-50` |
| O2 post-projection mean threshold | `1e-70` |

No package was installed during Phase 13C.

---

## 4. Common reference-field checks

All four benchmark tracks passed the applicable common checks:

| Check | O1 | O2 | L | M |
|---|---:|---:|---:|---:|
| Periodic on `[0, 2*pi)^2` | PASS | PASS | PASS | PASS |
| Real-valued | PASS | PASS | PASS | PASS |
| Finite | PASS | PASS | PASS | PASS |
| `Laplacian(psi) = omega` | PASS | PASS | PASS | PASS |
| `u = partial_y psi` | PASS | PASS | PASS | PASS |
| `v = -partial_x psi` | PASS | PASS | PASS | PASS |
| Axis convention | PASS | PASS | PASS | PASS |
| Analytic derivative consistency | PASS | PASS | PASS | PASS |

---

## 5. Track O1 audit

Benchmark identifier:

`O1_BANDLIMITED_TWO_MODE_V1`

The audited streamfunction is:

`psi_O1
 = sin(x) * sin(y)
   + (1/4) * cos(2*x) * cos(y)`

The independently derived vorticity matched:

`omega_O1
 = -2 * sin(x) * sin(y)
   - (5/4) * cos(2*x) * cos(y)`

The independently derived velocity signs matched the Phase 13B convention.

The independently derived nonlinear advection matched:

`adv_O1 = (3/16) * F_O1`

where:

`F_O1
 = cos(x)
   + 3 * cos(x) * cos(2*y)
   - 3 * cos(3*x)
   - cos(3*x) * cos(2*y)`

Results:

- streamfunction–vorticity identity: PASS;
- velocity sign and axis identity: PASS;
- vorticity derivative identities: PASS;
- exact advection identity: PASS;
- nonlinear term nonzero: PASS;
- continuous zero mean: PASS;
- periodicity: PASS;
- real-valuedness and finiteness: PASS.

Fourier support:

- O1 vorticity:
  `(1,1)` and `(2,1)` in absolute wave-number coordinates;
- O1 advection:
  `(1,0)`, `(1,2)`, `(3,0)`, and `(3,2)`.

O1 is mathematically admissible as a later exact operator benchmark.

O1 remains unsuitable for a guaranteed rate fit if its numerical error reaches
the floating-point floor before a useful pre-floor sequence exists.

---

## 6. Track O2 audit

Benchmark identifier:

`O2_ANALYTIC_BROAD_SPECTRUM_V1`

The fixed coefficients are:

`a = 1/2`

`b = 1/3`

The audited primitive field is:

`q = a*cos(x) + b*cos(y)`

`psi_O2 = exp(q) - C_ab`

The independently derived vorticity matched:

`omega_O2 = exp(q) * H`

where:

`H
 = a^2*sin(x)^2
   - a*cos(x)
   + b^2*sin(y)^2
   - b*cos(y)`

The independently derived nonlinear advection matched:

`adv_O2
 = -2*a*b
   * (a*cos(x) - b*cos(y))
   * exp(2*q)
   * sin(x)
   * sin(y)`

Results:

- streamfunction–vorticity identity: PASS;
- velocity sign and axis identity: PASS;
- exact advection identity: PASS;
- nonlinear term nonzero: PASS;
- gauge independence: PASS;
- constant vorticity-offset advection invariance: PASS;
- continuous zero mean by periodic boundary flux: PASS;
- periodicity: PASS;
- real-valuedness and finiteness: PASS.

O2 is analytic and non-band-limited.

No finite grid represents all O2 Fourier modes.

No spectral or exponential convergence claim follows from the analytic
definition alone.

---

## 7. O2 sampled-mean diagnostic

The exact continuous O2 vorticity has zero mean because it is the periodic
Laplacian of a smooth periodic streamfunction.

Sampling a non-band-limited analytic function can nevertheless produce a small
nonzero discrete arithmetic mean.

The 80-digit diagnostic produced:

| N | Raw sampled mean | Mean after projection |
|---:|---:|---:|
| 16 | `-5.88775987836829210189262e-21` | `1.2257622e-83` |
| 32 | `-4.34553254558087297954891e-52` | `-1.3899210e-82` |
| 64 | `4.15334253213540923319155e-82` | `-1.7469775e-83` |
| 128 | `4.55056999861150103265227e-82` | `1.9627416e-83` |

These values were recorded as a diagnostic only.

No rate was fitted.

No convergence interpretation was assigned to the sampled means.

---

## 8. O2 compatibility-projection decision

Phase 13C approves the following fixed compatibility rule for a later O2
operator benchmark.

For each native grid, first evaluate:

`omega_O2_raw[i,j] = omega_O2(x_i, y_j)`

Then compute and record:

`m_N = discrete_mean(omega_O2_raw)`

Define:

`omega_O2_compatible = omega_O2_raw - m_N`

Required later behavior:

1. Record `m_N` for every grid.
2. Use `omega_O2_compatible` as the sampled vorticity supplied to the numerical
   operator path.
3. Evaluate exact `adv_O2` directly from the analytic expression.
4. Do not construct exact advection using a production numerical derivative.
5. Do not subtract a fitted or cross-grid mean.
6. Do not change the projection rule after viewing formal results.
7. Do not interpret the removed mean as a physical vorticity mode.
8. Do not use O2 as a time-evolution benchmark under this operator-only rule.

The projection is admissible because a constant vorticity offset has zero
gradient, and the independent symbolic audit confirmed advection invariance
under a constant vorticity offset.

The compatible discrete means passed the predeclared `1e-70` threshold.

---

## 9. Track L audit

Benchmark identifier:

`L_EQUAL_EIGENVALUE_DECAY_V1`

The audited exact field is:

`Phi_L = sin(3*x) + cos(3*y)`

`omega_L = exp(-9*nu*t) * Phi_L`

`psi_L = -(1/9) * omega_L`

Results:

- `Laplacian(Phi_L) = -9*Phi_L`: PASS;
- `Laplacian(psi_L) = omega_L`: PASS;
- velocity sign and axis identity: PASS;
- exact nonlinear advection equals zero: PASS;
- `partial_t omega_L = nu*Laplacian(omega_L)`: PASS;
- exact source `s_L = 0`: PASS;
- continuous zero mean: PASS;
- periodicity: PASS;
- real-valuedness and finiteness: PASS.

Track L Fourier support is:

- `(3,0)`;
- `(0,3)`.

Track L remains a linear diffusion and external time-step benchmark.

It does not verify nonlinear advection.

A later Track L evolution path must bypass both nonlinear advection and the
inherited baseline forcing.

---

## 10. Track M audit

Benchmark identifier:

`M_TWO_RATE_NONLINEAR_MMS_V1`

The fixed amplitudes are:

`A(t) = exp(-t)`

`B(t) = (1/4)*exp(-2*t)`

The exact streamfunction is:

`psi_M = A*f + B*g`

where:

`f = sin(x)*sin(y)`

`g = cos(2*x)*cos(y)`

The exact vorticity is:

`omega_M = -2*A*f - 5*B*g`

The independently derived nonlinear advection matched:

`adv_M = (3/4)*A*B*F_O1`

The exact time derivative matched:

`partial_t omega_M = 2*A*f + 10*B*g`

The exact vorticity Laplacian matched:

`Laplacian(omega_M) = 4*A*f + 25*B*g`

The manufactured source is:

`s_M
 = (2 - 4*nu)*A*f
   + (10 - 25*nu)*B*g
   + (3/4)*A*B*F_O1`

Results:

- streamfunction–vorticity identity: PASS;
- velocity sign and axis identity: PASS;
- exact time derivative: PASS;
- exact vorticity Laplacian: PASS;
- exact nonlinear advection: PASS;
- nonlinear term nonzero: PASS;
- source sign and formula: PASS;
- continuous residual: PASS;
- continuous zero mean: PASS;
- periodicity: PASS;
- real-valuedness and finiteness: PASS.

The continuous residual identity passed:

`partial_t omega_M
 - (
     -adv_M
     + nu*Laplacian(omega_M)
     + s_M
   )
 = 0`

---

## 11. Independent Track M source routes

The Track M source identity was checked by at least two independent routes.

### Route 1 — exact symbolic derivation

The source was regenerated from:

`partial_t omega_M + adv_M - nu*Laplacian(omega_M)`

The difference from the declared source simplified exactly to zero.

Result: PASS.

### Route 2 — 80-digit numerical differentiation

Time derivatives, spatial derivatives, advection, and the vorticity Laplacian
were independently evaluated from the primitive streamfunction.

At P1 through P4, the declared and independently derived source expressions
agreed below the predeclared `1e-50` threshold.

Result: PASS.

The largest residual across the complete high-precision point audit was:

`2.1084395886461046449e-81`

---

## 12. O1/M cross-check

At `t = 0`:

`A(0) = 1`

`B(0) = 1/4`

The following identities passed exactly:

`psi_M(x,y,0) = psi_O1(x,y)`

`omega_M(x,y,0) = omega_O1(x,y)`

`adv_M(x,y,0) = adv_O1(x,y)`

This is an internal reference consistency check.

It is not numerical convergence evidence.

---

## 13. Track M Fourier support

The audited absolute Fourier support is:

### Track M vorticity

- `(1,1)`;
- `(2,1)`.

### Track M advection

- `(1,0)`;
- `(1,2)`;
- `(3,0)`;
- `(3,2)`.

### Track M source

- `(1,0)`;
- `(1,1)`;
- `(1,2)`;
- `(2,1)`;
- `(3,0)`;
- `(3,2)`.

No Track M source zero mode was present.

---

## 14. Candidate-mask retention

For `N = 16`, the strict coordinate-wise two-thirds cutoff is:

`16/3`

The maximum required absolute coordinate wave number for O1, Track L, and
Track M is:

`3`

Because:

`3 < 16/3`

the candidate `N = 16` strict two-thirds mask retains all required finite
analytic modes.

Result: PASS.

This establishes mask admissibility only.

It does not establish:

- numerical accuracy at `N = 16`;
- resolution sufficiency;
- an asymptotic range;
- a formal starting resolution;
- convergence.

---

## 15. High-precision point results

The independent numerical-derivative results were:

| Point | Maximum absolute residual |
|---|---:|
| P1 | `1.05421979432e-81` |
| P2 | `2.10843958865e-81` |
| P3 | `2.10843958865e-81` |
| P4 | `2.10843958865e-81` |

All values were finite.

All points passed the `1e-50` threshold.

The O1, O2, and Track M nonlinear advection samples were nonzero.

---

## 16. Track M RK2 source-stage-time audit

The frozen source-stage diagnostic used:

`t_n = 1/5`

`dt = 1/20`

Therefore:

`stage_1_time = 0.20`

`stage_2_time = 0.25`

At:

`x = 2*pi/9`

`y = 5*pi/13`

`nu = 1/100`

the exact source values were:

| Stage | Time | Exact source |
|---|---:|---:|
| 1 | `0.20` | `1.08272847723972244949500460382` |
| 2 | `0.25` | `1.02365714294475329339164187078` |

Difference:

`-0.0590713342949691561033627330334`

Results:

- stage 1 source identity: PASS;
- stage 2 source identity: PASS;
- source evaluated at distinct stage times: PASS;
- source values differ at the selected point: PASS.

Only source expressions were evaluated.

No RK2 state update was performed.

No numerical time step was taken.

A later Track M harness must evaluate:

- stage 1 source at `t_n`;
- stage 2 source at `t_n + dt`.

Evaluating both stages at `t_n` is not the audited method.

---

## 17. Repository-integrity result

Before and after the read-only audit:

- Git HEAD remained
  `2351aeb8cedbd929f5ea5a5eae62de49b3bdc7ae`;
- the working tree remained clean;
- the Phase 13B specification hash remained unchanged;
- all protected solver-source hashes remained unchanged;
- no repository file was created by the mathematics audit;
- no project module was imported;
- no solver method was executed;
- no simulation or numerical time step was run.

Protected hashes remained:

| File | SHA-256 |
|---|---|
| `project/solver/spectral_solver.py` | `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1` |
| `project/solver/selectable_advection_solver.py` | `5EDA93A2E9358D81927BD9EE247F305E6DBC94367B351801913FFEAA2D7C5891` |
| `project/solver/advection_operators.py` | `2C86465570DDF095D5B0A9B7F67E6E78A89D14F82933FA983D91156DD0F76409` |

---

## 18. Phase 13C limitations

Phase 13C establishes continuous-reference and manufactured-source
consistency.

It does not establish:

- numerical operator convergence;
- exact-error decay under grid refinement;
- a finite-difference observed order;
- a pseudo-spectral error-decay model;
- an Arakawa observed order;
- time-integration order;
- a formal asymptotic range;
- numerical uncertainty;
- solver-wide verification;
- physical validation;
- turbulence;
- an inertial range;
- an enstrophy cascade;
- an inverse-energy cascade;
- a `k^-3` law;
- method superiority;
- production readiness.

The high-precision point audit is an independent identity check.

It is not a substitute for a later numerical refinement study.

---

## 19. Phase 13C decision

Phase 13C passes.

The following reference definitions are mathematically consistent with the
audited project equation and sign conventions:

- `O1_BANDLIMITED_TWO_MODE_V1`;
- `O2_ANALYTIC_BROAD_SPECTRUM_V1`;
- `L_EQUAL_EIGENVALUE_DECAY_V1`;
- `M_TWO_RATE_NONLINEAR_MMS_V1`.

The Track M manufactured source passes two independent identity routes.

The O2 sampled-mean compatibility projection is approved under the fixed rule
recorded in this report.

The candidate `N = 16` mask-retention check passes, but no accuracy or
refinement authorization follows from that result.

Phase 13C authorizes these audited definitions for a later external
verification-harness design.

Phase 13C does not authorize a formal benchmark run.

No convergence claim is made.

No turbulence, cascade, or `k^-3` claim is made.

---

## 20. Recommended next phase

The recommended next phase is:

**Phase 13D — External Verification-Harness Design**

Phase 13D should remain design-only and should freeze:

- independent exact-reference functions;
- benchmark identifiers;
- O2 compatibility handling;
- source replacement rather than baseline-source supplementation;
- Track M source-stage timing;
- method-specific operator boundaries;
- post-step mask behavior;
- result metadata;
- output schemas;
- failure gates;
- pilot authorization boundaries.

Phase 13D should not begin a formal refinement run merely because Phase 13C
passed.
