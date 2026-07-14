from pathlib import Path
import json
import subprocess
import time

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


OUT_CSV = Path("PHASE12C_N256_CONTROLLED_SELECTABLE_DIAGNOSTIC_FEASIBILITY_AUDIT.csv")

METHOD = "fd_centered"

N = 256
RE = 1000
DT = 0.001
STEPS = 100
FINAL_TIME = STEPS * DT
LOG_EVERY = 10
INITIAL_RMS = 0.01

SPECTRUM_DIRECT_REL_TOL = 1e-10

RMS_RATIO_MIN = 0.01
RMS_RATIO_MAX = 100.0

ENERGY_RATIO_MIN = 0.0001
ENERGY_RATIO_MAX = 10000.0

ENSTROPHY_RATIO_MIN = 0.0001
ENSTROPHY_RATIO_MAX = 10000.0


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    arr = np.asarray(field)
    return float(np.sqrt(np.mean(arr * arr)))


def max_abs(field):
    arr = np.asarray(field)
    return float(np.max(np.abs(arr)))


def ratio(a, b):
    return float(a / max(abs(b), 1e-300))


def relative_difference(a, b):
    return float(abs(a - b) / max(abs(b), 1e-300))


def finite_number(value):
    try:
        return bool(np.isfinite(float(value)))
    except Exception:
        return False


def git_file_has_no_diff(path):
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet", "--", path],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def build_test_field(solver):
    X = solver.X
    Y = solver.Y

    raw = (
        np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(Y)
        + 0.50 * np.sin(X) * np.cos(4 * Y)
        + 0.35 * np.cos(4 * X - 2 * Y)
    )

    raw_rms = rms(raw)

    if raw_rms == 0:
        raise ValueError("Cannot rescale zero-RMS field.")

    return raw * (INITIAL_RMS / raw_rms)


def state_metrics(solver, w):
    arr = np.asarray(w).real

    psi = solver.streamfunction(arr)
    u, v = solver.velocity(psi)

    return {
        "rms": float(np.sqrt(np.mean(arr * arr))),
        "energy": float(solver.energy(u, v)),
        "enstrophy": float(0.5 * np.mean(arr * arr)),
        "max_abs": float(np.max(np.abs(arr))),
        "finite": bool(np.isfinite(arr).all()),
        "real": bool(np.isrealobj(arr)),
    }


def spectrum_metrics(solver, w):
    k_bins, Ek, mode_counts = solver.energy_spectrum(w)

    k_bins = np.asarray(k_bins, dtype=float)
    Ek = np.asarray(Ek, dtype=float)
    mode_counts = np.asarray(mode_counts, dtype=int)

    total_energy = float(np.sum(Ek))

    if len(Ek) == 0:
        dominant_shell = np.nan
        low_k_fraction = np.nan
        high_k_fraction = np.nan
        spectrum_finite = False
        spectrum_nonnegative = False
    else:
        dominant_shell = float(k_bins[int(np.argmax(Ek))])
        low_k_fraction = float(np.sum(Ek[k_bins <= 4]) / max(total_energy, 1e-300))
        high_k_fraction = float(np.sum(Ek[k_bins >= 10]) / max(total_energy, 1e-300))
        spectrum_finite = bool(np.isfinite(Ek).all())
        spectrum_nonnegative = bool(float(np.min(Ek)) >= -1e-14)

    return {
        "k_bins": k_bins,
        "Ek": Ek,
        "mode_counts": mode_counts,
        "energy_sum": total_energy,
        "dominant_shell": dominant_shell,
        "low_k_fraction_k_le_4": low_k_fraction,
        "high_k_fraction_k_ge_10": high_k_fraction,
        "finite": spectrum_finite,
        "nonnegative": spectrum_nonnegative,
    }


def audit_run_disabled(solver):
    try:
        solver.run()
        return False
    except NotImplementedError:
        return True


def output_files_exist(output_paths):
    return all(Path(path).exists() for path in output_paths.values())


def expected_logged_steps():
    steps = list(range(0, STEPS + 1, LOG_EVERY))

    if steps[-1] != STEPS:
        steps.append(STEPS)

    return sorted(set(steps))


def bool_column_all_true(series):
    values = series.astype(str).str.lower().str.strip()
    return bool(values.isin(["true", "1"]).all())


def audit_diagnostics_dataframe(diagnostics_df):
    required_columns = {
        "step",
        "time",
        "rms_vorticity",
        "kinetic_energy",
        "enstrophy",
        "max_abs_vorticity",
        "finite",
        "real",
    }

    diagnostics_columns_ok = required_columns.issubset(set(diagnostics_df.columns))

    if not diagnostics_columns_ok:
        return {
            "diagnostics_columns_ok": False,
            "diagnostics_rows_ok": False,
            "diagnostics_steps_ok": False,
            "diagnostics_step0_present": False,
            "diagnostics_final_step_present": False,
            "diagnostics_numeric_finite": False,
            "diagnostics_finite_flags_ok": False,
            "diagnostics_real_flags_ok": False,
            "diagnostics_time_monotone": False,
            "diagnostics_min_rms": np.nan,
            "diagnostics_max_rms": np.nan,
            "diagnostics_min_energy": np.nan,
            "diagnostics_max_energy": np.nan,
            "diagnostics_min_enstrophy": np.nan,
            "diagnostics_max_enstrophy": np.nan,
        }

    expected_steps = expected_logged_steps()
    observed_steps = [int(x) for x in diagnostics_df["step"].tolist()]

    diagnostics_rows_ok = len(diagnostics_df) == len(expected_steps)
    diagnostics_steps_ok = observed_steps == expected_steps
    diagnostics_step0_present = 0 in observed_steps
    diagnostics_final_step_present = STEPS in observed_steps

    numeric_columns = [
        "step",
        "time",
        "rms_vorticity",
        "kinetic_energy",
        "enstrophy",
        "max_abs_vorticity",
    ]

    numeric_values = diagnostics_df[numeric_columns].to_numpy(dtype=float)
    diagnostics_numeric_finite = bool(np.isfinite(numeric_values).all())

    diagnostics_finite_flags_ok = bool_column_all_true(diagnostics_df["finite"])
    diagnostics_real_flags_ok = bool_column_all_true(diagnostics_df["real"])

    times = diagnostics_df["time"].to_numpy(dtype=float)
    diagnostics_time_monotone = bool(np.all(np.diff(times) >= 0.0))

    return {
        "diagnostics_columns_ok": diagnostics_columns_ok,
        "diagnostics_rows_ok": diagnostics_rows_ok,
        "diagnostics_steps_ok": diagnostics_steps_ok,
        "diagnostics_step0_present": diagnostics_step0_present,
        "diagnostics_final_step_present": diagnostics_final_step_present,
        "diagnostics_numeric_finite": diagnostics_numeric_finite,
        "diagnostics_finite_flags_ok": diagnostics_finite_flags_ok,
        "diagnostics_real_flags_ok": diagnostics_real_flags_ok,
        "diagnostics_time_monotone": diagnostics_time_monotone,
        "diagnostics_min_rms": float(diagnostics_df["rms_vorticity"].min()),
        "diagnostics_max_rms": float(diagnostics_df["rms_vorticity"].max()),
        "diagnostics_min_energy": float(diagnostics_df["kinetic_energy"].min()),
        "diagnostics_max_energy": float(diagnostics_df["kinetic_energy"].max()),
        "diagnostics_min_enstrophy": float(diagnostics_df["enstrophy"].min()),
        "diagnostics_max_enstrophy": float(diagnostics_df["enstrophy"].max()),
    }


print("\n=== PHASE 12C N256 CONTROLLED SELECTABLE DIAGNOSTIC FEASIBILITY AUDIT ===")
print("Purpose: run a short N256 fd_centered feasibility audit.")
print("This uses run_selectable_diagnostic(...) only.")
print("This does not call SpectralSolver.run().")
print("SelectableAdvectionSolver.run() must remain disabled.")
print("This does not run pseudo_spectral or arakawa at N256.")
print("This does not prove convergence, turbulence, k^-3 scaling, or method superiority.")

solver = SelectableAdvectionSolver(
    nx=N,
    ny=N,
    Re=RE,
    run_path=Path("experiments") / "selectable_diagnostics" / "phase12C_N256_fd_centered_feasibility",
    dt=DT,
    steps=STEPS,
    advection_method=METHOD,
)

initial_w = build_test_field(solver)
initial_w_before = initial_w.copy()
solver_w_before = solver.w.copy()

initial_metrics = state_metrics(solver, initial_w)

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
method_supported = METHOD in SelectableAdvectionSolver.supported_advection_methods()
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
selected_method_ok = solver.advection_method == METHOD
rhs_method_exists = hasattr(SelectableAdvectionSolver, "compute_rhs_selectable")
step_method_exists = hasattr(SelectableAdvectionSolver, "step_once_selectable")
diagnostic_run_exists = hasattr(SelectableAdvectionSolver, "run_selectable_diagnostic")
run_disabled = audit_run_disabled(solver)

spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
advection_operators_no_diff = git_file_has_no_diff("project/solver/advection_operators.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")

N_ok = solver.N == N
shape_ok = solver.w.shape == (N, N)
Re_ok = RE == 1000
dt_ok = abs(solver.dt - DT) <= 0.0
steps_ok = STEPS == 100
final_time_ok = abs(FINAL_TIME - 0.1) <= 1e-15
log_every_ok = LOG_EVERY == 10
initial_rms_ok = abs(initial_metrics["rms"] - INITIAL_RMS) <= 1e-14

global_checks_pass = all(
    [
        baseline_import_ok,
        selectable_import_ok,
        method_supported,
        default_method_ok,
        selected_method_ok,
        rhs_method_exists,
        step_method_exists,
        diagnostic_run_exists,
        run_disabled,
        spectral_solver_no_diff,
        advection_operators_no_diff,
        selectable_solver_no_diff,
        N_ok,
        shape_ok,
        Re_ok,
        dt_ok,
        steps_ok,
        final_time_ok,
        log_every_ok,
        initial_rms_ok,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"fd_centered supported: {pass_fail(method_supported)}")
print(f"default method fd_centered: {pass_fail(default_method_ok)}")
print(f"selected method fd_centered: {pass_fail(selected_method_ok)}")
print(f"compute_rhs_selectable exists: {pass_fail(rhs_method_exists)}")
print(f"step_once_selectable exists: {pass_fail(step_method_exists)}")
print(f"run_selectable_diagnostic exists: {pass_fail(diagnostic_run_exists)}")
print(f"SelectableAdvectionSolver.run disabled: {pass_fail(run_disabled)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"selectable_advection_solver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"N == 256: {pass_fail(N_ok)}")
print(f"shape == (256, 256): {pass_fail(shape_ok)}")
print(f"Re == 1000: {pass_fail(Re_ok)}")
print(f"dt == 0.001: {pass_fail(dt_ok)}")
print(f"steps == 100: {pass_fail(steps_ok)}")
print(f"final time == 0.1: {pass_fail(final_time_ok)}")
print(f"log_every == 10: {pass_fail(log_every_ok)}")
print(f"initial RMS == 0.01: {pass_fail(initial_rms_ok)}")
print(f"Global checks: {pass_fail(global_checks_pass)}")

print("\n=== RUNNING N256 FD_CENTERED FEASIBILITY DIAGNOSTIC ===")
start_time = time.perf_counter()

result = solver.run_selectable_diagnostic(
    initial_w=initial_w,
    steps=STEPS,
    log_every=LOG_EVERY,
    write_outputs=True,
    save_initial_state=True,
    save_final_state=True,
)

elapsed_seconds = time.perf_counter() - start_time
print(f"Run completed in {elapsed_seconds:.3f} seconds.")

final_w = result["final_w"]
output_paths = result.get("output_paths", {})

required_output_keys = {
    "metadata",
    "diagnostics",
    "spectrum",
    "summary",
    "initial_state",
    "final_state",
}

output_keys_present = required_output_keys.issubset(set(output_paths.keys()))
outputs_exist = output_files_exist(output_paths)

metadata = load_json(output_paths["metadata"])
summary = load_json(output_paths["summary"])
diagnostics_df = pd.read_csv(output_paths["diagnostics"])
spectrum_df = pd.read_csv(output_paths["spectrum"])

initial_state = np.load(output_paths["initial_state"])
final_state = np.load(output_paths["final_state"])

initial_w_unchanged = np.allclose(initial_w, initial_w_before, rtol=0.0, atol=0.0)
solver_w_unchanged = np.allclose(solver.w, solver_w_before, rtol=0.0, atol=0.0)

final_metrics = state_metrics(solver, final_w)
final_spectrum = spectrum_metrics(solver, final_w)
diagnostics_audit = audit_diagnostics_dataframe(diagnostics_df)

spectrum_direct_relative_error = relative_difference(
    final_spectrum["energy_sum"],
    final_metrics["energy"],
)

rms_ratio = ratio(final_metrics["rms"], initial_metrics["rms"])
energy_ratio = ratio(final_metrics["energy"], initial_metrics["energy"])
enstrophy_ratio = ratio(final_metrics["enstrophy"], initial_metrics["enstrophy"])

final_w_exists = isinstance(final_w, np.ndarray)
final_w_shape_ok = final_w.shape == (N, N)

initial_state_matches = np.allclose(initial_state, initial_w_before, rtol=0.0, atol=0.0)
final_state_matches = np.allclose(final_state, final_w, rtol=0.0, atol=0.0)

spectrum_columns_ok = {"k", "E_k", "mode_count"}.issubset(set(spectrum_df.columns))
spectrum_file_finite = bool(np.isfinite(spectrum_df["E_k"].to_numpy()).all())
spectrum_file_nonnegative = bool(float(spectrum_df["E_k"].min()) >= -1e-14)

metadata_method_ok = metadata.get("advection_method") == METHOD
metadata_diagnostic_method_ok = metadata.get("diagnostic_run_method") == "run_selectable_diagnostic"
metadata_run_enabled_false = metadata.get("run_enabled") is False
metadata_run_method_enabled_false = metadata.get("run_method_enabled") is False
metadata_production_ready_false = metadata.get("production_ready") is False
metadata_turbulence_false = metadata.get("turbulence_claim") is False
metadata_k_minus_3_false = metadata.get("k_minus_3_claim") is False

summary_method_ok = summary.get("advection_method") == METHOD
summary_production_ready_false = summary.get("production_ready") is False
summary_turbulence_false = summary.get("turbulence_claim") is False
summary_k_minus_3_false = summary.get("k_minus_3_claim") is False

rms_ratio_ok = RMS_RATIO_MIN <= rms_ratio <= RMS_RATIO_MAX
energy_ratio_ok = ENERGY_RATIO_MIN <= energy_ratio <= ENERGY_RATIO_MAX
enstrophy_ratio_ok = ENSTROPHY_RATIO_MIN <= enstrophy_ratio <= ENSTROPHY_RATIO_MAX
spectrum_direct_relative_error_ok = spectrum_direct_relative_error <= SPECTRUM_DIRECT_REL_TOL

diagnostics_pass = all(
    [
        diagnostics_audit["diagnostics_columns_ok"],
        diagnostics_audit["diagnostics_rows_ok"],
        diagnostics_audit["diagnostics_steps_ok"],
        diagnostics_audit["diagnostics_step0_present"],
        diagnostics_audit["diagnostics_final_step_present"],
        diagnostics_audit["diagnostics_numeric_finite"],
        diagnostics_audit["diagnostics_finite_flags_ok"],
        diagnostics_audit["diagnostics_real_flags_ok"],
        diagnostics_audit["diagnostics_time_monotone"],
    ]
)

run_checks_pass = all(
    [
        final_w_exists,
        final_metrics["finite"],
        final_metrics["real"],
        final_w_shape_ok,
        initial_w_unchanged,
        solver_w_unchanged,
        output_keys_present,
        outputs_exist,
        initial_state_matches,
        final_state_matches,
        diagnostics_pass,
        spectrum_columns_ok,
        spectrum_file_finite,
        spectrum_file_nonnegative,
        final_spectrum["finite"],
        final_spectrum["nonnegative"],
        metadata_method_ok,
        metadata_diagnostic_method_ok,
        metadata_run_enabled_false,
        metadata_run_method_enabled_false,
        metadata_production_ready_false,
        metadata_turbulence_false,
        metadata_k_minus_3_false,
        summary_method_ok,
        summary_production_ready_false,
        summary_turbulence_false,
        summary_k_minus_3_false,
        rms_ratio_ok,
        energy_ratio_ok,
        enstrophy_ratio_ok,
        spectrum_direct_relative_error_ok,
        finite_number(elapsed_seconds),
    ]
)

overall_pass = global_checks_pass and run_checks_pass

print("\n=== FEASIBILITY METRICS ===")
print(f"elapsed_seconds: {elapsed_seconds:.12e}")
print(f"initial_rms: {initial_metrics['rms']:.12e}")
print(f"final_rms: {final_metrics['rms']:.12e}")
print(f"final_energy: {final_metrics['energy']:.12e}")
print(f"final_enstrophy: {final_metrics['enstrophy']:.12e}")
print(f"final_max_abs: {final_metrics['max_abs']:.12e}")
print(f"rms_ratio: {rms_ratio:.12e}")
print(f"energy_ratio: {energy_ratio:.12e}")
print(f"enstrophy_ratio: {enstrophy_ratio:.12e}")
print(f"dominant_shell: {final_spectrum['dominant_shell']}")
print(f"low_k_fraction_k_le_4: {final_spectrum['low_k_fraction_k_le_4']:.12e}")
print(f"high_k_fraction_k_ge_10: {final_spectrum['high_k_fraction_k_ge_10']:.12e}")
print(f"spectrum_direct_relative_error: {spectrum_direct_relative_error:.12e}")
print(f"diagnostics_min_rms: {diagnostics_audit['diagnostics_min_rms']:.12e}")
print(f"diagnostics_max_rms: {diagnostics_audit['diagnostics_max_rms']:.12e}")

print("\n=== RUN CHECKS ===")
print(f"final_w exists: {pass_fail(final_w_exists)}")
print(f"final_w finite: {pass_fail(final_metrics['finite'])}")
print(f"final_w real: {pass_fail(final_metrics['real'])}")
print(f"final_w shape ok: {pass_fail(final_w_shape_ok)}")
print(f"initial_w unchanged: {pass_fail(initial_w_unchanged)}")
print(f"solver.w unchanged: {pass_fail(solver_w_unchanged)}")
print(f"output keys present: {pass_fail(output_keys_present)}")
print(f"output files exist: {pass_fail(outputs_exist)}")
print(f"diagnostics pass: {pass_fail(diagnostics_pass)}")
print(f"spectrum columns ok: {pass_fail(spectrum_columns_ok)}")
print(f"spectrum file finite: {pass_fail(spectrum_file_finite)}")
print(f"spectrum file nonnegative: {pass_fail(spectrum_file_nonnegative)}")
print(f"metadata production_ready false: {pass_fail(metadata_production_ready_false)}")
print(f"metadata turbulence false: {pass_fail(metadata_turbulence_false)}")
print(f"metadata k_minus_3 false: {pass_fail(metadata_k_minus_3_false)}")
print(f"rms ratio ok: {pass_fail(rms_ratio_ok)}")
print(f"energy ratio ok: {pass_fail(energy_ratio_ok)}")
print(f"enstrophy ratio ok: {pass_fail(enstrophy_ratio_ok)}")
print(f"spectrum direct relative error ok: {pass_fail(spectrum_direct_relative_error_ok)}")
print(f"Run checks: {pass_fail(run_checks_pass)}")

row = {
    "phase": "12C",
    "test": "N256_fd_centered_controlled_selectable_diagnostic_feasibility",
    "method": METHOD,
    "N": N,
    "Re": RE,
    "dt": DT,
    "steps": STEPS,
    "final_time": FINAL_TIME,
    "log_every": LOG_EVERY,
    "elapsed_seconds": elapsed_seconds,
    "global_checks": pass_fail(global_checks_pass),
    "run_checks": pass_fail(run_checks_pass),
    "baseline_import_ok": pass_fail(baseline_import_ok),
    "selectable_import_ok": pass_fail(selectable_import_ok),
    "method_supported": pass_fail(method_supported),
    "default_method_ok": pass_fail(default_method_ok),
    "selected_method_ok": pass_fail(selected_method_ok),
    "rhs_method_exists": pass_fail(rhs_method_exists),
    "step_method_exists": pass_fail(step_method_exists),
    "diagnostic_run_exists": pass_fail(diagnostic_run_exists),
    "run_disabled": pass_fail(run_disabled),
    "spectral_solver_no_diff": pass_fail(spectral_solver_no_diff),
    "advection_operators_no_diff": pass_fail(advection_operators_no_diff),
    "selectable_solver_no_diff": pass_fail(selectable_solver_no_diff),
    "N_ok": pass_fail(N_ok),
    "shape_ok": pass_fail(shape_ok),
    "Re_ok": pass_fail(Re_ok),
    "dt_ok": pass_fail(dt_ok),
    "steps_ok": pass_fail(steps_ok),
    "final_time_ok": pass_fail(final_time_ok),
    "log_every_ok": pass_fail(log_every_ok),
    "initial_rms_ok": pass_fail(initial_rms_ok),
    "initial_rms": initial_metrics["rms"],
    "initial_energy": initial_metrics["energy"],
    "initial_enstrophy": initial_metrics["enstrophy"],
    "final_rms": final_metrics["rms"],
    "final_energy": final_metrics["energy"],
    "final_enstrophy": final_metrics["enstrophy"],
    "final_max_abs": final_metrics["max_abs"],
    "rms_ratio": rms_ratio,
    "energy_ratio": energy_ratio,
    "enstrophy_ratio": enstrophy_ratio,
    "rms_ratio_ok": pass_fail(rms_ratio_ok),
    "energy_ratio_ok": pass_fail(energy_ratio_ok),
    "enstrophy_ratio_ok": pass_fail(enstrophy_ratio_ok),
    "dominant_shell": final_spectrum["dominant_shell"],
    "low_k_fraction_k_le_4": final_spectrum["low_k_fraction_k_le_4"],
    "high_k_fraction_k_ge_10": final_spectrum["high_k_fraction_k_ge_10"],
    "spectrum_energy_sum": final_spectrum["energy_sum"],
    "spectrum_direct_relative_error": spectrum_direct_relative_error,
    "spectrum_direct_relative_error_ok": pass_fail(spectrum_direct_relative_error_ok),
    "diagnostics_columns_ok": pass_fail(diagnostics_audit["diagnostics_columns_ok"]),
    "diagnostics_rows_ok": pass_fail(diagnostics_audit["diagnostics_rows_ok"]),
    "diagnostics_steps_ok": pass_fail(diagnostics_audit["diagnostics_steps_ok"]),
    "diagnostics_step0_present": pass_fail(diagnostics_audit["diagnostics_step0_present"]),
    "diagnostics_final_step_present": pass_fail(diagnostics_audit["diagnostics_final_step_present"]),
    "diagnostics_numeric_finite": pass_fail(diagnostics_audit["diagnostics_numeric_finite"]),
    "diagnostics_finite_flags_ok": pass_fail(diagnostics_audit["diagnostics_finite_flags_ok"]),
    "diagnostics_real_flags_ok": pass_fail(diagnostics_audit["diagnostics_real_flags_ok"]),
    "diagnostics_time_monotone": pass_fail(diagnostics_audit["diagnostics_time_monotone"]),
    "diagnostics_min_rms": diagnostics_audit["diagnostics_min_rms"],
    "diagnostics_max_rms": diagnostics_audit["diagnostics_max_rms"],
    "diagnostics_min_energy": diagnostics_audit["diagnostics_min_energy"],
    "diagnostics_max_energy": diagnostics_audit["diagnostics_max_energy"],
    "diagnostics_min_enstrophy": diagnostics_audit["diagnostics_min_enstrophy"],
    "diagnostics_max_enstrophy": diagnostics_audit["diagnostics_max_enstrophy"],
    "final_w_exists": pass_fail(final_w_exists),
    "final_w_finite": pass_fail(final_metrics["finite"]),
    "final_w_real": pass_fail(final_metrics["real"]),
    "final_w_shape_ok": pass_fail(final_w_shape_ok),
    "initial_w_unchanged": pass_fail(initial_w_unchanged),
    "solver_w_unchanged": pass_fail(solver_w_unchanged),
    "output_keys_present": pass_fail(output_keys_present),
    "output_files_exist": pass_fail(outputs_exist),
    "initial_state_matches": pass_fail(initial_state_matches),
    "final_state_matches": pass_fail(final_state_matches),
    "spectrum_columns_ok": pass_fail(spectrum_columns_ok),
    "spectrum_file_finite": pass_fail(spectrum_file_finite),
    "spectrum_file_nonnegative": pass_fail(spectrum_file_nonnegative),
    "metadata_method_ok": pass_fail(metadata_method_ok),
    "metadata_diagnostic_method_ok": pass_fail(metadata_diagnostic_method_ok),
    "metadata_run_enabled_false": pass_fail(metadata_run_enabled_false),
    "metadata_run_method_enabled_false": pass_fail(metadata_run_method_enabled_false),
    "metadata_production_ready_false": pass_fail(metadata_production_ready_false),
    "metadata_turbulence_false": pass_fail(metadata_turbulence_false),
    "metadata_k_minus_3_false": pass_fail(metadata_k_minus_3_false),
    "summary_method_ok": pass_fail(summary_method_ok),
    "summary_production_ready_false": pass_fail(summary_production_ready_false),
    "summary_turbulence_false": pass_fail(summary_turbulence_false),
    "summary_k_minus_3_false": pass_fail(summary_k_minus_3_false),
    "overall_result": pass_fail(overall_pass),
    "run_path": str(solver.run_path),
}

pd.DataFrame([row]).to_csv(OUT_CSV, index=False)

print("\n=== OVERALL RESULT ===")
print(f"Phase 12C N256 controlled selectable diagnostic feasibility audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")

print("\n=== SCIENTIFIC BOUNDARY ===")
print("This is an N256 fd_centered feasibility test only.")
print("This does not prove full N256 final-time-1.0 feasibility.")
print("This does not prove pseudo_spectral or arakawa N256 feasibility.")
print("This does not prove convergence.")
print("This does not prove turbulence.")
print("This does not prove k^-3 scaling.")
print("This does not prove method superiority.")
print("Phase 12C audit complete.")