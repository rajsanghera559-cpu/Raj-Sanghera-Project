\# Phase 12F N256 Three-Method Short Feasibility Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.31-phase12E-N256-three-method-short-feasibility-design

\- Audit script: phase12f\_N256\_three\_method\_short\_feasibility\_audit.py

\- Method output: PHASE12F\_N256\_THREE\_METHOD\_SHORT\_FEASIBILITY\_AUDIT.csv

\- Pairwise output: PHASE12F\_N256\_THREE\_METHOD\_SHORT\_FEASIBILITY\_PAIRWISE.csv

\- Report: PHASE12F\_N256\_THREE\_METHOD\_SHORT\_FEASIBILITY\_AUDIT\_REPORT.md



\## Purpose



Phase 12F audits short N256 feasibility across all selectable advection methods:



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

| steps | 100 |

| final time | 0.1 |

| log\_every | 10 |

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



\## Method Results



| Method | Runtime Seconds | Final RMS | Final Energy | Final Enstrophy | RMS Ratio | Energy Ratio | Enstrophy Ratio | Dominant Shell | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|

| fd\_centered | 2.667840200011e+00 | 1.034368880507e-02 | 5.500504856169e-06 | 5.349594904806e-05 | 1.034368880507e+00 | 1.087124783764e+00 | 1.069918980961e+00 | 3.0 | PASS |

| pseudo\_spectral | 3.442676099949e+00 | 1.034368880452e-02 | 5.500504855934e-06 | 5.349594904240e-05 | 1.034368880452e+00 | 1.087124783718e+00 | 1.069918980848e+00 | 3.0 | PASS |

| arakawa | 2.208111900021e+00 | 1.034368880452e-02 | 5.500504855930e-06 | 5.349594904237e-05 | 1.034368880452e+00 | 1.087124783717e+00 | 1.069918980847e+00 | 3.0 | PASS |



\## Spectrum Results



| Method | Low-k Fraction k<=4 | High-k Fraction k>=10 | Spectrum Direct Relative Error | Result |

|---|---:|---:|---:|---:|

| fd\_centered | 9.999999914418e-01 | 7.610056746065e-18 | 3.079837103695e-16 | PASS |

| pseudo\_spectral | 9.999999914044e-01 | 7.727623770231e-18 | 6.159674207654e-16 | PASS |

| arakawa | 9.999999914579e-01 | 7.540133676010e-18 | 4.619755655744e-16 | PASS |



\## Pairwise Comparisons



| Pair | Field Relative L2 Difference | Energy Relative Difference | Enstrophy Relative Difference | RMS Relative Difference | Spectrum Relative L2 Difference | Spectrum Cosine Similarity | Dominant Shell Match | Result |

|---|---:|---:|---:|---:|---:|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 5.789137008613e-07 | 4.272257635133e-11 | 1.058317184795e-10 | 5.291585677272e-11 | 1.670887381757e-10 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs fd\_centered | 3.243568479849e-07 | 4.356660570960e-11 | 1.063166063530e-10 | 5.315836311582e-11 | 8.799464207476e-11 | 1.000000000000e+00 | PASS | PASS |

| arakawa vs pseudo\_spectral | 6.665119460197e-07 | 8.440293583037e-13 | 4.848878735875e-13 | 2.425063431110e-13 | 1.610053590211e-10 | 1.000000000000e+00 | PASS | PASS |



\## Final Checks



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



\## Scientific Boundary



Correct statement:



Phase 12F proves short N256 three-method selectable diagnostic feasibility under the tested conditions.



Incorrect statement:



Phase 12F proves full N256 feasibility, convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported.



\## Recommended Next Phase



Phase 12G — N256 Three-Method Short Feasibility Decision Gate



Purpose:



Document the Phase 12F result and decide whether to proceed to an intermediate longer N256 feasibility design.



Recommended decision:



Proceed to Phase 12G decision gate.



Do not jump directly to a full N256 final-time-1.0 audit.



\## Final Result



Phase 12F N256 three-method short feasibility audit:



PASS



Proceed to Phase 12G decision gate.

