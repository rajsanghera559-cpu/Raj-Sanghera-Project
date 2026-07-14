"""
Selectable advection solver scaffold for Raj-Sanghera-Project.

Phase 10K purpose:
- Create a separate selectable-advection solver variant.
- Preserve project/solver/spectral_solver.py unchanged.
- Reuse the validated SpectralSolver setup where possible.
- Allow explicit nonlinear advection method selection for diagnostics.
- Do not claim production readiness.
- Do not run long simulations.
- Do not claim turbulence or k^-3 scaling.

Phase 10N addition:
- Add compute_rhs_selectable(self, w).
- Preserve run() as disabled.
- Do not enable production time evolution.
- Do not modify SpectralSolver.

Phase 10P addition:
- Add step_once_selectable(self, w).
- Preserve run() as disabled.
- Do not enable production time evolution.
- Do not modify SpectralSolver.

Phase 11K addition:
- Add run_selectable_diagnostic(...).
- Keep run() disabled.
- Keep the selectable pathway explicitly diagnostic.
- Do not modify SpectralSolver.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.advection_operators import (
    ensure_real_array,
    advection_fd_centered,
    advection_pseudo_spectral,
    advection_arakawa,
)


class SelectableAdvectionSolver(SpectralSolver):
    """
    Separate selectable-advection solver scaffold.

    This class inherits grid setup, streamfunction, velocity, and baseline
    numerical infrastructure from SpectralSolver, but it does not modify
    SpectralSolver and does not replace validated baseline behavior.

    Supported advection methods:

        fd_centered
        pseudo_spectral
        arakawa

    The default is fd_centered to match the current baseline method.
    """

    SUPPORTED_ADVECTION_METHODS = (
        "fd_centered",
        "pseudo_spectral",
        "arakawa",
    )

    DEFAULT_ADVECTION_METHOD = "fd_centered"

    def __init__(self, *args, advection_method="fd_centered", **kwargs):
        """
        Initialize a selectable-advection solver scaffold.

        Parameters
        ----------
        *args, **kwargs:
            Passed through to SpectralSolver.

        advection_method:
            One of:
                fd_centered
                pseudo_spectral
                arakawa
        """
        self.advection_method = self.validate_advection_method(advection_method)

        super().__init__(*args, **kwargs)

        self.solver_variant = "selectable_advection"
        self.solver_class = "SelectableAdvectionSolver"
        self.baseline_solver_class = "SpectralSolver"
        self.production_baseline_modified = False

    @classmethod
    def validate_advection_method(cls, advection_method):
        """
        Validate and normalize the requested advection method.

        No aliases are allowed in the first scaffold version.
        """
        if not isinstance(advection_method, str):
            raise ValueError(
                "advection_method must be a string. "
                f"Received: {type(advection_method).__name__}"
            )

        method = advection_method.strip().lower()

        if method not in cls.SUPPORTED_ADVECTION_METHODS:
            allowed = ", ".join(cls.SUPPORTED_ADVECTION_METHODS)
            raise ValueError(
                f"Unsupported advection_method={advection_method!r}. "
                f"Allowed values: {allowed}"
            )

        return method

    @classmethod
    def supported_advection_methods(cls):
        """
        Return supported method names.
        """
        return tuple(cls.SUPPORTED_ADVECTION_METHODS)

    def compute_advection(self, w):
        """
        Compute nonlinear advection using the selected method.

        All operators return:

            adv = u * omega_x + v * omega_y

        The time update convention remains:

            d omega / dt = -adv + diffusion + forcing

        This method does not mutate the input field and does not mutate solver.w.
        """
        if self.advection_method == "fd_centered":
            return advection_fd_centered(self, w)

        if self.advection_method == "pseudo_spectral":
            return advection_pseudo_spectral(
                self,
                w,
                dealias_product=False,
            )

        if self.advection_method == "arakawa":
            return advection_arakawa(self, w)

        raise ValueError(
            f"Unsupported advection_method={self.advection_method!r}. "
            "This should not occur if validation succeeded."
        )

    def compute_rhs_selectable(self, w):
        """
        Compute the selectable right-hand side for a vorticity field.

        Project convention:

            d omega / dt = -adv + diffusion + forcing

        where every advection operator returns:

            adv = u * omega_x + v * omega_y

        This method:
        - validates shape
        - computes selected nonlinear advection
        - computes spectral diffusion
        - adds baseline forcing
        - returns rhs
        - does not mutate input w
        - does not mutate solver.w
        - does not advance time
        - does not write files
        - does not enable run()
        """
        arr = ensure_real_array(w)

        if arr.shape != self.w.shape:
            raise ValueError(f"Shape mismatch: w={arr.shape}, expected={self.w.shape}")

        adv = self.compute_advection(arr)
        diffusion = self.laplacian_spectral(arr)
        force = self.forcing()

        if force.shape != arr.shape:
            raise ValueError(
                f"Forcing shape mismatch: forcing={force.shape}, expected={arr.shape}"
            )

        rhs = -adv + diffusion + force

        return rhs.real

    def step_once_selectable(self, w):
        """
        Compute one RK2-style selectable update without mutating solver state.

        This mirrors the baseline SpectralSolver.run() one-step structure:

            k1 = rhs(w)
            w1 = w + dt * k1
            k2 = rhs(w1)
            w_new = w + 0.5 * dt * (k1 + k2)

        Then it applies the same post-step 2/3 spectral dealiasing mask used
        by SpectralSolver.run().

        This method:
        - validates shape through compute_rhs_selectable
        - does not mutate input w
        - does not mutate solver.w
        - does not write diagnostics
        - does not enable run()
        """
        arr = ensure_real_array(w)

        if arr.shape != self.w.shape:
            raise ValueError(f"Shape mismatch: w={arr.shape}, expected={self.w.shape}")

        k1 = self.compute_rhs_selectable(arr)
        w1 = arr + self.dt * k1

        k2 = self.compute_rhs_selectable(w1)
        w_new = arr + 0.5 * self.dt * (k1 + k2)

        W = np.fft.fft2(w_new)
        W *= self.deal

        return np.fft.ifft2(W).real

    def _state_diagnostics_record(self, step, w):
        """
        Build one diagnostic record for a vorticity field.
        """
        arr = ensure_real_array(w)

        if arr.shape != self.w.shape:
            raise ValueError(f"Shape mismatch: w={arr.shape}, expected={self.w.shape}")

        psi = self.streamfunction(arr)
        u, v = self.velocity(psi)

        energy = float(self.energy(u, v))
        enstrophy = float(0.5 * np.mean(arr * arr))

        return {
            "step": int(step),
            "time": float(step * self.dt),
            "rms_vorticity": float(np.sqrt(np.mean(arr * arr))),
            "kinetic_energy": energy,
            "enstrophy": enstrophy,
            "max_abs_vorticity": float(np.max(np.abs(arr))),
            "finite": bool(np.isfinite(arr).all()),
            "real": bool(np.isrealobj(arr)),
        }

    def _spectrum_records(self, w):
        """
        Build final spectrum records from a vorticity field.
        """
        arr = ensure_real_array(w)

        if arr.shape != self.w.shape:
            raise ValueError(f"Shape mismatch: w={arr.shape}, expected={self.w.shape}")

        k_bins, Ek, mode_counts = self.energy_spectrum(arr)

        records = []

        for k, energy, count in zip(k_bins, Ek, mode_counts):
            records.append(
                {
                    "k": float(k),
                    "E_k": float(energy),
                    "mode_count": int(count),
                }
            )

        return records

    def _write_json(self, path, payload):
        """
        Write JSON using ordinary Python scalar values.
        """
        with Path(path).open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, sort_keys=True)

    def run_selectable_diagnostic(
        self,
        initial_w,
        steps=None,
        log_every=100,
        write_outputs=True,
        save_final_state=True,
        save_initial_state=True,
    ):
        """
        Run a selectable diagnostic loop without enabling production run().

        This method is explicitly diagnostic. It repeatedly calls
        step_once_selectable(w) using a local copy of the supplied initial
        vorticity field.

        This method:
        - requires initial_w
        - validates initial_w shape
        - does not mutate initial_w
        - does not mutate solver.w
        - does not call SpectralSolver.run()
        - does not call SelectableAdvectionSolver.run()
        - writes clearly labeled selectable outputs if requested
        - returns metadata, diagnostics, spectrum, initial_w, and final_w

        It is not a production simulation interface.
        It does not make turbulence or k^-3 claims.
        """
        if steps is None:
            steps = self.steps

        if not isinstance(steps, int):
            raise ValueError(f"steps must be an integer. Received: {type(steps).__name__}")

        if steps < 0:
            raise ValueError(f"steps must be nonnegative. Received: {steps}")

        if not isinstance(log_every, int):
            raise ValueError(
                f"log_every must be an integer. Received: {type(log_every).__name__}"
            )

        if log_every <= 0:
            raise ValueError(f"log_every must be positive. Received: {log_every}")

        arr = ensure_real_array(initial_w)

        if arr.shape != self.w.shape:
            raise ValueError(f"Shape mismatch: initial_w={arr.shape}, expected={self.w.shape}")

        initial_copy = arr.copy()
        w = arr.copy()
        solver_w_before = self.w.copy()

        initial_record = self._state_diagnostics_record(0, w)
        diagnostics = [initial_record]

        for step in range(1, steps + 1):
            w_before = w.copy()
            w_next = self.step_once_selectable(w)

            if not np.allclose(w, w_before, rtol=0.0, atol=0.0):
                raise RuntimeError(
                    "step_once_selectable mutated the local input field unexpectedly."
                )

            w = w_next

            if step % log_every == 0 or step == steps:
                diagnostics.append(self._state_diagnostics_record(step, w))

        solver_w_unchanged = np.allclose(
            self.w,
            solver_w_before,
            rtol=0.0,
            atol=0.0,
        )

        if not solver_w_unchanged:
            raise RuntimeError("run_selectable_diagnostic mutated solver.w unexpectedly.")

        initial_w_unchanged = np.allclose(
            arr,
            initial_copy,
            rtol=0.0,
            atol=0.0,
        )

        if not initial_w_unchanged:
            raise RuntimeError("run_selectable_diagnostic mutated initial_w unexpectedly.")

        final_record = self._state_diagnostics_record(steps, w)
        spectrum_records = self._spectrum_records(w)

        spectrum_energy_sum = float(sum(row["E_k"] for row in spectrum_records))
        direct_energy = final_record["kinetic_energy"]
        spectrum_direct_relative_error = abs(spectrum_energy_sum - direct_energy) / max(
            abs(direct_energy),
            1e-300,
        )

        initial_energy = initial_record["kinetic_energy"]
        initial_enstrophy = initial_record["enstrophy"]

        final_energy = final_record["kinetic_energy"]
        final_enstrophy = final_record["enstrophy"]

        relative_energy_change = (final_energy - initial_energy) / max(
            abs(initial_energy),
            1e-300,
        )
        relative_enstrophy_change = (final_enstrophy - initial_enstrophy) / max(
            abs(initial_enstrophy),
            1e-300,
        )

        force = self.forcing()

        forcing_shape_ok = force.shape == self.w.shape
        forcing_finite = bool(np.isfinite(force).all())
        forcing_real = bool(np.isrealobj(force))
        forcing_rms = float(np.sqrt(np.mean(force * force)))
        forcing_max_abs = float(np.max(np.abs(force)))

        metadata = self.selectable_advection_metadata()
        metadata.update(
            {
                "diagnostic_run_method": "run_selectable_diagnostic",
                "selectable_run_type": "diagnostic",
                "production_ready": False,
                "run_method_enabled": False,
                "write_outputs": bool(write_outputs),
                "save_initial_state": bool(save_initial_state),
                "save_final_state": bool(save_final_state),
                "steps": int(steps),
                "log_every": int(log_every),
                "dt": float(self.dt),
                "final_time": float(steps * self.dt),
                "N": int(self.N),
                "Re": float(1.0 / self.nu) if self.nu != 0 else float("inf"),
                "nu": float(self.nu),
                "run_path": str(self.run_path),
                "initial_rms": float(initial_record["rms_vorticity"]),
                "final_rms": float(final_record["rms_vorticity"]),
                "initial_energy": float(initial_energy),
                "final_energy": float(final_energy),
                "relative_energy_change": float(relative_energy_change),
                "initial_enstrophy": float(initial_enstrophy),
                "final_enstrophy": float(final_enstrophy),
                "relative_enstrophy_change": float(relative_enstrophy_change),
                "forcing_shape_ok": bool(forcing_shape_ok),
                "forcing_finite": bool(forcing_finite),
                "forcing_real": bool(forcing_real),
                "forcing_rms": float(forcing_rms),
                "forcing_max_abs": float(forcing_max_abs),
                "spectrum_energy_sum": float(spectrum_energy_sum),
                "spectrum_direct_relative_error": float(spectrum_direct_relative_error),
                "solver_w_unchanged": bool(solver_w_unchanged),
                "initial_w_unchanged": bool(initial_w_unchanged),
            }
        )

        summary = {
            "advection_method": self.advection_method,
            "steps": int(steps),
            "dt": float(self.dt),
            "final_time": float(steps * self.dt),
            "initial_rms": float(initial_record["rms_vorticity"]),
            "final_rms": float(final_record["rms_vorticity"]),
            "initial_energy": float(initial_energy),
            "final_energy": float(final_energy),
            "relative_energy_change": float(relative_energy_change),
            "initial_enstrophy": float(initial_enstrophy),
            "final_enstrophy": float(final_enstrophy),
            "relative_enstrophy_change": float(relative_enstrophy_change),
            "spectrum_energy_sum": float(spectrum_energy_sum),
            "spectrum_direct_relative_error": float(spectrum_direct_relative_error),
            "finite_final": bool(final_record["finite"]),
            "real_final": bool(final_record["real"]),
            "solver_w_unchanged": bool(solver_w_unchanged),
            "initial_w_unchanged": bool(initial_w_unchanged),
            "production_ready": False,
            "turbulence_claim": False,
            "k_minus_3_claim": False,
        }

        output_paths = {}

        if write_outputs:
            self.run_path.mkdir(parents=True, exist_ok=True)

            metadata_path = self.run_path / "selectable_metadata.json"
            diagnostics_path = self.run_path / "selectable_diagnostics.csv"
            spectrum_path = self.run_path / "selectable_spectrum.csv"
            summary_path = self.run_path / "selectable_run_summary.json"

            self._write_json(metadata_path, metadata)
            pd.DataFrame(diagnostics).to_csv(diagnostics_path, index=False)
            pd.DataFrame(spectrum_records).to_csv(spectrum_path, index=False)
            self._write_json(summary_path, summary)

            output_paths.update(
                {
                    "metadata": str(metadata_path),
                    "diagnostics": str(diagnostics_path),
                    "spectrum": str(spectrum_path),
                    "summary": str(summary_path),
                }
            )

            if save_initial_state:
                initial_state_path = self.run_path / "selectable_initial_state.npy"
                np.save(initial_state_path, initial_copy)
                output_paths["initial_state"] = str(initial_state_path)

            if save_final_state:
                final_state_path = self.run_path / "selectable_final_state.npy"
                np.save(final_state_path, w)
                output_paths["final_state"] = str(final_state_path)

        result = {
            "metadata": metadata,
            "summary": summary,
            "diagnostics": diagnostics,
            "spectrum": spectrum_records,
            "initial_w": initial_copy,
            "final_w": w.copy(),
            "output_paths": output_paths,
        }

        return result

    def selectable_advection_metadata(self):
        """
        Return metadata describing the selectable-advection scaffold.

        This is intentionally separate from any production metadata writer.
        Future phases may integrate this into audited run outputs.
        """
        return {
            "solver_variant": "selectable_advection",
            "solver_class": "SelectableAdvectionSolver",
            "baseline_solver_class": "SpectralSolver",
            "advection_method": self.advection_method,
            "advection_operator_file": "project/solver/advection_operators.py",
            "rhs_method": "compute_rhs_selectable",
            "rhs_status": "diagnostic_scaffold",
            "step_method": "step_once_selectable",
            "step_status": "diagnostic_scaffold",
            "diagnostic_run_method": "run_selectable_diagnostic",
            "diagnostic_run_status": "diagnostic_scaffold",
            "production_baseline_modified": False,
            "method_family": "mixed_spectral_selectable_advection",
            "streamfunction_method": "spectral",
            "velocity_method": "spectral",
            "diffusion_method": "spectral",
            "forcing_method": "inherited_baseline_forcing",
            "timestep_method": "RK2-style",
            "dealiasing_method": "post-step 2/3 spectral mask",
            "run_enabled": False,
            "production_ready": False,
            "arakawa_status": "diagnostic_candidate",
            "turbulence_claim": False,
            "k_minus_3_claim": False,
        }

    def metadata_dict(self):
        """
        Return selectable-advection metadata.

        This method is intentionally simple in Phase 10K/10N/10P/11K.
        It avoids assuming details of SpectralSolver's internal metadata format.
        """
        return self.selectable_advection_metadata()

    def run(self, *args, **kwargs):
        """
        Disable inherited production run behavior for this scaffold.

        Reason:
        The selectable-advection time-evolution loop has not yet been audited
        as a production run path.

        Future phases must explicitly implement and validate selectable
        production-style behavior before run() is allowed.
        """
        raise NotImplementedError(
            "SelectableAdvectionSolver.run() is intentionally disabled. "
            "Use run_selectable_diagnostic(...) for explicit diagnostic runs. "
            "This class is not production-ready and does not make turbulence "
            "or k^-3 claims."
        )