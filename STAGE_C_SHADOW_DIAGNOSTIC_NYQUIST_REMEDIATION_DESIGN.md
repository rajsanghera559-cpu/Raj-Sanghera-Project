# Stage C Shadow-Diagnostic-Only Nyquist Remediation Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Focused localization evidence-report commit:
  `1878619a564e7599817735614fec417f710952af`
- Focused localization evidence report:
  `STAGE_C_NYQUIST_FAILURE_LOCALIZATION_EVIDENCE_REPORT.md`
- Focused localization evidence-report SHA-256:
  `EEFB82BFBC74C5E2EEC75C816D0A8F4C56601921E3EAEFD1D5B820B5F74BBE7D`
- Protected baseline solver:
  `project/solver/spectral_solver.py`
- Protected baseline solver SHA-256:
  `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1`
- Original Stage C shadow runner:
  `run_stage_c_same_state_advection_shadow_audit.py`
- Original Stage C shadow-runner SHA-256:
  `5E13CF350DF5356E1E8E44F0D921A7C92FFDD6830978466DFA5B6648818F4BC1`
- Focused localization runner:
  `run_stage_c_nyquist_failure_localization.py`
- Focused localization-runner SHA-256:
  `945CD7D940CBAA823A15AC6A3E5885F97ED4E46AFE4919C40181F3FCA6B9BFA0`
- Focused localization design:
  `STAGE_C_NYQUIST_IMAGINARY_RATIO_FAILURE_LOCALIZATION_AND_REMEDIATION_DESIGN.md`
- Focused localization-design SHA-256:
  `809196A724D4CD94C936A6A96BB7A6B39717A6667EB57D932ED023C6469EC1A2`
- Focused evidence inventory SHA-256:
  `9FF4E524A0A05ED2E2CC5214E5EE4075254D11852F8CECF895C1F22F87328D5C`
- Document type:
  design only
- Protected baseline solver modification authorized:
  no
- Accepted baseline-update modification authorized:
  no
- Advection-operator source modification authorized:
  no
- Full Stage C rerun authorized:
  no
- Remediated Stage C numerical execution authorized:
  no
- Alternate trajectory execution authorized:
  no
- Method-superiority claim authorized:
  no
- Stage C operator-form-specificity classification authorized:
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
- Full Stage C form-specificity conclusion: not authorized

---

## 1. Evidence basis

The focused localization established:

```text
First failing loop index: 3059
First failing stage: 2
First failing quantity: omega_gradient_imaginary_ratio
Raw imaginary ratio: 1.0021037272233111e-13
Nyquist-zeroed imaginary ratio: 7.983551748537457e-16
```

The frozen conclusions were:

> **FAILURE CONSISTENT WITH NYQUIST DERIVATIVE CONVENTION**

> **NYQUIST TREATMENT CHANGES ONLY IMAGINARY CONTENT**

The accepted baseline trajectory, protected solver, preserved partial Stage C
evidence, and focused localization evidence remained unchanged.

The focused result did not complete the planned 20,001-step Stage C
operator-form comparison.

---

## 2. Remediation question

The remediation question is:

> Can the shadow-only spectral derivative and spectral-divergence diagnostics
> use an explicitly real-compatible even-grid Nyquist convention while leaving
> the accepted centered-advection RK2-plus-mask update byte-for-byte and
> numerically unchanged?

This question is limited to the shadow diagnostic path.

It is not a request to alter the production or protected baseline solver.

---

## 3. Scope

The remediation applies only to:

- spectral vorticity gradients used by pseudo-spectral shadow operators;
- spectral velocity derivatives used by shadow divergence diagnostics;
- derivative-generated imaginary-ratio integrity checks;
- projected pseudo-spectral shadow transport derived from those gradients.

The remediation does not apply to:

- the baseline centered finite-difference advection update;
- the baseline RK2 stage construction;
- the baseline viscosity calculation;
- the baseline forcing;
- the accepted post-step mask;
- protected solver wavenumber arrays;
- `project/solver/advection_operators.py`;
- any selectable solver trajectory;
- archived Stage B or Stage C evidence.

---

## 4. Frozen baseline update

The accepted baseline advection remains:

\[
A^{base}
=
-\left(
uD_x^c\omega + vD_y^c\omega
\right).
\]

The accepted state remains:

\[
\omega_{n+1}
=
P\left[
\omega_n
+
\frac{\Delta t}{2}
\left(
N_1+N_2
\right)
\right].
\]

No Nyquist-zeroed spectral derivative may enter either formula.

The remediation runner must prove that the baseline replay remains identical to
the archived Stage B and partial Stage C references.

---

## 5. Raw historical route

The historical shadow derivative remains defined for reproduction as:

\[
\widehat{D_x^{raw}q}
=
ik_x\widehat q,
\]

\[
\widehat{D_y^{raw}q}
=
ik_y\widehat q.
\]

The raw route must remain available as a read-only comparison path.

It must reproduce:

```text
loop_index = 3059
stage = 2
quantity = omega_gradient_imaginary_ratio
raw ratio = 1.0021037272233111e-13
```

The raw threshold remains:

```text
1.0e-13
```

The remediation may not erase, relabel, suppress, or retroactively pass the
historical raw-route failure.

---

## 6. Real-compatible Nyquist-zeroed route

For an even grid, define local diagnostic derivative wavenumber copies:

\[
k_x^{RC}
=
\begin{cases}
0,& k_x=-N/2,\\
k_x,& \text{otherwise},
\end{cases}
\]

\[
k_y^{RC}
=
\begin{cases}
0,& k_y=-N/2,\\
k_y,& \text{otherwise}.
\end{cases}
\]

Then define:

\[
\widehat{D_x^{RC}q}
=
ik_x^{RC}\widehat q,
\]

\[
\widehat{D_y^{RC}q}
=
ik_y^{RC}\widehat q.
\]

Requirements:

- derive the Nyquist location from the actual solver wavenumber arrays;
- do not hard-code an array index without checking the `-N/2` value;
- copy the wavenumber arrays before zeroing;
- never mutate `solver.kx` or `solver.ky`;
- retain complex inverse transforms until real and imaginary diagnostics are
  recorded;
- use the real part only for shadow transport evaluation;
- report the imaginary part independently.

---

## 7. Shadow operator use

The real-compatible route may be used only for:

```text
SHADOW_PS_ADVECTIVE_RAW_V1
SHADOW_PS_ADVECTIVE_PROJECTED_V1
```

and the associated shadow spectral-divergence diagnostics.

The following operators remain unchanged:

```text
BASE_FD_ADVECTIVE_V1
SHADOW_FD_ADVECTIVE_PROJECTED_V1
SHADOW_FD_CONSERVATIVE_V1
SHADOW_FD_SKEW_V1
SHADOW_ARAKAWA_V1
```

The projected centered-baseline transport remains based on the unchanged
centered transport and the existing mask projection.

---

## 8. Dual-route evidence policy

A future remediation implementation must calculate both routes at controlled
checkpoints:

1. historical raw-`ik` route;
2. real-compatible Nyquist-zeroed route.

The raw route is used to prove historical reproduction.

The real-compatible route is the candidate shadow diagnostic route.

Both routes must be evaluated on the exact same baseline current and RK2 stage
states.

Neither route may advance a state.

---

## 9. Focused remediation-verification range

Before any full Stage C run is considered, a focused remediation verification
must stop at the original failure point.

Authorized verification range:

```text
loop_index 0 through 3059
```

Required results:

- all preserved partial rows through loop index `3058` reproduced;
- raw-route failure at loop index `3059`, stage 2 reproduced;
- real-compatible route evaluated at the same state;
- real-compatible route passes the historical `1.0e-13` gate;
- baseline accepted state remains identical;
- real shadow work remains within the frozen material-change limits;
- execution stops immediately after the comparison.

This design does not authorize that execution yet.

---

## 10. Frozen remediation integrity gates

The focused remediation verification shall require:

### 10.1 Source identity

- protected solver SHA-256 unchanged;
- advection-operator Git blob unchanged;
- original Stage C runner unchanged;
- focused localization runner unchanged;
- localization evidence report unchanged;
- focused evidence inventory unchanged.

### 10.2 State identity

- baseline current-state hash unchanged by shadow evaluation;
- baseline RK2 stage-state hash unchanged;
- accepted filtered-state hash unchanged;
- forcing hash unchanged;
- solver wavenumber arrays unchanged.

### 10.3 Historical reproduction

- last passing loop index `3058` reproduced;
- first failing loop index `3059` reproduced;
- raw failing quantity reproduced;
- raw failing ratio reproduced within frozen comparison tolerance;
- all seven last-passing operator-work values reproduced.

### 10.4 Real-compatible route

- real-compatible failing-quantity ratio `<= 1.0e-13`;
- real-compatible arrays finite;
- real-compatible Hermitian residual lower than raw residual;
- relevant Nyquist-line power remains measurable;
- no denominator-floor classification.

### 10.5 Real-result preservation

- real derivative relative RMS difference `<= 1.0e-10`;
- real transport relative RMS difference `<= 1.0e-10`;
- work absolute difference `<= 1.0e-14` or relative difference `<= 1.0e-6`;
- no nonzero work-sign change;
- no near-zero/nonzero character change under the frozen `1.0e-14` work scale.

---

## 11. Remediation implementation boundary

A future implementation may modify only a new remediation runner or a new
shadow-diagnostic helper local to that runner.

It may not modify:

```text
project/solver/spectral_solver.py
project/solver/advection_operators.py
project/solver/selectable_advection_solver.py
run_stage_c_same_state_advection_shadow_audit.py
run_stage_c_nyquist_failure_localization.py
```

The original runners and evidence remain historical references.

A remediated full Stage C runner, if later justified, must be created as a new
file with a new name and a separately archived design checkpoint.

---

## 12. Proposed focused remediation runner

Prospective filename:

```text
run_stage_c_shadow_nyquist_remediation_verification.py
```

Required command modes:

```powershell
python -B .\run_stage_c_shadow_nyquist_remediation_verification.py inspect
python -B .\run_stage_c_shadow_nyquist_remediation_verification.py run
```

This design permits future creation and static inspection only after this
design is committed and pushed.

It does not authorize numerical execution.

---

## 13. Static inspection requirements

Future `inspect` mode shall verify:

- exact filename;
- LF-only UTF-8 source;
- syntax compilation;
- exact design checkpoint;
- expected parent commit;
- only the remediation runner is untracked;
- protected source identities;
- evidence identities;
- output-header uniqueness;
- exactly one baseline solver construction in the run path;
- no protected or selectable `run()` call;
- no selectable stepping call;
- no alternate-trajectory variable;
- no full Stage C classification string;
- raw and real-compatible derivative routes both present;
- local copied wavenumber arrays present;
- solver wavenumber mutation absent;
- hard stop at loop index `3059`;
- no files written during inspection;
- no solver construction during inspection;
- no numerical timestep during inspection;
- no Git mutation.

Inspection must conclude:

```text
Focused remediation numerical execution authorized by inspection: NO
Full Stage C rerun authorized: NO
```

---

## 14. Focused remediation output bundle

A future controlled focused verification may create one Git-ignored directory
under:

```text
experiments/advection_form_shadow_audit_remediation/
```

Required files:

1. `run_metadata.json`;
2. `raw_and_real_compatible_trace.csv`;
3. `real_work_comparison.csv`;
4. `remediation_summary.json`;
5. `STAGE_C_SHADOW_NYQUIST_REMEDIATION_VERIFICATION_REPORT.md`;
6. `file_inventory.csv`.

No full 20,001-step Stage C tables are authorized.

No Stage C specificity classification is authorized.

---

## 15. Permitted focused remediation conclusions

A future focused remediation verification may return exactly one primary
conclusion:

```text
SHADOW NYQUIST REMEDIATION CONSISTENT WITH LOCALIZATION
SHADOW NYQUIST REMEDIATION NOT CONSISTENT WITH LOCALIZATION
SHADOW NYQUIST REMEDIATION INCONCLUSIVE
NUMERICAL INTEGRITY FAILURE
```

It may return exactly one real-effect conclusion:

```text
REAL SHADOW WORK PRESERVED UNDER REMEDIATION
REAL SHADOW WORK MATERIALLY CHANGED UNDER REMEDIATION
REAL SHADOW WORK EFFECT INCONCLUSIVE
```

These are implementation-level remediation conclusions.

They are not method rankings and are not full Stage C conclusions.

---

## 16. Full Stage C rerun gate

A full Stage C rerun remains prohibited until all of the following exist as
separate clean checkpoints:

1. this remediation design;
2. a new focused remediation runner;
3. static inspection of that runner;
4. one focused remediation verification through loop index `3059`;
5. an archived focused remediation evidence report;
6. a separate full-run authorization design.

No item in this list may be inferred from a console-only result.

---

## 17. Failure policy

Any focused remediation failure must:

- preserve partial output;
- record the failed gate;
- record the loop index and stage;
- record raw and real-compatible ratios;
- record source identities;
- stop immediately;
- prohibit automatic rerun;
- leave the original evidence unchanged.

---

## 18. Interpretation boundary

A successful focused remediation verification would support only:

> The shadow-only real-compatible derivative convention reproduces the
> localization result at the original failure point without materially changing
> real shadow work under the frozen thresholds.

It would not establish:

- full-run operator-form specificity;
- alternate-trajectory behavior;
- method superiority;
- formal convergence;
- physical validation;
- turbulence;
- cascade behavior;
- a spectral law;
- production readiness.

---

## 19. Current decision

The shadow-diagnostic-only Nyquist remediation is specified at the design
level.

The protected baseline solver remains untouched.

The accepted baseline update remains untouched.

The historical raw-route failure remains preserved.

No remediated numerical execution has been authorized.

No full Stage C rerun has been authorized.

The next controlled task, after this design is archived, is creation and static
inspection of the focused remediation-verification runner.
