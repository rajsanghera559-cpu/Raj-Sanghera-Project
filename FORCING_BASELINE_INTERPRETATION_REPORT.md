# Forcing Baseline Interpretation Report

## 0. Document control

- Repository: `Raj-Sanghera-Project`
- Branch: `phase4_validation`
- Source checkpoint: `b392598f710886fd26837470f9df2e364ead9137`
- Created UTC: `2026-07-19T06:16:17+00:00`
- Report type: descriptive interpretation of existing evidence
- New solver execution: none
- Numerical rerun: none
- Formal convergence claim: none
- Physical-validation claim: none
- Turbulence claim: none
- `k^-3` claim: none

---

## 1. Purpose

This report records the interpretation of the existing default single-mode
forcing run and the existing RMS-matched multimode forcing runs.

The central question is whether changing the forcing geometry broadened the
stored kinetic-energy spectrum beyond the radial shell containing the default
forcing modes.

No new simulation was required.

---

## 2. Default forcing definition

The baseline vorticity-source field is

\[
f_\omega(x,y)=0.01\sin(2x)\cos(2y).
\]

Its Fourier components have coordinate wave numbers

\[
(k_x,k_y)=(\pm2,\pm2).
\]

Their radial magnitude is

\[
|k|=\sqrt{k_x^2+k_y^2}=\sqrt{8}\approx2.828.
\]

Under the project's radial shell binning, these modes are represented in
shell 3.

Therefore:

- `k2_energy` means radial-shell-2 kinetic energy;
- `k3_energy` means radial-shell-3 kinetic energy;
- shell 3 is the radial shell associated with the default forcing modes.

The earlier diagnostic name `forced_shell_k2_energy` was misleading. It was
renamed to `k2_energy` at commit `b392598`. Historical outputs remain
unchanged and must be interpreted as radial-shell-2 energy.

---

## 3. Matched run identities

### 3.1 Default single-mode forcing

- Run directory:
  `experiments/runs/run_2026-07-01_01-13-58`
- Recorded source commit:
  `3c675070ab7339d56a851ab7f87d11b919cca070`
- Resolution: `128 x 128`
- Reynolds number: `1000`
- Viscosity: `0.001`
- Timestep: `0.005`
- Configured steps: `10000`
- Initial vorticity: zero
- Forcing:
  `0.01*sin(2X)*cos(2Y)`
- Status: completed

### 3.2 RMS-matched multimode forcing

- Run directory:
  `experiments/runs/run_2026-07-01_01-53-34`
- Recorded source commit:
  `70e70f3a5a4d15c85c0320c039f4cd42fb6d302c`
- Resolution: `128 x 128`
- Reynolds number: `1000`
- Viscosity: `0.001`
- Timestep: `0.005`
- Configured steps: `10000`
- Initial vorticity: zero
- Matched forcing RMS: `0.005`
- Status: completed

The multimode forcing terms were:

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

The combined field was rescaled so its RMS equaled the baseline forcing RMS.

### 3.3 Short multimode smoke run

- Run directory:
  `experiments/runs/run_2026-07-02_21-57-26`
- Resolution: `64 x 64`
- Timestep: `0.005`
- Configured steps: `1001`
- Status: completed

This run reproduced the early multimode response but is not a controlled
resolution-convergence study.

---

## 4. Why the default run remains in shell 3

Define

\[
\phi(x,y)=\sin(2x)\cos(2y).
\]

This is a Laplacian eigenfunction:

\[
\nabla^2\phi=-8\phi.
\]

Starting from zero vorticity and forcing only this pattern permits a solution
of the form

\[
\omega(x,y,t)=A(t)\phi(x,y).
\]

The corresponding streamfunction is proportional to the same spatial mode:

\[
\psi=-\frac{\omega}{8}.
\]

Because the vorticity and streamfunction contours are aligned, the nonlinear
advection term vanishes for this isolated mode:

\[
\mathbf{u}\cdot\nabla\omega=0.
\]

The evolution therefore reduces to

\[
\frac{dA}{dt}=-8\nu A+0.01.
\]

For `Re = 1000`, `nu = 0.001`, and `A(0)=0`,

\[
A(t)=\frac{0.01}{8(0.001)}
\left(1-e^{-8(0.001)t}\right).
\]

The kinetic energy and enstrophy are then

\[
E(t)=\frac{A(t)^2}{64},
\]

\[
Z(t)=\frac{A(t)^2}{8}.
\]

This explains why the default run contains essentially 100 percent of its
stored kinetic energy in radial shell 3. It is a single-mode forced-diffusion
control, not a broadband nonlinear-flow experiment.

---

## 5. Diagnostic step-number semantics

The solver loop uses the zero-based index `n`.

At each iteration it:

1. computes and applies one RK2 update;
2. stores the updated vorticity field;
3. then records diagnostics when `n % 500 == 0`;
4. writes `n` into the CSV field named `step`.

Consequently, the CSV value is a loop index, not the number of completed
updates.

Examples:

- CSV `step = 0` represents one completed update and time `0.005`;
- CSV `step = 500` represents 501 completed updates;
- CSV `step = 9500` represents 9501 completed updates.

For `dt = 0.005`, the last stored snapshot therefore corresponds to

\[
t=(9500+1)(0.005)=47.505.
\]

The configured 10000-step solver reaches a later state, but `spectrum.csv`
is overwritten only at diagnostic intervals. The stored spectrum is therefore
the last diagnostic snapshot, not an explicitly written final-step spectrum.

---

## 6. Analytic check of the default run

At `t = 47.505`, the scalar forced-diffusion solution predicts approximately:

\[
E_{\mathrm{analytic}}
=
2.440451772122\times10^{-3},
\]

\[
Z_{\mathrm{analytic}}
=
1.952361417697\times10^{-2}.
\]

The stored default-run values were:

\[
E_{\mathrm{stored}}
=
2.440451771056\times10^{-3},
\]

\[
Z_{\mathrm{stored}}
=
1.952361416844\times10^{-2}.
\]

The close agreement supports the interpretation that the default run remained
on the expected single-mode forced-diffusion trajectory.

---

## 7. Matched stored-spectrum comparison

Both long runs used:

- `N = 128`;
- `Re = 1000`;
- `dt = 0.005`;
- `10000` configured steps;
- zero initial vorticity;
- forcing-field RMS `0.005`.

### 7.1 Default single-mode spectrum

- Diagnostic energy:
  `2.440451771056e-03`
- Enstrophy:
  `1.952361416844e-02`
- Dominant radial shell:
  `3`
- Shell-3 fraction:
  `1.000000000000`
- Fraction at `k <= 4`:
  `1.000000000000`
- Fraction above `k = 4`:
  approximately `2.418475688634e-27`

The apparent tail is at numerical roundoff scale.

### 7.2 RMS-matched multimode spectrum

- Diagnostic energy:
  `1.763401582439e-03`
- Enstrophy:
  `1.599716952717e-02`
- Dominant radial shell:
  `3`
- Shell-2 fraction:
  `0.013632275267`
- Shell-3 fraction:
  `0.877902478168`
- Shell-4 fraction:
  `0.058022816193`
- Fraction at `k <= 4`:
  `0.989426744916`
- Fraction at `5 <= k <= 9`:
  `0.010397473839`
- Fraction at `k >= 10`:
  `0.000175781245`
- Fraction above `k = 4`:
  `0.010573255084`

---

## 8. Direct interpretation

The RMS-matched multimode forcing produced real spectral broadening beyond
shell 3.

Approximately 1.057 percent of the stored multimode kinetic energy was located
above shell 4, whereas the corresponding default-run fraction was at
roundoff scale.

The multimode spectrum nevertheless remained strongly low-wave-number
dominated:

- about 87.79 percent in shell 3;
- about 98.94 percent at `k <= 4`;
- about 0.0176 percent at `k >= 10`.

The appropriate conclusion is:

> The RMS-matched deterministic multimode forcing activated nonlinear mode
> coupling and produced limited broadband spectral transfer, while shell 3
> remained dominant.

The evidence does not support saying that shell-3 dominance was eliminated.

---

## 9. Comparison metrics and cautions

The stored comparison produced:

- multimode/default energy ratio:
  `0.722571780911`;
- multimode/default enstrophy ratio:
  `0.819375418360`;
- spectrum cosine similarity:
  `0.996653247391`;
- normalized total-variation gap:
  `0.122097521833`.

The high cosine similarity is largely caused by shell 3 dominating both
spectra. It must not be interpreted as proof that the spectra are physically
equivalent.

A reported tail-enhancement ratio of approximately `4.37e24` is not a useful
physical metric because its denominator is a roundoff-scale default tail.
The absolute tail fractions should be reported instead.

Equal forcing-field RMS also does not imply equal instantaneous energy or
enstrophy injection. Those depend on correlations between the evolving state
and the vorticity-source field.

---

## 10. Stationarity limitation

The multimode diagnostics show energy and enstrophy continuing to rise through
the saved sequence.

The stored long-run spectrum is therefore a developing forced-response
snapshot. The available evidence does not demonstrate statistical
stationarity.

It must not be described as:

- a stationary spectrum;
- an inertial range;
- an enstrophy cascade;
- an inverse-energy cascade;
- a verified `k^-3` spectrum;
- physical validation;
- turbulence validation.

---

## 11. Final forcing-baseline classifications

### Default single-mode run

> Single-mode forced-diffusion control with an analytically invariant
> shell-3 response.

### RMS-matched multimode run

> Deterministic low-wave-number multimode forced response with limited
> nonlinear spectral broadening and persistent shell-3 dominance.

### Short multimode smoke run

> Early-time reproducibility check for the multimode forced response.

---

## 12. Decision

The original default forcing configuration cannot generate a meaningful
broadband spectrum from exactly zero initial vorticity because it remains on
a single-mode invariant response.

The multimode forcing is the more appropriate existing baseline for continued
spectral-artifact research, but the current stored run remains low-mode
dominated and nonstationary.

Before making any `k^-3`-related claim, future work must separately control:

- forcing geometry;
- actual energy and enstrophy injection;
- stationarity;
- drag or large-scale dissipation;
- resolution and timestep;
- spectral fitting window;
- forcing-shell and peak masking;
- numerical-floor exclusion;
- shell-by-shell influence.

No new numerical run is authorized by this report.
