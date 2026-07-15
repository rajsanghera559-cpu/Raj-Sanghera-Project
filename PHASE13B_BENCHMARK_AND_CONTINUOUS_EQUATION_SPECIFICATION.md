# Phase 13B — Benchmark and Continuous-Equation Specification

## 0. Document control

- Project: Raj-Sanghera-Project
- Phase: 13B
- Phase title: Benchmark and Continuous-Equation Specification
- Starting checkpoint:
  `v0.5.45-phase13A-formal-convergence-study-claim-design`
- Starting commit:
  `64c100c480eb5f37f5a13c9a15dfef53c584d030`
- Phase 13A status: complete and archived
- Phase 13B status: specification-only
- Numerical simulations authorized: none
- Time steps authorized: none
- Refinement runs authorized: none
- Solver source changes authorized: none
- Formal convergence claims authorized: none
- Physical-validation claims authorized: none

Phase 13B freezes candidate continuous equations, analytic fields, manufactured
source terms, sign conventions, and later verification-path requirements.

Phase 13B is a specification-only phase.

No convergence claim is made.

---

## 1. Phase boundaries

Phase 13B authorizes:

- recording the audited project equation;
- defining exact analytic benchmark fields;
- deriving exact continuous reference expressions;
- specifying later source-term and residual audits;
- specifying later external verification-harness requirements;
- defining limitations and failure conditions.

Phase 13B does not authorize:

- importing and running the project solver;
- instantiating a solver object;
- executing a solver method;
- running a simulation;
- taking a time step;
- running a grid sequence;
- running a time-step sequence;
- modifying solver source;
- enabling `SelectableAdvectionSolver.run()`;
- implementing a verification runner;
- claiming convergence;
- claiming an observed order;
- claiming an asymptotic range;
- claiming turbulence;
- claiming a cascade;
- claiming a `k^-3` law;
- claiming method superiority;
- claiming production readiness.

`SelectableAdvectionSolver.run()` remains disabled.

---

## 2. Audited source snapshot

The Phase 13B source-and-convention audit passed at the starting checkpoint.

Protected source files:

| File | SHA-256 |
|---|---|
| `project/solver/spectral_solver.py` | `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1` |
| `project/solver/selectable_advection_solver.py` | `5EDA93A2E9358D81927BD9EE247F305E6DBC94367B351801913FFEAA2D7C5891` |
| `project/solver/advection_operators.py` | `2C86465570DDF095D5B0A9B7F67E6E78A89D14F82933FA983D91156DD0F76409` |

Audited local source ranges:

- `SpectralSolver.__init__`: lines 11–37;
- `SpectralSolver.streamfunction`: lines 39–41;
- `SpectralSolver.velocity`: lines 43–48;
- `SpectralSolver.laplacian_spectral`: lines 50–52;
- `SelectableAdvectionSolver.compute_advection`: lines 127–157;
- `SelectableAdvectionSolver.compute_rhs_selectable`: lines 159–199;
- `SelectableAdvectionSolver.step_once_selectable`: lines 201–236;
- `SelectableAdvectionSolver.run`: lines 571–587;
- `jacobian_arakawa_periodic`: lines 155–243;
- `advection_arakawa`: lines 246–270.

The source audit used static parsing.

It did not import a project module, instantiate a solver, execute a solver
method, or run a simulation.

---

## 3. Coordinates, domain, and grid

The audited domain is:

`(x, y) in [0, 2*pi) x [0, 2*pi)`

The grid is square:

`N x N`

with:

`dx = 2*pi / N`

Array-axis convention:

- axis 1 is `x`;
- axis 0 is `y`.

Grid points exclude the repeated periodic endpoint.

The Fourier wave numbers are constructed from the periodic grid using the
project FFT convention.

No alternative domain or coordinate convention is part of Phase 13B.

---

## 4. Frozen continuous equation

The project streamfunction–vorticity convention is:

`Laplacian(psi) = omega`

for nonzero Fourier modes.

Velocity is:

`u = partial_y psi`

`v = -partial_x psi`

Define project advection as:

`adv(psi, omega) = u * partial_x omega + v * partial_y omega`

Therefore:

`adv = partial_y psi * partial_x omega
       - partial_x psi * partial_y omega`

The continuous evolution equation is:

`partial_t omega
 = -adv(psi, omega)
   + nu * Laplacian(omega)
   + s(x, y, t)`

where:

- `nu > 0` is kinematic viscosity;
- `s` is the declared benchmark source.

If the standard Jacobian is defined as:

`J(psi, omega)
 = partial_x psi * partial_y omega
   - partial_y psi * partial_x omega`

then:

`adv = -J`

and the equation may equivalently be written:

`partial_t omega = J + nu * Laplacian(omega) + s`

The numerical operators return `adv`, not `-adv`.

This sign distinction must remain explicit in every later audit.

---

## 5. Baseline forcing is not the manufactured source

The inherited baseline forcing is:

`s_base(x, y) = 0.01 * sin(2*x) * cos(2*y)`

The current selectable RHS computes:

`rhs = -adv + diffusion + s_base`

Therefore:

- `compute_rhs_selectable()` always includes the inherited baseline forcing;
- `step_once_selectable()` calls `compute_rhs_selectable()`;
- `run_selectable_diagnostic()` ultimately uses that selectable RHS;
- none of those paths can represent a zero-source or manufactured-source
  benchmark without a separately audited adapter.

For Tracks O, L, and M:

`compute_rhs_selectable() must not be used unmodified`

The baseline source must not be silently added to Track L or Track M.

No production source method is modified in Phase 13B.

---

## 6. Zero-mode and periodic-Poisson compatibility

A periodic solution of:

`Laplacian(psi) = omega`

requires:

`mean(omega) = 0`

The implementation replaces:

`k2[0, 0]`

with the sentinel value:

`1.0`

That sentinel prevents division by zero but is not a physical zero-mode
wave-number squared.

Consequences:

1. A constant streamfunction component has no effect on velocity.

2. A nonzero vorticity mean is incompatible with the continuous periodic
   Poisson equation.

3. The shared `k2` array is also used by spectral diffusion. A nonzero numerical
   vorticity mean would therefore receive an artificial zero-mode diffusion
   treatment.

All evolution benchmarks must have continuous zero-mean vorticity.

Before any later benchmark run, sampled vorticity must pass a predeclared
discrete-mean check.

No physical conclusion may depend on the zero-mode sentinel.

---

## 7. Dealiasing and filtering convention

The existing mask is a coordinate-wise two-thirds mask using strict
inequalities.

Conceptually:

`abs(kx) < (2/3) * kmax`

and:

`abs(ky) < (2/3) * kmax`

The current selectable pseudo-spectral path uses:

`dealias_product = False`

inside `compute_advection()`.

The current selectable one-step method applies the two-thirds mask to the
completed provisional state after the RK2-style update.

Therefore these are distinct policies:

- nonlinear-product masking: disabled in the current selectable path;
- post-step state masking: enabled in `step_once_selectable()`.

A later study must not describe the selectable pseudo-spectral method as
product-dealiased unless the tested path actually uses that configuration.

A change in this policy defines a different numerical algorithm.

---

## 8. Time-integration convention

The existing selectable step has the form:

`k1 = rhs(w_n)`

`w_predictor = w_n + dt * k1`

`k2 = rhs(w_predictor)`

`w_star = w_n + 0.5 * dt * (k1 + k2)`

followed by the post-step spectral mask.

This is an explicit RK2-style predictor–corrector structure.

For a nonautonomous manufactured source, the mathematically consistent later
external benchmark form is:

`k1 = R(w_n, t_n)`

`w_predictor = w_n + dt * k1`

`k2 = R(w_predictor, t_n + dt)`

`w_star = w_n + 0.5 * dt * (k1 + k2)`

The source must therefore be evaluated at:

- `t_n` for the first stage;
- `t_n + dt` for the second stage.

Evaluating both source stages at `t_n` is not the specified Track M method.

No time integration is executed in Phase 13B.

---

## 9. Benchmark registry

| ID | Track | Purpose | Exact reference | Main limitation |
|---|---|---|---|---|
| `O1_BANDLIMITED_TWO_MODE_V1` | O1 | Sign, consistency, and low-mode operator correctness | Exact advection field | May reach the pseudo-spectral numerical floor too quickly |
| `O2_ANALYTIC_BROAD_SPECTRUM_V1` | O2 | Smooth non-bandlimited operator error-decay study | Exact analytic advection field | Requires a discrete-mean compatibility audit |
| `L_EQUAL_EIGENVALUE_DECAY_V1` | L | Isolated spectral diffusion and RK2-style time behavior | Exact viscous-decay field | Does not verify nonlinear advection |
| `M_TWO_RATE_NONLINEAR_MMS_V1` | M | Nonlinear manufactured full-evolution benchmark | Exact vorticity and exact source | Requires an external source-aware verification step |

Track S is not specified here.

A future self-convergence study remains secondary and cannot replace exact-error
Tracks O or M.

---

## 10. Common benchmark requirements

Every accepted benchmark must be:

- real-valued;
- finite;
- smooth;
- periodic on the audited domain;
- analytically differentiable;
- consistent with `Laplacian(psi) = omega`;
- consistent with the audited velocity signs;
- zero-mean in vorticity;
- evaluated from the same continuous expression on every grid;
- independent of the production discrete derivative used for testing.

Every exact reference must be evaluated directly from its analytic expression.

A production numerical operator must not be used to generate the exact
reference against which that same operator is tested.

No benchmark coefficient may be tuned after formal results are viewed.

---

## 11. Track O1 — band-limited two-mode operator benchmark

Benchmark ID:

`O1_BANDLIMITED_TWO_MODE_V1`

Define:

`psi_O1(x, y)
 = sin(x) * sin(y)
   + (1/4) * cos(2*x) * cos(y)`

Then:

`omega_O1 = Laplacian(psi_O1)`

and explicitly:

`omega_O1(x, y)
 = -2 * sin(x) * sin(y)
   - (5/4) * cos(2*x) * cos(y)`

Velocity is:

`u_O1
 = sin(x) * cos(y)
   - (1/4) * cos(2*x) * sin(y)`

`v_O1
 = -cos(x) * sin(y)
   + (1/2) * sin(2*x) * cos(y)`

Vorticity derivatives are:

`partial_x omega_O1
 = -2 * cos(x) * sin(y)
   + (5/2) * sin(2*x) * cos(y)`

`partial_y omega_O1
 = -2 * sin(x) * cos(y)
   + (5/4) * cos(2*x) * sin(y)`

Define:

`F_O1(x, y)
 = cos(x)
   + 3 * cos(x) * cos(2*y)
   - 3 * cos(3*x)
   - cos(3*x) * cos(2*y)`

The exact project-convention nonlinear advection is:

`adv_O1(x, y) = (3/16) * F_O1(x, y)`

This advection field is not identically zero.

### O1 Fourier support

The streamfunction and vorticity contain modes associated with:

- `(abs(kx), abs(ky)) = (1, 1)`;
- `(abs(kx), abs(ky)) = (2, 1)`.

The exact advection contains modes associated with:

- `(1, 0)`;
- `(1, 2)`;
- `(3, 0)`;
- `(3, 2)`.

The exact vorticity and exact advection have zero spatial mean.

### O1 intended use

For each selectable method separately, a later operator audit may compare:

`computed_adv - adv_O1`

using the Phase 13A error norms.

O1 is intended to test:

- sign consistency;
- axis consistency;
- low-mode derivative correctness;
- Arakawa sign conversion;
- method-specific operator error.

O1 is not a time-evolution benchmark.

O1 does not verify diffusion or time integration.

Because O1 is band-limited, a pseudo-spectral result may reach floating-point
error before enough useful refinement levels exist.

If that occurs, no decay-rate claim may be made from O1.

---

## 12. Track O2 — analytic broad-spectrum operator benchmark

Benchmark ID:

`O2_ANALYTIC_BROAD_SPECTRUM_V1`

Fix:

`a = 1/2`

`b = 1/3`

Define:

`q(x, y) = a * cos(x) + b * cos(y)`

Define the gauge constant:

`C_ab = domain_mean(exp(q))`

and:

`psi_O2(x, y) = exp(q(x, y)) - C_ab`

The constant does not affect velocity or vorticity.

Define:

`H(x, y)
 = a^2 * sin(x)^2
   - a * cos(x)
   + b^2 * sin(y)^2
   - b * cos(y)`

Then:

`omega_O2(x, y) = exp(q(x, y)) * H(x, y)`

Velocity is:

`u_O2(x, y)
 = -b * sin(y) * exp(q(x, y))`

`v_O2(x, y)
 = a * sin(x) * exp(q(x, y))`

The exact nonlinear advection is:

`adv_O2(x, y)
 = -2 * a * b
   * (a * cos(x) - b * cos(y))
   * exp(2*q(x, y))
   * sin(x)
   * sin(y)`

This advection is not identically zero.

### O2 properties

O2 is:

- smooth;
- periodic;
- analytic;
- real-valued;
- non-band-limited;
- zero-mean in continuous vorticity because it is a periodic Laplacian.

O2 is intended to provide a meaningful smooth broad-spectrum reference for the
pseudo-spectral operator.

Defining an analytic benchmark does not establish spectral or exponential
convergence.

Any later error-decay description must satisfy the Phase 13A pre-floor,
model-selection, and fit-quality rules.

### O2 discrete-mean issue

Because O2 is non-band-limited, unresolved analytic Fourier coefficients can
alias into a sampled discrete zero mode.

Before formal use, Phase 13C must audit a compatibility procedure.

The provisional candidate is:

`omega_O2_compatible
 = sampled_omega_O2
   - discrete_mean(sampled_omega_O2)`

The removed mean must be recorded at every resolution.

A constant vorticity offset has zero gradient and contributes only a constant
streamfunction through the current sentinel, so it does not change the
advection field under the audited velocity construction.

This compatibility procedure remains provisional until Phase 13C passes it.

O2 is not authorized for formal runs by Phase 13B.

---

## 13. Track L — equal-eigenvalue viscous-decay benchmark

Benchmark ID:

`L_EQUAL_EIGENVALUE_DECAY_V1`

Define:

`Phi_L(x, y) = sin(3*x) + cos(3*y)`

For any fixed `nu > 0`, define:

`omega_L(x, y, t)
 = exp(-9*nu*t) * Phi_L(x, y)`

Because:

`Laplacian(Phi_L) = -9 * Phi_L`

the streamfunction is:

`psi_L(x, y, t) = -(1/9) * omega_L(x, y, t)`

Velocity is:

`u_L
 = (1/3) * exp(-9*nu*t) * sin(3*y)`

`v_L
 = (1/3) * exp(-9*nu*t) * cos(3*x)`

Vorticity derivatives are:

`partial_x omega_L
 = 3 * exp(-9*nu*t) * cos(3*x)`

`partial_y omega_L
 = -3 * exp(-9*nu*t) * sin(3*y)`

Therefore:

`adv_L = u_L * partial_x omega_L
         + v_L * partial_y omega_L
       = 0`

Also:

`Laplacian(omega_L) = -9 * omega_L`

and:

`partial_t omega_L = -9 * nu * omega_L`

The source is:

`s_L = 0`

Thus:

`partial_t omega_L
 = nu * Laplacian(omega_L)`

exactly.

### L intended use

The primary Track L verification RHS is linear:

`R_L(omega) = nu * Laplacian(omega)`

The primary Track L time-evolution path must bypass nonlinear advection.

It must also bypass the inherited baseline forcing.

A later secondary diagnostic may evaluate each advection operator on the exact
Track L field to determine whether it returns numerical zero.

That secondary diagnostic is not nonlinear-advection verification.

Track L may support evidence concerning:

- spectral diffusion;
- final-time alignment;
- the external RK2-style verification step;
- field-error norm infrastructure;
- post-step retention of represented exact modes.

Track L must not support a nonlinear-advection claim.

---

## 14. Track M — nonlinear manufactured solution

Benchmark ID:

`M_TWO_RATE_NONLINEAR_MMS_V1`

Define spatial basis functions:

`f(x, y) = sin(x) * sin(y)`

`g(x, y) = cos(2*x) * cos(y)`

Define time amplitudes:

`A(t) = exp(-t)`

`B(t) = (1/4) * exp(-2*t)`

Define the exact streamfunction:

`psi_M(x, y, t)
 = A(t) * f(x, y)
   + B(t) * g(x, y)`

The exact vorticity is:

`omega_M
 = Laplacian(psi_M)
 = -2 * A(t) * f(x, y)
   - 5 * B(t) * g(x, y)`

Velocity is:

`u_M
 = A(t) * sin(x) * cos(y)
   - B(t) * cos(2*x) * sin(y)`

`v_M
 = -A(t) * cos(x) * sin(y)
   + 2 * B(t) * sin(2*x) * cos(y)`

Vorticity derivatives are:

`partial_x omega_M
 = -2 * A(t) * cos(x) * sin(y)
   + 10 * B(t) * sin(2*x) * cos(y)`

`partial_y omega_M
 = -2 * A(t) * sin(x) * cos(y)
   + 5 * B(t) * cos(2*x) * sin(y)`

Using the O1 function:

`F_O1(x, y)
 = cos(x)
   + 3 * cos(x) * cos(2*y)
   - 3 * cos(3*x)
   - cos(3*x) * cos(2*y)`

the exact nonlinear advection is:

`adv_M
 = (3/4) * A(t) * B(t) * F_O1(x, y)`

Equivalently:

`adv_M
 = (3/16) * exp(-3*t) * F_O1(x, y)`

This nonlinear advection is not identically zero.

The exact time derivative is:

`partial_t omega_M
 = 2 * A(t) * f(x, y)
   + 10 * B(t) * g(x, y)`

The exact vorticity Laplacian is:

`Laplacian(omega_M)
 = 4 * A(t) * f(x, y)
   + 25 * B(t) * g(x, y)`

The manufactured source is defined by:

`s_M
 = partial_t omega_M
   + adv_M
   - nu * Laplacian(omega_M)`

Therefore:

`s_M(x, y, t; nu)
 = (2 - 4*nu) * A(t) * f(x, y)
   + (10 - 25*nu) * B(t) * g(x, y)
   + (3/4) * A(t) * B(t) * F_O1(x, y)`

This source gives the exact continuous residual identity:

`partial_t omega_M
 - (
     -adv_M
     + nu * Laplacian(omega_M)
     + s_M
   )
 = 0`

### M/O1 cross-check

At:

`t = 0`

the amplitudes are:

`A(0) = 1`

`B(0) = 1/4`

Therefore:

`psi_M(x, y, 0) = psi_O1(x, y)`

`omega_M(x, y, 0) = omega_O1(x, y)`

`adv_M(x, y, 0) = adv_O1(x, y)`

This cross-track identity is an internal reference check.

It is not convergence evidence.

---

## 15. Track M external verification RHS

The later method-specific Track M numerical RHS must have the form:

`R_M_method(omega, t)
 = -adv_method(omega)
   + diffusion_spectral(omega)
   + s_M(x, y, t; nu)`

where `adv_method` is exactly one of:

- `fd_centered`;
- `pseudo_spectral`;
- `arakawa`.

Each method must have a separate result sequence.

The exact manufactured source must be evaluated directly from the analytic
formula.

It must not be generated using:

- centered finite differences;
- pseudo-spectral derivatives from the solver;
- the Arakawa Jacobian;
- a production solver residual.

The source must replace the inherited baseline forcing.

It must not be added on top of the inherited baseline forcing.

The later external benchmark step must evaluate `s_M` at the correct RK2 stage
times.

No external verification RHS is implemented in Phase 13B.

---

## 16. Method-specific boundaries

### `fd_centered`

The numerical velocity remains spectral through the inherited streamfunction
and velocity methods.

Only the vorticity gradient in the advection term is centered finite
difference.

Any later observed behavior applies to this mixed numerical algorithm.

### `pseudo_spectral`

The numerical velocity and vorticity gradient are spectral.

The current selectable path does not mask the nonlinear product inside
`compute_advection()`.

The current post-step state mask remains a separate operation.

No claim of product dealiasing is permitted for this configuration.

### `arakawa`

The standalone Jacobian function returns:

`J(psi, omega)
 = partial_x psi * partial_y omega
   - partial_y psi * partial_x omega`

The selectable Arakawa advection returns:

`-J`

so that it matches:

`adv = u * partial_x omega + v * partial_y omega`

A later audit must preserve this sign.

No nominal-order or conservation claim is made merely from the method name.

---

## 17. Mode support and candidate minimum grid

O1 exact advection and the Track M manufactured source contain modes no larger
than:

`abs(kx) = 3`

`abs(ky) = 2`

Track L contains modes no larger than:

`abs(kx) = 3`

`abs(ky) = 3`

A candidate preliminary minimum is:

`N >= 16`

because, under the current strict coordinate-wise two-thirds mask, these modes
remain below the cutoff.

This is a benchmark-admissibility candidate.

It is not:

- a formal refinement level;
- evidence that `N=16` is accurate;
- evidence that `N=16` is sufficient;
- authorization for a formal run.

O2 is non-band-limited, so no finite grid represents all O2 modes.

---

## 18. Exact-reference evaluation

For O1, O2, L, and M:

1. Evaluate the exact analytic field directly at native grid points.

2. Do not interpolate an exact field from another grid.

3. Do not initialize a fine grid from a coarse numerical result.

4. Use the same continuous coefficients at every resolution.

5. Evaluate exact final-time fields at the identical physical time used by the
   numerical result.

6. Record any compatibility projection separately.

7. Keep exact-reference code independent of production numerical derivative
   code.

The initial primary arithmetic target is ordinary double precision.

Phase 13C must also use an independent higher-precision or symbolic check for
the continuous identities.

---

## 19. Primary error quantities

For Tracks O1 and O2, the primary error field is:

`e_adv = computed_adv - exact_adv`

Primary operator norms are:

- mean-normalized absolute `L1`;
- mean-normalized absolute `L2`;
- absolute `L-infinity`.

Relative `L2` is secondary and may be used only when the exact-advection norm is
safely nonzero.

For Tracks L and M, the primary error field is:

`e_omega = numerical_omega - exact_omega`

Primary evolution norms are:

- mean-normalized absolute `L1`;
- mean-normalized absolute `L2`;
- absolute `L-infinity`.

Vorticity is the primary field.

Energy, enstrophy, RMS vorticity, velocity, and Fourier coefficients remain
secondary diagnostics.

Spectral slopes are not primary convergence evidence.

No `k^-3` fitting is part of these benchmark definitions.

---

## 20. Viscosity and parameter policy

The benchmark formulas are valid for:

`nu > 0`

The solver input relation is:

`Re = 1 / nu`

A later pilot and pre-registration must freeze one viscosity for each formal
study.

Within one refinement sequence, viscosity must not change.

The following are already fixed and must not be tuned:

- O2 parameter `a = 1/2`;
- O2 parameter `b = 1/3`;
- Track L wave number `3`;
- Track M decay rate in `A(t)`;
- Track M decay rate in `B(t)`;
- Track M amplitude ratio `B(0) = 1/4`.

Phase 13B does not select:

- the formal viscosity;
- the formal final time;
- the formal spatial levels;
- the formal time-step levels;
- error-floor thresholds;
- contamination thresholds.

Those decisions require later audits and pilots.

---

## 21. Required Phase 13C continuous checks

Before any benchmark implementation or run, Phase 13C must independently check:

### All tracks

- periodicity;
- finiteness;
- real-valuedness;
- continuous zero-mean vorticity;
- streamfunction–vorticity consistency;
- velocity signs;
- axis convention;
- analytic derivative identities.

### O1

- exact advection formula;
- nonzero nonlinear term;
- Fourier support;
- zero mean;
- O1/M cross-check at `t=0`.

### O2

- exact vorticity formula;
- exact advection formula;
- nonzero nonlinear term;
- continuous zero mean;
- gauge independence;
- sampled discrete-mean behavior;
- proposed compatibility projection;
- independence from production derivatives.

### Track L

- zero nonlinear advection;
- eigenvalue `-9`;
- exact viscous decay;
- zero source;
- exact-mode retention under the candidate mask;
- optional numerical zero-advection diagnostic design.

### Track M

- exact time derivative;
- exact Laplacian;
- exact nonlinear advection;
- manufactured source sign;
- continuous residual;
- nonzero nonlinear term;
- source Fourier support;
- source evaluation at both RK2 stage times.

Phase 13C must use at least two independent approaches for the Track M source
identity.

The pointwise checks performed during Phase 13B document creation are document
integrity checks only.

They are not the formal Phase 13C audit.

---

## 22. Later external verification-harness requirements

A later verification harness must:

- be separate from production solver source;
- record its own revision and hash;
- use an explicit benchmark identifier;
- use one selectable advection method at a time;
- avoid mutating the input field;
- avoid mutating `solver.w`;
- avoid calling `SelectableAdvectionSolver.run()`;
- avoid enabling a production run loop;
- replace rather than supplement baseline forcing for Tracks L and M;
- evaluate the Track M source at stage times;
- apply the declared post-step mask exactly once;
- record whether product dealiasing is enabled or disabled;
- record exact final physical time;
- return numerical and exact fields for native-grid error calculation;
- produce no turbulence, cascade, or `k^-3` claim.

Track O may later call the audited `compute_advection()` interface.

Track L requires a linear external RHS.

Track M requires a source-aware external RHS.

`step_once_selectable()` cannot be used unmodified for Tracks L or M because it
calls the baseline selectable RHS.

---

## 23. Predeclared failure conditions

A benchmark is not authorized for formal use if any of the following occurs:

- the continuous residual does not pass;
- the source sign is ambiguous;
- the velocity convention is inconsistent;
- vorticity is not zero mean under the declared compatibility rule;
- the exact reference uses the production operator under test;
- the nonlinear term is zero in O1, O2, or M;
- Track L includes inherited baseline forcing;
- Track M includes inherited baseline forcing;
- Track M evaluates both RK2 source stages at the same time;
- an exact analytic mode required by O1, L, or M is removed by the declared
  mask;
- O2 compatibility handling changes after formal results are viewed;
- one method's output is substituted into another method's refinement sequence;
- the exact solution is interpolated from a different grid;
- a solver source file changes without a separately authorized phase;
- `SelectableAdvectionSolver.run()` is enabled or called.

A failed benchmark gate produces no convergence claim.

---

## 24. Claim boundaries

Phase 13B defines mathematical benchmark candidates.

It does not establish:

- operator convergence;
- exact-error decay;
- observed algebraic order;
- pseudo-spectral error-decay rate;
- an asymptotic range;
- a numerical uncertainty estimate;
- solver-wide verification;
- physical validation;
- turbulence;
- an inertial range;
- an enstrophy cascade;
- an inverse-energy cascade;
- a `k^-3` law;
- method superiority;
- production readiness.

A correct analytic identity is necessary for later verification.

It is not itself numerical convergence evidence.

---

## 25. Phase 13B completion criteria

Phase 13B passes when:

- this specification document exists;
- the Phase 13A checkpoint remains the parent checkpoint;
- the starting source hashes are preserved;
- the working tree contains only this new untracked document;
- the audited continuous equation is recorded;
- the zero-mode constraint is recorded;
- baseline forcing is distinguished from manufactured sources;
- O1 is specified;
- O2 is specified;
- Track L is specified;
- Track M is specified;
- the Track M source is explicitly recorded;
- Track M source-stage timing is recorded;
- later external-harness boundaries are recorded;
- `SelectableAdvectionSolver.run()` remains disabled;
- no simulation was run;
- no solver method was executed;
- no convergence, turbulence, cascade, or `k^-3` claim was made.

---

## 26. Recommended next phase

After Phase 13B passes its content audit and archive gate, the next phase is:

**Phase 13C — Reference-Solution and Source-Term Audit**

Expected Phase 13C work:

- independent symbolic checks;
- independent high-precision point checks;
- zero-mean checks;
- Fourier-support checks;
- O2 compatibility-projection decision;
- Track M continuous residual verification;
- Track M stage-time source verification;
- an audit report.

Phase 13C should still avoid a formal refinement run.

---

## 27. Phase 13B decision

Phase 13B authorizes the benchmark and continuous-equation specifications in
this document for independent Phase 13C auditing.

It does not authorize implementation or numerical execution.

`SelectableAdvectionSolver.run()` remains disabled.

No convergence claim is made.

No turbulence, cascade, or `k^-3` claim is made.
