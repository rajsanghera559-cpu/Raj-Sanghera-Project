import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import glob

def plot_compensated_spectrum():
    # 1. Locate the newest run with spectrum.csv
    base_dir = os.path.join("experiments", "runs")
    runs = sorted(glob.glob(os.path.join(base_dir, "run_*")), key=os.path.getmtime, reverse=True)
    
    csv_path = None
    for run in runs:
        candidate = os.path.join(run, "spectrum.csv")
        if os.path.exists(candidate):
            csv_path = candidate
            run_name = os.path.basename(run)
            break
            
    if not csv_path:
        print("No spectrum.csv found.")
        return
        
    # 2. Load data
    df = pd.read_csv(csv_path)
    k = df['k'].values
    Ek = df['E(k)'].values
    
    # 3. Compute Compensated Energy (k^3 * E(k))
    # We avoid k=0 to prevent division/log issues
    compensated = (k**3) * Ek
    
    # 4. Plotting
    plt.figure(figsize=(10, 6))
    
    # Primary Plot: Compensated Spectrum
    plt.loglog(k, compensated, marker='o', linestyle='-', label=r'$k^3 E(k)$ (Compensated)')
    
    plt.axhline(y=np.mean(compensated[5:15]), color='r', linestyle='--', label='Mean Level')
    
    plt.xlabel('Wavenumber (k)')
    plt.ylabel(r'$k^3 E(k)$')
    plt.title(f'Compensated Spectrum: {run_name}')
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.legend()
    
    # Save and Show
    plot_path = os.path.join(os.path.dirname(csv_path), "compensated_spectrum.png")
    plt.savefig(plot_path)
    print(f"Plot saved to: {plot_path}")
    plt.show(block=True)

if __name__ == "__main__":
    plot_compensated_spectrum()