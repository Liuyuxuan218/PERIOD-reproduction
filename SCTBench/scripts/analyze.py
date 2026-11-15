#!/usr/bin/env python3
"""Aggregate SCTBench repetition logs and compare them with Table 2."""
import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_table2.json"
OUT = ROOT / "results"


def mean_sd(values):
    nums = [v for v in values if isinstance(v, (int, float))]
    if not nums:
        return None, None, 0
    if len(nums) == 1:
        return nums[0], 0.0, 1
    return statistics.mean(nums), statistics.stdev(nums), len(nums)


def paper_limit(program, schedules):
    if schedules != "L":
        return schedules
    if program == "CS.twostage_100_bad":
        return 100000
    return 10000


def main():
    if len(sys.argv) > 1:
        cases = Path(sys.argv[1])
    else:
        cases = None
        for candidate in (
            Path("/experiment-data/sctbench/cases"),
            Path.home() / "sctbench-data" / "sctbench" / "cases",
        ):
            if candidate.is_dir():
                cases = candidate
                break
        if cases is None:
            raise SystemExit("usage: analyze.py /path/to/sctbench/cases")
    global CASES
    CASES = cases
    paper = json.loads(PAPER.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    per_run = []
    summary = []
    for prog in paper["programs"]:
        name = prog["program"]
        rep_dir = CASES / name
        reps = []
        if rep_dir.exists():
            for metrics in sorted(rep_dir.glob("rep*/metrics.json")):
                item = json.loads(metrics.read_text(encoding="utf-8"))
                item["metrics_path"] = str(metrics)
                reps.append(item)
                per_run.append(item)
        valid = [r for r in reps if r.get("valid")]
        explored = [r["schedules_explored"] for r in valid]
        errors = [r["error_interleavings"] for r in valid]
        timeouts = [r["timeout_interleavings"] for r in valid if r.get("timeout_interleavings") is not None]
        found = [r for r in valid if r.get("bug_found")]
        firsts = [r["first_bug_schedule"] for r in found if r.get("first_bug_schedule") is not None]
        em, es, en = mean_sd(explored)
        erm, ers, _ = mean_sd(errors)
        fm, fs, fn = mean_sd(firsts)
        tm, ts, _ = mean_sd(timeouts)
        paper_sched = prog["schedules"]
        row = {
            "program": name,
            "valid_reps": len(valid),
            "attempted_reps": len(reps),
            "detection_count": len(found),
            "explored_mean": em,
            "explored_sd": es,
            "errors_mean": erm,
            "errors_sd": ers,
            "first_bug_mean": fm,
            "first_bug_sd": fs,
            "first_bug_n": fn,
            "timeouts_mean": tm,
            "timeouts_sd": ts,
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
                  "errors_mean", "errors_sd", "first_bug_mean", "first_bug_sd", "first_bug_n",
                  "timeouts_mean", "paper_schedules", "explored_abs_diff", "explored_rel_diff"]
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in summary:
            writer.writerow(row)
    print("runs", len(per_run), "programs", len(summary))


if __name__ == "__main__":
    main()
