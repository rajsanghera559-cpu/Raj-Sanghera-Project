\# Phase 9A.4R Tolerance-Robust Nonlinear Drift Re-Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.30-phase9A4-half-dt-nonlinear-drift-review

\- Re-audit script: phase9a4R\_tolerance\_robust\_nonlinear\_drift\_reaudit.py

\- Re-audit output: PHASE9A4R\_TOLERANCE\_ROBUST\_NONLINEAR\_DRIFT\_REAUDIT.csv

\- Phase 9A.4 run folder: experiments/runs/run\_2026-07-12\_00-45-24

\- Phase 9A.3 reference run folder: experiments/runs/run\_2026-07-12\_00-38-33

\- Strict Phase 9A.4 audit CSV: PHASE9A4\_HALF\_DT\_NONLINEAR\_DRIFT\_AUDIT.csv

\- Phase 9A.3 reference CSV: PHASE9A3\_NONLINEAR\_DRIFT\_AUDIT.csv



\## Purpose



Phase 9A.4R performs a tolerance-robust re-audit of the Phase 9A.4 half-dt nonlinear no-forcing drift test.



The original strict Phase 9A.4 audit returned FAIL because one exact final enstrophy comparison against Phase 9A.3 was too strict for nonlinear timestep comparison.



This re-audit preserves the original FAIL result and evaluates the run using physically meaningful tolerances.



This is a validation re-audit.



This is not a turbulence claim.



This is not a k^-3 scaling claim.



\## Original Strict Audit Result



| Check | Result |

|---|---:|

| Strict Phase 9A.4 original result | FAIL |

| Strict failure preserved | PASS |



The original strict audit failed because:



| Quantity | Value |

|---|---:|

| Reference 9A.3 final enstrophy | 4.999889986756e-05 |

| Phase 9A.4 final enstrophy | 4.999890041315e-05 |

| Relative difference | approximately 1.09e-08 |



This difference is small and does not indicate material solver instability.



\## Metadata and Structure



| Check | Result |

|---|---:|

| Run ID | run\_2026-07-12\_00-45-24 |

| Metadata OK | PASS |

| Actual steps | \[0, 500, 1000, 1500, 2000] |

| Expected steps | \[0, 500, 1000, 1500, 2000] |

| Steps OK | PASS |

| Finite OK | PASS |

| Nonnegative OK | PASS |



\## Energy and Spectrum Consistency



| Quantity | Result |

|---|---:|

| Initial energy | 5.059681223644e-06 |

| Final energy | 5.059581499236e-06 |

| Initial E/spectrum relative error | 1.674083622692e-16 |

| Final E/spectrum relative error | 0.000000000000e+00 |

| Energy/spectrum OK | PASS |



\## Drift Results



| Quantity | Result |

|---|---:|

| Energy change | -1.970962276343e-05 |

| Enstrophy change | -2.199173708008e-05 |

| Drift small OK | PASS |



Interpretation:



Energy and enstrophy decreased slightly.



The drift was small and non-material.



There was no energy or enstrophy growth.



\## Spectral Shape



| Quantity | Result |

|---|---:|

| Peak k | 3 |

| Peak fraction | 8.705346486079e-01 |

| k=3 fraction | 8.705346486079e-01 |

| k=4 fraction | 1.294636410865e-01 |

| k>=5 fraction | 8.343765062185e-07 |

| Spectrum shape OK | PASS |



The spectrum remained consistent with the Phase 9A.3 nonlinear drift test.



\## Robust Comparison to Phase 9A.3



| Quantity | Result |

|---|---:|

| Final energy relative diff vs 9A.3 | 9.818086265509e-09 |

| Final enstrophy relative diff vs 9A.3 | 1.091193117353e-08 |

| Final E\_k4 relative diff vs 9A.3 | 3.065933972342e-08 |

| Energy drift absolute diff | 9.817892754733e-09 |

| Enstrophy drift absolute diff | 1.091169120121e-08 |

| k=3 fraction absolute diff | 9.884140173000e-10 |

| k=4 fraction absolute diff | 2.698184647931e-09 |

| k>=5 fraction absolute diff | 8.341603517106e-10 |

| Robust 9A.3 comparison OK | PASS |



\## Overall Result



Phase 9A.4R tolerance-robust re-audit: PASS



\## Interpretation



The Phase 9A.4 half-dt nonlinear drift run is stable under physically meaningful tolerance checks.



The original strict FAIL is preserved as an audit-design issue, not hidden.



The tolerance-robust re-audit supports the conclusion that Phase 9A.4 is consistent with Phase 9A.3 for the tested nonlinear no-forcing drift case.



\## What This Confirms



Phase 9A.4R confirms:



\- the Phase 9A.4 run completed cleanly

\- metadata and diagnostic structure are valid

\- energy and spectrum diagnostics are internally consistent

\- energy and enstrophy drift remained small

\- spectral shape remained consistent with Phase 9A.3

\- the original strict audit failure was caused by tolerance choice, not material solver instability



\## What This Does Not Confirm



Phase 9A.4R does not prove turbulence.



Phase 9A.4R does not prove k^-3 scaling.



Phase 9A.4R does not prove long-time nonlinear stability.



Phase 9A.4R does not prove a resolved inertial-range cascade.



Phase 9A.4R does not make the solver a fully spectral Navier-Stokes solver.



\## Conclusion



Phase 9A.4R passes as a tolerance-robust nonlinear drift re-audit.



The project should classify the Phase 9A.4 sequence as:



Original strict audit: FAIL

Review classification: tolerance issue

Tolerance-robust re-audit: PASS



Recommended next step:



Phase 9A.5 — Nonlinear Drift Decision Gate



Purpose:



Summarize Phases 9A.1 through 9A.4R and decide whether the current solver is sufficient for controlled nonlinear exploratory runs or whether an Arakawa/full-spectral advection upgrade should be prioritized.

