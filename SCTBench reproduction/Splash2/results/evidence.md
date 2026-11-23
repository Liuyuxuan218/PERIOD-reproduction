# Evidence status

Historical `metrics.json` files were not modified.
Each `run.log.gz` is a lossless gzip copy of the local scheduler log whose start time, command, exit status, and parsed counts match that repetition.
`run.log.sha256` is the SHA-256 of the uncompressed log.
The execution workflow that produced these runs retained at most two files in each Errors or Timeouts directory. Those remaining files were copied unchanged. Deleted files were not reconstructed from the metrics.
A build log is included only when its recorded time is not later than the earliest submitted run of that program.
These records do not contain the source, toolchain, and executable fingerprint now required before a run can be reused. They remain historical records.

## Recovered

- `Splash2.barnes/rep02`
  - [run.log.gz](cases/Splash2.barnes/rep02/run.log.gz) ([checksum](cases/Splash2.barnes/rep02/run.log.sha256))
  - [command.json](cases/Splash2.barnes/rep02/command.json)
  - [output.sha256](cases/Splash2.barnes/rep02/output.sha256) lists 3 unchanged output file(s)
- `Splash2.barnes/rep03`
  - [run.log.gz](cases/Splash2.barnes/rep03/run.log.gz) ([checksum](cases/Splash2.barnes/rep03/run.log.sha256))
  - [command.json](cases/Splash2.barnes/rep03/command.json)
  - [output.sha256](cases/Splash2.barnes/rep03/output.sha256) lists 3 unchanged output file(s)
- `Splash2.fft/rep02`
  - [run.log.gz](cases/Splash2.fft/rep02/run.log.gz) ([checksum](cases/Splash2.fft/rep02/run.log.sha256))
  - [command.json](cases/Splash2.fft/rep02/command.json)
  - [output.sha256](cases/Splash2.fft/rep02/output.sha256) lists 3 unchanged output file(s)
- `Splash2.fft/rep03`
  - [run.log.gz](cases/Splash2.fft/rep03/run.log.gz) ([checksum](cases/Splash2.fft/rep03/run.log.sha256))
  - [command.json](cases/Splash2.fft/rep03/command.json)
  - [output.sha256](cases/Splash2.fft/rep03/output.sha256) lists 2 unchanged output file(s)
- `Splash2.lu/rep01`
  - [run.log.gz](cases/Splash2.lu/rep01/run.log.gz) ([checksum](cases/Splash2.lu/rep01/run.log.sha256))
  - [command.json](cases/Splash2.lu/rep01/command.json)
  - [output.sha256](cases/Splash2.lu/rep01/output.sha256) lists 2 unchanged output file(s)
- `Splash2.lu/rep02`
  - [run.log.gz](cases/Splash2.lu/rep02/run.log.gz) ([checksum](cases/Splash2.lu/rep02/run.log.sha256))
  - [command.json](cases/Splash2.lu/rep02/command.json)
  - [output.sha256](cases/Splash2.lu/rep02/output.sha256) lists 2 unchanged output file(s)
- `Splash2.lu/rep03`
  - [run.log.gz](cases/Splash2.lu/rep03/run.log.gz) ([checksum](cases/Splash2.lu/rep03/run.log.sha256))
  - [command.json](cases/Splash2.lu/rep03/command.json)
  - [output.sha256](cases/Splash2.lu/rep03/output.sha256) lists 3 unchanged output file(s)

## Build records

- `Splash2.barnes`: [build.json](cases/Splash2.barnes/build.json), [build.log](cases/Splash2.barnes/build.log)
- `Splash2.fft`: [build.json](cases/Splash2.fft/build.json), [build.log](cases/Splash2.fft/build.log)
- `Splash2.lu`: [build.json](cases/Splash2.lu/build.json), [build.log](cases/Splash2.lu/build.log)

## Missing raw logs

None.
