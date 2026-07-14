\# Phase 11L fd\_centered Diagnostic Run-Loop Equivalence Design



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.5.11-phase11K1-selectable-diagnostic-run-loop-scaffold-audit

\- Current previous commit: d1ea024

\- Design file: PHASE11L\_FD\_CENTERED\_DIAGNOSTIC\_RUN\_LOOP\_EQUIVALENCE\_DESIGN.md



\## Purpose



Phase 11L is a design-only phase.



The purpose is to design an equivalence audit for the selectable diagnostic run-loop when using:



advection\_method = "fd\_centered"



The audit should compare:



SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic(...)



against a direct transcription of the validated baseline SpectralSolver update loop.



This phase does not modify source code.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Why This Phase Is Needed



Phase 11K added:



run\_selectable\_diagnostic(...)



Phase 11K.1 confirmed that the scaffold works mechanically for:



\- fd\_centered

\- pseudo\_spectral

\- arakawa



However, Phase 11K.1 did not prove that:



run\_selectable\_diagnostic(...)



reproduces the baseline solver path when the selectable method is:



fd\_centered



The next validation step must check that the new diagnostic run-loop preserves the known baseline behavior before using it for larger comparisons.



\## Current Validated Baseline



The validated baseline solver remains:



project/solver/spectral\_solver.py



The baseline nonlinear method is classified as:



mixed\_spectral\_finite\_difference



The baseline update structure is:



1\. spectral streamfunction

2\. spectral velocity

3\. centered finite-difference vorticity gradients

4\. nonlinear advection adv = u \* omega\_x + v \* omega\_y

5\. spectral diffusion

6\. inherited deterministic forcing

7\. RK2-style update

8\. post-step 2/3 spectral dealiasing



\## Selectable Path Under Test



The selectable solver remains:



project/solver/selectable\_advection\_solver.py



The method under test is:



fd\_centered



The selectable diagnostic method under test is:



run\_selectable\_diagnostic(...)



The selectable step method under test is:



step\_once\_selectable(w)



The selectable RHS method under test is:



compute\_rhs\_selectable(w)



\## Required Comparison



The next audit should compare two paths:



| Path | Description |

|---|---|

| Baseline transcription path | Direct local transcription of SpectralSolver.run() one-step logic |

| Selectable diagnostic path | SelectableAdvectionSolver.run\_selectable\_diagnostic(...), using fd\_centered |



The comparison should use the same:



\- N

\- Re

\- dt

\- steps

\- initial field

\- forcing

\- dealiasing mask

\- diagnostics definitions



\## Important Rule



Do not call SpectralSolver.run().



Reason:



SpectralSolver.run() writes its own production-style outputs and mutates solver state.



The audit should instead use a direct local baseline-loop transcription so the comparison is controlled and explicit.



\## Baseline Transcription Logic



The baseline transcription should follow the validated SpectralSolver.run() step structure.



For each step:



1\. Compute streamfunction:



psi = baseline\_solver.streamfunction(w)



2\. Compute velocity:



u, v = baseline\_solver.velocity(psi)



3\. Compute centered finite-difference vorticity gradients:



omega\_x = (roll(w, -1, axis=1) - roll(w, 1, axis=1)) / (2 \* dx)



omega\_y = (roll(w, -1, axis=0) - roll(w, 1, axis=0)) / (2 \* dx)



4\. Compute nonlinear advection:



adv = u \* omega\_x + v \* omega\_y



5\. Compute first RHS:



k1 = -adv + baseline\_solver.laplacian\_spectral(w) + baseline\_solver.forcing()



6\. Compute provisional state:



w1 = w + dt \* k1



7\. Repeat the same RHS logic at w1 to compute k2.



8\. Compute RK2-style update:



w\_new = w + 0.5 \* dt \* (k1 + k2)



9\. Apply post-step 2/3 dealiasing:



W = fft2(w\_new)



W \*= baseline\_solver.deal



w = ifft2(W).real



This local transcription should not mutate baseline\_solver.w.



\## Selectable Diagnostic Logic



The selectable diagnostic path should run:



SelectableAdvectionSolver(

&#x20;   nx=N,

&#x20;   ny=N,

&#x20;   Re=Re,

&#x20;   dt=dt,

&#x20;   steps=steps,

&#x20;   advection\_method="fd\_centered",

&#x20;   run\_path=selectable\_run\_path,

)



Then:



result = solver.run\_selectable\_diagnostic(

&#x20;   initial\_w=initial\_w,

&#x20;   steps=steps,

&#x20;   log\_every=log\_every,

&#x20;   write\_outputs=True,

&#x20;   save\_initial\_state=True,

&#x20;   save\_final\_state=True,

)



The comparison should use:



result\["final\_w"]



as the selectable final state.



\## Recommended First Audit Parameters



Use a small controlled test first.



| Parameter | Value |

|---|---:|

| N | 64 |

| Re | 1000 |

| dt | 0.001 |

| steps | 20 |

| log\_every | 1 |

| initial RMS | 0.01 |

| forcing | inherited baseline deterministic forcing |

| method | fd\_centered |



Reason:



The first equivalence audit should check exact logic agreement, not long-time research behavior.



\## Recommended Initial Field



Use a deterministic smooth multimode initial condition:



\- sin(2X) cos(2Y)

\- 0.75 sin(3X) cos(Y)

\- 0.50 sin(X) cos(4Y)

\- 0.35 cos(4X - 2Y)



Then rescale to RMS = 0.01.



This field is useful because it is smooth, deterministic, nontrivial, and already consistent with prior audit style.



\## Required Output Files



The next audit should write:



| File | Purpose |

|---|---|

| phase11m\_fd\_centered\_diagnostic\_run\_loop\_equivalence\_audit.py | audit script |

| PHASE11M\_FD\_CENTERED\_DIAGNOSTIC\_RUN\_LOOP\_EQUIVALENCE\_AUDIT.csv | audit result table |

| PHASE11M\_FD\_CENTERED\_DIAGNOSTIC\_RUN\_LOOP\_EQUIVALENCE\_AUDIT\_REPORT.md | audit report |



The audit may also create selectable diagnostic outputs under:



experiments/selectable\_diagnostics/phase11M\_fd\_centered\_equivalence



\## Required Audit Checks



The Phase 11M audit should check:



1\. SpectralSolver imports.



2\. SelectableAdvectionSolver imports.



3\. advection\_method is fd\_centered.



4\. SelectableAdvectionSolver.run() remains disabled.



5\. SpectralSolver file has no git diff.



6\. advection\_operators file has no git diff.



7\. Baseline local transcription completes.



8\. Selectable diagnostic run completes.



9\. Baseline final field is finite.



10\. Selectable final field is finite.



11\. Baseline final field is real.



12\. Selectable final field is real.



13\. Final field shapes match.



14\. Initial field is not mutated.



15\. baseline\_solver.w is not mutated.



16\. selectable\_solver.w is not mutated.



17\. Final fields match within strict tolerance.



18\. Final energy values match within strict tolerance.



19\. Final enstrophy values match within strict tolerance.



20\. Final RMS values match within strict tolerance.



21\. Spectrum energy sums match within strict tolerance.



22\. Spectrum dominant shell matches.



23\. Metadata says production\_ready = false.



24\. Metadata says turbulence\_claim = false.



25\. Metadata says k\_minus\_3\_claim = false.



\## Recommended Numerical Tolerances



Because fd\_centered should reproduce the same path, the expected differences should be near roundoff.



Recommended tolerances:



| Quantity | Tolerance |

|---|---:|

| final field max abs difference | <= 1e-13 |

| final field L2 difference | <= 1e-13 |

| final field relative L2 difference | <= 1e-11 |

| energy relative difference | <= 1e-11 |

| enstrophy relative difference | <= 1e-11 |

| RMS relative difference | <= 1e-11 |

| spectrum relative L2 difference | <= 1e-10 |



If the audit fails by a small numerical amount, do not loosen tolerances immediately.



First inspect:



\- whether both paths use the same forcing

\- whether both paths use the same dealiasing

\- whether both paths use the same grid

\- whether both paths use the same initial field copy

\- whether either path mutates solver.w

\- whether baseline transcription exactly matches SpectralSolver.run() logic



\## Expected Result



Expected Phase 11M result:



PASS



Expected interpretation:



The selectable diagnostic run-loop reproduces the validated baseline fd\_centered path for a short controlled run.



\## What a PASS Would Confirm



A PASS would confirm:



\- run\_selectable\_diagnostic preserves fd\_centered baseline behavior

\- the selectable diagnostic run-loop is suitable for controlled method comparison

\- the diagnostic run-loop can be used before longer controlled experiments

\- SelectableAdvectionSolver.run() can remain disabled

\- SpectralSolver can remain unchanged



\## What a PASS Would Not Confirm



A PASS would not confirm:



\- production readiness

\- long-time stability

\- turbulence

\- k^-3 scaling

\- inertial range behavior

\- Arakawa superiority

\- Arakawa production readiness

\- pseudo\_spectral production readiness



\## What a FAIL Would Mean



A FAIL would mean the selectable diagnostic run-loop has not yet been proven equivalent to the baseline path.



A FAIL should stop advancement.



Do not proceed to Arakawa or pseudo\_spectral run-loop comparisons until fd\_centered equivalence passes.



\## Recommended Next Phase



Phase 11M — fd\_centered Diagnostic Run-Loop Equivalence Audit



Purpose:



Implement the audit designed in Phase 11L.



The audit should compare:



SelectableAdvectionSolver(advection\_method="fd\_centered").run\_selectable\_diagnostic(...)



against:



a direct local transcription of SpectralSolver.run() one-step logic.



The audit should be short, deterministic, and strict.



\## Guardrails



Phase 11M must preserve:



\- SpectralSolver unchanged

\- advection\_operators unchanged

\- SelectableAdvectionSolver.run() disabled

\- fd\_centered default unchanged

\- Arakawa not default

\- no production simulation

\- no turbulence claim

\- no k^-3 claim

\- no inertial-range claim



\## Scientific Boundary



Correct statement after Phase 11L:



An fd\_centered diagnostic run-loop equivalence audit has been designed.



Incorrect statement:



The selectable diagnostic run-loop has already been proven equivalent to the baseline solver.



That statement requires Phase 11M.



\## Decision



Phase 11L decision:



PROCEED TO PHASE 11M FD\_CENTERED DIAGNOSTIC RUN-LOOP EQUIVALENCE AUDIT.



Do not enable run().



Do not replace SpectralSolver.



Do not make Arakawa the default.



Do not run turbulence experiments.



Do not make k^-3 claims.



\## Final Result



Phase 11L design:



PASS



Next phase:



Phase 11M — fd\_centered Diagnostic Run-Loop Equivalence Audit

