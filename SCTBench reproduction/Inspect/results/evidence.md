# Evidence status

Historical `metrics.json` files were not modified.
Each `run.log.gz` is a lossless gzip copy of the local scheduler log whose start time, command, exit status, and parsed counts match that repetition.
`run.log.sha256` is the SHA-256 of the uncompressed log.
The execution workflow that produced these runs retained at most two files in each Errors or Timeouts directory. Those remaining files were copied unchanged. Deleted files were not reconstructed from the metrics.
A build log is included only when its recorded time is not later than the earliest submitted run of that program.
These records do not contain the source, toolchain, and executable fingerprint now required before a run can be reused. They remain historical records.

## Recovered

- `Inspect.boundedbuffer/rep01`
  - [run.log.gz](cases/Inspect.boundedbuffer/rep01/run.log.gz) ([checksum](cases/Inspect.boundedbuffer/rep01/run.log.sha256))
  - [command.json](cases/Inspect.boundedbuffer/rep01/command.json)
  - [output.sha256](cases/Inspect.boundedbuffer/rep01/output.sha256) lists 2 unchanged output file(s)
- `Inspect.boundedbuffer/rep02`
  - [run.log.gz](cases/Inspect.boundedbuffer/rep02/run.log.gz) ([checksum](cases/Inspect.boundedbuffer/rep02/run.log.sha256))
  - [command.json](cases/Inspect.boundedbuffer/rep02/command.json)
  - [output.sha256](cases/Inspect.boundedbuffer/rep02/output.sha256) lists 2 unchanged output file(s)
- `Inspect.boundedbuffer/rep03`
  - [run.log.gz](cases/Inspect.boundedbuffer/rep03/run.log.gz) ([checksum](cases/Inspect.boundedbuffer/rep03/run.log.sha256))
  - [command.json](cases/Inspect.boundedbuffer/rep03/command.json)
  - [output.sha256](cases/Inspect.boundedbuffer/rep03/output.sha256) lists 3 unchanged output file(s)
- `Inspect.qsort_mt/rep01`
  - [run.log.gz](cases/Inspect.qsort_mt/rep01/run.log.gz) ([checksum](cases/Inspect.qsort_mt/rep01/run.log.sha256))
  - [command.json](cases/Inspect.qsort_mt/rep01/command.json)
  - [output.sha256](cases/Inspect.qsort_mt/rep01/output.sha256) lists 2 unchanged output file(s)
- `Inspect.qsort_mt/rep02`
  - [run.log.gz](cases/Inspect.qsort_mt/rep02/run.log.gz) ([checksum](cases/Inspect.qsort_mt/rep02/run.log.sha256))
  - [command.json](cases/Inspect.qsort_mt/rep02/command.json)
  - [output.sha256](cases/Inspect.qsort_mt/rep02/output.sha256) lists 2 unchanged output file(s)
- `Inspect.qsort_mt/rep03`
  - [run.log.gz](cases/Inspect.qsort_mt/rep03/run.log.gz) ([checksum](cases/Inspect.qsort_mt/rep03/run.log.sha256))
  - [command.json](cases/Inspect.qsort_mt/rep03/command.json)
  - [output.sha256](cases/Inspect.qsort_mt/rep03/output.sha256) lists 2 unchanged output file(s)

## Build records

- `Inspect.boundedbuffer`: [build.json](cases/Inspect.boundedbuffer/build.json), [build.log](cases/Inspect.boundedbuffer/build.log)
- `Inspect.qsort_mt`: [build.json](cases/Inspect.qsort_mt/build.json), [build.log](cases/Inspect.qsort_mt/build.log)

## Missing raw logs

None.
