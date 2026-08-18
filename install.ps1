param(
    [switch]$NoBackup
)

$ErrorActionPreference = "Stop"

$source = Join-Path $PSScriptRoot "skill"
$target = Join-Path $env:USERPROFILE ".agents\skills\pingpong"

if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
    throw "Source SKILL.md not found: $source"
}

if (-not (Test-Path (Join-Path $source "scripts\claude_review.py"))) {
    throw "Claude reviewer not found in source tree."
}

if ((Test-Path $target) -and (-not $NoBackup)) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupRoot = Join-Path $env:USERPROFILE ".agents\skills"
    $backup = Join-Path $backupRoot "pingpong-backup-$stamp"

    Copy-Item $target $backup -Recurse -Force

    Write-Host "Backup created:"
    Write-Host "  $backup"
}

Remove-Item $target -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item (Join-Path $source "*") $target -Recurse -Force

Write-Host ""
Write-Host "PingPong installed."
Write-Host "Source:"
Write-Host "  $source"
Write-Host "Installed:"
Write-Host "  $target"
Write-Host ""
Write-Host "Use in Codex:"
Write-Host '  $pingpong <task>'
Write-Host '  $pingpong final-opus <task>'
Write-Host '  $pingpong opus <task>'