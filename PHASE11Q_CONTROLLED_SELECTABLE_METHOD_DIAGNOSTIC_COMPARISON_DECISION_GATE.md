\# Phase 11Q Controlled Selectable Method Diagnostic Comparison Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.16-phase11P-controlled-selectable-method-diagnostic-comparison-audit

\- Current previous commit: c8f09e7

\- Decision gate file: PHASE11Q\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_DECISION\_GATE.md



\## Purpose



Phase 11Q is a documentation-only decision gate.



The purpose is to summarize Phase 11P and decide whether the selectable diagnostic comparison pathway is ready for a longer controlled comparison.



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



\## Phase 11P Summary



Phase 11P ran a short controlled selectable diagnostic comparison across:



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



\## Phase 11P Parameters



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 20 |

| final time | 0.02 |

| log\_every | 1 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



\## Phase 11P Global Checks



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



\## Phase 11P Method Results



| Method | Final RMS | Final Energy | Final Enstrophy | Dominant Shell | Low-k Fraction k<=4 | High-k Fraction k>=10 | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.006775597736e-02 | 5.145430176190e-06 | 5.067985520984e-05 | 3.0 | 9.999999996692e-01 | 1.017029198268e-20 | PASS |

| pseudo\_spectral | 1.006775597704e-02 | 5.145430176058e-06 | 5.067985520665e-05 | 3.0 | 9.999999996451e-01 | 1.292692891086e-20 | PASS |

| arakawa | 1.006775597704e-02 | 5.145430176057e-06 | 5.067985520664e-05 | 3.0 | 9.999999996790e-01 | 8.681960300832e-21 | PASS |



\## Phase 11P Spectrum Energy Checks



| Method | Spectrum Direct Relative Error | Result |

|---|---:|---:|

| fd\_centered | 4.938554707285e-16 | PASS |

| pseudo\_spectral | 4.938554707412e-16 | PASS |

| arakawa | 1.646184902471e-16 | PASS |



\## Phase 11P Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.851056115083e-06 | 2.555586828077e-11 | 6.300178196328e-11 | 3.150077798779e-11 | 1.058371389290e-10 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 1.028800714180e-06 | 2.566303491792e-11 | 6.306248505037e-11 | 3.153110364650e-11 | 5.316866655706e-11 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 2.112634740028e-06 | 1.071666371508e-13 | 6.070308709217e-14 | 3.032565871363e-14 | 1.023728022848e-10 | 1.000000000000e+00 | PASS | PASS |



\## Phase 11P Final Checks



| Check | Result |

|---|---:|

| Shared initial\_w unchanged across all runs | PASS |

| All method audits pass | PASS |

| All pairwise comparisons pass | PASS |

| Overall Phase 11P audit | PASS |



\## Main Finding



Phase 11P passed.



All three selectable diagnostic methods completed the same short controlled diagnostic run.



The methods produced finite, real, comparable outputs with valid metadata guardrails.



All three methods agreed on dominant shell:



k = 3.0



All pairwise comparisons were finite and passed.



\## What Phase 11P Confirms



Phase 11P confirms:



1\. run\_selectable\_diagnostic(...) works for fd\_centered.



2\. run\_selectable\_diagnostic(...) works for pseudo\_spectral.



3\. run\_selectable\_diagnostic(...) works for arakawa.



4\. All methods preserve metadata guardrails.



5\. All methods produce finite final states.



6\. All methods produce real final states.



7\. All methods write diagnostic outputs.



8\. All methods write spectrum outputs.



9\. All pairwise comparison metrics are finite.



10\. All methods agree on dominant shell k = 3.0 in this short controlled test.



11\. SelectableAdvectionSolver.run() remains disabled.



12\. SpectralSolver remains unchanged.



13\. advection\_operators remains unchanged.



14\. No turbulence claim is present.



15\. No k\_minus\_3 claim is present.



\## What Phase 11P Does Not Confirm



Phase 11P does not confirm:



1\. production readiness



2\. long-time stability



3\. turbulence



4\. k^-3 scaling



5\. inertial range behavior



6\. Arakawa superiority



7\. pseudo\_spectral superiority



8\. statistical steady state behavior



9\. long forced-response behavior



10\. validated production simulation behavior



\## Decision



Decision:



PASS



The controlled selectable method diagnostic comparison pathway is ready for a longer controlled comparison design.



\## Advancement Approved



Proceed to a design phase for a longer controlled selectable-method diagnostic comparison.



The longer comparison should still use:



run\_selectable\_diagnostic(...)



for each method.



The longer comparison should still avoid:



\- SpectralSolver.run()

\- SelectableAdvectionSolver.run()

\- production claims

\- turbulence claims

\- k^-3 claims

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



Phase 11R — Longer Controlled Selectable Method Diagnostic Comparison Design



Purpose:



Design a longer controlled audit comparing:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The next audit should still be controlled and diagnostic.



It should not be framed as turbulence.



It should not be framed as k^-3 scaling.



It should not be framed as method superiority.



\## Recommended Longer Comparison Parameters



Recommended first longer comparison:



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



Reason:



This extends the Phase 11P controlled comparison from final time 0.02 to final time 1.0 while keeping resolution, Reynolds number, forcing, and initial condition controlled.



\## Required Guardrails for Phase 11R



Phase 11R must preserve:



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



\## Recommended Metrics for Phase 11R



The longer comparison design should include:



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



Correct statement after Phase 11Q:



The controlled short selectable method diagnostic comparison passed across fd\_centered, pseudo\_spectral, and arakawa.



Incorrect statement:



The project has proven turbulence, k^-3 scaling, or method superiority.



Those statements are not supported.



\## Final Result



Phase 11Q decision gate:



PASS



Proceed to Phase 11R longer controlled selectable method diagnostic comparison design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make method superiority claims.

