"""
Standalone nonlinear advection operators for Raj-Sanghera-Project.

Phase 10C purpose:
- Preserve project/solver/spectral_solver.py as the validated baseline.
- Provide standalone advection operators for diagnostics and future comparison.
- Do not modify production solver behavior.

Current project sign convention:
    u = d psi / dy
    v = - d psi / dx

    adv = u * omega_x + v * omega_y

The solver update uses:
    d omega / dt = -adv + diffusion + forcing

Therefore all advection operators in this file return adv, not -adv.
"""

import numpy as np


def ensure_real_array(field):
    """Return field as a real NumPy array."""
    arr = np.asarray(field)

    if not np.isrealobj(arr):
        arr = arr.real

    return arr.astype(float, copy=False)


def l2_norm(field):
    """Root-mean-square L2-style norm."""
    arr = np.asarray(field)
    return float(np.sqrt(np.mean(arr * arr)))


def max_abs(field):
    """Maximum absolute value."""
    return float(np.max(np.abs(np.asarray(field))))


def apply_dealias_mask(solver, field):
    """
    Apply the solver's 2/3 spectral dealiasing mask to a physical-space field.

    This is a diagnostic helper. It does not modify the solver.
    """
    arr = ensure_real_array(field)

    if arr.shape != solver.w.shape:
        raise ValueError(f"Shape mismatch: field={arr.shape}, expected={solver.w.shape}")

    field_hat = np.fft.fft2(arr)
    field_hat *= solver.deal
    return np.fft.ifft2(field_hat).real


def velocity_from_vorticity(solver, w):
    """
    Compute velocity from vorticity using the solver's streamfunction and velocity methods.
    """
    arr = ensure_real_array(w)

    if arr.shape != solver.w.shape:
        raise ValueError(f"Shape mismatch: w={arr.shape}, expected={solver.w.shape}")

    psi = solver.streamfunction(arr)
    u, v = solver.velocity(psi)

    return u, v


def vorticity_grad_fd_centered(solver, w):
    """
    Centered finite-difference vorticity gradients.

    This matches the current active SpectralSolver advection gradient method.
    """
    arr = ensure_real_array(w)

    if arr.shape != solver.w.shape:
        raise ValueError(f"Shape mismatch: w={arr.shape}, expected={solver.w.shape}")

    wx = (np.roll(arr, -1, 1) - np.roll(arr, 1, 1)) / (2 * solver.dx)
    wy = (np.roll(arr, -1, 0) - np.roll(arr, 1, 0)) / (2 * solver.dx)

    return wx, wy


def vorticity_grad_pseudo_spectral(solver, w):
    """
    Pseudo-spectral vorticity gradients using FFT derivatives.
    """
    arr = ensure_real_array(w)

    if arr.shape != solver.w.shape:
        raise ValueError(f"Shape mismatch: w={arr.shape}, expected={solver.w.shape}")

    w_hat = np.fft.fft2(arr)

    wx = np.fft.ifft2(1j * solver.kx * w_hat).real
    wy = np.fft.ifft2(1j * solver.ky * w_hat).real

    return wx, wy


def advection_fd_centered(solver, w):
    """
    Current baseline nonlinear advection:

        adv = u * omega_x + v * omega_y

    with omega_x and omega_y computed using centered finite differences.

    This should match the advection logic currently embedded in SpectralSolver.run().
    """
    arr = ensure_real_array(w)
    u, v = velocity_from_vorticity(solver, arr)
    wx, wy = vorticity_grad_fd_centered(solver, arr)

    adv = u * wx + v * wy

    return adv.real


def advection_pseudo_spectral(solver, w, dealias_product=False):
    """
    Pseudo-spectral nonlinear advection diagnostic:

        adv = u * omega_x + v * omega_y

    with omega_x and omega_y computed using FFT derivatives.

    If dealias_product=True, the final physical-space nonlinear product is
    transformed, masked by solver.deal, and transformed back.

    This is a diagnostic operator. It does not modify the solver.
    """
    arr = ensure_real_array(w)
    u, v = velocity_from_vorticity(solver, arr)
    wx, wy = vorticity_grad_pseudo_spectral(solver, arr)

    adv = u * wx + v * wy
    adv = adv.real

    if dealias_product:
        adv = apply_dealias_mask(solver, adv)

    return adv


def jacobian_arakawa_periodic(psi, w, dx):
    """
    Placeholder for a future Arakawa Jacobian implementation.

    Phase 10C intentionally does not implement Arakawa yet.

    Reason:
    - Arakawa sign convention must be handled carefully.
    - The project currently uses adv = u*omega_x + v*omega_y.
    - A standard Jacobian J(psi, omega) may have the opposite sign depending on convention.
    - Implementation should be introduced in a dedicated audited phase.
    """
    raise NotImplementedError(
        "Arakawa Jacobian is intentionally not implemented in Phase 10C."
    )


def advection_arakawa(solver, w):
    """
    Placeholder for future Arakawa advection diagnostic.

    This function intentionally raises NotImplementedError until an audited
    Arakawa implementation phase is created.
    """
    raise NotImplementedError(
        "Arakawa advection is intentionally not implemented in Phase 10C."
    )


def compare_advection_operators(solver, w, dealias_pseudo_spectral=False):
    """
    Compare baseline centered finite-difference advection against
    pseudo-spectral derivative advection on the same vorticity field.

    Returns a dictionary suitable for CSV output.
    """
    arr = ensure_real_array(w)

    fd_adv = advection_fd_centered(solver, arr)
    ps_adv = advection_pseudo_spectral(
        solver,
        arr,
        dealias_product=dealias_pseudo_spectral,
    )

    diff = fd_adv - ps_adv

    fd_l2 = l2_norm(fd_adv)
    ps_l2 = l2_norm(ps_adv)
    diff_l2 = l2_norm(diff)

    if ps_l2 > 0:
        relative_l2_error = float(diff_l2 / ps_l2)
    else:
        relative_l2_error = np.nan

    fd_flat = fd_adv.ravel()
    ps_flat = ps_adv.ravel()

    denom = np.linalg.norm(fd_flat) * np.linalg.norm(ps_flat)

    if denom > 0:
        cosine_similarity = float(np.dot(fd_flat, ps_flat) / denom)
    else:
        cosine_similarity = np.nan

    finite_all = (
        np.isfinite(arr).all()
        and np.isfinite(fd_adv).all()
        and np.isfinite(ps_adv).all()
        and np.isfinite(diff).all()
    )

    return {
        "finite_all": "PASS" if finite_all else "FAIL",
        "fd_adv_l2": fd_l2,
        "pseudo_spectral_adv_l2": ps_l2,
        "diff_l2": diff_l2,
        "relative_l2_error_vs_pseudo_spectral": relative_l2_error,
        "fd_adv_max_abs": max_abs(fd_adv),
        "pseudo_spectral_adv_max_abs": max_abs(ps_adv),
        "diff_max_abs": max_abs(diff),
        "cosine_similarity": cosine_similarity,
        "dealias_pseudo_spectral_product": bool(dealias_pseudo_spectral),
    }