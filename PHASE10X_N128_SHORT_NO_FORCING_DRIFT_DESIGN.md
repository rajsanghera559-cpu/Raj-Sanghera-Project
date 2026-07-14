\# Phase 10X N128 Short No-Forcing Drift Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.60-phase10W-extended-no-forcing-drift-decision-gate

\- Current previous commit: 1bcec78

\- Design file: PHASE10X\_N128\_SHORT\_NO\_FORCING\_DRIFT\_DESIGN.md



\## Purpose



Phase 10X is a design-only phase.



The purpose is to design a short no-forcing drift audit at higher resolution:



N = 128



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



\## Recent Validation Chain



The project has passed:



| Phase | Result |

|---|---:|

| Phase 10P.1 fd\_centered one-step equivalence | PASS |

| Phase 10Q.1 selectable one-step operator comparison | PASS |

| Phase 10S short no-forcing drift, N=64, final time 1.0 | PASS |

| Phase 10V extended no-forcing drift, N=64, final time 5.0 | PASS |

| Phase 10W extended no-forcing drift decision gate | PASS |



\## Why Phase 10X Is Needed



The previous no-forcing drift audits used:



N = 64



The next conservative question is:



Do fd\_centered, pseudo\_spectral, and arakawa remain finite, non-explosive, and closely aligned at N=128 for a short no-forcing drift audit?



This changes one major variable:



N from 64 to 128



The time horizon should remain short:



final time = 1.0



This avoids changing resolution and duration at the same time.



\## Design Decision



Proceed with a short N=128 no-forcing drift audit.



Recommended parameters:



| Parameter | Value |

|---|---:|

| N | 128 |

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| forcing | zero |

| initial RMS | 0.01 |

| initial field | phase6d\_like\_multimode |



\## Methods to Compare



The N=128 audit should compare:



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



The future Phase 10Y audit should use an audit-local subclass:



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



Use the same controlled phase6d\_like\_multimode field:



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



phase10y\_n128\_short\_no\_forcing\_drift\_comparison\_audit.py



Recommended outputs:



PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT.csv



PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_TIME\_HISTORY.csv



PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_PAIRWISE\_SUMMARY.csv



PHASE10Y\_N128\_SHORT\_NO\_FORCING\_DRIFT\_COMPARISON\_AUDIT\_REPORT.md



\## Required Global Checks



The Phase 10Y audit should verify:



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



The N=128 audit should pass if all methods satisfy:



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



Phase 10S and 10V pairwise comparisons were well below this threshold.



The N=128 audit may accumulate different small numerical differences, but a 1e-2 threshold remains conservative for detecting large disagreement.



\## Monotonicity Interpretation



The audit should record:



\- energy\_monotone\_nonincreasing\_logged

\- enstrophy\_monotone\_nonincreasing\_logged



For this first N=128 no-forcing audit, monotonicity should be diagnostic rather than the only pass/fail criterion.



If monotonicity fails but final drift remains small and non-explosive, the report should classify the result carefully as PASS with review note, or REVIEW if drift behavior looks suspicious.



Do not silently loosen thresholds after seeing results.



\## Review Criteria



The Phase 10Y audit should report REVIEW if:



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



\## Runtime Expectation



This audit should be more expensive than Phase 10S because N increases from 64 to 128.



The work scales roughly with FFT size and grid size.



Expected runtime on the laptop:



\- best case: a few minutes

\- reasonable range: 5 to 20 minutes

\- slow case: longer if system is busy or power settings throttle CPU



The script should print progress every 100 steps.



\## What Phase 10Y Should Not Do



Phase 10Y should not call:



SpectralSolver.run()



Phase 10Y should not call:



SelectableAdvectionSolver.run()



Phase 10Y should not modify:



project/solver/spectral\_solver.py



Phase 10Y should not modify:



project/solver/selectable\_advection\_solver.py



Phase 10Y should not modify:



project/solver/advection\_operators.py



Phase 10Y should not use forcing.



Phase 10Y should not run forced turbulence experiments.



Phase 10Y should not run k^-3 experiments.



Phase 10Y should not claim Arakawa is production-ready.



\## What Phase 10Y May Do



Phase 10Y may create a standalone audit script.



Phase 10Y may define an audit-local no-forcing subclass.



Phase 10Y may repeatedly call:



step\_once\_selectable(w)



inside the audit script.



Phase 10Y may write CSV diagnostic outputs.



Phase 10Y may compare method drift.



Phase 10Y may produce a report.



\## Scientific Boundary



Correct statement after a passing Phase 10Y would be:



The selectable methods remained finite and non-explosive in a controlled N=128 short no-forcing drift audit through final time 1.0.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Recommended Next Phase After 10Y



If Phase 10Y passes, the next phase should be:



Phase 10Z — N128 Short No-Forcing Drift Decision Gate



Purpose:



Decide whether to proceed to either:



\- longer N=128 no-forcing drift

\- N=64 controlled forced-response design

\- selectable run-loop design



Do not jump directly to k^-3 claims.



\## Decision



Phase 10X decision:



Proceed to Phase 10Y N=128 short no-forcing drift comparison audit.



Use:



\- N=128

\- Re=1000000

\- dt=0.001

\- steps=1000

\- final time=1.0

\- forcing=zero

\- phase6d\_like\_multimode initial condition



Do not modify solver source files.



Do not enable run().



Do not run forced turbulence experiments.



Do not claim turbulence.



Do not claim k^-3 scaling.



\## Final Result



Phase 10X design:



PASS



Next phase:



Phase 10Y — N128 Short No-Forcing Drift Comparison Audit



Required guardrails:



\- SpectralSolver must remain unchanged.

\- SelectableAdvectionSolver must remain unchanged.

\- advection\_operators must remain unchanged.

\- SelectableAdvectionSolver.run() must remain disabled.

\- No forcing must be verified.

\- No forced turbulence.

\- No k^-3 claims.

