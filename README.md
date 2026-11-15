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

### Week 2 – SCTBench Reproduction

- Reproduced the 36 SCTBench programs in Table 2 with PERIOD, in seven groups: CS (18), CB (3), Chess (4), Inspect (2), Misc (1), Splash2 (3), and RADBench (5).
- Used the official image `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` (Ubuntu 18.04.5 LTS, GCC 7.5.0, Clang/LLVM 10.0.0, Python 3.6.9, PERIOD commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`) in a privileged container so `SCHED_DEADLINE` is available. Every run used bug depth 3 (`-d 3`). The measurement host was an Intel Core i7-13650HX under WSL2.
- Set the configured schedule budget to 10,000 per run, and to 100,000 for `CS.twostage_100_bad`. The target was three repetitions. Those budgets are the caps passed to `-f`. The schedule totals in the group reports are the counts recorded in the metrics.
- The submitted metrics contain 97 valid repetitions. 30 programs have three completed repetitions. `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two. `CS.queue_bad` has one. `CS.account_bad` and `RADBench.bug4` have none.
- On every submitted repetition, 14 programs match a numeric Table 2 schedule total, including `CS.reorder_3_bad`, `CS.reorder_4_bad`, `CS.reorder_5_bad`, `CS.lazy01_bad`, `CS.twostage_bad`, and `CS.wronglock_bad`. `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` also match Table 2 on the error count and the first-bug schedule. `CS.reorder_20_bad` and `CS.twostage_100_bad` recorded exactly the configured budget, which Table 2 marks as L.
- For `CS.reorder_3_bad`, all three repetitions explored 27 schedules and identified 6 error interleavings, with the first bug at schedule 6 (sample standard deviation 0), matching Table 2.
- Timeout interleavings are schedules that hit the per-schedule time limit, 5 seconds, or 15 seconds for `CB.pbzip2`. They are counted separately from error interleavings. `CS.deadlock01_bad` recorded 14 schedules, 0 error interleavings, and 6 timeout interleavings on every repetition (sample standard deviation 0). Those timeouts are not confirmed deadlocks.
- `CS.account_bad` and `RADBench.bug4` have no completed run, and the submitted records do not establish the cause. `CS.queue_bad` has one completed repetition. `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two. `Chess.SWSQ`, `Chess.IWSQWS`, `Inspect.qsort_mt`, `Inspect.boundedbuffer`, `Splash2.barnes`, `Splash2.fft`, `Splash2.lu`, `RADBench.bug3`, and `RADBench.bug5` record a schedule total above the configured budget; that extra count is unresolved. `Misc.safestack` recorded 135 schedules and 0 error interleavings on every repetition (sample standard deviation 0), while Table 2 lists 6519 schedules and no buggy schedule.

Contributor: 1240019547 邱洋.

- [CS](SCTBench%20reproduction/CS/README.md)
- [CB](SCTBench%20reproduction/CB/README.md)
- [Chess](SCTBench%20reproduction/Chess/README.md)
- [Inspect](SCTBench%20reproduction/Inspect/README.md)
- [Misc](SCTBench%20reproduction/Misc/README.md)
- [Splash2](SCTBench%20reproduction/Splash2/README.md)
- [RADBench](SCTBench%20reproduction/RADBench/README.md)
