#!/usr/bin/env python3
"""Parameter sweep runner for vortex solver."""

import subprocess
import os
import numpy as np
import multiprocessing as mp

def run_simulation(params):
    """Run a single simulation with given parameters."""
    omega, A = params
    print(f"Running: omega={omega:.3f}, A={A:.4f}")
    cmd = ["python", "solver.py", "--omega", str(omega), "--A", str(A)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return f"✓ omega={omega:.3f}, A={A:.4f} completed"
    else:
        return f"✗ omega={omega:.3f}, A={A:.4f} failed: {result.stderr}"

if __name__ == "__main__":
    # Parameter ranges (dense around resonance χ~1)
    omegas = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0]
    As = [0.001, 0.005, 0.01, 0.05, 0.1]  # Finer amplitude resolution

    # Generate parameter combinations
    param_combinations = [(omega, A) for omega in omegas for A in As]

    print("Starting parallel parameter sweep...")
    print(f"Omegas: {len(omegas)} values from {omegas[0]:.1f} to {omegas[-1]:.1f}")
    print(f"Amplitudes: {As}")
    print(f"Total runs: {len(param_combinations)}")

    # Run sequentially for now to avoid multiprocessing issues
    results = []
    for params in param_combinations:
        result = run_simulation(params)
        results.append(result)
        print(result)

    print("\nParameter sweep complete!")
    print("Check outputs/ directory for results.")