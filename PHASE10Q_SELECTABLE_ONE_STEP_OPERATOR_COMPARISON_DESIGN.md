\# Phase 10Q Selectable One-Step Operator Comparison Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.52-phase10P1-fd-centered-one-step-equivalence-audit

\- Current previous commit: 97dbc15

\- Design file: PHASE10Q\_SELECTABLE\_ONE\_STEP\_OPERATOR\_COMPARISON\_DESIGN.md



\## Purpose



Phase 10Q is a design-only phase.



The purpose is to design a controlled one-step comparison across selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Current Status



The current validated baseline solver is:



project/solver/spectral\_solver.py



The current selectable solver scaffold is:



project/solver/selectable\_advection\_solver.py



The selectable solver currently has:



\- compute\_advection(w)

\- compute\_rhs\_selectable(w)

\- step\_once\_selectable(w)

\- metadata\_dict()

\- selectable\_advection\_metadata()

\- run() intentionally disabled



Phase 10N.1 proved:



SelectableAdvectionSolver(advection\_method="fd\_centered").compute\_rhs\_selectable(w)



matches the direct baseline RHS logic exactly.



Phase 10P.1 proved:



SelectableAdvectionSolver(advection\_method="fd\_centered").step\_once\_selectable(w)



matches the direct baseline one-step RK2-style update exactly.



For all tested fields and resolutions in Phase 10P.1:



\- diff\_l2 = 0

\- diff\_max\_abs = 0

\- relative\_error = 0

\- cosine\_similarity = 1



\## Why Phase 10Q Is Needed



The selectable solver now reproduces the baseline fd\_centered one-step update.



The next controlled question is not long-time stability.



The next controlled question is:



How do the one-step outputs differ across fd\_centered, pseudo\_spectral, and arakawa on the same controlled fields?



This should be measured before any short-time Arakawa drift test.



\## Design Decision



Proceed to a one-step operator comparison audit.



Do not enable run().



Do not run long simulations.



Do not replace SpectralSolver.



Do not claim turbulence.



Do not claim k^-3 scaling.



The comparison should use the already-audited method:



step\_once\_selectable(w)



with each advection method.



\## Methods to Compare



The audit should instantiate:



SelectableAdvectionSolver(advection\_method="fd\_centered")



SelectableAdvectionSolver(advection\_method="pseudo\_spectral")



SelectableAdvectionSolver(advection\_method="arakawa")



Each solver should use the same:



\- N

\- Re

\- dt

\- steps

\- initial field

\- forcing

\- dealiasing mask

\- grid



The only intended difference should be the selected nonlinear advection operator.



\## Reference Method



The primary baseline reference remains:



fd\_centered



Reason:



fd\_centered is the validated baseline-compatible method.



However, the audit should also compare:



\- arakawa vs pseudo\_spectral

\- pseudo\_spectral vs fd\_centered

\- arakawa vs fd\_centered



The pseudo\_spectral method remains a diagnostic reference, not the production baseline.



\## Test Fields



The audit should use the same controlled fields used in prior phases:



| Field | Classification |

|---|---|

| single\_mode\_k2\_2 | controlled\_single\_mode\_reference |

| low\_mode\_pair | low\_k\_nonlinear |

| phase6d\_like\_multimode | phase6d\_like\_low\_k\_nonlinear |

| higher\_smooth\_multimode | higher\_smooth\_nonlinear |



The audit should test:



\- N=64

\- N=128



Recommended parameters:



\- Re=1000

\- dt=0.005

\- steps=1



\## Required Checks Per Method



For each field, resolution, and method, the audit should check:



\- solver imports

\- method accepted

\- step\_once\_selectable exists

\- compute\_rhs\_selectable exists

\- output finite

\- output real

\- input w unchanged

\- solver.w unchanged

\- run() remains disabled

\- metadata method correct

\- metadata run\_enabled=false

\- metadata turbulence\_claim=false

\- metadata k\_minus\_3\_claim=false



\## Required Pairwise Comparisons



For each field and resolution, compute pairwise comparisons:



| Pair | Purpose |

|---|---|

| pseudo\_spectral vs fd\_centered | measures diagnostic spectral step difference from baseline |

| arakawa vs fd\_centered | measures Arakawa step difference from baseline |

| arakawa vs pseudo\_spectral | measures Arakawa agreement with pseudo-spectral diagnostic |



Each pair should report:



\- output L2 for method A

\- output L2 for method B

\- difference L2

\- difference max\_abs

\- relative error

\- cosine similarity

\- energy of output A

\- energy of output B

\- energy difference

\- enstrophy of output A

\- enstrophy of output B

\- enstrophy difference



\## Energy and Enstrophy Diagnostics



For each one-step output, compute:



enstrophy = 0.5 \* mean(w\_next \* w\_next)



Kinetic energy should use the solver velocity convention:



psi = streamfunction(w\_next)



u, v = velocity(psi)



energy = 0.5 \* mean(u\*u + v\*v)



The audit should not use energy or enstrophy to claim turbulence.



These are diagnostic comparison quantities only.



\## Expected Interpretation



The fd\_centered method is already validated against the baseline one-step update.



The pseudo\_spectral and arakawa methods are expected to produce different one-step outputs because they use different nonlinear advection operators.



Different output is not automatically a failure.



A failure should mean:



\- non-finite output

\- complex output

\- mutation of input w

\- mutation of solver.w

\- method metadata incorrect

\- run() unexpectedly enabled

\- sign-flipped behavior visible as strongly negative cosine where positive alignment is expected

\- unexpectedly huge difference from both fd\_centered and pseudo\_spectral on controlled small-amplitude fields



\## Recommended Pass/Review Rules



The audit should avoid pretending all methods must match exactly.



Recommended case-level PASS conditions:



For every method:



\- finite output PASS

\- real output PASS

\- input w unchanged PASS

\- solver.w unchanged PASS

\- run disabled PASS

\- metadata checks PASS



For pairwise comparisons:



\- cosine similarity should be positive for primary nonlinear fields

\- arakawa vs pseudo\_spectral cosine should remain high on primary nonlinear fields

\- no output should show explosive one-step growth

\- near-null single-mode should be retained as review reference, not primary evidence



Recommended review threshold:



For primary nonlinear fields:



\- arakawa vs pseudo\_spectral cosine > 0.99

\- pseudo\_spectral vs fd\_centered cosine > 0.99

\- arakawa vs fd\_centered cosine > 0.99



The near-null single-mode case should not determine pass/fail if norms are near machine precision or dominated by forcing.



\## Output Files for Future Phase 10Q.1



Recommended audit script:



phase10q1\_selectable\_one\_step\_operator\_comparison\_audit.py



Recommended CSV output:



PHASE10Q1\_SELECTABLE\_ONE\_STEP\_OPERATOR\_COMPARISON\_AUDIT.csv



Recommended pairwise summary output:



PHASE10Q1\_SELECTABLE\_ONE\_STEP\_PAIRWISE\_SUMMARY.csv



Recommended report:



PHASE10Q1\_SELECTABLE\_ONE\_STEP\_OPERATOR\_COMPARISON\_AUDIT\_REPORT.md



\## Required Global Checks



The future audit should verify:



\- SpectralSolver imports

\- SelectableAdvectionSolver imports

\- supported methods are exactly fd\_centered, pseudo\_spectral, arakawa

\- default method is fd\_centered

\- compute\_rhs\_selectable exists

\- step\_once\_selectable exists

\- SpectralSolver file has no git diff

\- SelectableAdvectionSolver file has no git diff

\- invalid method remains rejected

\- run() remains disabled



\## What the Audit Should Not Do



The Phase 10Q.1 audit should not call:



SpectralSolver.run()



The Phase 10Q.1 audit should not call:



SelectableAdvectionSolver.run()



The Phase 10Q.1 audit should not run many steps.



The Phase 10Q.1 audit should not create production run outputs.



The Phase 10Q.1 audit should not test long-time stability.



The Phase 10Q.1 audit should not make Arakawa production-ready.



\## Scientific Boundary



Correct statement after a passing Phase 10Q.1 would be:



The selectable one-step outputs for fd\_centered, pseudo\_spectral, and arakawa were compared on controlled fields, and the non-baseline methods produced finite, real, non-mutating one-step outputs with documented pairwise differences.



Incorrect statement:



The Arakawa selectable solver is now validated for turbulence or k^-3 scaling.



That statement is not supported.



\## Recommended Next Phase After 10Q.1



If Phase 10Q.1 passes, the next stage should be:



Phase 10R — Short No-Forcing Drift Design



Purpose:



Design a short controlled no-forcing drift test comparing:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



using step\_once\_selectable repeatedly inside a separate audit script.



Important:



Even then, SelectableAdvectionSolver.run() should remain disabled unless a later phase explicitly audits a selectable run loop.



\## What Must Not Happen Yet



Do not enable SelectableAdvectionSolver.run().



Do not replace SpectralSolver.



Do not modify project/solver/spectral\_solver.py.



Do not run long simulations.



Do not run forced turbulence experiments.



Do not run k^-3 experiments.



Do not claim Arakawa is production-ready.



Do not claim turbulence.



Do not claim k^-3 scaling.



\## Decision



Phase 10Q decision:



Proceed to Phase 10Q.1 one-step operator comparison audit.



No implementation changes are required before Phase 10Q.1.



The existing step\_once\_selectable method is sufficient for the next audit.



\## Final Result



Phase 10Q design:



PASS



Next phase:



Phase 10Q.1 — Selectable One-Step Operator Comparison Audit



Required guardrails:



\- SpectralSolver must remain unchanged.

\- SelectableAdvectionSolver.run() must remain disabled.

\- No long simulations.

\- No turbulence claims.

\- No k^-3 claims.

