\# Phase 11R Longer Controlled Selectable Method Diagnostic Comparison Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.17-phase11Q-controlled-selectable-method-diagnostic-comparison-decision-gate

\- Current previous commit: daf34e4

\- Design file: PHASE11R\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_DESIGN.md



\## Purpose



Phase 11R is a design-only phase.



The purpose is to design a longer controlled diagnostic comparison across the selectable advection methods:



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



\## Why Phase 11R Is Needed



Phase 11P passed a short controlled selectable method diagnostic comparison at:



final time = 0.02



Phase 11Q accepted that result and approved a longer controlled comparison design.



The next step is to extend the controlled diagnostic comparison to:



final time = 1.0



This is still a controlled diagnostic test.



It is not a turbulence test.



It is not a k^-3 test.



It is not a production simulation.



\## Recommended Next Audit



Recommended next phase:



Phase 11S — Longer Controlled Selectable Method Diagnostic Comparison Audit



Purpose:



Run a longer controlled diagnostic comparison across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



using:



run\_selectable\_diagnostic(...)



for each method.



\## Recommended Audit Parameters



Use the same controlled setup style as Phase 11P, but extend the runtime.



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



This extends the short controlled comparison from final time 0.02 to final time 1.0 while preserving the same resolution, Reynolds number, initial field style, and forcing style.



\## Recommended Initial Field



Use the same deterministic smooth multimode field used in Phase 11M and Phase 11P:



\- sin(2X) cos(2Y)

\- 0.75 sin(3X) cos(Y)

\- 0.50 sin(X) cos(4Y)

\- 0.35 cos(4X - 2Y)



Then rescale to:



RMS = 0.01



Reason:



This field is smooth, deterministic, nontrivial, and already tied to the previous equivalence and comparison audits.



\## Required Method Runs



The Phase 11S audit should run:



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

| phase11s\_longer\_controlled\_selectable\_method\_diagnostic\_comparison\_audit.py | audit script |

| PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv | method-level audit results |

| PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv | pairwise method comparisons |

| PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT\_REPORT.md | audit report |



The audit may also create selectable diagnostic output folders under:



experiments/selectable\_diagnostics/phase11S\_fd\_centered



experiments/selectable\_diagnostics/phase11S\_pseudo\_spectral



experiments/selectable\_diagnostics/phase11S\_arakawa



\## Required Global Checks



The Phase 11S audit should check:



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



11\. selectable\_advection\_solver file has no unexpected git diff during the audit.



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



16\. diagnostics contain step 0



17\. diagnostics contain the final step



18\. diagnostics contain the expected logged steps



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



\## Required Method Metrics



For each method, record:



\- initial RMS vorticity

\- final RMS vorticity

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

\- minimum diagnostic RMS

\- maximum diagnostic RMS

\- minimum diagnostic energy

\- maximum diagnostic energy

\- minimum diagnostic enstrophy

\- maximum diagnostic enstrophy

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

\- spectrum cosine similarity

\- dominant shell agreement



\## Required Time-History Comparison



Because Phase 11S is longer than Phase 11P, the audit should also inspect time histories.



For each method, the diagnostics CSV should include:



\- step

\- time

\- rms\_vorticity

\- kinetic\_energy

\- enstrophy

\- max\_abs\_vorticity

\- finite

\- real



The audit should check:



\- step 0 exists

\- final step exists

\- logged steps are present

\- all logged diagnostics are finite

\- all logged diagnostics are real where applicable

\- no logged RMS is NaN

\- no logged energy is NaN

\- no logged enstrophy is NaN



\## Pass/Fail Philosophy



The audit should not require pseudo\_spectral or arakawa to exactly match fd\_centered.



They are different nonlinear advection discretizations.



Pairwise differences are expected.



The audit should pass if:



\- every method completes

\- every method remains finite

\- every method remains real

\- every method writes required outputs

\- every method preserves metadata guardrails

\- every method has finite nonnegative spectra

\- pairwise comparison metrics are successfully computed

\- no method produces obvious blow-up

\- no method produces NaN or infinite diagnostics

\- no unsupported claim is made



\## Recommended Sanity Bounds



Use broad sanity bounds, not equality bounds.



Recommended first-pass bounds:



| Quantity | Suggested Bound |

|---|---:|

| final RMS ratio relative to initial RMS | between 0.01 and 100 |

| final energy ratio relative to initial energy | between 0.0001 and 10000 |

| final enstrophy ratio relative to initial enstrophy | between 0.0001 and 10000 |

| spectrum energy direct relative error | <= 1e-10 |

| high-k energy fraction k >= 10 | record only, do not overinterpret |

| pairwise field relative L2 difference | record only, do not fail unless NaN or infinite |

| pairwise spectrum relative L2 difference | record only, do not fail unless NaN or infinite |



Reason:



The longer run is still diagnostic. The goal is to verify stable, comparable, auditable behavior, not to prove equality or superiority.



\## Expected Result



Expected Phase 11S result:



PASS



Expected interpretation:



All three selectable methods complete a longer controlled diagnostic run and produce finite, real, comparable outputs with valid metadata guardrails.



\## What a PASS Would Confirm



A PASS would confirm:



1\. run\_selectable\_diagnostic works for all three methods through final time 1.0.



2\. fd\_centered remains the internal reference method.



3\. pseudo\_spectral remains comparable against fd\_centered under diagnostic conditions.



4\. arakawa remains comparable against fd\_centered under diagnostic conditions.



5\. pairwise method differences can be measured over a longer controlled run.



6\. spectra can be compared across methods over a longer controlled run.



7\. time-history diagnostics remain finite.



8\. metadata guardrails remain active.



9\. SelectableAdvectionSolver.run() remains disabled.



10\. SpectralSolver remains unchanged.



\## What a PASS Would Not Confirm



A PASS would not confirm:



1\. production readiness



2\. turbulence



3\. k^-3 scaling



4\. inertial range behavior



5\. Arakawa superiority



6\. pseudo\_spectral superiority



7\. statistical steady state behavior



8\. long-time asymptotic stability



9\. validated production simulation behavior



10\. physical cascade behavior



\## What a FAIL Would Mean



A FAIL would mean the longer controlled selectable comparison pathway is not ready.



A FAIL should stop advancement.



Do not proceed to longer runs or higher-resolution comparisons until the failure is inspected.



\## Recommended Phase 11T



After Phase 11S, the next phase should be:



Phase 11T — Longer Controlled Selectable Method Diagnostic Comparison Decision Gate



Purpose:



Document the Phase 11S results and decide whether to proceed to one of the following:



\- N=128 longer controlled selectable comparison design

\- longer final-time comparison design

\- no-forcing longer comparison design

\- controlled forcing-amplitude comparison design



Do not proceed directly to turbulence claims.



Do not proceed directly to k^-3 claims.



\## Guardrails



Phase 11S must preserve:



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



Correct statement after Phase 11R:



A longer controlled selectable method diagnostic comparison has been designed.



Incorrect statement:



The project has proven Arakawa, pseudo\_spectral, turbulence, or k^-3 behavior.



Those statements are not supported.



\## Decision



Phase 11R decision:



PROCEED TO PHASE 11S LONGER CONTROLLED SELECTABLE METHOD DIAGNOSTIC COMPARISON AUDIT.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not run turbulence experiments.



Do not make k^-3 claims.



Do not make method superiority claims.



\## Final Result



Phase 11R design:



PASS



Next phase:



Phase 11S — Longer Controlled Selectable Method Diagnostic Comparison Audit

