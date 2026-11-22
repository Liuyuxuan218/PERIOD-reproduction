[CmdletBinding()]
param([switch]$Repair, [switch]$Pilot)
$ErrorActionPreference = 'Stop'
$rq3Workspace = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$rq3VmDirectory = Join-Path $rq3Workspace 'work\rq3-legacy-vm'
$rq3RunPrefix = if ($Pilot) { 'four-cs-pilot-' } elseif ($Repair) { 'four-cs-repair-' } else { 'four-cs-formal-' }
$rq3Logs = Join-Path $rq3VmDirectory ($rq3RunPrefix + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))
$rq3Vagrant = 'C:\Program Files\Vagrant\bin\vagrant.exe'
$rq3Exit = 0
$rq3Pushed = $false
$rq3StartedUtc = [DateTime]::UtcNow
$rq3PowerHeld = $false
$rq3GroupsPlanned = 60
$rq3LaunchesPlanned = 600
$rq3Selection = 'all'
$rq3SourceName = 'none'
$rq3MeasurementComplete = $false
$rq3Watch = [Diagnostics.Stopwatch]::StartNew()
function Invoke-Rq3Formal {
    param([string[]]$Arguments, [string]$LogName, [switch]$Compact, [switch]$AllowFailure)
    $ErrorActionPreference = 'Continue'
    & $rq3Vagrant @Arguments 2>&1 | Tee-Object -FilePath (Join-Path $rq3Logs $LogName) | ForEach-Object {
        $rq3Line = [string]$_
        if ($rq3Line -match '^FORMAL_(START|DONE|PROFILE|STOPPED|MEASUREMENTS_COMPLETED)') {
            @{ utc = [DateTime]::UtcNow.ToString('o'); host_elapsed_seconds = $rq3Watch.Elapsed.TotalSeconds; line = $rq3Line } |
                ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $rq3Logs 'host-progress.jsonl') -Encoding utf8
        }
        if (-not $Compact -or $rq3Line -match '^FORMAL_') { Write-Host $rq3Line }
    }
    $script:rq3LastCode = $LASTEXITCODE
    if ($LASTEXITCODE -ne 0 -and -not $AllowFailure) { throw ($LogName + ': command exited ' + $LASTEXITCODE) }
}
try {
    New-Item -ItemType Directory -Path $rq3Logs -Force | Out-Null
    if ($Repair -and $Pilot) { throw 'Choose Pilot or Repair, not both.' }
    if ($Repair) { throw 'The old repair plan belongs to the legacy clock environment. Use Pilot, then a fresh complete KVM-clock batch after review.' }
    if ($Pilot) {
        $rq3Selection = '1:10'
        $rq3GroupsPlanned = 5
        $rq3LaunchesPlanned = 50
        $rq3SourceName = 'kvm-clock-validation-pilot-excluded-from-final'
    }
    if ($Repair) {
        $rq3PlanPath = Join-Path $PSScriptRoot 'interruption-audit-20261120\repair-plan.json'
        $rq3Plan = Get-Content -LiteralPath $rq3PlanPath -Raw | ConvertFrom-Json
        if (-not $rq3Plan.source_execution_checks_passed -or $rq3Plan.selection -notmatch '^[1-3]:(3|4|5|10)(,[1-3]:(3|4|5|10))*$') { throw 'Invalid repair plan.' }
        $rq3OriginalArchive = Join-Path $rq3Plan.source_host_directory 'evidence.tar.gz'
        if ((Get-FileHash -LiteralPath $rq3OriginalArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $rq3Plan.source_archive_sha256) { throw 'Original audited archive changed.' }
        $rq3Selection = $rq3Plan.selection
        $rq3GroupsPlanned = @($rq3Plan.repair_blocks).Count * 5
        $rq3LaunchesPlanned = $rq3GroupsPlanned * 10
        $rq3SourceName = Split-Path $rq3Plan.source_host_directory -Leaf
        Copy-Item -LiteralPath $rq3PlanPath -Destination (Join-Path $rq3Logs 'repair-plan.json')
    }
    # A request local to this running process; no Windows power-plan settings
    # are changed. The request is cleared when the command ends.
    if (-not ('Rq3PowerState' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Rq3PowerState {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
    }
    $rq3PowerHeld = [Rq3PowerState]::SetThreadExecutionState([uint32]2147483649) -ne 0
    if ($rq3PowerHeld) { Write-Host 'Automatic idle sleep is inhibited while this command runs; screen may turn off. Keep laptop plugged in and lid open.' }
    else { Write-Host 'Could not inhibit automatic sleep. Set plugged-in sleep to Never before timing.'; throw 'Sleep inhibition unavailable; no measurements started.' }
    $rq3RuntimeEvidence = Get-Content -LiteralPath (Join-Path $rq3VmDirectory 'period-import-20261118T051032Z\period-evidence.txt') -Raw
    $rq3Runtime = [regex]::Match($rq3RuntimeEvidence, '(?m)^PERIOD_RUNTIME_DIRECTORY=(/home/vagrant/rq3-period-runtime-[A-Za-z0-9]+)\s*$')
    $rq3BuildEvidence = Get-Content -LiteralPath (Join-Path $rq3VmDirectory 'four-cs-preparation-20261118T054325Z\four-cs-evidence.txt') -Raw
    $rq3Build = [regex]::Match($rq3BuildEvidence, '(?m)^FOUR_CS_DIRECTORY=(/workdir/rq3-four-cs-[A-Za-z0-9]+)\s*$')
    if (-not $rq3Runtime.Success -or -not $rq3Build.Success -or $rq3BuildEvidence -notmatch '(?m)^FOUR_CS_MATCHED_BUILD_AND_EXECUTION_PASSED\s*$') {
        throw 'Validated runtime/build evidence missing; no measurements started.'
    }
    Push-Location -LiteralPath $rq3VmDirectory
    $rq3Pushed = $true
    $env:PATH = 'C:\Program Files\Oracle\VirtualBox;' + (Split-Path $rq3Vagrant -Parent) + ';' + $env:PATH
    Write-Host 'Checking/starting the existing VM, without provisioning or rebuilding.'
    Invoke-Rq3Formal @('up', '--no-provision', '--provider', 'virtualbox') 'vm-start.txt'
    # Avoid nested quotes in native argv on Windows PowerShell 5.1. Read two
    # simple lines over SSH and compare them on the host instead.
    Invoke-Rq3Formal @('ssh', '--command', 'uname -r && cat /sys/devices/system/clocksource/clocksource0/current_clocksource') 'clock-preflight.txt'
    $rq3ClockEvidence = Get-Content -LiteralPath (Join-Path $rq3Logs 'clock-preflight.txt') -Raw
    if ($rq3ClockEvidence -notmatch '(?m)^3\.16\.0-77-generic\s*$' -or $rq3ClockEvidence -notmatch '(?m)^kvm-clock\s*$') {
        throw 'Kernel/clocksource preflight failed; no benchmark launched.'
    }
    Write-Host 'KVM_CLOCK_PREFLIGHT_PASSED'
    foreach ($rq3Name in @('observe-executions.py', 'run-four-cs-formal.py', 'run-four-cs-formal-guest.sh')) {
        $rq3Local = Join-Path $rq3Logs $rq3Name
        $rq3Body = [IO.File]::ReadAllText((Join-Path $PSScriptRoot $rq3Name))
        [IO.File]::WriteAllText($rq3Local, ($rq3Body -replace "`r", ''), (New-Object Text.UTF8Encoding($false)))
        $rq3Guest = switch ($rq3Name) {
            'observe-executions.py' { '/home/vagrant/rq3-observe-executions.py' }
            'run-four-cs-formal.py' { '/home/vagrant/rq3-run-four-cs-formal.py' }
            'run-four-cs-formal-guest.sh' { '/home/vagrant/rq3-run-four-cs-formal-guest.sh' }
        }
        Invoke-Rq3Formal @('upload', $rq3Local, $rq3Guest) ($rq3Name + '.upload.txt')
    }
    Write-Host ('Planned: ' + $rq3GroupsPlanned + ' groups / ' + $rq3LaunchesPlanned + ' measured launches. Selected paired blocks: ' + $rq3Selection)
    if ($Repair) { Write-Host 'Repair estimate: 24-40 minutes of measurement, about 25-45 minutes including startup/export. Original results stay intact.' }
    if ($Pilot) { Write-Host 'Validation pilot: 10-worker CS case x 5 methods x 10 launches. Estimated 5-12 minutes; actual time recorded. Excluded from final 600.' }
    elseif (-not $Repair) { Write-Host 'Final KVM-clock batch: 600 launches. Pilot-based estimate 45-70 minutes, depending on host load; actual start/end and elapsed time recorded automatically.' }
    Write-Host 'Each FORMAL_START / FORMAL_DONE pair is one group of 10 launches. Profiling is excluded. Run once; keep this terminal open.'
    Invoke-Rq3Formal @('ssh', '--command', ('sudo -n timeout -k 30s 7440s bash /home/vagrant/rq3-run-four-cs-formal-guest.sh ' + $rq3Runtime.Groups[1].Value + ' ' + $rq3Build.Groups[1].Value + ' ' + $rq3Selection + ' ' + $rq3SourceName)) 'formal-evidence.txt' -Compact -AllowFailure
    $rq3Evidence = Get-Content -LiteralPath (Join-Path $rq3Logs 'formal-evidence.txt') -Raw
    $rq3SummaryMatch = [regex]::Match($rq3Evidence, '(?ms)^BEGIN_FORMAL_SUMMARY_JSON\r?\n(.*?)^END_FORMAL_SUMMARY_JSON\s*$')
    $rq3ArchiveMatch = [regex]::Match($rq3Evidence, '(?ms)^BEGIN_FORMAL_ARCHIVE_BASE64\r?\n([A-Za-z0-9+/=\s]+?)^END_FORMAL_ARCHIVE_BASE64\s*$')
    $rq3HashMatch = [regex]::Match($rq3Evidence, '(?m)^FORMAL_ARCHIVE_SHA256=([a-f0-9]{64})\s*$')
    if ($rq3ArchiveMatch.Success -and $rq3HashMatch.Success) {
        $rq3ArchivePath = Join-Path $rq3Logs 'evidence.tar.gz'
        [IO.File]::WriteAllBytes($rq3ArchivePath, [Convert]::FromBase64String($rq3ArchiveMatch.Groups[1].Value))
        if ((Get-FileHash -LiteralPath $rq3ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $rq3HashMatch.Groups[1].Value) {
            throw 'Evidence archive hash mismatch.'
        }
        Write-Host 'FORMAL_RAW_EVIDENCE_ARCHIVE_VERIFIED'
    } else { throw 'Raw evidence archive was not received; inspect guest directory and host log.' }
    if (-not $rq3SummaryMatch.Success) { throw 'Summary missing; raw evidence is preserved.' }
    [IO.File]::WriteAllText((Join-Path $rq3Logs 'summary.json'), $rq3SummaryMatch.Groups[1].Value, (New-Object Text.UTF8Encoding($false)))
    $rq3Summary = $rq3SummaryMatch.Groups[1].Value | ConvertFrom-Json
    if ($script:rq3LastCode -ne 0 -or -not $rq3Summary.complete -or $rq3Summary.actual_measurements -ne $rq3LaunchesPlanned -or $rq3Summary.measurement_groups_completed -ne $rq3GroupsPlanned) {
        throw ('Batch incomplete: ' + $rq3Summary.failure + '. Completed groups=' + $rq3Summary.measurement_groups_completed)
    }
    $rq3MeasurementComplete = $true
    # Detect the same large host/guest elapsed disagreement immediately.
    $rq3Progress = @(Get-Content -LiteralPath (Join-Path $rq3Logs 'host-progress.jsonl') | ForEach-Object { $_ | ConvertFrom-Json })
    $rq3QualityRows = @()
    for ($rq3Index = 0; $rq3Index -lt $rq3Summary.records.Count; $rq3Index++) {
        $rq3Number = $rq3Index + 1
        $rq3Record = $rq3Summary.records[$rq3Index]
        $rq3StartEvent = $rq3Progress | Where-Object line -Match ('^FORMAL_START group=' + $rq3Number + '/') | Select-Object -First 1
        $rq3EndEvent = $rq3Progress | Where-Object line -Match ('^FORMAL_DONE group=' + $rq3Number + '/') | Select-Object -First 1
        if (-not $rq3StartEvent -or -not $rq3EndEvent) { throw ('Missing host timestamps for group ' + $rq3Number) }
        $rq3ChildSeconds = ($rq3Record.samples | Measure-Object elapsed_seconds -Sum).Sum
        $rq3HostSeconds = $rq3EndEvent.host_elapsed_seconds - $rq3StartEvent.host_elapsed_seconds
        $rq3Flagged = ($rq3HostSeconds - $rq3ChildSeconds) -gt [math]::Max(30, 0.2 * $rq3ChildSeconds)
        $rq3QualityRows += [pscustomobject]@{ group=$rq3Number; case=$rq3Record.case; repetition=$rq3Record.repetition; method=$rq3Record.method; host_seconds=$rq3HostSeconds; guest_child_seconds=$rq3ChildSeconds; flagged=$rq3Flagged }
    }
    $rq3QualityRows | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $rq3Logs 'host-timing-audit.json') -Encoding utf8
    $rq3FlagCount = @($rq3QualityRows | Where-Object flagged).Count
    Write-Host ('FORMAL_RESULTS_SAVED: ' + $rq3LaunchesPlanned + ' measurements complete. Large host/guest timing disagreements=' + $rq3FlagCount)
    if ($rq3FlagCount) { Write-Host 'TIMING_REVIEW_REQUIRED: preserve this run and return to chat before using the timings.' }
} catch {
    $rq3Exit = 1
    $_.Exception.Message | Set-Content -LiteralPath (Join-Path $rq3Logs 'failure.txt') -Encoding utf8
    Write-Host ('FORMAL_HOST_STOPPED: ' + $_.Exception.Message)
} finally {
    if ($rq3Pushed) { Pop-Location }
    $rq3Watch.Stop()
    $rq3EndedUtc = [DateTime]::UtcNow
    if ($rq3PowerHeld) { [Rq3PowerState]::SetThreadExecutionState([uint32]2147483648) | Out-Null }
    $rq3Timing = [ordered]@{ started_utc=$rq3StartedUtc.ToString('o'); ended_utc=$rq3EndedUtc.ToString('o'); host_elapsed_seconds=$rq3Watch.Elapsed.TotalSeconds; host_elapsed_minutes=$rq3Watch.Elapsed.TotalMinutes; wall_clock_seconds=($rq3EndedUtc-$rq3StartedUtc).TotalSeconds; planned_groups=$rq3GroupsPlanned; planned_launches=$rq3LaunchesPlanned; repair=[bool]$Repair; pilot=[bool]$Pilot; required_clocksource='kvm-clock'; selection=$rq3Selection; measurements_complete=$rq3MeasurementComplete; command_exit_code=$rq3Exit; sleep_inhibition_requested=$rq3PowerHeld; source_batch=$rq3SourceName }
    if (Test-Path -LiteralPath $rq3Logs) { $rq3Timing | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $rq3Logs 'run-timing.json') -Encoding utf8 }
    Write-Host ('Host elapsed minutes: ' + [math]::Round($rq3Watch.Elapsed.TotalMinutes, 2))
    Write-Host ('Saved logs: ' + $rq3Logs)
}
exit $rq3Exit
