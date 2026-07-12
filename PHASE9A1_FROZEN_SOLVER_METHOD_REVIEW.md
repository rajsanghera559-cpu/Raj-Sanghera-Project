\# Phase 9A.1 Frozen Solver Method Review



\## Checkpoint



\- Branch: phase4\_validation

\- Current prior tag: v0.4.24-phase8D-linear-benchmark-decision-gate

\- Active solver file: project/solver/spectral\_solver.py

\- Active solver class: SpectralSolver

\- Purpose: freeze the current numerical method before nonlinear-advection validation



\## Purpose



Phase 9A.1 documents the current active solver method before any nonlinear-advection benchmark or solver modification is attempted.



This phase does not run the solver.



This phase does not modify solver code.



The goal is to prevent accidental overclaiming and to define the next validation target clearly.



\## Active Solver Path



Recent active runners use:



| Runner | Uses SpectralSolver |

|---|---:|

| run\_phase6B\_spreading.py | yes |

| run\_phase6C\_perturbed\_ic.py | yes |

| run\_phase6D\_multimode\_forcing.py | yes |

| run\_phase7B\_smoke.py | yes |

| run\_phase7D\_multimode\_smoke.py | yes |

| run\_phase8A\_no\_forcing\_decay.py | yes |

| run\_phase8B\_no\_forcing\_decay\_dt\_half.py | yes |

| run\_phase8C\_no\_forcing\_decay\_N128.py | yes |



The active recent path is:



project/solver/spectral\_solver.py



The older files are not the active recent execution path:



\- project/run.py

\- project/solver/core.py

\- project/solver/legacy\_solver.py



\## Current Numerical Method



The active solver is classified as:



mixed\_spectral\_finite\_difference



\## Confirmed Components



\### Spectral streamfunction



The solver computes the streamfunction using FFT methods.



Method:



\- compute fft2(w)

\- divide by k^2

\- return ifft2 result



\### Spectral velocity



The solver computes velocity from the streamfunction using FFT derivatives.



Method:



\- u from ky derivative of streamfunction

\- v from kx derivative of streamfunction



\### Spectral diffusion



The solver applies diffusion using a spectral Laplacian.



Method:



\- fft2(w)

\- multiply by -nu \* k^2

\- return ifft2 result



\### Finite-difference advection



The nonlinear advection term is not spectral.



The solver computes vorticity gradients using centered finite differences with np.roll:



\- wx = centered x derivative of w

\- wy = centered y derivative of w

\- adv = u \* wx + v \* wy



This means nonlinear advection is finite-difference based.



\### RK2-style stepping



The solver uses a two-stage update:



\- k1 from the current state

\- w1 = w + dt \* k1

\- k2 from the predicted state

\- w\_new = w + 0.5 \* dt \* (k1 + k2)



\### Post-step dealiasing



After the RK2 update, the solver applies a 2/3 spectral mask:



\- W = fft2(w\_new)

\- W \*= self.deal

\- w = ifft2(W)



This is post-step spectral filtering.



\## What Has Been Validated So Far



The linear benchmark stage has passed:



| Phase | Test | Result |

|---|---|---:|

| Phase 8A | no-forcing single-mode viscous decay | PASS |

| Phase 8B | half-dt timestep sensitivity | PASS |

| Phase 8C | N128 resolution sensitivity | PASS |

| Phase 8D | linear benchmark decision gate | PASS |



Validated claim:



The active solver reproduces analytical viscous decay for a clean single Fourier mode under zero forcing.



Validated claim:



Energy and enstrophy diagnostics match the expected decay ratio for the linear benchmark.



Validated claim:



The spectrum diagnostic agrees with the kinetic energy diagnostic to machine-level precision in the tested linear benchmark.



\## What Remains Unvalidated



The nonlinear advection term has not been benchmark-validated.



The current solver has not been fully validated for 2D turbulence.



The current solver has not demonstrated k^-3 scaling.



The current solver has not demonstrated a resolved inertial-range cascade.



The current solver is not a fully spectral Navier-Stokes solver.



The current solver is not an Arakawa Jacobian solver.



\## Main Scientific Risk



The main remaining numerical risk is nonlinear advection accuracy.



The advection term uses centered finite differences on vorticity gradients while the streamfunction, velocity, diffusion, and spectrum diagnostics use spectral methods.



This mixed method may be acceptable for controlled exploratory experiments, but it must be validated before larger turbulence claims.



\## Decision Options



\### Option A: Validate current advection as-is



Proceed with nonlinear sanity tests using the current finite-difference advection implementation.



Possible next tests:



\- two-mode no-forcing nonlinear interaction check

\- short inviscid or very-low-viscosity drift check

\- energy and enstrophy drift audit at high Reynolds number

\- compare nonlinear run behavior across dt and N



Benefit:



Fastest path.



Risk:



If advection is structurally weak, later turbulence results may be artifacts.



\### Option B: Add a diagnostic spectral Jacobian comparison



Keep the solver unchanged but add an audit script that computes a spectral Jacobian diagnostic and compares it with the current np.roll advection term on selected fields.



Benefit:



Lower risk than modifying the solver immediately.



Risk:



Diagnostic comparison may reveal differences but not fix them.



\### Option C: Create an Arakawa or fully spectral branch



Create a new solver branch or separate solver file with a more standard nonlinear advection method.



Benefit:



Stronger numerical foundation.



Risk:



More code changes and more validation work.



\## Recommended Next Step



Recommended next phase:



Phase 9A.2 — Nonlinear Advection Diagnostic Comparison



Purpose:



Compare the current finite-difference advection term against an independently computed spectral-advection diagnostic on controlled test fields, without modifying the production solver yet.



This keeps the current solver frozen and avoids mixing validation with solver redesign.



\## Phase 9A.1 Conclusion



The current active solver method is now frozen and documented.



The project should proceed to nonlinear-advection validation before any larger turbulence experiment or k^-3 claim.



The safest next move is a diagnostic comparison, not a solver rewrite.

