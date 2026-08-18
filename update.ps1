$ErrorActionPreference = "Stop"

Write-Host "Updating PingPong from local source..."
Write-Host ""

& (Join-Path $PSScriptRoot "install.ps1")