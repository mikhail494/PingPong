$ErrorActionPreference = "Continue"

$source = Join-Path $PSScriptRoot "skill"
$installed = Join-Path $env:USERPROFILE ".agents\skills\pingpong"

function Check-Command {
    param(
        [string]$Name
    )

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue

    if ($cmd) {
        Write-Host "[OK]   $Name"
        Write-Host "       $($cmd.Source)"
        return $true
    }

    Write-Host "[FAIL] $Name not found"
    return $false
}

function Compare-File {
    param(
        [string]$RelativePath
    )

    $a = Join-Path $source $RelativePath
    $b = Join-Path $installed $RelativePath

    if (-not (Test-Path $a)) {
        Write-Host "[FAIL] Source missing: $RelativePath"
        return
    }

    if (-not (Test-Path $b)) {
        Write-Host "[FAIL] Installed missing: $RelativePath"
        return
    }

    $ha = (Get-FileHash $a -Algorithm SHA256).Hash
    $hb = (Get-FileHash $b -Algorithm SHA256).Hash

    if ($ha -eq $hb) {
        Write-Host "[OK]   In sync: $RelativePath"
    } else {
        Write-Host "[WARN] Installed copy differs: $RelativePath"
        Write-Host "       Run update.ps1"
    }
}

Write-Host ""
Write-Host "====================================="
Write-Host " PingPong Doctor"
Write-Host "====================================="
Write-Host ""

Write-Host "Source:"
Write-Host "  $PSScriptRoot"

if (Test-Path (Join-Path $PSScriptRoot "VERSION")) {
    $version = (Get-Content (Join-Path $PSScriptRoot "VERSION") -Raw).Trim()
    Write-Host "Version:"
    Write-Host "  $version"
}

Write-Host ""
Write-Host "Commands"

$pythonOk = Check-Command "python"
$gitOk = Check-Command "git"
$codexOk = Check-Command "codex"
$claudeOk = Check-Command "claude"

Write-Host ""
Write-Host "Versions"

if ($pythonOk) {
    python --version
}

if ($gitOk) {
    git --version
}

if ($codexOk) {
    codex --version
}

if ($claudeOk) {
    claude --version
}

Write-Host ""
Write-Host "Codex authentication"

if ($codexOk) {
    codex login status
} else {
    Write-Host "[SKIP] Codex unavailable"
}

Write-Host ""
Write-Host "Claude billing environment"

$apiKeyFound = $false

foreach ($scope in @("Process", "User", "Machine")) {
    $value = [Environment]::GetEnvironmentVariable(
        "ANTHROPIC_API_KEY",
        $scope
    )

    if (-not [string]::IsNullOrWhiteSpace($value)) {
        Write-Host "[WARN] ANTHROPIC_API_KEY is set in $scope scope"
        $apiKeyFound = $true
    }
}

if (-not $apiKeyFound) {
    Write-Host "[OK]   ANTHROPIC_API_KEY not found"
}

Write-Host ""
Write-Host "Global installation"

if (Test-Path $installed) {
    Write-Host "[OK]   PingPong installed globally"
    Write-Host "       $installed"
} else {
    Write-Host "[FAIL] PingPong global skill not installed"
}

Write-Host ""
Write-Host "Installed version sync"

Compare-File "SKILL.md"
Compare-File "scripts\claude_review.py"

Write-Host ""
Write-Host "Configuration"

Write-Host "Default Critic: Sonnet"
Write-Host "Final Opus mode: configured"
Write-Host "Full Opus mode: configured"
Write-Host ""
Write-Host "No LLM request was made by doctor."