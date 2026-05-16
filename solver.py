import numpy as np

# ============================================================
# PARAMETERS
# ============================================================
N = 128
dt = 0.005
nu = 0.01
steps = 20000
L = 2 * np.pi
dx = L / N

# ============================================================
# GRID + WAVENUMBERS
# ============================================================
x = np.linspace(0, L, N, endpoint=False)
X, Y = np.meshgrid(x, x)

k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
kx, ky = np.meshgrid(k, k)
k2 = kx**2 + ky**2
k2[0, 0] = 1.0

# ============================================================
# 2/3 DEALIASING MASK (Tier 3)
# ============================================================
kmax = np.max(np.abs(k))
deal = (np.abs(kx) < (2/3) * kmax) & (np.abs(ky) < (2/3) * kmax)

# ============================================================
# INITIAL CONDITION
# ============================================================
w = np.zeros((N, N))

# ============================================================
# OPERATORS
# ============================================================

def streamfunction(w):
    """FFT Poisson solve: ψ = -∇⁻² ω"""
    return np.fft.ifft2(-np.fft.fft2(w) / k2).real


def velocity(psi):
    """u = ∂y ψ, v = -∂x ψ"""
    psihat = np.fft.fft2(psi)
    u = np.fft.ifft2(1j * ky * psihat).real
    v = np.fft.ifft2(-1j * kx * psihat).real
    return u, v


def laplacian_spectral(w):
    """Spectral diffusion operator (Tier 2 consistency fix)"""
    return np.fft.ifft2(-nu * k2 * np.fft.fft2(w)).real


def jacobian(a, b):
    """Physical-space nonlinear term"""
    ax = (np.roll(a, -1, 1) - np.roll(a, 1, 1)) / (2 * dx)
    ay = (np.roll(a, -1, 0) - np.roll(a, 1, 0)) / (2 * dx)
    bx = (np.roll(b, -1, 1) - np.roll(b, 1, 1)) / (2 * dx)
    by = (np.roll(b, -1, 0) - np.roll(b, 1, 0)) / (2 * dx)
    return ax * by - ay * bx


# ============================================================
# TIER 1: FORCING (steady turbulence driver)
# ============================================================

def forcing(X, Y):
    """Low-wavenumber energy injection"""
    return 0.01 * np.sin(2 * X) * np.cos(2 * Y)


# ============================================================
# TIER 2: ENERGY DIAGNOSTIC
# ============================================================

def energy(u, v):
    return 0.5 * np.mean(u*u + v*v)


# ============================================================
# TIER 2: ENERGY SPECTRUM (basic radial binning)
# ============================================================

def energy_spectrum(w):
    w_hat = np.fft.fft2(w)
    E = np.abs(w_hat)**2

    k_mag = np.sqrt(kx**2 + ky**2).flatten()
    E_flat = E.flatten()

    bins = np.arange(1, N//2)
    Ek = np.zeros_like(bins, dtype=float)

    for i, kb in enumerate(bins):
        mask = (k_mag >= kb - 0.5) & (k_mag < kb + 0.5)
        Ek[i] = np.sum(E_flat[mask])

    return bins, Ek


# ============================================================
# TIER 1–2–3 CORE TIME INTEGRATION (RK2 + forcing + dealiasing)
# ============================================================

for n in range(steps):

    # ----------------------------
    # RK2 STAGE 1
    # ----------------------------
    psi = streamfunction(w)
    u, v = velocity(psi)

    wx = (np.roll(w, -1, 1) - np.roll(w, 1, 1)) / (2 * dx)
    wy = (np.roll(w, -1, 0) - np.roll(w, 1, 0)) / (2 * dx)

    adv = u * wx + v * wy

    k1 = -adv + laplacian_spectral(w) + forcing(X, Y)
    w1 = w + dt * k1

    # ----------------------------
    # RK2 STAGE 2
    # ----------------------------
    psi = streamfunction(w1)
    u, v = velocity(psi)

    wx = (np.roll(w1, -1, 1) - np.roll(w1, 1, 1)) / (2 * dx)
    wy = (np.roll(w1, -1, 0) - np.roll(w1, 1, 0)) / (2 * dx)

    adv = u * wx + v * wy

    k2 = -adv + laplacian_spectral(w1) + forcing(X, Y)

    # update
    w_new = w + 0.5 * dt * (k1 + k2)

    # ----------------------------
    # TIER 3: DEALIASING
    # ----------------------------
    W = np.fft.fft2(w_new)
    W *= deal
    w = np.fft.ifft2(W).real

    # ----------------------------
    # DIAGNOSTICS (TIER 2)
    # ----------------------------
    if n % 500 == 0:
        psi = streamfunction(w)
        u, v = velocity(psi)

        E = energy(u, v)
        k_bins, Ek = energy_spectrum(w)

        print(f"step={n}, E={E:.6e}, E(k=4)={Ek[4]:.3e}")

print("Simulation complete.")