\# Phase 10P.1 fd\_centered One-Step Equivalence Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.51-phase10P-selectable-one-step-scaffold

\- Audit script: phase10p1\_fd\_centered\_one\_step\_equivalence\_audit.py

\- Audit output: PHASE10P1\_FD\_CENTERED\_ONE\_STEP\_EQUIVALENCE\_AUDIT.csv

\- Report: PHASE10P1\_FD\_CENTERED\_ONE\_STEP\_EQUIVALENCE\_AUDIT\_REPORT.md



\## Purpose



Phase 10P.1 audits whether the selectable-advection solver one-step path reproduces the baseline fd\_centered one-step RK2-style update.



The comparison target is:



baseline one-step update logic transcribed from SpectralSolver.run()



against:



SelectableAdvectionSolver(advection\_method="fd\_centered").step\_once\_selectable(w)



This phase does not modify SpectralSolver.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not run a production simulation.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Global Checks



| Check | Result |

|---|---:|

| SpectralSolver import | PASS |

| SelectableAdvectionSolver import | PASS |

| Supported methods check | PASS |

| Default method fd\_centered | PASS |

| compute\_rhs\_selectable exists | PASS |

| step\_once\_selectable exists | PASS |

| SpectralSolver file has no git diff | PASS |

| SelectableAdvectionSolver file has no git diff | PASS |

| Shape mismatch rejected | PASS |

| Global checks | PASS |



\## Baseline One-Step Definition



The baseline one-step update was transcribed from SpectralSolver.run():



1\. Compute k1 from baseline fd\_centered RHS.

2\. Compute w1 = w + dt \* k1.

3\. Compute k2 from baseline fd\_centered RHS at w1.

4\. Compute w\_new = w + 0.5 \* dt \* (k1 + k2).

5\. Apply the baseline 2/3 spectral dealiasing mask.

6\. Return the dealiased real field.



The audit did not call SpectralSolver.run().



Reason:



SpectralSolver.run() is a full loop with diagnostics and file output. This audit isolates one-step numerical equivalence.



\## Selectable One-Step Definition



The selectable one-step update was:



SelectableAdvectionSolver(advection\_method="fd\_centered").step\_once\_selectable(w)



This uses:



compute\_rhs\_selectable(w)



and applies the same RK2-style structure and post-step 2/3 dealiasing mask.



\## Test Fields



The audit used four controlled fields:



| Field | Classification |

|---|---|

| single\_mode\_k2\_2 | controlled\_single\_mode\_reference |

| low\_mode\_pair | low\_k\_nonlinear |

| phase6d\_like\_multimode | phase6d\_like\_low\_k\_nonlinear |

| higher\_smooth\_multimode | higher\_smooth\_nonlinear |



The audit tested:



\- N=64

\- N=128

\- Re=1000

\- dt=0.005

\- steps=1



\## N=64 Results



| Field | Baseline Next L2 | Selectable Next L2 | Diff L2 | Diff Max Abs | Relative Error | Cosine | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 5.024799504000e-03 | 5.024799504000e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| low\_mode\_pair | 6.269745120476e-03 | 6.269745120476e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| phase6d\_like\_multimode | 1.001689141379e-02 | 1.001689141379e-02 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| higher\_smooth\_multimode | 9.997969950135e-03 | 9.997969950135e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |



\## N=128 Results



| Field | Baseline Next L2 | Selectable Next L2 | Diff L2 | Diff Max Abs | Relative Error | Cosine | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 5.024799504000e-03 | 5.024799504000e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| low\_mode\_pair | 6.269745120475e-03 | 6.269745120475e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| phase6d\_like\_multimode | 1.001689141377e-02 | 1.001689141377e-02 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| higher\_smooth\_multimode | 9.997969950116e-03 | 9.997969950116e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |



\## Guardrail Checks



Each tested case passed:



\- finite\_all

\- real\_all

\- input\_w\_unchanged

\- baseline\_solver\_w\_unchanged

\- selectable\_solver\_w\_unchanged

\- exact\_match

\- strict\_equivalence

\- metadata\_method\_ok

\- metadata\_rhs\_method\_ok

\- metadata\_step\_method\_ok

\- metadata\_step\_status\_ok

\- metadata\_variant\_ok

\- metadata\_baseline\_ok

\- metadata\_run\_disabled\_ok

\- metadata\_no\_turbulence\_claim

\- metadata\_no\_k\_minus\_3\_claim

\- run\_disabled



\## Main Finding



The selectable fd\_centered one-step update is exactly equivalent to the direct baseline one-step update transcription.



For every tested field and resolution:



\- diff\_l2 = 0

\- diff\_max\_abs = 0

\- relative\_error = 0

\- cosine\_similarity = 1



This is exact equality for the tested cases.



No fallback tolerance was needed.



\## What This Confirms



Phase 10P.1 confirms:



\- step\_once\_selectable works for fd\_centered

\- fd\_centered selectable one-step update reproduces baseline one-step logic exactly

\- post-step 2/3 dealiasing placement matches the baseline

\- compute\_rhs\_selectable remains usable inside one-step logic

\- input w is not mutated

\- baseline solver.w is not mutated

\- selectable solver.w is not mutated

\- shape mismatch is rejected

\- metadata guardrails are present

\- run() remains disabled

\- SpectralSolver remains unchanged



\## What This Does Not Confirm



Phase 10P.1 does not validate long-time time evolution.



Phase 10P.1 does not validate SelectableAdvectionSolver.run().



Phase 10P.1 does not validate Arakawa time evolution.



Phase 10P.1 does not validate pseudo\_spectral time evolution.



Phase 10P.1 does not validate production runs.



Phase 10P.1 does not prove turbulence.



Phase 10P.1 does not prove k^-3 scaling.



Phase 10P.1 does not prove a resolved inertial-range cascade.



\## Recommended Next Phase



Phase 10Q — Selectable One-Step Operator Comparison Design



Purpose:



Design a controlled one-step comparison across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The next phase should remain design-first.



Recommended guardrails:



\- do not enable run()

\- do not run long simulations

\- do not replace SpectralSolver

\- do not make turbulence claims

\- do not make k^-3 claims



\## Final Result



Phase 10P.1 fd\_centered one-step equivalence audit:



PASS



Proceed to Phase 10Q design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

