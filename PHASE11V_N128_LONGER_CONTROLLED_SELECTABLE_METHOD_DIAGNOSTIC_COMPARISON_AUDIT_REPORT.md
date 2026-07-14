\# Phase 11V N128 Longer Controlled Selectable Method Diagnostic Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.21-phase11U-N128-longer-controlled-selectable-method-diagnostic-comparison-design

\- Audit script: phase11v\_N128\_longer\_controlled\_selectable\_method\_diagnostic\_comparison\_audit.py

\- Method output: PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- Pairwise output: PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv

\- Report: PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 11V audits the N=128 longer controlled selectable diagnostic comparison across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The audit uses:



run\_selectable\_diagnostic(...)



This audit does not call SpectralSolver.run().



This audit does not enable SelectableAdvectionSolver.run().



This audit does not prove turbulence.



This audit does not prove k^-3 scaling.



This audit does not prove convergence.



This audit does not prove method superiority.



\## Parameters



| Parameter | Value |

|---|---:|

| N | 128 |

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

| fd\_centered | 1.383832541415e-02 | 1.081609991096e-05 | 9.574962513398e-05 | 1.383832541415e+00 | 2.137703826166e+00 | 1.914992502680e+00 | 3.0 | PASS |

| pseudo\_spectral | 1.383832514162e-02 | 1.081609974827e-05 | 9.574962136262e-05 | 1.383832514162e+00 | 2.137703794011e+00 | 1.914992427252e+00 | 3.0 | PASS |

| arakawa | 1.383832513401e-02 | 1.081609972773e-05 | 9.574962125729e-05 | 1.383832513401e+00 | 2.137703789951e+00 | 1.914992425146e+00 | 3.0 | PASS |



\## Spectrum Results



| Method | Low-k Fraction k<=4 | High-k Fraction k>=10 | Spectrum Direct Relative Error | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 9.999993822143e-01 | 4.811172943166e-14 | 6.264978720440e-16 | PASS |

| pseudo\_spectral | 9.999993713576e-01 | 5.145804105620e-14 | 4.698734111008e-16 | PASS |

| arakawa | 9.999993869243e-01 | 4.663544254778e-14 | 4.698734119932e-16 | PASS |



\## Time-History Diagnostics



| Method | Diagnostics Min RMS | Diagnostics Max RMS | Result |

|---|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 1.383832541415e-02 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 1.383832514162e-02 | PASS |

| arakawa | 1.000000000000e-02 | 1.383832513401e-02 | PASS |



\## Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 2.117135768632e-05 | 1.504188750238e-08 | 3.938765425646e-08 | 1.969382730585e-08 | 4.913982615903e-08 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 1.134297610978e-05 | 1.694119928233e-08 | 4.048776482117e-08 | 2.024388254876e-08 | 3.049532971221e-08 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 2.414609989113e-05 | 1.899311808512e-09 | 1.100110608040e-09 | 5.500552537478e-10 | 4.385026889381e-08 | 1.000000000000e+00 | PASS | PASS |



\## Final Checks



| Check | Result |

|---|---:|

| Shared initial\_w unchanged across all runs | PASS |

| All method audits pass | PASS |

| All pairwise comparisons pass | PASS |

| Overall Phase 11V audit | PASS |



\## Main Finding



Phase 11V passed.



All three selectable diagnostic methods completed the N=128 longer controlled diagnostic run through final time 1.0.



The methods produced finite, real, comparable outputs with valid metadata guardrails.



All three methods agreed on dominant shell:



k = 3.0



Pairwise comparison metrics were finite and passed.



\## N64 to N128 Context



Phase 11S previously passed the same longer controlled diagnostic comparison at N=64.



Phase 11V repeats the controlled comparison at N=128.



The broad diagnostic behavior remained consistent:



\- finite final states

\- real final states

\- dominant shell k = 3.0

\- low-k dominated spectra

\- very small high-k energy fraction

\- finite pairwise method differences

\- metadata guardrails preserved



This is not a convergence proof.



A convergence claim would require a separately designed convergence-study phase.



\## Interpretation



This is a higher-resolution controlled diagnostic comparison.



It confirms that the selectable diagnostic pathway remains stable and auditable through final time 1.0 at N=128 for:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The spectra remain strongly low-k dominated.



The high-k energy fraction remains extremely small.



This is not evidence of turbulence.



This is not evidence of k^-3 scaling.



This is not evidence of an inertial range.



This is not evidence of convergence.



This is not evidence of method superiority.



\## What This Confirms



Phase 11V confirms:



\- run\_selectable\_diagnostic works for fd\_centered at N=128 through final time 1.0

\- run\_selectable\_diagnostic works for pseudo\_spectral at N=128 through final time 1.0

\- run\_selectable\_diagnostic works for arakawa at N=128 through final time 1.0

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



Phase 11V does not confirm:



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

\- convergence



\## Recommended Next Phase



Phase 11W — N128 Longer Controlled Selectable Method Diagnostic Comparison Decision Gate



Purpose:



Document the Phase 11V result and decide whether to proceed to a controlled N64/N128 comparison summary or a dedicated convergence-study design.



Recommended decision:



Proceed to Phase 11W decision gate.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims.



Do not make method superiority claims.



\## Final Result



Phase 11V N128 longer controlled selectable method diagnostic comparison audit:



PASS



Proceed to Phase 11W decision gate.

