\# Phase 10M Baseline Update Logic Inspection



\## Checkpoint



\- Branch: phase4\_validation

\- Current previous tag: v0.4.46-phase10L-selectable-fd-centered-equivalence-design

\- Current previous commit: 0b5264c

\- Inspection target: project/solver/spectral\_solver.py

\- Inspection file: PHASE10M\_BASELINE\_UPDATE\_LOGIC\_INSPECTION.md



\## Purpose



Phase 10M inspects the exact update logic in the validated baseline solver before implementing any selectable right-hand-side or one-step update path.



This phase is documentation-only.



This phase does not modify SpectralSolver.



This phase does not modify SelectableAdvectionSolver.



This phase does not run a simulation.



This phase does not enable SelectableAdvectionSolver.run().



This phase does not prove turbulence.



This phase does not prove k^-3 scaling.



\## Files Inspected



The inspected baseline file is:



project/solver/spectral\_solver.py



The selectable scaffold file is not modified in this phase:



project/solver/selectable\_advection\_solver.py



\## Baseline Class



The baseline class is:



SpectralSolver



Constructor signature:



SpectralSolver(nx, ny, Re, run\_path, dt=0.005, steps=20000)



The constructor requires a square grid:



nx == ny



The constructor initializes:



\- N

\- dt

\- nu = 1.0 / Re

\- steps

\- L = 2\*pi

\- dx = L / N

\- run\_path

\- grid arrays X and Y

\- wavenumbers k, kx, ky

\- k2 = kx^2 + ky^2

\- k2\[0, 0] = 1.0

\- 2/3 dealiasing mask

\- vorticity field w

\- diagnostics\_history



\## Grid and Wavenumber Setup



The baseline solver uses:



L = 2\*pi



dx = L / N



x = linspace(0, L, N, endpoint=False)



X, Y = meshgrid(x, x)



The wavenumbers are:



k = fftfreq(N, d=dx) \* 2\*pi



kx, ky = meshgrid(k, k)



The spectral squared wavenumber is:



k2 = kx^2 + ky^2



The zero mode is protected by:



k2\[0, 0] = 1.0



This avoids division by zero in the streamfunction solve.



\## Dealiasing Setup



The baseline solver defines:



kmax = max(abs(k))



deal = abs(kx) < (2/3) \* kmax and abs(ky) < (2/3) \* kmax



This is a 2/3 spectral mask.



The mask is applied after the RK2-style update, not inside the advection calculation.



\## Streamfunction Method



The streamfunction is computed by:



psi = ifft2(-fft2(w) / k2).real



This is a spectral Poisson solve.



\## Velocity Method



The velocity is computed from the streamfunction by FFT derivatives:



psihat = fft2(psi)



u = ifft2(1j \* ky \* psihat).real



v = ifft2(-1j \* kx \* psihat).real



Therefore the project velocity convention is:



u = d psi / dy



v = - d psi / dx



\## Diffusion Method



The spectral diffusion operator is:



laplacian\_spectral(w) = ifft2(-nu \* k2 \* fft2(w)).real



This returns the viscous diffusion term directly.



\## Forcing Method



The baseline forcing is deterministic and low-wavenumber:



forcing() = 0.01 \* sin(2X) \* cos(2Y)



The forcing does not depend on time or w.



The same forcing is used in both RK2 stages.



\## Energy Method



The kinetic energy diagnostic is:



energy(u, v) = 0.5 \* mean(u\*u + v\*v)



\## Spectrum Method



The kinetic energy spectrum diagnostic uses:



compute\_kinetic\_energy\_spectrum\_from\_vorticity(w, kx, ky)



The diagnostic writes:



\- k

\- E(k)

\- mode\_count



to:



spectrum.csv



\## Baseline Nonlinear Advection



The baseline nonlinear advection uses centered finite differences.



For a field w:



wx = (roll(w, -1, axis=1) - roll(w, 1, axis=1)) / (2\*dx)



wy = (roll(w, -1, axis=0) - roll(w, 1, axis=0)) / (2\*dx)



adv = u \* wx + v \* wy



This means the baseline active nonlinear method is:



fd\_centered



The method family remains:



mixed\_spectral\_finite\_difference



\## Baseline Update Convention



The baseline time update convention is:



d omega / dt = -adv + diffusion + forcing



where:



adv = u \* omega\_x + v \* omega\_y



The solver computes:



k1 = -adv(w) + laplacian\_spectral(w) + forcing()



Then:



w1 = w + dt \* k1



Then it recomputes the same right-hand-side at w1:



k2 = -adv(w1) + laplacian\_spectral(w1) + forcing()



Then:



w\_new = w + 0.5 \* dt \* (k1 + k2)



This is an RK2 / Heun-style update.



\## Baseline RK2-Style Sequence



The exact update sequence inside SpectralSolver.run() is:



1\. Compute psi from self.w.

2\. Compute u, v from psi.

3\. Compute wx and wy from self.w using centered finite differences.

4\. Compute adv = u \* wx + v \* wy.

5\. Compute k1 = -adv + laplacian\_spectral(self.w) + forcing().

6\. Compute w1 = self.w + dt \* k1.

7\. Compute psi from w1.

8\. Compute u, v from psi.

9\. Compute wx and wy from w1 using centered finite differences.

10\. Compute adv = u \* wx + v \* wy.

11\. Compute k2 = -adv + laplacian\_spectral(w1) + forcing().

12\. Compute w\_new = self.w + 0.5 \* dt \* (k1 + k2).

13\. Apply the 2/3 dealiasing mask to fft2(w\_new).

14\. Set self.w = ifft2(masked fft2(w\_new)).real.

15\. Compute enstrophy from the updated self.w.

16\. Every 500 steps, compute diagnostics and write CSV files.



\## Dealiasing Placement



Dealiasing is applied after the full RK2-style update.



The baseline does not apply the dealiasing mask to:



\- wx

\- wy

\- adv

\- k1

\- w1

\- k2



The mask is applied only to w\_new before assigning self.w.



Exact placement:



W = fft2(w\_new)



W \*= self.deal



self.w = ifft2(W).real



\## Diagnostics Placement



After self.w is updated and dealiased, the baseline computes:



Z = 0.5 \* mean(self.w \* self.w)



Every 500 steps, the baseline computes:



\- psi from self.w

\- u, v from psi

\- E = energy(u, v)

\- k\_bins, Ek, mode\_counts = energy\_spectrum(self.w)

\- E\_k4 from the spectrum if k=4 exists



The baseline prints:



step, E, Z, E(k=4)



The baseline appends diagnostics to diagnostics\_history.



The baseline writes:



diagnostics.csv



and:



spectrum.csv



inside run\_path.



\## Mutation Behavior



The baseline run loop mutates:



self.w



The mutation occurs after each RK2-style update and dealiasing step.



Intermediate arrays are local:



\- psi

\- u

\- v

\- wx

\- wy

\- adv

\- k1

\- w1

\- k2

\- w\_new

\- W



The baseline run method is not a pure function.



For selectable equivalence work, a separate pure helper should be created first before enabling any run behavior.



\## Implication for SelectableAdvectionSolver



The selectable scaffold currently has:



compute\_advection(w)



but does not yet have:



compute\_rhs\_selectable(w)



or:



step\_once\_selectable(w)



and run() is intentionally disabled.



This remains correct.



\## Required Selectable RHS Design



A future selectable RHS helper should compute:



rhs = -compute\_advection(w) + laplacian\_spectral(w) + forcing()



For fd\_centered, this should reproduce the baseline stage RHS.



For pseudo\_spectral, it should use pseudo-spectral advection.



For arakawa, it should use Arakawa advection.



No method should special-case the time-update sign.



All advection functions return adv.



The RHS applies -adv.



\## Recommended Phase 10N Implementation Target



Phase 10N should implement:



compute\_rhs\_selectable(self, w)



inside:



project/solver/selectable\_advection\_solver.py



The method should:



1\. Validate that w has the expected solver shape.

2\. Compute adv = self.compute\_advection(w).

3\. Compute diffusion = self.laplacian\_spectral(w).

4\. Compute force = self.forcing().

5\. Return rhs = -adv + diffusion + force.

6\. Not mutate input w.

7\. Not mutate solver.w.

8\. Not advance time.

9\. Not write diagnostics.

10\. Not enable run().



This is safer than implementing a full one-step update immediately.



\## Recommended Phase 10N.1 Audit Target



Phase 10N.1 should audit fd\_centered RHS equivalence.



The audit should compare:



baseline-style RHS computed directly from SpectralSolver logic



against:



SelectableAdvectionSolver(advection\_method="fd\_centered").compute\_rhs\_selectable(w)



The test should use:



\- N=64

\- N=128

\- single\_mode\_k2\_2

\- low\_mode\_pair

\- phase6d\_like\_multimode

\- higher\_smooth\_multimode



The audit should check:



\- finite output

\- real output

\- input w unchanged

\- solver.w unchanged

\- RHS L2 norm

\- RHS difference L2

\- RHS difference max\_abs

\- relative error

\- cosine similarity

\- SpectralSolver file has no git diff

\- SelectableAdvectionSolver.run() remains disabled



\## Recommended Phase 10O Target



Only after RHS equivalence passes, Phase 10O should implement or audit one-step equivalence.



A one-step selectable helper would need to reproduce:



k1 = rhs(w)



w1 = w + dt\*k1



k2 = rhs(w1)



w\_new = w + 0.5\*dt\*(k1+k2)



then apply the same 2/3 dealiasing mask.



Phase 10O should compare fd\_centered selectable one-step output against baseline one-step logic.



\## What Must Not Happen Yet



Do not enable SelectableAdvectionSolver.run().



Do not replace SpectralSolver.



Do not modify project/solver/spectral\_solver.py.



Do not make Arakawa the default.



Do not run long simulations.



Do not run turbulence tests.



Do not make k^-3 claims.



Do not claim production readiness.



\## Decision



Phase 10M decision:



Proceed to Phase 10N RHS scaffold implementation.



Do not implement full one-step update yet.



Do not enable run().



Do not run Arakawa time evolution yet.



\## Final Result



Phase 10M baseline update logic inspection:



PASS



The baseline update logic has been inspected and documented.



The next phase should implement only:



compute\_rhs\_selectable(self, w)



inside SelectableAdvectionSolver.



SpectralSolver must remain unchanged.

