import numpy as np
import matplotlib.pyplot as plt
import glob

# ============================================================
# LOAD ALL SPECTRUM FILES
# ============================================================

files = sorted(
    glob.glob("outputs/spectrum_k_*.npy")
)

# ============================================================
# LOAD SPECTRA
# ============================================================

spectra = []

for f in files:

    Ek = np.load(f)

    spectra.append(Ek)

spectra = np.array(spectra)

# ============================================================
# LOAD K BINS
# ============================================================

k_bins = np.load("outputs/spectrum_bins.npy")

# ============================================================
# TIME-AVERAGED SPECTRUM
# ============================================================

Ek_mean = np.mean(spectra, axis=0)

# ============================================================
# PLOT
# ============================================================

plt.figure(figsize=(8, 6))

plt.loglog(
    k_bins,
    Ek_mean,
    linewidth=2
)

plt.xlabel("Wavenumber k")
plt.ylabel("Time-averaged E(k)")
plt.title("Time-Averaged Energy Spectrum")

plt.grid(True)

plt.show()