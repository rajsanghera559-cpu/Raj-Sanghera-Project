\# Phase 7B Reproducibility Smoke Run Report



\## Checkpoint



\- Branch: phase4\_validation

\- Runner commit: 7e86077

\- Runner tag: v0.4.12-phase7B-smoke-runner

\- Runner script: run\_phase7B\_smoke.py

\- Run folder: experiments/runs/run\_2026-07-02\_14-48-55



\## Purpose



Phase 7B performed a short fresh smoke run using the currently committed active solver path.



The purpose was not to test turbulence, k^-3 scaling, or inertial-range behavior.



The purpose was to verify that the current code can still generate a new run folder, metadata, diagnostics, and spectrum output without crashing.



\## Configuration



| Quantity | Value |

|---|---:|

| Mode | phase7B\_reproducibility\_smoke |

| Re | 1000 |

| Grid | 64 x 64 |

| dt | 0.005 |

| steps | 1001 |

| Forcing | default\_solver\_forcing |

| Expected diagnostic steps | 0, 500, 1000 |



\## Metadata Result



| Field | Result |

|---|---|

| run\_id | run\_2026-07-02\_14-48-55 |

| status | completed |

| git\_commit | 7e860779bd863eeb942976448e41a7d516eee24a |

| git\_dirty | false |

| started\_at | 2026-07-02T14:48:55.304221 |

| updated\_at | 2026-07-02T14:48:56.327076 |



\## Diagnostic Output



| Step | Energy | Enstrophy | E(k=4) |

|---:|---:|---:|---:|

| 0 | 3.9060937515625016e-11 | 3.12487500125e-10 | 4.158135192827272e-43 |

| 500 | 9.610517174911415e-06 | 7.688413739929126e-05 | 1.6379947291378764e-37 |

| 1000 | 3.7609456671298174e-05 | 3.008756533703853e-04 | 9.912415967546596e-37 |



\## Spectrum Result



The final spectrum was dominated by k=3.



The first spectral rows showed:



| k | E(k) | mode\_count |

|---:|---:|---:|

| 1 | 2.4696238438223244e-36 | 8 |

| 2 | 7.52337010364056e-36 | 12 |

| 3 | 3.760945667129817e-05 | 16 |

| 4 | 9.912415967546596e-37 | 32 |

| 5 | 5.283800216312821e-37 | 28 |



\## Interpretation



The Phase 7B smoke run completed successfully.



The run produced:



\- metadata.json

\- diagnostics.csv

\- spectrum.csv



The diagnostic steps were exactly as expected:



\- step 0

\- step 500

\- step 1000



Energy and enstrophy remained finite and nonnegative in the printed diagnostics.



Because this smoke run used the default single-mode solver forcing, the final spectrum remained concentrated at k=3. That is expected and does not contradict the Phase 6D multimode-forcing result.



\## What This Confirms



Phase 7B confirms that the current committed code can still execute a fresh short run and write usable output files.



\## What This Does Not Confirm



Phase 7B does not prove k^-3 scaling.



Phase 7B does not prove turbulence.



Phase 7B does not benchmark-validate the solver.



Phase 7B does not test the multimode forcing configuration.



\## Overall Result



Phase 7B reproducibility smoke run: PASS



\## Conclusion



Phase 7B passes as a controlled reproducibility smoke run.



Recommended next step:



Phase 7C — Fresh Run Output Audit



The next phase should audit the newly created Phase 7B run folder for finite values, energy-spectrum consistency, metadata consistency, and clean git provenance.

