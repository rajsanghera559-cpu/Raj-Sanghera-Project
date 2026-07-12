\# Phase 9A.4 Half-dt Nonlinear Drift Audit Review



\## Checkpoint



\- Branch: phase4\_validation

\- Runner tag: v0.4.29-phase9A4-half-dt-nonlinear-drift-runner

\- Runner script: run\_phase9A4\_nonlinear\_no\_forcing\_drift\_dt\_half.py

\- Audit script: phase9a4\_half\_dt\_nonlinear\_drift\_audit.py

\- Audit output: PHASE9A4\_HALF\_DT\_NONLINEAR\_DRIFT\_AUDIT.csv

\- Source run: experiments/runs/run\_2026-07-12\_00-45-24

\- Reference run: experiments/runs/run\_2026-07-12\_00-38-33

\- Reference audit: PHASE9A3\_NONLINEAR\_DRIFT\_AUDIT.csv



\## Purpose



Phase 9A.4 repeated the Phase 9A.3 nonlinear no-forcing drift test with half the timestep while preserving the same physical comparison time.



The purpose was to test whether the nonlinear drift behavior remained stable and consistent under a smaller timestep.



This was a validation test.



This was not a turbulence claim.



This was not a k^-3 scaling claim.



\## Configuration



| Quantity | Phase 9A.3 | Phase 9A.4 |

|---|---:|---:|

| Re | 1000000 | 1000000 |

| nu | 1.0e-06 | 1.0e-06 |

| Grid | 64 x 64 | 64 x 64 |

| dt | 0.001 | 0.0005 |

| steps | 1001 | 2001 |

| comparison time | 1.0 | 1.0 |

| forcing | zero | zero |

| initial condition | phase6d-like multimode | phase6d-like multimode |

| target RMS | 0.01 | 0.01 |



\## Audit Result



The audit script returned:



| Check | Result |

|---|---:|

| Phase 9A.4 half-dt nonlinear drift audit | FAIL |



The failure was caused by one strict comparison:



| Check | Result |

|---|---:|

| Final enstrophy matches 9A.3 | FAIL |



\## Failed Comparison Detail



| Quantity | Value |

|---|---:|

| Reference 9A.3 final enstrophy | 4.999889986756e-05 |

| Phase 9A.4 final enstrophy | 4.999890041315e-05 |

| Absolute difference | approximately 5.46e-13 |

| Relative difference | approximately 1.09e-08 |



The comparison threshold was effectively too strict for an exact final-state match between nonlinear trajectories with different timestep sizes.



\## Checks That Passed



| Check | Result |

|---|---:|

| Status completed | PASS |

| Git commit starts with 1c1cd19 | PASS |

| Git dirty false | PASS |

| Mode expected | PASS |

| Config expected | PASS |

| Initial invariants finite | PASS |

| Diagnostics finite | PASS |

| Spectrum finite | PASS |

| Energy nonnegative | PASS |

| Enstrophy nonnegative | PASS |

| E\_k4 nonnegative | PASS |

| Spectrum nonnegative | PASS |

| Mode counts positive | PASS |

| Expected diagnostic steps match | PASS |

| Steps increasing | PASS |

| Initial energy/spectrum check | PASS |

| Final energy/spectrum check | PASS |

| Energy abs drift < 1e-3 | PASS |

| Enstrophy abs drift < 1e-3 | PASS |

| Energy not growing materially | PASS |

| Enstrophy not growing materially | PASS |

| Logged energy monotonic nonincreasing | PASS |

| Logged enstrophy monotonic nonincreasing | PASS |

| Final energy matches 9A.3 | PASS |

| Energy drift consistent | PASS |

| Energy drift not worse | PASS |

| Enstrophy drift consistent | PASS |

| Enstrophy drift not worse | PASS |

| k=3 fraction matches 9A.3 | PASS |

| k=4 fraction matches 9A.3 | PASS |

| k>=5 fraction matches 9A.3 | PASS |



\## Drift Results



| Quantity | Phase 9A.4 Result |

|---|---:|

| Energy change initial to final | -1.970962276343e-05 |

| Enstrophy change initial to final | -2.199173708008e-05 |

| Energy change logged step0 to final | -1.969974092886e-05 |

| Enstrophy change logged step0 to final | -2.198066810398e-05 |



Interpretation:



Energy and enstrophy remained finite, nonnegative, and gently decreasing.



There was no material growth.



There was no blow-up.



\## Spectrum Result



| Quantity | Phase 9A.4 Result |

|---|---:|

| Final peak k | 3 |

| Final peak fraction | 8.705346486079e-01 |

| k=3 fraction | 8.705346486079e-01 |

| k=4 fraction | 1.294636410865e-01 |

| k>=5 fraction | 8.343765062185e-07 |



The spectral fractions matched Phase 9A.3 within the audit tolerance.



\## Interpretation



The Phase 9A.4 audit failed technically because one exact final enstrophy comparison was slightly outside the chosen tolerance.



This should be treated as a tolerance-review issue, not as evidence of solver instability.



The physically meaningful checks passed:



\- finite diagnostics

\- nonnegative energy and enstrophy

\- monotonic nonincreasing logged energy

\- monotonic nonincreasing logged enstrophy

\- small drift

\- no material growth

\- spectral fractions consistent with Phase 9A.3



\## Scientific Status



Phase 9A.4 should be classified as:



REVIEW



It should not be classified as a clean PASS yet, because the original audit script returned FAIL.



It should not be classified as a solver failure, because the failure was caused by an overly strict exact-match tolerance on final enstrophy.



\## Recommended Next Step



Phase 9A.4R — Tolerance-Robust Half-dt Nonlinear Drift Re-Audit



Purpose:



Create a revised audit that emphasizes physically meaningful drift consistency rather than exact final-state equality.



The revised audit should preserve the original failed audit result and explicitly document the tolerance correction.



\## Conclusion



Phase 9A.4 produced a successful run with stable nonlinear no-forcing behavior.



The audit script returned FAIL because one exact final enstrophy comparison was too strict.



The correct status is REVIEW pending a tolerance-robust re-audit.

