# Literature Roadmap for Preprint Manuscript

## Purpose

This roadmap identifies literature areas needed before converting the current preprint outline into a full manuscript. It does not provide citations, does not invent references, and does not claim literature support until specific references are identified and checked.

The manuscript's central claim remains limited to residual `k^-3`-like spectral validation in selected peak-masked windows. It does not claim a fully stationary enstrophy cascade, a new turbulence law, or a proof-level result.

Primary source documents for this roadmap:

- `preprint_manuscript_outline.md`
- `technical_report_draft.md`
- `research_checkpoint_report.md`

## 1. 2D Turbulence and Enstrophy Cascade Theory

What literature is needed:

- Foundational work on two-dimensional turbulence.
- Theoretical descriptions of inverse energy transfer and forward enstrophy transfer.
- Reviews or textbooks that define the expected phenomenology and limitations of ideal cascade arguments.

Why it matters:

- Provides the physical context for why a `k^-3`-like residual spectrum is interesting.
- Helps frame the distinction between an observed spectral shape and a validated cascade.
- Establishes why 2D turbulence differs from 3D turbulence.

What claim it can support:

- A `k^-3` spectral form is historically associated with enstrophy-cascade phenomenology in 2D turbulence.
- A forced 2D system can exhibit scale-transfer behavior that motivates spectral diagnostics.

What claim it cannot support:

- It cannot prove that this project's simulations have achieved a stationary enstrophy cascade.
- It cannot justify treating a residual fitted slope as full-system cascade evidence.
- It cannot remove the need for stationarity, flux, and energy-partition diagnostics.

Suggested search terms:

- `two-dimensional turbulence enstrophy cascade theory`
- `2D turbulence inverse energy cascade forward enstrophy cascade`
- `Kraichnan 2D turbulence enstrophy cascade`
- `Batchelor two dimensional turbulence spectrum`
- `2D turbulence review enstrophy cascade`

## 2. Kraichnan-Batchelor `k^-3` Scaling Context

What literature is needed:

- Original or canonical discussions of `k^-3` scaling in the 2D enstrophy cascade.
- Later theoretical refinements involving logarithmic corrections or finite-domain effects.
- Literature distinguishing spectral slope observation from flux-verified cascade behavior.

Why it matters:

- The manuscript uses `k^-3` as a reference exponent, so the origin and interpretation of that reference must be cited carefully.
- It helps prevent overclaiming from slope agreement alone.

What claim it can support:

- The `-3` exponent is a relevant reference value for interpreting residual spectra in 2D turbulence.
- Compensated `k^3 E(k)` plots are a standard way to inspect plateau-like consistency with a `k^-3` form.

What claim it cannot support:

- It cannot prove the project's residual spectra are a true inertial or enstrophy-cascade range.
- It cannot validate the result without stationarity, flux, and robustness diagnostics.
- It cannot make a finite-resolution, window-local result equivalent to an asymptotic scaling law.

Suggested search terms:

- `Kraichnan Batchelor k^-3 spectrum`
- `2D enstrophy cascade k^-3 logarithmic correction`
- `compensated spectra k^3 E(k) enstrophy cascade`
- `finite size effects k^-3 spectrum two dimensional turbulence`
- `spectral slope versus flux enstrophy cascade`

## 3. Forced-Dissipative 2D Navier-Stokes Simulations

What literature is needed:

- Numerical studies of forced-dissipative 2D Navier-Stokes turbulence.
- Studies using deterministic, random, narrow-band, or spectral forcing.
- Work discussing transient versus statistically stationary regimes in forced 2D simulations.

Why it matters:

- The project uses forced simulations and compares forcing amplitude, forcing mode, and low-k drag.
- The manuscript needs context for why forcing design and damping strategy affect stationarity and spectral interpretation.

What claim it can support:

- Forced-dissipative simulations are a standard computational setting for studying 2D turbulence.
- Stationarity and forcing-scale energy accumulation are known practical concerns in such simulations.

What claim it cannot support:

- It cannot show that this project's specific solver, forcing, or parameter choices reproduce established stationary regimes.
- It cannot replace direct validation of this project's output data.

Suggested search terms:

- `forced dissipative two dimensional Navier Stokes turbulence simulation`
- `spectral forcing 2D turbulence simulation`
- `deterministic forcing two dimensional turbulence`
- `random forcing 2D Navier Stokes turbulence`
- `statistical stationarity forced 2D turbulence simulation`

## 4. Large-Scale Friction / Ekman Drag in 2D Turbulence

What literature is needed:

- Studies using linear drag, Ekman friction, hypofriction, or large-scale damping in 2D turbulence.
- Literature on controlling inverse-cascade accumulation at large scales.
- Comparisons of global drag versus scale-selective low-k damping.

Why it matters:

- The project added global drag and low-k selective drag to reduce low-k/peak energy accumulation.
- Runs 011-013 show a stationarity/residual-cleanliness tradeoff; literature can help frame this as a known modeling choice rather than an arbitrary tuning exercise.

What claim it can support:

- Large-scale friction is a standard mechanism for controlling low-k energy growth in forced 2D turbulence.
- Drag can improve stationarity while also affecting spectral structure.

What claim it cannot support:

- It cannot prove that the chosen low-k drag parameters are physically optimal.
- It cannot claim that low-k drag validates a stationary enstrophy cascade in this project.
- It cannot erase the severe peak-domination caveat.

Suggested search terms:

- `Ekman friction two dimensional turbulence`
- `linear drag forced 2D turbulence`
- `large scale friction enstrophy cascade simulation`
- `hypofriction 2D turbulence spectral simulation`
- `low wavenumber drag two dimensional turbulence`

## 5. Spectral Methods and Shell Averaging

What literature is needed:

- References on pseudo-spectral methods for incompressible flow or vorticity formulations.
- Literature or numerical-methods texts on Fourier shell averaging and radial spectra.
- Discussions of shell population, binning, and isotropic spectra in finite grids.

Why it matters:

- The project analyzes spectra using radial bins/shells and performs shell-support checks.
- The manuscript must explain why shell population matters and why sparse-bin geometry was checked.

What claim it can support:

- Fourier spectral methods and radial shell spectra are standard tools for turbulence analysis.
- Shell population and binning choices can affect spectral estimates and should be checked.

What claim it cannot support:

- It cannot guarantee that a fitted exponent is physically meaningful without additional diagnostics.
- It cannot remove finite-grid limitations.
- It cannot make shell-summed and shell-mean spectra interchangeable without interpretation.

Suggested search terms:

- `pseudo-spectral method 2D Navier Stokes vorticity`
- `Fourier shell averaging turbulence spectrum`
- `radial energy spectrum shell binning finite grid`
- `spectral methods incompressible Navier Stokes turbulence`
- `isotropic spectrum shell population discrete Fourier modes`

## 6. Compensated Spectra and Finite-Resolution Caveats

What literature is needed:

- Work using compensated spectra to assess power-law ranges.
- Studies warning about finite inertial ranges, bottlenecks, noise floors, and fitting artifacts.
- Literature on uncertainty in spectral exponent fitting.

Why it matters:

- The project uses compensated `k^3 E(k)` spectra and compensated CV as a plateau-quality diagnostic.
- The manuscript needs support for why compensated spectra are useful and why they are not sufficient by themselves.

What claim it can support:

- A flatter compensated spectrum is consistent with a power-law-like range over the examined window.
- Finite-resolution and finite-time simulations require cautious interpretation of fitted slopes.

What claim it cannot support:

- It cannot turn a finite compensated shoulder into proof of an asymptotic inertial range.
- It cannot eliminate the need for sensitivity, uncertainty, and signal-floor checks.
- It cannot validate full stationarity.

Suggested search terms:

- `compensated energy spectrum turbulence finite inertial range`
- `spectral exponent uncertainty turbulence`
- `finite resolution effects turbulence spectrum`
- `bottleneck effect compensated spectrum turbulence`
- `power law fitting turbulence spectra caveats`

## 7. Stationarity and Flux Diagnostics

What literature is needed:

- Studies defining statistical stationarity in forced turbulence simulations.
- Literature on energy and enstrophy flux diagnostics in 2D turbulence.
- Work connecting spectral slopes to flux plateaus and transfer diagnostics.

Why it matters:

- The current manuscript must state that residual-shape validation is not the same as full-system stationarity.
- The strongest missing validation step is likely flux or transfer diagnostics, not another slope-only comparison.

What claim it can support:

- Stationarity requires more than a stable fitted spectral shape.
- Flux diagnostics are important for validating cascade behavior.
- Energy partition and time-window behavior are relevant safeguards against overinterpretation.

What claim it cannot support:

- It cannot claim this project has already demonstrated a stationary cascade unless project-specific flux or stationarity evidence is added later.
- It cannot replace the documented caveat that peak domination remains severe.

Suggested search terms:

- `statistical stationarity forced turbulence simulation diagnostics`
- `energy flux enstrophy flux 2D turbulence`
- `spectral energy transfer diagnostics two dimensional turbulence`
- `enstrophy flux plateau 2D turbulence simulation`
- `stationary enstrophy cascade numerical evidence`

## 8. Background-Only vs Directly Relevant Papers

Background-only literature:

- Broad turbulence reviews.
- General introductions to 2D turbulence phenomenology.
- General spectral methods references.
- Papers that explain `k^-3` theory without matching the project's numerical setup.

How to use background-only papers:

- Use them to motivate the reference exponent and diagnostic vocabulary.
- Use them to define standard concepts such as enstrophy cascade, inverse energy transfer, and compensated spectra.
- Do not use them as evidence that this project has achieved a stationary cascade.

Directly relevant literature:

- Forced-dissipative 2D Navier-Stokes simulations with spectra, forcing, drag, and stationarity diagnostics.
- Papers using large-scale friction or Ekman drag to control low-k energy accumulation.
- Papers using spectral flux diagnostics to validate enstrophy-cascade behavior.
- Papers discussing finite-resolution limitations, shell averaging, and compensated-spectrum interpretation.

How to use directly relevant papers:

- Compare diagnostic standards against the project's validation chain.
- Identify what additional evidence would be needed before making stronger cascade claims.
- Support the manuscript's conservative framing: residual spectral-shape validation is meaningful, but not sufficient for full cascade validation.

What neither category should be used to claim:

- That the current project proves a fully stationary enstrophy cascade.
- That Run 004, Run 009, Run 011, Run 012, or Run 013 establishes a new law.
- That severe peak domination can be ignored.

Suggested search terms:

- `forced dissipative 2D turbulence Ekman drag enstrophy cascade`
- `2D turbulence spectral flux validation simulation`
- `finite resolution compensated spectra 2D turbulence`
- `large scale friction inverse cascade numerical simulation`
- `stationary enstrophy cascade evidence spectral flux`

## 9. Practical Literature Review Workflow

Recommended sequence:

1. Identify 3-5 foundational papers or review sources for 2D turbulence and enstrophy-cascade theory.
2. Identify 3-5 numerical forced-dissipative 2D simulation papers with clear stationarity or flux diagnostics.
3. Identify 2-4 references on Ekman drag or large-scale friction.
4. Identify 2-4 references on spectral methods, shell averaging, compensated spectra, or finite-range caveats.
5. Only after references are verified, add citations to the manuscript draft.

Evidence rule:

- If a paper is not actually read and verified, do not cite it as support.
- If a paper supports only background theory, label it as background in the manuscript notes.
- If a paper directly informs diagnostics or interpretation, connect it to the specific diagnostic it supports.

## 10. Manuscript Integration Notes

Where references will likely be needed:

- Introduction: 2D turbulence, inverse energy transfer, enstrophy cascade, and the `k^-3` reference.
- Methods: spectral solver context, shell averaging, and compensated spectra.
- Results interpretation: finite-resolution caveats, peak masking, and why slope agreement alone is insufficient.
- Limitations: stationarity, flux diagnostics, and why the manuscript avoids a full cascade claim.

Current claim boundary:

- The manuscript may claim that the project documents a robust residual `k^-3`-like spectral shape in selected peak-masked windows.
- The manuscript may not claim a fully stationary enstrophy cascade.
- The manuscript may not claim a new turbulence law.
- The manuscript must preserve the caveat that peak domination remains severe.
