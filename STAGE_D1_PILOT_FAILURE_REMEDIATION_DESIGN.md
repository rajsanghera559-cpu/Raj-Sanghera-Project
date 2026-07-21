# Stage D1 Pilot Failure Remediation Design

## 1. Status and authority

This document is a design-only remediation overlay for the failed Stage D1
separate-trajectory pilot.

It authorizes only:

- creation of this Markdown design;
- static inspection of this Markdown design;
- later archival of this design after a separate explicit instruction.

It does **not** authorize:

- creation or modification of a numerical runner;
- modification of the archived failed runner;
- modification of protected source;
- modification or deletion of the failed partial evidence;
- modification of Stage B or Stage C evidence;
- relaxation of any numerical-integrity threshold;
- numerical execution or a forensic numerical probe;
- a Stage D1 retry;
- Stage D2 output or execution;
- the full Stage D comparison;
- scientific trajectory classification.

## 2. Relationship to frozen records

This design is subordinate to and must be read with:

1. `STAGE_D_SEPARATELY_ADVANCED_ADVECTION_FORM_TRAJECTORY_COMPARISON_DESIGN.md`;
2. `STAGE_D1_PILOT_FAILURE_DIAGNOSIS.md`;
3. the archived failed runner
   `run_stage_d_separate_trajectory_pilot.py`;
4. the preserved failed partial evidence bundle.

This overlay changes only the mask-ledger implementation and failure
observability requirements needed to remediate the diagnosed Stage D1 runner.
All original scientific boundaries and all unaffected implementation contracts
remain frozen.

## 3. Frozen ancestry and identities

| Item | Frozen identity |
|---|---|
| Branch | `phase4_validation` |
| Original Stage D design commit | `5bb62e25be4c789bc730e9f04fe34f1921ecae1e` |
| Original Stage D design SHA-256 | `491B1118B40523CF4EC340E40C38CAC462C8985377809D09484571884FC445BF` |
| Failed Stage D1 runner commit | `a5397a6b106591dff7219f2b7b53dda2c35f57cc` |
| Failed Stage D1 runner SHA-256 | `BF23D8C755810988821B1A36CBD3023EB839B9EF8BE0EF5F31B808EF239E14B7` |
| Failure-diagnosis commit | `0f5fb1c1901db39334f1d55e87ac84da04320e5e` |
| Failure-diagnosis SHA-256 | `526E4243C40D850F3CA5F158AB04F783283C299754C6CA759FAB5EA7536743C0` |
| Stage B exact-ledger runner SHA-256 | `970AE47D4DF69819FA6D831557FC2679D843B860D901CF367361A3A34126E246` |

Any future runner created under this design must be added in a new commit whose
parent is the eventual archived commit of this remediation design. That runner
commit may change exactly one file: the new remediated runner.

## 4. Frozen failed execution identity

| Field | Frozen value |
|---|---|
| Run ID | `stage_d_separate_trajectory_pilot_20260721T041525Z_a5397a6` |
| Status | `failed` |
| Failed trajectory | `TRAJ_BASE_FD_ADVECTIVE_V1` |
| Failed gate | `trajectory_update_integrity` |
| Failed loop index | `0` |
| Last completed loop | `-1` |
| Completed numerical updates | `0` |
| Completed integrity rows | `0` |
| Partial inventory SHA-256 | `8685631746E8F7F7B6E97C95775E6B6A7BF8155A14364ED90458B563FE0F7EB9` |

The preserved failed directory must remain byte-for-byte unchanged. It must not
be renamed, moved, deleted, overwritten, supplemented, or used as an output
directory for a remediated attempt.

## 5. Confirmed defects being remediated

The failure diagnosis established two implementation defects.

### 5.1 Mask-ledger definition divergence

The failed Stage D1 runner used whole-field subtraction
`(z_filtered - z_unfiltered) / dt` as its mask ledger rate and compared it with
discarded-field physical energy. The frozen Stage B ledger instead uses the
discarded-field physical energy as the exact mask rate and cross-checks that
energy against its Fourier-space Parseval expression.

### 5.2 Failure-observability deficiency

The failed runner combined five integrity conditions into one Boolean and
raised before returning or persisting their values. It recorded a generic gate
and no failed stage. The preserved evidence therefore cannot identify the exact
failed sub-gate.

The remediation shall correct both defects without changing thresholds or
scientific scope.

## 6. Non-findings

The failed pilot did not establish:

- a scientific trajectory disagreement;
- failure or superiority of an advection method;
- temporal or spatial convergence;
- turbulence, cascade, inertial-range, or `k^-3` behavior;
- a Lyapunov exponent or predictability horizon;
- physical validation;
- production readiness;
- authority to replace the baseline.

No remediation language may convert the implementation failure into any such
claim.

## 7. Remediation objective

A future remediated Stage D1 runner, if separately authorized for creation,
must be capable of:

1. reproducing the frozen Stage B mask ledger by definition;
2. applying a true physical/Fourier discarded-field Parseval cross-check;
3. keeping whole-field filter bookkeeping separate from the exact mask rate;
4. recording every post-filter integrity component before a failure is raised;
5. assigning a deterministic failed sub-gate and nonempty failed stage;
6. preserving all original Stage D1 trajectory and row-count contracts;
7. preserving all original prohibitions.

This objective does not authorize implementation or execution.

## 8. Future remediated runner identity

The only future runner name permitted by this design is:

```text
run_stage_d_separate_trajectory_pilot_remediated.py
```

The archived failed runner:

```text
run_stage_d_separate_trajectory_pilot.py
```

must remain unchanged and present at its frozen hash.

The remediated runner must offer exactly two command modes:

```text
inspect
run
```

The `inspect` mode must be repository-bound and nonnumerical. The `run` mode
must remain blocked operationally until a separate explicit one-execution
authorization is given after runner archival and preauthorization inspection.

## 9. Frozen numerical configuration

| Parameter | Frozen value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `1/1000` |
| Time step | `0.005` |
| Updates per trajectory | `3060` |
| Loop indices | `0..3059` |
| Final loop index | `3059` |
| Final physical time | `15.300` |
| Trajectories | `7` |
| Trajectory pairs | `21` |

The forcing construction, forcing RMS target, forcing hash, initial state, dealias
mask, solver configuration, and archived source identities remain exactly those
of the failed runner and original Stage D design.

## 10. Frozen trajectory registry

The future runner must retain these seven IDs and operator kinds in this exact
order:

| Order | Trajectory ID | Operator kind |
|---:|---|---|
| 1 | `TRAJ_BASE_FD_ADVECTIVE_V1` | `fd_advective` |
| 2 | `TRAJ_FD_ADVECTIVE_PROJECTED_V1` | `fd_advective_projected` |
| 3 | `TRAJ_FD_CONSERVATIVE_V1` | `fd_conservative` |
| 4 | `TRAJ_FD_SKEW_V1` | `fd_skew` |
| 5 | `TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2` | `ps_advective_rc_unprojected` |
| 6 | `TRAJ_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2` | `ps_advective_rc_projected` |
| 7 | `TRAJ_ARAKAWA_V1` | `arakawa` |

No eighth trajectory, fallback trajectory, shared baseline state, or Stage C
accepted-update reuse is permitted.

## 11. Independent ownership and RK2 contract

Every trajectory must own an independent contiguous `float64` state array.

For every loop and every trajectory:

1. copy the trajectory's current state into a read-only snapshot;
2. compute that trajectory's stage-1 operator from its own snapshot;
3. construct its own RK2 stage array;
4. compute its stage-2 operator from its own stage array;
5. construct its own unfiltered candidate;
6. construct its own filtered accepted candidate;
7. evaluate all integrity components;
8. accept the candidate only after every mandatory gate passes.

No state, stage, unfiltered candidate, accepted candidate, forcing array, or
real-compatible wavenumber array may share memory in a forbidden pairing.
Forward and reverse sentinel evaluation orders must remain exactly invariant.

## 12. Real-compatible pseudo-spectral contract

Both pseudo-spectral trajectories must retain local, independently owned copies
of the solver wavenumbers.

The local real-compatible copies must:

- be contiguous;
- not share memory with solver wavenumbers or trajectory states;
- have the Nyquist entries zeroed on the applicable axes;
- remain read-only after construction;
- remain byte-identical throughout the run.

The solver's protected wavenumber arrays must not be mutated. Complex inverse
transform values must be retained long enough to calculate the frozen
imaginary-ratio diagnostics.

## 13. Corrected exact mask ledger

For each trajectory and RK2 candidate, define:

```text
unfiltered_hat = fft2(unfiltered)
discarded_hat = where(deal, 0, unfiltered_hat)
removed_physical_complex = ifft2(discarded_hat)
```

Then define the discarded-component physical-space enstrophy loss:

```text
mask_loss_physical = 0.5 * mean(abs(removed_physical_complex)**2)
```

Define the independent Fourier-space Parseval value:

```text
mask_loss_spectral = sum(abs(discarded_hat)**2) / (2 * N**4)
```

Define the exact post-mask ledger contribution:

```text
mask_enstrophy_change_rate = -mask_loss_physical / dt
```

The filtered ledger must use exactly this
`mask_enstrophy_change_rate`. The baseline field of the same name must therefore
be definitionally aligned with the Stage B archive.

The remediated runner must not label a quantity derived from an inverse FFT as
the independent Fourier-space value.

## 14. Corrected mask Parseval cross-check

Define:

```text
mask_crosscheck_residual = mask_loss_physical - mask_loss_spectral
```

and:

```text
normalized_mask_crosscheck =
    abs(mask_crosscheck_residual)
    / max(abs(mask_loss_physical), abs(mask_loss_spectral), RESIDUAL_FLOOR)
```

The frozen pass limit remains:

```text
normalized_mask_crosscheck <= 1e-12
```

The limit must not be relaxed, rescaled after observation, replaced with an
absolute-only test, or skipped for near-zero discarded energy.

## 15. Separate whole-field filter bookkeeping

Whole-field subtraction remains useful but must be a distinct diagnostic:

```text
observed_mask_change_rate = (z_filtered - z_unfiltered) / dt
filter_bookkeeping_residual =
    observed_mask_change_rate - mask_enstrophy_change_rate
```

It must not replace:

- `mask_loss_physical`;
- `mask_loss_spectral`;
- `mask_enstrophy_change_rate`;
- `normalized_mask_crosscheck`.

If normalized, the bookkeeping residual must use the frozen ledger scale, not
the tiny mask term alone. It is an additional numerical diagnostic and not a
substitute threshold for the Parseval gate.

## 16. Exact enstrophy ledger

For every trajectory, preserve the exact RK2 enstrophy decomposition:

```text
observed_unfiltered_rate
  = rk2_advection_rate
  + rk2_viscous_rate
  + rk2_forcing_rate
  + rk2_quadratic_remainder_rate
```

and:

```text
observed_filtered_rate
  = unfiltered_ledger_rate
  + mask_enstrophy_change_rate
```

with residuals recorded explicitly.

The quadratic remainder remains:

```text
dt / 8 * mean((total_2 - total_1)**2)
```

No advection, viscosity, forcing, RK2 remainder, or mask term may be omitted or
reassigned.

## 17. Frozen integrity limits

| Gate | Frozen limit |
|---|---:|
| Baseline archive relative difference | `1e-11` |
| Baseline absolute floor | `1e-14` |
| Normalized filtered ledger closure | `1e-10` |
| Normalized unfiltered ledger closure | `1e-10` |
| Mask physical/Fourier cross-check | `1e-12` |
| Centered skew identity | `1e-15` |
| Centered advective/conservative identity | `1e-12` |
| Arakawa sign identity | `1e-12` |
| Pseudo-spectral projection identity | `1e-12` |
| Real-compatible imaginary ratio | `1e-13` |
| State memory aliasing | none |
| State mutation | exact zero |
| Order-invariance normalized difference | `1e-15` |
| Nonfinite arrays or scalars | none |

No implementation may tune a limit using the failed run or a future remediated
run.

## 18. Independent post-filter sub-gates

The failed compound label `trajectory_update_integrity` must not be the sole
failure identity. The future runner must calculate and retain these named
sub-gates independently:

1. `post_filter_update_finite`;
2. `unfiltered_ledger_closure`;
3. `filtered_ledger_closure`;
4. `mask_parseval_crosscheck`;
5. `real_compatible_imaginary_ratio`.

If multiple sub-gates fail in the same preview, the runner must record all
failed sub-gates and select the primary failure deterministically in the order
listed above.

The failure stage for these gates must be:

```text
post_filter_integrity
```

Earlier failures must use a specific nonempty stage such as `stage_1_operator`,
`rk2_stage_state`, `stage_2_operator`, or `accepted_state_projection`.

## 19. Failure snapshot contract

Before raising any numerical-integrity exception after the output directory
exists, the runner must atomically update `run_metadata.json` with a
`failure_snapshot` object containing, where applicable:

- trajectory ID;
- loop index;
- completed steps before failure;
- failed stage;
- primary failed sub-gate;
- all failed sub-gates;
- every sub-gate Boolean;
- every observed sub-gate value;
- every applicable limit;
- `z_current`, `z_stage`, `z_unfiltered`, and `z_filtered`;
- `mask_loss_physical`;
- `mask_loss_spectral`;
- `mask_enstrophy_change_rate`;
- `observed_mask_change_rate`;
- `filter_bookkeeping_residual`;
- normalized mask cross-check;
- normalized unfiltered closure;
- normalized filtered closure;
- maximum imaginary ratio;
- state hashes available at the failure point.

Nonfinite values must be represented in a deterministic JSON-safe form and
must not prevent the failure snapshot from being written.

## 20. Failed integrity-row preservation

When the post-filter arrays and scalar values can be serialized safely, the
runner must write and flush the failing trajectory's integrity row with
`integrity_pass = False` before raising.

That failed row is partial evidence. It does not count as a completed accepted
update. Successful row-count contracts apply only to a completed pilot.

If a failure occurs too early to form the row, the metadata failure snapshot
must still record all values available at that point and explain why the row was
not written.

## 21. Remediated integrity schema

The successful remediated integrity CSV must retain all original fields and add:

- `mask_loss_physical`;
- `mask_loss_spectral`;
- `mask_enstrophy_change_rate`;
- `observed_mask_change_rate`;
- `filter_bookkeeping_residual`;
- `normalized_filter_bookkeeping`;
- `normalized_mask_crosscheck`;
- `update_finite_pass`;
- `unfiltered_closure_pass`;
- `filtered_closure_pass`;
- `mask_crosscheck_pass`;
- `imaginary_ratio_pass`;
- `failed_subgates`.

All headers must be unique. The successful integrity row count remains exactly
`21,420`.

## 22. Baseline Stage B reproduction

The baseline trajectory must reproduce all `3,060 / 3,060` frozen Stage B
ledger rows using the original relative tolerance and absolute floor.

In particular, these Stage B values must be calculated from definitionally
aligned quantities:

- `mask_enstrophy_change_rate`;
- unfiltered closure terms;
- filtered closure terms;
- exact RK2 remainder;
- observed filtered enstrophy rate.

No archived Stage B value may be copied into a live trajectory ledger or used
as the trajectory update. Stage B rows are references only.

## 23. Frozen sampling and successful row counts

| Output category | Exact successful rows |
|---|---:|
| Baseline Stage B ledger reproductions | `3,060 / 3,060` |
| Trajectory diagnostics | `2,149` |
| Pairwise divergence diagnostics | `6,447` |
| Per-step integrity rows | `21,420` |
| Sentinel cross-check rows | `21` |

Diagnostic loops remain every tenth loop from `0` through `3050`, plus loop
`3059`. Sentinel loops remain `0`, `3058`, and `3059`.

## 24. Sentinel and order-invariance contract

At every sentinel loop, evaluate all seven trajectory previews in both frozen
forward order and exact reverse order from independent snapshots.

For each trajectory:

- accepted-state hashes must be identical;
- normalized accepted-state difference must not exceed `1e-15`;
- ledger scalar difference must be exactly zero;
- the Stage C operator helper cross-check must pass;
- no forward or reverse preview may mutate a snapshot or another preview.

The sentinel output remains `21` rows on successful completion.

## 25. Remediated output isolation

The future remediated runner must use:

```text
experiments/advection_form_trajectory_pilot_remediated/
```

with run directories prefixed:

```text
stage_d_separate_trajectory_pilot_remediated_
```

It must never write within the failed output root. The remediated output root
must be Git-ignored before execution and must contain no prior directory with
the frozen remediated prefix.

## 26. Successful output file set

A successful remediated pilot must contain exactly eight files:

1. `run_metadata.json`;
2. `trajectory_pilot_diagnostics.csv`;
3. `trajectory_pilot_pairwise_divergence.csv`;
4. `trajectory_pilot_integrity_per_step.csv`;
5. `trajectory_pilot_sentinel_crosscheck.csv`;
6. `trajectory_pilot_summary.json`;
7. `STAGE_D_REMEDIATED_SEPARATE_TRAJECTORY_PILOT_REPORT.md`;
8. `file_inventory.csv`.

No Stage D2 file, category file, convergence fit, Lyapunov fit, or method-ranking
file is permitted.

Every predicted and actual output file must remain below `40 MB`. The enlarged
integrity schema must receive a conservative static size estimate below that
limit before any run directory is created.

## 27. Failure output policy

On failure after output-directory creation, preserve:

- metadata with the complete failure snapshot;
- all CSV headers;
- all completed rows;
- a failed integrity row when safely available;
- last accepted update by trajectory;
- primary failed sub-gate;
- all failed sub-gates;
- failed trajectory, loop, and nonempty stage;
- source and evidence identities;
- partial file inventory.

Print:

```text
STAGE D REMEDIATED SEPARATE-TRAJECTORY PILOT: FAILED
Failed trajectory: <trajectory>
Failed gate: <specific-sub-gate>
Failed loop index: <loop>
Failed stage: <nonempty-stage>
Partial evidence preserved at: <path>
Do not rerun automatically.
```

Do not delete or rewrite any failed partial output.

## 28. Successful pass rule

Print:

```text
STAGE D REMEDIATED SEPARATE-TRAJECTORY PILOT: PASS
```

only if:

1. all seven independently owned trajectories accept exactly `3,060` updates;
2. the final accepted loop index is `3059` for every trajectory;
3. the baseline reproduces `3,060 / 3,060` Stage B rows;
4. all successful output row counts are exact;
5. all exact ledgers and named sub-gates pass;
6. all arrays and scalars remain finite;
7. all memory-alias and mutation gates pass;
8. all real-compatible Nyquist and imaginary-ratio gates pass;
9. all sentinel order and Stage C helper gates pass;
10. all source and evidence identities remain frozen;
11. the successful output set is exactly eight files;
12. no file reaches `40 MB`;
13. no scientific trajectory classification is produced;
14. no Stage D2 path is present or executed.

## 29. Repository-bound static inspection

The future runner's `inspect` mode must verify, without project imports or
numerical execution:

- active branch and exact repository ancestry;
- remediation-design commit identity and SHA-256;
- failure-diagnosis commit identity and SHA-256;
- failed runner commit identity and SHA-256;
- preserved failed inventory and all six partial-file hashes;
- protected-source and Stage B/Stage C evidence identities;
- exact seven-entry registry and 21 pairs;
- exact update, sampling, sentinel, and row-count constants;
- exact integrity thresholds;
- exact corrected mask formulas by AST and token checks;
- presence of the Fourier Parseval sum expression;
- absence of whole-field subtraction as the mask ledger rate;
- separate filter-bookkeeping fields;
- structured failure-snapshot fields;
- nonempty failure-stage assignments;
- independent state and RK2 stage allocation;
- local Nyquist-zeroed wavenumber copies;
- no solver-wavenumber mutation;
- no protected or selectable solver `run()` calls;
- no Stage C accepted-state reuse;
- unique output headers;
- exactly eight predicted successful outputs;
- every predicted output below `40 MB`;
- no classification, convergence, spectral-slope, Lyapunov, or Stage D2 code;
- no Git mutation in inspection mode.

Inspection must print explicitly:

```text
Project modules imported: NO
Solver constructed: NO
Numerical timesteps executed: NO
Files written: NO
Git mutations: NONE
Remediated numerical execution authorized by inspection: NO
Stage D2 authorized: NO
```

## 30. Future run preflight

Even after runner creation, static inspection, archival, and remote
synchronization, execution remains unauthorized until a separate read-only
preauthorization gate passes and the user gives a new explicit one-execution
instruction.

The future run preflight must require:

- branch `phase4_validation`;
- clean working tree;
- exact archived remediated-runner commit;
- runner commit parent equal to the remediation-design commit;
- runner commit changing exactly one file;
- committed and working runner bytes identical;
- remote branch equal to local HEAD;
- all protected and evidence identities frozen;
- preserved failed evidence unchanged;
- no prior remediated output directory;
- remediated output path Git-ignored;
- every predicted file below `40 MB`.

A failed preflight must create no run directory and execute no numerical step.

## 31. One-remediated-attempt policy

The prior Stage D1 execution remains the only execution authorized under the
failed-runner contract.

This design does not authorize a second attempt. If all design, creation,
inspection, archival, and preauthorization gates later pass, a separate exact
instruction may authorize one remediated Stage D1R attempt.

There shall be:

- no automatic retry;
- no retry after failure without another design decision;
- no hidden warm-up execution;
- no numerical inspection path;
- no fallback to the archived failed runner;
- no automatic transition to Stage D2.

## 32. Protected-source and evidence prohibition

No future remediation step may modify:

- `project/solver/spectral_solver.py`;
- `project/solver/advection_operators.py`;
- `project/solver/selectable_advection_solver.py`;
- any other protected numerical source;
- Stage B evidence or its runner;
- Stage C evidence or its runner;
- the archived failed Stage D1 runner;
- the preserved failed Stage D1 output;
- the archived failure diagnosis;
- the archived original Stage D design.

Any identity mismatch is a hard stop.

## 33. Stage D2 prohibition

The remediation design, future runner, inspections, and any separately
authorized Stage D1R pilot must contain no Stage D2 output or execution path.

No scientific trajectory category, method ranking, baseline replacement,
operational comparison label, or full-run launch may be emitted.

Stage D2 remains blocked even if a remediated pilot later passes. A passing
pilot would require a separate evidence audit, archive, and explicit design
decision before Stage D2 could be considered.

## 34. Required development sequence

The controlled sequence is:

1. create and statically inspect this remediation design;
2. archive only this design in a clean commit;
3. separately authorize creation of the remediated runner;
4. create and statically inspect that runner without numerical execution;
5. archive only the remediated runner in a clean child commit;
6. run a read-only repository and evidence preauthorization gate;
7. obtain explicit authority for one remediated numerical attempt;
8. execute at most once;
9. preserve success or failure evidence;
10. audit and archive that evidence before any later decision.

No step authorizes the next step automatically.

## 35. Current checkpoint

At completion of this document:

- failed Stage D1 result archived: **YES**;
- failed partial evidence preserved: **YES**;
- remediation design created: **YES**;
- remediation design statically inspected: **YES**;
- remediation design archived: **NO**;
- remediated runner created: **NO**;
- remediated runner execution authorized: **NO**;
- numerical retry executed: **NO**;
- Stage D2 authorized: **NO**;
- full Stage D comparison authorized: **NO**;
- scientific trajectory classification produced: **NO**.
