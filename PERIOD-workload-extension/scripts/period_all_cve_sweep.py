#!/usr/bin/env python3
"""PERIOD official 10-CVE sweep, with 7 new workload-sensitivity benchmarks.

Existing three CVE workload studies remain untouched.

Commands:
  python3 period_all_cve_sweep.py plan
  python3 period_all_cve_sweep.py all
  python3 period_all_cve_sweep.py analyze
  python3 period_all_cve_sweep.py run --retry-failed

Requires WSL2 Docker Desktop integration and the pinned official PERIOD image.
No third-party Python packages are required.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "PERIOD-workload-extension"
LAB = ROOT / "all_official_cve_sweep"
IMAGE = "wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc"
OFFICIAL = "/workdir/PERIOD/evaluation/ConVul-CVE-Benchmarks"
LEVELS = (0, 1, 2, 3, 4, 8)
REPEATS = (1, 2, 3)
DEPTH = 4
BUDGET = 60
PER_EXEC_TIMEOUT = 5
BUILD_TIMEOUT = 300
SEARCH_TIMEOUT = 240

# Official PERIOD repository's complete ConVul-CVE-Benchmarks list.
# The three earlier user studies (1972, 1973, 7911) are reused, not overwritten.
ALL_CVES = (
    "2009-3547", "2011-2183", "2013-1792", "2015-7550",
    "2016-1972", "2016-1973", "2016-7911", "2016-9806",
    "2017-6346", "2017-15265",
)
DONE_WORKLOAD = {"2016-1972", "2016-1973", "2016-7911"}
NEW_WORKLOAD = tuple(x for x in ALL_CVES if x not in DONE_WORKLOAD)
SOURCE_EXT = {x: (".c" if x == "2016-1972" else ".cpp") for x in ALL_CVES}

# Explicitly verified against the official source's pthread_create call targets.
# The same extra work is placed before the original worker body. No bug logic is replaced.
WORKERS = {
    "2009-3547": ("pipe_write_open", "involve"),
    "2011-2183": ("thread_one", "thread_two"),
    "2013-1792": ("thread_one", "thread_two"),
    "2015-7550": ("thread1", "thread2"),
    "2016-9806": ("netlink_dump",),     # both pthreads use this function
    "2017-6346": ("thread_func",),      # both pthreads use this function
    "2017-15265": ("thread_one", "thread_two"),
}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def src_filename(cve: str) -> str:
    return cve + SOURCE_EXT[cve]


def check_docker():
    p = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError("Cannot access Docker Engine from WSL. Open Docker Desktop, verify `docker ps`, then rerun.\n" + p.stderr[-1200:])


def extract_original(cve: str):
    out = LAB / "sources" / f"{cve}.original{SOURCE_EXT[cve]}"
    if out.exists():
        if out.stat().st_size < 100:
            raise RuntimeError(f"Suspicious existing original source: {out}")
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    path = f"{OFFICIAL}/CVE-{cve}/{src_filename(cve)}"
    p = subprocess.run(["docker", "run", "--rm", "--entrypoint", "cat", IMAGE, path], capture_output=True)
    if p.returncode or len(p.stdout) < 100:
        raise RuntimeError(f"Cannot read original source for {cve} in pinned Docker image: {p.stderr.decode(errors='replace')[-500:]}")
    out.write_bytes(p.stdout)
    return out


def patch_cpp(source: str, cve: str):
    # Source-level, explicit entry-point instrumentation. All 7 new CVEs use C++ files.
    if cve not in WORKERS:
        raise RuntimeError(f"No verified worker map for {cve}")
    for worker in WORKERS[cve]:
        uses = re.findall(r"\bpthread_create\s*\([^;]*?,\s*" + re.escape(worker) + r"\s*,", source, re.S)
        if not uses:
            raise RuntimeError(f"Expected pthread_create using worker {worker} in {cve}")

    helper = r'''
/* PERIOD EXTENSION: independent mutex-protected counter; controlled by argv N. */
#include <stdlib.h>
static pthread_mutex_t period_extra_mutex = PTHREAD_MUTEX_INITIALIZER;
static volatile unsigned long period_extra_counter = 0;
static int period_extra_n = 0;
static void period_extra_work(void) {
    for (int period_j = 0; period_j < period_extra_n; ++period_j) {
        pthread_mutex_lock(&period_extra_mutex);
        period_extra_counter++;
        pthread_mutex_unlock(&period_extra_mutex);
    }
}
'''
    lines = source.splitlines(keepends=True)
    include_indices = [i for i, line in enumerate(lines) if re.match(r"^\s*#\s*include\b", line)]
    if not include_indices:
        raise RuntimeError(f"No includes in {cve}")
    # Insert helper after includes so stdlib and pthread symbols are available.
    lines.insert(max(include_indices) + 1, helper)
    result = "".join(lines)
    for worker in WORKERS[cve]:
        pattern = re.compile(
            r"(\b(?:static\s+)?void\s*\*\s*" + re.escape(worker) +
            r"\s*\(\s*void\s*\*\s*\w+\s*\)\s*\{)"
        )
        result, hits = pattern.subn(lambda m: m.group(1) + "\n    period_extra_work();", result, count=1)
        if hits != 1:
            raise RuntimeError(f"Ambiguous worker function {worker} in {cve}; refusing to patch")
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


def plan():
    print("OFFICIAL CVE SUITE:", len(ALL_CVES), "programs")
    for cve in ALL_CVES:
        print(f"  CVE-{cve:10} original + " + ("reuse existing workload runs" if cve in DONE_WORKLOAD else "new N={0,1,2,3,4,8} x3"))
    print("Original-baseline checks: 10 single-run cases (source unchanged)")
    print("Additional workload runs: 7 x 6 x 3 = 126 new attempts")
    print("Existing workload runs: 3 x 6 x 3 = 54 (READ ONLY)")
    print("CVE-level total workload matrix: 10 x 6 x 3 = 180 planned cells")
    print("Fixed: -d4, -f60, -t5, search wall cap 240s")
    print("The original CVE checks are sanity baselines, not part of the 180 workload runs.")
    print("No claim of 180 valid runs until statuses are verified.")
    print("Output:", LAB)


def prepare():
    check_docker()
    for cve in ALL_CVES:
        original = extract_original(cve)
        print(f"SOURCE CVE-{cve}: {len(original.read_bytes())} bytes sha256={sha(original.read_bytes())[:16]}", flush=True)
        if cve in NEW_WORKLOAD:
            patched = patch_cpp(original.read_text(encoding="utf-8"), cve)
            target = LAB / "sources" / f"{cve}.workload.cpp"
            if target.exists() and target.read_text(encoding="utf-8") != patched:
                raise RuntimeError(f"Existing modified file has changed: {target}; refusing to overwrite")
            if not target.exists():
                target.write_text(patched, encoding="utf-8")
            print(f"PATCHED CVE-{cve}: {len(patched.splitlines())} lines; worker entry points: {','.join(WORKERS[cve])}", flush=True)
    manifest = {
        "created_utc": stamp(), "image": IMAGE, "all_official_cves": list(ALL_CVES),
        "new_workload_cves": list(NEW_WORKLOAD), "reused_workload_cves": sorted(DONE_WORKLOAD),
        "workload_N": list(LEVELS), "repetitions": list(REPEATS),
        "fixed_depth_bound": DEPTH, "fixed_schedule_budget": BUDGET,
        "per_execution_timeout_seconds": PER_EXEC_TIMEOUT,
        "build_timeout_seconds": BUILD_TIMEOUT, "outer_search_timeout_seconds": SEARCH_TIMEOUT,
        "modification": "Extra independent mutex-protected counter work at each worker function's entry; only argv N changes within a benchmark",
        "guards": "Original baseline separate from modified N0; non-exhaustive schedule budget; failed runs excluded, never silently dropped; UAF and SEGV counted separately.",
    }
    (LAB / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


BUILD_IN_CONTAINER = r'''
set -Eeuo pipefail
ROOT=/workdir/PERIOD
BENCH="CVE-${CVE_ID}"
SRC="$ROOT/evaluation/ConVul-CVE-Benchmarks/$BENCH"
DST="/extension/builds/$BUILD_KIND/$BENCH"
BASE="$CVE_ID"
trap 'chown -R "$HOST_UID:$HOST_GID" "$DST" 2>/dev/null || true' EXIT
mkdir -p "$DST"
export ROOT_DIR="$ROOT"
export PATH="$ROOT/clang+llvm/bin:$ROOT/tool/SVF/Release-build/bin:$PATH"
export LD_LIBRARY_PATH="$ROOT/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cd "$SRC"
if [ "$BUILD_KIND" = original ]; then
  cp "/extension/sources/${BASE}.original${SRC_EXT}" "${BASE}${SRC_EXT}"
else
  cp "/extension/sources/${BASE}.workload.cpp" "${BASE}.cpp"
fi
sha256sum "${BASE}${SRC_EXT}" > "$DST/source.sha256"
if ! timeout --signal=TERM --kill-after=5s "$BUILD_TIMEOUT" ./build.sh > "$DST/build.log" 2>&1; then
  echo BUILD_FAILED > "$DST/build_status.txt"
  tail -n 20 "$DST/build.log" || true
  exit 0
fi
if [ ! -s "ConConfig.${BASE}" ] || [ ! -x "./${BASE}" ]; then
  echo OUTPUT_MISSING > "$DST/build_status.txt"
  exit 0
fi
cp "./${BASE}" "$DST/binary"
cp "ConConfig.${BASE}" "$DST/ConConfig.${BASE}"
chmod 755 "$DST/binary"
sha256sum "$DST/binary" > "$DST/binary.sha256"
sha256sum "$DST/ConConfig.${BASE}" > "$DST/config.sha256"
echo OK > "$DST/build_status.txt"
echo "BUILT $BENCH $BUILD_KIND"
'''


SEARCH_IN_CONTAINER = r'''
set -Eeuo pipefail
ROOT=/workdir/PERIOD
BENCH="CVE-${CVE_ID}"
SRC="$ROOT/evaluation/ConVul-CVE-Benchmarks/$BENCH"
BUILD="/extension/builds/$BUILD_KIND/$BENCH"
OUT="/extension/results/$BUILD_KIND/$BENCH/$SAMPLE_ID"
BASE="$CVE_ID"
trap 'chown -R "$HOST_UID:$HOST_GID" "$OUT" 2>/dev/null || true' EXIT
mkdir -p "$OUT"
export ROOT_DIR="$ROOT"
export PATH="$ROOT/clang+llvm/bin:$ROOT/tool/SVF/Release-build/bin:$PATH"
export LD_LIBRARY_PATH="$ROOT/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cp "$BUILD/binary" "$SRC/$BASE"
cp "$BUILD/ConConfig.${BASE}" "$SRC/ConConfig.${BASE}"
chmod 755 "$SRC/$BASE"
export Con_PATH="$SRC/ConConfig.${BASE}"
cp "$BUILD/source.sha256" "$OUT/source.sha256"
cp "$BUILD/binary.sha256" "$OUT/binary.sha256"
cp "$BUILD/config.sha256" "$OUT/config.sha256"
cd "$OUT"
echo "SEARCH $BENCH $BUILD_KIND $SAMPLE_ID -d$DEPTH -f$BUDGET"
start=$(date +%s%N)
set +e
if [ "$BUILD_KIND" = original ]; then
  timeout --signal=TERM --kill-after=5s "$SEARCH_TIMEOUT" \
    "$ROOT/tool/DBDS/run_PDS.py" -y -d "$DEPTH" -f "$BUDGET" -t "$EXEC_TIMEOUT" "$SRC/$BASE" > "$OUT/search.log" 2>&1
else
  timeout --signal=TERM --kill-after=5s "$SEARCH_TIMEOUT" \
    "$ROOT/tool/DBDS/run_PDS.py" -y -d "$DEPTH" -f "$BUDGET" -t "$EXEC_TIMEOUT" "$SRC/$BASE" "$WORK_N" > "$OUT/search.log" 2>&1
fi
code=$?
set -e
end=$(date +%s%N)
echo "$code" > "$OUT/exit_code.txt"
printf '%d.%03d\n' "$(((end-start)/1000000000))" "$((((end-start)%1000000000)/1000000))" > "$OUT/wall_seconds.txt"
if [ "$code" -eq 0 ] && grep -q 'End Testing!' "$OUT/search.log"; then
  echo FINISHED_BUDGET_LIMITED > "$OUT/status.txt"
elif [ "$code" -eq 124 ] || [ "$code" -eq 137 ]; then
  echo SEARCH_TIMEOUT > "$OUT/status.txt"
else
  echo SEARCH_FAILED_OR_INCOMPLETE > "$OUT/status.txt"
fi
printf 'RESULT %s %s %s status=%s code=%s\n' "$BENCH" "$BUILD_KIND" "$SAMPLE_ID" "$(cat "$OUT/status.txt")" "$code"
grep -E 'ThreadNum:|MaxKpNum:|kpNumArray:|Total Error Interleavings:|Total Timeouts Interleavings:' "$OUT/search.log" | tail -n 7 || true
'''


def docker_call(stage: str, code: str, env: dict[str, str]):
    cmd = ["docker", "run", "--rm", "--privileged", "-v", f"{LAB}:/extension"]
    cmd += sum((["-e", f"{k}={v}"] for k, v in env.items()), [])
    cmd += [IMAGE, "bash", "-c", code]
    p = subprocess.run(cmd, check=False)
    if p.returncode:
        print(f"WARNING Docker exited {p.returncode} in {stage}", flush=True)
    return p.returncode


def archived(folder: Path):
    archive_dir = LAB / "failed_attempt_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / ("_".join(folder.relative_to(LAB).parts) + "_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f"))
    shutil.move(str(folder), str(target))
    print(f"ARCHIVED incomplete attempt {folder} -> {target}", flush=True)


def guarded(folder: Path, status_filename: str, retry_failed: bool):
    status_file = folder / status_filename
    if not status_file.exists():
        return False
    status = status_file.read_text(errors="replace").strip()
    if status in ("OK", "FINISHED_BUDGET_LIMITED"):
        print(f"SKIP completed {folder.relative_to(LAB)}", flush=True)
        return True
    if not retry_failed:
        print(f"SKIP previous incomplete {folder.relative_to(LAB)} status={status} (use --retry-failed to archive and retry)", flush=True)
        return True
    archived(folder)
    return False


def build(retry_failed: bool = False):
    prepare()
    uid, gid = str(os.getuid()), str(os.getgid())
    jobs = [(cve, "original") for cve in ALL_CVES] + [(cve, "workload") for cve in NEW_WORKLOAD]
    for idx, (cve, kind) in enumerate(jobs, 1):
        dst = LAB / "builds" / kind / f"CVE-{cve}"
        if guarded(dst, "build_status.txt", retry_failed):
            continue
        dst.mkdir(parents=True, exist_ok=True)
        print(f"BUILD [{idx}/{len(jobs)}] CVE-{cve} kind={kind}", flush=True)
        p = docker_call("build", BUILD_IN_CONTAINER, {
            "CVE_ID": cve, "SRC_EXT": SOURCE_EXT[cve], "BUILD_KIND": kind,
            "BUILD_TIMEOUT": str(BUILD_TIMEOUT), "HOST_UID": uid, "HOST_GID": gid,
        })
        if p:
            (dst / "build_status.txt").write_text(f"DOCKER_EXIT_{p}\n")


def run_one(cve: str, kind: str, n: int | None, rep: int, retry_failed: bool):
    src_stage = LAB / "builds" / kind / f"CVE-{cve}"
    out_name = (f"N{n}/rep{rep}" if kind == "workload" else "rep1")
    out = LAB / "results" / kind / f"CVE-{cve}" / out_name
    if guarded(out, "status.txt", retry_failed):
        return
    status = src_stage / "build_status.txt"
    if not status.is_file() or status.read_text().strip() != "OK":
        out.mkdir(parents=True, exist_ok=True)
        (out / "status.txt").write_text("BUILD_UNAVAILABLE\n")
        print(f"SKIP no built binary CVE-{cve} {kind} ({out_name})", flush=True)
        return
    out.mkdir(parents=True, exist_ok=True)
    rc = docker_call("search", SEARCH_IN_CONTAINER, {
        "CVE_ID": cve, "BUILD_KIND": kind, "SAMPLE_ID": out_name,
        "WORK_N": str(n if n is not None else 0), "DEPTH": str(DEPTH),
        "BUDGET": str(BUDGET), "EXEC_TIMEOUT": str(PER_EXEC_TIMEOUT),
        "SEARCH_TIMEOUT": str(SEARCH_TIMEOUT),
        "HOST_UID": str(os.getuid()), "HOST_GID": str(os.getgid()),
    })
    if rc and not (out / "status.txt").exists():
        (out / "status.txt").write_text(f"DOCKER_EXIT_{rc}\n")


def run(retry_failed: bool = False):
    check_docker()
    jobs = [(cve, "original", None, 1) for cve in ALL_CVES]
    for cve in NEW_WORKLOAD:
        jobs.extend((cve, "workload", n, rep) for n in LEVELS for rep in REPEATS)
    for idx, (cve, kind, n, rep) in enumerate(jobs, 1):
        print(f"[{idx}/{len(jobs)}] CVE-{cve} {kind} N={n} repeat={rep}", flush=True)
        run_one(cve, kind, n, rep, retry_failed)
    print("ALL-CVE SWEEP FINISHED (check status counts for success).", flush=True)
    analyze()


def get_int(txt: str, label: str):
    m = re.search(r"(?m)^\s*" + re.escape(label) + r":\s*(\d+)", txt)
    return int(m.group(1)) if m else None


def parse_first_error(txt: str):
    active = None
    for line in txt.splitlines():
        m = re.search(r"\btest\s+(\d+)\b", line)
        if m:
            active = int(m.group(1))
        if "[Error Found]" in line:
            return active
    return None


def load_run(folder: Path, cve: str, kind: str, n: int | None, rep: int):
    row = {
        "benchmark": f"CVE-{cve}", "kind": kind, "N": n, "repeat": rep,
        "status": "MISSING", "exit_code": None, "initial_total_kp": None,
        "first_error_round": None, "error_schedules": None, "timeout_schedules": None,
        "wall_seconds": None, "error_types": "", "first_uaf_round": None,
        "uaf_error_files": 0, "saved_error_files": 0,
        "source_hash": "", "binary_hash": "", "config_hash": "",
    }
    if (folder / "status.txt").exists():
        row["status"] = (folder / "status.txt").read_text(errors="replace").strip()
    elif kind == "existing" and (folder / "exit_code.txt").exists():
        row["status"] = "UNVERIFIED_EXISTING"
    for k in ("exit_code", "wall_seconds"):
        f = folder / ("exit_code.txt" if k == "exit_code" else "wall_seconds.txt")
        if f.exists():
            try:
                row[k] = int(f.read_text().strip()) if k == "exit_code" else float(f.read_text().strip())
            except ValueError:
                pass
    for key, f in (("source_hash", "source.sha256"), ("binary_hash", "binary.sha256"), ("config_hash", "config.sha256")):
        file = folder / f
        if file.exists():
            row[key] = file.read_text(errors="replace").split()[0]
    # Prior 1972/7911/1973 experiment uses ConConfig rather than config.sha256
    if not row["config_hash"]:
        conf = folder / f"ConConfig.{cve}"
        if conf.exists():
            row["config_hash"] = sha(conf.read_bytes())
    log = folder / "search.log"
    if log.exists():
        txt = re.sub(r"\x1b\[[0-9;]*m", "", log.read_text(errors="replace"))
        a = re.search(r"(?m)^kpNumArray:\s*([\d ]+)", txt)
        if a:
            row["initial_total_kp"] = sum(map(int, a.group(1).split()))
        row["first_error_round"] = parse_first_error(txt)
        row["error_schedules"] = get_int(txt, "Total Error Interleavings")
        row["timeout_schedules"] = get_int(txt, "Total Timeouts Interleavings")
        if kind == "existing" and row["exit_code"] == 0 and "End Testing!" in txt:
            row["status"] = "FINISHED_BUDGET_LIMITED"
    errs = sorted(f for f in folder.glob("out_*/Errors/*") if f.is_file())
    row["saved_error_files"] = len(errs)
    types = set()
    rounds = []
    for f in errs:
        s = f.read_text(errors="replace")
        m = re.search(r"ERROR: AddressSanitizer:\s*([^\n]+)", s)
        if not m:
            typ = "UNKNOWN"
        elif "heap-use-after-free" in m.group(1):
            typ = "heap-use-after-free"
        elif "SEGV" in m.group(1):
            typ = "SEGV"
        else:
            typ = m.group(1).split(" on ")[0]
        types.add(typ)
        if typ == "heap-use-after-free":
            row["uaf_error_files"] += 1
            round_m = re.search(r"_([0-9]+)_", f.name)
            if round_m:
                rounds.append(int(round_m.group(1)))
    row["first_uaf_round"] = min(rounds) if rounds else None
    row["error_types"] = "|".join(sorted(types))
    return row


def avg(vals):
    vals = [float(x) for x in vals if x is not None]
    if not vals:
        return None
    return round(statistics.mean(vals), 5)


def write_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)



def write_svg_heatmap(groups, field: str, title: str, filename: str):
    """Native-SVG grid. Grey means no valid samples. Each cell shows the mean."""
    from html import escape
    width, height = 940, 575
    left, top, cell_w, cell_h = 215, 110, 105, 38
    vals = [float(g[field]) for g in groups if g[field] is not None and g["finished"] > 0]
    upper = max(vals) if vals else 1.0
    def cell_color(value):
        if value is None:
            return "#e5e7eb"
        scale = float(value) / upper if upper else 0.0
        # Accessible blue light-to-dark gradient.
        return f"rgb({int(235-145*scale)}, {int(244-135*scale)}, {int(255-62*scale)})"
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           f'<text x="45" y="42" font-family="Arial,sans-serif" font-size="23" font-weight="bold" fill="#111827">{escape(title)}</text>',
           '<text x="45" y="68" font-family="Arial,sans-serif" font-size="13" fill="#4b5563">Fixed depth 4 / budget 60 · 3 planned repeats per cell · grey = no finished runs</text>']
    for j, n in enumerate(LEVELS):
        x = left + j * cell_w + cell_w/2
        svg.append(f'<text x="{x:.1f}" y="99" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" fill="#111827">N={n}</text>')
    for i, cve in enumerate(ALL_CVES):
        y = top + i*cell_h
        svg.append(f'<text x="{left-12}" y="{y+24}" text-anchor="end" font-family="Arial,sans-serif" font-size="13" fill="#111827">CVE-{escape(cve)}</text>')
        for j, n in enumerate(LEVELS):
            g = next(x for x in groups if x["benchmark"] == f"CVE-{cve}" and x["N"] == n)
            v = g[field] if g["finished"] else None
            x = left+j*cell_w
            fill = cell_color(v)
            label = "--" if v is None else f"{v:.1f}"
            svg.append(f'<rect x="{x+2}" y="{y+2}" width="{cell_w-4}" height="{cell_h-4}" rx="5" fill="{fill}" stroke="#d1d5db" stroke-width="0.5"/>')
            svg.append(f'<text x="{x+cell_w/2:.1f}" y="{y+24}" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#111827">{escape(label)}</text>')
            if g["finished"] < 3:
                svg.append(f'<text x="{x+cell_w-7}" y="{y+11}" text-anchor="end" font-family="Arial,sans-serif" font-size="9" fill="#b91c1c">{g["finished"]}/3</text>')
    svg += ['<text x="45" y="536" font-family="Arial,sans-serif" font-size="12" fill="#6b7280">Compare trends within each CVE. Different CVEs may have different failure categories and code structures.</text>', '</svg>']
    (LAB / filename).write_text("\n".join(svg), encoding="utf-8")


def analyze():
    LAB.mkdir(parents=True, exist_ok=True)
    rows = []
    baselines = []
    for cve in ALL_CVES:
        folder = LAB / "results" / "original" / f"CVE-{cve}" / "rep1"
        baselines.append(load_run(folder, cve, "original", None, 1))
    for cve in ALL_CVES:
        for n in LEVELS:
            for rep in REPEATS:
                if cve == "2016-1972":
                    folder = ROOT / "study_v1" / f"N{n}" / f"rep{rep}"
                    kind = "existing"
                elif cve in ("2016-1973", "2016-7911"):
                    folder = ROOT / "cross_validate_two_cves" / "results" / f"CVE-{cve}" / f"N{n}" / f"rep{rep}"
                    kind = "existing"
                else:
                    folder = LAB / "results" / "workload" / f"CVE-{cve}" / f"N{n}" / f"rep{rep}"
                    kind = "workload"
                rows.append(load_run(folder, cve, kind, n, rep))
    groups = []
    for cve in ALL_CVES:
        for n in LEVELS:
            cell = [r for r in rows if r["benchmark"] == f"CVE-{cve}" and r["N"] == n]
            ok = [r for r in cell if r["status"] == "FINISHED_BUDGET_LIMITED"]
            types = "|".join(sorted(set(z for r in ok for z in r["error_types"].split("|") if z)))
            source_hashes = set(r["source_hash"] for r in ok if r["source_hash"])
            binary_hashes = set(r["binary_hash"] for r in ok if r["binary_hash"])
            config_hashes = set(r["config_hash"] for r in ok if r["config_hash"])
            groups.append({
                "benchmark": f"CVE-{cve}", "N": n, "finished": len(ok), "planned": 3,
                "first_error_mean": avg([r["first_error_round"] for r in ok]),
                "keypoints_mean": avg([r["initial_total_kp"] for r in ok]),
                "failing_schedules_mean": avg([r["error_schedules"] for r in ok]),
                "search_wall_seconds_mean": avg([r["wall_seconds"] for r in ok]),
                "first_uaf_mean_detected_only": avg([r["first_uaf_round"] for r in ok]),
                "uaf_runs": sum(1 for r in ok if r["first_uaf_round"] is not None),
                "error_types": types, "unique_source_hashes": len(source_hashes),
                "unique_binary_hashes": len(binary_hashes), "unique_config_hashes": len(config_hashes),
                "run_statuses": "|".join(r["status"] for r in cell),
            })
    write_csv(LAB / "all_10_cve_workload_runs.csv", rows)
    write_csv(LAB / "all_10_cve_group_summary.csv", groups)
    write_csv(LAB / "official_original_baselines.csv", baselines)
    write_svg_heatmap(groups, "keypoints_mean", "Observed Key Points across 10 CVEs", "fig_keypoints_10cves.svg")
    write_svg_heatmap(groups, "first_error_mean", "First failing schedule across 10 CVEs", "fig_first_error_10cves.svg")
    complete = sum(r["status"] == "FINISHED_BUDGET_LIMITED" for r in rows)
    incomplete = [r for r in rows if r["status"] != "FINISHED_BUDGET_LIMITED"]
    source_notes = []
    for cve in ALL_CVES:
        x = [g for g in groups if g["benchmark"] == f"CVE-{cve}"]
        n0 = next(g for g in x if g["N"] == 0)
        n8 = next(g for g in x if g["N"] == 8)
        source_notes.append(f"| CVE-{cve} | {sum(g['finished'] for g in x)}/18 | {n0['keypoints_mean']} | {n8['keypoints_mean']} | {n0['first_error_mean']} | {n8['first_error_mean']} |")
    doc = [
        "# PERIOD full official CVE suite — extension audit", "",
        "Official ConVul-CVE-Benchmarks suite: 10 CVEs. Seven new workload-modified sources; three earlier experiment datasets reused.",
        "Fixed per-CVE within-group controls: N={0,1,2,3,4,8}, 3 repeats per N, depth bound 4, -f60 budget, -t5, pinned Docker image.",
        "", f"**Completed valid workload runs: {complete}/180.**",
        f"**Incomplete workload runs: {len(incomplete)}.** Results do not imply all requested tests succeeded.",
        "", "| CVE | Valid / 18 | N=0 KP | N=8 KP | N=0 first error | N=8 first error |",
        "|---|---:|---:|---:|---:|---:|", *source_notes,
        "", "## Original-source sanity baselines (not directly comparable to modified N=0)",
    ]
    for r in baselines:
        doc.append(f"- {r['benchmark']}: {r['status']}, first failure={r['first_error_round']}, errors={r['error_schedules']}, type={r['error_types'] or 'none'}")
    doc += [
        "", "## Scientific interpretation warnings",
        "- This is **all 10 official ConVul-CVE-Benchmarks** in PERIOD, not the entire CVE ecosystem or the 36 other benchmark programs.",
        "- The 7 new CVEs use identical N-controlled mutex work inserted into their worker entry functions. Original bugs are not intentionally altered; thread timing and scheduling *are* altered.",
        "- Original-source runs and modified N=0 are separate sanity checks. Do not pool them as identical baseline conditions.",
        "- A 60-schedule cap is **not exhaustive**. An absent failure only means not observed within this budget.",
        "- Error types may mix SEGV, UAF, double-free; compare specific types and inspect ASan traces, not just aggregate failure count.",
        "- No monotonicity or global effect-size claim is justified from this sweep alone. Aggregate graphs require cautious analysis of eligible runs.",
        "- Source patching is limited to the verified worker function list and is fail-closed if any expected anchor differs.",
        "- Not every original benchmark must exhibit the same detection pattern under N=0. Failures are part of the recorded evidence.",
        "", "## Incomplete workload runs",
    ]
    if incomplete:
        doc += [f"- {r['benchmark']} N={r['N']} rep={r['repeat']}: {r['status']}" for r in incomplete]
    else:
        doc += ["- None."]
    (LAB / "RESULTS_AND_LIMITATIONS.md").write_text("\n".join(doc) + "\n", encoding="utf-8")
    print("\n=========== 10 CVE WORKLOAD SUMMARY ===========")
    for cve in ALL_CVES:
        subset = [g for g in groups if g["benchmark"] == f"CVE-{cve}"]
        valid = sum(g["finished"] for g in subset)
        n0, n8 = subset[0], subset[-1]
        print(f"CVE-{cve:<12} valid={valid:2}/18, KP[N0,N8]=({n0['keypoints_mean']},{n8['keypoints_mean']}), first[N0,N8]=({n0['first_error_mean']},{n8['first_error_mean']})")
    print(f"Completed workload runs: {complete}/180; incomplete: {len(incomplete)}")
    print("Original baseline status counts:", {status: sum(r["status"] == status for r in baselines) for status in sorted(set(r["status"] for r in baselines))})
    print("Saved:", LAB / "all_10_cve_workload_runs.csv")
    print("Saved:", LAB / "all_10_cve_group_summary.csv")
    print("Saved:", LAB / "official_original_baselines.csv")
    print("Saved:", LAB / "RESULTS_AND_LIMITATIONS.md")
    print("Saved: fig_keypoints_10cves.svg and fig_first_error_10cves.svg")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", nargs="?", choices=("plan", "prepare", "build", "run", "analyze", "all"), default="plan")
    p.add_argument("--retry-failed", action="store_true", help="Archive existing failed run records before retrying; never touch successful records")
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
        print("Interrupted. Completed records remain on disk; rerun to resume.", file=sys.stderr)
        sys.exit(130)
    except Exception as ex:
        print("ERROR:", ex, file=sys.stderr)
        raise
