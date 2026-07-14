\# Phase 11T Longer Controlled Selectable Method Diagnostic Comparison Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.19-phase11S-longer-controlled-selectable-method-diagnostic-comparison-audit

\- Current previous commit: 6397513

\- Decision gate file: PHASE11T\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_DECISION\_GATE.md



\## Purpose



Phase 11T is a documentation-only decision gate.



The purpose is to summarize Phase 11S and decide whether the selectable diagnostic comparison pathway is ready for a higher-resolution controlled comparison.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



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



\## Phase 11S Summary



Phase 11S ran a longer controlled selectable diagnostic comparison across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Each method used:



run\_selectable\_diagnostic(...)



The audit did not call:



SpectralSolver.run()



The audit did not enable:



SelectableAdvectionSolver.run()



The audit used identical controlled conditions for all methods.



\## Phase 11S Parameters



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| log\_every | 100 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



\## Phase 11S Global Checks



| Check | Result |

|---|---:|

| SpectralSolver import | PASS |

| SelectableAdvectionSolver import | PASS |

| Supported methods exact | PASS |

| Default method fd\_centered | PASS |

| compute\_rhs\_selectable exists | PASS |

| step\_once\_selectable exists | PASS |

| run\_selectable\_diagnostic exists | PASS |

| SpectralSolver file has no git diff | PASS |

| advection\_operators file has no git diff | PASS |

| selectable\_advection\_solver file has no git diff | PASS |

| All grid shapes same | PASS |

| All dx same | PASS |

| All dt same | PASS |

| All nu same | PASS |

| All dealias masks same | PASS |

| All forcing fields same | PASS |

| Global checks | PASS |



\## Phase 11S Method Results



| Method | Final RMS | Final Energy | Final Enstrophy | RMS Ratio | Energy Ratio | Enstrophy Ratio | Dominant Shell | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.383832617489e-02 | 1.081610036476e-05 | 9.574963566127e-05 | 1.383832617489e+00 | 2.137703915855e+00 | 1.914992713225e+00 | 3.0 | PASS |

| pseudo\_spectral | 1.383832514162e-02 | 1.081609974827e-05 | 9.574962136261e-05 | 1.383832514162e+00 | 2.137703794011e+00 | 1.914992427252e+00 | 3.0 | PASS |

| arakawa | 1.383832511311e-02 | 1.081609967044e-05 | 9.574962096811e-05 | 1.383832511311e+00 | 2.137703778629e+00 | 1.914992419362e+00 | 3.0 | PASS |



\## Phase 11S Spectrum Results



| Method | Low-k Fraction k<=4 | High-k Fraction k>=10 | Spectrum Direct Relative Error | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 9.999994138821e-01 | 3.940095470626e-14 | 1.566244614397e-16 | PASS |

| pseudo\_spectral | 9.999993713576e-01 | 5.145804156150e-14 | 1.566244703670e-16 | PASS |

| arakawa | 9.999994315888e-01 | 3.456885984340e-14 | 1.566244714940e-16 | PASS |



\## Phase 11S Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.416286809714e-05 | 5.699784851319e-08 | 1.493339006612e-07 | 7.466695312720e-08 | 1.898853630556e-07 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 4.463033910031e-05 | 6.419339335323e-08 | 1.534539447487e-07 | 7.672697532158e-08 | 1.161741763811e-07 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 9.526899745687e-05 | 7.195545250174e-09 | 4.120044702725e-09 | 2.060022348196e-09 | 1.688920780038e-07 | 1.000000000000e+00 | PASS | PASS |



\## Phase 11S Final Checks



| Check | Result |

|---|---:|

| Shared initial\_w unchanged across all runs | PASS |

| All method audits pass | PASS |

| All pairwise comparisons pass | PASS |

| Overall Phase 11S audit | PASS |



\## Main Finding



Phase 11S passed.



All three selectable diagnostic methods completed the longer controlled diagnostic run through final time 1.0.



The methods produced finite, real, comparable outputs with valid metadata guardrails.



All three methods agreed on dominant shell:



k = 3.0



Pairwise comparison metrics were finite and passed.



\## Interpretation



Phase 11S shows that the selectable diagnostic pathway remains stable and auditable through final time 1.0 at N=64 for:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The spectra remain strongly low-k dominated.



The high-k energy fraction remains extremely small.



This is not evidence of turbulence.



This is not evidence of k^-3 scaling.



This is not evidence of an inertial range.



This is not evidence of method superiority.



\## What Phase 11S Confirms



Phase 11S confirms:



1\. run\_selectable\_diagnostic(...) works for fd\_centered through final time 1.0.



2\. run\_selectable\_diagnostic(...) works for pseudo\_spectral through final time 1.0.



3\. run\_selectable\_diagnostic(...) works for arakawa through final time 1.0.



4\. All methods preserve metadata guardrails.



5\. All methods produce finite final states.



6\. All methods produce real final states.



7\. All methods write diagnostic outputs.



8\. All methods write spectrum outputs.



9\. All method time-history diagnostics remain finite.



10\. All pairwise comparison metrics are finite.



11\. All methods agree on dominant shell k = 3.0.



12\. SelectableAdvectionSolver.run() remains disabled.



13\. SpectralSolver remains unchanged.



14\. advection\_operators remains unchanged.



15\. No turbulence claim is present.



16\. No k\_minus\_3 claim is present.



\## What Phase 11S Does Not Confirm



Phase 11S does not confirm:



1\. production readiness



2\. turbulence



3\. k^-3 scaling



4\. inertial range behavior



5\. Arakawa superiority



6\. pseudo\_spectral superiority



7\. statistical steady state behavior



8\. physical cascade behavior



9\. long-time asymptotic stability



10\. validated production simulation behavior



11\. higher-resolution behavior



\## Decision



Decision:



PASS



The longer controlled selectable method diagnostic comparison pathway is ready for a higher-resolution controlled comparison design.



\## Advancement Approved



Proceed to a design phase for an N=128 longer controlled selectable-method diagnostic comparison.



The higher-resolution comparison should still use:



run\_selectable\_diagnostic(...)



for each method.



The higher-resolution comparison should still avoid:



\- SpectralSolver.run()

\- SelectableAdvectionSolver.run()

\- production claims

\- turbulence claims

\- k^-3 claims

\- inertial-range claims

\- method superiority claims



\## Advancement Not Approved



This decision gate does not approve:



\- enabling SelectableAdvectionSolver.run()

\- replacing SpectralSolver

\- making Arakawa the default

\- production simulations

\- turbulence experiments

\- k^-3 claims

\- inertial-range claims

\- slope fitting as evidence

\- method superiority claims



\## Recommended Next Phase



Phase 11U — N128 Longer Controlled Selectable Method Diagnostic Comparison Design



Purpose:



Design a higher-resolution controlled audit comparing:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The next audit should still be controlled and diagnostic.



It should not be framed as turbulence.



It should not be framed as k^-3 scaling.



It should not be framed as method superiority.



\## Recommended N128 Comparison Parameters



Recommended first N128 comparison:



| Parameter | Value |

|---|---:|

| N | 128 |

| Re | 1000 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| log\_every | 100 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



Reason:



This repeats the Phase 11S controlled comparison at higher resolution while preserving Reynolds number, time step, final time, forcing, and initial condition style.



\## Required Guardrails for Phase 11U



Phase 11U must preserve:



\- SpectralSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- fd\_centered default unchanged

\- Arakawa not default

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no inertial-range claim

\- no method superiority claim



\## Recommended Metrics for Phase 11U



The N=128 comparison design should include:



\- final RMS vorticity

\- final kinetic energy

\- final enstrophy

\- final max abs vorticity

\- time-history diagnostics

\- final spectrum

\- dominant shell

\- low-k energy fraction for k <= 4

\- high-k energy fraction for k >= 10

\- pairwise field differences

\- pairwise spectrum differences

\- pairwise energy differences

\- pairwise enstrophy differences

\- metadata guardrails



\## Scientific Boundary



Correct statement after Phase 11T:



The longer controlled N=64 selectable method diagnostic comparison passed across fd\_centered, pseudo\_spectral, and arakawa.



Incorrect statement:



The project has proven turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Final Result



Phase 11T decision gate:



PASS



Proceed to Phase 11U N128 longer controlled selectable method diagnostic comparison design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make method superiority claims.

