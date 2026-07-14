\# Phase 12N Controlled Three-Resolution Comparison Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.39-phase12M-N256-full-final-time-1-0-feasibility-decision-gate

\- Current previous commit: 32f27a5

\- Design file: PHASE12N\_CONTROLLED\_THREE\_RESOLUTION\_COMPARISON\_DESIGN.md



\## Purpose



Phase 12N is a design-only phase.



The purpose is to design a controlled three-resolution comparison using already completed diagnostic outputs:



\- N64 from Phase 11S

\- N128 from Phase 11V

\- N256 from Phase 12L



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



\## Why Phase 12N Is Needed



The project has completed controlled selectable diagnostic feasibility/comparison runs at:



\- N64, final time 1.0

\- N128, final time 1.0

\- N256, final time 1.0



The next step is to compare those completed outputs in one structured audit.



This comparison may compute resolution-trend metrics.



This comparison may compute observed-order-style diagnostic quantities if finite and well-defined.



This comparison must not automatically claim convergence.



A convergence claim requires careful interpretation and a decision gate after the audit.



\## Completed Input Phases



| Resolution | Phase | Status |

|---:|---|---:|

| N64 | Phase 11S | PASS |

| N128 | Phase 11V | PASS |

| N256 | Phase 12L | PASS |



\## Recommended Next Audit



Recommended next phase:



Phase 12O — Controlled Three-Resolution Comparison Audit



Purpose:



Use existing N64, N128, and N256 outputs to compute structured three-resolution comparison metrics.



Phase 12O should not run new simulations.



Phase 12O should not modify source code.



Phase 12O should not claim convergence automatically.



\## Required Phase 12O Inputs



\### N64 Inputs



\- PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- PHASE11S\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv



\### N128 Inputs



\- PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_AUDIT.csv

\- PHASE11V\_N128\_LONGER\_CONTROLLED\_SELECTABLE\_METHOD\_DIAGNOSTIC\_COMPARISON\_PAIRWISE.csv



\### N256 Inputs



\- PHASE12L\_N256\_FULL\_FINAL\_TIME\_1\_0\_FEASIBILITY\_AUDIT.csv

\- PHASE12L\_N256\_FULL\_FINAL\_TIME\_1\_0\_FEASIBILITY\_PAIRWISE.csv



\## Optional Final-State Inputs



If final-state files exist, Phase 12O should also use them for grid-restricted field comparisons.



\### N64 Final States



\- experiments/selectable\_diagnostics/phase11S\_fd\_centered/selectable\_final\_state.npy

\- experiments/selectable\_diagnostics/phase11S\_pseudo\_spectral/selectable\_final\_state.npy

\- experiments/selectable\_diagnostics/phase11S\_arakawa/selectable\_final\_state.npy



\### N128 Final States



\- experiments/selectable\_diagnostics/phase11V\_N128\_fd\_centered/selectable\_final\_state.npy

\- experiments/selectable\_diagnostics/phase11V\_N128\_pseudo\_spectral/selectable\_final\_state.npy

\- experiments/selectable\_diagnostics/phase11V\_N128\_arakawa/selectable\_final\_state.npy



\### N256 Final States



\- experiments/selectable\_diagnostics/phase12L\_N256\_fd\_centered/selectable\_final\_state.npy

\- experiments/selectable\_diagnostics/phase12L\_N256\_pseudo\_spectral/selectable\_final\_state.npy

\- experiments/selectable\_diagnostics/phase12L\_N256\_arakawa/selectable\_final\_state.npy



If these files are missing, Phase 12O should still complete the CSV-based comparison and mark field-restriction comparisons as not available.



\## Required Phase 12O Outputs



The next audit should write:



| File | Purpose |

|---|---|

| phase12o\_controlled\_three\_resolution\_comparison\_audit.py | audit script |

| PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_METHOD\_SUMMARY.csv | method-level three-resolution summary |

| PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_PAIRWISE\_TRENDS.csv | pairwise method-difference trends |

| PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_FIELD\_RESTRICTION.csv | optional grid-restricted field comparisons |

| PHASE12O\_CONTROLLED\_THREE\_RESOLUTION\_COMPARISON\_AUDIT\_REPORT.md | audit report |



\## Required Global Checks



The Phase 12O audit should check:



1\. required N64 method CSV exists



2\. required N64 pairwise CSV exists



3\. required N128 method CSV exists



4\. required N128 pairwise CSV exists



5\. required N256 method CSV exists



6\. required N256 pairwise CSV exists



7\. all required CSV files contain expected columns



8\. N64 method results are PASS



9\. N128 method results are PASS



10\. N256 method results are PASS



11\. N64 pairwise results are PASS



12\. N128 pairwise results are PASS



13\. N256 pairwise results are PASS



14\. methods present are exactly:



&#x20;  - fd\_centered

&#x20;  - pseudo\_spectral

&#x20;  - arakawa



15\. method pairs present are exactly:



&#x20;  - pseudo\_spectral vs fd\_centered

&#x20;  - arakawa vs fd\_centered

&#x20;  - arakawa vs pseudo\_spectral



16\. SpectralSolver file has no git diff



17\. advection\_operators file has no git diff



18\. selectable\_advection\_solver file has no git diff



19\. no new simulation is run



20\. no unsupported claim is made



\## Required Method-Level Metrics



For each method and each resolution, Phase 12O should collect:



\- final RMS

\- final kinetic energy

\- final enstrophy

\- RMS ratio

\- energy ratio

\- enstrophy ratio

\- dominant shell

\- low-k fraction for k <= 4

\- high-k fraction for k >= 10

\- spectrum direct relative error

\- method result



Methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Resolutions:



\- N64

\- N128

\- N256



\## Required Pairwise Metrics



For each pair and each resolution, Phase 12O should collect:



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



\## Required Resolution Trend Metrics



For each pairwise metric, compute:



\- N64 value

\- N128 value

\- N256 value

\- N64\_over\_N128 reduction ratio

\- N128\_over\_N256 reduction ratio

\- monotone decrease flag

\- finite flag



Recommended metrics:



\- field relative L2 difference

\- spectrum relative L2 difference

\- energy relative difference

\- enstrophy relative difference

\- RMS relative difference



\## Optional Observed-Order Diagnostic



If the N64/N128 and N128/N256 reduction ratios are finite and positive, compute:



observed\_order\_64\_128\_256 = log(N64\_metric / N128\_metric) / log(2)



and:



observed\_order\_128\_256 = log(N128\_metric / N256\_metric) / log(2)



Important:



These are observed diagnostic order estimates.



They are not a proof of convergence.



They should be reported only if finite and positive.



They should be labeled as observed diagnostic trends.



\## Optional Field-Restriction Comparison



If final-state files exist, Phase 12O should compute field restriction comparisons.



For N128 to N64:



N128\_restricted\_to\_N64 = N128\_field\[::2, ::2]



Compare:



N64\_field



against:



N128\_restricted\_to\_N64



For N256 to N128:



N256\_restricted\_to\_N128 = N256\_field\[::2, ::2]



Compare:



N128\_field



against:



N256\_restricted\_to\_N128



For each method, compute:



\- field max absolute difference

\- field RMS difference

\- field relative RMS difference

\- finite check

\- real check



This is an aligned-grid restriction comparison.



This is not a full spectral projection convergence proof.



\## Optional Field-Restriction Observed Order



If both field restriction errors are finite and positive, compute:



observed\_order\_restricted\_field = log(error\_N64\_N128 / error\_N128\_N256) / log(2)



This value may be reported as an observed restriction-order diagnostic.



It must not be called a proof of convergence.



\## Required Scientific Boundary



Phase 12O must clearly state:



Correct statement:



The project completed controlled N64, N128, and N256 diagnostic comparisons and computed structured three-resolution trend metrics.



Incorrect statement:



The project has proven convergence, turbulence, k^-3 scaling, inertial-range behavior, or method superiority.



Those statements are not supported unless a later decision gate explicitly approves a narrower claim.



\## Pass/Fail Philosophy



Phase 12O should pass if:



1\. required CSV files exist



2\. required columns exist



3\. all source audits passed



4\. method-level metrics are finite



5\. pairwise trend metrics are finite



6\. optional field-restriction metrics are either finite or clearly marked unavailable



7\. source code files remain unchanged



8\. no new simulations are run



9\. no unsupported claims are made



\## What a Phase 12O PASS Would Confirm



A PASS would confirm:



\- three completed resolution outputs can be compared in one structured audit

\- method-level metrics are available at N64, N128, and N256

\- pairwise method-difference trends are available at N64, N128, and N256

\- optional field-restriction comparisons are available if final state files exist

\- diagnostic resolution trends can be reported

\- metadata guardrails remain respected

\- no unsupported scientific claim is needed



\## What a Phase 12O PASS Would Not Confirm



A PASS would not confirm:



\- convergence proof

\- convergence order proof

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- method superiority

\- production readiness

\- physical cascade behavior

\- statistical steady state behavior



\## Recommended Phase 12P



After Phase 12O, the next phase should be:



Phase 12P — Controlled Three-Resolution Comparison Decision Gate



Purpose:



Document the Phase 12O results and decide what claims, if any, are supported.



Phase 12P may decide among:



1\. resolution-consistency only



2\. observed convergence-trend language



3\. no convergence claim



4\. request an additional run or alternate norm



5\. archive Phase 12 as feasibility and diagnostic infrastructure only



Phase 12P should be conservative.



Do not approve a convergence claim unless the Phase 12O data strongly supports it and the wording is narrow.



\## Recommended Claim Language If Trends Are Strong



Potential cautious language:



The controlled three-resolution comparison showed decreasing diagnostic differences under grid refinement for the tested setup.



This is acceptable if the data supports it.



Avoid this stronger language unless justified:



The solver converges at second order.



That statement requires stricter evidence and should not be used casually.



\## Guardrails



Phase 12O must preserve:



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

\- no method superiority claim

\- no broad convergence claim



\## Scientific Boundary



Correct statement after Phase 12N:



A controlled three-resolution comparison audit has been designed using already completed N64, N128, and N256 diagnostic outputs.



Incorrect statement:



The project has proven convergence, turbulence, k^-3 scaling, inertial-range behavior, method superiority, production readiness, or physical cascade behavior.



Those statements are not supported.



\## Decision



Phase 12N decision:



PROCEED TO PHASE 12O CONTROLLED THREE-RESOLUTION COMPARISON AUDIT.



Do not run new simulations.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



Do not make method superiority claims.



Do not make broad convergence claims.



\## Final Result



Phase 12N controlled three-resolution comparison design:



PASS



Next phase:



Phase 12O — Controlled Three-Resolution Comparison Audit

