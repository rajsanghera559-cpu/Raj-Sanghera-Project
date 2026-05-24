# Analysis Architecture Manifest

## Purpose

This manifest freezes the current project layout before any analysis architecture cleanup. It documents the current file roles, output folders, analysis artifacts, report references, risks, and a copy-first cleanup strategy.

No files have been moved as part of this manifest. Output folders should remain fixed unless a later cleanup plan explicitly updates references and validates reproducibility.

## 1. Current Project Layout

The project root currently contains several kinds of files side by side:

| Category | Current location |
|---|---|
| Solver and run logic | project root |
| Analysis scripts | project root |
| Reports and documentation | project root |
| Generated root-level CSV/PNG diagnostics | project root |
| Validated comparison artifacts | project root |
| Raw and per-run simulation outputs | `outputs*` directories |
| Legacy or exploratory project files | project root, `outputs`, `snapshots`, `project`, and related folders |

This layout is workable but fragile because reports and scripts use root-relative paths. Moving files before path handling is cleaned up could break traceability.

## 2. Core Solver / Runner Files

| File | Role | Cleanup recommendation |
|---|---|---|
| `solver.py` | Primary numerical solver. Includes spectrum output generation and drag options. | Leave in project root. Do not modify during architecture cleanup unless explicitly approved. |
| `run_spectral_sweep.py` | Parameter sweep runner that calls `solver.py` and can trigger analysis. | Leave in root initially because it likely assumes root-relative paths. |
| `fit_spectral_slope.py` | Main spectral fitting / sweep analysis tool. | Treat as current analysis infrastructure; copy before moving. |

Supporting or older runner/infrastructure files:

| File | Observed role |
|---|---|
| `runner.py` | Older parameter sweep runner for earlier solver interface. |
| `run_phase_map.py` | Phase-map generation runner. |
| `collapse.py` | Generates a collapse figure from parameter sweep data. |
| `version_control.py` | Project-specific version control helper. |
| `init_repo.py` | Repository initialization helper. |

## 3. Current Analysis Scripts

Current root-level analysis or plotting scripts:

| Script | Known or likely purpose | Known inputs | Known outputs |
|---|---|---|---|
| `fit_spectral_slope.py` | Fits spectral slopes over one or more spectrum output folders; supports fixed and automatic fit windows. | `spectrum_bins.npy`, `spectrum_k_*.npy` in output folders. | Fit summary CSVs and spectrum comparison plots. |
| `time_stability_analysis.py` | Computes time-indexed slope and R^2 for selected runs. | Selected spectrum folders. | `time_stability_summary.csv`, `time_stability_slopes.png`, `time_stability_r2.png`. |
| `energy_peak_time_series_analysis.py` | Computes total, peak, midrange, and high-k energy proxies over time. | Selected spectrum folders. | `energy_peak_time_series_summary.csv`, `energy_total_vs_time.png`, `peak_mode_energy_vs_time.png`, `midrange_energy_vs_time.png`, `high_k_energy_vs_time.png`. |
| `peak_masked_spectrum_analysis.py` | Performs peak-masked normalized residual spectral analysis. | Selected spectrum folders. | `peak_masked_slope_summary.csv`, `peak_masked_time_stability.csv`, `peak_masked_normalized_spectra.png`, `peak_masked_slope_vs_time.png`. |
| `forcing_m3_validation_analysis.py` | Validation analysis for forcing-mode 3 and combined strategy cases. | Forcing redesign / combined strategy output folders. | Per-case validation summaries, time series, plots inside analysis folders. |
| `compare_validated_runs.py` | Consolidates validated run metrics into comparison artifacts. | Existing validation CSVs and fallback root artifacts. | `validated_run_comparison.csv`, `validated_run_comparison.md`, `validated_run_tradeoff_plot.png`. |
| `plot_spectrum_evolution.py` | Older spectrum evolution plotter. | `outputs/spectrum_k_*.npy`, `outputs/spectrum_bins.npy`. | Spectrum evolution plot. |
| `plot_time_averaged_spectrum.py` | Older time-averaged spectrum plotter. | `outputs/spectrum_k_*.npy`, `outputs/spectrum_bins.npy`. | Time-averaged spectrum plot. |
| `plot_phase_map.py` | Phase-map plotting helper. | `phase_map.csv`. | Phase-map figure. |
| `collapse.py` | Collapse figure generator. | `phase_map.csv` or related sweep data. | `chi_collapse.png`. |

## 4. Current Reports / Documentation Files

| File | Role |
|---|---|
| `experiment_log.md` | Chronological run log, run metadata, current status, and interpretation checkpoints. |
| `project_state.md` | Current project-state summary and decision checkpoint. |
| `evidence_summary.md` | Diagnostic evidence chain and source artifact table. |
| `lowk_drag_comparison.md` | Low-k drag comparison checkpoint. |
| `forcing_redesign_comparison.md` | Forcing redesign and combined strategy comparison checkpoint. |
| `research_checkpoint_report.md` | Short checkpoint report summarizing current evidence and recommendations. |
| `technical_report_draft.md` | Formal technical report draft. |
| `validated_run_comparison.md` | Generated comparison Markdown from `compare_validated_runs.py`. |
| `shortcuts.md` | Empty or placeholder document. |

## 5. Current Comparison Artifacts

| Artifact | Role |
|---|---|
| `compare_validated_runs.py` | Read-only consolidation script for validated run comparison. |
| `validated_run_comparison.csv` | Generated comparison table for Runs 004, 009, 011, 012, and 013. |
| `validated_run_comparison.md` | Generated Markdown summary for validated run comparison. |
| `validated_run_tradeoff_plot.png` | Generated tradeoff plot: best-window total energy growth vs compensated CV. |

## 6. Current Root Diagnostic CSV/PNG Artifacts

Root-level diagnostic CSV files include:

| CSV | Role |
|---|---|
| `time_stability_summary.csv` | Time-indexed slope/R^2 summary. |
| `energy_peak_time_series_summary.csv` | Total, peak, midrange, and high-k energy time-series summary. |
| `energy_partition_fractions.csv` | Peak, midrange, and high-k energy fractions. |
| `peak_masked_slope_summary.csv` | Peak-masked residual slope summary. |
| `peak_masked_time_stability.csv` | Time-indexed peak-masked slope stability data. |
| `compensated_peak_masked_summary.csv` | Compensated spectrum plateau metrics. |
| `stationarity_window_summary.csv` | Selected stationarity-window summary. |
| `stationarity_window_candidates.csv` | Candidate stationarity-window table. |
| `window_local_residual_budget.csv` | Window-local residual energy budget. |
| `window_sensitivity_summary.csv` | Time-window and fit-range sensitivity ensemble. |
| `residual_exponent_uncertainty.csv` | Residual exponent uncertainty summary. |
| `residual_signal_floor_summary.csv` | Signal-floor / numerical significance analysis. |
| `shell_support_summary.csv` | Shell-support / bin-population analysis. |
| `leave_one_shell_out_summary.csv` | Leave-one-shell-out fit influence analysis. |
| `phase_map.csv` | Older phase-map data. |
| `validated_run_comparison.csv` | Current validated run comparison artifact. |

Root-level diagnostic PNG files include:

| PNG | Role |
|---|---|
| `time_stability_slopes.png` | Slope vs saved spectrum index. |
| `time_stability_r2.png` | R^2 vs saved spectrum index. |
| `energy_total_vs_time.png` | Total energy proxy over time. |
| `peak_mode_energy_vs_time.png` | Peak-mode energy over time. |
| `midrange_energy_vs_time.png` | Midrange energy over time. |
| `high_k_energy_vs_time.png` | High-k energy over time. |
| `energy_partition_fractions.png` | Energy partition fraction plot. |
| `peak_masked_normalized_spectra.png` | Peak-masked normalized spectra. |
| `peak_masked_slope_vs_time.png` | Peak-masked slope over time. |
| `compensated_peak_masked_over_time.png` | Compensated spectra over time. |
| `compensated_peak_masked_late_mean.png` | Late-time compensated mean spectra. |
| `compensated_plateau_quality_vs_time.png` | Compensated plateau-quality time series. |
| `stationarity_window_spectrum.png` | Window-averaged residual spectrum. |
| `stationarity_window_compensated.png` | Window-averaged compensated spectrum. |
| `stationarity_window_diagnostics.png` | Stationarity-window diagnostic figure. |
| `window_local_residual_budget.png` | Window-local residual budget plot. |
| `window_sensitivity_heatmap_slope.png` | Window sensitivity slope heatmap. |
| `window_sensitivity_heatmap_r2.png` | Window sensitivity R^2 heatmap. |
| `window_sensitivity_heatmap_cv.png` | Window sensitivity CV heatmap. |
| `residual_exponent_uncertainty.png` | Residual exponent uncertainty plot. |
| `residual_signal_floor_spectrum.png` | Residual spectrum with floor estimate. |
| `residual_signal_floor_ratios.png` | Signal-to-floor ratios. |
| `shell_mode_counts.png` | Shell population counts. |
| `shell_sum_vs_shell_mean_spectrum.png` | Shell-sum vs shell-mean comparison. |
| `leave_one_shell_out_slope_change.png` | Leave-one-out slope change plot. |
| `leave_one_shell_out_r2_change.png` | Leave-one-out R^2 change plot. |
| `validated_run_tradeoff_plot.png` | Validated run tradeoff visualization. |
| `chi_collapse.png` | Older collapse figure. |
| `test.png` | Older / test image. |

## 7. Output Folders That Must Remain Fixed

Do not move or rename the following output folders during initial architecture cleanup:

| Folder | Role |
|---|---|
| `outputs_spectra_refined/` | Refined sweep outputs, including Run 004. |
| `outputs_forcing_redesign/` | Forcing redesign production outputs and analysis folders. |
| `outputs_combined_strategy/` | Combined forcing-plus-drag outputs and analysis folders. |
| `outputs_lowk_drag_production/` | Low-k drag production outputs and analysis folders. |
| `outputs_lowk_drag_kmax_tuning/` | Low-k drag cutoff-tuning outputs and analysis folders. |
| `outputs_lowk_drag_refine/` | Medium low-k drag refinement outputs. |
| `outputs_lowk_drag_pilot/` | Short low-k drag pilot outputs. |
| `outputs_drag_pilot/` | Short global-drag pilot outputs. |
| `outputs_drag_pilot_stronger/` | Stronger global-drag pilot outputs. |
| `outputs_spectra_full/` | Earlier full spectral sweep outputs. |
| `outputs_spectra_pilot/` | Earlier pilot sweep outputs. |
| `outputs_spectra_smoke/` | Smoke-test outputs. |
| `outputs_nu_0.001/` | Earlier baseline viscosity output. |
| `outputs_spectra/` | Earlier spectrum output folder. |
| `outputs/` | Older default output folder. |

These folders are referenced directly or indirectly by reports, scripts, and generated artifacts. Keeping them fixed preserves traceability.

## 8. Scripts and Expected Inputs / Outputs

| Script | Expected inputs | Expected outputs | Notes |
|---|---|---|---|
| `solver.py` | CLI parameters for grid, dt, viscosity, forcing, drag, output folder. | Spectrum files such as `spectrum_bins.npy`, `spectrum_k_*.npy`, and metadata/log outputs. | Solver should stay in root. |
| `run_spectral_sweep.py` | Solver parameters, viscosity values, forcing values, root output folder. | Sweep output folders, `sweep_log.csv`, optional sweep summary/plots. | Calls `solver.py`; path-sensitive. |
| `fit_spectral_slope.py` | One or more spectrum folders with `spectrum_bins.npy` and `spectrum_k_*.npy`. | Fit summary CSVs and comparison plots. | Major analysis tool; should be kept stable. |
| `time_stability_analysis.py` | Spectrum folders for candidate refined runs. | Time-stability CSV and slope/R^2 plots. | Current root-level output paths. |
| `energy_peak_time_series_analysis.py` | Spectrum folders for selected runs. | Energy time-series CSV and energy plots. | Current root-level output paths. |
| `peak_masked_spectrum_analysis.py` | Spectrum folders and candidate fit windows. | Peak-masked CSVs and plots. | Current root-level output paths. |
| `forcing_m3_validation_analysis.py` | Forcing redesign / combined strategy output folders. | Per-run analysis folders and validation summaries. | Current production validation workhorse for m=3 cases. |
| `compare_validated_runs.py` | Existing validation summaries plus Run 004 fallback artifacts. | `validated_run_comparison.csv`, `validated_run_comparison.md`, `validated_run_tradeoff_plot.png`. | Current comparison checkpoint script. |

## 9. Reports and Referenced Artifacts

| Report | Known referenced artifacts |
|---|---|
| `technical_report_draft.md` | Checkpoint docs, validated comparison artifacts, Run 004 root diagnostics, forcing redesign and combined strategy summaries. |
| `research_checkpoint_report.md` | `compare_validated_runs.py`, `validated_run_comparison.csv`, `validated_run_comparison.md`, `validated_run_tradeoff_plot.png`. |
| `validated_run_comparison.md` | Generated by `compare_validated_runs.py`; references primary combined summary plus Run 004 fallback artifacts. |
| `evidence_summary.md` | Run 004 validation artifacts, low-k drag production summaries, forcing redesign summaries, combined strategy summaries. |
| `project_state.md` | Run 004, low-k drag, forcing redesign, and combined strategy checkpoints. |
| `forcing_redesign_comparison.md` | Forcing redesign and combined strategy analysis folders and summary CSVs. |
| `lowk_drag_comparison.md` | Low-k drag production comparison artifacts. |
| `experiment_log.md` | Chronological run folders, analysis folders, and interpretation checkpoints. |

Do not update report links until a target structure is approved and copied artifacts have been verified.

## 10. Proposed Target Folder Structure

Proposed future structure:

```text
Raj-Sanghera-Project/
  solver.py
  run_spectral_sweep.py

  analysis/
    README.md
    scripts/
      fit_spectral_slope.py
      time_stability_analysis.py
      energy_peak_time_series_analysis.py
      peak_masked_spectrum_analysis.py
      forcing_m3_validation_analysis.py
      compare_validated_runs.py
    lib/
      spectra_io.py
      fitting.py
      diagnostics.py
      plotting.py

  reports/
    technical_report_draft.md
    research_checkpoint_report.md
    evidence_summary.md
    project_state.md
    experiment_log.md
    forcing_redesign_comparison.md
    lowk_drag_comparison.md

  comparisons/
    validated_run_comparison.csv
    validated_run_comparison.md
    validated_run_tradeoff_plot.png

  analysis_outputs/
    run004_validation/
    checkpoint_root_artifacts/

  outputs*/
    unchanged raw and per-run output folders
```

This target structure should be reached gradually. The first implementation step should copy files into the new structure while keeping root originals in place.

## 11. Copy-First Cleanup Strategy

Recommended cleanup strategy:

1. Create target folders only after this manifest is approved.
2. Copy reports into `reports/`.
3. Copy comparison artifacts into `comparisons/`.
4. Copy analysis scripts into `analysis/scripts/`.
5. Copy root Run 004 diagnostic CSV/PNG artifacts into `analysis_outputs/run004_validation/`.
6. Keep root originals in place until reports and scripts are updated and verified.
7. Add a lightweight `analysis/README.md` explaining that copied scripts may still assume project-root execution.
8. Update script path handling only after copy layout is reviewed.
9. Update report links only after path handling is stable.
10. Move files only after the copy-based structure has been verified.

Do not move output folders. Do not rename output folders.

## 12. Risks of Moving Files

Main risks:

- Reports currently use root-relative artifact paths.
- `compare_validated_runs.py` reads and writes root-relative paths.
- Some analysis scripts assume they run from the project root.
- `run_spectral_sweep.py` calls `solver.py` by root-relative name.
- `fit_spectral_slope.py` may be used by sweep workflows and should not be moved before compatibility is checked.
- Moving root diagnostic CSV/PNG files could break Run 004 traceability.
- Moving or renaming output folders would break many documented source references.
- Moving files before adding project-root-aware path handling could make old commands fail.

## 13. Safe Next Steps

Recommended safe next steps:

1. Review this manifest for accuracy.
2. Approve or revise the proposed target structure.
3. If approved, create empty target folders:
   - `analysis/scripts/`
   - `analysis/lib/`
   - `reports/`
   - `comparisons/`
   - `analysis_outputs/run004_validation/`
4. Copy files into the new folders without deleting or moving originals.
5. Create a `reports/README.md` and `analysis/README.md` explaining that root originals remain authoritative during transition.
6. Run no simulations during cleanup.
7. Do not modify `solver.py`.
8. Do not update report links until copied artifacts are verified.
9. After copy verification, plan a second pass for path-safe script refactoring.

This manifest is a planning and freeze document. It does not change scientific claims.
