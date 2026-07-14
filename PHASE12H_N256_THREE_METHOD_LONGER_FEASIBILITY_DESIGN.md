\# Phase 12H N256 Three-Method Longer Feasibility Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.33-phase12G-N256-three-method-short-feasibility-decision-gate

\- Current previous commit: 6e639f7

\- Design file: PHASE12H\_N256\_THREE\_METHOD\_LONGER\_FEASIBILITY\_DESIGN.md



\## Purpose



Phase 12H is a design-only phase.



The purpose is to design an intermediate longer N256 feasibility audit across all selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The audit should use:



run\_selectable\_diagnostic(...)



for each method.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove full N256 final-time-1.0 feasibility.



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



\## Why Phase 12H Is Needed



Phase 12F passed a short N256 feasibility audit across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



That audit used:



final time = 0.1



Phase 12G accepted that result and approved an intermediate longer N256 feasibility design.



The next controlled step is to extend N256 feasibility from:



final time = 0.1



to:



final time = 0.5



This remains a feasibility audit.



It is not a full N256 final-time-1.0 audit.



It is not a convergence study.



It is not a turbulence study.



It is not a k^-3 study.



It is not a method-superiority study.



\## Recommended Next Audit



Recommended next phase:



Phase 12I — N256 Three-Method Longer Feasibility Audit



Purpose:



Run an intermediate longer N256 feasibility audit across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



using:



run\_selectable\_diagnostic(...)



for each method.



\## Recommended Phase 12I Parameters



| Parameter | Value |

|---|---:|

| N | 256 |

| Re | 1000 |

| dt | 0.001 |

| steps | 500 |

| final time | 0.5 |

| log\_every | 50 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



Reason:



This is a conservative intermediate step between:



\- Phase 12F: final time 0.1

\- a future possible N256 final time 1.0 audit



\## Recommended Initial Field



Use the same deterministic smooth multimode field used in previous controlled phases:



\- sin(2X) cos(2Y)

\- 0.75 sin(3X) cos(Y)

\- 0.50 sin(X) cos(4Y)

\- 0.35 cos(4X - 2Y)



Then rescale to:



RMS = 0.01



Reason:



This keeps the N256 longer feasibility test tied to the already validated N64, N128, and short N256 controlled diagnostic setup.



\## Required Method Runs



The Phase 12I audit should run:



SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic(...)



SelectableAdvectionSolver(advection\_method="pseudo\_spectral").run\_selectable\_diagnostic(...)



SelectableAdvectionSolver(advection\_method="arakawa").run\_selectable\_diagnostic(...)



Each method should use:



\- same N

\- same Re

\- same dt

\- same steps

\- same log\_every

\- same initial\_w

\- same forcing

\- same dealiasing mask

\- same diagnostics definitions



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

| phase12i\_N256\_three\_method\_longer\_feasibility\_audit.py | audit script |

| PHASE12I\_N256\_THREE\_METHOD\_LONGER\_FEASIBILITY\_AUDIT.csv | method-level audit table |

| PHASE12I\_N256\_THREE\_METHOD\_LONGER\_FEASIBILITY\_PAIRWISE.csv | pairwise method comparison table |

| PHASE12I\_N256\_THREE\_METHOD\_LONGER\_FEASIBILITY\_AUDIT\_REPORT.md | audit report |



The audit may also create selectable diagnostic output folders under:



experiments/selectable\_diagnostics/phase12I\_N256\_fd\_centered



experiments/selectable\_diagnostics/phase12I\_N256\_pseudo\_spectral



experiments/selectable\_diagnostics/phase12I\_N256\_arakawa



\## Required Global Checks



The Phase 12I audit should check:



1\. SpectralSolver imports.



2\. SelectableAdvectionSolver imports.



3\. Supported methods are exactly:



&#x20;  - fd\_centered

&#x20;  - pseudo\_spectral

&#x20;  - arakawa



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



15\. steps is exactly 500.



16\. final time is exactly 0.5.



17\. log\_every is exactly 50.



18\. all methods use the same grid shape.



19\. all methods use the same dx.



20\. all methods use the same dt.



21\. all methods use the same nu.



22\. all methods use the same dealiasing mask.



23\. all methods use the same forcing.



24\. shared initial field is not mutated.



\## Required Per-Method Checks



For each method, the audit should check:



1\. diagnostic run completes



2\. final\_w exists



3\. final\_w is finite



4\. final\_w is real



5\. final\_w has expected shape



6\. solver.w is not mutated



7\. initial\_w is not mutated



8\. output paths are present



9\. output files exist



10\. metadata is written



11\. diagnostics CSV is written



12\. spectrum CSV is written



13\. summary JSON is written



14\. initial state file is written



15\. final state file is written



16\. diagnostics contain step 0



17\. diagnostics contain final step 500



18\. diagnostics contain expected logged steps



19\. spectrum contains k, E\_k, mode\_count



20\. spectrum is finite



21\. spectrum is nonnegative within tolerance



22\. metadata advection\_method matches the selected method



23\. metadata production\_ready is false



24\. metadata turbulence\_claim is false



25\. metadata k\_minus\_3\_claim is false



26\. summary production\_ready is false



27\. summary turbulence\_claim is false



28\. summary k\_minus\_3\_claim is false



\## Expected Logged Steps



The diagnostics should include:



\- 0

\- 50

\- 100

\- 150

\- 200

\- 250

\- 300

\- 350

\- 400

\- 450

\- 500



\## Required Method Metrics



For each method, record:



\- N

\- Re

\- dt

\- steps

\- final time

\- log\_every

\- method

\- elapsed seconds

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

\- method result



\## Required Pairwise Comparisons



The audit should compare these method pairs:



| Pair |

|---|

| pseudo\_spectral vs fd\_centered |

| arakawa vs fd\_centered |

| arakawa vs pseudo\_spectral |



For each pair, record:



\- final field max abs difference

\- final field RMS/L2 difference

\- final field relative L2 difference

\- energy relative difference

\- enstrophy relative difference

\- RMS relative difference

\- spectrum relative L2 difference

\- spectrum energy sum relative difference

\- spectrum cosine similarity

\- dominant shell agreement

\- pairwise result



\## Required Diagnostics Checks



For each method, the diagnostics CSV should include:



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

\- final step 500 exists

\- logged steps are present

\- all logged diagnostics are finite

\- finite flags are true

\- real flags are true

\- diagnostic time is monotone



\## Recommended Sanity Bounds



Use broad feasibility bounds.



| Quantity | Suggested Bound |

|---|---:|

| final RMS ratio relative to initial RMS | between 0.01 and 100 |

| final energy ratio relative to initial energy | between 0.0001 and 10000 |

| final enstrophy ratio relative to initial enstrophy | between 0.0001 and 10000 |

| spectrum energy direct relative error | <= 1e-10 |

| pairwise field relative L2 difference | record only, do not fail unless NaN or infinite |

| pairwise spectrum relative L2 difference | record only, do not fail unless NaN or infinite |

| high-k fraction k >= 10 | record only |

| runtime | record, do not fail unless the run does not complete |



Reason:



The purpose is intermediate feasibility, not proof.



\## Expected Result



Expected Phase 12I result:



PASS



Expected interpretation:



All three selectable methods can complete an intermediate N256 controlled diagnostic run through final time 0.5, remain finite and real, write outputs, and preserve metadata guardrails.



\## What a PASS Would Confirm



A PASS would confirm:



1\. N256 intermediate feasibility is acceptable for all three selectable methods.



2\. run\_selectable\_diagnostic works at N256 for fd\_centered through final time 0.5.



3\. run\_selectable\_diagnostic works at N256 for pseudo\_spectral through final time 0.5.



4\. run\_selectable\_diagnostic works at N256 for arakawa through final time 0.5.



5\. output writing works at N256 for all three methods.



6\. diagnostics remain finite at N256 for all three methods in the intermediate test.



7\. spectrum writing works at N256 for all three methods.



8\. pairwise comparisons can be computed at N256.



9\. metadata guardrails remain active.



10\. SelectableAdvectionSolver.run() remains disabled.



11\. SpectralSolver remains unchanged.



\## What a PASS Would Not Confirm



A PASS would not confirm:



1\. full N256 final-time-1.0 feasibility



2\. N256 long-run stability beyond final time 0.5



3\. convergence



4\. convergence order



5\. turbulence



6\. k^-3 scaling



7\. inertial range behavior



8\. method superiority



9\. production readiness



10\. statistical steady state behavior



\## What a FAIL Would Mean



A FAIL would mean the project should stop before attempting a full N256 final-time-1.0 comparison.



Possible causes to inspect:



\- runtime too long

\- memory pressure

\- output writing failure

\- diagnostics failure

\- numerical instability

\- shape mismatch

\- metadata guardrail failure

\- method-specific operator issue



Do not proceed to full N256 final-time-1.0 comparisons until the failure is understood.



\## Recommended Phase 12J



After Phase 12I, the next phase should be:



Phase 12J — N256 Three-Method Longer Feasibility Decision Gate



Purpose:



Document the Phase 12I result and decide whether to proceed to one of these options:



1\. N256 full final-time-1.0 feasibility design



2\. N256 fd\_centered-only final-time-1.0 feasibility design



3\. stop N256 expansion and archive Phase 12



4\. revise feasibility parameters



Recommended path if Phase 12I passes:



Phase 12K — N256 Full Final-Time-1.0 Feasibility Design



\## Guardrails



Phase 12I must preserve:



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



Correct statement after Phase 12H:



An N256 three-method intermediate longer controlled selectable diagnostic feasibility audit has been designed.



Incorrect statement:



The project has proven full N256 feasibility, convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Decision



Phase 12H decision:



PROCEED TO PHASE 12I N256 THREE-METHOD LONGER FEASIBILITY AUDIT.



Do not run a full N256 final-time-1.0 three-method comparison yet.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims.



Do not make method superiority claims.



\## Final Result



Phase 12H N256 three-method longer feasibility design:



PASS



Next phase:



Phase 12I — N256 Three-Method Longer Feasibility Audit

