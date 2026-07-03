\# Phase 7E Reproducibility Summary and Decision Gate



\## Checkpoint



\- Branch: phase4\_validation

\- Current prior tag: v0.4.16-phase7D-multimode-smoke-audit

\- Phase 7B default-forcing run: experiments/runs/run\_2026-07-02\_14-48-55

\- Phase 7D multimode-forcing run: experiments/runs/run\_2026-07-02\_21-57-26



\## Purpose



Phase 7E summarizes the Phase 7 reproducibility work and defines the next decision gate.



This phase does not rerun the solver.



The goal is to compare the fresh default-forcing smoke run against the fresh multimode-forcing smoke run.



\## Phase 7B Default-Forcing Smoke Run



Phase 7B tested whether the current committed code could still generate a fresh short run using the default solver forcing.



Result:



PASS



Configuration:



| Quantity | Value |

|---|---:|

| Run ID | run\_2026-07-02\_14-48-55 |

| Mode | phase7B\_reproducibility\_smoke |

| Re | 1000 |

| Grid | 64 x 64 |

| dt | 0.005 |

| steps | 1001 |

| Forcing | default\_solver\_forcing |

| Status | completed |

| Git dirty | false |



Final diagnostic result:



| Quantity | Value |

|---|---:|

| Final energy | 3.760945667130e-05 |

| Final enstrophy | 3.008756533704e-04 |

| Final E(k=4) | 9.912415967547e-37 |



Spectral result:



| Quantity | Value |

|---|---:|

| Peak k | 3 |

| Peak fraction | 1.000000000000e+00 |

| k=3 fraction | 1.000000000000e+00 |

| k=4 fraction | 2.635617965497e-32 |

| k>=5 fraction | 5.243426918251e-29 |



Interpretation:



The default single-mode forcing reproduced the pure k=3 single-shell lock.



\## Phase 7D Multimode-Forcing Smoke Run



Phase 7D tested whether the Phase 6D RMS-matched deterministic low-k multimode forcing method could reproduce low-k spectral broadening in a fresh short run.



Result:



PASS



Configuration:



| Quantity | Value |

|---|---:|

| Run ID | run\_2026-07-02\_21-57-26 |

| Mode | phase7D\_multimode\_smoke |

| Re | 1000 |

| Grid | 64 x 64 |

| dt | 0.005 |

| steps | 1001 |

| Forcing | phase6D\_rms\_matched\_deterministic\_low\_k\_multimode |

| Status | completed |

| Git dirty | false |



Forcing RMS result:



| Quantity | Value |

|---|---:|

| Base single-mode RMS | 0.005 |

| Raw multimode RMS | 0.7171994143890527 |

| Matched multimode RMS | 0.005 |



Final diagnostic result:



| Quantity | Value |

|---|---:|

| Final energy | 3.016811179391e-05 |

| Final enstrophy | 2.963990690100e-04 |

| Final E(k=4) | 3.743865030854e-06 |



Spectral result:



| Quantity | Value |

|---|---:|

| Peak k | 3 |

| Peak fraction | 8.758728449890e-01 |

| k=3 fraction | 8.758728449890e-01 |

| k=4 fraction | 1.241000781365e-01 |

| k>=5 fraction | 1.264900840531e-05 |



Interpretation:



The RMS-matched multimode forcing reproduced low-k spectral broadening.



The spectrum remained peaked at k=3, but the pure k=3 single-shell lock was broken because k=4 carried meaningful energy.



\## Side-by-Side Comparison



| Quantity | Phase 7B Default Forcing | Phase 7D Multimode Forcing |

|---|---:|---:|

| Grid | 64 x 64 | 64 x 64 |

| Re | 1000 | 1000 |

| dt | 0.005 | 0.005 |

| steps | 1001 | 1001 |

| Final energy | 3.760945667130e-05 | 3.016811179391e-05 |

| Peak k | 3 | 3 |

| Peak fraction | 1.000000000000e+00 | 8.758728449890e-01 |

| k=3 fraction | 1.000000000000e+00 | 8.758728449890e-01 |

| k=4 fraction | 2.635617965497e-32 | 1.241000781365e-01 |

| k>=5 fraction | 5.243426918251e-29 | 1.264900840531e-05 |

| Pure k=3 lock | yes | no |

| Low-k broadening | no | yes |



\## Confirmed Claims



The project can currently claim:



RMS-matched multimode forcing reproducibly breaks the pure k=3 single-shell lock in short controlled smoke runs.



The project can currently claim:



The default solver forcing reproducibly produces a k=3-dominated single-shell result under the same short-run conditions.



The project can currently claim:



The Phase 7B and Phase 7D runs were launched from clean committed states and produced internally consistent metadata, diagnostics, and spectra.



\## Claims Not Supported



The project should not claim:



k^-3 scaling has been demonstrated.



The project should not claim:



A resolved inertial-range cascade has been produced.



The project should not claim:



The solver has been benchmark-validated.



The project should not claim:



The current solver is a fully spectral Navier-Stokes solver.



\## Current Scientific Interpretation



The current defensible interpretation is:



The k=3 single-shell result is highly sensitive to forcing geometry.



Default single-mode forcing locks the spectrum at k=3.



RMS-matched multimode forcing weakens that lock and redistributes meaningful energy into k=4.



This is low-k spectral broadening, not turbulence scaling.



\## Decision Gate



Phase 7 reproducibility work passes.



The next major risk is not whether the code runs.



The next major risk is whether the numerical method is scientifically strong enough for larger turbulence claims.



\## Recommended Next Phase



Recommended next phase:



Phase 8A — Benchmark-Oriented Solver Validation



Purpose:



Validate the active solver against controlled numerical expectations before running larger turbulence experiments.



Suggested Phase 8A checks:



\- Confirm active solver path again

\- Add a no-forcing decay test

\- Check energy/enstrophy behavior under no forcing

\- Check timestep sensitivity

\- Check resolution sensitivity

\- Compare default forcing vs multimode forcing under matched conditions

\- Decide whether finite-difference advection is acceptable or whether Arakawa/full spectral advection is needed



\## Conclusion



Phase 7E closes the reproducibility stage.



Phase 7B and Phase 7D together show that forcing geometry controls whether the spectrum remains locked at k=3 or broadens into nearby low-k shells.



The project remains scientifically conservative:



Low-k spectral broadening is supported.



k^-3 scaling is not supported.



Benchmark validation should come before larger turbulence claims.

