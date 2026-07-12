\# Phase 8A No-Forcing Decay Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Runner tag: v0.4.18-phase8A-no-forcing-decay-runner

\- Runner script: run\_phase8A\_no\_forcing\_decay.py

\- Audit script: phase8a\_no\_forcing\_decay\_audit.py

\- Audit output: PHASE8A\_NO\_FORCING\_DECAY\_AUDIT.csv

\- Source run: experiments/runs/run\_2026-07-03\_23-57-36



\## Purpose



Phase 8A performs a benchmark-oriented no-forcing decay test.



The purpose is to check whether the active solver correctly reproduces viscous decay for a clean single Fourier mode when forcing is removed.



This is stronger than a smoke test because the expected energy and enstrophy decay ratio can be computed analytically.



\## Configuration



| Quantity | Value |

|---|---:|

| Mode | phase8A\_no\_forcing\_single\_mode\_decay |

| Re | 1000 |

| nu | 0.001 |

| Grid | 64 x 64 |

| dt | 0.005 |

| steps | 1001 |

| Forcing | zero\_forcing\_override |

| Initial condition | single\_fourier\_mode |

| Initial condition formula | amplitude \* sin(2X) \* cos(2Y) |

| amplitude | 0.01 |

| mode\_kx | 2 |

| mode\_ky | 2 |

| k\_squared | 8 |

| Expected diagnostic steps | \[0, 500, 1000] |



\## Theoretical Decay



For a single Fourier mode under viscous decay, energy and enstrophy should decay according to:



Energy ratio = exp(-2 \* nu \* k\_squared \* time)



For this run:



| Quantity | Value |

|---|---:|

| nu | 1.000000000000e-03 |

| k\_squared | 8.000000000000e+00 |

| dt | 5.000000000000e-03 |

| Time interval | 1000 \* dt = 5 |

| Expected ratio from metadata | 9.231163463866e-01 |

| Expected ratio recomputed | 9.231163463866e-01 |

| Expected ratio consistency | PASS |



\## Metadata Checks



| Check | Result |

|---|---:|

| Run ID | run\_2026-07-03\_23-57-36 |

| Status completed | PASS |

| Git commit starts with 5e981f4 | PASS |

| Git dirty false | PASS |

| Mode expected | PASS |

| Config expected | PASS |



\## Diagnostics Checks



| Check | Result |

|---|---:|

| Rows | 3 |

| Actual steps | \[0, 500, 1000] |

| Expected steps | \[0, 500, 1000] |

| Expected steps match | PASS |

| Steps increasing | PASS |

| Diagnostics finite | PASS |

| Energy nonnegative | PASS |

| Enstrophy nonnegative | PASS |

| E\_k4 nonnegative | PASS |



\## Decay Results



| Quantity | Result |

|---|---:|

| Initial energy | 1.562375005000e-06 |

| Final energy | 1.442253906332e-06 |

| Measured energy ratio | 9.231163464064e-01 |

| Energy ratio relative error | 2.146248849430e-11 |

| Energy decreases | PASS |

| Energy decay theory | PASS |

| Initial enstrophy | 1.249900004000e-05 |

| Final enstrophy | 1.153803125066e-05 |

| Measured enstrophy ratio | 9.231163464064e-01 |

| Enstrophy ratio relative error | 2.146236822527e-11 |

| Enstrophy decreases | PASS |

| Enstrophy decay theory | PASS |



\## Energy and Spectrum Consistency



| Quantity | Result |

|---|---:|

| Final diagnostics energy | 1.442253906332e-06 |

| Sum spectrum E(k) | 1.442253906332e-06 |

| Relative error | 1.468245195134e-16 |

| Energy-spectrum check | PASS |



\## Single-Mode Spectral Shape



The initialized mode was sin(2X) \* cos(2Y). Its shell magnitude is sqrt(2^2 + 2^2) = sqrt(8), which rounds to shell k=3 in the current spectrum binning.



| Quantity | Result |

|---|---:|

| Peak k | 3 |

| Peak fraction | 1.000000000000e+00 |

| k=3 fraction | 1.000000000000e+00 |

| k=4 fraction | 1.384913189174e-31 |

| k>=4 fraction | 2.026148754715e-28 |

| Peak k expected | PASS |

| Single-shell preserved | PASS |

| Non-target shells small | PASS |



\## Enstrophy / Energy Relation



For a clean single Fourier mode, Z/E should equal k\_squared.



| Quantity | Result |

|---|---:|

| Initial Z/E | 8.000000000000e+00 |

| Final Z/E | 8.000000000000e+00 |

| Expected k\_squared | 8.000000000000e+00 |

| Initial relation relative error | 0.000000000000e+00 |

| Final relation relative error | 1.110223024625e-16 |

| Z/E relation check | PASS |



\## Overall Result



Phase 8A no-forcing decay audit: PASS



\## Interpretation



The active solver correctly reproduces viscous decay for a clean single Fourier mode under zero forcing.



Energy and enstrophy decay at the analytically expected rate.



The spectrum remains concentrated in the expected shell.



The kinetic energy diagnostic and spectrum diagnostic agree to machine-level precision.



This is a benchmark-style validation result for the solver's linear diffusion and diagnostic pathway.



\## Limitations



This test does not validate nonlinear advection accuracy.



For this single-mode decay case, the nonlinear advection term is not being stress-tested in the way it would be in a multi-mode nonlinear flow.



This test does not prove turbulence, k^-3 scaling, or an inertial-range cascade.



This test does not prove that the finite-difference advection method is sufficient for larger turbulence claims.



\## Conclusion



Phase 8A passes as a no-forcing single-mode viscous decay benchmark.



The project now has a defensible benchmark-oriented validation point.



Recommended next step:



Phase 8B — Timestep Sensitivity for No-Forcing Decay



The next validation should rerun the same no-forcing decay benchmark with a smaller timestep and compare the measured decay-ratio error.

