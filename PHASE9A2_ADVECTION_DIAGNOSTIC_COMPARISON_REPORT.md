\# Phase 9A.2 Advection Diagnostic Comparison Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.25-phase9A1-frozen-solver-method-review

\- Script: phase9a2\_advection\_diagnostic\_comparison.py

\- Output: PHASE9A2\_ADVECTION\_DIAGNOSTIC\_COMPARISON.csv

\- Output: PHASE9A2\_ADVECTION\_DIAGNOSTIC\_RESOLUTION\_COMPARISON.csv



\## Purpose



Phase 9A.2 compares the current finite-difference nonlinear advection term against an independently computed spectral-derivative advection diagnostic.



This phase does not modify the solver.



This phase does not run a production turbulence simulation.



This phase does not prove k^-3 scaling.



The purpose is to check whether the current finite-difference advection term behaves consistently with a spectral-derivative diagnostic on controlled test fields.



\## Active Solver Context



The active solver is classified as:



mixed\_spectral\_finite\_difference



The solver uses:



\- spectral streamfunction

\- spectral velocity

\- spectral diffusion

\- centered finite-difference vorticity gradients using np.roll

\- nonlinear advection as u \* wx + v \* wy

\- RK2-style stepping

\- post-step spectral dealiasing



The remaining numerical risk after Phase 8 is nonlinear advection accuracy.



\## Diagnostic Method



For each controlled vorticity field, two advection fields were computed:



1\. Finite-difference advection, using the active solver's centered np.roll gradient method.

2\. Spectral-derivative advection, using FFT derivatives of vorticity.



The diagnostic compared:



\- finite value checks

\- L2 norm of finite-difference advection

\- L2 norm of spectral advection

\- L2 norm of the difference

\- relative L2 error versus spectral advection

\- maximum absolute difference

\- cosine similarity

\- error reduction from N=64 to N=128



\## Test Fields



The diagnostic used four fields:



| Field | Description |

|---|---|

| single\_mode\_k2\_2 | single Fourier mode |

| low\_mode\_pair | two low Fourier modes |

| phase6d\_like\_multimode | Phase 6D-like low-k multimode field |

| higher\_smooth\_multimode | smooth higher-mode multimode field |



The single-mode case has nearly zero nonlinear advection, so its relative error is not scientifically meaningful by itself. The nonlinear multimode fields are the main evidence.



\## N=64 Results



| Field | FD L2 | Spectral L2 | Diff L2 | Relative L2 Error | Cosine Similarity |

|---|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 2.603062116224e-20 | 4.285935878258e-20 | 3.248781075738e-20 | 7.580097248347e-01 | 6.539024468067e-01 |

| low\_mode\_pair | 2.846962154144e-06 | 2.964635306408e-06 | 1.340655928186e-07 | 4.522161377788e-02 | 9.997555383637e-01 |

| phase6d\_like\_multimode | 2.357918388325e-05 | 2.442200079635e-05 | 9.270959223276e-07 | 3.796150569556e-02 | 9.998704816527e-01 |

| higher\_smooth\_multimode | 1.132540669492e-05 | 1.285246991290e-05 | 2.129457985625e-06 | 1.656847283096e-01 | 9.924337813208e-01 |



\## N=128 Results



| Field | FD L2 | Spectral L2 | Diff L2 | Relative L2 Error | Cosine Similarity |

|---|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 6.015584764359e-20 | 8.803602144451e-20 | 5.840994076682e-20 | 6.634777425015e-01 | 7.512768089114e-01 |

| low\_mode\_pair | 2.934956367391e-06 | 2.964635306408e-06 | 3.365719651615e-08 | 1.135289606901e-02 | 9.999855209012e-01 |

| phase6d\_like\_multimode | 2.420940775854e-05 | 2.442200079635e-05 | 2.332277431521e-07 | 9.549903183481e-03 | 9.999922202941e-01 |

| higher\_smooth\_multimode | 1.244645439904e-05 | 1.285246991290e-05 | 5.426692079279e-07 | 4.222295104408e-02 | 9.995947891750e-01 |



\## Resolution Comparison



| Field | N64 Relative Error | N128 Relative Error | N128/N64 Error Ratio | Improved at N128 |

|---|---:|---:|---:|---:|

| higher\_smooth\_multimode | 1.656847283096e-01 | 4.222295104408e-02 | 2.548391241297e-01 | PASS |

| low\_mode\_pair | 4.522161377788e-02 | 1.135289606901e-02 | 2.510502195868e-01 | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 9.549903183481e-03 | 2.515680821533e-01 | PASS |

| single\_mode\_k2\_2 | 7.580097248347e-01 | 6.634777425015e-01 | 8.752892222408e-01 | PASS |



\## Main Finding



For the nonlinear multimode fields, doubling resolution from N=64 to N=128 reduced the finite-difference advection error to about one quarter of its previous value.



This is consistent with the expected behavior of a second-order centered finite-difference gradient.



\## Meaningful Nonlinear Results



The most relevant nonlinear results are:



| Field | N64 Error | N128 Error | Approximate Reduction |

|---|---:|---:|---:|

| low\_mode\_pair | 4.52 percent | 1.14 percent | about 4x |

| phase6d\_like\_multimode | 3.80 percent | 0.95 percent | about 4x |

| higher\_smooth\_multimode | 16.57 percent | 4.22 percent | about 4x |



The higher-mode field has larger error, which is expected because finite-difference derivative error grows for higher wavenumbers.



\## Important Caveat



The single-mode case is close to a nonlinear null case.



Both finite-difference and spectral advection norms are near machine precision, so the relative error is dominated by tiny denominator effects.



Therefore, the single-mode relative error should not be used as evidence against the method.



The nonlinear multimode fields are the meaningful comparison.



\## What This Confirms



Phase 9A.2 confirms:



\- finite-difference advection output is finite on controlled test fields

\- finite-difference advection closely aligns with spectral-derivative advection on low-k multimode fields

\- the error decreases strongly when resolution is doubled

\- the observed reduction is consistent with second-order centered finite-difference behavior



\## What This Does Not Confirm



Phase 9A.2 does not prove full nonlinear solver stability.



Phase 9A.2 does not prove energy or enstrophy conservation in nonlinear runs.



Phase 9A.2 does not prove turbulence.



Phase 9A.2 does not prove k^-3 scaling.



Phase 9A.2 does not convert the solver into a fully spectral Navier-Stokes solver.



\## Overall Result



Phase 9A.2 advection diagnostic comparison: PASS



\## Interpretation



The current finite-difference advection term behaves reasonably on controlled nonlinear diagnostic fields.



The evidence supports continuing validation of the current solver as-is before deciding whether an Arakawa or fully spectral advection upgrade is necessary.



The next validation should test dynamic nonlinear behavior over time, not just instantaneous advection-field agreement.



\## Recommended Next Step



Phase 9A.3 — Nonlinear No-Forcing Short-Time Drift Test



Purpose:



Run a short no-forcing, low-viscosity nonlinear multimode test and audit energy/enstrophy drift.



Suggested setup:



\- N = 64

\- Re = very high or effectively low viscosity

\- forcing = zero

\- initial condition = phase6d\_like\_multimode

\- short runtime

\- track energy and enstrophy

\- compare drift across dt or N



This should remain a validation test, not a turbulence claim.

