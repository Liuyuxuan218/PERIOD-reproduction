# DoubleFree Experiment

## 1. Objective

Reproduce the official DoubleFree benchmark provided by PERIOD.

## 2. Build

Run the following commands inside the PERIOD Docker container:

    cd /workdir/PERIOD/test/doubleFree
    ./build.sh

## 3. Scheduling Exploration

Run the following command inside the PERIOD Docker container:

    /workdir/PERIOD/tool/DBDS/run_PDS.py -y -d 3 ./df

## 4. Experimental Results

The experiment produced the following results:

| Metric | Result |
|---|---:|
| Total Error Interleavings | 4 |
| Total Timeouts Interleavings | 0 |
| Double-free error records | 4 |
| Deterministic replay confirmed | 4/4 |

All four discovered errors were identified as double-free errors.

## 5. Experiment Files

- `build.log`: Compilation output.
- `run.log`: Scheduling exploration output.
- `reproduction.log`: Deterministic replay output.
- `*_replay.log`: Replay logs for the other error records.
- `replay_check.txt`: Replay verification results.
- `summary.txt`: Experiment summary.
- `errors/`: Four discovered error records.
- `SHA256SUMS`: File integrity checksums.

## 6. Verification

Run the following command from the repository root to verify file integrity:

    sha256sum -c experiments/doubleFree/SHA256SUMS
