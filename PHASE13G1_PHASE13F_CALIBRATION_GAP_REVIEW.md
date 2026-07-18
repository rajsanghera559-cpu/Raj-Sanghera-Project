# Phase 13G.1 — Phase 13F Calibration-Gap Review

## 0. Document control

- Project: Raj-Sanghera-Project
- Parent phase: Phase 13F controlled single-grid verification pilot
- Current phase: Phase 13G — Formal Pre-registration Freeze and Phase 13F Calibration-Gap Review
- Subphase: Phase 13G.1 — read-only calibration-gap review
- Starting branch: `phase4_validation`
- Starting commit: `bfc0842177c2aa0eb6ebf0f00e088d335d6811f6`
- Starting annotated tag: `v0.5.57-phase13F4-successful-pilot-completion-evidence-archive`
- Successful Phase 13F run: `phase13F_pilot_20260717T072334Z_0b9a2b9`
- Document status: calibration-gap decision candidate
- Solver execution authorized: no
- Refinement execution authorized: no
- Formal pre-registration frozen: no
- Phase 13H authorized: no

---

## 1. Executive decision

> PASS-HOLD — Phase 13F is complete and supplies a valid, reproducible runtime
> and evidence-harness checkpoint. The Phase 13G calibration-gap review passes,
> but the formal pre-registration freeze is held because the archived evidence
> does not determine the formal refinement ranges, isolation thresholds, or
> numerical-floor decision rules required by Phase 13A.

This is a successful gap-review result, not a failure of Phase 13F.

No formal or exploratory numerical execution is authorized by this document.

---

## 2. Evidence inspected

| Evidence | Committed SHA-256 |
|---|---|
| Phase 13A claim design | `6A1DCB87E3E5C4C468C4C804E6059B98864AC84263E44D1342E655CCE7E024CC` |
| Phase 13B equation specification | `6FC0685AC0225F542C181174ECC5940CE1C1163F2CE90B15301AEF46D5CE7875` |
| Phase 13C reference/source audit | `ABEF31DF4F67913EB418C816DBB665531C5F2C854EB4E300B68CF9F45CA5A306` |
| Phase 13D harness design | `2F014D33623C5D7184F65EBF4E3CA34F4BAD13501BED0A66DC72D33FB1A90A5E` |
| Phase 13E implementation/static audit | `D59587426FD89AACC1A988CD892D52038595F13C4020202BB8A8B11BCAE0AB61` |
| Phase 13F completion report | `832C8B2BAFAA825C5C39286DA40F7742BDA5CA74A056159608EFE050EE89C610` |
| Phase 13F detailed inventory | `5C523EF510A52ED986CBF2182DB2864CB136C5A8B2A9E9462A66EE59905ECE2D` |
| Phase 13F successful-run manifest | `9E0D279852DECCAEA1F0A121E7F01671410DDC4BF56CF7FE08BF71248770879C` |

---

## 3. Completed prerequisites

The archived evidence establishes the following usable inputs for later design:

1. benchmark equations and analytic/manufactured references exist;
2. source signs, periodicity, compatibility, and reference independence were audited;
3. error norms, restriction behavior, metadata, and output schemas were designed;
4. the external runner passed fail-closed configuration and mutation guards;
5. all ten single-grid pilot cases passed at the frozen configuration;
6. the successful V1/V2 numerical arrays were bitwise identical;
7. the 51-file successful evidence set was independently audited and archived;
8. no inherited forcing or prohibited solver-interface execution occurred.

These establish runtime and evidence integrity only.

---

## 4. Phase 13F calibration boundary

The successful pilot used only:

- grid: `N = 16`;
- timestep: `dt = 0.001`;
- Reynolds parameter: `Re = 1000`;
- viscosity: `nu = 0.001`;
- operator steps: `0`;
- evolution steps: `2`;
- evolution final time: `0.002`;
- numerical cases: `10`;
- refinement sequence: none.

Therefore the pilot contains no independent variation from which to estimate a
spatial trend, temporal trend, competing-error contribution, useful refinement
range, or rate-estimation floor.

---

## 5. Calibration-gap matrix

| Required pre-registration item | Available evidence | Decision |
|---|---|---|
| Benchmark/reference revisions | Phase 13B/13C revisions are archived | Available for later freeze |
| Harness and output revisions | Phase 13D/13E/13F passed | Available for later freeze |
| Formal viscosity | Phase 13B deferred selection; Phase 13F sampled one value | Not determined |
| Formal final time | Phase 13B deferred selection; Phase 13F sampled `0.002` only | Not determined |
| Spatial refinement family | Candidate `r_h = 2` family exists; only `N=16` was executed | Not calibrated |
| Temporal refinement family | Candidate `r_t = 2` exists; only `dt=0.001` was executed | Not calibrated |
| Temporal contamination threshold | No timestep comparison exists | Not calibrated |
| Spatial contamination threshold | No grid comparison exists | Not calibrated |
| Absolute/relative error floor | Machine epsilon is recorded, but no formal floor rule was calibrated | Not frozen |
| Plateau handling | No refinement sequence exists | Not calibrated |
| Order-stability rule | Phase 13A requires prospective selection | Not frozen |
| Asymptotic-range rule | Phase 13A requires prospective selection | Not frozen |
| Formal analysis script hash | No formal analysis procedure has been frozen | Missing |
| Claim and downgrade wording | Templates exist in Phase 13A | Available for later freeze |

---

## 6. Why the formal freeze must wait

Freezing numerical thresholds from the observed `N=16`, `dt=0.001` result would
convert a single observation into an unsupported refinement rule. It would also
contradict Phase 13A's separation of spatial and temporal studies and Phase
13B's explicit deferral of these selections.

The near-roundoff O1 and Track L errors are observations at one configuration.
They do not, by themselves, define a general numerical-floor threshold.

The Phase 13F PASS remains unchanged.

---

## 7. Required recovery path inside Phase 13G

The controlled continuation is:

1. **Phase 13G.2 — Exploratory Isolation-Calibration Design and Authorization**
   freezes a small exploratory grid/timestep matrix, error quantities, stopping
   rules, output schema, and non-claim boundary before execution.
2. **Phase 13G.3 — Controlled Exploratory Isolation Calibration** executes only
   the Phase 13G.2 matrix and archives all outcomes, including failures.
3. **Phase 13G.4 — Formal Pre-registration Freeze** uses the exploratory evidence
   to freeze formal grids, timesteps, thresholds, analysis-script hash, claim
   wording, downgrade wording, and failure conditions.
4. **Phase 13H — Formal Refinement Runs** requires a separate explicit
   authorization after Phase 13G.4 is independently audited and archived.

Exploratory Phase 13G calibration data must remain separate from the Phase 13H
formal evidence set.

---

## 8. Phase 13G.2 design requirements

Before any calibration execution, Phase 13G.2 must predeclare:

- selected benchmark tracks and methods;
- candidate spatial levels and constant refinement ratio;
- candidate timestep levels and constant refinement ratio;
- fixed viscosity and final physical time for the exploratory matrix;
- primary and secondary error quantities;
- spatial/temporal isolation measurements;
- provisional numerical-floor observations to record;
- case-count and compute-cost ceiling;
- fail-closed configuration and mutation guards;
- file inventory, manifest, and independent-audit requirements;
- explicit prohibition on convergence, observed-order, asymptotic-range,
  method-superiority, physical-validation, turbulence, cascade, and `k^-3` claims.

No threshold may be selected after viewing formal Phase 13H data.

---

## 9. Non-claims

This review establishes no spatial or temporal convergence, observed order,
asymptotic regime, uncertainty bound, solver-wide verification, method ranking,
physical validation, turbulence, cascade, `k^-3` behavior, or production
readiness.

---

## 10. Decision

> PASS-HOLD — Archive this Phase 13G.1 gap review before designing the
> exploratory calibration. Do not create a formal pre-registration, analysis
> script, or numerical calibration run in this subphase.
