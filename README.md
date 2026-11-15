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

- Prepared the reproduction of the 36 SCTBench programs evaluated in Table 2 of the PERIOD paper.
- Used the official PERIOD Docker image and the PERIOD checkout at commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`, maintaining the shared software setup used for the group's experiments.
- Recorded the software versions and the hardware environment used for the SCTBench measurements.
- Organized a benchmark manifest containing each program's source directory, build command, workload arguments, and schedule budget.
- Configured all programs with a bug depth of 3 and a schedule budget of 10,000 per run, except `CS.twostage_100_bad`, which used 100,000.
- Implemented scripts to build the benchmarks, execute repeated experiments, preserve completed repetitions, and generate result tables.
- Collected 97 valid runs. Thirty programs have three completed repetitions; `Splash2.barnes`, `Splash2.fft`, and `RADBench.bug3` have two each; `CS.queue_bad` has one; and `CS.account_bad` and `RADBench.bug4` have no completed repetitions.
- Recorded the number of schedules explored, error interleavings, the schedule of the first detected error, timeout interleavings, and elapsed time for each repetition.
- Calculated mean values and sample standard deviations for programs with at least two valid repetitions, while retaining individual measurements for inspection.
- Reported timeouts separately from detected errors, without treating unverified timeouts as confirmed deadlocks.
- Compared selected measurements with the PERIOD results in Table 2. `CS.reorder_3_bad` matched the published figures for schedules explored, error interleavings, and the first bug schedule.
- Documented the incomplete repetitions and schedule counts exceeding the configured budget as issues requiring further investigation.
- Organized the benchmark configuration, reproduction scripts, per-run measurements, aggregate tables, and environment documentation under `SCTBench reproduction/`.

Contributor: 1240019547 邱洋.

Detailed reproduction procedures and experimental results are available in [SCTBench reproduction/README.md](SCTBench%20reproduction/README.md).
