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
"""

import numpy as np

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
            "production_baseline_modified": False,
            "method_family": "mixed_spectral_selectable_advection",
            "streamfunction_method": "spectral",
            "velocity_method": "spectral",
            "diffusion_method": "spectral",
            "forcing_method": "baseline_low_wavenumber_forcing",
            "timestep_method": "RK2-style",
            "dealiasing_method": "post-step 2/3 spectral mask",
            "run_enabled": False,
            "arakawa_status": "diagnostic_candidate",
            "turbulence_claim": False,
            "k_minus_3_claim": False,
        }

    def metadata_dict(self):
        """
        Return selectable-advection metadata.

        This method is intentionally simple in Phase 10K/10N/10P.
        It avoids assuming details of SpectralSolver's internal metadata format.
        """
        return self.selectable_advection_metadata()

    def run(self, *args, **kwargs):
        """
        Disable inherited production run behavior for this scaffold.

        Reason:
        The selectable-advection time-evolution loop has not yet been audited.

        Future phases must explicitly implement and validate selectable
        time evolution before any production-style runs are allowed.
        """
        raise NotImplementedError(
            "SelectableAdvectionSolver.run() is intentionally disabled. "
            "This scaffold only supports construction, metadata, "
            "compute_advection diagnostics, compute_rhs_selectable, "
            "and step_once_selectable. A selectable time-evolution loop "
            "must be implemented and audited in a later phase."
        )