\# Phase 10U Extended No-Forcing Drift Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.57-phase10T-short-no-forcing-drift-decision-gate

\- Current previous commit: befdb27

\- Design file: PHASE10U\_EXTENDED\_NO\_FORCING\_DRIFT\_DESIGN.md



\## Purpose



Phase 10U is a design-only phase.



The purpose is to design an extended no-forcing drift audit after the passing Phase 10S short no-forcing drift audit.



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Current Status



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



\## Phase 10S Summary



Phase 10S tested short no-forcing drift across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



using an audit-local no-forcing subclass.



Phase 10S parameters were:



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



Phase 10S result:



PASS



Phase 10S confirmed:



\- all methods remained finite

\- all methods remained real-valued

\- all methods were non-explosive

\- no-forcing check passed

\- run() remained disabled

\- solver source files remained unchanged

\- final pairwise comparisons passed



\## Phase 10S Method Results



| Method | Final RMS Ratio | Relative Energy Drift | Relative Enstrophy Drift | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 9.999890095267e-01 | -1.969980531063e-05 | -2.198082581009e-05 | PASS |

| pseudo\_spectral | 9.999889308042e-01 | -1.976387196671e-05 | -2.213826916559e-05 | PASS |

| arakawa | 9.999889308058e-01 | -1.976387196420e-05 | -2.213826585037e-05 | PASS |



\## Why Phase 10U Is Needed



Phase 10S tested final time 1.0.



The next controlled question is:



Do fd\_centered, pseudo\_spectral, and arakawa remain finite, non-explosive, and closely aligned over a slightly longer no-forcing drift horizon?



This is still not a production simulation.



This is still not a turbulence test.



This is still not a k^-3 test.



This is a longer diagnostic drift audit.



\## Design Decision



Proceed with Option A from Phase 10T.



Option A:



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 5000 |

| final time | 5.0 |

| forcing | zero |

| initial RMS | 0.01 |

| initial field | phase6d\_like\_multimode |



Reason:



This extends time from 1.0 to 5.0 while keeping the same resolution and time step.



This changes one major variable: duration.



It avoids mixing longer duration with higher resolution at the same time.



\## Methods to Compare



The extended audit should compare:



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

\- zero forcing

\- dealiasing mask

\- step\_once\_selectable update path



The only intended difference should be the selected nonlinear advection operator.



\## No-Forcing Mechanism



The future Phase 10V audit should use an audit-local subclass:



NoForcingSelectableAdvectionSolver(SelectableAdvectionSolver)



The subclass should override only:



forcing()



and return:



np.zeros\_like(self.w)



This preserves all solver source files.



The audit should verify:



max\_abs(solver.forcing()) == 0



for each method.



\## Initial Field



Use the same controlled phase6d\_like\_multimode field from Phase 10S:



\- sin(2X) \* cos(2Y)

\- 0.75 \* sin(3X) \* cos(Y)

\- 0.50 \* sin(X) \* cos(4Y)

\- 0.35 \* cos(4X - 2Y)



Then rescale to RMS 0.01.



Reason:



This field has already been used across prior diagnostics.



It is nonlinear enough to be meaningful while remaining controlled.



\## Future Audit Script



Recommended script:



phase10v\_extended\_no\_forcing\_drift\_comparison\_audit.py



Recommended outputs:



PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT.csv



PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_TIME\_HISTORY.csv



PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_PAIRWISE\_SUMMARY.csv



PHASE10V\_EXTENDED\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT\_REPORT.md



\## Required Global Checks



The Phase 10V audit should verify:



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

\- no-forcing subclass returns zero forcing



\## Required Per-Method Diagnostics



For each method, record:



\- method name

\- N

\- Re

\- nu

\- dt

\- steps

\- final time

\- forcing\_zero

\- initial RMS

\- final RMS

\- final RMS ratio

\- initial kinetic energy

\- final kinetic energy

\- relative energy drift

\- final energy ratio

\- initial enstrophy

\- final enstrophy

\- relative enstrophy drift

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

\- energy monotone nonincreasing logged

\- enstrophy monotone nonincreasing logged

\- overall result



\## Required Time-History Diagnostics



Record diagnostics every 500 steps.



Recommended diagnostic steps:



\- 0

\- 500

\- 1000

\- 1500

\- 2000

\- 2500

\- 3000

\- 3500

\- 4000

\- 4500

\- 5000



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

\- positive alignment

\- no large pairwise disagreement

\- pairwise result



\## Pass Criteria



The extended audit should pass if all methods satisfy:



\- forcing\_zero PASS

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



Recommended non-explosive thresholds:



| Quantity | Threshold |

|---|---:|

| final RMS / initial RMS | less than 1.10 |

| final energy / initial energy | less than 1.10 |

| final enstrophy / initial enstrophy | less than 1.10 |



These are stability-screen thresholds.



They are not turbulence criteria.



\## Pairwise Pass Criteria



For final pairwise comparisons:



| Quantity | Threshold |

|---|---:|

| cosine similarity | greater than 0.99 |

| relative error | less than 0.01 |



Reason:



Phase 10S pairwise relative errors were around 1e-4 or less.



A final-time 5.0 audit may accumulate larger pairwise differences.



A 1e-2 threshold is still conservative for detecting large disagreement while avoiding false failure from expected accumulated method differences.



\## Monotonicity Interpretation



The audit should record:



\- energy\_monotone\_nonincreasing\_logged

\- enstrophy\_monotone\_nonincreasing\_logged



For the first extended audit, monotonicity should be diagnostic rather than the only pass/fail criterion.



If monotonicity fails but final drift remains small and non-explosive, the report should classify the result carefully as PASS with review note, or REVIEW if drift behavior looks suspicious.



Do not silently loosen thresholds after seeing results.



\## Review Criteria



The Phase 10V audit should report REVIEW if:



\- one method remains finite but shows much larger drift than the others

\- energy increases but stays below the non-explosive threshold

\- enstrophy increases but stays below the non-explosive threshold

\- pairwise relative error exceeds 0.01 while cosine remains positive

\- monotonicity fails in a way that appears method-specific



The audit should report FAIL if:



\- any method becomes non-finite

\- any method becomes complex-valued

\- forcing is not zero

\- solver.w is mutated unexpectedly

\- run() becomes enabled

\- RMS, energy, or enstrophy exceeds the non-explosive threshold

\- pairwise cosine becomes strongly negative or undefined for primary outputs



\## What Phase 10V Should Not Do



Phase 10V should not call:



SpectralSolver.run()



Phase 10V should not call:



SelectableAdvectionSolver.run()



Phase 10V should not modify:



project/solver/spectral\_solver.py



Phase 10V should not modify:



project/solver/selectable\_advection\_solver.py



Phase 10V should not modify:



project/solver/advection\_operators.py



Phase 10V should not use forcing.



Phase 10V should not run forced turbulence experiments.



Phase 10V should not run k^-3 experiments.



Phase 10V should not claim Arakawa is production-ready.



\## What Phase 10V May Do



Phase 10V may create a standalone audit script.



Phase 10V may define an audit-local no-forcing subclass.



Phase 10V may repeatedly call:



step\_once\_selectable(w)



inside the audit script.



Phase 10V may write CSV diagnostic outputs.



Phase 10V may compare method drift.



Phase 10V may produce a report.



\## Scientific Boundary



Correct statement after a passing Phase 10V would be:



The selectable methods remained finite and non-explosive in an extended controlled no-forcing drift audit at N=64 through final time 5.0.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Recommended Next Phase After 10V



If Phase 10V passes, the next phase should be:



Phase 10W — Extended No-Forcing Drift Decision Gate



Purpose:



Decide whether to proceed to either:



\- N=128 short no-forcing drift

\- longer N=64 no-forcing drift

\- controlled forced-response design



Do not jump directly to k^-3 claims.



\## Decision



Phase 10U decision:



Proceed to Phase 10V extended no-forcing drift comparison audit.



Use Option A:



\- N=64

\- Re=1000000

\- dt=0.001

\- steps=5000

\- final time=5.0

\- forcing=zero

\- phase6d\_like\_multimode initial condition



Do not modify solver source files.



Do not enable run().



Do not run forced turbulence experiments.



Do not claim turbulence.



Do not claim k^-3 scaling.



\## Final Result



Phase 10U design:



PASS



Next phase:



Phase 10V — Extended No-Forcing Drift Comparison Audit



Required guardrails:



\- SpectralSolver must remain unchanged.

\- SelectableAdvectionSolver must remain unchanged.

\- advection\_operators must remain unchanged.

\- SelectableAdvectionSolver.run() must remain disabled.

\- No forcing must be verified.

\- No forced turbulence.

\- No k^-3 claims.

