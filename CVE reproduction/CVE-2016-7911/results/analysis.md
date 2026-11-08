# CVE-2016-7911 result analysis

- PERIOD command: `run_PDS.py -d 3 ./2016-7911`
- Interleavings tested: 19
- SEGV error interleavings: 8
- Timeout interleavings: 0
- PERIOD-reported runtime: 12.73331 s

The first saved schedule (`000001_0000003_SEGV`) was replayed with `run_PDS.py -r` and produced another ASan SEGV.

ASan reported a read from `0x000000000004`. Symbolization mapped the failing access to `get_task_ioprio`, line 68, at `p->io_context->ioprio`. The teardown path sets `task->io_context = NULL` under `task_lock`.

This is consistent with a race involving access to `io_context` while another thread detaches or tears it down. The evidence demonstrates a reproducible crash in this benchmark and environment; it does not establish exhaustive detection or a general detection probability.
