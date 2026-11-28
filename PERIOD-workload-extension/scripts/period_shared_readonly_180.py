
#!/usr/bin/env python3
'''PERIOD 10-CVE shared-read-only scheduling-point extension (180 planned runs).

A shared volatile table is initialized in main BEFORE pthread_create. Workers
only read it. N controls 8*N active entries plus one zero sentinel.

IMPORTANT: PERIOD's default static-analysis pipeline can filter read-only
memory groups. This script manually appends the helper's read source line to
ConConfig after staticAnalysis.sh and before DBDS instrumentation. This is a
manual scheduling-point extension, not automatic SVF discovery.
'''
from __future__ import annotations
import argparse, json, os, re, sys
from pathlib import Path
import period_all_cve_sweep as base

base.LAB = base.ROOT / "all_official_cve_shared_readonly_ablation"
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
TABLE_SIZE = 65
READS_PER_N = 8
PREFLIGHT_CVE = "2009-3547"


def patch_source(src: str, cve: str):
    if "period_shared_readonly_table" in src:
        raise RuntimeError(f"CVE-{cve}: source already patched")
    for worker in base.WORKERS[cve]:
        if not re.search(
            r"\bpthread_create\s*\([^;]*?,\s*" + re.escape(worker) + r"\s*,",
            src, re.S
        ):
            raise RuntimeError(f"CVE-{cve}: pthread_create target {worker} not found")

    helper = r'''
/* Shared table: initialized before worker creation, read-only in workers. */
static volatile unsigned long period_shared_readonly_table[65];
static __attribute__((noinline)) unsigned long period_shared_read_work(void) {
    unsigned long period_sum = 0UL;
    for (unsigned long period_i = 0UL; period_i < 65UL; ++period_i) {
        unsigned long period_value = period_shared_readonly_table[period_i];
        if (period_value == 0UL) break;
        period_sum += period_value;
    }
    return period_sum;
}
'''
    lines = src.splitlines(keepends=True)
    includes = [i for i, x in enumerate(lines) if re.match(r"^\s*#\s*include\b", x)]
    if not includes:
        raise RuntimeError(f"CVE-{cve}: no include directives")
    if not any(re.match(r'^\s*#\s*include\s*[<"]stdlib\.h[>"]', x) for x in lines):
        lines.insert(max(includes) + 1, "#include <stdlib.h>\n")
        includes = [i for i, x in enumerate(lines) if re.match(r"^\s*#\s*include\b", x)]
    lines.insert(max(includes) + 1, helper)
    patched = "".join(lines)

    for worker in base.WORKERS[cve]:
        pat = re.compile(
            r"(\b(?:static\s+)?void\s*\*\s*" + re.escape(worker)
            + r"\s*\(\s*void\s*\*\s*\w+\s*\)\s*\{)"
        )
        patched, hits = pat.subn(
            lambda m: m.group(1) + "\n    (void)period_shared_read_work();",
            patched, count=1
        )
        if hits != 1:
            raise RuntimeError(f"CVE-{cve}: cannot uniquely patch worker {worker}")

    main_pat = re.compile(r"\bint\s+main\s*\(\s*(?:void\s*)?\)\s*\{")
    main_prefix = r'''int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s N\n", argv[0]);
        return 2;
    }
    char *period_end = NULL;
    long period_n = strtol(argv[1], &period_end, 10);
    if (!argv[1][0] || *period_end != '\0' || period_n < 0 || period_n > 8) {
        fprintf(stderr, "N must be an integer in [0,8]\n");
        return 2;
    }
    unsigned long period_active = (unsigned long)period_n * 8UL;
    /* Initialize all shared data before any worker thread is created. */
    for (int period_i = 0; period_i < 65; ++period_i) {
        period_shared_readonly_table[period_i] =
            ((unsigned long)period_i < period_active)
                ? (unsigned long)(period_i + 1) : 0UL;
    }
'''
    patched, hits = main_pat.subn(lambda _m: main_prefix, patched, count=1)
    if hits != 1:
        raise RuntimeError(f"CVE-{cve}: unsupported main() signature")

    marker = "unsigned long period_value = period_shared_readonly_table[period_i];"
    read_lines = [i for i, x in enumerate(patched.splitlines(), 1) if marker in x]
    if len(read_lines) != 1:
        raise RuntimeError(f"CVE-{cve}: expected one helper read site, got {read_lines}")
    return patched, read_lines[0]


def prepare():
    base.check_docker()
    base.LAB.mkdir(parents=True, exist_ok=True)
    kp_map = {}
    for cve in base.ALL_CVES:
        original = base.extract_original(cve).read_text(encoding="utf-8")
        patched, read_line = patch_source(original, cve)
        ext = base.SOURCE_EXT[cve]
        src_path = base.LAB / "sources" / f"{cve}.workload{ext}"
        src_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.exists() and src_path.read_text(encoding="utf-8") != patched:
            raise RuntimeError(f"Refusing to overwrite changed source: {src_path}")
        if not src_path.exists():
            src_path.write_text(patched, encoding="utf-8")
        kp_line = f"{cve}{ext}:{read_line}"
        kp_path = base.LAB / "sources" / f"{cve}.kp_lines"
        if kp_path.exists() and kp_path.read_text().strip() != kp_line:
            raise RuntimeError(f"KP metadata differs: {kp_path}")
        kp_path.write_text(kp_line + "\n", encoding="utf-8")
        kp_map[cve] = kp_line
        print(f"PREPARED CVE-{cve}: workers={base.WORKERS[cve]}, manual KP={kp_line}", flush=True)

    manifest = {
        "experiment": "Shared read-only workload / manual scheduling-point extension",
        "image": base.IMAGE, "cves": list(base.ALL_CVES),
        "levels": list(base.LEVELS), "repetitions": list(base.REPEATS),
        "planned_runs": len(base.ALL_CVES) * len(base.LEVELS) * len(base.REPEATS),
        "depth": base.DEPTH, "schedule_budget": base.BUDGET,
        "per_execution_timeout": base.PER_EXEC_TIMEOUT,
        "table_size": TABLE_SIZE, "active_reads_per_worker": "8*N plus one sentinel read",
        "manual_conconfig_lines": kp_map,
        "safety": "Table is initialized in main before pthread_create and never written by workers.",
        "method_note": "Read site is manually appended to ConConfig because read-only memory groups may be filtered by default analysis.",
        "limits": [
            "One static read site repeats dynamically; this increases dynamic KP occurrences/DKPS length, not distinct static source sites.",
            "N=0 still performs one sentinel read per worker.",
            "Timing changes may still alter original bug exposure.",
            "A 60-schedule cap is not exhaustive.",
        ],
    }
    (base.LAB / "manifest_shared_readonly.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def patch_build_driver():
    old = '  cp "/extension/sources/${BASE}.workload.cpp" "${BASE}.cpp"'
    new = '  cp "/extension/sources/${BASE}.workload${SRC_EXT}" "${BASE}${SRC_EXT}"'
    if base.BUILD_IN_CONTAINER.count(old) != 1:
        raise RuntimeError("Unexpected upstream source-copy command")
    base.BUILD_IN_CONTAINER = base.BUILD_IN_CONTAINER.replace(old, new, 1)

    needle = 'fi\nsha256sum "${BASE}${SRC_EXT}"'
    if base.BUILD_IN_CONTAINER.count(needle) != 1:
        raise RuntimeError("Unexpected build-driver hook location")
    hook = r'''fi
if [ "$BUILD_KIND" = "workload" ]; then
python3 - "$BASE" <<'PY'
from pathlib import Path
import sys
base = sys.argv[1]
p = Path("build.sh")
text = p.read_text()
needle = f"$ROOT_DIR/tool/staticAnalysis/staticAnalysis.sh {base}"
if text.count(needle) != 1:
    raise SystemExit(f"Expected one staticAnalysis.sh line for {base}; got {text.count(needle)}")
kpfile = Path("/extension/sources") / f"{base}.kp_lines"
kp = [x.strip() for x in kpfile.read_text().splitlines() if x.strip()]
if len(kp) != 1:
    raise SystemExit(f"Expected one KP line in {kpfile}")
config = f"ConConfig.{base}"
snippet = "\n".join([
    f'test -s "{config}" || {{ echo "Missing {config}" >&2; exit 1; }}',
    "while IFS= read -r kp_line; do",
    f'  grep -Fxq "$kp_line" "{config}" || printf "%s\\\\n" "$kp_line" >> "{config}"',
    f'done < "/extension/sources/{base}.kp_lines"',
])
p.write_text(text.replace(needle, needle + "\n" + snippet, 1))
PY
fi
sha256sum "${BASE}${SRC_EXT}"'''
    base.BUILD_IN_CONTAINER = base.BUILD_IN_CONTAINER.replace(needle, hook, 1)

    old_config = 'cp "ConConfig.${BASE}" "$DST/ConConfig.${BASE}"\n'
    new_config = r'''cp "ConConfig.${BASE}" "$DST/ConConfig.${BASE}"
if [ "$BUILD_KIND" = "workload" ]; then
  while IFS= read -r kp_line; do
    grep -Fxq "$kp_line" "$DST/ConConfig.${BASE}" || {
      echo "MANUAL_KP_LINE_MISSING: $kp_line" > "$DST/build_status.txt"
      exit 0
    }
  done < "/extension/sources/${BASE}.kp_lines"
fi
'''
    if base.BUILD_IN_CONTAINER.count(old_config) != 1:
        raise RuntimeError("Unexpected ConConfig copy command")
    base.BUILD_IN_CONTAINER = base.BUILD_IN_CONTAINER.replace(old_config, new_config, 1)


def plan():
    print("PERIOD SHARED READ-ONLY WORKLOAD")
    print("CVEs:", len(base.ALL_CVES), "N:", base.LEVELS, "repeats:", base.REPEATS)
    print("Planned:", len(base.ALL_CVES) * len(base.LEVELS) * len(base.REPEATS), "runs")
    print("Fixed: -d4 -f60 -t5; pinned Docker image")
    print("Workers read 8*N shared table values plus one sentinel.")
    print("No worker-side table writes, added mutex, or shared counter.")
    print("The read site is manually appended to ConConfig.")
    print("Preflight uses CVE-2009-3547 N=0 and N=4 as two of the 180 runs.")
    print("Output:", base.LAB)


def build(retry_failed=False):
    prepare()
    patch_build_driver()
    uid, gid = str(os.getuid()), str(os.getgid())
    for i, cve in enumerate(base.ALL_CVES, 1):
        dst = base.LAB / "builds" / "workload" / f"CVE-{cve}"
        if base.guarded(dst, "build_status.txt", retry_failed):
            continue
        dst.mkdir(parents=True, exist_ok=True)
        print(f"BUILD [{i}/10] CVE-{cve}", flush=True)
        rc = base.docker_call("build", base.BUILD_IN_CONTAINER, {
            "CVE_ID": cve, "SRC_EXT": base.SOURCE_EXT[cve],
            "BUILD_KIND": "workload", "BUILD_TIMEOUT": str(base.BUILD_TIMEOUT),
            "HOST_UID": uid, "HOST_GID": gid,
        })
        if rc and not (dst / "build_status.txt").exists():
            (dst / "build_status.txt").write_text(f"DOCKER_EXIT_{rc}\n")
        sf = dst / "build_status.txt"
        status = sf.read_text().strip() if sf.exists() else "MISSING"
        print("BUILD STATUS:", status, flush=True)
        if status != "OK":
            raise RuntimeError(f"CVE-{cve} build did not succeed: {status}; inspect {dst / 'build.log'}")

    bad = []
    for cve in base.ALL_CVES:
        status_file = base.LAB / "builds" / "workload" / f"CVE-{cve}" / "build_status.txt"
        status = status_file.read_text().strip() if status_file.exists() else "MISSING"
        if status != "OK":
            bad.append(f"CVE-{cve}={status}")
    if bad:
        raise RuntimeError("Not all 10 workload binaries are ready: " + ", ".join(bad))


def run_path(cve, n, rep):
    return base.LAB / "results" / "workload" / f"CVE-{cve}" / f"N{n}" / f"rep{rep}"


def preflight(retry_failed=False):
    print("\n========== PRE-FLIGHT (2 of 180 cells) ==========", flush=True)
    for n in (0, 4):
        base.run_one(PREFLIGHT_CVE, "workload", n, 1, retry_failed)
    r0 = base.load_run(run_path(PREFLIGHT_CVE, 0, 1), PREFLIGHT_CVE, "workload", 0, 1)
    r4 = base.load_run(run_path(PREFLIGHT_CVE, 4, 1), PREFLIGHT_CVE, "workload", 4, 1)
    print("KP preflight:", r0["initial_total_kp"], "->", r4["initial_total_kp"],
          "| statuses:", r0["status"], r4["status"], flush=True)
    if r0["status"] != "FINISHED_BUDGET_LIMITED" or r4["status"] != "FINISHED_BUDGET_LIMITED":
        raise RuntimeError("Preflight run incomplete; inspect its logs before continuing.")
    if r0["initial_total_kp"] is None or r4["initial_total_kp"] is None:
        raise RuntimeError("Could not parse kpNumArray; stopping before the remaining 178 runs.")
    if r4["initial_total_kp"] <= r0["initial_total_kp"]:
        raise RuntimeError(
            "N=4 did not increase dynamic Key Points over N=0. "
            "ConConfig/manual instrumentation may not have taken effect; stopping."
        )
    print("Preflight passed; continuing with the remaining matrix.", flush=True)


def run(retry_failed=False):
    base.check_docker()
    preflight(retry_failed)
    jobs = [(c, n, r) for c in base.ALL_CVES for n in base.LEVELS for r in base.REPEATS]
    for i, (cve, n, rep) in enumerate(jobs, 1):
        print(f"[{i}/180] CVE-{cve} shared-read-only N={n} rep={rep}", flush=True)
        base.run_one(cve, "workload", n, rep, retry_failed)
    analyze()


def analyze():
    rows = []
    for cve in base.ALL_CVES:
        for n in base.LEVELS:
            for rep in base.REPEATS:
                rows.append(base.load_run(run_path(cve, n, rep), cve, "workload", n, rep))
    groups = []
    for cve in base.ALL_CVES:
        for n in base.LEVELS:
            cell = [x for x in rows if x["benchmark"] == f"CVE-{cve}" and x["N"] == n]
            ok = [x for x in cell if x["status"] == "FINISHED_BUDGET_LIMITED"]
            groups.append({
                "benchmark": f"CVE-{cve}", "N": n, "finished": len(ok), "planned": 3,
                "keypoints_mean": base.avg([x["initial_total_kp"] for x in ok]),
                "first_error_mean": base.avg([x["first_error_round"] for x in ok]),
                "failing_schedules_mean": base.avg([x["error_schedules"] for x in ok]),
                "search_wall_seconds_mean": base.avg([x["wall_seconds"] for x in ok]),
                "error_types": "|".join(sorted({e for x in ok for e in x["error_types"].split("|") if e})),
                "run_statuses": "|".join(x["status"] for x in cell),
            })
    lab = base.LAB
    base.write_csv(lab / "shared_readonly_10_cve_runs.csv", rows)
    base.write_csv(lab / "shared_readonly_10_cve_group_summary.csv", groups)
    base.write_svg_heatmap(groups, "keypoints_mean", "Dynamic Key Points: Shared Read-only Workload",
                           "fig_shared_readonly_keypoints.svg")
    base.write_svg_heatmap(groups, "first_error_mean", "First Error: Shared Read-only Workload",
                           "fig_shared_readonly_first_error.svg")
    complete = sum(x["status"] == "FINISHED_BUDGET_LIMITED" for x in rows)
    incomplete = [x for x in rows if x["status"] != "FINISHED_BUDGET_LIMITED"]
    doc = [
        "# PERIOD — Shared Read-only Workload", "",
        "10 CVEs x 6 levels x 3 repetitions = 180 planned cells.",
        "Fixed -d4, -f60, -t5, pinned Docker image.",
        f"Completed valid runs: {complete}/180.",
        f"Incomplete runs: {len(incomplete)}.", "",
        "## Method",
        "- Shared volatile table initialized in main before pthread_create.",
        "- Worker threads only read the table; no worker-side writes or added lock.",
        "- N controls 8*N active entries plus one zero sentinel.",
        "- The helper read line is manually appended to ConConfig after staticAnalysis.sh.",
        "", "## Interpretation limits",
        "- Manual scheduling-point extension; not automatic SVF discovery.",
        "- One static read site repeats dynamically; dynamic KP occurrences/DKPS length increase, not distinct static sites.",
        "- N=0 still performs one sentinel read per worker.",
        "- Timing changes can alter original bug exposure.",
        "- 60 schedules are not exhaustive; failing schedules are not distinct bug counts.",
        "- Inspect ASan traces and error types for every unexpected error.",
        "", "## Incomplete runs",
    ]
    doc += ([f"- {x['benchmark']} N={x['N']} rep={x['repeat']}: {x['status']}" for x in incomplete]
            if incomplete else ["- None."])
    (lab / "SHARED_READONLY_RESULTS_AND_LIMITATIONS.md").write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"Completed valid runs: {complete}/180; incomplete: {len(incomplete)}")
    print("Saved:", lab / "shared_readonly_10_cve_runs.csv")
    print("Saved:", lab / "shared_readonly_10_cve_group_summary.csv")
    print("Saved:", lab / "SHARED_READONLY_RESULTS_AND_LIMITATIONS.md")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", nargs="?", choices=("plan", "prepare", "build", "run", "analyze", "all"), default="plan")
    p.add_argument("--retry-failed", action="store_true")
    a = p.parse_args()
    if a.action == "plan":
        plan()
    elif a.action == "prepare":
        prepare()
    elif a.action == "build":
        build(a.retry_failed)
    elif a.action == "run":
        run(a.retry_failed)
    elif a.action == "analyze":
        analyze()
    else:
        plan()
        build(a.retry_failed)
        run(a.retry_failed)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted; completed records remain on disk for resume.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        raise
