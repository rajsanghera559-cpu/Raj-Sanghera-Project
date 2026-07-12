# Phase 8D Linear Benchmark Validation Summary and Decision Gate

## Checkpoint

- Branch: phase4_validation
- Current prior tag: v0.4.23-phase8C-N128-decay-audit
- Phase 8A audit: PHASE8A_NO_FORCING_DECAY_AUDIT.csv
- Phase 8B audit: PHASE8B_HALF_DT_DECAY_AUDIT.csv
- Phase 8C audit: PHASE8C_N128_DECAY_AUDIT.csv

## Purpose

Phase 8D summarizes the linear benchmark validation sequence from Phases 8A through 8C.

This phase does not rerun the solver.

The purpose is to define what has been validated, what remains unvalidated, and what the next rigorous validation step should be.

## Linear Benchmark Used

The benchmark used a no-forcing single Fourier mode viscous decay test.

Initial condition:

omega(x,y,0) = amplitude * sin(2X) * cos(2Y)

Benchmark parameters:

| Quantity | Value |
|---|---:|
| amplitude | 0.01 |
| mode_kx | 2 |
| mode_ky | 2 |
| k_squared | 8 |
| Re | 1000 |
| nu | 0.001 |
| forcing | zero_forcing_override |

For a single Fourier mode under viscous decay, energy and enstrophy should decay by:

ratio = exp(-2 * nu * k_squared * time)

For the benchmark time interval:

| Quantity | Value |
|---|---:|
| time | 5.0 |
| expected ratio | 9.231163463866e-01 |

## Phase 8A Result

Phase 8A tested the baseline no-forcing decay benchmark.

| Quantity | Value |
|---|---:|
| Grid | 64 x 64 |
| dt | 0.005 |
| steps | 1001 |
| comparison time | 5.0 |
| measured energy ratio | 9.231163464064e-01 |
| expected energy ratio | 9.231163463866e-01 |
| energy ratio relative error | 2.146248849430e-11 |
| measured enstrophy ratio | 9.231163464064e-01 |
| enstrophy ratio relative error | 2.146236822527e-11 |
| result | PASS |

Interpretation:

Phase 8A validated the linear diffusion and diagnostic pathway for a clean single Fourier mode.

## Phase 8B Result

Phase 8B repeated the benchmark with half the timestep while preserving the same physical comparison time.

| Quantity | Phase 8A | Phase 8B |
|---|---:|---:|
| Grid | 64 x 64 | 64 x 64 |
| dt | 0.005 | 0.0025 |
| steps | 1001 | 2001 |
| comparison time | 5.0 | 5.0 |
| energy ratio relative error | 2.146248849430e-11 | 5.584211075653e-12 |
| enstrophy ratio relative error | 2.146236822527e-11 | 5.584090806628e-12 |
| 8B / 8A energy error ratio |  | 2.601846974612e-01 |
| result | PASS | PASS |

Interpretation:

Halving dt reduced the decay-ratio error by approximately 3.84x.

This is consistent with RK2-style second-order behavior for the linear viscous decay benchmark.

## Phase 8C Result

Phase 8C repeated the benchmark at higher resolution while preserving the same timestep and physical comparison time.

| Quantity | Phase 8A | Phase 8C |
|---|---:|---:|
| Grid | 64 x 64 | 128 x 128 |
| dt | 0.005 | 0.005 |
| steps | 1001 | 1001 |
| comparison time | 5.0 | 5.0 |
| measured energy ratio | 9.231163464064e-01 | 9.231163464066e-01 |
| energy ratio relative error | 2.146248849430e-11 | 2.166995256152e-11 |
| measured enstrophy ratio | 9.231163464064e-01 | 9.231163464066e-01 |
| enstrophy ratio relative error | 2.146236822527e-11 | 2.167019309957e-11 |
| result | PASS | PASS |

Interpretation:

The N=128 result matched the N=64 result.

This supports resolution consistency for the linear no-forcing decay benchmark.

## Shared Validation Checks Passed

Across Phases 8A through 8C:

| Check | Result |
|---|---:|
| Metadata completed | PASS |
| Git dirty false at run time | PASS |
| Diagnostics finite | PASS |
| Energy nonnegative | PASS |
| Enstrophy nonnegative | PASS |
| Energy decreases | PASS |
| Enstrophy decreases | PASS |
| Energy decay matches theory | PASS |
| Enstrophy decay matches theory | PASS |
| Energy-spectrum consistency | PASS |
| Single-shell spectral shape preserved | PASS |
| Z/E = k_squared relation | PASS |

## Validated Claims

The project can now claim:

The active solver reproduces analytical viscous decay for a clean single Fourier mode under zero forcing.

The project can now claim:

The energy and enstrophy diagnostics match the expected decay ratio for the linear benchmark.

The project can now claim:

The kinetic energy spectrum diagnostic agrees with the kinetic energy diagnostic to machine-level precision in the tested linear benchmark.

The project can now claim:

The linear no-forcing benchmark shows timestep sensitivity consistent with RK2-style second-order behavior.

The project can now claim:

The linear no-forcing benchmark is consistent between N=64 and N=128 for this low Fourier mode.

## Claims Not Supported

The project should not claim:

The nonlinear advection term has been benchmark-validated.

The project should not claim:

The solver has been fully validated for 2D turbulence.

The project should not claim:

k^-3 scaling has been demonstrated.

The project should not claim:

A resolved inertial-range cascade has been produced.

The project should not claim:

The current solver is a fully spectral Navier-Stokes solver.

## Current Scientific Interpretation

The current solver has passed a meaningful linear benchmark sequence.

The validated part is:

linear viscous decay plus diagnostics

The unvalidated part is:

nonlinear advection accuracy

This distinction matters because the active solver is still classified as:

mixed_spectral_finite_difference

The solver uses spectral streamfunction and spectral diffusion, but finite-difference advection.

## Decision Gate

Phase 8A through Phase 8C pass as linear benchmark validation.

The next validation target should be nonlinear advection behavior.

## Recommended Next Phase

Recommended next phase:

Phase 9A — Nonlinear Advection Sanity Benchmark

Purpose:

Test whether the active solver behaves reasonably when nonlinear advection is present.

Suggested options:

1. Two-mode no-forcing interaction test
2. Inviscid or low-viscosity short-time energy/enstrophy drift check
3. Compare finite-difference advection against a spectral Jacobian diagnostic
4. Add an Arakawa Jacobian benchmark branch
5. Create a passive nonlinear consistency test before larger turbulence claims

Recommended first step:

Phase 9A.1 — Frozen Solver Method Review

Before writing new nonlinear tests, inspect the active advection implementation and decide whether to validate it as-is or upgrade to Arakawa/full spectral advection.

## Conclusion

Phase 8D closes the linear benchmark validation stage.

The project now has a defensible validation foundation for the linear diffusion and diagnostic components.

The next scientifically responsible step is nonlinear-advection validation before any larger turbulence experiment or k^-3 claim.