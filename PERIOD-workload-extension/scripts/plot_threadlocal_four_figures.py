#!/usr/bin/env python3
"""
Draw the same four PERIOD workload-ablation figures from the 10-CVE
thread-local run-level CSV.

Input:
  all_official_cve_threadlocal_ablation/threadlocal_10_cve_runs.csv

Only FINISHED_BUDGET_LIMITED runs are used. For each CVE and N, repetitions
are averaged first; the overall curve then gives each CVE equal weight.
Error bars show +/- 1 standard deviation across CVE-level means.
"""
from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

import matplotlib.pyplot as plt


DEFAULT_LAB = (
    Path.home()
    / "PERIOD-workload-extension"
    / "all_official_cve_threadlocal_ablation"
)
N_LEVELS = [0, 1, 2, 3, 4, 8]

METRICS = [
    (
        "initial_total_kp",
        "Additional Workload vs. Observed Key Points",
        "Initial Key Points",
        "fig_threadlocal_keypoints",
    ),
    (
        "first_error_round",
        "Additional Workload vs. First Detected Error",
        "First failing schedule index",
        "fig_threadlocal_first_error",
    ),
    (
        "error_schedules",
        "Additional Workload vs. Failing Schedules",
        "Observed failing schedules (within 60-schedule budget)",
        "fig_threadlocal_errors",
    ),
    (
        "wall_seconds",
        "Additional Workload vs. Search Runtime",
        "Search wall-clock time (seconds)",
        "fig_threadlocal_runtime",
    ),
]


def number(value):
    """Convert CSV cells to float; blank/None/NaN become missing values."""
    if value is None:
        return None
    value = str(value).strip()
    if not value or value.lower() in {"none", "null", "nan", "na"}:
        return None
    try:
        result = float(value)
    except ValueError:
        return None
    return result if math.isfinite(result) else None


def load_rows(csv_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Cannot find {csv_path}\n"
            "Run the experiment's analyze step first so the run-level CSV exists."
        )

    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = set(reader.fieldnames or [])

    required = {
        "benchmark", "N", "status", "initial_total_kp",
        "first_error_round", "error_schedules", "wall_seconds",
    }
    missing = required - fields
    if missing:
        raise ValueError(
            "The run-level CSV is missing columns: "
            + ", ".join(sorted(missing))
            + f"\nColumns found: {', '.join(sorted(fields))}"
        )

    valid = [
        row for row in rows
        if row.get("status", "").strip() == "FINISHED_BUDGET_LIMITED"
    ]
    return rows, valid


def aggregate_by_cve_and_n(valid_rows, metric):
    """Return {CVE: {N: mean over valid repetitions}}."""
    raw = defaultdict(lambda: defaultdict(list))
    for row in valid_rows:
        cve = row["benchmark"].strip()
        n_value = number(row["N"])
        y_value = number(row.get(metric))
        if n_value is None or y_value is None:
            continue
        n = int(n_value)
        if n in N_LEVELS:
            raw[cve][n].append(y_value)

    return {
        cve: {
            n: mean(values)
            for n, values in by_n.items()
            if values
        }
        for cve, by_n in raw.items()
    }


def plot_metric(valid_rows, metric, title, ylabel, filename, output_dir):
    per_cve = aggregate_by_cve_and_n(valid_rows, metric)
    if not per_cve:
        print(f"SKIP {metric}: no numeric values found")
        return

    fig, ax = plt.subplots(figsize=(10, 6.2))

    # One curve per CVE: average its available valid repetitions at each N.
    for cve in sorted(per_cve):
        xs = [n for n in N_LEVELS if n in per_cve[cve]]
        ys = [per_cve[cve][n] for n in xs]
        if xs:
            ax.plot(xs, ys, marker="o", linewidth=1.5, alpha=0.65, label=cve)

    # Equal-CVE-weighted overall mean and SD across CVEs at each workload level.
    overall_x, overall_mean, overall_sd = [], [], []
    for n in N_LEVELS:
        values = [
            per_cve[cve][n]
            for cve in per_cve
            if n in per_cve[cve]
        ]
        if not values:
            continue
        overall_x.append(n)
        overall_mean.append(mean(values))
        overall_sd.append(stdev(values) if len(values) > 1 else 0.0)

    ax.errorbar(
        overall_x,
        overall_mean,
        yerr=overall_sd,
        marker="D",
        markersize=7,
        linewidth=3,
        capsize=4,
        label="10-CVE mean ± 1 SD",
    )

    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel("Additional workload N", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_xticks(N_LEVELS)
    ax.grid(True, alpha=0.3)
    ax.legend(
        title="Benchmark",
        fontsize=8,
        title_fontsize=9,
        ncol=2,
        frameon=True,
        loc="best",
    )
    fig.tight_layout()

    png_path = output_dir / f"{filename}.png"
    svg_path = output_dir / f"{filename}.svg"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {png_path}")
    print(f"Saved: {svg_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lab",
        type=Path,
        default=DEFAULT_LAB,
        help="Thread-local experiment output directory",
    )
    args = parser.parse_args()

    csv_path = args.lab / "threadlocal_10_cve_runs.csv"
    output_dir = args.lab / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_rows, valid_rows = load_rows(csv_path)

    print(f"Input CSV: {csv_path}")
    print(f"Total planned rows: {len(all_rows)}")
    print(f"Valid completed runs: {len(valid_rows)}")
    print(f"Incomplete/other-status runs: {len(all_rows) - len(valid_rows)}")
    print(f"Output directory: {output_dir}")
    print()

    for metric, title, ylabel, filename in METRICS:
        plot_metric(
            valid_rows, metric, title, ylabel, filename, output_dir
        )

    print("\nDone. Four figures have been generated.")
    print(
        "Note: missing first-error values are omitted, not treated as zero. "
        "Incomplete runs are excluded."
    )


if __name__ == "__main__":
    main()
