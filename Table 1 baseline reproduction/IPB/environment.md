# Environment

The campaigns are running in a guest created for this task. The host cannot run Pin 2.12.

## Guest

- QEMU 11.1.0 on Windows, accelerator WHPX, 2 virtual CPUs, 4 GiB RAM.
- Ubuntu 14.04 cloud image, kernel `3.13.0-170-generic`.
- Pin 2.12 from SCTBench commit `d59ab26ddaedcd575ffb6a1f5e9711f7d6d2d9f2`, which vendors that kit. Pin 2.12's own notes list Ubuntu 12.04 among the tested systems and withdraw support only for kernel 2.4. They do not claim support for kernel 6.18. On this 3.13 kernel, `pin.sh -injection child -- /bin/echo` printed `pin-ok`. The 32-bit Pin launcher needed `libc6-i386`. Inside this guest, `/proc/sys/kernel/yama/ptrace_scope` was set to 0 because Pin's parent-injection mode requires it. The host's ptrace setting was not changed.
- Maple was built in that tree with `make compiletype=release`. The scheduler binary is `maple/build-release/systematic_controller.so`.
- GCC 4.8 from Ubuntu 14.04. CVE sources were compiled with `-g -fno-omit-frame-pointer -pthread`, not with PERIOD's `build.sh`.

## Host inspection

- WSL kernel `6.18.58.1-microsoft-standard-WSL2`. Pin 2.12 was not run there.
- Docker is installed in WSL, but this user is not in the `docker` group and `sudo` asks for a password. Docker would still use kernel 6.18.
- No VirtualBox or VMware installation was found. QEMU is at `C:\Program Files\qemu\qemu-system-x86_64.exe`.

## Earlier record that was not reused

The RQ3 submission describes Maple/PIN 2.12 on kernel `3.16.0-77` in a VirtualBox guest. That guest is not on this machine. Its overhead timings are not detection results.
