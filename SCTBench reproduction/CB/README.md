# CB Reproduction

## 1. Experiment Overview

This directory records the PERIOD reproduction of the 3 CB programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The objective is to measure those programs with PERIOD and compare the measurements with the PERIOD columns of Table 2.

Each program is built with the build command in [manifest.json](manifest.json), using the compilers in the official PERIOD image. PERIOD then explores schedules with `run_PDS.py`. The target is three repetitions per program. Each repetition records the schedules explored, the error interleavings, the first bug schedule, the timeout interleavings, and the elapsed time in seconds.

The programs are `CB.aget-bug`, `CB.stringbuffer`, `CB.pbzip2`. Their upstream paths and workload arguments are listed in Section 3. This directory does not contain a separate description of each program's concurrency behavior beyond the manifest and [paper_table2.json](paper_table2.json), so this report does not expand abbreviations or infer a confirmed bug type from a program name.

## 2. Experimental Results

3 of the 3 programs have three valid repetitions. This group has 9 valid repetitions.

A results cell with two or more repetitions is the mean ± the sample standard deviation, rounded to one decimal place when the value is not an integer. A single observation is the measured value, and the sample standard deviation is unavailable. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving. A measured error count of 0 is a real zero. `Measurement unavailable` would mean a valid record omitted the field. In these records, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug number uses the same observation count as the valid-repetition count. [results/summary.csv](results/summary.csv) stores 0.0 in a standard-deviation column for a one-repetition program. That 0.0 is the script's placeholder, not a sample standard deviation.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| CB.aget-bug | 3 | 3945 ± 0 | 702.7 ± 11.6 | 9 ± 0 | 0.3 ± 0.6 | 787.1 ± 11.4 |
| CB.stringbuffer | 3 | 163 ± 0 | 4 ± 0 | 121 ± 0 | 0 ± 0 | 9.2 ± 0.4 |
| CB.pbzip2 | 3 | 1609.3 ± 200.4 | 104 ± 8.9 | 47.7 ± 5.9 | 0 ± 0 | 3215.3 ± 418.1 |

3 of the 3 programs have three valid repetitions. This group contributes 9 valid repetitions.

The per-program records are in [results/cases/](results/cases/). The group tables are [results/summary.csv](results/summary.csv) and [results/per_run.csv](results/per_run.csv). The runner's last-attempt snapshot for these programs is [results/status.md](results/status.md); its explored column is the last attempt, not the mean. No raw scheduler log is stored here, so this report does not quote one and does not claim that a schedule was replayed.

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
| `CB.aget-bug` | `evaluation/CB/aget-bug2` | `./build.sh` | 10000 | 5 | `./aget-devel/aget -l dl.txt http://www.gnu.org/licenses/gpl.txt` |
| `CB.stringbuffer` | `evaluation/CB/stringbuffer-jdk1.4` | `./build.sh` | 10000 | 5 | `./main` |
| `CB.pbzip2` | `evaluation/CB/pbzip2-0.9.4` | `./build.sh` | 10000 | 15 | `./pbzip2-0.9.4-src/pbzip2 -k -f -p3 test.tar` |

`CB.pbzip2` is the only Table 2 program whose manifest sets a per-schedule timeout, 15 seconds. Its arguments include `-k -f -p3 test.tar`; that `-f` is part of the program command, after the binary. `CB.aget-bug` uses the manifest arguments `-l dl.txt` and the URL stored there. `CB.stringbuffer` runs `./main`.

## 4. Reproduction Instructions


The commands below use this directory by itself. Run the host commands in Ubuntu or in Ubuntu on WSL2. Docker Engine newer than 18.09.7 must be able to start a privileged container.

### Obtain this directory

On the host:

```bash
git clone https://github.com/Liuyuxuan218/PERIOD-reproduction.git
cd PERIOD-reproduction
export REPO="$(pwd)"
export GROUP="${REPO}/SCTBench reproduction/CB"
```

### Prepare the environment

On the host, download the pinned image and confirm `SCHED_DEADLINE`:

```bash
docker pull wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
docker run --rm --privileged wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  chrt -m | grep SCHED_DEADLINE
```

Prepare this group's external data directory and copy its manifest and runner. The runner writes under `/experiment-data/sctbench/CB`, which the bind mount exposes from `${SCT_DATA}/sctbench/CB`.

```bash
export SCT_DATA="${HOME}/sctbench-data"
mkdir -p "${SCT_DATA}/sctbench/CB/scripts"
cp "${GROUP}/manifest.json" "${SCT_DATA}/sctbench/CB/manifest.json"
cp "${GROUP}/scripts/run_sctbench.py" "${SCT_DATA}/sctbench/CB/scripts/run_sctbench.py"
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
mkdir -p "${SCT_DATA}/sctbench/CB/cases"
cp -a "${GROUP}/results/cases/." "${SCT_DATA}/sctbench/CB/cases/"
```

An earlier combined suite, if it is still on this machine, is at `${SCT_DATA}/sctbench/cases`. That directory is not the output path of this group's runner.

### Build and run

Inside the container, through `docker exec`:

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/CB/scripts/run_sctbench.py \
  /experiment-data/sctbench/CB/manifest.json --suite
```

The runner accepts `--suite`. This group's manifest has no pilot program, so `--pilot` is not an entry point. It runs only the programs listed in this directory's manifest. There is no flag that selects a single program. Each program is built with its manifest build command and then run as `run_PDS.py -y -d 3 -f <schedule budget>` plus that program's arguments. New output is written to `${SCT_DATA}/sctbench/CB/cases/<program>/repNN/`.

### Collect the records and build the tables

On the host, copy finished external records into this directory. The command copies only programs named in this group's manifest, leaves the source tree in place, and does not replace a destination file whose bytes differ.

```bash
python3 "${GROUP}/scripts/analyze.py" --collect "${SCT_DATA}/sctbench/CB/cases"
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


## 5. Comparison with Table 2

Published values are the PERIOD columns in [paper_table2.json](paper_table2.json). `L` means the configured schedule budget. Measured cells use the same rules as Section 2.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| CB.aget-bug | 3279 | 3945 ± 0 | 679 | 702.7 ± 11.6 | 9 | 9 ± 0 |
| CB.stringbuffer | 163 | 163 ± 0 | 16 | 4 ± 0 | 12 | 121 ± 0 |
| CB.pbzip2 | 1626 | 1609.3 ± 200.4 | BOF 14; NPD 41; UAF 24 | 104 ± 8.9 | BOF 41; NPD 52; UAF 53 | 47.7 ± 5.9 |

Some compared columns match, and others differ, for `CB.aget-bug` and `CB.stringbuffer`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The compared columns differ for `CB.pbzip2`. Table 2 lists more than one bug row for `CB.pbzip2`. Those rows are shown separately and are not averaged. The measured error count is the single footer total in `error_interleavings`.

### Final Result

The submitted evidence establishes 9 valid repetitions in this group and three completed repetitions for 3 of the 3 programs. Every program has three valid repetitions. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.
