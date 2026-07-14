\# Phase 11D N128 Controlled Forced-Response Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.2-phase11C-controlled-forced-response-decision-gate

\- Current previous commit: ea17c0b

\- Design file: PHASE11D\_N128\_CONTROLLED\_FORCED\_RESPONSE\_DESIGN.md



\## Purpose



Phase 11D is a design-only phase.



The purpose is to design a controlled forced-response audit at higher resolution:



N = 128



The audit will compare selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



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

| Phase 11C controlled forced-response decision gate | PASS |



\## Why Phase 11D Is Needed



Phase 11B tested controlled forced response at:



N = 64



The next conservative validation question is:



Do fd\_centered, pseudo\_spectral, and arakawa remain finite, non-explosive, and closely aligned under the same deterministic baseline forcing at N=128?



This changes one major variable:



N from 64 to 128



The time horizon remains short:



final time = 1.0



This avoids changing both resolution and duration at the same time.



\## Design Decision



Proceed with a short N=128 controlled forced-response audit.



Recommended parameters:



| Parameter | Value |

|---|---:|

| N | 128 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| forcing | baseline deterministic forcing |

| initial RMS | 0.01 |

| initial field | phase6d\_like\_multimode |



\## Baseline Forcing



The inherited baseline forcing from SpectralSolver is:



forcing() = 0.01 \* sin(2X) \* cos(2Y)



The audit should not override forcing.



The audit should use SelectableAdvectionSolver directly.



The audit should verify:



\- forcing is nonzero

\- forcing is finite

\- forcing is real

\- forcing has shape (N, N)

\- forcing RMS is greater than zero

\- forcing max\_abs is greater than zero

\- forcing is identical across methods



\## Methods to Compare



The audit should compare:



| Method | Role |

|---|---|

| fd\_centered | baseline-compatible method |

| pseudo\_spectral | diagnostic spectral-advection method |

| arakawa | candidate conservative advection method |



Each method should use the same:



\- N

\- Re

\- dt

\- number of steps

\- initial field

\- baseline deterministic forcing

\- dealiasing mask

\- step\_once\_selectable update path



The only intended difference should be the selected nonlinear advection operator.



\## Initial Field



Use the controlled phase6d\_like\_multimode field:



\- sin(2X) \* cos(2Y)

\- 0.75 \* sin(3X) \* cos(Y)

\- 0.50 \* sin(X) \* cos(4Y)

\- 0.35 \* cos(4X - 2Y)



Then rescale to RMS 0.01.



Reason:



This field has already been used across prior diagnostics and drift audits.



It is nonlinear enough to be meaningful while remaining controlled.



\## Future Audit Script



Recommended script:



phase11e\_n128\_controlled\_forced\_response\_audit.py



Recommended outputs:



PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_AUDIT.csv



PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_TIME\_HISTORY.csv



PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_PAIRWISE\_SUMMARY.csv



PHASE11E\_N128\_CONTROLLED\_FORCED\_RESPONSE\_AUDIT\_REPORT.md



\## Required Global Checks



The Phase 11E audit should verify:



\- SpectralSolver imports

\- SelectableAdvectionSolver imports

\- supported methods are exactly fd\_centered, pseudo\_spectral, arakawa

\- default method is fd\_centered

\- compute\_rhs\_selectable exists

\- step\_once\_selectable exists

\- SpectralSolver file has no git diff

\- SelectableAdvectionSolver file has no git diff

\- advection\_operators file has no git diff

\- invalid method remains rejected

\- SelectableAdvectionSolver.run() remains disabled



\## Required Forcing Checks



The Phase 11E audit should verify:



\- forcing is nonzero

\- forcing is finite

\- forcing is real

\- forcing has shape (128, 128)

\- forcing RMS is greater than zero

\- forcing max\_abs is greater than zero

\- forcing field is identical across fd\_centered, pseudo\_spectral, and arakawa solver instances



Recommended forcing diagnostics:



\- forcing\_rms

\- forcing\_max\_abs

\- forcing\_l2

\- forcing\_shape\_ok

\- forcing\_identical\_across\_methods



\## Required Per-Method Diagnostics



For each method, record:



\- method name

\- N

\- Re

\- nu

\- dt

\- steps

\- final time

\- forcing\_rms

\- forcing\_max\_abs

\- initial RMS

\- final RMS

\- final RMS ratio

\- initial kinetic energy

\- final kinetic energy

\- relative energy change

\- final energy ratio

\- initial enstrophy

\- final enstrophy

\- relative enstrophy change

\- final enstrophy ratio

\- initial max absolute vorticity

\- final max absolute vorticity

\- finite throughout

\- real throughout

\- input not mutated each step

\- solver.w unchanged

\- run disabled

\- metadata guardrails

\- final RMS nonexplosive

\- final energy nonexplosive

\- final enstrophy nonexplosive

\- overall result



\## Required Time-History Diagnostics



Record diagnostics every 100 steps.



Recommended diagnostic steps:



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



For each method and logged step, record:



\- step

\- time

\- RMS vorticity

\- kinetic energy

\- enstrophy

\- max absolute vorticity

\- finite flag

\- real flag



\## Required Pairwise Final Comparisons



At the final step, compare:



| Pair | Purpose |

|---|---|

| pseudo\_spectral vs fd\_centered | diagnostic spectral forced response compared with baseline-compatible forced response |

| arakawa vs fd\_centered | Arakawa forced response compared with baseline-compatible forced response |

| arakawa vs pseudo\_spectral | Arakawa forced response compared with spectral diagnostic forced response |



Each pair should report:



\- final field diff\_l2

\- final field diff\_max\_abs

\- relative error

\- cosine similarity

\- final energy difference

\- final enstrophy difference

\- positive alignment

\- no large pairwise disagreement

\- pairwise result



\## Pass Criteria



The N=128 controlled forced-response audit should pass if all methods satisfy:



\- forcing\_nonzero PASS

\- forcing\_shape\_ok PASS

\- forcing\_finite PASS

\- forcing\_real PASS

\- forcing\_identical\_across\_methods PASS

\- finite throughout PASS

\- real throughout PASS

\- input not mutated each step PASS

\- solver.w unchanged PASS

\- run disabled PASS

\- final RMS nonexplosive PASS

\- final energy nonexplosive PASS

\- final enstrophy nonexplosive PASS

\- metadata turbulence\_claim=false

\- metadata k\_minus\_3\_claim=false



\## Non-Explosive Thresholds



Because this is a forced-response audit, energy and enstrophy are allowed to increase.



Do not require monotonic decay.



Recommended non-explosive thresholds:



| Quantity | PASS Threshold |

|---|---:|

| final RMS / initial RMS | less than 2.0 |

| final energy / initial energy | less than 4.0 |

| final enstrophy / initial enstrophy | less than 4.0 |



These are stability-screen thresholds.



They are not turbulence criteria.



\## Review Thresholds



The audit should report REVIEW if:



| Quantity | REVIEW Range |

|---|---:|

| final RMS / initial RMS | 2.0 to 5.0 |

| final energy / initial energy | 4.0 to 10.0 |

| final enstrophy / initial enstrophy | 4.0 to 10.0 |



The audit should report FAIL if:



\- any method becomes non-finite

\- any method becomes complex-valued

\- forcing is zero

\- forcing differs across methods

\- solver.w is mutated unexpectedly

\- run() becomes enabled

\- final RMS / initial RMS exceeds 5.0

\- final energy / initial energy exceeds 10.0

\- final enstrophy / initial enstrophy exceeds 10.0

\- pairwise cosine becomes strongly negative or undefined



\## Pairwise Pass Criteria



For final pairwise comparisons:



| Quantity | Threshold |

|---|---:|

| cosine similarity | greater than 0.99 |

| relative error | less than 0.05 |



Reason:



Forced dynamics may create larger method separation than no-forcing drift.



A 5 percent pairwise relative-error threshold is conservative enough to detect large disagreement while allowing expected method differences.



\## Pairwise Review Criteria



Report REVIEW if:



\- cosine similarity remains positive but drops below 0.99

\- pairwise relative error is between 0.05 and 0.20

\- arakawa differs much more from both methods than fd\_centered and pseudo\_spectral differ from each other

\- energy or enstrophy differences are method-specific and large



Do not silently loosen thresholds after seeing results.



\## Monotonicity Interpretation



For forced response, energy and enstrophy may increase.



The audit may record monotonicity, but monotonic nonincrease should not be a pass/fail criterion.



Recommended logged diagnostics:



\- energy\_monotone\_nonincreasing\_logged

\- enstrophy\_monotone\_nonincreasing\_logged



These should be interpreted as diagnostics only.



\## Runtime Expectation



This audit should be more expensive than Phase 11B because N increases from 64 to 128.



Expected runtime on the laptop:



\- best case: a few minutes

\- reasonable range: 5 to 20 minutes

\- slow case: longer if system is busy or power settings throttle CPU



The script should print progress every 100 steps.



\## What Phase 11E Should Not Do



Phase 11E should not call:



SpectralSolver.run()



Phase 11E should not call:



SelectableAdvectionSolver.run()



Phase 11E should not modify:



project/solver/spectral\_solver.py



Phase 11E should not modify:



project/solver/selectable\_advection\_solver.py



Phase 11E should not modify:



project/solver/advection\_operators.py



Phase 11E should not run long simulations.



Phase 11E should not run turbulence experiments.



Phase 11E should not run k^-3 experiments.



Phase 11E should not claim Arakawa is production-ready.



\## What Phase 11E May Do



Phase 11E may create a standalone audit script.



Phase 11E may use the inherited baseline forcing.



Phase 11E may repeatedly call:



step\_once\_selectable(w)



inside the audit script.



Phase 11E may write CSV diagnostic outputs.



Phase 11E may compare method forced-response behavior.



Phase 11E may produce a report.



\## Scientific Boundary



Correct statement after a passing Phase 11E would be:



The selectable methods remained finite and non-explosive in a short controlled forced-response audit at N=128 using the baseline deterministic forcing.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Recommended Next Phase After 11E



If Phase 11E passes, the next phase should be:



Phase 11F — N128 Controlled Forced-Response Decision Gate



Purpose:



Decide whether to proceed to either:



\- longer N=64 controlled forced-response audit

\- longer N=128 controlled forced-response design

\- spectrum-focused diagnostic design

\- selectable run-loop design



Do not jump directly to k^-3 claims.



\## Decision



Phase 11D decision:



Proceed to Phase 11E N=128 controlled forced-response audit.



Use:



\- N=128

\- Re=1000000

\- dt=0.001

\- steps=1000

\- final time=1.0

\- forcing=baseline deterministic forcing

\- phase6d\_like\_multimode initial condition



Do not modify solver source files.



Do not enable run().



Do not run turbulence experiments.



Do not claim turbulence.



Do not claim k^-3 scaling.



\## Final Result



Phase 11D design:



PASS



Next phase:



Phase 11E — N128 Controlled Forced-Response Audit



Required guardrails:



\- SpectralSolver must remain unchanged.

\- SelectableAdvectionSolver must remain unchanged.

\- advection\_operators must remain unchanged.

\- SelectableAdvectionSolver.run() must remain disabled.

\- Baseline forcing must be verified.

\- No production simulation.

\- No turbulence claims.

\- No k^-3 claims.

