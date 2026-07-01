import pandas as pd
import matplotlib.pyplot as plt
import os

def check_normalization(df, name):
    total_spectral_energy = df['E(k)'].sum()
    print(f"{name:.<25} Spectral Sum: {total_spectral_energy:.6e}")

def compare_three_reynolds():
    # Concrete analytical paths
    path_1000 = os.path.join("experiments", "runs_N256", "spectrum.csv") 
    path_2000 = os.path.join("experiments", "runs_N256_Re2000_20k", "spectrum.csv")
    path_5000 = os.path.join("experiments", "runs_N256_Re5000_20k", "spectrum.csv")

    paths = [path_1000, path_2000, path_5000]
    names = ["Re=1000", "Re=2000", "Re=5000"]
    colors = ['tab:blue', 'tab:orange', 'tab:red']
    markers = ['o', 's', '^']

    for p, n in zip(paths, names):
        if not os.path.exists(p):
            print(f"Error: Missing data file at {p}")
            return

    dfs = [pd.read_csv(p) for p in paths]

    print("--- Hardened Normalization Verification ---")
    for df, name in zip(dfs, names):
        check_normalization(df, name)
    print("-------------------------------------------\n")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Left Plot: Energy Spectrum E(k)
    for df, name, color, marker in zip(dfs, names, colors, markers):
        ax1.loglog(df['k'], df['E(k)'], color=color, marker=marker, linestyle='-', alpha=0.6, label=name)
    ax1.set_xlabel('Wavenumber (k)')
    ax1.set_ylabel('E(k)')
    ax1.set_title('Energy Spectrum Evolution Across Reynolds Ladder')
    ax1.grid(True, which="both", ls="--", alpha=0.4)
    ax1.legend()

    # Right Plot: Compensated Spectrum k^3 * E(k)
    for df, name, color, marker in zip(dfs, names, colors, markers):
        comp = (df['k']**3) * df['E(k)']
        ax2.loglog(df['k'], comp, color=color, marker=marker, linestyle='-', alpha=0.6, label=name)
    ax2.set_xlabel('Wavenumber (k)')
    ax2.set_ylabel(r'$k^3 E(k)$')
    ax2.set_title('Compensated Spectrum ($k^3$) Comparative Overlay')
    ax2.grid(True, which="both", ls="--", alpha=0.4)
    ax2.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    compare_three_reynolds()