param(
    [switch]$NoBackup
)

$ErrorActionPreference = "Stop"

$source = $PSScriptRoot
$target = Join-Path $env:USERPROFILE ".agents\skills\pingpong"

if (-not (Test-Path (Join-Path $source "SKILL.md"))) {
    throw "SKILL.md not found: $source"
}

if (-not (Test-Path (Join-Path $source "scripts\claude_review.py"))) {
    throw "Claude reviewer not found."
}

if ((Test-Path $target) -and (-not $NoBackup)) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backup = Join-Path $env:USERPROFILE ".agents\skills\pingpong-backup-$stamp"
    Copy-Item $target $backup -Recurse -Force
    Write-Host "Backup: $backup"
}

Remove-Item $target -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $target | Out-Null

Copy-Item (Join-Path $source "SKILL.md") $target -Force
Copy-Item (Join-Path $source "scripts") $target -Recurse -Force

if (Test-Path (Join-Path $source "agents")) {
    Copy-Item (Join-Path $source "agents") $target -Recurse -Force
}

if (Test-Path (Join-Path $source "VERSION")) {
    Copy-Item (Join-Path $source "VERSION") $target -Force
}

Write-Host ""
Write-Host "PingPong installed globally:"
Write-Host "  $target"