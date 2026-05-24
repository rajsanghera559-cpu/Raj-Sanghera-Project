import numpy as np
import matplotlib.pyplot as plt
import glob

# ============================================================
# LOAD SPECTRUM FILES
# ============================================================

files = sorted(
    glob.glob("outputs/spectrum_k_*.npy")
)

# ============================================================
# LOAD DATA
# ============================================================

spectra = []

for f in files:

    Ek = np.load(f)

    spectra.append(Ek)

spectra = np.array(spectra)

k_bins = np.load("outputs/spectrum_bins.npy")

# ============================================================
# PLOT EVOLUTION
# ============================================================

plt.figure(figsize=(8, 6))

for i in range(
    0,
    len(spectra),
    max(1, len(spectra)//10)
):

    plt.loglog(
        k_bins,
        spectra[i],
        alpha=0.6
    )

plt.xlabel("Wavenumber k")
plt.ylabel("Energy E(k)")
plt.title("Spectrum Evolution E(k,t)")

plt.grid(True)

plt.show()