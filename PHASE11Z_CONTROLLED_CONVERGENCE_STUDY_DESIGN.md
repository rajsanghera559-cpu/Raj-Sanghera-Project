\# Phase 11Z Controlled Convergence Study Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.25-phase11Y-N64-N128-controlled-selectable-diagnostic-comparison-summary-report

\- Current previous commit: 7579f80

\- Design file: PHASE11Z\_CONTROLLED\_CONVERGENCE\_STUDY\_DESIGN.md



\## Purpose



Phase 11Z is a design-only phase.



The purpose is to design a controlled convergence-study pathway for the selectable diagnostic solver.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove convergence.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



This phase does not claim method superiority.



\## Current Solver Status



The validated baseline solver remains:



project/solver/spectral\_solver.py



The selectable diagnostic solver remains:



project/solver/selectable\_advection\_solver.py



The selectable solver currently supports:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The selectable solver currently includes:



\- compute\_advection(w)

\- compute\_rhs\_selectable(w)

\- step\_once\_selectable(w)

\- run\_selectable\_diagnostic(...)



The selectable solver still has:



run() intentionally disabled



This remains correct.



\## Why Phase 11Z Is Needed



Phase 11S passed a controlled selectable diagnostic comparison at:



N = 64



Phase 11V passed the same controlled selectable diagnostic comparison at:



N = 128



Phase 11Y summarized those results.



The N64/N128 comparison showed consistent controlled diagnostic behavior, but it did not prove convergence.



A proper convergence study needs a dedicated design.



\## Core Scientific Boundary



A two-resolution comparison can show controlled resolution consistency.



A two-resolution comparison cannot prove a convergence rate by itself.



A stronger convergence study requires at least one of the following:



1\. an analytical reference solution



2\. a manufactured solution



3\. a sufficiently resolved reference run



4\. at least three resolutions for observed error-ratio behavior



The current nonlinear forced selectable comparison has no analytical reference solution.



Therefore, Phase 11Z must design a careful staged convergence pathway.



\## Recommended Convergence Pathway



Use a staged approach.



| Stage | Purpose | Claim Allowed |

|---|---|---|

| Phase 12A | N64/N128 controlled resolution-consistency audit | consistency only |

| Phase 12B | N256 feasibility and runtime design | feasibility only |

| Phase 12C | N64/N128/N256 controlled convergence audit, if feasible | limited observed convergence trend |

| Phase 12D | convergence decision gate | decide what claims are supported |



This prevents overclaiming.



\## Recommended Next Phase



Phase 12A — Controlled Resolution-Consistency Audit



Purpose:



Use the completed Phase 11S and Phase 11V outputs to compute structured N64/N128 consistency metrics.



Phase 12A should not run new simulations.



Phase 12A should not claim convergence.



Phase 12A should only report controlled resolution-consistency observations.



\## Recommended Phase 12A Inputs



Use these existing files:



\- PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv

\- PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv

\- PHASE11Y\_N64\_N128\_CONTROLLED\_SELECTABLE\_DIAGNOSTIC\_COMPARISON\_SUMMARY\_REPORT.md



Optional existing state files may also be used from:



experiments/selectable\_diagnostics/phase11S\_fd\_centered



experiments/selectable\_diagnostics/phase11S\_pseudo\_spectral



experiments/selectable\_diagnostics/phase11S\_arakawa



experiments/selectable\_diagnostics/phase11V\_N128\_fd\_centered



experiments/selectable\_diagnostics/phase11V\_N128\_pseudo\_spectral



experiments/selectable\_diagnostics/phase11V\_N128\_arakawa



\## Recommended Phase 12A Outputs



Phase 12A should create:



\- phase12a\_controlled\_resolution\_consistency\_audit.py

\- PHASE12A\_CONTROLLED\_RESOLUTION\_CONSISTENCY\_AUDIT.csv

\- PHASE12A\_CONTROLLED\_RESOLUTION\_CONSISTENCY\_PAIRWISE\_TRENDS.csv

\- PHASE12A\_CONTROLLED\_RESOLUTION\_CONSISTENCY\_AUDIT\_REPORT.md



The audit should only reorganize and compare existing Phase 11S and Phase 11V results.



No new simulation should be run in Phase 12A.



\## Phase 12A Method-Level Metrics



For each method, compare N64 and N128:



\- final RMS

\- final kinetic energy

\- final enstrophy

\- RMS ratio

\- energy ratio

\- enstrophy ratio

\- dominant shell

\- low-k fraction k <= 4

\- high-k fraction k >= 10

\- spectrum direct relative error

\- method result



Methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



\## Phase 12A Pairwise Metrics



For each method pair, compare N64 and N128:



\- field relative L2 difference

\- energy relative difference

\- enstrophy relative difference

\- RMS relative difference

\- spectrum relative L2 difference

\- spectrum cosine similarity

\- dominant shell match

\- pairwise result



Pairs:



\- pseudo\_spectral vs fd\_centered

\- arakawa vs fd\_centered

\- arakawa vs pseudo\_spectral



\## Phase 12A Reduction-Ratio Metrics



Phase 12A may compute reduction ratios for pairwise method differences.



Example:



reduction\_ratio = N64\_metric / N128\_metric



This may be computed for:



\- field relative L2 difference

\- spectrum relative L2 difference

\- energy relative difference

\- enstrophy relative difference

\- RMS relative difference



Important:



These ratios are diagnostic trend metrics only.



They are not convergence-order proof.



\## Field-Level Comparison Design



If Phase 12A uses saved final state files, it may compare fields across resolutions.



For N64 and N128:



\- The N128 grid aligns with the N64 grid on every second point.

\- A simple controlled restriction can be:



N128\_restricted\_to\_N64 = N128\_field\[::2, ::2]



Then compare:



N64\_field



against:



N128\_restricted\_to\_N64



This should be reported as an aligned-grid restriction comparison.



It should not be presented as a full spectral projection convergence proof.



\## Field-Level Norms



If saved final state files are used, compute:



\- field max absolute difference

\- field RMS/L2 difference

\- field relative RMS/L2 difference

\- final state finite check

\- final state real check



Recommended formula:



relative\_l2 = rms(N64\_field - restricted\_N128\_field) / max(rms(restricted\_N128\_field), 1e-300)



\## Spectrum-Level Comparison Design



Compare spectrum values on common shell bins.



For each method:



\- read N64 final spectrum

\- read N128 final spectrum

\- compare common k bins

\- compute spectrum relative L2 difference

\- compare dominant shell

\- compare low-k fraction

\- compare high-k fraction



Do not fit slopes.



Do not claim k^-3 behavior.



Do not claim inertial-range behavior.



\## Phase 12A Pass/Fail Philosophy



Phase 12A should pass if:



1\. required Phase 11S files exist



2\. required Phase 11V files exist



3\. method rows can be loaded



4\. pairwise rows can be loaded



5\. all Phase 11S method results are PASS



6\. all Phase 11V method results are PASS



7\. all Phase 11S pairwise results are PASS



8\. all Phase 11V pairwise results are PASS



9\. N64/N128 comparison metrics are finite



10\. metadata guardrails remain documented



11\. no convergence claim is made



12\. no turbulence claim is made



13\. no k^-3 claim is made



14\. no method-superiority claim is made



\## What Phase 12A Would Confirm



A Phase 12A PASS would confirm:



\- completed N64 and N128 controlled diagnostic results can be compared in a structured way

\- all required source CSV files exist

\- both resolutions passed their controlled diagnostic audits

\- pairwise method differences can be compared across resolution

\- broad resolution-consistency metrics are finite

\- no unsupported scientific claim is needed



\## What Phase 12A Would Not Confirm



A Phase 12A PASS would not confirm:



\- convergence

\- convergence order

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- method superiority

\- production readiness

\- statistical steady state behavior



\## Phase 12B N256 Feasibility Design



After Phase 12A, a separate feasibility phase should decide whether N=256 is practical.



Suggested design:



Phase 12B — N256 Controlled Selectable Diagnostic Feasibility Design



Purpose:



Estimate and test whether N=256 can be run safely under the same controlled setup.



Recommended first feasibility test:



| Parameter | Value |

|---|---:|

| N | 256 |

| Re | 1000 |

| dt | 0.001 |

| steps | 100 |

| final time | 0.1 |

| log\_every | 10 |

| methods | fd\_centered first only |

| forcing | inherited baseline deterministic forcing |



Reason:



N=256 has four times as many grid points as N=128 and sixteen times as many grid points as N=64.



The project should not jump directly into a full N=256 three-method run without a feasibility check.



\## Phase 12C Three-Resolution Convergence Audit



If Phase 12B passes, Phase 12C may run a three-resolution controlled convergence audit.



Candidate resolutions:



\- N = 64

\- N = 128

\- N = 256



Candidate methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Candidate parameters:



| Parameter | Value |

|---|---:|

| Re | 1000 |

| dt | 0.001 |

| final time | 1.0 |

| initial RMS | 0.01 |

| forcing | inherited baseline deterministic forcing |



Phase 12C may compute observed reduction trends.



It still must not overclaim beyond what the data supports.



\## Optional Observed-Order Formula



If three resolutions are available, an observed order may be estimated.



Let:



E64\_128 = difference between N64 and restricted N128



E128\_256 = difference between N128 and restricted N256



Then:



observed\_order = log(E64\_128 / E128\_256) / log(2)



This should only be computed if:



\- both errors are finite

\- both errors are positive

\- same norm is used

\- same physical setup is used

\- same final time is used

\- same comparison logic is used



A single observed order does not prove general convergence.



It only describes the observed behavior of that controlled test.



\## Recommended Norms for Future Three-Resolution Study



Use multiple norms:



\- field RMS/L2 norm

\- field max absolute norm

\- energy relative difference

\- enstrophy relative difference

\- RMS relative difference

\- spectrum relative L2 difference

\- low-k fraction difference

\- high-k fraction difference



Do not rely on one metric.



\## Initial Condition Rule



All convergence-related studies should use the same smooth deterministic initial condition family:



\- sin(2X) cos(2Y)

\- 0.75 sin(3X) cos(Y)

\- 0.50 sin(X) cos(4Y)

\- 0.35 cos(4X - 2Y)



Then rescale to:



RMS = 0.01



The field should be evaluated directly on each grid.



Do not interpolate the initial field from one grid to another unless a later phase explicitly designs that.



\## Forcing Rule



All convergence-related studies should use the inherited baseline deterministic forcing unless a later phase explicitly designs a forcing sensitivity study.



No forcing-amplitude changes should be mixed into a convergence study.



\## Time Step Rule



The first convergence design keeps:



dt = 0.001



Reason:



This isolates resolution behavior while preserving the already tested time step.



A separate temporal convergence study would be needed to study dt refinement.



Do not mix spatial and temporal convergence claims in the same first study.



\## Guardrails



All convergence-related phases must preserve:



\- SpectralSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- fd\_centered default unchanged

\- Arakawa not default

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no inertial-range claim

\- no method superiority claim

\- no convergence claim until a dedicated convergence audit supports it



\## Scientific Boundary



Correct statement after Phase 11Z:



A controlled convergence-study pathway has been designed, beginning with an N64/N128 resolution-consistency audit and requiring later N256 feasibility before any convergence-rate claim.



Incorrect statement:



The project has proven convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Decision



Phase 11Z decision:



PROCEED TO PHASE 12A CONTROLLED RESOLUTION-CONSISTENCY AUDIT.



Do not run new simulations in Phase 12A.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims.



Do not make method superiority claims.



\## Final Result



Phase 11Z controlled convergence study design:



PASS



Next phase:



Phase 12A — Controlled Resolution-Consistency Audit

