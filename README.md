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

- Finished three repetitions for 30 of the 36 SCTBench programs in Table 2, using the official PERIOD image at commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`, bug depth 3, and a schedule budget of 10,000 (100,000 for `CS.twostage_100_bad`).
- `CS.reorder_3_bad` matches Table 2: the first bug is at schedule 6, 27 schedules were explored, and 6 were error interleavings.
- `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two completed repetitions. `CS.queue_bad` has one. `CS.account_bad` and `RADBench.bug4` have none.

Contributor: 1240019547 邱洋.

The 97 valid runs are in [SCTBench reproduction/README.md](SCTBench%20reproduction/README.md).
