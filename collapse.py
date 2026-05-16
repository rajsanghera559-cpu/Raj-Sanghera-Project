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
a_vals = []
