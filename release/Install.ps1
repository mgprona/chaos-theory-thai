[CmdletBinding()]
param(
    [string]$GameDir,
    [switch]$CheckOnly,
    [switch]$Verify,
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
# Use this PowerShell's built-in modules even when launched from PowerShell 7
# or a developer shell that supplied a different PSModulePath.
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1')
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Management\Microsoft.PowerShell.Management.psd1')

function Get-Digest([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Safe-Path([string]$Root, [string]$Relative) {
    if ([string]::IsNullOrWhiteSpace($Relative) -or [IO.Path]::IsPathRooted($Relative) -or
        $Relative.Contains(':') -or $Relative -match '(^|[\\/])\.\.?([\\/]|$)') {
        throw "Unsafe relative path: $Relative"
    }
    $prefix = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
    $full = [IO.Path]::GetFullPath((Join-Path $Root $Relative))
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path outside expected directory: $Relative"
    }
    $current = $full
    while ($current.Length -ge $prefix.TrimEnd('\').Length) {
        if (Test-Path -LiteralPath $current) {
            if (((Get-Item -LiteralPath $current -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Linked paths are unsupported: $current"
            }
        }
        $current = Split-Path -Parent $current
        if (-not $current) { break }
    }
    return $full
}

function Assert-File([string]$Path, [string]$Digest, [long]$Size = -1) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing file: $Path" }
    if ($Size -ge 0 -and (Get-Item -LiteralPath $Path).Length -ne $Size) { throw "Size mismatch: $Path" }
    if ((Get-Digest $Path) -ne $Digest) { throw "SHA-256 mismatch: $Path" }
}

function Get-IniValue([string]$Text, [string]$Section, [string]$Key) {
    $active = ''
    $value = $null
    foreach ($line in ($Text -split '\r?\n')) {
        if ($line -match '^\s*\[([^\]]+)\]\s*$') { $active = $Matches[1] }
        elseif ($active -eq $Section -and $line -match ('^\s*' + [regex]::Escape($Key) + '\s*=\s*(.*?)\s*$')) {
            $value = $Matches[1]
        }
    }
    return $value
}

function Find-Game {
    $candidates = @()
    $registryPath = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 13570'
    if (Test-Path $registryPath) {
        $location = (Get-ItemProperty $registryPath).InstallLocation
        if ($location) { $candidates += $location }
    }
    $steamRoots = @("${env:ProgramFiles(x86)}\Steam")
    if (Test-Path 'HKCU:\Software\Valve\Steam') {
        $steamRoots += (Get-ItemProperty 'HKCU:\Software\Valve\Steam').SteamPath
    }
    foreach ($steam in $steamRoots | Select-Object -Unique) {
        if (-not $steam) { continue }
        $libraries = @($steam)
        $libraryFile = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $libraryFile) {
            $text = Get-Content -LiteralPath $libraryFile -Raw
            foreach ($match in [regex]::Matches($text, '"path"\s+"([^"]+)"')) {
                $libraries += $match.Groups[1].Value.Replace('\\', '\')
            }
        }
        foreach ($library in $libraries) {
            $candidates += Join-Path $library 'steamapps\common\Splintercell Chaos Theory'
        }
    }
    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-Path -LiteralPath (Join-Path $candidate 'System\splintercell3.exe')) { return $candidate }
    }
    return Read-Host 'Paste the game folder containing System and Data'
}

function Write-State($State, [string]$Path) {
    $temp = $Path + '.tmp'
    $State | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $temp -Encoding UTF8
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

function Restore-Files($State, [string]$Backup, [string]$Game) {
    # Validate every backup before restoring even the first game file.
    foreach ($record in $State.files) {
        if ($record.existed) { Assert-File (Safe-Path $Backup $record.path) $record.original_sha256 }
    }
    foreach ($record in $State.files) {
        $target = Safe-Path $Game $record.path
        if ($record.existed) {
            [IO.Directory]::CreateDirectory((Split-Path -Parent $target)) | Out-Null
            [IO.File]::Copy((Safe-Path $Backup $record.path), $target, $true)
            Assert-File $target $record.original_sha256
        }
        elseif (Test-Path -LiteralPath $target) {
            Remove-Item -LiteralPath $target -Force
        }
    }
}

try {
    if (@(@($CheckOnly, $Verify, $Uninstall) | Where-Object { $_ }).Count -gt 1) {
        throw 'Choose only one of -CheckOnly, -Verify, or -Uninstall.'
    }
    $manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.format -ne 1) { throw 'Unsupported release manifest.' }
    if (-not $GameDir) { $GameDir = Find-Game }
    if (-not $GameDir) { throw 'No game folder selected.' }
    $GameDir = [IO.Path]::GetFullPath($GameDir.Trim('"')).TrimEnd('\')
    $exe = Safe-Path $GameDir 'System/splintercell3.exe'
    $umd = Safe-Path $GameDir 'System/dynamic-pc.umd'
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) { throw 'Choose the game root, not its System folder.' }
    $backupRoot = Safe-Path $GameDir '.chaos-theory-thai'
    $statePath = Safe-Path $backupRoot 'state.json'
    $state = $null
    if (Test-Path -LiteralPath $statePath) {
        $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($state.version -ne $manifest.version -or $state.backup_id -notmatch '^[a-f0-9]{32}$') {
            throw 'Backup belongs to another version or has invalid metadata. Use its original installer.'
        }
        $expectedPaths = @($manifest.files.path | Sort-Object)
        $actualPaths = @($state.files.path | Sort-Object)
        if ($actualPaths.Count -ne $expectedPaths.Count -or
            (Compare-Object $expectedPaths $actualPaths)) { throw 'Invalid backup file list.' }
        $backup = Safe-Path $backupRoot ($state.backup_id + '/original')
    }
    if ($Uninstall) {
        if (-not $state -or $state.status -eq 'uninstalled') {
            Write-Host 'Mod is already uninstalled.'; exit 0
        }
        if (Get-Process -Name splintercell3 -ErrorAction SilentlyContinue) { throw 'Close the game first.' }
        if ($state.status -eq 'installed') {
            foreach ($record in $state.files) {
                Assert-File (Safe-Path $GameDir $record.path) $record.installed_sha256
            }
        }
        Restore-Files $state $backup $GameDir
        $state.status = 'uninstalled'
        Write-State $state $statePath
        Write-Host "Uninstall complete. Original files restored; backups retained in $backup"
        exit 0
    }
    # Package corruption and incompatible executable are rejected before writes.
    foreach ($record in $manifest.package_files) {
        Assert-File (Safe-Path $PSScriptRoot $record.path) $record.sha256 $record.size
    }
    Assert-File $exe $manifest.executable_sha256
    if ($state -and $state.status -eq 'installed') {
        foreach ($record in $manifest.files) {
            Assert-File (Safe-Path $GameDir $record.path) $record.sha256 $record.size
        }
        Write-Host "All $($manifest.files.Count) installed files verified. Mod $($manifest.version) is already installed."
        exit 0
    }
    if ($Verify) { throw 'No completed installation recorded for this release.' }
    if ($state -and $state.status -ne 'uninstalled') {
        throw 'An interrupted installation was recorded. Run Uninstall.cmd to restore the backup first.'
    }
    Assert-File $umd $manifest.base_umd_sha256
    foreach ($record in $manifest.files) {
        $target = Safe-Path $GameDir $record.path
        if (Test-Path -LiteralPath $target) {
            $item = Get-Item -LiteralPath $target
            if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReadOnly) -ne 0) {
                throw "Target must be a writable file: $target"
            }
        }
    }
    $settings = Safe-Path $GameDir 'System/SplinterCell3.ini'
    if (-not (Test-Path -LiteralPath $settings)) { throw 'Missing System/SplinterCell3.ini.' }
    $settingsText = Get-Content -LiteralPath $settings -Raw
    if ((Get-IniValue $settingsText 'Engine.Engine' 'Language') -ne 'int' -or
        (Get-IniValue $settingsText 'Init' 'UseDynamicDataFile') -ne 'true') {
        throw 'Set the game language to English (int) and UseDynamicDataFile=true before installing. See README-TH.txt.'
    }
    $languageFile = Safe-Path $GameDir 'System/Settings.ini'
    if ((Test-Path -LiteralPath $languageFile) -and
        (Get-IniValue (Get-Content -LiteralPath $languageFile -Raw) 'Localization' 'Language') -ne 'int') {
        throw 'System/Settings.ini must use Language=int. See README-TH.txt.'
    }
    if ($CheckOnly) {
        Write-Host 'PASS: package hashes, Steam executable, original UMD and English settings. No files changed.'
        exit 0
    }
    if (Get-Process -Name splintercell3 -ErrorAction SilentlyContinue) { throw 'Close the game first.' }
    $drive = New-Object IO.DriveInfo ([IO.Path]::GetPathRoot($GameDir))
    if ($drive.AvailableFreeSpace -lt 2GB) { throw 'At least 2 GB free space is required for staging and backups.' }
    Add-Type -Path (Safe-Path $PSScriptRoot 'Delta.cs')
    $backupId = [guid]::NewGuid().ToString('N')
    $session = Safe-Path $backupRoot $backupId
    $stage = Safe-Path $session 'stage'
    $backup = Safe-Path $session 'original'
    $records = @()
    Write-Host 'Preparing and checking the mod. This may take a minute...'
    foreach ($record in $manifest.files) {
        $target = Safe-Path $GameDir $record.path
        $staged = Safe-Path $stage $record.path
        [IO.Directory]::CreateDirectory((Split-Path -Parent $staged)) | Out-Null
        if ($record.PSObject.Properties.Name -contains 'patch') {
            [ChaosThaiDelta]::Apply($umd, (Safe-Path $PSScriptRoot $record.patch), $staged, $record.size)
        }
        else { [IO.File]::Copy((Safe-Path $PSScriptRoot $record.payload), $staged, $false) }
        Assert-File $staged $record.sha256 $record.size
        $existed = Test-Path -LiteralPath $target -PathType Leaf
        $originalDigest = $null
        if ($existed) {
            $originalDigest = Get-Digest $target
            $saved = Safe-Path $backup $record.path
            [IO.Directory]::CreateDirectory((Split-Path -Parent $saved)) | Out-Null
            [IO.File]::Copy($target, $saved, $false)
            Assert-File $saved $originalDigest
        }
        $records += [pscustomobject]@{ path = $record.path; existed = $existed;
            original_sha256 = $originalDigest; installed_sha256 = $record.sha256 }
    }
    $state = [pscustomobject]@{ version = $manifest.version; backup_id = $backupId;
        status = 'prepared'; files = $records }
    Write-State $state $statePath
    try {
        foreach ($record in $manifest.files) {
            $target = Safe-Path $GameDir $record.path
            [IO.Directory]::CreateDirectory((Split-Path -Parent $target)) | Out-Null
            [IO.File]::Copy((Safe-Path $stage $record.path), $target, $true)
            Assert-File $target $record.sha256 $record.size
        }
        $state.status = 'installed'
        Write-State $state $statePath
    }
    catch {
        $failure = $_
        Restore-Files $state $backup $GameDir
        $state.status = 'uninstalled'
        Write-State $state $statePath
        throw "Installation failed; originals restored: $failure"
    }
    # Remove only known staged files; retain all original backups and state.
    foreach ($record in $manifest.files) { Remove-Item -LiteralPath (Safe-Path $stage $record.path) }
    Write-Host "Installed Chaos Theory Thai $($manifest.version). All $($manifest.files.Count) files verified."
    Write-Host "Backup: $backup"
}
catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    Write-Host 'If access is denied under Program Files, run the CMD launcher as administrator.'
    exit 1
}
