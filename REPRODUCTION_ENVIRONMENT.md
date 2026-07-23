# Reproduction environment record

## Purpose

This file distinguishes recorded historical execution facts from a
present-day environment used to inspect the repository and regenerate
publication artifacts. A later environment capture must not be represented as
the original D1R or Stage E runtime.

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

Status: **pending capture on the publication workstation**.

The following read-only command records the minimal packages used by the
solver, tabular analysis, and manuscript-figure renderer without advancing a
numerical state:

```powershell
python -B -c "import sys, platform, numpy, pandas, matplotlib, PIL; print('Python:',sys.version); print('Platform:',platform.platform()); print('NumPy:',numpy.__version__); print('pandas:',pandas.__version__); print('Matplotlib:',matplotlib.__version__); print('Pillow:',PIL.__version__)"
```

The resulting versions will describe a present-day inspection environment.
They will not prove byte-identical historical numerical reproduction.

## Reproduction boundary

- Numerical conclusions remain bound to the archived execution commits and
  evidence inventories.
- The historical runners are repository-state-bound and should be used only
  with their recorded prerequisites.
- Publication-figure inspection and rendering perform no solver advancement.
- Final release requires the present-day environment values and the permanent
  companion-evidence locator to replace the pending status.
