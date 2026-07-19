from pathlib import Path
import subprocess
import time

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


OUT_AUDIT_CSV = Path("PHASE11H_CONTROLLED_FORCED_RESPONSE_SPECTRUM_DIAGNOSTIC_AUDIT.csv")
OUT_SPECTRA_CSV = Path("PHASE11H_CONTROLLED_FORCED_RESPONSE_SPECTRA.csv")
OUT_PAIRWISE_CSV = Path("PHASE11H_CONTROLLED_FORCED_RESPONSE_SPECTRUM_PAIRWISE_SUMMARY.csv")

METHODS = ("fd_centered", "pseudo_spectral", "arakawa")

PAIRS = (
    ("pseudo_spectral", "fd_centered"),
    ("arakawa", "fd_centered"),
    ("arakawa", "pseudo_spectral"),
)

RESOLUTIONS = (64, 128)

RE = 1_000_000
DT = 0.001
STEPS = 1000
LOG_EVERY = 100
TARGET_RMS = 0.01


def pass_fail(condition):
    return "PASS" if bool(condition) else "FAIL"


def rms(field):
    arr = np.asarray(field)
    return float(np.sqrt(np.mean(arr * arr)))


def l2_norm(field):
    arr = np.asarray(field)
    return float(np.sqrt(np.mean(arr * arr)))


def max_abs(field):
    return float(np.max(np.abs(np.asarray(field))))


def relative_error(diff_norm, reference_norm):
    denom = max(abs(float(reference_norm)), 1e-300)
    return float(diff_norm) / denom


def relative_abs_difference(a, b):
    denom = max(abs(float(b)), 1e-300)
    return abs(float(a) - float(b)) / denom


def cosine_similarity(a, b):
    a_flat = np.asarray(a).ravel()
    b_flat = np.asarray(b).ravel()

    denom = np.linalg.norm(a_flat) * np.linalg.norm(b_flat)

    if denom <= 0:
        return np.nan

    return float(np.dot(a_flat, b_flat) / denom)


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


def rescale_to_rms(field, target_rms):
    field_rms = rms(field)

    if field_rms == 0:
        raise ValueError("Cannot rescale zero-RMS field.")

    return field * (target_rms / field_rms)


def kinetic_energy_from_vorticity(solver, w):
    psi = solver.streamfunction(w)
    u, v = solver.velocity(psi)
    return float(0.5 * np.mean(u * u + v * v))


def enstrophy_from_vorticity(w):
    arr = np.asarray(w)
    return float(0.5 * np.mean(arr * arr))


def build_phase6d_like_field(solver):
    X = solver.X
    Y = solver.Y

    raw = (
        np.sin(2 * X) * np.cos(2 * Y)
        + 0.75 * np.sin(3 * X) * np.cos(Y)
        + 0.50 * np.sin(X) * np.cos(4 * Y)
        + 0.35 * np.cos(4 * X - 2 * Y)
    )

    return rescale_to_rms(raw, TARGET_RMS)


def audit_invalid_method(N):
    try:
        SelectableAdvectionSolver(
            nx=N,
            ny=N,
            Re=RE,
            run_path=Path("experiments") / "method_diagnostics" / f"phase11H_invalid_N{N}",
            dt=DT,
            steps=1,
            advection_method="invalid_method",
        )
        return False
    except ValueError:
        return True


def make_solver(N, method):
    return SelectableAdvectionSolver(
        nx=N,
        ny=N,
        Re=RE,
        run_path=Path("experiments") / "method_diagnostics" / f"phase11H_N{N}_{method}",
        dt=DT,
        steps=STEPS,
        advection_method=method,
    )


def forcing_checks_across_methods(N):
    solvers = {method: make_solver(N, method) for method in METHODS}
    forcing_fields = {method: solvers[method].forcing() for method in METHODS}

    forcing_shape_ok = all(field.shape == (N, N) for field in forcing_fields.values())
    forcing_finite = all(np.isfinite(field).all() for field in forcing_fields.values())
    forcing_real = all(np.isrealobj(field) for field in forcing_fields.values())
    forcing_nonzero = all(rms(field) > 0 for field in forcing_fields.values())
    forcing_max_nonzero = all(max_abs(field) > 0 for field in forcing_fields.values())

    reference = forcing_fields["fd_centered"]
    forcing_identical = all(
        np.allclose(field, reference, rtol=0.0, atol=0.0)
        for field in forcing_fields.values()
    )

    return {
        "forcing_shape_ok": forcing_shape_ok,
        "forcing_finite": forcing_finite,
        "forcing_real": forcing_real,
        "forcing_nonzero": forcing_nonzero,
        "forcing_max_nonzero": forcing_max_nonzero,
        "forcing_identical_across_methods": forcing_identical,
        "forcing_rms": rms(reference),
        "forcing_l2": l2_norm(reference),
        "forcing_max_abs": max_abs(reference),
    }


def run_forced_response(N, method, initial_field):
    solver = make_solver(N, method)

    solver_w_before = solver.w.copy()
    force = solver.forcing()

    forcing_shape_ok = force.shape == (N, N)
    forcing_finite = np.isfinite(force).all()
    forcing_real = np.isrealobj(force)
    forcing_nonzero = rms(force) > 0
    forcing_max_nonzero = max_abs(force) > 0

    metadata = solver.selectable_advection_metadata()
    metadata_method_ok = metadata.get("advection_method") == method
    metadata_run_disabled_ok = metadata.get("run_enabled") is False
    metadata_no_turbulence_claim = metadata.get("turbulence_claim") is False
    metadata_no_k_minus_3_claim = metadata.get("k_minus_3_claim") is False

    try:
        solver.run()
        run_disabled = False
    except NotImplementedError:
        run_disabled = True

    w = np.asarray(initial_field).copy()

    initial_w_before = w.copy()
    finite_throughout = np.isfinite(w).all()
    real_throughout = np.isrealobj(w)
    input_not_mutated_each_step = True

    start = time.time()

    for step in range(1, STEPS + 1):
        w_before = w.copy()
        w_next = solver.step_once_selectable(w)

        if not np.allclose(w, w_before, rtol=0.0, atol=0.0):
            input_not_mutated_each_step = False

        w = w_next

        finite_throughout = finite_throughout and np.isfinite(w).all()
        real_throughout = real_throughout and np.isrealobj(w)

        if step % LOG_EVERY == 0 or step == STEPS:
            elapsed = time.time() - start
            energy = kinetic_energy_from_vorticity(solver, w)
            enstrophy = enstrophy_from_vorticity(w)
            print(
                f"N={N}, {method}: step {step}/{STEPS}, "
                f"time={step * DT:.3f}, "
                f"rms={rms(w):.12e}, "
                f"E={energy:.12e}, "
                f"Z={enstrophy:.12e}, "
                f"elapsed={elapsed:.1f}s"
            )

    initial_field_unchanged = np.allclose(
        np.asarray(initial_field),
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

    method_valid = all(
        [
            forcing_shape_ok,
            forcing_finite,
            forcing_real,
            forcing_nonzero,
            forcing_max_nonzero,
            finite_throughout,
            real_throughout,
            input_not_mutated_each_step,
            initial_field_unchanged,
            solver_w_unchanged,
            run_disabled,
            metadata_method_ok,
            metadata_run_disabled_ok,
            metadata_no_turbulence_claim,
            metadata_no_k_minus_3_claim,
        ]
    )

    method_checks = {
        "forcing_shape_ok": pass_fail(forcing_shape_ok),
        "forcing_finite": pass_fail(forcing_finite),
        "forcing_real": pass_fail(forcing_real),
        "forcing_nonzero": pass_fail(forcing_nonzero),
        "forcing_max_nonzero": pass_fail(forcing_max_nonzero),
        "finite_throughout": pass_fail(finite_throughout),
        "real_throughout": pass_fail(real_throughout),
        "input_not_mutated_each_step": pass_fail(input_not_mutated_each_step),
        "initial_field_unchanged": pass_fail(initial_field_unchanged),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "run_disabled": pass_fail(run_disabled),
        "metadata_method_ok": pass_fail(metadata_method_ok),
        "metadata_run_disabled_ok": pass_fail(metadata_run_disabled_ok),
        "metadata_no_turbulence_claim": pass_fail(metadata_no_turbulence_claim),
        "metadata_no_k_minus_3_claim": pass_fail(metadata_no_k_minus_3_claim),
        "method_valid_for_spectrum": pass_fail(method_valid),
    }

    return w, solver, method_checks


def shell_energy(k_bins, Ek, shell):
    mask = np.isclose(k_bins, shell)
    if not np.any(mask):
        return np.nan
    return float(Ek[mask][0])


def summarize_spectrum(N, method, solver, w, method_checks):
    k_bins, Ek, mode_counts = solver.energy_spectrum(w)

    k_bins = np.asarray(k_bins)
    Ek = np.asarray(Ek)
    mode_counts = np.asarray(mode_counts)

    direct_energy = kinetic_energy_from_vorticity(solver, w)
    spectrum_energy_sum = float(np.sum(Ek))
    spectrum_direct_relative_error = relative_abs_difference(
        spectrum_energy_sum,
        direct_energy,
    )

    enstrophy = enstrophy_from_vorticity(w)

    finite_spectrum = np.isfinite(Ek).all()
    min_Ek = float(np.min(Ek)) if len(Ek) else np.nan
    max_Ek = float(np.max(Ek)) if len(Ek) else np.nan
    spectrum_nonnegative_with_tolerance = min_Ek >= -1e-14

    if len(Ek) and np.isfinite(Ek).all():
        dominant_index = int(np.argmax(Ek))
        dominant_shell = float(k_bins[dominant_index])
        dominant_energy = float(Ek[dominant_index])
    else:
        dominant_shell = np.nan
        dominant_energy = np.nan

    # The default forcing modes have component wave numbers (2, 2).
    # Their radial magnitude sqrt(8) is binned at shell 3.
    # This variable records radial-shell-2 energy only.
    k2_energy = shell_energy(k_bins, Ek, 2)
    k3_energy = shell_energy(k_bins, Ek, 3)
    k4_energy = shell_energy(k_bins, Ek, 4)

    low_mask = k_bins <= 4
    high_mask = k_bins >= 10

    if spectrum_energy_sum > 0:
        low_k_fraction = float(np.sum(Ek[low_mask]) / spectrum_energy_sum)
        high_k_fraction = float(np.sum(Ek[high_mask]) / spectrum_energy_sum)
    else:
        low_k_fraction = np.nan
        high_k_fraction = np.nan

    finite_bin_count = int(np.isfinite(Ek).sum())
    nonzero_bin_count = int((np.abs(Ek) > 0).sum())

    energy_consistency_ok = spectrum_direct_relative_error <= 1e-8

    spectrum_summary_ok = all(
        [
            method_checks["method_valid_for_spectrum"] == "PASS",
            finite_spectrum,
            spectrum_nonnegative_with_tolerance,
            energy_consistency_ok,
            np.isfinite(direct_energy),
            np.isfinite(spectrum_energy_sum),
            np.isfinite(enstrophy),
        ]
    )

    audit_row = {
        "N": N,
        "method": method,
        "Re": RE,
        "nu": 1.0 / RE,
        "dt": DT,
        "steps": STEPS,
        "final_time": STEPS * DT,
        "direct_energy": direct_energy,
        "spectrum_energy_sum": spectrum_energy_sum,
        "spectrum_direct_relative_error": spectrum_direct_relative_error,
        "energy_consistency_ok": pass_fail(energy_consistency_ok),
        "enstrophy": enstrophy,
        "dominant_shell": dominant_shell,
        "dominant_shell_energy": dominant_energy,
        "k2_energy": k2_energy,
        "k3_energy": k3_energy,
        "k4_energy": k4_energy,
        "low_k_fraction_k_le_4": low_k_fraction,
        "high_k_fraction_k_ge_10": high_k_fraction,
        "max_Ek": max_Ek,
        "min_Ek": min_Ek,
        "finite_bin_count": finite_bin_count,
        "nonzero_bin_count": nonzero_bin_count,
        "spectrum_finite": pass_fail(finite_spectrum),
        "spectrum_nonnegative_with_tolerance": pass_fail(spectrum_nonnegative_with_tolerance),
        "spectrum_summary_ok": pass_fail(spectrum_summary_ok),
    }

    audit_row.update(method_checks)

    spectrum_rows = []

    for k, e, count in zip(k_bins, Ek, mode_counts):
        spectrum_rows.append(
            {
                "N": N,
                "method": method,
                "k": float(k),
                "E_k": float(e),
                "mode_count": int(count),
            }
        )

    return audit_row, spectrum_rows, k_bins, Ek


def pairwise_spectrum_summary(N, method_a, method_b, method_data):
    data_a = method_data[method_a]
    data_b = method_data[method_b]

    k_a = data_a["k_bins"]
    k_b = data_b["k_bins"]

    if len(k_a) != len(k_b) or not np.allclose(k_a, k_b, rtol=0.0, atol=0.0):
        raise ValueError(f"Spectrum k-bin mismatch for N={N}: {method_a} vs {method_b}")

    Ek_a = data_a["Ek"]
    Ek_b = data_b["Ek"]

    diff = Ek_a - Ek_b

    a_l2 = l2_norm(Ek_a)
    b_l2 = l2_norm(Ek_b)
    diff_l2 = l2_norm(diff)
    diff_max = max_abs(diff)
    rel_spectrum_error = relative_error(diff_l2, b_l2)
    spectrum_cosine = cosine_similarity(Ek_a, Ek_b)

    a_direct_energy = data_a["audit_row"]["direct_energy"]
    b_direct_energy = data_b["audit_row"]["direct_energy"]
    direct_energy_relative_difference = relative_abs_difference(
        a_direct_energy,
        b_direct_energy,
    )

    a_spectrum_energy = data_a["audit_row"]["spectrum_energy_sum"]
    b_spectrum_energy = data_b["audit_row"]["spectrum_energy_sum"]
    spectrum_energy_relative_difference = relative_abs_difference(
        a_spectrum_energy,
        b_spectrum_energy,
    )

    a_enstrophy = data_a["audit_row"]["enstrophy"]
    b_enstrophy = data_b["audit_row"]["enstrophy"]
    enstrophy_relative_difference = relative_abs_difference(a_enstrophy, b_enstrophy)

    a_low = data_a["audit_row"]["low_k_fraction_k_le_4"]
    b_low = data_b["audit_row"]["low_k_fraction_k_le_4"]
    low_k_fraction_abs_difference = abs(float(a_low) - float(b_low))

    a_high = data_a["audit_row"]["high_k_fraction_k_ge_10"]
    b_high = data_b["audit_row"]["high_k_fraction_k_ge_10"]
    high_k_fraction_abs_difference = abs(float(a_high) - float(b_high))

    dominant_shell_agreement = np.isclose(
        data_a["audit_row"]["dominant_shell"],
        data_b["audit_row"]["dominant_shell"],
    )

    spectrum_cosine_ok = spectrum_cosine > 0.99
    relative_spectrum_error_ok = rel_spectrum_error < 0.05
    direct_energy_difference_ok = direct_energy_relative_difference < 0.05
    spectrum_energy_difference_ok = spectrum_energy_relative_difference < 0.05
    low_k_fraction_difference_ok = low_k_fraction_abs_difference < 0.05
    high_k_fraction_difference_ok = high_k_fraction_abs_difference < 0.05

    pairwise_result = all(
        [
            spectrum_cosine_ok,
            relative_spectrum_error_ok,
            direct_energy_difference_ok,
            spectrum_energy_difference_ok,
            low_k_fraction_difference_ok,
            high_k_fraction_difference_ok,
            dominant_shell_agreement,
        ]
    )

    return {
        "N": N,
        "method_a": method_a,
        "method_b_reference": method_b,
        "spectrum_diff_l2": diff_l2,
        "spectrum_diff_max_abs": diff_max,
        "relative_spectrum_error": rel_spectrum_error,
        "spectrum_cosine_similarity": spectrum_cosine,
        "method_a_direct_energy": a_direct_energy,
        "method_b_direct_energy": b_direct_energy,
        "direct_energy_relative_difference": direct_energy_relative_difference,
        "method_a_spectrum_energy_sum": a_spectrum_energy,
        "method_b_spectrum_energy_sum": b_spectrum_energy,
        "spectrum_energy_relative_difference": spectrum_energy_relative_difference,
        "method_a_enstrophy": a_enstrophy,
        "method_b_enstrophy": b_enstrophy,
        "enstrophy_relative_difference": enstrophy_relative_difference,
        "method_a_dominant_shell": data_a["audit_row"]["dominant_shell"],
        "method_b_dominant_shell": data_b["audit_row"]["dominant_shell"],
        "dominant_shell_agreement": pass_fail(dominant_shell_agreement),
        "method_a_low_k_fraction": a_low,
        "method_b_low_k_fraction": b_low,
        "low_k_fraction_abs_difference": low_k_fraction_abs_difference,
        "method_a_high_k_fraction": a_high,
        "method_b_high_k_fraction": b_high,
        "high_k_fraction_abs_difference": high_k_fraction_abs_difference,
        "spectrum_cosine_ok": pass_fail(spectrum_cosine_ok),
        "relative_spectrum_error_ok": pass_fail(relative_spectrum_error_ok),
        "direct_energy_difference_ok": pass_fail(direct_energy_difference_ok),
        "spectrum_energy_difference_ok": pass_fail(spectrum_energy_difference_ok),
        "low_k_fraction_difference_ok": pass_fail(low_k_fraction_difference_ok),
        "high_k_fraction_difference_ok": pass_fail(high_k_fraction_difference_ok),
        "pairwise_result": pass_fail(pairwise_result),
    }


print("\n=== PHASE 11H CONTROLLED FORCED-RESPONSE SPECTRUM DIAGNOSTIC AUDIT ===")
print("Purpose: compute and compare spectra under controlled forced-response conditions.")
print("This does not modify SpectralSolver.")
print("This does not modify SelectableAdvectionSolver.")
print("This does not enable SelectableAdvectionSolver.run().")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")
print("No slope fitting is performed.")

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods_ok = SelectableAdvectionSolver.supported_advection_methods() == METHODS
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
rhs_method_exists = hasattr(SelectableAdvectionSolver, "compute_rhs_selectable")
step_method_exists = hasattr(SelectableAdvectionSolver, "step_once_selectable")
spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")
advection_operators_no_diff = git_file_has_no_diff("project/solver/advection_operators.py")

invalid_methods_rejected = all(audit_invalid_method(N) for N in RESOLUTIONS)

global_pass = all(
    [
        baseline_import_ok,
        selectable_import_ok,
        supported_methods_ok,
        default_method_ok,
        rhs_method_exists,
        step_method_exists,
        spectral_solver_no_diff,
        selectable_solver_no_diff,
        advection_operators_no_diff,
        invalid_methods_rejected,
    ]
)

print("\n=== GLOBAL CHECKS ===")
print(f"SpectralSolver import: {pass_fail(baseline_import_ok)}")
print(f"SelectableAdvectionSolver import: {pass_fail(selectable_import_ok)}")
print(f"Supported methods check: {pass_fail(supported_methods_ok)}")
print(f"Default method fd_centered: {pass_fail(default_method_ok)}")
print(f"compute_rhs_selectable exists: {pass_fail(rhs_method_exists)}")
print(f"step_once_selectable exists: {pass_fail(step_method_exists)}")
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"SelectableAdvectionSolver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"Invalid methods rejected: {pass_fail(invalid_methods_rejected)}")
print(f"Global checks: {pass_fail(global_pass)}")

audit_rows = []
spectrum_rows_all = []
pairwise_rows = []

for N in RESOLUTIONS:
    print(f"\n=== RESOLUTION N={N} ===")

    forcing_global = forcing_checks_across_methods(N)

    forcing_global_pass = all(
        [
            forcing_global["forcing_shape_ok"],
            forcing_global["forcing_finite"],
            forcing_global["forcing_real"],
            forcing_global["forcing_nonzero"],
            forcing_global["forcing_max_nonzero"],
            forcing_global["forcing_identical_across_methods"],
        ]
    )

    print(f"forcing_shape_ok: {pass_fail(forcing_global['forcing_shape_ok'])}")
    print(f"forcing_finite: {pass_fail(forcing_global['forcing_finite'])}")
    print(f"forcing_real: {pass_fail(forcing_global['forcing_real'])}")
    print(f"forcing_nonzero: {pass_fail(forcing_global['forcing_nonzero'])}")
    print(f"forcing_max_nonzero: {pass_fail(forcing_global['forcing_max_nonzero'])}")
    print(f"forcing_identical_across_methods: {pass_fail(forcing_global['forcing_identical_across_methods'])}")
    print(f"forcing_rms: {forcing_global['forcing_rms']:.12e}")
    print(f"forcing_max_abs: {forcing_global['forcing_max_abs']:.12e}")
    print(f"forcing_global_pass: {pass_fail(forcing_global_pass)}")

    field_solver = make_solver(N, "fd_centered")
    initial_field = build_phase6d_like_field(field_solver)

    method_data = {}

    for method in METHODS:
        print(f"\n--- RUN AND SPECTRUM: N={N}, method={method} ---")

        final_w, solver, method_checks = run_forced_response(N, method, initial_field)

        audit_row, spectrum_rows, k_bins, Ek = summarize_spectrum(
            N,
            method,
            solver,
            final_w,
            method_checks,
        )

        audit_row["forcing_global_pass"] = pass_fail(forcing_global_pass)
        audit_row["forcing_rms"] = forcing_global["forcing_rms"]
        audit_row["forcing_max_abs"] = forcing_global["forcing_max_abs"]
        audit_row["global_checks_pass"] = pass_fail(global_pass)

        audit_rows.append(audit_row)
        spectrum_rows_all.extend(spectrum_rows)

        method_data[method] = {
            "final_w": final_w,
            "solver": solver,
            "audit_row": audit_row,
            "k_bins": k_bins,
            "Ek": Ek,
        }

        print(f"direct_energy: {audit_row['direct_energy']:.12e}")
        print(f"spectrum_energy_sum: {audit_row['spectrum_energy_sum']:.12e}")
        print(f"spectrum_direct_relative_error: {audit_row['spectrum_direct_relative_error']:.12e}")
        print(f"energy_consistency_ok: {audit_row['energy_consistency_ok']}")
        print(f"dominant_shell: {audit_row['dominant_shell']}")
        print(f"dominant_shell_energy: {audit_row['dominant_shell_energy']:.12e}")
        print(f"k2_energy: {audit_row['k2_energy']:.12e}")
        print(f"k3_energy: {audit_row['k3_energy']:.12e}")
        print(f"k4_energy: {audit_row['k4_energy']:.12e}")
        print(f"low_k_fraction_k_le_4: {audit_row['low_k_fraction_k_le_4']:.12e}")
        print(f"high_k_fraction_k_ge_10: {audit_row['high_k_fraction_k_ge_10']:.12e}")
        print(f"spectrum_finite: {audit_row['spectrum_finite']}")
        print(f"spectrum_nonnegative_with_tolerance: {audit_row['spectrum_nonnegative_with_tolerance']}")
        print(f"spectrum_summary_ok: {audit_row['spectrum_summary_ok']}")

    print(f"\n--- PAIRWISE SPECTRUM COMPARISONS: N={N} ---")

    for method_a, method_b in PAIRS:
        pair = pairwise_spectrum_summary(N, method_a, method_b, method_data)
        pairwise_rows.append(pair)

        print(f"\n{method_a} vs {method_b}")
        print(f"spectrum_diff_l2: {pair['spectrum_diff_l2']:.12e}")
        print(f"spectrum_diff_max_abs: {pair['spectrum_diff_max_abs']:.12e}")
        print(f"relative_spectrum_error: {pair['relative_spectrum_error']:.12e}")
        print(f"spectrum_cosine_similarity: {pair['spectrum_cosine_similarity']:.12e}")
        print(f"direct_energy_relative_difference: {pair['direct_energy_relative_difference']:.12e}")
        print(f"spectrum_energy_relative_difference: {pair['spectrum_energy_relative_difference']:.12e}")
        print(f"low_k_fraction_abs_difference: {pair['low_k_fraction_abs_difference']:.12e}")
        print(f"high_k_fraction_abs_difference: {pair['high_k_fraction_abs_difference']:.12e}")
        print(f"dominant_shell_agreement: {pair['dominant_shell_agreement']}")
        print(f"pairwise_result: {pair['pairwise_result']}")

audit_df = pd.DataFrame(audit_rows)
spectra_df = pd.DataFrame(spectrum_rows_all)
pairwise_df = pd.DataFrame(pairwise_rows)

audit_df.to_csv(OUT_AUDIT_CSV, index=False)
spectra_df.to_csv(OUT_SPECTRA_CSV, index=False)
pairwise_df.to_csv(OUT_PAIRWISE_CSV, index=False)

spectrum_summary_pass = (audit_df["spectrum_summary_ok"] == "PASS").all()
forcing_pass = (audit_df["forcing_global_pass"] == "PASS").all()
global_checks_pass = (audit_df["global_checks_pass"] == "PASS").all()
pairwise_pass = (pairwise_df["pairwise_result"] == "PASS").all()

overall_pass = bool(
    global_pass
    and global_checks_pass
    and forcing_pass
    and spectrum_summary_pass
    and pairwise_pass
)

print("\n=== OVERALL RESULT ===")
print(f"Global checks pass: {pass_fail(global_pass)}")
print(f"Forcing checks pass: {pass_fail(forcing_pass)}")
print(f"Spectrum summary checks pass: {pass_fail(spectrum_summary_pass)}")
print(f"Pairwise spectrum checks pass: {pass_fail(pairwise_pass)}")
print(f"Phase 11H controlled forced-response spectrum diagnostic audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_AUDIT_CSV}")
print(f"Wrote: {OUT_SPECTRA_CSV}")
print(f"Wrote: {OUT_PAIRWISE_CSV}")
print("Phase 11H controlled forced-response spectrum diagnostic audit complete.")