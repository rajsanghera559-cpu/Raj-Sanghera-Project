\# Phase 10G Arakawa Operator Sanity Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.39-phase10F-standalone-arakawa-operator

\- Implementation file: project/solver/advection\_operators.py

\- Audit script: phase10g\_arakawa\_operator\_sanity\_audit.py

\- Audit output: PHASE10G\_ARAKAWA\_OPERATOR\_SANITY\_AUDIT.csv



\## Purpose



Phase 10G audits the standalone Arakawa operator implementation added in Phase 10F.



This phase does not modify SpectralSolver.



This phase does not run a production simulation.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



The purpose is to verify that the standalone Arakawa operator:



\- imports correctly

\- returns finite real arrays

\- does not mutate input fields

\- does not mutate solver.w

\- preserves the project sign convention

\- aligns positively with the pseudo-spectral advection diagnostic on controlled nonlinear fields



\## Project Sign Convention



The project uses:



u = d psi / dy



v = - d psi / dx



adv = u \* omega\_x + v \* omega\_y



The solver update uses:



d omega / dt = -adv + diffusion + forcing



The Arakawa implementation computes a standard Jacobian:



J(psi, omega) = psi\_x \* omega\_y - psi\_y \* omega\_x



Because:



adv = u \* omega\_x + v \* omega\_y



and:



u = psi\_y

v = -psi\_x



then:



adv = psi\_y \* omega\_x - psi\_x \* omega\_y



Therefore:



adv = -J(psi, omega)



The standalone function advection\_arakawa returns:



\-J\_arakawa



This sign convention was tested by checking positive cosine similarity against the pseudo-spectral advection diagnostic.



\## Test Fields



The audit used four controlled vorticity fields:



| Field | Classification | Primary Evidence |

|---|---|---:|

| single\_mode\_k2\_2 | near\_null\_reference | false |

| low\_mode\_pair | low\_k\_nonlinear | true |

| phase6d\_like\_multimode | phase6d\_like\_low\_k\_nonlinear | true |

| higher\_smooth\_multimode | higher\_smooth\_nonlinear | true |



The single-mode case is a near-null nonlinear reference and is not primary evidence.



The primary evidence comes from the nonlinear multimode fields.



\## Required Checks



Each case checked:



\- finite arrays

\- real-valued output

\- input w unchanged

\- input psi unchanged

\- solver.w unchanged

\- Arakawa advection norm

\- pseudo-spectral advection norm

\- finite-difference advection norm

\- Arakawa vs pseudo-spectral relative error

\- Arakawa vs pseudo-spectral cosine similarity

\- Arakawa vs finite-difference cosine similarity

\- sign matches pseudo-spectral

\- sign is not flipped



\## N=64 Results



| Field | Arakawa L2 | Pseudo-Spectral L2 | Arakawa vs Pseudo-Spectral Relative Error | Arakawa vs Pseudo-Spectral Cosine | Sign Check | Result |

|---|---:|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 1.345522684856e-20 | 4.285935878258e-20 | 8.202195640192e-01 | 6.781532688405e-01 | PASS | PASS |

| low\_mode\_pair | 2.880050698904e-06 | 2.964635306408e-06 | 2.965207758581e-02 | 9.999664342065e-01 | PASS | PASS |

| phase6d\_like\_multimode | 2.339798552349e-05 | 2.442200079635e-05 | 4.333502934896e-02 | 9.999374799356e-01 | PASS | PASS |

| higher\_smooth\_multimode | 1.117528641234e-05 | 1.285246991290e-05 | 1.369979222888e-01 | 9.989997315515e-01 | PASS | PASS |



\## N=128 Results



| Field | Arakawa L2 | Pseudo-Spectral L2 | Arakawa vs Pseudo-Spectral Relative Error | Arakawa vs Pseudo-Spectral Cosine | Sign Check | Result |

|---|---:|---:|---:|---:|---:|---:|

| single\_mode\_k2\_2 | 2.742345987433e-20 | 8.803602144451e-20 | 8.648968498468e-01 | 5.601674765178e-01 | PASS | PASS |

| low\_mode\_pair | 2.943276294728e-06 | 2.964635306408e-06 | 7.484768129075e-03 | 9.999979273212e-01 | PASS | PASS |

| phase6d\_like\_multimode | 2.416228873414e-05 | 2.442200079635e-05 | 1.098536655970e-02 | 9.999961647572e-01 | PASS | PASS |

| higher\_smooth\_multimode | 1.241221913510e-05 | 1.285246991290e-05 | 3.587552292981e-02 | 9.999411312435e-01 | PASS | PASS |



\## Sign Convention Result



The primary nonlinear fields all had positive cosine similarity with pseudo-spectral advection.



The cosine similarities were very close to 1 for the primary fields.



This means the Arakawa implementation is not sign-flipped relative to the project pseudo-spectral advection convention.



\## Non-Mutation Result



The audit confirmed:



| Check | Result |

|---|---:|

| input w unchanged | PASS |

| input psi unchanged | PASS |

| solver.w unchanged | PASS |



The standalone Arakawa operator does not mutate the solver state.



\## Near-Null Single-Mode Interpretation



The single-mode case is close to a nonlinear null case.



The operator norms are near machine precision.



Therefore, the relative errors for this case are not primary evidence.



The single-mode case is retained as a review reference, not as a basis for accepting or rejecting the operator.



\## Main Findings



The standalone Arakawa operator:



\- imports correctly

\- returns finite real arrays

\- preserves input arrays

\- preserves solver state

\- has the expected sign relative to pseudo-spectral advection

\- passes the primary nonlinear field tests at N=64 and N=128



\## Overall Result



Phase 10G Arakawa operator sanity audit: PASS



\## What This Confirms



Phase 10G confirms that the standalone Arakawa operator is ready for deeper comparison audits.



The implementation is suitable for diagnostic comparison work.



The implementation should not yet replace the production solver.



\## What This Does Not Confirm



Phase 10G does not validate long-time Arakawa time evolution.



Phase 10G does not implement a selectable-advection solver.



Phase 10G does not modify SpectralSolver.



Phase 10G does not prove turbulence.



Phase 10G does not prove k^-3 scaling.



Phase 10G does not prove a resolved inertial-range cascade.



\## Recommended Next Step



Phase 10H — Arakawa vs Pseudo-Spectral Operator Comparison



Purpose:



Compare Arakawa, finite-difference, and pseudo-spectral advection operators across controlled fields and resolutions.



The comparison should measure:



\- Arakawa vs pseudo-spectral relative error

\- finite-difference vs pseudo-spectral relative error

\- Arakawa vs finite-difference relative error

\- cosine similarities

\- resolution behavior from N=64 to N=128

\- whether Arakawa improves, matches, or worsens operator agreement on controlled nonlinear fields



\## Conclusion



Phase 10G passes as a standalone Arakawa operator sanity audit.



The next step should remain diagnostic.



Do not replace the production solver yet.

