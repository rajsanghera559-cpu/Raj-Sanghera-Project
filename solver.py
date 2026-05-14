import numpy as np
import argparse
import os
import csv
import matplotlib.pyplot as plt

# ----------------------------
# CLI PARAMETERS
# ----------------------------
parser = argparse.ArgumentParser(description="Harmonic forcing + shear solver")
parser.add_argument("--omega", type=float, default=1.0)
parser.add_argument("--A", type=float, default=0.01)
parser.add_argument("--N", type=int, default=128)
parser.add_argument("--dt", type=float, default=0.01)
parser.add_argument("--max_steps", type=int, default=100000)
args = parser.parse_args()

OMEGA = args.omega
A = args.A
N = args.N
dt = args.dt
MAX_STEPS = args.max_steps

# ----------------------------
# DOMAIN
# ----------------------------
L = 2 * np.pi
dx = L / N

x = np.linspace(0, L, N, endpoint=False)
y = np.linspace(0, L, N, endpoint=False)
X, Y = np.meshgrid(x, y)

# ----------------------------
# STATE VARIABLES
# ----------------------------
u = np.zeros((N, N))
v = np.zeros((N, N))

# ----------------------------
# OPERATORS
# ----------------------------
def shear(u):
    """Simple structured shear"""
    return 0.1 * np.roll(u, shift=1, axis=1)

def forcing(X, t, A, omega, kf=4.0):
    """Harmonic forcing: f(x,t) = A sin(kx - ωt)"""
    return A * np.sin(kf * X - omega * t)

def energy(u, v):
    return 0.5 * np.mean(u**2 + v**2)

# ----------------------------
# DIAGNOSTICS
# ----------------------------
def vorticity(u, v):
    du_dy = np.gradient(u, axis=0)
    dv_dx = np.gradient(v, axis=1)
    return dv_dx - du_dy

def helicity_proxy(u, v):
    omega = vorticity(u, v)
    return np.mean(u * omega)

def spectral_slope(u):
    """
    Estimate spectral slope from 2D FFT energy spectrum
    """
    U = np.fft.fft2(u)
    E = np.abs(U)**2

    # radial average (simplified)
    E_mean = np.mean(E, axis=0)

    k = np.arange(1, len(E_mean))
    spectrum = E_mean[1:]

    # log-log slope
    logk = np.log(k)
    logE = np.log(spectrum + 1e-12)

    slope, _ = np.polyfit(logk, logE, 1)
    return slope

def kurtosis(u):
    mean = np.mean(u)
    std = np.std(u)
    if std == 0:
        return 0.0
    return np.mean(((u - mean)/std)**4)
run_dir = f"outputs/omega_{OMEGA}_A_{A}_N_{N}"
os.makedirs(run_dir, exist_ok=True)

csv_path = os.path.join(run_dir, "energy.csv")

csv_file = open(csv_path, "w", newline="")
writer = csv.writer(csv_file)
writer.writerow(["step", "time", "energy", "helicity", "kurtosis", "slope"])

# ----------------------------
# PHASE AVERAGING SETUP
# ----------------------------
n_phase_bins = 32
phase_energy = [[] for _ in range(n_phase_bins)]
phase_helicity = [[] for _ in range(n_phase_bins)]
phase_kurtosis = [[] for _ in range(n_phase_bins)]
phase_slope = [[] for _ in range(n_phase_bins)]

# ----------------------------
# STEADY-STATE DETECTION
# ----------------------------
window = 200
tolerance = 1e-7
steady_required = 50

energy_history = []
steady_counter = 0

# ----------------------------
# MAIN LOOP
# ----------------------------
t = 0.0

for step in range(MAX_STEPS):

    # shear + forcing
    u += dt * shear(u)
    u += dt * forcing(X, t, A, OMEGA)

    # simple transport surrogate
    u = np.roll(u, 1, axis=0)
    v = np.roll(v, 1, axis=1)

    # diagnostics
    E = energy(u, v)
    H = helicity_proxy(u, v)
    K = kurtosis(u)
    S = spectral_slope(u)

    # phase averaging
    phase = (OMEGA * t) % (2 * np.pi)
    phase_bin = int((phase / (2 * np.pi)) * n_phase_bins) % n_phase_bins

    phase_energy[phase_bin].append(E)
    phase_helicity[phase_bin].append(H)
    phase_kurtosis[phase_bin].append(K)
    phase_slope[phase_bin].append(S)

    energy_history.append(E)
    writer.writerow([step, t, E, H, K, S])

    # steady-state detection
    if len(energy_history) > window:
        recent = energy_history[-window:]
        slope = abs(recent[-1] - recent[0]) / window

        if slope < tolerance:
            steady_counter += 1
        else:
            steady_counter = 0

        if steady_counter >= steady_required:
            print(f"Steady state reached at step {step}, t={t:.3f}")
            break

    if step % 500 == 0:
        print(f"step={step:6d}, t={t:8.3f}, E={E:.6e}")

    t += dt

csv_file.close()

print("Simulation complete.")

# ----------------------------
# PHASE-AVERAGED DIAGNOSTICS
# ----------------------------
phase_file = os.path.join(run_dir, "phase_averaged.csv")
with open(phase_file, "w", newline="") as f:
    writer_phase = csv.writer(f)
    writer_phase.writerow(["phase_bin", "phase_center", "mean_energy", "std_energy", "mean_helicity", "std_helicity", "mean_kurtosis", "std_kurtosis", "mean_slope", "std_slope", "n_samples"])

    for i in range(n_phase_bins):
        if phase_energy[i]:
            phase_center = (i + 0.5) * (2 * np.pi) / n_phase_bins
            mean_E = np.mean(phase_energy[i])
            std_E = np.std(phase_energy[i])
            mean_H = np.mean(phase_helicity[i])
            std_H = np.std(phase_helicity[i])
            mean_K = np.mean(phase_kurtosis[i])
            std_K = np.std(phase_kurtosis[i])
            mean_S = np.mean(phase_slope[i])
            std_S = np.std(phase_slope[i])
            n_samples = len(phase_energy[i])
            writer_phase.writerow([i, phase_center, mean_E, std_E, mean_H, std_H, mean_K, std_K, mean_S, std_S, n_samples])

print(f"Saved phase-averaged diagnostics to: {phase_file}")

# ----------------------------
# AUTO PLOTTING (PUBLICATION READY)
# ----------------------------
data = np.loadtxt(csv_path, delimiter=",", skiprows=1)

time = data[:, 1]
E_vals = data[:, 2]
H_vals = data[:, 3]
K_vals = data[:, 4]
S_vals = data[:, 5]

plt.figure(figsize=(8, 6))

plt.subplot(2,2,1)
plt.plot(time, E_vals)
plt.title("Energy")

plt.subplot(2,2,2)
plt.plot(time, H_vals)
plt.title("Helicity (proxy)")

plt.subplot(2,2,3)
plt.plot(time, K_vals)
plt.title("Kurtosis")

plt.subplot(2,2,4)
plt.plot(time, S_vals)
plt.title("Spectral slope")

plt.tight_layout()

plt.savefig(os.path.join(run_dir, "diagnostics.png"), dpi=300, bbox_inches="tight")
plt.close()

# Phase-averaged plotting
phase_data = np.loadtxt(phase_file, delimiter=",", skiprows=1)

phase_centers = phase_data[:, 1]
mean_H_phase = phase_data[:, 4]
std_H_phase = phase_data[:, 5]

plt.figure(figsize=(6, 4))
plt.errorbar(phase_centers, mean_H_phase, yerr=std_H_phase, fmt='o-', capsize=3)
plt.xlabel("Forcing Phase φ")
plt.ylabel("Mean Helicity Proxy")
plt.title("Phase-Averaged Helicity")
plt.grid(True)
plt.savefig(os.path.join(run_dir, "phase_helicity.png"), dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved results to: {run_dir}")