\# Phase 10W Extended No-Forcing Drift Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.59-phase10V-extended-no-forcing-drift-comparison-audit

\- Current previous commit: 505af7b

\- Decision gate file: PHASE10W\_EXTENDED\_NO\_FORCING\_DRIFT\_DECISION\_GATE.md



\## Purpose



Phase 10W is a documentation-only decision gate.



The purpose is to summarize Phase 10V and decide the next controlled validation step.



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



\## Phase 10V Summary



Phase 10V performed an extended no-forcing drift comparison across:



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



\## Phase 10V Parameters



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



The initial condition was the controlled phase6d\_like\_multimode field.



\## Phase 10V Global Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method drift checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 10V extended no-forcing drift comparison audit | PASS |



\## Phase 10V Method Results



| Method | Initial RMS | Final RMS | Final RMS Ratio | Relative Energy Drift | Relative Enstrophy Drift | Result |

|---|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 9.999466242702e-03 | 9.999466242702e-01 | -9.720249103554e-05 | -1.067486105431e-04 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 9.999446535699e-03 | 9.999446535699e-01 | -9.881498446585e-05 | -1.106897969551e-04 | PASS |

| arakawa | 1.000000000000e-02 | 9.999446537769e-03 | 9.999446537769e-01 | -9.881498447807e-05 | -1.106893829326e-04 | PASS |



\## Phase 10V Pairwise Results



| Pair | Diff L2 | Relative Error | Cosine Similarity | Result |

|---|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 4.636669462082e-06 | 4.636916960909e-04 | 9.999998924967e-01 | PASS |

| arakawa vs fd\_centered | 2.576301812865e-06 | 2.576439332194e-04 | 9.999999668117e-01 | PASS |

| arakawa vs pseudo\_spectral | 5.291251024269e-06 | 5.291543892333e-04 | 9.999998599978e-01 | PASS |



\## Evidence Supporting Advancement



Phase 10V supports advancement because:



1\. All methods remained finite through final time 5.0.



2\. All methods remained real-valued.



3\. All methods passed the zero-forcing check.



4\. All methods had small negative energy drift.



5\. All methods had small negative enstrophy drift.



6\. No method showed explosive RMS growth.



7\. No method showed explosive energy growth.



8\. No method showed explosive enstrophy growth.



9\. Pairwise final comparisons passed.



10\. Arakawa remained closely aligned with both fd\_centered and pseudo\_spectral.



11\. SpectralSolver remained unchanged.



12\. SelectableAdvectionSolver remained unchanged.



13\. advection\_operators remained unchanged.



14\. SelectableAdvectionSolver.run() remained disabled.



\## Evidence Against Production Readiness



Phase 10V does not justify production readiness because:



1\. The audit was still no-forcing.



2\. The audit used only N=64.



3\. The audit used one controlled initial condition.



4\. The audit did not validate a selectable production run loop.



5\. The audit did not validate forced dynamics.



6\. The audit did not validate spectra.



7\. The audit did not validate long-time turbulence behavior.



8\. The audit did not validate k^-3 scaling.



9\. The audit did not prove a resolved inertial-range cascade.



10\. The audit did not make Arakawa production-ready.



\## Decision



Decision:



PROCEED TO N=128 SHORT NO-FORCING DRIFT DESIGN.



Do not proceed directly to forced turbulence experiments.



Do not proceed directly to k^-3 spectrum experiments.



Do not enable SelectableAdvectionSolver.run() yet.



Do not replace SpectralSolver.



\## Rationale for Next Step



The project has now passed:



\- N=64 short no-forcing drift through final time 1.0

\- N=64 extended no-forcing drift through final time 5.0



The next conservative question is:



Do the same methods remain stable and aligned at higher resolution for a short no-forcing drift audit?



This changes one major variable:



N from 64 to 128



It should keep the time horizon shorter:



final time 1.0



This avoids mixing higher resolution and longer duration at the same time.



\## Recommended Next Phase



Phase 10X — N128 Short No-Forcing Drift Design



Purpose:



Design a controlled N=128 no-forcing drift audit.



Recommended parameters:



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

| initial field | phase6d\_like\_multimode |



Methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



\## Guardrails for Phase 10X



Phase 10X should remain design-only.



Phase 10X should not run the N=128 audit.



Phase 10X should not modify solver source files.



Phase 10X should preserve these rules:



\- SpectralSolver unchanged

\- SelectableAdvectionSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- no forcing

\- no production simulation

\- no turbulence claim

\- no k^-3 claim



\## Recommended Phase 10Y



After Phase 10X design, Phase 10Y may run the N=128 short no-forcing drift audit.



Phase 10Y should still use an audit-local no-forcing subclass.



Phase 10Y should still call:



step\_once\_selectable(w)



inside the audit script.



Phase 10Y should not call:



SelectableAdvectionSolver.run()



Phase 10Y should not call:



SpectralSolver.run()



\## Scientific Boundary



Correct statement after Phase 10W:



The selectable methods passed an extended controlled no-forcing drift audit at N=64 through final time 5.0 and are ready for a carefully designed N=128 short no-forcing drift audit.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Final Result



Phase 10W decision gate:



PASS



Proceed to Phase 10X design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not run forced turbulence experiments.



Do not make turbulence claims.



Do not make k^-3 claims.

