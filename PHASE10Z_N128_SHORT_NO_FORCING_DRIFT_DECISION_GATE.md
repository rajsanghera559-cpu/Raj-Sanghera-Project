\# Phase 10Z N128 Short No-Forcing Drift Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.62-phase10Y-N128-short-no-forcing-drift-comparison-audit

\- Current previous commit: 6e37447

\- Decision gate file: PHASE10Z\_N128\_SHORT\_NO\_FORCING\_DRIFT\_DECISION\_GATE.md



\## Purpose



Phase 10Z is a documentation-only decision gate.



The purpose is to summarize Phase 10Y and decide the next controlled validation step.



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



\## Recent Validation Chain



The project has now passed:



| Phase | Result |

|---|---:|

| Phase 10P.1 fd\_centered one-step equivalence | PASS |

| Phase 10Q.1 selectable one-step operator comparison | PASS |

| Phase 10S short no-forcing drift, N=64, final time 1.0 | PASS |

| Phase 10V extended no-forcing drift, N=64, final time 5.0 | PASS |

| Phase 10Y short no-forcing drift, N=128, final time 1.0 | PASS |



\## Phase 10Y Summary



Phase 10Y performed a short no-forcing drift comparison at N=128 across:



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



\## Phase 10Y Parameters



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



\## Phase 10Y Global Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method drift checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 10Y N128 short no-forcing drift comparison audit | PASS |



\## Phase 10Y Method Results



| Method | Initial RMS | Final RMS | Final RMS Ratio | Relative Energy Drift | Relative Enstrophy Drift | Result |

|---|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.000000000000e-02 | 9.999889516448e-03 | 9.999889516448e-01 | -1.974688318096e-05 | -2.209658840179e-05 | PASS |

| pseudo\_spectral | 1.000000000000e-02 | 9.999889308042e-03 | 9.999889308042e-01 | -1.976387175611e-05 | -2.213826897368e-05 | PASS |

| arakawa | 1.000000000000e-02 | 9.999889308047e-03 | 9.999889308047e-01 | -1.976387175109e-05 | -2.213826810985e-05 | PASS |



\## Phase 10Y Pairwise Results



| Pair | Diff L2 | Relative Error | Cosine Similarity | Result |

|---|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 2.332308684811e-07 | 2.332334453271e-05 | 9.999999997280e-01 | PASS |

| arakawa vs fd\_centered | 1.311142138760e-07 | 1.311156624884e-05 | 9.999999999140e-01 | PASS |

| arakawa vs pseudo\_spectral | 2.682684437413e-07 | 2.682714132901e-05 | 9.999999996402e-01 | PASS |



\## Evidence Supporting Advancement



Phase 10Y supports advancement because:



1\. All methods remained finite at N=128.



2\. All methods remained real-valued.



3\. All methods passed the zero-forcing check.



4\. All methods showed small negative energy drift.



5\. All methods showed small negative enstrophy drift.



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



Phase 10Y does not justify production readiness because:



1\. The audit was still no-forcing.



2\. The audit was short.



3\. The audit used one controlled initial condition.



4\. The audit did not validate a selectable production run loop.



5\. The audit did not validate forced dynamics.



6\. The audit did not validate spectra.



7\. The audit did not validate turbulence.



8\. The audit did not validate k^-3 scaling.



9\. The audit did not prove a resolved inertial-range cascade.



10\. The audit did not make Arakawa production-ready.



\## Decision



Decision:



PROCEED TO CONTROLLED FORCED-RESPONSE DESIGN.



Do not proceed directly to turbulence experiments.



Do not proceed directly to k^-3 spectrum experiments.



Do not enable SelectableAdvectionSolver.run() yet.



Do not replace SpectralSolver.



\## Rationale for Next Step



The project has now passed controlled no-forcing drift at:



\- N=64 through final time 1.0

\- N=64 through final time 5.0

\- N=128 through final time 1.0



The next conservative validation question is:



Do the selectable methods remain finite, non-explosive, and aligned under a controlled nonzero forcing response?



This changes one major variable:



forcing changes from zero to controlled baseline forcing



The next phase should remain design-only before any forced-response audit is run.



\## Recommended Next Phase



Phase 11A — Controlled Forced-Response Design



Purpose:



Design a short controlled forced-response audit using the existing baseline forcing inherited from SpectralSolver.



Recommended parameters:



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

| initial field | phase6d\_like\_multimode |



Methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



\## Baseline Forcing



The inherited baseline forcing is:



forcing() = 0.01 \* sin(2X) \* cos(2Y)



The forced-response audit should verify:



\- forcing is nonzero

\- forcing has the expected shape

\- all methods receive the same forcing

\- solver source files remain unchanged



\## Guardrails for Phase 11A



Phase 11A should remain design-only.



Phase 11A should not run the forced-response audit.



Phase 11A should not modify solver source files.



Phase 11A should preserve these rules:



\- SpectralSolver unchanged

\- SelectableAdvectionSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- no production simulation

\- no turbulence claim

\- no k^-3 claim



\## Recommended Phase 11B



After Phase 11A design, Phase 11B may run the controlled forced-response audit.



Phase 11B should still call:



step\_once\_selectable(w)



inside the audit script.



Phase 11B should not call:



SelectableAdvectionSolver.run()



Phase 11B should not call:



SpectralSolver.run()



\## Scientific Boundary



Correct statement after Phase 10Z:



The selectable methods passed no-forcing drift audits at N=64 and N=128 and are ready for a carefully designed controlled forced-response audit.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Final Result



Phase 10Z decision gate:



PASS



Proceed to Phase 11A design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not run turbulence experiments.



Do not make turbulence claims.



Do not make k^-3 claims.

