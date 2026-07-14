from pathlib import Path
import json
import subprocess

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


OUT_CSV = Path("PHASE11M_FD_CENTERED_DIAGNOSTIC_RUN_LOOP_EQUIVALENCE_AUDIT.csv")

N = 64
RE = 1000
DT = 0.001
STEPS = 20
LOG_EVERY = 1
METHOD = "fd_centered"

FIELD_MAX_ABS_TOL = 1e-13
FIELD_L2_TOL = 1e-13
FIELD_REL_L2_TOL = 1e-11
ENERGY_REL_TOL = 1e-11
ENSTROPHY_REL_TOL = 1e-11
RMS_REL_TOL = 1e-11
SPECTRUM_REL_L2_TOL = 1e-10


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
    return float(abs(a - b) / max(abs(a), 1e-300))


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

    return raw * (0.01 / raw_rms)


def baseline_rhs_transcription(solver, w):
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)

    wx = (np.roll(w, -1, axis=1) - np.roll(w, 1, axis=1)) / (2 * solver.dx)
    wy = (np.roll(w, -1, axis=0) - np.roll(w, 1, axis=0)) / (2 * solver.dx)

    adv = u * wx + v * wy

    rhs = -adv + solver.laplacian_spectral(w) + solver.forcing()

    return rhs.real


def baseline_step_transcription(solver, w):
    k1 = baseline_rhs_transcription(solver, w)
    w1 = w + solver.dt * k1

    k2 = baseline_rhs_transcription(solver, w1)
    w_new = w + 0.5 * solver.dt * (k1 + k2)

    W = np.fft.fft2(w_new)
    W *= solver.deal

    return np.fft.ifft2(W).real


def run_baseline_transcription(solver, initial_w, steps):
    w = np.asarray(initial_w).real.copy()

    for _ in range(steps):
        w_before = w.copy()
        w_next = baseline_step_transcription(solver, w)

        if not np.allclose(w, w_before, rtol=0.0, atol=0.0):
            raise RuntimeError("Baseline transcription mutated its input unexpectedly.")

        w = w_next

    return w.copy()


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

    if len(Ek) == 0:
        dominant_shell = np.nan
    else:
        dominant_shell = float(k_bins[int(np.argmax(Ek))])

    return {
        "k_bins": k_bins,
        "Ek": Ek,
        "mode_counts": mode_counts,
        "energy_sum": float(np.sum(Ek)),
        "dominant_shell": dominant_shell,
        "finite": bool(np.isfinite(Ek).all()),
        "nonnegative": bool(float(np.min(Ek)) >= -1e-14),
    }


def relative_l2_vector(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    diff_norm = float(np.sqrt(np.sum((a - b) ** 2)))
    base_norm = float(np.sqrt(np.sum(a ** 2)))

    return diff_norm / max(base_norm, 1e-300)


def audit_run_disabled(solver):
    try:
        solver.run()
        return False
    except NotImplementedError:
        return True


print("\n=== PHASE 11M FD_CENTERED DIAGNOSTIC RUN-LOOP EQUIVALENCE AUDIT ===")
print("Purpose: compare selectable fd_centered diagnostic loop against baseline transcription.")
print("This does not call SpectralSolver.run().")
print("SelectableAdvectionSolver.run() must remain disabled.")
print("This does not prove turbulence or k^-3 scaling.")

baseline_solver = SpectralSolver(
    nx=N,
    ny=N,
    Re=RE,
    run_path=Path("experiments") / "baseline_transcriptions" / "phase11M_fd_centered_equivalence",
    dt=DT,
    steps=STEPS,
)

selectable_solver = SelectableAdvectionSolver(
    nx=N,
    ny=N,
    Re=RE,
    run_path=Path("experiments") / "selectable_diagnostics" / "phase11M_fd_centered_equivalence",
    dt=DT,
    steps=STEPS,
    advection_method=METHOD,
)

initial_w = build_test_field(baseline_solver)
initial_w_before = initial_w.copy()

baseline_solver_w_before = baseline_solver.w.copy()
selectable_solver_w_before = selectable_solver.w.copy()

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods_ok = METHOD in SelectableAdvectionSolver.supported_advection_methods()
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
selectable_method_ok = selectable_solver.advection_method == METHOD
rhs_method_exists = hasattr(SelectableAdvectionSolver, "compute_rhs_selectable")
step_method_exists = hasattr(SelectableAdvectionSolver, "step_once_selectable")
diagnostic_run_exists = hasattr(SelectableAdvectionSolver, "run_selectable_diagnostic")
run_disabled = audit_run_disabled(selectable_solver)
spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
advection_operators_no_diff = git_file_has_no_diff("project/solver/advection_operators.py")

same_grid_shape = baseline_solver.w.shape == selectable_solver.w.shape == initial_w.shape
same_dx = baseline_solver.dx == selectable_solver.dx
same_dt = baseline_solver.dt == selectable_solver.dt
same_nu = baseline_solver.nu == selectable_solver.nu
same_dealias_mask = np.allclose(baseline_solver.deal, selectable_solver.deal, rtol=0.0, atol=0.0)
same_forcing = np.allclose(baseline_solver.forcing(), selectable_solver.forcing(), rtol=0.0, atol=0.0)

global_checks_pass = all(
    [
        baseline_import_ok,
        selectable_import_ok,
        supported_methods_ok,
        default_method_ok,
        selectable_method_ok,
        rhs_method_exists,
        step_method_exists,
        diagnostic_run_exists,
        run_disabled,
        spectral_solver_no_diff,
        advection_operators_no_diff,
        same_grid_shape,
        same_dx,
        same_dt,
        same_nu,
        same_dealias_mask,
        same_forcing,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"fd_centered supported: {pass_fail(supported_methods_ok)}")
print(f"default method fd_centered: {pass_fail(default_method_ok)}")
print(f"selectable method fd_centered: {pass_fail(selectable_method_ok)}")
print(f"compute_rhs_selectable exists: {pass_fail(rhs_method_exists)}")
print(f"step_once_selectable exists: {pass_fail(step_method_exists)}")
print(f"run_selectable_diagnostic exists: {pass_fail(diagnostic_run_exists)}")
print(f"SelectableAdvectionSolver.run disabled: {pass_fail(run_disabled)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"same grid shape: {pass_fail(same_grid_shape)}")
print(f"same dx: {pass_fail(same_dx)}")
print(f"same dt: {pass_fail(same_dt)}")
print(f"same nu: {pass_fail(same_nu)}")
print(f"same dealias mask: {pass_fail(same_dealias_mask)}")
print(f"same forcing: {pass_fail(same_forcing)}")
print(f"Global checks: {pass_fail(global_checks_pass)}")

print("\n=== RUNNING BASELINE TRANSCRIPTION ===")
baseline_final = run_baseline_transcription(
    solver=baseline_solver,
    initial_w=initial_w,
    steps=STEPS,
)

print("Baseline transcription complete.")

print("\n=== RUNNING SELECTABLE DIAGNOSTIC LOOP ===")
selectable_result = selectable_solver.run_selectable_diagnostic(
    initial_w=initial_w,
    steps=STEPS,
    log_every=LOG_EVERY,
    write_outputs=True,
    save_initial_state=True,
    save_final_state=True,
)

selectable_final = selectable_result["final_w"]

print("Selectable diagnostic loop complete.")

initial_w_unchanged = np.allclose(initial_w, initial_w_before, rtol=0.0, atol=0.0)
baseline_solver_w_unchanged = np.allclose(
    baseline_solver.w,
    baseline_solver_w_before,
    rtol=0.0,
    atol=0.0,
)
selectable_solver_w_unchanged = np.allclose(
    selectable_solver.w,
    selectable_solver_w_before,
    rtol=0.0,
    atol=0.0,
)

baseline_metrics = state_metrics(baseline_solver, baseline_final)
selectable_metrics = state_metrics(selectable_solver, selectable_final)

baseline_spectrum = spectrum_metrics(baseline_solver, baseline_final)
selectable_spectrum = spectrum_metrics(selectable_solver, selectable_final)

field_diff = baseline_final - selectable_final

field_max_abs_diff = max_abs(field_diff)
field_l2_diff = l2_rms(field_diff)
field_relative_l2_diff = field_l2_diff / max(l2_rms(baseline_final), 1e-300)

energy_relative_difference = relative_difference(
    baseline_metrics["energy"],
    selectable_metrics["energy"],
)

enstrophy_relative_difference = relative_difference(
    baseline_metrics["enstrophy"],
    selectable_metrics["enstrophy"],
)

rms_relative_difference = relative_difference(
    baseline_metrics["rms"],
    selectable_metrics["rms"],
)

spectra_same_length = len(baseline_spectrum["Ek"]) == len(selectable_spectrum["Ek"])
spectra_same_k_bins = np.allclose(
    baseline_spectrum["k_bins"],
    selectable_spectrum["k_bins"],
    rtol=0.0,
    atol=0.0,
)

if spectra_same_length:
    spectrum_relative_l2_difference = relative_l2_vector(
        baseline_spectrum["Ek"],
        selectable_spectrum["Ek"],
    )
else:
    spectrum_relative_l2_difference = float("inf")

spectrum_energy_sum_relative_difference = relative_difference(
    baseline_spectrum["energy_sum"],
    selectable_spectrum["energy_sum"],
)

dominant_shell_matches = baseline_spectrum["dominant_shell"] == selectable_spectrum["dominant_shell"]

output_paths = selectable_result.get("output_paths", {})
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

metadata = load_json(output_paths["metadata"])
summary = load_json(output_paths["summary"])
diagnostics_df = pd.read_csv(output_paths["diagnostics"])
spectrum_df = pd.read_csv(output_paths["spectrum"])

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

diagnostics_rows_ok = len(diagnostics_df) == STEPS + 1
diagnostics_steps_ok = list(diagnostics_df["step"]) == list(range(0, STEPS + 1))
spectrum_columns_ok = {"k", "E_k", "mode_count"}.issubset(set(spectrum_df.columns))
spectrum_file_finite = np.isfinite(spectrum_df["E_k"].to_numpy()).all()
spectrum_file_nonnegative = float(spectrum_df["E_k"].min()) >= -1e-14

baseline_final_finite = baseline_metrics["finite"]
selectable_final_finite = selectable_metrics["finite"]
baseline_final_real = baseline_metrics["real"]
selectable_final_real = selectable_metrics["real"]
final_shapes_match = baseline_final.shape == selectable_final.shape

field_max_abs_pass = field_max_abs_diff <= FIELD_MAX_ABS_TOL
field_l2_pass = field_l2_diff <= FIELD_L2_TOL
field_relative_l2_pass = field_relative_l2_diff <= FIELD_REL_L2_TOL
energy_relative_pass = energy_relative_difference <= ENERGY_REL_TOL
enstrophy_relative_pass = enstrophy_relative_difference <= ENSTROPHY_REL_TOL
rms_relative_pass = rms_relative_difference <= RMS_REL_TOL
spectrum_relative_l2_pass = spectrum_relative_l2_difference <= SPECTRUM_REL_L2_TOL

equivalence_checks_pass = all(
    [
        baseline_final_finite,
        selectable_final_finite,
        baseline_final_real,
        selectable_final_real,
        final_shapes_match,
        initial_w_unchanged,
        baseline_solver_w_unchanged,
        selectable_solver_w_unchanged,
        field_max_abs_pass,
        field_l2_pass,
        field_relative_l2_pass,
        energy_relative_pass,
        enstrophy_relative_pass,
        rms_relative_pass,
        baseline_spectrum["finite"],
        selectable_spectrum["finite"],
        baseline_spectrum["nonnegative"],
        selectable_spectrum["nonnegative"],
        spectra_same_length,
        spectra_same_k_bins,
        spectrum_relative_l2_pass,
        dominant_shell_matches,
        output_keys_present,
        output_files_exist,
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
        diagnostics_rows_ok,
        diagnostics_steps_ok,
        spectrum_columns_ok,
        spectrum_file_finite,
        spectrum_file_nonnegative,
    ]
)

overall_pass = global_checks_pass and equivalence_checks_pass

print("\n=== EQUIVALENCE METRICS ===")
print(f"field_max_abs_diff: {field_max_abs_diff:.12e}")
print(f"field_l2_diff: {field_l2_diff:.12e}")
print(f"field_relative_l2_diff: {field_relative_l2_diff:.12e}")
print(f"energy_relative_difference: {energy_relative_difference:.12e}")
print(f"enstrophy_relative_difference: {enstrophy_relative_difference:.12e}")
print(f"rms_relative_difference: {rms_relative_difference:.12e}")
print(f"spectrum_relative_l2_difference: {spectrum_relative_l2_difference:.12e}")
print(f"spectrum_energy_sum_relative_difference: {spectrum_energy_sum_relative_difference:.12e}")
print(f"baseline_dominant_shell: {baseline_spectrum['dominant_shell']}")
print(f"selectable_dominant_shell: {selectable_spectrum['dominant_shell']}")

print("\n=== EQUIVALENCE CHECKS ===")
print(f"baseline final finite: {pass_fail(baseline_final_finite)}")
print(f"selectable final finite: {pass_fail(selectable_final_finite)}")
print(f"baseline final real: {pass_fail(baseline_final_real)}")
print(f"selectable final real: {pass_fail(selectable_final_real)}")
print(f"final shapes match: {pass_fail(final_shapes_match)}")
print(f"initial_w unchanged: {pass_fail(initial_w_unchanged)}")
print(f"baseline_solver.w unchanged: {pass_fail(baseline_solver_w_unchanged)}")
print(f"selectable_solver.w unchanged: {pass_fail(selectable_solver_w_unchanged)}")
print(f"field max abs tolerance: {pass_fail(field_max_abs_pass)}")
print(f"field L2 tolerance: {pass_fail(field_l2_pass)}")
print(f"field relative L2 tolerance: {pass_fail(field_relative_l2_pass)}")
print(f"energy relative tolerance: {pass_fail(energy_relative_pass)}")
print(f"enstrophy relative tolerance: {pass_fail(enstrophy_relative_pass)}")
print(f"RMS relative tolerance: {pass_fail(rms_relative_pass)}")
print(f"spectrum relative L2 tolerance: {pass_fail(spectrum_relative_l2_pass)}")
print(f"dominant shell matches: {pass_fail(dominant_shell_matches)}")
print(f"metadata production_ready false: {pass_fail(metadata_production_ready_false)}")
print(f"metadata turbulence false: {pass_fail(metadata_turbulence_false)}")
print(f"metadata k_minus_3 false: {pass_fail(metadata_k_minus_3_false)}")
print(f"Equivalence checks: {pass_fail(equivalence_checks_pass)}")

row = {
    "phase": "11M",
    "test": "fd_centered_diagnostic_run_loop_equivalence",
    "N": N,
    "Re": RE,
    "dt": DT,
    "steps": STEPS,
    "log_every": LOG_EVERY,
    "method": METHOD,
    "global_checks": pass_fail(global_checks_pass),
    "baseline_import_ok": pass_fail(baseline_import_ok),
    "selectable_import_ok": pass_fail(selectable_import_ok),
    "supported_methods_ok": pass_fail(supported_methods_ok),
    "default_method_ok": pass_fail(default_method_ok),
    "selectable_method_ok": pass_fail(selectable_method_ok),
    "rhs_method_exists": pass_fail(rhs_method_exists),
    "step_method_exists": pass_fail(step_method_exists),
    "diagnostic_run_exists": pass_fail(diagnostic_run_exists),
    "run_disabled": pass_fail(run_disabled),
    "spectral_solver_no_diff": pass_fail(spectral_solver_no_diff),
    "advection_operators_no_diff": pass_fail(advection_operators_no_diff),
    "same_grid_shape": pass_fail(same_grid_shape),
    "same_dx": pass_fail(same_dx),
    "same_dt": pass_fail(same_dt),
    "same_nu": pass_fail(same_nu),
    "same_dealias_mask": pass_fail(same_dealias_mask),
    "same_forcing": pass_fail(same_forcing),
    "baseline_final_finite": pass_fail(baseline_final_finite),
    "selectable_final_finite": pass_fail(selectable_final_finite),
    "baseline_final_real": pass_fail(baseline_final_real),
    "selectable_final_real": pass_fail(selectable_final_real),
    "final_shapes_match": pass_fail(final_shapes_match),
    "initial_w_unchanged": pass_fail(initial_w_unchanged),
    "baseline_solver_w_unchanged": pass_fail(baseline_solver_w_unchanged),
    "selectable_solver_w_unchanged": pass_fail(selectable_solver_w_unchanged),
    "field_max_abs_diff": field_max_abs_diff,
    "field_l2_diff": field_l2_diff,
    "field_relative_l2_diff": field_relative_l2_diff,
    "energy_relative_difference": energy_relative_difference,
    "enstrophy_relative_difference": enstrophy_relative_difference,
    "rms_relative_difference": rms_relative_difference,
    "spectrum_relative_l2_difference": spectrum_relative_l2_difference,
    "spectrum_energy_sum_relative_difference": spectrum_energy_sum_relative_difference,
    "baseline_dominant_shell": baseline_spectrum["dominant_shell"],
    "selectable_dominant_shell": selectable_spectrum["dominant_shell"],
    "field_max_abs_pass": pass_fail(field_max_abs_pass),
    "field_l2_pass": pass_fail(field_l2_pass),
    "field_relative_l2_pass": pass_fail(field_relative_l2_pass),
    "energy_relative_pass": pass_fail(energy_relative_pass),
    "enstrophy_relative_pass": pass_fail(enstrophy_relative_pass),
    "rms_relative_pass": pass_fail(rms_relative_pass),
    "spectrum_relative_l2_pass": pass_fail(spectrum_relative_l2_pass),
    "dominant_shell_matches": pass_fail(dominant_shell_matches),
    "output_keys_present": pass_fail(output_keys_present),
    "output_files_exist": pass_fail(output_files_exist),
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
    "diagnostics_rows_ok": pass_fail(diagnostics_rows_ok),
    "diagnostics_steps_ok": pass_fail(diagnostics_steps_ok),
    "spectrum_columns_ok": pass_fail(spectrum_columns_ok),
    "spectrum_file_finite": pass_fail(spectrum_file_finite),
    "spectrum_file_nonnegative": pass_fail(spectrum_file_nonnegative),
    "equivalence_checks": pass_fail(equivalence_checks_pass),
    "overall_result": pass_fail(overall_pass),
}

pd.DataFrame([row]).to_csv(OUT_CSV, index=False)

print("\n=== OVERALL RESULT ===")
print(f"Phase 11M fd_centered diagnostic run-loop equivalence audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_CSV}")
print("Phase 11M audit complete.")