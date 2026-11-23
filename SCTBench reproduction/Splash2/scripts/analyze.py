#!/usr/bin/env python3
"""Aggregate this group's repetition metrics.

Paths are resolved from this file's location.
With no arguments, read results/cases in this group and write
results/summary.csv and results/per_run.csv.

    python3 analyze.py --collect /path/to/cases

copies programs named in this group's manifest into results/cases.
The source directory is left in place. A destination file with different
bytes is not overwritten.
"""
import csv
import json
import os
import shutil
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_table2.json"
MANIFEST = ROOT / "manifest.json"
OUT = ROOT / "results"
CASES = OUT / "cases"


def mean_sd(values):
    nums = [v for v in values if isinstance(v, (int, float))]
    count = len(nums)
    if count == 0:
        return None, None, 0
    if count == 1:
        return nums[0], None, 1
    return statistics.mean(nums), statistics.stdev(nums), count


def paper_limit(program, schedules):
    if schedules != "L":
        return schedules
    for case in load_manifest()["cases"]:
        if case["id"] == program:
            return case["schedule_limit"]
    return 10000


def load_paper():
    return json.loads(PAPER.read_text(encoding="utf-8"))


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def manifest_ids():
    return [case["id"] for case in load_manifest()["cases"]]


def metrics_path_for(metrics):
    try:
        return metrics.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(metrics)


def flat_program_dirs(cases):
    found = {}
    if not cases.is_dir():
        raise SystemExit("not a directory: %s" % cases)
    for child in sorted(cases.iterdir()):
        if child.is_dir():
            found[child.name] = child
    return found


def submission_program_dirs():
    found = {}
    if not CASES.is_dir():
        return found
    for child in sorted(CASES.iterdir()):
        if not child.is_dir():
            continue
        if child.name in found:
            raise SystemExit("duplicate program directory: %s" % child.name)
        found[child.name] = child
    return found


def program_dirs_for_analysis(cases):
    known = [prog["program"] for prog in load_paper()["programs"]]
    known_set = set(known)
    manifest_set = set(manifest_ids())
    if known_set != manifest_set:
        raise SystemExit("manifest.json and paper_table2.json name different programs")
    if cases is None:
        found = submission_program_dirs()
        if not found:
            group = ROOT.name
            for candidate in (
                Path("/experiment-data/sctbench") / group / "cases",
                Path("/experiment-data/sctbench/cases"),
                Path.home() / "sctbench-data" / "sctbench" / group / "cases",
                Path.home() / "sctbench-data" / "sctbench" / "cases",
            ):
                if candidate.is_dir():
                    found = flat_program_dirs(candidate)
                    break
        if not found:
            raise SystemExit("usage: analyze.py [/path/to/cases]")
        unknown = sorted(name for name in found if name not in known_set)
        if unknown:
            raise SystemExit("submission directory is not in this group: %s" % ", ".join(unknown))
        return {name: found.get(name) for name in known}
    found = flat_program_dirs(cases)
    unknown = sorted(name for name in found if name not in known_set)
    if unknown:
        print("ignoring directories outside this group: %s" % ", ".join(unknown), file=sys.stderr)
    return {name: found.get(name) for name in known}


def files_differ(src, dest):
    if src.stat().st_size != dest.stat().st_size:
        return True
    with src.open("rb") as left, dest.open("rb") as right:
        while True:
            a = left.read(1024 * 1024)
            b = right.read(1024 * 1024)
            if a != b:
                return True
            if not a:
                return False


def copy_new_files(src, dest):
    copied = 0
    for dirpath, _dirnames, filenames in os.walk(str(src)):
        rel = Path(dirpath).relative_to(src)
        target_dir = dest / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for name in filenames:
            source = Path(dirpath) / name
            target = target_dir / name
            if target.exists():
                if files_differ(source, target):
                    raise SystemExit("refusing to overwrite a different file: %s" % target)
                continue
            shutil.copy2(str(source), str(target))
            copied += 1
    return copied


def collect(cases):
    if not cases.is_dir():
        raise SystemExit("not a directory: %s" % cases)
    copied_programs = 0
    copied_files = 0
    missing = []
    for program in manifest_ids():
        source = cases / program
        if not source.is_dir():
            missing.append(program)
            continue
        dest = CASES / program
        dest.parent.mkdir(parents=True, exist_ok=True)
        copied_files += copy_new_files(source, dest)
        copied_programs += 1
    print("collected programs", copied_programs, "new files", copied_files)
    if missing:
        print("no source directory for: %s" % ", ".join(missing))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--collect":
        if len(sys.argv) != 3:
            raise SystemExit("usage: analyze.py --collect /path/to/cases")
        collect(Path(sys.argv[2]))
        return
    if len(sys.argv) > 1:
        cases = Path(sys.argv[1])
    else:
        cases = None
    dirs = program_dirs_for_analysis(cases)
    paper = load_paper()
    OUT.mkdir(exist_ok=True)
    per_run = []
    summary = []
    seen_metrics = set()
    for prog in paper["programs"]:
        name = prog["program"]
        rep_dir = dirs.get(name)
        reps = []
        if rep_dir is not None and rep_dir.exists():
            for metrics in sorted(rep_dir.glob("rep*/metrics.json")):
                key = str(metrics.resolve())
                if key in seen_metrics:
                    raise SystemExit("duplicate metrics file: %s" % metrics)
                seen_metrics.add(key)
                item = json.loads(metrics.read_text(encoding="utf-8"))
                item["metrics_path"] = metrics_path_for(metrics)
                reps.append(item)
                per_run.append(item)
        valid = [r for r in reps if r.get("valid")]
        explored = [r["schedules_explored"] for r in valid]
        errors = [r["error_interleavings"] for r in valid]
        timeouts = [r["timeout_interleavings"] for r in valid if r.get("timeout_interleavings") is not None]
        found = [r for r in valid if r.get("bug_found")]
        firsts = [r["first_bug_schedule"] for r in found if r.get("first_bug_schedule") is not None]
        em, es, en = mean_sd(explored)
        erm, ers, ern = mean_sd(errors)
        fm, fs, fn = mean_sd(firsts)
        tm, ts, tn = mean_sd(timeouts)
        paper_sched = prog["schedules"]
        row = {
            "program": name,
            "valid_reps": len(valid),
            "attempted_reps": len(reps),
            "detection_count": len(found),
            "explored_mean": em,
            "explored_sd": es,
            "explored_n": en,
            "errors_mean": erm,
            "errors_sd": ers,
            "errors_n": ern,
            "first_bug_mean": fm,
            "first_bug_sd": fs,
            "first_bug_n": fn,
            "timeouts_mean": tm,
            "timeouts_sd": ts,
            "timeouts_n": tn,
            "paper_schedules": paper_sched,
            "paper_schedules_numeric": paper_limit(name, paper_sched),
            "paper_bugs": prog["bugs"],
            "stop_reasons": sorted({r.get("stop_reason") for r in valid}),
        }
        if em is not None and isinstance(row["paper_schedules_numeric"], int) and row["paper_schedules_numeric"]:
            row["explored_abs_diff"] = em - row["paper_schedules_numeric"]
            row["explored_rel_diff"] = (em - row["paper_schedules_numeric"]) / row["paper_schedules_numeric"]
        summary.append(row)

    (OUT / "per_run.json").write_text(json.dumps(per_run, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (OUT / "per_run.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["case", "repetition", "valid", "stop_reason", "schedules_explored",
                  "round_footer_total", "error_interleavings", "timeout_interleavings",
                  "first_bug_schedule", "bug_found", "elapsed_sec", "exit_code", "metrics_path"]
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for item in per_run:
            writer.writerow(item)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["program", "valid_reps", "detection_count", "explored_mean", "explored_sd",
                  "explored_n", "errors_mean", "errors_sd", "errors_n", "first_bug_mean",
                  "first_bug_sd", "first_bug_n", "timeouts_mean", "timeouts_sd", "timeouts_n",
                  "paper_schedules", "explored_abs_diff", "explored_rel_diff"]
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in summary:
            writer.writerow(row)
    print("runs", len(per_run), "programs", len(summary))


if __name__ == "__main__":
    main()
