# Evidence status

Historical `metrics.json` files were not modified.
Each `run.log.gz` is a lossless gzip copy of the local scheduler log whose start time, command, exit status, and parsed counts match that repetition.
`run.log.sha256` is the SHA-256 of the uncompressed log.
The execution workflow that produced these runs retained at most two files in each Errors or Timeouts directory. Those remaining files were copied unchanged. Deleted files were not reconstructed from the metrics.
A build log is included only when its recorded time is not later than the earliest submitted run of that program.
These records do not contain the source, toolchain, and executable fingerprint now required before a run can be reused. They remain historical records.

## Recovered

- `Misc.safestack/rep01`
  - [run.log.gz](cases/Misc.safestack/rep01/run.log.gz) ([checksum](cases/Misc.safestack/rep01/run.log.sha256))
  - [command.json](cases/Misc.safestack/rep01/command.json)
  - no error or timeout file remained in this repetition
- `Misc.safestack/rep02`
  - [run.log.gz](cases/Misc.safestack/rep02/run.log.gz) ([checksum](cases/Misc.safestack/rep02/run.log.sha256))
  - [command.json](cases/Misc.safestack/rep02/command.json)
  - no error or timeout file remained in this repetition
- `Misc.safestack/rep03`
  - [run.log.gz](cases/Misc.safestack/rep03/run.log.gz) ([checksum](cases/Misc.safestack/rep03/run.log.sha256))
  - [command.json](cases/Misc.safestack/rep03/command.json)
  - no error or timeout file remained in this repetition

## Build records

- `Misc.safestack`: [build.json](cases/Misc.safestack/build.json), [build.log](cases/Misc.safestack/build.log)

## Missing raw logs

None.
