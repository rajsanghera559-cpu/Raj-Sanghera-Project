\# Phase 11I Controlled Forced-Response Spectrum Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.7-phase11H-controlled-forced-response-spectrum-diagnostic-audit

\- Current previous commit: c0a3e6e

\- Decision gate file: PHASE11I\_CONTROLLED\_FORCED\_RESPONSE\_SPECTRUM\_DECISION\_GATE.md



\## Purpose



Phase 11I is a documentation-only decision gate.



The purpose is to summarize Phase 11H and decide the next controlled validation step.



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



This phase does not prove an inertial range.



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

| Phase 11E controlled forced response, N=128, final time 1.0 | PASS |

| Phase 11H controlled forced-response spectrum diagnostic | PASS |



\## Phase 11H Summary



Phase 11H performed a controlled forced-response spectrum diagnostic audit at:



\- N=64

\- N=128



The tested selectable methods were:



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



No slope fitting was performed.



No turbulence claim was made.



No k^-3 claim was made.



\## Phase 11H Parameters



| Parameter | Value |

|---|---:|

| Resolutions | N=64 and N=128 |

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



\## Phase 11H Overall Result



| Check | Result |

|---|---:|

| Global checks pass | PASS |

| Forcing checks pass | PASS |

| Spectrum summary checks pass | PASS |

| Pairwise spectrum checks pass | PASS |

| Phase 11H controlled forced-response spectrum diagnostic audit | PASS |



\## N=64 Spectrum Summary



| Method | Direct Energy | Spectrum Energy Sum | Energy Relative Error | Dominant Shell | Low-k Fraction k<=4 | High-k Fraction k>=10 | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.097924266346e-05 | 1.097924266346e-05 | 6.171886154396e-16 | 3.0 | 9.999993866682e-01 | 4.444260485332e-14 | PASS |

| pseudo\_spectral | 1.097924201553e-05 | 1.097924201553e-05 | 4.628914888967e-16 | 3.0 | 9.999993421581e-01 | 5.803815274166e-14 | PASS |

| arakawa | 1.097924193458e-05 | 1.097924193458e-05 | 4.628914923094e-16 | 3.0 | 9.999994052425e-01 | 3.898503509840e-14 | PASS |



\## N=128 Spectrum Summary



| Method | Direct Energy | Spectrum Energy Sum | Energy Relative Error | Dominant Shell | Low-k Fraction k<=4 | High-k Fraction k>=10 | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.097924218660e-05 | 1.097924218660e-05 | 6.171886422459e-16 | 3.0 | 9.999993535219e-01 | 5.426428387836e-14 | PASS |

| pseudo\_spectral | 1.097924201553e-05 | 1.097924201553e-05 | 4.628914888966e-16 | 3.0 | 9.999993421581e-01 | 5.803815205372e-14 | PASS |

| arakawa | 1.097924199417e-05 | 1.097924199417e-05 | 6.171886530628e-16 | 3.0 | 9.999993584626e-01 | 5.259734582921e-14 | PASS |



\## N=64 Pairwise Spectrum Results



| Pair | Relative Spectrum Error | Spectrum Cosine Similarity | Direct Energy Relative Difference | Dominant Shell Agreement | Result |

|---|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.961468317670e-07 | 1.000000000000e+00 | 5.901377707500e-08 | PASS | PASS |

| arakawa vs fd\_centered | 1.184255584011e-07 | 1.000000000000e+00 | 6.638647188008e-08 | PASS | PASS |

| arakawa vs pseudo\_spectral | 1.758186681246e-07 | 1.000000000000e+00 | 7.372695240166e-09 | PASS | PASS |



\## N=128 Pairwise Spectrum Results



| Pair | Relative Spectrum Error | Spectrum Cosine Similarity | Direct Energy Relative Difference | Dominant Shell Agreement | Result |

|---|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 5.076069567640e-08 | 1.000000000000e+00 | 1.558066666559e-08 | PASS | PASS |

| arakawa vs fd\_centered | 3.109398749084e-08 | 1.000000000000e+00 | 1.752602921905e-08 | PASS | PASS |

| arakawa vs pseudo\_spectral | 4.564720952450e-08 | 1.000000000000e+00 | 1.945362583764e-09 | PASS | PASS |



\## Main Interpretation



The selectable methods produced finite, energy-consistent, mutually aligned spectra under controlled forced-response conditions.



For both N=64 and N=128:



\- spectra were finite

\- spectra were nonnegative within tolerance

\- spectrum energy matched direct kinetic energy

\- pairwise spectra were strongly aligned

\- dominant shell was k=3

\- low-k fraction was approximately 0.999999

\- high-k fraction was near machine-level magnitude



This is a controlled diagnostic result.



This is not turbulence evidence.



This is not k^-3 evidence.



This is not inertial-range evidence.



\## Evidence Supporting Advancement



Phase 11H supports advancement because:



1\. Both N=64 and N=128 spectrum diagnostics passed.



2\. All methods produced finite spectra.



3\. All methods produced nonnegative spectra within tolerance.



4\. Spectrum energy matched direct kinetic energy.



5\. Dominant shell agreed across methods.



6\. Pairwise spectrum comparisons passed.



7\. Arakawa remained spectrally aligned with fd\_centered.



8\. Arakawa remained spectrally aligned with pseudo\_spectral.



9\. SpectralSolver remained unchanged.



10\. SelectableAdvectionSolver remained unchanged.



11\. advection\_operators remained unchanged.



12\. SelectableAdvectionSolver.run() remained disabled.



13\. No slope fitting was performed.



14\. No turbulence or k^-3 claim was made.



\## Evidence Against Turbulence or k^-3 Claims



Phase 11H does not support turbulence or k^-3 claims because:



1\. The audit was short.



2\. The audit used one controlled initial condition.



3\. The audit used deterministic low-wavenumber forcing.



4\. The spectra were low-k dominated.



5\. The dominant shell was k=3.



6\. The high-k fraction was near machine-level magnitude.



7\. No inertial range was established.



8\. No slope fit was performed.



9\. No cascade validation was performed.



10\. No long-time statistical steady state was established.



\## Evidence Against Production Readiness



Phase 11H does not justify production readiness because:



1\. The audit used standalone scripts.



2\. The selectable run loop remains disabled.



3\. The audit did not validate SelectableAdvectionSolver.run().



4\. The audit did not validate production metadata writing.



5\. The audit did not validate production output directory structure.



6\. The audit did not validate long-time forced behavior.



7\. The audit did not validate multiple forcing amplitudes.



8\. The audit did not validate multiple initial conditions.



9\. The audit did not make Arakawa production-ready.



10\. The audit did not establish a full workflow for research runs.



\## Decision



Decision:



PROCEED TO SELECTABLE RUN-LOOP DESIGN.



Do not proceed directly to turbulence experiments.



Do not proceed directly to k^-3 spectrum claims.



Do not replace SpectralSolver.



Do not make Arakawa the default.



The next phase should be design-only.



\## Rationale for Next Step



The project has now validated the selectable method path through:



\- direct advection comparisons

\- RHS equivalence

\- one-step equivalence

\- no-forcing drift

\- controlled forced response

\- controlled forced-response spectra



The next engineering question is:



Can a selectable run loop be designed safely while preserving SpectralSolver and preserving all metadata guardrails?



A run-loop design is the correct next step before any longer or more automated controlled experiments.



\## Recommended Next Phase



Phase 11J — Selectable Run-Loop Design



Purpose:



Design a controlled selectable run-loop pathway without modifying SpectralSolver and without making the selectable solver production-ready.



Recommended design options:



Option A:



Add a separate method to SelectableAdvectionSolver:



run\_selectable\_diagnostic()



Option B:



Create a separate runner utility:



project/solver/selectable\_runner.py



Recommended first choice:



Option A, only after design approval.



Reason:



SelectableAdvectionSolver already owns step\_once\_selectable(w), metadata, and method selection.



A clearly named diagnostic run method is safer than enabling run().



\## Guardrails for Phase 11J



Phase 11J should remain design-only.



Phase 11J should not modify solver source files.



Phase 11J should preserve these rules:



\- SpectralSolver unchanged

\- SelectableAdvectionSolver unchanged

\- SelectableAdvectionSolver.run() disabled

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no Arakawa default

\- no replacing fd\_centered

\- no replacing baseline solver



\## Required Design Questions for Phase 11J



Phase 11J should decide:



1\. Whether to add run\_selectable\_diagnostic() or create a separate runner utility.



2\. How to write metadata for selectable runs.



3\. How to record advection\_method.



4\. How to record forcing status.



5\. How to record solver\_variant.



6\. How to record run\_enabled status.



7\. How to prevent confusion with SpectralSolver.run().



8\. How to write diagnostics.csv.



9\. How to write spectrum.csv.



10\. How to write final\_state.npy or equivalent.



11\. How to preserve existing validation reports.



12\. How to test fd\_centered equivalence first.



\## Recommended Phase 11K



After Phase 11J design, Phase 11K may implement a selectable diagnostic run scaffold.



Phase 11K should not run long simulations.



Phase 11K should only test:



\- import

\- constructor

\- run\_selectable\_diagnostic existence

\- metadata output

\- fd\_centered short-run equivalence

\- run() still disabled

\- SpectralSolver unchanged



\## Scientific Boundary



Correct statement after Phase 11I:



The selectable methods passed controlled forced-response spectrum diagnostics and are ready for a carefully designed selectable diagnostic run-loop pathway.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Final Result



Phase 11I decision gate:



PASS



Proceed to Phase 11J design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make Arakawa the default.



Do not run turbulence experiments.



Do not make turbulence claims.



Do not make k^-3 claims.

