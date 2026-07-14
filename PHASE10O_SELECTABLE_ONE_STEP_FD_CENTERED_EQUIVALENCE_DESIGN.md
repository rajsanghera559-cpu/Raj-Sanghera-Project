\# Phase 10O Selectable One-Step fd\_centered Equivalence Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.49-phase10N1-fd-centered-rhs-equivalence-audit

\- Current previous commit: 637af4e

\- Design file: PHASE10O\_SELECTABLE\_ONE\_STEP\_FD\_CENTERED\_EQUIVALENCE\_DESIGN.md



\## Purpose



Phase 10O is a design-only phase.



The purpose is to design a narrow one-step RK2-style selectable update path.



The first one-step target is:



SelectableAdvectionSolver(advection\_method="fd\_centered")



against:



the baseline SpectralSolver one-step update logic



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

\- metadata\_dict()

\- selectable\_advection\_metadata()

\- run() intentionally disabled



Phase 10N.1 proved:



SelectableAdvectionSolver(advection\_method="fd\_centered").compute\_rhs\_selectable(w)



matches the direct baseline RHS logic exactly.



For all tested fields and resolutions:



\- diff\_l2 = 0

\- diff\_max\_abs = 0

\- relative\_error = 0

\- cosine\_similarity = 1



\## Why Phase 10O Is Needed



RHS equivalence is not the same as one-step equivalence.



A one-step audit must verify the full baseline RK2-style update:



1\. k1 = rhs(w)

2\. w1 = w + dt \* k1

3\. k2 = rhs(w1)

4\. w\_new = w + 0.5 \* dt \* (k1 + k2)

5\. apply 2/3 spectral dealiasing to w\_new



Only after this passes for fd\_centered should Arakawa short-time update tests be considered.



\## Baseline One-Step Logic



The baseline SpectralSolver.run() loop applies this sequence:



psi = streamfunction(self.w)



u, v = velocity(psi)



wx = centered finite difference of self.w in x



wy = centered finite difference of self.w in y



adv = u \* wx + v \* wy



k1 = -adv + laplacian\_spectral(self.w) + forcing()



w1 = self.w + dt \* k1



Then the solver repeats the RHS calculation on w1:



psi = streamfunction(w1)



u, v = velocity(psi)



wx = centered finite difference of w1 in x



wy = centered finite difference of w1 in y



adv = u \* wx + v \* wy



k2 = -adv + laplacian\_spectral(w1) + forcing()



Then:



w\_new = self.w + 0.5 \* dt \* (k1 + k2)



Then dealiasing is applied:



W = fft2(w\_new)



W \*= self.deal



self.w = ifft2(W).real



\## Design Decision



Proceed to a pure one-step helper.



Recommended future method name:



step\_once\_selectable(self, w)



The method should return the next vorticity field.



It should not mutate input w.



It should not mutate solver.w.



It should not write files.



It should not call run().



It should not enable production simulation behavior.



\## Recommended Future Implementation



Phase 10P should add this method to:



project/solver/selectable\_advection\_solver.py



Recommended method:



step\_once\_selectable(self, w)



Conceptual implementation:



1\. Validate shape.

2\. Convert input to real array.

3\. Save local arr.

4\. Compute k1 = compute\_rhs\_selectable(arr).

5\. Compute w1 = arr + dt \* k1.

6\. Compute k2 = compute\_rhs\_selectable(w1).

7\. Compute w\_new = arr + 0.5 \* dt \* (k1 + k2).

8\. Apply the same 2/3 dealiasing mask used by SpectralSolver.

9\. Return dealiased w\_new.real.

10\. Do not mutate arr.

11\. Do not mutate solver.w.

12\. Do not write diagnostics.

13\. Do not enable run().



\## Required Dealiasing Placement



The one-step selectable helper must apply dealiasing after the RK2-style update, matching SpectralSolver.run().



Correct placement:



After:



w\_new = w + 0.5 \* dt \* (k1 + k2)



Then:



W = fft2(w\_new)



W \*= self.deal



w\_next = ifft2(W).real



Incorrect placement:



\- before k1

\- inside compute\_rhs\_selectable

\- inside compute\_advection

\- between k1 and k2

\- on adv only

\- on diffusion only

\- on forcing only



\## Required fd\_centered Equivalence Audit



After implementation, Phase 10P.1 should compare:



baseline one-step update



against:



SelectableAdvectionSolver(advection\_method="fd\_centered").step\_once\_selectable(w)



The baseline one-step update should be a direct transcription of SpectralSolver.run() logic.



The audit should not call SpectralSolver.run().



Reason:



SpectralSolver.run() is a loop with diagnostics and file writing.



The audit should isolate one-step numerical equivalence.



\## Test Fields



The one-step audit should use:



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



\## Required Checks



The Phase 10P.1 one-step audit should check:



\- SpectralSolver imports

\- SelectableAdvectionSolver imports

\- SpectralSolver file has no git diff

\- SelectableAdvectionSolver file has no git diff

\- advection\_method is fd\_centered

\- input w unchanged

\- baseline solver.w unchanged

\- selectable solver.w unchanged

\- baseline one-step output finite

\- selectable one-step output finite

\- baseline one-step output real

\- selectable one-step output real

\- field difference L2

\- field difference max\_abs

\- relative field error

\- cosine similarity

\- exact match or strict floating-point equivalence

\- run() remains disabled

\- metadata says run\_enabled=false

\- metadata says turbulence\_claim=false

\- metadata says k\_minus\_3\_claim=false



\## Recommended Tolerances



Because Phase 10N.1 RHS equivalence was exact, one-step fd\_centered equivalence should likely be exact for the tested cases.



Initial strict target:



\- diff\_l2 = 0

\- diff\_max\_abs = 0

\- relative\_error = 0

\- cosine\_similarity = 1



If exact equality fails from harmless floating-point ordering, use strict fallback tolerance:



\- relative\_error <= 1e-12

\- diff\_max\_abs <= 1e-14



If this fallback is needed, report it explicitly.



Do not silently relax tolerances.



\## Metadata Requirements



Future metadata should include:



| Field | Required Value |

|---|---|

| solver\_variant | selectable\_advection |

| solver\_class | SelectableAdvectionSolver |

| baseline\_solver\_class | SpectralSolver |

| advection\_method | fd\_centered |

| rhs\_method | compute\_rhs\_selectable |

| step\_method | step\_once\_selectable |

| step\_status | diagnostic\_scaffold |

| production\_baseline\_modified | false |

| run\_enabled | false |

| turbulence\_claim | false |

| k\_minus\_3\_claim | false |



\## What Phase 10P May Modify



Phase 10P may modify only:



project/solver/selectable\_advection\_solver.py



Allowed change:



Add step\_once\_selectable(self, w)



Optional metadata addition:



\- step\_method

\- step\_status



\## What Phase 10P Must Not Modify



Phase 10P must not modify:



project/solver/spectral\_solver.py



Phase 10P must not modify:



project/solver/advection\_operators.py



Phase 10P must not modify previous audit reports.



Phase 10P must not enable run().



Phase 10P must not run long simulations.



Phase 10P must not test Arakawa time evolution yet.



\## What Phase 10P.1 Must Not Claim



Phase 10P.1 must not claim:



\- production readiness

\- turbulence

\- k^-3 scaling

\- inertial-range cascade

\- long-time stability

\- Arakawa time-evolution validity



The only valid claim after a passing Phase 10P.1 would be:



The selectable fd\_centered one-step helper reproduces the baseline one-step update on controlled fields.



\## Recommended Sequence After Phase 10O



Recommended next phases:



1\. Phase 10P — implement step\_once\_selectable scaffold.

2\. Phase 10P.1 — audit fd\_centered one-step equivalence.

3\. Phase 10Q — design short controlled comparison of fd\_centered, pseudo\_spectral, and arakawa one-step outputs.

4\. Phase 10R — only after one-step equivalence passes, design short no-forcing Arakawa drift test.

5\. Phase 10S — only after design and guardrails, run short no-forcing Arakawa drift test.



\## Decision



Phase 10O decision:



Proceed to Phase 10P implementation.



Phase 10P should add only:



step\_once\_selectable(self, w)



Do not enable run().



Do not replace SpectralSolver.



Do not run long simulations.



Do not test Arakawa time evolution yet.



\## Final Result



Phase 10O design:



PASS



Next phase:



Phase 10P — Selectable One-Step Scaffold Implementation



Required guardrail:



SpectralSolver must remain unchanged.

