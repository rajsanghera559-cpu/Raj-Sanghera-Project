\# Phase 10E Arakawa Operator Planning and Sign-Convention Audit



\## Checkpoint



\- Branch: phase4\_validation

\- Current prior tag: v0.4.37-phase10D-advection-operator-comparison-audit

\- Current baseline solver: project/solver/spectral\_solver.py

\- Current advection scaffold: project/solver/advection\_operators.py

\- Current method classification: mixed\_spectral\_finite\_difference



\## Purpose



Phase 10E documents the sign convention, indexing requirements, and acceptance criteria for a future Arakawa advection implementation.



This phase does not run the solver.



This phase does not modify production solver behavior.



This phase does not implement Arakawa.



This phase does not make turbulence or k^-3 claims.



The purpose is to prevent sign mistakes, indexing mistakes, and unvalidated solver changes before any Arakawa code is written.



\## Current Baseline Solver Convention



The current solver uses vorticity omega and streamfunction psi.



The current velocity convention is:



u = d psi / dy



v = - d psi / dx



The current vorticity-gradient convention is:



omega\_x = d omega / dx



omega\_y = d omega / dy



The current nonlinear advection diagnostic is:



adv = u \* omega\_x + v \* omega\_y



The current time-update convention is:



d omega / dt = -adv + diffusion + forcing



This means all future advection operators should return adv, not -adv.



The production solver applies the negative sign outside the advection operator.



\## Critical Sign-Convention Rule



Any future Arakawa or spectral Jacobian function must preserve the project convention:



operator returns adv = u dot grad omega



The solver RHS then uses:



\-adv



A future implementation must not silently return -adv unless explicitly documented.



This is the highest-risk source of error.



\## Relationship to Jacobian Notation



A common Jacobian notation is:



J(psi, omega) = psi\_x \* omega\_y - psi\_y \* omega\_x



Given the current project velocity convention:



u = psi\_y



v = -psi\_x



Then:



u \* omega\_x + v \* omega\_y = psi\_y \* omega\_x - psi\_x \* omega\_y



This is the negative of J(psi, omega) under the convention above.



Therefore:



adv = u dot grad omega = -J(psi, omega)



If an Arakawa formula computes J(psi, omega), then the advection returned to this project must be:



adv = -J\_arakawa(psi, omega)



If an Arakawa formula is written directly to compute u dot grad omega, then it may return adv directly.



This must be tested explicitly.



\## Required Sign Tests Before Acceptance



A future Arakawa implementation must pass sign tests against the current pseudo-spectral advection diagnostic.



The reference diagnostic is:



advection\_pseudo\_spectral(solver, w)



from:



project/solver/advection\_operators.py



A future Arakawa advection function should be tested on controlled nonlinear fields.



Expected result:



arakawa\_adv should have positive cosine similarity with pseudo\_spectral\_adv.



If cosine similarity is near -1, the sign is likely flipped.



If cosine similarity is near 0, the formula or indexing is likely wrong.



Acceptance threshold for low-k nonlinear fields:



cosine similarity greater than 0.99



\## Required Shape and Boundary Assumptions



The Arakawa implementation must assume:



\- square grid

\- periodic boundary conditions

\- uniform grid spacing

\- dx = dy

\- domain length L = 2\*pi

\- vorticity field shape equals solver.w.shape



The implementation must use periodic indexing.



Preferred indexing method:



np.roll



Reason:



np.roll makes periodic boundary conditions explicit and consistent with the current finite-difference implementation.



\## Required Function Design



The future Arakawa implementation should be added to:



project/solver/advection\_operators.py



The existing placeholders are:



jacobian\_arakawa\_periodic(psi, w, dx)



advection\_arakawa(solver, w)



The recommended design is:



jacobian\_arakawa\_periodic computes a documented Arakawa Jacobian expression.



advection\_arakawa converts that Jacobian to the project advection convention.



If jacobian\_arakawa\_periodic returns J(psi, omega), then advection\_arakawa should return -J.



The docstring must state the sign convention.



\## Required Non-Mutation Rule



A future Arakawa implementation must not mutate:



\- input psi

\- input w

\- solver.w

\- solver.kx

\- solver.ky

\- solver.deal



It should return a new real-valued NumPy array.



\## Required Finite-Value Rule



A future Arakawa implementation must return finite values for:



\- single\_mode\_k2\_2

\- low\_mode\_pair

\- phase6d\_like\_multimode

\- higher\_smooth\_multimode



No NaN.



No Inf.



No complex output.



\## Required Controlled Test Fields



The Arakawa audit should use the same controlled fields as Phase 10D.



\### single\_mode\_k2\_2



Purpose:



Near-null nonlinear reference.



Caution:



Relative error is not primary evidence because nonlinear advection norms can be near machine precision.



\### low\_mode\_pair



Purpose:



Primary low-k nonlinear comparison.



\### phase6d\_like\_multimode



Purpose:



Continuity with Phase 6D, Phase 9A, and Phase 10D tests.



\### higher\_smooth\_multimode



Purpose:



Stress derivative behavior at moderately higher wavenumbers.



\## Required Comparisons



A future Arakawa audit should compare:



\- finite-difference advection

\- pseudo-spectral advection

\- Arakawa advection



For each field and resolution, compute:



\- L2 norm of each operator

\- max absolute value of each operator

\- L2 difference FD vs pseudo-spectral

\- L2 difference Arakawa vs pseudo-spectral

\- L2 difference Arakawa vs FD

\- relative L2 error against pseudo-spectral

\- cosine similarity against pseudo-spectral

\- finite-value checks

\- input mutation checks

\- solver.w mutation checks



\## Required Resolutions



A future Arakawa audit should test at:



\- N = 64

\- N = 128



Optional later:



\- N = 256



N = 256 should not be required for the first Arakawa implementation audit.



\## Required Acceptance Criteria



A future Arakawa implementation should not be accepted unless:



| Check | Requirement |

|---|---|

| imports successfully | PASS |

| returns finite real arrays | PASS |

| does not mutate input fields | PASS |

| does not mutate solver.w | PASS |

| sign matches pseudo-spectral reference | PASS |

| low\_mode\_pair cosine similarity vs pseudo-spectral | greater than 0.99 |

| phase6d\_like cosine similarity vs pseudo-spectral | greater than 0.99 |

| higher\_smooth cosine similarity vs pseudo-spectral | greater than 0.95 |

| Arakawa relative error is documented | PASS |

| N128 behavior is not worse than N64 | PASS or REVIEW |

| single-mode near-null case handled as REVIEW | PASS |



\## Required Reports



A future Arakawa implementation phase should produce:



\- implementation commit

\- audit script

\- audit CSV

\- audit report

\- decision gate

\- git tag



The report must state:



\- exact formula used

\- sign convention

\- boundary convention

\- indexing convention

\- comparisons against pseudo-spectral diagnostic

\- limitations

\- whether the implementation is accepted, rejected, or under review



\## Do Not Replace SpectralSolver Yet



The baseline solver should remain unchanged until the Arakawa operator passes standalone audits.



The future Arakawa implementation should first exist only as a standalone operator in:



project/solver/advection\_operators.py



Only after standalone tests pass should a selectable-advection solver be considered.



\## Proposed Future Phase Sequence



Recommended sequence:



Phase 10F — Implement Arakawa Operator Placeholder Replacement



Purpose:



Replace the NotImplementedError placeholder with a documented Arakawa operator.



Phase 10G — Arakawa Operator Sanity Audit



Purpose:



Verify import, sign, finite values, mutation safety, and basic comparisons.



Phase 10H — Arakawa vs Pseudo-Spectral Operator Comparison



Purpose:



Compare Arakawa, finite-difference, and pseudo-spectral operators on controlled fields.



Phase 11A — Selectable-Advection Solver Planning



Purpose:



Plan a solver class that can select fd\_centered, pseudo\_spectral, or arakawa advection.



Phase 11B — Selectable-Advection Solver Implementation



Purpose:



Implement a new solver variant without replacing SpectralSolver.



Phase 11C — Rerun Phase 8 Benchmarks on New Solver



Purpose:



Verify the new solver reproduces linear decay benchmarks.



Phase 11D — Rerun Phase 9 Nonlinear Drift Benchmarks on New Solver



Purpose:



Verify nonlinear no-forcing behavior with upgraded advection.



\## Current Decision



Phase 10E decision:



Do not implement Arakawa directly into production solver.



Do not replace current solver.



Do not run turbulence experiments yet.



Implement Arakawa only as a standalone audited operator first.



The next code phase should be narrow and reversible.



\## Recommended Next Phase



Recommended next phase:



Phase 10F — Standalone Arakawa Operator Implementation



Purpose:



Implement jacobian\_arakawa\_periodic and advection\_arakawa in project/solver/advection\_operators.py while preserving all existing functions and preserving the baseline solver.



The implementation must include clear docstrings explaining sign convention.



The implementation must not change SpectralSolver.



\## Conclusion



Phase 10E establishes the sign-convention and acceptance framework for Arakawa implementation.



The project should proceed cautiously.



The next credibility improvement is not a larger simulation.



The next credibility improvement is a carefully audited standalone Arakawa operator.

