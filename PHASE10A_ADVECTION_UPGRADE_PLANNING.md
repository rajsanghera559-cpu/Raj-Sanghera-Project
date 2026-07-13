\# Phase 10A Advection Upgrade Planning



\## Checkpoint



\- Branch: phase4\_validation

\- Current prior tag: v0.4.32-phase9A5-nonlinear-drift-decision-gate

\- Current solver file: project/solver/spectral\_solver.py

\- Current solver class: SpectralSolver

\- Current method classification: mixed\_spectral\_finite\_difference



\## Purpose



Phase 10A is a planning phase.



This phase does not run the solver.



This phase does not modify solver code.



The purpose is to decide whether the project should continue controlled exploratory validation with the current solver or prioritize an upgraded nonlinear advection method.



The key question is:



Should the project continue with the current mixed spectral / finite-difference solver, or should it create an Arakawa or fully spectral advection upgrade path before larger experiments?



\## Current Solver Method



The active solver currently uses:



\- spectral streamfunction

\- spectral velocity

\- spectral diffusion

\- centered finite-difference vorticity gradients using np.roll

\- nonlinear advection as u \* wx + v \* wy

\- RK2-style time stepping

\- post-step spectral dealiasing

\- vorticity-based kinetic energy spectrum diagnostic



The active solver is not a fully spectral Navier-Stokes solver.



The active solver is not an Arakawa Jacobian solver.



The active solver is best described as:



mixed\_spectral\_finite\_difference



\## Completed Validation Foundation



The project has completed a substantial validation sequence.



\### Linear Benchmark Stage



| Phase | Test | Result |

|---|---|---:|

| Phase 8A | no-forcing single-mode viscous decay | PASS |

| Phase 8B | half-dt timestep sensitivity | PASS |

| Phase 8C | N128 resolution sensitivity | PASS |

| Phase 8D | linear benchmark decision gate | complete |



Validated from Phase 8:



The active solver reproduces analytical viscous decay for a clean single Fourier mode under zero forcing.



The energy and enstrophy diagnostics match the expected decay ratio for the linear benchmark.



The kinetic energy spectrum diagnostic agrees with the kinetic energy diagnostic to machine-level precision.



The linear benchmark shows timestep sensitivity consistent with RK2-style second-order behavior.



The linear benchmark is consistent between N=64 and N=128 for the tested low Fourier mode.



\### Nonlinear Sanity Stage



| Phase | Test | Result |

|---|---|---:|

| Phase 9A.1 | frozen solver method review | complete |

| Phase 9A.2 | advection diagnostic comparison | PASS |

| Phase 9A.3 | nonlinear no-forcing drift audit | PASS |

| Phase 9A.4 | strict half-dt nonlinear drift audit | FAIL, reviewed |

| Phase 9A.4R | tolerance-robust half-dt nonlinear drift re-audit | PASS |

| Phase 9A.5 | nonlinear drift decision gate | complete |



Validated from Phase 9A:



The current finite-difference advection diagnostic converges toward a spectral-derivative diagnostic as resolution increases on controlled nonlinear fields.



The active solver can evolve a low-amplitude nonlinear multimode vorticity field with zero forcing over a short time interval without blow-up or material energy/enstrophy growth.



The short nonlinear no-forcing drift behavior is consistent under a half-dt rerun when physically meaningful tolerances are used.



The original strict Phase 9A.4 audit failure was preserved, reviewed, and traced to an over-strict final-state tolerance rather than material solver instability.



\## Current Scientific Boundary



The project can currently claim:



The current solver has passed linear diffusion validation.



The current solver has passed short nonlinear no-forcing sanity checks.



The current solver is useful for controlled exploratory research when claims are conservative.



The project should not claim:



k^-3 scaling has been demonstrated.



A resolved inertial-range cascade has been produced.



The solver is fully validated for 2D turbulence.



The solver is a fully spectral Navier-Stokes solver.



The solver uses an Arakawa Jacobian.



Long-time nonlinear stability has been proven.



\## Main Remaining Numerical Risk



The main remaining risk is nonlinear advection accuracy.



The current advection method is centered finite difference, while the streamfunction, velocity, diffusion, and spectral diagnostics are spectral.



This mixed method has passed controlled short tests, but it remains less rigorous than a standard Arakawa or fully spectral nonlinear formulation.



For larger turbulence experiments, the nonlinear advection method will become the credibility bottleneck.



\## Upgrade Options



\### Option A: Continue with the current solver for controlled exploratory runs



Description:



Keep the current solver unchanged and run carefully labeled exploratory tests.



Benefits:



\- fastest path

\- no new implementation risk

\- current validation foundation remains directly applicable

\- useful for controlled low-amplitude studies

\- good for pipeline, diagnostics, and workflow development



Risks:



\- nonlinear advection remains finite-difference based

\- long-time behavior remains uncertain

\- high-Reynolds turbulence claims would be weak

\- reviewers may challenge the method

\- k^-3 claims would remain unsupported



Appropriate use:



\- smoke runs

\- short nonlinear drift tests

\- forcing-geometry comparisons

\- diagnostics development

\- pipeline validation



Not appropriate for:



\- strong turbulence claims

\- k^-3 scaling claims

\- publication-level Navier-Stokes turbulence claims



\### Option B: Add diagnostic comparison tools without changing solver



Description:



Keep the solver unchanged but add more diagnostic tools to compare current advection against spectral or Arakawa-style diagnostics.



Benefits:



\- low implementation risk

\- preserves current solver path

\- strengthens evidence before rewriting code

\- helps identify whether current advection is good enough

\- gives quantitative upgrade targets



Risks:



\- does not fix the solver

\- only diagnoses differences

\- can delay the necessary upgrade



Possible tools:



\- spectral Jacobian diagnostic

\- Arakawa Jacobian diagnostic

\- nonlinear residual comparison

\- energy/enstrophy drift comparison across advection formulas

\- controlled field library for advection tests



Appropriate use:



\- method validation

\- upgrade planning

\- choosing between Arakawa and full spectral advection



\### Option C: Create an Arakawa advection branch



Description:



Add a separate solver or branch using an Arakawa Jacobian for nonlinear advection.



Benefits:



\- stronger conservation properties

\- widely recognized in 2D fluid simulations

\- better suited for energy/enstrophy behavior

\- likely stronger for nonlinear long-time stability

\- more defensible than plain centered finite-difference advection



Risks:



\- implementation complexity

\- must validate from scratch

\- may not match current spectral diagnostics immediately

\- can introduce new bugs

\- requires new benchmark suite



Required validation:



\- reproduce Phase 8 linear decay benchmarks

\- reproduce Phase 9A nonlinear drift tests

\- compare energy/enstrophy drift against current solver

\- compare spectra across matched runs

\- verify no new instability



\### Option D: Create a fully spectral advection solver



Description:



Add a pseudo-spectral nonlinear term with spectral derivatives and dealiasing.



Benefits:



\- methodologically aligned with spectral diffusion and spectral diagnostics

\- strong fit for periodic domains

\- clearer connection to spectral turbulence analysis

\- potentially better for k-space diagnostics



Risks:



\- nonlinear aliasing must be handled correctly

\- implementation and validation burden is higher

\- may require careful forcing and filtering design

\- may expose issues in current analysis pipeline

\- still requires extensive validation



Required validation:



\- reproduce Phase 8 linear benchmarks

\- reproduce Phase 9A nonlinear drift tests

\- validate dealiasing behavior

\- compare spectra against current solver

\- test timestep and resolution sensitivity

\- document all normalization choices



\## Recommended Direction



The recommended direction is:



Option B first, then Option C or D.



Reason:



The project should not immediately rewrite the solver without diagnostic targets.



The project already has a working validated baseline. The next move should preserve that baseline while designing the upgraded nonlinear method carefully.



Recommended sequence:



1\. Phase 10A — planning decision gate

2\. Phase 10B — Arakawa and spectral advection design notes

3\. Phase 10C — standalone nonlinear advection operator tests

4\. Phase 10D — choose upgrade path

5\. Phase 11A — implement upgraded solver branch or separate solver file

6\. Phase 11B — rerun Phase 8 and Phase 9 benchmarks on upgraded solver



\## Recommended Immediate Next Phase



Recommended next phase:



Phase 10B — Nonlinear Advection Upgrade Design Notes



Purpose:



Define the mathematical and software requirements for an Arakawa or fully spectral advection upgrade before writing production solver code.



Phase 10B should answer:



\- What equations will the upgraded advection term compute?

\- Will the upgrade use Arakawa, pseudo-spectral Jacobian, or both?

\- Will the upgrade be a new solver file or a branch inside SpectralSolver?

\- What exact tests must the upgraded method pass?

\- Which prior Phase 8 and Phase 9 tests must be rerun?

\- What outputs must be compared against the current solver?

\- What acceptance criteria define success?



\## Proposed Acceptance Criteria for Any Upgrade



An upgraded advection method should not be accepted unless it passes:



1\. Phase 8A no-forcing decay benchmark

2\. Phase 8B half-dt decay benchmark

3\. Phase 8C N128 decay benchmark

4\. Phase 9A.2 advection diagnostic comparison

5\. Phase 9A.3 nonlinear no-forcing drift test

6\. Phase 9A.4 half-dt nonlinear drift sensitivity test

7\. energy/spectrum consistency checks

8\. metadata provenance checks

9\. clean git checkpointing

10\. conservative interpretation report



\## Decision



Phase 10A decision:



Do not make larger turbulence or k^-3 claims with the current solver.



Do not immediately discard the current solver.



Use the current solver as a validated baseline for controlled exploratory work.



Begin planning an upgraded nonlinear advection pathway.



Prioritize diagnostic design before implementation.



\## Conclusion



Phase 10A establishes the next development direction.



The project has moved beyond simple smoke testing and now has a meaningful validation foundation.



The current solver is useful but methodologically limited.



The next credibility step is not a larger run. The next credibility step is a better nonlinear advection plan.

