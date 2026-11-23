# Evidence status

Historical `metrics.json` files were not modified.
Each `run.log.gz` is a lossless gzip copy of the local scheduler log whose start time, command, exit status, and parsed counts match that repetition.
`run.log.sha256` is the SHA-256 of the uncompressed log.
The execution workflow that produced these runs retained at most two files in each Errors or Timeouts directory. Those remaining files were copied unchanged. Deleted files were not reconstructed from the metrics.
A build log is included only when its recorded time is not later than the earliest submitted run of that program.
These records do not contain the source, toolchain, and executable fingerprint now required before a run can be reused. They remain historical records.

## Recovered

- `RADBench.bug2/rep01`
  - [run.log.gz](cases/RADBench.bug2/rep01/run.log.gz) ([checksum](cases/RADBench.bug2/rep01/run.log.sha256))
  - [command.json](cases/RADBench.bug2/rep01/command.json)
  - [output.sha256](cases/RADBench.bug2/rep01/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug2/rep02`
  - [run.log.gz](cases/RADBench.bug2/rep02/run.log.gz) ([checksum](cases/RADBench.bug2/rep02/run.log.sha256))
  - [command.json](cases/RADBench.bug2/rep02/command.json)
  - [output.sha256](cases/RADBench.bug2/rep02/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug2/rep03`
  - [run.log.gz](cases/RADBench.bug2/rep03/run.log.gz) ([checksum](cases/RADBench.bug2/rep03/run.log.sha256))
  - [command.json](cases/RADBench.bug2/rep03/command.json)
  - [output.sha256](cases/RADBench.bug2/rep03/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug3/rep01`
  - [run.log.gz](cases/RADBench.bug3/rep01/run.log.gz) ([checksum](cases/RADBench.bug3/rep01/run.log.sha256))
  - [command.json](cases/RADBench.bug3/rep01/command.json)
  - [output.sha256](cases/RADBench.bug3/rep01/output.sha256) lists 3 unchanged output file(s)
- `RADBench.bug3/rep02`
  - [run.log.gz](cases/RADBench.bug3/rep02/run.log.gz) ([checksum](cases/RADBench.bug3/rep02/run.log.sha256))
  - [command.json](cases/RADBench.bug3/rep02/command.json)
  - [output.sha256](cases/RADBench.bug3/rep02/output.sha256) lists 3 unchanged output file(s)
- `RADBench.bug5/rep01`
  - [run.log.gz](cases/RADBench.bug5/rep01/run.log.gz) ([checksum](cases/RADBench.bug5/rep01/run.log.sha256))
  - [command.json](cases/RADBench.bug5/rep01/command.json)
  - [output.sha256](cases/RADBench.bug5/rep01/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug5/rep02`
  - [run.log.gz](cases/RADBench.bug5/rep02/run.log.gz) ([checksum](cases/RADBench.bug5/rep02/run.log.sha256))
  - [command.json](cases/RADBench.bug5/rep02/command.json)
  - [output.sha256](cases/RADBench.bug5/rep02/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug5/rep03`
  - [run.log.gz](cases/RADBench.bug5/rep03/run.log.gz) ([checksum](cases/RADBench.bug5/rep03/run.log.sha256))
  - [command.json](cases/RADBench.bug5/rep03/command.json)
  - [output.sha256](cases/RADBench.bug5/rep03/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug6/rep01`
  - [run.log.gz](cases/RADBench.bug6/rep01/run.log.gz) ([checksum](cases/RADBench.bug6/rep01/run.log.sha256))
  - [command.json](cases/RADBench.bug6/rep01/command.json)
  - [output.sha256](cases/RADBench.bug6/rep01/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug6/rep02`
  - [run.log.gz](cases/RADBench.bug6/rep02/run.log.gz) ([checksum](cases/RADBench.bug6/rep02/run.log.sha256))
  - [command.json](cases/RADBench.bug6/rep02/command.json)
  - [output.sha256](cases/RADBench.bug6/rep02/output.sha256) lists 2 unchanged output file(s)
- `RADBench.bug6/rep03`
  - [run.log.gz](cases/RADBench.bug6/rep03/run.log.gz) ([checksum](cases/RADBench.bug6/rep03/run.log.sha256))
  - [command.json](cases/RADBench.bug6/rep03/command.json)
  - [output.sha256](cases/RADBench.bug6/rep03/output.sha256) lists 2 unchanged output file(s)

## Build records

- `RADBench.bug2`: [build.json](cases/RADBench.bug2/build.json), [build.log](cases/RADBench.bug2/build.log)
- `RADBench.bug3`: [build.json](cases/RADBench.bug3/build.json), [build.log](cases/RADBench.bug3/build.log)
- `RADBench.bug5`: [build.json](cases/RADBench.bug5/build.json), [build.log](cases/RADBench.bug5/build.log)
- `RADBench.bug6`: [build.json](cases/RADBench.bug6/build.json), [build.log](cases/RADBench.bug6/build.log)

## Missing raw logs

None.

## Additional repetitions

`RADBench.bug3/rep03` is a completed run recovered from the local experiment tree. `RADBench.bug4` rep01, rep02, and rep03 are failed attempts: the scheduler log ends in a 5-second dry-run timeout and no schedule was explored. These files were copied unchanged and do not contain the provenance fingerprint required before a run can be reused.
