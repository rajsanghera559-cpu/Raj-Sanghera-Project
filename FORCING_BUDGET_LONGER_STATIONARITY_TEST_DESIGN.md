# Forcing Budget Longer Stationarity Test Design

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Source checkpoint: `c1bc524`
- Created UTC: `2026-07-19T07:58:45+00:00`
- Document type: design only
- Solver execution authorized by this document: no
- Numerical rerun authorized: no
- Formal convergence claim: none
- Physical-validation claim: none
- Turbulence claim: none
- Cascade claim: none
- `k^-3` claim: none
- Method-superiority claim: none

---

## 1. Purpose

This document defines one controlled longer-duration stationarity test for the
existing RMS-matched deterministic low-wave-number multimode forcing.

The test is intended to answer only:

> Does the `N = 64` multimode forced response approach a budget-balanced,
> slowly varying state within the prospectively fixed interval
> `0 < t <= 100.005`?

This is a stationarity-screening calculation. It is not a convergence study,
physical validation, turbulence validation, or spectral-law test.

---

## 2. Evidence motivating the design

The archived short multimode forcing-budget pilot established that, at
`t = 5.005`:

- the forcing RMS was `0.005`;
- nonlinear advection was measurable;
- energy and enstrophy injection exceeded viscous losses;
- the response remained concentrated in shells 3 and 4;
- the run was not close to injection-dissipation balance;
- no high-wave-number fitting range existed.

The longer test therefore focuses on time-window behavior and budget balance,
not on fitting a spectral exponent.

---

## 3. Frozen numerical configuration

The stationarity-screening run shall use:

| Parameter | Frozen value |
|---|---:|
| Grid | `64 x 64` |
| Reynolds number | `1000` |
| Viscosity | `0.001` |
| Timestep | `0.005` |
| Completed steps | `20001` |
| Final physical time | `100.005` |
| Initial vorticity | exact zero |
| Time integrator | external mirror of protected RK2 |
| Protected solver `run()` | not called |
| Dealiasing | inherited protected 2/3 mask |
| Budget output interval | `100` loop indices |
| Budget sampling interval | `0.5` time units |
| Spectrum output interval | `500` loop indices |
| Spectrum sampling interval | `2.5` time units |

The final step must always be recorded even when it does not coincide with a
regular output interval.

No parameter may be changed after execution begins.

---

## 4. Frozen forcing definition

The vorticity-source field shall be the existing deterministic multimode field

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
\Big],
\]

where `c` is chosen once at initialization so that

\[
\sqrt{\langle f_\omega^2\rangle}=0.005.
\]

Required forcing records:

- exact term list;
- normalization coefficient `c`;
- raw forcing RMS;
- normalized forcing RMS;
- forcing-field SHA-256;
- forcing-array shape;
- forcing-array dtype;
- finite and real checks.

The forcing field must remain time independent and byte-identical throughout
the run.

---

## 5. Required instantaneous budget diagnostics

At every budget output time, record:

- `loop_index`;
- `completed_steps`;
- `physical_time`;
- kinetic energy `E`;
- enstrophy `Z`;
- forcing RMS;
- energy injection rate
  \[
  \varepsilon_f=-\langle\psi f_\omega\rangle;
  \]
- enstrophy injection rate
  \[
  \eta_f=\langle\omega f_\omega\rangle;
  \]
- viscous energy dissipation rate
  \[
  D_E=\nu\langle\omega^2\rangle;
  \]
- viscous enstrophy dissipation rate
  \[
  D_Z=\nu\langle|\nabla\omega|^2\rangle;
  \]
- continuous energy right-hand side
  \[
  R_E^{\mathrm{cont}}=\varepsilon_f-D_E;
  \]
- continuous enstrophy right-hand side
  \[
  R_Z^{\mathrm{cont}}=\eta_f-D_Z;
  \]
- stage-1 advection RMS;
- stage-2 advection RMS;
- dealiasing-mask removal RMS;
- vorticity RMS;
- maximum absolute vorticity;
- forcing-array identity check.

---

## 6. Required interval diagnostics

For each pair of consecutive budget snapshots, record:

- interval duration;
- observed energy rate;
- mean continuous energy right-hand side;
- energy-budget residual;
- observed enstrophy rate;
- mean continuous enstrophy right-hand side;
- enstrophy-budget residual.

Define normalized interval residuals as

\[
r_E
=
\frac{|R_E|}
{\max(
|\overline{\varepsilon_f}|,
|\overline{D_E}|,
10^{-30}
)},
\]

\[
r_Z
=
\frac{|R_Z|}
{\max(
|\overline{\eta_f}|,
|\overline{D_Z}|,
10^{-30}
)}.
\]

The denominator floor is only a numerical safeguard and must be recorded.

---

## 7. Required spectral diagnostics

At every spectrum output time, record the complete radial kinetic-energy
spectrum and mode counts.

Also record:

- direct kinetic energy;
- spectrum energy sum;
- relative energy-consistency error;
- dominant radial shell;
- dominant-shell energy;
- shell energies `k = 1, 2, 3, 4`;
- fraction at `k <= 4`;
- fraction at `5 <= k <= 9`;
- fraction at `k >= 10`;
- fraction at `k > 4`;
- finite-shell count;
- nonzero-shell count;
- minimum and maximum spectral values.

The shell-2 diagnostic must be named `k2_energy`. The forcing-associated
default radial shell is shell 3.

No power-law slope shall be fitted in this stationarity test.

---

## 8. Candidate stationarity window

The prospectively fixed candidate stationarity window is

\[
80.005 \le t \le 100.005.
\]

With budget sampling every `0.5` time units, this window contains 41 budget
snapshots, including both endpoints.

The window shall be split into four consecutive subwindows of five time units:

1. `80.005 <= t <= 85.005`;
2. `85.005 < t <= 90.005`;
3. `90.005 < t <= 95.005`;
4. `95.005 < t <= 100.005`.

No alternate window may be selected after inspecting the result.

If the run ends before `t = 100.005`, the stationarity decision is
`INCOMPLETE`, not PASS.

---

## 9. Trend metrics

For each of the following quantities,

- energy;
- enstrophy;
- energy injection;
- enstrophy injection;
- viscous energy dissipation;
- viscous enstrophy dissipation;

fit an ordinary least-squares line over the fixed stationarity window.

For quantity `Q`, define the normalized window drift

\[
S_Q
=
\frac{|b_Q|\Delta T}
{\max(|\overline{Q}|,10^{-30})},
\]

where:

- `b_Q` is the fitted slope;
- `Delta T = 20`;
- `mean(Q)` is the window mean.

Required threshold for a stationarity candidate:

\[
S_E \le 0.05,
\qquad
S_Z \le 0.05.
\]

Injection and dissipation trends are reported, but the primary drift gate is
applied to energy and enstrophy.

---

## 10. Injection-dissipation balance metrics

Over the fixed stationarity window, calculate

\[
B_E
=
\frac{|\overline{\varepsilon_f}-\overline{D_E}|}
{\max(
|\overline{\varepsilon_f}|,
|\overline{D_E}|,
10^{-30}
)},
\]

\[
B_Z
=
\frac{|\overline{\eta_f}-\overline{D_Z}|}
{\max(
|\overline{\eta_f}|,
|\overline{D_Z}|,
10^{-30}
)}.
\]

Required thresholds:

\[
B_E \le 0.10,
\qquad
B_Z \le 0.10.
\]

Also report the ratios

\[
\overline{\varepsilon_f}/\overline{D_E},
\qquad
\overline{\eta_f}/\overline{D_Z}.
\]

A ratio near one is descriptive support for balance. It is not, by itself, a
stationarity decision.

---

## 11. Subwindow consistency metrics

For energy and enstrophy, calculate the mean in each of the four fixed
subwindows.

For each subwindow mean `Q_j`, require

\[
\frac{|Q_j-\overline{Q}|}
{\max(|\overline{Q}|,10^{-30})}
\le 0.10.
\]

This requirement prevents a single full-window slope from hiding a late
transition or systematic drift.

---

## 12. Budget-residual integrity criteria

Within the fixed stationarity window, require:

- median normalized energy residual `<= 0.01`;
- maximum normalized energy residual `<= 0.05`;
- median normalized enstrophy residual `<= 0.01`;
- maximum normalized enstrophy residual `<= 0.05`.

These thresholds assess the stored interval-budget consistency at the frozen
sampling cadence.

They do not establish temporal convergence.

---

## 13. Numerical-integrity gates

The run fails immediately if any of the following occurs:

- a nonfinite vorticity value;
- a nonfinite forcing value;
- a nonfinite budget value;
- a nonfinite spectral value;
- forcing-field identity changes;
- protected source hash changes;
- output schema or atomic write failure;
- direct energy and spectrum energy disagree by more than `1e-8`;
- the runner detects an existing output directory with the same run ID;
- the working tree is dirty before execution;
- the active branch or authorized commit changes.

A numerical-integrity failure must preserve all partial outputs and stop.

No automatic rerun is allowed.

---

## 14. Growth and imbalance observations

Large positive energy or enstrophy growth is not automatically a numerical
failure when all fields remain finite.

Instead, the run must complete to the fixed final time unless a numerical
integrity gate fails.

If injection remains substantially greater than dissipation, the final
decision is `NOT STATIONARY WITHIN TESTED DURATION`.

The runner must not automatically extend the duration.

---

## 15. Decision logic

The final classification shall be exactly one of:

### A. `STATIONARITY CANDIDATE`

Use only when all of the following pass:

- full run reaches `t = 100.005`;
- all numerical-integrity gates pass;
- `S_E <= 0.05`;
- `S_Z <= 0.05`;
- `B_E <= 0.10`;
- `B_Z <= 0.10`;
- all energy subwindow deviations are `<= 0.10`;
- all enstrophy subwindow deviations are `<= 0.10`;
- all budget-residual integrity criteria pass.

This classification is limited to the tested `N = 64` calculation.

### B. `NOT STATIONARY WITHIN TESTED DURATION`

Use when the full run completes without a numerical-integrity failure but one
or more stationarity criteria fail.

This is a scientifically useful result and does not authorize automatic
extension.

### C. `INCOMPLETE`

Use when the planned final time is not reached for a non-numerical reason.

### D. `NUMERICAL FAILURE`

Use only when a numerical-integrity gate fails.

---

## 16. Required output bundle

The run shall write one new immutable directory containing:

1. `run_metadata.json`;
2. `forcing_budget.csv`;
3. `forcing_spectra.csv`;
4. `stationarity_window.csv`;
5. `stationarity_summary.json`;
6. `file_inventory.csv`.

The summary must include:

- run identity;
- source hashes;
- forcing identity;
- all frozen parameters;
- all decision thresholds;
- observed metrics;
- pass/fail value for each criterion;
- final classification;
- explicit claim boundaries.

Partial outputs must remain available after failure.

---

## 17. Reproducibility requirements

Record:

- Git branch;
- Git commit;
- runner SHA-256;
- protected solver SHA-256;
- forcing-budget diagnostic SHA-256;
- Python version;
- NumPy version;
- operating system;
- floating dtype;
- machine epsilon;
- UTC start and completion times;
- file hashes for every persistent output.

The result directory must be Git-ignored during execution.

A successful result may be force-added only after read-only inspection.

---

## 18. Scientific claim boundaries

Even a `STATIONARITY CANDIDATE` result would not establish:

- spatial convergence;
- temporal convergence;
- an asymptotic numerical regime;
- physical validation;
- turbulence validation;
- an inverse-energy cascade;
- a direct-enstrophy cascade;
- an inertial range;
- a `k^-3` law;
- method superiority;
- production readiness.

A stationarity candidate would support only:

> Under the frozen `N = 64` multimode configuration, the recorded energy,
> enstrophy, injection, dissipation, and interval-budget diagnostics satisfy
> the prospectively specified stationarity-screening criteria over the fixed
> final twenty-time-unit window.

---

## 19. Relationship to later spectral work

No spectral slope fitting is authorized in this test.

If and only if the result is `STATIONARITY CANDIDATE`, a later design may
define:

- a fixed stationary averaging interval;
- time-averaged spectra;
- forcing-peak masking;
- numerical-floor exclusion;
- shell-support requirements;
- leave-one-shell-out influence;
- fixed slope windows;
- matched resolution and timestep checks.

Those tasks require a separate design and execution decision.

---

## 20. Execution decision

This document is design-only.

> The longer multimode stationarity test is not yet authorized for numerical
> execution.

The next task is to create and statically inspect one standalone runner that
implements this document exactly, without modifying the protected solver.
