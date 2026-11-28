# PERIOD Reproduction

This repository records our weekly work on setting up, understanding, and reproducing PERIOD.

## Weekly Progress

### Week 1 – Environment Setup and CVE Reproduction

- Set up the PERIOD development environment and configured the required LLVM/Clang toolchain.
- Built and tested PERIOD's static analysis components.
- Ran initial tests on Double Free and other concurrency-related benchmarks.
- Set up a separate Docker environment using the official PERIOD image to ensure a consistent reproduction environment.
- Reproduced CVE-2016-7911 using PERIOD with a bug depth of 3.
- Identified 8 error interleavings among 19 tested interleavings.
- Replayed all 8 generated schedules and confirmed the SEGV errors using AddressSanitizer.
- Organized the benchmark source code, schedules, logs, and reproduction scripts.

Additionally, a separate reproduction attempt was conducted using WSL2 (preserved in the archive).

Contributors: 1240033600 赵士锦, 1240016737 刘语萱.

### Week 2 – SCTBench Reproduction

- This experiment reproduces the 36 SCTBench programs in Table 2. The programs belong to seven groups: CS (18), CB (3), Chess (4), Inspect (2), Misc (1), Splash2 (3), and RADBench (5). The target was three repetitions per program.
- The runs used the official image `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`, which provides Ubuntu 18.04.5, GCC 7.5.0, Clang/LLVM 10.0.0, Python 3.6.9, and PERIOD commit `b6f72a7`. The search used bug depth 3 and a schedule budget of 10,000, or 100,000 for `CS.twostage_100_bad`. The host was an Intel Core i7-13650HX under WSL2.
- The submitted measurements contain 105 valid repetitions. `CS.account_bad`, `CS.queue_bad`, `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` now have three valid repetitions; the repetitions that were missing from the first submission were recovered from the local experiment tree with their scheduler logs. `RADBench.bug4` still has no valid run. Its three attempts stop during PERIOD's 5-second dry run, before any schedule is explored, so they are not recorded as a failure to find a bug.
- The CS group contains 18 programs from `evaluation/CS`, with 2 to 100 threads. Table 2 labels most of them AF and two of them DL, at published depths of 1 or 2. `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` match Table 2. `CS.deadlock01_bad` matches the published total of 14 schedules and records 6 timeouts with 0 errors.
- The CB group contains aget, stringbuffer, and pbzip2 from `evaluation/CB`. Table 2 labels aget and stringbuffer AF, and lists BOF, NPD, and UAF rows for pbzip2. `CB.stringbuffer` matches the published total of 163 schedules. `CB.pbzip2` recorded 104 ± 8.9 error interleavings.
- The Chess group contains four 3-thread work-stealing queues from `evaluation/Chess`. Table 2 labels WSQ and IWSQ AF at depth 3, and lists both BOF and AF for SWSQ and IWSQWS, whose schedule column is marked L. `Chess.WSQ` matches the published count of 15 error interleavings. `Chess.SWSQ` and `Chess.IWSQWS` recorded 10,001 schedules.
- The Inspect group contains `qsort_mt` (3 threads) and `boundedBuffer` (4 threads) from `evaluation/Inspect_benchmarks`. Table 2 labels both AF at depth 2. `Inspect.qsort_mt` found the first bug at schedule 27, matching Table 2. Both programs recorded 10,001 schedules.
- The Misc group contains SafeStack, a 3-thread program from `evaluation/SafeStack`. Table 2 labels it AF, marks the bug depth as not applicable, and reports no bug across 6,519 schedules. These runs recorded 0 errors in 135 schedules.
- The Splash2 group contains barnes, fft, and lu from `evaluation/Splash2`. Each program has 2 threads and is labeled AF at depth 1. Table 2 marks the schedule column L for barnes and fft, and lists 6,129 schedules for lu. The first bug occurred at schedule 2 for all three programs. The runs recorded 10,001 schedules.
- The RADBench group contains five 2-thread programs from `evaluation/RADBench`. Table 2 labels bug2 through bug4 AF and bug5 and bug6 DL. It marks the schedule column L for bug2 through bug5, and lists 2,950 schedules for bug6. `RADBench.bug5` recorded 0 errors. `RADBench.bug6` recorded 330 ± 11.5 timeouts, compared with 340 buggy schedules in Table 2.

Contributor: 1240019547 邱洋.

- [CS](SCTBench%20reproduction/CS/README.md)
- [CB](SCTBench%20reproduction/CB/README.md)
- [Chess](SCTBench%20reproduction/Chess/README.md)
- [Inspect](SCTBench%20reproduction/Inspect/README.md)
- [Misc](SCTBench%20reproduction/Misc/README.md)
- [Splash2](SCTBench%20reproduction/Splash2/README.md)
- [RADBench](SCTBench%20reproduction/RADBench/README.md)

### Week 4 – PERIOD Workload Extension and Robustness Evaluation

- Investigated the robustness of PERIOD under different workload structures. The goal was to understand how controlled workload perturbations affect Key Points and DKPS-related schedule exploration, bug-discovery behavior, and exploration cost, including first-error discovery round, failing schedules, and runtime.
- Designed and evaluated three complementary workload extensions on 10 official CVE concurrency benchmarks:
  - **Shared Mutex + Counter Workload:** added a process-wide mutex protecting a shared counter, introducing shared writes and synchronization contention.
  - **Thread-local Mutex Workload:** added mutex creation and lock/unlock operations local to each worker, without sharing the added mutex across threads.
  - **Shared Read-only Memory-access Workload:** initialized a shared table before worker creation and added worker-side read-only accesses, without worker-side writes or an additional mutex. The read source site was manually added to ConConfig as a scheduling point.
- Used the same experiment matrix for each workload: workload levels `N = {0, 1, 2, 3, 4, 8}`, three repetitions per CVE and level (180 planned runs per workload), PERIOD depth bound 4, schedule budget 60, and a 5-second per-execution timeout. Runs used the pinned official image `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`.
- Collected and analyzed initial Key Point counts, first-error discovery rounds, failing schedules, search runtime, and run-completion status. The archived datasets contain 178/180 valid runs for Shared Mutex + Counter, 166/180 for Thread-local Mutex, and 175/180 for Shared Read-only Memory.
- Compared workload levels using benchmark-balanced summaries and matched N=0 versus N=8 runs. Across the three studies, the recorded Key Point count increased from N=0 to N=8, while the mean number of failing schedules did not increase. Search runtime also increased:

  | Workload | Key Points (N=0 → N=8) | First-error round* (N=0 → N=8) | Failing schedules (N=0 → N=8) | Runtime (N=0 → N=8) |
  |---|---:|---:|---:|---:|
  | Shared Mutex + Counter | 11.60 → 27.60 | 5.40 → 11.59 | 7.87 → 6.13 | 2.48s → 2.90s |
  | Thread-local Mutex | 11.60 → 21.60 | 5.37 → 9.56 | 7.87 → 6.60 | 2.51s → 3.18s |
  | Shared Read-only Memory | 13.60 → 19.60 | 9.70 → 9.80 | 8.10 → 7.40 | 3.02s → 4.06s |

  *First-error means include only benchmark groups with an observed first error; denominators can differ across workload levels. Failing schedules count error-triggering schedules/interleavings, not distinct bugs. Incomplete runs are retained and are not treated as zero.
- The results suggest that increasing workload or the recorded Key Point structure does not automatically improve bug-discovery effectiveness. The observed effects vary by benchmark and workload type, and greater workload can increase search cost without increasing the number of failing schedules. The shared read-only experiment is specifically a memory-access workload with a manually added scheduling point; it should not be interpreted as automatic SVF discovery of additional static Key Points.
- Organized the experiment configurations, run-level CSVs, per-CVE summaries, figures, plotting/retry scripts, and methodology in [PERIOD-workload-extension](PERIOD-workload-extension/README.md).

Contributor: 1240016737 刘语萱.

## Table 1 IPB and PCT columns

The IPB and PCT columns are being measured in an Ubuntu 14.04 guest with kernel 3.13.0-170 and Pin 2.12. Finished programs in this submission: `CVE-2009-3547`, `CVE-2011-2183`, `CVE-2013-1792`. Each has ten IPB campaigns and ten PCT campaigns. The other programs are still running and are not included yet.

Contributor: 1240019547 邱洋.

- [IPB](Table%201%20baseline%20reproduction/IPB/README.md)
- [PCT](Table%201%20baseline%20reproduction/PCT/README.md)
