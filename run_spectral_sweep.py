import argparse
import csv
import os
import subprocess
import sys
from itertools import product


def comma_floats(value):
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run a viscosity/forcing spectral parameter sweep."
    )
    parser.add_argument("--N", type=int, default=256, help="Grid size. Default: 256")
    parser.add_argument("--dt", type=float, default=0.0005, help="Timestep. Default: 0.0005")
    parser.add_argument("--steps", type=int, default=50000, help="Timesteps per run. Default: 50000")
    parser.add_argument("--save-every", type=int, default=1000, help="Spectrum save interval. Default: 1000")
    parser.add_argument("--seed", type=int, default=0, help="Base random seed. Default: 0")
    parser.add_argument(
        "--nu-values",
        type=comma_floats,
        default=comma_floats("0.003,0.001,0.0003,0.0001"),
        help="Comma-separated viscosities. Default: 0.003,0.001,0.0003,0.0001",
    )
    parser.add_argument(
        "--forcing-amplitudes",
        type=comma_floats,
        default=comma_floats("0.003,0.01"),
        help="Comma-separated forcing amplitudes. Default: 0.003,0.01",
    )
    parser.add_argument(
        "--forcing-mode",
        type=int,
        default=2,
        help="Forcing mode passed to solver.py. Default: 2",
    )
    parser.add_argument(
        "--root",
        default="outputs_spectra",
        help="Root directory for sweep outputs. Default: outputs_spectra",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip runs where spectrum_bins.npy already exists.",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze all completed sweep outputs after running.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned commands without running them.",
    )
    return parser


def output_dir(root, nu, forcing_amplitude, forcing_mode):
    return os.path.join(
        root,
        f"nu_{nu:g}_f_{forcing_amplitude:g}_m_{forcing_mode}",
    )


def write_sweep_log(root, rows):
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, "sweep_log.csv")

    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "status",
                "nu",
                "forcing_amplitude",
                "forcing_mode",
                "output_dir",
                "returncode",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    return path


def run_command(command, dry_run):
    print(" ".join(command), flush=True)

    if dry_run:
        return 0

    completed = subprocess.run(command)
    return completed.returncode


def analyze_outputs(output_dirs, root, dry_run):
    completed_dirs = [
        path
        for path in output_dirs
        if os.path.exists(os.path.join(path, "spectrum_bins.npy"))
    ]

    if not completed_dirs:
        print("No completed spectrum directories found for analysis.")
        return 1

    command = [
        sys.executable,
        "fit_spectral_slope.py",
        "--output-dir",
        completed_dirs[0],
        "--save",
        os.path.join(root, "sweep_spectrum_comparison.png"),
        "--summary-csv",
        os.path.join(root, "sweep_fit_summary.csv"),
    ]

    for path in completed_dirs[1:]:
        command.extend(["--compare-dir", path])

    return run_command(command, dry_run)


def main():
    args = build_parser().parse_args()
    os.makedirs(args.root, exist_ok=True)

    parameter_grid = list(product(args.nu_values, args.forcing_amplitudes))
    planned_outputs = []
    rows = []

    print("Spectral parameter sweep", flush=True)
    print("========================", flush=True)
    print(f"N={args.N}, dt={args.dt}, steps={args.steps}, save_every={args.save_every}", flush=True)
    print(f"nu_values={args.nu_values}", flush=True)
    print(f"forcing_amplitudes={args.forcing_amplitudes}", flush=True)
    print(f"total_runs={len(parameter_grid)}", flush=True)

    for index, (nu, forcing_amplitude) in enumerate(parameter_grid):
        run_dir = output_dir(args.root, nu, forcing_amplitude, args.forcing_mode)
        planned_outputs.append(run_dir)

        if args.skip_existing and os.path.exists(os.path.join(run_dir, "spectrum_bins.npy")):
            print(f"Skipping existing run: {run_dir}", flush=True)
            rows.append(
                {
                    "status": "skipped",
                    "nu": nu,
                    "forcing_amplitude": forcing_amplitude,
                    "forcing_mode": args.forcing_mode,
                    "output_dir": run_dir,
                    "returncode": 0,
                }
            )
            continue

        command = [
            sys.executable,
            "solver.py",
            "--N",
            str(args.N),
            "--dt",
            str(args.dt),
            "--nu",
            str(nu),
            "--steps",
            str(args.steps),
            "--save-every",
            str(args.save_every),
            "--seed",
            str(args.seed + index),
            "--forcing-amplitude",
            str(forcing_amplitude),
            "--forcing-mode",
            str(args.forcing_mode),
            "--output-dir",
            run_dir,
        ]

        returncode = run_command(command, args.dry_run)
        rows.append(
            {
                "status": "completed" if returncode == 0 else "failed",
                "nu": nu,
                "forcing_amplitude": forcing_amplitude,
                "forcing_mode": args.forcing_mode,
                "output_dir": run_dir,
                "returncode": returncode,
            }
        )

        if returncode != 0:
            print(f"Stopping sweep after failed run: {run_dir}", flush=True)
            break

    log_path = write_sweep_log(args.root, rows)
    print(f"Sweep log: {log_path}", flush=True)

    if args.analyze:
        return analyze_outputs(planned_outputs, args.root, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
