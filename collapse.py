#!/usr/bin/env python3
"""Generate χ-collapse figure from parameter sweep data."""

import os
import numpy as np
import matplotlib.pyplot as plt
import glob

# Shear timescale (from shear strength 0.1)
tau_s = 10.0  # 1/shear_rate

def load_final_diagnostics(run_dir):
    """Load final diagnostics from CSV."""
    csv_path = os.path.join(run_dir, "energy.csv")
    if not os.path.exists(csv_path):
        return None
    data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    if len(data) == 0:
        return None
    E_final = data[-1, 2]
    if data.shape[1] >= 6:
        # New format with all diagnostics
        H_final = data[-1, 3]
        K_final = data[-1, 4]
        S_final = data[-1, 5]
    else:
        # Old format, only energy
        H_final = 0.0
        K_final = 3.0  # Default kurtosis for Gaussian
        S_final = -1.0  # Default slope
    return E_final, H_final, K_final, S_final

# Collect data
chi_vals = []
energies = []
helicities = []
kurtoses = []
slopes = []

outputs_dir = "outputs"
if os.path.exists(outputs_dir):
    for run_dir in os.listdir(outputs_dir):
        if run_dir.startswith("omega_"):
            # Parse parameters from dirname
            parts = run_dir.split("_")
            omega = float(parts[1])
            A = float(parts[3])

            chi = omega * tau_s
            diagnostics = load_final_diagnostics(os.path.join(outputs_dir, run_dir))

            if diagnostics is not None:
                E_final, H_final, K_final, S_final = diagnostics
                chi_vals.append(chi)
                energies.append(E_final)
                helicities.append(H_final)
                kurtoses.append(K_final)
                slopes.append(S_final)
                print(f"Loaded: ω={omega}, A={A}, χ={chi:.1f}, E={E_final:.2e}, H={H_final:.2e}, K={K_final:.2f}, S={S_final:.2f}")

# Sort by chi
if chi_vals:
    sorted_idx = np.argsort(chi_vals)
    chi_vals = np.array(chi_vals)[sorted_idx]
    energies = np.array(energies)[sorted_idx]
    helicities = np.array(helicities)[sorted_idx]
    kurtoses = np.array(kurtoses)[sorted_idx]
    slopes = np.array(slopes)[sorted_idx]

    # Multi-panel publication-quality plots
    plt.figure(figsize=(10, 8))

    # Energy
    plt.subplot(2,2,1)
    plt.scatter(chi_vals, energies, s=40, alpha=0.7)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel(r"$\chi = \omega \tau_s$", fontsize=12)
    plt.ylabel("Final Energy", fontsize=12)
    plt.title("Energy Collapse", fontsize=13)
    plt.grid(alpha=0.3)

    # Helicity
    plt.subplot(2,2,2)
    plt.scatter(chi_vals, helicities, s=40, alpha=0.7)
    plt.xscale("log")
    plt.xlabel(r"$\chi = \omega \tau_s$", fontsize=12)
    plt.ylabel("Final Helicity (proxy)", fontsize=12)
    plt.title("Helicity Collapse", fontsize=13)
    plt.grid(alpha=0.3)

    # Kurtosis
    plt.subplot(2,2,3)
    plt.scatter(chi_vals, kurtoses, s=40, alpha=0.7)
    plt.xscale("log")
    plt.xlabel(r"$\chi = \omega \tau_s$", fontsize=12)
    plt.ylabel("Final Kurtosis", fontsize=12)
    plt.title("Kurtosis Collapse", fontsize=13)
    plt.grid(alpha=0.3)

    # Spectral slope
    plt.subplot(2,2,4)
    plt.scatter(chi_vals, slopes, s=40, alpha=0.7)
    plt.xscale("log")
    plt.xlabel(r"$\chi = \omega \tau_s$", fontsize=12)
    plt.ylabel("Final Spectral Slope", fontsize=12)
    plt.title("Spectral Slope Collapse", fontsize=13)
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("chi_collapse.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("✓ Saved chi_collapse.png with all diagnostics")
else:
    print("No data found in outputs/ directory")