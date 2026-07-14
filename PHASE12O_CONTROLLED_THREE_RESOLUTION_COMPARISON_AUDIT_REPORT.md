\# Phase 12O Controlled Three-Resolution Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.40-phase12N-controlled-three-resolution-comparison-design

\- Audit script: phase12o\_controlled\_three\_resolution\_comparison\_audit.py

\- Method summary output: PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_METHOD\_SUMMARY.csv

\- Pairwise trends output: PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_PAIRWISE\_TRENDS.csv

\- Field restriction output: PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_FIELD\_RESTRICTION.csv

\- Report: PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 12O audits structured three-resolution diagnostic comparison metrics using existing outputs from:



\- N64: Phase 11S

\- N128: Phase 11V

\- N256: Phase 12L



This audit does not run a new simulation.



This audit does not modify solver source code.



This audit does not enable SelectableAdvectionSolver.run().



This audit does not prove convergence.



This audit does not prove turbulence.



This audit does not prove k^-3 scaling.



This audit does not prove method superiority.



\## Required File Checks



| File Group | Result |

|---|---:|

| N64 method CSV exists | PASS |

| N64 pairwise CSV exists | PASS |

| N128 method CSV exists | PASS |

| N128 pairwise CSV exists | PASS |

| N256 method CSV exists | PASS |

| N256 pairwise CSV exists | PASS |



\## Global Checks



| Check | Result |

|---|---:|

| SpectralSolver file has no git diff | PASS |

| advection\_operators file has no git diff | PASS |

| selectable\_advection\_solver file has no git diff | PASS |

| All source method/pairwise results PASS | PASS |

| Expected methods present | PASS |

| Expected pairs present | PASS |

| Global checks | PASS |



\## Method Three-Resolution Summary



| Method | N64 Final RMS | N128 Final RMS | N256 Final RMS | N64 Final Energy | N128 Final Energy | N256 Final Energy | Dominant Shell Same | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.383832617489e-02 | 1.383832541415e-02 | 1.383832521066e-02 | 1.081610036476e-05 | 1.081609991096e-05 | 1.081609978949e-05 | PASS | PASS |

| pseudo\_spectral | 1.383832514162e-02 | 1.383832514162e-02 | 1.383832514162e-02 | 1.081609974827e-05 | 1.081609974827e-05 | 1.081609974827e-05 | PASS | PASS |

| arakawa | 1.383832511311e-02 | 1.383832513401e-02 | 1.383832513969e-02 | 1.081609967044e-05 | 1.081609972773e-05 | 1.081609974306e-05 | PASS | PASS |



\## Pairwise Three-Resolution Trends



| Pair | N64 Field Rel L2 | N128 Field Rel L2 | N256 Field Rel L2 | Field Order 64→128 | Field Order 128→256 | N64 Spectrum Rel L2 | N128 Spectrum Rel L2 | N256 Spectrum Rel L2 | Spectrum Order 64→128 | Spectrum Order 128→256 | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.416286809714e-05 | 2.117135768632e-05 | 5.301033204002e-06 | 1.991070079436e+00 | 1.997768307768e+00 | 1.898853630556e-07 | 4.913982615903e-08 | 1.239118238052e-08 | 1.950164043399e+00 | 1.987578896290e+00 | PASS |

| arakawa vs fd\_centered | 4.463033910031e-05 | 1.134297610978e-05 | 2.847534850621e-06 | 1.976225551592e+00 | 1.994013812486e+00 | 1.161741763811e-07 | 3.049532971221e-08 | 7.716663892674e-09 | 1.929629197508e+00 | 1.982539140108e+00 | PASS |

| arakawa vs pseudo\_spectral | 9.526899745687e-05 | 2.414609989113e-05 | 6.057281792013e-06 | 1.980216625149e+00 | 1.995047747966e+00 | 1.688920780038e-07 | 4.385026889381e-08 | 1.106711221916e-08 | 1.945444064601e+00 | 1.986306865743e+00 | PASS |



\## Pairwise Trend Interpretation



The pairwise method-difference metrics decreased monotonically from N64 to N128 to N256.



The observed diagnostic orders were close to 2 for the reported pairwise field and spectrum differences.



This is a strong controlled diagnostic trend.



This is not, by itself, a formal convergence proof.



A formal convergence claim requires a conservative decision gate and precise claim wording.



\## Optional Field-Restriction Comparisons



| Method | N64 vs Restricted N128 Relative RMS Difference | N128 vs Restricted N256 Relative RMS Difference | Restricted Field Observed Order | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 6.299152358022e-05 | 1.587032492782e-05 | 1.988826040104e+00 | PASS |

| pseudo\_spectral | 1.044273181878e-13 | 1.181408609302e-13 | -1.780088601680e-01 | PASS |

| arakawa | 7.112298854627e-05 | 1.808881952675e-05 | 1.975217685640e+00 | PASS |



\## Field-Restriction Interpretation



The fd\_centered and arakawa field-restriction comparisons showed near-second-order observed diagnostic behavior.



The pseudo\_spectral field-restriction comparison produced differences near roundoff level, around 1e-13. Because those differences are near numerical precision, the negative observed order should not be interpreted as evidence against convergence. It is a near-roundoff artifact of the diagnostic ratio.



These field-restriction comparisons are aligned-grid restriction diagnostics.



They are not full spectral projection convergence proofs.



\## Final Checks



| Check | Result |

|---|---:|

| Method three-resolution summary rows pass | PASS |

| Pairwise three-resolution trend rows pass | PASS |

| Field restriction rows acceptable | PASS |

| Overall Phase 12O audit | PASS |



\## Main Finding



Phase 12O passed.



The project successfully compared existing N64, N128, and N256 controlled diagnostic outputs.



The method summaries passed.



The pairwise trend summaries passed.



The optional field-restriction comparisons passed.



The pairwise field and spectrum differences decreased monotonically across the three resolutions.



The observed pairwise diagnostic orders were close to 2.



\## What This Confirms



Phase 12O confirms:



\- completed N64, N128, and N256 outputs can be compared in one structured audit

\- method-level metrics are available at all three resolutions

\- pairwise method-difference trends are available at all three resolutions

\- optional field-restriction comparisons are available

\- diagnostic resolution trends can be reported

\- pairwise field differences decrease from N64 to N128 to N256

\- pairwise spectrum differences decrease from N64 to N128 to N256

\- source-code files remained unchanged

\- no new simulation was run

\- metadata guardrails remain respected



\## What This Does Not Confirm



Phase 12O does not confirm:



\- formal convergence proof

\- general convergence order

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- method superiority

\- production readiness

\- physical cascade behavior

\- statistical steady state behavior



\## Scientific Boundary



Correct statement:



Phase 12O reports structured three-resolution diagnostic comparison metrics. The tested pairwise method-difference metrics decreased under refinement, with observed diagnostic orders near 2 for the tested setup.



Incorrect statement:



Phase 12O proves convergence, turbulence, k^-3 scaling, inertial-range behavior, method superiority, production readiness, or physical cascade behavior.



Those statements are not supported.



\## Recommended Next Phase



Phase 12P — Controlled Three-Resolution Comparison Decision Gate



Purpose:



Document the Phase 12O result and decide what claim language is supported.



Potential cautious claim language:



The controlled three-resolution comparison showed decreasing diagnostic method-difference metrics under grid refinement for the tested setup.



Avoid stronger language unless approved by a decision gate:



The solver is proven convergent.



The solver is second-order convergent.



The solver proves turbulence.



The solver proves k^-3 scaling.



\## Final Result



Phase 12O controlled three-resolution comparison audit:



PASS



Proceed to Phase 12P controlled three-resolution comparison decision gate.

