# CVE-2016-7911 Reproduction with PERIOD

> Week 1 reproduction record. Environment setup is documented separately by another group member.

## Objective

Reproduce the concurrency bug in PERIOD's CVE-2016-7911 benchmark using static analysis, instrumentation, AddressSanitizer (ASan), and periodical scheduling.

- Benchmark source: `evaluation/ConVul-CVE-Benchmarks/CVE-2016-7911/2016-7911.cpp`
- PERIOD run: `run_PDS.py -d 3 ./2016-7911`
- Sanitizer: AddressSanitizer

## Recorded environment

| Component | Observed value |
|---|---|
| OS kernel | `6.18.54.1-microsoft-standard-WSL2` |
| PERIOD Clang | 10.0.0 |
| Python | 3.14.4 in `~/venvs/period-env` |
| Benchmark | CVE-2016-7911 |
| Bug depth | 3 |

## Procedure

Run from the PERIOD repository root:

```bash
cd ~/PERIOD
source ~/venvs/period-env/bin/activate
source tool/init_env.sh
cd ~/PERIOD/evaluation/ConVul-CVE-Benchmarks/CVE-2016-7911

./cleanDIR.sh
clang -g -emit-llvm -c ./2016-7911.cpp -o 2016-7911.bc
~/PERIOD/tool/staticAnalysis/staticAnalysis.sh 2016-7911

export Con_PATH=$ROOT_DIR/evaluation/ConVul-CVE-Benchmarks/CVE-2016-7911/ConConfig.2016-7911
$ROOT_DIR/tool/staticAnalysis/DBDS-INSTRU/dbds-clang-fast++ \
  -g -fsanitize=address ./2016-7911.cpp \
  -o 2016-7911 -lpthread -ldl

$ROOT_DIR/tool/DBDS/run_PDS.py -d 3 ./2016-7911
```

**Warning:** `cleanDIR.sh` may remove generated output from previous runs. Back up `out_2016-7911_1` before rerunning if you need to preserve schedules.

The first attempt timed out during the sudo-authenticated dry run. After sudo credentials were refreshed in a second terminal, the PDS run completed.

## Results

| Metric | Result |
|---|---:|
| Threads | 2 |
| Maximum key points | 4 |
| Interleavings tested | 19 |
| Error interleavings | **8** |
| Timeout interleavings | **0** |
| Bug depth | 3 |
| Runtime reported by PERIOD | 12.73331 s |

Eight schedules were saved under `out_2016-7911_1/Errors/`:

```text
000001_0000003_SEGV
000002_0000004_SEGV
000003_0000010_SEGV
000004_0000013_SEGV
000005_0000014_SEGV
000006_0000015_SEGV
000007_0000017_SEGV
000008_0000018_SEGV
```

## Replay confirmation

The first saved schedule was replayed:

```bash
$ROOT_DIR/tool/DBDS/run_PDS.py \
  -r out_2016-7911_1/Errors/000001_0000003_SEGV \
  ./2016-7911
```

The output reached `Perform Reproduction!` and AddressSanitizer again reported a SEGV.

## Failure analysis

ASan reported a read from address `0x000000000004` in thread T1. `addr2line` mapped the relevant frames to:

- `get_task_ioprio(struct task_struct*)`, line 68
- `thread_one(void*)`, line 91

The faulting source operation is:

```cpp
ret = p->io_context->ioprio;
```

The competing teardown function contains:

```cpp
task_lock(task);
ioc = task->io_context;
task->io_context = NULL;
task_unlock(task);
```

The observed crash is consistent with a concurrency-sensitive access to `io_context` while another thread detaches/tears down that context. The experiment establishes the SEGV and source location; it does not independently prove every kernel-level lifetime detail.

## Artifact Status

This package includes:

- The original 130-line CVE-2016-7911 benchmark source.
- Eight original PERIOD-generated SEGV schedules.
- Reproduction and schedule replay scripts.
- Twelve experiment screenshots.
- Experiment analysis and PERIOD version information.

Not included:

- Raw terminal execution logs (to be added).
- Compiled executable and LLVM bitcode.
- Generated static analysis intermediate files.

The executable and intermediate files are generated during the reproduction process.

## References

- Cheng Wen, Mengda He, Bohao Wu et al., *Controlled Concurrency Testing via Periodical Scheduling*, ICSE 2022.
- Official PERIOD repository: https://github.com/wcventure/PERIOD

## Additional Reproduction Artifacts

### Benchmark Source

The benchmark source is included at:
`benchmark/2016-7911.cpp`

### Original Error Schedules

Eight original PERIOD-generated schedules are included in:
`schedules/`

### Schedule Replay

After preparing the PERIOD environment and building the instrumented executable:

    bash "CVE reproduction/scripts/replay.sh"

To replay a specific schedule:

    bash "CVE reproduction/scripts/replay.sh" 000002_0000004_SEGV

### Python Environment

Activate the Python environment:

    source ~/venvs/period-env/bin/activate

Initialize PERIOD:

    cd ~/PERIOD
    source tool/init_env.sh
