# CS Reproduction

## 1. Objective

This directory records the PERIOD measurements for the CS programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The group contains 18 programs: `CS.account_bad`, `CS.bluetooth_driver_bad`, `CS.carter01_bad`, `CS.circular_buffer_bad`, `CS.deadlock01_bad`, `CS.lazy01_bad`, `CS.queue_bad`, `CS.reorder_10_bad`, `CS.reorder_20_bad`, `CS.reorder_3_bad`, `CS.reorder_4_bad`, `CS.reorder_5_bad`, `CS.stack_bad`, `CS.token_ring_bad`, `CS.twostage_100_bad`, `CS.twostage_bad`, `CS.wronglock_3_bad`, `CS.wronglock_bad`.

The purpose is to run each program at bug depth 3 under the schedule budget in the manifest, repeat that run three times, and compare the recorded schedules, error interleavings, and first-bug schedule with the PERIOD columns of Table 2. Three repetitions are the target. The counts below are the repetitions that have a valid metrics record.

## 2. Files

This directory contains the group report and the metrics records for the programs that have a completed run.

| Path | Description |
|---|---|
| [`README.md`](README.md) | This report |
| `CS.account_bad` | No result directory. No completed run was submitted. |
| [`results/CS.bluetooth_driver_bad/`](results/CS.bluetooth_driver_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.carter01_bad/`](results/CS.carter01_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.circular_buffer_bad/`](results/CS.circular_buffer_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.deadlock01_bad/`](results/CS.deadlock01_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.lazy01_bad/`](results/CS.lazy01_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.queue_bad/`](results/CS.queue_bad/) | 1 valid repetition directory, containing `metrics.json` |
| [`results/CS.reorder_10_bad/`](results/CS.reorder_10_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.reorder_20_bad/`](results/CS.reorder_20_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.reorder_3_bad/`](results/CS.reorder_3_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.reorder_4_bad/`](results/CS.reorder_4_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.reorder_5_bad/`](results/CS.reorder_5_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.stack_bad/`](results/CS.stack_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.token_ring_bad/`](results/CS.token_ring_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.twostage_100_bad/`](results/CS.twostage_100_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.twostage_bad/`](results/CS.twostage_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.wronglock_3_bad/`](results/CS.wronglock_3_bad/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CS.wronglock_bad/`](results/CS.wronglock_bad/) | 3 valid repetition directories, each containing `metrics.json` |

The combined 36-program tables are [`../results/summary.csv`](../results/summary.csv) and [`../results/per_run.csv`](../results/per_run.csv). The runner's last-attempt snapshot, which is not the mean table, is [`../results/status.md`](../results/status.md).

## 3. Source Information

The benchmark sources are the upstream paths in [`../manifest.json`](../manifest.json). They were used from the official image at the commit recorded in [`../source_metadata.txt`](../source_metadata.txt).

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `CS.account_bad` | `evaluation/CS/account` | `./build.sh` | 10000 | 5 | `./account_bad` |
| `CS.bluetooth_driver_bad` | `evaluation/CS/bluetooth_driver` | `./build.sh` | 10000 | 5 | `./bluetooth_driver_bad` |
| `CS.carter01_bad` | `evaluation/CS/carter01` | `./build.sh` | 10000 | 5 | `./carter01_bad` |
| `CS.circular_buffer_bad` | `evaluation/CS/circular_buffer` | `./build.sh` | 10000 | 5 | `./circular_buffer_bad` |
| `CS.deadlock01_bad` | `evaluation/CS/deadlock01` | `./build.sh` | 10000 | 5 | `./deadlock01_bad` |
| `CS.lazy01_bad` | `evaluation/CS/lazy01` | `./build.sh` | 10000 | 5 | `./lazy01_bad` |
| `CS.queue_bad` | `evaluation/CS/queue` | `./build.sh` | 10000 | 5 | `./queue_bad` |
| `CS.reorder_10_bad` | `evaluation/CS/reorder_10` | `./build.sh` | 10000 | 5 | `./reorder_10_bad` |
| `CS.reorder_20_bad` | `evaluation/CS/reorder_20` | `./build.sh` | 10000 | 5 | `./reorder_20_bad` |
| `CS.reorder_3_bad` | `evaluation/CS/reorder_3` | `./build.sh` | 10000 | 5 | `./reorder_3_bad` |
| `CS.reorder_4_bad` | `evaluation/CS/reorder_4` | `./build.sh` | 10000 | 5 | `./reorder_4_bad` |
| `CS.reorder_5_bad` | `evaluation/CS/reorder_5` | `./build.sh` | 10000 | 5 | `./reorder_5_bad` |
| `CS.stack_bad` | `evaluation/CS/stack` | `./build.sh` | 10000 | 5 | `./stack_bad` |
| `CS.token_ring_bad` | `evaluation/CS/token_ring` | `./build.sh` | 10000 | 5 | `./token_ring_bad` |
| `CS.twostage_100_bad` | `evaluation/CS/twostage_100` | `./build.sh` | 100000 | 5 | `./twostage_100_bad` |
| `CS.twostage_bad` | `evaluation/CS/twostage` | `./build.sh` | 10000 | 5 | `./twostage_bad` |
| `CS.wronglock_3_bad` | `evaluation/CS/wronglock_3` | `./build.sh` | 10000 | 5 | `./wronglock_3_bad` |
| `CS.wronglock_bad` | `evaluation/CS/wronglock` | `./build.sh` | 10000 | 5 | `./wronglock_bad` |

The image, the PERIOD commit, the host that produced these measurements, and the flag meanings are recorded once for all seven groups:

- [`../source_metadata.txt`](../source_metadata.txt)
- [`../SHARED_SETUP.md`](../SHARED_SETUP.md)
- [`../docs/IMAGE.md`](../docs/IMAGE.md)
- [`../docs/FLAG_SEMANTICS.md`](../docs/FLAG_SEMANTICS.md)
- [`../paper_table2.json`](../paper_table2.json), the PERIOD columns of Table 2

This group uses that common container and host. It does not have a separate toolchain.

## 4. Reproduction Procedure and Results

These programs are entries in the shared manifest. The runner is [`../scripts/run_sctbench.py`](../scripts/run_sctbench.py). It has no option that selects only the CS group. The suite command in [`../docs/REPRODUCTION.md`](../docs/REPRODUCTION.md) builds every manifest program and runs it.

For each program, the runner executes the build command in the upstream directory, then runs `run_PDS.py` with `-y -d 3 -f` set to that program's schedule budget. If the manifest sets `exec_timeout`, the runner inserts `-t` with that value. It then appends the arguments in the table above. The repetition target is 3. A repetition that already has `valid: true` in its metrics file is left unchanged. Before each repetition the runner removes System V shared-memory key 1111 and runs one repetition at a time.

The per-schedule timeout is 5 seconds except where the table above gives another value. `-d 3` is the Table 2 bug-depth bound. The schedule budget is the configured cap. A larger number in `schedules_explored` is the recorded count, not a change to that cap.

After the external cases tree has been copied into this `results/` directory, the tables below are produced by [`../scripts/analyze.py`](../scripts/analyze.py), as described in the common procedure. The first-bug mean uses only repetitions that recorded a bug. In this group, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug value uses the same observation count as the valid-repetition count unless the cell says otherwise.

**Actual experimental results:**

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| CS.account_bad | 0 | No completed run | No completed run | No completed run | No completed run | No completed run |
| CS.bluetooth_driver_bad | 3 | 205 ± 0 | 6.7 ± 0.6 | 9 ± 0 | 0 ± 0 | 10.7 ± 1.3 |
| CS.carter01_bad | 3 | 42 ± 0 | 0 ± 0 | No error detected | 10.3 ± 0.6 | 55.3 ± 2.9 |
| CS.circular_buffer_bad | 3 | 544.7 ± 2.3 | 57.3 ± 2.1 | 16.7 ± 0.6 | 0 ± 0 | 37.3 ± 1.2 |
| CS.deadlock01_bad | 3 | 14 ± 0 | 0 ± 0 | No error detected | 6 ± 0 | 31.5 ± 0.2 |
| CS.lazy01_bad | 3 | 39 ± 0 | 12 ± 0 | 8 ± 0 | 0 ± 0 | 5.2 ± 0.9 |
| CS.queue_bad | 1 | 1048; sample standard deviation unavailable | 114; sample standard deviation unavailable | 4; sample standard deviation unavailable | 0; sample standard deviation unavailable | 71.8; sample standard deviation unavailable |
| CS.reorder_10_bad | 3 | 2350 ± 0 | 90 ± 2 | 27 ± 0 | 0 ± 0 | 212 ± 23 |
| CS.reorder_20_bad | 3 | 10000 ± 0 | 2848.7 ± 30.9 | 39 ± 0 | 12.3 ± 6.1 | 6523.5 ± 375.9 |
| CS.reorder_3_bad | 3 | 27 ± 0 | 6 ± 0 | 6 ± 0 | 0 ± 0 | 2.8 ± 0.2 |
| CS.reorder_4_bad | 3 | 100 ± 0 | 12 ± 0 | 9 ± 0 | 0 ± 0 | 9.3 ± 0.5 |
| CS.reorder_5_bad | 3 | 225 ± 0 | 20 ± 0 | 12 ± 0 | 0 ± 0 | 19.3 ± 1.2 |
| CS.stack_bad | 3 | 918 ± 0 | 117.7 ± 32.3 | 5.7 ± 1.5 | 0 ± 0 | 69.9 ± 4.9 |
| CS.token_ring_bad | 3 | 232 ± 0 | 53.3 ± 1.5 | 2.3 ± 0.6 | 0 ± 0 | 29.3 ± 4.3 |
| CS.twostage_100_bad | 3 | 100000 ± 0 | 112.7 ± 20.5 | 886.3 ± 340.1 | 19 ± 6.6 | 7387.5 ± 190 |
| CS.twostage_bad | 3 | 33 ± 0 | 2 ± 0 | 4 ± 0 | 0 ± 0 | 2.1 ± 0.1 |
| CS.wronglock_3_bad | 3 | 172 ± 0 | 42.3 ± 0.6 | 6 ± 0 | 0 ± 0 | 21.5 ± 1.6 |
| CS.wronglock_bad | 3 | 1464 ± 0 | 217.7 ± 2.1 | 10 ± 0 | 0 ± 0 | 197.7 ± 4.9 |

A value with two or more repetitions is the mean ± sample standard deviation, rounded to one decimal place when it is not an integer. A single measured value has no sample standard deviation; the cell says so. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving. `Missing measurement` would mean a valid record omitted the field. Unrounded schedule, error, first-bug, and timeout values are in [`../results/summary.csv`](../results/summary.csv) and [`../results/summary.json`](../results/summary.json). Each `elapsed_sec` is kept to three decimal places in its metrics file. When `summary.csv` shows 0.0 in a standard-deviation column for a program with one valid repetition, that 0.0 is the script's one-observation placeholder, not a sample standard deviation.

The evidence submitted for each repetition is a metrics record, `metrics.json`. This directory does not contain the raw scheduler log or a replay log. A representative record is [`results/CS.reorder_3_bad/rep01/metrics.json`](results/CS.reorder_3_bad/rep01/metrics.json), repetition 1 of `CS.reorder_3_bad`:

```text
command: python3 /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 -f 10000 ./reorder_3_bad
schedules_explored: 27
error_interleavings: 6
first_bug_schedule: 6
timeout_interleavings: 0
elapsed_sec: 3.008
stop_reason: completed
valid: true
```

The lines above are the fields stored in that file. The same fields are present in every repetition directory linked in this group.


### Comparison with the Official Reference

The published values are the PERIOD columns in [`../paper_table2.json`](../paper_table2.json). Paper values and measured values are labeled in each paragraph.

**CS.account_bad.** Table 2 lists 65 schedules. It labels the row AF, lists 26 buggy schedules, and lists the first bug at schedule 2. No completed run was submitted. There is no measured comparison. `CS.account_bad` has no result directory. [`../results/status.md`](../results/status.md) lists the build column as ok, 0 valid repetitions, last stop incomplete, and explored 0. The cause of the missing run is not established by the submitted records.

**CS.bluetooth_driver_bad.** Table 2 lists 205 schedules. It labels the row AF, lists 9 buggy schedules, and lists the first bug at schedule 9. All three repetitions recorded 205 schedules. The three repetitions recorded 7, 7, 6 error interleavings (6.7 ± 0.6). All three repetitions recorded 9 for the first-bug schedule. The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 9. The metrics do not establish the cause. The first-bug schedule matches Table 2.

**CS.carter01_bad.** Table 2 lists 42 schedules. It labels the row DL, lists 11 buggy schedules, and lists the first bug at schedule 5. All three repetitions recorded 42 schedules. All three repetitions recorded 0 error interleavings. No repetition recorded an error interleaving, so the first-bug schedule is not defined for these runs. The schedule total matches Table 2. Table 2 lists 11 buggy schedules. These runs recorded no error interleaving. The metrics do not establish the cause. Table 2 lists the first bug at schedule 5. These runs have no first-bug schedule because they recorded no error interleaving. The three repetitions recorded 11, 10, 10 timeout interleavings (10.3 ± 0.6). The same runs recorded 0 error interleavings. A timeout is the per-schedule time limit. It is reported separately and is not treated as a confirmed deadlock.

**CS.circular_buffer_bad.** Table 2 lists 871 schedules. It labels the row AF, lists 207 buggy schedules, and lists the first bug at schedule 17. The three repetitions recorded 546, 546, 542 schedules (544.7 ± 2.3). The three repetitions recorded 58, 59, 55 error interleavings (57.3 ± 2.1). The three repetitions recorded 17, 16, 17 for the first-bug schedule (16.7 ± 0.6). The schedule total differs from Table 2. The metrics do not establish the cause. The error count differs from the published buggy-schedule count of 207. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause.

**CS.deadlock01_bad.** Table 2 lists 14 schedules. It labels the row DL, lists 6 buggy schedules, and lists the first bug at schedule 3. All three repetitions recorded 14 schedules. All three repetitions recorded 0 error interleavings. No repetition recorded an error interleaving, so the first-bug schedule is not defined for these runs. The schedule total matches Table 2. Table 2 lists 6 buggy schedules. These runs recorded no error interleaving. The metrics do not establish the cause. Table 2 lists the first bug at schedule 3. These runs have no first-bug schedule because they recorded no error interleaving. All three repetitions recorded 6 timeout interleavings. The same runs recorded 0 error interleavings. A timeout is the per-schedule time limit. It is reported separately and is not treated as a confirmed deadlock.

**CS.lazy01_bad.** Table 2 lists 39 schedules. It labels the row AF, lists 12 buggy schedules, and lists the first bug at schedule 3. All three repetitions recorded 39 schedules. All three repetitions recorded 12 error interleavings. All three repetitions recorded 8 for the first-bug schedule. The schedule total matches Table 2. The error count matches the published buggy-schedule count. The first-bug schedule differs from Table 2. The metrics do not establish the cause.

**CS.queue_bad.** Table 2 lists 998 schedules. It labels the row AF, lists 119 buggy schedules, and lists the first bug at schedule 25. The one valid repetition recorded 1048 schedules. The sample standard deviation is unavailable. The one valid repetition recorded 114 error interleavings. The sample standard deviation is unavailable. The one valid repetition recorded 4 for the first-bug schedule. The sample standard deviation is unavailable. The schedule total differs from Table 2. The metrics do not establish the cause. The error count differs from the published buggy-schedule count of 119. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause. `CS.queue_bad` has valid repetitions rep01. [`../results/status.md`](../results/status.md) lists the last attempt as incomplete, with explored 0. That incomplete attempt has no metrics file in this submission, and the cause is not established.

**CS.reorder_10_bad.** Table 2 lists 2350 schedules. It labels the row AF, lists 89 buggy schedules, and lists the first bug at schedule 27. All three repetitions recorded 2350 schedules. The three repetitions recorded 88, 92, 90 error interleavings (90 ± 2). All three repetitions recorded 27 for the first-bug schedule. The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 89. The metrics do not establish the cause. The first-bug schedule matches Table 2.

**CS.reorder_20_bad.** Table 2 marks the schedule column L, the configured budget of 10000. It labels the row AF, lists 2870 buggy schedules, and lists the first bug at schedule 39. All three repetitions recorded 10000 schedules. The three repetitions recorded 2882, 2821, 2843 error interleavings (2848.7 ± 30.9). All three repetitions recorded 39 for the first-bug schedule. The recorded schedule total equals the configured budget, which is what Table 2 marks as L. The error count differs from the published buggy-schedule count of 2870. The metrics do not establish the cause. The first-bug schedule matches Table 2. The three repetitions recorded 7, 19, 11 timeout interleavings (12.3 ± 6.1). Timeouts are reported separately from error interleavings and are not treated as confirmed deadlocks.

**CS.reorder_3_bad.** Table 2 lists 27 schedules. It labels the row AF, lists 6 buggy schedules, and lists the first bug at schedule 6. All three repetitions recorded 27 schedules. All three repetitions recorded 6 error interleavings. All three repetitions recorded 6 for the first-bug schedule. The measured schedule total, error count, and first-bug schedule match Table 2.

**CS.reorder_4_bad.** Table 2 lists 100 schedules. It labels the row AF, lists 12 buggy schedules, and lists the first bug at schedule 9. All three repetitions recorded 100 schedules. All three repetitions recorded 12 error interleavings. All three repetitions recorded 9 for the first-bug schedule. The measured schedule total, error count, and first-bug schedule match Table 2.

**CS.reorder_5_bad.** Table 2 lists 225 schedules. It labels the row AF, lists 20 buggy schedules, and lists the first bug at schedule 12. All three repetitions recorded 225 schedules. All three repetitions recorded 20 error interleavings. All three repetitions recorded 12 for the first-bug schedule. The measured schedule total, error count, and first-bug schedule match Table 2.

**CS.stack_bad.** Table 2 lists 918 schedules. It labels the row AF, lists 144 buggy schedules, and lists the first bug at schedule 3. All three repetitions recorded 918 schedules. The three repetitions recorded 155, 100, 98 error interleavings (117.7 ± 32.3). The three repetitions recorded 4, 7, 6 for the first-bug schedule (5.7 ± 1.5). The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 144. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause.

**CS.token_ring_bad.** Table 2 lists 232 schedules. It labels the row AF, lists 58 buggy schedules, and lists the first bug at schedule 2. All three repetitions recorded 232 schedules. The three repetitions recorded 53, 55, 52 error interleavings (53.3 ± 1.5). The three repetitions recorded 2, 3, 2 for the first-bug schedule (2.3 ± 0.6). The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 58. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause.

**CS.twostage_100_bad.** Table 2 marks the schedule column L, the configured budget of 100000. It labels the row AF, lists 141 buggy schedules, and lists the first bug at schedule 690. All three repetitions recorded 100000 schedules. The three repetitions recorded 124, 125, 89 error interleavings (112.7 ± 20.5). The three repetitions recorded 690, 1279, 690 for the first-bug schedule (886.3 ± 340.1). The recorded schedule total equals the configured budget, which is what Table 2 marks as L. The error count differs from the published buggy-schedule count of 141. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause. The three repetitions recorded 13, 18, 26 timeout interleavings (19 ± 6.6). Timeouts are reported separately from error interleavings and are not treated as confirmed deadlocks.

**CS.twostage_bad.** Table 2 lists 33 schedules. It labels the row AF, lists 3 buggy schedules, and lists the first bug at schedule 4. All three repetitions recorded 33 schedules. All three repetitions recorded 2 error interleavings. All three repetitions recorded 4 for the first-bug schedule. The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 3. The metrics do not establish the cause. The first-bug schedule matches Table 2.

**CS.wronglock_3_bad.** Table 2 lists 172 schedules. It labels the row AF, lists 42 buggy schedules, and lists the first bug at schedule 6. All three repetitions recorded 172 schedules. The three repetitions recorded 42, 43, 42 error interleavings (42.3 ± 0.6). All three repetitions recorded 6 for the first-bug schedule. The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 42. The metrics do not establish the cause. The first-bug schedule matches Table 2.

**CS.wronglock_bad.** Table 2 lists 1464 schedules. It labels the row AF, lists 210 buggy schedules, and lists the first bug at schedule 10. All three repetitions recorded 1464 schedules. The three repetitions recorded 216, 220, 217 error interleavings (217.7 ± 2.1). All three repetitions recorded 10 for the first-bug schedule. The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 210. The metrics do not establish the cause. The first-bug schedule matches Table 2.

### Final Result

The CS group has 18 programs and 49 valid repetitions in the submitted metrics. 16 of the 18 programs have the intended three repetitions.

`CS.account_bad` has no result directory. [`../results/status.md`](../results/status.md) lists the build column as ok, 0 valid repetitions, last stop incomplete, and explored 0. The cause of the missing run is not established by the submitted records. `CS.queue_bad` has valid repetitions rep01. [`../results/status.md`](../results/status.md) lists the last attempt as incomplete, with explored 0. That incomplete attempt has no metrics file in this submission, and the cause is not established.

`CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` match Table 2 on the compared schedule figure, the error count, and the first-bug figure.

Timeout interleavings stay separate from error interleavings. The group evidence is the metrics records linked above. Raw scheduler logs and replay logs were not submitted, so this report does not claim replay confirmation.
