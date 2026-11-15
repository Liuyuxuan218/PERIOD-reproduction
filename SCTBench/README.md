# SCTBench reproduction (Table 2)

Contributor: 1240019547 邱洋.

This directory records our PERIOD runs for the SCTBench programs in Table 2 of Wen et al., “Controlled Concurrency Testing via Periodical Scheduling,” ICSE 2022.

- Paper: https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf
- Tool: https://github.com/wcventure/PERIOD
- Image: `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`
- Tool commit inside that image: `b6f72a7b06d01ffa7114b640312873ec2578a5ea`

The image provides Ubuntu 18.04.5, GCC 7.5.0, Clang/LLVM 10.0.0, and Python 3.6.9. `run_PDS.py` uses that Python 3 and NumPy 1.19.5. The upstream `build.sh` scripts use Python 2 wllvm. The container uses the host kernel, which needs `SCHED_DEADLINE`.

## What we ran

Each program was built with the script in the image and searched with:

```text
python3 /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 -f <limit> [program arguments]
```

`-d 3` covers bug depths 1, 2, and 3. The schedule budget is 10,000, and 100,000 for `CS.twostage_100_bad`. `-y` continues past the Enter prompt. `CB.pbzip2` uses a 15-second limit on each schedule, from that program’s upstream README. The other programs use the tool default of 5 seconds per schedule.

We ran three repetitions and recorded schedules explored, error interleavings, the schedule of the first recorded bug, timeout interleavings, and elapsed time. The per-run files are under `measurements/`. `results/summary.csv` is the aggregate, with mean and sample standard deviation. `paper_table2.json` is the PERIOD column of Table 2, including the markers `L` (budget reached) and `%` (no bug found in the paper).

On this machine the small programs finished in seconds. `CB.pbzip2` took about 50–60 minutes per repetition. A 10,000-schedule RADBench run took about 4 hours 20 minutes. One 100,000-schedule run of `CS.twostage_100_bad` took long enough that a full three-repetition pass of all 36 programs occupies one to two days.

## Clone and run on another machine

Use Ubuntu or Ubuntu on WSL2, with Docker Engine newer than 18.09.7 and permission to start a privileged container. Keep the commands in that Linux shell. Allow at least 20 GB of disk and network access for the image pull and the RADBench downloads.

```bash
git clone https://github.com/Liuyuxuan218/PERIOD-reproduction.git
cd PERIOD-reproduction
export REPO="$(pwd)"

docker pull wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc

docker run --rm --privileged wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  chrt -m | grep SCHED_DEADLINE
```

`SCHED_DEADLINE` in that output means the host kernel can run PERIOD.

```bash
export SCT_DATA="${HOME}/sctbench-data"
mkdir -p "${SCT_DATA}/sctbench/scripts"
cp "${REPO}/SCTBench/manifest.json" "${SCT_DATA}/sctbench/manifest.json"
cp "${REPO}/SCTBench/scripts/run_sctbench.py" "${SCT_DATA}/sctbench/scripts/run_sctbench.py"

docker rm -f period-sctbench >/dev/null 2>&1 || true
docker run -d --privileged --name period-sctbench \
  --mount "type=bind,source=${SCT_DATA},target=/experiment-data" \
  wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  sleep infinity

docker exec period-sctbench git -C /workdir/PERIOD rev-parse HEAD
```

The commit printed there is `b6f72a7b06d01ffa7114b640312873ec2578a5ea`. The runner checks that value before the suite.

Confirm the tool with the four-schedule pilot. A working setup reports `schedules_explored` equal to 4 in `${SCT_DATA}/sctbench/pilot/result.json`.

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/scripts/run_sctbench.py \
  /experiment-data/sctbench/manifest.json --pilot
```

Then run the 36 programs for three repetitions. The programs run one after another.

```bash
docker exec period-sctbench python3 /experiment-data/sctbench/scripts/run_sctbench.py \
  /experiment-data/sctbench/manifest.json --suite
```

Running that command again continues from the repetitions already stored. Finished repetitions stay in place. Watch progress with:

```bash
cat "${SCT_DATA}/sctbench/status.md"
```

When the suite command returns, build the tables from the clone:

```bash
python3 "${REPO}/SCTBench/scripts/analyze.py" "${SCT_DATA}/sctbench/cases"
```

That writes `SCTBench/results/summary.csv` and `SCTBench/results/per_run.csv`.

## Output of a run

| Path under `${SCT_DATA}/sctbench` | Contents |
|---|---|
| `status.md` | Valid repetitions, schedules, errors, first bug, timeouts |
| `cases/<program>/build.log` | Build of that program |
| `cases/<program>/rep01/metrics.json` | Parsed repetition |
| `cases/<program>/rep01/run.log` | Scheduler log |
| `cases/<program>/replay_rep01.log` | AddressSanitizer replay of one saved bug |

`schedules_explored` is the Table 2 schedule count. `error_interleavings` is the tool’s “Total Error Interleavings”. `first_bug_schedule` is the schedule of the first recorded bug. `timeout_interleavings` counts schedules that hit the per-schedule time limit. For the deadlock programs in Table 2, that timeout count is the buggy-schedule figure: `CS.deadlock01_bad` recorded 6 timeouts in 14 schedules, and `CS.carter01_bad` recorded 10 or 11 timeouts in 42 schedules.

Our measured files in this directory are under `measurements/`, with the same `metrics.json` layout. `manifest.json` lists every program’s upstream directory, build command, arguments, thread count, and schedule limit.
