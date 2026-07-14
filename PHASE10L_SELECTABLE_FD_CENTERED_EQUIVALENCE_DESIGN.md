\# Phase 10L Selectable fd\_centered Equivalence Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.45-phase10K1-selectable-advection-solver-scaffold-audit

\- Current previous commit: ec6998f

\- Design file: PHASE10L\_SELECTABLE\_FD\_CENTERED\_EQUIVALENCE\_DESIGN.md



\## Purpose



Phase 10L is a design-only phase.



The purpose is to design a narrow, audited one-step equivalence path for the selectable-advection solver.



The first equivalence target is:



fd\_centered selectable advection



against the current baseline solver logic.



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not run a simulation.



This phase does not enable production runs.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Current Status



The current baseline solver is:



project/solver/spectral\_solver.py



The current selectable scaffold is:



project/solver/selectable\_advection\_solver.py



The current selectable scaffold supports:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The current selectable scaffold has:



compute\_advection(w)



The current selectable scaffold intentionally disables:



run()



This remains correct.



\## Why Phase 10L Is Needed



Phase 10K.1 proved that compute\_advection selects the correct standalone operator.



However, compute\_advection alone does not prove that the selectable solver can reproduce the baseline solver time update.



The next validation question is narrower:



Can a selectable solver using fd\_centered reproduce the baseline fd\_centered update in a controlled one-step test?



That question must be answered before any Arakawa time-evolution run is attempted.



\## Design Decision



Proceed with a one-step equivalence design.



Do not enable full run() yet.



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not run long simulations.



The next implementation phase should create a narrowly scoped one-step method or helper.



Recommended future method name:



step\_once\_selectable



or:



compute\_rhs\_selectable



The safer first target is:



compute\_rhs\_selectable



Reason:



A right-hand-side comparison is less risky than immediately implementing full time stepping.



\## Recommended Future Phase Sequence



The recommended sequence is:



1\. Phase 10L — design only.

2\. Phase 10M — inspect baseline SpectralSolver update logic and write exact equivalence notes.

3\. Phase 10N — implement compute\_rhs\_selectable or step\_once\_selectable.

4\. Phase 10N.1 — audit fd\_centered RHS equivalence.

5\. Phase 10O — audit fd\_centered one-step equivalence.

6\. Phase 10P — only after fd\_centered equivalence passes, test Arakawa short no-forcing drift.



This avoids combining design, implementation, and validation in one step.



\## Baseline Preservation Rule



The following file must not be edited during this equivalence work:



project/solver/spectral\_solver.py



The baseline solver is the reference.



The selectable solver must conform to the baseline where fd\_centered is selected.



The baseline must not be changed to fit the selectable solver.



\## First Equivalence Target



The first target is:



SelectableAdvectionSolver(advection\_method="fd\_centered")



It should match the current baseline nonlinear advection behavior.



The equivalence target should use:



\- same grid

\- same N

\- same Re

\- same dt

\- same initial condition

\- same forcing configuration

\- same streamfunction method

\- same velocity method

\- same diffusion method

\- same nonlinear advection convention

\- same dealiasing convention

\- same time-step convention



\## Required Baseline Inspection Before Implementation



Before writing any update code, the next phase must inspect:



project/solver/spectral\_solver.py



The inspection must identify:



\- how SpectralSolver computes streamfunction

\- how SpectralSolver computes velocity

\- how SpectralSolver computes nonlinear advection

\- how diffusion is applied

\- how forcing is applied

\- how RK2-style stepping is implemented

\- where dealiasing is applied

\- when diagnostics are written

\- whether the solver mutates w during intermediate stages

\- what metadata exists



The inspection must be documented before implementation.



\## Recommended RHS Definition



The project update convention is:



d omega / dt = -adv + diffusion + forcing



Each advection operator returns:



adv = u \* omega\_x + v \* omega\_y



Therefore a selectable RHS should conceptually compute:



rhs = -compute\_advection(w) + diffusion(w) + forcing



For fd\_centered:



compute\_advection(w) = advection\_fd\_centered(self, w)



For pseudo\_spectral:



compute\_advection(w) = advection\_pseudo\_spectral(self, w, dealias\_product=False)



For arakawa:



compute\_advection(w) = advection\_arakawa(self, w)



The time-update logic should not special-case Arakawa sign.



The sign belongs inside advection\_arakawa.



\## Recommended Phase 10M Output



Phase 10M should be documentation-only or inspection-only.



Recommended file:



PHASE10M\_BASELINE\_UPDATE\_LOGIC\_INSPECTION.md



It should include:



\- the exact baseline update sequence

\- the exact baseline nonlinear advection expression

\- the exact baseline diffusion expression

\- the exact baseline forcing expression

\- the exact baseline RK2-style stepping sequence

\- the exact baseline dealiasing placement

\- a decision on whether to implement RHS-only comparison first or one-step comparison first



\## Recommended Phase 10N Implementation



Only after Phase 10M inspection should implementation occur.



Recommended new or modified file:



project/solver/selectable\_advection\_solver.py



Allowed change:



Add a narrow audited method, such as:



compute\_rhs\_selectable(self, w)



or:



step\_once\_selectable(self, w)



Do not enable run().



Do not create production run behavior.



Do not alter SpectralSolver.



Do not alter existing advection operator functions.



\## Recommended compute\_rhs\_selectable Behavior



If compute\_rhs\_selectable is chosen, it should:



1\. Accept a vorticity field w.

2\. Validate shape.

3\. Compute selected nonlinear advection.

4\. Compute diffusion using the same spectral convention as baseline.

5\. Compute forcing using the same convention as baseline.

6\. Return rhs.

7\. Not mutate input w.

8\. Not mutate solver.w.

9\. Not advance time.

10\. Not write files.

11\. Not claim production readiness.



\## Recommended step\_once\_selectable Behavior



If step\_once\_selectable is chosen later, it should:



1\. Accept a vorticity field w.

2\. Apply the exact baseline RK2-style step.

3\. Use compute\_advection for the nonlinear term.

4\. Apply diffusion and forcing consistently with baseline.

5\. Apply dealiasing at the same location as baseline.

6\. Return the next vorticity field.

7\. Not mutate input w unless explicitly documented.

8\. Not mutate solver.w unless explicitly documented.

9\. Not write diagnostics unless explicitly requested.

10\. Not call run().



\## Audit Requirements for fd\_centered RHS Equivalence



The first equivalence audit should compare:



baseline RHS using current SpectralSolver logic



against:



selectable RHS with advection\_method="fd\_centered"



The audit should use controlled fields:



\- single\_mode\_k2\_2

\- low\_mode\_pair

\- phase6d\_like\_multimode

\- higher\_smooth\_multimode



The audit should test N=64 and N=128.



Required checks:



\- finite output

\- real output

\- input w unchanged

\- solver.w unchanged

\- RHS difference L2

\- RHS difference max\_abs

\- cosine similarity

\- exact or near-exact equivalence, depending on implementation path

\- SpectralSolver file no git diff

\- run() still disabled



\## Audit Requirements for fd\_centered One-Step Equivalence



After RHS equivalence passes, one-step equivalence should compare:



baseline one-step update



against:



selectable one-step update with advection\_method="fd\_centered"



Required checks:



\- same initial condition

\- same dt

\- same Re

\- same N

\- same forcing

\- same dealiasing

\- final w difference L2

\- final w difference max\_abs

\- final energy difference

\- final enstrophy difference

\- finite output

\- real output

\- no unintended mutation

\- SpectralSolver file no git diff



\## Recommended Tolerances



For direct operator and RHS comparisons:



\- exact equality may be possible if the same helper functions are used

\- otherwise use strict floating-point tolerance



Suggested initial tolerance:



relative L2 error <= 1e-12



For one-step comparisons:



Suggested initial tolerance:



relative field L2 error <= 1e-10



If tolerances fail at very small norms, the audit should report REVIEW rather than silently loosening the threshold.



\## Metadata Requirements for Future One-Step Audits



Any future selectable update audit should record:



| Metadata Field | Meaning |

|---|---|

| solver\_variant | selectable\_advection |

| solver\_class | SelectableAdvectionSolver |

| baseline\_solver\_class | SpectralSolver |

| advection\_method | selected method |

| equivalence\_target | fd\_centered\_baseline |

| update\_scope | rhs\_only or one\_step |

| production\_baseline\_modified | false |

| run\_enabled | false unless future audited phase changes it |

| turbulence\_claim | false |

| k\_minus\_3\_claim | false |



\## What Must Not Happen Yet



Do not enable SelectableAdvectionSolver.run().



Do not run long simulations.



Do not run turbulence experiments.



Do not run forced cascade experiments.



Do not make k^-3 claims.



Do not make Arakawa production default.



Do not delete fd\_centered.



Do not modify SpectralSolver.



Do not modify previous validation reports.



\## Decision



Phase 10L decision:



Proceed to Phase 10M baseline update logic inspection.



Do not implement one-step logic yet.



Do not enable run().



Do not test Arakawa time evolution yet.



\## Final Result



Phase 10L design:



PASS



Next phase should be:



Phase 10M — Baseline Update Logic Inspection



The next phase should inspect and document SpectralSolver's exact update logic before implementing selectable RHS or one-step equivalence.

