# PERIOD Reproduction Environment

This directory documents the environment configuration and experimental procedures used to reproduce PERIOD.

The purpose is to provide a clear reference for setting up the Docker environment, verifying dependencies, and running the DoubleFree benchmark.

## 1. Environment Architecture

The reproduction environment consists of three main layers:

```text
Windows Host
    |
    v
WSL2 (Ubuntu)
    |
    v
Docker Desktop
    |
    v
Docker Container (Ubuntu 18.04.5 LTS)
    |
    v
PERIOD Reproduction Environment
```

The Docker container shares the Linux kernel provided by WSL2.

The host environment and container environment are documented separately.

## 2. Directory Contents

| File | Description |
|---|---|
| `host_environment.txt` | Windows, WSL2, hardware, and Docker information |
| `container_environment.txt` | Container OS, compiler, LLVM, and Python versions |
| `docker_image.txt` | Docker image and container identification |
| `period_source_version.txt` | PERIOD source repository and Git commit |
| `experiment_metadata.txt` | Recorded experimental configuration and results |
| `sched_deadline_verification.txt` | SCHED_DEADLINE system call verification |

## 3. Prerequisites

Before setting up the environment, ensure that the following components are available:

- Windows with WSL2 enabled.
- Ubuntu installed under WSL2.
- Docker Desktop installed and running.
- WSL Integration enabled for the Ubuntu distribution in Docker Desktop.
- Docker CLI accessible from the WSL Ubuntu terminal.
- The PERIOD Docker image available locally.

### 3.1 Verify WSL2

Run the following commands in Windows PowerShell:

```powershell
wsl --version
wsl -l -v
```

Make sure the Ubuntu distribution uses WSL2.

### 3.2 Verify Docker

Run the following commands in the WSL Ubuntu terminal:

```bash
docker --version
docker version
docker info
```

If Docker is unavailable, check:

Docker Desktop -> Settings -> Resources -> WSL Integration

Enable integration for the Ubuntu distribution.

## 4. Docker Image Preparation

The experiment uses the Docker image:

```text
period:latest
```

The recorded image identification information is available in `docker_image.txt`.

Before creating a container, check whether the image exists locally:

```bash
docker image inspect period:latest
```

If the image is unavailable, obtain the exact recorded image from the project team or its documented original source before proceeding.

Do not assume that an image with the same tag necessarily contains the same environment.

## 5. Docker Container Setup

A persistent container named `period-reproduction` is used for the experiments.

### 5.1 Create a New Container

Only execute this command if the container does not already exist.

Run in the WSL Ubuntu terminal:

```bash
docker run --privileged -it \
  --name period-reproduction \
  period:latest \
  bash
```

The `--privileged` option is part of the recorded experimental configuration.

It provides extended container privileges and should only be used when required by the experimental environment.

The container is persistent because `--rm` is not specified.

### 5.2 Enter an Existing Container

Check existing containers:

```bash
docker ps -a
```

If the container is already running:

```bash
docker exec -it period-reproduction bash
```

If the container is stopped:

```bash
docker start -ai period-reproduction
```

### 5.3 Exit the Container

Inside the container:

```bash
exit
```

Exiting the original interactive Bash session stops the container but does not delete it.

Exiting an additional shell opened with `docker exec` only terminates that shell.

### 5.4 Stop the Container

From the WSL Ubuntu terminal:

```bash
docker stop period-reproduction
```

Avoid using `docker rm` if you intend to preserve the existing container.

## 6. Environment Verification

After entering the Docker container, verify the operating system:

```bash
cat /etc/os-release
uname -a
```

Check compiler and build tools:

```bash
gcc --version
g++ --version
make --version
cmake --version
ld --version
```

Check Clang and LLVM:

```bash
clang --version
llvm-config --version
```

Check Python and dependencies:

```bash
python --version
pip show wllvm
pip show numpy
```

The expected software versions are documented in:

- `container_environment.txt`
- `host_environment.txt`

Note that `uname -a` reports the Linux kernel provided by WSL2, not an independently installed container kernel.

## 7. SCHED_DEADLINE Verification

PERIOD uses Linux SCHED_DEADLINE for periodical scheduling.

A standalone C test program was compiled and executed inside the Docker container to verify the availability of the scheduling system call.

The test used the following parameters:

| Parameter | Value |
|---|---|
| Scheduling Policy | SCHED_DEADLINE (6) |
| Runtime | 1 ms |
| Deadline | 10 ms |
| Period | 10 ms |

The recorded terminal output was:

```text
Testing SCHED_DEADLINE...
Current scheduling policy: 6
PASS: SCHED_DEADLINE is working.
```

The running test process was also observed with scheduling class `#6`.

This confirms that the tested process can successfully use SCHED_DEADLINE in the current WSL2 and Docker environment.

This standalone test does not independently establish that every PERIOD experiment uses SCHED_DEADLINE.

For detailed verification information, see:

`sched_deadline_verification.txt`

## 8. PERIOD Source Code

Original repository:

https://github.com/wcventure/PERIOD

Recorded Git commit:

```text
b6f72a7b06d01ffa7114b640312873ec2578a5ea
```

The source code is located inside the container at:

```text
/workdir/PERIOD
```

Enter the source directory:

```bash
cd /workdir/PERIOD
```

Verify the source version:

```bash
git rev-parse HEAD
git status --short
```

The recorded source commit is specified in `period_source_version.txt`.

## 9. Reproducing the DoubleFree Experiment

The current reproduction focuses on the DoubleFree benchmark.

### 9.1 Enter the Benchmark Directory

Inside the Docker container:

```bash
cd /workdir/PERIOD/test/doubleFree
```

### 9.2 Build the Benchmark

```bash
./build.sh
```

### 9.3 Run the Experiment

```bash
/workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 ./df
```

### 9.4 Recorded Results

The recorded experiment produced:

| Metric | Result |
|---|---:|
| Error Interleavings | 4 |
| Timeout Interleavings | 0 |
| Deterministic Replay | 4/4 |
| Bug Type | Double-free |

These results are documented in `experiment_metadata.txt`.

Detailed experimental logs and artifacts are stored in:

```text
experiments/doubleFree/
```

The current reproduction covers the recorded DoubleFree benchmark and does not claim to reproduce the entire evaluation in the original paper.

## 10. Troubleshooting

### 10.1 Docker Command Not Found

If the WSL terminal reports:

```text
bash: docker: command not found
```

Check that Docker Desktop is running and WSL Integration is enabled for Ubuntu.

Close and reopen the WSL terminal, then execute:

```bash
docker --version
```

### 10.2 Container Already Exists

If Docker reports that the container name is already in use, do not create another container with the same name.

Check its status:

```bash
docker ps -a
```

Use `docker start -ai` or `docker exec -it` as appropriate.

### 10.3 Container Is Not Running

Start the existing container:

```bash
docker start -ai period-reproduction
```

### 10.4 SCHED_DEADLINE Permission Error

If the test program reports:

```text
Operation not permitted
```

Check the container privileges and scheduling configuration.

Do not immediately conclude that the WSL2 kernel lacks SCHED_DEADLINE support.

Refer to `sched_deadline_verification.txt` for the recorded test results.

## 11. Reproducibility Notes

- Use the recorded Docker image identification information when preparing the environment.
- Use the specified PERIOD Git commit when checking the source version.
- Keep the existing persistent container if you intend to reuse its environment.
- Do not remove the container unless its contents have been backed up.
- Distinguish host-side software versions from container-side software versions.
- Preserve experiment logs and artifacts for verification.
- Document differences between the reproduction environment and the original paper's environment.

## 12. References

- Original PERIOD repository: https://github.com/wcventure/PERIOD
- Linux SCHED_DEADLINE documentation: https://docs.kernel.org/scheduler/sched-deadline.html
- Docker documentation: https://docs.docker.com/
- Microsoft WSL documentation: https://learn.microsoft.com/en-us/windows/wsl/
