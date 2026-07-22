# Phase 4 manuscript figure captions

Source checkpoint: `9b1b4eb981982178815bf6387e9edd2e8a1182b5`.

## Figure 1

**Selected-window residual spectral diagnostics for Run 004.** (a)
Peak-masked window-mean spectrum over saved indices 38--43 (steps
38,000--43,000). Markers identify the fitted shells `k=9:41`, the reference
line shows the fitted exponent near `-3`, and the recorded floor estimates
remain well below the fitted values. The forcing-scale band `k=2:4` is
excluded. (b) The corresponding normalized compensation, `k^3 E_norm(k)`,
shows limited plateau-like behavior over the same interval. These panels
establish a residual spectral resemblance in a selected window; they do not
establish stationarity, an inertial range, or an enstrophy cascade.

## Figure 2

**Physical limitation and growth--shape tradeoff in the archived production
comparison.** (a) Independently normalized Run 004 total and masked peak-band
energies continue to grow through the selected analysis window, while the
residual decreases slightly. The annotation, rather than vertical separation
of the normalized curves, records the near-unity peak-band fraction at step
43,000. (b)
Across the five documented cases, stronger low-wavenumber control reduces
selected-window growth but generally increases compensated-spectrum
variation. Run 011 has the lowest selected-window growth among the listed
combined cases, while Run 013 is a descriptive compromise. The comparison
identifies neither a stationary case nor a universally optimal configuration.

## Figure 3

**Grid contraction and unresolved operator-pair differences in the separate
Stage E smooth problem.** (a) Every final-time pairwise separation decreases
with grid refinement; at `N=144`, the ten separations are approximately
`0.1987--0.2015` of their `N=64` values. (b) Nevertheless, all final
uncertainty-to-separation ratios exceed the frozen resolution threshold of
`0.20` (`1.239--5.154` observed), so none of the ten pairs is resolved. The
finite-grid differences are measurable, but these results establish neither
distinct nor identical continuum limits and do not rank the methods. Stage E
uses a separate smooth, L-shaped refinement problem and is not a refinement
test of Runs 004--013.

Trajectory abbreviations: FD-A, finite-difference advective; FD-C,
finite-difference conservative; FD-S, finite-difference skew-symmetric; PS-A,
pseudo-spectral advective; Arakawa, Arakawa Jacobian trajectory.
