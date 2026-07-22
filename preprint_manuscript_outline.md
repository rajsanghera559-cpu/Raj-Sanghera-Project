# Historical Preprint Manuscript Outline (Superseded)

> **Status:** This file is retained only as a planning record. The canonical
> submission prose is `technical_report_draft.md`; the frozen figure plan is
> `MANUSCRIPT_FIGURE_SELECTION.md`; and the approved artwork is
> `manuscript_figures/phase4_checkpoint_9b1b4eb_qa_revision1`. Do not maintain
> this outline as a parallel manuscript or use its older placeholders as
> current scientific claims.

> **Figure-plan update:** The older figure placeholders retained in this
> planning document are superseded by `MANUSCRIPT_FIGURE_SELECTION.md`, which
> freezes three main figures after the Phase 4 numerical closure and primary-
> literature pass. The updated plan combines redundant production panels and
> adds one Stage E grid-contraction/resolution figure from archived evidence.

## 1. Proposed Title

Primary title:

**Peak-Masked Residual `k^-3`-Like Spectral Structure in Forced 2D Turbulence Simulations**

Alternative title options:

- Residual Spectral Scaling Diagnostics in a Forced Two-Dimensional Turbulence Simulation
- Validation Chain for Peak-Masked Residual `k^-3`-Like Spectra in a 2D Turbulence Model
- Separating Residual Spectral Shape from Full-System Stationarity in Forced 2D Turbulence Simulations

## 2. Abstract Skeleton

Paragraph 1: Motivation

- Introduce the numerical objective: distinguish apparent spectral slopes from robust residual spectral structure.
- State that the work focuses on forced 2D turbulence simulations and the diagnostic problem of overinterpreting fitted slopes.
- Frame the central question as whether a residual `k^-3`-like spectral shape survives peak masking, stability checks, and numerical-significance diagnostics.

Paragraph 2: Method

- Summarize the validation chain: slope fitting, time stability, energy partition, peak masking, compensated `k^3 E(k)`, stationarity windows, residual budgets, sensitivity, uncertainty, signal-floor checks, shell support, and leave-one-shell-out influence tests.
- Mention that comparison metrics are consolidated using `compare_validated_runs.py`.
- Mention the documented comparison set: Run 004, Run 009, Run 011, Run 012, and Run 013.

Paragraph 3: Main results

- State that Run 004 is the cleanest residual spectral reference.
- State that Run 009 is the cleanest `m=3` no-drag forcing case.
- State that Run 011 gives the strongest stationarity control among combined cases.
- State that Run 013 is the current best balanced combined-strategy case.

Paragraph 4: Caveat and conclusion

- State clearly that the central claim is residual `k^-3`-like spectral validation.
- State that peak domination remains severe.
- State that no fully stationary enstrophy cascade is claimed.
- State that no new turbulence law is claimed.

## 3. Section-by-Section Outline

### 1. Introduction

Purpose:

- Explain the risk of interpreting a clean log-log slope as evidence for a cascade without checking stationarity, energy partition, signal floor, and shell support.
- Introduce the project as a diagnostic pipeline for residual spectral scaling in forced 2D turbulence simulations.
- Keep the manuscript goal limited to documenting a validation chain, not establishing a new physical law.

Paragraph-level notes:

- Paragraph 1: Introduce the broader setting of forced 2D turbulence and spectral scaling diagnostics.
- Paragraph 2: Explain why low-k forcing peaks can make raw spectral interpretations misleading.
- Paragraph 3: State the manuscript objective: validate residual spectral shape after masking the dominant peak and testing robustness.
- Paragraph 4: Preview the conservative conclusion: residual `k^-3`-like structure is supported, full-system stationarity is not.

Source material:

- `technical_report_draft.md`
- `research_checkpoint_report.md`
- `evidence_summary.md`

### 2. Numerical Model and Production Run Setup

Purpose:

- Describe the documented numerical setup and the validated comparison cases without overextending into a full solver derivation.
- Identify the common run parameters and controlled variations.

Paragraph-level notes:

- Paragraph 1: Describe the 2D vorticity solver at a high level and note that spectra are saved for post-processing.
- Paragraph 2: List the common validated production settings: `N=256`, `dt=0.0005`, `nu=5e-05`, `50000` steps, and documented saved-index to step mappings.
- Paragraph 3: Define the case set:
  - Run 004: `f=0.01`, `m=2`, no drag.
  - Run 009: `f=0.01`, `m=3`, no drag.
  - Run 011: `m=3`, `lowk_drag_alpha=0.10`, `lowk_drag_kmax=5`.
  - Run 012: `m=3`, `lowk_drag_alpha=0.05`, `lowk_drag_kmax=5`.
  - Run 013: `m=3`, `lowk_drag_alpha=0.075`, `lowk_drag_kmax=5`.
- Paragraph 4: Explain peak masks and fit windows at the documented level: Run 004 used `k=2:4` mask and `k=9:41`; `m=3` cases used the shifted peak treatment where appropriate.

Source material:

- `technical_report_draft.md`
- `validated_run_comparison.csv`
- `forcing_redesign_comparison.md`
- `analysis_architecture_manifest.md`

### 3. Diagnostic and Validation Methodology

Purpose:

- Present the validation chain as the main methodological contribution of the current checkpoint.
- Make clear that slope fitting is only the first stage.

Paragraph-level notes:

- Paragraph 1: Define the candidate spectral exponent measurement from log-log fitting.
- Paragraph 2: Explain time stability and stationarity-window analysis.
- Paragraph 3: Explain energy and peak-mode diagnostics, especially the need to distinguish residual shape from full-system energy stationarity.
- Paragraph 4: Explain peak masking and normalized residual spectra.
- Paragraph 5: Explain compensated `k^3 E(k)` analysis and compensated CV as a plateau-quality metric.
- Paragraph 6: Explain robustness checks: window sensitivity, exponent uncertainty, signal floor, shell support, and leave-one-shell-out analysis.

Source material:

- `evidence_summary.md`
- `technical_report_draft.md`
- `README_analysis.md`

Figure/table placeholders:

- Table 1: Diagnostic validation chain and purpose.
- Figure 1: Schematic validation flow from raw slope fit to residual robustness checks.

### 4. Baseline Result: Run 004 No-Drag Reference

Purpose:

- Present Run 004 as the cleanest residual spectral reference.
- Preserve the distinction between validated residual shape and nonstationary full-system behavior.

Paragraph-level notes:

- Paragraph 1: Introduce Run 004 parameters and why it became the reference case.
- Paragraph 2: Present the validated residual window: saved indices `38:43`, steps `38000:43000`, fit range `k=9:41`, peak mask `k=2:4`.
- Paragraph 3: Report documented metrics carefully:
  - validated shell-summed window fit slope approximately `-3.0004`, R^2 `0.9668`;
  - consolidated best-window mean slope/R^2 `-3.0036` / `0.9650`;
  - compensated CV `0.2433`;
  - residual exponent uncertainty approximately `-3.00 +/- 0.15`;
  - leave-one-shell-out range `[-3.0778, -2.9517]`.
- Paragraph 4: State the caveat: best-window total/peak energy grew about `+27.92%`, and the full spectrum remained severely low-k dominated.
- Paragraph 5: State the supported conclusion: robust residual `k^-3`-like shape, not full stationary cascade evidence.

Source material:

- `technical_report_draft.md`
- `evidence_summary.md`
- `validated_run_comparison.md`

Figure/table placeholders:

- Figure 2: Run 004 stationarity-window diagnostics.
- Figure 3: Run 004 peak-masked residual spectrum and compensated spectrum.
- Table 2: Run 004 validation metrics.

### 5. Forcing Redesign Results

Purpose:

- Summarize the no-drag forcing redesign cases and their tradeoffs.
- Identify Run 009 as the cleanest `m=3` no-drag forcing case.

Paragraph-level notes:

- Paragraph 1: Explain the motivation for forcing redesign after observing low-k/peak domination.
- Paragraph 2: Summarize lower forcing amplitude `f=0.006`, `m=2`: lower total/peak amplitude than Run 004, residual quality reasonably preserved, but stationarity and peak domination not sufficiently improved.
- Paragraph 3: Summarize Run 009, `f=0.01`, `m=3`, no drag: peak shifted to `k=4`, mask `k=3:5`, slope `-3.0116`, R^2 `0.9619`, compensated CV `0.2366`, best-window growth `+20.78%`.
- Paragraph 4: State that Run 009 is the cleanest `m=3` no-drag forcing case but still only modestly improves stationarity.

Source material:

- `forcing_redesign_comparison.md`
- `validated_run_comparison.md`
- `technical_report_draft.md`

Figure/table placeholders:

- Table 3: Forcing redesign case comparison.
- Optional Figure 4: Run 009 residual and compensated spectra.

### 6. Low-k Drag and Combined Strategy Results

Purpose:

- Present the low-k drag and combined forcing-plus-drag results as stationarity/residual-quality tradeoff tests.
- Identify Run 011 as strongest stationarity control among combined cases.
- Identify Run 013 as current best balanced combined-strategy case.

Paragraph-level notes:

- Paragraph 1: Explain why low-k selective drag was introduced: to reduce low-k energy accumulation while preserving residual transfer-range structure.
- Paragraph 2: Note that pure low-k drag improved stationarity/peak control but did not recover the cleanest residual validation of Run 004.
- Paragraph 3: Explain the combined `m=3` strategy and the null `kmax=4` result: the shifted forced reservoir near `|k| ~= 4.24` was likely not included.
- Paragraph 4: Present Run 011 (`alpha=0.10`, `kmax=5`) as strongest stationarity control among combined cases: best-window growth `+6.80%`, but residual metrics degraded relative to Run 009.
- Paragraph 5: Present Run 012 (`alpha=0.05`, `kmax=5`) as the previous balanced case before Run 013.
- Paragraph 6: Present Run 013 (`alpha=0.075`, `kmax=5`) as the current best balanced combined-strategy case: slope `-2.9916`, R^2 `0.9466`, compensated CV `0.2962`, best-window growth `+9.38%`.
- Paragraph 7: State that further alpha-only tuning is not immediately justified by the current checkpoint.

Source material:

- `forcing_redesign_comparison.md`
- `validated_run_comparison.csv`
- `validated_run_comparison.md`
- `research_checkpoint_report.md`

Figure/table placeholders:

- Table 4: Combined strategy comparison.
- Figure 5: `validated_run_tradeoff_plot.png`.

### 7. Comparative Results Across Validated Cases

Purpose:

- Consolidate the current validated comparison set.
- Highlight the best case by objective without implying a single final winner.

Paragraph-level notes:

- Paragraph 1: Introduce the comparison set and the role of `compare_validated_runs.py`.
- Paragraph 2: Present the best-case-by-objective table:
  - Run 004: cleanest residual spectral validation.
  - Run 009: cleanest `m=3` no-drag forcing case.
  - Run 011: strongest stationarity control among combined cases.
  - Run 013: best balanced compromise.
- Paragraph 3: Present the tradeoff interpretation: within the current validated comparison set, stronger stationarity control tends to trade off against residual spectral cleanliness.
- Paragraph 4: State the main caveat directly after the table: these are residual-spectrum validation results, not evidence of a fully stationary enstrophy cascade.

Source material:

- `research_checkpoint_report.md`
- `validated_run_comparison.md`
- `validated_run_comparison.csv`
- `technical_report_draft.md`

Figure/table placeholders:

- Table 5: Current best case by objective.
- Table 6: Validated run comparison.
- Figure 5: Tradeoff plot, `validated_run_tradeoff_plot.png`.

### 8. Interpretation

Purpose:

- Interpret the evidence conservatively.
- Separate residual spectral validation from full-system stationarity.

Paragraph-level notes:

- Paragraph 1: State the strongest supported result: Run 004 shows a robust peak-masked residual `k^-3`-like spectral shape over steps `38000-43000`.
- Paragraph 2: State that Run 013 is currently the best balanced combined-strategy case, not because it is the cleanest residual spectrum, but because it balances residual-shape survival with improved stationarity behavior.
- Paragraph 3: Explain the tradeoff among Run 004, Run 009, Run 011, and Run 013.
- Paragraph 4: Emphasize that severe peak domination remains and prevents a full stationary cascade claim.

Source material:

- `technical_report_draft.md`
- `research_checkpoint_report.md`
- `validated_run_comparison.md`

### 9. Limitations and Non-Claims

Purpose:

- Make the caveats visible and prevent accidental overclaiming.

Paragraph-level notes:

- Paragraph 1: State that no fully stationary enstrophy cascade is claimed.
- Paragraph 2: State that no new turbulence law is claimed.
- Paragraph 3: State that the full system remains severely low-k/peak dominated.
- Paragraph 4: State that residual energy is small compared with peak energy.
- Paragraph 5: State that the strongest evidence is window-local and residual-spectrum based.
- Paragraph 6: State that fit-window choice affects exact exponent estimates, though robustness checks support `k^-3`-like wording.

Source material:

- `technical_report_draft.md`
- `evidence_summary.md`
- `research_checkpoint_report.md`

### 10. Reproducibility and Artifact Index

Purpose:

- Document how the current checkpoint can be reproduced from existing artifacts.
- Point readers to the comparison tool and traceability documents.

Paragraph-level notes:

- Paragraph 1: Introduce `compare_validated_runs.py` as a read-only consolidation tool.
- Paragraph 2: List generated curated comparison outputs:
  - `validated_run_comparison.csv`
  - `validated_run_comparison.md`
  - `validated_run_tradeoff_plot.png`
- Paragraph 3: Explain that raw `outputs_*` folders are preserved but ignored by Git.
- Paragraph 4: Point to `README_analysis.md` and `analysis_architecture_manifest.md` for workflow and layout documentation.
- Paragraph 5: State that no simulations are run by the comparison tool.

Source material:

- `README_analysis.md`
- `analysis_architecture_manifest.md`
- `validated_run_comparison.md`

### 11. Recommended Next Work

Purpose:

- Define what should happen before a full manuscript draft or another scientific phase.

Paragraph-level notes:

- Paragraph 1: Recommend pausing new simulations while the manuscript structure and reproducibility story are stabilized.
- Paragraph 2: Recommend a literature/reference pass before converting the outline into a formal manuscript.
- Paragraph 3: Recommend preserving the current claims and caveats during full drafting.
- Paragraph 4: Note possible future scientific directions only as future work: longer integration, stationarity-focused redesign, higher-resolution validation, or analysis architecture cleanup.

Source material:

- `technical_report_draft.md`
- `research_checkpoint_report.md`
- `analysis_architecture_manifest.md`

## 4. Figure and Table Placeholders

Tables:

- Table 1: Diagnostic validation chain and purpose.
- Table 2: Run 004 validation metrics.
- Table 3: Forcing redesign comparison.
- Table 4: Combined strategy comparison.
- Table 5: Current best case by objective.
- Table 6: Validated run comparison.
- Table 7: Artifact index and source files.

Figures:

- Figure 1: Validation-chain schematic.
- Figure 2: Run 004 peak-masked residual spectrum.
- Figure 3: Run 004 compensated `k^3 E(k)` spectrum.
- Figure 4: Run 004 stationarity-window diagnostics.
- Figure 5: `validated_run_tradeoff_plot.png`.
- Optional Figure 6: Run 009 residual/compensated spectrum.
- Optional Figure 7: Run 013 residual/compensated spectrum.

Current curated figure reference:

- `validated_run_tradeoff_plot.png`

## 5. Supported Claims

- Run 004 is the cleanest residual spectral reference.
- Run 004 shows a robust peak-masked residual `k^-3`-like spectral shape over steps `38000-43000`.
- Run 009 is the cleanest `m=3` no-drag forcing case.
- Run 011 gives the strongest stationarity control among the listed combined cases.
- Run 013 is the current best balanced combined-strategy case.
- The current validated comparison set shows a stationarity/residual-cleanliness tradeoff.
- The validation chain supports residual `k^-3`-like wording for selected windows.
- Signal-floor, shell-support, and leave-one-shell-out diagnostics support that the residual fit is not obviously controlled by numerical floor, sparse shells, or one individual shell.

## 6. Claims to Avoid

- Do not claim a fully stationary enstrophy cascade.
- Do not claim a new turbulence law.
- Do not claim global stationarity.
- Do not claim that peak domination has been solved.
- Do not claim that residual `k^-3`-like spectral shape proves full-system cascade behavior.
- Do not describe Run 013 as universally best; it is the best balanced case within the current validated comparison set.
- Do not describe further alpha-only tuning as immediately justified.

## 7. Literature Placeholders

References to add before full drafting:

- Foundational 2D turbulence theory and enstrophy cascade literature.
- Kraichnan-Batchelor `k^-3` spectral scaling context.
- Forced-dissipative 2D Navier-Stokes simulation methods.
- Large-scale friction / Ekman drag in 2D turbulence.
- Spectral shell averaging and compensated-spectrum diagnostics.
- Finite-time and finite-resolution effects in numerical turbulence.
- Best practices for uncertainty and robustness checks in spectral fitting.

The literature review should be a separate step before final manuscript polishing. Exact citations should be verified from primary sources.

## 8. Reproducibility and Artifact Section

Core reproducibility files:

- `README_analysis.md`
- `analysis_architecture_manifest.md`
- `compare_validated_runs.py`

Curated comparison outputs:

- `validated_run_comparison.csv`
- `validated_run_comparison.md`
- `validated_run_tradeoff_plot.png`

Primary documentation sources:

- `technical_report_draft.md`
- `research_checkpoint_report.md`
- `forcing_redesign_comparison.md`
- `evidence_summary.md`

Notes:

- `compare_validated_runs.py` consolidates existing validation metrics and does not run simulations.
- Raw `outputs_*` folders remain fixed and should not be moved during manuscript cleanup.
- Root diagnostic artifacts are generated/local unless later curated into a formal analysis-output package.

## 9. Next Steps Before Full Drafting

1. Perform a literature/reference planning pass.
2. Decide which figures are manuscript-grade and which need re-rendering from existing data.
3. Convert this outline into a manuscript draft only after references and figure choices are approved.
4. Keep all claims limited to residual-spectrum validation unless new evidence is generated later.
5. Preserve the central caveat that peak domination remains severe.

No new simulations are required before drafting a conservative preprint-style manuscript. New simulations would only be needed for stronger claims about stationarity, resolution convergence, or a validated full enstrophy cascade.
