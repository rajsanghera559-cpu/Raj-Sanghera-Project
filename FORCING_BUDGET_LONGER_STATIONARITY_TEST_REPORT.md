# Longer Forcing-Budget Stationarity Test Report

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Evidence archive checkpoint: `2ce245b`
- Design checkpoint:
  `3af047b12429bb75f2b4d8eb4d9437cdca4c3a82`
- Authorized execution checkpoint:
  `9a9f2e0618cf290e0b658a3dc565e5ca42f26f38`
- Run ID:
  `forcing_budget_stationarity_20260719T083403Z_9a9f2e0`
- Created UTC: `2026-07-19T08:48:22+00:00`
- Report type: post-run evidence interpretation
- New numerical execution for this report: none
- Numerical rerun for this report: none
- Protected solver modification: none
- Protected solver `run()` call: none
- Spectral slope fitting: none

### Claim status

- Stationarity candidate: not established
- Formal convergence: not established
- Physical validation: not established
- Turbulence: not established
- Cascade: not established
- Inertial range: not established
- `k^-3` law: not established
- Method superiority: not established
- Production readiness: not established

---

## 1. Executive result

The controlled longer forcing-budget test completed all 20,001 planned
updates and reached physical time

\[
t=100.005.
\]

The prospectively specified final classification was

> **NOT STATIONARY WITHIN TESTED DURATION**

This classification is a valid scientific result, not a numerical-execution
failure.

The energy budget approached a slowly varying balance over the fixed final
window, but the enstrophy budget did not. The energy drift, energy
injection-dissipation balance, and energy residual gates passed. The
enstrophy drift, enstrophy balance, and two enstrophy residual gates failed.

The run therefore does not support a stationarity claim for the tested
configuration.

---

## 2. Test purpose

The test addressed one controlled question:

> Does the `N=64` RMS-matched deterministic low-wave-number multimode forced
> response approach a budget-balanced, slowly varying state within
> `0<t<=100.005`?

The test was designed as a stationarity screen only.

It was not designed to establish:

- numerical convergence;
- physical validation;
- turbulence;
- an energy or enstrophy cascade;
- an inertial range;
- a spectral exponent;
- method superiority.

---

## 3. Frozen numerical configuration

| Parameter | Value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Completed updates | `20001` |
| Final physical time | `100.005` |
| Initial vorticity | exact zero |
| Integrator | external mirror of protected RK2 |
| Protected solver `run()` | not called |
| Dealiasing | inherited protected two-thirds mask |
| Budget output interval | 100 loop indices |
| Budget sampling interval | 0.5 time units |
| Spectrum output interval | 500 loop indices |
| Spectrum sampling interval | 2.5 time units |

The run reached the complete planned duration without numerical interruption.

---

## 4. Frozen forcing definition

The vorticity-source field was

\[
f_\omega(x,y)
=
c\Big[
\sin(2x)\cos(2y)
+
0.75\sin(3x)\cos(y)
+
0.50\sin(x)\cos(4y)
+
0.35\cos(4x-2y)
\Big].
\]

The coefficient was fixed once at initialization:

\[
c=0.006971561743757498.
\]

Recorded forcing properties:

| Quantity | Value |
|---|---:|
| Base single-mode RMS | `0.005` |
| Raw multimode RMS | `0.7171994143890527` |
| Normalized multimode RMS | `0.005` |
| Forcing mean | `-3.5507761769604404e-21` |
| Maximum absolute forcing | `0.015914546647182223` |
| Array shape | `64 x 64` |
| Array dtype | `float64` |
| Finite | true |
| Real | true |
| Writeable after construction | false |

Forcing-array SHA-256:

```text
504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB
```

The forcing identity matched at every recorded output.

---

## 5. Source and runner identities

| Item | SHA-256 |
|---|---|
| Stationarity design | `91C0ACFDF526CF5C86309ACCB5033892644A36326DA3D3D7F4A01DA6565A46C6` |
| Standalone stationarity runner | `95EF84BDF29564BD5AB404481844113CC3F92CF6CC579D4419A13BD81644EDAA` |
| Protected spectral solver | `1195AF013057C31FC227FECD05DBCB277553D340096C0348F53DFE79A7A483C1` |
| Forcing-budget diagnostic | `A9A98C605DBB2E0289A1299008B39B08B72746FDE2EEAABE8344B2FB7D9E323B` |

The protected source hashes matched the expected identities during execution.

---

## 6. Evidence bundle

The archived run produced six files.

| File | Bytes | SHA-256 |
|---|---:|---|
| `run_metadata.json` | `4815` | `57640568F657C26E47F495B1BE7C4C23F54EF0ACB882250ECB596A426F504ED9` |
| `forcing_budget.csv` | `130166` | `38D01CE7278979EB4D7433414C849F65820C729DC5928A964FFED1EB3E4F482F` |
| `forcing_spectra.csv` | `648198` | `62235ED6A5C9BD17D4FF21D22A1F830EE637FC22F26ABD43B483359B5873275A` |
| `stationarity_window.csv` | `27832` | `FD1C5017DC24C6BF9F12F3BB56E44631491BA8178B174968743175976C06ED9A` |
| `stationarity_summary.json` | `13231` | `3573F19100A4BD817B97C603B3C13D0137AD56D1F52FD05D602DFFC6400DBE1E` |
| `file_inventory.csv` | `662` | `3745C4E279E304A1A04CA14CEFE04BAA0FABD1A6072BB2E4C407FAB78CA1A028` |

Inventory verification passed for every non-inventory file.

The inventory intentionally omitted its own internal self-hash to avoid
circular self-reference.

---

## 7. Evidence counts

| Evidence category | Count |
|---|---:|
| Budget snapshots | `201` |
| Spectrum snapshots | `41` |
| Spectrum rows | `1845` |
| Stationarity-window snapshots | `41` |
| Stationarity-window residual intervals | `40` |

The expected counts were achieved.

---

## 8. Prospectively fixed stationarity window

The fixed analysis window was

\[
80.005\le t\le100.005.
\]

Its duration was

\[
\Delta T=20.
\]

The window contained 41 stored budget snapshots and was divided into four
fixed subwindows:

1. `80.005 <= t <= 85.005`;
2. `85.005 < t <= 90.005`;
3. `90.005 < t <= 95.005`;
4. `95.005 < t <= 100.005`.

No alternate window was selected after execution.

---

## 9. Decision thresholds

The stationarity-candidate gates were:

| Criterion | Required limit |
|---|---:|
| Energy normalized drift | `<= 0.05` |
| Enstrophy normalized drift | `<= 0.05` |
| Energy balance metric | `<= 0.10` |
| Enstrophy balance metric | `<= 0.10` |
| Each energy subwindow deviation | `<= 0.10` |
| Each enstrophy subwindow deviation | `<= 0.10` |
| Median normalized energy residual | `<= 0.01` |
| Maximum normalized energy residual | `<= 0.05` |
| Median normalized enstrophy residual | `<= 0.01` |
| Maximum normalized enstrophy residual | `<= 0.05` |

All numerical-integrity gates also had to pass.

---

## 10. Gate results

| Criterion | Observed | Limit | Result |
|---|---:|---:|---|
| Energy normalized drift | `0.0056531886689457364` | `0.05` | PASS |
| Enstrophy normalized drift | `0.18316303915302523` | `0.05` | FAIL |
| Energy balance metric | `0.004718866187377041` | `0.10` | PASS |
| Enstrophy balance metric | `0.3580633279251752` | `0.10` | FAIL |
| All energy subwindow deviations | all passed | `0.10` | PASS |
| All enstrophy subwindow deviations | all passed | `0.10` | PASS |
| Median normalized energy residual | `0.006975630021169467` | `0.01` | PASS |
| Maximum normalized energy residual | `0.010790902277951337` | `0.05` | PASS |
| Median normalized enstrophy residual | `0.05107587377269546` | `0.01` | FAIL |
| Maximum normalized enstrophy residual | `0.05843424054745961` | `0.05` | FAIL |
| Numerical-integrity gates | passed | required | PASS |
| Full run reached `t=100.005` | true | required | PASS |

Four required stationarity gates failed.

The resulting classification was therefore correct.

---

## 11. Window means

Over the fixed final window:

| Quantity | Window mean |
|---|---:|
| Energy | `0.003070787073228494` |
| Enstrophy | `0.02262705894043823` |
| Energy injection rate | `4.546867849038948e-05` |
| Enstrophy injection rate | `0.0004056060526304712` |
| Viscous energy dissipation rate | `4.5254117880876465e-05` |
| Viscous enstrophy dissipation rate | `0.0006318474551695239` |

The mean energy injection and dissipation were close.

The mean enstrophy dissipation remained substantially larger than the mean
enstrophy injection.

---

## 12. Injection-dissipation balance

### 12.1 Energy

The fixed-window mean ratio was

\[
\frac{\overline{\varepsilon_f}}
{\overline{D_E}}
=
1.0047412394619604.
\]

The energy balance metric was

\[
B_E=0.004718866187377041.
\]

This passed the prospective limit of `0.10`.

The energy channel was therefore close to mean injection-dissipation balance
over the final window.

### 12.2 Enstrophy

The fixed-window mean ratio was

\[
\frac{\overline{\eta_f}}
{\overline{D_Z}}
=
0.6419366720748247.
\]

The enstrophy balance metric was

\[
B_Z=0.3580633279251752.
\]

This failed the prospective limit of `0.10`.

The final-window enstrophy dissipation exceeded enstrophy injection by a
substantial margin.

---

## 13. Trend analysis

### 13.1 Energy

The energy slope over the fixed window was

\[
b_E=-8.679869343560182\times10^{-7}.
\]

The normalized drift was

\[
S_E=0.0056531886689457364.
\]

This corresponds to approximately `0.565%` normalized change across the
20-time-unit window and passed the `5%` limit.

### 13.2 Enstrophy

The enstrophy slope was

\[
b_Z=-2.0722204413126485\times10^{-4}.
\]

The normalized drift was

\[
S_Z=0.18316303915302523.
\]

This corresponds to approximately `18.316%` normalized change across the
window and failed the `5%` limit.

### 13.3 Injection and dissipation trends

| Quantity | Normalized drift |
|---|---:|
| Energy injection | `0.28401436613055825` |
| Enstrophy injection | `0.25972446736026794` |
| Viscous energy dissipation | `0.18316303915302526` |
| Viscous enstrophy dissipation | `0.2034742916968052` |

These diagnostics show that the individual injection and dissipation terms
continued to evolve even though their energy-channel means were close over the
fixed window.

---

## 14. Subwindow consistency

### 14.1 Energy subwindows

| Subwindow | Mean energy | Deviation from full-window mean | Result |
|---|---:|---:|---|
| 1 | `0.003074341562398693` | `0.0011575173027095942` | PASS |
| 2 | `0.003079274410707417` | `0.002763896446261833` | PASS |
| 3 | `0.003067566767119791` | `0.001048690785752632` | PASS |
| 4 | `0.003061610103771054` | `0.0029884746934901924` | PASS |

### 14.2 Enstrophy subwindows

| Subwindow | Mean enstrophy | Deviation from full-window mean | Result |
|---|---:|---:|---|
| 1 | `0.024197330029039513` | `0.06939793159750668` | PASS |
| 2 | `0.02310982935328959` | `0.021335977164428206` | PASS |
| 3 | `0.021994642320933334` | `0.027949572287305283` | PASS |
| 4 | `0.021049406949630353` | `0.06972412963438018` | PASS |

All subwindow deviations remained below the `0.10` threshold.

However, the monotonic decline in the enstrophy subwindow means is also
consistent with the failed full-window enstrophy drift gate.

---

## 15. Budget-residual interpretation

The stored interval diagnostics used a budget sampling interval of `0.5`.

### 15.1 Energy residuals

| Metric | Observed | Limit | Result |
|---|---:|---:|---|
| Median normalized residual | `0.006975630021169467` | `0.01` | PASS |
| Maximum normalized residual | `0.010790902277951337` | `0.05` | PASS |

The energy interval-budget residuals were within the prospective integrity
limits.

### 15.2 Enstrophy residuals

| Metric | Observed | Limit | Result |
|---|---:|---:|---|
| Median normalized residual | `0.05107587377269546` | `0.01` | FAIL |
| Maximum normalized residual | `0.05843424054745961` | `0.05` | FAIL |

The enstrophy residuals exceeded both prospective limits.

This does not prove timestep nonconvergence. The residuals may include
discrete-advection, filtering, time-integration, and finite sampling effects.

The result does show that the stored enstrophy budget did not meet the
prospectively defined integrity standard at this cadence and configuration.

---

## 16. Final budget snapshot

At `t=100.005`:

| Quantity | Value |
|---|---:|
| Energy | `0.003062956683543696` |
| Enstrophy | `0.020685325366307034` |
| Energy injection | `4.345137804267879e-05` |
| Energy dissipation | `4.1370650732614066e-05` |
| Enstrophy injection | `0.0003884831864491168` |
| Enstrophy dissipation | `0.0005621313744810756` |
| Continuous energy RHS | `2.0807273100647205e-06` |
| Continuous enstrophy RHS | `-0.0001736481880319588` |
| Observed energy rate | `1.4361924112141905e-06` |
| Observed enstrophy rate | `-0.0001511657143501502` |
| Normalized energy residual | `0.010790902277951337` |
| Normalized enstrophy residual | `0.04336268462912876` |
| Stage-1 advection RMS | `0.017217945155243646` |
| Stage-2 advection RMS | `0.017217871797427807` |
| Mask-removal RMS | `2.7705828452027027e-06` |
| Vorticity RMS | `0.20339776481715346` |
| Maximum absolute vorticity | `0.6634938829443502` |

At the final snapshot, energy was still increasing slowly, while enstrophy was
decreasing.

---

## 17. Temporal evolution

The progress record shows the following broad stages.

### 17.1 Early forced growth

From `t=0.005` through approximately `t=60`, both energy and enstrophy grew
strongly while injection exceeded dissipation.

### 17.2 Enstrophy peak and turnover

Enstrophy reached its largest recorded progress value near `t=75.005`:

\[
Z\approx0.02481506.
\]

It then declined through the remainder of the run:

\[
Z(80.005)\approx0.02459302,
\]

\[
Z(90.005)\approx0.02259283,
\]

\[
Z(100.005)\approx0.02068533.
\]

This declining final-window behavior is the primary reason the enstrophy drift
gate failed.

### 17.3 Energy near plateau

Energy increased through most of the run and approached a broad plateau near
the final window:

\[
E(80.005)\approx0.00306014,
\]

\[
E(85.005)\approx0.00308212,
\]

\[
E(90.005)\approx0.00307455,
\]

\[
E(100.005)\approx0.00306296.
\]

The small final-window energy drift passed the prospective gate.

---

## 18. Nonlinear activity and filtering

Global integrity metrics recorded:

| Quantity | Maximum |
|---|---:|
| Advection RMS over all steps | `0.017223401076415394` |
| Mask-removal RMS over all steps | `5.5143894587390165e-06` |
| Spectrum-energy consistency error | `5.810850255710926e-16` |

The nonlinear advection term was materially active.

The dealiasing-mask removal remained much smaller than the advection RMS.

Direct energy and spectrum-summed energy agreed to near machine precision.

---

## 19. Final spectral state

At `t=100.005`:

| Spectral quantity | Value |
|---|---:|
| Dominant shell | `2` |
| Shell-1 energy | `0.0006001522876401624` |
| Shell-2 energy | `0.0012914123374708456` |
| Shell-3 energy | `0.000815429895322484` |
| Shell-4 energy | `0.0002825248990834166` |
| Fraction at `k<=4` | `0.9760240605355792` |
| Fraction at `5<=k<=9` | `0.023525745107484806` |
| Fraction at `k>=10` | `0.0004501943569360326` |
| Fraction at `k>4` | `0.02397593946442084` |
| Spectrum energy sum | `0.003062956683543695` |
| Direct energy | `0.003062956683543696` |
| Relative consistency error | `2.8317793152233123e-16` |

The spectrum remained predominantly low-wave-number.

Approximately `97.60%` of the kinetic energy remained at `k<=4`.

Approximately `2.40%` was above shell 4.

Approximately `0.045%` was at `k>=10`.

---

## 20. Dominant-shell transition

The dominant shell was shell 3 through most of the run.

The progress record showed shell 2 becoming dominant by approximately

\[
t=87.505.
\]

The final shell ordering was:

\[
E_{k=2}>E_{k=3}>E_{k=1}>E_{k=4}.
\]

This is evidence of low-wave-number spectral redistribution.

It is not, by itself, evidence of an inverse cascade.

A cascade claim would require additional flux diagnostics, scale separation,
stationarity, and matched numerical checks that were not part of this test.

---

## 21. Spectral broadening

The fraction above shell 4 increased from negligible early values to

\[
0.02397593946442084
\]

at the final time.

The fraction at `k>=10` remained much smaller:

\[
0.0004501943569360326.
\]

The test therefore supports limited nonlinear spectral broadening beyond the
directly forced low-wave-number structure.

It does not support a resolved inertial range or a power-law spectrum.

No spectral slope was fitted.

---

## 22. Numerical integrity

The following integrity conditions passed:

- all planned updates completed;
- all expected evidence counts were achieved;
- vorticity remained finite;
- forcing remained finite and byte-identical;
- protected source identities remained unchanged;
- all persistent outputs were written;
- direct and spectral energy remained consistent;
- the protected solver `run()` method was not called;
- the run exited successfully;
- the complete evidence bundle was archived.

The final classification did not result from a numerical crash.

---

## 23. Scientific interpretation

The tested flow reached a state in which the energy channel was close to
mean injection-dissipation balance and exhibited little net drift over the
fixed final window.

The enstrophy channel remained materially out of balance and continued to
decline. Its window drift and balance metrics failed by substantial margins.

This suggests that energy and enstrophy were evolving on different effective
timescales under the tested forcing and dissipation.

The test duration was sufficient to show that an energy plateau alone would
have been an inadequate stationarity criterion.

The prospective multi-gate design prevented that false positive.

---

## 24. Supported findings

The archived evidence supports the following statements:

1. The full 20,001-step `N=64` test completed successfully.
2. The forcing remained deterministic, time independent, and RMS matched.
3. Nonlinear advection was active.
4. The energy channel approached a slowly varying mean balance over the fixed
   final window.
5. The enstrophy channel did not satisfy the fixed stationarity criteria.
6. The dominant radial shell shifted from 3 to 2 during the later run.
7. The response developed limited spectral broadening above shell 4.
8. The response remained overwhelmingly low-wave-number dominated.
9. Direct and spectrum-summed kinetic energy agreed to numerical precision.
10. The tested configuration was not stationary within the prospectively
    fixed duration.

---

## 25. Unsupported claims

This report does not support:

- formal numerical convergence;
- timestep independence;
- resolution independence;
- an asymptotic numerical regime;
- physical validation;
- turbulence validation;
- an inverse-energy cascade;
- a direct-enstrophy cascade;
- an inertial range;
- a `k^-3` spectral law;
- method superiority;
- production readiness.

The shell-3 to shell-2 transition must not be described as an inverse cascade
without flux evidence and additional validation.

The energy plateau must not be described as full stationarity because the
enstrophy criteria failed.

---

## 26. Decision

> The longer forcing-budget stationarity test is complete and archived.

> The correct result is `NOT STATIONARY WITHIN TESTED DURATION`.

No rerun or automatic extension is authorized.

The archived evidence should remain unchanged.

---

## 27. Recommended next research step

The next step should be analysis and design, not immediate execution.

A defensible follow-on document should examine whether the failed enstrophy
residual gates arise primarily from:

- the `0.5` budget sampling interval;
- the discrete advection operator;
- dealiasing/filtering removal;
- RK2 temporal error;
- genuine continuing enstrophy evolution;
- or a combination of these effects.

Any new execution should be separately designed and should not overwrite,
replace, or reinterpret the archived `t=100.005` result.

---

## 28. Final claim statement

The strongest supported statement is:

> Under the frozen `N=64`, `Re=1000`, `dt=0.005` RMS-matched deterministic
> multimode configuration, the energy budget became nearly balanced and slowly
> varying over `80.005<=t<=100.005`, but the enstrophy drift, enstrophy
> injection-dissipation balance, and enstrophy residual criteria did not satisfy
> the prospectively specified limits. The tested response is therefore
> classified as not stationary within the tested duration.
