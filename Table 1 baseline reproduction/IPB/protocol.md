# Protocol

This file states what the paper and the SCTBench launcher each say, and which reading is being executed. Measured numbers are not in this file.

## Sources

- PERIOD paper, Section 4.1.3 and Table 1: https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf
- PERIOD README: IPB is implemented in https://github.com/mc-imperial/sctbench
- SCTBench commit `d59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2`, files `scripts/run_many.py`, `scripts/run_single.py`, and `maple/script/maple/runner.py`
- Maple controller `maple/src/systematic/chess.cc` in that same tree

## What the paper says

Section 4.1.3 says that every controlled-concurrency technique checks bugs whose depth is no more than 5 on the CVE benchmark. Each invocation may explore up to 10,000 schedules. Each technique is invoked 10 times on each program. Table 1 uses `L` for that 10,000-schedule limit and `%` when no bug was found. The footnote says every program has two subthreads.

An invocation is one search campaign. It is not one schedule. The paper's "10 times" is ten campaigns.

## What the launcher does

`run_many.py --mode pb` calls `run_single.py` once, with the bound range `range(0, --max)`. The default `--max` is 5, so the preemption limits that actually run are 0, 1, 2, 3, and 4. Inside the runner, `mode=chess`, `enable_chess_scheduler=1`, `pb=1`, `delay_bound=0`, and `pb_limit` is that bound. `enable_pct_scheduler` is not set.

Each bound starts by deleting `search.db`. A later bound does not continue the previous bound's search. `chess.cc` exits 77 when that bound's search state is exhausted. The runner treats exit 77 as "no more executions" and stops the bound. It also stops a bound when the execution count reaches `limit`. A target crash is not itself the stop condition: the search continues until exit 77 or the limit. The runner prints `finished execution N` for every target execution, including crashes.

`--limit` defaults to 10,000 and is applied separately to each bound, not once across all bounds. A bound that reaches exactly 10,000 stops the iteration over later bounds (`run_single.py` checks `numEx == limit` after the bound). The SCTBench README also says the total across bounds can exceed 10,000 and that its own table scripts may ignore the extra schedules. The paper does not say which of those aggregations produced the single "schedules" cell.

Race profiling is a separate `mode=race` execution. Its log is not one of the `finished execution` lines of the chess search. It does not count toward the 10,000 schedule limit. The launcher's default `--max 5` also requests five race runs. Those are outside the limit as well.

PCT depth, PCT job splitting, and IPB's preemption bound are different controls. This file does not treat them as the same number.

## Conflict and the protocol being executed

The paper's "no more than 5" includes a preemption bound of 5. The launcher's `range(0, 5)` never runs `pb_limit=5`. That default is not being used.

The executed IPB protocol is:

- Ten independent campaigns per program. Each campaign deletes its search state and starts again at bound 0.
- Each campaign runs `pb_limit` 0, 1, 2, 3, 4, and 5, in that order.
- Each bound has its own fresh `search.db` and a cap of 10,000 target executions.
- One race-profiling execution is run first and is not counted in the 10,000.
- The campaign records every `finished execution` line, and separately counts lines containing `signal 11` as target crashes. A Pin assertion or a missing `finished execution` line is a tool failure, not a bug result.
- There is no PCT seed. IPB's chess scheduler seeds its own random generator with 0 (`srand(0)` in `chess.cc`).

This follows the paper's depth of 5 and its ten full invocations. It does not follow the launcher's exclusive `range(0, 5)`. The per-bound cap of 10,000 is the launcher's behavior; the paper does not say whether the 10,000 applies per bound or once to the sum. Both readings are recorded here. The executed reading is the launcher's per-bound cap, with bounds 0 through 5.
