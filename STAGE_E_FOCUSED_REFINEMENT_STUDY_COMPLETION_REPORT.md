# Stage E Focused Refinement Study Completion Report

## Result

> **STAGE E FOCUSED RESOLUTION/TIMESTEP STUDY: PASS**

The single Stage E execution completed its frozen five-case contract, and the
uploaded evidence passed an independent read-only audit. The scientific result
is that the Stage D operator-form separations are dominated by spatial
discretization at the tested settings: they shrink approximately as second
order under grid refinement, while timestep sensitivity is negligible by
comparison. No operator pair is resolved relative to the study's combined
discretization-uncertainty criterion.

This result does not rank methods, identify a best method, validate a reference
solution, or establish general continuum convergence.

## Repository and evidence identity

| Item | Identity |
|---|---|
| Branch | `phase4_validation` |
| Design commit | `778606a9b54f5d0a2b1b1117ec805573278d4d1d` |
| Design SHA-256 | `75AE9F88326026BF015104D83861CD456584351252522F0CBD34323A5B07A825` |
| Execution commit | `8ab70dc74f76996fe054d578e292459b020a3b02` |
| Runner SHA-256 | `6ED7D7084A79E38EE99B06641BD92DE45D2CA2E34495689210156A25F10F28A7` |
| Run ID | `stage_e_focused_refinement_20260721T074126Z_8ab70dc` |
| Evidence files | `10` exact |
| File-inventory SHA-256 | `D5DA8930A9F16FE444C49C7186F15F54531076DD0376D1696140490D93CF181A` |
| Uploaded ZIP SHA-256 | `BD8203EE98B752D74657D20FF7938E28367828D7AE4047B1BDDE29E45C64BCEA` |

Every inventory byte count and SHA-256 matched the uploaded evidence. All 175
checkpoint arrays had the expected name, shape, `float64` dtype, finite values,
and state hash.

## Execution and integrity audit

| Contract | Observed |
|---|---:|
| Cases | `5 / 5` |
| Primary trajectories per case | `5` |
| Accepted primary updates | `229,500 / 229,500` |
| C0 Stage D1R rows reproduced exactly | `1,535 / 1,535` |
| Case-diagnostic rows | `7,675` |
| Within-case pairwise rows | `15,350` |
| Refinement rows | `140` |
| Projection-control rows | `70` |
| Integrity-summary rows | `25` |
| Spectrum rows | `10,780` |
| Checkpoint arrays | `175` |
| Integrity failures, mutations, or aliases | `0` |

The completed metadata reports exact equality for all 1,535 C0 rows and zero
maximum scalar difference. All five retained final hashes were independently
matched against the Stage D1R archive, and the C2 forward/reverse order canary
matched exactly. The Fourier-restriction and cross-grid forcing harnesses
passed. Because Stage E does not re-emit the historical D1R scalar rows, their
full row-by-row equality is a runner-audited result rather than a comparison
that can be replayed from the ten Stage E files alone.

| Integrity quantity | Maximum | Frozen limit | Result |
|---|---:|---:|---|
| Normalized unfiltered closure | `2.76683e-12` | `1e-10` | PASS |
| Normalized filtered closure | `5.09360e-12` | `1e-10` | PASS |
| Physical/Fourier mask cross-check | `8.79420e-16` | `1e-12` | PASS |
| Real-compatible imaginary ratio | `3.36655e-15` | `1e-13` | PASS |
| CFL | `2.59837e-3` | recorded diagnostic | finite |

## Refinement result

The table reports final-anchor (`T=15.3`) mean-free RMS increments. `E_t,fine`
is the `dt=0.0025` versus `dt=0.00125` difference on `N=64`; `E_x,coarse` and
`E_x,fine` are the `N=64` versus `N=96` and `N=96` versus `N=144` common-band
differences at `dt=0.00125`.

| Primary trajectory | `E_t,fine` | `p_t` | `E_x,coarse` | `E_x,fine` | `p_x` |
|---|---:|---:|---:|---:|---:|
| FD advective | `7.96350e-11` | `2.00009` | `1.20150e-4` | `5.37055e-5` | `1.98592` |
| FD conservative | `7.83374e-11` | `2.00008` | `2.74185e-4` | `1.23811e-4` | `1.96083` |
| FD skew | `7.89224e-11` | `2.00009` | `1.81658e-4` | `8.17261e-5` | `1.96996` |
| Pseudo-spectral advective | `8.33849e-11` | `1.99800` | `2.86892e-8` | `6.05372e-12` | near-floor; not reportable |
| Arakawa | `7.88836e-11` | `2.00009` | `1.32500e-4` | `5.97500e-5` | `1.96419` |

All five trajectories showed second-order temporal behavior at every positive
anchor. The four finite-difference/Arakawa positions showed approximately
second-order spatial behavior at every positive anchor. The pseudo-spectral
spatial increments became too close to the measured numerical floor for a
meaningful formal order; this supports grid convergence for this smooth case,
not a claim of an unusually high measured order.

For the finite-difference/Arakawa positions, final spatial increments are about
`6.7e5` to `1.6e6` times the timestep increments—roughly six orders of
magnitude. A longer run at the same grid would therefore not address the
observed Stage D separation.

## Operator-pair resolution

All 10 operator pairs were unresolved: `0 / 70` pair-anchor records overall and
`0 / 60` positive-time records passed the frozen requirement that combined
uncertainty be at most 20% of separation. At the final anchor,
uncertainty/separation ranged from `1.239` to `5.154`, or about `6.2` to `25.8`
times the allowed criterion.

At the same time, every pair's positive-time separation decreased monotonically
with grid refinement. Final `N=144` separation was only `0.1987` to `0.2015` of
its `N=64` value, consistent with approximately second-order grid decay. Thus
“unresolved” is informative here: the data do not support distinct persistent
continuum trajectories or a method ranking; they support a truncation-error
explanation for the Stage D differences.

## Sparse projection controls

Sparse controls were sufficient; four additional production trajectories were
not needed. All 60 evaluated one-step accepted-update previews passed, with a
maximum normalized effect of `2.16405e-13`. The 10 endpoint rows intentionally
contain transport comparisons only because no step was taken beyond `T=15.3`.

Raw same-state transport projection was not uniformly negligible under the
frozen descriptive rule: `22 / 70` rows failed (`9` FD and `13`
pseudo-spectral), although every `N=144` row passed. Therefore the evidence
supports “negligible post-filter one-step effect at the sampled previews,” but
not a grid-wide claim that projection is irrelevant or that projected and
unprojected definitions may always be collapsed.

## Additional numerical observation

The centered FD advective and FD skew trajectories developed small nonzero mean
vorticity; their final magnitudes fell from about `2.12e-5` and `1.06e-5` at
`N=64` to `4.22e-6` and `2.11e-6` at `N=144`. Conservative, pseudo-spectral,
and Arakawa means remained near roundoff. The roughly second-order decrease
marks this as a discrete nonconservation signature, and the study appropriately
used mean-free fields for trajectory comparisons.

## Disposition

Stage E answers the immediate scientific question without automatic escalation:

- the Stage D separations are grid-driven rather than timestep-driven;
- they decrease consistently under refinement;
- no pair is resolved against measured discretization uncertainty;
- no accuracy ranking or best-method claim is supported.

If the research goal is to determine whether the Stage D differences persist,
the focused study is complete and no `N=216` or longer same-grid run is needed.
If a defensible accuracy ranking is required, that is a different question and
requires a separately designed and validated reference-candidate study.

Reference-candidate execution: **NO**. Validated reference: **NO**. Method
ranking: **NO**. Automatic escalation: **NO**.
