# SCTBench Reproduction

## 1. Experiment Overview

This experiment reproduces the PERIOD results for the 36 SCTBench programs evaluated in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022 ([paper](https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf)). The programs are divided into seven groups: CS (18), CB (3), Chess (4), Inspect (2), Misc (1), Splash2 (3), and RADBench (5).

Each program is built with the build command shipped in the official PERIOD artifact. PERIOD then performs periodical scheduling exploration on the built program. The target is three repetitions of each program. For every repetition the experiment records five quantities: the number of schedules explored, the number of error interleavings, the schedule number of the first recorded bug, the number of timeout interleavings, and the elapsed time in seconds.

Section 3 states the shared depth, schedule budget, and machines. Sections 4–10 report every program. The commands that run the suite are kept in [docs/REPRODUCTION.md](docs/REPRODUCTION.md). Each group also has a short runner note in its own report, linked from the group section.

## 2. Overall Experimental Results

The counts below were recomputed from the `metrics.json` files in the seven group directories. A repetition counts as valid when its metrics file sets `valid` to true.

| Benchmark group | Number of programs | Programs with three completed repetitions | Total valid repetitions |
|---|---:|---:|---:|
| [CS](#4-cs) | 18 | 16 | 49 |
| [CB](#5-cb) | 3 | 3 | 9 |
| [Chess](#6-chess) | 4 | 4 | 12 |
| [Inspect](#7-inspect) | 2 | 2 | 6 |
| [Misc](#8-misc) | 1 | 1 | 3 |
| [Splash2](#9-splash2) | 3 | 1 | 7 |
| [RADBench](#10-radbench) | 5 | 3 | 11 |
| Total | 36 | 30 | 97 |

The submitted records contain 97 valid repetitions. 30 programs have three completed repetitions. `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two. `CS.queue_bad` has one. `CS.account_bad` and `RADBench.bug4` have no completed run. The Table 2 reproduction is therefore incomplete.

On every submitted repetition, 14 programs match a numeric schedule total printed in Table 2: `CS.bluetooth_driver_bad`, `CS.carter01_bad`, `CS.deadlock01_bad`, `CS.lazy01_bad`, `CS.reorder_10_bad`, `CS.reorder_3_bad`, `CS.reorder_4_bad`, `CS.reorder_5_bad`, `CS.stack_bad`, `CS.token_ring_bad`, `CS.twostage_bad`, `CS.wronglock_3_bad`, `CS.wronglock_bad`, and `CB.stringbuffer`. `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` also match Table 2 on the buggy-schedule count and the first-bug schedule. `CS.reorder_20_bad` and `CS.twostage_100_bad` recorded exactly the configured schedule budget on every repetition. Table 2 marks that schedule cell `L`.

The remaining differences are reported in Sections 4–10 and are unresolved except where a comparison cell matches. In particular, `Chess.SWSQ`, `Chess.IWSQWS`, `Inspect.qsort_mt`, `Inspect.boundedbuffer`, `Splash2.barnes`, `Splash2.fft`, `Splash2.lu`, `RADBench.bug3`, and `RADBench.bug5` recorded a schedule total above the configured budget of 10,000. Those recorded totals are kept. [docs/FLAG_SEMANTICS.md](docs/FLAG_SEMANTICS.md) explains that the footer Round total can be larger than the number of executed schedules; the totals in these tables are `schedules_explored`, and for the programs just named that executed count is itself above the configured `-f` limit. The raw logs are not in this submission. `Misc.safestack` recorded 135 schedules and 0 error interleavings on every repetition, while Table 2 lists 6519 schedules and 0 buggy schedules.

Timeout interleavings are schedules that reached the per-schedule time limit. They are reported in their own column. They are not treated as confirmed deadlocks, including where Table 2 labels a program DL and the timeout count is numerically close to the published buggy-schedule count. `CS.deadlock01_bad` shows the distinction directly: every repetition explored 14 schedules, recorded 0 error interleavings, and recorded 6 timeout interleavings, while Table 2 lists 14 schedules and 6 buggy schedules.

For two or more observations, a results cell is the arithmetic mean ± the sample standard deviation, rounded to one decimal place when the value is not an integer. For one observation, the cell is the measured value and states that the sample standard deviation is unavailable. `No completed run` means the program has no valid metrics file. `No error detected` means the valid runs finished without an error interleaving; a measured error count of 0 is a real zero, not a missing cell. `Measurement unavailable` would mean a valid record omitted the field. In these records, every valid repetition of a program either recorded a bug or recorded none, so a printed first-bug number uses the same observation count as the valid-repetition count. [results/summary.csv](results/summary.csv) stores 0.0 in a standard-deviation column when a program has one valid repetition. That 0.0 is the analysis script's one-observation placeholder, not a sample standard deviation. Unrounded values are in that CSV, in [results/summary.json](results/summary.json), and in [results/per_run.csv](results/per_run.csv).

## 3. Experimental Environment and Configuration

The measurements were produced by 1240019547 邱洋. The host and the container are recorded separately. The container runs on the host kernel.

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

The host row is the machine recorded for 邱洋 in [SHARED_SETUP.md](SHARED_SETUP.md). The paper's workstation is an Intel Xeon Silver 4214. `environment/host_environment.txt` records 赵士锦's Intel Core i9-14900HX and is a separate host record. The container is privileged so that `SCHED_DEADLINE` is available. The executed PERIOD commit is the checkout inside the image. The later GitHub commit `cb8deb9a176e5bb292d70d46557dd61dc0e98069` changes only `AdvancedUsage.md`, `INSTALL.md`, `README.md`, and `STATUS.md`.

The shared run configuration is:

- Bug depth: 3, passed as `-d 3`.
- Configured schedule budget: 10,000 per repetition, passed as `-f 10000`.
- Exception: 100,000 for `CS.twostage_100_bad`, passed as `-f 100000`.
- Target: three repetitions per program.
- Workload arguments: the `argv` entries in [manifest.json](manifest.json), appended after the scheduler flags.
- Per-schedule timeout: 5 seconds, except `CB.pbzip2`, whose manifest and recorded command use `-t 15`.

Every submitted metrics file records bug depth 3 and a schedule limit equal to that program's manifest budget. The stored command is `run_PDS.py -y -d 3 -f <budget>`, with `-t 15` only for `CB.pbzip2`, followed by the manifest arguments. The recorded `schedules_explored` value is a measurement. Where it exceeds the configured budget, Section 2 names the programs and the tables keep the recorded number.

The image digest, the commit check, and the flag meanings are in [source_metadata.txt](source_metadata.txt), [SHARED_SETUP.md](SHARED_SETUP.md), [docs/IMAGE.md](docs/IMAGE.md), and [docs/FLAG_SEMANTICS.md](docs/FLAG_SEMANTICS.md). The published PERIOD columns used for comparison are in [paper_table2.json](paper_table2.json).

## 4. CS

### Basic Information

The CS group contains 18 programs: `CS.account_bad`, `CS.bluetooth_driver_bad`, `CS.carter01_bad`, `CS.circular_buffer_bad`, `CS.deadlock01_bad`, `CS.lazy01_bad`, `CS.queue_bad`, `CS.reorder_10_bad`, `CS.reorder_20_bad`, `CS.reorder_3_bad`, `CS.reorder_4_bad`, `CS.reorder_5_bad`, `CS.stack_bad`, `CS.token_ring_bad`, `CS.twostage_100_bad`, `CS.twostage_bad`, `CS.wronglock_3_bad`, `CS.wronglock_bad`.

Their official source locations are the upstream paths in [manifest.json](manifest.json). Common bug depth, schedule budget, repetition target, and toolchain are in Section 3.

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

This repository does not contain a separate description of each program's concurrency behavior beyond those manifest entries and the Table 2 transcription in [paper_table2.json](paper_table2.json). The comparison below uses that transcription and does not expand its type codes.

### Experimental Results

Cells follow the reporting rules in Section 2.

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

The metrics records are in [CS/results/](CS/results/). A program with no completed run has no directory there. Each submitted repetition is a `metrics.json` file. No raw scheduler log is stored for this group, so this report does not quote one. The group report, including the runner notes for these programs, is [CS/README.md](CS/README.md).

### Comparison with Table 2

Published values come from [paper_table2.json](paper_table2.json). `L` is the configured schedule budget named in that cell. A measured cell is the value computed from the submitted repetitions.

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

The submitted evidence establishes 49 valid repetitions in this group and three completed repetitions for 16 of the 18 programs. Unfinished measurements remain for `CS.account_bad` and `CS.queue_bad`. Exact agreement on the schedule total, the error count, and the first-bug schedule holds for `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad`. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.

## 5. CB

### Basic Information

The CB group contains 3 programs: `CB.aget-bug`, `CB.stringbuffer`, `CB.pbzip2`.

Their official source locations are the upstream paths in [manifest.json](manifest.json). Common bug depth, schedule budget, repetition target, and toolchain are in Section 3.

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `CB.aget-bug` | `evaluation/CB/aget-bug2` | `./build.sh` | 10000 | 5 | `./aget-devel/aget -l dl.txt http://www.gnu.org/licenses/gpl.txt` |
| `CB.stringbuffer` | `evaluation/CB/stringbuffer-jdk1.4` | `./build.sh` | 10000 | 5 | `./main` |
| `CB.pbzip2` | `evaluation/CB/pbzip2-0.9.4` | `./build.sh` | 10000 | 15 | `./pbzip2-0.9.4-src/pbzip2 -k -f -p3 test.tar` |

`CB.pbzip2` is the only Table 2 program whose manifest sets a per-schedule timeout, 15 seconds. Its arguments include `-k -f -p3 test.tar`; that `-f` is part of the program command, after the binary. `CB.aget-bug` uses the manifest arguments `-l dl.txt` and the URL stored there. `CB.stringbuffer` runs `./main`.

This repository does not contain a separate description of each program's concurrency behavior beyond those manifest entries and the Table 2 transcription in [paper_table2.json](paper_table2.json). The comparison below uses that transcription and does not expand its type codes.

### Experimental Results

Cells follow the reporting rules in Section 2.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| CB.aget-bug | 3 | 3945 ± 0 | 702.7 ± 11.6 | 9 ± 0 | 0.3 ± 0.6 | 787.1 ± 11.4 |
| CB.stringbuffer | 3 | 163 ± 0 | 4 ± 0 | 121 ± 0 | 0 ± 0 | 9.2 ± 0.4 |
| CB.pbzip2 | 3 | 1609.3 ± 200.4 | 104 ± 8.9 | 47.7 ± 5.9 | 0 ± 0 | 3215.3 ± 418.1 |

3 of the 3 programs have three valid repetitions. This group contributes 9 valid repetitions.

The metrics records are in [CB/results/](CB/results/). A program with no completed run has no directory there. Each submitted repetition is a `metrics.json` file. No raw scheduler log is stored for this group, so this report does not quote one. The group report, including the runner notes for these programs, is [CB/README.md](CB/README.md).

### Comparison with Table 2

Published values come from [paper_table2.json](paper_table2.json). `L` is the configured schedule budget named in that cell. A measured cell is the value computed from the submitted repetitions.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| CB.aget-bug | 3279 | 3945 ± 0 | 679 | 702.7 ± 11.6 | 9 | 9 ± 0 |
| CB.stringbuffer | 163 | 163 ± 0 | 16 | 4 ± 0 | 12 | 121 ± 0 |
| CB.pbzip2 | 1626 | 1609.3 ± 200.4 | BOF 14; NPD 41; UAF 24 | 104 ± 8.9 | BOF 41; NPD 52; UAF 53 | 47.7 ± 5.9 |

Some compared columns match, and others differ, for `CB.aget-bug` and `CB.stringbuffer`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The compared columns differ for `CB.pbzip2`. Table 2 lists more than one bug row for `CB.pbzip2`. Those rows are shown separately and are not averaged. The measured error count is the single footer total in `error_interleavings`.

The submitted evidence establishes 9 valid repetitions in this group and three completed repetitions for 3 of the 3 programs. Every program has three valid repetitions. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.

## 6. Chess

### Basic Information

The Chess group contains 4 programs: `Chess.WSQ`, `Chess.IWSQ`, `Chess.SWSQ`, `Chess.IWSQWS`.

Their official source locations are the upstream paths in [manifest.json](manifest.json). Common bug depth, schedule budget, repetition target, and toolchain are in Section 3.

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `Chess.WSQ` | `evaluation/Chess/WorkStealQueue` | `./build.sh` | 10000 | 5 | `./WorkStealQueue 1 4 2` |
| `Chess.IWSQ` | `evaluation/Chess/InterlockedWorkStealQueue` | `./build.sh` | 10000 | 5 | `./InterlockedWorkStealQueue 1 4 2` |
| `Chess.SWSQ` | `evaluation/Chess/StateWorkStealQueue` | `./build.sh` | 10000 | 5 | `./StateWorkStealQueue 2 4 2` |
| `Chess.IWSQWS` | `evaluation/Chess/InterlockedWorkStealQueueWithState` | `./build.sh` | 10000 | 5 | `./InterlockedWorkStealQueueWithState 2 4 2` |

Each Chess program is started with the three numeric workload arguments in the table. Those arguments are the values stored in the manifest and in the metrics commands.

This repository does not contain a separate description of each program's concurrency behavior beyond those manifest entries and the Table 2 transcription in [paper_table2.json](paper_table2.json). The comparison below uses that transcription and does not expand its type codes.

### Experimental Results

Cells follow the reporting rules in Section 2.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| Chess.WSQ | 3 | 320.3 ± 23.1 | 15 ± 0 | 95.3 ± 5.8 | 0 ± 0 | 10.4 ± 0.7 |
| Chess.IWSQ | 3 | 684 ± 25.2 | 16.3 ± 0.6 | 120.7 ± 3.1 | 0 ± 0 | 24.6 ± 1 |
| Chess.SWSQ | 3 | 10001 ± 0 | 33 ± 1 | 1090 ± 892.7 | 1 ± 1 | 2415.7 ± 100.8 |
| Chess.IWSQWS | 3 | 10001 ± 0 | 34.3 ± 0.6 | 2004.3 ± 506.8 | 0.3 ± 0.6 | 2349.3 ± 102.5 |

4 of the 4 programs have three valid repetitions. This group contributes 12 valid repetitions. `Chess.SWSQ` and `Chess.IWSQWS` recorded a schedule total above the configured budget. The table keeps the recorded totals.

The metrics records are in [Chess/results/](Chess/results/). A program with no completed run has no directory there. Each submitted repetition is a `metrics.json` file. No raw scheduler log is stored for this group, so this report does not quote one. The group report, including the runner notes for these programs, is [Chess/README.md](Chess/README.md).

### Comparison with Table 2

Published values come from [paper_table2.json](paper_table2.json). `L` is the configured schedule budget named in that cell. A measured cell is the value computed from the submitted repetitions.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| Chess.WSQ | 434 | 320.3 ± 23.1 | 15 | 15 ± 0 | 105 | 95.3 ± 5.8 |
| Chess.IWSQ | 711 | 684 ± 25.2 | 17 | 16.3 ± 0.6 | 108 | 120.7 ± 3.1 |
| Chess.SWSQ | L (budget 10000) | 10001 ± 0 | BOF 11; AF 13 | 33 ± 1 | BOF 1628; AF 1630 | 1090 ± 892.7 |
| Chess.IWSQWS | L (budget 10000) | 10001 ± 0 | BOF 11; AF 13 | 34.3 ± 0.6 | BOF 1661; AF 1663 | 2004.3 ± 506.8 |

Some compared columns match, and others differ, for `Chess.WSQ`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The compared columns differ for `Chess.IWSQ`, `Chess.SWSQ`, and `Chess.IWSQWS`. The configured limit and the recorded schedule total are different quantities for `Chess.SWSQ` and `Chess.IWSQWS`. The recorded totals exceed the limit and are left unchanged. Their interpretation remains unresolved; the raw scheduler logs are not in this submission. Table 2 lists more than one bug row for `Chess.SWSQ` and `Chess.IWSQWS`. Those rows are shown separately and are not averaged. The measured error count is the single footer total in `error_interleavings`.

The submitted evidence establishes 12 valid repetitions in this group and three completed repetitions for 4 of the 4 programs. Every program has three valid repetitions. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Recorded schedule totals above the configured budget are kept as measured. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.

## 7. Inspect

### Basic Information

The Inspect group contains 2 programs: `Inspect.qsort_mt`, `Inspect.boundedbuffer`.

Their official source locations are the upstream paths in [manifest.json](manifest.json). Common bug depth, schedule budget, repetition target, and toolchain are in Section 3.

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `Inspect.qsort_mt` | `evaluation/Inspect_benchmarks/qsort_mt` | `./build.sh` | 10000 | 5 | `./qsort_mt -n 32 -f 4 -h 3 -v` |
| `Inspect.boundedbuffer` | `evaluation/Inspect_benchmarks/boundedBuffer` | `./build.sh` | 10000 | 5 | `./boundedBuffer` |

The `-f 4` in the `Inspect.qsort_mt` argument list is a program argument. The scheduler budget is the `-f 10000` that precedes the program name in the recorded command. `Inspect.boundedbuffer` has no extra program arguments.

This repository does not contain a separate description of each program's concurrency behavior beyond those manifest entries and the Table 2 transcription in [paper_table2.json](paper_table2.json). The comparison below uses that transcription and does not expand its type codes.

### Experimental Results

Cells follow the reporting rules in Section 2.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| Inspect.qsort_mt | 3 | 10001 ± 0 | 138.7 ± 2.3 | 27 ± 0 | 0 ± 0 | 423.8 ± 11.1 |
| Inspect.boundedbuffer | 3 | 10001 ± 0 | 714.3 ± 28.4 | 13.7 ± 4.5 | 0.3 ± 0.6 | 776.2 ± 4.2 |

2 of the 2 programs have three valid repetitions. This group contributes 6 valid repetitions. `Inspect.qsort_mt` and `Inspect.boundedbuffer` recorded a schedule total above the configured budget. The table keeps the recorded totals.

The metrics records are in [Inspect/results/](Inspect/results/). A program with no completed run has no directory there. Each submitted repetition is a `metrics.json` file. No raw scheduler log is stored for this group, so this report does not quote one. The group report, including the runner notes for these programs, is [Inspect/README.md](Inspect/README.md).

### Comparison with Table 2

Published values come from [paper_table2.json](paper_table2.json). `L` is the configured schedule budget named in that cell. A measured cell is the value computed from the submitted repetitions.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| Inspect.qsort_mt | 8643 | 10001 ± 0 | 135 | 138.7 ± 2.3 | 27 | 27 ± 0 |
| Inspect.boundedbuffer | L (budget 10000) | 10001 ± 0 | 1514 | 714.3 ± 28.4 | 20 | 13.7 ± 4.5 |

Some compared columns match, and others differ, for `Inspect.qsort_mt`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The compared columns differ for `Inspect.boundedbuffer`. The configured limit and the recorded schedule total are different quantities for `Inspect.qsort_mt` and `Inspect.boundedbuffer`. The recorded totals exceed the limit and are left unchanged. Their interpretation remains unresolved; the raw scheduler logs are not in this submission.

The submitted evidence establishes 6 valid repetitions in this group and three completed repetitions for 2 of the 2 programs. Every program has three valid repetitions. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Recorded schedule totals above the configured budget are kept as measured. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.

## 8. Misc

### Basic Information

The Misc group contains 1 programs: `Misc.safestack`.

Their official source locations are the upstream paths in [manifest.json](manifest.json). Common bug depth, schedule budget, repetition target, and toolchain are in Section 3.

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `Misc.safestack` | `evaluation/SafeStack` | `./build.sh` | 10000 | 5 | `./SafeStack` |

`Misc.safestack` is run as `./SafeStack` with the common bug depth of 3 and the 10,000-schedule budget. The metrics commands record that command.

This repository does not contain a separate description of each program's concurrency behavior beyond those manifest entries and the Table 2 transcription in [paper_table2.json](paper_table2.json). The comparison below uses that transcription and does not expand its type codes.

### Experimental Results

Cells follow the reporting rules in Section 2.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| Misc.safestack | 3 | 135 ± 0 | 0 ± 0 | No error detected | 0 ± 0 | 7.9 ± 0.5 |

1 of the 1 programs have three valid repetitions. This group contributes 3 valid repetitions.

The metrics records are in [Misc/results/](Misc/results/). A program with no completed run has no directory there. Each submitted repetition is a `metrics.json` file. No raw scheduler log is stored for this group, so this report does not quote one. The group report, including the runner notes for these programs, is [Misc/README.md](Misc/README.md).

### Comparison with Table 2

Published values come from [paper_table2.json](paper_table2.json). `L` is the configured schedule budget named in that cell. A measured cell is the value computed from the submitted repetitions.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| Misc.safestack | 6519 | 135 ± 0 | 0 | 0 ± 0 | no bug found (%) | No error detected |

Some compared columns match, and others differ, for `Misc.safestack`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column.

The submitted evidence establishes 3 valid repetitions in this group and three completed repetitions for 1 of the 1 programs. Every program has three valid repetitions. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.

## 9. Splash2

### Basic Information

The Splash2 group contains 3 programs: `Splash2.barnes`, `Splash2.fft`, `Splash2.lu`.

Their official source locations are the upstream paths in [manifest.json](manifest.json). Common bug depth, schedule budget, repetition target, and toolchain are in Section 3.

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `Splash2.barnes` | `evaluation/Splash2/barnes` | `./build.sh` | 10000 | 5 | `./BARNES` |
| `Splash2.fft` | `evaluation/Splash2/fft` | `./build.sh` | 10000 | 5 | `LOOP_UNWINDED_NUM=3 ./FFT -p2 -m2 -n4 -l4` |
| `Splash2.lu` | `evaluation/Splash2/lu` | `./build.sh` | 10000 | 5 | `./LU -p2 -n2 -b1` |

`Splash2.fft` is run with the manifest token `LOOP_UNWINDED_NUM=3` and the arguments `-p2 -m2 -n4 -l4`. `Splash2.lu` uses `-p2 -n2 -b1`. `Splash2.barnes` is run as `./BARNES`.

This repository does not contain a separate description of each program's concurrency behavior beyond those manifest entries and the Table 2 transcription in [paper_table2.json](paper_table2.json). The comparison below uses that transcription and does not expand its type codes.

### Experimental Results

Cells follow the reporting rules in Section 2.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| Splash2.barnes | 2 | 10001 ± 0 | 1365 ± 149.9 | 2 ± 0 | 1 ± 0 | 2424.5 ± 9.2 |
| Splash2.fft | 2 | 10001 ± 0 | 3850.5 ± 16.3 | 2 ± 0 | 0.5 ± 0.7 | 1463.6 ± 13.6 |
| Splash2.lu | 3 | 10001 ± 0 | 4740.3 ± 384.7 | 2 ± 0 | 0.3 ± 0.6 | 1668 ± 100.7 |

1 of the 3 programs have three valid repetitions. This group contributes 7 valid repetitions. `Splash2.barnes` has 2 valid repetitions (`rep02, rep03`); `Splash2.fft` has 2 valid repetitions (`rep02, rep03`). The cause of each missing repetition is not established by the submitted records. `Splash2.barnes`, `Splash2.fft`, and `Splash2.lu` recorded a schedule total above the configured budget. The table keeps the recorded totals.

The metrics records are in [Splash2/results/](Splash2/results/). A program with no completed run has no directory there. Each submitted repetition is a `metrics.json` file. No raw scheduler log is stored for this group, so this report does not quote one. The group report, including the runner notes for these programs, is [Splash2/README.md](Splash2/README.md).

### Comparison with Table 2

Published values come from [paper_table2.json](paper_table2.json). `L` is the configured schedule budget named in that cell. A measured cell is the value computed from the submitted repetitions.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| Splash2.barnes | L (budget 10000) | 10001 ± 0 | 1186 | 1365 ± 149.9 | 2 | 2 ± 0 |
| Splash2.fft | L (budget 10000) | 10001 ± 0 | 3963 | 3850.5 ± 16.3 | 2 | 2 ± 0 |
| Splash2.lu | 6129 | 10001 ± 0 | 2848 | 4740.3 ± 384.7 | 2 | 2 ± 0 |

Some compared columns match, and others differ, for `Splash2.barnes`, `Splash2.fft`, and `Splash2.lu`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The configured limit and the recorded schedule total are different quantities for `Splash2.barnes`, `Splash2.fft`, and `Splash2.lu`. The recorded totals exceed the limit and are left unchanged. Their interpretation remains unresolved; the raw scheduler logs are not in this submission.

The submitted evidence establishes 7 valid repetitions in this group and three completed repetitions for 1 of the 3 programs. Unfinished measurements remain for `Splash2.barnes` and `Splash2.fft`. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Recorded schedule totals above the configured budget are kept as measured. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.

## 10. RADBench

### Basic Information

The RADBench group contains 5 programs: `RADBench.bug2`, `RADBench.bug3`, `RADBench.bug4`, `RADBench.bug5`, `RADBench.bug6`.

Their official source locations are the upstream paths in [manifest.json](manifest.json). Common bug depth, schedule budget, repetition target, and toolchain are in Section 3.

| Program | Upstream path | Build | Schedule budget | Per-schedule timeout (s) | Arguments |
|---|---|---|---:|---:|---|
| `RADBench.bug2` | `evaluation/RADBench/bug2` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug2/src/js/src/Linux_All_DBG.OBJ:/workdir/PERIOD/evaluation/RADBench/bug2/src/nspr-4.6.7/target/dist/lib/ LOOP_UNWINDED_NUM=1 /workdir/PERIOD/evaluation/RADBench/bug2/bin/main` |
| `RADBench.bug3` | `evaluation/RADBench/bug3` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug3/src/js/src/Linux_All_DBG.OBJ:/workdir/PERIOD/evaluation/RADBench/bug3/bin/install/lib bin/main` |
| `RADBench.bug4` | `evaluation/RADBench/bug4` | `make` | 10000 | 5 | `bin/main` |
| `RADBench.bug5` | `evaluation/RADBench/bug5` | `make` | 10000 | 5 | `LD_LIBRARY_PATH=/workdir/PERIOD/evaluation/RADBench/bug5/src/nspr-4.8.6/target/dist/lib/ bin/main` |
| `RADBench.bug6` | `evaluation/RADBench/bug6` | `make` | 10000 | 5 | `bin/main` |

The build command for every RADBench program is `make`. Several argument lists begin with an `LD_LIBRARY_PATH=...` token, stored as an argument in the manifest and in the metrics commands. `RADBench.bug2` also includes the token `LOOP_UNWINDED_NUM=1`.

This repository does not contain a separate description of each program's concurrency behavior beyond those manifest entries and the Table 2 transcription in [paper_table2.json](paper_table2.json). The comparison below uses that transcription and does not expand its type codes.

### Experimental Results

Cells follow the reporting rules in Section 2.

| Program | Valid repetitions | Schedules explored | Error interleavings | First bug schedule | Timeout interleavings | Elapsed time (s) |
|---|---:|---|---|---|---|---|
| RADBench.bug2 | 3 | 8476.7 ± 141.4 | 8.7 ± 0.6 | 2472 ± 0 | 0 ± 0 | 1808.7 ± 45.7 |
| RADBench.bug3 | 2 | 10001.5 ± 0.7 | 3811 ± 1.4 | 31.5 ± 2.1 | 1 ± 0 | 1472.6 ± 20.6 |
| RADBench.bug4 | 0 | No completed run | No completed run | No completed run | No completed run | No completed run |
| RADBench.bug5 | 3 | 10001.3 ± 0.6 | 0 ± 0 | No error detected | 2.7 ± 0.6 | 16039.7 ± 452 |
| RADBench.bug6 | 3 | 3131.7 ± 12.4 | 0 ± 0 | No error detected | 330 ± 11.5 | 1806.7 ± 60.1 |

3 of the 5 programs have three valid repetitions. This group contributes 11 valid repetitions. `RADBench.bug3` has 2 valid repetitions (`rep01, rep02`); `RADBench.bug4` has no completed run. The cause of each missing repetition is not established by the submitted records. Table 2 labels `RADBench.bug5` and `RADBench.bug6` as DL. Those runs recorded 0 error interleavings. Their timeout counts stay in the timeout column and are not treated as confirmed deadlocks. `RADBench.bug3` and `RADBench.bug5` recorded a schedule total above the configured budget. The table keeps the recorded totals. `RADBench.bug2` ended before the configured budget. Table 2 marks that schedule cell L.

The metrics records are in [RADBench/results/](RADBench/results/). A program with no completed run has no directory there. Each submitted repetition is a `metrics.json` file. No raw scheduler log is stored for this group, so this report does not quote one. The group report, including the runner notes for these programs, is [RADBench/README.md](RADBench/README.md).

### Comparison with Table 2

Published values come from [paper_table2.json](paper_table2.json). `L` is the configured schedule budget named in that cell. A measured cell is the value computed from the submitted repetitions.

| Program | Table 2 schedules | Measured schedules | Table 2 buggy schedules | Measured error interleavings | Table 2 first bug | Measured first bug |
|---|---|---|---|---|---|---|
| RADBench.bug2 | L (budget 10000) | 8476.7 ± 141.4 | 9 | 8.7 ± 0.6 | 1985 | 2472 ± 0 |
| RADBench.bug3 | L (budget 10000) | 10001.5 ± 0.7 | 3478 | 3811 ± 1.4 | 42 | 31.5 ± 2.1 |
| RADBench.bug4 | L (budget 10000) | No completed run | 6 | No completed run | 259 | No completed run |
| RADBench.bug5 | L (budget 10000) | 10001.3 ± 0.6 | 0 | 0 ± 0 | no bug found (%) | No error detected |
| RADBench.bug6 | 2950 | 3131.7 ± 12.4 | 340 | 0 ± 0 | 24 | No error detected |

Some compared columns match, and others differ, for `RADBench.bug5`. The table above is the column-by-column record. The metrics do not establish the cause of a differing column. The compared columns differ for `RADBench.bug2`, `RADBench.bug3`, and `RADBench.bug6`. There is no measured comparison for `RADBench.bug4`, because no valid repetition was submitted. The configured limit and the recorded schedule total are different quantities for `RADBench.bug3` and `RADBench.bug5`. The recorded totals exceed the limit and are left unchanged. Their interpretation remains unresolved; the raw scheduler logs are not in this submission. `RADBench.bug2` stopped before the configured budget, while Table 2 marks the schedule cell L. The metrics do not establish why the search stopped short of that budget.

The submitted evidence establishes 11 valid repetitions in this group and three completed repetitions for 3 of the 5 programs. Unfinished measurements remain for `RADBench.bug3` and `RADBench.bug4`. No program in this group matches Table 2 on the schedule total, the error count, and the first-bug schedule together. Recorded schedule totals above the configured budget are kept as measured. Other numeric differences remain unresolved. Timeout interleavings are not confirmed bugs.

