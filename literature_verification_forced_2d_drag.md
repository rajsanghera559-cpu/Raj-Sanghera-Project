# Literature Verification: Forced-Dissipative 2D Turbulence, Drag, and Condensation

## Purpose

This file records targeted citation verification for forced-dissipative 2D turbulence references relevant to forcing scale, large-scale drag/friction, enstrophy-cascade ranges, low-k condensation, and stationarity caveats.

These sources are context and methodological background. They do not validate this project's numerical result directly. The current project claim remains limited to residual `k^-3`-like spectral validation in selected peak-masked windows, with severe peak domination and incomplete full-system stationarity still active caveats.

## Verified Sources

### 1. The Enstrophy Cascade in Forced Two-Dimensional Turbulence

- Full citation metadata: Andreas Vallgren and Erik Lindborg, "The enstrophy cascade in forced two-dimensional turbulence," Journal of Fluid Mechanics, volume 671, pages 168-183, 2011.
- DOI / stable URL: `10.1017/S0022112010005562`; Cambridge Core record: `https://doi.org/10.1017/S0022112010005562`; KTH DiVA record: `https://www.diva-portal.org/smash/record.jsf?pid=diva2:359537`
- Source type: simulation
- Relevance to this project: Highly relevant to forcing scale, enstrophy-cascade spectra, and the distinction between quasi-stationary enstrophy and growing energy in forced 2D simulations.
- What claim it supports: Forced 2D simulations can reach states where enstrophy is quasi-stationary while energy continues growing; forcing scale and large-scale drag affect coherence, intermittency, and spectral behavior.
- What claim it does NOT support: It does not validate this project's Run 004 or Run 013 as a stationary enstrophy cascade. It should not be used as direct evidence for this project's residual spectral fit.
- Confidence level: high

### 2. Energy and Enstrophy Fluxes in the Double Cascade of Two-Dimensional Turbulence

- Full citation metadata: Guido Boffetta, "Energy and enstrophy fluxes in the double cascade of two-dimensional turbulence," Journal of Fluid Mechanics, volume 589, pages 253-260, 2007.
- DOI / stable URL: `10.1017/S0022112007008014`; Cambridge Core record: `https://doi.org/10.1017/S0022112007008014`
- Source type: simulation
- Relevance to this project: Directly relevant to the diagnostic standard for cascade claims because it analyzes energy and enstrophy fluxes in high-resolution stationary simulations.
- What claim it supports: Flux diagnostics are a stronger validation standard than slope fitting alone for double-cascade claims.
- What claim it does NOT support: It does not imply this project has flux-validated an enstrophy cascade; the current project has not yet documented comparable flux diagnostics.
- Confidence level: high

### 3. Effects of Friction on Two-Dimensional Navier-Stokes Turbulence

- Full citation metadata: Luke A. K. Blackbourn and Chuong V. Tran, "Effects of friction on two-dimensional Navier-Stokes turbulence," Physical Review E, volume 84, issue 4, article 046322, 2011.
- DOI / stable URL: `10.1103/PhysRevE.84.046322`; University of St Andrews record: `https://research-portal.st-andrews.ac.uk/en/publications/effects-of-friction-on-two-dimensional-navier-stokes-turbulence/`
- Source type: theory and simulation
- Relevance to this project: Directly relevant to the project's low-k/drag motivation, because it discusses large-scale dissipation mechanisms and the effects of mechanical friction on forced 2D Navier-Stokes turbulence.
- What claim it supports: Mechanical friction and large-scale dissipation can affect small-scale dynamics and enstrophy-transfer interpretation; friction is not a neutral intervention.
- What claim it does NOT support: It does not prove that this project's low-k selective drag parameters are optimal or that drag produces a stationary cascade.
- Confidence level: high

### 4. Nonuniversal Velocity Probability Densities in Two-Dimensional Turbulence: The Effect of Large-Scale Dissipation

- Full citation metadata: Yue-Kin Tsang, "Nonuniversal velocity probability densities in two-dimensional turbulence: The effect of large-scale dissipation," Physics of Fluids, volume 22, article 115102, 2010.
- DOI / stable URL: `10.1063/1.3504377`; article PDF / metadata page: `https://www.mas.ncl.ac.uk/Yue-Kin.Tsang/paper/PhysFluids_22_115102.pdf`
- Source type: simulation
- Relevance to this project: Highly relevant to the comparison between global/linear drag and low-wavenumber selective drag. The paper explicitly compares linear Ekman drag, quadratic drag, and scale-selective hypo-drag in forced 2D turbulence.
- What claim it supports: Large-scale dissipation choices can materially change statistically steady forced 2D turbulence statistics; scale-selective drag is an established modeling choice but can alter coherent-vortex statistics.
- What claim it does NOT support: It does not validate this project's low-k drag implementation or show that Run 013 is physically optimal.
- Confidence level: high

### 5. Large Scale Drag Representation in Simulations of Two-Dimensional Turbulence

- Full citation metadata: Semion Sukoriansky, Boris Galperin, and Alexei Chekhlov, "Large Scale Drag Representation in Simulations of Two-dimensional Turbulence," Physics of Fluids, volume 11, 1999.
- DOI / stable URL: `10.1063/1.870163`; University of South Florida record: `https://digitalcommons.usf.edu/msc_facpub/1451/`
- Source type: simulation / modeling
- Relevance to this project: Directly relevant to low-k domination and the reason large-scale drag is introduced. The paper frames forced-dissipative 2D turbulence as complicated by inverse-cascade energy accumulation at large-scale modes.
- What claim it supports: Large-scale energy condensation and coherent-vortex formation are known issues in forced-dissipative 2D turbulence simulations; large-scale drag representation can affect whether expected statistical laws persist.
- What claim it does NOT support: It does not show that this project's low-k peak domination has been solved, and it does not validate the residual `k^-3`-like result.
- Confidence level: high

## Sources Considered but Not Added in This Pass

- Boffetta and Musacchio, "Evidence for the double cascade scenario in two-dimensional turbulence," Physical Review E 82, 016307, 2010. Metadata was verified, but it was not included in the five-source list to keep this pass focused on forced/dissipative drag, forcing scale, flux, and condensation context. It remains a strong candidate for a later broader double-cascade literature pass.
- Smith and Yakhot, "Bose condensation and small-scale structure generation in a random force driven 2D turbulence," Physical Review Letters 71, 352-355, 1993. Metadata was visible from secondary records, but it was not included in this pass because the five selected sources already cover condensation and drag representation more directly for the current manuscript framing.

## How These References Should Be Used

Appropriate use:

- Frame why forcing scale matters in forced 2D turbulence.
- Explain why energy growth can coexist with quasi-stationary enstrophy behavior.
- Support the need for large-scale drag or low-k damping when inverse transfer accumulates energy at large scales.
- Support the caution that drag and scale-selective damping can change spectral and statistical behavior.
- Motivate future flux diagnostics as a stronger cascade-validation step.

Inappropriate use:

- Do not cite these papers as evidence that this project's runs validate a fully stationary enstrophy cascade.
- Do not use these papers to claim that Run 004, Run 009, Run 011, Run 012, or Run 013 reproduces their simulations.
- Do not claim that low-k drag solves peak domination or stationarity in this project.
- Do not use these sources to strengthen the project claim beyond residual-spectrum validation.

## Still Needed After This Pass

- Direct references on compensated spectra as a diagnostic and the risk of short finite scaling ranges.
- Direct references on radial shell averaging / shell population effects in discrete Fourier spectra.
- Additional flux-diagnostic references if a future analysis computes energy/enstrophy fluxes.
- If low-k selective drag becomes central to the manuscript, add a deeper pass on hypofriction, hypo-drag, and Ekman drag parameterizations.
