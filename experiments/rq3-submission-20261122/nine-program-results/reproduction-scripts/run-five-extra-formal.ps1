[CmdletBinding()]
param([switch]$RepairIwsqws)
$ErrorActionPreference = 'Stop'
$rq3Workspace = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$rq3VmDirectory = Join-Path $rq3Workspace 'work\rq3-legacy-vm'
$rq3Tag = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,6)
$rq3Prefix = if ($RepairIwsqws) { 'five-extra-repair-' } else { 'five-extra-formal-' }
$rq3Groups = if ($RepairIwsqws) { 5 } else { 75 }
$rq3Launches = $rq3Groups * 10
$rq3Selection = if ($RepairIwsqws) { 'repair-iwsqws-rep3' } else { 'all' }
$rq3Logs = Join-Path $rq3VmDirectory ($rq3Prefix + $rq3Tag)
$rq3Upload = '/home/vagrant/rq3-extra-formal-upload-' + $rq3Tag
$rq3Vagrant = 'C:\Program Files\Vagrant\bin\vagrant.exe'
$rq3Started = [DateTime]::UtcNow
$rq3Watch = [Diagnostics.Stopwatch]::StartNew()
$rq3PreviousPath = $env:PATH
$rq3Exit = 0
$rq3Pushed = $false
$rq3Complete = $false
$rq3PowerHeld = $false
function Invoke-Rq3Extra {
    param([string[]]$Arguments, [string]$LogName, [switch]$Compact, [switch]$AllowFailure)
    $ErrorActionPreference = 'Continue'
    & $rq3Vagrant @Arguments 2>&1 | Tee-Object -FilePath (Join-Path $rq3Logs $LogName) | ForEach-Object {
        $rq3Line = [string]$_
        if ($rq3Line -match '^FORMAL_(START|DONE|PROFILE|BLOCK_FAILED|STOPPED|BATCH_FINISHED|MEASUREMENTS_COMPLETED)') {
            @{ utc=[DateTime]::UtcNow.ToString('o'); host_elapsed_seconds=$rq3Watch.Elapsed.TotalSeconds; line=$rq3Line } |
                ConvertTo-Json -Compress | Add-Content -LiteralPath (Join-Path $rq3Logs 'host-progress.jsonl') -Encoding utf8
        }
        if (-not $Compact -or $rq3Line -match '^FORMAL_') { Write-Host $rq3Line }
    }
    $script:rq3LastCode = $LASTEXITCODE
    if ($script:rq3LastCode -ne 0 -and -not $AllowFailure) { throw ($LogName + ': command exited ' + $script:rq3LastCode) }
}
try {
    New-Item -ItemType Directory -Path $rq3Logs | Out-Null
    if ($RepairIwsqws) {
        $rq3Original = Join-Path $rq3VmDirectory 'five-extra-formal-20261120T151904Z-b3d307\evidence.tar.gz'
        $rq3OriginalHash = '139fcd474eec08a8b905cbf732b69b9c5d36383602aec7145499f12df600c188'
        if ((Get-FileHash -LiteralPath $rq3Original -Algorithm SHA256).Hash.ToLowerInvariant() -ne $rq3OriginalHash) { throw 'Original evidence archive mismatch; repair not started.' }
        @{original_batch='five-extra-formal-20261120T151904Z-b3d307';original_archive_sha256=$rq3OriginalHash;replace_complete_block=@{case='Chess.IWSQWS';repetition=3;original_group_numbers=@(66,67,68,69,70)};original_native_and_partial_period_excluded=$true;preserve_other_14_paired_blocks=$true;protocol_amendment_file='five-extra-budget-amendment.md';protocol_amendment_sha256=(Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'five-extra-budget-amendment.md') -Algorithm SHA256).Hash.ToLowerInvariant();created_before_run_utc=[DateTime]::UtcNow.ToString('o')} |
            ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $rq3Logs 'repair-provenance.json') -Encoding utf8
    }
    $rq3RuntimeText = Get-Content -Raw -LiteralPath (Join-Path $rq3VmDirectory 'period-import-20261118T051032Z\period-evidence.txt')
    $rq3Runtime = [regex]::Match($rq3RuntimeText, '(?m)^PERIOD_RUNTIME_DIRECTORY=(/home/vagrant/rq3-period-runtime-[A-Za-z0-9]+)\s*$')
    if (-not $rq3Runtime.Success) { throw 'Existing runtime evidence missing.' }
    $rq3Plan = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'five-extra-approved-plan.json') | ConvertFrom-Json
    if (@($rq3Plan.cases).Count -ne 5 -or ($rq3Plan.cases.case -join ',') -ne 'Inspect.qsort_mt,Chess.WSQ,Chess.IWSQ,Chess.IWSQWS,Misc.safestack') { throw 'Approved case list differs.' }
    if (-not ('Rq3ExtraPowerState' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Rq3ExtraPowerState {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
    }
    $rq3PowerHeld = [Rq3ExtraPowerState]::SetThreadExecutionState([uint32]2147483649) -ne 0
    if (-not $rq3PowerHeld) { throw 'Could not inhibit idle sleep; no benchmark started.' }
    Push-Location -LiteralPath $rq3VmDirectory
    $rq3Pushed = $true
    $env:PATH = 'C:\Program Files\Oracle\VirtualBox;' + (Split-Path $rq3Vagrant -Parent) + ';' + $env:PATH
    Invoke-Rq3Extra @('up', '--no-provision', '--provider', 'virtualbox') 'vm-start.txt'
    Invoke-Rq3Extra @('ssh', '--command', 'uname -r && cat /sys/devices/system/clocksource/clocksource0/current_clocksource') 'clock-preflight.txt'
    $rq3Clock = Get-Content -Raw -LiteralPath (Join-Path $rq3Logs 'clock-preflight.txt')
    if ($rq3Clock -notmatch '(?m)^3\.16\.0-77-generic\s*$' -or $rq3Clock -notmatch '(?m)^kvm-clock\s*$') { throw 'Existing kernel/clock preflight failed; no benchmark started.' }
    Invoke-Rq3Extra @('ssh', '--command', ('mkdir -m 700 ' + $rq3Upload)) 'upload-directory.txt'
    foreach ($rq3Name in @('observe-cross-family.py','cross-family-formal-support.py','run-five-extra-formal.py','five-extra-approved-plan.json','run-five-extra-formal-guest.sh')) {
        $rq3Local = Join-Path $rq3Logs $rq3Name
        [IO.File]::WriteAllText($rq3Local, ([IO.File]::ReadAllText((Join-Path $PSScriptRoot $rq3Name)) -replace "`r", ''), (New-Object Text.UTF8Encoding($false)))
        Invoke-Rq3Extra @('upload', $rq3Local, ($rq3Upload + '/' + $rq3Name)) ($rq3Name + '.upload.txt')
    }
    $rq3Amendment = Join-Path $rq3Logs 'five-extra-budget-amendment.md'
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'five-extra-budget-amendment.md') -Destination $rq3Amendment
    Invoke-Rq3Extra @('upload', $rq3Amendment, ($rq3Upload + '/five-extra-budget-amendment.md')) 'amendment.upload.txt'
    if ($RepairIwsqws) {
        $rq3Provenance = Join-Path $rq3Logs 'repair-provenance.json'
        $rq3ProvenanceText = [IO.File]::ReadAllText($rq3Provenance)
        [IO.File]::WriteAllText($rq3Provenance, $rq3ProvenanceText, (New-Object Text.UTF8Encoding($false)))
        Invoke-Rq3Extra @('upload', $rq3Provenance, ($rq3Upload + '/repair-provenance.json')) 'provenance.upload.txt'
        Write-Host 'Repair ONLY Chess.IWSQWS repetition3: five methods x 10 actual launches = 50 measurements. Keep other14 complete blocks.'
        Write-Host 'Estimate: 6-10 minutes. Same binaries, seed20264123, method order and timing; fresh profile. Actual time recorded.'
    } else {
        Write-Host 'Formal batch: 5 programs x 5 methods x 3 independent repetitions x 10 actual launches = 750 planned measurements.'
        Write-Host 'Rough estimate: 50-90 minutes; actual start/end and elapsed time recorded.'
    }
    Write-Host 'SWSQ and boundedBuffer are excluded. Existing binaries reused. No software installation or rebuild.'
    Write-Host 'Keep plugged in, lid open, terminal open. Screen may turn off. Run once; do not start another test.'
    Invoke-Rq3Extra @('ssh','--command',('sudo -n timeout -k 45s 10920s bash ' + $rq3Upload + '/run-five-extra-formal-guest.sh ' + $rq3Runtime.Groups[1].Value + ' ' + $rq3Upload + ' ' + $rq3Selection)) 'formal-evidence.txt' -Compact -AllowFailure
    $rq3GuestCode = $script:rq3LastCode
    $rq3Evidence = Get-Content -Raw -LiteralPath (Join-Path $rq3Logs 'formal-evidence.txt')
    $rq3ArchiveMatch = [regex]::Match($rq3Evidence, '(?ms)^BEGIN_FORMAL_ARCHIVE_BASE64\r?\n([A-Za-z0-9+/=\s]+?)^END_FORMAL_ARCHIVE_BASE64\s*$')
    $rq3HashMatch = [regex]::Match($rq3Evidence, '(?m)^FORMAL_ARCHIVE_SHA256=([a-f0-9]{64})\s*$')
    if (-not $rq3ArchiveMatch.Success -or -not $rq3HashMatch.Success) { throw 'Raw evidence archive not received; guest logs retained.' }
    $rq3Archive = Join-Path $rq3Logs 'evidence.tar.gz'
    [IO.File]::WriteAllBytes($rq3Archive, [Convert]::FromBase64String($rq3ArchiveMatch.Groups[1].Value))
    if ((Get-FileHash -LiteralPath $rq3Archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $rq3HashMatch.Groups[1].Value) { throw 'Evidence archive SHA256 mismatch.' }
    Write-Host 'FORMAL_RAW_EVIDENCE_ARCHIVE_VERIFIED'
    $rq3SummaryMatch = [regex]::Match($rq3Evidence, '(?ms)^BEGIN_FORMAL_SUMMARY_JSON\r?\n(.*?)^END_FORMAL_SUMMARY_JSON\s*$')
    if (-not $rq3SummaryMatch.Success) { throw 'Summary unavailable; raw evidence retained.' }
    [IO.File]::WriteAllText((Join-Path $rq3Logs 'summary.json'), $rq3SummaryMatch.Groups[1].Value, (New-Object Text.UTF8Encoding($false)))
    $rq3Summary = $rq3SummaryMatch.Groups[1].Value | ConvertFrom-Json
    $rq3Progress = @()
    if (Test-Path -LiteralPath (Join-Path $rq3Logs 'host-progress.jsonl')) {
        $rq3Progress = @(Get-Content -LiteralPath (Join-Path $rq3Logs 'host-progress.jsonl') | ForEach-Object { $_ | ConvertFrom-Json })
    }
    $rq3Quality = @()
    foreach ($rq3Record in $rq3Summary.records) {
        $rq3Number = $rq3Record.group_number
        $rq3Start = $rq3Progress | Where-Object line -Match ('^FORMAL_START group=' + $rq3Number + '/' + $rq3Groups + ' ') | Select-Object -First 1
        $rq3End = $rq3Progress | Where-Object line -Match ('^FORMAL_DONE group=' + $rq3Number + '/' + $rq3Groups + ' ') | Select-Object -First 1
        if (-not $rq3Start -or -not $rq3End) { throw ('Host timestamps missing for group ' + $rq3Number) }
        $rq3HostSeconds = $rq3End.host_elapsed_seconds - $rq3Start.host_elapsed_seconds
        $rq3ChildSeconds = ($rq3Record.samples | Measure-Object elapsed_seconds -Sum).Sum
        $rq3Quality += [pscustomobject]@{group=$rq3Number;case=$rq3Record.case;repetition=$rq3Record.repetition;method=$rq3Record.method;host_seconds=$rq3HostSeconds;guest_child_seconds=$rq3ChildSeconds;flagged=(($rq3HostSeconds-$rq3ChildSeconds) -gt [math]::Max(30,0.2*$rq3ChildSeconds))}
    }
    ConvertTo-Json -InputObject $rq3Quality -Depth 5 | Set-Content -LiteralPath (Join-Path $rq3Logs 'host-timing-audit.json') -Encoding utf8
    $rq3Flags = @($rq3Quality | Where-Object flagged).Count
    Write-Host ('FORMAL_RESULTS_SAVED completed_groups=' + $rq3Summary.measurement_groups_completed + '/' + $rq3Groups + ' valid_measured_children=' + $rq3Summary.actual_measurements + '/' + $rq3Launches + ' timing_flags=' + $rq3Flags)
    if ($rq3GuestCode -ne 0 -or -not $rq3Summary.complete) { throw ('Batch has incomplete paired blocks; other cases were continued. See saved failures. ' + $rq3Summary.failure) }
    $rq3Complete = $true
    if ($rq3Flags) { Write-Host 'TIMING_REVIEW_REQUIRED: keep all evidence for audit before plotting.' }
} catch {
    $rq3Exit = 1
    if (Test-Path -LiteralPath $rq3Logs) { $_.Exception.Message | Set-Content -LiteralPath (Join-Path $rq3Logs 'failure.txt') -Encoding utf8 }
    Write-Host ('FORMAL_HOST_STOPPED: ' + $_.Exception.Message)
} finally {
    if ($rq3Pushed) { Pop-Location }
    $env:PATH = $rq3PreviousPath
    if ($rq3PowerHeld) { [Rq3ExtraPowerState]::SetThreadExecutionState([uint32]2147483648) | Out-Null }
    $rq3Watch.Stop()
    if (Test-Path -LiteralPath $rq3Logs) {
        @{started_utc=$rq3Started.ToString('o');ended_utc=[DateTime]::UtcNow.ToString('o');host_elapsed_seconds=$rq3Watch.Elapsed.TotalSeconds;planned_groups=$rq3Groups;planned_launches=$rq3Launches;selection=$rq3Selection;measurements_complete=$rq3Complete;command_exit_code=$rq3Exit;required_clocksource='kvm-clock'} |
            ConvertTo-Json | Set-Content -LiteralPath (Join-Path $rq3Logs 'run-timing.json') -Encoding utf8
    }
    Write-Host ('Host elapsed minutes: ' + [math]::Round($rq3Watch.Elapsed.TotalMinutes,2))
    Write-Host ('Saved logs: ' + $rq3Logs)
}
exit $rq3Exit
