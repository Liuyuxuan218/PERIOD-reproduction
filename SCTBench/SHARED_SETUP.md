# SCTBench setup aligned with the group repository

Recorded 2026-11-13 by 1240019547 邱洋 before the SCTBench measurement runs.
This file does not replace teammates' environment records. Their files are unchanged.

Collaborative repository HEAD at inspection: `1df282008e9d939c32200b13be9d205d85ecbcf2`.
No task-allocation document and no presentation instruction are in the repository.
Contributors with commits: 1240033600 赵士锦 and 1240016737 刘语萱 (GitHub account Liuyuxuan218).

## Executed upstream revision

The official image contains a Git checkout, and that checkout is the code that runs.

| Check | Result |
|---|---|
| `git -C /workdir/PERIOD rev-parse HEAD` inside `period:latest` | `b6f72a7b06d01ffa7114b640312873ec2578a5ea` |
| Commit time and subject | 2022-01-17 02:34:23 +0000, `fix run_PDS.py` |
| Working tree | clean, `main...origin/main` |
| Image creation time | 2022-01-17T02:55:03Z |
| Current GitHub HEAD of wcventure/PERIOD | `cb8deb9a176e5bb292d70d46557dd61dc0e98069` (2022-10-09, `fix Install.md`) |

`git diff --stat b6f72a7 cb8deb9` changes only `AdvancedUsage.md`, `INSTALL.md`, `README.md`, and `STATUS.md`.
`tool/DBDS/run_PDS.py` is identical at both commits and inside the image (`sha256:c6ed1312f61f7ec739e3dcead0086e0265d37f07bd88ef64d6588d3ff61a8e8f`).

刘语萱's `CVE reproduction/CVE-2016-7911/environment/versions.txt` and `check_environment.sh` record and require this image commit. That matches the container.
赵士锦's `environment/period_source_version.txt` also records `b6f72a7` for the doubleFree experiment.
赵士锦's later CVE-2009-3547 and CVE-2011-2183 metadata, and the archived WSL note for CVE-2016-7911, name `cb8deb9` instead.

Those two names do not describe two different tools. `cb8deb9` is the later documentation-only GitHub HEAD. The Docker tree that was executed is `b6f72a7`. The benchmark sources committed for the three CVEs match the image byte for byte (Git blobs, not the CRLF working-tree copies created by a Windows checkout). SCTBench will cite `b6f72a7` as the executed revision and state that `cb8deb9` does not change the scheduler or the benchmarks.

## Patches

No PERIOD patch is committed in the collaborative repository. Submitted statements say the benchmark sources were copied without modification. The CVE-2016-7911 source SHA-256 in `logs/experiment_record.md` (`349db36a3c84a7aebd90de1bbc029201a609fcd8d0764821e998cbeceaaf39fa`) matches the file in the image. SCTBench will not patch `run_PDS.py` or the benchmarks.

## Docker image and toolchain

Shared image, verified on this machine and in the submitted files:

| Item | Value |
|---|---|
| Tag used by the group | `wcventure/period:stable`, also tagged `period:latest` |
| Image ID pinned by 刘语萱 and `environment/docker_image.txt` | `sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |
| Guest OS | Ubuntu 18.04.5 LTS |
| GCC / G++ | 7.5.0 (`7.5.0-3ubuntu1~18.04`) |
| Clang / LLVM | 10.0.0 |
| Python | 2.7.17 and 3.6.9 |
| NumPy | 1.16.6 on Python 2, 1.19.5 on Python 3 |
| wllvm | installed for Python 2 |
| sysv_ipc | 1.1.0 on Python 3 |
| Make / CMake | 4.1 / 3.10.2 |

`environment/container_environment.txt` lists NumPy 1.16.6 and Python 2.7.17. That pair is real, and it is the Python 2 installation. `run_PDS.py` starts with `#!/usr/bin/env python3`, so the search uses Python 3.6.9 and NumPy 1.19.5. Both are in the same image the group used. SCTBench will record both and will invoke `python3`.

The container shares the host kernel. `SCHED_DEADLINE` is present. A privileged container is required, matching `reproduce.sh` (`docker run --privileged`) and `environment/docker_image.txt`.

## How the group actually launches PERIOD

`CVE reproduction/CVE-2016-7911/scripts/reproduce.sh` is the only non-interactive launcher in the repository. It does not `source tool/init_env.sh`. It exports `ROOT_DIR`, prepends `clang+llvm/bin` and `tool/SVF/Release-build/bin` to `PATH`, sets `LD_LIBRARY_PATH`, runs `./build.sh`, then runs:

```text
printf '\n' | run_PDS.py -d 3 ./2016-7911
```

`tool/init_env.sh` asks for a keypress before it exports the same paths. The READMEs tell a person to source it inside an interactive shell. Sourcing it from a script would block. SCTBench scripts will follow `reproduce.sh` for the environment variables and will call each program's own `./build.sh`.

Prompt handling in the logs:

| Experiment | Logged options | Who |
|---|---|---|
| doubleFree | `-y -d 3` | 赵士锦. README says `-y` only skips the Enter prompt. |
| CVE-2016-7911 | `-d 3`, with a newline supplied by the script | 刘语萱 |
| CVE-2009-3547 | `-d 1` | 赵士锦 |

`-y` and a newline are the same continuation unless the typed text is `debug`. The doubleFree log and a smoke run on this machine both explored 6 schedules and reported 4 double-free errors, with the first error at test `0003`. SCTBench will pass `-y` so a batch run does not wait for a terminal.

## Metric definitions that match the logs

The summaries are taken from `run_PDS.py`'s footer, not from a separate analysis program.

| Group name | Log source | Paper Table 2 column |
|---|---|---|
| Interleavings tested, Total schedules explored, Total Tests | Footer `Round` total. Examples: doubleFree `6`, CVE-2016-7911 `19`, CVE-2009-3547 `2`. | schedules |
| Total Error Interleavings | Footer line of that name. | buggy schedules |
| Schedules to first bug | Test number in the first `Errors/` filename, such as `000001_0000003_SEGV` (schedule 3). | schedules to bug (1st) |
| Bug category | Suffix of that filename (`SEGV`, `double-free`), from AddressSanitizer text. | Bug Type |
| Total Timeout Interleavings | Footer line of that name. Kept separate from errors. | not a confirmed bug |
| Replay | `run_PDS.py -r <error file> <program>`, then an AddressSanitizer report. | confirmation |

The footer field `Last New Find` is 0 in these logs because `lastRound` is assigned as a local variable inside `record_error_message`. The group correctly uses the Total column. SCTBench will do the same.

One submitted number is not backed by a search log. CVE-2011-2183's README and `results/summary.txt` say 56 tests and 15 error interleavings at `-d 2`. The repository has `results/replay.log` and the 15 error files' names appear in that replay log, including `000001_0000003_SEGV`, but it has no `run.log`. The 15 replays and the first-bug index 3 are supported. The total of 56 cannot be recomputed from a committed search log.

## Repetition policy

Every submitted result is one execution. No file reports a repetition count, a mean, or a standard deviation. The course assignment asks for at least three runs and mean ± standard deviation. The paper says each SCTBench technique was invoked 10 times. SCTBench will keep the group's per-run fields and add repetition count, mean, and sample standard deviation around them. Three runs is the minimum. Ten runs will be used when the schedule budget finishes quickly enough to do so. A deterministic search can have a standard deviation of zero.

## Hardware, left on the contributor who measured it

`environment/host_environment.txt` was written with 赵士锦's environment commits. It is not this machine.

| | 赵士锦, `environment/host_environment.txt` | 刘语萱, CVE-2016-7911 Docker record | This machine, 邱洋, not yet used for Table 2 |
|---|---|---|---|
| CPU | Intel Core i9-14900HX, 16 cores / 32 threads | not recorded | Intel Core i7-13650HX, 14 cores / 20 threads |
| Memory seen by the Linux side | about 15 GiB, 4 GiB swap | not recorded | WSL reports 11 GiB of the host's 24 GiB |
| WSL kernel | 6.18.54.1 | container shares the WSL kernel; the Docker record does not print `uname` | 6.18.58.1-microsoft-standard-WSL2 |
| Docker Engine | 29.9.2 (Docker Desktop 4.96.3) | image ID matches | 29.1.3, image ID matches |
| Paper workstation | Intel Xeon Silver 4214, Ubuntu 18.04 host | same paper target | same paper target |

SCTBench results will be labeled with this machine. `environment/host_environment.txt` stays 赵士锦's record.

## What SCTBench keeps from the paper

These settings are not what the CVE runs used, and they are required for Table 2.

| Setting | Group CVE practice | SCTBench run |
|---|---|---|
| Bug-depth bound | The artifact README value for that CVE: `-d 1`, `-d 2`, or `-d 3`. Not the paper's CVE bound of 5. | `-d 3` for every Table 2 program. The paper sets the SCTBench bound to 3. SafeStack's README example of `-d 5` is not the Table 2 setting; the paper says that bug needs five context switches and was outside the bound. |
| Schedule budget | `-f` is never passed. The CVE searches end because the bounded space is small (2, 19, or the reported 56). | `-f 10000`, and `-f 100000` for `CS.twostage_100_bad`. The Table 2 note defines `L` as that budget. |
| Per-execution timeout | No `-t` in the logs, so the tool default of 5 seconds. | Default 5 seconds. A program whose artifact README sets `-t` keeps that value, because a short timeout would turn a slow normal run into a timeout. |
| Workload arguments | The benchmark's own command line. | The artifact command for that Table 2 program: binary, thread arguments, `LD_LIBRARY_PATH`, and input files. `--no-prefix` is not a paper setting and is not used unless a case fails to make progress; if it is used, that run will be marked as a deviation. |

Effect on comparability:

- Using `-d 3` and `-f 10000` makes the three PERIOD columns comparable to Table 2. Copying the CVE habit of "the README's `-d`, with no schedule cap" would not.
- CVE-2009-3547 shows the effect of the CVE habit. The log at `-d 1` contains 2 schedules and 1 error. Table 1 lists 6 schedules and 3 buggy schedules for that program. The log is consistent with stopping at the artifact's `-d 1`.
- CVE-2011-2183's reported 56 schedules and 15 errors, if accurate, are likewise a `-d 2` search. Table 1 lists 906 schedules and 130 buggy schedules. The missing search log means this explanation is not rechecked from raw output.
- `-y` does not change the schedule generator.
- CPU, WSL kernel, and WSL memory differ from the paper and from 赵士锦's host file. The guest compilers match the paper (GCC 7.5, LLVM 10.0). Timing and timeout-sensitive programs can differ for that reason. Schedule counts from a deterministic search should still be comparable when the depth and the schedule cap match.

## Repository conventions to follow

- Commit subjects already used by 赵士锦: `1240033600 赵士锦: <what changed>`. New SCTBench commits use `1240019547 邱洋: <what changed>`.
- One directory per contribution. Existing ones are `environment/`, `experiments/doubleFree/`, and `CVE reproduction/<id>/`. SCTBench work stays in `SCTBench/` and does not edit those trees.
- Raw search logs are kept when they are small enough. Build products, `out_*/`, bitcode, and `.npz` files are not committed. CVE-2016-7911's `.gitignore` is the local pattern.
- Replay evidence is an error file plus the AddressSanitizer log, as in the CVE and doubleFree directories.
