# IPB CVE Benchmark Reproduction

## 1. Experiment Overview

IPB is the systematic preemption-bounding scheduler compared in Table 1 of *Controlled Concurrency Testing via Periodical Scheduling* (ICSE 2022). The PERIOD README identifies its implementation as the corresponding mode of SCTBench, which drives Maple and Intel PIN. This directory records the attempt to reproduce that Table 1 column on the ten ConVul CVE programs. The measured quantities are schedules to the first bug, schedules explored, and buggy schedules.

The ten programs are CVE-2009-3547, CVE-2011-2183, CVE-2013-1792, CVE-2015-7550, CVE-2016-1972, CVE-2016-1973, CVE-2016-7911, CVE-2016-9806, CVE-2017-15265, and CVE-2017-6346. Programs that Table 1 splits by bug type keep one row per printed bug type. The paper runs each technique ten times per program, and each invocation has a budget of 10,000 schedules. A repetition is one whole search, not one schedule.

## 2. Experimental Results

Three of the ten programs have finished both methods. The other seven have not been reached, and their rows stay empty. An empty cell is not zero and it is not 10,000. A signal 11 crash is counted on a program's single published bug row. These programs do not produce an AddressSanitizer type.

CVE-2009-3547: 10/10 campaigns detected the signal 11 crash. Measured first / explored / buggy is 3 ± 0 / 46 ± 0 / 6 ± 0. CVE-2011-2183: 10/10 campaigns detected the signal 11 crash. Measured first / explored / buggy is 5.5 ± 2.6 / 104.5 ± 25.8 / 10 ± 4.2. CVE-2013-1792: 10/10 campaigns detected the signal 11 crash. Measured first / explored / buggy is 15 ± 0 / 321 ± 0 / 18 ± 0.

The logs are under `results/cases/`. The generated table is [results/summary.csv](results/summary.csv).

| CVE | Bug type | Row | Published first / explored / buggy | Status | Measured first / explored / buggy |
|---|---|---:|---|---|---|
| CVE-2009-3547 | NPD | 1 | 3 / 36 / 5 | 10/10 detected | 3 ± 0 / 46 ± 0 / 6 ± 0 |
| CVE-2011-2183 | NPD | 1 | 8 / 98 / 11 | 10/10 detected | 5.5 ± 2.6 / 104.5 ± 25.8 / 10 ± 4.2 |
| CVE-2013-1792 | NPD | 1 | 15 / 321 / 18 | 10/10 detected | 15 ± 0 / 321 ± 0 / 18 ± 0 |
| CVE-2015-7550 | NPD | 1 | 8 / 73 / 11 | Not started | not measured |
| CVE-2015-7550 | NPD | 2 | 16 / blank / 881 | Not started | not measured |
| CVE-2016-1972 | UAF | 1 | 91 / L (10,000) / 918 | Not started | not measured |
| CVE-2016-1972 | DF | 2 | blank / blank / 0 | Not started | not measured |
| CVE-2016-1973 | NPD | 1 | blank / blank / 0 | Not started | not measured |
| CVE-2016-1973 | UAF | 2 | blank / L (10,000) / 0 | Not started | not measured |
| CVE-2016-7911 | NPD | 1 | 8 / 204 / 66 | Not started | not measured |
| CVE-2016-9806 | DF | 1 | 9 / 226 / 84 | Not started | not measured |
| CVE-2017-15265 | UAF | 1 | blank / 88 / 0 | Not started | not measured |
| CVE-2017-15265 | NPD | 2 | blank / blank / 0 | Not started | not measured |
| CVE-2017-6346 | UAF | 1 | blank / L (10,000) / 0 | Not started | not measured |
| CVE-2017-6346 | DF | 2 | blank / blank / 0 | Not started | not measured |

The paper's IPB total for this table is 8 bugs in 7 programs. The paper's PCT total is also 8 bugs in 7 programs. Those totals are published values. This directory does not add a measured total.

## 3. Environment and Configuration

The inspection host is the Windows 11 machine used for the SCTBench work, running WSL2 kernel 6.18.58.1. Details of the search are in [environment.md](environment.md). Source checksums and the scheduler commits are in [source_metadata.txt](source_metadata.txt).

SCTBench commit `d59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2` is the launcher that was read. Maple commit `14b2769a07473f9eca6ea1bc7f57bbefe1db46f4` is the HEAD reported by the remote; it was not built. The PERIOD image previously recorded for the CVE sources is `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc`, commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`. The `build.sh` files in that tree instrument the programs for PERIOD. They were not used as IPB builds.

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
python scripts/run_many.py --mode pb --limit 10000 benchmarks/buggy.txt
```

That command belongs in a sourced SCTBench tree with `PIN_HOME` set. It is not run by `preflight.py`.

Rebuild the tables from whatever campaign records exist. With no `metrics.json` files, every measured cell stays empty:

```bash
python scripts/analyze.py
```

A later run belongs in `results/cases/<CVE-ID>/<repetition>-<attempt>/` and is reusable only when its recorded source, tool commit, build, executable, arguments, budget, timeout, repetition, and seed match the request. This submission has no such record.

## 5. Comparison with Table 1

CVE-2009-3547 publishes first 3, explored 36, and buggy 5. The executed bounds 0 through 5 measure 3 ± 0 / 46 ± 0 / 6 ± 0. Bounds 0 through 4 alone are 36 schedules and 5 buggy schedules. The ten campaigns use `srand(0)`, so a standard deviation of 0 is a repeated deterministic search.
CVE-2011-2183 publishes first 8, explored 98, and buggy 11. The executed bounds 0 through 5 measure 5.5 ± 2.6 / 104.5 ± 25.8 / 10 ± 4.2. Bounds 0 through 4 alone are 61 schedules and 5 buggy schedules. The ten campaigns use `srand(0)`, so a standard deviation of 0 is a repeated deterministic search.
CVE-2013-1792 publishes first 15, explored 321, and buggy 18. The executed bounds 0 through 5 measure 15 ± 0 / 321 ± 0 / 18 ± 0. Bounds 0 through 4 alone are 233 schedules and 13 buggy schedules. The ten campaigns use `srand(0)`, so a standard deviation of 0 is a repeated deterministic search.

The other programs have no measurement, so they are not counted as missed bugs. The guest is still running those campaigns.

### Final Result

The first three programs have finished IPB campaigns. The measured values above are the ones in the saved logs. The remaining seven programs are not part of this submission.
