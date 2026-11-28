#!/usr/bin/env python3
"""Generate four comparable CVE-balanced figures from one run-level CSV."""
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt

LEVELS = [0, 1, 2, 3, 4, 8]
VALID = "FINISHED_BUDGET_LIMITED"
METRICS = [
    ("initial_total_kp", "Observed Key Points", "Mean Initial Key Points", "01_keypoints"),
    ("first_error_round", "First Error Discovery", "Mean First-error Round (detected only)", "02_first_error"),
    ("error_schedules", "Failing Schedules", "Mean Failing Schedules", "03_failing_schedules"),
    ("wall_seconds", "Search Runtime", "Mean Runtime (seconds)", "04_runtime"),
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--prefix", default="workload")
    args = p.parse_args()
    df = pd.read_csv(args.csv)
    required = {"benchmark", "N", "status", *[m[0] for m in METRICS]}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Missing columns: {sorted(missing)}")
    valid = df[df.status == VALID].copy()
    args.out.mkdir(parents=True, exist_ok=True)
    for col, title, ylabel, stem in METRICS:
        # Average repetitions within each CVE first, then give each CVE equal weight.
        by_cve = valid.groupby(["benchmark", "N"])[col].mean().reset_index()
        overall = by_cve.groupby("N")[col].agg(["mean", "std", "count"]).reindex(LEVELS)
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        ax.errorbar(LEVELS, overall["mean"], yerr=overall["std"],
                    marker="o", capsize=4, linewidth=2)
        ax.set_title(title)
        ax.set_xlabel("Workload Level (N)")
        ax.set_ylabel(ylabel)
        ax.set_xticks(LEVELS)
        ax.grid(True, alpha=0.28)
        for n, row in overall.iterrows():
            if pd.notna(row["mean"]):
                ax.annotate(f"{row['mean']:.2f}", (n, row["mean"]),
                            xytext=(0, 8), textcoords="offset points",
                            ha="center", fontsize=8)
        fig.tight_layout()
        fig.savefig(args.out / f"{args.prefix}_{stem}.png", dpi=200)
        fig.savefig(args.out / f"{args.prefix}_{stem}.svg")
        plt.close(fig)

if __name__ == "__main__":
    main()
