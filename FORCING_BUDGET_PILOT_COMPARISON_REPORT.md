# Forcing Budget Pilot Comparison Report

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Source checkpoint: `59d28a6`
- Report scope: comparison of two archived short forcing-budget pilots
- New numerical execution for this report: none
- Analytic pilot rerun: none
- Multimode pilot rerun: none
- Formal convergence claim: none
- Physical-validation claim: none
- Turbulence claim: none
- Cascade claim: none
- `k^-3` claim: none
- Method-superiority claim: none

---

## 1. Purpose

This report compares two controlled short forcing-budget pilots that used the
same numerical configuration but different vorticity-source geometries:

1. the default single-mode analytic control;
2. the RMS-matched deterministic low-wave-number multimode pilot.

The comparison addresses five questions:

1. Does equal forcing-field RMS produce equal energy injection?
2. Does equal forcing-field RMS produce equal enstrophy injection?
3. Does multimode forcing activate nonlinear advection?
4. Are the short runs close to injection-dissipation balance?
5. Has a meaningful high-wave-number spectral range developed by `t = 5.005`?

---

## 2. Common numerical configuration

Both pilots used:

- grid: `64 x 64`;
- Reynolds number: `1000`;
- viscosity: `0.001`;
- timestep: `0.005`;
- completed steps: `1001`;
- final physical time: `5.005`;
- initial vorticity: exact zero;
- forcing-field RMS: `0.005`;
- output interval: 100 loop indices;
- stored snapshots: 11;
- time integration: external mirror of the protected RK2 update;
- protected solver `run()` method: not called.

The protected solver and standalone budget diagnostic retained their frozen
source hashes during both runs.

---

## 3. Analytic single-mode control

### 3.1 Evidence identity

- Runner commit: `d39f374`
- Archived-result commit: `08b7cf8`
- Run ID:
  `forcing_budget_analytic_20260719T070250Z_d39f374`
- Runner:
  `run_forcing_budget_analytic_pilot.py`
- Runner SHA-256:
  `520D1BC1C44BD9F5277CDB1D621288EB03D32EAB40008844C6234DBB23ED11AF`

Archived result hashes:

| File | SHA-256 |
|---|---|
| `forcing_budget.csv` | `92F4D6FE1176C7D62841947820062C6B1E4701A665DFCCDEB8E9CED1BC78F227` |
| `run_metadata.json` | `4A4D8D4A69EC1FD21655F46354B7E28780876D3C2D5FB4FF94AD88D1A30F2034` |
| `summary.json` | `ACCBC46BBC7FA59B19C373584DB31DA5FE8E42F46CE9FA838B67DB779182A918` |

### 3.2 Forcing geometry

The control used

\[
f_\omega(x,y)=0.01\sin(2x)\cos(2y).
\]

Its Fourier components have coordinate wave numbers `(±2, ±2)` and radial
magnitude

\[
|k|=\sqrt{8}\approx2.828,
\]

which is represented in radial shell 3.

Starting from exact zero vorticity, this forcing preserves the isolated
Laplacian eigenmode. The nonlinear advection term remains at roundoff scale.

### 3.3 Pilot result

Classification:

> `ANALYTIC FORCING-BUDGET PILOT PASS`

Maximum recorded comparison errors:

| Quantity | Maximum relative error |
|---|---:|
| Energy | `5.322513866311e-10` |
| Enstrophy | `5.322513866311e-10` |
| Energy injection | `2.661257254405e-10` |
| Enstrophy injection | `2.661258598952e-10` |
| Viscous energy dissipation | `5.322514210213e-10` |
| Viscous enstrophy dissipation | `5.322514210213e-10` |

Additional control observations:

- maximum advection RMS:
  `1.826732491072e-17`;
- maximum mask-removal RMS:
  `6.180868782020e-18`;
- all declared analytic checks:
  PASS.

This establishes that the standalone budget formulas, time indexing, and
external RK2 mirror agree with the exact single-mode forced-diffusion
reference within the declared pilot tolerance.

---

## 4. RMS-matched multimode pilot

### 4.1 Evidence identity

- Runner commit: `5193d15`
- Archived-result commit: `59d28a6`
- Run ID:
  `forcing_budget_multimode_20260719T072157Z_5193d15`
- Runner:
  `run_forcing_budget_multimode_pilot.py`
- Runner SHA-256:
  `1BF1874A68ABBA281B73DC8A99444B771BB4BDAE9AA87CB21B948AD2294AD98A`

Archived result hashes:

| File | SHA-256 |
|---|---|
| `forcing_budget.csv` | `A23BD387239217FEE475115B178969457451624EA53EF7EC782D6F942833D36C` |
| `run_metadata.json` | `A75C54EF70AAA3EEA690C14F1B01D91F01A574764B265578B598D185E5E35547` |
| `summary.json` | `740D2A1530B917D1130F00B4FDFD71904637FC0633FBBF68DC1763CF503204FC` |

### 4.2 Forcing geometry

The pilot used the existing Phase 6D deterministic low-wave-number multimode
forcing:

\[
\sin(2X)\cos(2Y),
\]

\[
0.75\sin(3X)\cos(Y),
\]

\[
0.50\sin(X)\cos(4Y),
\]

and

\[
0.35\cos(4X-2Y).
\]

The combined field was rescaled to forcing RMS `0.005`, matching the
single-mode control.

### 4.3 Pilot result

Classification:

> `MULTIMODE FORCING-BUDGET PILOT PASS`

Recorded summary:

- forcing RMS:
  `5.000000000000e-03`;
- maximum advection RMS:
  `1.382031018008e-04`;
- maximum mask-removal RMS:
  approximately `7.70e-17` at the final stored snapshot;
- final dominant shell:
  `3`;
- final tail fraction at `k > 4`:
  `1.264900840531e-05`;
- final high-wave-number fraction at `k >= 10`:
  `1.978948087852e-11`;
- maximum absolute energy-budget residual:
  `1.552252841977e-09`;
- maximum absolute enstrophy-budget residual:
  `1.716510105153e-08`.

The multimode source activated nonlinear advection but remained strongly
low-wave-number dominated at the final short-pilot time.

---

## 5. Final-snapshot comparison

Both columns below correspond to 1001 completed steps and physical time
`t = 5.005`.

| Quantity | Single-mode control | RMS-matched multimode |
|---|---:|---:|
| Energy | `3.760945667130e-05` | `3.016811179391e-05` |
| Enstrophy | `3.008756533704e-04` | `2.963990690100e-04` |
| Forcing RMS | `5.000000000000e-03` | `5.000000000000e-03` |
| Energy injection rate | `1.533163736186e-05` | `1.235404486431e-05` |
| Enstrophy injection rate | `1.226530988949e-04` | `1.217249761697e-04` |
| Viscous energy dissipation rate | `6.017513067408e-07` | `5.927981380199e-07` |
| Viscous enstrophy dissipation rate | `4.814010453926e-06` | `6.508150038561e-06` |
| Continuous energy RHS | `1.472988605512e-05` | `1.176124672629e-05` |
| Continuous enstrophy RHS | `1.178390884410e-04` | `1.152168261311e-04` |
| Maximum advection RMS | `1.826732491072e-17` | `1.382031018008e-04` |

---

## 6. Derived comparison ratios

Using multimode divided by single-mode:

| Quantity | Ratio | Difference |
|---|---:|---:|
| Energy | `0.802141654360` | `-19.786%` |
| Enstrophy | `0.985121480219` | `-1.488%` |
| Energy injection | `0.805787703735` | `-19.421%` |
| Enstrophy injection | `0.992432945164` | `-0.757%` |
| Viscous energy dissipation | `0.985121480219` | `-1.488%` |
| Viscous enstrophy dissipation | `1.351918551247` | `+35.192%` |
| Continuous energy RHS | `0.798461487229` | `-20.154%` |
| Continuous enstrophy RHS | `0.977747092713` | `-2.225%` |

These numbers demonstrate that matching forcing-field RMS does not match the
state-dependent injection or dissipation rates.

---

## 7. Injection-to-dissipation balance

At the final snapshot:

### Single-mode control

\[
\frac{\varepsilon_f}{D_E}
=
25.4783615592,
\]

\[
\frac{\eta_f}{D_Z}
=
25.4783615592.
\]

The equal ratios reflect the isolated eigenmode structure.

### Multimode pilot

\[
\frac{\varepsilon_f}{D_E}
=
20.8402221127,
\]

\[
\frac{\eta_f}{D_Z}
=
18.7034680283.
\]

Both multimode ratios are far above 1.

Therefore, the short multimode pilot is not close to an
injection-dissipation balance. Energy and enstrophy are still accumulating.

---

## 8. Nonlinear activation

The analytic control recorded maximum advection RMS near

\[
1.83\times10^{-17},
\]

which is roundoff scale.

The multimode pilot recorded maximum advection RMS near

\[
1.38\times10^{-4}.
\]

The forcing-geometry change therefore activated measurable nonlinear
advection.

This is a supported numerical observation. It does not by itself establish
turbulence or a cascade.

---

## 9. Spectral status at `t = 5.005`

For the multimode pilot:

- shell-3 energy fraction:
  approximately `0.875872844989`;
- shell-4 energy fraction:
  approximately `0.124100078136`;
- fraction at `k > 4`:
  `1.264900840531e-05`;
- fraction at `k >= 10`:
  `1.978948087852e-11`.

The response is almost entirely confined to shells 3 and 4.

The short pilot therefore does not provide:

- a resolved high-wave-number range;
- an inertial range;
- a direct-enstrophy-cascade range;
- a stationary spectrum;
- a defensible power-law fitting window;
- a `k^-3` result.

---

## 10. Budget-residual interpretation

### Single-mode final interval

Relative residual magnitudes:

\[
\frac{|R_E|}{|\overline{\mathrm{RHS}}_E|}
\approx
1.0185\times10^{-4},
\]

\[
\frac{|R_Z|}{|\overline{\mathrm{RHS}}_Z|}
\approx
1.0185\times10^{-4}.
\]

### Multimode final interval

Relative residual magnitudes:

\[
\frac{|R_E|}{|\overline{\mathrm{RHS}}_E|}
\approx
1.2630\times10^{-4},
\]

\[
\frac{|R_Z|}{|\overline{\mathrm{RHS}}_Z|}
\approx
1.4386\times10^{-4}.
\]

The residuals are small relative to the corresponding interval rates.

They include the effect of estimating an interval derivative and mean RHS
over a `0.5` time interval. They are not formal temporal-convergence
measurements.

---

## 11. Main scientific findings

The two pilots support the following statements:

1. The standalone forcing-budget formulas pass an exact single-mode analytic
   control.
2. Matching forcing-field RMS does not match energy injection.
3. Matching forcing-field RMS does not match enstrophy injection.
4. Multimode forcing activates measurable nonlinear advection.
5. Multimode forcing increases viscous enstrophy dissipation relative to the
   single-mode control.
6. At `t = 5.005`, the multimode response is still strongly concentrated in
   shells 3 and 4.
7. At `t = 5.005`, injection substantially exceeds dissipation.
8. The short multimode pilot is not stationary.
9. No defensible `k^-3` fitting range exists in this short-pilot spectrum.

---

## 12. Execution-provenance note

One attempted analytic-pilot launch used Python isolated mode, which blocked a
local module import before solver construction, output-directory creation, or
time stepping.

That pre-execution import-path incident produced no numerical evidence and is
not part of either archived pilot dataset.

Both archived datasets listed in this report were successful executions.

---

## 13. Requirements before a longer stationarity test

A longer multimode run should not begin until a simple prospective plan
specifies:

- the exact forcing field and frozen RMS;
- actual energy- and enstrophy-injection diagnostics;
- viscous energy- and enstrophy-dissipation diagnostics;
- output cadence;
- final-step output behavior;
- stationarity-window definition;
- injection-dissipation balance criteria;
- maximum permitted budget residual;
- resolution and timestep;
- stopping conditions;
- failure-preservation rule;
- claim boundaries.

A future stationarity assessment should use time-window behavior, not a single
final snapshot.

---

## 14. Decision

> The analytic and multimode forcing-budget pilots are complete, archived, and
> mutually interpretable at their declared short-run scope.

The multimode source is the appropriate forcing baseline for subsequent
nonlinear forced-response work.

However:

> No longer run is authorized by this report.

The next task is design-only: define one controlled longer multimode
stationarity test with prospective diagnostics and stopping criteria.
