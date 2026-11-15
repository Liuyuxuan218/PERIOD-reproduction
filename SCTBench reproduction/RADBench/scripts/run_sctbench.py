#!/usr/bin/env python3
"""Resumable runner for one SCTBench group inside the PERIOD image (Python 3.6)."""
from __future__ import print_function

import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GROUP_DIR = os.path.dirname(HERE)
GROUP = os.path.basename(GROUP_DIR)
ROOT = "/workdir/PERIOD"
# This group's external tree. The original combined suite, if still present,
# stays at /experiment-data/sctbench/cases and is not written by this script.
DATA = "/experiment-data/sctbench/" + GROUP
PDS = os.path.join(ROOT, "tool", "DBDS", "run_PDS.py")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.rename(tmp, path)


def tool_env():
    env = os.environ.copy()
    env["ROOT_DIR"] = ROOT
    env["PATH"] = (
        os.path.join(ROOT, "clang+llvm", "bin")
        + ":"
        + os.path.join(ROOT, "tool", "SVF", "Release-build", "bin")
        + ":"
        + env.get("PATH", "")
    )
    lib = os.path.join(ROOT, "clang+llvm", "lib")
    prev = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = lib + (":" + prev if prev else "")
    env["PYTHONUNBUFFERED"] = "1"
    return env


def run_logged(cmd, cwd, log_path, env):
    ensure_dir(os.path.dirname(log_path))
    started = time.time()
    with open(log_path, "w") as log:
        log.write("cwd: %s\n" % cwd)
        log.write("cmd: %s\n" % json.dumps(cmd))
        log.write("started: %s\n" % utc_now())
        log.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        code = proc.wait()
        log.write("\nexit: %s\nended: %s\nelapsed_sec: %.3f\n" % (code, utc_now(), time.time() - started))
    return code, time.time() - started


def reset_shm():
    subprocess.call(["ipcrm", "-M", "1111"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def move_out_dirs(workdir, dest):
    ensure_dir(dest)
    moved = []
    for name in os.listdir(workdir):
        if name.startswith("out_"):
            src = os.path.join(workdir, name)
            target = os.path.join(dest, name)
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.move(src, target)
            moved.append(name)
    return moved


def parse_log(text, schedule_limit):
    clean = ANSI.sub("", text)
    executed = []
    bare = []
    errors = []
    current_test = None
    for line in clean.splitlines():
        match = re.search(r"test\s+(\d+)(.*)$", line)
        if match and "retest" not in line:
            num = int(match.group(1))
            rest = match.group(2)
            current_test = num
            if "[" in rest:
                executed.append(num)
            else:
                bare.append(num)
        err = re.search(r"\[Error Found\]:\s*NO\.\d+\s+(\S+)", line)
        if err:
            errors.append({"type": err.group(1), "test": current_test})
        tmo = re.search(r"\[Timeout\s+(\d+)\]", line)
        if tmo:
            pass
    footer_errors = re.search(r"Total Error Interleavings:\s*(\d+)", clean)
    footer_timeouts = re.search(r"Total Timeouts Interleavings:\s*(\d+)", clean)
    footer_round = re.search(r"Round\s+(\d+)\s+(\d+)", clean)
    ended = "End Testing" in clean
    by_type = {}
    for err in errors:
        slot = by_type.setdefault(err["type"], {"count": 0, "first_schedule": err["test"]})
        slot["count"] += 1
        if err["test"] is not None and (slot["first_schedule"] is None or err["test"] < slot["first_schedule"]):
            slot["first_schedule"] = err["test"]
    filenames = re.findall(r"Errors/(\d+)_(\d+)_([^\s]+)", clean)
    file_types = {}
    for _seq, round_s, kind in filenames:
        kind = kind.strip()
        slot = file_types.setdefault(kind, {"count": 0, "first_schedule": int(round_s)})
        slot["count"] += 1
        if int(round_s) < slot["first_schedule"]:
            slot["first_schedule"] = int(round_s)
    first = errors[0]["test"] if errors else None
    if first is None and filenames:
        first = int(filenames[0][1])
    explored = len(executed)
    if explored >= schedule_limit and ended:
        stop = "budget"
    elif ended and not errors:
        stop = "completed_no_bug"
    elif ended:
        stop = "completed"
    else:
        stop = "incomplete"
    return {
        "schedules_explored": explored,
        "bare_test_lines": bare,
        "round_footer_last": int(footer_round.group(1)) if footer_round else None,
        "round_footer_total": int(footer_round.group(2)) if footer_round else None,
        "error_interleavings": int(footer_errors.group(1)) if footer_errors else len(errors),
        "timeout_interleavings": int(footer_timeouts.group(1)) if footer_timeouts else None,
        "first_bug_schedule": first,
        "bug_found": bool(errors or filenames),
        "by_type_log": by_type,
        "by_type_files": file_types,
        "end_testing": ended,
        "stop_reason": stop,
    }


def load_manifest(path):
    with open(path) as fh:
        return json.load(fh)


def case_dir(case_id):
    return os.path.join(DATA, "cases", case_id)


def build_case(case, env):
    workdir = os.path.join(ROOT, case["workdir"])
    cdir = case_dir(case["id"])
    ensure_dir(cdir)
    marker = os.path.join(cdir, "build.ok")
    if os.path.exists(marker):
        return True, "cached"
    for item in case.get("fetch") or []:
        dest = os.path.join(workdir, item["dest"])
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            continue
        ensure_dir(os.path.dirname(dest))
        code, _elapsed = run_logged(
            ["wget", "-c", "-O", dest, item["url"]],
            workdir,
            os.path.join(cdir, "fetch.log"),
            env,
        )
        if code != 0 or not os.path.exists(dest) or os.path.getsize(dest) == 0:
            write_json(os.path.join(cdir, "build.json"), {
                "ok": False,
                "stage": "fetch",
                "url": item["url"],
                "exit": code,
                "time": utc_now(),
            })
            return False, "fetch"
    code, elapsed = run_logged(
        ["bash", "-lc", case["build"]],
        workdir,
        os.path.join(cdir, "build.log"),
        env,
    )
    write_json(os.path.join(cdir, "build.json"), {
        "ok": code == 0,
        "exit": code,
        "elapsed_sec": elapsed,
        "time": utc_now(),
        "build": case["build"],
    })
    if code == 0:
        with open(marker, "w") as fh:
            fh.write(utc_now() + "\n")
        return True, "built"
    return False, "build"


def pds_command(case):
    cmd = ["python3", PDS, "-y", "-d", "3", "-f", str(case["schedule_limit"])]
    if case.get("exec_timeout"):
        cmd.extend(["-t", str(case["exec_timeout"])])
    cmd.extend(case["argv"])
    return cmd


def run_one(case, rep, env, limit_override=None):
    workdir = os.path.join(ROOT, case["workdir"])
    cdir = case_dir(case["id"])
    rdir = os.path.join(cdir, "rep%02d" % rep)
    metrics_path = os.path.join(rdir, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as fh:
            old = json.load(fh)
        if old.get("valid"):
            return old
    ensure_dir(rdir)
    reset_shm()
    limit = case["schedule_limit"] if limit_override is None else limit_override
    spec = dict(case)
    spec["schedule_limit"] = limit
    cmd = pds_command(spec)
    meta = {
        "case": case["id"],
        "repetition": rep,
        "command": cmd,
        "workdir": workdir,
        "schedule_limit": limit,
        "bug_depth": 3,
        "started": utc_now(),
        "host_note": "executed inside period-sctbench",
    }
    write_json(os.path.join(rdir, "command.json"), meta)
    started = time.time()
    log_path = os.path.join(rdir, "run.log")
    with open(log_path, "w") as log:
        log.write("started: %s\n" % meta["started"])
        log.write("cmd: %s\n\n" % json.dumps(cmd))
        log.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=workdir,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        code = proc.wait()
        elapsed = time.time() - started
        log.write("\nexit: %s\nended: %s\nelapsed_sec: %.3f\n" % (code, utc_now(), elapsed))
    with open(log_path) as fh:
        text = fh.read()
    parsed = parse_log(text, limit)
    parsed.update({
        "case": case["id"],
        "repetition": rep,
        "exit_code": code,
        "elapsed_sec": round(elapsed, 3),
        "started": meta["started"],
        "ended": utc_now(),
        "command": cmd,
        "valid": parsed["end_testing"] and code == 0,
        "configuration": "table2-period",
        "schedule_limit": limit,
        "bug_depth": 3,
    })
    moved = move_out_dirs(workdir, os.path.join(rdir, "output"))
    parsed["output_dirs"] = moved
    # Keep one error file for replay evidence. Drop the rest of the bulky ASAN dumps
    # from the copied tree only after the first file is saved; full output stays until
    # compact_output runs.
    compact_output(os.path.join(rdir, "output"))
    write_json(metrics_path, parsed)
    write_excerpt(log_path, os.path.join(rdir, "run.excerpt.log"))
    return parsed


def compact_output(output_root):
    if not os.path.isdir(output_root):
        return
    for dirpath, _dirnames, filenames in os.walk(output_root):
        base = os.path.basename(dirpath)
        if base not in ("Errors", "Timeouts"):
            continue
        filenames = sorted(filenames)
        keep = filenames[:2]
        for name in filenames:
            if name not in keep:
                os.remove(os.path.join(dirpath, name))


def write_excerpt(src, dest):
    keys = ("opts:", "bugDepth:", "Start Testing", "End Testing", "Error Found",
            "Timeout", "Total Error", "Total Timeouts", "Round", "Time\t", "exit:", "cmd:")
    with open(src) as fh, open(dest, "w") as out:
        kept_tests = 0
        for line in fh:
            plain = ANSI.sub("", line)
            if plain.startswith("test ") or "test " in plain[:40]:
                if "[" in plain and kept_tests < 5:
                    out.write(plain)
                    kept_tests += 1
                elif "[" not in plain:
                    out.write(plain)
                continue
            if any(key in plain for key in keys):
                out.write(plain)


def replay_first(case, env):
    rdir = os.path.join(case_dir(case["id"]), "rep01", "output")
    if not os.path.isdir(rdir):
        return {"replayed": False, "reason": "no output"}
    chosen = None
    for dirpath, _dirnames, filenames in os.walk(rdir):
        if os.path.basename(dirpath) != "Errors":
            continue
        files = sorted(filenames)
        if files:
            chosen = os.path.join(dirpath, files[0])
            break
    if not chosen:
        return {"replayed": False, "reason": "no error file"}
    workdir = os.path.join(ROOT, case["workdir"])
    cmd = ["python3", PDS, "-r", chosen] + case["argv"]
    log_path = os.path.join(case_dir(case["id"]), "replay_rep01.log")
    code, elapsed = run_logged(cmd, workdir, log_path, env)
    with open(log_path) as fh:
        text = ANSI.sub("", fh.read())
    confirmed = ("ERROR: AddressSanitizer" in text) or ("Assertion" in text) or ("Aborted" in text)
    result = {
        "replayed": True,
        "exit_code": code,
        "elapsed_sec": round(elapsed, 3),
        "error_file": chosen,
        "asan_or_assertion": confirmed,
        "command": cmd,
    }
    write_json(os.path.join(case_dir(case["id"]), "replay.json"), result)
    return result


def write_status(rows):
    ensure_dir(DATA)
    write_json(os.path.join(DATA, "status.json"), {"updated": utc_now(), "rows": rows})
    lines = ["| case | build | valid reps | last stop | explored | errors | first bug | timeouts |",
             "|---|---|---:|---|---:|---:|---:|---:|"]
    for row in rows:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            row["id"], row.get("build", ""), row.get("valid_reps", ""),
            row.get("stop", ""), row.get("explored", ""), row.get("errors", ""),
            row.get("first", ""), row.get("timeouts", ""),
        ))
    with open(os.path.join(DATA, "status.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


def summarize_case(case_id, reps):
    valids = [item for item in reps if item.get("valid")]
    last = reps[-1] if reps else {}
    return {
        "id": case_id,
        "build": "ok" if os.path.exists(os.path.join(case_dir(case_id), "build.ok")) else "failed",
        "valid_reps": len(valids),
        "stop": last.get("stop_reason", ""),
        "explored": last.get("schedules_explored", ""),
        "errors": last.get("error_interleavings", ""),
        "first": last.get("first_bug_schedule", ""),
        "timeouts": last.get("timeout_interleavings", ""),
    }



def suite(env, manifest):
    rows = []
    for case in manifest["cases"]:
        ok, how = build_case(case, env)
        reps = []
        if not ok:
            rows.append({
                "id": case["id"], "build": how, "valid_reps": 0,
                "stop": "build_failure", "explored": "", "errors": "",
                "first": "", "timeouts": "",
            })
            write_status(rows)
            print("BUILD FAIL", case["id"], how)
            continue
        for rep in range(1, int(manifest["repetitions"]) + 1):
            print("RUN", case["id"], "rep", rep, flush=True)
            result = run_one(case, rep, env)
            reps.append(result)
            print(" DONE", case["id"], rep, result.get("stop_reason"),
                  "explored", result.get("schedules_explored"),
                  "errors", result.get("error_interleavings"), flush=True)
        if any(item.get("bug_found") for item in reps):
            replay_first(case, env)
        rows.append(summarize_case(case["id"], reps))
        write_status(rows)
    write_json(os.path.join(DATA, "suite_finished.json"), {"time": utc_now(), "cases": len(rows)})
    print("SUITE FINISHED", utc_now())


def main():
    if len(sys.argv) < 2:
        manifest_path = os.path.join(GROUP_DIR, "manifest.json")
        mode = "--suite"
    else:
        manifest_path = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) > 2 else "--suite"
    manifest = load_manifest(manifest_path)
    for case in manifest["cases"]:
        prefix = case["id"].split(".", 1)[0]
        if prefix != GROUP:
            raise SystemExit("manifest program %s is outside %s" % (case["id"], GROUP))
    if manifest.get("upstream_commit"):
        head = subprocess.check_output(["git", "-C", ROOT, "rev-parse", "HEAD"], universal_newlines=True).strip()
        if head != manifest["upstream_commit"]:
            raise SystemExit("commit mismatch: %s" % head)
    env = tool_env()
    ensure_dir(DATA)
    if mode == "--suite":
        suite(env, manifest)
        return
    raise SystemExit("unknown mode")


if __name__ == "__main__":
    main()
