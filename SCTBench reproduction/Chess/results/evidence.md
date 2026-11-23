# Evidence status

Historical `metrics.json` files were not modified.
Each `run.log.gz` is a lossless gzip copy of the local scheduler log whose start time, command, exit status, and parsed counts match that repetition.
`run.log.sha256` is the SHA-256 of the uncompressed log.
The execution workflow that produced these runs retained at most two files in each Errors or Timeouts directory. Those remaining files were copied unchanged. Deleted files were not reconstructed from the metrics.
A build log is included only when its recorded time is not later than the earliest submitted run of that program.
These records do not contain the source, toolchain, and executable fingerprint now required before a run can be reused. They remain historical records.

## Recovered

- `Chess.IWSQ/rep01`
  - [run.log.gz](cases/Chess.IWSQ/rep01/run.log.gz) ([checksum](cases/Chess.IWSQ/rep01/run.log.sha256))
  - [command.json](cases/Chess.IWSQ/rep01/command.json)
  - [output.sha256](cases/Chess.IWSQ/rep01/output.sha256) lists 2 unchanged output file(s)
- `Chess.IWSQ/rep02`
  - [run.log.gz](cases/Chess.IWSQ/rep02/run.log.gz) ([checksum](cases/Chess.IWSQ/rep02/run.log.sha256))
  - [command.json](cases/Chess.IWSQ/rep02/command.json)
  - [output.sha256](cases/Chess.IWSQ/rep02/output.sha256) lists 2 unchanged output file(s)
- `Chess.IWSQ/rep03`
  - [run.log.gz](cases/Chess.IWSQ/rep03/run.log.gz) ([checksum](cases/Chess.IWSQ/rep03/run.log.sha256))
  - [command.json](cases/Chess.IWSQ/rep03/command.json)
  - [output.sha256](cases/Chess.IWSQ/rep03/output.sha256) lists 2 unchanged output file(s)
- `Chess.IWSQWS/rep01`
  - [run.log.gz](cases/Chess.IWSQWS/rep01/run.log.gz) ([checksum](cases/Chess.IWSQWS/rep01/run.log.sha256))
  - [command.json](cases/Chess.IWSQWS/rep01/command.json)
  - [output.sha256](cases/Chess.IWSQWS/rep01/output.sha256) lists 3 unchanged output file(s)
- `Chess.IWSQWS/rep02`
  - [run.log.gz](cases/Chess.IWSQWS/rep02/run.log.gz) ([checksum](cases/Chess.IWSQWS/rep02/run.log.sha256))
  - [command.json](cases/Chess.IWSQWS/rep02/command.json)
  - [output.sha256](cases/Chess.IWSQWS/rep02/output.sha256) lists 2 unchanged output file(s)
- `Chess.IWSQWS/rep03`
  - [run.log.gz](cases/Chess.IWSQWS/rep03/run.log.gz) ([checksum](cases/Chess.IWSQWS/rep03/run.log.sha256))
  - [command.json](cases/Chess.IWSQWS/rep03/command.json)
  - [output.sha256](cases/Chess.IWSQWS/rep03/output.sha256) lists 2 unchanged output file(s)
- `Chess.SWSQ/rep01`
  - [run.log.gz](cases/Chess.SWSQ/rep01/run.log.gz) ([checksum](cases/Chess.SWSQ/rep01/run.log.sha256))
  - [command.json](cases/Chess.SWSQ/rep01/command.json)
  - [output.sha256](cases/Chess.SWSQ/rep01/output.sha256) lists 4 unchanged output file(s)
- `Chess.SWSQ/rep02`
  - [run.log.gz](cases/Chess.SWSQ/rep02/run.log.gz) ([checksum](cases/Chess.SWSQ/rep02/run.log.sha256))
  - [command.json](cases/Chess.SWSQ/rep02/command.json)
  - [output.sha256](cases/Chess.SWSQ/rep02/output.sha256) lists 2 unchanged output file(s)
- `Chess.SWSQ/rep03`
  - [run.log.gz](cases/Chess.SWSQ/rep03/run.log.gz) ([checksum](cases/Chess.SWSQ/rep03/run.log.sha256))
  - [command.json](cases/Chess.SWSQ/rep03/command.json)
  - [output.sha256](cases/Chess.SWSQ/rep03/output.sha256) lists 3 unchanged output file(s)
- `Chess.WSQ/rep01`
  - [run.log.gz](cases/Chess.WSQ/rep01/run.log.gz) ([checksum](cases/Chess.WSQ/rep01/run.log.sha256))
  - [command.json](cases/Chess.WSQ/rep01/command.json)
  - [output.sha256](cases/Chess.WSQ/rep01/output.sha256) lists 2 unchanged output file(s)
- `Chess.WSQ/rep02`
  - [run.log.gz](cases/Chess.WSQ/rep02/run.log.gz) ([checksum](cases/Chess.WSQ/rep02/run.log.sha256))
  - [command.json](cases/Chess.WSQ/rep02/command.json)
  - [output.sha256](cases/Chess.WSQ/rep02/output.sha256) lists 2 unchanged output file(s)
- `Chess.WSQ/rep03`
  - [run.log.gz](cases/Chess.WSQ/rep03/run.log.gz) ([checksum](cases/Chess.WSQ/rep03/run.log.sha256))
  - [command.json](cases/Chess.WSQ/rep03/command.json)
  - [output.sha256](cases/Chess.WSQ/rep03/output.sha256) lists 2 unchanged output file(s)

## Build records

- `Chess.IWSQ`: [build.json](cases/Chess.IWSQ/build.json), [build.log](cases/Chess.IWSQ/build.log)
- `Chess.IWSQWS`: [build.json](cases/Chess.IWSQWS/build.json), [build.log](cases/Chess.IWSQWS/build.log)
- `Chess.SWSQ`: [build.json](cases/Chess.SWSQ/build.json), [build.log](cases/Chess.SWSQ/build.log)
- `Chess.WSQ`: [build.json](cases/Chess.WSQ/build.json), [build.log](cases/Chess.WSQ/build.log)

## Missing raw logs

None.
