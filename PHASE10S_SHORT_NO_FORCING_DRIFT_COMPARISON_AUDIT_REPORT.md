\# Phase 10S Short No-Forcing Drift Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.55-phase10R-short-no-forcing-drift-design

\- Audit script: phase10s\_short\_no\_forcing\_drift\_comparison\_audit.py

\- Audit output: PHASE10S\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT.csv

\- Time-history output: PHASE10S\_SHORT\_NO\_FORCING\_DRIFT\_TIME\_HISTORY.csv

\- Pairwise output: PHASE10S\_SHORT\_NO\_FORCING\_DRIFT\_PAIRWISE\_SUMMARY.csv

\- Report: PHASE10S\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 10S audits short no-forcing drift behavior across selectable advection methods:



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



\## No-Forcing Mechanism



The audit used an audit-local subclass:



NoForcingSelectableAdvectionSolver



This subclass overrides only:



forcing()



and returns:



np.zeros\_like(self.w)



This preserves the source files:



\- project/solver/spectral\_solver.py

\- project/solver/selectable\_advection\_solver.py

\- project/solver/advection\_operators.py



The audit verified:



forcing\_zero: PASS



for each method.



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



\## Audit Parameters



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| forcing | zero |

| initial RMS | 0.01 |

| diagnostic interval | every 100 steps |



\## Initial Field



The audit used the controlled phase6d\_like\_multimode field:



\- sin(2X) \* cos(2Y)

\- 0.75 \* sin(3X) \* cos(Y)

\- 0.50 \* sin(X) \* cos(4Y)

\- 0.35 \* cos(4X - 2Y)



The field was rescaled to RMS 0.01.



\## Method Drift Results



| Method | Initial RMS | Final RMS | Final RMS Ratio | Relative Energy Drift | Relative Enstrophy Drift | Result |

|---|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 9.999890095267e-03 | 9.999890095267e-01 | -1.969980531063e-05 | -2.198082581009e-05 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 9.999889308042e-03 | 9.999889308042e-01 | -1.976387196671e-05 | -2.213826916559e-05 | PASS |

| arakawa | 1.000000000000e-02 | 9.999889308058e-03 | 9.999889308058e-01 | -1.976387196420e-05 | -2.213826585037e-05 | PASS |



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

| pseudo\_spectral vs fd\_centered | 9.271077934012e-07 | 3.357209194163e-06 | 9.271179828667e-05 | 9.999999957023e-01 | PASS |

| arakawa vs fd\_centered | 5.157686719299e-07 | 1.530423721559e-06 | 5.157743405340e-05 | 9.999999986699e-01 | PASS |

| arakawa vs pseudo\_spectral | 1.058264569273e-06 | 4.205002282468e-06 | 1.058276283540e-04 | 9.999999944003e-01 | PASS |



\## Energy and Enstrophy Pairwise Differences



| Pair | Energy Abs Diff | Enstrophy Abs Diff |

|---|---:|---:|

| pseudo\_spectral vs fd\_centered | 3.241568568541e-13 | 7.872167774961e-12 |

| arakawa vs fd\_centered | 3.241568441486e-13 | 7.872002014001e-12 |

| arakawa vs pseudo\_spectral | 1.270549420881e-20 | 1.657609596459e-16 |



\## Overall Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method drift checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 10S short no-forcing drift comparison audit | PASS |



\## Main Finding



All three selectable methods remained finite, real, non-explosive, and non-mutating during the short no-forcing drift audit.



The three methods showed small negative energy and enstrophy drift.



The arakawa and pseudo\_spectral methods remained closely aligned with fd\_centered over this short controlled drift test.



The arakawa and pseudo\_spectral final states were especially close to each other in energy.



\## What This Confirms



Phase 10S confirms:



\- fd\_centered short no-forcing drift is stable in this audit

\- pseudo\_spectral short no-forcing drift is stable in this audit

\- arakawa short no-forcing drift is stable in this audit

\- no-forcing override worked

\- forcing was zero

\- outputs remained finite and real

\- input fields were not mutated by step\_once\_selectable

\- solver.w remained unchanged

\- run() remained disabled

\- source solver files remained unchanged

\- pairwise final comparisons passed



\## What This Does Not Confirm



Phase 10S does not validate long-time stability.



Phase 10S does not enable SelectableAdvectionSolver.run().



Phase 10S does not validate production simulations.



Phase 10S does not prove turbulence.



Phase 10S does not prove k^-3 scaling.



Phase 10S does not prove a resolved inertial-range cascade.



Phase 10S does not prove Arakawa is production-ready.



\## Recommended Next Phase



Phase 10T — Short No-Forcing Drift Decision Gate



Purpose:



Summarize Phase 10S and decide whether to proceed to a slightly longer or higher-resolution no-forcing drift audit.



Recommended decision:



Proceed cautiously to a longer diagnostic drift design only after documenting the Phase 10S result.



Do not jump to forced turbulence experiments.



Do not make k^-3 claims.



Do not enable SelectableAdvectionSolver.run() yet.



\## Final Result



Phase 10S short no-forcing drift comparison audit:



PASS



Proceed to Phase 10T decision gate.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

