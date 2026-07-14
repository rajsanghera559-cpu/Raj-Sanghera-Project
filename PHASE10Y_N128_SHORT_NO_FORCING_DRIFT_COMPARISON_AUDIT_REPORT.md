\# Phase 10Y N128 Short No-Forcing Drift Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.61-phase10X-N128-short-no-forcing-drift-design

\- Audit script: phase10y\_n128\_short\_no\_forcing\_drift\_comparison\_audit.py

\- Audit output: PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT.csv

\- Time-history output: PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_TIME\_HISTORY.csv

\- Pairwise output: PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_PAIRWISE\_SUMMARY.csv

\- Report: PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 10Y audits short no-forcing drift behavior at N=128 across selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The audit repeatedly calls:



step\_once\_selectable(w)



inside a standalone audit script.



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not run a production simulation.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Audit Parameters



| Parameter | Value |

|---|---:|

| N | 128 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| forcing | zero |

| initial RMS | 0.01 |

| diagnostic interval | every 100 steps |



\## No-Forcing Mechanism



The audit used an audit-local subclass:



NoForcingSelectableAdvectionSolver



This subclass overrode only:



forcing()



and returned:



np.zeros\_like(self.w)



This preserved the source files:



\- project/solver/spectral\_solver.py

\- project/solver/selectable\_advection\_solver.py

\- project/solver/advection\_operators.py



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

| advection\_operators file has no git diff | PASS |

| Invalid method rejected | PASS |

| Global checks | PASS |



\## Method Drift Results



| Method | Initial RMS | Final RMS | Final RMS Ratio | Relative Energy Drift | Relative Enstrophy Drift | Result |

|---|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 9.999889516448e-03 | 9.999889516448e-01 | -1.974688318096e-05 | -2.209658840179e-05 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 9.999889308042e-03 | 9.999889308042e-01 | -1.976387175611e-05 | -2.213826897368e-05 | PASS |

| arakawa | 1.000000000000e-02 | 9.999889308047e-03 | 9.999889308047e-01 | -1.976387175109e-05 | -2.213826810985e-05 | PASS |



\## Detailed Method Checks



Each method passed:



\- forcing\_zero

\- finite\_throughout

\- real\_throughout

\- input\_not\_mutated\_each\_step

\- solver\_w\_unchanged

\- run\_disabled

\- final\_rms\_nonexplosive

\- final\_energy\_nonexplosive

\- final\_enstrophy\_nonexplosive

\- energy\_monotone\_nonincreasing\_logged

\- enstrophy\_monotone\_nonincreasing\_logged

\- overall\_result



\## Final Pairwise Comparisons



| Pair | Diff L2 | Diff Max Abs | Relative Error | Cosine Similarity | Result |

|---|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 2.332308684811e-07 | 8.542671117596e-07 | 2.332334453271e-05 | 9.999999997280e-01 | PASS |

| arakawa vs fd\_centered | 1.311142138760e-07 | 3.932642454697e-07 | 1.311156624884e-05 | 9.999999999140e-01 | PASS |

| arakawa vs pseudo\_spectral | 2.682684437413e-07 | 1.066735613978e-06 | 2.682714132901e-05 | 9.999999996402e-01 | PASS |



\## Energy and Enstrophy Pairwise Differences



| Pair | Energy Abs Diff | Enstrophy Abs Diff |

|---|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.595677473836e-14 | 2.084028594498e-12 |

| arakawa vs fd\_centered | 8.595674932737e-14 | 2.083985402594e-12 |

| arakawa vs pseudo\_spectral | 2.541098841763e-20 | 4.319190404639e-17 |



\## Overall Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method drift checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 10Y N128 short no-forcing drift comparison audit | PASS |



\## Main Finding



All three selectable methods remained finite, real, non-explosive, and non-mutating during the N=128 short no-forcing drift audit through final time 1.0.



All three methods showed small negative energy drift and small negative enstrophy drift.



The final pairwise comparisons passed.



Arakawa remained closely aligned with both fd\_centered and pseudo\_spectral.



The arakawa and pseudo\_spectral final energy values were extremely close.



\## What This Confirms



Phase 10Y confirms:



\- fd\_centered N=128 short no-forcing drift is stable in this audit

\- pseudo\_spectral N=128 short no-forcing drift is stable in this audit

\- arakawa N=128 short no-forcing drift is stable in this audit

\- no-forcing override worked

\- forcing was zero

\- outputs remained finite and real

\- input fields were not mutated by step\_once\_selectable

\- solver.w remained unchanged

\- run() remained disabled

\- source solver files remained unchanged

\- final pairwise comparisons passed



\## What This Does Not Confirm



Phase 10Y does not validate long-time stability.



Phase 10Y does not enable SelectableAdvectionSolver.run().



Phase 10Y does not validate production simulations.



Phase 10Y does not prove turbulence.



Phase 10Y does not prove k^-3 scaling.



Phase 10Y does not prove a resolved inertial-range cascade.



Phase 10Y does not prove Arakawa is production-ready.



\## Recommended Next Phase



Phase 10Z — N128 Short No-Forcing Drift Decision Gate



Purpose:



Summarize Phase 10Y and decide whether to proceed to either:



\- longer N=128 no-forcing drift

\- N=64 controlled forced-response design

\- selectable run-loop design



Recommended conservative next step:



Proceed to a decision gate first.



Do not jump directly to forced turbulence experiments.



Do not make k^-3 claims.



Do not enable SelectableAdvectionSolver.run() yet.



\## Final Result



Phase 10Y N128 short no-forcing drift comparison audit:



PASS



Proceed to Phase 10Z decision gate.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

