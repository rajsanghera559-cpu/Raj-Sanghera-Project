\# Phase 7D Multimode Smoke Audit Report



\## Checkpoint



\- Branch: phase4\_validation

\- Runner commit: 4173531

\- Runner tag: v0.4.15-phase7D-multimode-smoke-runner

\- Runner script: run\_phase7D\_multimode\_smoke.py

\- Audit script: phase7d\_multimode\_smoke\_audit.py

\- Audit output: PHASE7D\_MULTIMODE\_SMOKE\_AUDIT.csv

\- Source run: experiments/runs/run\_2026-07-02\_21-57-26



\## Purpose



Phase 7D tested whether the Phase 6D RMS-matched deterministic low-k multimode forcing method could reproduce low-k spectral broadening in a short fresh smoke run.



This phase does not attempt to prove turbulence, k^-3 scaling, or inertial-range behavior.



The purpose is reproducibility of the multimode forcing effect.



\## Run Configuration



| Quantity | Value |

|---|---:|

| Mode | phase7D\_multimode\_smoke |

| Re | 1000 |

| Grid | 64 x 64 |

| dt | 0.005 |

| steps | 1001 |

| Expected diagnostic steps | \[0, 500, 1000] |

| Forcing | phase6D\_rms\_matched\_deterministic\_low\_k\_multimode |



\## Forcing Configuration



| Quantity | Value |

|---|---:|

| Forcing type | rms\_matched\_deterministic\_low\_k\_multimode |

| Base single-mode RMS | 0.005 |

| Raw multimode RMS | 0.7171994143890527 |

| Matched multimode RMS | 0.005 |



Forcing terms:



\- sin(2X)cos(2Y)

\- 0.75\*sin(3X)cos(Y)

\- 0.50\*sin(X)cos(4Y)

\- 0.35\*cos(4X-2Y)



\## Metadata Checks



| Check | Result |

|---|---:|

| Run ID | run\_2026-07-02\_21-57-26 |

| Status completed | PASS |

| Git commit starts with 4173531 | PASS |

| Git dirty false | PASS |

| Mode expected | PASS |

| Config expected | PASS |

| Forcing stats expected | PASS |



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



\## Spectrum Checks



| Check | Result |

|---|---:|

| Spectrum rows | 45 |

| Spectrum finite | PASS |

| Spectrum nonnegative | PASS |

| Mode counts positive | PASS |



\## Energy Consistency



| Quantity | Result |

|---|---:|

| Final diagnostics energy | 3.016811179391e-05 |

| Sum spectrum E(k) | 3.016811179391e-05 |

| Relative error | 0.000000000000e+00 |

| Energy-spectrum check | PASS |



\## E(k=4) Consistency



| Quantity | Result |

|---|---:|

| Diagnostics E\_k4 | 3.743865030854e-06 |

| Spectrum E(k=4) | 3.743865030854e-06 |

| Relative error | 0.000000000000e+00 |

| E(k=4) check | PASS |



\## Multimode Broadening Check



| Quantity | Result |

|---|---:|

| Peak k | 3 |

| Peak fraction | 8.758728449890e-01 |

| k=3 fraction | 8.758728449890e-01 |

| k=4 fraction | 1.241000781365e-01 |

| k>=5 fraction | 1.264900840531e-05 |

| Peak k expected | PASS |

| k=4 meaningful >1% | PASS |

| Single-shell broken | PASS |

| Low-k broadening result | PASS |



\## Interpretation



The Phase 7D fresh multimode smoke run completed successfully.



The run was launched from a clean committed state.



The output files are internally consistent.



The spectrum remains peaked at k=3, but the pure k=3 single-shell lock is broken because k=4 carries meaningful energy.



The k=4 fraction was approximately 12.41%.



This reproduces the central Phase 6D finding in a short N=64 smoke run: RMS-matched multimode forcing broadens the spectrum across low-k shells.



\## What This Confirms



Phase 7D confirms that the current committed code can reproduce multimode-forcing low-k spectral broadening in a fresh short run.



\## What This Does Not Confirm



Phase 7D does not prove k^-3 scaling.



Phase 7D does not prove turbulence.



Phase 7D does not prove an inertial-range cascade.



Phase 7D does not benchmark-validate the solver.



\## Overall Result



Phase 7D multimode smoke audit: PASS



\## Conclusion



Phase 7D passes as a controlled multimode smoke run and audit.



The correct claim is:



RMS-matched multimode forcing reproducibly breaks the pure k=3 single-shell lock and produces low-k spectral broadening.



The project should still not claim k^-3 scaling.



Recommended next step:



Phase 7E — Phase 7 Reproducibility Summary and Decision Gate



The next phase should compare Phase 7B default forcing and Phase 7D multimode forcing side by side, then decide whether to proceed toward benchmark validation or a larger controlled multimode experiment.

