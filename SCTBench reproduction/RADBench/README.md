# RADBench Reproduction

## 1. Experiment Overview

This directory records the PERIOD reproduction of the 5 RADBench programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The objective is to measure those programs with PERIOD and compare the measurements with the PERIOD columns of Table 2.

Each program is built with the build command in [manifest.json](manifest.json), using the compilers in the official PERIOD image. PERIOD then explores schedules with `run_PDS.py`. The target is three repetitions per program. Each repetition records the schedules explored, the error interleavings, the first bug schedule, the timeout interleavings, and the elapsed time in seconds.

The programs are `RADBench.bug2`, `RADBench.bug3`, `RADBench.bug4`, `RADBench.bug5`, `RADBench.bug6`. Their upstream paths and workload arguments are listed in Section 3. This directory does not contain a separate description of each program's concurrency behavior beyond the manifest and [paper_table2.json](paper_table2.json), so this report does not expand abbreviations or infer a confirmed bug type from a program name.

## 2. Experimental Results

3 of the 5 programs have three valid repetitions. This group has 11 valid repetitions.

A results cell with two or more repetitions is the mean ± the sample standard deviation, rounded to one decimal place when the value is not an integer. A single observation is the measured value, and the sample standard deviation is unavailable. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving. A measured error count of 0 is a real zero. `Measurement unavailable` would mean a valid record omitted the field. In these records, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug number uses the same observation count as the valid-repetition count. [results/summary.csv](results/summary.csv) leaves a standard-deviation field empty, and [results/summary.json](results/summary.json) stores null, when fewer than two observations exist. A standard deviation of 0 is retained only when at least two observations are identical. The observation counts are `explored_n`, `errors_n`, `first_bug_n`, and `timeouts_n`. The submitted metrics files are historical records. They do not contain the provenance fingerprint now required before a run can be reused. Recovered scheduler logs, checksums, and remaining error or timeout files are linked from [results/evidence.md](results/evidence.md). A submitted measurement with no recovered log is not independently verifiable from raw scheduler output. Reparsing each recovered log reproduces the submitted metrics. The logs do not record source or executable checksums, so these runs are not relabeled as newly verified.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| RADBench.bug2 | 3 | 8476.7 ± 141.4 | 8.7 ± 0.6 | 2472 ± 0 | 0 ± 0 | 1808.7 ± 45.7 |
| RADBench.bug3 | 2 | 10001.5 ± 0.7 | 3811 ± 1.4 | 31.5 ± 2.1 | 1 ± 0 | 1472.6 ± 20.6 |
| RADBench.bug4 | 0 | No completed run | No completed run | No completed run | No completed run | No completed run |
| RADBench.bug5 | 3 | 10001.3 ± 0.6 | 0 ± 0 | No error detected | 2.7 ± 0.6 | 16039.7 ± 452 |
| RADBench.bug6 | 3 | 3131.7 ± 12.4 | 0 ± 0 | No error detected | 330 ± 11.5 | 1806.7 ± 60.1 |

3 of the 5 programs have three valid repetitions. This group contributes 11 valid repetitions. `RADBench.bug3` has 2 valid repetitions (`rep01, rep02`); `RADBench.bug4` has no completed run. The cause of each missing repetition is not established by the submitted records. Table 2 labels `RADBench.bug5` and `RADBench.bug6` as DL. Those runs recorded 0 error interleavings. Their timeout counts stay in the timeout column and are not treated as confirmed deadlocks. `RADBench.bug3` and `RADBench.bug5` recorded a schedule total above the configured budget. The table keeps the recorded totals. `RADBench.bug2` ended before the configured budget. Table 2 marks that schedule cell L.

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

The shared settings are bug depth 3 (`-d 3`), a configured schedule budget of 10,000 (`-f 10000`), and three repetitions. The per-schedule timeout is 5 seconds except where the table gives another value. Every submitted metrics command in this group records those settings. A recorded schedule total above the configured budget is kept as measured. The workload arguments are:

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `RADBench.bug2` | `evaluation/RADBench/bug2` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug2/src/js/src/Linux_All_DBG.OBJ:/workdir/PERIOD/evaluation/RADBench/bug2/src/nspr-4.6.7/target/dist/lib/ LOOP_UNWINDED_NUM=1 /workdir/PERIOD/evaluation/RADBench/bug2/bin/main` |
| `RADBench.bug3` | `evaluation/RADBench/bug3` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug3/src/js/src/Linux_All_DBG.OBJ:/workdir/PERIOD/evaluation/RADBench/bug3/bin/install/lib bin/main` |
| `RADBench.bug4` | `evaluation/RADBench/bug4` | `make` | 10000 | 5 | `bin/main` |
| `RADBench.bug5` | `evaluation/RADBench/bug5` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug5/src/nspr-4.8.6/target/dist/lib/ bin/main` |
| `RADBench.bug6` | `evaluation/RADBench/bug6` | `make` | 10000 | 5 | `bin/main` |

The build command for every RADBench program is `make`. Several argument lists begin with an `LD_LIBRARY_PATH=...` token, stored as an argument in the manifest and in the metrics commands. `RADBench.bug2` also includes the token `LOOP_UNWINDED_NUM=1`.

## 4. Reproduction Instructions


The commands below use this directory by itself. Run the host commands in Ubuntu or in Ubuntu on WSL2. Docker Engine newer than 18.09.7 must be able to start a privileged container.

### Obtain this directory

On the host:

```bash
git clone https://github.com/Liuyuxuan218/PERIOD-reproduction.git
cd PERIOD-reproduction
export REPO="$(pwd)"
export GROUP="${REPO}/SCTBench reproduction/RADBench"
```

### Prepare the environment

On the host, download the pinned image and confirm `SCHED_DEADLINE`:

```bash
docker pull wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
docker run --rm --privileged wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  chrt -m | grep SCHED_DEADLINE
```

Prepare this group's external data directory and copy its manifest and runner. The runner writes under `/experiment-data/sctbench/RADBench`, which the bind mount exposes from `${SCT_DATA}/sctbench/RADBench`.

```bash
export SCT_DATA="${HOME}/sctbench-data"
mkdir -p "${SCT_DATA}/sctbench/RADBench/scripts"
cp "${GROUP}/manifest.json" "${SCT_DATA}/sctbench/RADBench/manifest.json"
cp "${GROUP}/scripts/run_sctbench.py" "${SCT_DATA}/sctbench/RADBench/scripts/run_sctbench.py"
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
mkdir -p "${SCT_DATA}/sctbench/RADBench/cases"
cp -a "${GROUP}/results/cases/." "${SCT_DATA}/sctbench/RADBench/cases/"
```

An earlier combined suite, if it is still on this machine, is at `${SCT_DATA}/sctbench/cases`. That directory is not the output path of this group's runner.

### Build and run

Inside the container, through `docker exec`:

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/RADBench/scripts/run_sctbench.py \
  /experiment-data/sctbench/RADBench/manifest.json --suite
```

The runner accepts `--suite`. This group's manifest has no pilot program, so `--pilot` is not an entry point. It runs only the programs listed in this directory's manifest. There is no flag that selects a single program. Each program is built with its manifest build command and then run as `run_PDS.py -y -d 3 -f <schedule budget>` plus that program's arguments. New output is written to `${SCT_DATA}/sctbench/RADBench/cases/<program>/repNN/`.

### Collect the records and build the tables

On the host, copy finished external records into this directory. The command copies only programs named in this group's manifest, leaves the source tree in place, and does not replace a destination file whose bytes differ.

```bash
python3 "${GROUP}/scripts/analyze.py" --collect "${SCT_DATA}/sctbench/RADBench/cases"
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
| RADBench.bug2 | L (budget 10000) | 8476.7 ± 141.4 | 9 | 8.7 ± 0.6 | 1985 | 2472 ± 0 |
| RADBench.bug3 | L (budget 10000) | 10001.5 ± 0.7 | 3478 | 3811 ± 1.4 | 42 | 31.5 ± 2.1 |
| RADBench.bug4 | L (budget 10000) | No completed run | 6 | No completed run | 259 | No completed run |
| RADBench.bug5 | L (budget 10000) | 10001.3 ± 0.6 | 0 | 0 ± 0 | no bug found (%) | No error detected |
| RADBench.bug6 | 2950 | 3131.7 ± 12.4 | 340 | 0 ± 0 | 24 | No error detected |

Some compared columns match, and others differ, for `RADBench.bug5`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The compared columns differ for `RADBench.bug2`, `RADBench.bug3`, and `RADBench.bug6`. There is no measured comparison for `RADBench.bug4`, because no valid repetition was submitted. The configured limit and the recorded schedule total are different quantities for `RADBench.bug3` and `RADBench.bug5`. The recorded totals exceed the limit and are left unchanged. Their interpretation remains unresolved; the raw scheduler logs are not in this submission. `RADBench.bug2` stopped before the configured budget, while Table 2 marks the schedule cell L. The metrics do not establish why the search stopped short of that budget.

### Final Result

The submitted evidence establishes 11 valid repetitions in this group and three completed repetitions for 3 of the 5 programs. Unfinished measurements remain for `RADBench.bug3` and `RADBench.bug4`. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Recorded schedule totals above the configured budget are kept as measured. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.
