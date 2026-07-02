\# Phase 7A.2 Time-Series Sanity Report



\## Checkpoint



\- Branch: phase4\_validation

\- Previous tag: v0.4.9-phase7A-solver-sanity-audit

\- Source run: experiments/runs/run\_2026-07-01\_01-53-34

\- Source file: diagnostics.csv

\- Audit script: phase7a2\_time\_series\_sanity.py

\- Audit output: PHASE7A2\_TIME\_SERIES\_SANITY.csv



\## Purpose



Phase 7A.2 checks the time-series behavior of the saved Phase 6D diagnostics.



This check does not rerun the solver.



The goal is to confirm that the diagnostic time series is finite, ordered, nonnegative, and free from obvious large negative jumps.



\## File Shape



| Quantity | Result |

|---|---:|

| Rows | 20 |

| First step | 0 |

| Last step | 9500 |

| Cadence | 500 |



\## Basic Checks



| Check | Result |

|---|---:|

| Finite values | PASS |

| Steps increasing | PASS |

| Cadence consistent | PASS |

| Energy nonnegative | PASS |

| Enstrophy nonnegative | PASS |

| E\_k4 nonnegative | PASS |



\## Energy Time Series



| Quantity | Result |

|---|---:|

| Initial energy | 3.162144516939e-11 |

| Final energy | 1.763401582438e-03 |

| Minimum energy | 3.162144516939e-11 |

| Maximum energy | 1.763401582438e-03 |

| Final / initial ratio | 5.576600e+07 |

| Large negative energy jump check | PASS |



\## Enstrophy Time Series



| Quantity | Result |

|---|---:|

| Initial enstrophy | 3.124827045589e-10 |

| Final enstrophy | 1.599716952717e-02 |

| Minimum enstrophy | 3.124827045589e-10 |

| Maximum enstrophy | 1.599716952717e-02 |

| Final / initial ratio | 5.119378e+07 |

| Large negative enstrophy jump check | PASS |



\## E(k=4) Time Series



| Quantity | Result |

|---|---:|

| Initial E\_k4 | 4.093773907978e-12 |

| Final E\_k4 | 1.023175258923e-04 |

| Minimum E\_k4 | 4.093773907978e-12 |

| Maximum E\_k4 | 1.023175258923e-04 |

| Final / initial ratio | 2.499345e+07 |



\## Interpretation



The large growth ratios are expected because the run began from near-zero vorticity and was driven by forcing.



The diagnostics do not show NaN values, negative energy, negative enstrophy, inconsistent step ordering, inconsistent cadence, or obvious large negative jumps.



The result supports the internal usability of the saved Phase 6D diagnostic time series.



\## Limitations



This check only inspects the saved diagnostic cadence.



The diagnostics were written every 500 steps, so this check does not prove that every internal solver step behaved smoothly.



This check does not validate the solver against a known benchmark and does not support a k^-3 scaling claim.



\## Overall Result



Phase 7A.2 time-series sanity check: PASS



\## Conclusion



Phase 7A.2 passes as a time-series sanity check.



Recommended next step:



Phase 7A.3 — create a compact Phase 7A combined validation summary, then decide whether to move into benchmark-style validation or controlled reruns.

