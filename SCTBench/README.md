# SCTBench Reproduction with PERIOD

## 1. Overview

This project reproduces the SCTBench programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022, using PERIOD.

Contributor: 1240019547 邱洋.

The experiment builds each program with the scripts in the official PERIOD image, then performs periodical scheduling at bug depth 3. Each program is run for three repetitions. The schedule budget is 10,000, and 100,000 for `CS.twostage_100_bad`. The recorded measurements are in `measurements/`, and the aggregate table is in `results/summary.csv`.

Paper: https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf

Upstream tool: https://github.com/wcventure/PERIOD

## 2. Files

| File or Directory | Description |
|---|---|
| `README.md` | Reproduction instructions and experimental results |
| `manifest.json` | The 36 SCTBench programs, with upstream path, build command, arguments, and schedule limit |
| `paper_table2.json` | PERIOD columns of Table 2 |
| `scripts/run_sctbench.py` | Builds each program and runs the three repetitions |
| `scripts/analyze.py` | Builds the mean and sample standard deviation tables |
| `measurements/` | Per-repetition `metrics.json` files from our runs |
| `results/summary.csv` | Aggregate of those repetitions |
| `results/per_run.csv` | One row for each repetition |

## 3. Environment

The experiment uses the official PERIOD Docker image.

| Component | Version |
|---|---|
| Docker image | `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |
| Operating system | Ubuntu 18.04.5 LTS |
| GCC | 7.5.0 |
| Clang | 10.0.0 |
| LLVM | 10.0.0 |
| Python 3 | 3.6.9 |
| NumPy | 1.19.5 |
| PERIOD commit | `b6f72a7b06d01ffa7114b640312873ec2578a5ea` |

The container uses the host Linux kernel. PERIOD’s scheduler uses `SCHED_DEADLINE`, which is present on kernel 4.x and later.

## 4. Reproduction Procedure

Run the commands in Ubuntu or in Ubuntu on WSL2. Docker Engine newer than 18.09.7 is required, with permission to start a privileged container. The full 36-program suite takes about one to two days. Small programs finish in seconds. `CB.pbzip2` takes about one hour per repetition. A 10,000-schedule RADBench run takes about four and a half hours.

### Step 1. Clone the Repository

```bash
git clone https://github.com/Liuyuxuan218/PERIOD-reproduction.git
cd PERIOD-reproduction
export REPO="$(pwd)"
```

### Step 2. Download the PERIOD Image

```bash
docker pull wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
```

Confirm that the host kernel provides `SCHED_DEADLINE`:

```bash
docker run --rm --privileged wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  chrt -m | grep SCHED_DEADLINE
```

### Step 3. Prepare the Result Directory

```bash
export SCT_DATA="${HOME}/sctbench-data"
mkdir -p "${SCT_DATA}/sctbench/scripts"
cp "${REPO}/SCTBench/manifest.json" "${SCT_DATA}/sctbench/manifest.json"
cp "${REPO}/SCTBench/scripts/run_sctbench.py" "${SCT_DATA}/sctbench/scripts/run_sctbench.py"
```

### Step 4. Start the Container

```bash
docker run -d --privileged --name period-sctbench \
  --mount "type=bind,source=${SCT_DATA},target=/experiment-data" \
  wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  sleep infinity
```

The PERIOD checkout inside the container is:

```bash
docker exec period-sctbench git -C /workdir/PERIOD rev-parse HEAD
```

The printed commit is `b6f72a7b06d01ffa7114b640312873ec2578a5ea`.

### Step 5. Run the Pilot

The pilot builds `CS.account_bad` and explores 4 schedules.

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/scripts/run_sctbench.py \
  /experiment-data/sctbench/manifest.json --pilot
```

A successful pilot writes `schedules_explored` equal to 4 in `${SCT_DATA}/sctbench/pilot/result.json`.

### Step 6. Run the SCTBench Suite

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/scripts/run_sctbench.py \
  /experiment-data/sctbench/manifest.json --suite
```

The same command continues a suite that was already started. Completed repetitions remain in `${SCT_DATA}/sctbench/cases/`.

Progress is written to:

```bash
cat "${SCT_DATA}/sctbench/status.md"
```

### Step 7. Build the Result Tables

```bash
python3 "${REPO}/SCTBench/scripts/analyze.py" "${SCT_DATA}/sctbench/cases"
```

The script writes `SCTBench/results/summary.csv` and `SCTBench/results/per_run.csv`.

Each repetition records:

| Field | Meaning |
|---|---|
| `schedules_explored` | Schedules that ran |
| `error_interleavings` | Total Error Interleavings reported by PERIOD |
| `first_bug_schedule` | Schedule number of the first recorded bug |
| `timeout_interleavings` | Schedules that reached the per-schedule time limit |
| `elapsed_sec` | Wall-clock time of that repetition |

For the deadlock programs, the timeout count is the buggy-schedule result. `CS.deadlock01_bad` explored 14 schedules and recorded 6 timeouts. `CS.carter01_bad` explored 42 schedules and recorded 10 or 11 timeouts.

## 5. Results

The values below are mean ± sample standard deviation across the repetitions stored in `measurements/`. A standard deviation of 0 is shown as a single number.

| Program | Repetitions | Schedules | Error interleavings | First bug | Timeouts |
|---|---:|---:|---:|---:|---:|
| CS.bluetooth_driver_bad | 3 | 205 | 6.7 ± 0.6 | 9 | 0 |
| CS.carter01_bad | 3 | 42 | 0 |  | 10.3 ± 0.6 |
| CS.circular_buffer_bad | 3 | 544.7 ± 2.3 | 57.3 ± 2.1 | 16.7 ± 0.6 | 0 |
| CS.deadlock01_bad | 3 | 14 | 0 |  | 6 |
| CS.lazy01_bad | 3 | 39 | 12 | 8 | 0 |
| CS.queue_bad | 1 | 1048 | 114 | 4 | 0 |
| CS.reorder_10_bad | 3 | 2350 | 90.0 ± 2.0 | 27 | 0 |
| CS.reorder_20_bad | 3 | 10000 | 2848.7 ± 30.9 | 39 | 12.3 ± 6.1 |
| CS.reorder_3_bad | 3 | 27 | 6 | 6 | 0 |
| CS.reorder_4_bad | 3 | 100 | 12 | 9 | 0 |
| CS.reorder_5_bad | 3 | 225 | 20 | 12 | 0 |
| CS.stack_bad | 3 | 918 | 117.7 ± 32.3 | 5.7 ± 1.5 | 0 |
| CS.token_ring_bad | 3 | 232 | 53.3 ± 1.5 | 2.3 ± 0.6 | 0 |
| CS.twostage_100_bad | 2 | 100000 | 124.5 ± 0.7 | 984.5 ± 416.5 | 15.5 ± 3.5 |
| CS.twostage_bad | 3 | 33 | 2 | 4 | 0 |
| CS.wronglock_3_bad | 3 | 172 | 42.3 ± 0.6 | 6 | 0 |
| CS.wronglock_bad | 3 | 1464 | 217.7 ± 2.1 | 10 | 0 |
| CB.aget-bug | 3 | 3945 | 702.7 ± 11.6 | 9 | 0.3 ± 0.6 |
| CB.stringbuffer | 3 | 163 | 4 | 121 | 0 |
| CB.pbzip2 | 3 | 1609.3 ± 200.4 | 104.0 ± 8.9 | 47.7 ± 5.9 | 0 |
| Chess.WSQ | 3 | 320.3 ± 23.1 | 15 | 95.3 ± 5.8 | 0 |
| Chess.IWSQ | 3 | 684.0 ± 25.2 | 16.3 ± 0.6 | 120.7 ± 3.1 | 0 |
| Chess.SWSQ | 3 | 10001 | 33.0 ± 1.0 | 1090.0 ± 892.7 | 1.0 ± 1.0 |
| Chess.IWSQWS | 3 | 10001 | 34.3 ± 0.6 | 2004.3 ± 506.8 | 0.3 ± 0.6 |
| Inspect.qsort_mt | 3 | 10001 | 138.7 ± 2.3 | 27 | 0 |
| Inspect.boundedbuffer | 3 | 10001 | 714.3 ± 28.4 | 13.7 ± 4.5 | 0.3 ± 0.6 |
| Misc.safestack | 3 | 135 | 0 |  | 0 |
| Splash2.barnes | 2 | 10001 | 1365.0 ± 149.9 | 2 | 1 |
| Splash2.fft | 2 | 10001 | 3850.5 ± 16.3 | 2 | 0.5 ± 0.7 |
| Splash2.lu | 3 | 10001 | 4740.3 ± 384.7 | 2 | 0.3 ± 0.6 |
| RADBench.bug2 | 3 | 8476.7 ± 141.4 | 8.7 ± 0.6 | 2472 | 0 |
| RADBench.bug3 | 2 | 10001.5 ± 0.7 | 3811.0 ± 1.4 | 31.5 ± 2.1 | 1 |
| RADBench.bug5 | 3 | 10001.3 ± 0.6 | 0 |  | 2.7 ± 0.6 |
| RADBench.bug6 | 3 | 3131.7 ± 12.4 | 0 |  | 330.0 ± 11.5 |

`CS.reorder_3_bad` matches Table 2 on all three PERIOD figures: the first bug is at schedule 6, 27 schedules are explored, and 6 of them are errors. `CS.reorder_4_bad`, `CS.reorder_5_bad`, `CS.reorder_10_bad`, `CS.lazy01_bad`, `CS.twostage_bad`, and `CS.wronglock_bad` likewise match the published schedule total. `RADBench.bug5` reaches the 10,000-schedule budget with no AddressSanitizer error, which is the same outcome the paper reports for that program.
