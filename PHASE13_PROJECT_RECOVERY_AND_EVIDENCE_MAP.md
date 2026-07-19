# Phase 13 Project Recovery and Evidence Map

## Document control

- **Project:** Raj-Sanghera-Project
- **Purpose:** Recover the project from an overcomplicated audit workflow by consolidating the real scientific and software evidence into one readable control document.
- **Document type:** Project-state reconstruction and decision map
- **This is not:** a new numbered phase, a remediation gate, an audit script, a convergence report, or a numerical rerun
- **Repository branch:** `phase4_validation`
- **Current remote commit:** `fa720851bb23f43e9a69f0eb33775f04bd9a3130`
- **Current annotated tag:** `v0.5.62-phase13G3B-calibration-runner-signature-remediation`
- **Current runner:** `run_phase13G_isolation_calibration.py`
- **Current runner SHA-256:** `2558DBB7B22BD5AA340916EAFE4C6FF61E077404F02D59AB96584D4DF494497D`
- **Preserved exploratory run:** `phase13G_calibration_20260718T083709Z_fa72085`
- **Preserved run directory:** `experiments/verification/phase13/phase13G_calibration_20260718T083709Z_fa72085/`
- **Recovery decision:** Keep the evidence, stop the recursive audit chain, interpret the existing numerical results conservatively, and close Phase 13 at the exploratory verification/calibration level.
- **Phase 13G.4:** not begun
- **Phase 13H:** not authorized

---

## 1. Executive recovery decision

The project is intact. The protected solver source was not lost or overwritten. The current branch and tagged runner are remotely archived. Phase 12 is complete. Phase 13A through Phase 13F produced legitimate, cumulative verification infrastructure and evidence. The Phase 13G.3 numerical runner completed all 77 authorized cases and wrote the complete 390-file exploratory dataset.

The bad outcome was not the loss of the project. The bad outcome was a workflow that allowed auditing machinery to become the main activity. Several later red `FAIL` or `STOP` messages were caused by defects in wrapper or audit logic:

- case-sensitive versus Windows-style path ordering;
- a redundant `git check-ignore` text gate;
- assuming that plan records contained a `case_id`;
- requiring every Boolean in `checks.json` to be `true`, including correct non-claim values such as `"convergence_claim": false`.

Those errors do not identify a solver defect or corrupted numerical dataset. They identify unvalidated audit assumptions.

The correct recovery is:

1. preserve the completed 77-case run;
2. treat the full independent file/array audit as **unfinished**, not failed evidence;
3. analyze the recorded numerical patterns descriptively, without a formal convergence claim;
4. close Phase 13 without beginning Phase 13G.4 or Phase 13H;
5. return to the broader scientific question with a much simpler workflow.

### Recommended option

Use **Option 2, then Option 3**:

- **Now:** analyze the 77-case results without claiming formal convergence.
- **Then:** close Phase 13 at the exploratory verification/calibration level and return to the broader research question.
- **Defer:** the simplified independent audit unless a paper, reviewer, supervisor, or formal claim later makes it necessary.

---

## 2. Where the project is

### 2.1 Repository state

| Item | Current state |
|---|---|
| Repository | `Raj-Sanghera-Project` |
| Branch | `phase4_validation` |
| Remote commit | `fa720851bb23f43e9a69f0eb33775f04bd9a3130` |
| Annotated tag | `v0.5.62-phase13G3B-calibration-runner-signature-remediation` |
| Runner SHA-256 | `2558DBB7B22BD5AA340916EAFE4C6FF61E077404F02D59AB96584D4DF494497D` |
| Runner format | 1,000 lines, LF-only |
| Last committed change | Corrected the schema helper call and the runner tag boundary |
| Protected solver changes during Phase 13 | None |
| Phase 13H authorization | No |

### 2.2 Protected solver identities

| File | Preserved SHA-256 |
|---|---|
| `project/solver/spectral_solver.py` | `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1` |
| `project/solver/selectable_advection_solver.py` | `5EDA93A2E9358D81927BD9EE247F305E6DBC94367B351801913FFEAA2D7C5891` |
| `project/solver/advection_operators.py` | `2C86465570DDF095D5B0A9B7F67E6E78A89D14F82933FA983D91156DD0F76409` |

### 2.3 Verification-module identities

| File | Preserved SHA-256 |
|---|---|
| `project/verification/phase13_exact_references.py` | `6904C78E54948D07C92173C8B313844B28C92209B4F61CE447FFC29E15DA4EED` |
| `project/verification/phase13_external_harness.py` | `CDB6DBC249EA2DFF27E729AF0CF3D5C545C48BE57624CC59842B3222DAA752A2` |
| `project/verification/phase13_output_schema.py` | `6899C611C56E8154435BB6C042B520A13B466CD10042DE5325C7F9EF634FB11F` |

### 2.4 Preserved Phase 13G.3 result

| Item | Recorded value |
|---|---|
| Run identifier | `phase13G_calibration_20260718T083709Z_fa72085` |
| Authorized commit | `fa720851bb23f43e9a69f0eb33775f04bd9a3130` |
| Authorized tag | `v0.5.62-phase13G3B-calibration-runner-signature-remediation` |
| Unique cases | `77/77 PASS` |
| External RK2 steps | `850` |
| Advection calls | `1632` |
| Diffusion calls | `1700` |
| Track M source evaluations | `1608` |
| Inherited forcing calls | `0` |
| Post-step masks | `850` |
| Persistent files | `390` |
| Recorded inventory SHA-256 | `F60AD7FD883FAA1EDB058CCA6024658C33570661DEA206D9BB418212BFCBE161` |
| Observed-order calculation | None |
| Convergence claim | None |
| Physical-validation claim | None |

The recovered path inventory later showed:

- 390 physical paths;
- 390 Git-ignored paths;
- zero missing paths;
- zero extra paths;
- zero tracked result paths;
- exact NUL-safe path-set equality;
- clean visible Git status;
- no files modified by the recovery audit;
- no solver execution or calibration rerun.

---

## 3. Correct technical classification: verification, not physical validation

In ordinary project language, it is understandable to say the project is in a “validation phase.” In formal computational-science terminology, the work completed so far is primarily:

- **code verification:** checking whether the implementation represents the intended equations and numerical methods;
- **calculation or solution verification:** characterizing numerical error for specific benchmark calculations;
- **provenance and evidence integrity:** checking source identity, configuration, outputs, and reproducibility.

It is **not physical validation**, because no Phase 13 result compares the model with experimental or observational physical data.

A precise current description is:

> The project is in numerical verification and evidence-consolidation, with physical validation not yet attempted.

---

## 4. Evidence reliability hierarchy

Not every artifact has the same status. The recovery depends on separating strong evidence from incomplete process work.

| Level | Meaning | Current contents |
|---|---|---|
| **A — Archived and independently supported** | Completed evidence with successful audit/archival appropriate to its scope | Phase 12; Phase 13A–13F |
| **B — Completed numerical execution, structurally recovered** | Runner completed; case and aggregate counts passed; dataset preserved; inventory path set recovered; full independent file/array audit unfinished | Phase 13G.3 exploratory dataset |
| **C — Tooling incidents** | Wrapper or audit logic failed without demonstrating a numerical defect | G.3 inventory ordering stop; recovery-audit text gate; plan-schema assumption; blanket Boolean assumption |
| **D — Not started** | No evidence exists and no claim is authorized | Phase 13G.4 formal freeze; Phase 13H formal refinement |

The Level C failures must not be promoted into claims that the Level B numerical dataset is defective. They also must not be ignored: they explain why the dataset should be described as **complete but not fully independently audited**.

---

## 5. Phase 12 baseline

Phase 12 was a real, completed validation/verification checkpoint for the controlled diagnostic pathway.

### What Phase 12 established

- The entire Phase 12A–12R chain was recorded as PASS.
- N256 short, intermediate, and final-time-1.0 feasibility runs completed for:
  - `fd_centered`;
  - `pseudo_spectral`;
  - `arakawa`.
- A controlled N64/N128/N256 comparison showed decreasing method-difference diagnostics for the tested setup.
- The selectable diagnostic interface remained controlled.
- `SelectableAdvectionSolver.run()` remained disabled.
- The protected baseline solver and advection-operator files remained unchanged.

### Supported Phase 12 conclusion

> Under the tested controlled diagnostic setup, N256 final-time-1.0 execution was feasible for all three selectable methods, and the recorded pairwise field and spectrum differences decreased across N64, N128, and N256.

### What Phase 12 did not establish

- formal convergence;
- physical validation;
- turbulence;
- an inertial range;
- a cascade;
- a `k^-3` law;
- method superiority;
- production readiness.

### Why Phase 13 was a legitimate next step

Phase 12 used controlled diagnostic comparisons but did not have independently manufactured exact references and a prospectively isolated spatial/temporal benchmark program. Phase 13 was intended to fill that verification gap.

---

## 6. Complete Phase 13 evidence map

| Work item | Primary artifact or evidence | What it established | What it did not establish | Recovery status |
|---|---|---|---|---|
| **13A — Claim design** | `PHASE13A_FORMAL_CONVERGENCE_STUDY_CLAIM_DESIGN.md` | Defined code verification, calculation verification, claim classes, refinement separation, evidence gates, and conservative language | No execution, observed order, convergence, or validation | Complete and archived |
| **13B — Equation and benchmark specification** | `PHASE13B_BENCHMARK_AND_CONTINUOUS_EQUATION_SPECIFICATION.md` | Froze equation signs, O1/O2/L/M benchmark formulas, source rules, error fields, and method boundaries | No benchmark execution or numerical convergence | Complete and archived |
| **13C — Mathematical reference audit** | `PHASE13C_REFERENCE_SOLUTION_AND_SOURCE_TERM_AUDIT_REPORT.md` | Audited periodicity, derivatives, signs, means, Fourier support, O2 compatibility, Track L decay, and Track M manufactured source using independent routes | No solver execution or numerical accuracy claim | Complete and archived |
| **13D — Harness design** | `PHASE13D_EXTERNAL_VERIFICATION_HARNESS_DESIGN.md` | Defined external, non-mutating, source-aware, fail-closed harness and output contracts | No implementation or runtime result | Complete and archived |
| **13E — Harness implementation/static audit** | Three verification modules plus Phase 13E report | Implemented exact-reference, harness, and output-schema modules; static contracts passed | Static checks did not establish runtime correctness | Complete and archived |
| **13F — Single-grid runtime pilot** | Successful 10-case run, 51 files, completion report, independent audit | Runtime integration, fail-closed tests, mutation guards, source-stage timing, zero forcing, mask counts, output writing, deterministic V1/V2 repetition | No refinement trend, observed order, convergence, method superiority, or physical validation | Complete, independently audited, archived |
| **13G.1 — Calibration-gap review** | `PHASE13G1_PHASE13F_CALIBRATION_GAP_REVIEW.md` | Correctly found that one grid and one timestep could not determine formal refinement ranges or thresholds | Did not authorize execution | Complete and archived |
| **13G.2 — Exploratory calibration design** | `PHASE13G2_EXPLORATORY_ISOLATION_CALIBRATION_DESIGN_AND_AUTHORIZATION.md` | Prospectively fixed a bounded 77-case exploratory matrix, error quantities, isolation observations, storage ceiling, and non-claim rules | Did not freeze formal Phase 13H thresholds | Complete and archived |
| **13G.3 — Runner and execution** | Tagged runner plus `phase13G_calibration_20260718T083709Z_fa72085/` | All 77 cases completed; aggregate operation counts matched; 390 files written; exact path-set inventory recovered | The intended full independent file/array audit did not finish because audit tools made incorrect schema assumptions | Numerical execution complete; formal audit unresolved |
| **13G.4 — Formal pre-registration freeze** | None | Nothing yet | No thresholds or formal sequences frozen | Not begun |
| **13H — Formal refinement runs** | None | Nothing yet | No formal convergence evidence | Not authorized |

---

## 7. What Phase 13 genuinely achieved

Phase 13 was not wasted. Its useful achievements are substantial:

1. **The continuous equation and signs were made explicit.**
2. **Four benchmark tracks were defined:**
   - O1 resolved two-mode operator case;
   - O2 analytic broad-spectrum operator case;
   - L exact linear viscous-decay evolution;
   - M nonlinear manufactured evolution.
3. **The exact references and manufactured source were independently audited.**
4. **The verification harness was kept external to the protected solver source.**
5. **The harness imposed source replacement, stage-time, mutation, mask, and forcing safeguards.**
6. **A 10-case runtime pilot completed and was independently audited.**
7. **A 77-case exploratory matrix completed.**
8. **The recorded dataset separates useful spatial and temporal patterns.**

The failure was not that Phase 13 contained no progress. The failure was allowing process controls to keep multiplying after the main exploratory dataset had already been obtained.

---

## 8. Phase 13G.3 run map

### 8.1 Frozen matrix

| Component | Cases | RK2 steps |
|---|---:|---:|
| O1 operator | 9 | 0 |
| O2 operator | 15 | 0 |
| Track L evolution | 5 | 46 |
| Track M evolution | 48 | 804 |
| **Total** | **77** | **850** |

### 8.2 Methods

- `fd_centered`
- `pseudo_spectral`
- `arakawa`

### 8.3 Continuous configuration

- domain: `L = 2*pi`;
- initial time: `t_0 = 0`;
- Reynolds parameter: `Re = 1000`;
- viscosity: `nu = 0.001`;
- requested evolution final time: `T = 0.008`;
- arithmetic: `float64`;
- product dealiasing: disabled;
- inherited forcing: prohibited;
- exact references: direct native-grid analytic evaluation.

### 8.4 Output structure

The run contains five root files:

1. `calibration_plan.json`
2. `run_manifest.json`
3. `calibration_case_summary.csv`
4. `calibration_isolation_metrics.csv`
5. `calibration_floor_observations.csv`

Each of the 77 case directories contains:

1. `case_metadata.json`
2. `checks.json`
3. `error_summary.csv`
4. `field_manifest.json`
5. `fields.npz`

Total:

`77 * 5 + 5 = 390 files`

### 8.5 Honest audit status

The original design required a full independent read-only audit before calling the dataset fully audited. That audit has not completed.

What has been verified after execution:

- all 77 runner cases reported PASS;
- expected aggregate operation counts matched;
- all 390 physical paths exist;
- the physical and Git-ignored inventories are the same exact NUL-safe path set;
- no result path is tracked;
- the repository remained visibly clean;
- no recovery action reran the solver or modified the dataset.

What remains unverified by a successful independent end-to-end audit:

- every file hash against the manifest;
- every NPZ array against every field manifest;
- every case metadata/checks/error row across all 77 cases;
- every root summary row and null reason.

The unfinished audit is a documentation and assurance gap. It is not evidence that those checks would fail.

---

## 9. Workflow incident map

| Incident | What actually happened | Effect on scientific evidence |
|---|---|---|
| Initial runner helper failure | Runner called a nonexistent or wrong-signature inherited schema helper before numerical execution | No numerical evidence produced; runner was corrected |
| Post-run inventory stop | Two identical path sets were compared in different sort orders on Windows | False stop after the numerical run had completed |
| Recovery audit V1 stop | Redundant text-based `git check-ignore` gate did not echo every path as assumed | Audit-tool defect; dataset unchanged |
| Independent audit V1 stop | Audit expected `case_id` inside each `calibration_plan.json` case record | Schema-assumption defect; dataset unchanged |
| Independent audit V2 stop | Audit required every Boolean in `checks.json` to be `true`, including correct non-claim flags | Boolean-semantics defect; dataset unchanged |

### Rule established by this recovery

No future audit may be generated from assumed schemas. The actual emitted files must be inspected first, the typed schema must be written down, and a one-case compatibility test must pass before a full audit is attempted.

More importantly, no future audit chain should be pursued unless it changes a real scientific decision.

---

## 10. Descriptive interpretation of the 77-case numerical evidence

The following interpretation uses only recorded `L2_rms` values from the preserved run. It is deliberately descriptive. It does not calculate or claim formal observed order.

### 10.1 O1 resolved two-mode operator benchmark

| Method | `N=16` | `N=32` | `N=64` | Descriptive pattern |
|---|---:|---:|---:|---|
| `fd_centered` | `6.898904e-02` | `1.768397e-02` | `4.448674e-03` | About 3.90× and 3.98× lower per grid doubling |
| `arakawa` | `8.955452e-02` | `2.369994e-02` | `6.010247e-03` | About 3.78× and 3.94× lower per grid doubling |
| `pseudo_spectral` | `1.091107e-15` | `2.448220e-15` | `6.071125e-15` | Near floating-point scale; no useful decay sequence |

Interpretation:

- `fd_centered` and `arakawa` show a strong, regular, approximately fourfold error reduction under grid doubling.
- The pseudo-spectral operator already resolves this band-limited benchmark to near roundoff, so a spatial rate cannot be inferred from O1.

### 10.2 O2 broad-spectrum operator benchmark

| Method | `N=16` | `N=32` | `N=64` | `N=128` | `N=256` |
|---|---:|---:|---:|---:|---:|
| `fd_centered` | `1.399159e-02` | `3.640892e-03` | `9.194415e-04` | `2.304410e-04` | `5.764662e-05` |
| `arakawa` | `1.053152e-02` | `2.767056e-03` | `7.004859e-04` | `1.756720e-04` | `4.395249e-05` |
| `pseudo_spectral` | `5.393724e-09` | `7.811569e-16` | `1.682700e-15` | `3.829500e-15` | `7.006252e-15` |

Descriptive pattern:

- `fd_centered` reduction factors approach four: approximately `3.84`, `3.96`, `3.99`, `4.00`.
- `arakawa` reduction factors also approach four: approximately `3.81`, `3.95`, `3.99`, `4.00`.
- `pseudo_spectral` falls from `5.39e-09` at N16 to near floating-point scale at N32, after which the sequence is floor-dominated.

This is strong benchmark-specific evidence of regular operator-error reduction for the finite-difference-based methods and rapid resolution of the smooth O2 field by the pseudo-spectral operator. It is not a formal method ranking or fitted convergence result.

### 10.3 Track L exact viscous decay

| Grid | `dt` | Steps | `L2_rms` |
|---:|---:|---:|---:|
| 32 | `0.0005` | 16 | `1.120397e-15` |
| 64 | `0.004` | 2 | `1.586483e-14` |
| 64 | `0.002` | 4 | `4.478700e-15` |
| 64 | `0.001` | 8 | `2.313396e-15` |
| 64 | `0.0005` | 16 | `2.744506e-15` |

Track L is mostly floor-limited. It is useful as evidence that the linear diffusion/RK2 path and exact-mode retention behave at near-roundoff scale. It is not a robust rate-estimation sequence.

### 10.4 Track M spatial behavior at `dt = 0.0005`

| Method | N16 | N32 | N64 | N128 | N256 |
|---|---:|---:|---:|---:|---:|
| `fd_centered` | `5.453124e-04` | `1.397805e-04` | `3.516478e-05` | `8.805796e-06` | `2.203188e-06` |
| `arakawa` | `7.078834e-04` | `1.873367e-04` | `4.750903e-05` | `1.192073e-05` | `2.983784e-06` |
| `pseudo_spectral` | `1.519701e-09` | `1.519701e-09` | `1.519701e-09` | `1.519700e-09` | `1.519701e-09` |

Descriptive pattern:

- `fd_centered` reductions are approximately `3.90`, `3.98`, `3.99`, `4.00`.
- `arakawa` reductions are approximately `3.78`, `3.94`, `3.99`, `4.00`.
- The pseudo-spectral spatial sequence is essentially flat because the remaining error is dominated by the timestep rather than grid resolution.

The same spatial pattern is present at `dt = 0.00025`.

### 10.5 Track M temporal behavior at `N = 256`

| Method | `dt=.004` | `.002` | `.001` | `.0005` | `.00025` |
|---|---:|---:|---:|---:|---:|
| `fd_centered` | `2.277819e-06` | `2.220832e-06` | `2.206711e-06` | `2.203188e-06` | `2.202308e-06` |
| `arakawa` | `3.062681e-06` | `3.002502e-06` | `2.987525e-06` | `2.983784e-06` | `2.982849e-06` |
| `pseudo_spectral` | `9.718300e-08` | `2.430690e-08` | `6.078113e-09` | `1.519701e-09` | `3.799456e-10` |

Descriptive pattern:

- The finite-difference and Arakawa sequences approach plateaus as `dt` is reduced, consistent with spatial error dominating at N256.
- The pseudo-spectral sequence decreases almost exactly fourfold whenever `dt` is halved.
- At `N=128`, the same pseudo-spectral temporal pattern appears.
- The pseudo-spectral result is nearly independent of N between 128 and 256 at fixed timestep, which supports the interpretation that temporal error dominates that sequence.

This is descriptively compatible with the declared second-order RK2 time integration on this smooth manufactured benchmark. A formal observed-order claim remains deferred.

### 10.6 Spatial/temporal isolation observations

For Track M:

- At `dt=.0005` versus `.00025`, the finite-difference and Arakawa errors change by very small percentages while the grid-to-grid changes are much larger. That is useful evidence that their spatial sequences are not strongly contaminated by time error over the tested fine timesteps.
- For the pseudo-spectral method, changing N has almost no effect while halving `dt` produces an almost fourfold error reduction. That is useful evidence of temporal isolation for the tested high-resolution sequence.
- These are exactly the types of observations the exploratory calibration was designed to collect.

### 10.7 Method comparison boundary

The pseudo-spectral errors are much smaller on these smooth periodic analytic benchmarks. That fact may be reported as a benchmark-specific error observation.

It must not be converted into a general statement that the pseudo-spectral method is “superior,” because:

- the benchmarks strongly favor spectral differentiation;
- conservation, stability, robustness, computational cost, and nonsmooth behavior are separate questions;
- product dealiasing is disabled in this declared pseudo-spectral configuration;
- the project has not tested every relevant application regime.

---

## 11. Supported and unsupported statements

### 11.1 Supported now

The following statements are defensible:

1. The protected solver and verification source identities were preserved at the current checkpoint.
2. The Phase 13 exact benchmark definitions and manufactured source were independently audited mathematically.
3. The external verification harness completed a successful, independently audited 10-case single-grid pilot.
4. The preserved Phase 13G.3 runner completed all 77 exploratory cases and recorded the expected aggregate operation counts.
5. The Phase 13G.3 result directory contains the expected 390-path physical inventory, matching the Git-ignored inventory by exact path set.
6. In the exploratory data, `fd_centered` and `arakawa` exhibit regular, approximately fourfold error decreases under grid doubling on O1, O2, and the spatial Track M sequences.
7. In the exploratory data, the pseudo-spectral Track M error decreases approximately fourfold under timestep halving at N128 and N256.
8. O1 pseudo-spectral, O2 pseudo-spectral beyond N32, and Track L are near numerical-floor regimes.
9. These are benchmark-specific exploratory observations.

### 11.2 Not supported

Do not claim:

- formal spatial convergence;
- formal temporal convergence;
- a measured observed order;
- an asymptotic range;
- a Richardson or GCI uncertainty estimate;
- universal solver verification;
- method superiority;
- physical validation;
- turbulence;
- an inertial range;
- an enstrophy or inverse-energy cascade;
- a verified `k^-3` law;
- production readiness.

---

## 12. Is Phase 13 worth finishing?

Yes—but only if “finishing” is redefined.

Phase 13 is worth **closing cleanly** because it produced useful benchmark definitions, verification infrastructure, a successful runtime pilot, and a substantial exploratory dataset.

Phase 13 is **not worth extending now** into Phase 13G.4 and Phase 13H. The incremental scientific value does not justify re-entering the audit machinery before the existing data has been interpreted and the broader research direction has been reconsidered.

A sensible finish is:

> Phase 13 closed at the exploratory code-verification and calibration-evidence level. Formal independent audit of the 77-case array/file dataset and any formal convergence program are deferred.

This preserves the work without pretending that the original Phase 13G.2 acceptance chain was fully completed.

---

## 13. Decision among the three options

| Option | Scientific value | User burden | Workflow risk | Recommendation |
|---|---:|---:|---:|---|
| **1. Finish one simplified manual audit** | Moderate if a formal claim is required | High | High under the current workflow | **Defer** |
| **2. Analyze the 77-case results without formal convergence claims** | High | Low to moderate | Low | **Do now** |
| **3. Close Phase 13 and return to the broader research question** | High strategic value | Low | Low | **Do after Option 2** |

### Why not Option 1 now

A successful audit would improve assurance, but it would not change the most useful immediate scientific interpretation. The current data already shows clear exploratory patterns. Re-entering the audit chain now creates a high risk of spending more time on tooling rather than research.

Option 1 becomes worthwhile only when one of these conditions exists:

- a journal or reviewer requires a formal convergence statement;
- a supervisor asks for a formally audited benchmark sequence;
- the project intends to publish numerical order values;
- a separate technically qualified reviewer can inspect the audit logic;
- the audit can be validated against the real schema before the user is asked to run anything.

### Why Option 2 is the best immediate move

It uses the evidence already obtained, requires no solver rerun, and returns the work to scientific interpretation. The analysis can clearly distinguish:

- spatially dominated sequences;
- temporally dominated sequences;
- numerical-floor sequences;
- benchmark-specific method behavior.

### Why Option 3 should follow

After the descriptive analysis is documented, Phase 13 has served its purpose. The project can then return to the broader question rather than continuing procedural verification indefinitely.

---

## 14. Recommended closure plan

No scripts or new numerical runs are required.

### Closure deliverables

1. **This recovery and evidence map.**
2. **One descriptive numerical-results note** based only on the existing:
   - `calibration_case_summary.csv`;
   - `calibration_isolation_metrics.csv`;
   - `calibration_floor_observations.csv`.
3. **One closure statement** declaring:
   - exploratory execution complete;
   - formal independent audit deferred;
   - formal convergence deferred;
   - no physical validation claim;
   - no Phase 13H execution.
4. Return to the broader scientific question.

### Suggested closure wording

> Phase 13 produced independently audited benchmark mathematics, an external verification harness, a successful audited single-grid pilot, and a preserved 77-case exploratory calibration dataset. The exploratory runner completed all declared cases and recorded the expected operation and file counts. Subsequent audit-tool failures were localized to wrapper ordering and schema-assumption defects rather than demonstrated numerical-data defects. The project therefore closes Phase 13 at the exploratory verification/calibration level. Formal observed-order, convergence, method-superiority, and physical-validation claims remain deferred.

### Stop rules

- Do not rerun the 77-case calibration.
- Do not begin Phase 13G.4.
- Do not begin Phase 13H.
- Do not create another numbered remediation.
- Do not write another audit unless a concrete scientific or publication decision depends on it.
- Do not ask the user to debug generated audit code.

---

## 15. Return to the broader research question

The larger project is a specialized computational research code for two-dimensional incompressible vorticity dynamics with selectable advection methods and a substantial diagnostic pipeline.

The verification work should now support—not replace—the research.

A suitable return point is:

> Use the verified benchmark and runtime knowledge to interpret the solver’s forced-flow diagnostics, while testing whether any reported spectral behavior is robust to resolution, timestep, forcing, drag, stationarity window, shell support, and fitting choices.

The Phase 13 results can increase confidence in the code pathways exercised by the benchmarks. They do not themselves prove turbulence, cascade physics, or a `k^-3` regime.

Future work should be organized by one scientific question at a time, not by an expanding chain of micro-phases.

---

## 16. Future formal-convergence re-entry criteria

A formal convergence study may be reopened later, but only under a simpler process:

1. State the exact claim in one sentence.
2. Use the existing Phase 13 benchmark definitions.
3. Inspect and freeze the actual emitted schema before writing an audit.
4. Validate the audit on one real case.
5. Have a technically qualified second reader inspect the logic.
6. Run one full audit, not an audit chain.
7. Report a PASS, an inconclusive result, or a failure without creating nested remediation phases.
8. Never rerun the numerical matrix merely because an audit script has a schema bug.

Until those conditions exist, formal convergence remains deferred.

---

## 17. Evidence identity ledger

| Evidence | Identity |
|---|---|
| Phase 12 archive checkpoint | Commit `970b17a52ac6466f543aa66758d3c3756dc0db9f` |
| Phase 13A claim design SHA-256 | `6A1DCB87E3E5C4C468C4C804E6059B98864AC84263E44D1342E655CCE7E024CC` |
| Phase 13B specification SHA-256 | `6FC0685AC0225F542C181174ECC5940CE1C1163F2CE90B15301AEF46D5CE7875` |
| Phase 13C reference/source audit SHA-256 | `ABEF31DF4F67913EB418C816DBB665531C5F2C854EB4E300B68CF9F45CA5A306` |
| Phase 13D harness design SHA-256 | `2F014D33623C5D7184F65EBF4E3CA34F4BAD13501BED0A66DC72D33FB1A90A5E` |
| Phase 13E completion report SHA-256 | `D59587426FD89AACC1A988CD892D52038595F13C4020202BB8A8B11BCAE0AB61` |
| Phase 13F completion report SHA-256 | `832C8B2BAFAA825C5C39286DA40F7742BDA5CA74A056159608EFE050EE89C610` |
| Phase 13F successful manifest SHA-256 | `9E0D279852DECCAEA1F0A121E7F01671410DDC4BF56CF7FE08BF71248770879C` |
| Phase 13F successful inventory SHA-256 | `1FE50C08B049FEE256690CFCCD1F880D40D5D72EDCB85FB2402F1D508F10C202` |
| Phase 13F canonical numerical SHA-256 | `722282151CB161F596A9797CB024E4C422F34FAB54EA6E25C7272800E21C3761` |
| Phase 13G.1 review SHA-256 | `170258780D8EDA00E5E3FA08351C9E203F5E27BEAE92C5D0C00D0CF777689028` |
| Phase 13G.2 design SHA-256 | `688B4FDAEF4776CD87EB8EF1FBCD4F09D5BF639B40B0F23BB0A0AF205A3E8F13` |
| Current runner SHA-256 | `2558DBB7B22BD5AA340916EAFE4C6FF61E077404F02D59AB96584D4DF494497D` |
| Current runner commit | `fa720851bb23f43e9a69f0eb33775f04bd9a3130` |
| Current runner tag | `v0.5.62-phase13G3B-calibration-runner-signature-remediation` |
| Phase 13G.3 recorded 390-file inventory SHA-256 | `F60AD7FD883FAA1EDB058CCA6024658C33570661DEA206D9BB418212BFCBE161` |

---

## 18. Final reconstructed project status

### Plain-language status

The project is not broken and has not been lost. It has completed a substantial numerical-verification program. The workflow became overengineered after the main exploratory dataset was produced, and several generated audit scripts failed because they assumed the wrong schema or semantics.

### Technical status

- Phase 12: complete.
- Phase 13A–13F: complete for their declared design, mathematical-audit, implementation, and single-grid runtime-pilot scopes.
- Phase 13G.1–13G.2: complete as gap review and exploratory design.
- Phase 13G.3 numerical execution: complete.
- Phase 13G.3 structural inventory recovery: complete.
- Phase 13G.3 full independent file/array audit: unfinished.
- Phase 13G.4: not begun.
- Phase 13H: not authorized.
- Formal convergence: not claimed.
- Physical validation: not performed.
- Broader research: ready to resume after descriptive analysis and closure.

### Final recommendation

> Retain Phase 13 as valuable exploratory verification evidence. Do not continue the audit chain. Analyze the 77-case dataset descriptively, close Phase 13 with formal convergence deferred, and return to the broader scientific research question.
