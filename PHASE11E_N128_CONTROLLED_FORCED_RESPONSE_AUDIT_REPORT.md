\# Phase 11E N128 Controlled Forced-Response Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.3-phase11D-N128-controlled-forced-response-design

\- Audit script: phase11e\_n128\_controlled\_forced\_response\_audit.py

\- Audit output: PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_AUDIT.csv

\- Time-history output: PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_TIME\_HISTORY.csv

\- Pairwise output: PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_PAIRWISE\_SUMMARY.csv

\- Report: PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_AUDIT\_REPORT.md



\## Purpose



Phase 11E audits controlled forced-response behavior at N=128 across selectable advection methods:



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

| forcing | baseline deterministic forcing |

| forcing RMS | 5.000000000000e-03 |

| forcing max abs | 1.000000000000e-02 |

| initial RMS | 0.01 |

| diagnostic interval | every 100 steps |



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

| forcing\_shape\_ok | PASS |

| forcing\_finite | PASS |

| forcing\_real | PASS |

| forcing\_nonzero | PASS |

| forcing\_max\_nonzero | PASS |

| forcing\_identical\_across\_methods | PASS |

| Global checks | PASS |



\## Method Forced-Response Results



| Method | Initial RMS | Final RMS | Final RMS Ratio | Relative Energy Change | Final Energy Ratio | Relative Enstrophy Change | Final Enstrophy Ratio | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 1.395393731695e-02 | 1.395393731695e+00 | 1.169947413938e+00 | 2.169947413938e+00 | 9.471236664540e-01 | 1.947123666454e+00 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 1.395393703669e-02 | 1.395393703669e+00 | 1.169947380129e+00 | 2.169947380129e+00 | 9.471235882397e-01 | 1.947123588240e+00 | PASS |

| arakawa | 1.000000000000e-02 | 1.395393702445e-02 | 1.395393702445e+00 | 1.169947375907e+00 | 2.169947375907e+00 | 9.471235848236e-01 | 1.947123584824e+00 | PASS |



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



The logged monotonic nonincrease checks failed for energy and enstrophy.



This is expected under nonzero forcing and was not used as a hard pass/fail criterion.



\## Final Pairwise Comparisons



| Pair | Diff L2 | Diff Max Abs | Relative Error | Cosine Similarity | Result |

|---|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 3.004886970439e-07 | 1.045365817036e-06 | 2.153433043438e-05 | 9.999999997681e-01 | PASS |

| arakawa vs fd\_centered | 1.611879249104e-07 | 4.699547548927e-07 | 1.155142962514e-05 | 9.999999999333e-01 | PASS |

| arakawa vs pseudo\_spectral | 3.439057255719e-07 | 1.288594578896e-06 | 2.464578453146e-05 | 9.999999996963e-01 | PASS |



\## Energy and Enstrophy Pairwise Differences



| Pair | Energy Abs Diff | Enstrophy Abs Diff |

|---|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.710639127502e-13 | 3.910712140405e-12 |

| arakawa vs fd\_centered | 1.924225193653e-13 | 4.081518543281e-12 |

| arakawa vs pseudo\_spectral | 2.135860661511e-14 | 1.708064028758e-13 |



\## Overall Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method forced-response checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 11E N128 controlled forced-response audit | PASS |



\## Main Finding



All three selectable methods remained finite, real, non-explosive, and non-mutating during the N=128 controlled forced-response audit.



The inherited baseline deterministic forcing was nonzero, finite, real, and identical across methods.



Energy and enstrophy increased under forcing, as expected, but remained inside the predefined non-explosive thresholds.



The final pairwise comparisons passed.



Arakawa remained closely aligned with both fd\_centered and pseudo\_spectral.



\## What This Confirms



Phase 11E confirms:



\- fd\_centered N=128 controlled forced response is stable in this audit

\- pseudo\_spectral N=128 controlled forced response is stable in this audit

\- arakawa N=128 controlled forced response is stable in this audit

\- baseline forcing was applied and verified

\- outputs remained finite and real

\- input fields were not mutated by step\_once\_selectable

\- solver.w remained unchanged

\- run() remained disabled

\- source solver files remained unchanged

\- final pairwise comparisons passed



\## What This Does Not Confirm



Phase 11E does not validate long-time stability.



Phase 11E does not enable SelectableAdvectionSolver.run().



Phase 11E does not validate production simulations.



Phase 11E does not prove turbulence.



Phase 11E does not prove k^-3 scaling.



Phase 11E does not prove a resolved inertial-range cascade.



Phase 11E does not prove Arakawa is production-ready.



\## Recommended Next Phase



Phase 11F — N128 Controlled Forced-Response Decision Gate



Purpose:



Summarize Phase 11E and decide whether to proceed to either:



\- longer N=64 controlled forced-response audit

\- longer N=128 controlled forced-response design

\- spectrum-focused diagnostic design

\- selectable run-loop design



Recommended conservative next step:



Proceed to a decision gate first.



Do not jump directly to turbulence experiments.



Do not make k^-3 claims.



Do not enable SelectableAdvectionSolver.run() yet.



\## Final Result



Phase 11E N128 controlled forced-response audit:



PASS



Proceed to Phase 11F decision gate.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

