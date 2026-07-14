\# Phase 11S Longer Controlled Selectable Method Diagnostic Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.18-phase11R-longer-controlled-selectable-method-diagnostic-comparison-design

\- Audit script: phase11s\_longer\_controlled\_selectable\_method\_diagnostic\_comparison\_audit.py

\- Method output: PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- Pairwise output: PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv

\- Report: PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 11S audits the longer controlled selectable diagnostic comparison across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The audit uses:



run\_selectable\_diagnostic(...)



This audit does not call SpectralSolver.run().



This audit does not enable SelectableAdvectionSolver.run().



This audit does not prove turbulence.



This audit does not prove k^-3 scaling.



This audit does not prove method superiority.



\## Parameters



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| log\_every | 100 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



\## Global Checks



| Check | Result |

|---|---:|

| SpectralSolver import | PASS |

| SelectableAdvectionSolver import | PASS |

| Supported methods exact | PASS |

| Default method fd\_centered | PASS |

| compute\_rhs\_selectable exists | PASS |

| step\_once\_selectable exists | PASS |

| run\_selectable\_diagnostic exists | PASS |

| SpectralSolver file has no git diff | PASS |

| advection\_operators file has no git diff | PASS |

| selectable\_advection\_solver file has no git diff | PASS |

| All grid shapes same | PASS |

| All dx same | PASS |

| All dt same | PASS |

| All nu same | PASS |

| All dealias masks same | PASS |

| All forcing fields same | PASS |

| Global checks | PASS |



\## Method Results



| Method | Final RMS | Final Energy | Final Enstrophy | RMS Ratio | Energy Ratio | Enstrophy Ratio | Dominant Shell | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.383832617489e-02 | 1.081610036476e-05 | 9.574963566127e-05 | 1.383832617489e+00 | 2.137703915855e+00 | 1.914992713225e+00 | 3.0 | PASS |

| pseudo\_spectral | 1.383832514162e-02 | 1.081609974827e-05 | 9.574962136261e-05 | 1.383832514162e+00 | 2.137703794011e+00 | 1.914992427252e+00 | 3.0 | PASS |

| arakawa | 1.383832511311e-02 | 1.081609967044e-05 | 9.574962096811e-05 | 1.383832511311e+00 | 2.137703778629e+00 | 1.914992419362e+00 | 3.0 | PASS |



\## Spectrum Results



| Method | Low-k Fraction k<=4 | High-k Fraction k>=10 | Spectrum Direct Relative Error | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 9.999994138821e-01 | 3.940095470626e-14 | 1.566244614397e-16 | PASS |

| pseudo\_spectral | 9.999993713576e-01 | 5.145804156150e-14 | 1.566244703670e-16 | PASS |

| arakawa | 9.999994315888e-01 | 3.456885984340e-14 | 1.566244714940e-16 | PASS |



\## Time-History Diagnostics



| Method | Diagnostics Min RMS | Diagnostics Max RMS | Result |

|---|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 1.383832617489e-02 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 1.383832514162e-02 | PASS |

| arakawa | 1.000000000000e-02 | 1.383832511311e-02 | PASS |



\## Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.416286809714e-05 | 5.699784851319e-08 | 1.493339006612e-07 | 7.466695312720e-08 | 1.898853630556e-07 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 4.463033910031e-05 | 6.419339335323e-08 | 1.534539447487e-07 | 7.672697532158e-08 | 1.161741763811e-07 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 9.526899745687e-05 | 7.195545250174e-09 | 4.120044702725e-09 | 2.060022348196e-09 | 1.688920780038e-07 | 1.000000000000e+00 | PASS | PASS |



\## Final Checks



| Check | Result |

|---|---:|

| Shared initial\_w unchanged across all runs | PASS |

| All method audits pass | PASS |

| All pairwise comparisons pass | PASS |

| Overall Phase 11S audit | PASS |



\## Main Finding



Phase 11S passed.



All three selectable diagnostic methods completed the longer controlled diagnostic run through final time 1.0.



The methods produced finite, real, comparable outputs with valid metadata guardrails.



All three methods agreed on dominant shell:



k = 3.0



Pairwise comparison metrics were finite and passed.



\## Interpretation



This is a longer controlled diagnostic comparison.



It confirms that the selectable diagnostic pathway remains stable and auditable through final time 1.0 for:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The spectra remain strongly low-k dominated.



The high-k energy fraction remains extremely small.



This is not evidence of turbulence.



This is not evidence of k^-3 scaling.



This is not evidence of an inertial range.



This is not evidence of method superiority.



\## What This Confirms



Phase 11S confirms:



\- run\_selectable\_diagnostic works for fd\_centered through final time 1.0

\- run\_selectable\_diagnostic works for pseudo\_spectral through final time 1.0

\- run\_selectable\_diagnostic works for arakawa through final time 1.0

\- all methods preserve metadata guardrails

\- all methods produce finite final states

\- all methods produce real final states

\- all methods write diagnostic outputs

\- all methods write spectrum outputs

\- all method time-history diagnostics remain finite

\- all pairwise comparison metrics are finite

\- all methods agree on dominant shell k = 3.0

\- SelectableAdvectionSolver.run() remains disabled

\- SpectralSolver remains unchanged

\- advection\_operators remains unchanged

\- no turbulence claim is present

\- no k\_minus\_3 claim is present



\## What This Does Not Confirm



Phase 11S does not confirm:



\- production readiness

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- Arakawa superiority

\- pseudo\_spectral superiority

\- statistical steady state behavior

\- physical cascade behavior

\- long-time asymptotic stability

\- validated production simulation behavior



\## Recommended Next Phase



Phase 11T — Longer Controlled Selectable Method Diagnostic Comparison Decision Gate



Purpose:



Document the Phase 11S result and decide whether to proceed to a higher-resolution controlled selectable comparison or another controlled diagnostic branch.



Recommended decision:



Proceed to Phase 11T decision gate.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make method superiority claims.



\## Final Result



Phase 11S longer controlled selectable method diagnostic comparison audit:



PASS



Proceed to Phase 11T decision gate.

