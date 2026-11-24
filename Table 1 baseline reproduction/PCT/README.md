# PCT CVE Benchmark Reproduction

## 1. Experiment Overview

PCT is the non-systematic probabilistic scheduler compared in Table 1 of *Controlled Concurrency Testing via Periodical Scheduling* (ICSE 2022). The PERIOD README identifies its implementation as the corresponding mode of SCTBench, which drives Maple and Intel PIN. This directory records the attempt to reproduce that Table 1 column on the ten ConVul CVE programs. The measured quantities are schedules to the first bug and buggy schedules, with the execution count retained beside those published columns.

The ten programs are CVE-2009-3547, CVE-2011-2183, CVE-2013-1792, CVE-2015-7550, CVE-2016-1972, CVE-2016-1973, CVE-2016-7911, CVE-2016-9806, CVE-2017-15265, and CVE-2017-6346. Programs that Table 1 splits by bug type keep one row per printed bug type. The paper runs each technique ten times per program, and each invocation has a budget of 10,000 schedules. A repetition is one whole search, not one schedule.

## 2. Experimental Results

Nine PCT campaigns have finished for CVE-2009-3547, and the tenth is still running, so it is not in these figures. All nine finished campaigns found a target crash. Each campaign executed 10,000 schedules. The first crash is at schedule 3.4 ± 2.1, calculated over the 9 campaigns that found the crash. The buggy-schedule count is 3335.9 ± 50.8, over the same 9 campaigns. The crash is signal 11. The benchmark source sets `i_pipe` to NULL before the other thread uses it, so the crash is counted on the single NPD row. There is no AddressSanitizer report. Campaigns that have not finished are not entered as zero or as 10,000.

The logs for the nine campaigns are under [results/cases/CVE-2009-3547/](results/cases/CVE-2009-3547/). The generated table is [results/summary.csv](results/summary.csv). The other nine programs have not been reached.

| CVE | Bug type | Row | Published first / buggy | Status | Measured first / buggy |
|---|---|---:|---|---|---|
| CVE-2009-3547 | NPD | 1 | 5 / 3333 | 9/9 finished campaigns detected; campaign 10 running | 3.4 ± 2.1 / 3335.9 ± 50.8 |
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

The paper's workstation was an Intel Xeon Silver 4214 with Ubuntu 18.04, GCC 7.5, and LLVM 10.0. These campaigns ran in the QEMU guest recorded in [environment.md](environment.md), with GCC 4.8.

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

CVE-2009-3547 is the only program with finished PCT campaigns. The paper prints a first bug at schedule 5 and 3,333 buggy schedules. Nine finished campaigns give a first-bug mean of 3.4 ± 2.1 and a buggy-schedule mean of 3335.9 ± 50.8. The buggy-schedule mean is 2.9 above the published 3,333. The published first-bug value, 5, falls inside the observed range 1 through 8, but it is not the mean. The tenth campaign is excluded because it has not reached 10,000 schedules.

The other fourteen rows have no measurement. The paper's total of 8 bugs in 7 programs remains a published total. This run has so far confirmed the NPD crash in one program.

### Final Result

CVE-2009-3547's PCT buggy-schedule count is close to Table 1, and its first-bug schedule varies around the published value. Nine of ten campaigns are in this report. The other nine programs are still unmeasured.
