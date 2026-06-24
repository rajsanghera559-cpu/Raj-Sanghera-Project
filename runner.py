import subprocess
import os


def run_simulation(params):
    omega, A, N = params

    print(f"Running: omega={omega:.3f}, A={A:.4f}, N={N}")

    cmd = [
        "python", "solver.py",
        "--omega", str(omega),
        "--A", str(A),
        "--N", str(N)
    ]

    env = os.environ.copy()
    env["RUN_ID"] = f"omega_{omega}_A_{A}_N_{N}"

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )

    if result.returncode == 0:
        return f"✓ omega={omega:.3f}, A={A:.4f}, N={N} completed"
    else:
        return f"✗ omega={omega:.3f}, A={A:.4f}, N={N} failed: {result.stderr}"