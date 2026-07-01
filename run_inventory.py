import argparse
import csv
import json
import math
from pathlib import Path


def short_text(value, width=18):
    if value is None:
        return ""
    text = str(value)
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."


def to_float(value):
    try:
        return float(value)
    except Exception:
        return math.nan


def is_false(value):
    if value is False:
        return True
    if isinstance(value, str) and value.lower() == "false":
        return True
    return False


def load_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_last_diagnostics(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return None

    return rows[-1]


def sum_spectrum(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return math.nan, "missing_spectrum_header"

        if "E(k)" in reader.fieldnames:
            energy_col = "E(k)"
        elif "Ek" in reader.fieldnames:
            energy_col = "Ek"
        else:
            return math.nan, "missing_Ek_column"

        total = 0.0
        count = 0

        for row in reader:
            val = to_float(row.get(energy_col))
            if math.isfinite(val):
                total += val
                count += 1

        if count == 0:
            return math.nan, "empty_spectrum_values"

        return total, ""


def extract_re(metadata):
    config = metadata.get("config", {})

    if isinstance(config, dict) and "Re" in config:
        return config["Re"], ""

    # Detect older nested metadata bug but still report Re if available.
    if isinstance(config, dict) and isinstance(config.get("config"), dict):
        nested = config["config"]
        if "Re" in nested:
            return nested["Re"], "nested_metadata"

    return "", "missing_Re"


def audit_run(run_path, rtol):
    notes = []

    metadata_path = run_path / "metadata.json"
    diagnostics_path = run_path / "diagnostics.csv"
    spectrum_path = run_path / "spectrum.csv"

    metadata = {}

    if metadata_path.exists():
        try:
            metadata = load_json(metadata_path)
        except Exception as exc:
            notes.append(f"metadata_read_error:{type(exc).__name__}")
    else:
        notes.append("missing_metadata")

    re_value, re_note = extract_re(metadata)
    if re_note:
        notes.append(re_note)

    status = metadata.get("status", "")
    git_commit = metadata.get("git_commit", "")
    git_dirty = metadata.get("git_dirty", "")

    energy = math.nan
    sum_ek = math.nan
    rel_err = math.nan

    if diagnostics_path.exists():
        try:
            last_diag = load_last_diagnostics(diagnostics_path)
            if last_diag is None:
                notes.append("empty_diagnostics")
            else:
                energy = to_float(last_diag.get("energy"))
        except Exception as exc:
            notes.append(f"diagnostics_read_error:{type(exc).__name__}")
    else:
        notes.append("missing_diagnostics")

    if spectrum_path.exists():
        try:
            sum_ek, spectrum_note = sum_spectrum(spectrum_path)
            if spectrum_note:
                notes.append(spectrum_note)
        except Exception as exc:
            notes.append(f"spectrum_read_error:{type(exc).__name__}")
    else:
        notes.append("missing_spectrum")

    if math.isfinite(energy) and math.isfinite(sum_ek):
        denom = max(abs(energy), 1e-300)
        rel_err = abs(sum_ek - energy) / denom
    else:
        notes.append("nonfinite_energy_or_spectrum")

    passed = True

    if status != "completed":
        passed = False
        notes.append("status_not_completed")

    if not is_false(git_dirty):
        passed = False
        notes.append("git_dirty_or_unknown")

    if not math.isfinite(rel_err) or rel_err > rtol:
        passed = False
        notes.append("energy_spectrum_mismatch")

    return {
        "run_id": run_path.name,
        "Re": re_value,
        "status": status,
        "git_commit": str(git_commit)[:7] if git_commit else "",
        "git_dirty": git_dirty,
        "energy": energy,
        "sum_Ek": sum_ek,
        "rel_err": rel_err,
        "result": "PASS" if passed else "FAIL",
        "notes": ";".join(dict.fromkeys(notes)),
    }


def format_float(value):
    if not math.isfinite(value):
        return "nan"
    return f"{value:.6e}"


def print_table(rows):
    headers = [
        "run_id",
        "Re",
        "status",
        "commit",
        "dirty",
        "energy",
        "sum_Ek",
        "rel_err",
        "result",
        "notes",
    ]

    table = []

    for row in rows:
        table.append(
            [
                short_text(row["run_id"], 28),
                str(row["Re"]),
                str(row["status"]),
                str(row["git_commit"]),
                str(row["git_dirty"]),
                format_float(row["energy"]),
                format_float(row["sum_Ek"]),
                format_float(row["rel_err"]),
                row["result"],
                short_text(row["notes"], 50),
            ]
        )

    widths = [len(h) for h in headers]

    for line in table:
        for i, cell in enumerate(line):
            widths[i] = max(widths[i], len(cell))

    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * widths[i] for i in range(len(headers)))

    print(header_line)
    print(sep_line)

    for line in table:
        print(" | ".join(line[i].ljust(widths[i]) for i in range(len(headers))))


def write_csv(rows, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "run_id",
        "Re",
        "status",
        "git_commit",
        "git_dirty",
        "energy",
        "sum_Ek",
        "rel_err",
        "result",
        "notes",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Audit experiment run folders.")
    parser.add_argument("--base", default="experiments/runs", help="Base run folder.")
    parser.add_argument("--latest", type=int, default=None, help="Only show latest N runs.")
    parser.add_argument("--rtol", type=float, default=1e-8, help="Relative tolerance for energy vs sum E(k).")
    parser.add_argument("--csv", default=None, help="Optional CSV output path.")

    args = parser.parse_args()

    base = Path(args.base)

    if not base.exists():
        raise SystemExit(f"Run folder does not exist: {base}")

    run_dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith("run_")]
    run_dirs = sorted(run_dirs, key=lambda p: p.stat().st_mtime, reverse=True)

    if args.latest is not None:
        run_dirs = run_dirs[: args.latest]

    rows = [audit_run(run_path, args.rtol) for run_path in run_dirs]

    print_table(rows)

    total = len(rows)
    passed = sum(1 for row in rows if row["result"] == "PASS")
    failed = total - passed

    print()
    print(f"Total runs: {total}")
    print(f"PASS:       {passed}")
    print(f"FAIL:       {failed}")

    if args.csv:
        write_csv(rows, args.csv)
        print(f"CSV saved:  {args.csv}")


if __name__ == "__main__":
    main()