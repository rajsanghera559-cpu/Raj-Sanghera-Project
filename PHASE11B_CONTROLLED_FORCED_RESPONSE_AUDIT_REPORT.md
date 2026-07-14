\# Phase 11B Controlled Forced-Response Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.0-phase11A-controlled-forced-response-design

\- Audit script: phase11b\_controlled\_forced\_response\_audit.py

\- Audit output: PHASE11B\_CONTROLLED\_FORCED\_RESPONSE\_AUDIT.csv

\- Time-history output: PHASE11B\_CONTROLLED\_FORCED\_RESPONSE\_TIME\_HISTORY.csv

\- Pairwise output: PHASE11B\_CONTROLLED\_FORCED\_RESPONSE\_PAIRWISE\_SUMMARY.csv

\- Report: PHASE11B\_CONTROLLED\_FORCED\_RESPONSE\_AUDIT\_REPORT.md



\## Purpose



Phase 11B audits controlled forced-response behavior across selectable advection methods:



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

| steps | 1000 |

| final time | 1.0 |

| forcing | baseline deterministic forcing |

| initial RMS | 0.01 |

| diagnostic interval | every 100 steps |



\## Baseline Forcing



The inherited baseline forcing was used:



forcing() = 0.01 \* sin(2X) \* cos(2Y)



The audit verified:



| Forcing Check | Result |

|---|---:|

| forcing\_shape\_ok | PASS |

| forcing\_finite | PASS |

| forcing\_real | PASS |

| forcing\_nonzero | PASS |

| forcing\_max\_nonzero | PASS |

| forcing\_identical\_across\_methods | PASS |

| forcing\_rms | 5.000000000000e-03 |

| forcing\_max\_abs | 1.000000000000e-02 |



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



\## Method Forced-Response Results



| Method | Initial RMS | Final RMS | Final RMS Ratio | Relative Energy Change | Final Energy Ratio | Relative Enstrophy Change | Final Enstrophy Ratio | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 1.395393809873e-02 | 1.395393809873e+00 | 1.169947508185e+00 | 2.169947508185e+00 | 9.471238846309e-01 | 1.947123884631e+00 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 1.395393703669e-02 | 1.395393703669e+00 | 1.169947380128e+00 | 2.169947380128e+00 | 9.471235882394e-01 | 1.947123588239e+00 | PASS |

| arakawa | 1.000000000000e-02 | 1.395393699030e-02 | 1.395393699030e+00 | 1.169947364130e+00 | 2.169947364130e+00 | 9.471235752928e-01 | 1.947123575293e+00 | PASS |



\## Detailed Method Checks



Each method passed:



\- forcing\_nonzero

\- finite\_throughout

\- real\_throughout

\- input\_not\_mutated\_each\_step

\- solver\_w\_unchanged

\- run\_disabled

\- final\_rms\_nonexplosive

\- final\_energy\_nonexplosive

\- final\_enstrophy\_nonexplosive

\- overall\_result



The logged monotonic nonincrease checks failed for energy and enstrophy, which is expected under nonzero forcing and was not used as a hard pass/fail criterion.



\## Final Pairwise Comparisons



| Pair | Diff L2 | Diff Max Abs | Relative Error | Cosine Similarity | Result |

|---|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.194534477191e-06 | 4.102300006009e-06 | 8.560554509699e-05 | 9.999999963358e-01 | PASS |

| arakawa vs fd\_centered | 6.341330636077e-07 | 1.840999586033e-06 | 4.544473818940e-05 | 9.999999989674e-01 | PASS |

| arakawa vs pseudo\_spectral | 1.356852597460e-06 | 5.080241515796e-06 | 9.723797619925e-05 | 9.999999952724e-01 | PASS |



\## Energy and Enstrophy Pairwise Differences



| Pair | Energy Abs Diff | Enstrophy Abs Diff |

|---|---:|---:|

| pseudo\_spectral vs fd\_centered | 6.479265789936e-13 | 1.481957328934e-11 |

| arakawa vs fd\_centered | 7.288731843422e-13 | 1.546690450412e-11 |

| arakawa vs pseudo\_spectral | 8.094660534854e-14 | 6.473312147816e-13 |



\## Overall Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method forced-response checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 11B controlled forced-response audit | PASS |



\## Main Finding



All three selectable methods remained finite, real, non-explosive, and non-mutating during the controlled forced-response audit.



The baseline deterministic forcing was nonzero, finite, real, and identical across methods.



Energy and enstrophy increased under forcing, as expected, but remained within the predefined non-explosive thresholds.



The final pairwise comparisons passed.



Arakawa remained closely aligned with both fd\_centered and pseudo\_spectral.



\## What This Confirms



Phase 11B confirms:



\- fd\_centered controlled forced response is stable in this audit

\- pseudo\_spectral controlled forced response is stable in this audit

\- arakawa controlled forced response is stable in this audit

\- baseline forcing was applied and verified

\- outputs remained finite and real

\- input fields were not mutated by step\_once\_selectable

\- solver.w remained unchanged

\- run() remained disabled

\- source solver files remained unchanged

\- final pairwise comparisons passed



\## What This Does Not Confirm



Phase 11B does not validate long-time stability.



Phase 11B does not enable SelectableAdvectionSolver.run().



Phase 11B does not validate production simulations.



Phase 11B does not prove turbulence.



Phase 11B does not prove k^-3 scaling.



Phase 11B does not prove a resolved inertial-range cascade.



Phase 11B does not prove Arakawa is production-ready.



\## Recommended Next Phase



Phase 11C — Controlled Forced-Response Decision Gate



Purpose:



Summarize Phase 11B and decide whether to proceed to either:



\- N=128 controlled forced-response design

\- longer N=64 controlled forced-response design

\- selectable run-loop design

\- spectrum-focused diagnostic design



Recommended conservative next step:



Proceed to a decision gate first.



Do not jump directly to turbulence experiments.



Do not make k^-3 claims.



Do not enable SelectableAdvectionSolver.run() yet.



\## Final Result



Phase 11B controlled forced-response audit:



PASS



Proceed to Phase 11C decision gate.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

