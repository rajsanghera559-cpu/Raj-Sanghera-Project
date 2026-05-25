# Literature Verification: Flux and Stationarity Diagnostics in 2D Turbulence

## Purpose

This file records targeted citation verification for spectral flux and stationarity diagnostics in 2D turbulence. The focus is on sources that discuss energy flux, enstrophy flux, double-cascade diagnostics, statistical stationarity in forced-dissipative settings, and why spectral slope alone is not sufficient to claim a cascade.

These references should be used to justify future work and limitation language. The current project does not yet have full spectral flux validation. The current supported project claim remains limited to residual `k^-3`-like spectral validation in selected peak-masked windows.

## Verified Sources

### 1. Energy and Enstrophy Fluxes in the Double Cascade of Two-Dimensional Turbulence

- Full citation metadata: Guido Boffetta, "Energy and enstrophy fluxes in the double cascade of two-dimensional turbulence," Journal of Fluid Mechanics, volume 589, pages 253-260, 2007.
- DOI / stable URL: `10.1017/S0022112007008014`; Cambridge Core record: `https://doi.org/10.1017/S0022112007008014`
- Diagnostic discussed: Energy and enstrophy fluxes in high-resolution direct numerical simulations under stationary conditions; joint distribution of energy and enstrophy fluxes.
- What claim it can support: Flux diagnostics are central evidence for double-cascade validation; stationary simulations with extended inertial ranges can be compared against classical Kraichnan theory using flux statistics.
- What claim it cannot support: It cannot imply this project has flux-validated a double cascade, because the current project has not yet computed comparable energy/enstrophy fluxes.
- Relevance to this project's limitation section: Strong support for saying slope and compensated spectra are not enough for a full cascade claim; flux diagnostics remain a necessary future validation step.
- Confidence level: high

### 2. Exact Results on Stationary Turbulence in 2D: Consequences of Vorticity Conservation

- Full citation metadata: Gregory L. Eyink, "Exact results on stationary turbulence in 2D: consequences of vorticity conservation," Physica D: Nonlinear Phenomena, volume 91, issues 1-2, pages 97-142, 1996.
- DOI / stable URL: `10.1016/0167-2789(95)00250-2`; ScienceDirect record: `https://doi.org/10.1016/0167-2789(95)00250-2`
- Diagnostic discussed: Stationary 2D turbulence, energy/enstrophy balance equations, flux directions and magnitudes under assumptions including infrared dissipation and finite mean energy.
- What claim it can support: Statistical stationarity and invariant balance constraints are mathematically central to cascade claims in 2D turbulence; infrared dissipation matters for controlling energy growth.
- What claim it cannot support: It cannot certify that this project's runs satisfy those assumptions or achieve steady-state flux balances.
- Relevance to this project's limitation section: Useful for explaining why the observed low-k/peak energy growth is a serious caveat and why stationarity cannot be inferred from a residual slope.
- Confidence level: high

### 3. The Enstrophy Cascade in Forced Two-Dimensional Turbulence

- Full citation metadata: Andreas Vallgren and Erik Lindborg, "The enstrophy cascade in forced two-dimensional turbulence," Journal of Fluid Mechanics, volume 671, pages 168-183, 2011.
- DOI / stable URL: `10.1017/S0022112010005562`; Cambridge Core record: `https://doi.org/10.1017/S0022112010005562`; KTH DiVA record: `https://www.diva-portal.org/smash/record.jsf?pid=diva2:359537`
- Diagnostic discussed: Forced 2D turbulence with forcing at different wavenumbers; quasi-stationary enstrophy with growing energy in the absence of large-scale drag; enstrophy-cascade spectral behavior.
- What claim it can support: In forced 2D turbulence, enstrophy-related behavior can become quasi-stationary while energy continues to grow, so energy stationarity and enstrophy-cascade diagnostics must be separated.
- What claim it cannot support: It cannot validate this project's residual `k^-3`-like range as a full stationary cascade or show that the project's energy growth is acceptable.
- Relevance to this project's limitation section: Directly relevant to the project's observed split between residual spectral-shape stability and continuing total/peak energy growth.
- Confidence level: high

### 4. Energy and Enstrophy Transfer in Decaying Two-Dimensional Turbulence

- Full citation metadata: M. K. Rivera, W. B. Daniel, S. Y. Chen, and R. E. Ecke, "Energy and Enstrophy Transfer in Decaying Two-Dimensional Turbulence," Physical Review Letters, volume 90, article 104502, 2003.
- DOI / stable URL: `10.1103/PhysRevLett.90.104502`; APS record: `https://doi.org/10.1103/PhysRevLett.90.104502`
- Diagnostic discussed: Direct computation of energy and enstrophy fluxes from velocity and vorticity fields using a filtering technique; comparison with structure-function or spectral analysis.
- What claim it can support: Direct flux measurements provide insight beyond structure functions or spectra; flux diagnostics are useful for distinguishing actual transfer behavior from spectral appearance.
- What claim it cannot support: It cannot support any claim that this project's peak-masked residual spectrum has direct measured flux support.
- Relevance to this project's limitation section: Useful citation for explaining why future flux diagnostics would strengthen or qualify the current residual-spectrum result.
- Confidence level: high

### 5. Physical Mechanism of the Inverse Energy Cascade of Two-Dimensional Turbulence: A Numerical Investigation

- Full citation metadata: Z. Xiao, M. Wan, S. Chen, and G. L. Eyink, "Physical mechanism of the inverse energy cascade of two-dimensional turbulence: a numerical investigation," Journal of Fluid Mechanics, volume 619, pages 1-44, 2009.
- DOI / stable URL: `10.1017/S0022112008004266`; Cambridge Core / LANL metadata record: `https://doi.org/10.1017/S0022112008004266`
- Diagnostic discussed: Direct numerical simulation of steady-state 2D turbulence; mean spectral energy flux; local energy flux through smooth filtering; scale-locality and physical mechanism of inverse energy cascade.
- What claim it can support: Cascade diagnostics can involve both spectral flux and spatially localized flux analysis; a constant spectral flux over a wavenumber range is a stronger cascade indicator than a slope alone.
- What claim it cannot support: It cannot show that this project's residual `k^-3`-like spectrum has a corresponding energy or enstrophy flux plateau.
- Relevance to this project's limitation section: Supports the recommendation that future work should include spectral or coarse-grained flux diagnostics before making stronger cascade claims.
- Confidence level: high

## How These References Should Be Used

Appropriate use:

- Justify why energy and enstrophy flux diagnostics are needed for stronger cascade claims.
- Explain why statistical stationarity and invariant balances matter in forced-dissipative 2D turbulence.
- Support limitation language stating that spectral slope, compensated spectra, and residual-shape validation are not equivalent to full flux-validated cascade evidence.
- Motivate future analysis: compute energy/enstrophy transfer or flux diagnostics for the strongest candidate cases.

Inappropriate use:

- Do not cite these references as evidence that this project has already demonstrated energy or enstrophy flux plateaus.
- Do not use them to claim Run 004, Run 009, Run 011, Run 012, or Run 013 is a fully stationary enstrophy cascade.
- Do not use them to turn a peak-masked residual slope into a cascade claim.
- Do not use them to claim that low-k/peak domination is acceptable without additional evidence.

## Sources Considered but Not Added in This Pass

- Boffetta and Ecke, "Two-Dimensional Turbulence," Annual Review of Fluid Mechanics, 2012. Already verified in the 2D theory notes and useful as a review source, but not included here to keep this pass focused on flux/stationarity-specific sources.
- Boffetta and Musacchio, "Evidence for the double cascade scenario in two-dimensional turbulence," Physical Review E 82, 016307, 2010. Strong candidate for a broader double-cascade literature pass; not needed in this five-source targeted flux/stationarity list.

## Still Needed After This Pass

- A direct future-work plan for computing spectral energy/enstrophy fluxes from this project's saved fields, if sufficient fields are available.
- If only spectra are saved, a note identifying what additional solver outputs would be needed for true flux diagnostics.
- A solver/output audit to determine whether velocity/vorticity fields are saved often enough to support flux computation.
- Additional references on practical flux computation from pseudo-spectral 2D Navier-Stokes simulations if the project proceeds to flux validation.

## Current Claim Boundary

The current project does not yet have full spectral flux validation. These sources support the limitation that a residual `k^-3`-like spectral shape is not sufficient to claim a stationary enstrophy cascade. They should be used to justify future work and conservative wording, not to strengthen the present numerical claim.
