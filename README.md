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
- Runs used `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` (Ubuntu 18.04.5, GCC 7.5.0, Clang/LLVM 10.0.0, Python 3.6.9, commit `b6f72a7`), bug depth 3, and a 10,000-schedule budget, or 100,000 for `CS.twostage_100_bad`, on an i7-13650HX under WSL2.
- CS: 18 programs from `evaluation/CS`, 2–100 threads. Table 2 labels most AF and two DL, at published depths 1 or 2. `CS.reorder_3_bad`, `CS.reorder_4_bad`, and `CS.reorder_5_bad` match Table 2. `CS.deadlock01_bad` matches 14 schedules, with 6 timeouts and 0 errors.
- CB: aget, stringbuffer, and pbzip2 from `evaluation/CB`. aget and stringbuffer are AF; pbzip2 has BOF, NPD, and UAF rows. `CB.stringbuffer` matches the published 163 schedules. `CB.pbzip2` recorded 104 ± 8.9 errors.
- Chess: four 3-thread work-stealing queues from `evaluation/Chess`. WSQ and IWSQ are AF at depth 3. SWSQ and IWSQWS each have BOF and AF, and Table 2 marks their schedules L. `Chess.WSQ` matches 15 errors. `Chess.SWSQ` and `Chess.IWSQWS` recorded 10001 schedules.
- Inspect: `qsort_mt` (3 threads) and `boundedBuffer` (4 threads) from `evaluation/Inspect_benchmarks`, both AF at depth 2. `Inspect.qsort_mt` found the first bug at schedule 27, matching Table 2. Both recorded 10001 schedules.
- Misc: SafeStack, 3 threads, from `evaluation/SafeStack`. Table 2 labels it AF, marks the depth not applicable, and records no bug over 6519 schedules. These runs recorded 0 errors in 135 schedules.
- Splash2: barnes, fft, and lu from `evaluation/Splash2`, each 2 threads, AF, depth 1. Table 2 marks barnes and fft L and lists 6129 schedules for lu. The first bug is at schedule 2 for all three. The runs recorded 10001 schedules.
- RADBench: five 2-thread programs from `evaluation/RADBench`. bug2–bug4 are AF; bug5 and bug6 are DL. Table 2 marks bug2–bug5 L and lists 2950 schedules for bug6. `RADBench.bug5` recorded 0 errors. `RADBench.bug6` recorded 330 ± 11.5 timeouts against 340 buggy schedules.

Contributor: 1240019547 邱洋.

- [CS](SCTBench%20reproduction/CS/README.md)
- [CB](SCTBench%20reproduction/CB/README.md)
- [Chess](SCTBench%20reproduction/Chess/README.md)
- [Inspect](SCTBench%20reproduction/Inspect/README.md)
- [Misc](SCTBench%20reproduction/Misc/README.md)
- [Splash2](SCTBench%20reproduction/Splash2/README.md)
- [RADBench](SCTBench%20reproduction/RADBench/README.md)
