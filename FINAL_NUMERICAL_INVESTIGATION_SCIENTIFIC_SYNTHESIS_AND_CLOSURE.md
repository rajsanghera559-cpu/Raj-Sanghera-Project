# Final Numerical Investigation Scientific Synthesis and Closure

## Executive conclusion

> **THE ADVECTION-FORM NUMERICAL INVESTIGATION IS CLOSED AT THE FOCUSED SELF-REFINEMENT LEVEL.**

For the frozen smooth, periodically forced two-dimensional vorticity problem at
`Re=1000` through `T=15.3`, the operator-form trajectory differences first
measured at `N=64` are dominated by spatial discretization at the tested
settings. Timestep sensitivity is negligible relative to the method-pair
separations, those separations contract approximately as second order under
grid refinement, and no operator pair is resolved against the declared
discretization-uncertainty rule.

The evidence is consistent with a common-continuum truncation-error explanation
over the measured range. It does not prove a common exact trajectory, numerical
equivalence, or method superiority.

No longer same-grid Stage D2 run, automatic `N=216` escalation, or numerical
reference execution is needed to answer the present persistence question.

## 1. Scientific question and tested scope

The immediate investigation asked whether the discrete-advection contribution
identified on the baseline trajectory, and the form-dependent responses found
on identical states, led to persistent differences when each operator advanced
its own state.

The decisive refinement study used:

- a periodic `2*pi` square domain;
- exact-zero initial vorticity;
- the same smooth multimode forcing with RMS `0.005`;
- `Re=1000` and viscosity `0.001`;
- five primary advection trajectories;
- grids `N=64`, `96`, and `144`;
- timesteps `0.005`, `0.0025`, and `0.00125`;
- final physical time `T=15.3`.

The higher-resolution cases used `dt=0.00125`; consequently, a full
space–time interaction matrix was not measured.

## 2. Verification foundation

Phase 13 froze the benchmark equations, source terms, sign conventions, and
claim language before testing exact and manufactured problems. Its completed
77-case exploratory matrix separated arithmetic-floor, spatial-error-dominated,
and temporal-error-dominated regimes. Centered finite-difference and Arakawa
errors decreased regularly under spatial refinement, while the pseudo-spectral
benchmarks either reached the numerical floor or displayed the expected RK2
timestep sensitivity.

Phase 13 closed at the exploratory verification and calibration-evidence level.
Its deferred 390-file audit and formal Phase 13H program were not required for
the focused question answered here and are not reopened by this closure.

## 3. Evidence chain

| Stage | Question | Result | Scientific meaning |
|---|---|---|---|
| Stage B | Which implemented term closes the unexplained baseline enstrophy ledger? | The exact RK2-plus-mask ledger closed, and discrete advection was the leading omitted non-forcing/non-viscous contributor. | This was exact discrete accounting for one configuration, not proof of unique physical causation or dominance of the complete budget. |
| Stage C | Does advection work depend on operator form on identical states? | Centered conservative work retained the baseline magnitude with opposite sign; centered skew, real-compatible pseudo-spectral, and Arakawa responses were near-neutral. | The same-state response was form-dependent and mixed; accuracy and alternate-trajectory behavior remained unknown. |
| Stage D1R | Can seven forms advance independent, internally consistent trajectories? | Seven independently owned trajectories completed 3,060 updates each with exact baseline reproduction and zero integrity, sharing, or order-invariance failures. | Separate finite-grid trajectories were implemented reliably; the pilot did not rank or classify scientific accuracy. |
| Stage E | Do the resulting separations persist under timestep and grid refinement? | Five primary trajectories completed the focused five-case matrix; separations contracted with grid refinement and no pair cleared the uncertainty rule. | The Stage D differences behave as spatial truncation effects over the tested range rather than resolved persistent continuum differences. |

The first Stage D1 implementation stopped before its first accepted update
because its discarded-field Parseval definition did not reproduce Stage B.
That stopped run supplied no scientific result. D1R corrected the bookkeeping
definition and observability without relaxing the integrity thresholds.

## 4. Integrated numerical findings

### 4.1 Execution integrity

Stage E completed all five cases and all 25 primary trajectories:

| Quantity | Audited result |
|---|---:|
| Accepted primary updates | `229,500 / 229,500` |
| C0 selected D1R rows reproduced | `1,535 / 1,535` |
| Diagnostic rows | `7,675` |
| Pairwise rows | `15,350` |
| Refinement rows | `140` |
| Projection-control rows | `70` |
| Verified checkpoint arrays | `175` |
| Integrity, mutation, ownership, or aliasing failures | `0` |

All inventory identities, output counts, checkpoint hashes, and declared
integrity limits passed the independent read-only audit. The five final C0
state identities were independently matched to the preserved D1R evidence.

### 4.2 Temporal and spatial refinement

All five primary trajectories exhibited essentially second-order temporal
self-refinement at every positive-time anchor. Final observed temporal orders
ranged from `1.997998` to `2.000092`, with fine timestep increments between
`7.83e-11` and `8.34e-11`.

At the final anchor, the four finite-difference/Arakawa spatial results were:

| Trajectory | Fine spatial increment | Observed `p_x` |
|---|---:|---:|
| FD advective | `5.37055e-5` | `1.98592` |
| FD conservative | `1.23811e-4` | `1.96083` |
| FD skew | `8.17261e-5` | `1.96996` |
| Arakawa | `5.97500e-5` | `1.96419` |

These spatial increments were about `6.7e5` to `1.6e6` times their timestep
increments. The pseudo-spectral spatial increment fell from `2.86892e-8` to
`6.05372e-12`; much of its sequence approached the measured numerical floor,
so its formal spatial-order ratio is not scientifically reportable. At the
finest comparison its already tiny timestep increment exceeded its spatial
increment, which is a reminder that the L-shaped matrix did not measure the
full space–time interaction.

### 4.3 Operator-pair resolution

Every operator-pair separation decreased monotonically under spatial
refinement. At `T=15.3`, each `N=144` separation was only `0.1987` to `0.2015`
of its `N=64` value, consistent with approximately second-order decay.

None of the ten pairs was resolved under the frozen requirement that combined
discretization uncertainty be at most 20% of separation:

- `0 / 70` pair-anchor records passed overall;
- `0 / 60` positive-time records passed;
- final uncertainty/separation ranged from `1.239` to `5.154`, versus the
  required maximum of `0.20`.

The finite `N=144` differences are therefore not called zero or equal. They are
measurable but unresolved relative to the conservative uncertainty envelope.

### 4.4 Projection and mean-vorticity controls

Treating the two projected variants as sparse controls was sufficient. All 60
evaluated post-filter one-step previews passed, with maximum normalized effect
`2.16405e-13`. Raw same-state transport projection was not uniformly
negligible: `22 / 70` rows failed the descriptive criterion, although all
`N=144` rows passed. The accepted-step sampled effect may be described as
negligible; projection itself may not be declared irrelevant or universally
equivalent.

FD advective and FD skew developed small mean-vorticity drift that decreased
approximately as second order with grid refinement. Conservative,
pseudo-spectral, and Arakawa means remained near roundoff. The use of mean-free
fields for trajectory comparisons was therefore necessary and appropriate.

## 5. Scientific answers

| Question | Answer supported by the evidence |
|---|---|
| Are the fixed-grid operator trajectories identical? | No. Finite-grid differences are measurable. |
| Are the Stage D differences primarily timestep-driven? | No at the tested settings. Pairwise differences were effectively unchanged by the N64 timestep refinement, while grid refinement reduced them strongly. |
| Do the differences persist as resolved method-dependent trajectories? | Not in the measured range. They contract approximately as spatial truncation error and remain unresolved against the uncertainty rule. |
| Do the data identify a best or most accurate operator? | No. There is no validated reference and no ranking. |
| Were four additional projected production trajectories necessary? | No. Sparse accepted-step controls answered the trajectory-level projection question, subject to the raw-transport qualification above. |
| Would a longer run on the same grid answer the refinement question? | No. It would extend the horizon without reducing the dominant spatial uncertainty. |

## 6. Broader physical interpretation

Stage B's long baseline ledger remained **not stationary within the tested
duration**: in its final window, enstrophy declined at every recorded step and
viscous removal exceeded forcing plus discrete-advection input. Stage E's final
fields were also strongly low-mode dominated.

Accordingly, this investigation does not validate turbulence, a cascade, an
inertial range, or a `k^-3` law. It improves confidence in the tested numerical
pathways and explains the observed operator sensitivity, but it does not turn a
spectral resemblance into physical validation.

## 7. Supported conclusions and boundaries

The archived evidence supports:

- exact implemented-ledger accounting for the frozen Stage B run;
- form-dependent same-state advection work;
- independently owned and internally consistent alternate trajectories;
- benchmark-specific RK2 temporal self-refinement;
- approximately second-order FD/Arakawa spatial self-refinement;
- systematic grid decay of every measured operator-pair separation;
- absence of resolved pair separation under the declared uncertainty rule;
- negligible sampled accepted-step projection effects.

It does not establish formal or universal continuum convergence, equality of
the methods, a validated numerical reference, accuracy ranking, method
superiority, production readiness, physical validation, long-time or ensemble
statistics, turbulence, cascade behavior, an inertial range, or a spectral law.
It does not generalize beyond the tested domain, forcing, initial condition,
Reynolds number, time horizon, grids, and timesteps.

## 8. Closure decision

The present numerical question has been answered efficiently enough to stop.

1. Retain the Stage B, Stage C, D1R, and Stage E evidence as the immutable
   numerical record.
2. Retire the longer same-grid Stage D2 pathway for this question.
3. Do not add another audit chain, automatic retry, `N=216` case, or reference
   calculation merely to continue the phase sequence.
4. Treat any future accuracy-ranking request as a new scientific objective with
   its own minimal reference-candidate design.
5. Carry the qualified conclusions and nonclaims in this document into the
   final project narrative.

This closes the advection-form numerical investigation. It does not claim that
the project's broader physical and spectral questions have been positively
validated; their honest present status is **not established by the archived
evidence**.

## 9. Minimal provenance

| Archived report | Report SHA-256 | Evidence inventory SHA-256 |
|---|---|---|
| `STAGE_B_EXACT_OPERATOR_LEDGER_EVIDENCE_REPORT.md` | `5419765B72A757A4C048761CDBC55B1AAD8ED2A0414E3D9E79CC118A64D40DE4` | `A29D6D1E774E96D6C197B05C7124388EC5AE8A962DACA7B5938A92AAAB07F2C9` |
| `STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_COMPLETION_REPORT.md` | `ABB2F348A678C59A5CDEAB9D6CDC8640870C998C3945CC883662AD2E36DCFB05` | `142B74CF928AEE7E25407D434E29624129B64870619108BE9AAD6964264657A2` |
| `STAGE_D1_REMEDIATED_SEPARATE_TRAJECTORY_PILOT_COMPLETION_REPORT.md` | `C5BDCDE3D97EDB1568B2A6C959CF98A94DE0207415772DAAE181144C0E2850BA` | `B71EF5D9313B1C3FAE007726C92F77F7C0CD17B26D2A27F7841F073BECD8BE20` |
| `STAGE_E_FOCUSED_REFINEMENT_STUDY_COMPLETION_REPORT.md` | `CF1DADE9E99C7EB235AE482F2BD09491E1EE55810D4CFD2928914FB11D5FAE93` | `D5DA8930A9F16FE444C49C7186F15F54531076DD0376D1696140490D93CF181A` |

The Stage E completion report was archived at checkpoint `ecd979d` on branch
`phase4_validation`. This synthesis was created from the archived reports and
audited Stage E evidence without additional numerical execution.
