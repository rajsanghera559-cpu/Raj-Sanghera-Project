import pandas as pd
import os
import glob

# Find latest run
run_dir = os.path.join("experiments", "runs")
runs = sorted(glob.glob(os.path.join(run_dir, "run_*")), key=os.path.getmtime, reverse=True)
csv_path = os.path.join(runs[0], "spectrum.csv")

# Print columns
df = pd.read_csv(csv_path)
print("Available columns in spectrum.csv:")
print(df.columns.tolist())