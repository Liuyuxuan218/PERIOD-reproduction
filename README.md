# PERIOD Reproduction

Reproduction work for the paper:

**Controlled Concurrency Testing via Periodical Scheduling (ICSE 2022)**

## 1. Original Project

Official repository: https://github.com/wcventure/PERIOD

## 2. Reproduction Scope

The current reproduction focuses on the official DoubleFree benchmark provided by PERIOD.

The experiment includes:
- Building the DoubleFree benchmark.
- Running PERIOD scheduling exploration.
- Collecting discovered error interleavings.
- Replaying discovered errors to verify reproducibility.

This repository records the completed DoubleFree experiment and does not claim that the entire paper has been fully reproduced.

## 3. Experimental Environment

- Operating system: Ubuntu on WSL2
- Container runtime: Docker
- Docker image: period:latest
- PERIOD source commit: b6f72a7b06d01ffa7114b640312873ec2578a5ea

## 4. DoubleFree Experiment

Experiment directory: `experiments/doubleFree/`

Build commands (inside the PERIOD Docker container):

    cd /workdir/PERIOD/test/doubleFree
    ./build.sh

Scheduling exploration command:

    /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 ./df

### Experimental Results

| Metric | Result |
|---|---:|
| Total Error Interleavings | 4 |
| Total Timeouts Interleavings | 0 |
| Discovered double-free errors | 4 |
| Deterministic replay confirmed | 4/4 |

All four discovered error interleavings were identified as double-free errors.

See [DoubleFree Experiment README](experiments/doubleFree/README.md) for details.

## 5. Repository Structure

    .
    ├── environment/
    ├── experiments/
    │   └── doubleFree/
    │       ├── errors/
    │       ├── README.md
    │       └── SHA256SUMS
    └── README.md

## 6. File Integrity

Run from the repository root:

    sha256sum -c experiments/doubleFree/SHA256SUMS
