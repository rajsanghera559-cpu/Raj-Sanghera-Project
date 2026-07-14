from pathlib import Path
import json
import subprocess

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


OUT_CSV = Path("PHASE11K1_SELECTABLE_DIAGNOSTIC_RUN_LOOP_SCAFFOLD_AUDIT.csv")

METHODS = ("fd_centered", "pseudo_spectral", "arakawa")


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    arr = np.asarray(field)
    return float(np.sqrt(np.mean(arr * arr)))


def max_abs(field):
    return float(np.max(np.abs(np.asarray(field))))


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


def build_test_field(solver):
    X = solver.X
    Y = solver.Y

    raw = (
        np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(Y)
        + 0.50 * np.sin(X) * np.cos(4 * Y)
        + 0.35 * np.cos(4 * X - 2 * Y)
    )

    field_rms = rms(raw)

    if field_rms == 0:
        raise ValueError("Cannot rescale zero-RMS field.")

    return raw * (0.01 / field_rms)


def audit_invalid_method():
    try:
        SelectableAdvectionSolver(
            nx=32,
            ny=32,
            Re=1000,
            run_path=Path("experiments") / "method_diagnostics" / "phase11K1_invalid",
            dt=0.001,
            steps=5,
            advection_method="invalid_method",
        )
        return False
    except ValueError:
        return True


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def audit_method(method):
    run_path = Path("experiments") / "selectable_diagnostics" / f"phase11K1_{method}"

    solver = SelectableAdvectionSolver(
        nx=32,
        ny=32,
        Re=1000,
        run_path=run_path,
        dt=0.001,
        steps=5,
        advection_method=method,
    )

    initial_w = build_test_field(solver)
    initial_w_before = initial_w.copy()
    solver_w_before = solver.w.copy()

    try:
        solver.run()
        run_disabled = False
    except NotImplementedError:
        run_disabled = True

    result = solver.run_selectable_diagnostic(
        initial_w=initial_w,
        steps=5,
        log_every=1,
        write_outputs=True,
        save_initial_state=True,
        save_final_state=True,
    )

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
    output_files_exist = all(Path(path).exists() for path in output_paths.values())

    metadata_path = Path(output_paths["metadata"])
    diagnostics_path = Path(output_paths["diagnostics"])
    spectrum_path = Path(output_paths["spectrum"])
    summary_path = Path(output_paths["summary"])
    initial_state_path = Path(output_paths["initial_state"])
    final_state_path = Path(output_paths["final_state"])

    metadata = load_json(metadata_path)
    summary = load_json(summary_path)
    diagnostics_df = pd.read_csv(diagnostics_path)
    spectrum_df = pd.read_csv(spectrum_path)

    initial_state = np.load(initial_state_path)
    final_state = np.load(final_state_path)

    initial_w_unchanged = np.allclose(initial_w, initial_w_before, rtol=0.0, atol=0.0)
    solver_w_unchanged = np.allclose(solver.w, solver_w_before, rtol=0.0, atol=0.0)

    result_has_metadata = isinstance(result.get("metadata"), dict)
    result_has_summary = isinstance(result.get("summary"), dict)
    result_has_diagnostics = isinstance(result.get("diagnostics"), list)
    result_has_spectrum = isinstance(result.get("spectrum"), list)
    result_has_initial_w = isinstance(result.get("initial_w"), np.ndarray)
    result_has_final_w = isinstance(result.get("final_w"), np.ndarray)

    final_w = result["final_w"]

    final_w_finite = np.isfinite(final_w).all()
    final_w_real = np.isrealobj(final_w)
    final_w_shape_ok = final_w.shape == solver.w.shape

    initial_state_matches = np.allclose(initial_state, initial_w_before, rtol=0.0, atol=0.0)
    final_state_matches = np.allclose(final_state, final_w, rtol=0.0, atol=0.0)

    diagnostics_rows_ok = len(diagnostics_df) == 6
    diagnostics_steps_ok = list(diagnostics_df["step"]) == [0, 1, 2, 3, 4, 5]

    spectrum_columns_ok = {"k", "E_k", "mode_count"}.issubset(set(spectrum_df.columns))
    spectrum_finite = np.isfinite(spectrum_df["E_k"].to_numpy()).all()
    spectrum_nonnegative = float(spectrum_df["E_k"].min()) >= -1e-14

    metadata_solver_variant_ok = metadata.get("solver_variant") == "selectable_advection"
    metadata_solver_class_ok = metadata.get("solver_class") == "SelectableAdvectionSolver"
    metadata_baseline_class_ok = metadata.get("baseline_solver_class") == "SpectralSolver"
    metadata_method_ok = metadata.get("advection_method") == method
    metadata_diagnostic_method_ok = metadata.get("diagnostic_run_method") == "run_selectable_diagnostic"
    metadata_run_enabled_false = metadata.get("run_enabled") is False
    metadata_run_method_enabled_false = metadata.get("run_method_enabled") is False
    metadata_production_ready_false = metadata.get("production_ready") is False
    metadata_turbulence_false = metadata.get("turbulence_claim") is False
    metadata_k_minus_3_false = metadata.get("k_minus_3_claim") is False
    metadata_steps_ok = metadata.get("steps") == 5
    metadata_log_every_ok = metadata.get("log_every") == 1
    metadata_N_ok = metadata.get("N") == 32

    summary_method_ok = summary.get("advection_method") == method
    summary_steps_ok = summary.get("steps") == 5
    summary_finite_final = summary.get("finite_final") is True
    summary_real_final = summary.get("real_final") is True
    summary_solver_w_unchanged = summary.get("solver_w_unchanged") is True
    summary_initial_w_unchanged = summary.get("initial_w_unchanged") is True
    summary_production_ready_false = summary.get("production_ready") is False
    summary_turbulence_false = summary.get("turbulence_claim") is False
    summary_k_minus_3_false = summary.get("k_minus_3_claim") is False

    exact_final_return_saved_match = np.allclose(final_state, result["final_w"], rtol=0.0, atol=0.0)

    overall = all(
        [
            run_disabled,
            output_keys_present,
            output_files_exist,
            initial_w_unchanged,
            solver_w_unchanged,
            result_has_metadata,
            result_has_summary,
            result_has_diagnostics,
            result_has_spectrum,
            result_has_initial_w,
            result_has_final_w,
            final_w_finite,
            final_w_real,
            final_w_shape_ok,
            initial_state_matches,
            final_state_matches,
            diagnostics_rows_ok,
            diagnostics_steps_ok,
            spectrum_columns_ok,
            spectrum_finite,
            spectrum_nonnegative,
            metadata_solver_variant_ok,
            metadata_solver_class_ok,
            metadata_baseline_class_ok,
            metadata_method_ok,
            metadata_diagnostic_method_ok,
            metadata_run_enabled_false,
            metadata_run_method_enabled_false,
            metadata_production_ready_false,
            metadata_turbulence_false,
            metadata_k_minus_3_false,
            metadata_steps_ok,
            metadata_log_every_ok,
            metadata_N_ok,
            summary_method_ok,
            summary_steps_ok,
            summary_finite_final,
            summary_real_final,
            summary_solver_w_unchanged,
            summary_initial_w_unchanged,
            summary_production_ready_false,
            summary_turbulence_false,
            summary_k_minus_3_false,
            exact_final_return_saved_match,
        ]
    )

    return {
        "test_type": "method_audit",
        "method": method,
        "run_path": str(run_path),
        "run_disabled": pass_fail(run_disabled),
        "output_keys_present": pass_fail(output_keys_present),
        "output_files_exist": pass_fail(output_files_exist),
        "initial_w_unchanged": pass_fail(initial_w_unchanged),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "result_has_metadata": pass_fail(result_has_metadata),
        "result_has_summary": pass_fail(result_has_summary),
        "result_has_diagnostics": pass_fail(result_has_diagnostics),
        "result_has_spectrum": pass_fail(result_has_spectrum),
        "result_has_initial_w": pass_fail(result_has_initial_w),
        "result_has_final_w": pass_fail(result_has_final_w),
        "final_w_finite": pass_fail(final_w_finite),
        "final_w_real": pass_fail(final_w_real),
        "final_w_shape_ok": pass_fail(final_w_shape_ok),
        "initial_state_matches": pass_fail(initial_state_matches),
        "final_state_matches": pass_fail(final_state_matches),
        "diagnostics_rows_ok": pass_fail(diagnostics_rows_ok),
        "diagnostics_steps_ok": pass_fail(diagnostics_steps_ok),
        "spectrum_columns_ok": pass_fail(spectrum_columns_ok),
        "spectrum_finite": pass_fail(spectrum_finite),
        "spectrum_nonnegative": pass_fail(spectrum_nonnegative),
        "metadata_solver_variant_ok": pass_fail(metadata_solver_variant_ok),
        "metadata_solver_class_ok": pass_fail(metadata_solver_class_ok),
        "metadata_baseline_class_ok": pass_fail(metadata_baseline_class_ok),
        "metadata_method_ok": pass_fail(metadata_method_ok),
        "metadata_diagnostic_method_ok": pass_fail(metadata_diagnostic_method_ok),
        "metadata_run_enabled_false": pass_fail(metadata_run_enabled_false),
        "metadata_run_method_enabled_false": pass_fail(metadata_run_method_enabled_false),
        "metadata_production_ready_false": pass_fail(metadata_production_ready_false),
        "metadata_turbulence_false": pass_fail(metadata_turbulence_false),
        "metadata_k_minus_3_false": pass_fail(metadata_k_minus_3_false),
        "metadata_steps_ok": pass_fail(metadata_steps_ok),
        "metadata_log_every_ok": pass_fail(metadata_log_every_ok),
        "metadata_N_ok": pass_fail(metadata_N_ok),
        "summary_method_ok": pass_fail(summary_method_ok),
        "summary_steps_ok": pass_fail(summary_steps_ok),
        "summary_finite_final": pass_fail(summary_finite_final),
        "summary_real_final": pass_fail(summary_real_final),
        "summary_solver_w_unchanged": pass_fail(summary_solver_w_unchanged),
        "summary_initial_w_unchanged": pass_fail(summary_initial_w_unchanged),
        "summary_production_ready_false": pass_fail(summary_production_ready_false),
        "summary_turbulence_false": pass_fail(summary_turbulence_false),
        "summary_k_minus_3_false": pass_fail(summary_k_minus_3_false),
        "exact_final_return_saved_match": pass_fail(exact_final_return_saved_match),
        "diagnostics_row_count": len(diagnostics_df),
        "spectrum_row_count": len(spectrum_df),
        "final_rms": rms(final_w),
        "final_max_abs": max_abs(final_w),
        "overall_result": pass_fail(overall),
    }


print("\n=== PHASE 11K.1 SELECTABLE DIAGNOSTIC RUN-LOOP SCAFFOLD AUDIT ===")
print("Purpose: audit run_selectable_diagnostic scaffold mechanics.")
print("This does not modify SpectralSolver.")
print("SelectableAdvectionSolver.run() must remain disabled.")
print("This does not prove turbulence or k^-3 scaling.")

rows = []

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods_ok = SelectableAdvectionSolver.supported_advection_methods() == METHODS
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
rhs_method_exists = hasattr(SelectableAdvectionSolver, "compute_rhs_selectable")
step_method_exists = hasattr(SelectableAdvectionSolver, "step_once_selectable")
diagnostic_run_exists = hasattr(SelectableAdvectionSolver, "run_selectable_diagnostic")
spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
advection_operators_no_diff = git_file_has_no_diff("project/solver/advection_operators.py")
invalid_method_rejected = audit_invalid_method()

global_pass = all(
    [
        baseline_import_ok,
        selectable_import_ok,
        supported_methods_ok,
        default_method_ok,
        rhs_method_exists,
        step_method_exists,
        diagnostic_run_exists,
        spectral_solver_no_diff,
        advection_operators_no_diff,
        invalid_method_rejected,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"Supported methods check: {pass_fail(supported_methods_ok)}")
print(f"Default method fd_centered: {pass_fail(default_method_ok)}")
print(f"compute_rhs_selectable exists: {pass_fail(rhs_method_exists)}")
print(f"step_once_selectable exists: {pass_fail(step_method_exists)}")
print(f"run_selectable_diagnostic exists: {pass_fail(diagnostic_run_exists)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"Invalid method rejected: {pass_fail(invalid_method_rejected)}")
print(f"Global checks: {pass_fail(global_pass)}")

rows.append(
    {
        "test_type": "global_checks",
        "method": "global",
        "run_path": "",
        "run_disabled": "N/A",
        "output_keys_present": "N/A",
        "output_files_exist": "N/A",
        "initial_w_unchanged": "N/A",
        "solver_w_unchanged": "N/A",
        "result_has_metadata": "N/A",
        "result_has_summary": "N/A",
        "result_has_diagnostics": "N/A",
        "result_has_spectrum": "N/A",
        "result_has_initial_w": "N/A",
        "result_has_final_w": "N/A",
        "final_w_finite": "N/A",
        "final_w_real": "N/A",
        "final_w_shape_ok": "N/A",
        "initial_state_matches": "N/A",
        "final_state_matches": "N/A",
        "diagnostics_rows_ok": "N/A",
        "diagnostics_steps_ok": "N/A",
        "spectrum_columns_ok": "N/A",
        "spectrum_finite": "N/A",
        "spectrum_nonnegative": "N/A",
        "metadata_solver_variant_ok": "N/A",
        "metadata_solver_class_ok": "N/A",
        "metadata_baseline_class_ok": "N/A",
        "metadata_method_ok": "N/A",
        "metadata_diagnostic_method_ok": "N/A",
        "metadata_run_enabled_false": "N/A",
        "metadata_run_method_enabled_false": "N/A",
        "metadata_production_ready_false": "N/A",
        "metadata_turbulence_false": "N/A",
        "metadata_k_minus_3_false": "N/A",
        "metadata_steps_ok": "N/A",
        "metadata_log_every_ok": "N/A",
        "metadata_N_ok": "N/A",
        "summary_method_ok": "N/A",
        "summary_steps_ok": "N/A",
        "summary_finite_final": "N/A",
        "summary_real_final": "N/A",
        "summary_solver_w_unchanged": "N/A",
        "summary_initial_w_unchanged": "N/A",
        "summary_production_ready_false": "N/A",
        "summary_turbulence_false": "N/A",
        "summary_k_minus_3_false": "N/A",
        "exact_final_return_saved_match": "N/A",
        "diagnostics_row_count": np.nan,
        "spectrum_row_count": np.nan,
        "final_rms": np.nan,
        "final_max_abs": np.nan,
        "overall_result": pass_fail(global_pass),
    }
)

for method in METHODS:
    print(f"\n=== METHOD AUDIT: {method} ===")
    result = audit_method(method)
    rows.append(result)

    print(f"run_disabled: {result['run_disabled']}")
    print(f"output_keys_present: {result['output_keys_present']}")
    print(f"output_files_exist: {result['output_files_exist']}")
    print(f"initial_w_unchanged: {result['initial_w_unchanged']}")
    print(f"solver_w_unchanged: {result['solver_w_unchanged']}")
    print(f"final_w_finite: {result['final_w_finite']}")
    print(f"final_w_real: {result['final_w_real']}")
    print(f"diagnostics_rows_ok: {result['diagnostics_rows_ok']}")
    print(f"diagnostics_steps_ok: {result['diagnostics_steps_ok']}")
    print(f"spectrum_columns_ok: {result['spectrum_columns_ok']}")
    print(f"spectrum_finite: {result['spectrum_finite']}")
    print(f"spectrum_nonnegative: {result['spectrum_nonnegative']}")
    print(f"metadata_method_ok: {result['metadata_method_ok']}")
    print(f"metadata_diagnostic_method_ok: {result['metadata_diagnostic_method_ok']}")
    print(f"metadata_production_ready_false: {result['metadata_production_ready_false']}")
    print(f"metadata_turbulence_false: {result['metadata_turbulence_false']}")
    print(f"metadata_k_minus_3_false: {result['metadata_k_minus_3_false']}")
    print(f"summary_production_ready_false: {result['summary_production_ready_false']}")
    print(f"summary_turbulence_false: {result['summary_turbulence_false']}")
    print(f"summary_k_minus_3_false: {result['summary_k_minus_3_false']}")
    print(f"overall_result: {result['overall_result']}")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

all_pass = (df["overall_result"] == "PASS").all()

print("\n=== OVERALL RESULT ===")
print(f"Phase 11K.1 selectable diagnostic run-loop scaffold audit: {pass_fail(all_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 11K.1 selectable diagnostic run-loop scaffold audit complete.")