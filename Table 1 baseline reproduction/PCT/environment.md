# Environment

This file records the machine that was inspected for the PCT runs. No PCT campaign was launched.

## Host

- Windows 11 host, WSL2 kernel `6.18.58.1-microsoft-standard-WSL2`.
- The earlier SCTBench runs in this repository used an Intel Core i7-13650HX. This inspection did not repeat a hardware benchmark.
- `docker` is not on the Windows PATH used by this session. Inside WSL, `docker` could not connect to `/var/run/docker.sock`, and `sudo -n docker images` returned no image list.

## Search for the baseline runtime

- `VBoxManage` was not on PATH. `C:\Program Files\Oracle\VirtualBox` and `C:\Users\LOQ\VirtualBox VMs` were absent. No `.vdi` or `.vbox` file was found under `/home` or `/opt` at depth 5.
- No `pin` executable and no Maple directory were found under `/home`, `/opt`, or `/usr/local` at depth 5.
- `/home/qiuyang/period-root` contains the exported PERIOD tree, including `evaluation/ConVul-CVE-Benchmarks`. It does not contain Maple or PIN.
- `/home/qiuyang/CMakeCache.txt` belongs to an unrelated project (`HW8`). It is not a Maple build.
- The RQ3 submission at `experiments/rq3-submission-20261122/` describes a VirtualBox guest with kernel `3.16.0-77`, Ubuntu 18.04.5 in a chroot, and Maple/PIN 2.12. That guest is not on this machine. Its runtime figures are overhead measurements and are not detection results.

## Why that search matters

The SCTBench README says its PIN-based tools require a kernel version no newer than 3.x. The kernel visible here is 6.18. A PERIOD Docker container would still use this WSL kernel, so the container is not a substitute for the PIN guest. `scripts/preflight.py` checks the same conditions and writes `results/diagnostics/preflight.json`.
