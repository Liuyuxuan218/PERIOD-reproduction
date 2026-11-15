# Misc Reproduction

## 1. Objective

This directory records the PERIOD measurements for the Misc programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The group contains 1 programs: `Misc.safestack`.

The purpose is to run each program at bug depth 3 under the schedule budget in the manifest, repeat that run three times, and compare the recorded schedules, error interleavings, and first-bug schedule with the PERIOD columns of Table 2. Three repetitions are the target. The counts below are the repetitions that have a valid metrics record.

## 2. Files

This directory contains the group report and the metrics records for the programs that have a completed run.

| Path | Description |
|---|---|
| [`README.md`](README.md) | This report |
| [`results/Misc.safestack/`](results/Misc.safestack/) | 3 valid repetition directories, each containing `metrics.json` |

The combined 36-program tables are [`../results/summary.csv`](../results/summary.csv) and [`../results/per_run.csv`](../results/per_run.csv). The runner's last-attempt snapshot, which is not the mean table, is [`../results/status.md`](../results/status.md).

## 3. Source Information

The benchmark sources are the upstream paths in [`../manifest.json`](../manifest.json). They were used from the official image at the commit recorded in [`../source_metadata.txt`](../source_metadata.txt).

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `Misc.safestack` | `evaluation/SafeStack` | `./build.sh` | 10000 | 5 | `./SafeStack` |

The image, the PERIOD commit, the host that produced these measurements, and the flag meanings are recorded once for all seven groups:

- [`../source_metadata.txt`](../source_metadata.txt)
- [`../SHARED_SETUP.md`](../SHARED_SETUP.md)
- [`../docs/IMAGE.md`](../docs/IMAGE.md)
- [`../docs/FLAG_SEMANTICS.md`](../docs/FLAG_SEMANTICS.md)
- [`../paper_table2.json`](../paper_table2.json), the PERIOD columns of Table 2

This group uses that common container and host. It does not have a separate toolchain.

## 4. Reproduction Procedure and Results

These programs are entries in the shared manifest. The runner is [`../scripts/run_sctbench.py`](../scripts/run_sctbench.py). It has no option that selects only the Misc group. The suite command in [`../docs/REPRODUCTION.md`](../docs/REPRODUCTION.md) builds every manifest program and runs it.

For each program, the runner executes the build command in the upstream directory, then runs `run_PDS.py` with `-y -d 3 -f` set to that program's schedule budget. If the manifest sets `exec_timeout`, the runner inserts `-t` with that value. It then appends the arguments in the table above. The repetition target is 3. A repetition that already has `valid: true` in its metrics file is left unchanged. Before each repetition the runner removes System V shared-memory key 1111 and runs one repetition at a time.

The per-schedule timeout is 5 seconds except where the table above gives another value. `-d 3` is the Table 2 bug-depth bound. The schedule budget is the configured cap. A larger number in `schedules_explored` is the recorded count, not a change to that cap.

After the external cases tree has been copied into this `results/` directory, the tables below are produced by [`../scripts/analyze.py`](../scripts/analyze.py), as described in the common procedure. The first-bug mean uses only repetitions that recorded a bug. In this group, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug value uses the same observation count as the valid-repetition count unless the cell says otherwise.

**Actual experimental results:**

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| Misc.safestack | 3 | 135 ± 0 | 0 ± 0 | No error detected | 0 ± 0 | 7.9 ± 0.5 |

A value with two or more repetitions is the mean ± sample standard deviation, rounded to one decimal place when it is not an integer. A single measured value has no sample standard deviation; the cell says so. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving. `Missing measurement` would mean a valid record omitted the field. Unrounded schedule, error, first-bug, and timeout values are in [`../results/summary.csv`](../results/summary.csv) and [`../results/summary.json`](../results/summary.json). Each `elapsed_sec` is kept to three decimal places in its metrics file. When `summary.csv` shows 0.0 in a standard-deviation column for a program with one valid repetition, that 0.0 is the script's one-observation placeholder, not a sample standard deviation.

The evidence submitted for each repetition is a metrics record, `metrics.json`. This directory does not contain the raw scheduler log or a replay log. A representative record is [`results/Misc.safestack/rep01/metrics.json`](results/Misc.safestack/rep01/metrics.json), repetition 1 of `Misc.safestack`:

```text
command: python3 /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 -f 10000 ./SafeStack
schedules_explored: 135
error_interleavings: 0
first_bug_schedule: null
timeout_interleavings: 0
elapsed_sec: 8.33
stop_reason: completed_no_bug
valid: true
```

The lines above are the fields stored in that file. The same fields are present in every repetition directory linked in this group.


### Comparison with the Official Reference

The published values are the PERIOD columns in [`../paper_table2.json`](../paper_table2.json). Paper values and measured values are labeled in each paragraph.

**Misc.safestack.** Table 2 lists 6519 schedules. It labels the row AF, lists 0 buggy schedules, and marks the first bug as %, which this transcription records as no bug found. All three repetitions recorded 135 schedules. All three repetitions recorded 0 error interleavings. No repetition recorded an error interleaving, so the first-bug schedule is not defined for these runs. The schedule total differs from Table 2. The metrics do not establish the cause. The error count matches the published buggy-schedule count. Table 2 marks no bug found, and these runs likewise recorded no error interleaving.

### Final Result

The Misc group has 1 programs and 3 valid repetitions in the submitted metrics. 1 of the 1 programs have the intended three repetitions.

Every program in this group has three valid repetitions.

No program in this group matches Table 2 on the schedule figure, the error count, and the first-bug figure together. The individual differences are stated above.

Timeout interleavings stay separate from error interleavings. The group evidence is the metrics records linked above. Raw scheduler logs and replay logs were not submitted, so this report does not claim replay confirmation.
