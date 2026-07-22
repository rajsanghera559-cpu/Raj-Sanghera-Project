---
bibliography: references.bib
link-citations: true
---

# Residual `k^-3`-Like Spectral Structure, Stationarity Tradeoffs, and Numerical Sensitivity in a Forced Two-Dimensional Vorticity Solver

## Document status

This is the canonical technical-report manuscript source synchronized to the
Phase 4 numerical-closure checkpoint:
`8fbe94541cf57ef7c2b519ca080f4288207e6c95` on branch
`phase4_validation`.

It integrates two related but distinct evidence streams:

1. the archived Run 004–013 residual-spectrum campaign; and
2. the Phase 13 and Stage B–E numerical-verification campaign.

The configurations and scientific questions differ between those streams.
Stage E is therefore numerical-method sensitivity evidence for its frozen
smooth problem, not a direct refinement or convergence test of Runs 004–013.
The primary-literature citation pass is integrated through `references.bib`;
final manuscript-figure selection remains to be completed. No new numerical
result is introduced here.

## Abstract

This report examines two distinct questions in a forced two-dimensional
vorticity solver: whether selected peak-masked spectra exhibit a robust residual
`k^-3`-like shape, and whether the numerical pathways used to produce and
interpret such results show controlled benchmark and refinement behavior.

In the archived production comparison, Run 004 provides the cleanest residual
spectral-shape case over steps `38,000–43,000`. Runs 009, 011, and 013 expose a
tradeoff between residual-shape quality and improved stationarity control. The
reported shape survives time-window, fit-range, signal-floor, shell-support,
and leave-one-shell-out checks. Nevertheless, the spectra remain strongly
low-wavenumber dominated and the strongest results are peak-masked and
window-local. They do not establish a stationary enstrophy cascade or a
physical `k^-3` law.

A separate verification and sensitivity campaign was conducted under
independently frozen configurations. Phase 13 exact, manufactured, and
exploratory benchmarks separated arithmetic-floor, spatial-error-dominated,
and timestep-error-dominated regimes. Stage B closed an exact implemented
RK2-plus-mask enstrophy ledger. Stage C found mixed, operator-form-dependent
same-state enstrophy work. Stage D1R demonstrated independently owned,
internally consistent alternate trajectories. Stage E then completed 229,500
accepted primary updates across five refinement cases. All five primary
trajectories showed essentially second-order temporal self-refinement; the
finite-difference and Arakawa positions showed approximately second-order
spatial self-refinement; and all ten operator-pair separations decreased under
grid refinement, with none resolved against the declared uncertainty rule.

The combined evidence supports a reproducible residual spectral resemblance in
selected production windows and a truncation-error explanation for the
operator-form separations measured in the separate smooth refinement problem.
It does not provide a validated numerical reference, method ranking, formal
universal convergence result, or physical cascade validation. The numerical
investigation closes at Phase 4 checkpoint `8fbe945`.

## 1. Research questions and claim boundaries

The production spectral campaign asks:

> Does a residual spectral shape close to `k^-3` remain after masking the
> forcing-scale peak and testing time-window stability, compensated spectra,
> signal floor, shell support, and fit sensitivity?

The later numerical-verification campaign asks:

> Are the implemented solver pathways internally consistent, and do measurable
> advection-form trajectory differences persist after controlled timestep and
> grid refinement?

The first is a spectral-diagnostic question. The second is a code-verification
and numerical-sensitivity question. Neither alone establishes turbulence, a
cascade, an inertial range, or a physical scaling law.

The `-3` reference originates in classical two-dimensional turbulence theory.
Conservation of kinetic energy and mean-square vorticity constrains inviscid
spectral redistribution [@Fjortoft1953], while the Kraichnan--Batchelor
phenomenology associates a direct enstrophy-transfer range with
$E(k) \propto k^{-3}$ [@Kraichnan1967; @Batchelor1969]. The nominal
`k^-3` range is marginally nonlocal and admits a logarithmic correction
[@Kraichnan1971]; limited scale separation therefore complicates asymptotic
interpretation [@Bowman1996]. These theoretical results make `-3` a meaningful
comparison exponent, but they do not turn agreement with that exponent into
evidence of a cascade.

Throughout this report:

- “residual `k^-3`-like” describes a qualified spectral resemblance in selected
  peak-masked windows;
- “reference case” means a descriptive within-set comparison case, not a
  validated numerical truth;
- “unresolved” means that measured separation does not exceed the conservative
  discretization-uncertainty envelope; and
- refinement behavior is reported only for its declared frozen problem and
  measured range.

## 2. Numerical configurations

### 2.1 Archived production spectral cases

The spectral comparison cases used:

| Parameter | Common production value |
|---|---:|
| Grid | `N=256` |
| Timestep | `dt=0.0005` |
| Viscosity | `nu=5e-05` |
| Updates | `50,000` |
| Saved-spectrum spacing | `1,000` updates in the documented windows |

The controlled variations were forcing mode, forcing amplitude, and low-k
selective drag.

### 2.2 Focused Stage E refinement problem

Stage E used a different frozen problem:

| Parameter | Stage E value |
|---|---|
| Domain | periodic `2*pi` square |
| Initial vorticity | exact zero |
| Reynolds number / viscosity | `Re=1000` / `nu=0.001` |
| Forcing | smooth multimode, RMS `0.005` |
| Grids | `N=64`, `96`, `144` |
| Timesteps | `0.005`, `0.0025`, `0.00125` |
| Final time | `T=15.3` |
| Primary trajectories | FD advective, FD conservative, FD skew, pseudo-spectral advective, Arakawa |

The case matrix was L-shaped: timestep refinement was performed at `N=64`,
and spatial refinement used `dt=0.00125`. A complete space–time interaction
matrix was not measured.

## 3. Residual-spectrum diagnostic methodology

The production analysis used a chained diagnostic standard rather than a slope
fit alone.

| Diagnostic | Purpose |
|---|---|
| Candidate slope fit | Identify spectra with a residual exponent near `-3`. |
| Time-window analysis | Test whether the fitted shape persists over nearby saved spectra. |
| Total and peak energy histories | Separate shape persistence from full-system stationarity. |
| Energy partition | Quantify low-k and forcing-peak domination. |
| Peak masking | Test whether the residual shape survives removal of the dominant forcing band. |
| Compensated `k^3 E(k)` spectrum | Examine plateau-like residual behavior. |
| Window sensitivity | Measure dependence on time and fit-range choices. |
| Exponent uncertainty | Report a defensible range rather than a single exact exponent. |
| Signal-floor analysis | Verify that fitted residual values exceed numerical-floor estimates. |
| Shell-support analysis | Check radial-mode population in the fitted range. |
| Leave-one-shell-out analysis | Test whether one shell controls the fit. |

This chain supports cautious residual-shape wording. It cannot replace
stationary budgets or spectral-flux evidence for a cascade claim. More
generally, apparent power-law fits are sensitive to range selection and require
goodness-of-fit and competing-explanation checks [@ClausetEtAl2009]. In forced
two-dimensional turbulence, stronger cascade demonstrations combine
stationarity with signed energy and enstrophy flux diagnostics
[@Boffetta2007; @VallgrenLindborg2011]. The present diagnostic chain does not
claim to reproduce either paper's physical regime or flux analysis.

## 4. Archived production spectral results

### 4.1 Run 004 residual-shape result

Run 004 is the cleanest residual-shape comparison case in the archived set.

| Field | Value |
|---|---|
| Parameters | `N=256`, `dt=0.0005`, `nu=5e-05`, forcing amplitude `0.01`, forcing mode `2`, no drag |
| Selected window | saved indices `38:43`, steps `38,000:43,000` |
| Fit range / peak mask | `k=9:41` / `k=2:4` |
| Window fit slope / `R^2` | approximately `-3.0004` / `0.9668` |
| Consolidated mean slope / `R^2` | `-3.0036` / `0.9650` |
| Compensated coefficient of variation | `0.2433` |
| Residual exponent uncertainty | approximately `-3.00 +/- 0.15` |
| Leave-one-shell-out slope range | `[-3.0778, -2.9517]` |
| Minimum leave-one-out `R^2` | `0.9631` |
| Minimum / median fitted-shell population | `56 / 160` modes |
| Selected-window total/peak energy growth | approximately `+27.92%` |

The residual shape is well above the recorded numerical floor and is not
controlled by one radial shell. Its key limitation is physical: total and peak
energy continued growing, the residual amplitude was small relative to the
forcing-scale peak, and the full spectrum remained severely low-k dominated.

### 4.2 Forcing and drag comparisons

| Case | Configuration | Slope | `R^2` | Compensated CV | Window growth | Descriptive interpretation |
|---|---|---:|---:|---:|---:|---|
| Run 004 | mode `2`, no drag | `-3.0036` | `0.9650` | `0.2433` | `+27.92%` | Cleanest residual-shape case; weakest stationarity control. |
| Run 009 | mode `3`, no drag | `-3.0116` | `0.9619` | `0.2366` | `+20.78%` | Cleanest mode-3 no-drag residual shape. |
| Run 011 | mode `3`, `alpha=0.10`, `kmax=5` | `-3.0004` | `0.9448` | `0.3022` | `+6.80%` | Strongest stationarity control among the listed combined cases; weaker residual quality. |
| Run 012 | mode `3`, `alpha=0.05`, `kmax=5` | `-3.0217` | `0.9504` | `0.2860` | `+12.23%` | Intermediate combined case. |
| Run 013 | mode `3`, `alpha=0.075`, `kmax=5` | `-2.9916` | `0.9466` | `0.2962` | `+9.38%` | Representative balanced compromise within the archived set. |

The comparison exposes a tradeoff: stronger low-k stationarity control reduces
total/peak growth but generally weakens residual-shape metrics. Run 013 is not
universally “best”; it is a balanced descriptive case within this limited set.
Further alpha-only tuning was not justified by the archived comparison.

This tradeoff is physically plausible rather than a neutral post-processing
effect. In finite periodic domains, inverse transfer can accumulate energy in
the lowest modes [@SmithYakhot1994], and the representation and strength of
large-scale drag can alter coherent structures, budgets, and spectral slopes
[@SukorianskyEtAl1999; @TsangYoung2009]. Those prior results motivate the drag
comparison; they do not establish that any drag choice here is physically
optimal or stationary.

## 5. Numerical-verification methodology

The verification campaign progressively separated implementation correctness,
same-state operator behavior, independent-trajectory behavior, and refinement.

| Evidence stage | Frozen question |
|---|---|
| Phase 13 | Do exact and manufactured benchmarks expose arithmetic-floor, spatial, and temporal error regimes as expected? |
| Stage B | Which implemented term closes the baseline RK2-plus-mask enstrophy ledger? |
| Stage C | How does discrete advection work change with operator form on identical current and RK2-stage states? |
| Stage D1R | Can every frozen form advance a separately owned trajectory with exact baseline reproduction and integrity controls? |
| Stage E | Do the resulting trajectory differences persist under focused timestep and grid refinement? |

Projected variants were reduced to sparse same-state controls in Stage E rather
than being advanced as four additional production paths.

## 6. Verification and numerical-sensitivity results

### 6.1 Phase 13 foundation

Phase 13 completed an independently audited 10-case pilot followed by 77 finite
exploratory benchmark cases. The matrix separated floating-point-floor,
spatial-error-dominated, and timestep-error-dominated regimes. Manufactured
solutions are a code-verification device rather than physical validation
[@Roache2002]. Accordingly, Phase 13 closed at the exploratory verification and
calibration-evidence level. The deferred full 390-file audit and formal Phase
13H convergence program were not completed and are not silently implied here.

### 6.2 Stage B exact ledger

Stage B closed an exact implemented RK2-plus-mask enstrophy ledger for 20,001
updates. Discrete advection dominated the three omitted
non-forcing/non-viscous terms: advection work, the RK2 quadratic remainder, and
the post-step mask contribution.

This does not mean advection dominated the complete forcing-viscosity budget.
In the final Stage B window, viscous removal exceeded forcing plus positive
discrete-advection input, and accepted-state enstrophy declined at every
recorded step. The baseline was **not stationary within the tested duration**.

### 6.3 Stage C same-state operator behavior

On identical baseline current and RK2-stage states, centered conservative work
retained the baseline magnitude with opposite sign. Centered skew,
real-compatible pseudo-spectral, and Arakawa work were near-neutral. This
established mixed form dependence on the frozen baseline states, not accuracy
or alternate-trajectory behavior.

The Arakawa position is historically motivated by a conservation-designed
discrete Jacobian [@Arakawa1966]. That construction does not imply conservation
for the present forced, viscous, filtered RK2 trajectory, and the Stage C result
is therefore reported only for the implemented same-state comparison.

### 6.4 Stage D1R independent trajectories

The remediated D1 pilot advanced seven independently owned trajectories for
3,060 updates each through `T=15.3`. It reproduced all 3,060 required baseline
rows and recorded zero integrity, shared-memory, or order-invariance failures.
The result established implementation integrity; it did not rank trajectories
or establish convergence.

The original D1 implementation stopped before its first accepted update because
its discarded-field Parseval definition did not reproduce the Stage B ledger.
It supplied no scientific result. D1R corrected that bookkeeping definition
without relaxing the thresholds.

### 6.5 Stage E focused refinement

Stage E completed five cases, 25 primary trajectories, and 229,500 accepted
updates. Its independent evidence audit verified the expected row counts, 175
checkpoint arrays, and zero integrity, ownership, mutation, aliasing, or
finite-value failures.

All five trajectories showed essentially second-order temporal self-refinement
at every positive-time anchor. At `T=15.3`, observed temporal orders ranged
from `1.997998` to `2.000092`.

The final finite-difference/Arakawa spatial results were:

| Trajectory | Fine spatial increment | Observed `p_x` |
|---|---:|---:|
| FD advective | `5.37055e-5` | `1.98592` |
| FD conservative | `1.23811e-4` | `1.96083` |
| FD skew | `8.17261e-5` | `1.96996` |
| Arakawa | `5.97500e-5` | `1.96419` |

The pseudo-spectral spatial increment fell from `2.86892e-8` to
`6.05372e-12`. Much of that sequence approached the measured numerical floor,
so its large formal ratio is not reported as a physical convergence order.

Every one of the ten operator-pair separations decreased monotonically under
grid refinement. At `N=144`, final separations were approximately
`0.1987–0.2015` of their `N=64` values. Nevertheless, no pair satisfied the
frozen resolution condition:

- `0 / 70` pair-anchor records were resolved overall;
- `0 / 60` positive-time records were resolved; and
- final uncertainty/separation ranged from `1.239` to `5.154`, versus the
  required maximum of `0.20`.

The finite-grid differences are measurable and are not called zero. Their grid
decay and unresolved status support a truncation-error explanation within the
tested range rather than resolved persistent continuum separation.

Systematic grid-refinement reporting normally distinguishes observed order,
estimated discretization uncertainty, and the assumptions behind an
asymptotic-range interpretation [@CelikEtAl2008]. Stage E followed its own
predeclared conservative uncertainty rule; it was not a formal Grid Convergence
Index calculation and does not claim compliance with that procedure.

All 60 sampled post-filter accepted-update projection previews passed, with a
maximum normalized effect of `2.16405e-13`. Raw same-state transport projection
was not uniformly negligible: 22 of 70 rows failed the descriptive rule. The
accepted-step sparse controls were sufficient for the trajectory question, but
projection cannot be declared irrelevant in general.

## 7. Integrated interpretation

Two findings coexist without being conflated.

First, selected production runs contain a peak-masked residual spectral shape
that remains close to `k^-3` across the documented window-sensitivity,
signal-floor, shell-support, and leave-one-shell-out checks. Run 004 remains the
cleanest residual-shape case, Run 011 the strongest stationarity-control case
among the listed combined configurations, and Run 013 a balanced compromise
within that parameter comparison.

Prior stationary high-resolution studies demonstrate why this distinction
matters: cascade evidence is materially stronger when spectral shape is paired
with signed fluxes and controlled forcing--dissipation balances
[@Boffetta2007; @VallgrenLindborg2011]. Those diagnostics were not established
for Runs 004--013.

Second, the separate verification campaign shows that discrete advection work
is operator-form dependent at fixed resolution, but that the independently
advanced trajectory differences measured in the smooth Stage E problem
contract approximately as spatial truncation error and remain unresolved
against the declared uncertainty envelope. This strengthens confidence in the
tested implementation pathways and explains the observed finite-grid
sensitivity. It does not directly prove convergence of the Run 004–013 spectra
or convert their residual spectral resemblance into evidence of a physical
cascade.

The strongest combined conclusion is diagnostic rather than universal: the
archived production data support a robust residual `k^-3`-like shape in
selected windows, while full-system stationarity, a cascade, and a physical
spectral law remain unestablished.

## 8. Limitations and non-claims

- Runs 004–013 were not subjected to the focused grid-and-timestep matrix used
  in Stage E.
- Stage E used a smooth forced problem at `Re=1000` through `T=15.3` and an
  L-shaped refinement matrix, not a complete space–time interaction study.
- Phase 13 closed at the exploratory verification level rather than producing
  formal solver-wide convergence or physical validation.
- No validated reference solution or accuracy ranking exists.
- The production spectra remain severely low-wavenumber dominated, with peak
  fractions close to one.
- The strongest spectral evidence is residual, peak-masked, and window-local.
- No archived result establishes global stationarity, turbulence, an inertial
  range, an enstrophy cascade, or a physical `k^-3` law.
- The conclusions do not generalize beyond the respective frozen
  configurations.

The evidence is consistent with a common-continuum truncation-error explanation
for the Stage E trajectories over the measured range. It does not prove that
the methods converge to the same exact solution, that their differences vanish,
or that any method is superior.

## 9. Reproducibility and artifact index

The current read-only production comparison is consolidated by:

- `compare_validated_runs.py`;
- `validated_run_comparison.csv`;
- `validated_run_comparison.md`; and
- `validated_run_tradeoff_plot.png`.

The canonical numerical-evidence chain is:

- `PHASE13_EXPLORATORY_NUMERICAL_RESULTS_AND_CLOSURE.md`;
- `STAGE_B_EXACT_OPERATOR_LEDGER_EVIDENCE_REPORT.md`;
- `STAGE_C_REMEDIATED_FULL_SAME_STATE_SHADOW_AUDIT_COMPLETION_REPORT.md`;
- `STAGE_D1_REMEDIATED_SEPARATE_TRAJECTORY_PILOT_COMPLETION_REPORT.md`;
- `STAGE_E_FOCUSED_REFINEMENT_STUDY_COMPLETION_REPORT.md`; and
- `FINAL_NUMERICAL_INVESTIGATION_SCIENTIFIC_SYNTHESIS_AND_CLOSURE.md`.

Generated run directories and inventories are preserved as immutable evidence.
The synthesis and completion reports contain their controlling repository and
file identities; this manuscript does not duplicate those hash inventories.
This artifact-centered reporting follows the general reproducibility principle
that computational results should retain traceable inputs, code, intermediate
evidence, and versioned provenance [@SandveEtAl2013]. The citation supports the
reporting practice, not the scientific validity of the solver or spectra.

The manuscript bibliography is maintained in `references.bib`. Project-specific
numerical values remain sourced to the repository artifacts listed above, not
to external literature.

## 10. Phase 4 closure and future scope

The numerical investigation is closed at checkpoint `8fbe945`. No longer
same-grid Stage D2 run, automatic `N=216` escalation, or additional provenance
gate is required for the present operator-persistence question.

Remaining Phase 4 work is documentary:

1. select or re-render manuscript-grade figures from existing evidence;
2. complete the full prose manuscript and reproducibility section;
3. perform one final editorial and reference check; and
4. prepare the documentation-aligned Phase 4 release or tag under the
   repository's established convention.

Any future method-ranking study must be treated as a new objective requiring a
separately validated reference candidate. Any future physical cascade claim
would require a production-configuration refinement study, stationary budget
and flux evidence, and appropriate long-time or ensemble analysis. Neither is
part of the closed Phase 4 numerical scope.

## Manuscript work remaining

The primary-literature pass now covers two-dimensional cascade theory,
finite-range limitations, finite-box accumulation, large-scale drag, flux and
stationarity standards, manufactured-solution verification, the Arakawa
Jacobian, discretization-uncertainty reporting, and reproducible computational
practice. Citations are scoped as context, methodology, or limitations; none is
used as external validation of a project-specific numerical value.

Figure selection should prioritize existing evidence that communicates the
scientific tradeoffs directly: the Run 004 peak-masked and compensated spectra,
stationarity-window diagnostics, the validated-run tradeoff plot, and one
compact Stage E refinement/uncertainty figure generated only from archived
evidence.

## References

::: {#refs}
:::
