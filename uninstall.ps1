$ErrorActionPreference = "Stop"

$target = Join-Path $env:USERPROFILE ".agents\skills\pingpong"

if (-not (Test-Path $target)) {
    Write-Host "PingPong is not installed."
    exit 0
}

Remove-Item $target -Recurse -Force

Write-Host "PingPong removed:"
Write-Host "  $target"
Write-Host ""
Write-Host "Standalone source was NOT deleted."