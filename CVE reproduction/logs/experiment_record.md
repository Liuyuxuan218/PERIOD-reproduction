# CVE-2016-7911 Experiment Record

Date: 2026-11-05
Benchmark: CVE-2016-7911
Tool: PERIOD
Bug depth: 3

Note: This record was organized from the terminal outputs captured during the experiment. It is not an unedited raw terminal log.

## 1. PERIOD Execution

Command:

    ~/PERIOD/tool/DBDS/run_PDS.py -d 3 ./2016-7911

The initial dry run completed successfully.

The program exited successfully under default system scheduling.

Reported information:

- ThreadNum: 2
- MaxKpNum: 4
- kpNumArray: 3 4
- Bug depth: 3

## 2. PDS Testing Results

PERIOD tested 19 interleavings.

| Metric | Result |
|---|---:|
| Interleavings tested | 19 |
| Error interleavings | 8 |
| Timeout interleavings | 0 |
| SEGV errors | 8 |
| Bug depth | 3 |

The eight error schedules were:

- 000001_0000003_SEGV
- 000002_0000004_SEGV
- 000003_0000010_SEGV
- 000004_0000013_SEGV
- 000005_0000014_SEGV
- 000006_0000015_SEGV
- 000007_0000017_SEGV
- 000008_0000018_SEGV

PERIOD-reported runtime: 12.73331 seconds.

## 3. Schedule Replay

The first saved schedule was replayed using:

    ~/PERIOD/tool/DBDS/run_PDS.py \
      -r out_2016-7911_1/Errors/000001_0000003_SEGV \
      ./2016-7911

The output reached:

    Perform Reproduction!

AddressSanitizer reported a SEGV again.

## 4. Error Details

ASan reported:

    SEGV on unknown address 0x000000000004

The failing access was mapped to:

    get_task_ioprio() - line 68
    thread_one() - line 91

The source operation was:

    ret = p->io_context->ioprio;

The replay therefore confirmed that the saved schedule could trigger the reported crash again.

## 5. Notes

The eight schedule files are preserved in the schedules directory.

The screenshots are preserved in the screenshots directory.

This record summarizes the observed experiment results. It does not claim that every possible thread interleaving was tested.
