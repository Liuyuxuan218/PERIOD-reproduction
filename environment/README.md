
cat > environment/README.md <<'EOF'
# PERIOD Reproduction Environment

This document describes how to prepare the PERIOD reproduction environment using Docker, configure persistent experimental data storage, verify the software environment, and access the experimental records.

The setup follows the official PERIOD repository and provides additional instructions for WSL2 and Docker Desktop users.


## 1. Requirements

Before installing PERIOD, make sure that your machine satisfies the following requirements.

### 1.1 Hardware Requirements

- A workstation or PC with a multi-core processor.
- Sufficient memory and disk space for Docker images, source code, and experimental data.

Multi-core processors are recommended because PERIOD is a concurrency testing tool.

### 1.2 Operating System Requirements

- Ubuntu 18.04 LTS or later.
- Linux kernel version 4.x or later.
- Windows users can use Ubuntu through WSL2.

### 1.3 Docker Requirements

- Docker version higher than 18.09.7.
- Docker must be installed, running, and accessible from the Ubuntu terminal.

For Linux users installing Docker directly on Ubuntu, Docker can be installed using:

```bash
sudo apt-get update
sudo apt-get install docker.io
```

For Windows users, Docker Desktop with WSL2 integration is recommended.

Official installation resources:

- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Docker Engine Installation on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Desktop WSL2 Backend](https://docs.docker.com/desktop/features/wsl/)
- [Microsoft WSL Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install)

Windows users should enable WSL2 integration for their Ubuntu distribution in Docker Desktop.

### 1.4 Verify the Host Environment

For Windows users, open PowerShell and check the WSL configuration:

```powershell
wsl --version
wsl -l -v
```

Make sure that the Ubuntu distribution is running under WSL 2.

Then open the WSL Ubuntu terminal and verify Docker:

```bash
docker --version
docker info
```

If Docker is not accessible, check that Docker Desktop is running and WSL2 integration is enabled.

## 2. Clone the Official PERIOD Repository

The original PERIOD source code is maintained at:

https://github.com/wcventure/PERIOD

Clone the official repository in the WSL Ubuntu terminal:

```bash
git clone https://github.com/wcventure/PERIOD.git
```

Enter the source directory:

```bash
cd PERIOD
```

Define the project root automatically:

```bash
export PERIOD_ROOT="$(git rev-parse --show-toplevel)"
```

Verify the source directory:

```bash
echo "$PERIOD_ROOT"
ls "$PERIOD_ROOT"
```

This environment variable is used in subsequent commands to avoid hard-coded user-specific paths.

The source commit used in our reproduction is recorded separately in `period_source_version.txt` in the reproduction repository.


## 3. Install the PERIOD Docker Image

The official PERIOD project provides two ways to prepare the Docker image.

### 3.1 Option A: Pull the Official Pre-built Image (Recommended)

Download the official PERIOD image from Docker Hub:

```bash
docker pull wcventure/period:stable
```

Tag the downloaded image as `period:latest`:

```bash
docker tag wcventure/period:stable period:latest
```

This is the recommended method because the official image already contains the configured PERIOD environment.

### 3.2 Option B: Build the Docker Image from Source

Alternatively, users can build their own Docker image using the Dockerfile provided in the official PERIOD repository.

First, enter the root directory of the cloned repository:

```bash
cd "$PERIOD_ROOT"
```

Build the image:

```bash
docker build -t period:latest --no-cache ./
```

The `--no-cache` option prevents Docker from reusing previously cached build layers.

### 3.3 Verify the Docker Image

After completing either installation method, verify that the image is available:

```bash
docker image inspect period:latest
```

Display the image ID:

```bash
docker image inspect --format '{{.Id}}' period:latest
```

Display the repository digest, if available:

```bash
docker image inspect --format '{{json .RepoDigests}}' period:latest
```

The image should be available locally with the tag `period:latest`.

The two installation methods are alternatives. Only one is required.


## 4. Create and Run the Docker Container

The official PERIOD documentation provides the following basic Docker command:

```bash
docker run --privileged -it period:latest /bin/bash
```

This command creates a new container and opens an interactive Bash shell.

For repeated experiments and persistent data storage, we recommend creating a named container with a mounted host directory. The complete procedure is described in Section 5.

### 4.1 Create a Persistent Container

For the recommended setup, create the experiment data directory first, as described in Section 5. Then create the container with the required mount configuration.

The recommended container is named `period-container`.

The container is persistent because the `--rm` option is not used.

### 4.2 Enter an Existing Container

Check the container status:

```bash
docker ps -a
```

If the container is running, open another Bash session:

```bash
docker exec -it period-container bash
```

If the container is stopped, restart it:

```bash
docker start -ai period-container
```

### 4.3 Exit and Stop the Container

Exit the container:

```bash
exit
```

To stop the container manually from the WSL terminal:

```bash
docker stop period-container
```

The container can be restarted without rebuilding the Docker image.

Important:

- Do not use `--rm` when creating a persistent container.
- Exiting a container does not necessarily delete it.
- Removing a container deletes its writable layer.
- Files stored in a separately mounted host directory remain available even after the container is removed.


## 5. Experiment Data Persistence and Directory Mounting

During PERIOD experiments, intermediate files, execution logs, and generated results may be produced inside the Docker container.

To preserve these files independently of the container lifecycle, we use a directory in WSL Ubuntu and mount it into Docker.

### 5.1 Create the Experiment Data Directory

Return to the WSL Ubuntu terminal.

Create the experiment data directory:

```bash
mkdir -p "$HOME/period-reproduction"
```

This directory is used to store experimental records, logs, intermediate files, and generated results.

If the directory already exists and contains experimental data, keep its existing contents. Do not delete or overwrite the directory.

### 5.2 Create a Container with the Data Directory Mounted

Docker Bind Mounts must be configured when a container is created.

An existing container that was created without a mount cannot have a new Bind Mount added directly.

Create a persistent container with the experiment data directory mounted:

```bash
docker run --privileged -it \
  --name period-container \
  --mount "type=bind,source=$HOME/period-reproduction,target=/experiment-data" \
  period:latest \
  /bin/bash
```

This command:

- Creates a container named `period-container`.
- Enables privileged mode for the PERIOD environment.
- Mounts the WSL experiment data directory into the container.
- Opens an interactive Bash shell.

The directory mapping is:

| WSL Host Directory | Docker Container Directory |
|---|---|
| `$HOME/period-reproduction` | `/experiment-data` |

Files written to `/experiment-data` inside the container are stored directly in the WSL host directory.

Note: If a container named `period-container` already exists, Docker cannot create another container with the same name. Check existing containers using `docker ps -a` and choose an unused container name if necessary.

### 5.3 Verify the Directory Mount

After entering the container, check the mounted directory:

```bash
ls -la /experiment-data
```

The existing files in the WSL experiment data directory should be visible inside the container.

To verify that the mount works correctly, create a test file:

```bash
echo "Docker mount test" > /experiment-data/mount_test.txt
```

Exit the container:

```bash
exit
```

Return to the WSL Ubuntu terminal and check the test file:

```bash
cat "$HOME/period-reproduction/mount_test.txt"
```

Expected output:

```text
Docker mount test
```

If the expected output appears, the directory mount is working correctly.

Remove the test file after verification:

```bash
rm "$HOME/period-reproduction/mount_test.txt"
```

### 5.4 Save Experimental Logs and Intermediate Data

Files written to `/experiment-data` are stored in the WSL host directory.

For example, redirect an experiment's output to a log file:

```bash
your_experiment_command > /experiment-data/run.log 2>&1
```

To append output to an existing log:

```bash
your_experiment_command >> /experiment-data/run.log 2>&1
```

To copy generated experimental files into the persistent data directory:

```bash
cp -r /path/to/generated/results /experiment-data/
```

Replace the example source path with the actual location of the generated results.

The corresponding files can be accessed directly from WSL Ubuntu under:

```text
~/period-reproduction/
```

Important:

- Files written inside `/experiment-data` are preserved independently of the container.
- Files written elsewhere inside the container are not automatically saved in the WSL data directory.
- If the container is removed, files that were not stored in a mounted directory may be lost.
- The WSL experiment data directory should not be deleted when recreating containers.
- Do not use the `--rm` option if you want to preserve the container itself.

## 6. Environment Verification

After entering the Docker container, verify the environment.

### 6.1 Operating System and Kernel

```bash
cat /etc/os-release
uname -a
```

Note that Docker containers share the Linux kernel provided by the host environment.

When using WSL2, the kernel reported by `uname -a` is the WSL2 Linux kernel.

### 6.2 Compiler and Build Tools

```bash
gcc --version
g++ --version
make --version
cmake --version
ld --version
```

### 6.3 LLVM and Clang

```bash
clang --version
llvm-config --version
```

### 6.4 Python and Dependencies

```bash
python --version
pip show wllvm
pip show numpy
```

The recorded environment versions are documented in the following files:

- `host_environment.txt`
- `container_environment.txt`
- `docker_image.txt`

These records distinguish between the host environment and the software environment inside the Docker container.

## 7. Run Experiments

After completing the environment setup and verification, proceed to the experimental reproduction.

Detailed instructions for building and running the DoubleFree benchmark, including the execution procedure and result verification, are provided in the experiment documentation.

Please refer to:

[DoubleFree Experiment Guide](../experiments/doubleFree/README.md)

The experiment guide is the primary reference for the actual DoubleFree reproduction procedure.

## 8. Experiment Documentation

The `experiments/doubleFree/` directory contains the experimental instructions, execution logs, generated error cases, and verification records.

The following table describes the main files and directories:

| File or Directory | Description |
|---|---|
| `README.md` | Instructions for reproducing the DoubleFree experiment |
| `build.log` | Compilation process and build output |
| `run.log` | Recorded experimental execution log |
| `reproduction.log` | Recorded bug reproduction process |
| `replay_check.txt` | Deterministic replay verification records |
| `summary.txt` | Summary of experimental results |
| `SHA256SUMS` | SHA-256 checksums for verifying recorded files |
| `errors/` | Generated error cases identified during testing |
| `*_double-free_replay.log` | Replay logs corresponding to detected double-free cases |

These files provide evidence of the experimental process and support the verification of the reproduced results.

The original experiment records are preserved separately from the environment setup instructions.

## 9. References

- [Official PERIOD Repository](https://github.com/wcventure/PERIOD)
- [Official PERIOD Requirements](https://github.com/wcventure/PERIOD/blob/master/REQUIREMENTS.md)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Docker Engine Installation on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Desktop WSL2 Backend](https://docs.docker.com/desktop/features/wsl/)
- [Microsoft WSL Documentation](https://learn.microsoft.com/en-us/windows/wsl/)
- [Docker Bind Mount Documentation](https://docs.docker.com/engine/storage/bind-mounts/)

EOF
