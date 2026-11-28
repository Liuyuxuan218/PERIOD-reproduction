#!/usr/bin/env python3
"""
Retry only incomplete cells from the PERIOD shared-read-only 180-run experiment.

Keep the 145 successful runs. Retry SEARCH_FAILED_OR_INCOMPLETE and
SEARCH_TIMEOUT cells in-place using the existing experiment runner.
No rebuilding and no changes to workload/source/configuration are performed.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Keep this script beside period_shared_readonly_180.py and
# period_all_cve_sweep.py in ~/PERIOD-workload-extension.
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import period_shared_readonly_180 as exp  # noqa: E402

base = exp.base
VALID_STATUS = "FINISHED_BUDGET_LIMITED"


def get_record(cve: str, n: int, rep: int) -> dict:
    return base.load_run(exp.run_path(cve, n, rep), cve, "workload", n, rep)


def get_all_records() -> list[dict]:
    rows = []
    for cve in base.ALL_CVES:
        for n in base.LEVELS:
            for rep in base.REPEATS:
                rows.append(get_record(cve, n, rep))
    return rows


def check_builds() -> None:
    problems = []
    for cve in base.ALL_CVES:
        build_dir = base.LAB / "builds" / "workload" / f"CVE-{cve}"
        status_file = build_dir / "build_status.txt"
        status = status_file.read_text(encoding="utf-8").strip() if status_file.exists() else "MISSING"
        if status != "OK":
            problems.append(f"CVE-{cve}: build status={status}")
    if problems:
        raise RuntimeError(
            "Some workload builds are not ready. Do not retry searches until fixed:\n"
            + "\n".join(problems)
        )


def print_status(rows: list[dict], heading: str) -> None:
    done = [r for r in rows if r.get("status") == VALID_STATUS]
    pending = [r for r in rows if r.get("status") != VALID_STATUS]
    print(f"\n{heading}")
    print(f"Completed: {len(done)}/180")
    print(f"Still incomplete: {len(pending)}")
    for r in pending:
        print(
            f"  {r.get('benchmark')} N={r.get('N')} rep={r.get('repeat')} "
            f"status={r.get('status')}"
        )


def retry_incomplete(max_attempts: int, dry_run: bool = False) -> None:
    if max_attempts < 1:
        raise ValueError("--max-attempts must be >= 1")

    base.check_docker()
    check_builds()

    log_path = base.LAB / "supplement_retry_log.txt"
    base.LAB.mkdir(parents=True, exist_ok=True)

    rows = get_all_records()
    print_status(rows, "INITIAL STATUS")

    pending = [
        (r["benchmark"].replace("CVE-", ""), int(r["N"]), int(r["repeat"]))
        for r in rows
        if r.get("status") != VALID_STATUS
    ]

    if dry_run:
        print("\nDRY RUN: no searches will be started.")
        print(f"Would retry {len(pending)} incomplete cells.")
        return

    with log_path.open("a", encoding="utf-8") as log:
        log.write("\n" + "=" * 72 + "\n")
        log.write(f"Supplement retry started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Initial incomplete cells: {len(pending)}\n")

        for attempt in range(1, max_attempts + 1):
            if not pending:
                break

            print(f"\n========== RETRY PASS {attempt}/{max_attempts} "
                  f"({len(pending)} cells) ==========", flush=True)
            next_pending = []

            for index, (cve, n, rep) in enumerate(pending, 1):
                before = get_record(cve, n, rep)
                if before.get("status") == VALID_STATUS:
                    continue

                msg = (
                    f"[pass {attempt}/{max_attempts} | {index}/{len(pending)}] "
                    f"CVE-{cve} N={n} rep={rep} previous={before.get('status')}"
                )
                print(msg, flush=True)
                log.write(msg + "\n")
                log.flush()

                try:
                    # retry_failed=True tells the existing PERIOD sweep runner
                    # to retry an existing failed/incomplete result directory.
                    base.run_one(cve, "workload", n, rep, True)
                except Exception as exc:
                    err = f"RUN_EXCEPTION CVE-{cve} N={n} rep={rep}: {exc!r}"
                    print(err, file=sys.stderr, flush=True)
                    log.write(err + "\n")
                    log.flush()

                after = get_record(cve, n, rep)
                status = after.get("status")
                result_msg = (
                    f"RESULT CVE-{cve} N={n} rep={rep}: {status}; "
                    f"KP={after.get('initial_total_kp')}; "
                    f"first_error={after.get('first_error_round')}; "
                    f"failing_schedules={after.get('error_schedules')}; "
                    f"wall={after.get('wall_seconds')}"
                )
                print(result_msg, flush=True)
                log.write(result_msg + "\n")
                log.flush()

                if status != VALID_STATUS:
                    next_pending.append((cve, n, rep))

            pending = next_pending
            print(f"Pass {attempt} finished; remaining incomplete={len(pending)}", flush=True)

    # Rebuild the canonical CSVs/figures from all 180 result directories.
    print("\n========== REGENERATING FINAL TABLES ==========", flush=True)
    exp.analyze()

    final_rows = get_all_records()
    print_status(final_rows, "FINAL STATUS")
    final_done = sum(r.get("status") == VALID_STATUS for r in final_rows)
    print(f"\nFinal valid completion: {final_done}/180")
    print(f"Retry log: {log_path}")
    print(f"Results directory: {base.LAB}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-attempts", type=int, default=2,
        help="maximum retry passes for each still-incomplete cell (default: 2)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="list incomplete cells without starting any PERIOD search"
    )
    args = parser.parse_args()
    retry_incomplete(args.max_attempts, args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Successful runs are preserved; rerun this script to resume.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
