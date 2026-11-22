# RQ3 Runtime Overhead: Reduced-Scale Results

Contributor: 梁羽帆 (student ID: 1240024116).

## Scope

This directory contains a reduced-scale comparison of Native, PERIOD,
IPB, IDB and PCT. Native is the uninstrumented reference configuration.

The recorded dataset comprises ten programs, five configurations, three
sessions per program and ten adopted timed launches per configuration
per session: 1,500 adopted launches in total.

The programs cover four of seven SCTBench families:
- CS: reorder_3_bad, reorder_4_bad, reorder_5_bad, reorder_10_bad.
- Inspect: qsort_mt.
- Chess: WSQ, IWSQ, IWSQWS and SWSQ.
- Misc: safestack.

This is not a reproduction of all 36 SCTBench programs.

## Contents

- [Nine-program results](nine-program-results/): 1,350 adopted launches,
  data tables, plots, report draft and reproduction scripts.
- [SWSQ audit](swsq-audit/): supplementary audit records for SWSQ.
- [SWSQ evidence](swsq-evidence/): raw evidence archive, summary,
  command timing and host timing audit for 150 supplementary launches.

The existing nine-program plots and report exclude SWSQ.
A unified ten-program plot is not included in this snapshot.
Historical files describe their own experiment stage.

## Execution Environment

The experiment used a VirtualBox VM with two virtual CPUs and 2 GB RAM,
Linux 3.16.0-77-generic, and an Ubuntu 18.04.5 userland accessed through
chroot. Windows/WSL and Vagrant controlled execution.

Tools included Clang 10, Maple/PIN 2.12 and PERIOD commit
b6f72a7b06d01ffa7114b640312873ec2578a5ea.
The Docker image supplied userland materials; it was not the runtime
container for these formal measurements.

## Measurement and Interpretation

The metric is startup-inclusive observed child-process lifetime, not
steady-state application overhead. Compilation and profiling/discovery
are excluded. See the saved protocols for exact boundaries.

Within each session, ten adopted launches are averaged. Slowdowns are
paired with Native for the same program and session. Reported variability
uses the three session-level ratios and sample standard deviation.
The ten launches within a session are not ten independent repetitions.

Retained target assertions must be distinguished from tool failures.
Timeout limits must not be interpreted as normally completed runtimes.
These selected workloads cannot establish the paper's claim for every
benchmark or reproduce its exact per-program values.

## Evidence and Reproduction Limitations

The result directories contain measurements, summaries, audits and raw
evidence archives. The copied directories were compared with their local
source directories before this README was added.

Existing helper scripts retain machine-specific paths and prerequisites.
This snapshot does not claim clean-machine reproduction from this README
alone; portable environment setup and command validation remain pending.

The separate one-factor extension is not established by this snapshot.
Increasing coverage within the original benchmark set alone is not
evidence that the extension requirement has been completed.

## Provenance and AI Assistance

Original research and upstream implementation:
Wen et al., "Controlled Concurrency Testing via Periodical Scheduling",
ICSE 2022; https://github.com/wcventure/PERIOD.

Upstream code remains subject to its original license.
AI assistance was used for scripting, troubleshooting and documentation
drafting. Experimental claims must remain grounded in saved evidence.
This statement must be reconciled with the team's final AI-use and
contribution statements.
