# Protocol

This protocol was written from the PERIOD paper and the SCTBench launcher at commit `d59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2`. No formal campaign was started. Nothing in this file is a measured Table 1 result.

## Official sources

- Paper: https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf, Section 4.1.3 and Table 1.
- PERIOD README: https://github.com/wcventure/PERIOD. It says IPB, IDB, DFS, PCT, and Random are implemented in SCTBench, and it points to Maple at https://github.com/jieyu/maple.
- SCTBench: https://github.com/mc-imperial/sctbench, commit `d59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2`.
- Maple HEAD reported by `git ls-remote` on 2026-11-23: `14b2769a07473f9eca6ea1bc7f57bbefe1db46f4`. Maple was not checked out or built.
- CVE programs: `evaluation/ConVul-CVE-Benchmarks` in the local PERIOD tree. Checksums are in `source_metadata.txt`. These ten programs are not entries in SCTBench's own benchmark list.

## Commands that the launcher actually accepts

From a sourced SCTBench environment, after `PIN_HOME` is set:

```bash
python scripts/run_many.py --mode pct --limit 10000 --timelimit 30 benchmarks/buggy.txt
```

`--limit` defaults to 10000 and `--timelimit` defaults to 30 seconds in `run_many.py`. The README's examples use `--timelimit 300`. The paper does not state the per-execution timeout. `buggy.txt` does not list these CVE programs, so that command is the launcher's interface, not a command that already targets Table 1.

The CVE programs in the PERIOD tree are built by that tree's `build.sh`. Those scripts are PERIOD instrumentations. They are not Maple/PIN builds, and running them would not select IPB or PCT.

## Paper settings that are explicit

Section 4.1.3 sets the schedule bound for every CCT technique so that it checks bugs of depth no more than 5 on the CVE benchmark. The footnote of Table 1 says every program has two subthreads. Each invocation may explore up to 10,000 schedules. The paper says each technique is run 10 times per program. The published hardware is an Intel Xeon Silver 4214, Ubuntu 18.04, GCC 7.5, and LLVM 10.0.

`L` in the table means that 10,000-schedule limit was reached. `%` means no bug was found. A blank schedule cell is blank in the PDF; it is not filled in from a neighbouring row.

## Counting

IPB's published columns are schedules to the first bug, schedules explored, and buggy schedules. PCT's published columns are schedules to the first bug and buggy schedules. Total PCT executions would be kept as supporting evidence, because the paper does not print that column.

A repetition is one complete search campaign. One schedule inside a campaign is not a repetition. The paper asks for 10 campaigns. This project also requires at least three. Neither number was run.

For a campaign that finds a bug, the first-bug statistic is conditional on detection. A campaign that finishes without a bug stays visible as no detection. It is not replaced by zero or by 10,000. A timeout, a tool crash, a build failure, and an interrupted campaign are separate statuses. A SEGV is not classified as NPD unless the log identifies that bug type.


## PCT control flow in the official launcher

`scripts/run_many.py --mode pct` sets `bug_depth` to `--max`. The default `--max` is 5. It also sets `seed` to 0 in the launcher source. The default `--numjobs` is 10, and each job receives `limit / numjobs` schedules (1,000 when the limit is 10,000). The jobs differ by `start_index`, not by seed.

That split is one launcher invocation whose parts add to 10,000 schedules. Section 4.1.3 also says that each invocation has a budget of up to 10,000 schedules and that each technique is invoked 10 times. Those two readings are not the same experiment. The paper does not say which one produced Table 1, and it does not publish the PCT seeds. This protocol does not treat `--numjobs 10` as ten independent campaigns, and it does not invent seeds.

The RQ3 submission used PCT depth 3 on SCTBench overhead workloads. That setting belongs to a different task and is not used here.

## What was not established

- The paper does not publish the `--max` value, the per-execution timeout, the PCT seeds, or the rule that turns several IPB bounds into one Table 1 cell.
- SCTBench has no CVE manifest with `max_threads` and `max_steps` for these ten programs.
- No PIN binary and no kernel of version 3.x or older were available, so these uncertainties were not resolved by a pilot.
