\# Raj-Sanghera-Project



\## Purpose

2-D pseudo-spectral turbulence solver for controlled Reynolds-number experiments and k^-3 spectral analysis.



\## Current Status

Managed pilot execution achieved. Re=100 and Re=250 completed under RunManager. 

Stable state tagged as: `v0.1-pilot-validated`



\## Main Components

\- `SpectralSolver`: frozen reference solver core (DO NOT EDIT)

\- `RunManager`: manages experiment folders and metadata

\- `validate\_solver.py`: regression test against legacy logic

\- `analyze\_spectrum.py`: automated spectral plotting

\- `experiments/runs/`: storage for generated run data



\## Run Evidence Protocol

Each run folder contains:

\- `config.json`

\- `metadata.json` (includes git\_commit, git\_branch, git\_dirty, config\_hash)

\- `diagnostics.csv`

\- `spectrum.csv`

\- `error.log` (if failed)



\## Rules for Research

1\. Do not edit solver internals casually. 

2\. Add diagnostics and plotting \*around\* the solver (Composition over Modification).

3\. Serious runs require a clean Git state (`git\_dirty` must be false).

4\. Treat every completed run as immutable evidence.

