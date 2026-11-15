# `run_PDS.py` flags at `b6f72a7`

Source: `/workdir/PERIOD/tool/DBDS/run_PDS.py` in image `sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`. These are the flags used for the Inspect runs.

## `-d` / `--bugDepth`

Default `bugDepth` is 2. `-d 3` sets `bugDepth = 3` and `period_limit = bugDepth + 1` (4).

The search loop is `for iterPeriod in range(2, period_limit + 1)`. With `-d 3` that is periods 2, 3, and 4. The log line is `bug depth = iterPeriod - 1`, so the bound is bug depths 1, 2, and 3. These runs pass `-d 3`.

## `-f` / `--runs`

`-f` sets `runs_limit`. The default is 0, which means no schedule cap.

Inside the schedule loop the tool increments `rounds`, prints `test NNNN:`, and only then checks `rounds > runs_limit`. On that check it breaks before the program runs. The breaking test line has no schedule after the colon. The footer `Round` total can therefore be larger than the number of executed schedules. A schedule is counted as executed only when the test line contains a schedule (`[`). The footer is stored separately in the metrics file.

The configured schedule budget for every program in this group is 10,000. The command places `-f 10000` before the program name. `Inspect.qsort_mt` also receives `-f` after the program name. That later `-f` is a program argument. Python stops option parsing at the program name, so it is not the schedule cap.

## `-y` / `--skip-enter`

`-y` sets `skipEnter = 1` and skips `input("Press Enter to continue...")`. It does not change the scheduler. These runs pass `-y`.

## `-t` / `--timeout`

Default `subprocessTimeout` is 5 seconds. `-t` replaces that value. It is the limit for one schedule's `process.communicate`, not the whole experiment. On expiry the tool records a timeout interleaving and continues. A timeout is not an error interleaving.

Every program in this group uses that default of 5 seconds. None of the recorded commands passes `-t`.

## Flags not used

`--no-prefix` (`-e`) is not used. `-z` only changes exploration once bug depth is at least 4, so it does not apply to `-d 3`.
