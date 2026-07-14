\# Phase 12K N256 Full Final-Time-1.0 Feasibility Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.36-phase12J-N256-three-method-longer-feasibility-decision-gate

\- Current previous commit: dd8132a

\- Design file: PHASE12K\_N256\_FULL\_FINAL\_TIME\_1\_0\_FEASIBILITY\_DESIGN.md



\## Purpose



Phase 12K is a design-only phase.



The purpose is to design a full N256 final-time-1.0 feasibility audit across all selectable advection methods:



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



\## Why Phase 12K Is Needed



Phase 12F passed a short N256 three-method feasibility audit at:



final time = 0.1



Phase 12I passed an intermediate N256 three-method feasibility audit at:



final time = 0.5



Phase 12J accepted the Phase 12I result and approved a full N256 final-time-1.0 feasibility design.



The next controlled step is to extend N256 feasibility from:



final time = 0.5



to:



final time = 1.0



This remains a feasibility audit.



It is not a convergence study.



It is not a turbulence study.



It is not a k^-3 study.



It is not a method-superiority study.



\## Recommended Next Audit



Recommended next phase:



Phase 12L — N256 Full Final-Time-1.0 Feasibility Audit



Purpose:



Run a full final-time-1.0 N256 feasibility audit across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



using:



run\_selectable\_diagnostic(...)



for each method.



\## Recommended Phase 12L Parameters



| Parameter | Value |

|---|---:|

| N | 256 |

| Re | 1000 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| log\_every | 100 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



Reason:



This extends the passed Phase 12I final-time-0.5 audit to final time 1.0 while preserving the same controlled setup.



\## Runtime Expectation



Phase 12I used 500 steps and completed successfully.



Phase 12L uses 1000 steps.



Expected runtime should be roughly about twice Phase 12I, but actual runtime may vary by system load and disk I/O.



This remains a diagnostic feasibility audit, not a production run.



\## Recommended Initial Field



Use the same deterministic smooth multimode field used in previous controlled phases:



\- sin(2X) cos(2Y)

\- 0.75 sin(3X) cos(Y)

\- 0.50 sin(X) cos(4Y)

\- 0.35 cos(4X - 2Y)



Then rescale to:



RMS = 0.01



Reason:



This keeps the full N256 feasibility audit tied to the already validated N64, N128, and shorter N256 controlled diagnostic setup.



\## Required Method Runs



The Phase 12L audit should run:



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

| phase12l\_N256\_full\_final\_time\_1\_0\_feasibility\_audit.py | audit script |

| PHASE12L\_N256\_FULL\_FINAL\_TIME\_1\_0\_FEASIBILITY\_AUDIT.csv | method-level audit table |

| PHASE12L\_N256\_FULL\_FINAL\_TIME\_1\_0\_FEASIBILITY\_PAIRWISE.csv | pairwise method comparison table |

| PHASE12L\_N256\_FULL\_FINAL\_TIME\_1\_0\_FEASIBILITY\_AUDIT\_REPORT.md | audit report |



The audit may also create selectable diagnostic output folders under:



experiments/selectable\_diagnostics/phase12L\_N256\_fd\_centered



experiments/selectable\_diagnostics/phase12L\_N256\_pseudo\_spectral



experiments/selectable\_diagnostics/phase12L\_N256\_arakawa



\## Required Global Checks



The Phase 12L audit should check:



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



15\. steps is exactly 1000.



16\. final time is exactly 1.0.



17\. log\_every is exactly 100.



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



17\. diagnostics contain final step 1000



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

\- 100

\- 200

\- 300

\- 400

\- 500

\- 600

\- 700

\- 800

\- 900

\- 1000



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

\- final step 1000 exists

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



The purpose is full N256 feasibility, not convergence proof.



\## Expected Result



Expected Phase 12L result:



PASS



Expected interpretation:



All three selectable methods can complete a full N256 controlled diagnostic run through final time 1.0, remain finite and real, write outputs, and preserve metadata guardrails.



\## What a PASS Would Confirm



A PASS would confirm:



1\. N256 final-time-1.0 feasibility is acceptable for fd\_centered.



2\. N256 final-time-1.0 feasibility is acceptable for pseudo\_spectral.



3\. N256 final-time-1.0 feasibility is acceptable for arakawa.



4\. run\_selectable\_diagnostic works at N256 for all three methods through final time 1.0.



5\. output writing works at N256 for all three methods.



6\. diagnostics remain finite at N256 for all three methods through final time 1.0.



7\. spectrum writing works at N256 for all three methods.



8\. pairwise comparisons can be computed at N256.



9\. metadata guardrails remain active.



10\. SelectableAdvectionSolver.run() remains disabled.



11\. SpectralSolver remains unchanged.



\## What a PASS Would Not Confirm



A PASS would not confirm:



1\. convergence



2\. convergence order



3\. turbulence



4\. k^-3 scaling



5\. inertial range behavior



6\. method superiority



7\. production readiness



8\. statistical steady state behavior



9\. asymptotic long-time stability beyond final time 1.0



10\. physical cascade behavior



\## What a FAIL Would Mean



A FAIL would mean the project should stop before attempting any N256 convergence audit.



Possible causes to inspect:



\- runtime too long

\- memory pressure

\- output writing failure

\- diagnostics failure

\- numerical instability

\- shape mismatch

\- metadata guardrail failure

\- method-specific operator issue



Do not proceed to convergence auditing until the failure is understood.



\## Recommended Phase 12M



After Phase 12L, the next phase should be:



Phase 12M — N256 Full Final-Time-1.0 Feasibility Decision Gate



Purpose:



Document the Phase 12L result and decide whether the project is ready for a controlled three-resolution comparison design.



Recommended path if Phase 12L passes:



Phase 12N — Controlled Three-Resolution Comparison Design



Candidate resolutions:



\- N = 64

\- N = 128

\- N = 256



Candidate final time:



\- 1.0



Candidate methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Important:



Even after Phase 12L, do not claim convergence until a dedicated convergence comparison phase is designed and executed.



\## Guardrails



Phase 12L must preserve:



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



Correct statement after Phase 12K:



A full N256 final-time-1.0 three-method selectable diagnostic feasibility audit has been designed.



Incorrect statement:



The project has proven N256 convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Decision



Phase 12K decision:



PROCEED TO PHASE 12L N256 FULL FINAL-TIME-1.0 FEASIBILITY AUDIT.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims.



Do not make method superiority claims.



\## Final Result



Phase 12K N256 full final-time-1.0 feasibility design:



PASS



Next phase:



Phase 12L — N256 Full Final-Time-1.0 Feasibility Audit

