\# Phase 11M fd\_centered Diagnostic Run-Loop Equivalence Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.5.12-phase11L-fd-centered-diagnostic-run-loop-equivalence-design

\- Audit script: phase11m\_fd\_centered\_diagnostic\_run\_loop\_equivalence\_audit.py

\- Audit output: PHASE11M\_FD\_CENTERED\_DIAGNOSTIC\_RUN\_LOOP\_EQUIVALENCE\_AUDIT.csv

\- Report: PHASE11M\_FD\_CENTERED\_DIAGNOSTIC\_RUN\_LOOP\_EQUIVALENCE\_AUDIT\_REPORT.md



\## Purpose



Phase 11M audits whether the selectable diagnostic run-loop reproduces the validated baseline solver path when using:



advection\_method = "fd\_centered"



The comparison is between:



\- a direct local transcription of the validated SpectralSolver update loop

\- SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic(...)



This audit does not call SpectralSolver.run().



This audit does not enable SelectableAdvectionSolver.run().



This audit does not prove turbulence.



This audit does not prove k^-3 scaling.



\## Parameters



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



\## Global Checks



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



\## Equivalence Metrics



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



\## Equivalence Checks



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



The selectable diagnostic run-loop reproduces the validated baseline fd\_centered path exactly for this short controlled audit.



The final field, kinetic energy, enstrophy, RMS, spectrum, and dominant shell matched the direct baseline transcription with zero measured difference.



\## What This Confirms



Phase 11M confirms:



\- run\_selectable\_diagnostic works for fd\_centered

\- the fd\_centered selectable path reproduces the validated baseline update logic

\- the selectable diagnostic loop preserves input initial\_w

\- the selectable diagnostic loop preserves solver.w

\- SelectableAdvectionSolver.run() remains disabled

\- SpectralSolver remains unchanged

\- advection\_operators remains unchanged

\- metadata guardrails remain present

\- no turbulence claim is present

\- no k\_minus\_3 claim is present



\## What This Does Not Confirm



Phase 11M does not confirm:



\- production readiness

\- long-time stability

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- Arakawa superiority

\- Arakawa production readiness

\- pseudo\_spectral production readiness



\## Interpretation



This is an important engineering validation.



The selectable diagnostic loop can now be trusted to reproduce the baseline fd\_centered path under the tested controlled conditions.



This means future method comparisons using run\_selectable\_diagnostic(...) can use fd\_centered as the internal reference path.



\## Recommended Next Phase



Phase 11N — fd\_centered Diagnostic Run-Loop Equivalence Decision Gate



Purpose:



Document the Phase 11M result and decide whether to proceed to controlled pseudo\_spectral and Arakawa diagnostic run-loop comparisons.



Recommended decision:



Proceed to Phase 11N decision gate.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not make turbulence claims.



Do not make k^-3 claims.



\## Final Result



Phase 11M fd\_centered diagnostic run-loop equivalence audit:



PASS



Proceed to Phase 11N decision gate.

