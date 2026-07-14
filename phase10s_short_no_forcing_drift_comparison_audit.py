from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from project.solver.spectral_solver import SpectralSolver
from project.solver.selectable_advection_solver import SelectableAdvectionSolver


OUT_AUDIT_CSV = Path("PHASE10S_SHORT_NO_FORCING_DRIFT_COMPARISON_AUDIT.csv")
OUT_TIME_CSV = Path("PHASE10S_SHORT_NO_FORCING_DRIFT_TIME_HISTORY.csv")
OUT_PAIRWISE_CSV = Path("PHASE10S_SHORT_NO_FORCING_DRIFT_PAIRWISE_SUMMARY.csv")

METHODS = ("fd_centered", "pseudo_spectral", "arakawa")

PAIRS = (
    ("pseudo_spectral", "fd_centered"),
    ("arakawa", "fd_centered"),
    ("arakawa", "pseudo_spectral"),
)

N = 64
RE = 1_000_000
DT = 0.001
STEPS = 1000
LOG_EVERY = 100
TARGET_RMS = 0.01


class NoForcingSelectableAdvectionSolver(SelectableAdvectionSolver):
    """
    Audit-local no-forcing subclass.

    This preserves project/solver/spectral_solver.py and
    project/solver/selectable_advection_solver.py unchanged.
    """

    def forcing(self):
        return np.zeros_like(self.w)


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


def monotone_nonincreasing(values, tolerance=1e-15):
    values = list(values)

    if len(values) < 2:
        return True

    for a, b in zip(values[:-1], values[1:]):
        if b > a + tolerance:
            return False

    return True


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


def audit_invalid_method():
    try:
        NoForcingSelectableAdvectionSolver(
            nx=N,
            ny=N,
            Re=RE,
            run_path=Path("experiments") / "method_diagnostics" / "phase10S_invalid",
            dt=DT,
            steps=1,
            advection_method="invalid_method",
        )
        return False
    except ValueError:
        return True


def make_solver(method):
    return NoForcingSelectableAdvectionSolver(
        nx=N,
        ny=N,
        Re=RE,
        run_path=Path("experiments") / "method_diagnostics" / f"phase10S_{method}",
        dt=DT,
        steps=STEPS,
        advection_method=method,
    )


def record_time_row(method, step, solver, w):
    return {
        "method": method,
        "N": N,
        "Re": RE,
        "nu": 1.0 / RE,
        "dt": DT,
        "steps": STEPS,
        "step": step,
        "time": step * DT,
        "rms_vorticity": rms(w),
        "kinetic_energy": kinetic_energy_from_vorticity(solver, w),
        "enstrophy": enstrophy_from_vorticity(w),
        "max_abs_vorticity": max_abs(w),
        "finite": pass_fail(np.isfinite(w).all()),
        "real": pass_fail(np.isrealobj(w)),
    }


def run_method_drift(method, initial_field):
    solver = make_solver(method)

    solver_w_before = solver.w.copy()
    forcing_zero = max_abs(solver.forcing()) == 0.0

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

    initial_rms = rms(w)
    initial_energy = kinetic_energy_from_vorticity(solver, w)
    initial_enstrophy = enstrophy_from_vorticity(w)
    initial_max_abs = max_abs(w)

    finite_throughout = np.isfinite(w).all()
    real_throughout = np.isrealobj(w)
    input_not_mutated_each_step = True

    time_rows = []
    energy_values = []
    enstrophy_values = []

    row0 = record_time_row(method, 0, solver, w)
    time_rows.append(row0)
    energy_values.append(row0["kinetic_energy"])
    enstrophy_values.append(row0["enstrophy"])

    for step in range(1, STEPS + 1):
        w_before = w.copy()
        w_next = solver.step_once_selectable(w)

        if not np.allclose(w, w_before, rtol=0.0, atol=0.0):
            input_not_mutated_each_step = False

        w = w_next

        finite_throughout = finite_throughout and np.isfinite(w).all()
        real_throughout = real_throughout and np.isrealobj(w)

        if step % LOG_EVERY == 0 or step == STEPS:
            row = record_time_row(method, step, solver, w)
            time_rows.append(row)
            energy_values.append(row["kinetic_energy"])
            enstrophy_values.append(row["enstrophy"])

    final_rms = rms(w)
    final_energy = kinetic_energy_from_vorticity(solver, w)
    final_enstrophy = enstrophy_from_vorticity(w)
    final_max_abs = max_abs(w)

    final_rms_ratio = final_rms / max(initial_rms, 1e-300)
    final_energy_ratio = final_energy / max(initial_energy, 1e-300)
    final_enstrophy_ratio = final_enstrophy / max(initial_enstrophy, 1e-300)

    relative_energy_drift = (final_energy - initial_energy) / max(abs(initial_energy), 1e-300)
    relative_enstrophy_drift = (final_enstrophy - initial_enstrophy) / max(abs(initial_enstrophy), 1e-300)

    solver_w_unchanged = np.allclose(
        solver.w,
        solver_w_before,
        rtol=0.0,
        atol=0.0,
    )

    final_rms_nonexplosive = final_rms_ratio < 1.10
    final_energy_nonexplosive = final_energy_ratio < 1.10
    final_enstrophy_nonexplosive = final_enstrophy_ratio < 1.10

    energy_monotone = monotone_nonincreasing(energy_values)
    enstrophy_monotone = monotone_nonincreasing(enstrophy_values)

    overall = all(
        [
            forcing_zero,
            finite_throughout,
            real_throughout,
            input_not_mutated_each_step,
            solver_w_unchanged,
            run_disabled,
            metadata_method_ok,
            metadata_run_disabled_ok,
            metadata_no_turbulence_claim,
            metadata_no_k_minus_3_claim,
            final_rms_nonexplosive,
            final_energy_nonexplosive,
            final_enstrophy_nonexplosive,
        ]
    )

    summary = {
        "method": method,
        "N": N,
        "Re": RE,
        "nu": 1.0 / RE,
        "dt": DT,
        "steps": STEPS,
        "final_time": STEPS * DT,
        "forcing_zero": pass_fail(forcing_zero),
        "initial_rms": initial_rms,
        "final_rms": final_rms,
        "final_rms_ratio": final_rms_ratio,
        "initial_energy": initial_energy,
        "final_energy": final_energy,
        "relative_energy_drift": relative_energy_drift,
        "final_energy_ratio": final_energy_ratio,
        "initial_enstrophy": initial_enstrophy,
        "final_enstrophy": final_enstrophy,
        "relative_enstrophy_drift": relative_enstrophy_drift,
        "final_enstrophy_ratio": final_enstrophy_ratio,
        "initial_max_abs_vorticity": initial_max_abs,
        "final_max_abs_vorticity": final_max_abs,
        "finite_throughout": pass_fail(finite_throughout),
        "real_throughout": pass_fail(real_throughout),
        "input_not_mutated_each_step": pass_fail(input_not_mutated_each_step),
        "solver_w_unchanged": pass_fail(solver_w_unchanged),
        "run_disabled": pass_fail(run_disabled),
        "metadata_method_ok": pass_fail(metadata_method_ok),
        "metadata_run_disabled_ok": pass_fail(metadata_run_disabled_ok),
        "metadata_no_turbulence_claim": pass_fail(metadata_no_turbulence_claim),
        "metadata_no_k_minus_3_claim": pass_fail(metadata_no_k_minus_3_claim),
        "final_rms_nonexplosive": pass_fail(final_rms_nonexplosive),
        "final_energy_nonexplosive": pass_fail(final_energy_nonexplosive),
        "final_enstrophy_nonexplosive": pass_fail(final_enstrophy_nonexplosive),
        "energy_monotone_nonincreasing_logged": pass_fail(energy_monotone),
        "enstrophy_monotone_nonincreasing_logged": pass_fail(enstrophy_monotone),
        "overall_result": pass_fail(overall),
    }

    return summary, time_rows, w, solver


def pairwise_final_summary(method_a, method_b, final_fields, solvers):
    out_a = final_fields[method_a]
    out_b = final_fields[method_b]

    diff = out_a - out_b

    a_l2 = l2_norm(out_a)
    b_l2 = l2_norm(out_b)
    diff_l2 = l2_norm(diff)
    diff_max = max_abs(diff)
    rel_error = relative_error(diff_l2, b_l2)
    cosine = cosine_similarity(out_a, out_b)

    a_energy = kinetic_energy_from_vorticity(solvers[method_a], out_a)
    b_energy = kinetic_energy_from_vorticity(solvers[method_b], out_b)
    energy_abs_diff = abs(a_energy - b_energy)

    a_enstrophy = enstrophy_from_vorticity(out_a)
    b_enstrophy = enstrophy_from_vorticity(out_b)
    enstrophy_abs_diff = abs(a_enstrophy - b_enstrophy)

    positive_alignment = np.isfinite(cosine) and cosine > 0.99
    no_large_pairwise_disagreement = rel_error < 0.25

    pairwise_result = positive_alignment and no_large_pairwise_disagreement

    return {
        "method_a": method_a,
        "method_b_reference": method_b,
        "N": N,
        "Re": RE,
        "nu": 1.0 / RE,
        "dt": DT,
        "steps": STEPS,
        "final_time": STEPS * DT,
        "method_a_l2": a_l2,
        "method_b_l2": b_l2,
        "diff_l2": diff_l2,
        "diff_max_abs": diff_max,
        "relative_error_vs_method_b": rel_error,
        "cosine_similarity": cosine,
        "method_a_energy": a_energy,
        "method_b_energy": b_energy,
        "energy_abs_diff": energy_abs_diff,
        "method_a_enstrophy": a_enstrophy,
        "method_b_enstrophy": b_enstrophy,
        "enstrophy_abs_diff": enstrophy_abs_diff,
        "positive_alignment": pass_fail(positive_alignment),
        "no_large_pairwise_disagreement": pass_fail(no_large_pairwise_disagreement),
        "pairwise_result": pass_fail(pairwise_result),
    }


print("\n=== PHASE 10S SHORT NO-FORCING DRIFT COMPARISON AUDIT ===")
print("Purpose: compare short no-forcing drift across fd_centered, pseudo_spectral, and arakawa.")
print("This does not modify SpectralSolver.")
print("This does not modify SelectableAdvectionSolver.")
print("This does not enable SelectableAdvectionSolver.run().")
print("This does not run a production simulation.")
print("This does not prove turbulence or k^-3 scaling.")

baseline_import_ok = SpectralSolver is not None
selectable_import_ok = SelectableAdvectionSolver is not None
supported_methods_ok = SelectableAdvectionSolver.supported_advection_methods() == METHODS
default_method_ok = SelectableAdvectionSolver.DEFAULT_ADVECTION_METHOD == "fd_centered"
rhs_method_exists = hasattr(SelectableAdvectionSolver, "compute_rhs_selectable")
step_method_exists = hasattr(SelectableAdvectionSolver, "step_once_selectable")
spectral_solver_no_diff = git_file_has_no_diff("project/solver/spectral_solver.py")
selectable_solver_no_diff = git_file_has_no_diff("project/solver/selectable_advection_solver.py")
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
        spectral_solver_no_diff,
        selectable_solver_no_diff,
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
print(f"SpectralSolver file has no git diff: {pass_fail(spectral_solver_no_diff)}")
print(f"SelectableAdvectionSolver file has no git diff: {pass_fail(selectable_solver_no_diff)}")
print(f"advection_operators file has no git diff: {pass_fail(advection_operators_no_diff)}")
print(f"Invalid method rejected: {pass_fail(invalid_method_rejected)}")
print(f"Global checks: {pass_fail(global_pass)}")

field_solver = make_solver("fd_centered")
initial_field = build_phase6d_like_field(field_solver)

audit_rows = []
time_rows_all = []
final_fields = {}
solvers = {}

for method in METHODS:
    print(f"\n=== METHOD DRIFT: {method} ===")

    summary, time_rows, final_field, solver = run_method_drift(method, initial_field)

    audit_rows.append(summary)
    time_rows_all.extend(time_rows)
    final_fields[method] = final_field
    solvers[method] = solver

    print(f"forcing_zero: {summary['forcing_zero']}")
    print(f"initial_rms: {summary['initial_rms']:.12e}")
    print(f"final_rms: {summary['final_rms']:.12e}")
    print(f"final_rms_ratio: {summary['final_rms_ratio']:.12e}")
    print(f"initial_energy: {summary['initial_energy']:.12e}")
    print(f"final_energy: {summary['final_energy']:.12e}")
    print(f"relative_energy_drift: {summary['relative_energy_drift']:.12e}")
    print(f"final_energy_ratio: {summary['final_energy_ratio']:.12e}")
    print(f"initial_enstrophy: {summary['initial_enstrophy']:.12e}")
    print(f"final_enstrophy: {summary['final_enstrophy']:.12e}")
    print(f"relative_enstrophy_drift: {summary['relative_enstrophy_drift']:.12e}")
    print(f"final_enstrophy_ratio: {summary['final_enstrophy_ratio']:.12e}")
    print(f"finite_throughout: {summary['finite_throughout']}")
    print(f"real_throughout: {summary['real_throughout']}")
    print(f"input_not_mutated_each_step: {summary['input_not_mutated_each_step']}")
    print(f"solver_w_unchanged: {summary['solver_w_unchanged']}")
    print(f"run_disabled: {summary['run_disabled']}")
    print(f"final_rms_nonexplosive: {summary['final_rms_nonexplosive']}")
    print(f"final_energy_nonexplosive: {summary['final_energy_nonexplosive']}")
    print(f"final_enstrophy_nonexplosive: {summary['final_enstrophy_nonexplosive']}")
    print(f"energy_monotone_nonincreasing_logged: {summary['energy_monotone_nonincreasing_logged']}")
    print(f"enstrophy_monotone_nonincreasing_logged: {summary['enstrophy_monotone_nonincreasing_logged']}")
    print(f"overall_result: {summary['overall_result']}")

pairwise_rows = []

print("\n=== FINAL PAIRWISE COMPARISONS ===")

for method_a, method_b in PAIRS:
    pair = pairwise_final_summary(method_a, method_b, final_fields, solvers)
    pairwise_rows.append(pair)

    print(f"\n{method_a} vs {method_b}")
    print(f"diff_l2: {pair['diff_l2']:.12e}")
    print(f"diff_max_abs: {pair['diff_max_abs']:.12e}")
    print(f"relative_error_vs_{method_b}: {pair['relative_error_vs_method_b']:.12e}")
    print(f"cosine_similarity: {pair['cosine_similarity']:.12e}")
    print(f"energy_abs_diff: {pair['energy_abs_diff']:.12e}")
    print(f"enstrophy_abs_diff: {pair['enstrophy_abs_diff']:.12e}")
    print(f"positive_alignment: {pair['positive_alignment']}")
    print(f"no_large_pairwise_disagreement: {pair['no_large_pairwise_disagreement']}")
    print(f"pairwise_result: {pair['pairwise_result']}")

audit_df = pd.DataFrame(audit_rows)
time_df = pd.DataFrame(time_rows_all)
pairwise_df = pd.DataFrame(pairwise_rows)

audit_df.to_csv(OUT_AUDIT_CSV, index=False)
time_df.to_csv(OUT_TIME_CSV, index=False)
pairwise_df.to_csv(OUT_PAIRWISE_CSV, index=False)

method_pass = (audit_df["overall_result"] == "PASS").all()
pairwise_pass = (pairwise_df["pairwise_result"] == "PASS").all()

overall_pass = bool(global_pass and method_pass and pairwise_pass)

print("\n=== OVERALL RESULT ===")
print(f"Global checks pass: {pass_fail(global_pass)}")
print(f"Method drift checks pass: {pass_fail(method_pass)}")
print(f"Final pairwise checks pass: {pass_fail(pairwise_pass)}")
print(f"Phase 10S short no-forcing drift comparison audit: {pass_fail(overall_pass)}")

print("\n=== OUTPUT WRITTEN ===")
print(f"Wrote: {OUT_AUDIT_CSV}")
print(f"Wrote: {OUT_TIME_CSV}")
print(f"Wrote: {OUT_PAIRWISE_CSV}")
print("Phase 10S short no-forcing drift comparison audit complete.")