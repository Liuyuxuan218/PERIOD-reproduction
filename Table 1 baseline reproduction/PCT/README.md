# PCT CVE Benchmark Reproduction

## 1. Experiment Overview

PCT is the non-systematic probabilistic scheduler compared in Table 1 of *Controlled Concurrency Testing via Periodical Scheduling* (ICSE 2022). The PERIOD README identifies its implementation as the corresponding mode of SCTBench, which drives Maple and Intel PIN. This directory records the attempt to reproduce that Table 1 column on the ten ConVul CVE programs. The measured quantities are schedules to the first bug and buggy schedules, with the execution count retained beside those published columns.

The ten programs are CVE-2009-3547, CVE-2011-2183, CVE-2013-1792, CVE-2015-7550, CVE-2016-1972, CVE-2016-1973, CVE-2016-7911, CVE-2016-9806, CVE-2017-15265, and CVE-2017-6346. Programs that Table 1 splits by bug type keep one row per printed bug type. The paper runs each technique ten times per program, and each invocation has a budget of 10,000 schedules. A repetition is one whole search, not one schedule.

## 2. Experimental Results

No PCT campaign was executed. SCTBench states that this PIN toolchain requires a Linux kernel of version 3.x or older. The kernel on this machine is 6.18.58.1, and neither PIN, Maple, nor a VirtualBox guest was installed. `scripts/preflight.py` exits with status 2 and writes [results/diagnostics/preflight.json](results/diagnostics/preflight.json). That status is a missing tool, not a completed search and not a failure to find a bug.

All fifteen printed bug rows are listed below. An unstarted row has no measured value. It is not shown as zero and it is not shown as 10,000. The generated tables are [results/summary.csv](results/summary.csv) and [results/per_run.csv](results/per_run.csv). Each program has a [not-started status](results/cases/) and no `metrics.json`, because no scheduler was launched.

| CVE | Bug type | Row | Published first / buggy | Status | Measured |
|---|---|---:|---|---|---|
| CVE-2009-3547 | NPD | 1 | 5 / 3333 | Not started | not measured |
| CVE-2011-2183 | NPD | 1 | 5 / 394 | Not started | not measured |
| CVE-2013-1792 | NPD | 1 | 61 / 124 | Not started | not measured |
| CVE-2015-7550 | NPD | 1 | 3 / 394 | Not started | not measured |
| CVE-2015-7550 | NPD | 2 | 3 / 731 | Not started | not measured |
| CVE-2016-1972 | UAF | 1 | 134 / 15 | Not started | not measured |
| CVE-2016-1972 | DF | 2 | blank / 0 | Not started | not measured |
| CVE-2016-1973 | NPD | 1 | blank / 0 | Not started | not measured |
| CVE-2016-1973 | UAF | 2 | blank / 0 | Not started | not measured |
| CVE-2016-7911 | NPD | 1 | 5 / 511 | Not started | not measured |
| CVE-2016-9806 | DF | 1 | 3 / 1135 | Not started | not measured |
| CVE-2017-15265 | UAF | 1 | blank / 0 | Not started | not measured |
| CVE-2017-15265 | NPD | 2 | blank / 0 | Not started | not measured |
| CVE-2017-6346 | UAF | 1 | blank / 0 | Not started | not measured |
| CVE-2017-6346 | DF | 2 | blank / 0 | Not started | not measured |

The paper's IPB total for this table is 8 bugs in 7 programs. The paper's PCT total is also 8 bugs in 7 programs. Those totals are published values. This directory does not add a measured total.

## 3. Environment and Configuration

The inspection host is the Windows 11 machine used for the SCTBench work, running WSL2 kernel 6.18.58.1. Details of the search are in [environment.md](environment.md). Source checksums and the scheduler commits are in [source_metadata.txt](source_metadata.txt).

SCTBench commit `d59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2` is the launcher that was read. Maple commit `14b2769a07473f9eca6ea1bc7f57bbefe1db46f4` is the HEAD reported by the remote; it was not built. The PERIOD image previously recorded for the CVE sources is `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`, commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`. The `build.sh` files in that tree instrument the programs for PERIOD. They were not used as PCT builds.

Section 4.1.3 sets a CVE bug-depth bound of 5 and a 10,000-schedule budget, and it says each technique is invoked 10 times. The launcher's default `--max` is 5 and its default `--limit` is 10000. For IPB the loop is `range(0, max)`, so a default run executes preemption bounds 0 through 4 and can accumulate more than 10,000 schedules across bounds. For PCT the same default splits one 10,000-schedule limit into ten jobs of 1,000, all with seed 0. The paper does not say which of these readings matches Table 1. No seed, timeout, or bound was selected to fill that gap.

The paper's workstation was an Intel Xeon Silver 4214 with Ubuntu 18.04, GCC 7.5, and LLVM 10.0. This attempt did not reach a compiler or a guest.

## 4. Reproduction Instructions

Run the commands from this directory. They write only under `results/`.

Check the runtime. On this machine the command exits 2 and does not start a program:

```bash
python scripts/preflight.py
```

The scheduler command documented by SCTBench, which cannot be pointed at these CVE programs without a benchmark entry that the upstream list does not contain, is:

```bash
python scripts/run_many.py --mode pct --limit 10000 benchmarks/buggy.txt
```

That command belongs in a sourced SCTBench tree with `PIN_HOME` set. It is not run by `preflight.py`.

Rebuild the tables from whatever campaign records exist. With no `metrics.json` files, every measured cell stays empty:

```bash
python scripts/analyze.py
```

A later run belongs in `results/cases/<CVE-ID>/<repetition>-<attempt>/` and is reusable only when its recorded source, tool commit, build, executable, arguments, budget, timeout, repetition, and seed match the request. This submission has no such record.

## 5. Comparison with Table 1

The published cells were read from Table 1 of the ICSE 2022 PDF. `L` is the printed schedule limit of 10,000. A blank cell was blank in the PDF and is not inferred from another row. `%` in the paper is a null first-bug value here, with the printed buggy-schedule count kept beside it. For the second NPD row of CVE-2015-7550, IPB prints a first-bug schedule of 16 and 881 buggy schedules, while the explored-schedule cell is blank. That row is stored as printed.

No measured column can be compared. There is no supported match and no measured discrepancy. The published IPB result is 8 bugs in 7 programs, and the published PCT result is 8 bugs in 7 programs. CVE-2016-1973, CVE-2017-15265, and CVE-2017-6346 are the three programs with no printed detection in either column. Those statements describe the paper, not a run performed here.

### Final Result

The PCT column of Table 1 was not reproduced. The blocker is the missing PIN runtime on a kernel newer than the 3.x line required by SCTBench. The published numbers remain only the paper's numbers.
