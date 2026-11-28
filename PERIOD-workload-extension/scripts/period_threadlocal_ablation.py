#!/usr/bin/env python3
"""PERIOD 10-CVE thread-local mutex ablation: 180 fresh runs.

Run from ~/PERIOD-workload-extension, alongside period_all_cve_sweep.py.
Uses a separate output directory and never overwrites the shared-mutex study.
"""
from __future__ import annotations

import argparse
import json
import re
import os
from pathlib import Path

import period_all_cve_sweep as base

# Keep all data separate from the original shared-mutex/shared-counter experiment.
base.LAB = base.ROOT / "all_official_cve_threadlocal_ablation"
base.DONE_WORKLOAD = set()
base.NEW_WORKLOAD = tuple(base.ALL_CVES)
base.WORKERS = {
    "2009-3547": ("pipe_write_open", "involve"),
    "2011-2183": ("thread_one", "thread_two"),
    "2013-1792": ("thread_one", "thread_two"),
    "2015-7550": ("thread1", "thread2"),
    "2016-1972": ("once",),
    "2016-1973": ("thread_one", "thread_two"),
    "2016-7911": ("thread_one", "thread_two"),
    "2016-9806": ("netlink_dump",),
    "2017-6346": ("thread_func",),
    "2017-15265": ("thread_one", "thread_two"),
}


def patch_threadlocal(source: str, cve: str) -> str:
    """Insert N lock/unlock pairs on a mutex local to each worker invocation."""
    if cve not in base.WORKERS:
        raise RuntimeError(f"No verified worker map for {cve}")

    # Fail closed: every configured worker must be a pthread_create target.
    for worker in base.WORKERS[cve]:
        uses = re.findall(
            r"\bpthread_create\s*\([^;]*?,\s*" + re.escape(worker) + r"\s*,",
            source,
            re.S,
        )
        if not uses:
            raise RuntimeError(f"Expected pthread_create using worker {worker} in {cve}")

    helper = r'''
/* THREAD-LOCAL ABLATION: N lock/unlock pairs; no shared counter or shared added mutex. */
#include <stdlib.h>
static int period_extra_n = 0;
static void period_extra_work(void) {
    if (period_extra_n <= 0) return;
    pthread_mutex_t period_local_mutex = PTHREAD_MUTEX_INITIALIZER;
    for (int period_j = 0; period_j < period_extra_n; ++period_j) {
        pthread_mutex_lock(&period_local_mutex);
        pthread_mutex_unlock(&period_local_mutex);
    }
    pthread_mutex_destroy(&period_local_mutex);
}
'''

    lines = source.splitlines(keepends=True)
    include_indices = [i for i, line in enumerate(lines) if re.match(r"^\s*#\s*include\b", line)]
    if not include_indices:
        raise RuntimeError(f"No includes in {cve}")
    lines.insert(max(include_indices) + 1, helper)
    result = "".join(lines)

    # Insert the same helper call at each verified worker entry.
    for worker in base.WORKERS[cve]:
        pattern = re.compile(
            r"(\b(?:static\s+)?void\s*\*\s*"
            + re.escape(worker)
            + r"\s*\(\s*void\s*\*\s*\w+\s*\)\s*\{)"
        )
        result, hits = pattern.subn(
            lambda m: m.group(1) + "\n    period_extra_work();",
            result,
            count=1,
        )
        if hits != 1:
            raise RuntimeError(f"Ambiguous worker function {worker} in {cve}; refusing to patch")

    # Make N a command-line argument, matching the original sweep driver.
    main_pattern = re.compile(r"\bint\s+main\s*\(\s*\)\s*\{")
    main = r'''int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s N\n", argv[0]);
        return 2;
    }
    char *period_end = NULL;
    long period_value = strtol(argv[1], &period_end, 10);
    if (!argv[1][0] || *period_end != '\0' || period_value < 0 || period_value > 8) {
        fprintf(stderr, "N must be an integer in [0,8]\n");
        return 2;
    }
    period_extra_n = (int)period_value;
'''
    result, hits = main_pattern.subn(lambda m: main, result, count=1)
    if hits != 1:
        raise RuntimeError(f"Unsupported main signature in {cve}")

    return result


def prepare():
    base.check_docker()
    for cve in base.ALL_CVES:
        original = base.extract_original(cve)
        original_text = original.read_text(encoding="utf-8")
        patched = patch_threadlocal(original_text, cve)
        target = base.LAB / "sources" / f"{cve}.workload{base.SOURCE_EXT[cve]}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_text(encoding="utf-8") != patched:
                raise RuntimeError(f"Existing ablation source differs; refusing to overwrite: {target}")
        else:
            target.write_text(patched, encoding="utf-8")
        print(
            f"PREPARED CVE-{cve}: {len(original_text.splitlines())} -> "
            f"{len(patched.splitlines())} lines; workers={','.join(base.WORKERS[cve])}",
            flush=True,
        )

    manifest = {
        "created_utc": base.stamp(),
        "image": base.IMAGE,
        "all_cves": list(base.ALL_CVES),
        "levels": list(base.LEVELS),
        "repetitions": list(base.REPEATS),
        "planned_runs": len(base.ALL_CVES) * len(base.LEVELS) * len(base.REPEATS),
        "depth_bound": base.DEPTH,
        "schedule_budget": base.BUDGET,
        "per_execution_timeout_seconds": base.PER_EXEC_TIMEOUT,
        "search_timeout_seconds": base.SEARCH_TIMEOUT,
        "intervention": "At each verified worker entry, perform N lock/unlock pairs on a mutex local to that worker invocation; no shared counter and no shared added mutex.",
        "interpretation": "Thread-local mutex ablation; not a pure Key-Point-only intervention because executed instructions and lock lifecycle also change.",
    }
    (base.LAB / "manifest_threadlocal.json").write_text(json.dumps(manifest, indent=2) + "\n")


# Adapt the original build script so .c and .cpp ablation sources are both copied correctly.
old_copy = 'cp "/extension/sources/${BASE}.workload.cpp" "${BASE}.cpp"'
new_copy = 'cp "/extension/sources/${BASE}.workload${SRC_EXT}" "${BASE}${SRC_EXT}"'
if base.BUILD_IN_CONTAINER.count(old_copy) != 1:
    raise RuntimeError("Unexpected upstream build script; refusing to patch build command")
base.BUILD_IN_CONTAINER = base.BUILD_IN_CONTAINER.replace(old_copy, new_copy, 1)


def plan():
    print("THREAD-LOCAL MUTEX ABLATION")
    print("CVEs:", len(base.ALL_CVES))
    print("N levels:", base.LEVELS)
    print("Repeats:", base.REPEATS)
    print("Planned runs:", len(base.ALL_CVES) * len(base.LEVELS) * len(base.REPEATS))
    print("Settings: -d4 -f60 -t5; pinned Docker image")
    print("Output:", base.LAB)
    print("No shared Counter; each worker gets its own local Mutex.")


def build(retry_failed: bool = False):
    prepare()
    uid, gid = str(os.getuid()), str(os.getgid())
    jobs = [(cve, "workload") for cve in base.ALL_CVES]
    for idx, (cve, kind) in enumerate(jobs, 1):
        dst = base.LAB / "builds" / kind / f"CVE-{cve}"
        if base.guarded(dst, "build_status.txt", retry_failed):
            continue
        dst.mkdir(parents=True, exist_ok=True)
        print(f"BUILD [{idx}/{len(jobs)}] CVE-{cve} thread-local", flush=True)
        rc = base.docker_call("build", base.BUILD_IN_CONTAINER, {
            "CVE_ID": cve,
            "SRC_EXT": base.SOURCE_EXT[cve],
            "BUILD_KIND": kind,
            "BUILD_TIMEOUT": str(base.BUILD_TIMEOUT),
            "HOST_UID": uid,
            "HOST_GID": gid,
        })
        if rc:
            (dst / "build_status.txt").write_text(f"DOCKER_EXIT_{rc}\n")


def run(retry_failed: bool = False):
    base.check_docker()
    jobs = [
        (cve, n, rep)
        for cve in base.ALL_CVES
        for n in base.LEVELS
        for rep in base.REPEATS
    ]
    for idx, (cve, n, rep) in enumerate(jobs, 1):
        print(f"[{idx}/180] CVE-{cve} thread-local N={n} rep={rep}", flush=True)
        base.run_one(cve, "workload", n, rep, retry_failed)
    print("THREAD-LOCAL ABLATION BATCH FINISHED; validating statuses.", flush=True)
    analyze()


def analyze():
    lab = base.LAB
    rows = []
    for cve in base.ALL_CVES:
        for n in base.LEVELS:
            for rep in base.REPEATS:
                folder = lab / "results" / "workload" / f"CVE-{cve}" / f"N{n}" / f"rep{rep}"
                rows.append(base.load_run(folder, cve, "workload", n, rep))

    groups = []
    for cve in base.ALL_CVES:
        for n in base.LEVELS:
            cell = [r for r in rows if r["benchmark"] == f"CVE-{cve}" and r["N"] == n]
            ok = [r for r in cell if r["status"] == "FINISHED_BUDGET_LIMITED"]
            types = "|".join(sorted(set(z for r in ok for z in r["error_types"].split("|") if z)))
            groups.append({
                "benchmark": f"CVE-{cve}", "N": n, "finished": len(ok), "planned": 3,
                "first_error_mean": base.avg([r["first_error_round"] for r in ok]),
                "keypoints_mean": base.avg([r["initial_total_kp"] for r in ok]),
                "failing_schedules_mean": base.avg([r["error_schedules"] for r in ok]),
                "search_wall_seconds_mean": base.avg([r["wall_seconds"] for r in ok]),
                "error_types": types,
                "run_statuses": "|".join(r["status"] for r in cell),
            })

    base.write_csv(lab / "threadlocal_10_cve_runs.csv", rows)
    base.write_csv(lab / "threadlocal_10_cve_group_summary.csv", groups)
    base.write_svg_heatmap(groups, "keypoints_mean", "Observed Key Points: Thread-local Mutex Ablation", "fig_threadlocal_keypoints.svg")
    base.write_svg_heatmap(groups, "first_error_mean", "First Failing Schedule: Thread-local Mutex Ablation", "fig_threadlocal_first_error.svg")

    complete = sum(r["status"] == "FINISHED_BUDGET_LIMITED" for r in rows)
    incomplete = [r for r in rows if r["status"] != "FINISHED_BUDGET_LIMITED"]
    doc = [
        "# PERIOD — Thread-local Mutex Ablation", "",
        "Fresh 10-CVE ablation: each worker executes N lock/unlock pairs on a mutex local to that worker invocation. No shared counter and no shared added mutex.",
        "Fixed settings: N={0,1,2,3,4,8}; 3 repetitions per N; depth bound 4; -f60; -t5; pinned Docker image.",
        "", f"**Completed valid runs: {complete}/180.**",
        f"**Incomplete runs: {len(incomplete)}.** Incomplete attempts remain in the run-level CSV.",
        "", "## Interpretation guardrails",
        "- This is a thread-local mutex ablation, not a pure Key-Point-only intervention.",
        "- The added lock/unlock calls do not create inter-thread contention through this added mutex.",
        "- Executed instructions and lock lifecycle still change; do not attribute all differences solely to Key Points.",
        "- Verify Key Points from PERIOD logs; do not assume every lock call becomes a distinct Key Point.",
        "- A 60-schedule cap is not exhaustive; an absent failure means not observed within this budget.",
        "- Failing schedules are not distinct CVEs; inspect error signatures and ASan traces separately.",
        "- Compare against the original shared-mutex/shared-counter runs at matched CVE, N, repeat, image, depth, budget, and timeout.",
        "", "## Incomplete runs",
    ]
    if incomplete:
        doc.extend(f"- {r['benchmark']} N={r['N']} rep={r['repeat']}: {r['status']}" for r in incomplete)
    else:
        doc.append("- None.")
    (lab / "THREADLOCAL_RESULTS_AND_LIMITATIONS.md").write_text("\n".join(doc) + "\n", encoding="utf-8")

    print("\n=========== THREAD-LOCAL 10-CVE SUMMARY ===========")
    for cve in base.ALL_CVES:
        subset = [g for g in groups if g["benchmark"] == f"CVE-{cve}"]
        valid = sum(g["finished"] for g in subset)
        n0, n8 = subset[0], subset[-1]
        print(f"CVE-{cve:<12} valid={valid:2}/18, KP[N0,N8]=({n0['keypoints_mean']},{n8['keypoints_mean']}), first[N0,N8]=({n0['first_error_mean']},{n8['first_error_mean']})")
    print(f"Completed runs: {complete}/180; incomplete: {len(incomplete)}")
    print("Saved:", lab / "threadlocal_10_cve_runs.csv")
    print("Saved:", lab / "threadlocal_10_cve_group_summary.csv")
    print("Saved:", lab / "THREADLOCAL_RESULTS_AND_LIMITATIONS.md")
    print("Saved: fig_threadlocal_keypoints.svg and fig_threadlocal_first_error.svg")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=("plan", "prepare", "build", "run", "analyze", "all"), default="plan")
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        plan()
    elif args.action == "prepare":
        prepare()
    elif args.action == "build":
        build(args.retry_failed)
    elif args.action == "run":
        run(args.retry_failed)
    elif args.action == "analyze":
        analyze()
    else:
        plan()
        build(args.retry_failed)
        run(args.retry_failed)


if __name__ == "__main__":
    main()
