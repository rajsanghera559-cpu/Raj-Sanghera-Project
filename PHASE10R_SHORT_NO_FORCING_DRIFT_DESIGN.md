\# Phase 10R Short No-Forcing Drift Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.54-phase10Q1-selectable-one-step-operator-comparison-audit

\- Current previous commit: 128811e

\- Design file: PHASE10R\_SHORT\_NO\_FORCING\_DRIFT\_DESIGN.md



\## Purpose



Phase 10R is a design-only phase.



The purpose is to design a short controlled no-forcing drift comparison across selectable advection methods:



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



The current selectable solver is:



project/solver/selectable\_advection\_solver.py



The selectable solver currently has:



\- compute\_advection(w)

\- compute\_rhs\_selectable(w)

\- step\_once\_selectable(w)

\- metadata\_dict()

\- selectable\_advection\_metadata()

\- run() intentionally disabled



Phase 10P.1 proved that:



SelectableAdvectionSolver(advection\_method="fd\_centered").step\_once\_selectable(w)



matches the direct baseline one-step update exactly.



Phase 10Q.1 proved that one-step outputs across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



are finite, real, non-mutating, positively aligned, and pass pairwise checks on controlled fields.



\## Why Phase 10R Is Needed



The selectable solver now passes one-step checks.



The next controlled validation question is:



Can fd\_centered, pseudo\_spectral, and arakawa remain finite and well-behaved over a short no-forcing drift audit when advanced repeatedly using step\_once\_selectable?



This is still not a turbulence test.



This is still not a k^-3 test.



This is a short numerical stability and drift audit.



\## Important No-Forcing Design Issue



The current SelectableAdvectionSolver inherits the baseline forcing method:



forcing() = 0.01 \* sin(2X) \* cos(2Y)



Therefore, simply calling step\_once\_selectable repeatedly would not be a no-forcing test.



The future no-forcing audit must explicitly disable forcing without modifying SpectralSolver or SelectableAdvectionSolver.



\## Recommended No-Forcing Mechanism



Use an audit-local subclass inside the Phase 10S audit script:



NoForcingSelectableAdvectionSolver(SelectableAdvectionSolver)



The subclass should override only:



forcing()



and return:



np.zeros\_like(self.w)



This preserves the source files:



\- project/solver/spectral\_solver.py

\- project/solver/selectable\_advection\_solver.py



The audit script should verify that the no-forcing subclass returns zero forcing.



Required no-forcing check:



max\_abs(solver.forcing()) == 0



\## Design Decision



Proceed to a short no-forcing drift audit using an audit-local no-forcing subclass.



Do not modify SpectralSolver.



Do not modify SelectableAdvectionSolver.



Do not enable run().



Do not run long simulations.



Do not claim turbulence.



Do not claim k^-3 scaling.



\## Future Audit Script



Recommended script:



phase10s\_short\_no\_forcing\_drift\_comparison\_audit.py



Recommended outputs:



PHASE10S\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT.csv



PHASE10S\_SHORT\_NO\_FORCING\_DRIFT\_PAIRWISE\_SUMMARY.csv



PHASE10S\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT\_REPORT.md



\## Methods to Compare



The audit should compare:



| Method | Role |

|---|---|

| fd\_centered | baseline-compatible method |

| pseudo\_spectral | diagnostic spectral-advection method |

| arakawa | candidate conservative advection method |



Each method should use the same:



\- grid

\- Re

\- dt

\- number of steps

\- initial condition

\- no-forcing subclass

\- dealiasing mask

\- step\_once\_selectable update path



The only intended difference should be the selected advection method.



\## Recommended Initial Parameters



Use a short, controlled audit first.



Recommended primary configuration:



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| forcing | zero |

| initial RMS | 0.01 |



Reason:



This is similar in scale to earlier short nonlinear drift checks, but now compares selectable methods.



Do not start with long simulations.



Do not start with N=128 unless the N=64 audit passes.



\## Initial Field



Recommended primary field:



phase6d\_like\_multimode



Definition should be consistent with prior controlled fields:



\- sin(2X) \* cos(2Y)

\- 0.75 \* sin(3X) \* cos(Y)

\- 0.50 \* sin(X) \* cos(4Y)

\- 0.35 \* cos(4X - 2Y)



Then rescale to RMS 0.01.



Reason:



This field has already been used repeatedly in prior diagnostics and is nonlinear enough to be meaningful while remaining controlled.



\## Optional Secondary Fields



If the primary Phase 10S audit passes, later phases may test:



\- low\_mode\_pair

\- higher\_smooth\_multimode



Do not expand scope before the first short no-forcing drift audit passes.



\## Required Per-Method Diagnostics



For each method, the audit should record:



\- method name

\- N

\- Re

\- nu

\- dt

\- steps

\- final time

\- initial RMS

\- final RMS

\- initial energy

\- final energy

\- relative energy drift

\- initial enstrophy

\- final enstrophy

\- relative enstrophy drift

\- maximum absolute vorticity at final step

\- finite throughout

\- real output throughout

\- no-forcing check

\- solver.w unchanged

\- run() disabled

\- metadata turbulence\_claim=false

\- metadata k\_minus\_3\_claim=false



\## Required Time-History Diagnostics



Record values at regular intervals.



Recommended interval:



every 100 steps



Record:



\- step

\- time

\- method

\- RMS vorticity

\- kinetic energy

\- enstrophy

\- max absolute vorticity

\- finite flag



Recommended output:



A CSV row for each method and diagnostic interval.



\## Required Pairwise Final Comparisons



At the final step, compare:



| Pair | Purpose |

|---|---|

| pseudo\_spectral vs fd\_centered | diagnostic spectral drift compared with baseline-compatible drift |

| arakawa vs fd\_centered | Arakawa drift compared with baseline-compatible drift |

| arakawa vs pseudo\_spectral | Arakawa drift compared with spectral diagnostic drift |



Each pair should report:



\- final field diff\_l2

\- final field diff\_max\_abs

\- relative error

\- cosine similarity

\- final energy difference

\- final enstrophy difference



\## Required Global Checks



The future Phase 10S audit should verify:



\- SpectralSolver imports

\- SelectableAdvectionSolver imports

\- supported methods are exactly fd\_centered, pseudo\_spectral, arakawa

\- default method is fd\_centered

\- compute\_rhs\_selectable exists

\- step\_once\_selectable exists

\- SpectralSolver file has no git diff

\- SelectableAdvectionSolver file has no git diff

\- invalid method remains rejected

\- SelectableAdvectionSolver.run() remains disabled

\- no-forcing subclass returns zero forcing



\## Pass Criteria



The audit should pass if all methods satisfy:



\- finite throughout

\- real output throughout

\- no-forcing check passes

\- solver.w is not mutated by step\_once\_selectable

\- run() remains disabled

\- final RMS does not show explosive growth

\- final energy does not show explosive growth

\- final enstrophy does not show explosive growth

\- metadata guardrails remain present



Recommended initial thresholds:



| Quantity | Threshold |

|---|---:|

| final RMS / initial RMS | less than 1.10 |

| final energy / initial energy | less than 1.10 |

| final enstrophy / initial enstrophy | less than 1.10 |

| finite throughout | required |

| no-forcing check | required |

| run disabled | required |



These are stability-screen thresholds, not turbulence criteria.



\## Review Criteria



The audit should report REVIEW rather than silently loosen thresholds if:



\- one method has finite output but drift differs much more than the others

\- energy increases slightly but remains small

\- enstrophy increases slightly but remains small

\- pairwise differences grow but all methods remain stable

\- monotonic decay fails but final drift remains small



Do not force a PASS by relaxing thresholds after seeing results.



\## Monotonicity



Because the test is short and numerical methods differ, strict monotonic energy or enstrophy decay should not be the first hard pass/fail condition.



The audit may record monotonicity as a diagnostic:



\- energy\_monotone\_nonincreasing

\- enstrophy\_monotone\_nonincreasing



But a monotonicity failure should be interpreted carefully.



A method can remain stable while not being perfectly monotone at every diagnostic interval.



\## What Phase 10S Should Not Do



Phase 10S should not call:



SpectralSolver.run()



Phase 10S should not call:



SelectableAdvectionSolver.run()



Phase 10S should not modify:



project/solver/spectral\_solver.py



Phase 10S should not modify:



project/solver/selectable\_advection\_solver.py



Phase 10S should not modify:



project/solver/advection\_operators.py



Phase 10S should not run long simulations.



Phase 10S should not use forcing.



Phase 10S should not generate turbulence claims.



Phase 10S should not generate k^-3 claims.



\## What Phase 10S May Do



Phase 10S may create a standalone audit script.



Phase 10S may define an audit-local no-forcing subclass.



Phase 10S may repeatedly call:



step\_once\_selectable(w)



inside the audit script.



Phase 10S may write CSV diagnostic outputs.



Phase 10S may compare method drift.



Phase 10S may produce a report.



\## Scientific Boundary



Correct statement after a passing Phase 10S would be:



The selectable methods remained finite and non-explosive in a short controlled no-forcing drift audit.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Recommended Next Phase After 10S



If Phase 10S passes, the next phase should be:



Phase 10T — Short No-Forcing Drift Decision Gate



Purpose:



Decide whether the selectable methods are ready for a slightly longer or higher-resolution diagnostic drift test.



Do not jump directly to forced turbulence or k^-3 experiments.



\## Decision



Phase 10R decision:



Proceed to Phase 10S short no-forcing drift comparison audit.



Use an audit-local no-forcing subclass.



Do not modify solver source files.



Do not enable run().



Do not run long simulations.



Do not claim turbulence.



Do not claim k^-3 scaling.



\## Final Result



Phase 10R design:



PASS



Next phase:



Phase 10S — Short No-Forcing Drift Comparison Audit



Required guardrails:



\- SpectralSolver must remain unchanged.

\- SelectableAdvectionSolver must remain unchanged.

\- SelectableAdvectionSolver.run() must remain disabled.

\- No forcing must be verified.

\- No long simulations.

\- No turbulence claims.

\- No k^-3 claims.

