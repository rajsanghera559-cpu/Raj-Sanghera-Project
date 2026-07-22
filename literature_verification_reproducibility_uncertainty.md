# Literature Verification: Reproducibility, Reporting, and Exponent-Fit Uncertainty

## Purpose

This file records targeted citation verification for methodology/reporting discipline. The sources below support reproducibility practices, computational-science reporting, CFD verification/validation concepts, and caution around fitted power-law exponents.

These references do not support the physical spectral result directly. They should be used to justify careful documentation, reproducible workflows, uncertainty reporting, and conservative interpretation of fitted slopes.

## Verified Sources

### 1. Ten Simple Rules for Reproducible Computational Research

- Full citation metadata: Geir Kjetil Sandve, Anton Nekrutenko, James Taylor, and Eivind Hovig, "Ten Simple Rules for Reproducible Computational Research," PLOS Computational Biology, volume 9, issue 10, article e1003285, 2013.
- DOI / stable URL: `10.1371/journal.pcbi.1003285`; PLOS record: `https://doi.org/10.1371/journal.pcbi.1003285`
- Source type: peer-reviewed guidance article
- What claim it supports: Computational results should be accompanied by traceable data, scripts, workflows, and documentation so that analyses can be rerun and audited.
- What claim it does NOT support: It does not validate this project's turbulence results or any residual spectral exponent.
- Relevance to this project: Supports the project's current checkpoint practice: committed scripts, curated comparison artifacts, documented source files, and explicit claim boundaries.
- Confidence level: high

### 2. Best Practices for Scientific Computing

- Full citation metadata: Greg Wilson, D. A. Aruliah, C. Titus Brown, Neil P. Chue Hong, Matt Davis, Richard T. Guy, Steven H. D. Haddock, Kathryn D. Huff, Ian M. Mitchell, Mark D. Plumbley, Ben Waugh, Ethan P. White, and Paul Wilson, "Best Practices for Scientific Computing," PLOS Biology, volume 12, issue 1, article e1001745, 2014.
- DOI / stable URL: `10.1371/journal.pbio.1001745`; PLOS record: `https://doi.org/10.1371/journal.pbio.1001745`
- Source type: peer-reviewed guidance article
- What claim it supports: Scientific software should be version controlled, documented, organized, and tested where practical; scripts and data-processing steps should be clear enough to audit.
- What claim it does NOT support: It does not support the physical conclusion that a residual `k^-3`-like range exists.
- Relevance to this project: Supports analysis architecture cleanup, Git checkpointing, README files, and reproducibility-oriented reporting.
- Confidence level: high

### 3. Verification and Validation in Computational Fluid Dynamics

- Full citation metadata: William L. Oberkampf and Timothy G. Trucano, "Verification and validation in computational fluid dynamics," Progress in Aerospace Sciences, volume 38, issue 3, pages 209-272, 2002.
- DOI / stable URL: journal DOI `10.1016/S0376-0421(02)00005-2`; the related Sandia report record uses `10.2172/793406`: `https://www.sandia.gov/research/publications/details/verification-and-validation-in-computational-fluid-dynamics-2002-03-01/`
- Source type: peer-reviewed review, with a related Sandia technical-report record
- What claim it supports: Verification and validation require explicit attention to numerical error, uncertainty, model assumptions, and the distinction between code verification, solution verification, and validation.
- What claim it does NOT support: It does not validate this project's solver or physical result; it only supports the need for careful V&V framing.
- Relevance to this project: Supports caution that solver implementation, resolution, stationarity, and diagnostic limitations should be documented before strong CFD claims are made.
- Confidence level: high

### 4. V&V 20 - Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer

- Full citation metadata: ASME, *V&V 20 - Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer*, ASME V&V 20-2009, reaffirmed 2021.
- DOI / stable URL: ASME standards page: `https://www.asme.org/codes-standards/find-codes-standards/standard-for-verification-and-validation-in-computational-fluid-dynamics-and-heat-transfer/2009`
- Source type: engineering standard
- What claim it supports: CFD validation should quantify accuracy and uncertainty relative to specified validation variables and should distinguish solution/data errors and uncertainties.
- What claim it does NOT support: It does not establish that this project is validated under ASME V&V 20, and the manuscript should not imply formal compliance.
- Relevance to this project: Useful as background for why uncertainty, reproducibility, and validation language must be precise.
- Confidence level: high

### 5. Power-Law Distributions in Empirical Data

- Full citation metadata: Aaron Clauset, Cosma Rohilla Shalizi, and M. E. J. Newman, "Power-Law Distributions in Empirical Data," SIAM Review, volume 51, issue 4, pages 661-703, 2009.
- DOI / stable URL: `10.1137/070710111`; SIAM record: `https://doi.org/10.1137/070710111`
- Source type: peer-reviewed review / methodological article
- What claim it supports: Power-law detection and exponent estimation are sensitive to fitting range, noise, and goodness-of-fit assumptions; simple least-squares/log-log line fitting can be misleading if used without robustness checks.
- What claim it does NOT support: It does not directly apply to turbulence spectra as a complete spectral-analysis method, and it does not validate this project's fitted exponent.
- Relevance to this project: Supports the manuscript's use of window sensitivity, uncertainty bands, and conservative "k^-3-like" wording rather than an exact exponent claim.
- Confidence level: high

### 6. Critical Truths About Power Laws

- Full citation metadata: Michael P. H. Stumpf and Mason A. Porter, "Critical Truths About Power Laws," Science, volume 335, issue 6069, pages 665-666, 2012.
- DOI / stable URL: `10.1126/science.1216142`; Science record / DOI: `https://doi.org/10.1126/science.1216142`
- Source type: peer-reviewed perspective/commentary
- What claim it supports: Apparent power-law behavior can be overinterpreted; rigorous testing and alternative explanations matter.
- What claim it does NOT support: It does not provide turbulence-specific validation and should not be used as direct evidence about 2D spectra.
- Relevance to this project: Supports cautious language around fitted residual spectral slopes and the need to avoid claiming a new law from limited scaling evidence.
- Confidence level: high

## How These References Should Be Used

Appropriate use:

- Support reproducibility practices: version control, script documentation, curated artifacts, and traceable workflows.
- Support careful numerical reporting and the distinction between verification, validation, uncertainty, and interpretation.
- Support cautious fitted-exponent language and sensitivity/uncertainty diagnostics.
- Justify why the manuscript should keep residual `k^-3`-like wording rather than exact-law language.

Inappropriate use:

- Do not cite these sources as evidence that Run 004, Run 009, Run 011, Run 012, or Run 013 has a physical cascade.
- Do not use ASME V&V 20 to imply formal validation compliance unless the project actually performs that standard's process.
- Do not use general power-law references as a substitute for turbulence-specific spectral diagnostics.
- Do not claim reproducibility guidance validates the solver.

## Still Needed After This Pass

- A turbulence-specific source on uncertainty or sensitivity in spectral-slope fitting, if available.
- A reference on robust regression or confidence intervals in log-log spectral fits, if that becomes a methodological section.
- A project-specific solver verification note documenting numerical methods, dealiasing status, and resolution limits.
- If a formal reproducibility package is prepared, a checklist mapping code, data, outputs, and report claims should be added.
