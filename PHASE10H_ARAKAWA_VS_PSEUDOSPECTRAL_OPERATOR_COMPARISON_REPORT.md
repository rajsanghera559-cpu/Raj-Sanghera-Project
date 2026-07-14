\# Phase 10H Arakawa vs Pseudo-Spectral Operator Comparison Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.40-phase10G-arakawa-operator-sanity-audit

\- Audit script: phase10h\_arakawa\_vs\_pseudospectral\_operator\_comparison.py

\- Audit output: PHASE10H\_ARAKAWA\_VS\_PSEUDOSPECTRAL\_OPERATOR\_COMPARISON.csv

\- Resolution output: PHASE10H\_ARAKAWA\_RESOLUTION\_SUMMARY.csv



\## Purpose



Phase 10H compares three standalone nonlinear advection operators:



\- finite-difference centered advection

\- pseudo-spectral diagnostic advection

\- Arakawa advection



This phase does not modify SpectralSolver.



This phase does not run a production simulation.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



The purpose is to compare whether the standalone Arakawa operator behaves consistently against the pseudo-spectral diagnostic and whether its resolution behavior is acceptable.



\## Operators Compared



The compared operators were:



| Operator | Function |

|---|---|

| finite-difference centered | advection\_fd\_centered |

| pseudo-spectral diagnostic | advection\_pseudo\_spectral |

| Arakawa | advection\_arakawa |



The pseudo-spectral diagnostic was used as the reference comparison operator.



\## Test Fields



The audit used four controlled fields:



| Field | Classification | Primary Evidence |

|---|---|---:|

| single\_mode\_k2\_2 | near\_null\_reference | false |

| low\_mode\_pair | low\_k\_nonlinear | true |

| phase6d\_like\_multimode | phase6d\_like\_low\_k\_nonlinear | true |

| higher\_smooth\_multimode | higher\_smooth\_nonlinear | true |



The single-mode field is near a nonlinear null case and is retained only as a review reference.



The primary evidence comes from the nonlinear multimode fields.



\## N=64 Results



| Field | FD vs PS Relative Error | Arakawa vs PS Relative Error | Arakawa vs FD Relative Error | Arakawa vs PS Cosine | Arakawa Quality | Result |

|---|---:|---:|---:|---:|---|---:|

| single\_mode\_k2\_2 | 7.580097248347e-01 | 8.202195640192e-01 | 8.094339304566e-01 | 6.781532688405e-01 | NEAR\_NULL\_REVIEW | PASS |

| low\_mode\_pair | 4.522161377788e-02 | 2.965207758581e-02 | 2.642135367812e-02 | 9.999664342065e-01 | BETTER\_THAN\_FD | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 4.333502934896e-02 | 2.188123153403e-02 | 9.999374799356e-01 | COMPARABLE\_TO\_FD | PASS |

| higher\_smooth\_multimode | 1.656847283096e-01 | 1.369979222888e-01 | 1.303783551866e-01 | 9.989997315515e-01 | BETTER\_THAN\_FD | PASS |



\## N=128 Results



| Field | FD vs PS Relative Error | Arakawa vs PS Relative Error | Arakawa vs FD Relative Error | Arakawa vs PS Cosine | Arakawa Quality | Result |

|---|---:|---:|---:|---:|---|---:|

| single\_mode\_k2\_2 | 6.634777425015e-01 | 8.648968498468e-01 | 8.640619992595e-01 | 5.601674765178e-01 | NEAR\_NULL\_REVIEW | PASS |

| low\_mode\_pair | 1.135289606901e-02 | 7.484768129075e-03 | 6.421902434057e-03 | 9.999979273212e-01 | BETTER\_THAN\_FD | PASS |

| phase6d\_like\_multimode | 9.549903183481e-03 | 1.098536655970e-02 | 5.417705588263e-03 | 9.999961647572e-01 | COMPARABLE\_TO\_FD | PASS |

| higher\_smooth\_multimode | 4.222295104408e-02 | 3.587552292981e-02 | 3.048186087720e-02 | 9.999411312435e-01 | BETTER\_THAN\_FD | PASS |



\## Resolution Summary



| Field | FD N64 Error | FD N128 Error | FD Ratio | Arakawa N64 Error | Arakawa N128 Error | Arakawa Ratio | Result |

|---|---:|---:|---:|---:|---:|---:|---:|

| higher\_smooth\_multimode | 1.656847283096e-01 | 4.222295104408e-02 | 2.548391241297e-01 | 1.369979222888e-01 | 3.587552292981e-02 | 2.618691023225e-01 | PASS |

| low\_mode\_pair | 4.522161377788e-02 | 1.135289606901e-02 | 2.510502195868e-01 | 2.965207758581e-02 | 7.484768129075e-03 | 2.524196865267e-01 | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 9.549903183481e-03 | 2.515680821533e-01 | 4.333502934896e-02 | 1.098536655970e-02 | 2.534985374358e-01 | PASS |

| single\_mode\_k2\_2 | 7.580097248347e-01 | 6.634777425015e-01 | 8.752892222408e-01 | 8.202195640192e-01 | 8.648968498468e-01 | 1.054469909994e+00 | PASS |



\## Main Findings



The primary nonlinear fields passed.



The Arakawa operator showed positive sign alignment with the pseudo-spectral diagnostic.



For the low\_mode\_pair field, Arakawa was better than finite-difference at both N=64 and N=128.



For the higher\_smooth\_multimode field, Arakawa was better than finite-difference at both N=64 and N=128.



For the phase6d\_like\_multimode field, Arakawa was comparable to finite-difference.



The resolution behavior passed for all primary fields.



The Arakawa error ratios from N=64 to N=128 were approximately one quarter for the primary fields.



This is consistent with expected second-order-like behavior on these controlled fields.



\## Near-Null Single-Mode Interpretation



The single-mode field is not primary evidence.



Its nonlinear advection norms are near machine precision.



The single-mode field was retained as a review reference and did not determine the overall result.



\## Overall Result



| Check | Result |

|---|---:|

| Primary operator cases pass | PASS |

| Primary resolution behavior pass | PASS |

| Near-null reference retained | PASS |

| Phase 10H Arakawa comparison audit | PASS |



\## What This Confirms



Phase 10H confirms:



\- the standalone Arakawa operator compares well against the pseudo-spectral diagnostic on controlled nonlinear fields

\- the Arakawa sign convention is correct for the project

\- Arakawa is better than finite-difference on two primary nonlinear fields

\- Arakawa is comparable on the Phase 6D-like multimode field

\- Arakawa resolution behavior is acceptable from N=64 to N=128

\- SpectralSolver remains unchanged



\## What This Does Not Confirm



Phase 10H does not replace the production solver.



Phase 10H does not validate Arakawa time evolution.



Phase 10H does not prove long-time nonlinear stability.



Phase 10H does not prove turbulence.



Phase 10H does not prove k^-3 scaling.



Phase 10H does not prove a resolved inertial-range cascade.



\## Scientific Interpretation



The standalone Arakawa operator is now credible enough for the next validation stage.



It should still not be inserted into the production solver yet.



The next step should be a decision gate that decides whether to create a selectable-advection solver variant.



\## Recommended Next Step



Phase 10I — Arakawa Operator Decision Gate



Purpose:



Summarize Phases 10E through 10H and decide whether to proceed to a selectable-advection solver variant.



Recommended decision:



Proceed to a separate solver variant only after preserving SpectralSolver as the baseline.



Do not replace SpectralSolver.



Do not run turbulence experiments yet.

