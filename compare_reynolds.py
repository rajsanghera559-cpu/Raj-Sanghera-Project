import pandas as pd
import matplotlib.pyplot as plt
import os

def check_normalization(df, name):
    total_spectral_energy = df['E(k)'].sum()
    print(f"--- {name} Normalization Check ---")
    print(f"Sum of E(k): {total_spectral_energy:.6e}")
    print("-----------------------------------\n")

def compare_reynolds():
    # Define paths to your specific N=256 run folders
    path_re1000 = os.path.join("experiments", "runs_N256", "spectrum.csv") 
    path_re2000 = os.path.join("experiments", "runs_N256_Re2000_20k", "spectrum.csv")

    if not os.path.exists(path_re1000) or not os.path.exists(path_re2000):
        print("Error: Could not find one or both spectrum.csv files. Check paths.")
        return

    df_1000 = pd.read_csv(path_re1000)
    df_2000 = pd.read_csv(path_re2000)

    # Normalization Sanity Check
    check_normalization(df_1000, "Re=1000 (N=256)")
    check_normalization(df_2000, "Re=2000 (N=256)")

    # Overlay Comparison Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Standard Energy Spectrum E(k)
    ax1.loglog(df_1000['k'], df_1000['E(k)'], 'b-o', label='Re=1000', alpha=0.7)
    ax1.loglog(df_2000['k'], df_2000['E(k)'], 'r-s', label='Re=2000', alpha=0.7)
    ax1.set_xlabel('Wavenumber (k)')
    ax1.set_ylabel('E(k)')
    ax1.set_title('Energy Spectrum: Re=1000 vs Re=2000')
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend()

    # Plot 2: Compensated Spectrum k^3 E(k)
    comp_1000 = (df_1000['k']**3) * df_1000['E(k)']
    comp_2000 = (df_2000['k']**3) * df_2000['E(k)']
    
    ax2.loglog(df_1000['k'], comp_1000, 'b-o', label='Re=1000', alpha=0.7)
    ax2.loglog(df_2000['k'], comp_2000, 'r-s', label='Re=2000', alpha=0.7)
    ax2.set_xlabel('Wavenumber (k)')
    ax2.set_ylabel(r'$k^3 E(k)$')
    ax2.set_title('Compensated Spectrum Comparison')
    ax2.grid(True, which="both", ls="--", alpha=0.5)
    ax2.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    compare_reynolds()