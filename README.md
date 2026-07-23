# Raj-Sanghera-Project

## Purpose

This repository contains a two-dimensional vorticity solver and a controlled
research workflow for distinguishing residual spectral structure from
numerical, fitting, and stationarity artifacts.

The project has two related evidence streams:

1. residual-spectrum analysis of the documented production runs; and
2. numerical verification of the solver, discrete advection operators, exact
   enstrophy ledgers, independently advanced trajectories, and refinement
   sensitivity.

## Current status

**Phase 4 numerical investigation: closed within its declared scope.**

- Branch: `phase4_validation`
- Numerical-closure checkpoint:
  `8fbe94541cf57ef7c2b519ca080f4288207e6c95`
- Manuscript-artwork checkpoint:
  `098ba417f504a273ff5e0420446be81c181c302e`
- Scientific-manuscript release-candidate checkpoint:
  `b6b0e52378352d579dac59306a1fa3ac737b8239`
- Annotated release-candidate tag:
  `v0.5.63-phase4-manuscript-release-candidate-1`
- Canonical closure document: [Final numerical investigation scientific
  synthesis and closure](FINAL_NUMERICAL_INVESTIGATION_SCIENTIFIC_SYNTHESIS_AND_CLOSURE.md)
- Additional numerical execution required for the closed advection-form
  question: none

The focused result is that, for the tested smooth forced-vorticity problem at
`Re=1000` through `T=15.3`, finite-grid advection-form trajectory differences
are dominated by spatial discretization. They decrease approximately as second
order under refinement, and no operator pair is resolved relative to the
declared discretization-uncertainty rule. This supports a truncation-error
interpretation over the measured range; it does not establish exact continuum
equivalence or rank the methods.

## Residual-spectrum result

The existing production-run analysis supports a robust **peak-masked residual
`k^-3`-like spectral shape** in selected windows. Run 004 remains the cleanest
residual spectral reference among the documented cases.

This is a residual-shape result, not validation of a stationary enstrophy
cascade or a physical `k^-3` law. The full spectra remain severely low-k/peak
dominated, and full-system stationarity was not established.

| Objective | Current documented case |
|---|---|
| Cleanest residual spectral reference | Run 004 |
| Cleanest `m=3` no-drag case | Run 009 |
| Lowest selected-window energy growth among combined cases | Run 011 |
| Descriptive balanced combined-strategy case | Run 013 |

These labels are objective-specific comparisons within the archived case set,
not a universal ranking.

## Numerical-verification result

The completed verification chain established:

- exact and manufactured benchmark behavior at the exploratory calibration
  level in Phase 13;
- an exact implemented RK2-plus-mask enstrophy ledger in Stage B;
- form-dependent and mixed same-state advection work in Stage C;
- seven independently owned and internally consistent trajectories in the
  remediated Stage D1 pilot; and
- focused timestep and grid self-refinement in Stage E.

Stage E completed 229,500 accepted primary updates with zero recorded
integrity, ownership, mutation, aliasing, or finite-value failures. All five
primary operator families showed essentially second-order temporal self-refinement.
The finite-difference and Arakawa trajectories showed approximately
second-order spatial self-refinement, while the pseudo-spectral spatial
increments approached the numerical floor. All ten operator pairs remained
unresolved against the declared uncertainty criterion.

## Scientific boundaries

The archived evidence does not establish:

- a fully stationary enstrophy cascade;
- turbulence, an inertial range, or a new physical law;
- a validated numerical reference solution;
- method superiority or production-solver replacement;
- formal universal continuum convergence; or
- generalization beyond the tested configurations.

The Stage E refinement problem and the older production spectral runs use
different configurations. Stage E therefore strengthens the numerical-method
interpretation but is not a direct convergence proof for Runs 004–013.

## Canonical documentation

| Document | Role |
|---|---|
| [Final numerical investigation scientific synthesis and closure](FINAL_NUMERICAL_INVESTIGATION_SCIENTIFIC_SYNTHESIS_AND_CLOSURE.md) | Authoritative numerical conclusion and closure |
| [Stage E focused-refinement completion report](STAGE_E_FOCUSED_REFINEMENT_STUDY_COMPLETION_REPORT.md) | Focused timestep/grid evidence and interpretation |
| [Phase 13 exploratory numerical results and closure](PHASE13_EXPLORATORY_NUMERICAL_RESULTS_AND_CLOSURE.md) | Verification and calibration foundation |
| [Technical report draft](technical_report_draft.md) | Canonical manuscript source |
| [Primary-literature bibliography](references.bib) | Verified bibliography used by the canonical manuscript |
| [Citation metadata](CITATION.cff) | Release-candidate author, title, version, and preferred-citation metadata |
| [Manuscript figure selection](MANUSCRIPT_FIGURE_SELECTION.md) | Frozen three-figure main-text plan and supplementary disposition |
| [Approved Phase 4 manuscript artwork](manuscript_figures/phase4_checkpoint_9b1b4eb_qa_revision1) | Three PNG/PDF figures, captions, and portable inventory |
| [Manuscript figure renderer](render_phase4_manuscript_figures.py) | Presentation-only assembly from archived evidence; no numerical stepping |
| [Phase 4 evidence manifest](PHASE4_EVIDENCE_MANIFEST.json) | Checksums, run identities, completion reports, and Zenodo DOI for the D1R and Stage E companion archives |
| [Reproduction environment record](REPRODUCTION_ENVIRONMENT.md) | Recorded historical facts, captured present-day inspection environment, and known limitations |
| [Publication environment pin](requirements-publication.txt) | Exact present-day package versions used for publication-artifact inspection and figure regeneration |
| [Software license](LICENSE) | MIT License for project-authored software |
| [Content and evidence license](LICENSE-CONTENT.md) | CC BY 4.0 terms for project-authored manuscript content, figures, documentation, and released evidence |
| [Preprint manuscript outline](preprint_manuscript_outline.md) | Superseded historical planning artifact |
| [Analysis README](README_analysis.md) | Existing read-only comparison workflow |

Historical phase reports remain part of the immutable evidence trail; they are
not all current-status entry points.

## Main software components

- `project/solver/spectral_solver.py`: frozen reference solver core
- `project/solver/advection_operators.py`: discrete advection implementations
- `compare_validated_runs.py`: read-only consolidation of existing validation
  metrics
- `render_phase4_manuscript_figures.py`: read-only inspection and
  presentation-only manuscript artwork assembly
- `experiments/`: generated run evidence and archived metadata

Solver internals should not be modified casually. Diagnostics and analysis
should be added around the solver, and completed run directories should be
treated as immutable evidence.

## Reproducibility boundary

The repository contains the Stage B and Stage C raw evidence and the approved
manuscript artwork. Some older production inputs and the D1R and Stage E
evidence bundles are generated-data artifacts and are not present in a clean
clone. The [Phase 4 evidence manifest](PHASE4_EVIDENCE_MANIFEST.json) records
the controlling package hashes, run identities, inventories, and completion
reports for the two companion bundles. The companion evidence record is
identified by Zenodo DOI
[`10.5281/zenodo.21505468`](https://doi.org/10.5281/zenodo.21505468). The
[environment record](REPRODUCTION_ENVIRONMENT.md) distinguishes recorded
historical execution facts from the captured present-day publication
workstation environment; `requirements-publication.txt` pins the corresponding
package versions. Complete independent row-level inspection of D1R and Stage E
from a clean clone requires downloading those DOI-identified companion
archives.

## Next project step

No new simulation or numerical audit is warranted for the closed Phase 4
question. The primary-literature citations, canonical prose, reproducibility
boundary, approved three-figure set, publication metadata, release-candidate
tag, and present-day publication environment are integrated. The
remaining release work is to upload the two evidence bundles, their completion
reports, and the manifest to the reserved Zenodo record, preview and publish
that record, and perform one venue-specific editorial/reference/layout pass
before a final release tag. Any future reference-ranking, stationarity/flux,
or physical-validation study should begin as a new, explicitly scoped
scientific objective.
