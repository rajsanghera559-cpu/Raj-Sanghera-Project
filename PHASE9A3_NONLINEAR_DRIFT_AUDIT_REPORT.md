\# Phase 9A.3 Nonlinear No-Forcing Drift Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Runner tag: v0.4.27-phase9A3-nonlinear-drift-runner

\- Runner script: run\_phase9A3\_nonlinear\_no\_forcing\_drift.py

\- Audit script: phase9a3\_nonlinear\_drift\_audit.py

\- Audit output: PHASE9A3\_NONLINEAR\_DRIFT\_AUDIT.csv

\- Source run: experiments/runs/run\_2026-07-12\_00-38-33



\## Purpose



Phase 9A.3 runs and audits a short nonlinear no-forcing drift test.



The goal is to check whether a nonlinear multimode vorticity field remains finite and behaves reasonably over a short time interval with zero forcing and very low viscosity.



This is a validation test.



This is not a turbulence claim.



This is not a k^-3 scaling claim.



\## Configuration



| Quantity | Value |

|---|---:|

| Mode | phase9A3\_nonlinear\_no\_forcing\_drift |

| Re | 1000000 |

| nu | 1.0e-06 |

| Grid | 64 x 64 |

| dt | 0.001 |

| steps | 1001 |

| comparison time | 1.0 |

| forcing | zero\_forcing\_override |

| initial condition | phase6d\_like\_multimode\_vorticity |

| target initial RMS | 0.01 |

| expected diagnostic steps | \[0, 500, 1000] |



\## Initial State



| Quantity | Result |

|---|---:|

| Initial field RMS | 1.000000000000e-02 |

| Target field RMS | 1.000000000000e-02 |

| Field RMS expected | PASS |

| Initial energy | 5.059681223644e-06 |

| Initial enstrophy | 5.000000000000e-05 |

| Initial sum spectrum | 5.059681223644e-06 |

| Initial energy/spectrum relative error | 1.674083622692e-16 |

| Initial energy/spectrum check | PASS |

| Initial peak k | 3 |

| Initial peak fraction | 8.705325610962e-01 |



\## Metadata Checks



| Check | Result |

|---|---:|

| Run ID | run\_2026-07-12\_00-38-33 |

| Status completed | PASS |

| Git commit starts with 598b7aa | PASS |

| Git dirty false | PASS |

| Mode expected | PASS |

| Config expected | PASS |



\## File and Finite Checks



| Check | Result |

|---|---:|

| Initial invariants finite | PASS |

| Diagnostics finite | PASS |

| Spectrum finite | PASS |

| Energy nonnegative | PASS |

| Enstrophy nonnegative | PASS |

| E\_k4 nonnegative | PASS |

| Spectrum nonnegative | PASS |

| Mode counts positive | PASS |



\## Diagnostic Step Checks



| Check | Result |

|---|---:|

| Actual steps | \[0, 500, 1000] |

| Expected steps | \[0, 500, 1000] |

| Expected steps match | PASS |

| Steps increasing | PASS |



\## Final State



| Quantity | Result |

|---|---:|

| Final energy | 5.059581449560e-06 |

| Final enstrophy | 4.999889986756e-05 |

| Final E\_k4 | 6.550318231820e-07 |

| Final sum spectrum | 5.059581449560e-06 |

| Final energy/spectrum relative error | 3.348233270671e-16 |

| Final energy/spectrum check | PASS |

| Final peak k | 3 |

| Final peak fraction | 8.705346495963e-01 |

| k=3 fraction | 8.705346495963e-01 |

| k=4 fraction | 1.294636383883e-01 |

| k>=5 fraction | 8.352106665703e-07 |



\## Drift Checks



| Quantity | Result |

|---|---:|

| Energy change initial to final | -1.971944065619e-05 |

| Enstrophy change initial to final | -2.200264877128e-05 |

| Energy change logged step0 to final | -1.969967701886e-05 |

| Enstrophy change logged step0 to final | -2.198051089809e-05 |

| Energy abs drift < 1e-3 | PASS |

| Enstrophy abs drift < 1e-3 | PASS |

| Energy not growing materially | PASS |

| Enstrophy not growing materially | PASS |

| Logged energy monotonic nonincreasing | PASS |

| Logged enstrophy monotonic nonincreasing | PASS |



\## Overall Result



Phase 9A.3 nonlinear drift audit: PASS



\## Interpretation



The short nonlinear no-forcing run completed successfully.



The run remained finite.



Energy and enstrophy remained nonnegative.



Energy and enstrophy did not grow materially.



Logged energy and logged enstrophy decreased monotonically over the diagnostic steps.



The relative drift was very small:



\- Energy drift was approximately -0.001972 percent.

\- Enstrophy drift was approximately -0.002200 percent.



The spectrum remained low-k dominated, with meaningful energy in k=3 and k=4.



This supports the current solver passing a short nonlinear no-forcing sanity test.



\## What This Confirms



Phase 9A.3 confirms:



\- the active solver can evolve a nonlinear multimode field without forcing over a short time interval

\- the run stays finite

\- diagnostics remain internally consistent

\- energy and enstrophy do not show material growth

\- the final energy spectrum agrees with the kinetic energy diagnostic to machine precision



\## What This Does Not Confirm



Phase 9A.3 does not prove full nonlinear benchmark validation.



Phase 9A.3 does not prove long-time nonlinear stability.



Phase 9A.3 does not prove turbulence.



Phase 9A.3 does not prove k^-3 scaling.



Phase 9A.3 does not prove a resolved inertial-range cascade.



Phase 9A.3 does not make the solver a fully spectral Navier-Stokes solver.



\## Limitations



The test is short.



The test uses only diagnostic outputs at steps 0, 500, and 1000.



The test uses low amplitude and very low viscosity.



The test does not compare against an exact nonlinear solution.



The test does not compare against Arakawa or fully spectral time evolution.



\## Conclusion



Phase 9A.3 passes as a nonlinear no-forcing short-time drift sanity test.



The project now has:



\- Phase 8 linear diffusion benchmark validation

\- Phase 9A.2 instantaneous nonlinear advection diagnostic comparison

\- Phase 9A.3 short nonlinear no-forcing drift sanity check



Recommended next step:



Phase 9A.4 — Half-dt Nonlinear Drift Sensitivity Test



Purpose:



Repeat the Phase 9A.3 nonlinear no-forcing drift test with half dt while preserving the same physical comparison time.



This will check whether nonlinear drift behavior is timestep-sensitive before moving to larger nonlinear or turbulence experiments.

