# Stage D1 Separate-Trajectory Pilot Failure Diagnosis

## 1. Document status

This document records the single authorized Stage D1 pilot failure and the
static diagnosis performed after preservation of its partial evidence.

Classification:

- Stage D1 pilot result: **NUMERICAL INTEGRITY FAILURE**
- Stage D1 scientific trajectory classification: **NOT PRODUCED**
- Stage D2 output or execution: **NOT AUTHORIZED AND NOT PRODUCED**
- automatic Stage D1 rerun: **NOT AUTHORIZED**
- protected-source modification: **NOT AUTHORIZED**
- Stage B or Stage C evidence modification: **NOT AUTHORIZED**
- integrity-threshold relaxation: **NOT AUTHORIZED**

This is an implementation-integrity diagnosis. It is not a method ranking,
physical validation, turbulence claim, convergence claim, or scientific
trajectory classification.

## 2. Frozen identities

| Item | Frozen identity |
|---|---|
| Branch | `phase4_validation` |
| Stage D design commit | `5bb62e25be4c789bc730e9f04fe34f1921ecae1e` |
| Stage D design SHA-256 | `491B1118B40523CF4EC340E40C38CAC462C8985377809D09484571884FC445BF` |
| Stage D1 runner commit | `a5397a6b106591dff7219f2b7b53dda2c35f57cc` |
| Stage D1 runner parent | `5bb62e25be4c789bc730e9f04fe34f1921ecae1e` |
| Stage D1 runner SHA-256 | `BF23D8C755810988821B1A36CBD3023EB839B9EF8BE0EF5F31B808EF239E14B7` |
| Stage B exact-ledger runner SHA-256 | `970AE47D4DF69819FA6D831557FC2679D843B860D901CF367361A3A34126E246` |

The Stage D1 runner was archived before execution. This diagnosis does not
change that runner or any protected source.

## 3. Authorized execution boundary

Exactly one Stage D1 pilot execution was authorized. The authorization did
not include:

- an automatic rerun;
- a second numerical diagnostic execution;
- Stage D2;
- the full Stage D comparison;
- scientific trajectory classification;
- threshold relaxation;
- protected-source modification.

The runner created its output directory and stopped during the first
trajectory preview at loop index `0`. No update was accepted.

## 4. Preserved failure identity

| Field | Preserved value |
|---|---|
| Run ID | `stage_d_separate_trajectory_pilot_20260721T041525Z_a5397a6` |
| Execution commit | `a5397a6b106591dff7219f2b7b53dda2c35f57cc` |
| Status | `failed` |
| Failed trajectory | `TRAJ_BASE_FD_ADVECTIVE_V1` |
| Failed gate | `trajectory_update_integrity` |
| Failed loop index | `0` |
| Failed RK2 stage | not recorded |
| Error type | `IntegrityFailure` |
| Last completed loop | `-1` |
| Completed baseline rows | `0` |
| Completed diagnostic rows | `0` |
| Completed pairwise rows | `0` |
| Completed integrity rows | `0` |
| Completed sentinel rows | `0` |
| Partial inventory SHA-256 | `8685631746E8F7F7B6E97C95775E6B6A7BF8155A14364ED90458B563FE0F7EB9` |

Preserved directory:

```text
experiments/advection_form_trajectory_pilot/
stage_d_separate_trajectory_pilot_20260721T041525Z_a5397a6/
```

The read-only preservation audit reported a clean working tree after the
failure.

## 5. Preserved partial file set

| File | Bytes | SHA-256 | Data rows |
|---|---:|---|---:|
| `file_inventory.csv` | 570 | `8685631746E8F7F7B6E97C95775E6B6A7BF8155A14364ED90458B563FE0F7EB9` | not applicable |
| `run_metadata.json` | 6,383 | `D531E482E4CCC1E08443C5C897BC4FFA8BCD3219303820A87BB55CD0755384AA` | not applicable |
| `trajectory_pilot_diagnostics.csv` | 418 | `32E44544395EA31C6CD7D5D1FC1F01606A81AAC0764126D394A91DC102F831A8` | 0 |
| `trajectory_pilot_integrity_per_step.csv` | 284 | `30B702EA4BA313C516FC9CE4AC1900A00223A17998EECA363F698B95773A22DA` | 0 |
| `trajectory_pilot_pairwise_divergence.csv` | 337 | `83492FD26F5833BDAF918B56CBA8A8146E8E52F111BA6E9E9A5DF5B99FCC910A` | 0 |
| `trajectory_pilot_sentinel_crosscheck.csv` | 302 | `CEF07116A5A8CED495B870A486C4AAC73B1188F2D34F803D7D4148624D9135F8` | 0 |

The summary JSON and Markdown report were not produced because the runner
stopped before pilot completion. Their absence from this failed partial bundle
is not evidence of a second execution failure.

## 6. Static failure-path reconstruction

The archived runner computes an RK2 preview without accepting it. After the
stage and filtered candidate are formed, it calculates:

1. finite-state and finite-scalar status;
2. normalized unfiltered ledger closure;
3. normalized filtered ledger closure;
4. normalized mask cross-check;
5. maximum imaginary ratio.

It then combines all five conditions into one Boolean. If any condition fails,
the runner raises:

```text
trajectory_update_integrity
```

before returning the preview to the caller. Because the per-step CSV row is
written only after a preview returns, no failing component values were
preserved. The exception also does not assign an RK2 stage.

Consequently, the preserved evidence proves that the compound gate failed but
does not prove which component of the compound gate failed.

## 7. Confirmed mask-ledger definition divergence

### 7.1 Frozen Stage B definition

The archived Stage B exact-ledger runner defines the discarded Fourier field
and its inverse transform, then calculates:

```text
mask_loss_physical = 0.5 * mean(abs(ifft2(discarded_hat))**2)
mask_loss_spectral = sum(abs(discarded_hat)**2) / (2 * N**4)
mask_rate          = -mask_loss_physical / dt
mask_crosscheck    = mask_loss_physical - mask_loss_spectral
```

This is a direct physical-space/Fourier-space Parseval cross-check of the
discarded component. The Stage B archived field
`mask_enstrophy_change_rate` is the resulting `mask_rate`.

### 7.2 Stage D1 runner definition

The archived Stage D1 runner instead calculates:

```text
mask_rate_physical = (z_filtered - z_unfiltered) / dt
mask_rate_spectral = -0.5 * mean(abs(ifft2(discarded_hat))**2) / dt
mask_crosscheck    = mask_rate_physical - mask_rate_spectral
```

Despite its local name, `mask_rate_spectral` is calculated from an inverse FFT
in physical space. The Stage D1 runner does not calculate the frozen Stage B
Fourier-space Parseval expression `sum(abs(discarded_hat)**2)/(2*N**4)`.

The Stage D1 runner also exposes `mask_rate_physical` as
`mask_enstrophy_change_rate`, then compares that field with the Stage B archive.
The two runners therefore calculate the same archived field name from different
definitions.

### 7.3 Integrity consequence

Whole-field subtraction

```text
z_filtered - z_unfiltered
```

can lose relative precision when the discarded mask energy is very small. The
loop-0 state is exactly the regime in which a near-zero discarded component is
plausible. A relative residual formed from that subtraction can therefore be
large even when the projection and Parseval identity are correct.

The definition divergence is statically proven. It blocks acceptance of the
runner's claimed exact Stage B ledger reproduction unless remediated.

It is a plausible explanation for the observed loop-0 compound-gate failure,
but it is **not proven to be the exact failed sub-gate**, because the runner did
not preserve the five component values.

## 8. Confirmed failure-observability defect

The frozen design requires preservation of the failed trajectory, gate, loop
index, RK2 stage, last completed updates, partial inventory, and source
identities.

The runner preserved the trajectory, compound gate, loop index, progress,
inventory, and source identities. It did not preserve:

- the failed RK2 stage;
- the individual compound-gate values;
- the identity of the failed compound sub-gate.

The missing stage is a direct failure-record deficiency. The missing component
values prevent a conclusive forensic attribution from the preserved evidence.

## 9. Findings

| ID | Finding | Status |
|---|---|---|
| D1-F01 | One authorized pilot stopped at loop `0` for `TRAJ_BASE_FD_ADVECTIVE_V1` | Confirmed |
| D1-F02 | No trajectory update or ledger row completed | Confirmed |
| D1-F03 | Partial evidence and inventory were preserved | Confirmed |
| D1-F04 | Working tree remained clean | Confirmed by read-only audit |
| D1-F05 | Stage D1 mask cross-check differs from the frozen Stage B physical/Fourier definition | Confirmed statically |
| D1-F06 | Stage D1 assigns a differently defined value to the Stage B field `mask_enstrophy_change_rate` | Confirmed statically |
| D1-F07 | The compound failure path omits component values and failed stage | Confirmed statically |
| D1-F08 | The mask-definition divergence caused this exact observed failure | Plausible, not proven |
| D1-F09 | A scientific trajectory disagreement was established | Not established |

## 10. Frozen remediation requirements

No remediation is performed by this document. Any future remediated design and
runner must, before any separately authorized execution:

1. preserve the failed Stage D1 directory unchanged;
2. preserve the archived Stage D1 runner commit and SHA-256 unchanged;
3. preserve all Stage B and Stage C evidence unchanged;
4. preserve all protected source unchanged;
5. keep every frozen integrity threshold unchanged;
6. restore the Stage B discarded-component physical/Fourier Parseval
   cross-check definition;
7. use the Stage B exact mask ledger rate for baseline ledger reproduction;
8. keep observed whole-field filter bookkeeping as a distinct diagnostic, not
   as a substitute for the frozen mask-loss cross-check;
9. evaluate and name each compound integrity sub-gate independently;
10. persist the failing sub-gate values before raising;
11. record a nonempty failure stage such as `post_filter_integrity` where
    applicable;
12. retain seven independently owned states and independent RK2 stages;
13. retain real-compatible Nyquist-zeroed pseudo-spectral derivatives;
14. retain the exact row-count contracts;
15. retain the prohibition on scientific classification in Stage D1;
16. contain no Stage D2 output or execution path;
17. undergo a new repository-bound static inspection;
18. receive separate explicit execution authority before any numerical retry.

These requirements do not authorize a retry. A remediated execution would be a
new controlled decision, not an automatic continuation of the failed run.

## 11. Current authorization state

| Action | Authorized? |
|---|---|
| Preserve and inspect the failed evidence | Yes; completed |
| Create this static diagnosis | Yes; completed |
| Modify the archived Stage D1 runner | No |
| Create a remediated runner | No |
| Execute a numerical forensic probe | No |
| Rerun Stage D1 | No |
| Relax a threshold | No |
| Modify protected source | No |
| Execute or emit Stage D2 | No |
| Perform the full Stage D comparison | No |
| Produce scientific trajectory classification | No |

## 12. Conclusion

The single authorized Stage D1 pilot produced a valid controlled numerical
integrity failure at loop `0` and preserved a coherent partial evidence bundle.
It did not produce a scientific result.

Static inspection identifies a confirmed mask-ledger definition divergence and
a confirmed failure-observability defect in the archived runner. Because the
compound-gate component values were not persisted, the exact failing component
cannot be recovered from the preserved evidence without additional numerical
execution, which is not authorized.

Stage D1 remains failed and archived. Stage D2 and the full Stage D comparison
remain blocked.
