# Reproduction procedure

This file preserves the commands used to run the SCTBench suite and to copy finished records into the seven group directories. The measurements, completion counts, and Table 2 comparison are in [../README.md](../README.md).

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

Each repetition is written under `${SCT_DATA}/sctbench/cases/<program>/repNN/`. A repetition whose `metrics.json` already contains `"valid": true` is not run again. The same command therefore continues a suite that was already started. The runner rewrites `${SCT_DATA}/sctbench/status.md` after each program. The copy of that snapshot submitted with these measurements is [`results/status.md`](../results/status.md). Its explored column is the last attempt, not the mean.

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

- [`results/summary.csv`](../results/summary.csv) and [`results/summary.json`](../results/summary.json), one row per program
- [`results/per_run.csv`](../results/per_run.csv) and [`results/per_run.json`](../results/per_run.json), one row per repetition

`metrics_path` in the per-run files is the path relative to `SCTBench reproduction/`. The mean is the arithmetic mean. The standard deviation is the sample standard deviation. Programs with one valid repetition store 0.0 in the CSV standard-deviation columns because that is the existing one-observation placeholder in `analyze.py`. That placeholder is not a sample standard deviation. The group tables print the single measured value and say the sample standard deviation is unavailable.

Passing the external cases directory, `python3 analyze.py "${SCT_DATA}/sctbench/cases"`, aggregates that live tree in place and writes the same combined files. It does not copy files into the group directories. The tables committed here were produced from the seven group directories after collection, so the submitted numbers have one source.
