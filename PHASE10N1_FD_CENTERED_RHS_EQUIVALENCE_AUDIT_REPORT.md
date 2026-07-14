\# Phase 10N.1 fd\_centered RHS Equivalence Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.48-phase10N-selectable-rhs-scaffold

\- Audit script: phase10n1\_fd\_centered\_rhs\_equivalence\_audit.py

\- Audit output: PHASE10N1\_FD\_CENTERED\_RHS\_EQUIVALENCE\_AUDIT.csv

\- Report: PHASE10N1\_FD\_CENTERED\_RHS\_EQUIVALENCE\_AUDIT\_REPORT.md



\## Purpose



Phase 10N.1 audits whether the selectable-advection solver RHS path reproduces the baseline fd\_centered right-hand-side logic.



The comparison target is:



baseline-style RHS from SpectralSolver logic



against:



SelectableAdvectionSolver(advection\_method="fd\_centered").compute\_rhs\_selectable(w)



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

| SpectralSolver file has no git diff | PASS |

| SelectableAdvectionSolver file has no git diff | PASS |

| Shape mismatch rejected | PASS |

| Global checks | PASS |



\## Baseline RHS Definition



The direct baseline RHS was transcribed from SpectralSolver.run():



rhs = -adv + laplacian\_spectral(w) + forcing()



where:



adv = u \* omega\_x + v \* omega\_y



and:



\- u, v are computed from the spectral streamfunction

\- omega\_x and omega\_y use centered finite differences

\- diffusion uses laplacian\_spectral(w)

\- forcing uses the baseline deterministic forcing



\## Selectable RHS Definition



The selectable RHS is:



SelectableAdvectionSolver(advection\_method="fd\_centered").compute\_rhs\_selectable(w)



For fd\_centered, this calls:



advection\_fd\_centered(self, w)



then computes:



rhs = -adv + diffusion + forcing



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



\## N=64 Results



| Field | Baseline RHS L2 | Selectable RHS L2 | Diff L2 | Diff Max Abs | Relative Error | Cosine | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 4.960000000000e-03 | 4.960000000000e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| low\_mode\_pair | 4.960142574079e-03 | 4.960142574079e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| phase6d\_like\_multimode | 4.945396861220e-03 | 4.945396861220e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| higher\_smooth\_multimode | 5.017818001443e-03 | 5.017818001443e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |



\## N=128 Results



| Field | Baseline RHS L2 | Selectable RHS L2 | Diff L2 | Diff Max Abs | Relative Error | Cosine | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 4.960000000000e-03 | 4.960000000000e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| low\_mode\_pair | 4.960142625366e-03 | 4.960142625366e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| phase6d\_like\_multimode | 4.945399906223e-03 | 4.945399906223e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |

| higher\_smooth\_multimode | 5.017820656918e-03 | 5.017820656918e-03 | 0.000000000000e+00 | 0.000000000000e+00 | 0.000000000000e+00 | 1.000000000000e+00 | PASS |



\## Metadata and Guardrail Checks



Each tested case passed:



\- metadata\_method\_ok

\- metadata\_rhs\_method\_ok

\- metadata\_variant\_ok

\- metadata\_baseline\_ok

\- metadata\_run\_disabled\_ok

\- metadata\_no\_turbulence\_claim

\- metadata\_no\_k\_minus\_3\_claim

\- run\_disabled



The selectable solver still does not enable production run behavior.



\## Main Finding



The selectable fd\_centered RHS is exactly equivalent to the direct baseline RHS transcription.



For every tested field and resolution:



\- diff\_l2 = 0

\- diff\_max\_abs = 0

\- relative\_error = 0

\- cosine\_similarity = 1



This is stronger than a tolerance-based match.



It is exact equality for the tested cases.



\## What This Confirms



Phase 10N.1 confirms:



\- compute\_rhs\_selectable works for fd\_centered

\- fd\_centered selectable RHS reproduces baseline RHS logic exactly

\- the selectable RHS does not mutate input w

\- the selectable RHS does not mutate solver.w

\- shape mismatch is rejected

\- metadata guardrails are present

\- run() remains disabled

\- SpectralSolver remains unchanged



\## What This Does Not Confirm



Phase 10N.1 does not validate one-step time integration.



Phase 10N.1 does not validate long-time stability.



Phase 10N.1 does not validate Arakawa time evolution.



Phase 10N.1 does not enable production runs.



Phase 10N.1 does not prove turbulence.



Phase 10N.1 does not prove k^-3 scaling.



Phase 10N.1 does not prove a resolved inertial-range cascade.



\## Recommended Next Phase



Phase 10O — Selectable One-Step fd\_centered Equivalence Design



Purpose:



Design the next narrow validation step: a one-step RK2-style selectable update that can be compared against the baseline one-step update.



The next phase should remain careful:



\- do not enable run()

\- do not run long simulations

\- do not replace SpectralSolver

\- do not test Arakawa time evolution yet



\## Final Result



Phase 10N.1 fd\_centered RHS equivalence audit:



PASS



Proceed to Phase 10O design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

