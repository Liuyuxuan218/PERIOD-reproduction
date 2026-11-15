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

- Reproduced the 36 SCTBench programs in Table 2 with PERIOD. The programs are in seven groups: CS (18), CB (3), Chess (4), Inspect (2), Misc (1), Splash2 (3), and RADBench (5). The target was three repetitions per program.
- The submitted metrics contain 97 valid repetitions. Thirty programs have three. `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two. `CS.queue_bad` has one. `CS.account_bad` and `RADBench.bug4` have none. `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` match Table 2 on schedules, error interleavings, and first-bug schedule.
- Used the official image `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` (Ubuntu 18.04.5, GCC 7.5.0, Clang/LLVM 10.0.0, Python 3.6.9, PERIOD commit `b6f72a7`) in a privileged container. Bug depth was 3. The schedule budget was 10,000, and 100,000 for `CS.twostage_100_bad`. The host was an Intel Core i7-13650HX under WSL2.
- CS: 16 of 18 programs have three repetitions. `CS.reorder_3_bad` recorded 27 schedules, 6 error interleavings, and the first bug at schedule 6 on every repetition. `CS.account_bad` has no completed run and `CS.queue_bad` has one. `CS.deadlock01_bad` recorded 14 schedules, 0 errors, and 6 timeouts; the timeouts are not confirmed deadlocks.
- CB: all 3 programs have three repetitions. `CB.stringbuffer` matches Table 2's 163 schedules. `CB.pbzip2` used a 15-second per-schedule timeout and recorded 1609.3 ± 200.4 schedules, against Table 2's 1626.
- Chess: all 4 programs have three repetitions. `Chess.WSQ` matches Table 2's 15 error interleavings. `Chess.SWSQ` and `Chess.IWSQWS` recorded 10001 schedules, above the configured budget of 10,000.
- Inspect: both programs have three repetitions and recorded 10001 schedules. `Inspect.qsort_mt` found the first bug at schedule 27, matching Table 2; Table 2 lists 8643 schedules.
- Misc: `Misc.safestack` has three repetitions, 135 schedules, and 0 error interleavings. Table 2 lists 6519 schedules and no bug.
- Splash2: `Splash2.lu` has three repetitions; `Splash2.barnes` and `Splash2.fft` have two. All three recorded 10001 schedules, and the recorded first bug is schedule 2, matching Table 2.
- RADBench: `RADBench.bug2`, `RADBench.bug5`, and `RADBench.bug6` have three repetitions; `RADBench.bug3` has two; `RADBench.bug4` has none. `RADBench.bug5` recorded 0 errors, matching Table 2's no-bug result. `RADBench.bug6` recorded 0 errors and 330 ± 11.5 timeouts; Table 2 lists 340 buggy schedules.

Contributor: 1240019547 邱洋.

- [CS](SCTBench%20reproduction/CS/README.md)
- [CB](SCTBench%20reproduction/CB/README.md)
- [Chess](SCTBench%20reproduction/Chess/README.md)
- [Inspect](SCTBench%20reproduction/Inspect/README.md)
- [Misc](SCTBench%20reproduction/Misc/README.md)
- [Splash2](SCTBench%20reproduction/Splash2/README.md)
- [RADBench](SCTBench%20reproduction/RADBench/README.md)
