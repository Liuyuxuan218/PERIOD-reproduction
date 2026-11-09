# DoubleFree Experiment Reproduction

## 1. Purpose

This experiment reproduces the official DoubleFree benchmark provided by [PERIOD](https://github.com/wcventure/PERIOD).

The purpose is to verify whether PERIOD can detect concurrency-related double-free bugs by systematically exploring different thread interleavings.

The benchmark program `df.c` creates two threads that attempt to free the same dynamically allocated memory. Depending on the execution order of the two threads, a double-free error may occur.

We follow the official PERIOD tutorial to build the benchmark, perform systematic controlled concurrency testing, and deterministically reproduce the detected errors using AddressSanitizer (ASAN).

## 2. Experiment Files

This directory contains the experimental records and verification materials generated during our DoubleFree reproduction.

| File or Directory | Description |
|---|---|
| `README.md` | Instructions for building and reproducing the DoubleFree experiment. |
| `build.log` | Records the compilation and build process, including its output. |
| `run.log` | Records the output of PERIOD scheduling exploration. |
| `reproduction.log` | Records the deterministic replay process and its ASAN output. |
| `000002_0000004_double-free_replay.log` | Replay output for the corresponding discovered double-free error. |
| `000003_0000005_double-free_replay.log` | Replay output for the corresponding discovered double-free error. |
| `000004_0000006_double-free_replay.log` | Replay output for the corresponding discovered double-free error. |
| `replay_check.txt` | Records the results of deterministic replay verification. |
| `summary.txt` | Summarizes the main experimental results and reproduction statistics. |
| `errors/` | Contains the four discovered error-interleaving records. |
| `SHA256SUMS` | Contains SHA256 checksums for verifying the integrity of the experimental files. |

These files preserve the results of our completed experiment and provide evidence for the reproduction process.

## 3. Prerequisites

Before starting the experiment, make sure that:

- The PERIOD Docker environment has been successfully configured.
- The PERIOD source code is available inside the Docker container.
- The Docker container is running.
- The required compilation tools and PERIOD scripts are available.

All commands in the following reproduction procedure should be executed inside the PERIOD Docker container, unless otherwise specified.

The official PERIOD source directory in the Docker environment is:

```bash
/workdir/PERIOD
```

## 4. Build the DoubleFree Benchmark

Follow the official PERIOD tutorial to build the DoubleFree benchmark.

### 4.1 Initialize the PERIOD Environment

Navigate to the PERIOD source directory:

```bash
cd /workdir/PERIOD
```

Initialize the environment variables:

```bash
source tool/init_env.sh
```

This initializes the PERIOD environment, including the `ROOT_DIR` variable and the paths required by its tools.

### 4.2 Enter the DoubleFree Directory

```bash
cd "${ROOT_DIR}/test/doubleFree"
```

### 4.3 Clean and Build the Program

Execute the official commands:

```bash
./cleanDIR.sh && ./build.sh
```

The build script performs the following operations:

1. Initializes the required PERIOD environment variables.
2. Cleans previous build artifacts.
3. Compiles `df.c` into LLVM Bitcode (`df.bc`).
4. Performs static analysis using `staticAnalysis.sh`.
5. Instruments the program using DBDS and AddressSanitizer.
6. Links the instrumented object files to generate the executable `df`.

The main components involved include:

- Clang and LLVM for Bitcode generation.
- PERIOD static analysis tools.
- DBDS instrumentation.
- AddressSanitizer (ASAN) for detecting memory errors.

Verify that the executable has been generated:

```bash
ls -lh ./df
```

The executable `df` should be available before proceeding.

**Important:** The official `cleanDIR.sh` script removes previous generated files, including logs, Bitcode files, object files, and the executable. The official `build.sh` also invokes `cleanDIR.sh` internally. Back up any experimental results that need to be preserved before rebuilding.

## 5. Perform Scheduling Exploration

After successfully building the benchmark, use PERIOD to perform systematic controlled concurrency testing based on periodical scheduling.

Execute the following command from the DoubleFree directory:

```bash
"${ROOT_DIR}/tool/DBDS/run_PDS.py" -y -d 3 ./df
```

Parameter descriptions:

- `-y`: Automatically confirms interactive prompts (equivalent to automatically pressing Enter).
- `-d 3`: Sets the maximum bug search depth to 3.

PERIOD explores scheduling interleavings across bug depths 1, 2, and 3.

## 6. Expected Results

If PERIOD works correctly, the output should indicate that four buggy interleavings have been discovered.

The following is the expected output based on the official PERIOD DoubleFree tutorial. The exact formatting of terminal output may vary.

```text
Start Testing!
Targeting bugs that bug depth = 1 . Iterate for 2 periods
test 0001: [[0, 0], [1, 1]]
test 0002: [[1, 1], [0, 0]]
Targeting bugs that bug depth = 2 . Iterate for 3 periods
test 0003: [[0], [1, 1], [0]]
        [Error Found]: NO.1 double-free
        The interleavings saved in out_df_1/Errors/000001_0000003_double-free
test 0004: [[1], [0, 0], [1]]
        [Error Found]: NO.2 double-free
        The interleavings saved in out_df_1/Errors/000002_0000004_double-free
Targeting bugs that bug depth = 3 . Iterate for 4 periods
test 0005: [[0], [1], [0], [1]]
        [Error Found]: NO.3 double-free
        The interleavings saved in out_df_1/Errors/000003_0000005_double-free
test 0006: [[1], [0], [1], [0]]
        [Error Found]: NO.4 double-free
        The interleavings saved in out_df_1/Errors/000004_0000006_double-free
End Testing!
```

### 6.1 Expected Experimental Statistics

The expected results are:

| Metric | Expected Result |
|---|---:|
| Total schedules explored | 6 |
| Total Error Interleavings | 4 |
| Total Timeouts Interleavings | 0 |
| Detected DoubleFree Errors | 4 |

A successful reproduction should identify four buggy interleavings, all classified as double-free errors.

The four error records should be generated under:

```text
out_df_1/Errors/
```

### 6.2 Understanding the Scheduling Output

Each schedule represents an execution order of the two threads.

For example:

```text
[[1], [0, 0], [1]]
```

This represents:

- The first period: Thread 1 executes one key point.
- The second period: Thread 0 executes two key points.
- The third period: Thread 1 executes another key point.

Different execution orders may expose different concurrency errors.

The detection of four buggy interleavings confirms that PERIOD successfully identifies the DoubleFree problem in this benchmark.

## 7. Deterministically Reproduce a DoubleFree Error

After scheduling exploration, PERIOD saves the discovered buggy interleavings.

To deterministically reproduce one of the discovered errors, use the following command from the DoubleFree directory:

```bash
"${ROOT_DIR}/tool/DBDS/run_PDS.py" \
  -r out_df_1/Errors/000001_0000003_double-free ./df
```

The `-r` option instructs PERIOD to replay the specified buggy interleaving.

### 7.1 Expected ASAN Output

If the replay successfully reproduces the bug, AddressSanitizer should report a double-free error.

The important output should contain:

```text
ERROR: AddressSanitizer: attempting double-free
```

The report should also contain a summary similar to:

```text
SUMMARY: AddressSanitizer: double-free
```

The process may terminate abnormally after ASAN detects the error. This is expected behavior during successful bug reproduction.

### 7.2 Verification Criteria

The DoubleFree reproduction is considered successful when:

1. The benchmark builds successfully.
2. PERIOD explores six schedules.
3. Four double-free error interleavings are discovered.
4. No timeout interleavings are reported.
5. The discovered buggy interleavings can be deterministically replayed.
6. ASAN reports `attempting double-free` during replay.

Our recorded experiment confirmed all four discovered errors through deterministic replay.

## 8. Experimental Data Management

The reproduction procedure described above follows the official PERIOD tutorial.

**The reproduction process is complete at this point.**

For our group's convenience, we additionally use a Docker Bind Mount to store intermediate files and experimental outputs in a dedicated WSL directory. This allows experimental data to be managed independently of the Docker container and makes it easier to select and upload relevant results to GitHub.

The mounted directory is available inside the container at:

```text
/experiment-data
```

The corresponding WSL host directory is:

```text
~/period-reproduction
```

This additional data-management procedure is optional and is not required to reproduce the DoubleFree benchmark.

If the mounted directory is available, generated experimental files can be copied there after the experiment:

```bash
mkdir -p /experiment-data/doubleFree-run

cp -a out_df_1 /experiment-data/doubleFree-run/
```

Additional logs can also be copied when available:

```bash
for file in build.log run.log reproduction.log; do
    if [ -f "$file" ]; then
        cp -a "$file" /experiment-data/doubleFree-run/
    fi
done
```

Files saved under `/experiment-data` are accessible from the WSL host directory and can subsequently be reviewed and selectively committed to the group's GitHub repository.

Readers who only want to reproduce the experiment can skip this additional data-copying procedure.

## 9. File Integrity Verification

To verify the integrity of the experimental records, execute the following command from the root directory of the reproduction repository:

```bash
sha256sum -c experiments/doubleFree/SHA256SUMS
```

All listed files should report `OK` if their contents match the recorded checksums.

This provides an additional check that the stored experimental records have not been unintentionally modified.
