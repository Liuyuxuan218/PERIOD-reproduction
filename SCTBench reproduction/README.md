# SCTBench Reproduction

## 1. Objective

This experiment reproduces the PERIOD results for the 36 SCTBench programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022. The programs are organized into seven benchmark groups: CS (18), CB (3), Chess (4), Inspect (2), Misc (1), Splash2 (3), and RADBench (5).

Each program is built from the official PERIOD image and tested at bug depth 3. The intended measurement is three repetitions per program. The schedule budget configured for those runs is 10,000, except `CS.twostage_100_bad`, whose configured budget is 100,000. Section 4 reports how many valid repetitions were submitted for each group.

The measurements were produced by 1240019547 邱洋.

## 2. Files

Individual records are stored under the group that owns the program. Combined tables for all 36 programs are stored in `results/`.

| Path | Description |
|---|---|
| [`README.md`](README.md) | This report: objective, source, procedure, and group-level results |
| [`CS/README.md`](CS/README.md) | CS, 18 programs, and its per-program results |
| [`CB/README.md`](CB/README.md) | CB, 3 programs, and its per-program results |
| [`Chess/README.md`](Chess/README.md) | Chess, 4 programs, and its per-program results |
| [`Inspect/README.md`](Inspect/README.md) | Inspect, 2 programs, and its per-program results |
| [`Misc/README.md`](Misc/README.md) | Misc, 1 program, and its per-program results |
| [`Splash2/README.md`](Splash2/README.md) | Splash2, 3 programs, and its per-program results |
| [`RADBench/README.md`](RADBench/README.md) | RADBench, 5 programs, and its per-program results |
| [`manifest.json`](manifest.json) | The 36 programs, upstream paths, build commands, arguments, and schedule budgets |
| [`paper_table2.json`](paper_table2.json) | PERIOD columns of Table 2 used for the comparison |
| [`source_metadata.txt`](source_metadata.txt) | Upstream repository, executed commit, image, and run configuration |
| [`SHARED_SETUP.md`](SHARED_SETUP.md) | Shared image and the distinction between this host and the container |
| [`docs/IMAGE.md`](docs/IMAGE.md) | Image digest check |
| [`docs/FLAG_SEMANTICS.md`](docs/FLAG_SEMANTICS.md) | Meanings of `-d`, `-f`, `-y`, and `-t` at the executed commit |
| [`scripts/run_sctbench.py`](scripts/run_sctbench.py) | Builds each program and runs the repetitions in the external data directory |
| [`scripts/analyze.py`](scripts/analyze.py) | Copies finished records into the group directories and writes the combined tables |
| [`results/summary.csv`](results/summary.csv) | One aggregate row for each of the 36 programs |
| [`results/per_run.csv`](results/per_run.csv) | One row for each submitted repetition |
| [`results/status.md`](results/status.md) | Runner snapshot. The explored column is the last attempt, not the mean |

Other files in `scripts/` record image checks and the host commands used to start a container. The procedure below uses `run_sctbench.py` and `analyze.py`. `results/summary.json` and `results/per_run.json` carry the same aggregates as the CSV files. `summary.json` also stores the sample standard deviation of the timeout counts.

## 3. Source Information

The benchmark source is the official PERIOD repository, [wcventure/PERIOD](https://github.com/wcventure/PERIOD). The paper is Wen et al., ICSE 2022, [Controlled Concurrency Testing via Periodical Scheduling](https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf). The PERIOD columns of Table 2 are transcribed in [`paper_table2.json`](paper_table2.json). In that file, `L` means the schedule budget was reached and `%` means no bug was found.

The code that executed is the Git checkout inside the official image, commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea` (`fix run_PDS.py`, 2022-01-17). The later GitHub commit `cb8deb9a176e5bb292d70d46557dd61dc0e98069` changes `AdvancedUsage.md`, `INSTALL.md`, `README.md`, and `STATUS.md`. `tool/DBDS/run_PDS.py` is the same file at both commits. These runs used the image commit, not a patched scheduler. Upstream paths for the 36 programs are in [`manifest.json`](manifest.json). No benchmark source was modified.

The container environment and the host environment are recorded separately.

| Item | Value |
|---|---|
| Docker image | `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |
| Container operating system | Ubuntu 18.04.5 LTS |
| GCC | 7.5.0 |
| Clang | 10.0.0 |
| LLVM | 10.0.0 |
| Python for `run_PDS.py` | 3.6.9 |
| NumPy for that Python | 1.19.5 |
| PERIOD commit in the image | `b6f72a7b06d01ffa7114b640312873ec2578a5ea` |
| Measurement host | Intel Core i7-13650HX, 14 cores / 20 threads, recorded for 1240019547 邱洋 |
| Host memory | 24 GiB, of which WSL reports about 11 GiB |
| WSL kernel | 6.18.58.1-microsoft-standard-WSL2 |
| Docker Engine on that host | 29.1.3 |

The container uses the host kernel. PERIOD's scheduler requires `SCHED_DEADLINE`, so the container is started privileged. `run_PDS.py` is executed with `python3`. The image also contains Python 2.7.17; the search commands in the metrics files call `python3`.

The host above is the 邱洋 column of [`SHARED_SETUP.md`](SHARED_SETUP.md). The paper reports its own workstation as an Intel Xeon Silver 4214. `environment/host_environment.txt` records 赵士锦's Intel Core i9-14900HX, which is a separate host record.

## 4. Reproduction Procedure and Results

Run the commands below on Ubuntu, or on Ubuntu under WSL2. Docker Engine newer than 18.09.7 is required, with permission to start a privileged container. The suite runs one repetition at a time. Small programs finish in seconds. `CB.pbzip2` takes about one hour per repetition, and a 10,000-schedule RADBench run takes several hours. The 36-program suite takes about one to two days.

### Step 1. Clone the repository

Run on the host:

```bash
git clone https://github.com/Liuyuxuan218/PERIOD-reproduction.git
cd PERIOD-reproduction
export REPO="$(pwd)"
```

### Step 2. Download the PERIOD image

Run on the host:

```bash
docker pull wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
docker run --rm --privileged wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  chrt -m | grep SCHED_DEADLINE
```

The second command prints `SCHED_DEADLINE` when the host kernel exposes that policy to the privileged container.

### Step 3. Prepare the external data directory

Run on the host. The runner writes here, not into the seven group directories:

```bash
export SCT_DATA="${HOME}/sctbench-data"
mkdir -p "${SCT_DATA}/sctbench/scripts"
cp "${REPO}/SCTBench reproduction/manifest.json" "${SCT_DATA}/sctbench/manifest.json"
cp "${REPO}/SCTBench reproduction/scripts/run_sctbench.py" "${SCT_DATA}/sctbench/scripts/run_sctbench.py"
```

### Step 4. Start the container and confirm the commit

Run on the host:

```bash
docker run -d --privileged --name period-sctbench \
  --mount "type=bind,source=${SCT_DATA},target=/experiment-data" \
  wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  sleep infinity
docker exec period-sctbench git -C /workdir/PERIOD rev-parse HEAD
```

The printed commit is `b6f72a7b06d01ffa7114b640312873ec2578a5ea`. The container's working directory for the tool is `/workdir/PERIOD`. The bind mount makes `${SCT_DATA}` appear as `/experiment-data`.

### Step 5. Run the pilot

Run inside the container, through `docker exec`. The pilot builds `CS.account_bad` and explores 4 schedules:

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/scripts/run_sctbench.py \
  /experiment-data/sctbench/manifest.json --pilot
```

A successful pilot writes `schedules_explored` equal to 4 in `${SCT_DATA}/sctbench/pilot/result.json`. The pilot program directory is `${SCT_DATA}/sctbench/cases/PILOT_account_f4`. It is not one of the 36 Table 2 programs, and the collection step does not copy it into a group directory.

### Step 6. Run the 36-program suite

Run inside the container:

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/scripts/run_sctbench.py \
  /experiment-data/sctbench/manifest.json --suite
```

The runner builds each program with the build command in the manifest, then runs `run_PDS.py -y -d 3 -f <schedule budget>` and that program's arguments. `CS.twostage_100_bad` uses `-f 100000`. `CB.pbzip2` also receives `-t 15`. Every other program uses the tool's 5-second per-schedule timeout. There is no flag that selects one benchmark group.

Each repetition is written under `${SCT_DATA}/sctbench/cases/<program>/repNN/`. A repetition whose `metrics.json` already contains `"valid": true` is not run again. The same command therefore continues a suite that was already started. The runner rewrites `${SCT_DATA}/sctbench/status.md` after each program. The copy of that snapshot submitted with these measurements is [`results/status.md`](results/status.md). Its explored column is the last attempt, not the mean.

### Step 7. Copy completed records into the seven group directories

Run on the host, after the suite has written the external cases tree:

```bash
python3 "${REPO}/SCTBench reproduction/scripts/analyze.py" --collect "${SCT_DATA}/sctbench/cases"
```

`--collect` copies each manifest program that has a directory under the external `cases` path into `SCTBench reproduction/<group>/results/<program>/`. The external tree stays where the runner wrote it. A file that is already present with different bytes is not overwritten. A manifest program with no source directory is not given an empty result directory. That is why `CS.account_bad` and `RADBench.bug4` have no directory in this submission.

### Step 8. Build the combined tables

Run on the host, with no path argument. The script reads only the seven `<group>/results/` directories, counts each metrics file once, and writes the combined tables:

```bash
python3 "${REPO}/SCTBench reproduction/scripts/analyze.py"
```

The outputs are:

- [`results/summary.csv`](results/summary.csv) and [`results/summary.json`](results/summary.json), one row per program
- [`results/per_run.csv`](results/per_run.csv) and [`results/per_run.json`](results/per_run.json), one row per repetition

`metrics_path` in the per-run files is the path relative to `SCTBench reproduction/`. The mean is the arithmetic mean. The standard deviation is the sample standard deviation. Programs with one valid repetition store 0.0 in the CSV standard-deviation columns because that is the existing one-observation placeholder in `analyze.py`. That placeholder is not a sample standard deviation. The group tables print the single measured value and say the sample standard deviation is undefined.

Passing the external cases directory, `python3 analyze.py "${SCT_DATA}/sctbench/cases"`, aggregates that live tree in place and writes the same combined files. It does not copy files into the group directories. The tables committed here were produced from the seven group directories after collection, so the submitted numbers have one source.


**Actual experimental results:**

The values below are counted from the metrics files now stored in the seven group directories.

| Group | Number of programs | Programs with three completed repetitions | Total valid repetitions |
|---|---:|---:|---:|
| [CS](CS/README.md) | 18 | 16 | 49 |
| [CB](CB/README.md) | 3 | 3 | 9 |
| [Chess](Chess/README.md) | 4 | 4 | 12 |
| [Inspect](Inspect/README.md) | 2 | 2 | 6 |
| [Misc](Misc/README.md) | 1 | 1 | 3 |
| [Splash2](Splash2/README.md) | 3 | 1 | 7 |
| [RADBench](RADBench/README.md) | 5 | 3 | 11 |

Across all seven groups there are 97 valid repetitions. 30 programs have three completed repetitions.

### Comparison with the Official Reference

The comparison uses [`paper_table2.json`](paper_table2.json). Each group report repeats it program by program. This section states only the matches that hold on the submitted records and the differences that remain open.

On every submitted repetition, 14 programs match a numeric Table 2 schedule total: `CS.bluetooth_driver_bad`, `CS.carter01_bad`, `CS.deadlock01_bad`, `CS.lazy01_bad`, `CS.reorder_10_bad`, `CS.reorder_3_bad`, `CS.reorder_4_bad`, `CS.reorder_5_bad`, `CS.stack_bad`, `CS.token_ring_bad`, `CS.twostage_bad`, `CS.wronglock_3_bad`, `CS.wronglock_bad`, and `CB.stringbuffer`. `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` also match the published buggy-schedule count and the published first-bug schedule.

`CS.reorder_20_bad` and `CS.twostage_100_bad` recorded exactly the configured schedule budget on every repetition. Table 2 marks that outcome as L.

The other numeric differences are left as differences. Several programs match the schedule total and differ in the error count or the first-bug schedule. `Misc.safestack` recorded 135 schedules and 0 error interleavings on every repetition (sample standard deviation 0); Table 2 lists 6519 schedules and 0 buggy schedules, with the first bug marked %. Programs whose recorded schedule count is above the configured budget are `Chess.SWSQ`, `Chess.IWSQWS`, `Inspect.qsort_mt`, `Inspect.boundedbuffer`, `Splash2.barnes`, `Splash2.fft`, `Splash2.lu`, `RADBench.bug3`, and `RADBench.bug5`. `docs/FLAG_SEMANTICS.md` explains that the footer Round total can be larger than the number of executed schedules. The totals in these tables are `schedules_explored`. For the programs just named, that executed count itself is above the configured `-f` limit, and the raw logs that would show the extra test line are not in this submission. The group reports give the stored footer values.

Timeout interleavings are not counted as error interleavings. For the programs Table 2 labels DL, the paper's buggy-schedule count is sometimes close to the timeout count, and the metrics still record 0 error interleavings. Those timeouts are not treated as confirmed deadlocks. `CS.deadlock01_bad` is the clearest case: every repetition explored 14 schedules, recorded 0 error interleavings, and recorded 6 timeout interleavings. Table 2 lists 14 schedules and 6 buggy schedules for that program.

### Final Result

The submitted metrics contain 97 valid repetitions from 34 programs. 30 programs have the intended three repetitions. `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two. `CS.queue_bad` has one. `CS.account_bad` and `RADBench.bug4` have no completed run. The Table 2 reproduction is therefore incomplete.

`results/status.md` lists the missing attempts as incomplete, or, for `Splash2.barnes` and `Splash2.fft`, does not record a cause for the absent repetition. The cause is not established by the submitted metrics. The schedule totals above the configured budget are also unresolved. Differences between the measured error counts and Table 2 are unresolved except where a group report says the figures match. Replay was not confirmed from logs in this submission, because the submitted evidence is the metrics records.

The per-program tables and the remaining differences are in the seven group reports linked above.
