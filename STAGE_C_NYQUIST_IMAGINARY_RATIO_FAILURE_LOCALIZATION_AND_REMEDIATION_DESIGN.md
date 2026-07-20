
# Stage C Nyquist Imaginary-Ratio Failure Localization and Remediation Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Current source checkpoint:
  `c6b2caca02a4067a8cad7398a2dfc7bc15841c42`
- Parent Stage C design checkpoint:
  `362fd2382ecb12cae875f4bf8ead656f69643103`
- Parent Stage C runner:
  `run_stage_c_same_state_advection_shadow_audit.py`
- Parent Stage C runner SHA-256:
  `5E13CF350DF5356E1E8E44F0D921A7C92FFDD6830978466DFA5B6648818F4BC1`
- Parent Stage C design:
  `STAGE_C_SAME_STATE_ADVECTION_FORM_SHADOW_AUDIT_DESIGN.md`
- Parent Stage C design SHA-256:
  `4C14EEA8E492CC5824686C3540D9ABF96EA3413C5F4B9B9A8E1D5EDD470D7D0C`
- Protected baseline solver:
  `project/solver/spectral_solver.py`
- Protected baseline solver SHA-256:
  `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1`
- Preserved partial Stage C run:
  `experiments/advection_form_shadow_audit/stage_c_same_state_advection_shadow_20260720T210332Z_c6b2cac`
- Partial inventory SHA-256:
  `E76B55EFD5D8C8FF16BA044856D3D9AFEF39219937C754C292D48D8D12227C09`
- Created UTC:
  `2026-07-20T21:17:44+00:00`
- Document type:
  design only
- Focused diagnostic runner created by this document:
  no
- Focused numerical execution authorized:
  no
- Full Stage C rerun authorized:
  no
- Preserved partial evidence modification authorized:
  no
- Protected source modification authorized:
  no
- Stage C specificity classification authorized:
  no
- Method-superiority claim authorized:
  no

### Claim boundaries

- Formal temporal convergence: not authorized
- Formal spatial convergence: not authorized
- Physical validation: not authorized
- Turbulence: not authorized
- Cascade: not authorized
- Inertial range: not authorized
- `k^-3` law: not authorized
- Method superiority: not authorized
- Production readiness: not authorized
- Unique physical causation: not authorized
- Baseline replacement: not authorized
- Alternate-trajectory execution: not authorized
- Stage C form-specificity conclusion: not authorized
- Full Stage C continuation: not authorized

---

## 1. Purpose

The original Stage C same-state advection-form shadow audit stopped during the
stage-2 shadow diagnostics after the frozen imaginary-ratio gate was exceeded.

The failure was:

```text
failed_gate: shadow_mechanism_integrity
error_message: same-state mechanism checks failed: ['imaginary_ratio']
```

This document freezes a focused diagnostic intended to answer:

> Which FFT-derived quantity exceeded the imaginary-ratio threshold, why did it
> exceed the threshold, and does a Nyquist-zeroed real-compatible derivative
> remove only imaginary content or also change the real same-state shadow work?

The focused diagnostic is a failure-localization study.

It is not a resumed Stage C audit.

It is not a full trajectory comparison.

It is not a solver-selection experiment.

---

## 2. Preserved partial-evidence facts

The preserved partial Stage C run reported:

| Quantity | Preserved value |
|---|---:|
| Metadata status | `failed` |
| Classification | `NUMERICAL INTEGRITY FAILURE` |
| Failed gate | `shadow_mechanism_integrity` |
| Last completed loop index | `3058` |
| Completed state-reference rows | `3059` |
| Completed shadow rows | `21413` |
| Last completed physical time | `15.295` |
| Last completed stage-1 maximum imaginary ratio | `3.2467038768288357e-15` |
| Last completed stage-2 maximum imaginary ratio | `9.955198638157299e-14` |
| Frozen imaginary-ratio limit | `1.0e-13` |

The last completed stage-2 value was only slightly below the frozen gate.

The next attempted stage-2 evaluation crossed the gate.

The exact failing scalar was not recorded separately.

---

## 3. Preserved partial-evidence identities

The following files must remain byte-identical:

| File | Bytes | SHA-256 |
|---|---:|---|
| `run_metadata.json` | `7887` | `E31762AE53BE53D6BCCC291296BCD1FC5A3571D605A327EB381E20FCC82DD400` |
| `shadow_state_reference.csv` | `3979483` | `DE01C0F7C0502B3A4917A4FDC70F6295D06A910D8CF60240351C602AF9E32A36` |
| `shadow_advection_per_step.csv` | `12790759` | `08D540C4170A0E7FC326E02E4D172945188A296E896330A60C77DB4A1FAB4944` |
| `file_inventory.csv` | `409` | `E76B55EFD5D8C8FF16BA044856D3D9AFEF39219937C754C292D48D8D12227C09` |

No file in the preserved directory may be:

- edited;
- renamed;
- moved;
- deleted;
- regenerated;
- normalized;
- line-ending converted;
- rehashed into a replacement inventory.

---

## 4. Last completed operator-work pattern

At physical time `15.295`, the preserved same-state values were:

| Operator | Stage-weighted RHS work |
|---|---:|
| `BASE_FD_ADVECTIVE_V1` | `+1.7413851867416074e-07` |
| `SHADOW_FD_ADVECTIVE_PROJECTED_V1` | `+1.7413851867408504e-07` |
| `SHADOW_FD_CONSERVATIVE_V1` | `-1.7413851867416e-07` |
| `SHADOW_FD_SKEW_V1` | `+1.0587911840678754e-22` |
| `SHADOW_PS_ADVECTIVE_RAW_V1` | `+6.352747104407253e-22` |
| `SHADOW_PS_ADVECTIVE_PROJECTED_V1` | `-1.3923104070492562e-19` |
| `SHADOW_ARAKAWA_V1` | `+1.0587911840678754e-22` |

These values are preserved partial observations.

They are not a final Stage C classification.

---

## 5. Frozen localization range

The focused diagnostic shall reproduce the baseline trajectory only through
the first original failing evaluation.

The expected range is:

```text
loop_index = 0 through the first failing loop index
```

The last known passing loop index is:

```text
3058
```

The first failing loop index is expected to be:

```text
3059
```

The focused diagnostic must determine the exact first failing index rather than
assume it.

The diagnostic shall stop immediately after recording:

1. the last passing evaluation;
2. the first failing evaluation;
3. the raw-versus-Nyquist-zeroed comparison at the failing evaluation.

It shall not continue to `t = 100.005`.

---

## 6. Baseline trajectory policy

The focused diagnostic shall reproduce one baseline centered-advection
trajectory only.

The baseline update remains:

\[
A^{base}
=
-\left(
uD_x^c\omega+vD_y^c\omega
\right).
\]

The accepted update remains the original RK2-plus-mask update.

Shadow operators may not advance state.

The Nyquist-zeroed derivative may not enter the accepted baseline update.

No alternate trajectory is authorized.

---

## 7. Five imaginary-ratio quantities

For each evaluated baseline current state and baseline RK2 stage state, the
focused diagnostic shall calculate and record exactly five quantities.

### 7.1 Vorticity spectral-gradient ratio

```text
omega_gradient_imaginary_ratio
```

Calculated from:

\[
D_x^{raw}\omega
=
\mathcal F^{-1}
\left(
ik_x\widehat{\omega}
\right),
\]

\[
D_y^{raw}\omega
=
\mathcal F^{-1}
\left(
ik_y\widehat{\omega}
\right).
\]

### 7.2 Projected centered-baseline transport ratio

```text
projected_baseline_transport_imaginary_ratio
```

Calculated from:

\[
\mathcal F^{-1}
\left[
P\mathcal F(T_{BA})
\right].
\]

### 7.3 Projected pseudo-spectral transport ratio

```text
projected_pseudo_transport_imaginary_ratio
```

Calculated from:

\[
\mathcal F^{-1}
\left[
P\mathcal F(T_{PSR})
\right].
\]

### 7.4 Spectral `u_x` ratio

```text
u_x_gradient_imaginary_ratio
```

Calculated from:

\[
D_x^{raw}u
=
\mathcal F^{-1}
\left(
ik_x\widehat{u}
\right).
\]

### 7.5 Spectral `v_y` ratio

```text
v_y_gradient_imaginary_ratio
```

Calculated from:

\[
D_y^{raw}v
=
\mathcal F^{-1}
\left(
ik_y\widehat{v}
\right).
\]

---

## 8. Required absolute measurements

For every one of the five quantities, record:

- real-part RMS;
- imaginary-part RMS;
- imaginary-to-real RMS ratio;
- real-part maximum absolute value;
- imaginary-part maximum absolute value;
- denominator used in the ratio;
- whether the denominator equals the residual floor;
- pass/fail against `1.0e-13`.

The ratio is:

\[
\rho
=
\frac{
\operatorname{RMS}(\operatorname{Im}q)
}{
\max(
\operatorname{RMS}(\operatorname{Re}q),
10^{-30}
)
}.
\]

The diagnostic must not report only the maximum of the five ratios.

---

## 9. Exact failing-quantity record

At the first failure, record:

- loop index;
- completed-step count;
- physical time;
- stage number;
- quantity ID;
- ratio;
- real RMS;
- imaginary RMS;
- ratio denominator;
- amount above the frozen threshold;
- relative amount above the threshold;
- current-state SHA-256;
- stage-state SHA-256;
- forcing SHA-256.

The focused report must identify exactly one maximum-producing quantity.

If two values are tied within exact floating-point equality, report all tied
quantities.

---

## 10. Even-grid Nyquist definitions

For `N = 64`, the NumPy FFT wavenumber array contains the negative Nyquist
value:

\[
k_N=-\frac{N}{2}=-32.
\]

Define:

```text
x-Nyquist column: kx == -32
y-Nyquist row:    ky == -32
Nyquist corner:   kx == -32 and ky == -32
```

The focused diagnostic shall identify these locations from the actual solver
wavenumber arrays.

It may not assume hard-coded array indices without verification.

---

## 11. Nyquist spectral-content measurements

For each relevant field:

- current vorticity;
- stage vorticity;
- current velocity `u`;
- current velocity `v`;
- stage velocity `u`;
- stage velocity `v`;
- raw centered transport;
- raw pseudo-spectral transport;

record:

### 11.1 Total spectral power

\[
P_{total}
=
\sum_{\boldsymbol{k}}
|\widehat{q}|^2.
\]

### 11.2 x-Nyquist-line power

\[
P_{xN}
=
\sum_{k_x=-32}
|\widehat{q}|^2.
\]

### 11.3 y-Nyquist-line power

\[
P_{yN}
=
\sum_{k_y=-32}
|\widehat{q}|^2.
\]

### 11.4 Nyquist-corner power

\[
P_{NN}
=
|\widehat{q}(-32,-32)|^2.
\]

### 11.5 Fractions

Record:

\[
f_{xN}
=
\frac{P_{xN}}{\max(P_{total},10^{-300})},
\]

\[
f_{yN}
=
\frac{P_{yN}}{\max(P_{total},10^{-300})},
\]

\[
f_{NN}
=
\frac{P_{NN}}{\max(P_{total},10^{-300})}.
\]

---

## 12. Hermitian-symmetry diagnostics

For each real input field, calculate a Hermitian-symmetry residual before
differentiation.

For each differentiated spectrum, calculate the symmetry residual after
multiplication by the derivative factor.

Required routes:

- raw `ikx`;
- raw `iky`;
- Nyquist-zeroed `ikx`;
- Nyquist-zeroed `iky`.

The diagnostic shall determine whether the raw derivative multiplier creates a
self-conjugate Nyquist inconsistency.

---

## 13. Existing raw-\(ik\) derivative route

The existing shadow route is:

\[
\widehat{D_x^{raw}q}
=
ik_x\widehat{q},
\]

\[
\widehat{D_y^{raw}q}
=
ik_y\widehat{q}.
\]

The inverse transforms are retained as complex arrays.

The real part is used by the shadow calculation.

The imaginary part is measured by the integrity gate.

No change to this definition is authorized in the original Stage C runner.

---

## 14. Nyquist-zeroed real-compatible route

Define diagnostic derivative wavenumbers:

\[
k_x^{NZ}
=
\begin{cases}
0,& k_x=-32,\\
k_x,& \text{otherwise},
\end{cases}
\]

\[
k_y^{NZ}
=
\begin{cases}
0,& k_y=-32,\\
k_y,& \text{otherwise}.
\end{cases}
\]

Then define:

\[
\widehat{D_x^{NZ}q}
=
ik_x^{NZ}\widehat{q},
\]

\[
\widehat{D_y^{NZ}q}
=
ik_y^{NZ}\widehat{q}.
\]

These derivatives are diagnostic only.

They shall not enter the accepted baseline update.

They shall not modify the protected solver wavenumber arrays.

---

## 15. Raw-versus-Nyquist-zeroed derivative comparison

For each relevant field and derivative direction, record:

- raw real RMS;
- raw imaginary RMS;
- raw imaginary ratio;
- Nyquist-zeroed real RMS;
- Nyquist-zeroed imaginary RMS;
- Nyquist-zeroed imaginary ratio;
- RMS difference between real parts;
- maximum absolute difference between real parts;
- cosine similarity between real parts;
- relative real-part difference;
- power removed from the derivative spectrum;
- fraction of derivative-spectrum power removed.

---

## 16. Real shadow-work comparison

The focused diagnostic must determine whether Nyquist zeroing changes only
imaginary contamination or materially changes real same-state work.

At the failing current and stage states, calculate both raw and
Nyquist-zeroed routes for:

```text
SHADOW_PS_ADVECTIVE_RAW_V1
SHADOW_PS_ADVECTIVE_PROJECTED_V1
```

Also calculate any affected mechanism diagnostic involving:

```text
spectral u_x
spectral v_y
spectral velocity divergence
```

For each operator and stage, record:

- raw RHS work;
- Nyquist-zeroed RHS work;
- absolute work difference;
- relative work difference;
- raw transport RMS;
- Nyquist-zeroed transport RMS;
- transport RMS difference;
- transport cosine similarity;
- raw work alignment;
- Nyquist-zeroed work alignment.

---

## 17. Stage-weighted work comparison

For pseudo-spectral operator \(m\), calculate:

\[
R_{A,m}^{raw}
=
\frac{1}{2}
\left[
\langle\omega_nA_{1,m}^{raw}\rangle
+
\langle\omega_sA_{2,m}^{raw}\rangle
\right],
\]

\[
R_{A,m}^{NZ}
=
\frac{1}{2}
\left[
\langle\omega_nA_{1,m}^{NZ}\rangle
+
\langle\omega_sA_{2,m}^{NZ}\rangle
\right].
\]

Record:

\[
\Delta R_{A,m}
=
R_{A,m}^{NZ}-R_{A,m}^{raw}.
\]

Normalize using:

\[
\delta R_{A,m}
=
\frac{
|\Delta R_{A,m}|
}{
\max(
|R_{A,m}^{raw}|,
|R_{A,m}^{NZ}|,
10^{-30}
)
}.
\]

---

## 18. Stable material-change tests

Nyquist treatment is classified as changing only imaginary content when all
of the following pass at the first failing step:

1. Nyquist-zeroed imaginary ratio for the failing quantity is `<= 1e-13`;
2. real derivative relative RMS difference is `<= 1e-10`;
3. real transport relative RMS difference is `<= 1e-10`;
4. pseudo-spectral stage-weighted work absolute difference is `<= 1e-14` or
   relative difference is `<= 1e-6`;
5. the sign of nonzero stage-weighted work does not change;
6. all arrays remain finite;
7. all input-state hashes remain unchanged.

These thresholds classify material effect for this diagnostic only.

They are not formal accuracy tolerances.

---

## 19. Material real-work change test

Return that Nyquist treatment also changes real shadow work when any of the
following is true:

- real derivative relative RMS difference exceeds `1e-10`;
- real transport relative RMS difference exceeds `1e-10`;
- stage-weighted work absolute difference exceeds `1e-14` and relative
  difference exceeds `1e-6`;
- a nonzero stage-weighted work changes sign;
- the raw near-zero/nonzero character changes under the frozen
  `1e-14` absolute work scale.

---

## 20. Frozen localization conclusions

The focused diagnostic may return exactly one primary conclusion:

```text
FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION
FAILURE NOT EXPLAINED BY NYQUIST DERIVATIVE CONVENTION
LOCALIZATION INCONCLUSIVE
NUMERICAL INTEGRITY FAILURE
```

It shall also return exactly one effect conclusion:

```text
NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT
NYQUIST TREATMENT ALSO CHANGES REAL SHADOW WORK
NYQUIST REAL-WORK EFFECT INCONCLUSIVE
```

No other scientific classification is authorized.

---

## 21. Rule for “consistent with Nyquist convention”

Return:

```text
FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION
```

only when:

1. the exact failing quantity is derivative-generated rather than
   projection-generated, or projection-generated content is traced to a raw
   spectral derivative;
2. measurable spectral power exists on the relevant Nyquist line;
3. the raw derivative exceeds the frozen imaginary-ratio threshold;
4. the Nyquist-zeroed derivative passes the threshold;
5. the Nyquist-zeroed derivative has improved Hermitian symmetry;
6. all baseline reproduction checks pass.

---

## 22. Rule for “not explained by Nyquist convention”

Return:

```text
FAILURE NOT EXPLAINED BY NYQUIST DERIVATIVE CONVENTION
```

when any of the following is established:

- no measurable relevant Nyquist-line content exists;
- zeroing the relevant Nyquist multiplier does not reduce the imaginary ratio;
- the failing quantity is independent of the derivative route;
- a non-Nyquist symmetry defect dominates;
- the baseline state fails archival reproduction.

---

## 23. Rule for inconclusive localization

Return:

```text
LOCALIZATION INCONCLUSIVE
```

when:

- the first failure cannot be reproduced;
- multiple candidate quantities cross together and cannot be separated;
- the failing ratio depends on evaluation order;
- the preserved state cannot be reconstructed;
- source identities do not match;
- the result is denominator-floor dominated.

---

## 24. Baseline reproduction gates

The focused diagnostic must reproduce, through the stopping point:

- Stage B per-step baseline scalar values;
- Stage C preserved partial baseline values;
- state-reference row count through loop index `3058`;
- last completed `z_filtered`;
- last completed baseline RK2 work;
- last completed stage-1 and stage-2 maximum imaginary ratios;
- seven preserved operator works at `t = 15.295`.

The last completed baseline values must match:

```text
physical_time = 15.295
z_filtered = 0.00247703643047042
baseline_rk2_work = 1.7413851867416074e-07
```

---

## 25. Preserved partial-evidence comparison

The future diagnostic shall read the preserved CSV files.

It shall not use them as mutable outputs.

For every reconstructed completed row through loop index `3058`, it shall
verify:

- loop index;
- physical time;
- `z_filtered`;
- baseline stage-weighted work;
- stage-1 maximum imaginary ratio;
- stage-2 maximum imaginary ratio.

A mismatch stops localization.

---

## 26. Exact stopping policy

The focused diagnostic shall stop when the first original raw-route
imaginary-ratio failure is reproduced.

Required sequence:

1. reproduce last passing loop index;
2. evaluate next loop index;
3. record all five raw ratios at both stages;
4. identify the first failing quantity;
5. calculate all Nyquist-line measurements;
6. calculate Nyquist-zeroed routes;
7. compare real derivatives and real shadow work;
8. write the focused summary;
9. stop.

No additional baseline step is authorized.

---

## 27. Future runner identity

The prospective focused runner filename is:

```text
run_stage_c_nyquist_failure_localization.py
```

It shall support:

```powershell
python -B .\run_stage_c_nyquist_failure_localization.py inspect
python -B .\run_stage_c_nyquist_failure_localization.py run
```

This design does not create that runner.

---

## 28. Future inspection requirements

The future `inspect` mode shall:

- parse and compile the runner;
- require exact filename;
- require LF-only bytes;
- verify branch `phase4_validation`;
- verify the archived localization-design checkpoint;
- require only the untracked focused runner;
- verify the Stage C runner hash;
- verify protected solver hash;
- verify partial-evidence file hashes;
- verify no output header duplicates;
- verify the stop-at-first-failure policy;
- verify both raw and Nyquist-zeroed derivative routes;
- reject changes to solver wavenumber arrays;
- reject protected solver `run()` calls;
- reject selectable solver calls;
- reject alternate trajectories;
- reject full Stage C output classifications;
- reject tolerance relaxation;
- write no files;
- construct no solver;
- execute no timestep;
- mutate no Git state.

Inspection must end with:

```text
Focused localization execution authorized by inspection: NO
```

---

## 29. Future execution preflight

A future run path shall require:

- clean working tree;
- exact branch;
- committed and pushed focused runner;
- focused runner commit changes exactly one file;
- runner commit parent equals the localization-design commit;
- source and evidence identities match;
- no prior focused localization output exists;
- focused output directory is Git ignored;
- preserved partial-evidence directory remains byte-identical;
- full Stage C output directory remains present and unchanged.

A failed preflight shall create no output directory.

---

## 30. Prospective output bundle

A future focused diagnostic shall create one immutable Git-ignored directory
under:

```text
experiments/advection_form_shadow_audit_localization/
```

Run-directory prefix:

```text
stage_c_nyquist_failure_localization_
```

Required files:

1. `run_metadata.json`;
2. `imaginary_ratio_trace.csv`;
3. `nyquist_spectral_content.csv`;
4. `raw_vs_nyquist_zeroed.csv`;
5. `localization_summary.json`;
6. `STAGE_C_NYQUIST_FAILURE_LOCALIZATION_REPORT.md`;
7. `file_inventory.csv`.

No state arrays are archived.

No full Stage C summary is produced.

No Stage C specificity classification is produced.

---

## 31. `imaginary_ratio_trace.csv`

One row per loop index, stage and quantity through the first failure.

Required unique columns:

- `loop_index`;
- `completed_steps`;
- `physical_time`;
- `stage`;
- `quantity_id`;
- `real_rms`;
- `imaginary_rms`;
- `imaginary_ratio`;
- `real_max_abs`;
- `imaginary_max_abs`;
- `ratio_denominator`;
- `denominator_uses_floor`;
- `threshold`;
- `threshold_pass`;
- `is_maximum_for_stage`;
- `is_first_failing_quantity`;
- `state_sha256`.

---

## 32. `nyquist_spectral_content.csv`

Required unique columns:

- `loop_index`;
- `physical_time`;
- `stage`;
- `field_id`;
- `total_power`;
- `x_nyquist_power`;
- `y_nyquist_power`;
- `nyquist_corner_power`;
- `x_nyquist_fraction`;
- `y_nyquist_fraction`;
- `nyquist_corner_fraction`;
- `input_hermitian_residual`;
- `raw_x_derivative_hermitian_residual`;
- `raw_y_derivative_hermitian_residual`;
- `nyquist_zeroed_x_derivative_hermitian_residual`;
- `nyquist_zeroed_y_derivative_hermitian_residual`.

---

## 33. `raw_vs_nyquist_zeroed.csv`

Required unique columns:

- `loop_index`;
- `physical_time`;
- `stage`;
- `field_id`;
- `derivative_direction`;
- `raw_real_rms`;
- `raw_imaginary_rms`;
- `raw_imaginary_ratio`;
- `nyquist_zeroed_real_rms`;
- `nyquist_zeroed_imaginary_rms`;
- `nyquist_zeroed_imaginary_ratio`;
- `real_part_difference_rms`;
- `real_part_difference_max_abs`;
- `real_part_difference_relative`;
- `real_part_cosine_similarity`;
- `derivative_power_removed`;
- `derivative_power_removed_fraction`;
- `operator_id`;
- `raw_operator_work`;
- `nyquist_zeroed_operator_work`;
- `operator_work_absolute_difference`;
- `operator_work_relative_difference`;
- `operator_work_sign_changed`;
- `material_real_work_change`.

---

## 34. Metadata requirements

`run_metadata.json` shall record:

- run ID;
- status;
- primary conclusion;
- effect conclusion;
- UTC timestamps;
- repository branch;
- design commit;
- execution commit;
- runner SHA-256;
- protected source hashes;
- Stage C runner hash;
- partial-evidence hashes;
- Python and NumPy versions;
- frozen thresholds;
- exact stopping policy;
- exact failure location;
- no-rerun policy;
- claim boundaries;
- error details after failure.

---

## 35. Summary requirements

`localization_summary.json` shall include:

- first failing loop index;
- first failing stage;
- first failing quantity;
- all five raw values at the failing stage;
- all five Nyquist-zeroed values where applicable;
- relevant Nyquist-line power fractions;
- Hermitian-symmetry comparison;
- real derivative differences;
- real transport differences;
- raw versus Nyquist-zeroed shadow work;
- primary conclusion;
- effect conclusion;
- baseline reproduction results;
- preserved-evidence identity results;
- limitations;
- explicit statement that no full Stage C classification was produced.

---

## 36. Report requirements

The focused report shall explain:

1. what failed;
2. which exact quantity failed;
3. whether the failure is derivative-generated or projection-generated;
4. whether relevant Nyquist content was present;
5. whether Nyquist zeroing removed the imaginary component;
6. whether real derivatives changed;
7. whether real shadow work changed;
8. what remains unresolved;
9. why no Stage C specificity classification is allowed;
10. why no full Stage C rerun is authorized by the report.

---

## 37. Failure preservation

After creating a focused output directory, any failure must preserve:

- metadata;
- completed ratio-trace rows;
- completed spectral-content rows;
- completed raw-versus-zeroed rows;
- last reconstructed loop index;
- failed gate;
- partial inventory.

The runner shall print:

```text
STAGE C NYQUIST FAILURE LOCALIZATION: FAILED
Partial focused evidence preserved at: <path>
Full Stage C rerun authorized: NO
```

---

## 38. No-rerun and no-continuation policy

After completion or failure:

- do not rerun automatically;
- do not delete focused partial evidence;
- do not modify original Stage C partial evidence;
- do not resume the original Stage C runner;
- do not execute a full Stage C audit;
- do not relax the historical `1e-13` threshold;
- do not modify the protected solver;
- do not modify the advection-operator source;
- do not claim operator-form specificity.

Any future remediation implementation requires a new design decision.

---

## 39. Permitted interpretation

A completed focused localization may state:

- the original failure is consistent with the even-grid Nyquist derivative
  convention;
- the original failure is not explained by that convention;
- Nyquist zeroing changes only imaginary content;
- Nyquist zeroing also changes real shadow work;
- localization is inconclusive.

It may quantify the partial operator-work pattern.

It may not elevate that pattern to a full-run Stage C result.

---

## 40. Scientific limitations

The focused diagnostic cannot establish:

- formal accuracy;
- convergence;
- long-time behavior;
- method superiority;
- baseline invalidity;
- alternate-method trajectory behavior;
- turbulence;
- cascade behavior;
- spectral-law validity;
- production readiness.

It examines one implementation-level spectral-reality gate near one failure
point.

---

## 41. Expected successful console summary

A future successful focused execution should report:

```text
STAGE C NYQUIST FAILURE LOCALIZATION: COMPLETE
Last reproduced passing loop index: 3058
First reproduced failing loop index: <index>
First failing stage: <stage>
First failing quantity: <quantity>
Raw imaginary ratio: <value>
Nyquist-zeroed imaginary ratio: <value>
Primary conclusion: <frozen primary conclusion>
Effect conclusion: <frozen effect conclusion>
Preserved partial evidence modified: NO
Full Stage C rerun performed: NO
Full Stage C rerun authorized: NO
Stage C specificity classification produced: NO
```

---

## 42. Current decision

The Stage C Nyquist imaginary-ratio failure-localization and remediation
design is now frozen.

No focused runner has been created.

No focused numerical step has been executed.

No preserved evidence has been modified.

No full Stage C rerun has been authorized.

No Stage C specificity classification has been produced.

The next controlled task is to archive this design before creating any focused
localization runner.
