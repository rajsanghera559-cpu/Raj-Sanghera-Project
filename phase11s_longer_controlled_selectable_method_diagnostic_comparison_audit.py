from pathlib import Path
import json
import subprocess

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


METHOD_OUT_CSV = Path("PHASE11S_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_AUDIT.csv")
PAIRWISE_OUT_CSV = Path("PHASE11S_LONGER_CONTROLLED_SELECTABLE_METHOD_DIAGNOSTIC_COMPARISON_PAIRWISE.csv")

METHODS = ("fd_centered", "pseudo_spectral", "arakawa")

N = 64
RE = 1000
DT = 0.001
STEPS = 1000
FINAL_TIME = STEPS * DT
LOG_EVERY = 100
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


def l2_rms(field):
    return rms(field)


def max_abs(field):
    arr = np.asarray(field)
    return float(np.max(np.abs(arr)))


def relative_difference(a, b):
    return float(abs(a - b) / max(abs(b), 1e-300))


def ratio(a, b):
    return float(a / max(abs(b), 1e-300))


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


def relative_l2_vector(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    diff_norm = float(np.sqrt(np.sum((a - b) ** 2)))
    base_norm = float(np.sqrt(np.sum(b ** 2)))

    return diff_norm / max(base_norm, 1e-300)


def cosine_similarity(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    denom = float(np.sqrt(np.sum(a * a)) * np.sqrt(np.sum(b * b)))

    if denom == 0:
        return 1.0

    return float(np.sum(a * b) / denom)


def audit_run_disabled(solver):
    try:
        solver.run()
        return False
    except NotImplementedError:
        return True


def same_across_solvers(solvers, attr):
    values = [getattr(solver, attr) for solver in solvers.values()]
    first = values[0]

    for value in values[1:]:
        if isinstance(first, np.ndarray):
            if not np.allclose(first, value, rtol=0.0, atol=0.0):
                return False
        else:
            if first != value:
                return False

    return True


def all_forcing_same(solvers):
    forces = [solver.forcing() for solver in solvers.values()]
    first = forces[0]

    for force in forces[1:]:
        if not np.allclose(first, force, rtol=0.0, atol=0.0):
            return False

    return True


def all_dealias_same(solvers):
    masks = [solver.deal for solver in solvers.values()]
    first = masks[0]

    for mask in masks[1:]:
        if not np.allclose(first, mask, rtol=0.0, atol=0.0):
            return False

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


def audit_method(method, solver, initial_w, initial_metrics):
    initial_w_before = initial_w.copy()
    solver_w_before = solver.w.copy()

    run_disabled = audit_run_disabled(solver)

    result = solver.run_selectable_diagnostic(
        initial_w=initial_w,
        steps=STEPS,
        log_every=LOG_EVERY,
        write_outputs=True,
        save_initial_state=True,
        save_final_state=True,
    )

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

    method_initial_w_unchanged = np.allclose(
        initial_w,
        initial_w_before,
        rtol=0.0,
        atol=0.0,
    )

    solver_w_unchanged = np.allclose(
        solver.w,
        solver_w_before,
        rtol=0.0,
        atol=0.0,
    )

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
    final_w_shape_ok = final_w.shape == solver.w.shape

    initial_state_matches = np.allclose(
        initial_state,
        initial_w_before,
        rtol=0.0,
        atol=0.0,
    )

    final_state_matches = np.allclose(
        final_state,
        final_w,
        rtol=0.0,
        atol=0.0,
    )

    spectrum_columns_ok = {"k", "E_k", "mode_count"}.issubset(set(spectrum_df.columns))
    spectrum_file_finite = bool(np.isfinite(spectrum_df["E_k"].to_numpy()).all())
    spectrum_file_nonnegative = bool(float(spectrum_df["E_k"].min()) >= -1e-14)

    metadata_method_ok = metadata.get("advection_method") == method
    metadata_diagnostic_method_ok = metadata.get("diagnostic_run_method") == "run_selectable_diagnostic"
    metadata_run_enabled_false = metadata.get("run_enabled") is False
    metadata_run_method_enabled_false = metadata.get("run_method_enabled") is False
    metadata_production_ready_false = metadata.get("production_ready") is False
    metadata_turbulence_false = metadata.get("turbulence_claim") is False
    metadata_k_minus_3_false = metadata.get("k_minus_3_claim") is False

    summary_method_ok = summary.get("advection_method") == method
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

    method_pass = all(
        [
            run_disabled,
            final_w_exists,
            final_metrics["finite"],
            final_metrics["real"],
            final_w_shape_ok,
            solver_w_unchanged,
            method_initial_w_unchanged,
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
        ]
    )

    row = {
        "phase": "11S",
        "test_type": "method_audit",
        "method": method,
        "N": N,
        "Re": RE,
        "dt": DT,
        "steps": STEPS,
        "final_time": FINAL_TIME,
        "log_every": LOG_EVERY,
        "initial_rms": initial_metrics["rms"],
        "initial_energy": initial_metrics["energy"],
        "initial_enstrophy": initial_metrics["enstrophy"],
        "run_disabled": pass_fail(run_disabled),
        "final_w_exists": pass_fail(final_w_exists),
        "final_w_finite": pass_fail(final_metrics["finite"]),
        "final_w_real": pass_fail(final_metrics["real"]),
        "final_w_shape_ok": pass_fail(final_w_shape_ok),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "initial_w_unchanged": pass_fail(method_initial_w_unchanged),
        "output_keys_present": pass_fail(output_keys_present),
        "output_files_exist": pass_fail(outputs_exist),
        "initial_state_matches": pass_fail(initial_state_matches),
        "final_state_matches": pass_fail(final_state_matches),
        "diagnostics_columns_ok": pass_fail(diagnostics_audit["diagnostics_columns_ok"]),
        "diagnostics_rows_ok": pass_fail(diagnostics_audit["diagnostics_rows_ok"]),
        "diagnostics_steps_ok": pass_fail(diagnostics_audit["diagnostics_steps_ok"]),
        "diagnostics_step0_present": pass_fail(diagnostics_audit["diagnostics_step0_present"]),
        "diagnostics_final_step_present": pass_fail(diagnostics_audit["diagnostics_final_step_present"]),
        "diagnostics_numeric_finite": pass_fail(diagnostics_audit["diagnostics_numeric_finite"]),
        "diagnostics_finite_flags_ok": pass_fail(diagnostics_audit["diagnostics_finite_flags_ok"]),
        "diagnostics_real_flags_ok": pass_fail(diagnostics_audit["diagnostics_real_flags_ok"]),
        "diagnostics_time_monotone": pass_fail(diagnostics_audit["diagnostics_time_monotone"]),
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
        "diagnostics_min_rms": diagnostics_audit["diagnostics_min_rms"],
        "diagnostics_max_rms": diagnostics_audit["diagnostics_max_rms"],
        "diagnostics_min_energy": diagnostics_audit["diagnostics_min_energy"],
        "diagnostics_max_energy": diagnostics_audit["diagnostics_max_energy"],
        "diagnostics_min_enstrophy": diagnostics_audit["diagnostics_min_enstrophy"],
        "diagnostics_max_enstrophy": diagnostics_audit["diagnostics_max_enstrophy"],
        "spectrum_energy_sum": final_spectrum["energy_sum"],
        "spectrum_direct_relative_error": spectrum_direct_relative_error,
        "spectrum_direct_relative_error_ok": pass_fail(spectrum_direct_relative_error_ok),
        "dominant_shell": final_spectrum["dominant_shell"],
        "low_k_fraction_k_le_4": final_spectrum["low_k_fraction_k_le_4"],
        "high_k_fraction_k_ge_10": final_spectrum["high_k_fraction_k_ge_10"],
        "method_result": pass_fail(method_pass),
        "run_path": str(solver.run_path),
    }

    data = {
        "method": method,
        "solver": solver,
        "result": result,
        "final_w": final_w.copy(),
        "metrics": final_metrics,
        "spectrum": final_spectrum,
        "diagnostics": diagnostics_df.copy(),
        "row": row,
    }

    return data


def pairwise_compare(name_a, data_a, name_b, data_b):
    final_a = data_a["final_w"]
    final_b = data_b["final_w"]

    metrics_a = data_a["metrics"]
    metrics_b = data_b["metrics"]

    spectrum_a = data_a["spectrum"]
    spectrum_b = data_b["spectrum"]

    field_diff = final_a - final_b

    field_max_abs_difference = max_abs(field_diff)
    field_l2_difference = l2_rms(field_diff)
    field_relative_l2_difference = field_l2_difference / max(l2_rms(final_b), 1e-300)

    energy_relative_difference = relative_difference(
        metrics_a["energy"],
        metrics_b["energy"],
    )

    enstrophy_relative_difference = relative_difference(
        metrics_a["enstrophy"],
        metrics_b["enstrophy"],
    )

    rms_relative_difference = relative_difference(
        metrics_a["rms"],
        metrics_b["rms"],
    )

    spectra_same_length = len(spectrum_a["Ek"]) == len(spectrum_b["Ek"])

    if spectra_same_length:
        spectra_same_k_bins = np.allclose(
            spectrum_a["k_bins"],
            spectrum_b["k_bins"],
            rtol=0.0,
            atol=0.0,
        )

        spectrum_relative_l2_difference = relative_l2_vector(
            spectrum_a["Ek"],
            spectrum_b["Ek"],
        )

        spectrum_cosine_similarity = cosine_similarity(
            spectrum_a["Ek"],
            spectrum_b["Ek"],
        )
    else:
        spectra_same_k_bins = False
        spectrum_relative_l2_difference = float("inf")
        spectrum_cosine_similarity = float("nan")

    spectrum_energy_sum_relative_difference = relative_difference(
        spectrum_a["energy_sum"],
        spectrum_b["energy_sum"],
    )

    dominant_shell_matches = spectrum_a["dominant_shell"] == spectrum_b["dominant_shell"]

    metrics_finite = all(
        [
            finite_number(field_max_abs_difference),
            finite_number(field_l2_difference),
            finite_number(field_relative_l2_difference),
            finite_number(energy_relative_difference),
            finite_number(enstrophy_relative_difference),
            finite_number(rms_relative_difference),
            finite_number(spectrum_relative_l2_difference),
            finite_number(spectrum_energy_sum_relative_difference),
            finite_number(spectrum_cosine_similarity),
        ]
    )

    pairwise_result = all(
        [
            spectra_same_length,
            spectra_same_k_bins,
            metrics_finite,
        ]
    )

    return {
        "phase": "11S",
        "test_type": "pairwise_comparison",
        "method_a": name_a,
        "method_b": name_b,
        "pair": f"{name_a} vs {name_b}",
        "N": N,
        "Re": RE,
        "dt": DT,
        "steps": STEPS,
        "final_time": FINAL_TIME,
        "field_max_abs_difference": field_max_abs_difference,
        "field_l2_difference": field_l2_difference,
        "field_relative_l2_difference": field_relative_l2_difference,
        "energy_relative_difference": energy_relative_difference,
        "enstrophy_relative_difference": enstrophy_relative_difference,
        "rms_relative_difference": rms_relative_difference,
        "spectrum_relative_l2_difference": spectrum_relative_l2_difference,
        "spectrum_energy_sum_relative_difference": spectrum_energy_sum_relative_difference,
        "spectrum_cosine_similarity": spectrum_cosine_similarity,
        "dominant_shell_a": spectrum_a["dominant_shell"],
        "dominant_shell_b": spectrum_b["dominant_shell"],
        "dominant_shell_matches": pass_fail(dominant_shell_matches),
        "spectra_same_length": pass_fail(spectra_same_length),
        "spectra_same_k_bins": pass_fail(spectra_same_k_bins),
        "metrics_finite": pass_fail(metrics_finite),
        "pairwise_result": pass_fail(pairwise_result),
    }


print("\n=== PHASE 11S LONGER CONTROLLED SELECTABLE METHOD DIAGNOSTIC COMPARISON AUDIT ===")
print("Purpose: compare fd_centered, pseudo_spectral, and arakawa through final time 1.0.")
print("This uses run_selectable_diagnostic(...) only.")
print("This does not call SpectralSolver.run().")
print("SelectableAdvectionSolver.run() must remain disabled.")
print("This does not prove turbulence, k^-3 scaling, or method superiority.")

reference_solver = SpectralSolver(
    nx=N,
    ny=N,
    Re=RE,
    run_path=Path("experiments") / "reference" / "phase11S_reference_grid",
    dt=DT,
    steps=STEPS,
)

initial_w = build_test_field(reference_solver)
initial_w_before_all_runs = initial_w.copy()
initial_metrics = state_metrics(reference_solver, initial_w)

solvers = {}

for method in METHODS:
    solvers[method] = SelectableAdvectionSolver(
        nx=N,
        ny=N,
        Re=RE,
        run_path=Path("experiments") / "selectable_diagnostics" / f"phase11S_{method}",
        dt=DT,
        steps=STEPS,
        advection_method=method,
    )

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods_exact = SelectableAdvectionSolver.supported_advection_methods() == METHODS
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
rhs_method_exists = hasattr(SelectableAdvectionSolver, "compute_rhs_selectable")
step_method_exists = hasattr(SelectableAdvectionSolver, "step_once_selectable")
diagnostic_run_exists = hasattr(SelectableAdvectionSolver, "run_selectable_diagnostic")

spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
advection_operators_no_diff = git_file_has_no_diff("project/solver/advection_operators.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")

all_grid_shapes_same = all(solver.w.shape == initial_w.shape for solver in solvers.values())
all_dx_same = same_across_solvers(solvers, "dx")
all_dt_same = same_across_solvers(solvers, "dt")
all_nu_same = same_across_solvers(solvers, "nu")
all_dealias_masks_same = all_dealias_same(solvers)
all_forcing_fields_same = all_forcing_same(solvers)

global_checks_pass = all(
    [
        baseline_import_ok,
        selectable_import_ok,
        supported_methods_exact,
        default_method_ok,
        rhs_method_exists,
        step_method_exists,
        diagnostic_run_exists,
        spectral_solver_no_diff,
        advection_operators_no_diff,
        selectable_solver_no_diff,
        all_grid_shapes_same,
        all_dx_same,
        all_dt_same,
        all_nu_same,
        all_dealias_masks_same,
        all_forcing_fields_same,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"Supported methods exact: {pass_fail(supported_methods_exact)}")
print(f"Default method fd_centered: {pass_fail(default_method_ok)}")
print(f"compute_rhs_selectable exists: {pass_fail(rhs_method_exists)}")
print(f"step_once_selectable exists: {pass_fail(step_method_exists)}")
print(f"run_selectable_diagnostic exists: {pass_fail(diagnostic_run_exists)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"selectable_advection_solver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"All grid shapes same: {pass_fail(all_grid_shapes_same)}")
print(f"All dx same: {pass_fail(all_dx_same)}")
print(f"All dt same: {pass_fail(all_dt_same)}")
print(f"All nu same: {pass_fail(all_nu_same)}")
print(f"All dealias masks same: {pass_fail(all_dealias_masks_same)}")
print(f"All forcing fields same: {pass_fail(all_forcing_fields_same)}")
print(f"Global checks: {pass_fail(global_checks_pass)}")

method_data = {}
method_rows = []

for method in METHODS:
    print(f"\n=== METHOD RUN: {method} ===")
    data = audit_method(method, solvers[method], initial_w, initial_metrics)
    method_data[method] = data
    method_rows.append(data["row"])

    row = data["row"]

    print(f"final_rms: {row['final_rms']:.12e}")
    print(f"final_energy: {row['final_energy']:.12e}")
    print(f"final_enstrophy: {row['final_enstrophy']:.12e}")
    print(f"rms_ratio: {row['rms_ratio']:.12e}")
    print(f"energy_ratio: {row['energy_ratio']:.12e}")
    print(f"enstrophy_ratio: {row['enstrophy_ratio']:.12e}")
    print(f"dominant_shell: {row['dominant_shell']}")
    print(f"low_k_fraction_k_le_4: {row['low_k_fraction_k_le_4']:.12e}")
    print(f"high_k_fraction_k_ge_10: {row['high_k_fraction_k_ge_10']:.12e}")
    print(f"spectrum_direct_relative_error: {row['spectrum_direct_relative_error']:.12e}")
    print(f"diagnostics_min_rms: {row['diagnostics_min_rms']:.12e}")
    print(f"diagnostics_max_rms: {row['diagnostics_max_rms']:.12e}")
    print(f"metadata_turbulence_false: {row['metadata_turbulence_false']}")
    print(f"metadata_k_minus_3_false: {row['metadata_k_minus_3_false']}")
    print(f"method_result: {row['method_result']}")

shared_initial_w_unchanged = np.allclose(
    initial_w,
    initial_w_before_all_runs,
    rtol=0.0,
    atol=0.0,
)

pairwise_rows = []

PAIRWISE_ORDER = (
    ("pseudo_spectral", "fd_centered"),
    ("arakawa", "fd_centered"),
    ("arakawa", "pseudo_spectral"),
)

print("\n=== PAIRWISE COMPARISONS ===")

for method_a, method_b in PAIRWISE_ORDER:
    row = pairwise_compare(
        method_a,
        method_data[method_a],
        method_b,
        method_data[method_b],
    )
    pairwise_rows.append(row)

    print(f"\n{row['pair']}")
    print(f"field_relative_l2_difference: {row['field_relative_l2_difference']:.12e}")
    print(f"energy_relative_difference: {row['energy_relative_difference']:.12e}")
    print(f"enstrophy_relative_difference: {row['enstrophy_relative_difference']:.12e}")
    print(f"rms_relative_difference: {row['rms_relative_difference']:.12e}")
    print(f"spectrum_relative_l2_difference: {row['spectrum_relative_l2_difference']:.12e}")
    print(f"spectrum_cosine_similarity: {row['spectrum_cosine_similarity']:.12e}")
    print(f"dominant_shell_matches: {row['dominant_shell_matches']}")
    print(f"pairwise_result: {row['pairwise_result']}")

method_df = pd.DataFrame(method_rows)
pairwise_df = pd.DataFrame(pairwise_rows)

method_df.to_csv(METHOD_OUT_CSV, index=False)
pairwise_df.to_csv(PAIRWISE_OUT_CSV, index=False)

methods_pass = (method_df["method_result"] == "PASS").all()
pairwise_pass = (pairwise_df["pairwise_result"] == "PASS").all()

overall_pass = all(
    [
        global_checks_pass,
        methods_pass,
        pairwise_pass,
        shared_initial_w_unchanged,
    ]
)

print("\n=== FINAL CHECKS ===")
print(f"Shared initial_w unchanged across all runs: {pass_fail(shared_initial_w_unchanged)}")
print(f"All method audits pass: {pass_fail(methods_pass)}")
print(f"All pairwise comparisons pass: {pass_fail(pairwise_pass)}")

print("\n=== OVERALL RESULT ===")
print(f"Phase 11S longer controlled selectable method diagnostic comparison audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {METHOD_OUT_CSV}")
print(f"Wrote: {PAIRWISE_OUT_CSV}")
print("Phase 11S audit complete.")