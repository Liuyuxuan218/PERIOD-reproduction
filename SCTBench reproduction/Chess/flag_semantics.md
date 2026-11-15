# `run_PDS.py` flags at `b6f72a7`

Source: `/workdir/PERIOD/tool/DBDS/run_PDS.py` in image `sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`. The file hash matches that commit. These notes are from that source, before the SCTBench runs.

## `-d` / `--bugDepth`

Default `bugDepth` is 2. `-d 3` sets `bugDepth = 3` and `period_limit = bugDepth + 1` (4).

The search loop is `for iterPeriod in range(2, period_limit + 1)`. With `-d 3` that is periods 2, 3, and 4. The log line is `bug depth = iterPeriod - 1`, so the bound is bug depths 1, 2, and 3. That is the Table 2 bound.

A run that omits `-d` stops after bug depth 2. That is a different search from Table 2. It is not, by itself, evidence about why a finished CVE log is smaller than Table 1: those logs print `End Testing` after the depth loop finishes.

## `-f` / `--runs`

`-f` sets `runs_limit`. The default is 0, which means no schedule cap.

Inside the schedule loop the tool increments `rounds`, prints `test NNNN:`, and only then checks `rounds > runs_limit`. On that check it breaks before `print(inter)` and before the program runs. So the number of executed schedules is `runs_limit` when the space is larger than the cap. The breaking test line has no schedule after the colon.

`reach_runs_limit` is tested after the depth's `while True`, and that `break` leaves the depth loop. Later iterations of the same `while` can increment `rounds` again, but they hit the same check before execution. The footer `Round` total can therefore be larger than the number of executed schedules. SCTBench counts a schedule as executed only when the test line contains a schedule (`[`). The footer is stored separately.

Pilot on `CS.account_bad` with `-f 4`, after a successful `./build.sh`, executed 4 schedules, printed one bare `test 0005:` line, and reported footer `Round` total 5. Exit status was 0 and the log contained `End Testing`. The executed count is the Table 2 schedule count. The footer is not used when the two differ.

Table 2 uses 10,000 schedules, and 100,000 for `CS.twostage_100_bad`. The command is `-f 10000` or `-f 100000`, placed before the benchmark argv. A later `-f` that belongs to the benchmark (pbzip2, qsort_mt) stays after the program name. Python `getopt` stops at the first non-option, so that second `-f` is not the schedule cap.

## `-y` / `--skip-enter`

`-y` sets `skipEnter = 1` and skips `input("Press Enter to continue...")`. It does not change the scheduler. The doubleFree log in this repository used `-y -d 3`.

## `-t` / `--timeout`

Default `subprocessTimeout` is 5 seconds. `-t` replaces that value. It is the limit for one schedule's `process.communicate`, not the whole experiment. On expiry the tool records a timeout interleaving and continues. A timeout is not an error interleaving.

`CB.pbzip2` keeps the artifact's `-t 15` because that README sets it for this compression command. Every other Table 2 command uses the tool default of 5 seconds.

## What is not changed

`--no-prefix` (`-e`) skips prefix-guided stage 2. It is not used for the Table 2 repetitions. `-z` only changes exploration once bug depth is at least 4, so it does not apply to `-d 3`.
