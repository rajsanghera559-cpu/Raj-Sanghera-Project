\# Phase 11C Controlled Forced-Response Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.1-phase11B-controlled-forced-response-audit

\- Current previous commit: a7e648a

\- Decision gate file: PHASE11C\_CONTROLLED\_FORCED\_RESPONSE\_DECISION\_GATE.md



\## Purpose



Phase 11C is a documentation-only decision gate.



The purpose is to summarize Phase 11B and decide the next controlled validation step.



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

| Phase 11B controlled forced response, N=64, final time 1.0 | PASS |



\## Phase 11B Summary



Phase 11B performed a controlled forced-response audit at N=64 across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The audit used the inherited baseline deterministic forcing:



forcing() = 0.01 \* sin(2X) \* cos(2Y)



The audit repeatedly called:



step\_once\_selectable(w)



inside a standalone audit script.



The audit did not call:



SpectralSolver.run()



The audit did not call:



SelectableAdvectionSolver.run()



\## Phase 11B Parameters



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| forcing | baseline deterministic forcing |

| forcing RMS | 5.000000000000e-03 |

| forcing max abs | 1.000000000000e-02 |

| initial RMS | 0.01 |

| initial field | phase6d\_like\_multimode |



\## Phase 11B Global Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Method forced-response checks pass | PASS |

| Final pairwise checks pass | PASS |

| Phase 11B controlled forced-response audit | PASS |



\## Phase 11B Method Results



| Method | Final RMS Ratio | Relative Energy Change | Final Energy Ratio | Relative Enstrophy Change | Final Enstrophy Ratio | Result |

|---|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.395393809873e+00 | 1.169947508185e+00 | 2.169947508185e+00 | 9.471238846309e-01 | 1.947123884631e+00 | PASS |

| pseudo\_spectral | 1.395393703669e+00 | 1.169947380128e+00 | 2.169947380128e+00 | 9.471235882394e-01 | 1.947123588239e+00 | PASS |

| arakawa | 1.395393699030e+00 | 1.169947364130e+00 | 2.169947364130e+00 | 9.471235752928e-01 | 1.947123575293e+00 | PASS |



\## Phase 11B Pairwise Results



| Pair | Diff L2 | Relative Error | Cosine Similarity | Result |

|---|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.194534477191e-06 | 8.560554509699e-05 | 9.999999963358e-01 | PASS |

| arakawa vs fd\_centered | 6.341330636077e-07 | 4.544473818940e-05 | 9.999999989674e-01 | PASS |

| arakawa vs pseudo\_spectral | 1.356852597460e-06 | 9.723797619925e-05 | 9.999999952724e-01 | PASS |



\## Monotonicity Interpretation



The logged monotonic nonincrease checks failed for energy and enstrophy.



This was expected because the audit used nonzero forcing.



This was not a failure condition for Phase 11B.



The correct interpretation is:



\- energy increased under forcing

\- enstrophy increased under forcing

\- the increases remained within predefined non-explosive thresholds

\- all methods stayed closely aligned



\## Evidence Supporting Advancement



Phase 11B supports advancement because:



1\. Baseline deterministic forcing was verified as nonzero.



2\. The forcing field was finite and real.



3\. The forcing field was identical across methods.



4\. All methods remained finite.



5\. All methods remained real-valued.



6\. All methods remained non-explosive.



7\. All methods passed metadata guardrails.



8\. All methods kept run() disabled.



9\. All methods left solver.w unchanged.



10\. Pairwise final comparisons passed.



11\. Arakawa remained closely aligned with fd\_centered.



12\. Arakawa remained closely aligned with pseudo\_spectral.



13\. SpectralSolver remained unchanged.



14\. SelectableAdvectionSolver remained unchanged.



15\. advection\_operators remained unchanged.



\## Evidence Against Production Readiness



Phase 11B does not justify production readiness because:



1\. The audit was short.



2\. The audit used only N=64.



3\. The audit used one controlled initial condition.



4\. The audit did not validate a selectable production run loop.



5\. The audit did not validate long-time forced behavior.



6\. The audit did not validate spectra.



7\. The audit did not validate turbulence.



8\. The audit did not validate k^-3 scaling.



9\. The audit did not prove a resolved inertial-range cascade.



10\. The audit did not make Arakawa production-ready.



\## Decision



Decision:



PROCEED TO N=128 CONTROLLED FORCED-RESPONSE DESIGN.



Do not proceed directly to turbulence experiments.



Do not proceed directly to k^-3 spectrum experiments.



Do not enable SelectableAdvectionSolver.run() yet.



Do not replace SpectralSolver.



\## Rationale for Next Step



The project has now passed controlled forced response at:



\- N=64

\- final time 1.0

\- baseline deterministic forcing

\- phase6d\_like\_multimode initial condition



The next conservative question is:



Do the selectable methods remain finite, non-explosive, and closely aligned under the same controlled forcing at N=128?



This changes one major variable:



N from 64 to 128



The time horizon should remain short:



final time 1.0



This avoids changing both resolution and duration at the same time.



\## Recommended Next Phase



Phase 11D — N128 Controlled Forced-Response Design



Purpose:



Design a controlled N=128 forced-response audit using the existing baseline forcing inherited from SpectralSolver.



Recommended parameters:



| Parameter | Value |

|---|---:|

| N | 128 |

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



\## Guardrails for Phase 11D



Phase 11D should remain design-only.



Phase 11D should not run the N=128 forced-response audit.



Phase 11D should not modify solver source files.



Phase 11D should preserve these rules:



\- SpectralSolver unchanged

\- SelectableAdvectionSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- no production simulation

\- no turbulence claim

\- no k^-3 claim



\## Recommended Phase 11E



After Phase 11D design, Phase 11E may run the N=128 controlled forced-response audit.



Phase 11E should still call:



step\_once\_selectable(w)



inside the audit script.



Phase 11E should not call:



SelectableAdvectionSolver.run()



Phase 11E should not call:



SpectralSolver.run()



\## Scientific Boundary



Correct statement after Phase 11C:



The selectable methods passed a short controlled forced-response audit at N=64 and are ready for a carefully designed N=128 controlled forced-response audit.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Final Result



Phase 11C decision gate:



PASS



Proceed to Phase 11D design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not run turbulence experiments.



Do not make turbulence claims.



Do not make k^-3 claims.

