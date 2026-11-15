# CB Reproduction

## 1. Objective

This directory records the PERIOD measurements for the CB programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The group contains 3 programs: `CB.aget-bug`, `CB.stringbuffer`, `CB.pbzip2`.

The purpose is to run each program at bug depth 3 under the schedule budget in the manifest, repeat that run three times, and compare the recorded schedules, error interleavings, and first-bug schedule with the PERIOD columns of Table 2. Three repetitions are the target. The counts below are the repetitions that have a valid metrics record.

## 2. Files

This directory contains the group report and the metrics records for the programs that have a completed run.

| Path | Description |
|---|---|
| [`README.md`](README.md) | This report |
| [`results/CB.aget-bug/`](results/CB.aget-bug/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CB.stringbuffer/`](results/CB.stringbuffer/) | 3 valid repetition directories, each containing `metrics.json` |
| [`results/CB.pbzip2/`](results/CB.pbzip2/) | 3 valid repetition directories, each containing `metrics.json` |

The combined 36-program tables are [`../results/summary.csv`](../results/summary.csv) and [`../results/per_run.csv`](../results/per_run.csv). The runner's last-attempt snapshot, which is not the mean table, is [`../results/status.md`](../results/status.md).

## 3. Source Information

The benchmark sources are the upstream paths in [`../manifest.json`](../manifest.json). They were used from the official image at the commit recorded in [`../source_metadata.txt`](../source_metadata.txt).

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `CB.aget-bug` | `evaluation/CB/aget-bug2` | `./build.sh` | 10000 | 5 | `./aget-devel/aget -l dl.txt http://www.gnu.org/licenses/gpl.txt` |
| `CB.stringbuffer` | `evaluation/CB/stringbuffer-jdk1.4` | `./build.sh` | 10000 | 5 | `./main` |
| `CB.pbzip2` | `evaluation/CB/pbzip2-0.9.4` | `./build.sh` | 10000 | 15 | `./pbzip2-0.9.4-src/pbzip2 -k -f -p3 test.tar` |

The image, the PERIOD commit, the host that produced these measurements, and the flag meanings are recorded once for all seven groups:

- [`../source_metadata.txt`](../source_metadata.txt)
- [`../SHARED_SETUP.md`](../SHARED_SETUP.md)
- [`../docs/IMAGE.md`](../docs/IMAGE.md)
- [`../docs/FLAG_SEMANTICS.md`](../docs/FLAG_SEMANTICS.md)
- [`../paper_table2.json`](../paper_table2.json), the PERIOD columns of Table 2

This group uses that common container and host. It does not have a separate toolchain.

## 4. Reproduction Procedure and Results

These programs are entries in the shared manifest. The runner is [`../scripts/run_sctbench.py`](../scripts/run_sctbench.py). It has no option that selects only the CB group. The suite command in [`../docs/REPRODUCTION.md`](../docs/REPRODUCTION.md) builds every manifest program and runs it.

For each program, the runner executes the build command in the upstream directory, then runs `run_PDS.py` with `-y -d 3 -f` set to that program's schedule budget. If the manifest sets `exec_timeout`, the runner inserts `-t` with that value. It then appends the arguments in the table above. The repetition target is 3. A repetition that already has `valid: true` in its metrics file is left unchanged. Before each repetition the runner removes System V shared-memory key 1111 and runs one repetition at a time.

The per-schedule timeout is 5 seconds except where the table above gives another value. `-d 3` is the Table 2 bug-depth bound. The schedule budget is the configured cap. A larger number in `schedules_explored` is the recorded count, not a change to that cap.

After the external cases tree has been copied into this `results/` directory, the tables below are produced by [`../scripts/analyze.py`](../scripts/analyze.py), as described in the common procedure. The first-bug mean uses only repetitions that recorded a bug. In this group, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug value uses the same observation count as the valid-repetition count unless the cell says otherwise.

**Actual experimental results:**

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| CB.aget-bug | 3 | 3945 ± 0 | 702.7 ± 11.6 | 9 ± 0 | 0.3 ± 0.6 | 787.1 ± 11.4 |
| CB.stringbuffer | 3 | 163 ± 0 | 4 ± 0 | 121 ± 0 | 0 ± 0 | 9.2 ± 0.4 |
| CB.pbzip2 | 3 | 1609.3 ± 200.4 | 104 ± 8.9 | 47.7 ± 5.9 | 0 ± 0 | 3215.3 ± 418.1 |

A value with two or more repetitions is the mean ± sample standard deviation, rounded to one decimal place when it is not an integer. A single measured value has no sample standard deviation; the cell says so. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving. `Missing measurement` would mean a valid record omitted the field. Unrounded schedule, error, first-bug, and timeout values are in [`../results/summary.csv`](../results/summary.csv) and [`../results/summary.json`](../results/summary.json). Each `elapsed_sec` is kept to three decimal places in its metrics file. When `summary.csv` shows 0.0 in a standard-deviation column for a program with one valid repetition, that 0.0 is the script's one-observation placeholder, not a sample standard deviation.

The evidence submitted for each repetition is a metrics record, `metrics.json`. This directory does not contain the raw scheduler log or a replay log. A representative record is [`results/CB.stringbuffer/rep01/metrics.json`](results/CB.stringbuffer/rep01/metrics.json), repetition 1 of `CB.stringbuffer`:

```text
command: python3 /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 -f 10000 ./main
schedules_explored: 163
error_interleavings: 4
first_bug_schedule: 121
timeout_interleavings: 0
elapsed_sec: 9.295
stop_reason: completed
valid: true
```

The lines above are the fields stored in that file. The same fields are present in every repetition directory linked in this group.


### Comparison with the Official Reference

The published values are the PERIOD columns in [`../paper_table2.json`](../paper_table2.json). Paper values and measured values are labeled in each paragraph.

**CB.aget-bug.** Table 2 lists 3279 schedules. It labels the row AF, lists 679 buggy schedules, and lists the first bug at schedule 9. All three repetitions recorded 3945 schedules. The three repetitions recorded 715, 692, 701 error interleavings (702.7 ± 11.6). All three repetitions recorded 9 for the first-bug schedule. The schedule total differs from Table 2. The metrics do not establish the cause. The error count differs from the published buggy-schedule count of 679. The metrics do not establish the cause. The first-bug schedule matches Table 2. The three repetitions recorded 0, 1, 0 timeout interleavings (0.3 ± 0.6). Timeouts are reported separately from error interleavings and are not treated as confirmed deadlocks.

**CB.stringbuffer.** Table 2 lists 163 schedules. It labels the row AF, lists 16 buggy schedules, and lists the first bug at schedule 12. All three repetitions recorded 163 schedules. All three repetitions recorded 4 error interleavings. All three repetitions recorded 121 for the first-bug schedule. The schedule total matches Table 2. The error count differs from the published buggy-schedule count of 16. The metrics do not establish the cause. The first-bug schedule differs from Table 2. The metrics do not establish the cause.

**CB.pbzip2.** Table 2 lists 1626 schedules. It lists separate rows (BOF: 14 buggy schedules, first bug at schedule 41; NPD: 41 buggy schedules, first bug at schedule 52; UAF: 24 buggy schedules, first bug at schedule 53). Those rows are compared separately and are not averaged. The three repetitions recorded 1464, 1838, 1526 schedules (1609.3 ± 200.4). The three repetitions recorded 94, 111, 107 error interleavings (104 ± 8.9). The three repetitions recorded 41, 50, 52 for the first-bug schedule (47.7 ± 5.9). The schedule total differs from Table 2. The metrics do not establish the cause. The measured error total is the single footer value in error_interleavings. The measured first-bug schedule is the earliest error in that repetition. Neither figure is assigned to one Table 2 row.

### Final Result

The CB group has 3 programs and 9 valid repetitions in the submitted metrics. 3 of the 3 programs have the intended three repetitions.

Every program in this group has three valid repetitions.

No program in this group matches Table 2 on the schedule figure, the error count, and the first-bug figure together. The individual differences are stated above.

Timeout interleavings stay separate from error interleavings. The group evidence is the metrics records linked above. Raw scheduler logs and replay logs were not submitted, so this report does not claim replay confirmation.
