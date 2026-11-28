# Experimental Methodology and Metric Definitions

## Shared experimental matrix
Each experiment targets the same 10 official ConVul-CVE-Benchmarks CVEs, six workload levels N={0,1,2,3,4,8}, and three repetitions per CVE/N cell (180 planned runs). The configured PERIOD bounds are depth 4, schedule budget 60, and per-execution timeout 5 seconds, using a pinned Docker image.

## Workload categories
- Shared Mutex + Counter: shared-state synchronization; a process-wide mutex serializes increments to a shared counter.
- Thread-local Mutex: per-worker lock lifecycle; each worker creates and uses a mutex that is not shared with other workers.
- Shared Read-only Memory: shared memory access; the table is initialized before worker creation and worker threads only read it. The read site is manually added to ConConfig.

## Metrics
- Initial Key Points: the initial KP count parsed from PERIOD logs for a run.
- First Error Round: first schedule/search round at which an error is reported. Missing means no error was recorded within the run's configured search budget; it is not zero.
- Failing Schedules: number of error-triggering schedules/interleavings reported by the runner. This is not the number of distinct bugs.
- Search Runtime: wall-clock search time recorded for that run.

## Aggregation
For overall N-level plots, repetitions are first averaged within each CVE and N, then CVE-level means are averaged equally across the benchmarks with available data. First-error averages are calculated only from CVE groups with observed first-error values. Detection coverage is therefore reported separately.

Paired N=0 vs N=8 analyses match by benchmark and repetition and include only pairs where both metric values exist. Pair counts differ by metric.

## Status handling
Only FINISHED_BUDGET_LIMITED runs contribute to completed-run metrics. Other statuses remain visible in the run-level CSV and are not silently treated as zeros. FINISHED_BUDGET_LIMITED is a finite-budget completion, not exhaustive search of all schedules.

## Reproducibility and interpretation
The shared read-only experiment manually appends its helper read source line to ConConfig after static analysis. It should not be described as automatic SVF discovery or as creating multiple distinct static source sites. Workload changes may alter timing and execution paths; observed associations do not alone prove a single causal mechanism.
