\# Phase 11N fd\_centered Diagnostic Run-Loop Equivalence Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.13-phase11M-fd-centered-diagnostic-run-loop-equivalence-audit

\- Current previous commit: 045bdf7

\- Decision gate file: PHASE11N\_FD\_CENTERED\_DIAGNOSTIC\_RUN\_LOOP\_EQUIVALENCE\_DECISION\_GATE.md



\## Purpose



Phase 11N is a documentation-only decision gate.



The purpose is to summarize Phase 11M and decide whether the selectable diagnostic run-loop is ready for controlled method comparisons.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not replace SpectralSolver.



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



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



\## Phase 11M Audit Summary



Phase 11M compared:



SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic(...)



against:



a direct local transcription of the validated SpectralSolver update loop.



The audit did not call:



SpectralSolver.run()



The audit did not enable:



SelectableAdvectionSolver.run()



The audit used a controlled short run.



\## Phase 11M Parameters



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 20 |

| log\_every | 1 |

| method | fd\_centered |

| initial RMS | 0.01 |

| forcing | inherited baseline deterministic forcing |



\## Phase 11M Global Checks



| Check | Result |

|---|---:|

| SpectralSolver import | PASS |

| SelectableAdvectionSolver import | PASS |

| fd\_centered supported | PASS |

| default method fd\_centered | PASS |

| selectable method fd\_centered | PASS |

| compute\_rhs\_selectable exists | PASS |

| step\_once\_selectable exists | PASS |

| run\_selectable\_diagnostic exists | PASS |

| SelectableAdvectionSolver.run disabled | PASS |

| SpectralSolver file has no git diff | PASS |

| advection\_operators file has no git diff | PASS |

| same grid shape | PASS |

| same dx | PASS |

| same dt | PASS |

| same nu | PASS |

| same dealias mask | PASS |

| same forcing | PASS |

| Global checks | PASS |



\## Phase 11M Equivalence Metrics



| Metric | Value |

|---|---:|

| field\_max\_abs\_diff | 0.000000000000e+00 |

| field\_l2\_diff | 0.000000000000e+00 |

| field\_relative\_l2\_diff | 0.000000000000e+00 |

| energy\_relative\_difference | 0.000000000000e+00 |

| enstrophy\_relative\_difference | 0.000000000000e+00 |

| rms\_relative\_difference | 0.000000000000e+00 |

| spectrum\_relative\_l2\_difference | 0.000000000000e+00 |

| spectrum\_energy\_sum\_relative\_difference | 0.000000000000e+00 |

| baseline\_dominant\_shell | 3.0 |

| selectable\_dominant\_shell | 3.0 |



\## Phase 11M Equivalence Checks



| Check | Result |

|---|---:|

| baseline final finite | PASS |

| selectable final finite | PASS |

| baseline final real | PASS |

| selectable final real | PASS |

| final shapes match | PASS |

| initial\_w unchanged | PASS |

| baseline\_solver.w unchanged | PASS |

| selectable\_solver.w unchanged | PASS |

| field max abs tolerance | PASS |

| field L2 tolerance | PASS |

| field relative L2 tolerance | PASS |

| energy relative tolerance | PASS |

| enstrophy relative tolerance | PASS |

| RMS relative tolerance | PASS |

| spectrum relative L2 tolerance | PASS |

| dominant shell matches | PASS |

| metadata production\_ready false | PASS |

| metadata turbulence false | PASS |

| metadata k\_minus\_3 false | PASS |

| Equivalence checks | PASS |



\## Main Finding



Phase 11M passed.



The selectable diagnostic run-loop reproduced the validated baseline fd\_centered path exactly for the controlled short audit.



The measured differences were zero for:



\- final field

\- kinetic energy

\- enstrophy

\- RMS

\- spectrum

\- spectrum energy sum



The dominant shell also matched:



k = 3.0



\## What Phase 11M Confirms



Phase 11M confirms:



1\. run\_selectable\_diagnostic(...) works for fd\_centered.



2\. The fd\_centered selectable diagnostic path reproduces the validated baseline update logic under the tested controlled conditions.



3\. The selectable diagnostic loop preserves input initial\_w.



4\. The selectable diagnostic loop preserves solver.w.



5\. SelectableAdvectionSolver.run() remains disabled.



6\. SpectralSolver remains unchanged.



7\. advection\_operators remains unchanged.



8\. Metadata guardrails remain present.



9\. No turbulence claim is present.



10\. No k\_minus\_3 claim is present.



\## What Phase 11M Does Not Confirm



Phase 11M does not confirm:



1\. production readiness



2\. long-time stability



3\. turbulence



4\. k^-3 scaling



5\. inertial range behavior



6\. Arakawa superiority



7\. Arakawa production readiness



8\. pseudo\_spectral production readiness



9\. long forced-response behavior



10\. statistical steady state behavior



\## Decision



Decision:



PASS



The selectable diagnostic run-loop has passed fd\_centered equivalence against a direct baseline transcription.



It is now acceptable to use fd\_centered as the internal reference method for controlled selectable-method comparisons.



\## Advancement Approved



Proceed to a design phase for controlled selectable-method comparison.



The next phase should compare, under controlled diagnostic conditions:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The next phase should remain design-only.



\## Advancement Not Approved



This decision gate does not approve:



\- enabling SelectableAdvectionSolver.run()

\- replacing SpectralSolver

\- making Arakawa the default

\- production simulations

\- turbulence experiments

\- k^-3 claims

\- inertial-range claims

\- slope fitting as evidence

\- long-time statistical claims



\## Recommended Next Phase



Phase 11O — Controlled Selectable Method Diagnostic Comparison Design



Purpose:



Design a controlled audit comparing diagnostic run-loop behavior across:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The comparison should use:



run\_selectable\_diagnostic(...)



for each method.



The comparison should include:



\- final field metrics

\- energy

\- enstrophy

\- RMS

\- spectrum

\- dominant shell

\- pairwise field differences

\- pairwise spectrum differences

\- metadata guardrails



The comparison should not claim one method is physically superior.



The comparison should only report controlled numerical differences.



\## Recommended First Comparison Parameters



Recommended first controlled comparison:



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 20 |

| log\_every | 1 |

| initial RMS | 0.01 |

| forcing | inherited baseline deterministic forcing |

| methods | fd\_centered, pseudo\_spectral, arakawa |



Reason:



This keeps the first comparison short, deterministic, and tied to the already-passed Phase 11M setup.



\## Required Guardrails for Phase 11O



Phase 11O must preserve:



\- SpectralSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- fd\_centered default unchanged

\- Arakawa not default

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no inertial-range claim



\## Scientific Boundary



Correct statement after Phase 11N:



The selectable diagnostic run-loop has passed fd\_centered equivalence against a direct baseline transcription for a controlled short run.



Incorrect statement:



The selectable solver is production-ready or proves turbulence or k^-3 scaling.



That statement is not supported.



\## Final Result



Phase 11N decision gate:



PASS



Proceed to Phase 11O controlled selectable method diagnostic comparison design.



Do not replace SpectralSolver.



Do not enable SelectableAdvectionSolver.run().



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.

