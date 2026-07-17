# Phase 13F — Controlled Single-Grid Verification Pilot Completion Report

## 0. Document control

- Project: Raj-Sanghera-Project
- Phase: 13F
- Report status: completion-report candidate
- Successful run identifier: `phase13F_pilot_20260717T072334Z_0b9a2b9`
- Preserved incident run identifier: `phase13F_pilot_20260716T060052Z_3af22b8`
- Authorized commit: `0b9a2b9918630a9109e72d8bf71762915471fa5c`
- Authorized annotated tag: `v0.5.56-phase13F3B-corrected-ignored-output-inventory-audit`
- Phase 13F design SHA-256: `AFA552CDF8983966F1C8C7CA7E21038270D58D26570D65131B00A9B811E037DD`
- V2 runner working-tree SHA-256: `DB9396579912AC8A02E756B92050E60884259EF78791E47DA3B6A10A24F862FA`
- V2 runner committed-content SHA-256: `E69AF039A9E11C9A02E258D5202BD0CFE1A2B2DEF2D049153E704BDC02DF99BD`
- Independent audit script SHA-256: `91C5DA913E8EE14B0CF3F37B7CF0AED72F14532649B689483F9CBB6C7C4166B0`
- Successful-run inventory file SHA-256: `5C523EF510A52ED986CBF2182DB2864CB136C5A8B2A9E9462A66EE59905ECE2D`
- Refinement sequence: none
- Observed-order calculation: none
- Convergence claim: none
- Physical-validation claim: none

---

## 1. Executive decision

Phase 13F completed its authorized controlled single-grid verification pilot.

The corrected V2 runner returned exit code zero after all preflight, fail-closed, guarded-construction, numerical-case, output, and corrected ignored-file inventory gates passed.

An independent read-only audit verified all ten case bundles, all 51 files, file and array hashes, call counts, stage-time records, claim boundaries, and exact Git/physical inventory equality.

> PASS — the controlled single-grid pilot and its independent read-only > audit completed successfully.

This PASS applies only to the frozen single-grid pilot boundary. It is not a convergence or physical-validation result.

---

## 2. Phase progression

- Phase 13F.1: pilot design and authorization — archived
- Phase 13F.2: V1 pilot-runner implementation and static audit — archived
- Phase 13F.3A: V1 post-run Git-visibility incident evidence — archived
- Phase 13F.3B: corrected V2 ignored-output inventory audit — archived
- Phase 13F.3C: non-numerical preserved-run integration test — PASS
- Phase 13F.3D: controlled V2 numerical pilot — PASS
- Phase 13F.4: independent read-only V2 result audit — PASS

---

## 3. Prior incident and remediation

The V1 numerical cases and physical outputs passed, but V1 returned a nonzero exit code because ordinary Git status could not display files under the ignored `/experiments/` path.

V2 replaced that condition with a path-scoped ignored-file inventory. The inventory was required to equal the physical file inventory exactly.

The preserved V1 and successful V2 numerical arrays are bitwise identical.

---

## 4. Successful execution identity

- Run ID: `phase13F_pilot_20260717T072334Z_0b9a2b9`
- Created UTC: `2026-07-17T07:23:36Z`
- Branch: `phase4_validation`
- Commit: `0b9a2b9918630a9109e72d8bf71762915471fa5c`
- Repository dirty flag: `false`
- Operating system: `Windows-11-10.0.26200-SP0`
- Python version: `3.14.5`
- NumPy version: `2.4.4`
- Floating dtype: `float64`
- Machine epsilon: `2.220446049250313e-16`

---

## 5. Pilot boundary

- Grid: `N = 16`
- Domain: `L = 2*pi`
- Reynolds parameter: `Re = 1000`
- Viscosity: `nu = 0.001`
- Timestep: `dt = 0.001`
- Initial time: `t_0 = 0.0`
- Evolution steps per evolution case: `2`
- Evolution final time: `0.002`
- Product dealiasing: `false`
- Operator cases: `6`
- Evolution cases: `4`
- Total numerical cases: `10`
- Total external RK2 steps: `8`

No second grid, timestep, Reynolds number, viscosity, or final time was used.

---

## 6. Preflight and fail-closed tests

- Repository preflight: PASS
- Import smoke test: PASS
- Exact-reference evaluations: 4/4 PASS
- Configuration rejection tests: 21 PASS
- Mutation-guard tests: 6 PASS
- Output-schema rejection tests: 26 PASS
- Atomic writer tests: 3/3 PASS
- Guarded solver-construction tests: 4/4 PASS

---

## 7. Aggregate execution counts

- Guarded advection calls: `18`
- Guarded spectral-diffusion calls: `16`
- Track M analytic source evaluations: `12`
- Inherited forcing calls: `0`
- Post-step mask applications: `8`
- Prohibited solver-interface calls: `0`

---

## 8. Case results

| Case ID | Track | Method | Steps | L1 mean | L2 RMS | Linf | Relative L2 | Finite |
|---|---|---|---:|---:|---:|---:|---:|---|
| L_EQUAL_EIGENVALUE_DECAY_V1__N16__Re1000__dt0.001__steps2__t00__method_none | L | none | 2 | 6.119563716096e-16 | 7.861840858770e-16 | 2.442490654175e-15 | 7.861982373179e-16 | true |
| M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_arakawa | M | arakawa | 2 | 1.394663685944e-04 | 1.785724849726e-04 | 3.546476729090e-04 | 1.518174700230e-04 | true |
| M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_fd_centered | M | fd_centered | 2 | 9.432420550381e-05 | 1.375642098233e-04 | 3.156334257187e-04 | 1.169533498080e-04 | true |
| M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_pseudo_spectral | M | pseudo_spectral | 2 | 1.279415470060e-09 | 1.531638465931e-09 | 3.608834786561e-09 | 1.302157367207e-09 | true |
| O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_arakawa | O1 | arakawa | 0 | 6.992623340448e-02 | 8.955452032487e-02 | 1.777386959245e-01 | 1.744036654524e-01 | true |
| O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_fd_centered | O1 | fd_centered | 0 | 4.729372385249e-02 | 6.898904138010e-02 | 1.581830170235e-01 | 1.343532593228e-01 | true |
| O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_pseudo_spectral | O1 | pseudo_spectral | 0 | 7.907458837334e-16 | 1.091106739981e-15 | 3.996802888651e-15 | 2.124884530252e-15 | true |
| O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_arakawa | O2 | arakawa | 0 | 6.642071372416e-03 | 1.053152204862e-02 | 2.933301167338e-02 | 1.632529371043e-01 | true |
| O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_fd_centered | O2 | fd_centered | 0 | 8.828091053508e-03 | 1.399159044423e-02 | 3.893020836035e-02 | 2.168887103152e-01 | true |
| O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_pseudo_spectral | O2 | pseudo_spectral | 0 | 4.005330173583e-09 | 5.393723983088e-09 | 1.200361483475e-08 | 8.361006871599e-08 | true |

These values are single-grid pilot observations. They are not an observed-order study and do not rank the methods.

---

## 9. Independent read-only audit

The audit imported no project module, executed no solver or numerical timestep, and modified no repository or result file.

It verified the checkpoint identity; the preserved V1 run; all 10 V2 case directories and 51 files; physical sizes and hashes; metadata, checks, CSV fields, NPZ arrays, and field manifests; call counts, source-stage timing, zero forcing, and exact Git/physical inventory equality; and bitwise identity of all V1/V2 numerical arrays.

---

## 10. Evidence identities

- V2 run-manifest SHA-256: `9E0D279852DECCAEA1F0A121E7F01671410DDC4BF56CF7FE08BF71248770879C`
- V2 aggregate 51-file inventory SHA-256: `1FE50C08B049FEE256690CFCCD1F880D40D5D72EDCB85FB2402F1D508F10C202`
- Canonical numerical SHA-256: `722282151CB161F596A9797CB024E4C422F34FAB54EA6E25C7272800E21C3761`
- V1 incident run-manifest SHA-256: `F3CC9B6ADB336BFC884FA3F582952A881EA198A55C2CDA6679FC271109539A60`
- V1 aggregate 51-file inventory SHA-256: `4E8F2DF95FE9927405821D7B70BD92E105B50BCC80FE2E1C498FBA7CC51F966A`
- Successful-run detailed inventory: `PHASE13F4_SUCCESSFUL_V2_RUN_FILE_INVENTORY.csv`
- Detailed inventory file SHA-256: `5C523EF510A52ED986CBF2182DB2864CB136C5A8B2A9E9462A66EE59905ECE2D`
- Detailed inventory rows: `51`

---

## 11. Reproducibility observation

Every stored numerical array in V2 is bitwise identical to its V1 counterpart. This establishes deterministic repetition for these two executions at the frozen pilot configuration only.

---

## 12. Repository and source integrity

- Protected solver source modifications: none
- Verification-module modifications: none
- Phase 13F design modifications: none
- Authorization environment variables: cleared
- Temporary result files: none
- Successful-run inventory modified by this report step: no

---

## 13. What Phase 13F establishes

Within the frozen pilot boundary, Phase 13F establishes successful runtime integration, fail-closed guard operation, finite and complete operator/evolution outputs, exact call and mask counts, zero inherited forcing, independently auditable evidence, and deterministic V1/V2 numerical repetition.

---

## 14. What Phase 13F does not establish

Phase 13F does not establish spatial or temporal convergence, observed order, an asymptotic regime, uncertainty bounds, solver-wide verification, method superiority, physical validation, turbulence, an inertial range, a cascade, a `k^-3` law, or production readiness.

---

## 15. Controlled evidence archive boundary

The controlled archive candidate consists of:

1. `experiments/verification/phase13/phase13F_pilot_20260717T072334Z_0b9a2b9/` containing 51 files;
2. `PHASE13F4_SUCCESSFUL_V2_RUN_FILE_INVENTORY.csv`;
3. `PHASE13F_CONTROLLED_SINGLE_GRID_VERIFICATION_PILOT_COMPLETION_REPORT.md`.

---

## 16. Completion decision

> PASS — Phase 13F controlled single-grid verification pilot is > complete, subject to controlled archival of the successful V2 > result directory, this report, and the successful-run inventory.

No refinement or convergence claim is authorized by this decision.

---

## 17. Recommended next phase

Any refinement study requires a separately designed and explicitly authorized phase that freezes its sequences, errors, acceptance logic, and claim boundaries before additional numerical execution.
