# Stage C Remediated Full Same-State Shadow Audit Report

## 0. Document control

- Run ID: `stage_c_remediated_full_same_state_shadow_20260721T010632Z_4bfd08a`
- Execution commit: `4bfd08abe117218ec3fcfe69774bf69e156b2c25`
- Design commit: `8fe0d1bee6e1139b2ca62daac1308666aa85fd20`
- Stage B evidence commit: `a5c200b25b17a9cc4ce709dae3695ceca8e63aba`
- Audit type: same-state local operator comparison
- Accepted trajectory changed by shadows: no
- Alternate trajectories executed: no
- Protected solver run loop called: no
- Method-superiority claim authorized: no

## 1. Classification

> **REMEDIATED SHADOW RESPONSE IS FORM-DEPENDENT AND MIXED**

This classification applies only to the frozen same-state shadow set.
It is not a solver-selection result.

## 2. Baseline reproduction

- Baseline steps: `20001`
- Stage B per-step scalar rows passed: `20001`
- Archived comparison points passed: `201 / 201`
- Final-window baseline integrated work: `6.4829121736954657e-04`
- Full-run baseline integrated work: `1.5368528716236765e-03`

## 3. Nyquist remediation checkpoint

- Historical raw checkpoint: `True`
- Real-compatible checkpoint: `True`
- Checkpoint loop index: `3059`
- Checkpoint stage: `2`
- Historical raw ratio: `1.0021037272233111e-13`
- Real-compatible ratio: `7.9835517485374568e-16`
- Maximum checkpoint real-derivative relative difference: `3.7832125302259419e-16`
- Maximum checkpoint transport relative difference: `5.3051267152275648e-16`
- Maximum checkpoint work absolute difference: `6.3527471044072525e-22`

## 4. Time-block classifications

| Block | Time range | Classification |
|---:|---|---|
| `1` | `0.005 <= t <= 20.005` | `REMEDIATED SHADOW RESPONSE FORM-DEPENDENT AND MIXED IN BLOCK` |
| `2` | `20.005 < t <= 40.005` | `REMEDIATED SHADOW RESPONSE FORM-DEPENDENT AND MIXED IN BLOCK` |
| `3` | `40.005 < t <= 60.005` | `REMEDIATED SHADOW RESPONSE FORM-DEPENDENT AND MIXED IN BLOCK` |
| `4` | `60.005 < t <= 80.005` | `REMEDIATED SHADOW RESPONSE FORM-DEPENDENT AND MIXED IN BLOCK` |
| `5` | `80.005 < t <= 100.005` | `REMEDIATED SHADOW RESPONSE FORM-DEPENDENT AND MIXED IN BLOCK` |
| `6` | `full run: 0.005 <= t <= 100.005` | `REMEDIATED SHADOW RESPONSE FORM-DEPENDENT AND MIXED IN BLOCK` |

## 5. Final-window operator comparison

| Operator | Family | Integrated signed work | Absolute-activity ratio | Signed-magnitude ratio | Maximum-rate ratio | Near-neutral | Persistent |
|---|---|---:|---:|---:|---:|---|---|
| `BASE_FD_ADVECTIVE_V1` | `BASELINE` | 6.482912173695e-04 | 1.000000000000e+00 | 1.000000000000e+00 | 1.000000000000e+00 | False | False |
| `SHADOW_FD_ADVECTIVE_PROJECTED_V1` | `PROJECTED_BASELINE_CHECK` | 6.482503301596e-04 | 9.999369307977e-01 | 9.999369307977e-01 | 9.999299743756e-01 | False | False |
| `SHADOW_FD_CONSERVATIVE_V1` | `CENTERED_ALGEBRAIC` | -6.482912173695e-04 | 1.000000000000e+00 | 1.000000000000e+00 | 1.000000000000e+00 | False | True |
| `SHADOW_FD_SKEW_V1` | `CENTERED_ALGEBRAIC` | -5.730177888175e-21 | 4.787832690624e-16 | 8.838894827892e-18 | 2.282359423823e-15 | True | False |
| `SHADOW_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2` | `PSEUDO_SPECTRAL_RC_NYQUIST` | -3.706370270449e-11 | 5.717137871291e-08 | 5.717137871291e-08 | 8.593041993195e-08 | True | False |
| `SHADOW_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2` | `PSEUDO_SPECTRAL_RC_NYQUIST` | -8.039744639911e-08 | 1.240144000798e-04 | 1.240144000798e-04 | 1.508344845788e-04 | True | False |
| `SHADOW_ARAKAWA_V1` | `ARAKAWA` | 1.129094918690e-20 | 4.887196763301e-16 | 1.741647717011e-17 | 1.980915726337e-15 | True | False |

## 6. Full-run operator comparison

| Operator | Family | Integrated signed work | Absolute-activity ratio | Signed-magnitude ratio | Maximum-rate ratio | Near-neutral | Persistent |
|---|---|---:|---:|---:|---:|---|---|
| `BASE_FD_ADVECTIVE_V1` | `BASELINE` | 1.536852871624e-03 | 1.000000000000e+00 | 1.000000000000e+00 | 1.000000000000e+00 | False | False |
| `SHADOW_FD_ADVECTIVE_PROJECTED_V1` | `PROJECTED_BASELINE_CHECK` | 1.536790325620e-03 | 9.999593025432e-01 | 9.999593025432e-01 | 9.999299743756e-01 | False | False |
| `SHADOW_FD_CONSERVATIVE_V1` | `CENTERED_ALGEBRAIC` | -1.536852871624e-03 | 1.000000000000e+00 | 1.000000000000e+00 | 1.000000000000e+00 | False | True |
| `SHADOW_FD_SKEW_V1` | `CENTERED_ALGEBRAIC` | -3.083410145475e-21 | 4.701398908481e-16 | 2.006314464063e-18 | 2.282359423823e-15 | True | False |
| `SHADOW_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2` | `PSEUDO_SPECTRAL_RC_NYQUIST` | -4.073286005133e-11 | 2.650407258271e-08 | 2.650407257807e-08 | 8.593041993195e-08 | True | False |
| `SHADOW_PS_ADVECTIVE_PROJECTED_RC_NYQUIST_V2` | `PSEUDO_SPECTRAL_RC_NYQUIST` | -1.233565135955e-07 | 8.026566229805e-05 | 8.026566229805e-05 | 1.508344845788e-04 | True | False |
| `SHADOW_ARAKAWA_V1` | `ARAKAWA` | 2.731510951490e-20 | 4.902219787023e-16 | 1.777340565206e-17 | 2.153169267757e-15 | True | False |

## 7. Same-state policy

Every shadow operator was evaluated at the baseline accepted state
and the baseline RK2 stage state. Only baseline centered advection
entered the accepted update. No shadow result advanced a state.

## 8. Mechanism diagnostics

- Maximum stage-1 centered-form identity residual: `0.000000000000e+00`
- Maximum stage-2 centered-form identity residual: `0.000000000000e+00`
- Maximum stage-1 spectral-divergence ratio: `6.476780586111e-15`
- Maximum stage-2 spectral-divergence ratio: `6.394517435186e-15`
- Maximum stage-1 Arakawa sign residual: `0.000000000000e+00`
- Maximum stage-2 Arakawa sign residual: `0.000000000000e+00`

## 9. Claim boundaries

This audit does not establish:

- formal temporal or spatial convergence;
- physical validation;
- long-time alternate-method behavior;
- which method should replace the baseline;
- turbulence, a cascade, an inertial range, or a spectral law;
- production readiness or unique physical causation.

Same-state shadow work is a local implemented-operator diagnostic.
