\# Phase 10J Selectable-Advection Solver Variant Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.42-phase10I-arakawa-operator-decision-gate

\- Current previous commit: f17eea8

\- Design file: PHASE10J\_SELECTABLE\_ADVECTION\_SOLVER\_VARIANT\_DESIGN.md



\## Purpose



Phase 10J is a design-only phase.



The purpose is to design a separate selectable-advection solver variant that can use one of several nonlinear advection operators without changing the validated baseline solver.



This phase does not modify SpectralSolver.



This phase does not add solver code.



This phase does not run a simulation.



This phase does not replace the validated baseline.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Design Decision



Create a separate solver variant.



Do not modify:



project/solver/spectral\_solver.py



Recommended new file:



project/solver/selectable\_advection\_solver.py



Recommended new class:



SelectableAdvectionSolver



Recommended relationship:



SelectableAdvectionSolver should inherit from SpectralSolver if this allows reuse of grid setup, streamfunction, velocity, diagnostics, and metadata logic without modifying SpectralSolver.



If inheritance creates risk, the safer fallback is to create a separate class that copies only the required baseline setup logic and documents the copied sections.



The preferred design is:



\- preserve SpectralSolver unchanged

\- create SelectableAdvectionSolver separately

\- make advection method explicit at construction

\- write selected advection method into metadata

\- require separate validation before research use



\## Baseline Solver Status



The validated baseline solver is:



project/solver/spectral\_solver.py



The baseline method is currently classified as:



mixed\_spectral\_finite\_difference



The baseline solver uses:



\- spectral streamfunction

\- spectral velocity

\- spectral diffusion

\- centered finite-difference nonlinear advection

\- RK2-style time stepping

\- post-step 2/3 spectral dealiasing



The baseline solver must remain unchanged.



The baseline validation chain remains valid only if SpectralSolver is not modified.



\## Selectable Methods



The selectable solver variant should support exactly these initial method names:



| Method Name | Operator Function | Status |

|---|---|---|

| fd\_centered | advection\_fd\_centered | baseline-compatible method |

| pseudo\_spectral | advection\_pseudo\_spectral | diagnostic comparison method |

| arakawa | advection\_arakawa | candidate conservative method |



Method names should be lowercase strings.



Invalid method names should raise ValueError.



No implicit aliasing should be allowed in the first version.



Accepted:



fd\_centered



pseudo\_spectral



arakawa



Rejected examples:



fd



finite\_difference



spectral



arakawa\_periodic



arka



\## Default Method



The default method should be:



fd\_centered



Reason:



fd\_centered is the current baseline nonlinear advection method.



The selectable solver variant must not silently change expected behavior.



A user must explicitly request:



pseudo\_spectral



or:



arakawa



if they want a non-baseline method.



\## Constructor Design



Recommended constructor argument:



advection\_method="fd\_centered"



Recommended constructor behavior:



1\. Store the selected advection method.

2\. Validate that the method is one of the accepted method names.

3\. Preserve all existing solver setup behavior.

4\. Do not modify SpectralSolver.

5\. Do not modify project/solver/advection\_operators.py during this phase.

6\. Record the selected method in metadata.



Recommended conceptual interface:



SelectableAdvectionSolver(

&#x20;   nx=64,

&#x20;   ny=64,

&#x20;   Re=1000,

&#x20;   dt=0.005,

&#x20;   steps=1001,

&#x20;   run\_path=...,

&#x20;   advection\_method="fd\_centered"

)



\## Internal Method Selection



Recommended internal method:



compute\_advection(self, w)



Expected behavior:



| advection\_method | compute\_advection behavior |

|---|---|

| fd\_centered | call advection\_fd\_centered(self, w) |

| pseudo\_spectral | call advection\_pseudo\_spectral(self, w, dealias\_product=False) |

| arakawa | call advection\_arakawa(self, w) |



The first selectable variant should avoid product de-aliasing options inside pseudo\_spectral unless explicitly designed later.



Keep pseudo\_spectral simple:



dealias\_product=False



Reason:



Phase 10H used pseudo-spectral advection without product dealiasing as the comparison reference.



Changing that now would mix two design changes.



\## Solver Update Rule



The update rule should preserve the project convention:



d omega / dt = -adv + diffusion + forcing



Each advection operator returns:



adv = u \* omega\_x + v \* omega\_y



For Arakawa:



advection\_arakawa returns -J(psi, omega)



Therefore the time update should still use:



\-adv



The solver variant should not special-case Arakawa sign inside the time step.



The sign belongs inside advection\_arakawa.



\## Metadata Requirements



Every run using SelectableAdvectionSolver must write metadata that includes:



| Metadata Field | Meaning |

|---|---|

| solver\_variant | selectable\_advection |

| solver\_class | SelectableAdvectionSolver |

| baseline\_solver\_class | SpectralSolver |

| advection\_method | fd\_centered, pseudo\_spectral, or arakawa |

| advection\_operator\_file | project/solver/advection\_operators.py |

| production\_baseline\_modified | false |

| method\_family | mixed\_spectral\_selectable\_advection |

| streamfunction\_method | spectral |

| velocity\_method | spectral |

| diffusion\_method | spectral |

| timestep\_method | RK2-style |

| dealiasing\_method | post-step 2/3 spectral mask |

| arakawa\_status | diagnostic\_candidate unless future audits promote it |

| turbulence\_claim | false |

| k\_minus\_3\_claim | false |



Metadata must make it impossible to confuse an Arakawa run with a baseline fd\_centered run.



\## Output Naming Rules



Recommended run-path naming pattern:



experiments/runs\_selectable/run\_YYYY-MM-DD\_HH-MM-SS\_METHOD



Examples:



experiments/runs\_selectable/run\_2026-07-13\_21-30-00\_fd\_centered



experiments/runs\_selectable/run\_2026-07-13\_21-30-00\_pseudo\_spectral



experiments/runs\_selectable/run\_2026-07-13\_21-30-00\_arakawa



Reason:



The method name should be visible before opening metadata.



\## Required Files for Future Phase 10K



Phase 10K should create only the scaffold.



Recommended files:



project/solver/selectable\_advection\_solver.py



phase10k\_selectable\_advection\_solver\_scaffold\_audit.py



PHASE10K\_SELECTABLE\_ADVECTION\_SOLVER\_SCAFFOLD\_AUDIT.csv



PHASE10K\_SELECTABLE\_ADVECTION\_SOLVER\_SCAFFOLD\_AUDIT\_REPORT.md



Phase 10K should not create production research runs.



Phase 10K should not run long simulations.



\## Phase 10K Minimum Scaffold Tests



The Phase 10K scaffold audit should test:



1\. SelectableAdvectionSolver imports.



2\. SpectralSolver still imports.



3\. SpectralSolver file is unchanged.



4\. Constructor accepts fd\_centered.



5\. Constructor accepts pseudo\_spectral.



6\. Constructor accepts arakawa.



7\. Constructor rejects invalid methods.



8\. compute\_advection returns finite output for each method.



9\. compute\_advection returns real output for each method.



10\. compute\_advection does not mutate input w.



11\. compute\_advection does not mutate solver.w.



12\. fd\_centered selectable output matches advection\_fd\_centered.



13\. pseudo\_spectral selectable output matches advection\_pseudo\_spectral.



14\. arakawa selectable output matches advection\_arakawa.



15\. Metadata includes advection\_method.



16\. Metadata includes solver\_variant.



17\. Metadata includes production\_baseline\_modified=false.



18\. No long-time run is performed.



\## Phase 10L Recommended Test



After Phase 10K scaffold passes, Phase 10L should test one-step or very-short-run equivalence.



Recommended Phase 10L tests:



\- fd\_centered selectable variant vs baseline SpectralSolver

\- same initial condition

\- same N

\- same dt

\- same Re

\- same steps

\- same forcing setting

\- compare final energy

\- compare final enstrophy

\- compare final vorticity field

\- compare metadata

\- confirm baseline behavior remains unchanged



Phase 10L should still avoid turbulence claims.



\## Phase 10M Recommended Test



After fd\_centered equivalence passes, Phase 10M can test short nonlinear drift with arakawa.



Recommended Phase 10M tests:



\- no forcing

\- high Re

\- controlled multimode initial field

\- short time

\- compare fd\_centered, pseudo\_spectral, and arakawa

\- track energy drift

\- track enstrophy drift

\- track finite values

\- track monotonicity if expected

\- avoid turbulence interpretation



\## Guardrails



The next implementation phase must follow these guardrails:



1\. Do not edit project/solver/spectral\_solver.py.



2\. Do not change baseline solver behavior.



3\. Do not change existing validation reports.



4\. Do not make Arakawa the global default.



5\. Do not remove fd\_centered.



6\. Do not rename existing operator functions.



7\. Do not run turbulence experiments.



8\. Do not claim k^-3 scaling.



9\. Do not call the selectable solver production-ready until time-evolution audits pass.



10\. Do not combine scaffold creation and long simulations in the same phase.



\## Scientific Interpretation After Phase 10J



Correct statement:



A selectable-advection solver variant has been designed, with explicit guardrails to preserve the validated baseline while enabling future fd\_centered, pseudo\_spectral, and arakawa comparisons.



Incorrect statement:



The solver has been upgraded to prove turbulence or k^-3 scaling.



That statement is not supported.



\## Decision



Phase 10J decision:



PROCEED TO PHASE 10K SCAFFOLD.



Phase 10K should create the separate selectable-advection solver scaffold.



Phase 10K should not run long simulations.



Phase 10K should not replace SpectralSolver.



Phase 10K should only test import, method selection, finite operator output, metadata, and baseline preservation.



\## Final Result



Phase 10J design:



PASS



Proceed to Phase 10K scaffold only.



Do not replace SpectralSolver.



Do not run turbulence experiments.



Do not make k^-3 claims.

