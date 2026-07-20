# Stage B Exact Operator-Ledger Evidence Report

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Runner-design commit:
  `2109b2d6046302085b47cb2219e61231432b1b03`
- Execution commit:
  `5c464c21f61e917f26e00c73c5ec691fadc2bed9`
- Runner:
  `run_stage_b_exact_operator_ledger_replay.py`
- Runner SHA-256:
  `970AE47D4DF69819FA6D831557FC2679D843B860D901CF367361A3A34126E246`
- Exact-ledger design SHA-256:
  `584A94C8A857D4869A95CC01BE31108CDFBC201C0BF56C03A0A8F9860D083B4C`
- Runner-design SHA-256:
  `A0E039CAFF9A71BBB8CA33C9043169C24CDC0E1B1F330F829752BE11F45C4710`
- Run ID:
  `stage_b_exact_operator_ledger_20260720T063420Z_5c464c2`
- Created UTC:
  `2026-07-20T06:46:14+00:00`
- Evidence type:
  completed exact implemented-operator ledger replay
- Numerical rerun authorized:
  no
- Protected solver `run()` called:
  no
- Original evidence modified after execution:
  no

---

## 1. Stage B decision

> **LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION**

This classification applies to the implemented discrete RK2-plus-mask
enstrophy ledger.

It does not establish unique physical causation.

---

## 2. Frozen configuration

| Parameter | Value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Completed updates | `20001` |
| Final physical time | `100.005` |
| Initial vorticity | exact zero |
| Forcing RMS | `0.005` |
| Ledger cadence | every update |
| High-cadence budget interval | 10 updates / 0.05 time units |
| Archived replay comparison interval | 100 updates / 0.5 time units |

---

## 3. Evidence directory

```text
experiments/forcing_budget_stage_b_ledger/
stage_b_exact_operator_ledger_20260720T063420Z_5c464c2/
```

The original seven-file evidence bundle is preserved exactly as generated.

---

## 4. Evidence identities

External `file_inventory.csv` SHA-256:

```text
A29D6D1E774E96D6C197B05C7124388EC5AE8A962DACA7B5938A92AAAB07F2C9
```

| File | Bytes | SHA-256 |
|---|---:|---|
| `run_metadata.json` | `5475` | `08FF6613861561E0A508650946DF82CC3B15AB4A8A72AAD683C53C34B63B5538` |
| `operator_ledger_per_step.csv` | `25732597` | `5EABDFB33B932089910B61C119A223EED83D4EF9247593C3B02DA68B1D74B115` |
| `high_cadence_budget.csv` | `1117846` | `BC05B327A5728B2F6C3DE876F73EAE3F5067F689C377A261EF94C3A91AFC98D9` |
| `operator_ledger_time_blocks.csv` | `11421` | `3D0A289FF0730AE2AE107711D3F7EBDE93E81151A6524A2ED4EC6B69A64280FB` |
| `operator_ledger_final_window.csv` | `5146682` | `ADA03C5BE2B65E6CB09CD92C634300B8B518A499C3282A2E8DD1DB4C73022E61` |
| `operator_ledger_summary.json` | `45759` | `A3A0633401B071774E72188E6574EFB2A1C92D33C1502E778EAF68CA6FAA9600` |
| `file_inventory.csv` | inventory self-hash omitted | external hash recorded above |

The read-only post-run audit verified every recorded byte count and SHA-256.

---

## 5. Record-count and replay-equivalence results

| Check | Result |
|---|---:|
| Exact per-step ledger rows | `20001` |
| High-cadence budget rows | `2001` |
| Final-window ledger rows | `4001` |
| Time-block rows | `6` |
| Archived comparison points | `201` |
| Archived comparisons passed | `201 / 201` |
| Failed per-step integrity gates | `0` |
| Final completed loop index | `20000` |

Every archived replay field matched exactly at all 201 comparison points.

---

## 6. Exact ledger

For every accepted update, the replay evaluated

\[
\frac{Z(\omega_{n+1})-Z(\omega_n)}{\Delta t}
=
R_A+R_V+R_F+R_{\mathrm{RK2}}+R_P.
\]

The terms were:

- `R_A`: stage-weighted discrete-advection enstrophy work;
- `R_V`: stage-weighted viscous enstrophy work;
- `R_F`: stage-weighted forcing enstrophy work;
- `R_RK2`: exact nonnegative quadratic RK2 remainder;
- `R_P`: exact signed post-step mask contribution.

---

## 7. Closure and cross-check integrity

| Integrity quantity | Maximum observed | Frozen limit | Result |
|---|---:|---:|---|
| Normalized filtered ledger closure | `2.645205267472769e-12` | `1e-10` | PASS |
| Normalized unfiltered ledger closure | `1.6528296892035835e-12` | `1e-10` | PASS |
| Normalized physical/spectral mask-loss mismatch | `5.743748687057573e-16` | `1e-10` | PASS |
| Normalized inverse-FFT imaginary ratio | `2.271716286257875e-16` | `1e-13` | PASS |

No numerical-integrity gate failed.

---

## 8. Time-block attribution

All six blocks returned the same implemented-ledger classification:

> **LEADING LEDGER CONTRIBUTOR: DISCRETE ADVECTION**

| Block | Time range | Advection share | RK2 share | Mask share |
|---:|---|---:|---:|---:|
| 1 | `0.005 <= t <= 20.005` | `0.9999999982643` | `1.718028965646e-09` | `1.771525019936e-11` |
| 2 | `20.005 < t <= 40.005` | `0.9999989153813` | `2.006237642452e-10` | `1.084418039985e-06` |
| 3 | `40.005 < t <= 60.005` | `0.9999870996122` | `4.037637080256e-10` | `1.289998401875e-05` |
| 4 | `60.005 < t <= 80.005` | `0.9999683406343` | `1.753340622873e-09` | `3.165761239276e-05` |
| 5 | `80.005 < t <= 100.005` | `0.9999370944163` | `9.319683494680e-09` | `6.289626401302e-05` |
| 6 | full run | `0.9999594074287` | `4.670712634743e-09` | `4.058790061827e-05` |

These shares compare only the three non-forcing/non-viscous ledger terms:

\[
R_A,\quad R_{\mathrm{RK2}},\quad R_P.
\]

They do not say that advection was the largest term in the complete
forcing-viscosity-advection budget.

---

## 9. Full-run integrated ledger contributions

| Component | Integrated signed contribution |
|---|---:|
| Discrete advection | `+0.0015368528716236765` |
| Viscosity | `-0.035906168942000216` |
| Forcing | `+0.055054703809584646` |
| RK2 remainder | `+7.178489518581576e-12` |
| Mask | `-6.23801637896089e-08` |
| Observed accepted-state change | `+0.020685325366307034` |

The complete full-run balance is consistent with the exact ledger and the
final accepted enstrophy.

---

## 10. Final-window result

For `80.005 < t <= 100.005`:

| Component | Mean signed rate | Integrated signed |
|---|---:|---:|
| Discrete advection | `+3.2414560868477325e-05` | `+0.0006482912173695466` |
| Viscosity | `-0.0006322622625405596` | `-0.012645245250811192` |
| Forcing | `+0.000404465219824691` | `+0.00808930439649382` |
| RK2 remainder | `+3.0211245247339874e-13` | `+6.0422490494679745e-12` |
| Mask | `-2.03888303537723e-09` | `-4.07776607075446e-08` |
| Observed accepted-state rate | `-0.00019538452042704003` | `-0.0039076904085408` |

The final-window enstrophy declined at every one of the 4000 recorded steps.

The positive discrete-advection contribution partly offset the decline, but
viscous removal exceeded forcing plus discrete advection.

The previously archived classification therefore remains:

> **NOT STATIONARY WITHIN TESTED DURATION**

---

## 11. Final exact ledger row

At physical time `100.005`:

| Quantity | Value |
|---|---:|
| Filtered enstrophy | `0.020685325366307034` |
| `R_A` | `+2.4319993912495697e-05` |
| `R_V` | `-0.0005621446291289011` |
| `R_F` | `+0.0003884767382714701` |
| `R_RK2` | `+5.105411083200017e-13` |
| `R_P` | `-7.676129302135587e-10` |
| Observed accepted-step rate | `-0.00014934866404622826` |
| Normalized filtered closure | `1.1243287866438782e-12` |

---

## 12. Stage A interpretation corrected by Stage B

Stage A found strong descriptive correlation between the old normalized
enstrophy residual and both:

- stage-advection RMS;
- mask-removal RMS.

Those correlations did not distinguish exact scalar ledger contributions.

Stage B directly calculated the missing terms.

The exact result is:

- discrete-advection work dominates the omitted
  non-forcing/non-viscous activity;
- exact mask enstrophy loss is small;
- the exact RK2 remainder is negligible at the tested timestep.

Therefore, mask-removal RMS was a correlated activity indicator, not evidence
that the mask supplied most of the missing scalar enstrophy budget.

---

## 13. Localized CSV schema defect

`operator_ledger_time_blocks.csv` contains 93 header fields and six valid data
rows.

Three header names appear twice:

| Duplicate header | Zero-based positions | Duplicate values |
|---|---|---|
| `advection_integrated_signed` | `[18, 34]` | identical in all six rows |
| `rk2_integrated_signed` | `[19, 61]` | identical in all six rows |
| `mask_integrated_signed` | `[20, 70]` | identical in all six rows |

Cause:

- the three attribution columns were declared explicitly;
- the generic component-statistics expansion generated the same three names
  again.

Impact:

- PowerShell `Import-Csv` rejects the file because it requires unique property
  names;
- positional CSV reading remains valid;
- all six rows have the expected 93 fields;
- both copies of each duplicate column contain identical values;
- the valid JSON summary contains the same time-block results;
- no numerical result, ledger row, byte count, or evidence hash was changed.

Disposition:

> Preserve the CSV exactly as generated and record the schema defect in this
> report. Do not regenerate or rerun the evidence.

---

## 14. Evidence status

- Original seven-file evidence bundle: complete
- Inventory verification: PASS
- Exact ledger integrity: PASS
- Archived replay equivalence: PASS
- Attribution classification: complete
- CSV schema defect: localized and non-numerical
- Numerical rerun: prohibited
- Evidence regeneration: prohibited

---

## 15. Claim boundaries

This Stage B evidence does not establish:

- formal temporal convergence;
- formal spatial convergence;
- physical validation;
- unique physical causation;
- turbulence;
- a cascade;
- an inertial range;
- a `k^-3` law;
- method superiority;
- production readiness.

It establishes an exact implemented-operator ledger for one frozen
configuration and identifies discrete advection as the leading omitted
non-forcing/non-viscous ledger contributor.

---

## 16. Archive decision

The Stage B evidence is suitable for archival **as generated**, accompanied by
this schema-defect report.

No rerun is authorized.
