# Phase 13D — External Verification-Harness Design

## 0. Document control

- Project: Raj-Sanghera-Project
- Phase: 13D
- Phase title: External Verification-Harness Design
- Starting checkpoint:
  `v0.5.47-phase13C-reference-solution-and-source-term-audit`
- Starting commit:
  `bc9dcd29ed0fe7609cec56aa7553c3c577dd5316`
- Parent mathematical specification:
  `PHASE13B_BENCHMARK_AND_CONTINUOUS_EQUATION_SPECIFICATION.md`
- Parent mathematical audit:
  `PHASE13C_REFERENCE_SOLUTION_AND_SOURCE_TERM_AUDIT_REPORT.md`
- Phase status: design-only
- Verification-harness implementation authorized: none
- Production solver changes authorized: none
- Solver imports authorized: none
- Solver object instantiations authorized: none
- Solver methods authorized: none
- Simulations authorized: none
- Numerical time steps authorized: none
- Pilot runs authorized: none
- Formal refinement sequences authorized: none
- Convergence claims authorized: none
- Physical-validation claims authorized: none

Phase 13D freezes the architecture, interfaces, data contracts, state guards,
source policy, mask policy, output schemas, failure gates, and future pilot
boundaries for an external verification harness.

Phase 13D does not implement or execute that harness.

No convergence claim is made.

---

## 1. Phase boundary

Phase 13D authorizes:

- documenting the external harness architecture;
- freezing future file boundaries;
- freezing benchmark identifiers;
- freezing exact-reference interfaces;
- freezing operator and evolution pathways;
- freezing O2 compatibility handling;
- freezing Track L and Track M RHS definitions;
- freezing Track M RK2 source-stage timing;
- freezing post-step masking behavior;
- freezing input and solver-state mutation guards;
- freezing error definitions;
- freezing metadata and output schemas;
- freezing failure conditions;
- freezing the maximum scope of a later pilot.

Phase 13D does not authorize:

- creating Python harness modules;
- modifying production or diagnostic solver source;
- importing `project`;
- instantiating `SpectralSolver`;
- instantiating `SelectableAdvectionSolver`;
- calling `compute_advection()`;
- calling `compute_rhs_selectable()`;
- calling `step_once_selectable()`;
- calling `run_selectable_diagnostic()`;
- calling `SelectableAdvectionSolver.run()`;
- evaluating a numerical operator;
- executing an external RHS;
- executing an RK2 stage;
- taking a time step;
- creating numerical result directories;
- running a pilot;
- running a refinement sequence;
- calculating observed order;
- fitting an error-decay model;
- making a convergence claim.

---

## 2. Inherited checkpoint

Phase 13C established that the following exact-reference definitions are
mathematically consistent with the audited continuous equation and project sign
conventions:

- `O1_BANDLIMITED_TWO_MODE_V1`;
- `O2_ANALYTIC_BROAD_SPECTRUM_V1`;
- `L_EQUAL_EIGENVALUE_DECAY_V1`;
- `M_TWO_RATE_NONLINEAR_MMS_V1`.

Phase 13C also established:

- the Track M manufactured source by two independent routes;
- the Track M continuous residual;
- the O1/M identity at `t = 0`;
- O1, Track L, and Track M Fourier support;
- continuous zero-mean conditions;
- the O2 compatibility-projection rule;
- Track M source evaluation at two distinct RK2 stage times;
- candidate-mask retention at `N = 16`.

These results establish reference consistency.

They do not establish numerical convergence or accuracy at any resolution.

---

## 3. Frozen source facts

The future harness must preserve the following audited source facts.

### Grid and viscosity

`SpectralSolver.__init__` sets:

`nu = 1 / Re`

The grid is square and periodic with:

`L = 2*pi`

`dx = L / N`

The constructor creates its declared `run_path`.

A later harness must therefore use a controlled case-specific scaffold path and
must record that path.

### Spectral diffusion

`SpectralSolver.laplacian_spectral(w)` already returns:

`nu * Laplacian(w)`

The future harness must not multiply its result by `nu` a second time.

### Selectable advection

`SelectableAdvectionSolver.compute_advection(w)` returns:

`adv = u * partial_x(omega) + v * partial_y(omega)`

The evolution equation uses:

`partial_t omega = -adv + diffusion + source`

The selectable methods are:

- `fd_centered`;
- `pseudo_spectral`;
- `arakawa`.

### Pseudo-spectral product policy

The current selectable pseudo-spectral path calls its operator with:

`dealias_product = False`

Therefore the current selectable pseudo-spectral method is not a
product-dealiased configuration.

Changing that policy defines a different numerical algorithm and requires a
different identifier and separately authorized phase.

### Baseline forcing

`compute_rhs_selectable(w)` adds inherited baseline forcing.

Therefore it is prohibited for Track L and Track M.

The manufactured source must replace, not supplement, inherited forcing.

### Existing selectable step

`step_once_selectable(w)` calls `compute_rhs_selectable(w)` and therefore
inherits baseline forcing.

It is prohibited for Track L and Track M.

### Existing run methods

`SelectableAdvectionSolver.run()` remains disabled.

`run_selectable_diagnostic()` is not the Phase 13 external harness and is also
prohibited for the verification tracks defined here.

---

## 4. Design principles

The external harness must be:

- separate from production solver source;
- explicit about every permitted solver interface;
- independent in exact-reference construction;
- deterministic;
- non-mutating with respect to input arrays;
- non-mutating with respect to `solver.w`;
- explicit about source replacement;
- explicit about stage times;
- explicit about product dealiasing;
- explicit about post-step masking;
- explicit about final physical time;
- explicit about benchmark and method identity;
- auditable by hashes and metadata;
- fail-closed rather than fail-open.

The harness must not silently correct an invalid configuration.

The harness must stop before numerical execution when a precondition fails.

---

## 5. Proposed architecture

The later implementation is divided into four logical layers.

### Layer 1 — exact references

This layer evaluates analytic expressions directly.

It must not import any project solver module.

### Layer 2 — guarded solver adapter

This layer constructs and holds one selectable solver instance while exposing
only the interfaces authorized for a particular track.

### Layer 3 — external verification operations

This layer performs:

- one operator evaluation for Track O;
- an external linear RHS for Track L;
- an external source-aware RHS for Track M;
- an external RK2-style step when later authorized.

### Layer 4 — result and provenance writer

This layer records:

- configuration;
- environment;
- hashes;
- checks;
- arrays;
- error norms;
- exact final time;
- pass or fail status.

The result writer must not change numerical fields.

---

## 6. Proposed future files

Phase 13D freezes the following proposed implementation boundaries.

### Exact-reference module

`project/verification/phase13_exact_references.py`

Responsibilities:

- native-grid construction;
- benchmark registry;
- exact O1 fields;
- exact O2 fields;
- O2 compatibility projection;
- exact Track L fields;
- exact Track M fields;
- exact Track M source;
- reference-field validation.

This module may import:

- Python standard-library modules;
- NumPy.

This module must not import:

- `project.solver`;
- `SpectralSolver`;
- `SelectableAdvectionSolver`;
- `advection_operators`.

### External-harness module

`project/verification/phase13_external_harness.py`

Responsibilities:

- guarded solver construction;
- method validation;
- solver-grid agreement checks;
- operator-track execution;
- external Track L RHS;
- external Track M RHS;
- external RK2-style step;
- post-step masking;
- mutation checks;
- final-time alignment;
- error calculation;
- in-memory result assembly.

### Output-schema module

`project/verification/phase13_output_schema.py`

Responsibilities:

- metadata-schema validation;
- deterministic case identifiers;
- JSON-safe conversion;
- array manifest construction;
- file-hash recording;
- atomic result writing.

### Future controlled runner

`run_phase13F_verification_pilot.py`

This runner is only a proposed future executable boundary.

It is not created or authorized in Phase 13D.

### No production-source changes

The following files remain protected:

- `project/solver/spectral_solver.py`;
- `project/solver/selectable_advection_solver.py`;
- `project/solver/advection_operators.py`.

---

## 7. Benchmark registry

The exact-reference module must expose only the following benchmark identifiers
in version 1.

| Identifier | Track | Numerical operation |
|---|---|---|
| `O1_BANDLIMITED_TWO_MODE_V1` | O1 | One advection-operator evaluation |
| `O2_ANALYTIC_BROAD_SPECTRUM_V1` | O2 | One advection-operator evaluation |
| `L_EQUAL_EIGENVALUE_DECAY_V1` | L | External linear diffusion evolution |
| `M_TWO_RATE_NONLINEAR_MMS_V1` | M | External nonlinear manufactured evolution |

Unknown identifiers must raise an error.

Aliases are prohibited.

Identifier matching is exact and case-sensitive.

A benchmark definition must include:

- `benchmark_id`;
- `track`;
- `reference_version`;
- `supports_operator_evaluation`;
- `supports_time_evolution`;
- `requires_advection_method`;
- `source_policy`;
- `compatibility_policy`;
- `post_step_mask_policy`.

---

## 8. Native grid and parameter contract

The exact-reference layer must construct the native grid independently from:

`N`

using:

`x_i = 2*pi*i/N`

for:

`i = 0, 1, ..., N-1`

and:

`X, Y = meshgrid(x, x)`

The repeated periodic endpoint must be excluded.

The independently constructed grid must be compared with:

- `solver.x`;
- `solver.X`;
- `solver.Y`;
- `solver.dx`;
- `solver.L`.

A mismatch is a hard failure.

Required configuration quantities are:

- `N`;
- `Re`;
- `nu`;
- `dt` when evolution is requested;
- integer `n_steps` when evolution is requested;
- benchmark identifier;
- advection method when required.

The required viscosity relation is:

`nu = 1 / Re`

A configuration supplying inconsistent `nu` and `Re` must fail before
execution.

`N` must be an even integer.

The first future pilot may use only `N = 16`.

No formal spatial sequence is frozen in Phase 13D.

---

## 9. Exact-reference API

The proposed exact-reference interface is:

`evaluate_reference(
    benchmark_id,
    X,
    Y,
    t,
    nu
) -> ReferenceFields`

The exact-reference implementation must use direct analytic formulas.

It must not generate exact fields using:

- finite differences;
- FFT differentiation;
- the project streamfunction method;
- the project velocity method;
- the project Laplacian method;
- any selectable advection operator;
- a production residual.

For each grid and time, the reference evaluator must create new arrays.

It must not interpolate from another grid.

It must not reuse a numerical result as an exact field.

---

## 10. Reference-field data contract

The proposed `ReferenceFields` result contains:

- `benchmark_id`;
- `track`;
- `reference_version`;
- `time`;
- `nu`;
- `psi`;
- `omega_raw`;
- `omega_input`;
- `u`;
- `v`;
- `adv`;
- `laplacian_omega`;
- `partial_t_omega`;
- `source`;
- `discrete_mean_removed`;
- `compatibility_policy`;
- `fourier_support`;
- `checks`.

Fields not applicable to a track must be explicitly `None`.

An absent field must not be represented by an all-zero placeholder unless the
exact analytic field is mathematically zero.

For Track L:

`adv = 0`

and:

`source = 0`

must be represented explicitly.

For O1 and O2, evolution-only fields may be `None`.

Reference arrays must be:

- real-valued;
- finite;
- shape `(N, N)`;
- independent copies;
- marked read-only after creation.

---

## 11. Guarded solver construction

A future harness may construct:

`SelectableAdvectionSolver(
    nx=N,
    ny=N,
    Re=Re,
    run_path=case_scaffold_path,
    dt=dt,
    steps=0,
    advection_method=method
)`

The constructor value:

`steps = 0`

is frozen for the external harness.

The external harness maintains its own `n_steps`.

This reduces the risk of accidental inherited-loop execution.

Because the constructor creates `run_path`, the harness must use:

`<case_directory>/_solver_scaffold`

and record the path.

The harness must verify immediately after construction:

- `solver.N == N`;
- `solver.nu == 1/Re`;
- `solver.dt == dt`;
- `solver.steps == 0`;
- `solver.advection_method == requested_method`;
- `solver.w` is finite and initially zero;
- the mask matches the independently reconstructed expected mask.

No inherited production run loop is permitted.

---

## 12. Allowed and prohibited solver interfaces

### Track O allowed interface

Track O may use:

`solver.compute_advection(w_input)`

It may also read immutable grid and configuration attributes needed for
validation.

### Track L allowed interface

Track L may use:

`solver.laplacian_spectral(w)`

Track L must not use nonlinear advection.

### Track M allowed interfaces

Track M may use:

- `solver.compute_advection(w)`;
- `solver.laplacian_spectral(w)`.

### Universally prohibited interfaces

The harness must not call:

- `solver.forcing()`;
- `solver.compute_rhs_selectable()`;
- `solver.step_once_selectable()`;
- `solver.run_selectable_diagnostic()`;
- `solver.run()`;
- `SpectralSolver.run()`.

The harness must not call a production metadata writer.

The implementation audit must statically search the future harness source for
these prohibited calls.

---

## 13. Immutability and state guards

Before every allowed numerical call, the harness must record independent copies
of:

- the input array;
- `solver.w`.

After the call, it must require exact array equality with the recorded copies.

Required checks are:

`array_equal(input_before, input_after)`

and:

`array_equal(solver_w_before, solver.w)`

A mutation is a hard failure.

The returned array must not share writable memory with the input array.

The returned array must be:

- real-valued;
- finite;
- shape `(N, N)`.

The harness must not assign the benchmark field to `solver.w`.

All evolution state must remain local to the external harness.

---

## 14. Track O1 operator path

For each selected method separately:

1. Construct the independent native grid.
2. Evaluate the exact O1 reference.
3. Set:
   `w_input = exact_omega_O1`.
4. Preserve immutable pre-call copies.
5. Call:
   `computed_adv = solver.compute_advection(w_input_copy)`.
6. Verify input and solver-state immutability.
7. Compute:
   `error_adv = computed_adv - exact_adv_O1`.
8. Calculate the declared operator error norms.
9. Record method-specific metadata and fields.

No time step is taken.

No state mask is applied.

No inherited forcing is evaluated.

A separate case must be produced for each method.

One method's result must not be reused for another method.

---

## 15. Track O2 operator path

For each selected method separately:

1. Construct the independent native grid.
2. Evaluate analytic O2 fields.
3. Compute the raw sampled vorticity mean.
4. Apply the frozen compatibility projection.
5. Use the compatible vorticity as numerical input.
6. Evaluate exact advection directly from the analytic O2 expression.
7. Call:
   `computed_adv = solver.compute_advection(w_input_copy)`.
8. Verify input and solver-state immutability.
9. Compute:
   `error_adv = computed_adv - exact_adv_O2`.
10. Record the removed mean and compatible mean.

No time step is taken.

No state mask is applied.

No inherited forcing is evaluated.

No numerical derivative may generate the exact O2 advection field.

---

## 16. O2 compatibility policy

The frozen O2 policy is:

`omega_raw = analytic_omega_O2(X, Y)`

`m_N = mean(omega_raw)`

`omega_input = omega_raw - m_N`

The harness must record:

- `m_N`;
- the mean of `omega_input`;
- the projection policy identifier;
- the dtype;
- the grid size.

The policy identifier is:

`O2_DISCRETE_MEAN_SUBTRACTION_V1`

The exact advection remains the direct analytic expression.

The projection must not be applied to exact advection.

The projection rule must not change between methods.

The projection rule must not change after results are viewed.

O2 remains an operator-only benchmark under this policy.

---

## 17. Track L external RHS

The Track L external RHS is:

`R_L(w) = solver.laplacian_spectral(w)`

Because `laplacian_spectral()` already includes viscosity, the harness must not
multiply its result by `nu`.

Track L must not call an advection method.

Track L must not call inherited forcing.

Track L must not call `compute_rhs_selectable()`.

The Track L evolution-method identifier is:

`linear_spectral_diffusion_external_rk2_v1`

Track L is executed once per numerical configuration, not once per selectable
advection method.

A secondary zero-advection operator diagnostic is a separate future case and
must not be represented as Track L nonlinear verification.

---

## 18. Track M external RHS

For exactly one selected advection method, the Track M external RHS is:

`R_M(w, t)
 = -solver.compute_advection(w)
   + solver.laplacian_spectral(w)
   + exact_source_M(X, Y, t, nu)`

The source must be evaluated directly from the analytic formula.

The source must replace inherited baseline forcing.

The source must not be added to inherited baseline forcing.

The harness must not call `solver.forcing()`.

The harness must not call `compute_rhs_selectable()`.

The harness must not call `step_once_selectable()`.

The source-policy identifier is:

`M_ANALYTIC_SOURCE_REPLACES_BASELINE_V1`

A separate Track M case is required for each selectable method.

---

## 19. External RK2-style step

The future external step interface is:

`external_rk2_step(
    rhs,
    w_n,
    t_n,
    dt,
    post_step_mask
) -> StepResult`

The frozen stage sequence is:

`k1 = rhs(w_n, t_n)`

`w_predictor = w_n + dt*k1`

`k2 = rhs(w_predictor, t_n + dt)`

`w_star = w_n + 0.5*dt*(k1 + k2)`

`w_next = apply_post_step_mask_once(w_star)`

For Track L, the RHS is autonomous, but the same stage structure is retained.

For Track M:

- stage 1 source time is `t_n`;
- stage 2 source time is `t_n + dt`.

Evaluating both source stages at `t_n` is prohibited.

The step result must record:

- `t_n`;
- `t_stage_1`;
- `t_stage_2`;
- `t_next`;
- stage source hashes for Track M;
- input-mutation status;
- solver-state-mutation status;
- post-step mask count.

The function must not mutate `w_n`.

---

## 20. Post-step mask policy

The post-step mask is applied exactly once after the completed RK2 provisional
state.

The policy identifier is:

`POST_STEP_STRICT_COORDINATE_TWO_THIRDS_ONCE_V1`

The external implementation is conceptually:

`W_star = fft2(w_star)`

`W_star = W_star * verified_mask`

`w_next = real(ifft2(W_star))`

The harness must independently reconstruct the expected mask from the audited
grid and compare it with `solver.deal`.

A mask mismatch is a hard failure.

The harness must record:

- mask-policy identifier;
- mask shape;
- retained-mode count;
- removed-mode count;
- number of mask applications;
- norm before masking;
- norm after masking.

For Track O, the post-step mask application count is zero.

For Track L and Track M, the mask application count per completed step is
exactly one.

Applying the mask to each RK2 stage is not the frozen algorithm.

---

## 21. Method-specific boundaries

### `fd_centered`

The method uses:

- spectral streamfunction;
- spectral velocity;
- centered finite-difference vorticity gradients.

It is a mixed numerical method.

Any future result applies only to this mixed method.

### `pseudo_spectral`

The method uses:

- spectral streamfunction;
- spectral velocity;
- spectral vorticity gradients;
- an unmasked physical nonlinear product.

The frozen product-dealiasing field is:

`false`

No product-dealiasing claim is permitted.

### `arakawa`

The method uses the project-convention return value:

`adv = -J_arakawa`

The harness must not reverse the sign again.

The method name does not itself establish a conservation property or nominal
order.

### Separation rule

Each case contains exactly one advection-method identifier.

Outputs from different methods must remain in different case directories.

No method averaging or substitution is permitted.

---

## 22. Time and final-time alignment

An evolution configuration must provide:

- integer `n_steps`;
- positive `dt`;
- initial time `t_0`.

The actual final time is:

`t_final = t_0 + n_steps*dt`

The exact final reference must be evaluated at that same actual time.

The harness must not:

- overshoot a requested final time;
- silently shorten the last step;
- interpolate an exact field from another time;
- report a requested time as though it were the actual time.

The metadata must record:

- `t_0`;
- `dt`;
- `n_steps`;
- `t_final_actual`;
- `t_final_requested`, if one was supplied;
- final-time alignment status.

A requested final time inconsistent with integer steps must fail before
execution.

---

## 23. Error norms

For operator tracks:

`e_adv = computed_adv - exact_adv`

For evolution tracks:

`e_omega = numerical_omega - exact_omega`

Primary absolute norms are:

`L1_mean = mean(abs(e))`

`L2_rms = sqrt(mean(e^2))`

`Linf = max(abs(e))`

The harness must also record:

- exact-field `L2_rms`;
- numerical-field `L2_rms`;
- error finiteness;
- maximum absolute imaginary residue before taking a real view, when applicable.

Relative L2 is secondary:

`relative_L2 = L2_rms(error) / L2_rms(exact)`

It may be recorded only when the exact denominator is finite and strictly
positive.

A missing relative norm must be represented as `null`, not zero.

No observed order is calculated by the core harness.

No rate fitting is performed by the core harness.

---

## 24. Metadata schema

The metadata schema identifier is:

`PHASE13_VERIFICATION_METADATA_V1`

Every case must record at least:

### Repository identity

- repository name;
- active branch;
- Git commit;
- Git dirty status;
- Phase 13B specification hash;
- Phase 13C audit-report hash;
- protected solver-source hashes;
- exact-reference module hash;
- harness module hash;
- output-schema module hash.

### Environment

- UTC timestamp;
- operating system;
- Python version;
- NumPy version;
- floating-point dtype;
- machine epsilon.

### Benchmark configuration

- benchmark identifier;
- track;
- reference version;
- O2 compatibility policy;
- source policy;
- advection method;
- product-dealiasing status;
- post-step mask policy.

### Numerical configuration

- `N`;
- `L`;
- `dx`;
- `Re`;
- `nu`;
- `dt`;
- `n_steps`;
- initial time;
- actual final time;
- constructor `steps` value.

### Execution-boundary record

- solver class;
- allowed methods called;
- prohibited methods called;
- forcing-call count;
- mask-application count;
- input-mutation status;
- solver-state-mutation status.

### Result identity

- case identifier;
- case status;
- output filenames;
- output SHA-256 values;
- error-summary values;
- failure messages.

A required missing field is a schema failure.

---

## 25. Output schema

The proposed output root is:

`experiments/verification/phase13/<run_id>/`

A future controlled run directory contains:

- `run_manifest.json`;
- one subdirectory per case.

Each case directory contains:

- `case_metadata.json`;
- `checks.json`;
- `error_summary.csv`;
- `fields.npz`;
- `field_manifest.json`.

### Operator-track arrays

`fields.npz` for O1 or O2 contains:

- `omega_raw`;
- `omega_input`;
- `computed_adv`;
- `exact_adv`;
- `error_adv`.

### Evolution-track arrays

`fields.npz` for Track L or Track M contains:

- `initial_omega`;
- `numerical_omega`;
- `exact_omega`;
- `error_omega`.

Track M may additionally contain explicitly named source-stage samples when
required by the pilot design.

### Atomic writing

Each JSON, CSV, or NPZ output must first be written to a temporary filename and
then atomically renamed.

A partially written case must have status:

`INCOMPLETE`

It must not be interpreted as a passing result.

### No automatic plots

The core harness does not create plots.

Plotting and rate analysis belong to a later analysis phase.

---

## 26. Predeclared failure gates

The harness must fail before or during a case when any of the following occurs:

- repository commit is not the authorized checkpoint;
- the repository is dirty when clean-state execution is required;
- a protected source hash differs;
- a harness or reference hash is missing;
- the benchmark identifier is unknown;
- the method identifier is unknown;
- an advection method is supplied to primary Track L evolution;
- a required advection method is absent for O1, O2, or M;
- `N` is invalid;
- `Re <= 0`;
- `nu <= 0`;
- `nu != 1/Re` under the declared tolerance;
- `dt <= 0` for evolution;
- `n_steps` is not a nonnegative integer;
- requested and actual final times do not align;
- the solver grid differs from the independent grid;
- the solver mask differs from the independent mask;
- an exact field is nonfinite, complex, or incorrectly shaped;
- an input field is mutated;
- `solver.w` is mutated;
- a returned field shares forbidden writable memory with an input;
- a prohibited method is called;
- inherited forcing is called;
- baseline forcing is included in Track L or Track M;
- Track M stage 2 source is evaluated at `t_n`;
- Track M source is not evaluated at `t_n + dt`;
- spectral diffusion is multiplied by viscosity twice;
- the post-step mask is applied zero times or more than once for an evolution
  step;
- the post-step mask is applied during Track O;
- O2 compatibility handling differs between methods;
- O2 exact advection is generated numerically;
- one method's result is reused for another method;
- output metadata is incomplete;
- an output hash cannot be computed;
- any primary error field is nonfinite.

A failed case produces no convergence claim.

---

## 27. Future implementation-audit requirements

Before any numerical pilot, the implementation phase must pass:

### Static import audit

The exact-reference module must contain no project-solver imports.

### Prohibited-call audit

The harness source must contain no call path to:

- `compute_rhs_selectable`;
- `step_once_selectable`;
- `run_selectable_diagnostic`;
- `run`;
- inherited forcing.

### Interface audit

Function signatures and schema identifiers must match this design.

### Source hash audit

The three protected solver files must remain unchanged unless a separately
authorized phase changes them.

### Reference-formula audit

The implemented analytic functions must be checked against the Phase 13C
identities.

### Mutation-guard audit

Deliberately mutating test doubles must be detected by the harness guards.

### Output-schema audit

Missing required metadata must cause failure.

### No numerical pilot during static audit

A static implementation audit does not authorize a solver evaluation or time
step.

---

## 28. Future pilot authorization boundary

Phase 13D authorizes no pilot.

A later explicitly authorized pilot may not exceed the following boundary.

### Single-grid boundary

Only:

`N = 16`

may be used.

No second spatial resolution is permitted.

### Operator boundary

At most one O1 and one O2 operator evaluation may be performed for each of:

- `fd_centered`;
- `pseudo_spectral`;
- `arakawa`.

These are isolated operator evaluations, not refinement sequences.

### Track L boundary

At most two external RK2-style steps may be performed in one Track L pilot
case.

### Track M boundary

At most two external RK2-style steps may be performed for each selectable
method in one Track M pilot case.

### No sequence boundary

The pilot must not include:

- a grid sequence;
- a time-step sequence;
- a viscosity sequence;
- a final-time sequence.

### Pilot interpretation

Pilot output may be used only to assess:

- interface correctness;
- source replacement;
- stage timing;
- mutation guards;
- mask count;
- output completeness;
- finite execution.

Pilot output must not support:

- observed-order calculation;
- an asymptotic-range claim;
- a method-superiority claim;
- solver-wide verification;
- physical validation.

Expansion beyond this boundary requires a new phase and explicit authorization.

---

## 29. Claim boundaries

Phase 13D establishes a harness design.

It does not establish:

- successful implementation;
- successful solver integration;
- operator accuracy;
- evolution accuracy;
- error decay;
- observed order;
- spectral convergence;
- exponential convergence;
- an asymptotic range;
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

A well-designed harness is necessary for later verification.

It is not itself verification evidence.

---

## 30. Phase 13D completion criteria

Phase 13D passes when:

- this design document exists;
- the Phase 13C checkpoint remains its parent;
- the Phase 13C report remains unchanged;
- the Phase 13B specification remains unchanged;
- protected solver-source hashes remain unchanged;
- exact-reference file boundaries are frozen;
- external-harness file boundaries are frozen;
- benchmark identifiers are frozen;
- O2 compatibility handling is frozen;
- Track L RHS behavior is frozen;
- Track M RHS behavior is frozen;
- source replacement is explicit;
- Track M stage times are explicit;
- post-step mask behavior is frozen;
- method-specific boundaries are explicit;
- immutability guards are explicit;
- error norms are explicit;
- metadata and output schemas are explicit;
- failure gates are explicit;
- future pilot limits are explicit;
- no Python module was created;
- no solver module was imported;
- no solver method was executed;
- no simulation or time step was run;
- no formal refinement sequence was run;
- no convergence or physical claim was made.

---

## 31. Recommended next phase

The recommended next phase is:

**Phase 13E — External Verification-Harness Implementation and Static Interface Audit**

Phase 13E may authorize creation of the proposed verification modules.

Phase 13E should initially remain non-executing and should include:

- exact-reference implementation;
- harness implementation;
- schema implementation;
- static import inspection;
- prohibited-call inspection;
- source-hash inspection;
- reference-formula inspection;
- mutation-guard unit design;
- output-schema inspection.

Phase 13E should not begin a numerical pilot merely because Phase 13D passes.

A numerical pilot should require a separately authorized Phase 13F gate.
