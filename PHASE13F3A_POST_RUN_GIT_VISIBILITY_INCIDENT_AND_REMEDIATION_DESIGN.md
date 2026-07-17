# Phase 13F.3A Post-Run Git-Visibility Incident and Remediation Design

## 1. Status

**Phase 13F.3 is not complete.**

The controlled runner returned exit code 2 during its final Git-status boundary. The numerical cases and persistent output audits completed, but the complete runner process did not return PASS.

## 2. Frozen execution identity

- Run identifier: `phase13F_pilot_20260716T060052Z_3af22b8`
- Authorized commit: `3af22b838666389f172fc15e439f7663031ca09b`
- Authorized tag: `v0.5.54-phase13F2-controlled-pilot-runner`
- Grid: `N = 16`
- Numerical cases: `10`
- Refinement sequence: none
- Observed order: none
- Convergence claim: none
- Physical-validation claim: none

## 3. Preserved physical evidence

- Run-manifest status: PASS
- Run-manifest case count: 10
- Case directories: 10
- Persistent files: 51
- Temporary files: 0
- Case metadata status: 10/10 PASS
- Case checks status: 10/10 PASS
- Run-manifest SHA-256: `F3CC9B6ADB336BFC884FA3F582952A881EA198A55C2CDA6679FC271109539A60`
- Aggregate file-inventory SHA-256: `4E8F2DF95FE9927405821D7B70BD92E105B50BCC80FE2E1C498FBA7CC51F966A`
- Detailed inventory: `PHASE13F3A_FAILED_RUN_FILE_INVENTORY.csv`

The aggregate inventory digest is calculated over each sorted relative path, a NUL separator, the uppercase SHA-256 of that file, and a final newline.

## 4. Numerical case records

| Case ID | L2 RMS | Linf | Relative L2 | Finite |
|---|---:|---:|---:|---|
| L_EQUAL_EIGENVALUE_DECAY_V1__N16__Re1000__dt0.001__steps2__t00__method_none | 7.861840858770107e-16 | 2.4424906541753444e-15 | 7.861982373179191e-16 | True |
| M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_arakawa | 0.0001785724849725756 | 0.00035464767290904753 | 0.00015181747002297968 | True |
| M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_fd_centered | 0.00013756420982325132 | 0.0003156334257187205 | 0.00011695334980797137 | True |
| M_TWO_RATE_NONLINEAR_MMS_V1__N16__Re1000__dt0.001__steps2__t00__method_pseudo_spectral | 1.5316384659309008e-09 | 3.608834786561488e-09 | 1.3021573672070365e-09 | True |
| O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_arakawa | 0.08955452032487404 | 0.17773869592451086 | 0.17440366545240318 | True |
| O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_fd_centered | 0.06898904138010331 | 0.15818301702345894 | 0.13435325932280862 | True |
| O1_BANDLIMITED_TWO_MODE_V1__N16__Re1000__dt0.001__steps0__t00__method_pseudo_spectral | 1.091106739980582e-15 | 3.9968028886505635e-15 | 2.124884530251693e-15 | True |
| O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_arakawa | 0.010531522048619802 | 0.02933301167337761 | 0.16325293710430838 | True |
| O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_fd_centered | 0.013991590444227953 | 0.03893020836035124 | 0.2168887103151569 | True |
| O2_ANALYTIC_BROAD_SPECTRUM_V1__N16__Re1000__dt0.001__steps0__t00__method_pseudo_spectral | 5.393723983088192e-09 | 1.2003614834749099e-08 | 8.361006871599293e-08 | True |

These values are preserved pilot observations only. They are not a refinement study, an observed-order result, a method ranking, a convergence claim, or a physical-validation claim.

## 5. Failure location

The runner completed all ten case writes and the physical post-run checks. It then called ordinary Git status and required at least one entry beginning with:

```text
?? experiments/verification/phase13/<run-id>/
```

Ordinary Git status returned no entries, causing:

```text
RuntimeError: Git status does not contain the authorized result files
```

## 6. Root cause

The repository `.gitignore` contains the rule `/experiments/`. The authorized output root is inside that ignored directory. Ordinary `git status --porcelain=v1 --untracked-files=all` therefore hides the result files and cannot produce the `??` entries required by runner version V1.

This is a runner/repository Git-visibility integration defect. It is not evidence of a failed numerical case, corrupted output, solver mutation, missing manifest, or incomplete file write.

## 7. Remediation decision

1. Preserve `.gitignore` unchanged.
2. Preserve the failed run unchanged as incident evidence.
3. Do not modify protected solver files.
4. Do not modify the Phase 13 exact-reference, harness, or output-schema modules.
5. Create a corrected runner version V2.
6. Keep the ordinary clean-tree Git-status check in preflight.
7. Replace the defective repository-wide post-run status expectation with a validated, path-scoped ignored-file inventory.
8. The proposed Git query is:

```text
git ls-files --others --ignored --exclude-standard -- experiments/verification/phase13/<validated-run-id>/
```

9. Compare that Git inventory exactly against the 51 physically observed files for only the selected run directory.
10. The dynamic path must be derived solely from the already validated run identifier.
11. Do not rerun the pilot until V2 passes syntax, static security, boundary, hash, commit, tag, and remote-checkpoint gates.

## 8. Current decision gate

- Numerical output layer: PASS
- Persistent physical-output audit: PASS
- Git-visibility post-run boundary: FAIL
- Complete Phase 13F.3 runner status: FAIL
- Existing run accepted as final Phase 13F pilot: NO
- Rerun authorized: NO
- Runner correction authorized for design and static implementation: YES

## 9. Prohibited interpretations

This incident and its preserved numerical files do not establish formal convergence, an observed order of accuracy, turbulence behavior, a k^-3 law, method superiority, production readiness, or physical validation.
