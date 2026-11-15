# Splash2 environment

These measurements were produced by 1240019547 邱洋. The host and the container are different layers. The container uses the host kernel.

| Item | Applies to | Value |
|---|---|---|
| CPU | Host | Intel Core i7-13650HX |
| Logical processors | Host | 20 (14 cores) |
| Memory visible to the experiment | Host, as reported by WSL | about 11 GiB of the host's 24 GiB |
| System and kernel | Host | WSL2, kernel 6.18.58.1-microsoft-standard-WSL2 |
| Docker Engine | Host | 29.1.3 |
| Docker image | Container | `wcventure/period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc` |
| Operating system | Container | Ubuntu 18.04.5 LTS |
| PERIOD source commit | Container | `b6f72a7b06d01ffa7114b640312873ec2578a5ea` |
| GCC | Container | 7.5.0 |
| Clang | Container | 10.0.0 |
| LLVM | Container | 10.0.0 |
| Python used by `run_PDS.py` | Container | 3.6.9 |
| NumPy used with that Python | Container | 1.19.5 |

The paper reports its workstation as an Intel Xeon Silver 4214. The measurements in this directory were taken on the host in the table above.

The container is privileged so `SCHED_DEADLINE` is available. The executed code is the image commit `b6f72a7b06d01ffa7114b640312873ec2578a5ea`. Commit `cb8deb9a176e5bb292d70d46557dd61dc0e98069` changes only documentation. The image identifiers are in [image.md](image.md). The flag meanings for these runs are in [flag_semantics.md](flag_semantics.md).

Bug depth is 3. The configured schedule budget is 10,000 per repetition. The target is three repetitions. The per-schedule timeout is 5 seconds. Workload arguments are the `argv` values in [manifest.json](manifest.json).
