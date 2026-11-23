#!/usr/bin/env python3
"""Summarise this method's campaign records.

A campaign that was not started is left blank. It is not written as zero
and it is not written as the schedule limit. Sample standard deviation is
null unless at least two numeric observations exist.
"""
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_table1.json"
CASES = ROOT / "results" / "cases"
OUT = ROOT / "results"


def mean_sd(values):
    nums = [value for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)]
    if len(nums) == 0:
        return None, None, 0
    if len(nums) == 1:
        return nums[0], None, 1
    return statistics.mean(nums), statistics.stdev(nums), len(nums)


def load_records(cve):
    metrics = []
    statuses = []
    directory = CASES / cve
    if not directory.is_dir():
        return metrics, statuses
    for path in sorted(directory.glob("*/metrics.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        item["record"] = path.relative_to(ROOT).as_posix()
        metrics.append(item)
    for path in sorted(directory.glob("*/status.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        item["record"] = path.relative_to(ROOT).as_posix()
        statuses.append(item)
    return metrics, statuses


def main():
    paper = json.loads(PAPER.read_text(encoding="utf-8"))
    per_run = []
    summary = []
    seen_status = set()
    for row in paper["rows"]:
        metrics, statuses = load_records(row["cve"])
        if row["cve"] not in seen_status:
            seen_status.add(row["cve"])
            for status in statuses:
                per_run.append({
                    "cve": row["cve"],
                    "status": status.get("status"),
                    "record": status.get("record"),
                    "bug_result": status.get("bug_result"),
                })
        runs = [item for item in metrics if item.get("row_index") == row["row_index"]]
        valid = [item for item in runs if item.get("status") == "completed"]
        detected = [item for item in valid if item.get("bug_found") is True]
        missed = [item for item in valid if item.get("bug_found") is False]
        first_mean, first_sd, first_n = mean_sd(
            [item.get("schedules_to_first_bug") for item in detected]
        )
        explored_mean, explored_sd, explored_n = mean_sd(
            [item.get("schedules_explored") for item in valid]
        )
        buggy_mean, buggy_sd, buggy_n = mean_sd(
            [item.get("buggy_schedules") for item in valid]
        )
        summary.append({
            "cve": row["cve"],
            "bug_type": row["bug_type"],
            "row_index": row["row_index"],
            "completed_campaigns": len(valid),
            "detected_campaigns": len(detected),
            "no_bug_campaigns": len(missed),
            "not_started": len(runs) == 0,
            "schedules_to_first_bug_mean": first_mean,
            "schedules_to_first_bug_sd": first_sd,
            "schedules_to_first_bug_n": first_n,
            "schedules_explored_mean": explored_mean,
            "schedules_explored_sd": explored_sd,
            "schedules_explored_n": explored_n,
            "buggy_schedules_mean": buggy_mean,
            "buggy_schedules_sd": buggy_sd,
            "buggy_schedules_n": buggy_n,
        })
        for item in runs:
            per_run.append(item)
    OUT.mkdir(exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "per_run.json").write_text(json.dumps(per_run, indent=2) + "\n", encoding="utf-8")
    summary_fields = list(summary[0].keys())
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary)
    with (OUT / "per_run.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["cve", "status", "record", "bug_result", "row_index", "bug_found",
                  "schedules_to_first_bug", "schedules_explored", "buggy_schedules"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(per_run)
    print("rows", len(summary), "completed", sum(row["completed_campaigns"] for row in summary))


if __name__ == "__main__":
    main()
