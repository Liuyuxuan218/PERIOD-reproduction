# PERIOD Workload Extension Studies

## Motivation

PERIOD reduces the cost of controlled concurrency testing by organizing executions into periods and exploring schedules around **Key Points** and **Dynamic Key Point Slices (DKPSs)**. Its schedule generator uses the dynamic key points activated during execution to guide exploration, while feedback from previous executions helps construct schedule prefixes and avoid redundant work. The PERIOD paper also highlights a fundamental challenge: the schedule space can grow rapidly as the number of scheduling points increases. This makes the relationship between a program's execution structure, the explored schedule space, and bug-discovery cost important in practice.

**Our motivation is to evaluate the robustness of PERIOD under different workload structures, and to investigate whether controlled workload perturbations can expand the observed Key Points / DKPS-related scheduling structure without simply introducing unrelated concurrency bugs.** We want to understand not only whether the recorded scheduling structure changes, but also what those changes mean for bug discovery: do they help PERIOD expose bugs earlier, lead to more error-triggering schedules, increase exploration cost, or consume more runtime without improving discovery?

Inspired by PERIOD's instrumentation- and feedback-guided exploration model, we introduce **controlled, artificial workload perturbations** into benchmark programs. Rather than changing the original bug-triggering logic deliberately, we vary additional operations around worker execution and compare the resulting exploration behavior across workload levels. The three studies cover complementary workload structures:

1. **Shared Mutex + Counter Workload** — adds a shared counter protected by a process-wide mutex, introducing shared writes and synchronization contention.
2. **Thread-local Mutex Workload** — adds mutex creation and lock/unlock operations local to each worker, without sharing the added mutex between workers.
3. **Shared Read-only Memory-access Workload** — adds reads from a shared table initialized before worker creation; workers do not write to the table and no additional mutex is introduced. This study also uses a manually added scheduling point for the read site.

These perturbations are deliberately different. They let us compare the effects of shared synchronization, thread-local lock operations, and shared read-only memory access instead of treating all added work as one generic workload. For each experiment, we vary the workload level and examine PERIOD's recorded Key Points, first-error discovery round, failing schedules, search runtime, and run completion status.

The central questions are:

- **Structural response:** How do different workload structures affect the Key Points and the dynamic execution slices (DKPSs) that PERIOD uses to guide schedule exploration?
- **Bug-discovery effectiveness:** Does a larger or different scheduling structure help PERIOD discover existing concurrency bugs earlier or across more schedules, or can discovery become delayed?
- **Exploration cost:** How do workload changes affect search runtime, the number of explored/error-triggering schedules, and the ability to complete within a fixed search budget?
- **Robustness:** Are PERIOD's results stable across workload types and benchmark programs, or are the effects benchmark-dependent?

This is an **evaluation and robustness study**, not a claim that adding more Key Points or DKPS entries must improve bug detection. In particular, more recorded Key Points do not automatically mean more distinct static scheduling locations, more useful DKPSs, or better bug-discovery effectiveness. The current archived result tables report the metrics available in the experiment logs; explicit DKPS cardinality/coverage should be instrumented and reported separately in future experiments if it is not already captured by the runner.

## Relationship to the Original PERIOD Paper

This extension builds on the concepts in Cheng Wen et al., **"Controlled Concurrency Testing via Periodical Scheduling" (ICSE 2022)**. The original work introduces periodical execution, period-bounding, dynamic key point slices, and feedback-guided schedule generation to explore feasible thread interleavings efficiently. Our experiments do not modify or claim to reproduce the paper's original algorithmic contributions. Instead, they use controlled workload perturbations to study how changes in the program's workload and scheduling structure interact with PERIOD's exploration behavior and bug-discovery cost.

Paper: [Controlled Concurrency Testing via Periodical Scheduling (ICSE 2022)](https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf).

---


Three workload-structure experiments evaluating how additional synchronization, thread-local lock lifecycle, and shared read-only memory access affect PERIOD's schedule exploration and bug-discovery behavior.

## Repository structure

```text
PERIOD-workload-extension/
├── README.md
├── scripts/
│   ├── period_all_cve_sweep.py
│   ├── period_threadlocal_ablation.py
│   ├── period_shared_readonly_180.py
│   ├── period_shared_readonly_supplement_retry.py
│   ├── plot_threadlocal_four_figures.py
│   └── plot_workload_figures.py
├── experiments/
│   ├── 01_shared_mutex_counter/
│   ├── 02_thread_local_mutex/
│   └── 03_shared_readonly_memory/
└── docs/
    └── cross_experiment_summary_by_N.csv
```

## Experiment overview

| Experiment | Workload category | Mechanism | Valid runs |
|---|---|---|---:|
| [Shared Mutex + Counter](experiments/01_shared_mutex_counter/README.md) | Synchronization workload | Shared mutex protects shared counter increments | 178/180 |
| [Thread-local Mutex](experiments/02_thread_local_mutex/README.md) | Thread-local synchronization / lock lifecycle | Each worker uses its own local mutex | 166/180 |
| [Shared Read-only Memory](experiments/03_shared_readonly_memory/README.md) | Memory-access workload | Shared table is read-only in worker threads; one read site manually added to ConConfig | 175/180 |

## Common configuration

- Official ConVul-CVE-Benchmarks: 10 CVEs.
- Workload levels: `N = {0, 1, 2, 3, 4, 8}`.
- Repetitions: 3 per CVE and N (180 planned cells per experiment).
- PERIOD search depth bound: `-d 4`.
- Schedule budget: `-f 60`.
- Per-execution timeout: `-t 5` seconds.
- Pinned Docker image: `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`.

## Important interpretation rules

1. `FINISHED_BUDGET_LIMITED` means the search completed under the configured finite budget, not that the schedule space was exhausted.
2. A missing first-error value in a completed run means no error was detected within that run's search budget; it is not zero.
3. `error_schedules` / failing schedules count error-triggering schedules or interleavings, not distinct bugs or CVEs.
4. Incomplete runs remain in the run-level CSV and are not silently converted to zero or dropped from the audit trail.
5. First-error averages are conditional on observed errors; always report detection coverage alongside them.
6. Workload changes can affect instruction count, timing, synchronization and schedule exploration. Do not attribute every change solely to Key Point count.
7. The shared read-only study manually appends a read site to ConConfig. It is not evidence of automatic SVF discovery of additional static Key Points.

## Cross-experiment result summary

| Experiment | N=0 → N=8 Key Points | First-error round* | Failing schedules | Runtime |
|---|---:|---:|---:|---:|
| Shared Mutex | 11.60 → 27.60 | 5.40 → 11.59 | 7.87 → 6.13 | 2.48s → 2.90s |
| Thread-local Mutex | 11.60 → 21.60 | 5.37 → 9.56 | 7.87 → 6.60 | 2.51s → 3.18s |
| Shared Read-only Memory | 13.60 → 19.60 | 9.70 → 9.80 | 8.10 → 7.40 | 3.02s → 4.06s |

*First-error averages are detected-only and can have different denominators at different N. See each experiment README and `docs/cross_experiment_summary_by_N.csv`.

## Reproduction environment

The Python drivers assume:
- WSL2 Ubuntu with Docker Desktop integration.
- The pinned PERIOD Docker image above.
- The PERIOD project layout expected by `period_all_cve_sweep.py`.
- Python 3.10+; the experiment drivers use the Python standard library. Plot regeneration requires `pandas` and `matplotlib`.

Install plotting dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas matplotlib
```

Run the shared mutex sweep (new 10-CVE matrix / baseline logic):

```bash
python3 scripts/period_all_cve_sweep.py plan
python3 scripts/period_all_cve_sweep.py all
```

Run the thread-local mutex ablation:

```bash
python3 scripts/period_threadlocal_ablation.py plan
python3 scripts/period_threadlocal_ablation.py all
```

Run the shared read-only memory workload:

```bash
python3 scripts/period_shared_readonly_180.py plan
python3 scripts/period_shared_readonly_180.py all
```

Retry only incomplete shared-read-only cells:

```bash
python3 scripts/period_shared_readonly_supplement_retry.py --dry-run
python3 scripts/period_shared_readonly_supplement_retry.py --max-attempts 2
```

Regenerate four figures from a run-level CSV:

```bash
python3 scripts/plot_workload_figures.py path/to/runs.csv --out path/to/figures --prefix experiment
```

## Data provenance

Run-level CSVs and group summaries are copied from the recorded experiment outputs available at packaging time. No synthetic run rows were generated. Derived summaries and plots are generated from those CSVs by the included plotting/analysis workflow.

Raw per-schedule traces, ASan logs, compiled binaries, and build directories are not included in this lightweight research package. They remain in the original WSL experiment output directories if retained locally.

## Citation / upstream project

PERIOD reproduction project: https://github.com/Liuyuxuan218/PERIOD-reproduction
