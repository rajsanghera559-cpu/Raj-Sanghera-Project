# Literature Verification: 2D Turbulence Theory and `k^-3` Context

## Purpose

This file records a targeted first-pass citation verification for the preprint manuscript. It focuses only on high-confidence sources relevant to:

1. 2D turbulence review context
2. inverse energy cascade / direct enstrophy cascade
3. Kraichnan-Batchelor or Kraichnan-Leith-Batchelor `k^-3` context

These sources are background theory and context. They may support why `k^-3` is a relevant theoretical comparison, but they do not support a claim that this project's simulations have produced a fully stationary enstrophy cascade.

## Verified Sources

### 1. Two-Dimensional Turbulence

- Full citation metadata: Guido Boffetta and Robert E. Ecke, "Two-Dimensional Turbulence," Annual Review of Fluid Mechanics, volume 44, pages 427-451, 2012.
- DOI / stable URL: `10.1146/annurev-fluid-120710-101240`; stable repository record: `https://hdl.handle.net/2318/102223`
- Category: 2D turbulence review context; modern review / survey source
- What claim it supports: 2D turbulence has a recognized dual-cascade framework involving inverse energy transfer and direct enstrophy transfer; `k^-3` is a standard theoretical reference in that context; friction, energy flux, and enstrophy flux are standard diagnostic concerns.
- What claim it does NOT support: It does not show that this project has achieved statistical stationarity or a full enstrophy cascade.
- Background theory or directly relevant: Background theory and review context.
- Confidence level: high

### 2. Two-Dimensional Turbulence: A Physicist Approach

- Full citation metadata: Patrick Tabeling, "Two-dimensional turbulence: a physicist approach," Physics Reports, volume 362, issue 1, pages 1-62, 2002.
- DOI / stable URL: `10.1016/S0370-1573(01)00064-3`; ScienceDirect record: `https://www.sciencedirect.com/science/article/pii/S0370157301000643`
- Category: 2D turbulence review context; modern review / survey source
- What claim it supports: 2D turbulence has established experimental, numerical, and theoretical literature around coherent structures, inverse energy cascade, direct enstrophy cascade, and cascade interpretation.
- What claim it does NOT support: It does not directly support the numerical metrics from Run 004, Run 009, Run 011, Run 012, or Run 013.
- Background theory or directly relevant: Background theory and review context.
- Confidence level: high

### 3. Inertial Ranges in Two-Dimensional Turbulence

- Full citation metadata: Robert H. Kraichnan, "Inertial Ranges in Two-Dimensional Turbulence," Physics of Fluids, volume 10, issue 7, pages 1417-1423, 1967.
- DOI / stable URL: `10.1063/1.1762301`; DOI URL: `https://doi.org/10.1063/1.1762301`
- Category: Kraichnan-Batchelor / Kraichnan-Leith-Batchelor `k^-3` context
- What claim it supports: The `k^-3` direct enstrophy-transfer spectrum is a classical theoretical reference for 2D turbulence; the dual inertial-range picture is foundational.
- What claim it does NOT support: It does not prove that this project's residual spectral window is a true stationary enstrophy-cascade range.
- Background theory or directly relevant: Background theory; directly relevant to the theoretical comparison exponent.
- Confidence level: high

### 4. Diffusion Approximation for Two-Dimensional Turbulence

- Full citation metadata: C. E. Leith, "Diffusion Approximation for Two-Dimensional Turbulence," Physics of Fluids, volume 11, issue 3, pages 671-672, 1968.
- DOI / stable URL: `10.1063/1.1691968`; DOI URL: `https://doi.org/10.1063/1.1691968`
- Category: Kraichnan-Leith-Batchelor `k^-3` context
- What claim it supports: Classical 2D turbulence theory predicts both inverse-energy and direct-enstrophy inertial ranges, including the `-3` enstrophy-transfer reference.
- What claim it does NOT support: It does not directly validate any finite-time, peak-masked residual spectrum from this project.
- Background theory or directly relevant: Background theory; directly relevant to the theoretical comparison exponent.
- Confidence level: high

### 5. Computation of the Energy Spectrum in Homogeneous Two-Dimensional Turbulence

- Full citation metadata: G. K. Batchelor, "Computation of the Energy Spectrum in Homogeneous Two-Dimensional Turbulence," Physics of Fluids, volume 12, issue 12, pages II-233-II-239, 1969.
- DOI / stable URL: `10.1063/1.1692443`; DOI URL: `https://doi.org/10.1063/1.1692443`
- Category: Kraichnan-Batchelor / Kraichnan-Leith-Batchelor `k^-3` context
- What claim it supports: The `k^-3` reference belongs to the classical 2D turbulence spectral theory context; homogeneous 2D turbulence spectra have a long numerical/theoretical history.
- What claim it does NOT support: It does not support claiming this project's residual spectra are asymptotic, stationary, or energetically dominant.
- Background theory or directly relevant: Background theory; directly relevant to the theoretical comparison exponent.
- Confidence level: high

## Sources That Could Not Be Verified

None in this targeted first pass. The five sources above were included because title, author, year, publication venue, and DOI or stable metadata could be checked from accessible metadata records.

## How These References Should Be Used

Appropriate use:

- Introduce the 2D turbulence dual-cascade framework.
- Explain why `k^-3` is a meaningful reference exponent.
- Support cautious language around inverse energy transfer, direct enstrophy transfer, and the need for flux/stationarity diagnostics.

Inappropriate use:

- Do not cite these sources as evidence that Run 004, Run 009, Run 011, Run 012, or Run 013 produced a fully stationary enstrophy cascade.
- Do not use these sources to imply that a peak-masked residual `k^-3`-like slope is sufficient for cascade validation.
- Do not use these sources to claim a new turbulence law.

## Still Needed After This Pass

- Direct references on compensated spectra and finite scaling-range caveats.
- Direct references on flux diagnostics for validating 2D cascades.
- Direct references on shell averaging / radial bin population in discrete Fourier spectra.
- Direct references on statistical stationarity criteria in forced numerical turbulence.
