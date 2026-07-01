from project.solver.spectral_solver import SpectralSolver
from pathlib import Path

# --- Configuration ---
# Hardened configuration for Stage 3 of the Reynolds Ladder Study
RUN_DIR = Path('experiments/runs_N256_Re5000_20k')
RUN_DIR.mkdir(parents=True, exist_ok=True)

total_steps = 20000
step_chunk = 2000

print(f"Starting Stage 3 Study (High-Re Stress Test): N=256, Re=5000, Total Steps={total_steps}")

# Initialize the solver with fixed grid and maximum Re parameter
solver = SpectralSolver(
    nx=256, 
    ny=256, 
    Re=5000, 
    steps=step_chunk, 
    run_path=RUN_DIR
)

# Loop to achieve total_steps
for i in range(0, total_steps, step_chunk):
    current_chunk_target = i + step_chunk
    print(f"Running chunk: {current_chunk_target} / {total_steps}...")
    solver.run()
    print(f"Completed {current_chunk_target} steps. Snapshot saved to {RUN_DIR}.")

print("Escalation complete.")
