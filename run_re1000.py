from project.solver.spectral_solver import SpectralSolver
from pathlib import Path

# --- Configuration ---
REYNOLDS_NUMBER = 1000
TOTAL_STEPS = 5000
RUN_DIR = Path('experiments/runs')

def execute_escalation():
    print(f"Starting Re={REYNOLDS_NUMBER} escalation: {TOTAL_STEPS} steps...")
    
    # Initialize the solver
    solver = SpectralSolver(
        nx=128, 
        ny=128, 
        Re=REYNOLDS_NUMBER, 
        run_path=RUN_DIR, 
        steps=TOTAL_STEPS
    )
    
    # Execute the run
    solver.run()
    
    print(f"Escalation complete. Data saved to {RUN_DIR}")

if __name__ == "__main__":
    execute_escalation()
