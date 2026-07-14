\# Phase 12I N256 Three-Method Longer Feasibility Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.34-phase12H-N256-three-method-longer-feasibility-design

\- Audit script: phase12i\_N256\_three\_method\_longer\_feasibility\_audit.py

\- Method output: PHASE12I\_N256\_THREE\_METHOD\_LONGER\_FEASIBILITY\_AUDIT.csv

\- Pairwise output: PHASE12I\_N256\_THREE\_METHOD\_LONGER\_FEASIBILITY\_PAIRWISE.csv

\- Report: PHASE12I\_N256\_THREE\_METHOD\_LONGER\_FEASIBILITY\_AUDIT\_REPORT.md



\## Purpose



Phase 12I audits intermediate N256 feasibility across all selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The audit uses:



run\_selectable\_diagnostic(...)



This audit does not call SpectralSolver.run().



This audit does not enable SelectableAdvectionSolver.run().



This audit does not prove full N256 final-time-1.0 feasibility.



This audit does not prove convergence.



This audit does not prove turbulence.



This audit does not prove k^-3 scaling.



This audit does not prove method superiority.



\## Parameters



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



\## Global Checks



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

| steps == 500 | PASS |

| final time == 0.5 | PASS |

| log\_every == 50 | PASS |

| All grid shapes same | PASS |

| All dx same | PASS |

| All dt same | PASS |

| All nu same | PASS |

| All dealias masks same | PASS |

| All forcing fields same | PASS |

| initial RMS == 0.01 | PASS |

| Global checks | PASS |



\## Method Results



| Method | Runtime Seconds | Final RMS | Final Energy | Final Enstrophy | RMS Ratio | Energy Ratio | Enstrophy Ratio | Dominant Shell | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 1.295509930002e+01 | 1.182262523973e-02 | 7.564604817664e-06 | 6.988723377950e-05 | 1.182262523973e+00 | 1.495075377934e+00 | 1.397744675590e+00 | 3.0 | PASS |

| pseudo\_spectral | 1.682911820000e+01 | 1.182262522432e-02 | 7.564604809936e-06 | 6.988723359734e-05 | 1.182262522432e+00 | 1.495075376406e+00 | 1.397744671947e+00 | 3.0 | PASS |

| arakawa | 1.046179410000e+01 | 1.182262522404e-02 | 7.564604809323e-06 | 6.988723359404e-05 | 1.182262522404e+00 | 1.495075376285e+00 | 1.397744671881e+00 | 3.0 | PASS |



\## Spectrum Results



| Method | Low-k Fraction k<=4 | High-k Fraction k>=10 | Spectrum Direct Relative Error | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 9.999998158271e-01 | 3.879018692226e-15 | 3.359195758421e-16 | PASS |

| pseudo\_spectral | 9.999998150231e-01 | 3.941479409825e-15 | 1.119731920618e-16 | PASS |

| arakawa | 9.999998161765e-01 | 3.845936389410e-15 | 3.359195762125e-16 | PASS |



\## Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 2.785104274575e-06 | 1.021637356775e-09 | 2.606478879885e-09 | 1.303239445768e-09 | 3.603956018851e-09 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 1.526965887341e-06 | 1.102600804918e-09 | 2.653771683435e-09 | 1.326885871629e-09 | 2.081699955374e-09 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 3.194650686045e-06 | 8.096344822538e-11 | 4.729280367299e-11 | 2.364642589219e-11 | 3.346777366681e-09 | 1.000000000000e+00 | PASS | PASS |



\## Final Checks



| Check | Result |

|---|---:|

| Shared initial\_w unchanged across all runs | PASS |

| All method audits pass | PASS |

| All pairwise comparisons pass | PASS |

| Overall Phase 12I audit | PASS |



\## Main Finding



Phase 12I passed.



All three selectable methods completed the intermediate N256 feasibility audit through final time 0.5.



The final states remained finite and real.



The methods wrote the required outputs.



The methods preserved metadata guardrails.



All pairwise comparisons passed.



All three methods agreed on dominant shell:



k = 3.0



\## Interpretation



This is an N256 three-method intermediate feasibility result.



It confirms that the selectable diagnostic pathway can run all three selectable methods at N256 for a 500-step controlled test.



This supports designing a final-time-1.0 N256 feasibility phase.



This is not a full N256 final-time-1.0 validation.



This is not convergence evidence.



This is not turbulence evidence.



This is not k^-3 evidence.



This is not method-superiority evidence.



\## What This Confirms



Phase 12I confirms:



\- N256 intermediate feasibility is acceptable for fd\_centered

\- N256 intermediate feasibility is acceptable for pseudo\_spectral

\- N256 intermediate feasibility is acceptable for arakawa

\- run\_selectable\_diagnostic works at N256 for all three methods through final time 0.5

\- output writing works at N256 for all three methods

\- diagnostics remain finite at N256 for all three methods in the intermediate test

\- spectrum writing works at N256 for all three methods

\- pairwise comparisons can be computed at N256

\- metadata guardrails remain active

\- SelectableAdvectionSolver.run() remains disabled

\- SpectralSolver remains unchanged

\- advection\_operators remains unchanged

\- selectable\_advection\_solver remains unchanged



\## What This Does Not Confirm



Phase 12I does not confirm:



\- full N256 final-time-1.0 feasibility

\- N256 long-run stability beyond final time 0.5

\- convergence

\- convergence order

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- method superiority

\- production readiness

\- statistical steady state behavior



\## Scientific Boundary



Correct statement:



Phase 12I proves intermediate N256 three-method selectable diagnostic feasibility through final time 0.5 under the tested conditions.



Incorrect statement:



Phase 12I proves full N256 feasibility, convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Recommended Next Phase



Phase 12J — N256 Three-Method Longer Feasibility Decision Gate



Purpose:



Document the Phase 12I result and decide whether to proceed to a full final-time-1.0 N256 feasibility design.



Recommended decision:



Proceed to Phase 12J decision gate.



Do not claim convergence.



Do not claim turbulence.



Do not claim k^-3 scaling.



Do not claim method superiority.



\## Final Result



Phase 12I N256 three-method longer feasibility audit:



PASS



Proceed to Phase 12J decision gate.

