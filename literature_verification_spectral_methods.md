# Literature Verification: Spectral Methods, Dealiasing, and Spectral Diagnostics

## Purpose

This file records targeted citation verification for numerical-method support relevant to:

1. Fourier pseudo-spectral methods for fluid simulations
2. nonlinear aliasing and high-wavenumber filtering / dealiasing
3. shell-averaged and isotropic spectra
4. compensated spectra and power-law spectra
5. finite-resolution and finite-range caveats

These sources support numerical-method choices and interpretation caveats. They do not support this project's specific residual `k^-3`-like numerical result directly.

## Verified Sources

### 1. Spectral Methods in Fluid Dynamics

- Full citation metadata: Claudio Canuto, M. Yousuff Hussaini, Alfio Quarteroni, and Thomas A. Zang, *Spectral Methods in Fluid Dynamics*, Springer, 1988.
- DOI / publisher / stable URL: Springer, DOI `10.1007/978-3-642-84108-8`; Springer record: `https://link.springer.com/book/10.1007/978-3-642-84108-8`
- Source type: textbook
- What claim it supports: Spectral and Fourier-based methods are established numerical tools for fluid-dynamics simulations, including unsteady Navier-Stokes algorithms and spectral approximation/stability concepts.
- What claim it does NOT support: It does not validate this project's solver implementation, dealiasing details, or spectral-slope result unless those implementation details are separately audited.
- Confidence level: high

### 2. Spectral Calculations of Isotropic Turbulence: Efficient Removal of Aliasing Interactions

- Full citation metadata: G. S. Patterson Jr. and Steven A. Orszag, "Spectral Calculations of Isotropic Turbulence: Efficient Removal of Aliasing Interactions," Physics of Fluids, volume 14, issue 11, pages 2538-2541, 1971.
- DOI / publisher / stable URL: AIP Publishing, DOI `10.1063/1.1693365`
- Source type: peer-reviewed article
- What claim it supports: Aliasing interactions are a known issue in spectral turbulence calculations, and specific removal/dealiasing procedures are part of established pseudo-spectral turbulence methodology.
- What claim it does NOT support: It does not prove that this project's numerical solver is correctly dealiased or that the observed residual slope is unaffected by aliasing.
- Confidence level: high

### 3. On the Elimination of Aliasing in Finite-Difference Schemes by Filtering High-Wavenumber Components

- Full citation metadata: Steven A. Orszag, "On the Elimination of Aliasing in Finite-Difference Schemes by Filtering High-Wavenumber Components," Journal of the Atmospheric Sciences, volume 28, issue 6, page 1074, 1971.
- DOI / publisher / stable URL: American Meteorological Society, DOI `10.1175/1520-0469(1971)028<1074:OTEOAI>2.0.CO;2`
- Source type: peer-reviewed article / short note
- What claim it supports: High-wavenumber filtering is a classical approach to eliminating aliasing errors in nonlinear numerical calculations; this is part of the historical basis for truncation/filtering dealiasing methods.
- What claim it does NOT support: It does not by itself document the current solver's dealiasing strategy, nor does it show that a particular fitted spectrum is alias-free.
- Confidence level: high

### 4. Turbulent Flows

- Full citation metadata: Stephen B. Pope, *Turbulent Flows*, Cambridge University Press, 2000.
- DOI / publisher / stable URL: Cambridge University Press, book DOI `10.1017/CBO9780511840531`; Appendix G "Power-law spectra" DOI `10.1017/CBO9781316179475.022`
- Source type: textbook
- What claim it supports: Energy spectra, Fourier/spectral representations, and power-law spectra are standard turbulence-analysis tools; compensated spectra are a common way to inspect consistency with a proposed power-law range.
- What claim it does NOT support: It does not prove that this project's compensated `k^3 E(k)` shoulder is an inertial range, nor that the project has achieved full stationarity.
- Confidence level: high

### 5. Turbulence: An Introduction for Scientists and Engineers

- Full citation metadata: P. A. Davidson, *Turbulence: An Introduction for Scientists and Engineers*, 2nd edition, Oxford University Press, 2015.
- DOI / publisher / stable URL: Oxford University Press, book DOI `10.1093/acprof:oso/9780198722588.001.0001`; Chapter 8 "Isotropic turbulence (in spectral space)" DOI `10.1093/acprof:oso/9780198722588.003.0008`
- Source type: textbook
- What claim it supports: Turbulence can be analyzed in spectral space using Fourier transforms, spectral tensors, energy spectra, and one-dimensional spectra; this supports the manuscript's general spectral-analysis vocabulary.
- What claim it does NOT support: It does not validate this project's radial shell binning implementation or residual spectral exponent.
- Confidence level: high

## How These References Should Be Used

Appropriate use:

- Support the use of spectral methods and Fourier-space diagnostics as standard numerical/turbulence-analysis tools.
- Explain why nonlinear aliasing and high-wavenumber filtering/dealiasing matter in pseudo-spectral simulations.
- Support cautious discussion of energy spectra, power-law spectra, compensated spectra, and finite spectral ranges.
- Motivate the need to document solver implementation details if dealiasing is discussed in the manuscript.

Inappropriate use:

- Do not cite these sources as evidence that this project's solver is correctly implemented unless the implementation is separately audited.
- Do not cite them as proof that Run 004, Run 009, Run 011, Run 012, or Run 013 has a validated stationary cascade.
- Do not use general turbulence-spectrum references to claim the residual `k^-3`-like window is an asymptotic inertial range.
- Do not use aliasing references to imply aliasing is solved unless the solver's dealiasing/filtering behavior is documented.

## Sources Considered but Not Added in This Pass

- Canuto, Hussaini, Quarteroni, and Zang, *Spectral Methods: Fundamentals in Single Domains*, Springer, 2006, DOI `10.1007/978-3-540-30726-6`. Verified and useful, but not added to the main five-source list because *Spectral Methods in Fluid Dynamics* is more directly tied to fluid simulation.
- Reputable university lecture notes on shell averaging and turbulence spectra. These may be useful later, but textbooks and peer-reviewed sources should be preferred for manuscript citations.

## Still Needed After This Pass

- A direct source specifically discussing shell-averaged spectra or radial bin population in discrete Fourier turbulence simulations.
- A direct source discussing compensated spectra as an interpretive diagnostic and the danger of short finite scaling ranges.
- A solver-specific implementation audit documenting whether the current code uses dealiasing, filtering, or neither.
- If the manuscript discusses the exact `2/3` rule, add a sentence tying that rule explicitly to the verified Orszag/Patterson-Orszag sources and the solver audit.
