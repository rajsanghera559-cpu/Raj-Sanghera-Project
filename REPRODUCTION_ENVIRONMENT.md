# Reproduction environment record

## Purpose

This file distinguishes recorded historical execution facts from a
present-day environment used to inspect the repository and regenerate
publication artifacts. This present-day capture must not be represented as the
original D1R or Stage E runtime.

## Recorded historical information

The tracked Stage B and Stage C metadata record:

- operating system: `Windows-11-10.0.26200-SP0`;
- Python: `CPython 3.14.5`, 64-bit MSC build;
- NumPy: `2.4.4`; and
- primary floating dtype: `float64`.

The D1R and Stage E `run_metadata.json` files do not record the operating
system, Python version, or package versions. Their complete historical
environments are therefore unavailable and are not reconstructed here.

## Present-day publication and artifact-inspection environment

Status: **captured on 2026-07-22**.

- operating system: `Windows-11-10.0.26200-SP0`;
- Python: `3.14.5` (`MSC v.1944`, 64-bit AMD64 build);
- NumPy: `2.4.4`;
- pandas: `3.0.3`;
- Matplotlib: `3.10.9`; and
- Pillow: `12.2.0`.

The Python build reported:
`tags/v3.14.5:5607950, May 10 2026, 10:43:50`.
The package versions are pinned in `requirements-publication.txt` for
publication-artifact inspection and figure regeneration.

The following read-only command records the minimal packages used by the
solver, tabular analysis, and manuscript-figure renderer without advancing a
numerical state:

```powershell
python -B -c "import sys, platform, numpy, pandas, matplotlib, PIL; print('Python:',sys.version); print('Platform:',platform.platform()); print('NumPy:',numpy.__version__); print('pandas:',pandas.__version__); print('Matplotlib:',matplotlib.__version__); print('Pillow:',PIL.__version__)"
```

The command above produced the recorded versions through package imports only;
it did not execute the solver or advance a numerical state. This present-day
inspection environment does not prove byte-identical historical numerical
reproduction.

## Reproduction boundary

- Numerical conclusions remain bound to the archived execution commits and
  evidence inventories.
- The historical runners are repository-state-bound and should be used only
  with their recorded prerequisites.
- Publication-figure inspection and rendering perform no solver advancement.
- The present-day package pin is not represented as the unavailable historical
  D1R or Stage E environment.
- Final release still requires the permanent companion-evidence locator.
