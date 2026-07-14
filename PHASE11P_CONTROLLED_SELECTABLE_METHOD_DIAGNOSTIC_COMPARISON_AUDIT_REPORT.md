\# Phase 11P Controlled Selectable Method Diagnostic Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.15-phase11O-controlled-selectable-method-diagnostic-comparison-design

\- Audit script: phase11p\_controlled\_selectable\_method\_diagnostic\_comparison\_audit.py

\- Method output: PHASE11P\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- Pairwise output: PHASE11P\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv

\- Report: PHASE11P\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 11P audits the controlled selectable diagnostic comparison across:



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

| steps | 20 |

| log\_every | 1 |

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



| Method | Final RMS | Final Energy | Final Enstrophy | Dominant Shell | Low-k Fraction k<=4 | High-k Fraction k>=10 | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.006775597736e-02 | 5.145430176190e-06 | 5.067985520984e-05 | 3.0 | 9.999999996692e-01 | 1.017029198268e-20 | PASS |

| pseudo\_spectral | 1.006775597704e-02 | 5.145430176058e-06 | 5.067985520665e-05 | 3.0 | 9.999999996451e-01 | 1.292692891086e-20 | PASS |

| arakawa | 1.006775597704e-02 | 5.145430176057e-06 | 5.067985520664e-05 | 3.0 | 9.999999996790e-01 | 8.681960300832e-21 | PASS |



\## Spectrum Energy Checks



| Method | Spectrum Direct Relative Error | Result |

|---|---:|---:|

| fd\_centered | 4.938554707285e-16 | PASS |

| pseudo\_spectral | 4.938554707412e-16 | PASS |

| arakawa | 1.646184902471e-16 | PASS |



\## Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.851056115083e-06 | 2.555586828077e-11 | 6.300178196328e-11 | 3.150077798779e-11 | 1.058371389290e-10 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 1.028800714180e-06 | 2.566303491792e-11 | 6.306248505037e-11 | 3.153110364650e-11 | 5.316866655706e-11 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 2.112634740028e-06 | 1.071666371508e-13 | 6.070308709217e-14 | 3.032565871363e-14 | 1.023728022848e-10 | 1.000000000000e+00 | PASS | PASS |



\## Final Checks



| Check | Result |

|---|---:|

| Shared initial\_w unchanged across all runs | PASS |

| All method audits pass | PASS |

| All pairwise comparisons pass | PASS |

| Overall Phase 11P audit | PASS |



\## Main Finding



All three selectable diagnostic methods completed the same short controlled diagnostic run.



The methods produced finite, real, comparable outputs with valid metadata guardrails.



The final spectra were strongly aligned, with dominant shell k = 3.0 for all methods.



Pairwise comparisons were successfully computed and passed.



\## Interpretation



This is a controlled diagnostic comparison.



The audit shows that fd\_centered, pseudo\_spectral, and arakawa can all be run through the selectable diagnostic loop under identical short controlled conditions.



The audit does not establish physical superiority of any method.



The audit does not establish turbulence.



The audit does not establish k^-3 scaling.



The audit does not establish an inertial range.



\## What This Confirms



Phase 11P confirms:



\- run\_selectable\_diagnostic works for fd\_centered

\- run\_selectable\_diagnostic works for pseudo\_spectral

\- run\_selectable\_diagnostic works for arakawa

\- all methods preserve metadata guardrails

\- all methods produce finite final states

\- all methods produce real final states

\- all methods write diagnostic outputs

\- all methods write spectrum outputs

\- all pairwise comparison metrics are finite

\- all methods agree on dominant shell k = 3.0

\- SelectableAdvectionSolver.run() remains disabled

\- SpectralSolver remains unchanged

\- no turbulence claim is present

\- no k\_minus\_3 claim is present



\## What This Does Not Confirm



Phase 11P does not confirm:



\- production readiness

\- long-time stability

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- Arakawa superiority

\- pseudo\_spectral superiority

\- statistical steady state behavior

\- long forced-response behavior



\## Recommended Next Phase



Phase 11Q — Controlled Selectable Method Diagnostic Comparison Decision Gate



Purpose:



Document the Phase 11P result and decide whether to proceed to a longer controlled selectable comparison.



Recommended decision:



Proceed to Phase 11Q decision gate.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make method superiority claims.



\## Final Result



Phase 11P controlled selectable method diagnostic comparison audit:



PASS



Proceed to Phase 11Q decision gate.

