import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

def check_binning():
    # 1. Automatically find the latest run
    run_dir = os.path.join("experiments", "runs")
    runs = sorted(glob.glob(os.path.join(run_dir, "run_*")), key=os.path.getmtime, reverse=True)
    if not runs:
        print("No run folders found.")
        return
    csv_path = os.path.join(runs[0], "spectrum.csv")
    df = pd.read_csv(csv_path)

    # 2. Plotting Energy vs Mode Count
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Raw Energy (Blue)
    ax1.set_xlabel('Wavenumber (k)')
    ax1.set_ylabel('E(k)', color='tab:blue')
    ax1.loglog(df['k'], df['E(k)'], color='tab:blue', marker='o', label='Energy E(k)')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Plot Mode Count (Red)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Mode Count per Shell', color='tab:red')
    ax2.semilogy(df['k'], df['mode_count'], color='tab:red', linestyle='--', label='Mode Count')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    
    plt.title(f'Sanity Check: {os.path.basename(runs[0])}')
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    check_binning()