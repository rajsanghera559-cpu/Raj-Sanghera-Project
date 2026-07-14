\# Phase 10D Advection Operator Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.36-phase10C1-advection-operator-scaffold-audit

\- Scaffold file: project/solver/advection\_operators.py

\- Audit script: phase10d\_advection\_operator\_comparison\_audit.py

\- Audit output: PHASE10D\_ADVECTION\_OPERATOR\_COMPARISON\_AUDIT.csv

\- Resolution comparison output: PHASE10D\_ADVECTION\_OPERATOR\_RESOLUTION\_COMPARISON.csv



\## Purpose



Phase 10D performs a formal comparison between the finite-difference advection operator and the pseudo-spectral advection diagnostic operator.



This phase does not modify SpectralSolver.



This phase does not implement Arakawa.



This phase does not run a production simulation.



This phase does not prove turbulence or k^-3 scaling.



The goal is to use the new Phase 10C advection operator scaffold to quantify finite-difference versus pseudo-spectral advection behavior across controlled fields and resolutions.



\## Operators Compared



The comparison used:



\- advection\_fd\_centered

\- advection\_pseudo\_spectral

\- compare\_advection\_operators



The finite-difference operator is the current baseline method.



The pseudo-spectral operator is a diagnostic comparison method.



Both operators follow the project convention:



adv = u \* omega\_x + v \* omega\_y



The solver update uses:



d omega / dt = -adv + diffusion + forcing



\## Test Fields



The audit used four controlled vorticity fields:



| Field | Classification | Primary Evidence |

|---|---|---:|

| single\_mode\_k2\_2 | near\_null\_reference | false |

| low\_mode\_pair | low\_k\_nonlinear | true |

| phase6d\_like\_multimode | phase6d\_like\_low\_k\_nonlinear | true |

| higher\_smooth\_multimode | higher\_smooth\_nonlinear | true |



The single-mode case is a near-null nonlinear reference.



It is not primary evidence because both finite-difference and pseudo-spectral nonlinear advection norms are near machine precision.



The primary evidence comes from the nonlinear multimode fields.



\## Product Dealiasing Conditions



The audit evaluated pseudo-spectral product dealiasing under two settings:



| Setting | Meaning |

|---|---|

| dealias\_pseudo\_spectral\_product = false | raw pseudo-spectral product diagnostic |

| dealias\_pseudo\_spectral\_product = true | pseudo-spectral product masked after nonlinear product |



For the primary nonlinear fields, both settings produced passing resolution behavior.



\## N=64 Results Without Pseudo-Spectral Product Dealiasing



| Field | Relative Error vs Pseudo-Spectral | Cosine Similarity | Primary Field Quality |

|---|---:|---:|---:|

| single\_mode\_k2\_2 | 7.580097248347e-01 | 6.539024468067e-01 | PASS |

| low\_mode\_pair | 4.522161377788e-02 | 9.997555383637e-01 | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 9.998704816527e-01 | PASS |

| higher\_smooth\_multimode | 1.656847283096e-01 | 9.924337813208e-01 | PASS |



\## N=128 Results Without Pseudo-Spectral Product Dealiasing



| Field | Relative Error vs Pseudo-Spectral | Cosine Similarity | Primary Field Quality |

|---|---:|---:|---:|

| single\_mode\_k2\_2 | 6.634777425015e-01 | 7.512768089114e-01 | PASS |

| low\_mode\_pair | 1.135289606901e-02 | 9.999855209012e-01 | PASS |

| phase6d\_like\_multimode | 9.549903183481e-03 | 9.999922202941e-01 | PASS |

| higher\_smooth\_multimode | 4.222295104408e-02 | 9.995947891750e-01 | PASS |



\## N=64 Results With Pseudo-Spectral Product Dealiasing



| Field | Relative Error vs Pseudo-Spectral | Cosine Similarity | Primary Field Quality |

|---|---:|---:|---:|

| single\_mode\_k2\_2 | 9.549830085060e-01 | 5.559030048221e-01 | PASS |

| low\_mode\_pair | 4.522161377788e-02 | 9.997555383637e-01 | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 9.998704816527e-01 | PASS |

| higher\_smooth\_multimode | 1.656847283096e-01 | 9.924337813208e-01 | PASS |



\## N=128 Results With Pseudo-Spectral Product Dealiasing



| Field | Relative Error vs Pseudo-Spectral | Cosine Similarity | Primary Field Quality |

|---|---:|---:|---:|

| single\_mode\_k2\_2 | 1.277644867717e+00 | 4.457851199395e-01 | PASS |

| low\_mode\_pair | 1.135289606901e-02 | 9.999855209012e-01 | PASS |

| phase6d\_like\_multimode | 9.549903183482e-03 | 9.999922202941e-01 | PASS |

| higher\_smooth\_multimode | 4.222295104408e-02 | 9.995947891750e-01 | PASS |



\## Resolution Comparison Without Pseudo-Spectral Product Dealiasing



| Field | N64 Relative Error | N128 Relative Error | N128/N64 Error Ratio | Improved at N128 | Second-Order Window | Result |

|---|---:|---:|---:|---:|---:|---:|

| low\_mode\_pair | 4.522161377788e-02 | 1.135289606901e-02 | 2.510502195868e-01 | PASS | PASS | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 9.549903183481e-03 | 2.515680821533e-01 | PASS | PASS | PASS |

| higher\_smooth\_multimode | 1.656847283096e-01 | 4.222295104408e-02 | 2.548391241297e-01 | PASS | PASS | PASS |

| single\_mode\_k2\_2 | 7.580097248347e-01 | 6.634777425015e-01 | 8.752892222408e-01 | PASS | FAIL | PASS |



\## Resolution Comparison With Pseudo-Spectral Product Dealiasing



| Field | N64 Relative Error | N128 Relative Error | N128/N64 Error Ratio | Improved at N128 | Second-Order Window | Result |

|---|---:|---:|---:|---:|---:|---:|

| low\_mode\_pair | 4.522161377788e-02 | 1.135289606901e-02 | 2.510502195868e-01 | PASS | PASS | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 9.549903183482e-03 | 2.515680821533e-01 | PASS | PASS | PASS |

| higher\_smooth\_multimode | 1.656847283096e-01 | 4.222295104408e-02 | 2.548391241297e-01 | PASS | PASS | PASS |

| single\_mode\_k2\_2 | 9.549830085060e-01 | 1.277644867717e+00 | 1.337871832627e+00 | FAIL | FAIL | FAIL |



\## Important Interpretation of Single-Mode Result



The single-mode case is close to a nonlinear null case.



The pseudo-spectral and finite-difference nonlinear advection norms are near machine precision.



Because the denominator is extremely small, relative error and cosine similarity are not reliable physical indicators for the single-mode case.



The single-mode case was retained as a review reference, not as primary evidence.



The single-mode dealiased comparison produced a FAIL in the resolution comparison, but this did not affect the overall audit because it was not primary evidence.



\## Primary Nonlinear Evidence



The primary nonlinear fields all passed:



| Field | Evidence |

|---|---|

| low\_mode\_pair | low-k nonlinear test passed with approximately 4x error reduction |

| phase6d\_like\_multimode | Phase 6D-like nonlinear field passed with approximately 4x error reduction |

| higher\_smooth\_multimode | higher smooth nonlinear field passed with approximately 4x error reduction |



For the primary nonlinear fields, the N128/N64 error ratios were approximately:



| Field | Error Ratio |

|---|---:|

| low\_mode\_pair | 0.251 |

| phase6d\_like\_multimode | 0.252 |

| higher\_smooth\_multimode | 0.255 |



This is consistent with second-order centered finite-difference behavior.



\## Overall Result



| Check | Result |

|---|---:|

| Primary field quality | PASS |

| Primary field resolution behavior | PASS |

| Single-mode near-null case retained as review reference | PASS |

| Phase 10D advection operator comparison audit | PASS |



\## What This Confirms



Phase 10D confirms:



\- finite-difference advection agrees closely with pseudo-spectral advection on low-k nonlinear fields

\- finite-difference advection error decreases strongly when resolution is doubled

\- the observed error reduction is consistent with second-order centered finite-difference behavior

\- the Phase 10C scaffold is useful for formal operator comparisons

\- the single-mode near-null case must be interpreted cautiously



\## What This Does Not Confirm



Phase 10D does not implement Arakawa.



Phase 10D does not replace the production solver.



Phase 10D does not prove long-time nonlinear stability.



Phase 10D does not prove turbulence.



Phase 10D does not prove k^-3 scaling.



Phase 10D does not create a fully spectral Navier-Stokes solver.



\## Scientific Interpretation



The current finite-difference advection operator continues to behave reasonably on controlled nonlinear diagnostic fields.



For primary nonlinear fields, the finite-difference-to-pseudo-spectral discrepancy decreases by approximately a factor of four when resolution doubles from N=64 to N=128.



This supports the current solver as a controlled exploratory baseline.



It does not remove the need for an Arakawa or fully spectral upgrade before stronger turbulence claims.



\## Recommended Next Step



Phase 10E — Arakawa Operator Planning and Sign-Convention Audit



Purpose:



Before implementing Arakawa, document the exact Jacobian sign convention, discrete formula, periodic indexing, and acceptance tests.



The next step should not be a production solver change.



The next step should be a careful Arakawa design and sign audit.

