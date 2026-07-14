\# Phase 11J Selectable Run-Loop Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.8-phase11I-controlled-forced-response-spectrum-decision-gate

\- Current previous commit: 9121fa3

\- Design file: PHASE11J\_SELECTABLE\_RUN\_LOOP\_DESIGN.md



\## Purpose



Phase 11J is a design-only phase.



The purpose is to design a safe selectable diagnostic run-loop pathway.



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



The project has passed:



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

| Phase 11I controlled forced-response spectrum decision gate | PASS |



\## Why Phase 11J Is Needed



The selectable method path has been validated through:



\- direct advection comparisons

\- RHS equivalence

\- one-step equivalence

\- no-forcing drift

\- controlled forced response

\- controlled forced-response spectrum diagnostics



However, the project still does not have an audited selectable diagnostic run-loop.



Current audits repeatedly call:



step\_once\_selectable(w)



inside standalone audit scripts.



The next engineering question is:



Can a selectable diagnostic run-loop be designed safely while preserving the validated SpectralSolver baseline and keeping SelectableAdvectionSolver.run() disabled?



\## Design Decision



Proceed with a separate diagnostic run-loop method.



Recommended future method name:



run\_selectable\_diagnostic()



Recommended location:



project/solver/selectable\_advection\_solver.py



Do not enable or modify:



run()



Reason:



run() should remain disabled to avoid confusing the selectable diagnostic pathway with the validated baseline SpectralSolver.run().



A clearly named method, run\_selectable\_diagnostic(), is safer and more explicit.



\## Rejected Design Option



Rejected option:



Enable SelectableAdvectionSolver.run()



Reason:



This would create ambiguity between:



\- SpectralSolver.run()

\- SelectableAdvectionSolver.run()

\- selectable diagnostic runs



The project is not ready to call selectable runs production-ready.



Therefore, run() should remain disabled.



\## Recommended Method Interface



Future method:



run\_selectable\_diagnostic(

&#x20;   initial\_w,

&#x20;   steps=None,

&#x20;   log\_every=100,

&#x20;   write\_outputs=True,

&#x20;   save\_final\_state=True,

&#x20;   save\_initial\_state=True,

)



Recommended behavior:



\- If steps is None, use self.steps.

\- initial\_w is required.

\- Validate initial\_w shape.

\- Copy initial\_w into a local variable.

\- Repeatedly call step\_once\_selectable(w).

\- Do not mutate input initial\_w.

\- Do not mutate solver.w.

\- Do not call SpectralSolver.run().

\- Do not call SelectableAdvectionSolver.run().

\- Write clearly labeled diagnostic outputs if write\_outputs=True.

\- Return a structured result dictionary.



\## Required Output Files



If write\_outputs=True, the diagnostic run-loop should write:



| File | Purpose |

|---|---|

| selectable\_metadata.json | Run metadata and guardrails |

| selectable\_diagnostics.csv | Time-history diagnostics |

| selectable\_spectrum.csv | Final spectrum |

| selectable\_final\_state.npy | Final vorticity field |

| selectable\_initial\_state.npy | Initial vorticity field |

| selectable\_run\_summary.json | Final summary metrics |



The filenames should include the word selectable to avoid confusion with baseline SpectralSolver outputs.



\## Output Directory Rule



The run path should be explicit.



Recommended run path pattern:



experiments/selectable\_diagnostics/run\_YYYY-MM-DD\_HH-MM-SS\_METHOD



Examples:



experiments/selectable\_diagnostics/run\_2026-07-14\_12-30-00\_fd\_centered



experiments/selectable\_diagnostics/run\_2026-07-14\_12-30-00\_pseudo\_spectral



experiments/selectable\_diagnostics/run\_2026-07-14\_12-30-00\_arakawa



The method name should be visible in the path.



\## Required Metadata Fields



The metadata file should include:



| Metadata Field | Required Value or Meaning |

|---|---|

| solver\_variant | selectable\_advection |

| solver\_class | SelectableAdvectionSolver |

| baseline\_solver\_class | SpectralSolver |

| advection\_method | fd\_centered, pseudo\_spectral, or arakawa |

| diagnostic\_run\_method | run\_selectable\_diagnostic |

| run\_method\_enabled | false |

| production\_baseline\_modified | false |

| selectable\_run\_type | diagnostic |

| production\_ready | false |

| turbulence\_claim | false |

| k\_minus\_3\_claim | false |

| forcing\_method | inherited baseline forcing unless overridden by audit subclass |

| streamfunction\_method | spectral |

| velocity\_method | spectral |

| diffusion\_method | spectral |

| timestep\_method | RK2-style |

| dealiasing\_method | post-step 2/3 spectral mask |

| steps | number of steps |

| dt | time step |

| final\_time | steps \* dt |

| N | grid resolution |

| Re | Reynolds number |

| nu | viscosity |

| initial\_rms | initial vorticity RMS |

| final\_rms | final vorticity RMS |

| final\_energy | final kinetic energy |

| final\_enstrophy | final enstrophy |



\## Required Diagnostics



At each logged step, record:



\- step

\- time

\- rms\_vorticity

\- kinetic\_energy

\- enstrophy

\- max\_abs\_vorticity

\- finite

\- real



The diagnostic log should include step 0.



The diagnostic log should include the final step.



\## Required Spectrum Output



At the final step, write a spectrum CSV with:



\- k

\- E(k)

\- mode\_count



The spectrum should use the existing project method:



energy\_spectrum(w)



or:



compute\_kinetic\_energy\_spectrum\_from\_vorticity(w, kx, ky)



The diagnostic run-loop should not fit slopes.



The diagnostic run-loop should not claim k^-3 scaling.



\## Required Return Object



The method should return a dictionary with:



\- metadata

\- diagnostics dataframe or records

\- spectrum dataframe or records

\- initial\_w copy

\- final\_w

\- summary metrics



The return object should be useful for audit scripts without requiring disk reads.



\## Required Guardrails



The future implementation must preserve these guardrails:



1\. SpectralSolver remains unchanged.



2\. SelectableAdvectionSolver.run() remains disabled.



3\. fd\_centered remains the default method.



4\. Arakawa does not become the default method.



5\. run\_selectable\_diagnostic is explicitly diagnostic.



6\. Metadata must say production\_ready=false.



7\. Metadata must say turbulence\_claim=false.



8\. Metadata must say k\_minus\_3\_claim=false.



9\. The method must not mutate input initial\_w.



10\. The method must not mutate solver.w.



11\. The method must not call SpectralSolver.run().



12\. The method must not call SelectableAdvectionSolver.run().



13\. Output filenames must be clearly distinguishable from baseline SpectralSolver outputs.



\## First Implementation Phase



Recommended next phase:



Phase 11K — Selectable Diagnostic Run-Loop Scaffold



Purpose:



Implement run\_selectable\_diagnostic() as a scaffold.



Allowed file modification:



project/solver/selectable\_advection\_solver.py



Required source files that must remain unchanged:



\- project/solver/spectral\_solver.py

\- project/solver/advection\_operators.py



\## Phase 11K Minimum Implementation



Phase 11K should add:



run\_selectable\_diagnostic()



to:



SelectableAdvectionSolver



The implementation should:



\- validate initial\_w shape

\- copy initial\_w

\- repeatedly call step\_once\_selectable(w)

\- log diagnostics

\- compute final spectrum

\- optionally write outputs

\- return a structured result

\- keep run() disabled



Phase 11K should not run long simulations.



Phase 11K should not make turbulence claims.



Phase 11K should not make k^-3 claims.



\## Phase 11K.1 Scaffold Audit



After Phase 11K implementation, Phase 11K.1 should audit the scaffold.



The audit should test:



\- import succeeds

\- run\_selectable\_diagnostic exists

\- run() remains disabled

\- SpectralSolver file has no git diff

\- advection\_operators file has no git diff

\- invalid advection method remains rejected

\- fd\_centered diagnostic run works for a tiny test

\- pseudo\_spectral diagnostic run works for a tiny test

\- arakawa diagnostic run works for a tiny test

\- initial\_w is not mutated

\- solver.w is not mutated

\- metadata fields are present

\- diagnostics are written

\- spectrum is written

\- final state is written

\- initial state is written

\- returned result contains final\_w

\- returned result contains metadata

\- no turbulence claim is present

\- no k\_minus\_3 claim is present



Recommended tiny test:



| Parameter | Value |

|---|---:|

| N | 32 or 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 5 |

| log\_every | 1 |



Reason:



The first audit should test mechanics, not numerical research behavior.



\## Phase 11L fd\_centered Equivalence Audit



After the scaffold audit passes, Phase 11L should compare:



SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic()



against a direct baseline loop transcription for a short controlled run.



This should verify that the diagnostic run-loop reproduces baseline fd\_centered behavior.



Do not compare Arakawa production behavior until fd\_centered run-loop equivalence passes.



\## What Phase 11J Does Not Approve



Phase 11J does not approve:



\- enabling SelectableAdvectionSolver.run()

\- production simulations

\- turbulence experiments

\- k^-3 experiments

\- Arakawa as default

\- replacing SpectralSolver

\- long forced-response simulations

\- slope fitting as evidence



\## Scientific Boundary



Correct statement after Phase 11J:



A diagnostic selectable run-loop has been designed, with explicit guardrails to preserve SpectralSolver and prevent unsupported turbulence or k^-3 claims.



Incorrect statement:



The selectable solver is production-ready or proves turbulence or k^-3 scaling.



That statement is not supported.



\## Decision



Phase 11J decision:



PROCEED TO PHASE 11K SELECTABLE DIAGNOSTIC RUN-LOOP SCAFFOLD.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not run turbulence experiments.



Do not make k^-3 claims.



\## Final Result



Phase 11J design:



PASS



Next phase:



Phase 11K — Selectable Diagnostic Run-Loop Scaffold



Required guardrails:



\- SpectralSolver must remain unchanged.

\- SelectableAdvectionSolver.run() must remain disabled.

\- run\_selectable\_diagnostic must be explicitly diagnostic.

\- Metadata must clearly state no turbulence claim and no k^-3 claim.

