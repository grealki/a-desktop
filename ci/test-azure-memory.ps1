param([Parameter(Mandatory = $true)][string]$Executable)
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Executable)) { throw "Azure memory test executable not found: $Executable" }
$modeDirectory = Join-Path $env:LOCALAPPDATA 'Azure'
$modeFile = Join-Path $modeDirectory 'memory-mode.txt'
$hadModeFile = Test-Path -LiteralPath $modeFile
$oldModeText = if ($hadModeFile) { [IO.File]::ReadAllText($modeFile) } else { $null }
$testRoot = Join-Path $env:TEMP ('azure-memory-test-' + [Guid]::NewGuid().ToString('N'))

try {
    New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
    $assembly = [Reflection.Assembly]::LoadFrom([IO.Path]::GetFullPath($Executable))
    $brain = $assembly.GetType('CapriDesktop.Brain', $true)
    $staticPrivate = [Reflection.BindingFlags]::Static -bor [Reflection.BindingFlags]::NonPublic
    $staticAll = $staticPrivate -bor [Reflection.BindingFlags]::Public
    $modeType = $brain.GetNestedType('MemoryMode', [Reflection.BindingFlags]::Public -bor [Reflection.BindingFlags]::NonPublic)
    if ($null -eq $modeType) { throw 'Brain.MemoryMode was not found.' }

    $setMode = $brain.GetMethod('SetMemoryMode', $staticPrivate)
    $cycleMode = $brain.GetMethod('CycleMemoryMode', $staticPrivate)
    $currentMode = $brain.GetProperty('CurrentMemoryMode', $staticPrivate)
    $modeLabel = $brain.GetProperty('MemoryModeLabel', $staticPrivate)
    $memoryAvailable = $brain.GetProperty('MemoryAvailable', $staticPrivate)
    $keeping = $brain.GetProperty('Keeping', $staticPrivate)
    $memoryModeValue = $brain.GetField('memoryModeValue', $staticPrivate)
    $keepingOverride = $brain.GetField('keepingOverride', $staticPrivate)
    $memoryPath = $brain.GetField('MemoryPath', $staticAll)
    $memoriesPath = $brain.GetField('MemoriesPath', $staticAll)
    $transcriptPath = $brain.GetField('TranscriptPath', $staticAll)
    $keeper = $brain.GetField('Keeper', $staticAll)
    $note = $brain.GetMethod('Note', $staticPrivate)
    $transcribe = $brain.GetMethod('Transcribe', $staticPrivate)
    $memories = $brain.GetMethod('Memories', $staticPrivate)
    $remembered = $brain.GetMethod('Remembered', $staticPrivate)

    foreach ($member in @($setMode, $cycleMode, $currentMode, $modeLabel, $memoryAvailable, $keeping, $memoryModeValue, $keepingOverride, $memoryPath, $memoriesPath, $transcriptPath, $keeper, $note, $transcribe, $memories, $remembered)) {
        if ($null -eq $member) { throw 'An Azure memory mode test member could not be found.' }
    }

    $memoryPath.SetValue($null, (Join-Path $testRoot 'me.md'))
    $memoriesPath.SetValue($null, (Join-Path $testRoot 'memories.md'))
    $transcriptPath.SetValue($null, (Join-Path $testRoot 'transcripts'))
    $keeper.SetValue($null, $null)
    $memoryModeValue.SetValue($null, -1)
    $keepingOverride.SetValue($null, -1)

    [IO.File]::WriteAllText([string]$memoriesPath.GetValue($null), "# What Azure remembers`n## Earlier`n- They like puzzle games.`n")

    $off = [Enum]::Parse($modeType, 'Off')
    $controlled = [Enum]::Parse($modeType, 'Controlled')
    $full = [Enum]::Parse($modeType, 'Full')
    $set = {
        param($choice)
        $ok = $setMode.Invoke($null, [object[]]@($choice))
        if (-not $ok) { throw "Could not persist memory mode $choice." }
    }
    $assertMode = {
        param($choice, [bool]$available, [bool]$automatic)
        $actual = $currentMode.GetValue($null).ToString()
        if ($actual -ne $choice) { throw "Expected memory mode $choice, got $actual." }
        if ([bool]$memoryAvailable.GetValue($null) -ne $available) { throw "Memory availability was wrong in $choice mode." }
        if ([bool]$keeping.GetValue($null) -ne $automatic) { throw "Automatic transcript setting was wrong in $choice mode." }
        if ([string]$modeLabel.GetValue($null) -ne $choice) { throw "Memory label was wrong in $choice mode." }
    }

    & $set $off
    & $assertMode 'Off' $false $false
    $blocked = [string]$note.Invoke($null, [object[]]@('likes puzzle games'))
    if (-not $blocked.StartsWith('Memory is off.', [StringComparison]::Ordinal)) { throw "Off mode accepted a note: $blocked" }
    $transcribe.Invoke($null, [object[]]@('You', 'this should not be logged', $true)) | Out-Null
    if (Test-Path -LiteralPath (Join-Path $testRoot 'transcripts')) { throw 'Off mode created a transcript folder.' }
    if ([string]$memories.Invoke($null, @()) -ne '' -or [string]$remembered.Invoke($null, @()) -ne '') { throw 'Off mode exposed saved memories.' }

    & $set $controlled
    & $assertMode 'Controlled' $true $false
    $saved = $note.Invoke($null, [object[]]@('likes puzzle games'))
    if (-not (Test-Path -LiteralPath (Join-Path $testRoot 'me.md'))) { throw "Controlled mode did not save an explicit note: $saved" }
    $transcribe.Invoke($null, [object[]]@('You', 'this should not be logged')) | Out-Null
    if (Test-Path -LiteralPath (Join-Path $testRoot 'transcripts')) { throw 'Controlled mode created automatic transcripts.' }
    if (-not ([string]$remembered.Invoke($null, @())).Contains('Likes puzzle games')) { throw 'Controlled mode did not expose the explicitly saved note.' }

    & $set $full
    & $assertMode 'Full' $true $true
    $transcribe.Invoke($null, [object[]]@('You', 'full mode transcript check', $true)) | Out-Null
    $day = Get-ChildItem -LiteralPath (Join-Path $testRoot 'transcripts') -Filter '*.md' | Select-Object -First 1
    if ($null -eq $day) { throw 'Full mode did not create a local transcript.' }
    $dayText = [IO.File]::ReadAllText($day.FullName)
    if (-not $dayText.StartsWith('# Azure and you, ', [StringComparison]::Ordinal) -or $dayText.IndexOf('full mode transcript check', [StringComparison]::Ordinal) -lt 0) { throw 'Full mode transcript content was incorrect.' }

    $memoryModeValue.SetValue($null, -1)
    $keepingOverride.SetValue($null, -1)
    & $assertMode 'Full' $true $true

    & $set $off
    $keeping.SetValue($null, $true, $null)
    & $assertMode 'Off' $false $false
    & $set $off
    if (-not $cycleMode.Invoke($null, [object[]]@())) { throw 'Could not cycle Off to Controlled.' }
    & $assertMode 'Controlled' $true $false
    if (-not $cycleMode.Invoke($null, [object[]]@())) { throw 'Could not cycle Controlled to Full.' }
    & $assertMode 'Full' $true $true
    if (-not $cycleMode.Invoke($null, [object[]]@())) { throw 'Could not cycle Full to Off.' }
    & $assertMode 'Off' $false $false

    Write-Output 'PASS Azure memory modes: Off blocks saves and reads; Controlled stores explicit notes only; Full records local transcripts; mode persists; legacy bool cannot override it; button cycles all three.'
}
finally {
    if ($hadModeFile) {
        New-Item -ItemType Directory -Path $modeDirectory -Force | Out-Null
        [IO.File]::WriteAllText($modeFile, $oldModeText)
    }
    elseif (Test-Path -LiteralPath $modeFile) {
        Remove-Item -LiteralPath $modeFile -Force
        if ((Test-Path -LiteralPath $modeDirectory) -and @(Get-ChildItem -LiteralPath $modeDirectory -Force).Count -eq 0) {
            Remove-Item -LiteralPath $modeDirectory -Force
        }
    }
    if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
}
