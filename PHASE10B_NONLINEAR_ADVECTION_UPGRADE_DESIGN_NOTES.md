\# Phase 10B Nonlinear Advection Upgrade Design Notes



\## Checkpoint



\- Branch: phase4\_validation

\- Current prior tag: v0.4.33-phase10A-advection-upgrade-planning

\- Current solver file: project/solver/spectral\_solver.py

\- Current solver class: SpectralSolver

\- Current method classification: mixed\_spectral\_finite\_difference



\## Purpose



Phase 10B defines the design requirements for a future nonlinear advection upgrade.



This phase does not run the solver.



This phase does not modify solver code.



This phase does not make turbulence or k^-3 claims.



The purpose is to define the mathematical, software, and validation requirements for comparing or replacing the current finite-difference nonlinear advection method.



\## Current Solver Baseline



The current active solver uses:



\- spectral streamfunction

\- spectral velocity

\- spectral diffusion

\- centered finite-difference vorticity gradients using np.roll

\- nonlinear advection as u \* wx + v \* wy

\- RK2-style time stepping

\- post-step spectral dealiasing

\- vorticity-based kinetic energy spectrum diagnostic



The current solver is not a fully spectral Navier-Stokes solver.



The current solver is not an Arakawa Jacobian solver.



The current solver should remain frozen as the validated baseline while upgrade options are designed.



\## Current Sign Convention



The current solver computes:



psi = streamfunction(w)



u = d psi / dy



v = - d psi / dx



wx = d w / dx



wy = d w / dy



adv = u \* wx + v \* wy



The time-step right-hand side uses:



dw/dt = -adv + diffusion + forcing



Any upgraded nonlinear advection implementation must preserve this project sign convention or explicitly document any sign conversion.



This is critical.



A mathematically correct operator with the wrong sign would invalidate comparisons.



\## Governing Equation Being Approximated



The project is approximating a 2D vorticity equation of the form:



d omega / dt + u dot grad omega = nu \* Laplacian(omega) + forcing



With the project convention:



u dot grad omega = u \* omega\_x + v \* omega\_y



The solver update uses:



d omega / dt = - u dot grad omega + nu \* Laplacian(omega) + forcing



\## Why Upgrade Is Being Considered



The current finite-difference advection has passed controlled diagnostic tests, but it remains the main credibility bottleneck.



Phase 9A.2 showed that the current finite-difference advection converges toward spectral-derivative advection as resolution increases.



Phase 9A.3 and Phase 9A.4R showed short-time nonlinear no-forcing stability under controlled conditions.



However, larger turbulence or scaling claims require stronger nonlinear advection validation.



\## Upgrade Options



\### Option 1: Keep Current Finite-Difference Advection



Description:



Continue using the current centered finite-difference advection method.



Benefits:



\- already implemented

\- already validated through Phase 8 and Phase 9A checks

\- fast to run

\- useful for controlled exploratory work

\- avoids new implementation bugs



Risks:



\- finite-difference nonlinear advection remains less rigorous than Arakawa or pseudo-spectral alternatives

\- long-time nonlinear stability remains uncertain

\- high-Reynolds turbulence claims remain weak

\- reviewers may challenge the method

\- k^-3 claims remain unsupported



Recommended role:



Use as the baseline solver.



Do not discard it.



Do not use it alone for strong turbulence-scaling claims.



\### Option 2: Add Pseudo-Spectral Advection Diagnostic



Description:



Compute vorticity derivatives spectrally:



omega\_x = inverse FFT of i\*kx\*omega\_hat



omega\_y = inverse FFT of i\*ky\*omega\_hat



Then compute:



adv = u \* omega\_x + v \* omega\_y



The nonlinear product is computed in physical space.



A 2/3 dealiasing mask should be applied after transforming the nonlinear product back to spectral space.



Benefits:



\- aligns with spectral streamfunction and spectral diffusion

\- natural fit for periodic domains

\- useful for direct comparison with current finite-difference advection

\- can be implemented first as a diagnostic operator without changing the production solver



Risks:



\- nonlinear aliasing must be handled carefully

\- product dealiasing design must be explicit

\- implementation must preserve the project sign convention

\- still requires time-integration validation



Recommended role:



Implement first as a standalone diagnostic operator.



Do not immediately replace the production solver.



\### Option 3: Add Arakawa Jacobian Diagnostic



Description:



Implement an Arakawa-style Jacobian operator for the nonlinear term.



The Arakawa method is designed to improve discrete conservation properties for 2D incompressible flow.



Benefits:



\- stronger conservation structure

\- well-suited to 2D vorticity dynamics

\- useful comparison against current finite-difference advection

\- potentially better long-time behavior than plain centered finite differences



Risks:



\- more complex formula

\- easy to implement with indexing or sign mistakes

\- must be tested carefully against known identities

\- may not align directly with current spectral derivative diagnostics

\- requires separate validation suite



Recommended role:



Implement as a separate diagnostic operator after the pseudo-spectral diagnostic is stable.



Do not replace the production solver until operator tests pass.



\### Option 4: New Solver Variant With Selectable Advection



Description:



Create a new solver file or solver class that allows selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



Benefits:



\- preserves the current validated solver

\- allows direct matched comparisons

\- makes method studies cleaner

\- avoids corrupting the baseline solver



Risks:



\- more software complexity

\- requires clean metadata

\- each solver variant must rerun benchmark validation

\- acceptance criteria must be strict



Recommended role:



Use only after standalone operator diagnostics are complete.



\## Recommended Development Path



Recommended sequence:



1\. Keep the current SpectralSolver frozen as baseline.

2\. Create standalone nonlinear advection operator diagnostics.

3\. Implement pseudo-spectral advection diagnostic first.

4\. Implement Arakawa diagnostic second.

5\. Compare finite-difference, pseudo-spectral, and Arakawa operators on controlled fields.

6\. Only then create a selectable-advection solver variant.

7\. Rerun Phase 8 and Phase 9 benchmark suites on any new solver variant.



\## Proposed File Structure



Recommended future files:



project/solver/advection\_operators.py



This file should contain standalone functions:



\- advection\_fd\_centered(solver, w)

\- advection\_pseudo\_spectral(solver, w)

\- jacobian\_arakawa\_periodic(psi, w, dx)

\- advection\_arakawa(solver, w)

\- apply\_dealias\_mask(solver, field)

\- compare\_advection\_operators(solver, w)



Recommended test or audit scripts:



\- phase10c\_operator\_sanity\_tests.py

\- phase10d\_advection\_operator\_comparison.py

\- phase10e\_arakawa\_operator\_audit.py



Recommended future solver variant:



project/solver/spectral\_solver\_selectable\_advection.py



This should not replace the current solver until the full benchmark suite is rerun.



\## Operator Requirements



Every advection operator must satisfy these requirements:



1\. Accept the same vorticity field shape as the current solver.

2\. Use the same domain length L = 2\*pi.

3\. Use the same periodic boundary assumption.

4\. Preserve the current project sign convention.

5\. Return a real-valued advection field.

6\. Return finite values on controlled test fields.

7\. Be tested at N=64 and N=128.

8\. Be tested on low-mode and multimode fields.

9\. Have documented normalization and derivative conventions.

10\. Have output saved to audit CSV files.



\## Controlled Test Fields



The operator comparison suite should include:



\### Single-mode nonlinear null field



omega = 0.01 \* sin(2X) \* cos(2Y)



Purpose:



Check near-null nonlinear behavior.



Caution:



Relative error may be misleading because true nonlinear advection can be near machine precision.



\### Low-mode pair



omega = 0.01 \* \[sin(2X)cos(2Y) + 0.75\*sin(3X)cos(Y)]



Purpose:



Basic nonlinear multimode interaction.



\### Phase 6D-like multimode field



omega = RMS-scaled combination of:



\- sin(2X)cos(2Y)

\- 0.75\*sin(3X)cos(Y)

\- 0.50\*sin(X)cos(4Y)

\- 0.35\*cos(4X-2Y)



Purpose:



Continuity with earlier forcing and drift tests.



\### Higher smooth multimode field



A smooth higher-mode field containing moderate wavenumbers.



Purpose:



Stress derivative accuracy.



\## Acceptance Criteria for Operator Diagnostics



The finite-difference operator should show decreasing relative error against pseudo-spectral derivatives as resolution increases.



Expected behavior:



Doubling resolution from N=64 to N=128 should reduce centered finite-difference derivative error by approximately 4x for smooth fields.



Acceptance criteria:



| Check | Requirement |

|---|---|

| finite values | PASS |

| nonzero nonlinear multimode operator norm | PASS |

| N128 error less than N64 error | PASS |

| N128/N64 error ratio near 0.25 for smooth multimode fields | REVIEW or PASS |

| cosine similarity near 1 for low-k fields | PASS |

| single-mode near-null case handled cautiously | REVIEW, not primary evidence |



\## Acceptance Criteria for Any New Solver Variant



A new solver variant should not be accepted unless it passes:



1\. Phase 8A no-forcing single-mode decay benchmark

2\. Phase 8B half-dt decay benchmark

3\. Phase 8C N128 decay benchmark

4\. Phase 9A.2 advection diagnostic comparison

5\. Phase 9A.3 nonlinear no-forcing drift test

6\. Phase 9A.4 half-dt nonlinear drift sensitivity

7\. energy-spectrum consistency audit

8\. metadata provenance audit

9\. clean git checkpointing

10\. conservative interpretation report



\## Metadata Requirements



Every future run must record:



\- mode

\- solver class

\- advection method

\- Re

\- nu

\- nx

\- ny

\- dt

\- steps

\- forcing type

\- initial condition

\- comparison time

\- git commit

\- git dirty status

\- expected diagnostic steps



Any selectable-advection solver must write the selected advection method into metadata.



\## Reporting Requirements



Every new operator or solver variant must have:



\- runner script

\- audit script

\- CSV audit output

\- markdown report

\- git commit

\- git tag

\- conservative interpretation



Reports must distinguish:



\- what passed

\- what failed

\- what was reviewed

\- what was not tested

\- what claims remain unsupported



\## Decision for Phase 10B



Phase 10B decision:



Do not modify the production solver yet.



Do not start a larger turbulence experiment yet.



Do not claim k^-3 scaling.



Next implementation step should be standalone operator diagnostics.



Recommended next phase:



Phase 10C — Standalone Nonlinear Advection Operator Test Scaffold



Purpose:



Create a standalone operator comparison scaffold that computes finite-difference, pseudo-spectral, and later Arakawa advection fields on controlled test fields without modifying SpectralSolver.



\## Conclusion



The current solver remains a validated baseline for controlled exploratory tests.



The next credibility improvement is not a bigger run.



The next credibility improvement is a clean nonlinear advection operator comparison framework.



Phase 10C should build the scaffold for that framework while preserving the current solver as-is.

