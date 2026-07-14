\# Phase 12B N256 Controlled Selectable Diagnostic Feasibility Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.27-phase12A-controlled-resolution-consistency-audit

\- Current previous commit: f45385f

\- Design file: PHASE12B\_N256\_CONTROLLED\_SELECTABLE\_DIAGNOSTIC\_FEASIBILITY\_DESIGN.md



\## Purpose



Phase 12B is a design-only phase.



The purpose is to design a safe N256 feasibility audit for the selectable diagnostic solver before attempting any full N256 controlled comparison.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove convergence.



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



\## Why Phase 12B Is Needed



Phase 12A compared existing N64 and N128 results and passed a controlled resolution-consistency audit.



Phase 12A did not prove convergence.



A stronger convergence pathway may eventually require N256 data.



However, N256 is more expensive than N64 and N128.



The project should not jump directly into a full N256 three-method final-time-1.0 audit.



The next correct step is a small N256 feasibility audit.



\## Resolution Cost Context



Grid size increases quadratically.



| Resolution | Grid Points | Relative to N64 | Relative to N128 |

|---|---:|---:|---:|

| N64 | 4,096 | 1x | 0.25x |

| N128 | 16,384 | 4x | 1x |

| N256 | 65,536 | 16x | 4x |



N256 has:



\- 16 times as many grid points as N64

\- 4 times as many grid points as N128



The first N256 test should therefore be short and conservative.



\## Recommended Next Audit



Recommended next phase:



Phase 12C — N256 Controlled Selectable Diagnostic Feasibility Audit



Purpose:



Run a small N256 feasibility audit using:



run\_selectable\_diagnostic(...)



for one method first:



fd\_centered



Reason:



fd\_centered is the baseline-equivalent internal reference method.



If fd\_centered fails at N256, do not proceed to pseudo\_spectral or arakawa at N256.



\## Recommended Phase 12C Parameters



| Parameter | Value |

|---|---:|

| N | 256 |

| Re | 1000 |

| dt | 0.001 |

| steps | 100 |

| final time | 0.1 |

| log\_every | 10 |

| method | fd\_centered |

| initial RMS | 0.01 |

| forcing | inherited baseline deterministic forcing |



Reason:



This is a feasibility test, not a full scientific run.



The goal is to verify that the N256 diagnostic pathway can complete, write outputs, preserve metadata guardrails, and remain finite.



\## Recommended Initial Field



Use the same deterministic smooth multimode field used in previous controlled phases:



\- sin(2X) cos(2Y)

\- 0.75 sin(3X) cos(Y)

\- 0.50 sin(X) cos(4Y)

\- 0.35 cos(4X - 2Y)



Then rescale to:



RMS = 0.01



Reason:



This keeps the N256 feasibility test tied to the already validated N64 and N128 controlled diagnostic setup.



\## Required Method Run



The Phase 12C audit should run:



SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic(...)



The audit should not run pseudo\_spectral or arakawa yet.



Reason:



This is a first feasibility test.



A three-method N256 audit should only be designed after fd\_centered N256 feasibility passes.



\## Important Rule



Do not call:



SpectralSolver.run()



Do not call:



SelectableAdvectionSolver.run()



The audit should use only:



run\_selectable\_diagnostic(...)



\## Required Output Files



The next audit should write:



| File | Purpose |

|---|---|

| phase12c\_N256\_controlled\_selectable\_diagnostic\_feasibility\_audit.py | audit script |

| PHASE12C\_N256\_CONTROLLED\_SELECTABLE\_DIAGNOSTIC\_FEASIBILITY\_AUDIT.csv | audit result table |

| PHASE12C\_N256\_CONTROLLED\_SELECTABLE\_DIAGNOSTIC\_FEASIBILITY\_AUDIT\_REPORT.md | audit report |



The audit may also create selectable diagnostic output under:



experiments/selectable\_diagnostics/phase12C\_N256\_fd\_centered\_feasibility



\## Required Global Checks



The Phase 12C audit should check:



1\. SpectralSolver imports.



2\. SelectableAdvectionSolver imports.



3\. fd\_centered is supported.



4\. default method remains fd\_centered.



5\. compute\_rhs\_selectable exists.



6\. step\_once\_selectable exists.



7\. run\_selectable\_diagnostic exists.



8\. SelectableAdvectionSolver.run() remains disabled.



9\. SpectralSolver file has no git diff.



10\. advection\_operators file has no git diff.



11\. selectable\_advection\_solver file has no unexpected git diff during the audit.



12\. N is exactly 256.



13\. Re is exactly 1000.



14\. dt is exactly 0.001.



15\. steps is exactly 100.



16\. final time is exactly 0.1.



17\. log\_every is exactly 10.



18\. initial field is not mutated.



19\. solver.w is not mutated.



\## Required Per-Run Checks



The Phase 12C audit should check:



1\. diagnostic run completes



2\. final\_w exists



3\. final\_w is finite



4\. final\_w is real



5\. final\_w has expected shape



6\. output paths are present



7\. output files exist



8\. metadata is written



9\. diagnostics CSV is written



10\. spectrum CSV is written



11\. summary JSON is written



12\. initial state file is written



13\. final state file is written



14\. diagnostics contain step 0



15\. diagnostics contain final step 100



16\. diagnostics contain expected logged steps



17\. spectrum contains k, E\_k, mode\_count



18\. spectrum is finite



19\. spectrum is nonnegative within tolerance



20\. metadata advection\_method is fd\_centered



21\. metadata production\_ready is false



22\. metadata turbulence\_claim is false



23\. metadata k\_minus\_3\_claim is false



24\. summary production\_ready is false



25\. summary turbulence\_claim is false



26\. summary k\_minus\_3\_claim is false



\## Required Metrics



Record:



\- N

\- Re

\- dt

\- steps

\- final time

\- log\_every

\- method

\- initial RMS

\- final RMS

\- final kinetic energy

\- final enstrophy

\- final max abs vorticity

\- RMS ratio relative to initial RMS

\- energy ratio relative to initial energy

\- enstrophy ratio relative to initial enstrophy

\- spectrum energy sum

\- spectrum direct energy relative error

\- dominant shell

\- low-k energy fraction for k <= 4

\- high-k energy fraction for k >= 10

\- diagnostics minimum RMS

\- diagnostics maximum RMS

\- diagnostics minimum energy

\- diagnostics maximum energy

\- diagnostics minimum enstrophy

\- diagnostics maximum enstrophy

\- output files exist

\- metadata guardrails pass

\- overall result



\## Required Diagnostics Checks



The diagnostics CSV should include:



\- step

\- time

\- rms\_vorticity

\- kinetic\_energy

\- enstrophy

\- max\_abs\_vorticity

\- finite

\- real



The audit should verify:



\- step 0 exists

\- final step 100 exists

\- logged steps are present

\- all logged diagnostics are finite

\- finite flags are true

\- real flags are true

\- diagnostic time is monotone



Expected logged steps:



\- 0

\- 10

\- 20

\- 30

\- 40

\- 50

\- 60

\- 70

\- 80

\- 90

\- 100



\## Recommended Sanity Bounds



Use broad feasibility bounds.



| Quantity | Suggested Bound |

|---|---:|

| final RMS ratio relative to initial RMS | between 0.01 and 100 |

| final energy ratio relative to initial energy | between 0.0001 and 10000 |

| final enstrophy ratio relative to initial enstrophy | between 0.0001 and 10000 |

| spectrum energy direct relative error | <= 1e-10 |

| high-k fraction k >= 10 | record only |

| runtime | record if convenient, do not fail unless the run does not complete |



Reason:



The purpose is feasibility, not proof.



\## Expected Result



Expected Phase 12C result:



PASS



Expected interpretation:



The N256 fd\_centered selectable diagnostic feasibility run completed, remained finite and real, wrote outputs, preserved metadata guardrails, and did not require enabling run().



\## What a PASS Would Confirm



A PASS would confirm:



1\. N256 fd\_centered feasibility is acceptable for a short controlled diagnostic run.



2\. run\_selectable\_diagnostic works at N256 for fd\_centered through final time 0.1.



3\. output writing works at N256.



4\. diagnostics remain finite at N256 for the short test.



5\. spectrum writing works at N256.



6\. metadata guardrails remain active.



7\. SelectableAdvectionSolver.run() remains disabled.



8\. SpectralSolver remains unchanged.



\## What a PASS Would Not Confirm



A PASS would not confirm:



1\. full N256 final-time-1.0 feasibility



2\. pseudo\_spectral N256 feasibility



3\. arakawa N256 feasibility



4\. three-method N256 comparison feasibility



5\. convergence



6\. convergence order



7\. turbulence



8\. k^-3 scaling



9\. inertial range behavior



10\. method superiority



11\. production readiness



\## What a FAIL Would Mean



A FAIL would mean the project should stop before attempting larger N256 comparisons.



Possible causes to inspect:



\- runtime too long

\- memory pressure

\- output writing failure

\- diagnostics failure

\- numerical instability

\- shape mismatch

\- metadata guardrail failure



Do not proceed to N256 three-method comparisons until the failure is understood.



\## Recommended Phase 12D



After Phase 12C, the next phase should be:



Phase 12D — N256 Controlled Selectable Diagnostic Feasibility Decision Gate



Purpose:



Document the Phase 12C result and decide whether to proceed to one of these options:



1\. N256 three-method short feasibility design



2\. N256 fd\_centered longer feasibility design



3\. stop N256 expansion and archive Phase 12



4\. revise feasibility parameters



Recommended path if Phase 12C passes:



Phase 12E — N256 Three-Method Short Feasibility Design



\## Guardrails



Phase 12C must preserve:



\- SpectralSolver unchanged

\- advection\_operators unchanged

\- selectable\_advection\_solver unchanged

\- SelectableAdvectionSolver.run() disabled

\- fd\_centered default unchanged

\- Arakawa not default

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no inertial-range claim

\- no convergence claim

\- no method superiority claim



\## Scientific Boundary



Correct statement after Phase 12B:



An N256 fd\_centered controlled selectable diagnostic feasibility audit has been designed.



Incorrect statement:



The project has proven N256 convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Decision



Phase 12B decision:



PROCEED TO PHASE 12C N256 CONTROLLED SELECTABLE DIAGNOSTIC FEASIBILITY AUDIT.



Do not run pseudo\_spectral at N256 yet.



Do not run arakawa at N256 yet.



Do not run a full N256 final-time-1.0 three-method comparison yet.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims.



Do not make method superiority claims.



\## Final Result



Phase 12B N256 controlled selectable diagnostic feasibility design:



PASS



Next phase:



Phase 12C — N256 Controlled Selectable Diagnostic Feasibility Audit

