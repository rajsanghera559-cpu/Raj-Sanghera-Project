\# Phase 11O Controlled Selectable Method Diagnostic Comparison Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.14-phase11N-fd-centered-diagnostic-run-loop-equivalence-decision-gate

\- Current previous commit: 124aa9e

\- Design file: PHASE11O\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_DESIGN.md



\## Purpose



Phase 11O is a design-only phase.



The purpose is to design a controlled diagnostic comparison across the selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The comparison should use:



run\_selectable\_diagnostic(...)



for each method.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



This phase does not claim one method is physically superior.



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



\## Why This Phase Is Needed



Phase 11M proved that:



SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic(...)



reproduces a direct local transcription of the validated baseline fd\_centered solver path.



Phase 11N accepted that result and approved controlled selectable-method comparison design.



The next step is to compare the three selectable methods under identical controlled diagnostic conditions.



\## What Phase 11O Should Design



Phase 11O should design an audit that compares:



| Method | Role |

|---|---|

| fd\_centered | internal reference path |

| pseudo\_spectral | selectable diagnostic candidate |

| arakawa | selectable diagnostic candidate |



The comparison should be numerical and diagnostic.



The comparison should not declare a winner.



The comparison should report controlled differences only.



\## Recommended Next Audit



Recommended next phase:



Phase 11P — Controlled Selectable Method Diagnostic Comparison Audit



Purpose:



Run the same short controlled diagnostic case for:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Then compare:



\- final field metrics

\- kinetic energy

\- enstrophy

\- RMS vorticity

\- final spectra

\- dominant shell

\- pairwise field differences

\- pairwise spectrum differences

\- metadata guardrails



\## Recommended Audit Parameters



Use the same controlled setup as Phase 11M.



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 20 |

| log\_every | 1 |

| initial RMS | 0.01 |

| forcing | inherited baseline deterministic forcing |

| methods | fd\_centered, pseudo\_spectral, arakawa |



Reason:



This keeps the comparison short, deterministic, and directly tied to the already-passed fd\_centered equivalence audit.



\## Recommended Initial Field



Use the same deterministic smooth multimode field used in Phase 11M:



\- sin(2X) cos(2Y)

\- 0.75 sin(3X) cos(Y)

\- 0.50 sin(X) cos(4Y)

\- 0.35 cos(4X - 2Y)



Then rescale to:



RMS = 0.01



Reason:



This field is smooth, deterministic, nontrivial, and already used in the previous equivalence audit.



\## Required Method Runs



The Phase 11P audit should run:



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



Reason:



The audit should use only the explicitly diagnostic method:



run\_selectable\_diagnostic(...)



\## Required Output Files



The next audit should write:



| File | Purpose |

|---|---|

| phase11p\_controlled\_selectable\_method\_diagnostic\_comparison\_audit.py | audit script |

| PHASE11P\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv | method-level audit results |

| PHASE11P\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv | pairwise method comparisons |

| PHASE11P\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT\_REPORT.md | audit report |



The audit may also create selectable diagnostic output folders under:



experiments/selectable\_diagnostics/phase11P\_fd\_centered



experiments/selectable\_diagnostics/phase11P\_pseudo\_spectral



experiments/selectable\_diagnostics/phase11P\_arakawa



\## Required Global Checks



The Phase 11P audit should check:



1\. SpectralSolver imports.



2\. SelectableAdvectionSolver imports.



3\. Supported methods are exactly:



&#x20;  - fd\_centered

&#x20;  - pseudo\_spectral

&#x20;  - arakawa



4\. Default method remains fd\_centered.



5\. compute\_rhs\_selectable exists.



6\. step\_once\_selectable exists.



7\. run\_selectable\_diagnostic exists.



8\. SelectableAdvectionSolver.run() remains disabled.



9\. SpectralSolver file has no git diff.



10\. advection\_operators file has no git diff.



11\. SelectableAdvectionSolver source file has no unexpected diff during audit.



12\. All methods use the same grid shape.



13\. All methods use the same dx.



14\. All methods use the same dt.



15\. All methods use the same nu.



16\. All methods use the same dealiasing mask.



17\. All methods use the same forcing.



18\. The shared initial field is not mutated.



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



16\. diagnostics contain steps 0 through 20



17\. spectrum contains k, E\_k, mode\_count



18\. spectrum is finite



19\. spectrum is nonnegative within tolerance



20\. metadata advection\_method matches the selected method



21\. metadata production\_ready is false



22\. metadata turbulence\_claim is false



23\. metadata k\_minus\_3\_claim is false



24\. summary production\_ready is false



25\. summary turbulence\_claim is false



26\. summary k\_minus\_3\_claim is false



\## Required Method Metrics



For each method, record:



\- final RMS vorticity

\- final kinetic energy

\- final enstrophy

\- final max abs vorticity

\- spectrum energy sum

\- spectrum direct energy relative error

\- dominant shell

\- low-k energy fraction for k <= 4

\- high-k energy fraction for k >= 10

\- finite final state

\- real final state



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

\- dominant shell agreement

\- spectrum cosine similarity if convenient



\## Pass/Fail Philosophy



The audit should not require pseudo\_spectral or arakawa to exactly match fd\_centered.



They are different nonlinear advection discretizations.



Therefore, pairwise differences are expected.



The audit should pass if:



\- every method completes

\- every method remains finite

\- every method remains real

\- every method writes required outputs

\- every method preserves metadata guardrails

\- every method has finite nonnegative spectra

\- pairwise comparison metrics are successfully computed

\- no method produces obvious blow-up in this short controlled test

\- no unsupported claim is made



\## Recommended Sanity Bounds



Use broad sanity bounds, not equality bounds.



Recommended first-pass bounds:



| Quantity | Suggested Bound |

|---|---:|

| final RMS ratio relative to initial RMS | between 0.1 and 10 |

| final energy ratio relative to initial energy | between 0.01 and 100 |

| final enstrophy ratio relative to initial enstrophy | between 0.01 and 100 |

| spectrum energy direct relative error | <= 1e-10 |

| high-k energy fraction k >= 10 | record only, do not overinterpret |

| pairwise field relative L2 difference | record only, do not fail unless NaN or infinite |

| pairwise spectrum relative L2 difference | record only, do not fail unless NaN or infinite |



Reason:



This phase is a controlled diagnostic comparison, not a proof of method superiority.



\## Expected Result



Expected Phase 11P result:



PASS



Expected interpretation:



All three selectable methods complete the same short controlled diagnostic run and produce finite, real, comparable outputs with valid metadata guardrails.



\## What a PASS Would Confirm



A PASS would confirm:



1\. run\_selectable\_diagnostic works for all three methods in the same controlled setup.



2\. fd\_centered can serve as the internal reference method.



3\. pseudo\_spectral can be compared against fd\_centered under diagnostic conditions.



4\. arakawa can be compared against fd\_centered under diagnostic conditions.



5\. pairwise method differences can be measured.



6\. spectra can be compared across methods.



7\. metadata guardrails remain active.



8\. SelectableAdvectionSolver.run() remains disabled.



9\. SpectralSolver remains unchanged.



\## What a PASS Would Not Confirm



A PASS would not confirm:



1\. production readiness



2\. long-time stability



3\. turbulence



4\. k^-3 scaling



5\. inertial range behavior



6\. Arakawa superiority



7\. pseudo\_spectral superiority



8\. Arakawa production readiness



9\. pseudo\_spectral production readiness



10\. statistical steady state behavior



\## What a FAIL Would Mean



A FAIL would mean the controlled selectable comparison pathway is not ready.



A FAIL should stop advancement.



Do not proceed to longer runs until the controlled short comparison passes.



\## Recommended Phase 11Q



After Phase 11P, the next phase should be:



Phase 11Q — Controlled Selectable Method Diagnostic Comparison Decision Gate



Purpose:



Document the Phase 11P results and decide whether to proceed to a longer controlled selectable comparison.



Do not proceed directly to turbulence claims.



Do not proceed directly to k^-3 claims.



\## Guardrails



Phase 11P must preserve:



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



\## Scientific Boundary



Correct statement after Phase 11O:



A controlled selectable method diagnostic comparison has been designed.



Incorrect statement:



The project has proven Arakawa, pseudo\_spectral, turbulence, or k^-3 behavior.



Those statements are not supported.



\## Decision



Phase 11O decision:



PROCEED TO PHASE 11P CONTROLLED SELECTABLE METHOD DIAGNOSTIC COMPARISON AUDIT.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not run turbulence experiments.



Do not make k^-3 claims.



Do not make method superiority claims.



\## Final Result



Phase 11O design:



PASS



Next phase:



Phase 11P — Controlled Selectable Method Diagnostic Comparison Audit

