# Citation Integration Plan

## Purpose

This plan maps verified literature sources to the preprint manuscript outline. It is a planning document only. It does not add citations to the manuscript and does not strengthen the project claims.

Current claim boundary:

- The central project claim is residual `k^-3`-like spectral validation in selected peak-masked windows.
- No fully stationary enstrophy cascade is claimed.
- No new turbulence law is claimed.
- Peak domination remains severe.
- The current project does not yet have full spectral flux validation.

## Section 1: Introduction

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Boffetta & Ecke 2012, "Two-Dimensional Turbulence" | Modern review context for 2D turbulence, dual cascade, energy/enstrophy flux language, and why `k^-3` is a relevant comparison. | Claiming this project has a stationary enstrophy cascade. | Background | High |
| Tabeling 2002, "Two-dimensional turbulence: a physicist approach" | Broad context for 2D turbulence, inverse cascade, direct enstrophy cascade, coherent structures, and spectral interpretation. | Supporting any Run 004/009/011/012/013 numerical metric directly. | Background | Medium |
| Kraichnan 1967, "Inertial Ranges in Two-Dimensional Turbulence" | Classical dual-cascade and `k^-3` enstrophy-transfer reference. | Treating a finite residual slope as proof of an inertial range. | Background | High |
| Leith 1968, "Diffusion Approximation for Two-Dimensional Turbulence" | Classical KLB context for inverse-energy and direct-enstrophy inertial ranges. | Validating the finite-window residual exponent measured here. | Background | Medium |
| Batchelor 1969, "Computation of the Energy Spectrum in Homogeneous Two-Dimensional Turbulence" | Classical 2D spectral-theory context and historical `k^-3` comparison. | Claiming the project result is asymptotic, stationary, or energetically dominant. | Background | High |
| Stumpf & Porter 2012, "Critical Truths About Power Laws" | Caution that apparent power laws can be overinterpreted. | Turbulence-specific validation. | Methodological caution | Medium |

Integration note:

- Use the theory sources to explain why `k^-3` is a meaningful reference, not as evidence that the project found a cascade.
- Use power-law caution only to motivate conservative wording, not to replace turbulence-specific diagnostics.

## Section 2: Numerical Model and Production Run Setup

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Canuto et al. 1988, *Spectral Methods in Fluid Dynamics* | Spectral methods as established numerical tools for fluid simulations. | Validating the current solver implementation without a solver audit. | Methodological | High |
| Patterson & Orszag 1971, "Spectral Calculations of Isotropic Turbulence: Efficient Removal of Aliasing Interactions" | Aliasing as a known issue in spectral turbulence calculations. | Claiming this solver is correctly dealiased. | Methodological | Medium |
| Orszag 1971, "On the Elimination of Aliasing..." | Historical high-wavenumber filtering / aliasing-removal context. | Claiming aliasing is controlled in this project unless documented from `solver.py`. | Methodological | Medium |
| Pope 2000, *Turbulent Flows* | General turbulence spectra and Fourier/spectral vocabulary. | Proving this project's compensated spectrum is an inertial range. | Methodological background | Medium |
| Davidson 2015, *Turbulence: An Introduction for Scientists and Engineers* | General spectral-space turbulence vocabulary. | Validating radial shell binning or the residual exponent. | Methodological background | Low |

Integration note:

- If the manuscript discusses dealiasing, include an explicit solver-status caveat: the literature supports why dealiasing matters, not that the current implementation has been audited.
- Do not over-describe numerical methods beyond what is documented.

## Section 3: Diagnostic and Validation Methodology

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Clauset, Shalizi & Newman 2009, "Power-Law Distributions in Empirical Data" | Fitted exponents depend on range selection, noise, and goodness-of-fit assumptions; robustness checks are important. | Serving as a complete turbulence-spectrum fitting method. | Methodological caution | High |
| Stumpf & Porter 2012, "Critical Truths About Power Laws" | Cautious treatment of apparent power-law behavior. | Directly validating a turbulence spectrum. | Methodological caution | Medium |
| Pope 2000, *Turbulent Flows* | Power-law spectra and compensated spectra as standard interpretive tools. | Claiming a finite compensated shoulder proves an inertial range. | Methodological | Medium |
| Davidson 2015, *Turbulence* | Spectral-space diagnostics vocabulary. | Project-specific shell-binning validation. | Methodological | Low |
| Boffetta 2007, "Energy and enstrophy fluxes..." | Flux diagnostics as a stronger cascade-validation standard. | Implying this project has computed fluxes. | Limitation/future-work | High |
| Rivera et al. 2003, "Energy and Enstrophy Transfer..." | Direct energy/enstrophy transfer measurements as diagnostics beyond spectra. | Claiming this project has measured flux transfer. | Limitation/future-work | Medium |

Integration note:

- Use these references to justify the validation chain: slope fitting is necessary but not sufficient; sensitivity, uncertainty, compensated spectra, and flux caveats matter.

## Section 4: Baseline Result: Run 004 No-Drag Reference

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Kraichnan 1967 | The `-3` comparison exponent is theoretically meaningful in 2D turbulence. | Treating Run 004 as a stationary enstrophy cascade. | Background | High |
| Batchelor 1969 | Historical context for 2D energy spectra and `k^-3` theory. | Claiming Run 004 is asymptotic or energetically dominant. | Background | High |
| Boffetta & Ecke 2012 | Review context for interpreting residual `k^-3`-like behavior cautiously. | Claiming full-system stationarity. | Background / limitation | High |
| Clauset, Shalizi & Newman 2009 | Need for fit-range sensitivity and uncertainty bands. | Replacing turbulence-specific physical validation. | Methodological caution | Medium |
| Boffetta 2007 | Flux diagnostics as the missing stronger cascade test. | Claiming flux validation for Run 004. | Limitation/future-work | High |
| Vallgren & Lindborg 2011 | Energy growth can coexist with quasi-stationary enstrophy behavior in forced 2D simulations. | Claiming Run 004's energy growth is acceptable or cascade-validating. | Limitation/future-work | High |

Integration note:

- Place references around interpretation, not in the numerical-result table.
- The result table should remain sourced to project artifacts, not literature.

## Section 5: Forcing Redesign Results

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Vallgren & Lindborg 2011 | Forcing scale matters in forced 2D enstrophy-cascade simulations. | Claiming Run 009 reproduces their result. | Background / limitation | High |
| Boffetta & Ecke 2012 | Review-level context for forcing, fluxes, friction, and cascade phenomenology. | Supporting Run 009 metrics directly. | Background | Medium |
| Boffetta 2007 | Flux diagnostics needed for stronger double-cascade validation. | Claiming the forcing redesign has flux support. | Limitation/future-work | High |
| Eyink 1996 | Stationarity and invariant balances matter in interpreting 2D turbulence. | Certifying the redesigned forcing cases as stationary. | Limitation/future-work | Medium |

Integration note:

- Use these references to motivate why forcing redesign was scientifically reasonable, while keeping all case-specific conclusions tied to project diagnostics.

## Section 6: Low-k Drag and Combined Strategy Results

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Sukoriansky, Galperin & Chekhlov 1999 | Large-scale energy condensation and coherent-vortex formation are known issues; large-scale drag representation matters. | Claiming this project's peak domination has been solved. | Background / methodological context | High |
| Tsang 2010 | Large-scale dissipation choices, including scale-selective drag, can materially change forced 2D turbulence statistics. | Claiming Run 013 is physically optimal. | Methodological / limitation | High |
| Blackbourn & Tran 2011 | Friction affects forced 2D Navier-Stokes dynamics and is not a neutral intervention. | Claiming drag validates stationarity or a cascade. | Limitation | High |
| Vallgren & Lindborg 2011 | Large-scale drag and forcing scale affect coherent structures and enstrophy-cascade behavior. | Directly validating the combined strategy. | Background / limitation | Medium |
| Eyink 1996 | Infrared dissipation and energy balance matter for stationarity. | Certifying low-k drag cases as stationary. | Limitation/future-work | Medium |

Integration note:

- These are the strongest references for explaining why low-k drag was considered and why the resulting stationarity/residual-cleanliness tradeoff must be interpreted carefully.

## Section 7: Comparative Results Across Validated Cases

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Sandve et al. 2013 | Traceable computational workflows and reproducible analysis artifacts are good practice. | Validating any physical conclusion. | Methodological / reporting | Medium |
| Wilson et al. 2014 | Scientific software should be organized, documented, and version controlled. | Validating the solver or spectra. | Methodological / reporting | Medium |
| Clauset, Shalizi & Newman 2009 | Sensitivity and uncertainty are important when comparing fitted exponents. | Proving a power law in the turbulence data. | Methodological caution | Medium |
| Boffetta 2007 | Flux diagnostics remain a standard for stronger cascade comparison. | Claiming any listed run has flux validation. | Limitation/future-work | High |

Integration note:

- This section should mostly cite project artifacts. Literature should frame why the comparison is cautious and reproducible, not why one case is physically superior.

## Section 8: Interpretation

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Boffetta & Ecke 2012 | Broad dual-cascade context and flux/stationarity caution. | Claiming the residual result is a validated cascade. | Background / limitation | High |
| Tran 2007 | Caution around inertial-range scaling laws in forced 2D Navier-Stokes turbulence. | Validating the project-specific residual window. | Limitation | Medium |
| Boffetta 2007 | Stronger cascade claims require flux evidence. | Claiming current flux evidence exists. | Limitation/future-work | High |
| Vallgren & Lindborg 2011 | Distinguishing energy growth from enstrophy-related behavior in forced 2D simulations. | Treating energy growth as harmless for this project. | Limitation | High |
| Stumpf & Porter 2012 | General caution around overinterpreting apparent power laws. | Replacing turbulence-specific interpretation. | Methodological caution | Low |

Integration note:

- This section should use references sparingly. The main interpretive claims should come from project diagnostics.

## Section 9: Limitations and Non-Claims

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Boffetta 2007 | Flux diagnostics as necessary for stronger double-cascade claims. | Claiming flux validation has been performed. | Limitation/future-work | High |
| Eyink 1996 | Stationarity and invariant balances are central to 2D cascade theory. | Certifying stationarity in current runs. | Limitation/future-work | High |
| Rivera et al. 2003 | Direct transfer/flux diagnostics reveal behavior beyond spectra. | Claiming transfer diagnostics exist for this project. | Limitation/future-work | Medium |
| Xiao et al. 2009 | Spectral and local flux analysis can diagnose inverse-cascade mechanisms. | Claiming the project has local flux analysis. | Limitation/future-work | Medium |
| Oberkampf & Trucano 2002 | Verification/validation requires explicit uncertainty and assumptions. | Claiming formal validation of the project. | Methodological limitation | Medium |
| ASME V&V 20-2009 | CFD validation language and uncertainty discipline. | Implying formal ASME compliance. | Methodological limitation | Low |

Integration note:

- This is the best place to cite flux/stationarity sources. The language should be "future work requires..." rather than "our result demonstrates..."

## Section 10: Reproducibility and Artifact Index

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Sandve et al. 2013 | Traceable computational research practices. | Validating turbulence physics. | Methodological / reporting | High |
| Wilson et al. 2014 | Version control, documentation, and scientific software practices. | Proving the solver is correct. | Methodological / reporting | High |
| Oberkampf & Trucano 2002 | Difference between verification, validation, and uncertainty. | Claiming the project is fully V&V complete. | Methodological / reporting | Medium |
| ASME V&V 20-2009 | Formal CFD V&V language and uncertainty framing. | Formal compliance without following the standard. | Methodological / reporting | Low |

Integration note:

- Use these references to justify why the project includes committed scripts, curated comparison outputs, documentation checkpoints, and claim boundaries.

## Section 11: Recommended Next Work

| Reference | May support | Must not be used for | Support type | Priority |
|---|---|---|---|---|
| Boffetta 2007 | Future flux diagnostics for cascade validation. | Claiming current flux validation. | Future-work support | High |
| Rivera et al. 2003 | Future direct energy/enstrophy transfer diagnostics. | Claiming transfer diagnostics already performed. | Future-work support | Medium |
| Xiao et al. 2009 | Future spectral/local flux analysis. | Applying inverse-cascade mechanism conclusions directly to current runs. | Future-work support | Medium |
| Canuto et al. 1988 | Future solver/numerical-method verification documentation. | Claiming current solver audit complete. | Future-work support | Medium |
| Oberkampf & Trucano 2002 | Future verification/validation and uncertainty work. | Claiming formal validation now. | Future-work support | Medium |

Integration note:

- Future work should include flux diagnostics and solver-output audit before any stronger cascade claim.

## Cross-Section Citation Priorities

Highest priority:

- Boffetta & Ecke 2012
- Kraichnan 1967
- Batchelor 1969
- Boffetta 2007
- Vallgren & Lindborg 2011
- Canuto et al. 1988
- Clauset, Shalizi & Newman 2009
- Sandve et al. 2013

Medium priority:

- Tabeling 2002
- Leith 1968
- Tran 2007
- Eyink 1996
- Rivera et al. 2003
- Tsang 2010
- Sukoriansky, Galperin & Chekhlov 1999
- Patterson & Orszag 1971
- Orszag 1971
- Wilson et al. 2014
- Oberkampf & Trucano 2002

Lower priority or use sparingly:

- Davidson 2015
- Pope 2000
- ASME V&V 20-2009
- Stumpf & Porter 2012
- Xiao et al. 2009

## Citation Use Guardrails

- Cite literature for context, method, or limitation only.
- Cite project artifacts for project-specific numerical metrics.
- Do not cite theory papers as evidence for stationarity.
- Do not cite flux papers as evidence for flux validation unless future project flux diagnostics are actually computed.
- Do not cite numerical-method sources as evidence that `solver.py` is verified unless a solver audit is performed.
- Do not claim a fully stationary enstrophy cascade.
- Do not claim a new turbulence law.
