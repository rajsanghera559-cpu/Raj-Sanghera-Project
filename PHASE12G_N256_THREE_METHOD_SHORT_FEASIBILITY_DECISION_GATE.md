\# Phase 12G N256 Three-Method Short Feasibility Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.32-phase12F-N256-three-method-short-feasibility-audit

\- Current previous commit: a7a8cf9

\- Decision gate file: PHASE12G\_N256\_THREE\_METHOD\_SHORT\_FEASIBILITY\_DECISION\_GATE.md



\## Purpose



Phase 12G is a documentation-only decision gate.



The purpose is to summarize Phase 12F and decide whether the project should proceed to an intermediate longer N256 feasibility design.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove full N256 final-time-1.0 feasibility.



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



\## Phase 12F Summary



Phase 12F ran a short N256 feasibility audit across all selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Each method used:



run\_selectable\_diagnostic(...)



The audit did not call:



SpectralSolver.run()



The audit did not enable:



SelectableAdvectionSolver.run()



The audit used identical controlled conditions for all three methods.



\## Phase 12F Parameters



| Parameter | Value |

|---|---:|

| N | 256 |

| Re | 1000 |

| dt | 0.001 |

| steps | 100 |

| final time | 0.1 |

| log\_every | 10 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



\## Phase 12F Global Checks



| Check | Result |

|---|---:|

| SpectralSolver import | PASS |

| SelectableAdvectionSolver import | PASS |

| Supported methods exact | PASS |

| Default method fd\_centered | PASS |

| compute\_rhs\_selectable exists | PASS |

| step\_once\_selectable exists | PASS |

| run\_selectable\_diagnostic exists | PASS |

| SpectralSolver file has no git diff | PASS |

| advection\_operators file has no git diff | PASS |

| selectable\_advection\_solver file has no git diff | PASS |

| N == 256 | PASS |

| Re == 1000 | PASS |

| dt == 0.001 | PASS |

| steps == 100 | PASS |

| final time == 0.1 | PASS |

| log\_every == 10 | PASS |

| All grid shapes same | PASS |

| All dx same | PASS |

| All dt same | PASS |

| All nu same | PASS |

| All dealias masks same | PASS |

| All forcing fields same | PASS |

| initial RMS == 0.01 | PASS |

| Global checks | PASS |



\## Phase 12F Method Results



| Method | Runtime Seconds | Final RMS | Final Energy | Final Enstrophy | RMS Ratio | Energy Ratio | Enstrophy Ratio | Dominant Shell | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 2.667840200011e+00 | 1.034368880507e-02 | 5.500504856169e-06 | 5.349594904806e-05 | 1.034368880507e+00 | 1.087124783764e+00 | 1.069918980961e+00 | 3.0 | PASS |

| pseudo\_spectral | 3.442676099949e+00 | 1.034368880452e-02 | 5.500504855934e-06 | 5.349594904240e-05 | 1.034368880452e+00 | 1.087124783718e+00 | 1.069918980848e+00 | 3.0 | PASS |

| arakawa | 2.208111900021e+00 | 1.034368880452e-02 | 5.500504855930e-06 | 5.349594904237e-05 | 1.034368880452e+00 | 1.087124783717e+00 | 1.069918980847e+00 | 3.0 | PASS |



\## Phase 12F Spectrum Results



| Method | Low-k Fraction k<=4 | High-k Fraction k>=10 | Spectrum Direct Relative Error | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 9.999999914418e-01 | 7.610056746065e-18 | 3.079837103695e-16 | PASS |

| pseudo\_spectral | 9.999999914044e-01 | 7.727623770231e-18 | 6.159674207654e-16 | PASS |

| arakawa | 9.999999914579e-01 | 7.540133676010e-18 | 4.619755655744e-16 | PASS |



\## Phase 12F Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 5.789137008613e-07 | 4.272257635133e-11 | 1.058317184795e-10 | 5.291585677272e-11 | 1.670887381757e-10 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 3.243568479849e-07 | 4.356660570960e-11 | 1.063166063530e-10 | 5.315836311582e-11 | 8.799464207476e-11 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 6.665119460197e-07 | 8.440293583037e-13 | 4.848878735875e-13 | 2.425063431110e-13 | 1.610053590211e-10 | 1.000000000000e+00 | PASS | PASS |



\## Phase 12F Final Checks



| Check | Result |

|---|---:|

| Shared initial\_w unchanged across all runs | PASS |

| All method audits pass | PASS |

| All pairwise comparisons pass | PASS |

| Overall Phase 12F audit | PASS |



\## Main Finding



Phase 12F passed.



All three selectable methods completed the short N256 feasibility audit through final time 0.1.



The final states remained finite and real.



The methods wrote the required outputs.



The methods preserved metadata guardrails.



All pairwise comparisons passed.



All three methods agreed on dominant shell:



k = 3.0



\## What Phase 12F Confirms



Phase 12F confirms:



1\. N256 short-run feasibility is acceptable for fd\_centered.



2\. N256 short-run feasibility is acceptable for pseudo\_spectral.



3\. N256 short-run feasibility is acceptable for arakawa.



4\. run\_selectable\_diagnostic(...) works at N256 for all three methods through final time 0.1.



5\. output writing works at N256 for all three methods.



6\. diagnostics remain finite at N256 for all three methods in the short test.



7\. spectrum writing works at N256 for all three methods.



8\. pairwise comparisons can be computed at N256.



9\. metadata guardrails remain active.



10\. SelectableAdvectionSolver.run() remains disabled.



11\. SpectralSolver remains unchanged.



12\. advection\_operators remains unchanged.



13\. selectable\_advection\_solver remains unchanged.



\## What Phase 12F Does Not Confirm



Phase 12F does not confirm:



1\. full N256 final-time-1.0 feasibility



2\. N256 long-run stability



3\. convergence



4\. convergence order



5\. turbulence



6\. k^-3 scaling



7\. inertial range behavior



8\. method superiority



9\. production readiness



10\. statistical steady state behavior



\## Decision



Decision:



PASS



The N256 three-method short feasibility audit passed.



It is acceptable to design an intermediate longer N256 feasibility audit.



\## Advancement Approved



Proceed to a design phase for an intermediate N256 three-method longer feasibility audit.



The next design should extend final time from:



0.1



to:



0.5



The next design should not jump directly to full final time 1.0.



\## Advancement Not Approved



This decision gate does not approve:



\- full N256 final-time-1.0 three-method audit

\- convergence claims

\- convergence-order claims

\- enabling SelectableAdvectionSolver.run()

\- replacing SpectralSolver

\- making Arakawa the default

\- production simulations

\- turbulence experiments

\- k^-3 claims

\- inertial-range claims

\- method superiority claims



\## Recommended Next Phase



Phase 12H — N256 Three-Method Longer Feasibility Design



Purpose:



Design an intermediate N256 feasibility audit across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Recommended parameters:



| Parameter | Value |

|---|---:|

| N | 256 |

| Re | 1000 |

| dt | 0.001 |

| steps | 500 |

| final time | 0.5 |

| log\_every | 50 |

| initial RMS | 0.01 |

| methods | fd\_centered, pseudo\_spectral, arakawa |

| forcing | inherited baseline deterministic forcing |



Reason:



This provides a conservative intermediate step between:



\- Phase 12F final time 0.1

\- a future possible final time 1.0 audit



\## Recommended Phase 12I



After Phase 12H design, Phase 12I may run the actual N256 three-method longer feasibility audit.



Phase 12I should still be a feasibility audit only.



It should not claim full N256 final-time-1.0 feasibility.



It should not claim convergence.



It should not claim turbulence.



It should not claim k^-3 scaling.



It should not claim method superiority.



\## Required Guardrails for Phase 12H



Phase 12H must preserve:



\- SpectralSolver unchanged

\- advection\_operators unchanged

\- selectable\_advection\_solver unchanged

\- SelectableAdvectionSolver.run() disabled

\- fd\_centered default unchanged

\- Arakawa not default

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no inertial-range claim

\- no convergence claim

\- no method superiority claim



\## Scientific Boundary



Correct statement after Phase 12G:



The N256 three-method short controlled selectable diagnostic feasibility audit passed through final time 0.1.



Incorrect statement:



The project has proven full N256 feasibility, convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Final Result



Phase 12G N256 three-method short feasibility decision gate:



PASS



Proceed to Phase 12H N256 three-method longer feasibility design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make convergence claims.



Do not make method superiority claims.

