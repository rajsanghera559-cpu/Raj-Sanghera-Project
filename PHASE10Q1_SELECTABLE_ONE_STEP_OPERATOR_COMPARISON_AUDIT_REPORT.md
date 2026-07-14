\# Phase 10Q.1 Selectable One-Step Operator Comparison Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.53-phase10Q-selectable-one-step-operator-comparison-design

\- Audit script: phase10q1\_selectable\_one\_step\_operator\_comparison\_audit.py

\- Method output CSV: PHASE10Q1\_SELECTABLE\_ONE\_STEP\_OPERATOR\_COMPARISON\_AUDIT.csv

\- Pairwise summary CSV: PHASE10Q1\_SELECTABLE\_ONE\_STEP\_PAIRWISE\_SUMMARY.csv

\- Report: PHASE10Q1\_SELECTABLE\_ONE\_STEP\_OPERATOR\_COMPARISON\_AUDIT\_REPORT.md



\## Purpose



Phase 10Q.1 compares one-step selectable outputs across three advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The comparison uses:



step\_once\_selectable(w)



This phase does not modify SpectralSolver.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not run a production simulation.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Global Checks



| Check | Result |

|---|---:|

| SpectralSolver import | PASS |

| SelectableAdvectionSolver import | PASS |

| Supported methods check | PASS |

| Default method fd\_centered | PASS |

| compute\_rhs\_selectable exists | PASS |

| step\_once\_selectable exists | PASS |

| SpectralSolver file has no git diff | PASS |

| SelectableAdvectionSolver file has no git diff | PASS |

| Invalid method rejected | PASS |

| Global checks | PASS |



\## Methods Compared



| Method | Role |

|---|---|

| fd\_centered | Validated baseline-compatible method |

| pseudo\_spectral | Diagnostic spectral-advection comparison method |

| arakawa | Candidate conservative advection method |



\## Test Fields



| Field | Classification | Primary Evidence |

|---|---|---:|

| single\_mode\_k2\_2 | controlled\_single\_mode\_reference | false |

| low\_mode\_pair | low\_k\_nonlinear | true |

| phase6d\_like\_multimode | phase6d\_like\_low\_k\_nonlinear | true |

| higher\_smooth\_multimode | higher\_smooth\_nonlinear | true |



The single-mode case is retained as a reference case.



The primary evidence comes from the nonlinear multimode fields.



\## Tested Resolutions



The audit tested:



\- N=64

\- N=128



Parameters:



\- Re=1000

\- dt=0.005

\- steps=1



\## Method Output Checks



Every method output passed:



\- finite\_output

\- real\_output

\- input\_w\_unchanged

\- solver\_w\_unchanged

\- run\_disabled

\- metadata\_method\_ok

\- metadata\_no\_turbulence\_claim

\- metadata\_no\_k\_minus\_3\_claim

\- overall\_result



\## Pairwise Comparisons



The audit compared:



| Pair | Purpose |

|---|---|

| pseudo\_spectral vs fd\_centered | spectral diagnostic compared with baseline-compatible method |

| arakawa vs fd\_centered | Arakawa compared with baseline-compatible method |

| arakawa vs pseudo\_spectral | Arakawa compared with spectral diagnostic method |



Each pair reported:



\- diff\_l2

\- diff\_max\_abs

\- relative error

\- cosine similarity

\- energy absolute difference

\- enstrophy absolute difference

\- positive alignment

\- no large pairwise disagreement

\- pairwise result



\## N=64 Summary



\### single\_mode\_k2\_2



All three methods produced matching one-step outputs to near machine precision.



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 8.736311147655e-22 | 1.000000000000e+00 | PASS |

| arakawa vs fd\_centered | 8.512482154882e-22 | 1.000000000000e+00 | PASS |

| arakawa vs pseudo\_spectral | 8.697739825711e-22 | 1.000000000000e+00 | PASS |



\### low\_mode\_pair



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.071612900835e-07 | 1.000000000000e+00 | PASS |

| arakawa vs fd\_centered | 6.011276191827e-08 | 1.000000000000e+00 | PASS |

| arakawa vs pseudo\_spectral | 7.027262764158e-08 | 1.000000000000e+00 | PASS |



\### phase6d\_like\_multimode



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 4.633530193661e-07 | 9.999999999999e-01 | PASS |

| arakawa vs fd\_centered | 2.577781574018e-07 | 1.000000000000e+00 | PASS |

| arakawa vs pseudo\_spectral | 5.289137668739e-07 | 9.999999999999e-01 | PASS |



\### higher\_smooth\_multimode



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.064497163957e-06 | 9.999999999994e-01 | PASS |

| arakawa vs fd\_centered | 7.381494199098e-07 | 9.999999999997e-01 | PASS |

| arakawa vs pseudo\_spectral | 8.801396155261e-07 | 9.999999999996e-01 | PASS |



\## N=128 Summary



\### single\_mode\_k2\_2



All three methods produced matching one-step outputs to near machine precision.



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.968134015439e-17 | 1.000000000000e+00 | PASS |

| arakawa vs fd\_centered | 1.801263747284e-17 | 1.000000000000e+00 | PASS |

| arakawa vs pseudo\_spectral | 2.054780922955e-17 | 1.000000000000e+00 | PASS |



\### low\_mode\_pair



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 2.690286860513e-08 | 1.000000000000e+00 | PASS |

| arakawa vs fd\_centered | 1.506242717030e-08 | 1.000000000000e+00 | PASS |

| arakawa vs pseudo\_spectral | 1.773819328444e-08 | 1.000000000000e+00 | PASS |



\### phase6d\_like\_multimode



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 1.165647785778e-07 | 1.000000000000e+00 | PASS |

| arakawa vs fd\_centered | 6.553066654304e-08 | 1.000000000000e+00 | PASS |

| arakawa vs pseudo\_spectral | 1.340786974055e-07 | 1.000000000000e+00 | PASS |



\### higher\_smooth\_multimode



| Pair | Relative Error | Cosine | Result |

|---|---:|---:|---:|

| pseudo\_spectral vs fd\_centered | 2.712754995494e-07 | 1.000000000000e+00 | PASS |

| arakawa vs fd\_centered | 1.896580825105e-07 | 1.000000000000e+00 | PASS |

| arakawa vs pseudo\_spectral | 2.304806455840e-07 | 1.000000000000e+00 | PASS |



\## Overall Result



| Check | Result |

|---|---:|

| Method output checks pass | PASS |

| Primary pairwise comparisons pass | PASS |

| Near-null/reference case retained | PASS |

| Phase 10Q.1 selectable one-step operator comparison audit | PASS |



\## Main Finding



The selectable one-step outputs for fd\_centered, pseudo\_spectral, and arakawa were finite, real, non-mutating, and positively aligned.



The primary nonlinear-field pairwise comparisons all passed.



Arakawa remained closely aligned with both fd\_centered and pseudo\_spectral in one-step output comparisons.



\## What This Confirms



Phase 10Q.1 confirms:



\- fd\_centered, pseudo\_spectral, and arakawa all produce valid one-step selectable outputs

\- outputs are finite and real

\- input fields are not mutated

\- solver.w is not mutated

\- run() remains disabled

\- metadata guardrails remain present

\- primary pairwise comparisons pass

\- near-null/reference case is retained but does not drive the main conclusion

\- SpectralSolver remains unchanged



\## What This Does Not Confirm



Phase 10Q.1 does not validate long-time stability.



Phase 10Q.1 does not enable SelectableAdvectionSolver.run().



Phase 10Q.1 does not validate production simulations.



Phase 10Q.1 does not prove turbulence.



Phase 10Q.1 does not prove k^-3 scaling.



Phase 10Q.1 does not prove a resolved inertial-range cascade.



Phase 10Q.1 does not prove Arakawa is production-ready.



\## Recommended Next Phase



Phase 10R — Short No-Forcing Drift Design



Purpose:



Design a short controlled no-forcing drift comparison using step\_once\_selectable repeatedly in an audit script.



Methods to compare:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Recommended guardrails:



\- do not enable run()

\- do not replace SpectralSolver

\- do not run long simulations

\- do not claim turbulence

\- do not claim k^-3 scaling

\- keep the drift test short and diagnostic



\## Final Result



Phase 10Q.1 selectable one-step operator comparison audit:



PASS



Proceed to Phase 10R design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make turbulence claims.



Do not make k^-3 claims.

