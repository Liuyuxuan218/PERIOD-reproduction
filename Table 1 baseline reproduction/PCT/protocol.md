# Protocol

This file states what the paper and the SCTBench launcher each say, and which reading is being executed. Measured numbers are not in this file.

## Sources

- PERIOD paper, Section 4.1.3 and Table 1: https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf
- PERIOD README: PCT is implemented in https://github.com/mc-imperial/sctbench
- SCTBench commit `d59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2`, files `scripts/run_many.py`, `scripts/run_single.py`, and `maple/script/maple/runner.py`

## What the paper says

Section 4.1.3 says that every controlled-concurrency technique checks bugs whose depth is no more than 5 on the CVE benchmark. Each invocation may explore up to 10,000 schedules. Each technique is invoked 10 times on each program. Table 1 prints schedules to the first bug and buggy schedules for PCT. It does not print a total-schedule column for PCT. `L` and `%` have the same meanings as in the rest of the table.

An invocation is one search campaign. It is not one schedule and it is not one of the launcher's parallel jobs.

## What the launcher does

`run_many.py --mode pct` sets `bug_depth` to `--max`. The default `--max` is 5, so `pct_d=5`. The runner passes that value as `-pct_d` with `-enable_pct_scheduler 1` and `-enable_chess_scheduler 0`. `-pct_n` comes from the benchmark list's thread field, and `-pct_k` comes from that list's step field. These ten CVE programs are not in that list.

The same function sets `seed=0` in source and splits `--limit` across `--numjobs`. The default is 10 jobs of `10000/10 = 1000` schedules. Job `i` fast-forwards the random stream by `i * 1000` and then draws one 32-bit seed per execution. The jobs continue one random stream. They do not restart it, and they do not use distinct campaign seeds.

The PCT loop does not stop when a target crashes. It runs until `limit` executions have printed `finished execution`, unless the timeout flag is set. Each execution is counted, whether or not it crashes.

Race profiling is a separate `mode=race` execution and is not part of the PCT `finished execution` count.

IPB's `pb_limit` and PCT's `pct_d` are different fields. The paper's word "depth" is applied to both, but the code does not implement them with the same loop.

## Conflict and the protocol being executed

The paper's ten invocations, each with a budget of 10,000, are not the launcher's ten jobs of 1,000 under one seed. The launcher's job split is recorded here and is not the campaign being run.

The executed PCT protocol is:

- Ten campaigns per program.
- Each campaign has `limit=10000`, `pct_d=5`, `start_index=0`, and its own seed `202611231` through `202611240`.
- `pct_n` is the number of `HandleThreadStart` lines observed in that program's race profile. For CVE-2009-3547 that number is 3, which is the main thread plus the paper's two subthreads.
- `pct_k` is at least 64 and at least twice the `PCT NUM STEPS` value observed in a one-schedule probe. The paper does not publish `pct_k`. The probe value is a measured setting, not a published one.
- One race-profiling execution comes first and is not counted in the 10,000.
- The campaign does not stop at the first crash. A Pin assertion or a runner crash is a tool failure. `signal 11` is a target crash. It is not by itself classified as NPD, UAF, or DF.

The distinct seeds are supported by `run_single.py`'s seed argument and by `runner.py`, which draws per-execution seeds from that campaign seed. They are a deliberate departure from the hardcoded `seed=0` in `run_many.py`. These campaigns are independent randomized trials under those recorded seeds. They are not ten replays of one seed.
