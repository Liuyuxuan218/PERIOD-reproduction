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

- Set up the SCTBench runs in the official PERIOD Docker image `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`. The guest is Ubuntu 18.04.5 LTS with GCC 7.5.0, Clang 10.0.0, LLVM 10.0.0, Python 3.6.9, and PERIOD commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`. The container is privileged so `SCHED_DEADLINE` can be used.
- Built the 36 SCTBench programs in Table 2 with the build scripts in that image. Each program was run with `run_PDS.py` at bug depth 3 (`-d 3`). The schedule budget was 10,000 per run, and 100,000 for `CS.twostage_100_bad`. The target was three repetitions.
- Completed three repetitions for 30 programs. For `CS.reorder_3_bad`, identified 6 error interleavings among 27 schedules, with the first bug at schedule 6, matching Table 2.
- `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two completed repetitions. `CS.queue_bad` has one completed repetition. `CS.account_bad` and `RADBench.bug4` have none.
- Saved the schedule count, error interleavings, first bug schedule, timeouts, and elapsed time for each run under `SCTBench reproduction/results/`.

Contributor: 1240019547 邱洋.

The image check, clone-and-run commands, and the full result table are in [SCTBench reproduction/README.md](SCTBench%20reproduction/README.md).
