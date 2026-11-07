# PERIOD Reproduction Environment

This directory documents the software environment, Docker image, container configuration, and basic procedures used in the reproduction of the PERIOD project.

The purpose of this documentation is to make the experimental environment easier to inspect, reuse, and reproduce.

## 1. Directory Contents

This directory contains the following environment records:

| File | Description |
|---|---|
| `period_source_version.txt` | PERIOD source repository and Git commit used in the experiment |
| `docker_image.txt` | Docker image identification and container information |
| `container_environment.txt` | Operating system, compiler, build tools, and Python environment inside the container |
| `host_environment.txt` | Host system and Docker installation information |
| `experiment_metadata.txt` | Summary of the recorded experimental results |

## 2. Docker Image

The experiment uses the PERIOD Docker image.

- Image tag: `period:latest`
- Immutable image reference:

```text
period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
```

- Image ID:

```text
sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc
```

Using the immutable image reference helps identify the exact image used for the experiment.

To inspect the local image:

```bash
docker image inspect period:latest
```

## 3. Docker Container Setup

A persistent Docker container named `period-reproduction` was created from the image.

The container was created with `--privileged` and without `--rm`, so it is not automatically deleted when the container stops.

The original creation command was:

```bash
docker run --privileged -it \
  --name period-reproduction \
  period@sha256:8f47d8b9148f2db579627842026e722d0f205ddeab13e70ee41a8df3dbd59fbc \
  bash
```

**Important:** This command is for initial container creation only. If the container already exists, do not run this command again with the same container name.

## 4. Container Management

The container is persistent. Exiting the interactive shell does not remove it.

### 4.1 Check Container Status

```bash
docker ps -a
```

### 4.2 Restart a Stopped Container

When the container is stopped, start it and attach to its original interactive Bash session:

```bash
docker start -ai period-reproduction
```

This is the recommended way to restart and enter this container.

### 4.3 Open an Additional Shell in a Running Container

If the container is already running, you can open another Bash session:

```bash
docker exec -it period-reproduction bash
```

This command requires the container to be running.

### 4.4 Exit the Container

Inside the container:

```bash
exit
```

Exiting the original Bash session started by `docker start -ai` stops the container, but does not delete it. Exiting an additional shell opened with `docker exec` only ends that shell session.

### 4.5 Stop the Container Manually

From the host terminal:

```bash
docker stop period-reproduction
```

The stopped container can be started again using `docker start -ai period-reproduction`.

**Note:** Avoid using `docker rm` or `docker run --rm` if you intend to preserve this container.

## 5. PERIOD Source Code

The PERIOD source code used in this experiment is from:

Repository: https://github.com/wcventure/PERIOD

Git commit:

```text
b6f72a7b06d01ffa7114b640312873ec2578a5ea
```

The source code is located inside the container at:

```text
/workdir/PERIOD
```

To enter the source directory:

```bash
cd /workdir/PERIOD
```

To verify the source version:

```bash
git rev-parse HEAD
git status --short
```

The recorded experiment used the source commit specified above with a clean working tree.

## 6. Environment Information

The experiment was conducted in a Docker container running Ubuntu 18.04.5 LTS.

The main software versions inside the container include:

| Component | Version |
|---|---|
| Ubuntu | 18.04.5 LTS |
| GCC | 7.5.0 |
| G++ | 7.5.0 |
| GNU Make | 4.1 |
| CMake | 3.10.2 |
| GNU Binutils ld | 2.30 |
| Clang | 10.0.0 |
| LLVM | 10.0.0 |
| Python | 2.7.17 |

Additional package information and host-side configuration are recorded in `container_environment.txt` and `host_environment.txt`.

## 7. Reproducing the DoubleFree Experiment

The recorded experiment targets:

```text
/workdir/PERIOD/test/doubleFree
```

After entering the container, navigate to the test directory:

```bash
cd /workdir/PERIOD/test/doubleFree
```

Build the test program:

```bash
./build.sh
```

Run PERIOD:

```bash
/workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 ./df
```

The recorded experiment produced:

- Total error interleavings: 4
- Total timeout interleavings: 0
- Deterministic replay confirmations: 4/4
- Bug type: double-free

These are the results of the recorded experiment. They are documented in `experiment_metadata.txt`.

For the detailed experimental artifacts, see:

```text
experiments/doubleFree/
```

## 8. Previous Container

A previous container with the short ID `8fa44dc533c9` was used during the earlier experimental work.

That container no longer exists in Docker. The exact mechanism by which it was removed has not been independently verified.

The current persistent container, `period-reproduction`, was created as a replacement to provide a reusable environment for subsequent work.

## 9. Reproducibility Notes

- Use the recorded immutable Docker image reference when identifying the experimental image.
- Use the recorded PERIOD Git commit when checking the source version.
- Keep the existing persistent container if you want to reuse its environment.
- Exiting the container does not delete it.
- The environment records distinguish between the host system and the software environment inside the Docker container.
- Experimental results should be interpreted together with the corresponding experiment metadata and artifacts.
