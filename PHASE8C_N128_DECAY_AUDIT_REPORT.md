\# Phase 8C N128 No-Forcing Decay Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Runner tag: v0.4.22-phase8C-N128-decay-runner

\- Runner script: run\_phase8C\_no\_forcing\_decay\_N128.py

\- Audit script: phase8c\_N128\_decay\_audit.py

\- Audit output: PHASE8C\_N128\_DECAY\_AUDIT.csv

\- Source run: experiments/runs/run\_2026-07-11\_17-53-38

\- Phase 8A reference: PHASE8A\_NO\_FORCING\_DECAY\_AUDIT.csv



\## Purpose



Phase 8C performs a resolution-sensitivity check for the no-forcing single-mode viscous decay benchmark.



The test repeats the Phase 8A benchmark at N=128 while preserving the same physical comparison time, timestep, viscosity, Reynolds number, and initial Fourier mode.



The purpose is to check whether increasing grid resolution preserves the expected analytic viscous decay behavior.



\## Configuration



| Quantity | Phase 8A | Phase 8C |

|---|---:|---:|

| Re | 1000 | 1000 |

| nu | 0.001 | 0.001 |

| Grid | 64 x 64 | 128 x 128 |

| dt | 0.005 | 0.005 |

| steps | 1001 | 1001 |

| Comparison intervals | 1000 | 1000 |

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

| Run ID | run\_2026-07-11\_17-53-38 |

| Status completed | PASS |

| Git commit starts with b7e51da | PASS |

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

| Final energy | 1.442253906333e-06 |

| Measured energy ratio | 9.231163464066e-01 |

| Energy ratio relative error | 2.166995256152e-11 |

| Energy decreases | PASS |

| Energy decay theory | PASS |

| Initial enstrophy | 1.249900004000e-05 |

| Final enstrophy | 1.153803125066e-05 |

| Measured enstrophy ratio | 9.231163464066e-01 |

| Enstrophy ratio relative error | 2.167019309957e-11 |

| Enstrophy decreases | PASS |

| Enstrophy decay theory | PASS |



\## Phase 8A Resolution Comparison



| Quantity | Phase 8A | Phase 8C |

|---|---:|---:|

| Measured energy ratio | 9.231163464064e-01 | 9.231163464066e-01 |

| Energy ratio relative error | 2.146248849430e-11 | 2.166995256152e-11 |

| Energy ratio matches 8A |  | PASS |

| Energy error consistent with 8A |  | PASS |

| Measured enstrophy ratio | 9.231163464064e-01 | 9.231163464066e-01 |

| Enstrophy ratio relative error | 2.146236822527e-11 | 2.167019309957e-11 |

| Enstrophy ratio matches 8A |  | PASS |

| Enstrophy error consistent with 8A |  | PASS |



\## Energy and Spectrum Consistency



| Quantity | Result |

|---|---:|

| Final diagnostics energy | 1.442253906333e-06 |

| Sum spectrum E(k) | 1.442253906333e-06 |

| Relative error | 4.404735585401e-16 |

| Energy-spectrum check | PASS |



\## Single-Mode Spectral Shape



The initialized mode was sin(2X) \* cos(2Y). Its shell magnitude is sqrt(8), which rounds to shell k=3 in the current spectrum binning.



| Quantity | Result |

|---|---:|

| Peak k | 3 |

| Peak fraction | 1.000000000000e+00 |

| k=3 fraction | 1.000000000000e+00 |

| k=4 fraction | 3.433541493303e-32 |

| k>=4 fraction | 5.624338487657e-28 |

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

| Initial relation relative error | 7.771561172376e-16 |

| Final relation relative error | 5.551115123126e-16 |

| Z/E relation check | PASS |



\## Overall Result



Phase 8C N128 decay audit: PASS



\## Interpretation



Phase 8C confirms resolution consistency for the no-forcing single-mode viscous decay benchmark.



The N=128 run reproduced the N=64 Phase 8A decay behavior while preserving the expected analytical energy and enstrophy decay ratios.



The spectrum remained concentrated in the expected shell.



The kinetic energy diagnostic and spectrum diagnostic agreed to machine-level precision.



This strengthens the validation of the solver's linear diffusion and diagnostic pathway.



\## Limitations



This benchmark validates a linear no-forcing decay case.



It does not validate nonlinear advection accuracy.



It does not prove turbulence, k^-3 scaling, or an inertial-range cascade.



It does not prove that the current finite-difference advection implementation is sufficient for larger turbulence claims.



\## Conclusion



Phase 8C passes as a resolution-sensitivity benchmark.



The project now has:



\- Phase 8A: no-forcing decay benchmark

\- Phase 8B: half-dt timestep-sensitivity confirmation

\- Phase 8C: N128 resolution-sensitivity confirmation



Recommended next step:



Phase 8D — Linear Benchmark Validation Summary and Decision Gate



The next phase should summarize Phases 8A through 8C and decide whether to proceed to nonlinear-advection validation.

