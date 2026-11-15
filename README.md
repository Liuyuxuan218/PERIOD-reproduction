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

- Reproduced PERIOD on the 36 SCTBench programs in Table 2: CS (18), CB (3), Chess (4), Inspect (2), Misc (1), Splash2 (3), and RADBench (5). Three repetitions were the target.
- `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` match Table 2 on schedules, error interleavings, and first-bug schedule. A matching schedule total can still come with a different error count. Where Table 2 labels a program DL, these runs record timeouts beside 0 error interleavings. Schedule totals recorded above the 10,000 budget are kept as measured.
- Runs used `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` (Ubuntu 18.04.5, GCC 7.5.0, Clang/LLVM 10.0.0, Python 3.6.9, commit `b6f72a7`), bug depth 3, and a 10,000-schedule budget, or 100,000 for `CS.twostage_100_bad`, on an i7-13650HX under WSL2.
- CS: the small reorder programs reproduce Table 2 exactly. `CS.reorder_3_bad` is 27 schedules, 6 errors, and the first bug at schedule 6. `CS.deadlock01_bad` matches the 14 schedules and records 6 timeouts with 0 errors, against Table 2's 6 buggy schedules.
- CB: `CB.stringbuffer` matches the published 163 schedules, with 4 errors and the first bug at 121 against Table 2's 16 and 12. `CB.pbzip2` uses a 15-second timeout. Table 2 splits it into BOF, NPD, and UAF rows; the measured error count is the one combined total, 104 ± 8.9.
- Chess: `Chess.WSQ` matches Table 2's 15 error interleavings, with 320.3 ± 23.1 schedules against 434. `Chess.SWSQ` and `Chess.IWSQWS` are the cases Table 2 marks L; both recorded 10001 schedules, and each has two published bug rows, which are not averaged.
- Inspect: both programs recorded 10001 schedules. `Inspect.qsort_mt` places the first bug at schedule 27, matching Table 2, whose schedule total is 8643. `Inspect.boundedbuffer` is marked L and recorded 714.3 ± 28.4 errors against 1514.
- Misc: Table 2 marks `Misc.safestack` as no bug found. These runs also recorded 0 errors, in 135 schedules. Table 2 lists 6519 schedules.
- Splash2: barnes, fft, and lu all place the first bug at schedule 2, matching Table 2, and then record 10001 schedules. For `Splash2.lu`, Table 2 lists 6129 schedules and 2848 buggy schedules; these runs recorded 4740.3 ± 384.7 errors.
- RADBench: `RADBench.bug5` matches Table 2's no-bug result, with 0 errors at the schedule cap. `RADBench.bug6`, labeled DL, recorded 0 errors and 330 ± 11.5 timeouts against Table 2's 340 buggy schedules. `RADBench.bug2` stopped before the budget, with the first bug at 2472 against 1985, while Table 2 marks that schedule cell L.

Contributor: 1240019547 邱洋.

- [CS](SCTBench%20reproduction/CS/README.md)
- [CB](SCTBench%20reproduction/CB/README.md)
- [Chess](SCTBench%20reproduction/Chess/README.md)
- [Inspect](SCTBench%20reproduction/Inspect/README.md)
- [Misc](SCTBench%20reproduction/Misc/README.md)
- [Splash2](SCTBench%20reproduction/Splash2/README.md)
- [RADBench](SCTBench%20reproduction/RADBench/README.md)
