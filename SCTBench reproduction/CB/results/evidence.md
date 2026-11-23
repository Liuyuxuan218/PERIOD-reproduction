# Evidence status

Historical `metrics.json` files were not modified.
Each `run.log.gz` is a lossless gzip copy of the local scheduler log whose start time, command, exit status, and parsed counts match that repetition.
`run.log.sha256` is the SHA-256 of the uncompressed log.
The execution workflow that produced these runs retained at most two files in each Errors or Timeouts directory. Those remaining files were copied unchanged. Deleted files were not reconstructed from the metrics.
A build log is included only when its recorded time is not later than the earliest submitted run of that program.
These records do not contain the source, toolchain, and executable fingerprint now required before a run can be reused. They remain historical records.

## Recovered

- `CB.aget-bug/rep01`
  - [run.log.gz](cases/CB.aget-bug/rep01/run.log.gz) ([checksum](cases/CB.aget-bug/rep01/run.log.sha256))
  - [command.json](cases/CB.aget-bug/rep01/command.json)
  - [output.sha256](cases/CB.aget-bug/rep01/output.sha256) lists 2 unchanged output file(s)
- `CB.aget-bug/rep02`
  - [run.log.gz](cases/CB.aget-bug/rep02/run.log.gz) ([checksum](cases/CB.aget-bug/rep02/run.log.sha256))
  - [command.json](cases/CB.aget-bug/rep02/command.json)
  - [output.sha256](cases/CB.aget-bug/rep02/output.sha256) lists 3 unchanged output file(s)
- `CB.aget-bug/rep03`
  - [run.log.gz](cases/CB.aget-bug/rep03/run.log.gz) ([checksum](cases/CB.aget-bug/rep03/run.log.sha256))
  - [command.json](cases/CB.aget-bug/rep03/command.json)
  - [output.sha256](cases/CB.aget-bug/rep03/output.sha256) lists 2 unchanged output file(s)
- `CB.pbzip2/rep01`
  - [run.log.gz](cases/CB.pbzip2/rep01/run.log.gz) ([checksum](cases/CB.pbzip2/rep01/run.log.sha256))
  - [command.json](cases/CB.pbzip2/rep01/command.json)
  - [output.sha256](cases/CB.pbzip2/rep01/output.sha256) lists 2 unchanged output file(s)
- `CB.pbzip2/rep02`
  - [run.log.gz](cases/CB.pbzip2/rep02/run.log.gz) ([checksum](cases/CB.pbzip2/rep02/run.log.sha256))
  - [command.json](cases/CB.pbzip2/rep02/command.json)
  - [output.sha256](cases/CB.pbzip2/rep02/output.sha256) lists 2 unchanged output file(s)
- `CB.pbzip2/rep03`
  - [run.log.gz](cases/CB.pbzip2/rep03/run.log.gz) ([checksum](cases/CB.pbzip2/rep03/run.log.sha256))
  - [command.json](cases/CB.pbzip2/rep03/command.json)
  - [output.sha256](cases/CB.pbzip2/rep03/output.sha256) lists 2 unchanged output file(s)
- `CB.stringbuffer/rep01`
  - [run.log.gz](cases/CB.stringbuffer/rep01/run.log.gz) ([checksum](cases/CB.stringbuffer/rep01/run.log.sha256))
  - [command.json](cases/CB.stringbuffer/rep01/command.json)
  - [output.sha256](cases/CB.stringbuffer/rep01/output.sha256) lists 2 unchanged output file(s)
- `CB.stringbuffer/rep02`
  - [run.log.gz](cases/CB.stringbuffer/rep02/run.log.gz) ([checksum](cases/CB.stringbuffer/rep02/run.log.sha256))
  - [command.json](cases/CB.stringbuffer/rep02/command.json)
  - [output.sha256](cases/CB.stringbuffer/rep02/output.sha256) lists 2 unchanged output file(s)
- `CB.stringbuffer/rep03`
  - [run.log.gz](cases/CB.stringbuffer/rep03/run.log.gz) ([checksum](cases/CB.stringbuffer/rep03/run.log.sha256))
  - [command.json](cases/CB.stringbuffer/rep03/command.json)
  - [output.sha256](cases/CB.stringbuffer/rep03/output.sha256) lists 2 unchanged output file(s)

## Build records

- `CB.aget-bug`: [build.json](cases/CB.aget-bug/build.json), [build.log](cases/CB.aget-bug/build.log)
- `CB.pbzip2`: [build.json](cases/CB.pbzip2/build.json), [build.log](cases/CB.pbzip2/build.log)
- `CB.stringbuffer`: [build.json](cases/CB.stringbuffer/build.json), [build.log](cases/CB.stringbuffer/build.log)

## Missing raw logs

None.
