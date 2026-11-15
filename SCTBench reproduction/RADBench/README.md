# RADBench Reproduction

## 1. Objective

This directory records the PERIOD measurements for the RADBench programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The group contains 5 programs: `RADBench.bug2`, `RADBench.bug3`, `RADBench.bug4`, `RADBench.bug5`, `RADBench.bug6`.

The purpose is to run each program at bug depth 3 under the schedule budget in the manifest, repeat that run three times, and compare the recorded schedules, error interleavings, and first-bug schedule with the PERIOD columns of Table 2. Three repetitions are the target. The counts below are the repetitions that have a valid metrics record.

## 2. Files

This directory contains the group report and the metrics records for the programs that have a completed run.

| Path | Description |
|---|---|
| [`README.md`](README.md) | This report |
| [`results/RADBench.bug2/`](results/RADBench.bug2/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/RADBench.bug3/`](results/RADBench.bug3/) | 2 valid repetition directories, each containing `metrics.json` |
| `RADBench.bug4` | No result directory. No completed run was submitted. |
| [`results/RADBench.bug5/`](results/RADBench.bug5/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/RADBench.bug6/`](results/RADBench.bug6/) | 3 valid repetition directories, each containing `metrics.json` |

The combined 36-program tables are [`../results/summary.csv`](../results/summary.csv) and [`../results/per_run.csv`](../results/per_run.csv). The runner's last-attempt snapshot, which is not the mean table, is [`../results/status.md`](../results/status.md).

## 3. Source Information

The benchmark sources are the upstream paths in [`../manifest.json`](../manifest.json). They were used from the official image at the commit recorded in [`../source_metadata.txt`](../source_metadata.txt).

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `RADBench.bug2` | `evaluation/RADBench/bug2` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug2/src/js/src/Linux_All_DBG.OBJ:/workdir/PERIOD/evaluation/RADBench/bug2/src/nspr-4.6.7/target/dist/lib/ LOOP_UNWINDED_NUM=1 /workdir/PERIOD/evaluation/RADBench/bug2/bin/main` |
| `RADBench.bug3` | `evaluation/RADBench/bug3` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug3/src/js/src/Linux_All_DBG.OBJ:/workdir/PERIOD/evaluation/RADBench/bug3/bin/install/lib bin/main` |
| `RADBench.bug4` | `evaluation/RADBench/bug4` | `make` | 10000 | 5 | `bin/main` |
| `RADBench.bug5` | `evaluation/RADBench/bug5` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug5/src/nspr-4.8.6/target/dist/lib/ bin/main` |
| `RADBench.bug6` | `evaluation/RADBench/bug6` | `make` | 10000 | 5 | `bin/main` |

The image, the PERIOD commit, the host that produced these measurements, and the flag meanings are recorded once for all seven groups:

- [`../source_metadata.txt`](../source_metadata.txt)
- [`../SHARED_SETUP.md`](../SHARED_SETUP.md)
- [`../docs/IMAGE.md`](../docs/IMAGE.md)
- [`../docs/FLAG_SEMANTICS.md`](../docs/FLAG_SEMANTICS.md)
- [`../paper_table2.json`](../paper_table2.json), the PERIOD columns of Table 2

This group uses that common container and host. It does not have a separate toolchain.

## 4. Reproduction Procedure and Results

These programs are entries in the shared manifest. The runner is [`../scripts/run_sctbench.py`](../scripts/run_sctbench.py). It has no option that selects only the RADBench group. The suite command in [`../README.md`](../README.md) builds every manifest program and runs it.

For each program, the runner executes the build command in the upstream directory, then runs `run_PDS.py` with `-y -d 3 -f` set to that program's schedule budget. If the manifest sets `exec_timeout`, the runner inserts `-t` with that value. It then appends the arguments in the table above. The repetition target is 3. A repetition that already has `valid: true` in its metrics file is left unchanged. Before each repetition the runner removes System V shared-memory key 1111 and runs one repetition at a time.

The per-schedule timeout is 5 seconds except where the table above gives another value. `-d 3` is the Table 2 bug-depth bound. The schedule budget is the configured cap. A larger number in `schedules_explored` is the recorded count, not a change to that cap.

After the external cases tree has been copied into this `results/` directory, the tables below are produced by [`../scripts/analyze.py`](../scripts/analyze.py), as described in the common procedure. The first-bug mean uses only repetitions that recorded a bug. In this group, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug value uses the same observation count as the valid-repetition count unless the cell says otherwise.

**Actual experimental results:**

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| RADBench.bug2 | 3 | 8476.7 ± 141.4 | 8.7 ± 0.6 | 2472 ± 0 | 0 ± 0 | 1808.7 ± 45.7 |
| RADBench.bug3 | 2 | 10001.5 ± 0.7 | 3811 ± 1.4 | 31.5 ± 2.1 | 1 ± 0 | 1472.6 ± 20.6 |
| RADBench.bug4 | 0 | No completed run | No completed run | No completed run | No completed run | No completed run |
| RADBench.bug5 | 3 | 10001.3 ± 0.6 | 0 ± 0 | No error detected | 2.7 ± 0.6 | 16039.7 ± 452 |
| RADBench.bug6 | 3 | 3131.7 ± 12.4 | 0 ± 0 | No error detected | 330 ± 11.5 | 1806.7 ± 60.1 |

A value with two or more repetitions is the mean ± sample standard deviation, rounded to one decimal place when it is not an integer. A single measured value has no sample standard deviation; the cell says so. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving. `Missing measurement` would mean a valid record omitted the field. Unrounded schedule, error, first-bug, and timeout values are in [`../results/summary.csv`](../results/summary.csv) and [`../results/summary.json`](../results/summary.json). Each `elapsed_sec` is kept to three decimal places in its metrics file. When `summary.csv` shows 0.0 in a standard-deviation column for a program with one valid repetition, that 0.0 is the script's one-observation placeholder, not a sample standard deviation.

The evidence submitted for each repetition is a metrics record, `metrics.json`. This directory does not contain the raw scheduler log or a replay log. A representative record is [`results/RADBench.bug2/rep01/metrics.json`](results/RADBench.bug2/rep01/metrics.json), repetition 1 of `RADBench.bug2`:

```text
command: python3 /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 -f 10000 LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug2/src/js/src/Linux_All_DBG.OBJ:/workdir/PERIOD/evaluation/RADBench/bug2/src/nspr-4.6.7/target/dist/lib/ LOOP_UNWINDED_NUM=1 /workdir/PERIOD/evaluation/RADBench/bug2/bin/main
schedules_explored: 8423
error_interleavings: 8
first_bug_schedule: 2472
timeout_interleavings: 0
elapsed_sec: 1777.262
stop_reason: completed
valid: true
```

The lines above are the fields stored in that file. The same fields are present in every repetition directory linked in this group.


### Comparison with the Official Reference

The published values are the PERIOD columns in [`../paper_table2.json`](../paper_table2.json). Paper values and measured values are labeled in each paragraph.

**RADBench.bug2.** Table 2 marks the schedule column L, the configured budget of 10000. It labels the row AF, lists 9 buggy schedules, and lists the first bug at schedule 1985. The three repetitions recorded 8423, 8637, 8370 schedules (8476.7 ± 141.4). The three repetitions recorded 8, 9, 9 error interleavings (8.7 ± 0.6). All three repetitions recorded 2472 for the first-bug schedule. The error count differs from the published buggy-schedule count of 9. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause. The runs ended before the configured budget of 10000. The recorded stop reason is completed. The metrics do not establish why the search stopped short of the budget Table 2 marks as L.

**RADBench.bug3.** Table 2 marks the schedule column L, the configured budget of 10000. It labels the row AF, lists 3478 buggy schedules, and lists the first bug at schedule 42. The two repetitions recorded 10002, 10001 schedules (10001.5 ± 0.7). The two repetitions recorded 3812, 3810 error interleavings (3811 ± 1.4). The two repetitions recorded 30, 33 for the first-bug schedule (31.5 ± 2.1). The error count differs from the published buggy-schedule count of 3478. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause. Both repetitions recorded 1 timeout interleavings. Timeouts are reported separately from error interleavings and are not treated as confirmed deadlocks. The recorded schedule count is above the configured budget of 10000. Every submitted repetition has an empty bare_test_lines list. The metrics store round_footer_total separately (10008, 10008). The raw scheduler log is not in this submission, so the extra executed count remains unresolved. `RADBench.bug3` has valid repetitions rep01, rep02. [`../results/status.md`](../results/status.md) lists the last attempt as incomplete, with explored 0. That incomplete attempt has no metrics file in this submission, and the cause is not established.

**RADBench.bug4.** Table 2 marks the schedule column L, the configured budget of 10000. It labels the row AF, lists 6 buggy schedules, and lists the first bug at schedule 259. No completed run was submitted. There is no measured comparison. `RADBench.bug4` has no result directory. [`../results/status.md`](../results/status.md) lists the build column as ok, 0 valid repetitions, last stop incomplete, and explored 0. The cause of the missing run is not established by the submitted records.

**RADBench.bug5.** Table 2 marks the schedule column L, the configured budget of 10000. It labels the row DL, lists 0 buggy schedules, and marks the first bug as %, which this transcription records as no bug found. The three repetitions recorded 10001, 10001, 10002 schedules (10001.3 ± 0.6). All three repetitions recorded 0 error interleavings. No repetition recorded an error interleaving, so the first-bug schedule is not defined for these runs. The error count matches the published buggy-schedule count. Table 2 marks no bug found, and these runs likewise recorded no error interleaving. The three repetitions recorded 3, 3, 2 timeout interleavings (2.7 ± 0.6). The same runs recorded 0 error interleavings. A timeout is the per-schedule time limit. It is reported separately and is not treated as a confirmed deadlock. The recorded schedule count is above the configured budget of 10000. Every submitted repetition has an empty bare_test_lines list. The metrics store round_footer_total separately (10039, 10031, 10025). The raw scheduler log is not in this submission, so the extra executed count remains unresolved.

**RADBench.bug6.** Table 2 lists 2950 schedules. It labels the row DL, lists 340 buggy schedules, and lists the first bug at schedule 24. The three repetitions recorded 3146, 3124, 3125 schedules (3131.7 ± 12.4). All three repetitions recorded 0 error interleavings. No repetition recorded an error interleaving, so the first-bug schedule is not defined for these runs. The schedule total differs from Table 2. The metrics do not establish the cause. Table 2 lists 340 buggy schedules. These runs recorded no error interleaving. The metrics do not establish the cause. Table 2 lists the first bug at schedule 24. These runs have no first-bug schedule because they recorded no error interleaving. The three repetitions recorded 342, 329, 319 timeout interleavings (330 ± 11.5). The same runs recorded 0 error interleavings. A timeout is the per-schedule time limit. It is reported separately and is not treated as a confirmed deadlock.

### Final Result

The RADBench group has 5 programs and 11 valid repetitions in the submitted metrics. 3 of the 5 programs have the intended three repetitions.

`RADBench.bug3` has valid repetitions rep01, rep02. [`../results/status.md`](../results/status.md) lists the last attempt as incomplete, with explored 0. That incomplete attempt has no metrics file in this submission, and the cause is not established. `RADBench.bug4` has no result directory. [`../results/status.md`](../results/status.md) lists the build column as ok, 0 valid repetitions, last stop incomplete, and explored 0. The cause of the missing run is not established by the submitted records.

No program in this group matches Table 2 on the schedule figure, the error count, and the first-bug figure together. The individual differences are stated above.

`RADBench.bug3` and `RADBench.bug5` have a recorded schedule total above the configured budget. That difference remains unresolved.

Timeout interleavings stay separate from error interleavings. The group evidence is the metrics records linked above. Raw scheduler logs and replay logs were not submitted, so this report does not claim replay confirmation.
