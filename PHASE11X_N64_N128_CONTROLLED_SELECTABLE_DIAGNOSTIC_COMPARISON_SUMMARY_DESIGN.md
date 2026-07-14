\# Phase 11X N64/N128 Controlled Selectable Diagnostic Comparison Summary Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.23-phase11W-N128-longer-controlled-selectable-method-diagnostic-comparison-decision-gate

\- Current previous commit: 4b6a7d5

\- Design file: PHASE11X\_N64\_N128\_CONTROLLED\_SELECTABLE\_DIAGNOSTIC\_COMPARISON\_SUMMARY\_DESIGN.md



\## Purpose



Phase 11X is a design-only phase.



The purpose is to design an integrated summary comparing the already completed controlled selectable diagnostic audits:



\- Phase 11S: N=64, final time 1.0

\- Phase 11V: N=128, final time 1.0



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



This phase does not prove convergence.



This phase does not claim method superiority.



\## Current Solver Status



The validated baseline solver remains:



project/solver/spectral\_solver.py



The selectable diagnostic solver remains:



project/solver/selectable\_advection\_solver.py



The selectable solver currently supports:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The selectable solver currently includes:



\- compute\_advection(w)

\- compute\_rhs\_selectable(w)

\- step\_once\_selectable(w)

\- run\_selectable\_diagnostic(...)



The selectable solver still has:



run() intentionally disabled



This remains correct.



\## Why Phase 11X Is Needed



Phase 11S passed the longer controlled selectable diagnostic comparison at:



N = 64



Phase 11V passed the longer controlled selectable diagnostic comparison at:



N = 128



Phase 11W accepted the N=128 result and approved an integrated N64/N128 summary design.



The next step is to summarize the two completed audits side by side.



This summary is useful for project organization.



This summary is not a convergence study.



This summary is not a turbulence study.



This summary is not a k^-3 study.



This summary is not a method-superiority study.



\## Inputs for the Future Summary



Phase 11Y should use the already created files from Phase 11S and Phase 11V.



\### Phase 11S Inputs



\- phase11s\_longer\_controlled\_selectable\_method\_diagnostic\_comparison\_audit.py

\- PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv

\- PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT\_REPORT.md



\### Phase 11V Inputs



\- phase11v\_N128\_longer\_controlled\_selectable\_method\_diagnostic\_comparison\_audit.py

\- PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv

\- PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT\_REPORT.md



\## Recommended Next Phase



Recommended next phase:



Phase 11Y — N64/N128 Controlled Selectable Diagnostic Comparison Summary Report



Purpose:



Create a documentation-only integrated summary comparing:



\- Phase 11S N=64 results

\- Phase 11V N=128 results



The report should use already produced results.



The report should not run new simulations.



The report should not modify source code.



The report should not claim convergence.



\## Recommended Phase 11Y Output



The next phase should create:



PHASE11Y\_N64\_N128\_CONTROLLED\_SELECTABLE\_DIAGNOSTIC\_COMPARISON\_SUMMARY\_REPORT.md



Optional supporting CSV:



PHASE11Y\_N64\_N128\_CONTROLLED\_SELECTABLE\_DIAGNOSTIC\_COMPARISON\_SUMMARY.csv



The optional CSV should only copy or reorganize existing Phase 11S and Phase 11V results.



It should not create new simulation data.



\## Phase 11Y Summary Structure



The future summary report should include:



1\. Purpose



2\. Source files used



3\. Shared setup



4\. N=64 method results



5\. N=128 method results



6\. N=64 pairwise results



7\. N=128 pairwise results



8\. N64/N128 side-by-side observations



9\. Scientific boundaries



10\. Recommended next phase



\## Shared Setup to Report



The future Phase 11Y report should state that Phase 11S and Phase 11V used the same controlled setup except for resolution.



| Parameter | Phase 11S | Phase 11V |

|---|---:|---:|

| N | 64 | 128 |

| Re | 1000 | 1000 |

| dt | 0.001 | 0.001 |

| steps | 1000 | 1000 |

| final time | 1.0 | 1.0 |

| log\_every | 100 | 100 |

| initial RMS | 0.01 | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing | inherited baseline deterministic forcing |



\## Method Metrics to Compare



For each method and each resolution, the future summary should compare:



\- final RMS

\- final kinetic energy

\- final enstrophy

\- RMS ratio

\- energy ratio

\- enstrophy ratio

\- dominant shell

\- low-k fraction k <= 4

\- high-k fraction k >= 10

\- spectrum direct relative error

\- diagnostics minimum RMS

\- diagnostics maximum RMS

\- method result



\## Pairwise Metrics to Compare



For each pair and each resolution, the future summary should compare:



\- field relative L2 difference

\- energy relative difference

\- enstrophy relative difference

\- RMS relative difference

\- spectrum relative L2 difference

\- spectrum cosine similarity

\- dominant shell match

\- pairwise result



The method pairs are:



\- pseudo\_spectral vs fd\_centered

\- arakawa vs fd\_centered

\- arakawa vs pseudo\_spectral



\## Known Phase 11S N64 Method Results



| Method | Final RMS | Final Energy | Final Enstrophy | Dominant Shell | Low-k Fraction k<=4 | High-k Fraction k>=10 | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.383832617489e-02 | 1.081610036476e-05 | 9.574963566127e-05 | 3.0 | 9.999994138821e-01 | 3.940095470626e-14 | PASS |

| pseudo\_spectral | 1.383832514162e-02 | 1.081609974827e-05 | 9.574962136261e-05 | 3.0 | 9.999993713576e-01 | 5.145804156150e-14 | PASS |

| arakawa | 1.383832511311e-02 | 1.081609967044e-05 | 9.574962096811e-05 | 3.0 | 9.999994315888e-01 | 3.456885984340e-14 | PASS |



\## Known Phase 11V N128 Method Results



| Method | Final RMS | Final Energy | Final Enstrophy | Dominant Shell | Low-k Fraction k<=4 | High-k Fraction k>=10 | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.383832541415e-02 | 1.081609991096e-05 | 9.574962513398e-05 | 3.0 | 9.999993822143e-01 | 4.811172943166e-14 | PASS |

| pseudo\_spectral | 1.383832514162e-02 | 1.081609974827e-05 | 9.574962136262e-05 | 3.0 | 9.999993713576e-01 | 5.145804105620e-14 | PASS |

| arakawa | 1.383832513401e-02 | 1.081609972773e-05 | 9.574962125729e-05 | 3.0 | 9.999993869243e-01 | 4.663544254778e-14 | PASS |



\## Known Phase 11S N64 Pairwise Results



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.416286809714e-05 | 5.699784851319e-08 | 1.493339006612e-07 | 7.466695312720e-08 | 1.898853630556e-07 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 4.463033910031e-05 | 6.419339335323e-08 | 1.534539447487e-07 | 7.672697532158e-08 | 1.161741763811e-07 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 9.526899745687e-05 | 7.195545250174e-09 | 4.120044702725e-09 | 2.060022348196e-09 | 1.688920780038e-07 | 1.000000000000e+00 | PASS | PASS |



\## Known Phase 11V N128 Pairwise Results



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 2.117135768632e-05 | 1.504188750238e-08 | 3.938765425646e-08 | 1.969382730585e-08 | 4.913982615903e-08 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 1.134297610978e-05 | 1.694119928233e-08 | 4.048776482117e-08 | 2.024388254876e-08 | 3.049532971221e-08 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 2.414609989113e-05 | 1.899311808512e-09 | 1.100110608040e-09 | 5.500552537478e-10 | 4.385026889381e-08 | 1.000000000000e+00 | PASS | PASS |



\## Broad Observations to Include in Phase 11Y



The future summary may state:



1\. Both N=64 and N=128 controlled diagnostic audits passed.



2\. All three selectable methods passed at both resolutions.



3\. All final states were finite and real.



4\. Metadata guardrails were preserved at both resolutions.



5\. SelectableAdvectionSolver.run() remained disabled.



6\. SpectralSolver remained unchanged.



7\. advection\_operators remained unchanged.



8\. Dominant shell remained k = 3.0 for every method at both resolutions.



9\. Spectra remained strongly low-k dominated.



10\. High-k energy fraction remained extremely small.



11\. Pairwise field differences decreased from N=64 to N=128 in the recorded comparisons.



12\. Pairwise spectrum differences decreased from N=64 to N=128 in the recorded comparisons.



13\. Spectrum cosine similarity was 1.0 for all recorded pairwise comparisons.



14\. These observations are controlled diagnostic observations only.



\## Important Boundary on N64/N128 Comparison



The future summary must not call the N64/N128 side-by-side comparison a convergence proof.



Reason:



A proper convergence study requires a dedicated design with:



\- clearly specified norms

\- multiple resolutions

\- controlled refinement logic

\- fixed physical time

\- error scaling expectations

\- acceptance criteria

\- interpretation boundaries



The N64/N128 comparison is useful context.



It is not enough to prove convergence.



\## Required Scientific Boundary Language



The future summary should include this boundary:



Correct statement:



The N=64 and N=128 controlled selectable diagnostic comparisons both passed, and their broad diagnostic behavior was consistent.



Incorrect statement:



The project has proven convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Recommended Phase 11Y Decision



Phase 11Y should summarize the completed N=64 and N=128 comparisons and then decide whether to proceed to one of the following:



1\. Phase 11Z — Controlled Convergence Study Design



2\. Phase 11Z — Controlled Forcing-Amplitude Sensitivity Design



3\. Phase 11Z — No-Forcing Longer Selectable Comparison Design



4\. Phase 11Z — Final Phase 11 Summary and Archive



Recommended choice:



Phase 11Z — Controlled Convergence Study Design



Reason:



The project now has controlled N=64 and N=128 evidence, but no convergence claim is allowed yet.



A dedicated convergence-study design is the correct next scientific step if the goal is to evaluate resolution behavior.



\## Required Guardrails for Phase 11Y



Phase 11Y must preserve:



\- SpectralSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- fd\_centered default unchanged

\- Arakawa not default

\- no new simulation

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no inertial-range claim

\- no method superiority claim

\- no convergence claim



\## What Phase 11X Approves



Phase 11X approves designing a summary report that integrates existing N=64 and N=128 controlled diagnostic results.



Phase 11X approves no new simulation.



Phase 11X approves no source-code modification.



Phase 11X approves no convergence claim.



\## What Phase 11X Does Not Approve



Phase 11X does not approve:



\- enabling SelectableAdvectionSolver.run()

\- replacing SpectralSolver

\- making Arakawa the default

\- production simulations

\- turbulence experiments

\- k^-3 claims

\- inertial-range claims

\- slope fitting as evidence

\- convergence claims

\- method superiority claims



\## Recommended Phase 11Y Output Structure



The Phase 11Y report should use this structure:



1\. Checkpoint



2\. Purpose



3\. Source files used



4\. Shared controlled setup



5\. Phase 11S N64 method summary



6\. Phase 11V N128 method summary



7\. Phase 11S N64 pairwise summary



8\. Phase 11V N128 pairwise summary



9\. N64/N128 broad observations



10\. What the summary confirms



11\. What the summary does not confirm



12\. Decision



13\. Recommended next phase



14\. Scientific boundary



15\. Final result



\## Scientific Boundary



Correct statement after Phase 11X:



An N64/N128 controlled selectable diagnostic comparison summary has been designed using already completed Phase 11S and Phase 11V results.



Incorrect statement:



The project has proven convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Decision



Phase 11X decision:



PROCEED TO PHASE 11Y N64/N128 CONTROLLED SELECTABLE DIAGNOSTIC COMPARISON SUMMARY REPORT.



Do not run new simulations.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims.



Do not make method superiority claims.



\## Final Result



Phase 11X design:



PASS



Next phase:



Phase 11Y — N64/N128 Controlled Selectable Diagnostic Comparison Summary Report

