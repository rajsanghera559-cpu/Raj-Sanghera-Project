\# Phase 10I Arakawa Operator Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.41-phase10H-arakawa-operator-comparison-audit

\- Current previous commit: f245ddc

\- Decision gate file: PHASE10I\_ARAKAWA\_OPERATOR\_DECISION\_GATE.md



\## Purpose



Phase 10I is a documentation-only decision gate.



The purpose is to summarize Phases 10E through 10H and decide whether the standalone Arakawa advection operator is ready to move toward a separate selectable-advection solver variant.



This phase does not modify SpectralSolver.



This phase does not run a production simulation.



This phase does not replace the validated baseline solver.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



This phase does not prove a resolved inertial-range cascade.



\## Background



The project currently has a validated baseline solver in:



project/solver/spectral\_solver.py



The current baseline method is best described as:



mixed\_spectral\_finite\_difference



The solver uses:



\- spectral streamfunction

\- spectral velocity

\- spectral diffusion

\- centered finite-difference nonlinear advection

\- RK2-style time stepping

\- post-step 2/3 spectral dealiasing



The current production solver should remain preserved.



The purpose of the Phase 10 sequence is not to overwrite the baseline solver.



The purpose is to build and audit standalone advection operators before deciding whether a selectable-advection solver variant is justified.



\## Phase 10E Summary — Sign Convention Planning



Phase 10E documented the project sign convention.



The project uses:



u = d psi / dy



v = - d psi / dx



adv = u \* omega\_x + v \* omega\_y



The solver update uses:



d omega / dt = -adv + diffusion + forcing



The standard Jacobian convention is:



J(psi, omega) = psi\_x \* omega\_y - psi\_y \* omega\_x



Because:



adv = psi\_y \* omega\_x - psi\_x \* omega\_y



then:



adv = -J(psi, omega)



Phase 10E established that a standard Arakawa Jacobian implementation should return J(psi, omega), while project advection should return -J(psi, omega).



Phase 10E result:



PASS as a planning and sign-convention phase.



\## Phase 10F Summary — Standalone Arakawa Operator Implementation



Phase 10F implemented the standalone Arakawa operator in:



project/solver/advection\_operators.py



The implementation added:



\- jacobian\_arakawa\_periodic

\- advection\_arakawa



The implementation preserved:



\- project/solver/spectral\_solver.py unchanged

\- baseline solver behavior unchanged

\- existing finite-difference and pseudo-spectral diagnostic operators



The implementation was committed at:



v0.4.39-phase10F-standalone-arakawa-operator



Phase 10F result:



PASS as implementation checkpoint.



\## Phase 10G Summary — Arakawa Operator Sanity Audit



Phase 10G audited the standalone Arakawa operator for basic correctness.



The audit checked:



\- imports

\- finite outputs

\- real-valued outputs

\- input w unchanged

\- input psi unchanged

\- solver.w unchanged

\- sign alignment with pseudo-spectral advection

\- primary nonlinear field behavior



Audit files:



\- phase10g\_arakawa\_operator\_sanity\_audit.py

\- PHASE10G\_ARAKAWA\_OPERATOR\_SANITY\_AUDIT.csv

\- PHASE10G\_ARAKAWA\_OPERATOR\_SANITY\_AUDIT\_REPORT.md



Phase 10G result:



PASS



Key finding:



The standalone Arakawa operator imports, runs, preserves input state, preserves solver state, and is not sign-flipped relative to the project pseudo-spectral advection convention.



\## Phase 10H Summary — Arakawa vs Pseudo-Spectral Operator Comparison



Phase 10H compared:



\- finite-difference centered advection

\- pseudo-spectral diagnostic advection

\- Arakawa advection



Audit files:



\- phase10h\_arakawa\_vs\_pseudospectral\_operator\_comparison.py

\- PHASE10H\_ARAKAWA\_VS\_PSEUDOSPECTRAL\_OPERATOR\_COMPARISON.csv

\- PHASE10H\_ARAKAWA\_RESOLUTION\_SUMMARY.csv

\- PHASE10H\_ARAKAWA\_VS\_PSEUDOSPECTRAL\_OPERATOR\_COMPARISON\_REPORT.md



Phase 10H result:



PASS



Overall checks:



| Check | Result |

|---|---:|

| Primary operator cases pass | PASS |

| Primary resolution behavior pass | PASS |

| Near-null reference retained | PASS |

| Phase 10H Arakawa comparison audit | PASS |



Primary field findings:



| Field | Finding |

|---|---|

| low\_mode\_pair | Arakawa better than finite-difference |

| phase6d\_like\_multimode | Arakawa comparable to finite-difference |

| higher\_smooth\_multimode | Arakawa better than finite-difference |

| single\_mode\_k2\_2 | near-null review reference only |



Resolution behavior:



The Arakawa relative error decreased from N=64 to N=128 by approximately one quarter on the primary nonlinear fields.



This is consistent with second-order-like behavior on the controlled comparison fields.



\## Evidence Supporting Advancement



The following evidence supports advancement to the next stage:



1\. The sign convention was explicitly planned before implementation.



2\. The standalone Arakawa implementation compiles and imports.



3\. The standalone Arakawa operator does not mutate input fields.



4\. The standalone Arakawa operator does not mutate solver.w.



5\. The Arakawa operator is not sign-flipped relative to the pseudo-spectral diagnostic.



6\. The Arakawa operator compares well against pseudo-spectral advection on controlled nonlinear fields.



7\. Arakawa improved over finite-difference on two primary nonlinear fields.



8\. Arakawa was comparable to finite-difference on the Phase 6D-like multimode field.



9\. Resolution behavior from N=64 to N=128 passed.



10\. The validated SpectralSolver baseline remained unchanged.



\## Evidence Against Immediate Production Replacement



The following evidence argues against replacing the production solver now:



1\. The Arakawa operator has only been tested as a standalone diagnostic operator.



2\. No long-time Arakawa time-evolution simulation has been validated.



3\. No selectable-advection solver variant exists yet.



4\. No conservation-focused Arakawa time-step audit has been performed.



5\. No nonlinear production run has been repeated using Arakawa as the active advection method.



6\. No performance or stability audit exists for Arakawa time evolution.



7\. No turbulence or inertial-range validation exists.



8\. No k^-3 claim is supported.



\## Decision



Decision:



PROCEED TO A SEPARATE SELECTABLE-ADVECTION SOLVER VARIANT.



Do not replace SpectralSolver.



Do not modify the validated baseline behavior.



Do not begin turbulence or k^-3 experiments yet.



The next stage should create a separate solver variant or wrapper that allows explicit selection among advection methods.



Recommended selectable methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The default baseline method should remain fd\_centered unless explicitly changed in the new variant.



\## Required Guardrails for Next Phase



The next phase must preserve these guardrails:



1\. SpectralSolver remains unchanged.



2\. The current baseline validation chain remains valid.



3\. The new selectable-advection solver must be isolated in a new file or separate class.



4\. The default behavior must be explicit.



5\. The selected advection method must be written into metadata.



6\. Any run output must clearly state which advection method was used.



7\. Arakawa must not be called production-ready until time-evolution audits pass.



8\. No k^-3 language is allowed unless future evidence supports it.



9\. No turbulence claim is allowed unless future evidence supports it.



10\. Any Arakawa run must be compared against baseline and pseudo-spectral diagnostics.



\## Recommended Next Phase



Phase 10J — Selectable-Advection Solver Variant Design



Purpose:



Design a separate solver variant that can select the nonlinear advection operator without changing the validated baseline SpectralSolver.



Recommended output:



\- design document only

\- no solver code yet



The design should specify:



\- new file name

\- new class name

\- accepted advection method names

\- default method

\- metadata fields

\- run-output naming rules

\- validation gates required before using the variant for research runs



\## Recommended Phase 10K



Phase 10K should create the selectable-advection solver scaffold after Phase 10J design is accepted.



Phase 10K should not run long production simulations.



Phase 10K should only test:



\- import

\- constructor

\- method selection

\- one-step compatibility

\- metadata write-out

\- no mutation of baseline SpectralSolver

\- no accidental default behavior change



\## Scientific Boundary



The correct scientific statement after Phase 10I is:



The standalone Arakawa operator passed controlled diagnostic comparison audits and is ready to be considered for an isolated selectable-advection solver variant.



The incorrect scientific statement would be:



The solver now proves turbulence or k^-3 scaling.



That statement is not supported.



\## Final Result



Phase 10I decision:



PASS



Proceed to Phase 10J design.



Do not replace SpectralSolver.



Do not run turbulence experiments.



Do not make k^-3 claims.

