\# Phase 9A.5 Nonlinear Drift Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current prior tag: v0.4.31-phase9A4R-tolerance-robust-nonlinear-drift-reaudit

\- Phase 9A.1 report: PHASE9A1\_FROZEN\_SOLVER\_METHOD\_REVIEW.md

\- Phase 9A.2 report: PHASE9A2\_ADVECTION\_DIAGNOSTIC\_COMPARISON\_REPORT.md

\- Phase 9A.3 report: PHASE9A3\_NONLINEAR\_DRIFT\_AUDIT\_REPORT.md

\- Phase 9A.4 review: PHASE9A4\_HALF\_DT\_NONLINEAR\_DRIFT\_AUDIT\_REVIEW.md

\- Phase 9A.4R report: PHASE9A4R\_TOLERANCE\_ROBUST\_NONLINEAR\_DRIFT\_REAUDIT\_REPORT.md



\## Purpose



Phase 9A.5 summarizes the nonlinear-advection validation work from Phase 9A.1 through Phase 9A.4R.



This phase does not rerun the solver.



This phase does not modify solver code.



The purpose is to decide whether the current mixed spectral / finite-difference solver is acceptable for controlled nonlinear exploratory runs, or whether an Arakawa or fully spectral advection upgrade should be prioritized before further experiments.



\## Active Solver Classification



The active solver remains classified as:



mixed\_spectral\_finite\_difference



The solver uses:



\- spectral streamfunction

\- spectral velocity

\- spectral diffusion

\- centered finite-difference vorticity gradients using np.roll

\- nonlinear advection as u \* wx + v \* wy

\- RK2-style time stepping

\- post-step spectral dealiasing

\- vorticity-based kinetic energy spectrum diagnostic



The solver is not a fully spectral Navier-Stokes solver.



The solver is not an Arakawa Jacobian solver.



\## Phase 8 Foundation



Before nonlinear testing, the linear benchmark validation stage passed.



| Phase | Test | Result |

|---|---|---:|

| Phase 8A | no-forcing single-mode viscous decay | PASS |

| Phase 8B | half-dt timestep sensitivity | PASS |

| Phase 8C | N128 resolution sensitivity | PASS |

| Phase 8D | linear benchmark decision gate | complete |



Validated from Phase 8:



The active solver reproduces analytical viscous decay for a clean single Fourier mode under zero forcing.



The energy and enstrophy diagnostics match the expected decay ratio for the linear benchmark.



The kinetic energy spectrum diagnostic agrees with the kinetic energy diagnostic to machine-level precision in the tested linear benchmark.



The linear benchmark shows timestep sensitivity consistent with RK2-style second-order behavior.



The linear benchmark is consistent between N=64 and N=128 for the tested low Fourier mode.



\## Phase 9A.1 Frozen Solver Method Review



Phase 9A.1 documented the current active solver method.



Result:



complete



Main finding:



The solver should be treated honestly as mixed spectral / finite-difference.



The main remaining numerical risk is nonlinear advection accuracy.



\## Phase 9A.2 Advection Diagnostic Comparison



Phase 9A.2 compared the active finite-difference advection term against an independently computed spectral-derivative advection diagnostic.



Result:



PASS



Main nonlinear-field results:



| Field | N64 Relative Error | N128 Relative Error | N128/N64 Error Ratio | Result |

|---|---:|---:|---:|---:|

| low\_mode\_pair | 4.522161377788e-02 | 1.135289606901e-02 | 2.510502195868e-01 | PASS |

| phase6d\_like\_multimode | 3.796150569556e-02 | 9.549903183481e-03 | 2.515680821533e-01 | PASS |

| higher\_smooth\_multimode | 1.656847283096e-01 | 4.222295104408e-02 | 2.548391241297e-01 | PASS |



Interpretation:



For controlled nonlinear multimode fields, the finite-difference advection diagnostic converges toward the spectral-derivative diagnostic as resolution increases.



The approximate 0.25 error ratio when doubling resolution is consistent with second-order centered finite-difference behavior.



\## Phase 9A.3 Nonlinear No-Forcing Drift Test



Phase 9A.3 ran a short nonlinear no-forcing drift test using a Phase 6D-like multimode vorticity field.



Result:



PASS



Configuration:



| Quantity | Value |

|---|---:|

| Re | 1000000 |

| nu | 1.0e-06 |

| Grid | 64 x 64 |

| dt | 0.001 |

| steps | 1001 |

| comparison time | 1.0 |

| forcing | zero |

| initial condition | phase6d-like multimode |

| target RMS | 0.01 |



Drift results:



| Quantity | Result |

|---|---:|

| Energy change initial to final | -1.971944065619e-05 |

| Enstrophy change initial to final | -2.200264877128e-05 |

| Energy abs drift < 1e-3 | PASS |

| Enstrophy abs drift < 1e-3 | PASS |

| Logged energy monotonic nonincreasing | PASS |

| Logged enstrophy monotonic nonincreasing | PASS |



Interpretation:



The solver evolved a nonlinear multimode field with zero forcing over a short time interval without blow-up, without material energy or enstrophy growth, and with internally consistent diagnostics.



\## Phase 9A.4 Half-dt Nonlinear Drift Test



Phase 9A.4 repeated the nonlinear drift test with half the timestep.



Configuration:



| Quantity | Phase 9A.3 | Phase 9A.4 |

|---|---:|---:|

| Re | 1000000 | 1000000 |

| nu | 1.0e-06 | 1.0e-06 |

| Grid | 64 x 64 | 64 x 64 |

| dt | 0.001 | 0.0005 |

| steps | 1001 | 2001 |

| comparison time | 1.0 | 1.0 |

| forcing | zero | zero |

| initial condition | phase6d-like multimode | phase6d-like multimode |

| target RMS | 0.01 | 0.01 |



Strict audit result:



FAIL



Reason:



One exact final enstrophy comparison against Phase 9A.3 was too strict.



The failed comparison was:



| Quantity | Value |

|---|---:|

| Reference 9A.3 final enstrophy | 4.999889986756e-05 |

| Phase 9A.4 final enstrophy | 4.999890041315e-05 |

| Relative difference | approximately 1.09e-08 |



Interpretation:



This was classified as a tolerance issue, not solver instability.



The strict failure was preserved and documented.



\## Phase 9A.4R Tolerance-Robust Re-Audit



Phase 9A.4R preserved the original strict FAIL result and re-audited the same Phase 9A.4 run using physically meaningful tolerances.



Result:



PASS



Robust comparison to Phase 9A.3:



| Quantity | Result |

|---|---:|

| Final energy relative diff vs 9A.3 | 9.818086265509e-09 |

| Final enstrophy relative diff vs 9A.3 | 1.091193117353e-08 |

| Final E\_k4 relative diff vs 9A.3 | 3.065933972342e-08 |

| Energy drift absolute diff | 9.817892754733e-09 |

| Enstrophy drift absolute diff | 1.091169120121e-08 |

| k=3 fraction absolute diff | 9.884140173000e-10 |

| k=4 fraction absolute diff | 2.698184647931e-09 |

| k>=5 fraction absolute diff | 8.341603517106e-10 |

| Robust 9A.3 comparison OK | PASS |



Interpretation:



The Phase 9A.4 half-dt nonlinear drift run is consistent with Phase 9A.3 under physically meaningful tolerance checks.



\## Validated Claims After Phase 9A



The project can now claim:



The current finite-difference advection diagnostic converges toward a spectral-derivative diagnostic as resolution increases on controlled nonlinear test fields.



The project can now claim:



The active solver can evolve a low-amplitude nonlinear multimode vorticity field with zero forcing over a short time interval without blow-up or material energy/enstrophy growth.



The project can now claim:



The short nonlinear no-forcing drift behavior is consistent under a half-dt rerun when physically meaningful tolerances are used.



The project can now claim:



The original strict Phase 9A.4 audit failure was preserved, reviewed, and traced to an over-strict final-state tolerance rather than material solver instability.



\## Claims Still Not Supported



The project should not claim:



k^-3 scaling has been demonstrated.



The project should not claim:



A resolved inertial-range cascade has been produced.



The project should not claim:



The solver is fully validated for 2D turbulence.



The project should not claim:



The current solver is a fully spectral Navier-Stokes solver.



The project should not claim:



The current solver is an Arakawa Jacobian solver.



The project should not claim:



Long-time nonlinear stability has been proven.



\## Main Remaining Risks



The main remaining risks are:



1\. The nonlinear tests are short-time tests.

2\. The nonlinear tests use low-amplitude controlled fields.

3\. The solver still uses finite-difference advection.

4\. The solver has not been compared against a full nonlinear reference solution.

5\. Long-time stability and high-Reynolds behavior remain untested.

6\. Turbulence scaling claims remain unsupported.



\## Decision



Phase 9A nonlinear sanity validation passes with caveats.



The current solver is acceptable for controlled, clearly labeled nonlinear exploratory runs if the project maintains conservative claims.



The current solver is not sufficient for strong turbulence or k^-3 claims.



Arakawa or fully spectral advection should remain a priority before any serious turbulence-scaling claim.



\## Recommended Next Step



Recommended next phase:



Phase 9B — Controlled Nonlinear Exploratory Run



Purpose:



Run a slightly longer, still-controlled nonlinear no-forcing or weak-forcing case while monitoring energy, enstrophy, spectrum, and drift.



Constraints:



\- keep claims conservative

\- preserve git checkpoints

\- audit every run

\- do not claim k^-3 scaling

\- compare against Phase 9A drift baselines

\- stop if energy/enstrophy drift becomes uncontrolled



Alternative next phase:



Phase 10A — Arakawa or Fully Spectral Advection Upgrade Planning



Purpose:



Plan a cleaner nonlinear advection implementation before larger experiments.



Recommended decision:



Proceed with Phase 9B only as controlled exploratory validation.



Do not proceed to turbulence-scaling claims until an upgraded nonlinear method or stronger benchmark suite exists.



\## Conclusion



Phase 9A.5 closes the nonlinear drift sanity validation stage.



The current solver has passed a meaningful set of linear and short nonlinear validation checks.



The solver remains useful for controlled exploratory research, but the scientific boundary remains clear:



Low-k broadening and short nonlinear stability are supported.



k^-3 scaling and resolved turbulence are not supported.

