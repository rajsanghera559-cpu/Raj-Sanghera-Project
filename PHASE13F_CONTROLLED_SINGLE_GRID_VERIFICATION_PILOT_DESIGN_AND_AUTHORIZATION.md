# Phase 13F — Controlled Single-Grid Verification Pilot Design and Authorization



## 0. Document control



- Project: Raj-Sanghera-Project

- Phase: 13F

- Phase title:

&#x20; Controlled Single-Grid Verification Pilot Design and Authorization

- Design file:

&#x20; `PHASE13F_CONTROLLED_SINGLE_GRID_VERIFICATION_PILOT_DESIGN_AND_AUTHORIZATION.md`

- Active branch:

&#x20; `phase4_validation`

- Starting checkpoint:

&#x20; `v0.5.52-phase13E-complete-implementation-and-static-audit`

- Starting commit:

&#x20; `4a13be163c5c1eeaaf7251e7dd5b9ef08e3d062e`

- Starting repository state:

&#x20; clean

- Design status:

&#x20; design-only candidate

- Pilot runner created:

&#x20; no

- Verification modules imported:

&#x20; no

- Solver constructed:

&#x20; no

- Solver method executed:

&#x20; no

- Numerical operator evaluated:

&#x20; no

- External RHS evaluated:

&#x20; no

- RK2 step executed:

&#x20; no

- Result directory created:

&#x20; no

- Refinement sequence authorized:

&#x20; no

- Convergence claim authorized:

&#x20; no

- Physical-validation claim authorized:

&#x20; no



---



## 1. Executive authorization decision



Phase 13F defines the first controlled runtime boundary for the Phase 13

verification harness.



This document authorizes a later, separately gated implementation of:



1\. one controlled pilot runner;

2\. non-solver fail-closed runtime tests;

3\. module-import smoke tests;

4\. exact-reference runtime smoke tests;

5\. guarded solver-construction smoke tests;

6\. a single-grid numerical pilot at `N = 16`;

7\. no more than two external RK2 steps per evolution case;

8\. deterministic result writing through the Phase 13 output schema;

9\. a post-run integrity audit;

10\. a Phase 13F completion report.



This document does not itself authorize immediate numerical execution.



The design must first be:



- saved;

- statically inspected;

- source-hash pinned;

- committed;

- annotated with a Git tag;

- pushed to the remote;

- verified against the remote.



After that archive, a separate Phase 13F runner-implementation gate is required.



No numerical command may be executed merely because this design file exists.



---



## 2. Phase objective



The objective of Phase 13F is to determine whether the dormant Phase 13

verification modules can operate together within a tightly limited runtime

boundary.



The pilot is intended to test:



- module importability;

- exact-reference evaluation;

- solver construction;

- solver-grid agreement;

- solver-mask agreement;

- guarded advection calls;

- guarded spectral-diffusion calls;

- input-mutation detection;

- solver-state-mutation detection;

- shared-memory detection;

- Track L forcing exclusion;

- Track M baseline-forcing replacement;

- Track M source-stage timing;

- external RK2 staging;

- exactly one post-step mask per completed step;

- final-time alignment;

- finite error calculation;

- metadata validation;

- array-manifest construction;

- atomic result writing;

- file-hash recording;

- fail-closed behavior.



The pilot is not a formal refinement study.



---



## 3. Inherited checkpoint



Phase 13F inherits the completed Phase 13E implementation checkpoint:



- commit:

&#x20; `4a13be163c5c1eeaaf7251e7dd5b9ef08e3d062e`

- annotated tag:

&#x20; `v0.5.52-phase13E-complete-implementation-and-static-audit`



Phase 13E established:



- three verification modules exist;

- their syntax is valid;

- their static interfaces agree;

- their benchmark identifiers agree;

- their policy identifiers agree;

- their case-identifier grammar agrees;

- their error and array contracts agree;

- protected solver source remained unchanged;

- no runtime numerical operation had occurred.



Phase 13E did not establish runtime correctness.



---



## 4. Inherited document hashes



The following document hashes are frozen for Phase 13F.



| Document | SHA-256 |

|---|---|

| `PHASE13B_BENCHMARK_AND_CONTINUOUS_EQUATION_SPECIFICATION.md` | `6FC0685AC0225F542C181174ECC5940CE1C1163F2CE90B15301AEF46D5CE7875` |

| `PHASE13C_REFERENCE_SOLUTION_AND_SOURCE_TERM_AUDIT_REPORT.md` | `ABEF31DF4F67913EB418C816DBB665531C5F2C854EB4E300B68CF9F45CA5A306` |

| `PHASE13D_EXTERNAL_VERIFICATION_HARNESS_DESIGN.md` | `2F014D33623C5D7184F65EBF4E3CA34F4BAD13501BED0A66DC72D33FB1A90A5E` |

| `PHASE13E_EXTERNAL_VERIFICATION_HARNESS_IMPLEMENTATION_AND_STATIC_INTERFACE_AUDIT_REPORT.md` | `35B84F64CB089E8B0AF5525709EFEDEE3447D92AE9BDA8059C9EC7B29CB7247D` |



A mismatch is a hard stop.



---



## 5. Protected production-source hashes



The following production solver files remain protected.



| Protected file | SHA-256 |

|---|---|

| `project/solver/spectral_solver.py` | `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1` |

| `project/solver/selectable_advection_solver.py` | `5EDA93A2E9358D81927BD9EE247F305E6DBC94367B351801913FFEAA2D7C5891` |

| `project/solver/advection_operators.py` | `2C86465570DDF095D5B0A9B7F67E6E78A89D14F82933FA983D91156DD0F76409` |



Phase 13F does not authorize modifications to these files.



A mismatch is a hard stop before imports or execution.



---



## 6. Verification-module hashes



The following Phase 13 verification-module hashes are frozen.



| Verification module | SHA-256 |

|---|---|

| `project/verification/phase13_exact_references.py` | `6904C78E54948D07C92173C8B313844B28C92209B4F61CE447FFC29E15DA4EED` |

| `project/verification/phase13_external_harness.py` | `CDB6DBC249EA2DFF27E729AF0CF3D5C545C48BE57624CC59842B3222DAA752A2` |

| `project/verification/phase13_output_schema.py` | `6899C611C56E8154435BB6C042B520A13B466CD10042DE5325C7F9EF634FB11F` |



Phase 13F does not authorize modifications to these files.



A mismatch is a hard stop.



---



## 7. Phase subdivision



Phase 13F is divided into controlled subphases.



### Phase 13F.1



Design and authorization.



Authorized artifact:



`PHASE13F_CONTROLLED_SINGLE_GRID_VERIFICATION_PILOT_DESIGN_AND_AUTHORIZATION.md`



Numerical execution:



none.



### Phase 13F.2



Pilot-runner implementation and static audit.



Proposed runner:



`run_phase13F_verification_pilot.py`



Numerical execution:



none.



### Phase 13F.3



Fail-closed runtime smoke tests.



Permitted:



- module imports;

- exact-reference evaluations;

- in-memory test doubles;

- temporary-directory output-schema tests;

- guarded solver construction at `N = 16`.



Numerical pilot cases:



none until all Phase 13F.3 tests pass.



### Phase 13F.4



Controlled single-grid numerical pilot.



Permitted:



- six operator cases;

- one Track L case;

- three Track M cases;

- eight total external RK2 steps;

- one controlled result directory.



### Phase 13F.5



Post-run result and integrity audit.



New numerical execution:



none.



### Phase 13F.6



Completion report and archive.



New numerical execution:



none.



---



## 8. Authorized future runner



The only runner authorized for later creation is:



`run_phase13F_verification_pilot.py`



No alternative runner name is authorized.



The runner must:



- be separate from production solver source;

- import the Phase 13 verification modules;

- perform independent preflight gates;

- fail closed;

- execute only the frozen pilot matrix;

- write only through the Phase 13 output-schema module;

- create no plots;

- perform no rate fitting;

- calculate no observed order;

- launch no subprocess other than read-only Git identity commands;

- use no network interface;

- accept no arbitrary Python expression;

- use no `eval`;

- use no `exec`;

- use no shell command string;

- use no `shell=True`;

- perform no package installation;

- perform no Git write operation;

- perform no Git commit, tag, or push operation;

- perform no source modification.



The runner must not be created in the same commit as this design document.



---



## 9. Authorized imports



The future runner may import:



- Python standard-library modules;

- NumPy;

- `project.verification.phase13_exact_references`;

- `project.verification.phase13_external_harness`;

- `project.verification.phase13_output_schema`.



The runner may indirectly import:



- `SelectableAdvectionSolver`;

- its protected baseline solver dependencies;

- the protected advection operators.



The runner must not directly import or call an alternative solver pathway.



The runner must not import plotting libraries.



The runner must not import optimization, curve-fitting, regression, or

observed-order packages.



---



## 10. Read-only Git identity boundary



The future runner may use `subprocess.run()` only for the following read-only

Git commands:



- `git rev-parse HEAD`;

- `git branch --show-current`;

- `git status --porcelain=v1 --untracked-files=all`;

- `git tag --points-at HEAD`.



Requirements:



- command arguments must be passed as a list;

- `shell=False`;

- `check=True`;

- text mode enabled;

- output captured;

- no user-controlled executable name;

- no Git write command;

- no checkout;

- no reset;

- no clean;

- no add;

- no commit;

- no tag creation;

- no push.



The active runner checkpoint must be clean and explicitly authorized by a later

execution gate.



---



## 11. Repository preflight gate



Before importing a project module, the execution wrapper and runner must verify:



- repository path is the expected repository;

- branch is `phase4_validation`;

- HEAD is the later authorized Phase 13F runner checkpoint;

- the authorized annotated tag points to HEAD;

- the repository is clean;

- no merge, rebase, cherry-pick, or revert is active;

- all inherited document hashes match;

- all protected solver hashes match;

- all verification-module hashes match;

- the Phase 13F runner hash matches its archived value;

- the Phase 13F design hash matches its archived value;

- no unexpected file exists under `project/verification`;

- no pre-existing output directory uses the selected run identifier.



A failure stops before project imports.



---



## 12. Frozen benchmark identifiers



The pilot may use only:



- `O1_BANDLIMITED_TWO_MODE_V1`;

- `O2_ANALYTIC_BROAD_SPECTRUM_V1`;

- `L_EQUAL_EIGENVALUE_DECAY_V1`;

- `M_TWO_RATE_NONLINEAR_MMS_V1`.



Identifier matching is exact and case-sensitive.



Aliases are prohibited.



---



## 13. Frozen selectable methods



The pilot may use only:



1\. `fd_centered`;

2\. `pseudo_spectral`;

3\. `arakawa`.



No method may substitute for another.



No method result may be reused as another method’s result.



No averaging across methods is authorized.



No method-superiority comparison is authorized.



---



## 14. Fixed numerical configuration



Every pilot case uses:



- grid:

&#x20; `N = 16`

- domain:

&#x20; `L = 2*pi`

- Reynolds parameter:

&#x20; `Re = 1000`

- viscosity:

&#x20; `nu = 0.001`

- timestep field:

&#x20; `dt = 0.001`

- initial time:

&#x20; `t_0 = 0.0`

- product dealiasing:

&#x20; `false`

- constructor steps:

&#x20; `0`

- floating dtype:

&#x20; `float64`



No other grid size is authorized.



No other Reynolds number is authorized.



No other timestep is authorized.



No second numerical configuration is authorized.



---



## 15. Operator-case configuration



For O1 and O2:



- `N = 16`;

- `Re = 1000`;

- `dt = 0.001`;

- `n_steps = 0`;

- `t_0 = 0.0`;

- `t_final_requested = 0.0`;

- one case per selectable method;

- no post-step mask;

- no external time step;

- no inherited forcing;

- exactly one guarded `compute_advection()` call per case.



Each operator case must evaluate the exact reference directly at `t = 0`.



---



## 16. Track L configuration



Track L uses:



- benchmark:

&#x20; `L_EQUAL_EIGENVALUE_DECAY_V1`

- `N = 16`;

- `Re = 1000`;

- `nu = 0.001`;

- `dt = 0.001`;

- `n_steps = 2`;

- `t_0 = 0.0`;

- `t_final_requested = 0.002`;

- primary advection method:

&#x20; `None`;

- constructor default method:

&#x20; `fd_centered`, unused and recorded;

- external RHS:

&#x20; `solver.laplacian_spectral(w)`;

- source:

&#x20; exactly zero;

- inherited forcing:

&#x20; prohibited;

- post-step mask:

&#x20; exactly once per completed step.



Track L is executed once, not once per selectable advection method.



---



## 17. Track M configuration



Track M uses:



- benchmark:

&#x20; `M_TWO_RATE_NONLINEAR_MMS_V1`

- `N = 16`;

- `Re = 1000`;

- `nu = 0.001`;

- `dt = 0.001`;

- `n_steps = 2`;

- `t_0 = 0.0`;

- `t_final_requested = 0.002`;

- one case for each selectable method;

- external source-aware RHS;

- inherited forcing:

&#x20; prohibited;

- post-step mask:

&#x20; exactly once per completed step.



The external Track M RHS is:



`-compute_advection(w) + laplacian_spectral(w) + exact_source_M(t)`



The analytic source replaces baseline forcing.



It does not supplement baseline forcing.



---



## 18. Exact pilot matrix



The authorized pilot contains exactly ten numerical cases.



| Case group | Benchmark | Method | Steps | Number of cases |

|---|---|---:|---:|---:|

| O1 operator | O1 | `fd_centered` | 0 | 1 |

| O1 operator | O1 | `pseudo_spectral` | 0 | 1 |

| O1 operator | O1 | `arakawa` | 0 | 1 |

| O2 operator | O2 | `fd_centered` | 0 | 1 |

| O2 operator | O2 | `pseudo_spectral` | 0 | 1 |

| O2 operator | O2 | `arakawa` | 0 | 1 |

| Track L | L | `None` | 2 | 1 |

| Track M | M | `fd_centered` | 2 | 1 |

| Track M | M | `pseudo_spectral` | 2 | 1 |

| Track M | M | `arakawa` | 2 | 1 |



No eleventh case is authorized.



---



## 19. Deterministic case identifiers



The case-identifier grammar is:



`<benchmark_id>__N<N>__Re<Re>__dt<dt>__steps<n_steps>__t0<t_0>__method_<method>`



The ten expected case identifiers are:



1\. `O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_fd_centered`

2\. `O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_pseudo_spectral`

3\. `O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_arakawa`

4\. `O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_fd_centered`

5\. `O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_pseudo_spectral`

6\. `O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_arakawa`

7\. `L_EQUAL_EIGENVALUE_DECAY_V1__N16__Re1000__dt0.001__steps2__t00__method_none`

8\. `M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_fd_centered`

9\. `M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_pseudo_spectral`

10\. `M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_arakawa`



The unusual `__t00` token is the frozen result of:



- literal token:

&#x20; `__t0`

- formatted value:

&#x20; `0`



It must not be manually corrected or renamed.



---



## 20. Expected solver-call counts



The runner must record and audit call counts.



### Per O1 or O2 operator case



- `compute_advection`:

&#x20; `1`

- `laplacian_spectral`:

&#x20; `0`

- inherited forcing:

&#x20; `0`

- post-step masks:

&#x20; `0`



### Track L case



Two external RK2 steps produce:



- RK2 stages:

&#x20; `4`

- `compute_advection`:

&#x20; `0`

- `laplacian_spectral`:

&#x20; `4`

- inherited forcing:

&#x20; `0`

- post-step masks:

&#x20; `2`



### Each Track M case



Two external RK2 steps produce:



- RK2 stages:

&#x20; `4`

- `compute_advection`:

&#x20; `4`

- `laplacian_spectral`:

&#x20; `4`

- analytic source evaluations:

&#x20; `4`

- inherited forcing:

&#x20; `0`

- post-step masks:

&#x20; `2`



### Entire numerical pilot



Expected totals:



- numerical cases:

&#x20; `10`

- operator-only cases:

&#x20; `6`

- evolution cases:

&#x20; `4`

- external RK2 steps:

&#x20; `8`

- external RK2 stages:

&#x20; `16`

- guarded advection calls:

&#x20; `18`

- guarded spectral-diffusion calls:

&#x20; `16`

- Track M analytic source evaluations:

&#x20; `12`

- inherited forcing calls:

&#x20; `0`

- post-step mask applications:

&#x20; `8`



A count mismatch is a hard failure.



---



## 21. Solver scaffold policy



`SpectralSolver` creates its declared `run_path`.



The pilot must not place solver scaffold directories inside a case-output

directory.



The runner must use a temporary system directory.



Each solver scaffold path must:



- be case-specific;

- end with:

&#x20; `_solver_scaffold`;

- be recorded in metadata;

- remain outside the repository;

- contain no numerical result files generated by the Phase 13 runner;

- be removed after the case or after the full run.



The runner must verify that cleanup succeeded.



Failure to remove a temporary scaffold prevents a full PASS.



---



## 22. Result-root policy



The only authorized persistent result root is:



`experiments/verification/phase13/<run_id>/`



The selected `<run_id>` must:



- be a safe path token;

- begin with:

&#x20; `phase13F_pilot_`;

- include a UTC timestamp;

- include the short authorized execution commit;

- contain no slash;

- contain no backslash;

- contain no whitespace.



Example form:



`phase13F_pilot_20260715T120000Z_abcdef1`



The actual timestamp and short commit are determined at execution.



Only one new run directory is authorized.



---



## 23. Result-directory structure



The authorized run directory contains:



- `run_manifest.json`;

- exactly ten case directories.



Each case directory contains:



- `case_metadata.json`;

- `checks.json`;

- `error_summary.csv`;

- `fields.npz`;

- `field_manifest.json`.



Expected persistent output count:



- ten case directories;

- five files per case;

- fifty case files;

- one run manifest;

- fifty-one persistent files total.



No plot is authorized.



No image file is authorized.



No additional CSV is authorized.



No free-form text log inside the result directory is authorized.



Console output is permitted.



---



## 24. Operator array bundles



Each O1 or O2 `fields.npz` contains exactly:



- `omega_raw`;

- `omega_input`;

- `computed_adv`;

- `exact_adv`;

- `error_adv`.



No evolution field belongs in an operator bundle.



---



## 25. Evolution array bundles



Each Track L or Track M `fields.npz` contains exactly:



- `initial_omega`;

- `numerical_omega`;

- `exact_omega`;

- `error_omega`.



Phase 13F does not require source-stage arrays in `fields.npz`.



Track M source-stage hashes and times must instead be recorded in:



- step records;

- checks;

- case metadata when supported by the frozen schema.



---



## 26. Error quantities



Every numerical case records:



- `L1_mean`;

- `L2_rms`;

- `Linf`;

- `exact_L2_rms`;

- `numerical_L2_rms`;

- `relative_L2`;

- `finite`.



Requirements:



- all primary quantities must be finite;

- all absolute norms must be nonnegative;

- relative L2 is null only when the exact denominator is not finite and strictly

&#x20; positive;

- no observed order is calculated;

- no fitted slope is calculated;

- no accuracy threshold is used to claim convergence.



The pilot may report error magnitudes.



It may not interpret a small error as formal convergence evidence.



---



## 27. Track M source-stage timing



For every Track M step:



- stage 1 time:

&#x20; `t_n`

- stage 2 time:

&#x20; `t_n + dt`

- stage 1 and stage 2 source hashes:

&#x20; required

- stage times:

&#x20; must differ

- source hash equality:

&#x20; not required because the analytic source is time-dependent



For the two-step pilot:



### Step 0



- stage 1:

&#x20; `0.000`

- stage 2:

&#x20; `0.001`

- next time:

&#x20; `0.001`



### Step 1



- stage 1:

&#x20; `0.001`

- stage 2:

&#x20; `0.002`

- next time:

&#x20; `0.002`



Using `t_n` for both stages is a hard failure.



---



## 28. Post-step mask policy



The post-step mask policy is:



`POST_STEP_STRICT_COORDINATE_TWO_THIRDS_ONCE_V1`



For each completed evolution step:



- construct the provisional RK2 result;

- transform the provisional field;

- multiply by the independently reconstructed mask;

- inverse transform;

- record maximum imaginary residue;

- take the real field;

- apply no additional mask.



For operator cases:



- mask count:

&#x20; `0`



For each two-step evolution case:



- mask count:

&#x20; `2`



Masking either RK2 stage is prohibited.



Masking the initial field is prohibited unless it is part of the frozen exact

input construction, which it is not.



---



## 29. Product-dealiasing policy



The selectable pseudo-spectral operator uses:



`dealias_product = False`



Phase 13F must record:



`product_dealiasing = false`



Changing this value defines a different numerical method.



No product-dealiasing claim is authorized.



---



## 30. Prohibited solver interfaces



The runner and harness call path must not use:



- `solver.forcing()`;

- `compute_rhs_selectable()`;

- `step_once_selectable()`;

- `run_selectable_diagnostic()`;

- `SelectableAdvectionSolver.run()`;

- `SpectralSolver.run()`.



A static occurrence inside protected source is not itself a pilot failure.



A call path from the Phase 13F runner is prohibited.



Any observed forcing call count above zero is a hard failure.



---



## 31. Runtime smoke-test sequence



Before numerical pilot cases, Phase 13F.3 must execute the following sequence.



### 31.1 Import smoke test



Import:



- exact-reference module;

- external-harness module;

- output-schema module.



Verify:



- import succeeds;

- no result directory is created;

- no solver scaffold is created;

- no numerical operation occurs during import;

- implementation contracts remain conservative.



### 31.2 Exact-reference smoke test



Using an independently constructed `N = 16` grid, evaluate each exact reference

once at:



- `t = 0.0`;

- `nu = 0.001`.



Verify:



- shape is `(16, 16)`;

- dtype is `float64`;

- all fields are finite;

- all fields are real;

- all arrays are read-only;

- arrays do not share memory;

- registry and track match;

- O2 mean policy matches;

- Track L advection is exactly zero;

- Track L source is exactly zero;

- Track M source exists.



These exact-reference evaluations are not numerical solver cases.



### 31.3 Configuration rejection tests



The following configurations must fail before solver execution:



- unknown benchmark identifier;

- lowercase or aliased benchmark identifier;

- unknown advection method;

- odd `N = 15`;

- disallowed pilot grid `N = 32`;

- `Re = 0`;

- negative Reynolds number;

- `dt = 0`;

- negative timestep;

- negative `n_steps`;

- evolution `n_steps = 0`;

- operator `n_steps = 1`;

- pilot evolution `n_steps = 3`;

- Track L with an advection method;

- O1 without an advection method;

- O2 without an advection method;

- Track M without an advection method;

- product dealiasing set to true;

- incorrect post-step policy;

- requested final time inconsistent with integer steps;

- scaffold path not ending in `_solver_scaffold`.



Every rejection must be caught and recorded.



### 31.4 Mutation-guard test doubles



Use in-memory test doubles, not the project solver, to verify detection of:



- input mutation;

- `solver.w` mutation;

- output sharing memory with the input;

- output sharing memory with `solver.w`.



A non-mutating independent-output test double must pass.



These tests must create no persistent output.



### 31.5 Output-schema rejection tests



The output schema must reject:



- missing repository metadata;

- missing environment metadata;

- missing benchmark metadata;

- missing numerical metadata;

- missing execution metadata;

- missing result metadata;

- invalid SHA-256;

- incomplete protected-solver hash set;

- inconsistent `nu` and `1/Re`;

- inconsistent `dx` and `L/N`;

- inconsistent final time;

- invalid case identifier;

- nonzero forcing count;

- incorrect mask count;

- passing case with a failure message;

- failed case without a failure message;

- nonfinite error quantity;

- missing required array;

- unexpected array;

- nonsquare array;

- complex array;

- nonfinite array;

- inconsistent array shape;

- unsafe run identifier;

- nonempty pre-existing case directory;

- pre-existing run manifest.



### 31.6 Atomic-writer temporary smoke test



Using a temporary directory outside the repository:



- write deterministic JSON;

- write one error-summary CSV;

- write one compressed NPZ;

- verify all files exist;

- verify hashes;

- verify JSON strictness;

- verify NPZ array names and values;

- verify no temporary `.tmp` file remains;

- delete the temporary directory;

- verify deletion.



This test is not a numerical pilot case.



---



## 32. Guarded solver-construction smoke test



After all non-solver tests pass, construct only `N = 16` guarded solvers.



Verify for each required method:



- class is `SelectableAdvectionSolver`;

- `N = 16`;

- square grid;

- `L = 2*pi`;

- `dx = L/N`;

- `Re = 1000`;

- `nu = 0.001`;

- `dt = 0.001`;

- constructor `steps = 0`;

- `solver.w` is zero;

- grid agrees with independent grid;

- mask agrees with independent mask;

- expected method is recorded;

- temporary scaffold path is recorded;

- no numerical result file exists in the scaffold;

- no production run method is called.



For Track L:



- constructor default method may be `fd_centered`;

- primary Track L method remains `None`;

- no advection method is called.



Solver construction is a runtime smoke test, not a simulation.



---



## 33. Operator pilot sequence



For each of the six operator cases:



1\. create validated configuration;

2\. validate Phase 13F pilot boundary;

3\. construct guarded solver;

4\. evaluate exact reference;

5\. copy and hash input field;

6\. call guarded advection exactly once;

7\. verify input unchanged;

8\. verify `solver.w` unchanged;

9\. verify output memory independence;

10\. calculate error field and norms;

11\. assemble checks and metadata;

12\. write the case bundle atomically;

13\. recompute output hashes;

14\. remove the temporary scaffold.



No diffusion call is needed.



No forcing call is permitted.



No mask is applied.



---



## 34. Track L pilot sequence



The Track L case must:



1\. construct a guarded solver with constructor steps zero;

2\. keep primary advection method as `None`;

3\. evaluate exact initial reference at `t = 0`;

4\. execute exactly two external RK2 steps;

5\. call only viscosity-weighted spectral diffusion in the RHS;

6\. evaluate no advection;

7\. evaluate no inherited forcing;

8\. apply exactly one mask after each completed step;

9\. reach exact final time `0.002`;

10\. evaluate exact final reference at `0.002`;

11\. calculate error field and norms;

12\. verify input and solver state remained unchanged;

13\. write one atomic case bundle;

14\. remove the temporary scaffold.



Track L must not be duplicated for three methods.



---



## 35. Track M pilot sequence



For each selectable method, the Track M case must:



1\. construct a guarded solver;

2\. evaluate exact initial reference at `t = 0`;

3\. execute exactly two external RK2 steps;

4\. evaluate advection at each RK2 stage;

5\. evaluate spectral diffusion at each RK2 stage;

6\. evaluate analytic source at each RK2 stage time;

7\. include no baseline forcing;

8\. apply exactly one post-step mask per completed step;

9\. record stage times;

10\. record stage source hashes;

11\. reach exact final time `0.002`;

12\. evaluate exact final reference at `0.002`;

13\. calculate error field and norms;

14\. verify mutation and memory guards;

15\. write one atomic case bundle;

16\. remove the temporary scaffold.



The three methods remain separate cases.



---



## 36. Case status policy



A case may receive:



- `PASS`;

- `FAIL`;

- `INCOMPLETE`.



`PASS` requires all frozen contract checks for that case.



`FAIL` requires at least one explicit failure message.



`INCOMPLETE` indicates that writing began but finalization did not complete.



An `INCOMPLETE` case is never interpreted as a passing case.



The pilot run receives `PASS` only if all ten cases receive `PASS`.



A single failed or incomplete case prevents a run-level PASS.



---



## 37. Fail-closed execution policy



The runner must stop before numerical cases when any preflight or smoke test

fails.



During numerical execution, the runner must stop on the first unhandled hard

failure.



The runner must not:



- continue and hide an error;

- replace a failed result with zeros;

- drop a failed method;

- rerun with changed parameters;

- silently reduce the step count;

- silently change the method;

- silently change the output path;

- silently alter a tolerance;

- silently delete evidence of an incomplete write;

- label partial output as PASS.



---



## 38. Required checks metadata



Each case `checks.json` must record at least:



- benchmark identifier;

- track;

- method;

- pilot-boundary validation;

- module-hash gate;

- protected-source hash gate;

- solver-grid agreement;

- solver-mask agreement;

- viscosity agreement;

- timestep agreement;

- constructor steps agreement;

- product-dealiasing status;

- source policy;

- forcing-call count;

- allowed method-call list;

- prohibited method-call list;

- input unchanged;

- solver state unchanged;

- output/input memory independence;

- output/solver-state memory independence;

- mask count;

- initial time;

- final time;

- final-time alignment;

- primary-error finiteness;

- case status.



Track M additionally records:



- every stage-1 source time;

- every stage-2 source time;

- every stage-1 source hash;

- every stage-2 source hash;

- stage-time distinction.



---



## 39. Repository metadata



Every case records:



- repository name;

- active branch;

- authorized execution commit;

- Git dirty status;

- Phase 13B specification hash;

- Phase 13C audit hash;

- Phase 13D design hash;

- Phase 13E completion-report hash;

- protected solver hashes;

- exact-reference module hash;

- harness module hash;

- output-schema module hash;

- runner hash;

- Phase 13F design hash.



The frozen output schema requires the Phase 13B, Phase 13C, solver, and module

hashes.



Additional Phase 13F provenance may be recorded in `checks.json` and the run

manifest where the existing schema permits it.



---



## 40. Environment metadata



Every case records:



- UTC timestamp;

- operating system;

- Python version;

- NumPy version;

- floating dtype;

- machine epsilon.



The runner must also print:



- executable path;

- current working directory;

- run identifier;

- authorized commit;

- case count.



No environment value is used as evidence of numerical convergence.



---



## 41. Post-run file audit



After writing all ten cases and the run manifest, the audit must verify:



- run directory exists;

- run manifest exists;

- exactly ten case directories exist;

- case directory names match the expected case identifiers;

- each case has exactly five expected files;

- no extra persistent file exists;

- every recorded SHA-256 matches the physical file;

- every JSON file parses;

- every CSV has the frozen columns;

- every NPZ contains the frozen array set;

- every field manifest matches its NPZ;

- every array has shape `(16, 16)`;

- every stored array is finite and real;

- every case status is PASS for a run-level PASS;

- run manifest case count equals ten;

- no `.tmp` file remains;

- no temporary scaffold remains;

- repository source remains unchanged;

- repository status contains only the authorized result directory before result

&#x20; archival.



A mismatch prevents Phase 13F completion.



---



## 42. Git handling of numerical results



The pilot result directory must not be committed automatically by the runner.



After execution:



1\. stop;

2\. audit the result directory;

3\. inspect repository status;

4\. decide in a separate controlled step whether the result directory and Phase

&#x20;  13F report should be archived.



The runner must not call Git write operations.



---



## 43. Tolerance policy



Tolerances may be used only for:



- floating grid-coordinate comparison;

- viscosity identity;

- timestep identity;

- final-time alignment;

- mask reconstruction checks where exact Boolean equality is not applicable.



Boolean masks must use exact equality.



Mutation checks must use exact array equality.



Call counts must use exact integer equality.



Case identifiers must use exact string equality.



Hashes must use exact equality.



No tolerance may be selected after observing pilot errors.



No error threshold is used to claim formal numerical accuracy.



---



## 44. Runtime claim boundary



A successful Phase 13F pilot may establish only that, for the frozen pilot:



- modules imported;

- exact references evaluated;

- guarded solvers constructed;

- grid and mask contracts matched;

- mutation guards did not trigger on the approved solver calls;

- deliberate invalid test doubles were detected;

- prohibited baseline forcing was not called;

- external RK2 stages executed at the intended times;

- post-step masks were counted correctly;

- finite errors were produced;

- output bundles were complete;

- output hashes matched;

- one controlled single-grid pilot completed.



It does not establish:



- formal verification;

- spatial convergence;

- temporal convergence;

- spectral convergence;

- exponential convergence;

- observed order;

- an asymptotic regime;

- solver-wide correctness;

- uncertainty bounds;

- physical validation;

- turbulence;

- an inertial range;

- an enstrophy cascade;

- an inverse-energy cascade;

- a `k^-3` law;

- method superiority;

- production readiness.



---



## 45. Prohibited pilot expansion



Phase 13F must not include:



- `N = 32`;

- `N = 64`;

- `N = 128`;

- any second grid;

- any second timestep;

- any timestep halving;

- any Reynolds-number sequence;

- any viscosity sequence;

- any final-time sequence;

- more than two evolution steps per case;

- more than one O1 case per method;

- more than one O2 case per method;

- more than one Track L case;

- more than one Track M case per method;

- parameter tuning after results are observed;

- error-slope fitting;

- observed-order calculation;

- method ranking;

- production solver modification.



Expansion requires a new phase.



---



## 46. Runner static-audit requirements



Before runtime smoke tests, the future runner must pass a static audit for:



- valid Python syntax;

- fixed runner filename;

- only authorized imports;

- no project-source modification;

- no dynamic import;

- no `eval`;

- no `exec`;

- no `shell=True`;

- no network import;

- no plotting import;

- no optimization or fitting import;

- no call to protected run methods;

- no call to inherited forcing;

- no call to `compute_rhs_selectable`;

- no call to `step_once_selectable`;

- no call to `run_selectable_diagnostic`;

- exactly ten case definitions;

- only `N = 16`;

- only `Re = 1000`;

- only `dt = 0.001`;

- only `n_steps` values zero or two;

- only `t_0 = 0.0`;

- only final times zero or `0.002`;

- no result execution at module top level;

- explicit `main()` boundary;

- explicit nonzero exit status on failure.



The runner must be committed and tagged before execution.



---



## 47. Execution authorization gate



Immediately before execution, a PowerShell gate must verify:



- correct repository root;

- correct branch;

- authorized runner commit;

- authorized annotated tag;

- clean working tree;

- all document hashes;

- all protected solver hashes;

- all verification-module hashes;

- Phase 13F runner hash;

- Phase 13F design hash;

- result run identifier absent;

- no active Git operation;

- Python executable resolved;

- no bytecode writing;

- isolated Python mode requested.



Only after this gate passes may the runner execute.



---



## 48. Console-output policy



The runner must print:



- phase title;

- authorized commit;

- run identifier;

- preflight results;

- fail-closed smoke-test results;

- each case start;

- each case completion status;

- call counts;

- mask counts;

- final-time alignment;

- error norms;

- output path;

- final run status.



The runner must not print:



- a convergence claim;

- a method ranking;

- production-readiness language;

- turbulence language;

- `k^-3` confirmation language.



---



## 49. Expected successful run summary



A successful pilot summary must state:



- preflight:

&#x20; PASS

- import smoke:

&#x20; PASS

- exact-reference smoke:

&#x20; PASS

- configuration rejection tests:

&#x20; PASS

- mutation-guard tests:

&#x20; PASS

- schema rejection tests:

&#x20; PASS

- atomic-writer temporary test:

&#x20; PASS

- solver-construction smoke:

&#x20; PASS

- O1 cases:

&#x20; `3/3 PASS`

- O2 cases:

&#x20; `3/3 PASS`

- Track L cases:

&#x20; `1/1 PASS`

- Track M cases:

&#x20; `3/3 PASS`

- total cases:

&#x20; `10/10 PASS`

- total external RK2 steps:

&#x20; `8`

- forcing calls:

&#x20; `0`

- persistent output files:

&#x20; `51`

- refinement sequence:

&#x20; `NONE`

- convergence claim:

&#x20; `NONE`



Anything less is not a full Phase 13F pilot PASS.



---



## 50. Failure interpretation



A failed Phase 13F case means only that the frozen pilot did not satisfy one or

more required runtime conditions.



It does not automatically identify:



- a production solver defect;

- an advection-operator defect;

- an exact-reference defect;

- a harness defect;

- an output-schema defect.



The failure must be localized before editing any source.



No protected source may be changed inside Phase 13F without closing the phase

as failed and opening a separately authorized corrective phase.



---



## 51. Phase 13F completion criteria



Phase 13F may be declared complete only when:



- this design is committed, tagged, and pushed;

- runner implementation is committed, tagged, and pushed;

- runner static audit passes;

- all hashes remain pinned;

- non-solver fail-closed runtime tests pass;

- exact-reference runtime smoke tests pass;

- solver-construction smoke tests pass;

- the exact ten-case pilot executes once;

- no unauthorized case executes;

- no unauthorized numerical configuration executes;

- all call counts match;

- all forcing counts are zero;

- all mask counts match;

- all final times align;

- all primary errors are finite;

- all ten case bundles are complete;

- the run manifest is complete;

- all physical file hashes match metadata;

- no temporary file remains;

- no solver scaffold remains;

- a Phase 13F completion report is created;

- the result and report archive boundary is explicitly approved;

- no refinement sequence is run;

- no convergence claim is made;

- no physical-validation claim is made.



---



## 52. Phase 13F design decision



This design authorizes a future controlled single-grid runtime pilot, subject to

separate implementation, static-audit, archive, and execution gates.



The authorized maximum is:



- one grid:

&#x20; `N = 16`;

- one Reynolds parameter:

&#x20; `Re = 1000`;

- one timestep:

&#x20; `dt = 0.001`;

- six isolated operator cases;

- one two-step Track L case;

- three two-step Track M cases;

- eight external RK2 steps total;

- ten numerical cases total;

- one persistent result run;

- no refinement sequence;

- no observed order;

- no convergence claim.



Current decision:



> PASS — Phase 13F controlled single-grid pilot design is complete as a

> design-only candidate, contingent on source inspection and controlled Git

> archive.



No numerical execution is authorized while this design remains unarchived.



---



## 53. Recommended next subphase



After this design is archived, the recommended next subphase is:



**Phase 13F.2 — Controlled Pilot Runner Implementation and Static Audit**



Phase 13F.2 may create only:



`run_phase13F_verification_pilot.py`



Phase 13F.2 must remain non-executing.



Runtime smoke tests require a separate Phase 13F.3 gate.

