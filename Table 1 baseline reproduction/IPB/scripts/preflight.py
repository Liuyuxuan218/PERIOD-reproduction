#!/usr/bin/env python3
"""Check whether this machine can launch the SCTBench scheduler.

This script does not run a benchmark and does not write a bug result.
Exit 0 means the required tools were found. Exit 2 means they were not.
"""
import json
import os
import platform
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def kernel_release():
    try:
        return os.uname().release
    except AttributeError:
        return platform.platform()


def main():
    release = kernel_release()
    major = None
    token = release.split("-", 1)[0].split(".", 1)[0]
    if token.isdigit():
        major = int(token)
    pin = os.environ.get("PIN_HOME")
    sctbench = os.environ.get("SCTBENCH_ROOT")
    pin_binary = shutil.which("pin")
    reasons = []
    if major is None or major > 3:
        reasons.append("SCTBench documents that Intel PIN in this artifact requires kernel version 3.x or older. This process sees %s." % release)
    if not pin or not os.path.isdir(pin):
        reasons.append("PIN_HOME is not a directory.")
    if not pin_binary:
        reasons.append("No pin executable is on PATH.")
    if not sctbench or not os.path.isfile(os.path.join(sctbench, "scripts", "run_many.py")):
        reasons.append("SCTBENCH_ROOT does not contain scripts/run_many.py.")
    report = {
        "status": "ready" if not reasons else "blocked",
        "kernel": release,
        "pin_home": pin,
        "pin_on_path": pin_binary,
        "sctbench_root": sctbench,
        "reasons": reasons,
        "bug_result": None,
    }
    destination = ROOT / "results" / "diagnostics"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "preflight.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if not reasons else 2)


if __name__ == "__main__":
    main()
