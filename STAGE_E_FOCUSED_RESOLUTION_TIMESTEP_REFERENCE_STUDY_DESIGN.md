# Stage E Focused Resolution, Timestep, and Reference-Candidate Study Design

## 1. Status and parent checkpoint

This is a design-only checkpoint. It authorizes no numerical execution by itself.

- Repository branch: `phase4_validation`
- Parent checkpoint: `6ee8cfb9a6011355771659350fec314b44e15f38`
- Completed Stage D1R runner SHA256: `21A7E2D1168C5A6D33C563B7A278006E5A047AD18025B42F2BFE4BB65BDD3BC3`
- Completed Stage D1R report SHA256: `C5BDCDE3D97EDB1568B2A6C959CF98A94DE0207415772DAAE181144C0E2850BA`
- Completed Stage D1R evidence inventory SHA256: `B71EF5D9313B1C3FAE007726C92F77F7C0CD17B26D2A27F7841F073BECD8BE20`

The protected solver and operator sources remain unchanged. Their Git blob identities at the parent checkpoint are:

- `project/solver/spectral_solver.py`: `09cb2d04b0f229c1f605bf883ce08dfd2cab51d5`
- `project/solver/advection_operators.py`: `849b3d5c95c955a7db73313d8680c942fd32c571`

## 2. Decision question

Stage D1R established operator-dependent trajectory separation at `N=64`, `dt=0.005`, `Re=1000`, and `T=15.3`. Stage E asks:

1. Is that separation larger than the measured RK2 timestep sensitivity?
2. Does it decrease under spatial refinement in a manner consistent with truncation error?
3. Which operator-pair separations are resolved relative to the combined discretization uncertainty?
4. Does nonlinear-product projection remain negligible relative to operator-form differences as the discretization is refined?
5. Is a separate numerical-reference calculation scientifically warranted after the core refinement evidence is examined?

Stage E is not a longer same-grid trajectory run and is not a full `N x dt` Cartesian sweep.

## 3. Five primary trajectory positions

Exactly five independently owned primary states are advanced in every core case:

| ID | Operator kind |
|---|---|
| `TRAJ_BASE_FD_ADVECTIVE_V1` | centered finite-difference advective form |
| `TRAJ_FD_CONSERVATIVE_V1` | centered finite-difference conservative form |
| `TRAJ_FD_SKEW_V1` | centered finite-difference skew form |
| `TRAJ_PS_ADVECTIVE_UNPROJECTED_RC_NYQUIST_V2` | pseudo-spectral advective form with real-compatible Nyquist-zeroed derivatives |
| `TRAJ_ARAKAWA_V1` | Arakawa Jacobian form |

The unprojected FD-advective and pseudo-spectral definitions are retained only to preserve the canonical Stage D1R positions. This is not a preference or ranking.

The projected FD-advective and projected pseudo-spectral variants are not separately advanced production trajectories. They are evaluated as sparse same-state controls under Section 9.

## 4. Crossed core matrix

All cases use `Re=1000`, `nu=0.001`, the same periodic `2*pi` domain, exact-zero initial vorticity, and final physical time `T=15.3`.

| Case | Grid `N` | `dt` | Updates per primary trajectory | Purpose |
|---|---:|---:|---:|---|
| `C0_N64_DT00500` | 64 | 0.005 | 3,060 | reproduce the Stage D1R nominal case and save state fields |
| `C1_N64_DT00250` | 64 | 0.0025 | 6,120 | first timestep refinement |
| `C2_N64_DT00125` | 64 | 0.00125 | 12,240 | second timestep refinement and spatial-slice intersection |
| `C3_N96_DT00125` | 96 | 0.00125 | 12,240 | first spatial refinement |
| `C4_N144_DT00125` | 144 | 0.00125 | 12,240 | second spatial refinement |

The matrix contains 25 primary trajectories and 229,500 accepted primary updates. The temporal refinement ratio is `2`; the spatial refinement ratio is `1.5`. Grids `64`, `96`, and `144` are even and FFT-friendly.

The cases execute sequentially. Within a case, the five states advance independently from immutable snapshots of their own current states. No state array may share memory with another state, forcing array, wavenumber array, RK2 stage, or accepted update.

No escalation case is included in the core runner.

## 5. Initial condition and forcing equivalence

Every case starts from a newly allocated exact-zero `float64` field of shape `(N,N)`. A coarse array is never interpolated to initialize a finer grid.

Every case constructs the Stage D1R analytic multimode forcing on its own grid:

```text
sin(2X)cos(2Y)
+ 0.75 sin(3X)cos(Y)
+ 0.50 sin(X)cos(4Y)
+ 0.35 cos(4X-2Y)
```

The discrete mean is removed and the field is normalized to RMS `0.005` exactly as in Stage D1R. The runner records the per-grid coefficient, RMS, mean, dtype, shape, and SHA256. It verifies that the analytic forced modes and normalized Fourier coefficients agree across grids after NumPy FFT normalization.

For `C0`, the forcing SHA256 must reproduce `504574DB2F92E127BAA6F699C7B21A4051435479A9B16A731501C6555F2FE6BB`.

## 6. Numerical implementation boundary

The runner may construct `SpectralSolver` separately for each case only to obtain the periodic grid, Poisson solve, velocity reconstruction, spectral diffusion, and dealias mask. It must not call `SpectralSolver.run()`.

The runner must not use `SelectableAdvectionSolver`; that interface does not contain all five remediated Stage D operator definitions.

The Stage D1R local implementations of the following are parameterized by the active case instead of global constants:

- centered gradients;
- real-compatible, Nyquist-zeroed spectral gradients;
- projected and unprojected transport forms;
- Arakawa transport;
- independent two-stage RK2 updates;
- post-update dealias filtering;
- exact discarded-field physical/Fourier mask ledgers;
- energy, enstrophy, velocity, spectrum, and band diagnostics.

All shape checks, Nyquist locations, Parseval factors, spectrum normalizations, row counts, and physical times are derived from the active `N` and `dt`.

`SpectralSolver.k2[0,0]=1` is preserved for exact baseline comparability. Because the same array is used by its diffusion method, the runner records mean vorticity and reports both total-field and mean-free comparison norms. It does not silently alter the protected solver.

## 7. Common scientific sampling

All cases record scalar diagnostics at the 307 common physical times

```text
t = 0.00, 0.05, 0.10, ..., 15.30.
```

Full `float64` vorticity states and shell spectra are retained only at seven anchors:

```text
t = 0.00, 2.55, 5.10, 7.65, 10.20, 12.75, 15.30.
```

The C0 reproduction gate separately reads the archived D1R diagnostic schedule at completed steps `1, 11, ..., 3051, 3060`. It checks the five retained primary-state hashes and frozen scalar diagnostics without changing the common Stage E sampling schedule.

## 8. Refinement comparisons

### 8.1 Temporal comparisons

For each primary operator and anchor time, compare on the common `N=64` grid:

- `C0` versus `C1`;
- `C1` versus `C2`.

Let the absolute mean-free vorticity RMS errors be `E_t_coarse` and `E_t_fine`. When both are above the measured numerical floor, report

```text
p_t = log(E_t_coarse / E_t_fine) / log(2).
```

Normalized errors are reported for scale; absolute errors are used for the order calculation.

### 8.2 Spatial comparisons

The primary spatial comparison uses explicitly normalized Fourier coefficients. Source modes are mapped by integer wavenumber to a common `N=64` band, ambiguous even-grid Nyquist axes are zeroed, and NumPy FFT scaling is applied explicitly. The actual rectangular dealias masks are recorded; no radial cutoff is substituted.

For each operator and anchor time, compare:

- `C2` versus Fourier-restricted `C3`;
- Fourier-restricted `C3` versus Fourier-restricted `C4`.

Let the absolute common-band mean-free vorticity RMS errors be `E_x_coarse` and `E_x_fine`. When both are above the measured numerical floor, report

```text
p_x = log(E_x_coarse / E_x_fine) / log(1.5).
```

The discarded-band enstrophy and energy are reported separately so common-band agreement cannot conceal unresolved fine-grid content.

### 8.3 Required comparison metrics

Every temporal and spatial row includes:

- absolute and normalized total-field vorticity RMS difference;
- absolute and normalized mean-free vorticity RMS difference;
- mean-vorticity difference;
- normalized velocity RMS difference;
- vorticity cosine similarity;
- relative energy and enstrophy differences;
- dominant-shell difference;
- low-, tail-, and high-wavenumber fraction differences;
- discarded-band energy and enstrophy where applicable;
- finite status and numerical-floor status.

Within every case, the ten primary operator pairs are compared at all 307 common diagnostic times. Cross-case comparisons are same-operator only; the runner must not create an all-to-all cross-case matrix.

## 9. Sparse projection controls

At each of the seven anchors in every case, the runner evaluates from independent copies of the same primary state:

1. unprojected versus projected FD-advective transport;
2. unprojected versus projected pseudo-spectral transport.

At the first six anchors, it also forms independent one-step RK2 previews for each canonical/control pair without accepting either control preview into a production trajectory. At `T=15.3`, it records the transport/projection defect without stepping beyond the endpoint.

Only the two canonical/control comparisons are written. Projected controls are never compared with unrelated operators.

A projection effect is descriptively negligible only when its normalized accepted-update or transport defect is both:

- no greater than `1e-8`; and
- no greater than `1%` of the smallest non-control operator separation at that case and anchor whenever that separation exceeds `1e-8`.

Failure of this descriptive criterion does not invalidate the numerical case. It marks projection dependence as unresolved and prohibits collapsing the variants in later work.

## 10. Integrity with reduced evidence volume

The runner applies these checks during every update:

- all RK2 stages, transports, ledgers, and accepted states are finite;
- each state is independently allocated and read-only between updates;
- accepted states and RK2 stages do not alias current or other trajectory states;
- normalized filtered and unfiltered enstrophy-ledger closure are at most `1e-10`;
- normalized physical/Fourier discarded-mask disagreement is at most `1e-12`;
- real-compatible imaginary ratio is at most `1e-13`;
- physical and Fourier discarded losses are nonnegative;
- corrected mask-enstrophy change is nonpositive;
- forcing and local wavenumber arrays remain immutable.

The checks remain fail-fast, but successful per-step rows are not written. For each case and trajectory, the runner writes only update count, failure count, and the maxima/minima needed to audit every gate. On failure it writes one detailed snapshot and preserves all completed cases. There is no automatic retry.

The solver environment is hashed at case entry and case exit rather than once per update. State ownership is verified at initialization, every acceptance boundary, and every saved anchor. One forward/reverse evaluation-order canary is performed at the final anchor of `C2`.

The C0 reproduction gate must match the archived Stage D1R sample hashes and scalars for all five retained trajectories and match the Stage D1R final checkpoint. Stage B and Stage C ledgers are not re-audited; their already archived evidence is referenced rather than duplicated.

## 11. Core output contract

Exactly these ten files are produced in one new ignored run directory:

1. `run_metadata.json`
2. `case_diagnostics.csv`
3. `within_case_pairwise.csv`
4. `refinement_comparisons.csv`
5. `projection_controls.csv`
6. `integrity_summary.csv`
7. `anchor_spectra.csv`
8. `state_checkpoints.npz`
9. `stage_e_summary.json`
10. `file_inventory.csv`

The Markdown interpretation report is created only by the later read-only evidence audit, not by the numerical runner. No individual output may exceed 40 MB. The runner predicts file sizes before execution and verifies the final file set, counts, sizes, and inventory.

Expected successful row counts are derived programmatically from the frozen matrix and schedules. The design-level expectations are:

- case diagnostics: `5 cases x 5 trajectories x 307 times = 7,675` rows;
- within-case primary pairwise: `5 cases x 10 pairs x 307 times = 15,350` rows;
- refinement comparisons: `4 adjacent comparisons x 5 trajectories x 7 anchors = 140` rows;
- projection controls: `5 cases x 2 controls x 7 anchors = 70` rows;
- integrity summary: `5 cases x 5 trajectories = 25` rows.

`anchor_spectra.csv` row count is derived from the recorded shell bins for each case, trajectory, and anchor. `state_checkpoints.npz` contains exactly one array for every case, primary trajectory, and anchor: `5 x 5 x 7 = 175` arrays.

## 12. Interpretation and stopping rules

### 12.1 Refinement resolved

For a method and refinement axis, the fine difference must be smaller than the coarse difference at the final anchor and at least five of the six positive-time anchors. Otherwise that axis is unresolved for that method.

An RK2 second-order diagnostic statement additionally requires:

- `p_t` between `1.7` and `2.3` at at least four of the final five anchors; and
- both errors at least 100 times the measured numerical floor.

A near-second-order spatial diagnostic statement additionally requires:

- `p_x` between `1.5` and `2.5` at at least four of the final five anchors; and
- both errors at least 100 times the measured numerical floor.

Near-floor ratios are reported as indeterminate, not as zero-order or negative-order convergence.

### 12.2 Operator separation resolved

For operator pair `i,j` at an anchor, define the conservative combined discretization uncertainty as the sum of the two fine temporal increments and the two fine spatial increments on the common representation.

The pair is numerically resolved only if that uncertainty is at most `20%` of the `C4` operator separation at the final anchor and at least four of the final five anchors. Otherwise it is unresolved. This is an uncertainty statement, not method ranking.

### 12.3 Escalation

No escalation runs automatically.

After the core audit:

- unresolved temporal behavior may justify `N=64, dt=0.000625` only for affected methods;
- unresolved spatial behavior may justify `N=216, dt=0.00125` only for affected methods;
- a reference-candidate study may be designed only if accuracy or ranking remains a live question.

A possible reference-candidate stage would independently advance pseudo-spectral and Arakawa trajectories at `N=144` with `dt=0.000625` and `dt=0.0003125`. They are two independent numerical reference candidates, never truth. A cross-validated reference envelope is allowed only if their time-extrapolated gap is no larger than the sum of their conservative temporal and spatial uncertainties at each of the final three anchors. If that condition fails, the result is `no validated reference` and no ranking is produced.

The reference-candidate stage requires its own design decision after the core evidence is analyzed. It has no output or execution path in the core runner.

## 13. Claims boundary

The core evidence may support statements about:

- temporal and spatial self-refinement for this exact problem;
- whether Stage D operator separation shrinks or persists under refinement;
- which pairwise separations exceed the measured discretization envelope;
- whether projection controls remain negligible relative to operator differences.

It does not by itself establish:

- a true, best, superior, or physically correct method;
- a validated numerical reference solution;
- general continuum convergence outside the measured refinement range;
- turbulence, cascade, inertial-range, spectral-law, Lyapunov, or predictability claims;
- generalization beyond this domain, forcing, zero initial condition, `Re=1000`, and `T=15.3`.

## 14. Streamlined workflow

1. Commit this design once.
2. Create one core runner: `run_stage_e_focused_refinement_study.py`.
3. Run the runner's single repository-bound static inspection.
4. Commit the runner once.
5. Run one read-only preauthorization check.
6. Execute the core matrix once.
7. Run one read-only evidence audit and archive one interpretation report.
8. Decide whether any targeted escalation or reference-candidate stage is warranted.

No additional manual regex inspection, duplicate copy authorization, repeated unchanged hash/status audit, or automatic numerical retry is part of this workflow.

## 15. Current authorization boundary

- Stage E design creation and static inspection: authorized.
- Stage E design commit: not performed by this design.
- Stage E runner creation: not yet performed.
- Stage E numerical execution: not authorized by this design.
- Stage E reference-candidate execution: not authorized.
- Protected-source modification: prohibited.

