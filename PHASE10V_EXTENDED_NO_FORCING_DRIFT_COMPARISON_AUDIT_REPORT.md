\# Phase 10V Extended No-Forcing Drift Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.58-phase10U-extended-no-forcing-drift-design

\- Audit script: phase10v\_extended\_no\_forcing\_drift\_comparison\_audit.py

\- Audit output: PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT.csv

\- Time-history output: PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_TIME\_HISTORY.csv

\- Pairwise output: PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_PAIRWISE\_SUMMARY.csv

\- Report: PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 10V audits extended no-forcing drift behavior across selectable advection methods:



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

| N | 64 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 5000 |

| final time | 5.0 |

| forcing | zero |

| initial RMS | 0.01 |

| diagnostic interval | every 500 steps |



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

| fd\_centered | 1.000000000000e-02 | 9.999466242702e-03 | 9.999466242702e-01 | -9.720249103554e-05 | -1.067486105431e-04 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 9.999446535699e-03 | 9.999446535699e-01 | -9.881498446585e-05 | -1.106897969551e-04 | PASS |

| arakawa | 1.000000000000e-02 | 9.999446537769e-03 | 9.999446537769e-01 | -9.881498447807e-05 | -1.106893829326e-04 | PASS |



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

| pseudo\_spectral vs fd\_centered | 4.636669462082e-06 | 1.653707681058e-05 | 4.636916960909e-04 | 9.999998924967e-01 | PASS |

| arakawa vs fd\_centered | 2.576301812865e-06 | 7.521338323688e-06 | 2.576439332194e-04 | 9.999999668117e-01 | PASS |

| arakawa vs pseudo\_spectral | 5.291251024269e-06 | 2.123064070454e-05 | 5.291543892333e-04 | 9.999998599978e-01 | PASS |



\## Energy and Enstrophy Pairwise Differences



| Pair | Energy Abs Diff | Enstrophy Abs Diff |

|---|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.158702732573e-12 | 1.970593206029e-10 |

| arakawa vs fd\_centered | 8.158702794406e-12 | 1.970386194768e-10 |

| arakawa vs pseudo\_spectral | 6.183340514956e-20 | 2.070112608893e-14 |



\## Overall Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method drift checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 10V extended no-forcing drift comparison audit | PASS |



\## Main Finding



All three selectable methods remained finite, real, non-explosive, and non-mutating during the extended no-forcing drift audit through final time 5.0.



All three methods showed small negative energy drift and small negative enstrophy drift.



The final pairwise comparisons passed.



Arakawa remained closely aligned with both fd\_centered and pseudo\_spectral.



The arakawa and pseudo\_spectral final energy values were extremely close.



\## What This Confirms



Phase 10V confirms:



\- fd\_centered extended no-forcing drift is stable in this audit

\- pseudo\_spectral extended no-forcing drift is stable in this audit

\- arakawa extended no-forcing drift is stable in this audit

\- no-forcing override worked

\- forcing was zero

\- outputs remained finite and real

\- input fields were not mutated by step\_once\_selectable

\- solver.w remained unchanged

\- run() remained disabled

\- source solver files remained unchanged

\- final pairwise comparisons passed



\## What This Does Not Confirm



Phase 10V does not validate long-time stability.



Phase 10V does not enable SelectableAdvectionSolver.run().



Phase 10V does not validate production simulations.



Phase 10V does not prove turbulence.



Phase 10V does not prove k^-3 scaling.



Phase 10V does not prove a resolved inertial-range cascade.



Phase 10V does not prove Arakawa is production-ready.



\## Recommended Next Phase



Phase 10W — Extended No-Forcing Drift Decision Gate



Purpose:



Summarize Phase 10V and decide whether to proceed to either:



\- N=128 short no-forcing drift

\- longer N=64 no-forcing drift

\- controlled forced-response design



Recommended conservative next step:



Proceed to a decision gate first.



Do not jump directly to forced turbulence experiments.



Do not make k^-3 claims.



Do not enable SelectableAdvectionSolver.run() yet.



\## Final Result



Phase 10V extended no-forcing drift comparison audit:



PASS



Proceed to Phase 10W decision gate.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

