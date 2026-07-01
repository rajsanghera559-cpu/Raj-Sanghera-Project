\# Phase 6D Multimode Forcing Report



\## Checkpoint



\- Branch: phase4\_validation

\- Runner commit: 70e70f3

\- Analysis commit: 6a4225f

\- Tag: v0.4.5-phase6D-multimode-forcing-analysis

\- Previous tag: v0.4.4-phase6C-perturbed-ic-analysis



\## Purpose



Phase 6D tested whether changing the forcing geometry could break the single-shell k=3 lock observed in Phases 6A, 6B, and 6C.



The solver core was not changed. The experiment used a runner that temporarily replaced the forcing function with RMS-matched deterministic low-k multimode forcing.



\## Configuration



\- Re: 1000

\- Grid: 128 x 128

\- dt: 0.005

\- steps: 10000

\- Initial condition: zero vorticity

\- Forcing: RMS-matched deterministic low-k multimode forcing

\- Output folder: experiments/runs/



\## Phase 6D Run



| Run | Re | Status | Commit | Git Dirty | Energy | Sum E(k) | Result |

|---|---:|---|---|---|---:|---:|---|

| run\_2026-07-01\_01-53-34 | 1000 | completed | 70e70f3 | False | 1.763402e-03 | 1.763402e-03 | PASS |



\## Spectrum Result



Compared with the Phase 6B single-forcing baseline:



| Case | Peak k | Peak Fraction | E(k=3) Fraction | E(k=4) Fraction | E(k>=5) Fraction | Active Shells >1% | Active Shells >0.1% |

|---|---:|---:|---:|---:|---:|---:|---:|

| Phase 6B baseline | 3 | 1.000000 | 1.000000 | \~0 | \~0 | 1 | 1 |

| Phase 6D multimode forcing | 3 | 0.8779025 | 0.8779025 | 0.05802282 | 0.01057326 | 4 | 7 |



\## Interpretation



Phase 6D broke the pure k=3 single-shell lock.



Energy was distributed across multiple low-k shells, and there was measurable energy at k>=5.



This suggests that the earlier single-shell behavior was primarily caused by the single-mode forcing geometry, not by runtime alone and not by lack of initial perturbation alone.



\## Limitations



Phase 6D does not prove k^-3 scaling.



Most energy remains concentrated in low-k shells. The observed broadening is forcing-driven low-k support, not yet evidence of an inertial-range cascade.



\## Conclusion



Phase 6D passes as a controlled forcing-geometry test.



Next step: inspect the detailed Phase 6D spectrum table before attempting slope fitting or stronger turbulence claims.

