
cat > environment/README.md <<'EOF'
# PERIOD Reproduction Environment

This document describes how to prepare the PERIOD reproduction environment using Docker, configure persistent experimental data storage, verify the software environment, and access the experimental records.

The setup follows the official PERIOD repository and provides additional instructions for WSL2 and Docker Desktop users.

## 1. Requirements

Before installing PERIOD, make sure that your machine satisfies the following requirements.

### 1.1 Hardware Requirements

- A multi-core processor.
- Sufficient memory and disk space for Docker images, source code, and experimental data.
- Multi-core processors are recommended for concurrency testing.

### 1.2 Operating System Requirements

- Ubuntu 18.04 LTS or later.
- Linux kernel version 4.x or later.
- Windows users can use Ubuntu through WSL2.

### 1.3 Docker Requirements

- Docker version higher than 18.09.7.
- Docker must be running and accessible from the Ubuntu terminal.

For Windows users, Docker Desktop with WSL2 integration is recommended.

Official installation resources:

- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- [Docker Engine Installation on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Desktop WSL2 Backend](https://docs.docker.com/desktop/features/wsl/)
- [Microsoft WSL Installation Guide](https://learn.microsoft.com/en-us/windows/wsl/install)

For Windows users, make sure that WSL2 integration is enabled for the Ubuntu distribution in Docker Desktop.

Verify the installation:

```bash
wsl --version
wsl -l -v
docker --version
docker info
```

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

## 3. Prepare the Docker Image

The official PERIOD documentation provides instructions for running the project using Docker.

The expected image name is:

```text
period:latest
```

Check whether the image is available:

```bash
docker image inspect period:latest
```

If the image is not available, prepare it using the official image distribution or the Docker build instructions provided by the original PERIOD repository.

If the official repository provides a Dockerfile in the directory used for building the image, build it from that directory:

```bash
docker build -t period:latest .
```

After preparing the image, verify it:

```bash
docker image inspect period:latest
```

Record the image ID and digest for reproducibility:

```bash
docker image inspect --format '{{.Id}}' period:latest
docker image inspect --format '{{json .RepoDigests}}' period:latest
```

Note that `latest` is a mutable image tag. The image ID and digest should be recorded when documenting the experimental environment.

## 4. Create and Run the Docker Container

The official PERIOD documentation provides the following basic Docker command:

```bash
docker run --privileged -it period:latest /bin/bash
```

This command starts an interactive container with privileged permissions.

For repeated experiments, a persistent container is recommended.

### 4.1 Create a Persistent Container

A persistent container allows the experimental environment to be reused without creating a new container every time.

The container can be created using:

```bash
docker run --privileged -it \
  --name period-container \
  period:latest \
  /bin/bash
```

The container name is `period-container`.

The container is persistent because the `--rm` option is not specified.

### 4.2 Enter an Existing Container

Check the container status:

```bash
docker ps -a
```

If the container is running:

```bash
docker exec -it period-container bash
```

If the container is stopped:

```bash
docker start -ai period-container
```

### 4.3 Exit and Stop the Container

Exit the container:

```bash
exit
```

Stop the container manually:

```bash
docker stop period-container
```

The container can be restarted without rebuilding the image.

Important:

- Do not use `--rm` when creating a persistent container.
- Exiting a container does not necessarily delete it.
- Removing a container deletes its writable layer.
- Files stored in a separately mounted host directory remain available after the container is removed.

## 5. Experiment Data Persistence and Directory Mounting

During PERIOD experiments, intermediate files, execution logs, and generated results may be produced inside the Docker container.

To preserve experimental data independently of the container lifecycle, we use a directory in WSL Ubuntu and mount it into Docker.

### 5.1 Prepare the Experiment Data Directory

Return to the WSL Ubuntu terminal.

Create the experiment data directory:

```bash
mkdir -p "$HOME/period-reproduction"
```

The directory is used to store experimental records and generated data.

The current reproduction environment already uses this directory to preserve experimental files.

Its existing contents should be retained.

### 5.2 Configure the Directory Mount

Docker Bind Mounts must be configured when a container is created.

An existing container that was created without a mount cannot have a new Bind Mount added directly.

Therefore, when creating a container with persistent experimental data storage, use the following command:

```bash
docker run --privileged -it \
  --name period-container \
  --mount "type=bind,source=$HOME/period-reproduction,target=/experiment-data" \
  period:latest \
  /bin/bash
```

This command mounts the WSL directory into the Docker container.

The directory mapping is:

| WSL Host Directory | Docker Container Directory |
|---|---|
| `$HOME/period-reproduction` | `/experiment-data` |

The same files can be accessed from both WSL Ubuntu and the Docker container.

If a container with the same name already exists, do not execute the creation command again. A new container name or an appropriately backed-up replacement container is required.

### 5.3 Verify the Mount

After entering the container, check the mounted directory:

```bash
ls -la /experiment-data
```

The existing WSL experimental data should be visible inside the container.

Create a test file:

```bash
echo "Docker mount test" > /experiment-data/mount_test.txt
```

Exit the container:

```bash
exit
```

Return to WSL Ubuntu and check the file:

```bash
cat "$HOME/period-reproduction/mount_test.txt"
```

Expected output:

```text
Docker mount test
```

If the expected output appears, the directory mount is working correctly.

After verification, the test file can be removed:

```bash
rm "$HOME/period-reproduction/mount_test.txt"
```

### 5.4 Save Experimental Logs and Intermediate Data

Files written to `/experiment-data` are stored in the WSL host directory.

For example, save an experiment log using:

```bash
your_experiment_command > /experiment-data/run.log 2>&1
```

Append additional output to an existing log:

```bash
your_experiment_command >> /experiment-data/run.log 2>&1
```

To copy generated experiment files into the persistent data directory:

```bash
cp -r /path/to/generated/results /experiment-data/
```

Replace the example source path with the actual location of the generated results.

Important:

- Files written inside `/experiment-data` are preserved independently of the container.
- Files written elsewhere inside the container are not automatically saved in the WSL data directory.
- If the container is removed, files that were not stored in a mounted directory may be lost.
- The existing WSL experiment data directory should not be deleted when recreating containers.

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
