import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

def compute_average_spectrum():
    # 1. Locate all spectrum.csv files in the experiments/runs folder
    run_dir = os.path.join("experiments", "runs")
    # This assumes all your snapshots are inside one run folder
    files = glob.glob(os.path.join(run_dir, "run_*", "spectrum.csv"))
    
    if not files:
        print("No spectrum.csv files found.")
        return

    # 2. Accumulate energy values
    all_spectra = []
    for f in files:
        df = pd.read_csv(f)
        all_spectra.append(df['E(k)'].values)
    
    # 3. Compute Mean and Std Deviation
    mean_Ek = np.mean(all_spectra, axis=0)
    std_Ek = np.std(all_spectra, axis=0)
    k = df['k'].values
    
    # 4. Compensated Plotting (k^3 * E(k))
    compensated_mean = (k**3) * mean_Ek
    
    plt.figure(figsize=(10, 6))
    plt.loglog(k, compensated_mean, 'b-', label='Averaged Compensated Spectrum')
    plt.fill_between(k, (k**3)*(mean_Ek - std_Ek), (k**3)*(mean_Ek + std_Ek), color='b', alpha=0.2)
    
    plt.axhline(y=np.mean(compensated_mean[5:15]), color='r', linestyle='--', label='Mean Cascade Level')
    plt.xlabel('Wavenumber (k)')
    plt.ylabel(r'$k^3 E(k)$')
    plt.title('Time-Averaged Compensated Spectrum (20,000 steps)')
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.legend()
    
    plt.show()

if __name__ == "__main__":
    compute_average_spectrum()