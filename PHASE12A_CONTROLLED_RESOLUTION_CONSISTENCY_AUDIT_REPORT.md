\# Phase 12A Controlled Resolution-Consistency Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.26-phase11Z-controlled-convergence-study-design

\- Audit script: phase12a\_controlled\_resolution\_consistency\_audit.py

\- Method output: PHASE12A\_CONTROLLED\_RESOLUTION\_CONSISTENCY\_AUDIT.csv

\- Pairwise output: PHASE12A\_CONTROLLED\_RESOLUTION\_CONSISTENCY\_PAIRWISE\_TRENDS.csv

\- Report: PHASE12A\_CONTROLLED\_RESOLUTION\_CONSISTENCY\_AUDIT\_REPORT.md



\## Purpose



Phase 12A audits controlled N64/N128 resolution-consistency using existing Phase 11S and Phase 11V outputs.



This phase reads existing CSV files.



This phase does not run a new simulation.



This phase does not modify solver source code.



This phase does not prove convergence.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



This phase does not prove method superiority.



\## Source Files Used



| File | Purpose | Result |

|---|---|---:|

| PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv | N64 method results | PASS |

| PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv | N64 pairwise results | PASS |

| PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv | N128 method results | PASS |

| PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv | N128 pairwise results | PASS |



\## Global Checks



| Check | Result |

|---|---:|

| SpectralSolver file has no git diff | PASS |

| advection\_operators file has no git diff | PASS |

| selectable\_advection\_solver file has no git diff | PASS |

| N64 method results PASS | PASS |

| N128 method results PASS | PASS |

| N64 pairwise results PASS | PASS |

| N128 pairwise results PASS | PASS |

| N64 methods present | PASS |

| N128 methods present | PASS |

| N64 pairs present | PASS |

| N128 pairs present | PASS |

| N64 resolution check | PASS |

| N128 resolution check | PASS |

| Global checks | PASS |



\## Method Resolution-Consistency Results



| Method | N64 Final RMS | N128 Final RMS | RMS Relative Difference | N64 Final Energy | N128 Final Energy | Energy Relative Difference | N64 Final Enstrophy | N128 Final Enstrophy | Enstrophy Relative Difference | Dominant Shell Same | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.383832617489e-02 | 1.383832541415e-02 | 5.497303879188e-08 | 1.081610036476e-05 | 1.081609991096e-05 | 4.195578109131e-08 | 9.574963566127e-05 | 9.574962513398e-05 | 1.099460867460e-07 | PASS | PASS |

| pseudo\_spectral | 1.383832514162e-02 | 1.383832514162e-02 | 8.674667151485e-14 | 1.081609974827e-05 | 1.081609974827e-05 | 1.827807569182e-13 | 9.574962136261e-05 | 9.574962136262e-05 | 1.760773937507e-13 | PASS | PASS |

| arakawa | 1.383832511311e-02 | 1.383832513401e-02 | 1.510052713742e-09 | 1.081609967044e-05 | 1.081609972773e-05 | 5.296415919228e-09 | 9.574962096811e-05 | 9.574962125729e-05 | 3.020110175400e-09 | PASS | PASS |



\## Pairwise Resolution-Trend Results



| Pair | N64 Field Relative L2 Difference | N128 Field Relative L2 Difference | Field Reduction Ratio N64/N128 | N64 Spectrum Relative L2 Difference | N128 Spectrum Relative L2 Difference | Spectrum Reduction Ratio N64/N128 | Dominant Shell Match Both | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.416286809714e-05 | 2.117135768632e-05 | 3.975317471090e+00 | 1.898853630556e-07 | 4.913982615903e-08 | 3.864184672552e+00 | PASS | PASS |

| arakawa vs fd\_centered | 4.463033910031e-05 | 1.134297610978e-05 | 3.934623388814e+00 | 1.161741763811e-07 | 3.049532971221e-08 | 3.809572727280e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 9.526899745687e-05 | 2.414609989113e-05 | 3.945523206084e+00 | 1.688920780038e-07 | 4.385026889381e-08 | 3.851563109288e+00 | PASS | PASS |



\## Final Checks



| Check | Result |

|---|---:|

| Method consistency rows pass | PASS |

| Pairwise trend rows pass | PASS |

| Overall Phase 12A audit | PASS |



\## Main Finding



Phase 12A passed.



The existing N64 and N128 controlled selectable diagnostic outputs were successfully compared.



All method-level consistency rows passed.



All pairwise trend rows passed.



The N128 pairwise field differences were smaller than the corresponding N64 pairwise field differences.



The N128 pairwise spectrum differences were smaller than the corresponding N64 pairwise spectrum differences.



The recorded field reduction ratios were approximately 3.9 to 4.0.



The recorded spectrum reduction ratios were approximately 3.8 to 3.9.



\## Interpretation



This is controlled resolution-consistency evidence.



It shows that the N64 and N128 controlled diagnostic results can be compared cleanly and that the recorded pairwise method differences decreased at N128.



This is useful evidence for the project.



This is not a convergence proof.



A convergence proof or convergence-rate claim requires a dedicated convergence audit with defined norms, refinement logic, acceptance criteria, and preferably at least three resolutions or a validated reference solution.



\## What This Confirms



Phase 12A confirms:



\- required Phase 11S files exist

\- required Phase 11V files exist

\- Phase 11S method results were PASS

\- Phase 11V method results were PASS

\- Phase 11S pairwise results were PASS

\- Phase 11V pairwise results were PASS

\- method-level N64/N128 consistency metrics are finite

\- pairwise N64/N128 trend metrics are finite

\- dominant shell matched across N64 and N128 for each method

\- pairwise field differences decreased at N128 in the recorded comparisons

\- pairwise spectrum differences decreased at N128 in the recorded comparisons

\- SpectralSolver remained unchanged

\- advection\_operators remained unchanged

\- selectable\_advection\_solver remained unchanged



\## What This Does Not Confirm



Phase 12A does not confirm:



\- convergence

\- convergence order

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- method superiority

\- production readiness

\- statistical steady state behavior

\- physical cascade behavior

\- validated production simulation behavior



\## Scientific Boundary



Correct statement:



Phase 12A reports controlled N64/N128 resolution-consistency metrics using existing Phase 11S and Phase 11V outputs.



Incorrect statement:



Phase 12A proves convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Recommended Next Phase



Phase 12B — N256 Controlled Selectable Diagnostic Feasibility Design



Purpose:



Design a safe feasibility test before attempting any N256 controlled comparison.



Recommended first N256 feasibility test:



| Parameter | Value |

|---|---:|

| N | 256 |

| Re | 1000 |

| dt | 0.001 |

| steps | 100 |

| final time | 0.1 |

| log\_every | 10 |

| method | fd\_centered first only |

| forcing | inherited baseline deterministic forcing |



Reason:



N256 has four times as many grid points as N128 and sixteen times as many grid points as N64.



The project should not jump directly to a full N256 three-method final-time-1.0 audit without a feasibility check.



\## Final Result



Phase 12A controlled resolution-consistency audit:



PASS



Proceed to Phase 12B N256 controlled selectable diagnostic feasibility design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims yet.



Do not make method superiority claims.

