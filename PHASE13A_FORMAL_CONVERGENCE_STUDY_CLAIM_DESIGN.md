# Phase 13A — Formal Convergence-Study Claim Design

## 0. Document control

- Project: Raj-Sanghera-Project
- Phase: 13A
- Phase title: Formal Convergence-Study Claim Design
- Starting checkpoint:
  `v0.5.44-phase12R-phase12-validation-summary-and-archive-report`
- Phase 12 status: complete
- Phase 13A status: design-only
- Numerical runs authorized by this document: none
- Solver source changes authorized by this document: none
- Formal convergence claims made by this document: none
- Physical-validation claims made by this document: none
- Production-readiness claims made by this document: none

Phase 13A defines the evidence, controls, calculations, decision gates, and
language that would be required before a future benchmark-specific numerical
convergence claim could be considered.

Phase 13A is a design-only phase.

---

## 1. Non-negotiable phase boundaries

During Phase 13A:

- no simulation is run;
- no time step is executed;
- no formal refinement sequence is run;
- no existing result is retroactively relabeled as a convergence study;
- `SpectralSolver` is not modified;
- `SelectableAdvectionSolver` is not modified;
- `advection_operators.py` is not modified;
- `SelectableAdvectionSolver.run()` remains disabled;
- no production-style selectable solver loop is enabled;
- no output directory is modified;
- no existing artifact is deleted, moved, or rewritten;
- no spectral slope is fitted;
- no numerical convergence is claimed;
- no turbulence is claimed;
- no inertial range is claimed;
- no direct or inverse cascade is claimed;
- no `k^-3` law or validated `k^-3` scaling is claimed;
- no method-superiority claim is made;
- no production-readiness claim is made.

A future Phase 13 calculation may use only an explicitly audited external
verification harness or controlled calls to `step_once_selectable()`.

It must not enable or use `SelectableAdvectionSolver.run()`.

---

## 2. Purpose of the convergence-study program

The future convergence-study program will answer narrow numerical questions:

1. Does a declared discrete operator approximate a declared continuous
   operator for a smooth periodic benchmark?

2. Does the exact error decrease as spatial or temporal resolution is refined?

3. When an algebraic error regime is supported, what observed order is measured
   for a declared method, benchmark, norm, and refinement interval?

4. When an exact reference is unavailable, do consistently restricted numerical
   solutions approach each other under refinement?

5. What is the strongest wording justified by the evidence actually obtained?

It will not answer whether a forced calculation is turbulent, whether a
physical cascade exists, whether a spectral law is present, or whether the
solver is generally valid for untested applications.

---

## 3. Required verification vocabulary

### 3.1 Code verification

Code verification asks whether the implementation correctly represents the
intended mathematical model and numerical method.

Appropriate evidence includes:

- exact solutions;
- independently derived manufactured solutions;
- analytic operator tests;
- benchmark solutions of demonstrably higher accuracy;
- systematic refinement studies.

Code verification is not physical validation.

### 3.2 Calculation or solution verification

Calculation verification estimates or characterizes numerical error in a
specific computed result.

Its conclusions are limited to the declared:

- equation;
- benchmark;
- numerical method;
- grid family;
- time-step family;
- norm or quantity of interest;
- final time;
- parameter values.

### 3.3 Physical validation

Physical validation compares the mathematical model with appropriate physical,
experimental, or observational evidence.

Phase 13 is not a physical-validation phase.

### 3.4 Operator consistency

An operator-consistency study compares a discrete operator with the
corresponding independently evaluated continuous operator on known smooth
fields.

Decreasing operator error under refinement is evidence about that operator.

It is not, by itself, evidence that the complete time-dependent solver
converges.

### 3.5 Resolution sensitivity

A resolution-sensitivity result states only that a declared result changed by a
reported amount when resolution changed.

Resolution sensitivity is not convergence.

### 3.6 Exact-error decay

Exact-error decay means that a declared norm of the difference between the
numerical solution and an exact or manufactured solution decreases under
systematic refinement.

This is stronger than comparison between numerical solutions alone.

### 3.7 Self-convergence

Self-convergence compares numerical solutions at multiple resolutions after
placing them on a consistent common representation.

Self-convergence may show approach toward a common numerical limit.

It does not prove that the common limit is the correct solution of the intended
continuous equation.

### 3.8 Nominal order

Nominal order is the formal order associated with the documented numerical
discretization under its mathematical assumptions.

A method name does not, by itself, establish nominal order for this
implementation.

Nominal order must be derived or documented from the actual implemented
stencil, filter, projection, and time-integration procedure.

### 3.9 Observed order

Observed order is an empirical rate inferred from a declared error measure over
a declared refinement interval.

Observed order is specific to:

- one benchmark;
- one method;
- one norm;
- one refinement sequence;
- one parameter set;
- one final time;
- one treatment of other error sources.

It is not a universal property of the entire solver.

### 3.10 Asymptotic range

An asymptotic-range statement requires evidence that the leading discretization
error term dominates the measured error over the tested refinement levels.

Small coarse–fine differences alone do not establish an asymptotic range.

### 3.11 Numerical uncertainty estimate

A Richardson-extrapolation or Grid Convergence Index style estimate is a
conditional numerical-discretization estimate.

It is not:

- experimental uncertainty;
- model-form uncertainty;
- physical validation;
- proof of the continuum solution;
- proof that every solver output has the same uncertainty.

---

## 4. Claim classes

The following claim classes are separate and must not be substituted for one
another.

### Class C0 — Execution and provenance integrity

Required evidence:

- clean tagged source state;
- documented environment;
- finite outputs;
- reproducible configuration;
- successful metadata checks.

Permitted wording:

> The declared benchmark calculation completed under the documented source and
> configuration controls.

Not permitted:

> The calculation converged.

### Class C1 — Resolution sensitivity

Required evidence:

- at least two resolutions;
- same continuous problem;
- same final physical time;
- same declared quantity;
- reported numerical difference.

Permitted wording:

> The declared quantity changed by the reported amount between the tested
> resolutions.

Not permitted:

> The result is resolution converged.

### Class C2 — Self-convergence evidence

Required evidence:

- at least three systematically refined solutions;
- audited common-grid restriction;
- same method and continuous problem;
- decreasing successive solution differences;
- controlled temporal contamination for a spatial study.

Permitted wording:

> Successive restricted solution differences decreased over the tested
> refinement sequence, providing benchmark-specific self-convergence evidence.

Mandatory limitation:

> This does not establish convergence to the correct continuous solution.

### Class C3 — Exact-error decay

Required evidence:

- exact or independently manufactured reference solution;
- at least three refinement levels;
- declared error norms;
- independently audited reference evaluation;
- controlled competing errors;
- decreasing exact error.

Permitted wording:

> The declared exact-solution error decreased over the tested refinement range.

This wording does not yet assert a stable observed order.

### Class C4 — Benchmark-specific observed algebraic order

Required evidence:

- all Class C3 requirements;
- errors above the numerical-noise floor;
- a justified algebraic error model;
- stable interval-order behavior under a predeclared rule;
- no post hoc deletion of unfavorable levels;
- no unresolved temporal or spatial contamination.

Permitted wording:

> For the declared benchmark, method, norm, and refinement interval, the
> measured exact error exhibited an observed algebraic order of approximately
> `p`.

Mandatory limitation:

> This result is benchmark-specific and does not establish a universal order
> for the complete solver.

### Class C5 — Pseudo-spectral error-decay characterization

This class is separate from Class C4.

A pseudo-spectral method must not be forced into an algebraic-order claim merely
because an algebraic-order formula is available.

Required evidence:

- a smooth periodic benchmark suitable for spectral differentiation;
- at least four useful pre-floor resolution levels for a fitted decay model;
- fixed dealiasing and filtering;
- exact errors above the numerical floor;
- predeclared model-selection and fit-quality rules.

Possible permitted wording:

> For the declared smooth periodic benchmark, the pseudo-spectral exact error
> decreased rapidly over the tested resolution range before reaching the
> reported numerical floor.

A stronger phrase such as `spectral` or `exponential error decay` requires a
predeclared model, sufficient pre-floor points, and a documented fit assessment.

No fixed algebraic order is assumed.

### Class C6 — Conditional scalar numerical-uncertainty estimate

Required evidence:

- a declared scalar quantity of interest;
- at least three suitable refinement levels;
- an algebraic error regime supported by the data;
- stable observed order;
- documented Richardson or GCI assumptions;
- documented factor of safety;
- no near-zero normalization problem;
- no unresolved oscillatory or divergent behavior.

Permitted wording:

> Under the stated refinement-model assumptions, the numerical
> discretization estimate for the declared scalar quantity is the reported
> value.

This does not establish physical uncertainty or validation.

### Class C7 — Broad solver or physical claim

Phase 13 does not authorize claims such as:

- the solver is converged;
- the solver is fully verified;
- every selectable method converges;
- the continuum solution has been proven;
- the model is physically validated;
- the simulation is turbulent;
- a cascade has been established;
- a `k^-3` law has been verified;
- the solver is production ready.

---

## 5. Conservative claim-selection rule

When evidence could be described using more than one class, the least ambitious
fully supported class must be used.

Examples:

- two close results support at most Class C1;
- decreasing three-grid differences without an exact solution support at most
  Class C2;
- decreasing exact errors without stable order support Class C3;
- a stable algebraic observed order may support Class C4;
- rapid pseudo-spectral decay without a justified fitted model supports only a
  descriptive Class C5 statement;
- an unstable or noise-dominated sequence is inconclusive.

A failed high-level gate does not authorize stronger wording through qualitative
interpretation.

---

## 6. Numerical methods under consideration

The selectable methods are:

- `fd_centered`;
- `pseudo_spectral`;
- `arakawa`.

Each method must be studied separately.

A valid method-specific sequence must use the same method at every refinement
level.

The following is invalid:

- coarse result from `fd_centered`;
- medium result from `pseudo_spectral`;
- fine result from `arakawa`;
- one observed-order calculation across those three results.

Cross-method differences may be reported as secondary comparisons only after
each method has independently passed its applicable verification gates.

Method comparison is not method superiority.

Computational cost, stability margin, conservation behavior, and error magnitude
are different questions and must not be collapsed into one ranking.

---

## 7. The tested algorithm includes more than the named advection operator

For a time-dependent result, the tested numerical algorithm may include:

- the selected advection discretization;
- streamfunction recovery;
- velocity reconstruction;
- diffusion;
- forcing or manufactured source evaluation;
- time integration;
- dealiasing;
- filtering;
- projection;
- field updates;
- initialization;
- final-time alignment.

An observed order for the integrated solution is therefore an observed order of
the complete declared benchmark algorithm, not automatically the isolated
advection stencil.

Operator-only and full-evolution studies must remain separate.

---

## 8. Proposed verification tracks

## 8.1 Track O — Static analytic operator verification

Purpose:

- isolate the spatial advection implementation;
- avoid temporal-discretization contamination;
- compare each selectable advection operator with an independently evaluated
  continuous advection term.

Required benchmark properties:

- periodic;
- smooth;
- real-valued;
- finite;
- analytically differentiable;
- streamfunction and vorticity mutually consistent;
- nonzero nonlinear advection;
- nontrivial variation in both coordinate directions;
- identical continuous field across all grids.

The analytic benchmark must be constructed so that:

- vorticity is not merely proportional to streamfunction;
- the nonlinear term does not vanish identically;
- multiple non-collinear modes or an appropriate smooth broad-spectrum function
  are present;
- the same discrete operator is not used to generate the reference derivative.

Primary error:

`discrete advection - independently evaluated continuous advection`

Primary norms:

- absolute discrete `L1`;
- absolute discrete `L2`;
- absolute discrete `L-infinity`;
- relative `L2` only when the reference norm is safely nonzero.

Track O may support operator-consistency or benchmark-specific operator-order
claims.

It does not verify the complete time-dependent solver.

### Pseudo-spectral Track O caution

A finite low-mode trigonometric polynomial may be differentiated to nearly
machine precision on every tested grid.

Such a benchmark can test correctness but may not provide a meaningful
resolution-decay sequence.

The pseudo-spectral benchmark design must therefore distinguish:

1. an exactness or near-exactness test for resolved modes; and
2. a smooth broad-spectrum resolution-decay test.

No observed order may be calculated from errors dominated by floating-point
noise.

---

## 8.2 Track L — Exact linear viscous-decay evolution

Purpose:

- verify viscous decay behavior;
- examine time integration;
- examine exact final-time field error;
- test spatial representation under a simple exact solution;
- confirm final-time and norm infrastructure.

A suitable periodic eigenmode may have a known exponential viscous-decay
solution.

Important limitation:

For a single Laplacian eigenmode, or another specially aligned field, the
nonlinear advection term may vanish identically.

Track L must therefore not be used to verify:

- nonlinear `fd_centered` advection;
- nonlinear `pseudo_spectral` advection;
- nonlinear `arakawa` advection;
- cross-method nonlinear behavior.

Track L can support only the components it actually exercises.

---

## 8.3 Track M — Time-dependent nonlinear manufactured solution

Purpose:

- exercise the complete declared vorticity evolution;
- produce an exact field reference;
- test each selectable method independently;
- estimate exact errors under spatial and temporal refinement.

Requirements:

- the manufactured streamfunction must be explicitly defined;
- the manufactured vorticity must satisfy the project’s audited
  streamfunction–vorticity sign convention;
- the velocity definition must match the implemented convention;
- the nonlinear advection term must be analytically nonzero;
- diffusion must be nontrivial unless a separate inviscid test is declared;
- time dependence must be nontrivial;
- the required source term must be independently derived from the continuous
  equation;
- the source must not be generated using the production discrete operator;
- the exact solution must be smooth and periodic;
- all expressions must remain finite;
- the exact initial condition must be used independently on every grid.

The continuous residual must be audited before numerical runs.

The source-term derivation must be independently checked by at least two of:

- symbolic substitution;
- independently written analytic derivative code;
- high-precision point evaluation;
- hand-derived term comparison;
- automatic differentiation independent of the solver discretization.

Using the same discrete derivative implementation to manufacture the source and
then test that implementation is prohibited because it can conceal matching
errors.

---

## 8.4 Track S — Controlled self-convergence study

Purpose:

- evaluate approach of selected numerical fields or observables under
  refinement when no exact solution is available;
- test fine-to-coarse restriction;
- provide secondary evidence about resolution behavior.

Track S is secondary.

It cannot replace Tracks O or M for code verification.

Track S cannot establish:

- correctness of the continuous-equation implementation;
- physical validation;
- turbulence;
- a cascade;
- a spectral law;
- `k^-3` behavior;
- universal solver convergence.

Existing Phase 12 comparisons may inform Track S design but must not be
retroactively relabeled as a formal self-convergence study unless every
predeclared Phase 13 requirement is independently satisfied.

---

## 9. Benchmark coverage matrix

| Track | Spatial operator | Time integrator | Diffusion | Nonlinear advection | Exact field reference | Main limitation |
|---|---:|---:|---:|---:|---:|---|
| O | Yes | No | Optional | Yes | Exact operator value | Not full evolution |
| L | Partial | Yes | Yes | Usually no | Yes | Does not verify nonlinear advection |
| M | Yes | Yes | Yes | Yes | Yes | Requires independently audited source |
| S | Combined response | Yes | As configured | As configured | No | Cannot prove correctness |

No single track is sufficient to verify every solver component.

---

## 10. Spatial and temporal refinement must be separated

## 10.1 Spatial-refinement study

Varied quantity:

- spatial resolution `N`;
- equivalently grid spacing `h = L / N`.

Held fixed:

- continuous equation;
- domain;
- method;
- viscosity;
- exact/manufactured solution;
- source definition;
- initial condition;
- final physical time;
- diagnostic definitions;
- filtering and dealiasing policy;
- software state;
- arithmetic precision;
- output comparison procedure.

Temporal error must be demonstrated to be subordinate under a predeclared rule.

## 10.2 Temporal-refinement study

Varied quantity:

- time step `dt`.

Held fixed:

- spatial grid;
- continuous equation;
- method;
- viscosity;
- exact/manufactured solution;
- source definition;
- initial condition;
- final physical time;
- diagnostic definitions;
- filtering and dealiasing policy;
- software state;
- arithmetic precision.

Spatial error must be demonstrated to be subordinate under a predeclared rule.

## 10.3 Coupled refinement is not a substitute

Changing `N` and `dt` together without a justified error-separation design does
not, by itself, identify spatial or temporal order.

A coupled sequence may be used only when:

- the scaling relation is predeclared;
- the resulting claim is explicitly about the coupled algorithm;
- separate pilot evidence supports the interpretation.

---

## 11. Refinement-family requirements

A constant refinement ratio is preferred for the initial formal study.

Candidate spatial ratio:

`r_h = 2`

Candidate temporal ratio:

`r_t = 2`

Candidate spatial families may include:

- `N = 32, 64, 128, 256`; or
- another four-level `r_h = 2` family justified by a pilot.

These are design candidates, not authorized runs.

Requirements:

- at least three levels for a basic three-level order estimate;
- four useful levels are strongly preferred for order-stability assessment;
- at least four useful pre-floor levels are required before fitting a
  pseudo-spectral decay model;
- all levels must represent the same continuous problem;
- all calculations must end at the same physical time;
- every `dt` must divide the final time consistently, or the final-step policy
  must be defined in advance;
- no level may be removed after results are viewed unless the entire formal
  sequence is declared invalid and redesigned.

A pilot level used to tune thresholds or choose the formal range is exploratory
and must not automatically be reused as formal claim evidence.

---

## 12. Initial-condition controls

The same continuous initial condition must be evaluated independently on every
grid.

The following are prohibited in a formal exact-error study unless explicitly
part of the declared benchmark:

- initializing a fine grid from an interpolated coarse numerical solution;
- changing mode amplitudes with resolution;
- changing phase with resolution;
- changing normalization with resolution;
- applying an undocumented resolution-dependent filter;
- using a previously evolved field as the exact initial condition.

At `t = 0`, the numerical field must be checked against the exact initial field.

Any initial projection or filter error must be measured and reported.

---

## 13. Source and forcing controls

For a manufactured solution:

- the source is part of the mathematical benchmark;
- its continuous expression must be frozen before formal runs;
- it must be evaluated consistently at every resolution;
- no resolution-dependent amplitude adjustment is permitted;
- no solver discrete derivative may be used to construct the reference source;
- sign conventions must be audited independently.

For Track S:

- forcing geometry;
- forcing amplitude;
- viscosity;
- drag, if any;
- integration duration;
- starting field;
- output time

must remain identical as continuous quantities across the refinement sequence.

No forced-response spectral result may be converted into a turbulence or
`k^-3` claim.

---

## 14. Dealiasing, filtering, and projection controls

The following are part of the tested numerical algorithm and must be frozen:

- dealiasing mask;
- mask cutoff convention;
- whether the mask is applied to the state, nonlinear product, or both;
- filter application frequency;
- FFT normalization;
- zero-mode treatment;
- Nyquist-mode treatment;
- real-field reconstruction;
- post-step projection.

A change in filter or dealiasing policy creates a different numerical method.

Results from different policies must not be combined in one observed-order
calculation.

For `pseudo_spectral`, aliasing and truncation effects must not be conflated
without analysis.

---

## 15. Primary exact-error norms

Let:

`e_ij = numerical_ij - exact_ij`

For an `N x N` periodic uniform grid, the primary mean-normalized discrete norms
are:

`L1(e) = (1 / N^2) * sum_ij |e_ij|`

`L2(e) = sqrt((1 / N^2) * sum_ij e_ij^2)`

`L-infinity(e) = max_ij |e_ij|`

The corresponding cell-area-weighted norms may also be reported, but one
definition must be selected before formal runs and used consistently.

Relative `L2` may be reported only when the exact reference norm is safely
nonzero:

`relative_L2 = L2(e) / L2(exact)`

If the denominator is near zero, the absolute error must be used.

Primary field:

- vorticity.

Possible secondary fields:

- streamfunction;
- velocity component `u`;
- velocity component `v`;
- continuous-equation residual;
- selected Fourier coefficients.

---

## 16. Secondary quantities of interest

Secondary scalar quantities may include:

- kinetic energy;
- enstrophy;
- vorticity RMS;
- selected mode amplitudes;
- selected integral diagnostics.

Agreement in a scalar quantity does not establish field convergence.

For example, similar total energy can coexist with significant phase or local
field error.

Field norms therefore remain primary when an exact field is available.

---

## 17. Spectral diagnostics are not primary convergence evidence

A spectrum may be reported as a secondary diagnostic.

Phase 13 does not use spectral slope fitting as a primary convergence measure.

Phase 13 must not infer from spectral similarity:

- turbulence;
- an inertial range;
- an enstrophy cascade;
- an inverse-energy cascade;
- a direct cascade;
- a `k^-3` law;
- convergence of a fitted exponent.

A future spectral convergence study would require its own predeclared
definition of spectral error, shell support, common resolved range, and
uncertainty.

That study is outside Phase 13A.

---

## 18. Exact-reference comparison procedure

When an exact solution is available:

1. evaluate the exact continuous solution directly on each grid;
2. compare the numerical and exact fields on that native grid;
3. use identical norm definitions;
4. use identical physical time;
5. avoid interpolation unless interpolation is explicitly part of the tested
   output procedure.

Native-grid exact comparison is preferred because it avoids introducing a
fine-to-coarse restriction error into the primary exact-error norm.

---

## 19. Self-convergence restriction procedure

When no exact field is available, all compared fields must be represented on a
common grid.

For a periodic domain, the preferred procedure is an audited Fourier
restriction:

1. transform each fine field using the documented FFT normalization;
2. retain only modes represented on the declared common coarse grid;
3. handle positive, negative, Nyquist, and zero modes explicitly;
4. preserve the documented amplitude normalization;
5. inverse transform to the common grid;
6. compare all fields using one norm definition.

The restriction implementation must first pass known-field tests:

- exact retention of supported low modes;
- removal of unsupported modes;
- real-field reconstruction;
- amplitude preservation;
- zero-field preservation;
- constant-field preservation;
- no unexpected phase shift.

Direct nested-grid point sampling may be reported as a secondary sensitivity
check, not silently substituted for the primary restriction method.

---

## 20. Exact-error observed-order calculation

Let the coarse and fine grid spacings satisfy:

`r = h_coarse / h_fine > 1`

Let the corresponding exact-error norms be:

`E_coarse` and `E_fine`

The pairwise observed order is:

`p = log(E_coarse / E_fine) / log(r)`

This estimate may be reported only when:

- both errors are finite;
- both errors are positive;
- both errors exceed the predeclared numerical floor;
- the same norm is used;
- the same benchmark is used;
- the same method is used;
- competing error sources are controlled;
- an algebraic error model is justified.

With four levels, adjacent interval orders must be reported separately.

A regression slope may be reported only as an additional analysis and must not
hide unstable interval orders.

---

## 21. Self-convergence order calculation

For three solutions with constant refinement ratio `r`, restrict all solutions
to the same declared coarse representation.

Define:

`D_01 = norm(u_h - R_h[u_(h/r)])`

`D_12 = norm(R_h[u_(h/r)] - R_h[u_(h/r^2)])`

A self-convergence estimate is:

`p_self = log(D_01 / D_12) / log(r)`

This calculation is interpretable only when:

- both differences are finite;
- both differences are positive;
- both differences exceed the numerical floor;
- the restriction operator has passed its audit;
- the same norm and common grid are used;
- the sequence is not irregular;
- temporal contamination is controlled.

The result must be labeled `self-convergence order estimate`.

It must not be labeled `exact order` or proof of correctness.

---

## 22. Pseudo-spectral error-decay policy

For `pseudo_spectral`, the primary record must include:

- exact errors at every tested `N`;
- the reported numerical floor;
- the dealiasing and filtering configuration;
- whether the benchmark is band-limited;
- whether all benchmark modes are exactly represented;
- the number of useful pre-floor points.

Possible descriptive models include:

`E(N) approximately C * exp(-alpha * N)`

or, when justified,

`E(N) approximately C * N^(-p)`

No model is selected after viewing results without a predeclared model-selection
rule.

A two-point or three-point rapid decrease is not sufficient to claim
exponential or spectral convergence.

If the error reaches roundoff too early, the permitted conclusion is:

> The tested benchmark reached the numerical error floor over the reported
> resolutions; no reliable decay rate was estimated.

---

## 23. Numerical-noise and error-floor rule

No observed order may be calculated from errors dominated by:

- machine roundoff;
- FFT roundoff;
- cancellation;
- exact-solution evaluation noise;
- output truncation;
- restriction error;
- source-evaluation noise.

Before formal runs, the pre-registration must define:

- machine precision;
- characteristic field scale;
- absolute error-floor rule;
- relative error-floor rule;
- plateau-detection rule;
- handling of zero or near-zero error.

If either member of a pair is at or below the declared floor, that pair is
excluded from rate estimation by the predeclared rule.

The raw value must still be reported.

---

## 24. Spatial–temporal error isolation

### Before a spatial-order claim

A time-step pilot must show that reducing `dt` changes the declared primary
error by less than a predeclared fraction of the spatial-refinement difference.

The fraction must be selected before the formal spatial sequence.

### Before a temporal-order claim

A spatial-resolution pilot must show that further increasing `N` changes the
declared primary error by less than a predeclared fraction of the temporal
refinement difference.

### Prohibited practice

The contamination threshold must not be selected after inspecting the formal
result.

Pilot calculations used to select the threshold must be labeled exploratory.

---

## 25. Asymptotic-range decision rule

An asymptotic-range claim requires more than decreasing error.

Before formal runs, the pre-registration must define a rule involving one or
more of:

- stability of adjacent observed orders;
- stability of `C = E / h^p`;
- consistency of fine/medium and medium/coarse error estimates;
- an applicable GCI asymptotic-ratio check;
- absence of oscillatory or divergent behavior.

The tolerance must be frozen prospectively.

If the rule fails, the phrase `asymptotic range` must not be used.

The result may be downgraded to exact-error decay, resolution sensitivity, or
inconclusive.

---

## 26. Monotonic, oscillatory, and irregular behavior

For a scalar quantity of interest, signed successive differences should be
examined.

Possible classifications include:

- monotonic approach;
- oscillatory approach;
- divergent behavior;
- irregular or indeterminate behavior.

A logarithmic observed-order formula must not be applied blindly when the
required ratio is nonpositive or unstable.

For field norms, decreasing nonnegative errors do not by themselves prove that
the leading asymptotic term dominates.

---

## 27. Optional Richardson extrapolation and GCI policy

Richardson extrapolation or a Grid Convergence Index style estimate is optional,
not automatic.

It may be considered only when:

- the quantity of interest is explicitly declared;
- an algebraic error model is supported;
- the observed order is stable;
- the sequence is suitable;
- normalization is well conditioned;
- assumptions are documented;
- the calculation follows a frozen analysis procedure.

It should not be applied to:

- a noise-dominated sequence;
- a nonmonotonic sequence without an appropriate method;
- two close values with no established order;
- mixed numerical methods;
- mismatched final times;
- an unsupported pseudo-spectral algebraic model;
- a fitted spectral exponent;
- a physical turbulence claim.

A GCI-style value is a numerical-discretization estimate for the declared
quantity.

It is not a physical uncertainty band.

---

## 28. Reproducibility metadata

Every future formal run must record:

- phase and track identifier;
- benchmark identifier and revision;
- equation revision;
- source-term revision;
- Git commit;
- Git tag;
- branch;
- Git dirty status;
- hashes of relevant source files;
- Python version;
- NumPy version;
- operating system;
- arithmetic precision;
- method;
- resolution;
- domain size;
- grid spacing;
- time step;
- step count;
- exact final time;
- viscosity or Reynolds-number parameter;
- forcing/source identifier;
- initial-condition identifier;
- dealiasing configuration;
- filtering configuration;
- primary norm definitions;
- restriction implementation revision;
- error-floor rule;
- temporal-isolation rule;
- output path;
- run completion status;
- confirmation that `SelectableAdvectionSolver.run()` remained disabled;
- confirmation that no turbulence, cascade, or `k^-3` claim was generated.

---

## 29. Pre-registration requirements

Before formal calculations begin, a machine-readable and human-readable
pre-registration must freeze:

- benchmark equation;
- exact or manufactured solution;
- source term;
- methods;
- resolution levels;
- time-step levels;
- final time;
- primary field;
- primary norm;
- secondary quantities;
- restriction method;
- error-floor rule;
- temporal-isolation threshold;
- spatial-isolation threshold;
- order-stability rule;
- asymptotic-range rule;
- pseudo-spectral model-selection rule;
- allowed claim language;
- downgrade language;
- failure conditions;
- formal analysis script hash.

No primary metric may be changed after formal data are viewed.

Exploratory results used to design the registration must be clearly separated
from the formal evidence set.

---

## 30. No-post-hoc-selection policy

The following are prohibited:

- removing an unfavorable resolution after seeing the result;
- changing the primary norm after seeing the result;
- reporting only the most favorable method;
- reporting only the most favorable field;
- replacing exact error with a scalar diagnostic because exact error performed
  poorly;
- fitting only a visually favorable subset without a predeclared rule;
- changing the final time after inspecting results;
- changing source amplitude with resolution;
- treating a failed run as if it never occurred;
- combining pilot and formal data without disclosure;
- claiming the expected theoretical order merely because it was expected.

All formal levels and all declared primary metrics must be reported.

---

## 31. Formal decision gates

## Gate G0 — Source provenance

Pass requirements:

- expected checkpoint or later authorized Phase 13 checkpoint;
- clean working tree before formal execution;
- recorded commit and hashes;
- documented environment.

Failure result:

- formal evidence invalid.

## Gate G1 — Solver-boundary integrity

Pass requirements:

- `SelectableAdvectionSolver.run()` remains disabled;
- formal harness does not call it;
- controlled execution uses only audited entry points;
- no production loop is enabled.

Failure result:

- Phase 13 stops.

## Gate G2 — Continuous benchmark correctness

Pass requirements:

- exact/manufactured fields satisfy periodicity;
- streamfunction–vorticity relation passes;
- velocity convention passes;
- continuous residual passes;
- source sign and normalization pass;
- nonlinear term is nonzero when required.

Failure result:

- no convergence study.

## Gate G3 — Error and restriction harness

Pass requirements:

- exact zero-error case passes;
- known-amplitude norm cases pass;
- restriction known-mode cases pass;
- FFT normalization passes;
- real-field reconstruction passes.

Failure result:

- no formal error calculation.

## Gate G4 — Refinement integrity

Pass requirements:

- same continuous problem at every level;
- systematic refinement;
- same final physical time;
- same method;
- same source and initial condition;
- fixed filter/dealiasing policy.

Failure result:

- no observed-order calculation.

## Gate G5 — Competing-error isolation

Pass requirements:

- temporal error subordinate in a spatial study;
- spatial error subordinate in a temporal study;
- no unresolved source or restriction contamination.

Failure result:

- downgrade or inconclusive.

## Gate G6 — Numerical-floor integrity

Pass requirements:

- reported rate points exceed the frozen error floor;
- no zero denominator;
- no unexplained plateau or cancellation.

Failure result:

- no reliable rate estimate.

## Gate G7 — Rate-model adequacy

For algebraic order:

- stable interval orders under the frozen rule;
- suitable algebraic regime.

For pseudo-spectral decay:

- sufficient pre-floor points;
- frozen model-selection rule passes.

Failure result:

- report tabulated error decay only or declare inconclusive.

## Gate G8 — Reproducibility

Pass requirements:

- deterministic rerun or documented repeatability check;
- matching metadata;
- matching source state;
- results agree under the frozen tolerance.

Failure result:

- no formal claim.

## Gate G9 — Claim-language audit

Pass requirements:

- claim names benchmark, method, norm, range, and final time;
- limitations are included;
- no universal solver claim;
- no physical claim;
- no turbulence/cascade/`k^-3` claim.

Failure result:

- report must be rewritten before archival.

---

## 32. Permitted decision outcomes

### PASS-OPERATOR-CONSISTENCY

The declared discrete operator error decreased under refinement for the stated
analytic benchmark.

### PASS-EXACT-ERROR-DECAY

The declared exact field error decreased under refinement, but a stable rate
was not established.

### PASS-OBSERVED-ALGEBRAIC-ORDER

The declared exact error supported a benchmark-specific algebraic observed-order
statement under all frozen gates.

### PASS-PSEUDO-SPECTRAL-ERROR-DECAY

The pseudo-spectral error showed a reportable benchmark-specific decay pattern
before the numerical floor.

This outcome does not automatically authorize the phrase `exponential
convergence`.

### PASS-SELF-CONVERGENCE

Successive restricted numerical differences decreased under the frozen
self-convergence procedure.

This outcome does not establish correctness.

### RESOLUTION-SENSITIVITY-ONLY

Differences were measured, but convergence evidence was insufficient.

### INCONCLUSIVE

The data did not support a defensible convergence classification.

### FAIL-HARNESS-OR-REFERENCE

The reference solution, source derivation, restriction, norm implementation, or
formal harness failed an audit.

No convergence claim is allowed.

---

## 33. Claim templates

### 33.1 Operator-consistency template

> For the declared smooth periodic analytic benchmark, the
> `[method]` discrete advection-operator error in `[norm]` decreased over
> `N = [...]`. This provides benchmark-specific operator-consistency evidence.
> It does not verify the complete time-dependent solver.

### 33.2 Exact-error decay template

> For benchmark `[identifier]`, method `[method]`, final time `[T]`, and
> `[norm]`, the exact vorticity error decreased from `[value]` to `[value]`
> over `N = [...]`. A stable observed order was not established, so no formal
> order claim is made.

### 33.3 Observed algebraic-order template

> For benchmark `[identifier]`, method `[method]`, final time `[T]`, and
> `[norm]`, exact errors over `N = [...]` yielded adjacent observed orders
> `[values]`. Under the predeclared isolation, error-floor, and rate-stability
> criteria, these results provide benchmark-specific evidence of approximately
> `[p]`-order convergence over the tested range.

Mandatory follow-up sentence:

> This does not establish a universal order for the solver, physical
> validation, turbulence, a cascade, or `k^-3` behavior.

### 33.4 Pseudo-spectral decay template

> For the declared smooth periodic benchmark, exact `[norm]` error for
> `pseudo_spectral` decreased over `N = [...]` before reaching the reported
> numerical floor. The result is limited to the tested benchmark and
> configuration.

Unless separately authorized, add:

> No fixed algebraic order or exponential-convergence claim is made.

### 33.5 Self-convergence template

> Under the documented common-grid restriction, successive `[norm]`
> differences decreased over the tested refinement sequence. This is
> benchmark-specific self-convergence evidence and does not prove convergence
> to the correct continuous solution.

### 33.6 Inconclusive template

> The declared refinement sequence did not satisfy the predeclared conditions
> for a formal convergence claim. The result is reported as inconclusive rather
> than interpreted post hoc.

---

## 34. Prohibited claim language

The following statements are prohibited unless supported by a substantially
broader future verification and validation program:

- `The solver is converged.`
- `The solver has been fully verified.`
- `All selectable methods converge.`
- `N=128 is sufficient for all results.`
- `The exact continuum solution has been established.`
- `The simulation is physically validated.`
- `The computation proves turbulence.`
- `The computation proves an enstrophy cascade.`
- `The computation proves an inverse cascade.`
- `The computation verifies a k^-3 law.`
- `The spectral slope converged.`
- `The numerical methods are equivalent.`
- `One method is superior.`
- `The solver is research-grade because it converged.`
- `The solver is production ready.`

Any approved statement must remain benchmark-, method-, norm-, parameter-, and
range-specific.

---

## 35. Relationship to Phase 12

Phase 12 is complete and archived at:

`v0.5.44-phase12R-phase12-validation-summary-and-archive-report`

Phase 12 evidence may establish that controlled calculations, diagnostics, and
archive procedures passed their declared checks.

Phase 12 does not automatically establish:

- exact-error convergence;
- self-convergence;
- observed order;
- an asymptotic range;
- a GCI value;
- physical validation;
- turbulence;
- a cascade;
- `k^-3` behavior.

Phase 13 must use prospectively declared procedures.

---

## 36. Proposed Phase 13 sequence

### Phase 13A — Formal Convergence-Study Claim Design

Current phase.

Deliverable:

- this document only.

No simulations.

### Phase 13B — Benchmark and Continuous-Equation Specification

Expected deliverables:

- Track O analytic fields;
- Track L exact solution;
- Track M manufactured solution;
- continuous equation and sign conventions;
- source derivation;
- candidate refinement families;
- proposed prospective thresholds.

No formal runs.

### Phase 13C — Reference-Solution and Source Audit

Expected deliverables:

- symbolic or independent residual verification;
- periodicity checks;
- nonzero nonlinear-term checks;
- exact initial-condition checks;
- source-independence checks.

No formal runs.

### Phase 13D — Error-Norm and Restriction Harness Audit

Expected deliverables:

- known-field norm tests;
- Fourier restriction tests;
- amplitude and mode-index tests;
- numerical-floor calibration design.

No formal runs.

### Phase 13E — Controlled External Runner Design

Expected deliverables:

- audited external verification runner;
- explicit use of controlled methods such as `step_once_selectable()`;
- confirmation that `SelectableAdvectionSolver.run()` remains disabled;
- metadata schema;
- output schema.

No formal refinement sequence.

### Phase 13F — Exploratory Isolation Pilot

Expected work:

- determine viable resolution range;
- assess temporal contamination;
- assess spatial contamination;
- identify numerical floor;
- select prospective formal thresholds.

Pilot data remain exploratory.

### Phase 13G — Formal Pre-registration Freeze

Expected deliverables:

- frozen benchmark revision;
- frozen grids and time steps;
- frozen primary norm;
- frozen thresholds;
- frozen analysis script hash;
- frozen claim and downgrade wording.

### Phase 13H — Formal Refinement Runs

Not authorized by Phase 13A.

### Phase 13I — Formal Analysis and Claim Decision Gate

Possible outcomes are limited to those in Section 32.

### Phase 13J — Validation Summary and Archive Report

Archive only the claims actually authorized by the decision gate.

---

## 37. Phase 13A completion criteria

Phase 13A passes only when:

- the required Phase 12 checkpoint is verified;
- the starting working tree is clean;
- this design document is the only new file;
- protected solver files are unchanged;
- `SelectableAdvectionSolver.run()` remains statically disabled;
- no solver module is imported for this phase gate;
- no solver method is executed;
- no simulation is run;
- no output artifact is generated;
- exact-error and self-convergence claims are separated;
- spatial and temporal refinement are separated;
- operator and full-evolution verification are separated;
- pseudo-spectral behavior is not forced into an unsupported algebraic order;
- no turbulence, cascade, or `k^-3` claim is made;
- the next phase remains design and equation specification.

---

## 38. Methodological reference basis

The following sources inform the terminology and conservative design:

1. NASA NPARC Alliance, `Verification Assessment`

   https://www.grc.nasa.gov/www/wind/valid/tutorial/verassess.html

2. NASA NPARC Alliance, `Examining Spatial (Grid) Convergence`

   https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html

3. NASA NPARC Alliance, `Examining Temporal Convergence`

   https://www.grc.nasa.gov/www/wind/valid/tutorial/tempconv.html

These references support methodological discipline.

Their inclusion does not claim formal compliance with an external standard.

Accessed for Phase 13A design on 2026-07-14.

---

## 39. Phase 13A decision

Phase 13A authorizes only the design of a future numerical-convergence study.

It does not authorize:

- solver execution;
- a formal refinement run;
- source-code modification;
- enabling `SelectableAdvectionSolver.run()`;
- a convergence claim;
- an observed-order claim;
- an asymptotic-range claim;
- a numerical-uncertainty claim;
- a turbulence claim;
- a cascade claim;
- a `k^-3` claim;
- a method-superiority claim;
- a production-readiness claim.

Recommended next phase:

**Phase 13B — Benchmark and Continuous-Equation Specification**
