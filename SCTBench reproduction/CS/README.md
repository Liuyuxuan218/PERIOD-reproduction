# CS Reproduction

## 1. Experiment Overview

This directory records the PERIOD reproduction of the 18 CS programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The objective is to measure those programs with PERIOD and compare the measurements with the PERIOD columns of Table 2.

Each program is built with the build command in [manifest.json](manifest.json), using the compilers in the official PERIOD image. PERIOD then explores schedules with `run_PDS.py`. The target is three repetitions per program. Each repetition records the schedules explored, the error interleavings, the first bug schedule, the timeout interleavings, and the elapsed time in seconds.

The programs are `CS.account_bad`, `CS.bluetooth_driver_bad`, `CS.carter01_bad`, `CS.circular_buffer_bad`, `CS.deadlock01_bad`, `CS.lazy01_bad`, `CS.queue_bad`, `CS.reorder_10_bad`, `CS.reorder_20_bad`, `CS.reorder_3_bad`, `CS.reorder_4_bad`, `CS.reorder_5_bad`, `CS.stack_bad`, `CS.token_ring_bad`, `CS.twostage_100_bad`, `CS.twostage_bad`, `CS.wronglock_3_bad`, `CS.wronglock_bad`. Their upstream paths and workload arguments are listed in Section 3. This directory does not contain a separate description of each program's concurrency behavior beyond the manifest and [paper_table2.json](paper_table2.json), so this report does not expand abbreviations or infer a confirmed bug type from a program name.

## 2. Experimental Results

16 of the 18 programs have three valid repetitions. This group has 49 valid repetitions.

A results cell with two or more repetitions is the mean ± the sample standard deviation, rounded to one decimal place when the value is not an integer. A single observation is the measured value, and the sample standard deviation is unavailable. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving. A measured error count of 0 is a real zero. `Measurement unavailable` would mean a valid record omitted the field. In these records, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug number uses the same observation count as the valid-repetition count. [results/summary.csv](results/summary.csv) leaves a standard-deviation field empty, and [results/summary.json](results/summary.json) stores null, when fewer than two observations exist. A standard deviation of 0 is retained only when at least two observations are identical. The observation counts are `explored_n`, `errors_n`, `first_bug_n`, and `timeouts_n`. The submitted metrics files are historical records. They do not contain the provenance fingerprint now required before a run can be reused. Recovered scheduler logs, checksums, and remaining error or timeout files are linked from [results/evidence.md](results/evidence.md). A submitted measurement with no recovered log is not independently verifiable from raw scheduler output. Reparsing each recovered log reproduces the submitted metrics. The logs do not record source or executable checksums, so these runs are not relabeled as newly verified.

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

16 of the 18 programs have three valid repetitions. This group contributes 49 valid repetitions. `CS.account_bad` has no completed run; `CS.queue_bad` has one valid repetition (`rep01`). The cause of each missing repetition is not established by the submitted records. `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` match Table 2 on the schedule total, the error count, and the first-bug schedule. Table 2 labels `CS.carter01_bad` and `CS.deadlock01_bad` as DL. Those runs recorded 0 error interleavings. Their timeout counts stay in the timeout column and are not treated as confirmed deadlocks.

The per-program records are in [results/cases/](results/cases/). The group tables are [results/summary.csv](results/summary.csv) and [results/per_run.csv](results/per_run.csv). The runner's last-attempt snapshot for these programs is [results/status.md](results/status.md); its explored column is the last attempt, not the mean. Scheduler stdout for every submitted metrics file in this group was recovered unchanged. [results/evidence.md](results/evidence.md) links each `run.log.gz`, its checksum, the matching command record, and any error or timeout files that were still present. Earlier runs kept at most two files in each Errors or Timeouts directory; files removed before this repair were not reconstructed. No schedule was replayed as part of this repair.

## 3. Environment and Configuration

The host and the container used for these measurements are:

| Item | Applies to | Value |
|---|---|---|
| CPU | Host | Intel Core i7-13650HX |
| Logical processors | Host | 20 (14 cores) |
| Memory visible to the experiment | Host, as reported by WSL | about 11 GiB of the host's 24 GiB |
| System and kernel | Host | WSL2, kernel 6.18.58.1-microsoft-standard-WSL2 |
| Docker Engine | Host | 29.1.3 |
| Docker image | Container | `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |
| Operating system | Container | Ubuntu 18.04.5 LTS |
| PERIOD source commit | Container | `b6f72a7b06d01ffa7114b640312873ec2578a5ea` |
| GCC | Container | 7.5.0 |
| Clang | Container | 10.0.0 |
| LLVM | Container | 10.0.0 |
| Python used by `run_PDS.py` | Container | 3.6.9 |
| NumPy used with that Python | Container | 1.19.5 |

The host and container record is in [environment.md](environment.md). The image digest is in [image.md](image.md). Flag meanings for these runs are in [flag_semantics.md](flag_semantics.md). The upstream paths and the modification statement are in [source_metadata.txt](source_metadata.txt).

The shared settings are bug depth 3 (`-d 3`), a configured schedule budget of 10,000 (`-f 10000`), except 100,000 for `CS.twostage_100_bad`, and three repetitions. The per-schedule timeout is 5 seconds except where the table gives another value. Every submitted metrics command in this group records those settings. A recorded schedule total above the configured budget is kept as measured. The workload arguments are:

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

`CS.twostage_100_bad` is the only program in this group whose configured schedule budget is 100,000. Every other CS program uses 10,000. The per-schedule timeout recorded for these programs is 5 seconds.

## 4. Reproduction Instructions


The commands below use this directory by itself. Run the host commands in Ubuntu or in Ubuntu on WSL2. Docker Engine newer than 18.09.7 must be able to start a privileged container.

### Obtain this directory

On the host:

```bash
git clone https://github.com/Liuyuxuan218/PERIOD-reproduction.git
cd PERIOD-reproduction
export REPO="$(pwd)"
export GROUP="${REPO}/SCTBench reproduction/CS"
```

### Prepare the environment

On the host, download the pinned image and confirm `SCHED_DEADLINE`:

```bash
docker pull wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
docker run --rm --privileged wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  chrt -m | grep SCHED_DEADLINE
```

Prepare this group's external data directory and copy its manifest and runner. The runner writes under `/experiment-data/sctbench/CS`, which the bind mount exposes from `${SCT_DATA}/sctbench/CS`.

```bash
export SCT_DATA="${HOME}/sctbench-data"
mkdir -p "${SCT_DATA}/sctbench/CS/scripts"
cp "${GROUP}/manifest.json" "${SCT_DATA}/sctbench/CS/manifest.json"
cp "${GROUP}/scripts/run_sctbench.py" "${SCT_DATA}/sctbench/CS/scripts/run_sctbench.py"
```

Start the container on the host, if it is not already running:

```bash
docker run -d --privileged --name period-sctbench \
  --mount "type=bind,source=${SCT_DATA},target=/experiment-data" \
  wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  sleep infinity
docker exec period-sctbench git -C /workdir/PERIOD rev-parse HEAD
```

The printed commit is `b6f72a7b06d01ffa7114b640312873ec2578a5ea`.

### Reuse completed repetitions

The submitted repetitions are in `"${GROUP}/results/cases"`. Copy them into the external tree before a new suite. `run_sctbench.py` leaves a repetition unchanged when its `metrics.json` already has `"valid": true`, so those runs are not repeated and their files are not overwritten.

```bash
mkdir -p "${SCT_DATA}/sctbench/CS/cases"
cp -a "${GROUP}/results/cases/." "${SCT_DATA}/sctbench/CS/cases/"
```

An earlier combined suite, if it is still on this machine, is at `${SCT_DATA}/sctbench/cases`. That directory is not the output path of this group's runner.

### Build and run

Inside the container, through `docker exec`:

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/CS/scripts/run_sctbench.py \
  /experiment-data/sctbench/CS/manifest.json --suite
```

The runner accepts `--suite` and, only when the manifest contains `CS.account_bad`, `--pilot`. It runs only the programs listed in this directory's manifest. There is no flag that selects a single program. Each program is built with its manifest build command and then run as `run_PDS.py -y -d 3 -f <schedule budget>` plus that program's arguments. New output is written to `${SCT_DATA}/sctbench/CS/cases/<program>/repNN/`.

This group includes the 4-schedule pilot for `CS.account_bad`. Run it inside the container before the suite:

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/CS/scripts/run_sctbench.py \
  /experiment-data/sctbench/CS/manifest.json --pilot
```

A successful pilot writes `schedules_explored` equal to 4 in `${SCT_DATA}/sctbench/CS/pilot/result.json`. The pilot directory is `cases/PILOT_account_f4`. It is not one of the Table 2 programs, and `--collect` does not copy it.

### Collect the records and build the tables

On the host, copy finished external records into this directory. The command copies only programs named in this group's manifest, leaves the source tree in place, and does not replace a destination file whose bytes differ.

```bash
python3 "${GROUP}/scripts/analyze.py" --collect "${SCT_DATA}/sctbench/CS/cases"
```

The same command accepts the original combined tree and still copies only this group:

```bash
python3 "${GROUP}/scripts/analyze.py" --collect "${SCT_DATA}/sctbench/cases"
```

Generate this group's tables from the records already stored in `results/cases`. The script locates that directory from its own path, so the current directory does not matter. It writes `results/summary.csv` and `results/per_run.csv` inside this group only.

```bash
python3 "${GROUP}/scripts/analyze.py"
```

To aggregate an external cases directory without copying it, pass that directory. Programs from other groups are ignored, and the external files stay where they are:

```bash
python3 "${GROUP}/scripts/analyze.py" "${SCT_DATA}/sctbench/cases"
```


A completed repetition is reused only when its provenance fingerprint matches the requested program source, tool commit, build command, compiler toolchain, executable checksum, workload arguments, schedule budget, bug depth, timeout, repetition, and seed. `build.ok` does not skip compilation unless `build.json` records those build identities and the executable is still present. A historical metrics file without that fingerprint stays in its original directory. A new execution is written to a separate attempt directory.

## 5. Comparison with Table 2

Published values are the PERIOD columns in [paper_table2.json](paper_table2.json). `L` means the configured schedule budget. Measured cells use the same rules as Section 2.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| CS.account_bad | 65 | No completed run | 26 | No completed run | 2 | No completed run |
| CS.bluetooth_driver_bad | 205 | 205 ± 0 | 9 | 6.7 ± 0.6 | 9 | 9 ± 0 |
| CS.carter01_bad | 42 | 42 ± 0 | 11 | 0 ± 0 | 5 | No error detected |
| CS.circular_buffer_bad | 871 | 544.7 ± 2.3 | 207 | 57.3 ± 2.1 | 17 | 16.7 ± 0.6 |
| CS.deadlock01_bad | 14 | 14 ± 0 | 6 | 0 ± 0 | 3 | No error detected |
| CS.lazy01_bad | 39 | 39 ± 0 | 12 | 12 ± 0 | 3 | 8 ± 0 |
| CS.queue_bad | 998 | 1048; sample standard deviation unavailable | 119 | 114; sample standard deviation unavailable | 25 | 4; sample standard deviation unavailable |
| CS.reorder_10_bad | 2350 | 2350 ± 0 | 89 | 90 ± 2 | 27 | 27 ± 0 |
| CS.reorder_20_bad | L (budget 10000) | 10000 ± 0 | 2870 | 2848.7 ± 30.9 | 39 | 39 ± 0 |
| CS.reorder_3_bad | 27 | 27 ± 0 | 6 | 6 ± 0 | 6 | 6 ± 0 |
| CS.reorder_4_bad | 100 | 100 ± 0 | 12 | 12 ± 0 | 9 | 9 ± 0 |
| CS.reorder_5_bad | 225 | 225 ± 0 | 20 | 20 ± 0 | 12 | 12 ± 0 |
| CS.stack_bad | 918 | 918 ± 0 | 144 | 117.7 ± 32.3 | 3 | 5.7 ± 1.5 |
| CS.token_ring_bad | 232 | 232 ± 0 | 58 | 53.3 ± 1.5 | 2 | 2.3 ± 0.6 |
| CS.twostage_100_bad | L (budget 100000) | 100000 ± 0 | 141 | 112.7 ± 20.5 | 690 | 886.3 ± 340.1 |
| CS.twostage_bad | 33 | 33 ± 0 | 3 | 2 ± 0 | 4 | 4 ± 0 |
| CS.wronglock_3_bad | 172 | 172 ± 0 | 42 | 42.3 ± 0.6 | 6 | 6 ± 0 |
| CS.wronglock_bad | 1464 | 1464 ± 0 | 210 | 217.7 ± 2.1 | 10 | 10 ± 0 |

The measured schedule total, error count, and first-bug schedule match Table 2 for `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad`. Some compared columns match, and others differ, for `CS.bluetooth_driver_bad`, `CS.carter01_bad`, `CS.deadlock01_bad`, `CS.lazy01_bad`, `CS.reorder_10_bad`, `CS.reorder_20_bad`, `CS.stack_bad`, `CS.token_ring_bad`, `CS.twostage_100_bad`, `CS.twostage_bad`, `CS.wronglock_3_bad`, and `CS.wronglock_bad`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The compared columns differ for `CS.circular_buffer_bad` and `CS.queue_bad`. There is no measured comparison for `CS.account_bad`, because no valid repetition was submitted.

### Final Result

The submitted evidence establishes 49 valid repetitions in this group and three completed repetitions for 16 of the 18 programs. Unfinished measurements remain for `CS.account_bad` and `CS.queue_bad`. Exact agreement on the schedule total, the error count, and the first-bug schedule holds for `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad`. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.
