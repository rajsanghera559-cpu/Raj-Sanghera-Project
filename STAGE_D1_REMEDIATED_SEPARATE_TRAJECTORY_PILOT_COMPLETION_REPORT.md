# Stage D1 Remediated Separate-Trajectory Pilot Completion Report

## Result

> **STAGE D1 REMEDIATED SEPARATE-TRAJECTORY PILOT: PASS**

The single authorized remediated Stage D1 pilot completed its frozen
implementation-integrity contract.

This is not a scientific trajectory classification, method ranking, formal
convergence result, or authorization for Stage D2 or the full Stage D
comparison.

## Repository identity

| Item | Identity |
|---|---|
| Branch | `phase4_validation` |
| Remediation-design commit | `beea25ca5ab83fcf011a029b079fe5af76aade22` |
| Remediation-design SHA-256 | `AE37B9226F6C0A58891A7C5167F9F7FCB540C616827D41C0E593655C6D2BD81B` |
| Remediated-runner commit | `b3612a031c4b34885dd85b3a14cae58bb879a54b` |
| Remediated-runner SHA-256 | `21A7E2D1168C5A6D33C563B7A278006E5A047AD18025B42F2BFE4BB65BDD3BC3` |

The working tree was clean before execution and after the read-only evidence
audit. The remote branch was synchronized before execution.

## Successful evidence identity

| Item | Value |
|---|---|
| Run ID | `stage_d_separate_trajectory_pilot_remediated_20260721T055827Z_b3612a0` |
| Evidence files | `8` exact |
| File-inventory SHA-256 | `B71EF5D9313B1C3FAE007726C92F77F7C0CD17B26D2A27F7841F073BECD8BE20` |
| Run status | `pass` |
| Last completed loop index | `3059` |
| Failed integrity rows | `0` |

The inventory SHA-256 binds the successful evidence file names, byte counts,
and individual file hashes.

## Frozen execution contract

| Contract | Observed result |
|---|---:|
| Independently owned trajectories | `7` |
| Updates per trajectory | `3,060` |
| Final loop index | `3059` |
| Final physical time | `15.300` |
| Baseline Stage B reproduction | `3,060 / 3,060` |
| Trajectory-diagnostic rows | `2,149` |
| Pairwise-divergence rows | `6,447` |
| Per-step integrity rows | `21,420` |
| Sentinel cross-check rows | `21` |
| Finite trajectories | `7 / 7` |
| Shared-memory violations | `0` |
| Order-invariance failures | `0` |
| Failed integrity gates | `0` |

## Audited integrity maxima

| Quantity | Observed maximum | Frozen limit | Result |
|---|---:|---:|---|
| Normalized filtered closure | `8.84938128294688e-13` | `1e-10` | PASS |
| Normalized physical/Fourier mask cross-check | `5.42651066925669e-16` | `1e-12` | PASS |
| Real-compatible imaginary ratio | `1.35648380476905e-15` | `1e-13` | PASS |

The evidence audit also verified:

- exactly eight expected output files;
- every inventory byte count and file SHA-256;
- every output file below `40 MB`;
- exact CSV row counts;
- all diagnostic and pairwise finite-value flags;
- all `21,420` per-step integrity pass flags;
- all sentinel order-invariance and helper cross-check pass flags;
- completed metadata and summary contracts;
- no scientific trajectory classification;
- no full-comparison authorization.

## Remediation disposition

The prior failed Stage D1 evidence remains preserved under inventory SHA-256:

```text
8685631746E8F7F7B6E97C95775E6B6A7BF8155A14364ED90458B563FE0F7EB9
```

The remediated pilot restored the frozen Stage B discarded-component
physical/Fourier Parseval definition, separated whole-field filter bookkeeping,
and provided named integrity sub-gates and failure-snapshot support.

No retry is required or authorized. The archived failed runner, protected
source, Stage B evidence, and Stage C evidence were not modified.

## Scientific boundary

This PASS establishes that the remediated pilot executed the intended software
contract with internally consistent ledgers, state ownership, evidence counts,
and frozen baseline reproduction.

It does not establish that the seven numerical trajectories agree, that any
method is superior, or that observed differences are physically meaningful.
Those questions require examination of the recorded diagnostics and a separate
scientific decision.

Stage D2 and the full Stage D comparison remain unauthorized.
