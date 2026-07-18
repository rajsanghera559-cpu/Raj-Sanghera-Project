# Phase 13G.2 — Exploratory Isolation-Calibration Design and Authorization

## 0. Document control

- Project: Raj-Sanghera-Project
- Phase: Phase 13G — Formal Pre-registration Freeze
- Subphase: Phase 13G.2 — Exploratory Isolation-Calibration Design and Authorization
- Starting branch: `phase4_validation`
- Starting commit: `22b0bd741d46f2d09eb002cdfcde4afb9cde8f64`
- Starting annotated tag: `v0.5.58-phase13G1-calibration-gap-review`
- Phase 13G.1 decision: `PASS-HOLD`
- Document status: design-and-authorization candidate
- Numerical execution authorized by this document: no
- Runner implementation authorized after archive: one file only
- Formal pre-registration frozen: no
- Phase 13H authorized: no

This document freezes a bounded exploratory calibration plan. It does not run
that plan and does not convert exploratory data into formal evidence.

---

## 1. Purpose

Phase 13G.1 established that the successful Phase 13F pilot used only one grid,
one timestep, one viscosity, and one short final time. It therefore could not
calibrate spatial or temporal isolation, a useful refinement range, or a
numerical-floor decision rule.

Phase 13G.2 closes the design gap by prospectively fixing:

- an exploratory spatial family;
- an exploratory timestep family;
- fixed continuous parameters;
- exact error quantities;
- contamination observations;
- numerical-floor observations;
- execution and storage ceilings;
- failure and non-claim boundaries.

---

## 2. Authorization boundary

After this design is independently audited, committed, annotated-tagged,
pushed, and remotely verified, a later Phase 13G.2 implementation gate may
create only:

`run_phase13G_isolation_calibration.py`

That implementation gate must remain non-executing and must end with a static
audit, committed script hash, annotated tag, remote verification, and clean
working tree.

Numerical execution requires a separate Phase 13G.3 runtime authorization.

This design does not authorize:

- importing a project solver during the design gate;
- constructing a solver;
- executing an operator or timestep;
- creating numerical result directories;
- modifying protected solver or verification modules;
- changing Phase 13F evidence;
- calculating observed order;
- fitting an error-decay model;
- freezing formal Phase 13H thresholds;
- running Phase 13H.

---

## 3. Frozen evidence basis

| Evidence | Committed SHA-256 |
|---|---|
| Phase 13A claim design | `6A1DCB87E3E5C4C468C4C804E6059B98864AC84263E44D1342E655CCE7E024CC` |
| Phase 13B benchmark specification | `6FC0685AC0225F542C181174ECC5940CE1C1163F2CE90B15301AEF46D5CE7875` |
| Phase 13C reference/source audit | `ABEF31DF4F67913EB418C816DBB665531C5F2C854EB4E300B68CF9F45CA5A306` |
| Phase 13D harness design | `2F014D33623C5D7184F65EBF4E3CA34F4BAD13501BED0A66DC72D33FB1A90A5E` |
| Phase 13G.1 calibration-gap review | `170258780D8EDA00E5E3FA08351C9E203F5E27BEAE92C5D0C00D0CF777689028` |

Phase 13E, Phase 13F, and the archived verification modules remain protected
inputs whose committed hashes must be pinned by the future runner.

---

## 4. Calibration classification

Every Phase 13G.3 numerical result is exploratory calibration evidence.

It may be used only to select the later Phase 13G.4 pre-registration values.

It must not be combined with Phase 13H formal data in one reported formal
sequence. A Phase 13G.3 case may be repeated formally only as a new Phase 13H
case under the frozen Phase 13G.4 registration.

---

## 5. Frozen continuous configuration

The exploratory matrix uses:

- domain: `L = 2*pi`;
- initial time: `t_0 = 0.0`;
- Reynolds parameter: `Re = 1000`;
- viscosity: `nu = 0.001`;
- requested evolution final time: `T = 0.008`;
- floating arithmetic: `float64`;
- product dealiasing: `false`;
- post-step mask: `POST_STEP_STRICT_COORDINATE_TWO_THIRDS_ONCE_V1`;
- constructor steps: `0`;
- inherited forcing: prohibited;
- Track M source: `M_ANALYTIC_SOURCE_REPLACES_BASELINE_V1`;
- Track L source: zero;
- exact references: native-grid analytic evaluation;
- selectable methods: `fd_centered`, `pseudo_spectral`, and `arakawa`.

The final time `0.008` is exploratory. It is selected because every declared
timestep divides it exactly and the temporal ladder contains between two and
sixteen steps. It is not frozen for Phase 13H.

---

## 6. Benchmark roles

| Track | Role in calibration | Time evolution |
|---|---|---:|
| O1 | resolved-mode correctness and near-floor observation | no |
| O2 | broad-spectrum spatial operator behavior | no |
| L | isolated diffusion/RK2 temporal behavior | yes |
| M | full nonlinear manufactured evolution and competing-error isolation | yes |

Track S is excluded because exact native-grid references are available for all
required calibration questions.

---

## 7. O1 operator matrix

For each of the three selectable methods, execute O1 at:

`N = 16, 32, 64`

Fixed operator-case values:

- `dt = 0.001` as metadata only;
- steps: `0`;
- final time: `0.0`;
- cases: `3 grids * 3 methods = 9`.

O1 is not used for a rate fit. Its purpose is to record whether resolved-mode
errors remain near ordinary floating-point scale across the declared grids.

---

## 8. O2 operator matrix

For each of the three selectable methods, execute O2 at:

`N = 16, 32, 64, 128, 256`

Fixed operator-case values:

- compatibility policy: `O2_DISCRETE_MEAN_SUBTRACTION_V1`;
- record the removed native-grid mean;
- `dt = 0.001` as metadata only;
- steps: `0`;
- final time: `0.0`;
- cases: `5 grids * 3 methods = 15`.

No algebraic, spectral, or exponential model is fitted in Phase 13G.3.

---

## 9. Track L temporal-isolation matrix

Primary temporal ladder at `N = 64`:

| `dt` | Steps | Final time |
|---:|---:|---:|
| `0.004` | 2 | `0.008` |
| `0.002` | 4 | `0.008` |
| `0.001` | 8 | `0.008` |
| `0.0005` | 16 | `0.008` |

One spatial companion uses:

- `N = 32`;
- `dt = 0.0005`;
- steps: `16`;
- final time: `0.008`.

Track L cases: `5`.

The companion is used only to measure whether the finest-step Track L error
changes across two grids. It does not establish spatial convergence.

---

## 10. Track M spatial-isolation matrix

For every selectable method, execute the Cartesian product:

- grids: `N = 16, 32, 64, 128, 256`;
- timesteps: `dt = 0.0005, 0.00025`;
- final time: `0.008`;
- corresponding steps: `16, 32`.

Cases:

`5 grids * 2 timesteps * 3 methods = 30`

The two timesteps permit direct observation of temporal sensitivity at every
grid while holding the continuous problem fixed.

---

## 11. Track M temporal-isolation matrix

For every selectable method, execute the Cartesian product:

- grids: `N = 128, 256`;
- timesteps: `dt = 0.004, 0.002, 0.001, 0.0005`;
- final time: `0.008`;
- corresponding steps: `2, 4, 8, 16`.

This matrix contains 24 configurations. Six `dt = 0.0005` configurations are
already present in Section 10 and must be executed only once.

Additional temporal configurations: `18`.

Unique Track M cases across Sections 10 and 11: `48`.

---

## 12. Exact case and operation ceilings

| Component | Unique cases | External RK2 steps |
|---|---:|---:|
| O1 | 9 | 0 |
| O2 | 15 | 0 |
| Track L | 5 | 46 |
| Track M | 48 | 804 |
| **Total** | **77** | **850** |

Expected aggregate guarded calls:

- advection calls: `1632`;
- spectral-diffusion calls: `1700`;
- Track M source evaluations: `1608`;
- inherited forcing calls: `0`;
- post-step mask applications: `850`.

No configuration outside this inventory may execute.

---

## 13. Primary and secondary error quantities

For O1 and O2:

`e_adv = computed_advection - exact_advection`

For Track L and Track M:

`e_omega = numerical_vorticity - exact_vorticity`

The primary exploratory scalar is:

`E = L2_rms(e)`

Required secondary quantities:

- `L1_mean`;
- `Linf`;
- exact-field `L2_rms`;
- numerical-field `L2_rms`;
- relative `L2` when the denominator is finite and positive;
- O2 removed discrete mean;
- pre-mask and post-mask norms for evolution steps;
- maximum imaginary reconstruction residue;
- exact final-time alignment.

All exact comparisons occur on the native grid. Fourier restriction is not
part of the primary calibration metric.

---

## 14. Predeclared spatial-isolation observations

For each Track M method, grid `N > 16`, and spatial timestep `dt`, record:

`Delta_h(N, dt) = abs(E(N/2, dt) - E(N, dt))`

For each method and grid, record temporal sensitivity:

`Delta_t(N) = abs(E(N, 0.0005) - E(N, 0.00025))`

When `Delta_h(N, 0.0005)` is finite and nonzero, record:

`C_t(N) = Delta_t(N) / Delta_h(N, 0.0005)`

If the denominator is zero, nonfinite, or unavailable, record `null` and a
reason code. Phase 13G.3 must report these values without a pass threshold.

---

## 15. Predeclared temporal-isolation observations

For each Track M method and temporal timestep, record:

`Delta_N(dt) = abs(E(128, dt) - E(256, dt))`

For adjacent temporal levels at `N = 256`, record:

`Delta_dt(dt) = abs(E(256, dt) - E(256, dt/2))`

When `Delta_dt(dt)` is finite and nonzero, record:

`C_h(dt) = Delta_N(dt) / Delta_dt(dt)`

Track L must analogously record adjacent timestep error differences at `N=64`
and the `N=32` versus `N=64` difference at `dt=0.0005`.

No observed-order logarithm is calculated in Phase 13G.3.

---

## 16. Numerical-floor observations

For every case, record:

- machine epsilon `eps`;
- characteristic scale `S = max(1, exact_L2_rms)`;
- arithmetic reference `F_eps = eps*S`;
- scaled error `R_eps = E/F_eps` when defined;
- adjacent error ratio `max(E_coarse,E_fine)/min(E_coarse,E_fine)` when both
  values are finite and positive;
- whether either error is exactly zero;
- adjacent direction: decrease when `E_fine < E_coarse`, equal when the values
  are exactly equal, and increase when `E_fine > E_coarse`;
- provisional floor-like flag: `R_eps <= 1e4`;
- provisional plateau-like flag: adjacent positive-error ratio `<= 2`.

These are observations, not the formal Phase 13H error floor. Phase 13G.4 must
freeze the absolute floor, relative floor, plateau rule, and excluded-pair rule
before formal execution.

The `1e4` and factor-of-two flags are calibration labels only. They must not be
copied into Phase 13G.4 automatically; the formal rules require a separate
documented decision using the complete exploratory dataset.

---

## 17. Exploratory classification vocabulary

Phase 13G.3 may use only:

- `DECREASE OBSERVED`;
- `EQUAL OBSERVED`;
- `INCREASE OBSERVED`;
- `PLATEAU-LIKE OBSERVATION`;
- `IRREGULAR`;
- `FLOOR-LIKE OBSERVATION`;
- `ISOLATION METRIC AVAILABLE`;
- `ISOLATION METRIC UNAVAILABLE`;
- `CALIBRATION COMPLETE`;
- `CALIBRATION INCOMPLETE`.

The words `converged`, `order`, `asymptotic`, `superior`, and `validated` must
not appear as numerical conclusions.

---

## 18. No numerical-value early stopping

The full 77-case matrix must execute unless a safety, integrity, configuration,
resource, or nonfinite-field failure occurs.

Error magnitude, apparent monotonicity, a favorable trend, or an unfavorable
trend must not stop or expand the matrix.

No extra grid, timestep, method, viscosity, or final time may be added after
results are viewed.

---

## 19. Fail-closed stopping rules

Stop before the next case if any of the following occurs:

- repository identity or pinned hash mismatch;
- dirty working tree at preflight;
- authorization token mismatch;
- unapproved case configuration;
- protected source mutation;
- solver-state or input mutation;
- prohibited solver-interface call;
- inherited forcing call;
- source-stage time mismatch;
- mask-count mismatch;
- final-time misalignment;
- nonfinite field, error, or required diagnostic;
- atomic-writer failure;
- output schema rejection;
- output inventory mismatch;
- resource exception or user interruption.

All completed case files and the failure record must be preserved. A failed or
interrupted run must not be silently deleted or treated as absent.

---

## 20. Runner implementation boundary

The future runner must:

- be external to protected solver modules;
- use the audited Phase 13 exact-reference, harness, and output-schema paths;
- retain `SelectableAdvectionSolver.run()` as disabled and uncalled;
- construct solvers with `steps=0`;
- execute only audited external operator and RK2 pathways;
- enforce the exact 77-case set before solver construction;
- reject duplicates and unauthorized configurations;
- use an explicit `main()` boundary;
- use isolated mode and suppress bytecode during authorized execution;
- use a unique run identifier and refuse overwrite;
- clear the authorization environment variable after execution.

No project module may be imported during the design or static-audit gate.

---

## 21. Authorization token

The future Phase 13G.3 execution must require the exact environment variable:

`PHASE13G_EXECUTE_AUTHORIZED_ISOLATION_CALIBRATION_V1`

with the exact value:

`PHASE13G_EXECUTE_AUTHORIZED_ISOLATION_CALIBRATION_V1`

Absence, misspelling, wrong value, or an additional Phase 13 authorization
variable must fail before project import or output creation.

This document does not authorize setting that variable yet.

---

## 22. Output directory and files

The future run directory pattern is:

`experiments/verification/phase13/phase13G_calibration_<UTC>_<commit7>/`

Every case directory must contain exactly the existing five Phase 13 case
files:

1. `case_metadata.json`;
2. `checks.json`;
3. `error_summary.csv`;
4. `field_manifest.json`;
5. `fields.npz`.

The run root must contain exactly:

1. `calibration_plan.json`;
2. `run_manifest.json`;
3. `calibration_case_summary.csv`;
4. `calibration_isolation_metrics.csv`;
5. `calibration_floor_observations.csv`.

Persistent file ceiling:

`77*5 + 5 = 390 files`

No plot, temporary file, cache, bytecode file, fitted model, observed-order
table, or convergence report may be created.

---

## 23. Required root summaries

`calibration_plan.json` must contain the complete frozen 77-case inventory and
aggregate expected counts before execution.

`calibration_case_summary.csv` must contain one row per unique case and all
primary/secondary error quantities.

`calibration_isolation_metrics.csv` must contain every predeclared `Delta_h`,
`Delta_t`, `C_t`, `Delta_N`, `Delta_dt`, and `C_h` value or an explicit null
reason.

`calibration_floor_observations.csv` must contain `eps`, `S`, `F_eps`, `E`,
`R_eps`, adjacent ratios, zero flags, and exploratory classifications.

The run manifest must hash every persistent file other than itself and must be
written last. A separate post-write inventory hash must cover all 390 files.

---

## 24. Independent audit requirements

Before interpretation, an independent read-only audit must verify:

- authorized commit and annotated tag;
- runner and pinned module hashes;
- exact 77-case identity with no duplicate or missing configuration;
- exact 850-step total;
- exact call, source, forcing, and mask counts;
- all metadata and final-time identities;
- every file size and SHA-256;
- every NPZ array against its field manifest;
- exact physical/Git-ignored inventory equality;
- exact 390-file ceiling;
- all predeclared summary rows and null reasons;
- no observed-order or fitted-model output;
- clean visible Git status;
- no audit mutation, solver execution, or project import.

---

## 25. Acceptance logic

The Phase 13G.3 execution may report `CALIBRATION EXECUTION PASS` only if:

- every preflight and fail-closed test passes;
- all 77 authorized cases complete;
- all required fields and diagnostics are finite;
- exact call counts match;
- forcing calls equal zero;
- all 390 files are complete and hash-valid;
- the independent audit passes.

This PASS means only that the calibration dataset is complete and auditable.

No error decrease or isolation metric is required for execution PASS. Numerical
behavior informs Phase 13G.4 design; it does not retroactively change Phase
13G.3 execution acceptance.

---

## 26. Failure interpretation

A `CALIBRATION INCOMPLETE` result does not automatically identify a production
solver defect. The failure must first be localized to configuration, reference,
harness, source, solver boundary, output, environment, or resource handling.

No protected source may be changed inside the failed run. Corrective work
requires a separately documented incident/remediation gate.

---

## 27. Phase 13G.4 handoff requirements

Phase 13G.4 may begin only after the complete exploratory dataset and its
independent audit are archived.

Phase 13G.4 must then freeze, without formal execution:

- selected benchmarks and methods;
- formal spatial and temporal levels;
- formal viscosity and final time;
- primary norm and secondary quantities;
- numerical-floor and plateau rules;
- temporal- and spatial-isolation thresholds;
- order-stability and asymptotic-range rules;
- pseudo-spectral model-selection rule;
- formal analysis script hash;
- allowed, downgrade, inconclusive, and failure wording.

If calibration evidence is insufficient, Phase 13G.4 must narrow the formal
claim or stop. It must not invent thresholds from desired conclusions.

---

## 28. Explicit non-claims

Phase 13G.2 establishes no:

- spatial or temporal convergence;
- observed order;
- asymptotic range;
- numerical uncertainty;
- solver-wide verification;
- method equivalence or superiority;
- physical validation;
- turbulence;
- inertial range;
- cascade;
- `k^-3` law;
- production readiness.

---

## 29. Completion criteria

Phase 13G.2 design passes only when:

- the Phase 13G.1 archive checkpoint is exact and clean;
- this document is the only new file;
- its evidence hashes and arithmetic are independently audited;
- the unique case count is exactly `77`;
- the RK2-step ceiling is exactly `850`;
- the persistent-file ceiling is exactly `390`;
- spatial and temporal observations are separated;
- no numerical execution occurs;
- no project module is imported;
- no protected source changes;
- no formal threshold or claim is frozen;
- the document is committed, annotated-tagged, pushed, and remotely verified.

---

## 30. Decision

> PASS — Phase 13G.2 exploratory isolation-calibration design is complete as a
> design candidate. After controlled archival, it authorizes only a separate,
> non-executing implementation and static-audit gate for
> `run_phase13G_isolation_calibration.py`.

Phase 13G.3 numerical execution and Phase 13H formal refinement remain
unauthorized.
