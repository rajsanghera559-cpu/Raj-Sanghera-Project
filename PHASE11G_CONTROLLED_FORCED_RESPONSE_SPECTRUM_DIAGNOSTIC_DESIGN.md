\# Phase 11G Controlled Forced-Response Spectrum Diagnostic Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.5-phase11F-N128-controlled-forced-response-decision-gate

\- Current previous commit: 38308d4

\- Design file: PHASE11G\_CONTROLLED\_FORCED\_RESPONSE\_SPECTRUM\_DIAGNOSTIC\_DESIGN.md



\## Purpose



Phase 11G is a design-only phase.



The purpose is to design a controlled forced-response spectrum diagnostic audit across selectable advection methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



This phase does not prove an inertial range.



\## Current Solver Status



The validated baseline solver remains:



project/solver/spectral\_solver.py



The selectable solver remains:



project/solver/selectable\_advection\_solver.py



The selectable solver currently supports:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



The selectable solver currently includes:



\- compute\_advection(w)

\- compute\_rhs\_selectable(w)

\- step\_once\_selectable(w)



The selectable solver still has:



run() intentionally disabled



This remains correct.



\## Recent Validation Chain



The project has passed:



| Phase | Result |

|---|---:|

| Phase 10P.1 fd\_centered one-step equivalence | PASS |

| Phase 10Q.1 selectable one-step operator comparison | PASS |

| Phase 10S short no-forcing drift, N=64, final time 1.0 | PASS |

| Phase 10V extended no-forcing drift, N=64, final time 5.0 | PASS |

| Phase 10Y short no-forcing drift, N=128, final time 1.0 | PASS |

| Phase 11B controlled forced response, N=64, final time 1.0 | PASS |

| Phase 11E controlled forced response, N=128, final time 1.0 | PASS |

| Phase 11F N128 controlled forced-response decision gate | PASS |



\## Why Phase 11G Is Needed



Phases 11B and 11E showed that fd\_centered, pseudo\_spectral, and arakawa remain finite, non-explosive, and closely aligned under controlled forced response.



The next conservative validation question is:



What spectral distributions do the selectable methods produce under the same controlled forced-response setup?



This is a diagnostic spectrum comparison.



This is not a turbulence test.



This is not a k^-3 test.



This is not an inertial-range claim.



\## Design Decision



Proceed to a controlled forced-response spectrum diagnostic audit.



The audit should regenerate controlled forced-response final fields using step\_once\_selectable(w), then compute kinetic energy spectra from those final fields.



Recommended resolutions:



\- N=64

\- N=128



Recommended parameters:



| Parameter | Value |

|---|---:|

| Re | 1000000 |

| nu | 1e-6 |

| dt | 0.001 |

| steps | 1000 |

| final time | 1.0 |

| forcing | baseline deterministic forcing |

| initial RMS | 0.01 |

| initial field | phase6d\_like\_multimode |



Methods:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



\## Baseline Forcing



The inherited baseline forcing from SpectralSolver is:



forcing() = 0.01 \* sin(2X) \* cos(2Y)



The audit should not override forcing.



The audit should verify:



\- forcing is nonzero

\- forcing is finite

\- forcing is real

\- forcing has shape (N, N)

\- forcing RMS is greater than zero

\- forcing max\_abs is greater than zero

\- forcing is identical across methods at each resolution



\## Initial Field



Use the controlled phase6d\_like\_multimode field:



\- sin(2X) \* cos(2Y)

\- 0.75 \* sin(3X) \* cos(Y)

\- 0.50 \* sin(X) \* cos(4Y)

\- 0.35 \* cos(4X - 2Y)



Then rescale to RMS 0.01.



Reason:



This field has been used across prior diagnostics, no-forcing drift audits, and controlled forced-response audits.



It is nonlinear enough to be meaningful while remaining controlled.



\## Future Audit Script



Recommended script:



phase11h\_controlled\_forced\_response\_spectrum\_diagnostic\_audit.py



Recommended outputs:



PHASE11H\_CONTROLLED\_FORCED\_RESPONSE\_SPECTRUM\_DIAGNOSTIC\_AUDIT.csv



PHASE11H\_CONTROLLED\_FORCED\_RESPONSE\_SPECTRA.csv



PHASE11H\_CONTROLLED\_FORCED\_RESPONSE\_SPECTRUM\_PAIRWISE\_SUMMARY.csv



PHASE11H\_CONTROLLED\_FORCED\_RESPONSE\_SPECTRUM\_DIAGNOSTIC\_AUDIT\_REPORT.md



\## Required Global Checks



The Phase 11H audit should verify:



\- SpectralSolver imports

\- SelectableAdvectionSolver imports

\- supported methods are exactly fd\_centered, pseudo\_spectral, arakawa

\- default method is fd\_centered

\- compute\_rhs\_selectable exists

\- step\_once\_selectable exists

\- SpectralSolver file has no git diff

\- SelectableAdvectionSolver file has no git diff

\- advection\_operators file has no git diff

\- invalid method remains rejected

\- SelectableAdvectionSolver.run() remains disabled



\## Required Forced-Response Checks



Before computing spectra, the audit should repeat basic controlled forced-response checks:



\- forcing is nonzero

\- forcing is finite

\- forcing is real

\- forcing is identical across methods

\- final field is finite

\- final field is real

\- input field is not mutated

\- solver.w is not mutated

\- run() remains disabled



These checks prevent the spectrum diagnostic from being computed on invalid fields.



\## Spectrum Computation



The audit should use the existing project spectrum diagnostic:



compute\_kinetic\_energy\_spectrum\_from\_vorticity(w, kx, ky)



or the inherited method:



solver.energy\_spectrum(w)



The audit should compute spectra for each:



\- resolution

\- method

\- final field



For each spectrum, record:



\- N

\- method

\- k

\- E(k)

\- mode\_count



\## Required Per-Method Spectrum Summary



For each method and resolution, compute:



\- direct kinetic energy from velocity

\- spectrum energy sum

\- spectrum/direct energy relative error

\- total enstrophy

\- dominant shell k

\- dominant shell energy

\- forced shell k=2 energy

\- k=3 energy

\- k=4 energy

\- low-k energy fraction

\- high-k energy fraction

\- maximum finite E(k)

\- minimum E(k)

\- number of finite spectrum bins

\- number of nonzero spectrum bins

\- spectrum finite check

\- spectrum nonnegative within tolerance check



\## Energy Consistency Check



The audit should compare:



direct\_energy = 0.5 \* mean(u\*u + v\*v)



against:



spectrum\_energy\_sum = sum(E(k))



Recommended pass threshold:



relative error <= 1e-8



Reason:



Earlier spectrum consistency audits showed very small energy-spectrum errors. This threshold is conservative but still strict.



If the error exceeds the threshold, the audit should report REVIEW or FAIL depending on severity.



\## Spectral Nonnegativity Check



Kinetic energy spectra should be nonnegative.



Because of floating-point noise, allow a tiny negative tolerance.



Recommended condition:



min(E(k)) >= -1e-14



If the minimum E(k) is below this threshold, report REVIEW or FAIL depending on magnitude.



\## Low-k and High-k Fractions



Define:



low-k fraction = sum E(k) for k <= 4 divided by total spectrum energy



high-k fraction = sum E(k) for k >= 10 divided by total spectrum energy



The exact shell thresholds are diagnostic only.



These fractions should not be used to claim turbulence or inertial-range behavior.



They are only used to compare method alignment under controlled forcing.



\## Pairwise Spectrum Comparisons



For each resolution, compare final spectra across methods:



| Pair | Purpose |

|---|---|

| pseudo\_spectral vs fd\_centered | spectral diagnostic method compared with baseline-compatible method |

| arakawa vs fd\_centered | Arakawa compared with baseline-compatible method |

| arakawa vs pseudo\_spectral | Arakawa compared with spectral diagnostic method |



For each pair, compute:



\- spectrum diff L2

\- spectrum diff max\_abs

\- relative spectrum error

\- spectrum cosine similarity

\- direct energy difference

\- spectrum energy sum difference

\- enstrophy difference

\- dominant shell agreement

\- low-k fraction difference

\- high-k fraction difference



\## Pairwise Pass Criteria



Recommended thresholds:



| Quantity | PASS Threshold |

|---|---:|

| spectrum cosine similarity | greater than 0.99 |

| relative spectrum error | less than 0.05 |

| direct energy relative difference | less than 0.05 |

| spectrum energy relative difference | less than 0.05 |

| low-k fraction difference | less than 0.05 |

| high-k fraction difference | less than 0.05 |



These thresholds are diagnostic-comparison thresholds.



They are not turbulence criteria.



\## Expected Interpretation



Because the forcing is deterministic and low-wavenumber, the spectra are expected to remain low-k dominated in this controlled short audit.



Expected outcomes:



\- spectra finite

\- spectra energy-consistent

\- methods spectrally aligned

\- dominant content remains near low wavenumbers

\- no claim of inertial range

\- no claim of k^-3 scaling



\## Explicitly Forbidden Interpretation



The audit must not fit a k^-3 slope as a validation claim.



The audit must not report k^-3 as evidence.



The audit must not claim turbulence.



The audit must not claim a resolved inertial range.



The audit must not call Arakawa production-ready.



If a slope is ever computed later, it must be clearly labeled exploratory and not used as proof without independent inertial-range validation.



\## Optional Diagnostic Slope



Phase 11H should avoid slope fitting unless necessary.



If any slope-like diagnostic is included, it must be labeled:



exploratory\_slope\_diagnostic\_only



and must state:



not evidence of k^-3 scaling



Recommended decision:



Do not include slope fitting in Phase 11H.



Keep Phase 11H focused on finite spectra, energy consistency, dominant shells, and pairwise spectrum alignment.



\## Runtime Expectation



The audit should rerun controlled forced response for:



\- N=64, 3 methods

\- N=128, 3 methods



Expected runtime:



\- likely a few minutes

\- possibly longer if CPU is throttled



The script should print progress every 100 steps for each method and resolution.



\## What Phase 11H Should Not Do



Phase 11H should not call:



SpectralSolver.run()



Phase 11H should not call:



SelectableAdvectionSolver.run()



Phase 11H should not modify:



project/solver/spectral\_solver.py



Phase 11H should not modify:



project/solver/selectable\_advection\_solver.py



Phase 11H should not modify:



project/solver/advection\_operators.py



Phase 11H should not run long simulations.



Phase 11H should not run turbulence experiments.



Phase 11H should not run k^-3 experiments.



Phase 11H should not claim Arakawa is production-ready.



\## What Phase 11H May Do



Phase 11H may create a standalone audit script.



Phase 11H may use the inherited baseline forcing.



Phase 11H may repeatedly call:



step\_once\_selectable(w)



inside the audit script.



Phase 11H may compute kinetic energy spectra.



Phase 11H may write CSV diagnostic outputs.



Phase 11H may compare spectra across selectable methods.



Phase 11H may produce a report.



\## Scientific Boundary



Correct statement after a passing Phase 11H would be:



The selectable methods produced finite, energy-consistent, and mutually aligned spectra under controlled forced-response conditions at N=64 and N=128.



Incorrect statement:



The selectable solver proves turbulence or k^-3 scaling.



That statement is not supported.



\## Recommended Next Phase After 11H



If Phase 11H passes, the next phase should be:



Phase 11I — Controlled Forced-Response Spectrum Decision Gate



Purpose:



Decide whether to proceed to either:



\- longer controlled forced-response spectrum audit

\- controlled forced-response at different forcing amplitudes

\- selectable run-loop design

\- carefully scoped spectrum slope exploration



Do not jump directly to k^-3 claims.



\## Decision



Phase 11G decision:



Proceed to Phase 11H controlled forced-response spectrum diagnostic audit.



Use:



\- N=64 and N=128

\- Re=1000000

\- dt=0.001

\- steps=1000

\- final time=1.0

\- forcing=baseline deterministic forcing

\- phase6d\_like\_multimode initial condition



Do not modify solver source files.



Do not enable run().



Do not run turbulence experiments.



Do not claim turbulence.



Do not claim k^-3 scaling.



\## Final Result



Phase 11G design:



PASS



Next phase:



Phase 11H — Controlled Forced-Response Spectrum Diagnostic Audit



Required guardrails:



\- SpectralSolver must remain unchanged.

\- SelectableAdvectionSolver must remain unchanged.

\- advection\_operators must remain unchanged.

\- SelectableAdvectionSolver.run() must remain disabled.

\- Baseline forcing must be verified.

\- Spectrum diagnostics must not be interpreted as turbulence proof.

\- No k^-3 claims.

