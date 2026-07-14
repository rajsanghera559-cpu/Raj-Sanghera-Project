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
    Compute the Arakawa Jacobian J(psi, w) on a periodic square grid.

    This function returns the standard Jacobian convention:

        J(psi, w) = psi_x * w_y - psi_y * w_x

    Project sign convention reminder:

        u = psi_y
        v = -psi_x

        adv = u * w_x + v * w_y
            = psi_y * w_x - psi_x * w_y
            = -J(psi, w)

    Therefore advection_arakawa(solver, w) returns -J_arakawa.

    Axis convention in this project:

        axis 1 is x
        axis 0 is y

    This function is standalone. It does not mutate psi, w, or solver state.
    """
    psi = ensure_real_array(psi)
    w = ensure_real_array(w)

    if psi.shape != w.shape:
        raise ValueError(f"Shape mismatch: psi={psi.shape}, w={w.shape}")

    if psi.ndim != 2:
        raise ValueError(f"Expected 2D arrays, got psi.ndim={psi.ndim}")

    if dx <= 0:
        raise ValueError(f"dx must be positive, got dx={dx}")

    # x-neighbors use axis=1.
    psi_xp = np.roll(psi, -1, axis=1)
    psi_xm = np.roll(psi, 1, axis=1)

    # y-neighbors use axis=0.
    psi_yp = np.roll(psi, -1, axis=0)
    psi_ym = np.roll(psi, 1, axis=0)

    # diagonal neighbors
    psi_xp_yp = np.roll(psi_xp, -1, axis=0)
    psi_xp_ym = np.roll(psi_xp, 1, axis=0)
    psi_xm_yp = np.roll(psi_xm, -1, axis=0)
    psi_xm_ym = np.roll(psi_xm, 1, axis=0)

    w_xp = np.roll(w, -1, axis=1)
    w_xm = np.roll(w, 1, axis=1)

    w_yp = np.roll(w, -1, axis=0)
    w_ym = np.roll(w, 1, axis=0)

    w_xp_yp = np.roll(w_xp, -1, axis=0)
    w_xp_ym = np.roll(w_xp, 1, axis=0)
    w_xm_yp = np.roll(w_xm, -1, axis=0)
    w_xm_ym = np.roll(w_xm, 1, axis=0)

    inv_12dx2 = 1.0 / (12.0 * dx * dx)

    # Arakawa's three-part averaged Jacobian.
    #
    # j1 approximates:
    #     psi_x * w_y - psi_y * w_x
    j1 = (
        (psi_xp - psi_xm) * (w_yp - w_ym)
        - (psi_yp - psi_ym) * (w_xp - w_xm)
    )

    j2 = (
        psi_xp * (w_xp_yp - w_xp_ym)
        - psi_xm * (w_xm_yp - w_xm_ym)
        - psi_yp * (w_xp_yp - w_xm_yp)
        + psi_ym * (w_xp_ym - w_xm_ym)
    )

    j3 = (
        w_yp * (psi_xp_yp - psi_xm_yp)
        - w_ym * (psi_xp_ym - psi_xm_ym)
        - w_xp * (psi_xp_yp - psi_xp_ym)
        + w_xm * (psi_xm_yp - psi_xm_ym)
    )

    return inv_12dx2 * (j1 + j2 + j3)


def advection_arakawa(solver, w):
    """
    Compute project-convention Arakawa advection:

        adv = u * w_x + v * w_y

    using the sign relation:

        adv = -J(psi, w)

    where jacobian_arakawa_periodic returns:

        J(psi, w) = psi_x * w_y - psi_y * w_x

    This function does not modify solver state.
    """
    arr = ensure_real_array(w)

    if arr.shape != solver.w.shape:
        raise ValueError(f"Shape mismatch: w={arr.shape}, expected={solver.w.shape}")

    psi = solver.streamfunction(arr)
    jacobian = jacobian_arakawa_periodic(psi, arr, solver.dx)

    return (-jacobian).real


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