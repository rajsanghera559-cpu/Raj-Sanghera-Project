\# Phase 6A Reynolds Ladder Report



\## Checkpoint



\- Branch: phase4\_validation

\- Ladder runner commit: 2a9ac92

\- Previous checkpoint: v0.3.4-phase5C-report



\## Purpose



Phase 6A tested a controlled Reynolds-number ladder using the fixed solver pipeline.



This phase verifies that the solver can run multiple Reynolds numbers from a clean Git state, generate completed run folders, and pass the inventory audit.



This phase does not yet prove turbulence scaling or k^-3 robustness.



\## Ladder Configuration



The ladder used:



\- Grid: 128 x 128

\- dt: 0.005

\- steps: 1000

\- Reynolds values: 100, 250, 500, 1000

\- Output folder: experiments/runs/

\- Audit script: run\_inventory.py



\## Successful Ladder Runs



The ladder was executed twice from the same clean commit.



\### Ladder Pass 1



| Run | Re | Status | Commit | Git Dirty | Energy | Sum E(k) | Result |

|---|---:|---|---|---|---:|---:|---|

| run\_2026-06-30\_23-43-13 | 100 | completed | 2a9ac92 | False | 8.051111e-06 | 8.051111e-06 | PASS |

| run\_2026-06-30\_23-43-17 | 250 | completed | 2a9ac92 | False | 9.054302e-06 | 9.054302e-06 | PASS |

| run\_2026-06-30\_23-43-22 | 500 | completed | 2a9ac92 | False | 9.420785e-06 | 9.420785e-06 | PASS |

| run\_2026-06-30\_23-43-26 | 1000 | completed | 2a9ac92 | False | 9.610517e-06 | 9.610517e-06 | PASS |



\### Ladder Pass 2



| Run | Re | Status | Commit | Git Dirty | Energy | Sum E(k) | Result |

|---|---:|---|---|---|---:|---:|---|

| run\_2026-06-30\_23-45-06 | 100 | completed | 2a9ac92 | False | 8.051111e-06 | 8.051111e-06 | PASS |

| run\_2026-06-30\_23-45-11 | 250 | completed | 2a9ac92 | False | 9.054302e-06 | 9.054302e-06 | PASS |

| run\_2026-06-30\_23-45-14 | 500 | completed | 2a9ac92 | False | 9.420785e-06 | 9.420785e-06 | PASS |

| run\_2026-06-30\_23-45-18 | 1000 | completed | 2a9ac92 | False | 9.610517e-06 | 9.610517e-06 | PASS |



\## Inventory Result



The latest inventory audit reported:



```text

Total runs: 12

PASS:       8

FAIL:       4

