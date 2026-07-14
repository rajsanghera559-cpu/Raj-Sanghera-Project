\# Phase 10T Short No-Forcing Drift Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.56-phase10S-short-no-forcing-drift-comparison-audit

\- Current previous commit: b7886b5

\- Decision gate file: PHASE10T\_SHORT\_NO\_FORCING\_DRIFT\_DECISION\_GATE.md



\## Purpose



Phase 10T is a documentation-only decision gate.



The purpose is to summarize Phase 10S and decide whether the selectable advection methods are ready for the next controlled no-forcing drift stage.



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Current Solver Status



The validated baseline solver remains:



project/solver/spectral\_solver.py



The selectable solver remains:



project/solver/selectable\_advection\_solver.py



The selectable solver currently supports:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The selectable solver currently includes:



\- compute\_advection(w)

\- compute\_rhs\_selectable(w)

\- step\_once\_selectable(w)



The selectable solver still has:



run() intentionally disabled



This remains correct.



\## Phase 10S Summary



Phase 10S performed a short no-forcing drift comparison across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The audit used an audit-local subclass:



NoForcingSelectableAdvectionSolver



This subclass overrode only:



forcing()



and returned:



np.zeros\_like(self.w)



This preserved all solver source files.



\## Phase 10S Parameters



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



The initial condition was the controlled phase6d\_like\_multimode field.



\## Phase 10S Global Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method drift checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 10S short no-forcing drift comparison audit | PASS |



\## Phase 10S Method Results



| Method | Initial RMS | Final RMS | Final RMS Ratio | Relative Energy Drift | Relative Enstrophy Drift | Result |

|---|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 9.999890095267e-03 | 9.999890095267e-01 | -1.969980531063e-05 | -2.198082581009e-05 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 9.999889308042e-03 | 9.999889308042e-01 | -1.976387196671e-05 | -2.213826916559e-05 | PASS |

| arakawa | 1.000000000000e-02 | 9.999889308058e-03 | 9.999889308058e-01 | -1.976387196420e-05 | -2.213826585037e-05 | PASS |



\## Phase 10S Final Pairwise Results



| Pair | Diff L2 | Relative Error | Cosine Similarity | Result |

|---|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 9.271077934012e-07 | 9.271179828667e-05 | 9.999999957023e-01 | PASS |

| arakawa vs fd\_centered | 5.157686719299e-07 | 5.157743405340e-05 | 9.999999986699e-01 | PASS |

| arakawa vs pseudo\_spectral | 1.058264569273e-06 | 1.058276283540e-04 | 9.999999944003e-01 | PASS |



\## Evidence Supporting Advancement



Phase 10S supports advancement because:



1\. All methods remained finite throughout the short drift audit.



2\. All methods remained real-valued throughout the short drift audit.



3\. All methods passed the no-forcing check.



4\. All methods had small negative energy drift.



5\. All methods had small negative enstrophy drift.



6\. No method showed explosive RMS growth.



7\. No method showed explosive energy growth.



8\. No method showed explosive enstrophy growth.



9\. Pairwise final comparisons passed.



10\. Arakawa remained closely aligned with both fd\_centered and pseudo\_spectral.



11\. SpectralSolver remained unchanged.



12\. SelectableAdvectionSolver remained unchanged.



13\. SelectableAdvectionSolver.run() remained disabled.



\## Evidence Against Production Readiness



Phase 10S does not justify production readiness because:



1\. The test was short.



2\. The test used only N=64.



3\. The test used one controlled initial condition.



4\. The test used no forcing.



5\. The test did not use a production run loop.



6\. The test did not validate long-time behavior.



7\. The test did not validate forced dynamics.



8\. The test did not validate spectra.



9\. The test did not validate turbulence.



10\. The test did not validate k^-3 scaling.



\## Decision



Decision:



PROCEED TO A SLIGHTLY EXTENDED NO-FORCING DRIFT DESIGN.



Do not proceed directly to forced turbulence experiments.



Do not proceed directly to k^-3 spectrum experiments.



Do not enable SelectableAdvectionSolver.run() yet.



Do not replace SpectralSolver.



The next phase should be a design phase for a longer or slightly higher-resolution no-forcing drift audit.



\## Recommended Next Phase



Phase 10U — Extended No-Forcing Drift Design



Purpose:



Design a controlled extension of Phase 10S.



Recommended options:



Option A:



\- N=64

\- Re=1000000

\- dt=0.001

\- steps=5000

\- final time=5.0

\- no forcing

\- same phase6d\_like\_multimode initial condition



Option B:



\- N=128

\- Re=1000000

\- dt=0.001

\- steps=1000

\- final time=1.0

\- no forcing

\- same phase6d\_like\_multimode initial condition



Recommended first choice:



Option A



Reason:



A longer N=64 test extends the time horizon without adding resolution cost or changing too many variables at once.



\## Guardrails for Phase 10U



Phase 10U should remain design-only.



Phase 10U should not run the extended audit.



Phase 10U should not modify solver source files.



Phase 10U should preserve these rules:



\- SpectralSolver unchanged

\- SelectableAdvectionSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- no forcing

\- no production simulation

\- no turbulence claim

\- no k^-3 claim



\## Recommended Phase 10V



After Phase 10U design, Phase 10V may run the extended no-forcing drift audit.



Phase 10V should still use an audit-local no-forcing subclass.



Phase 10V should still call:



step\_once\_selectable(w)



inside the audit script.



Phase 10V should not call:



SelectableAdvectionSolver.run()



Phase 10V should not call:



SpectralSolver.run()



\## Scientific Boundary



Correct statement after Phase 10T:



The selectable methods passed a short no-forcing drift audit and are ready for a carefully designed extended no-forcing drift audit.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Final Result



Phase 10T decision gate:



PASS



Proceed to Phase 10U design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not run forced turbulence experiments.



Do not make turbulence claims.



Do not make k^-3 claims.

