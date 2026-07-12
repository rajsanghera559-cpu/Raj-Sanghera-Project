\# Phase 8B Half-dt No-Forcing Decay Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Runner tag: v0.4.20-phase8B-half-dt-decay-runner

\- Runner script: run\_phase8B\_no\_forcing\_decay\_dt\_half.py

\- Audit script: phase8b\_half\_dt\_decay\_audit.py

\- Audit output: PHASE8B\_HALF\_DT\_DECAY\_AUDIT.csv

\- Source run: experiments/runs/run\_2026-07-11\_17-45-08

\- Phase 8A reference: PHASE8A\_NO\_FORCING\_DECAY\_AUDIT.csv



\## Purpose



Phase 8B performs a timestep-sensitivity check for the no-forcing single-mode viscous decay benchmark.



The test repeats the Phase 8A benchmark with half the timestep while preserving the same physical comparison time.



This checks whether the solver's decay-ratio error improves when dt is reduced.



\## Configuration



| Quantity | Phase 8A | Phase 8B |

|---|---:|---:|

| Re | 1000 | 1000 |

| nu | 0.001 | 0.001 |

| Grid | 64 x 64 | 64 x 64 |

| dt | 0.005 | 0.0025 |

| steps | 1001 | 2001 |

| Comparison intervals | 1000 | 2000 |

| Comparison time | 5.0 | 5.0 |

| Forcing | zero\_forcing\_override | zero\_forcing\_override |

| Initial condition | single Fourier mode | single Fourier mode |

| mode\_kx | 2 | 2 |

| mode\_ky | 2 | 2 |

| k\_squared | 8 | 8 |



\## Theoretical Decay



For a single Fourier mode under viscous decay:



Energy ratio = exp(-2 \* nu \* k\_squared \* time)



For this benchmark:



| Quantity | Value |

|---|---:|

| nu | 1.000000000000e-03 |

| k\_squared | 8.000000000000e+00 |

| comparison time | 5.000000000000e+00 |

| Expected ratio | 9.231163463866e-01 |



\## Metadata Checks



| Check | Result |

|---|---:|

| Run ID | run\_2026-07-11\_17-45-08 |

| Status completed | PASS |

| Git commit starts with b245295 | PASS |

| Git dirty false | PASS |

| Mode expected | PASS |

| Config expected | PASS |



\## Diagnostics Checks



| Check | Result |

|---|---:|

| Rows | 5 |

| Actual steps | \[0, 500, 1000, 1500, 2000] |

| Expected steps | \[0, 500, 1000, 1500, 2000] |

| Expected steps match | PASS |

| Steps increasing | PASS |

| Diagnostics finite | PASS |

| Energy nonnegative | PASS |

| Enstrophy nonnegative | PASS |

| E\_k4 nonnegative | PASS |



\## Decay Results



| Quantity | Result |

|---|---:|

| Initial energy | 1.562437501250e-06 |

| Final energy | 1.442311597619e-06 |

| Measured energy ratio | 9.231163463918e-01 |

| Energy ratio relative error | 5.584211075653e-12 |

| Energy decreases | PASS |

| Energy decay theory | PASS |

| Initial enstrophy | 1.249950001000e-05 |

| Final enstrophy | 1.153849278096e-05 |

| Measured enstrophy ratio | 9.231163463918e-01 |

| Enstrophy ratio relative error | 5.584090806628e-12 |

| Enstrophy decreases | PASS |

| Enstrophy decay theory | PASS |



\## Phase 8A Comparison



| Quantity | Phase 8A | Phase 8B |

|---|---:|---:|

| Energy ratio relative error | 2.146248849430e-11 | 5.584211075653e-12 |

| Enstrophy ratio relative error | 2.146236822527e-11 | 5.584090806628e-12 |

| 8B / 8A energy error ratio |  | 2.601846974612e-01 |

| 8B / 8A enstrophy error ratio |  | 2.601805517460e-01 |

| Energy error improved vs 8A |  | PASS |

| Enstrophy error improved vs 8A |  | PASS |



The half-dt run reduced the decay-ratio error by approximately 3.84x.



This is consistent with the RK2-style time stepping behaving like a second-order method for the linear viscous decay benchmark.



\## Energy and Spectrum Consistency



| Quantity | Result |

|---|---:|

| Final diagnostics energy | 1.442311597619e-06 |

| Sum spectrum E(k) | 1.442311597619e-06 |

| Relative error | 1.468186466524e-16 |

| Energy-spectrum check | PASS |



\## Single-Mode Spectral Shape



The initialized mode was sin(2X) \* cos(2Y). Its shell magnitude is sqrt(8), which rounds to shell k=3 in the current spectrum binning.



| Quantity | Result |

|---|---:|

| Peak k | 3 |

| Peak fraction | 1.000000000000e+00 |

| k=3 fraction | 1.000000000000e+00 |

| k=4 fraction | 3.715162342076e-31 |

| k>=4 fraction | 7.580168541707e-28 |

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

| Initial relation relative error | 2.220446049250e-16 |

| Final relation relative error | 4.440892098501e-16 |

| Z/E relation check | PASS |



\## Overall Result



Phase 8B half-dt decay audit: PASS



\## Interpretation



Phase 8B confirms timestep sensitivity for the no-forcing single-mode viscous decay benchmark.



Halving dt while preserving the same physical comparison time reduced the decay-ratio error by approximately 3.84x.



This supports the conclusion that the active solver's linear diffusion and diagnostic pathway is behaving consistently with second-order time-stepping behavior for this controlled benchmark.



\## Limitations



This benchmark validates a linear no-forcing decay case.



It does not validate nonlinear advection accuracy.



It does not prove turbulence, k^-3 scaling, or an inertial-range cascade.



It does not prove that the current finite-difference advection implementation is sufficient for larger turbulence claims.



\## Conclusion



Phase 8B passes as a timestep-sensitivity benchmark.



The project now has:



\- Phase 8A: no-forcing decay benchmark

\- Phase 8B: half-dt timestep-sensitivity confirmation



Recommended next step:



Phase 8C — Resolution Sensitivity for No-Forcing Decay



The next validation should rerun the same no-forcing decay benchmark at higher resolution while preserving the same physical time and initial Fourier mode.

