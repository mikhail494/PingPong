$ErrorActionPreference = "Continue"

$skillRoot = $PSScriptRoot
$checksFailed = 0

function Check-Command {
    param([string]$Name)

    $cmd = Get-Command $Name -ErrorAction SilentlyContinue

    if ($cmd) {
        Write-Host "[OK]   $Name"
        Write-Host "       $($cmd.Source)"
        return $true
    }

    Write-Host "[FAIL] $Name not found"
    $script:checksFailed++
    return $false
}

function Check-File {
    param([string]$RelativePath)

    $path = Join-Path $skillRoot $RelativePath

    if (Test-Path $path -PathType Leaf) {
        Write-Host "[OK]   $RelativePath"
        return $true
    }

    Write-Host "[FAIL] Missing from this skill copy: $RelativePath"
    $script:checksFailed++
    return $false
}

Write-Host ""
Write-Host "====================================="
Write-Host " PingPong Doctor"
Write-Host "====================================="
Write-Host ""

Write-Host "Skill copy:"
Write-Host "  $skillRoot"

$versionPath = Join-Path $skillRoot "VERSION"
if (Test-Path $versionPath -PathType Leaf) {
    $version = (Get-Content $versionPath -Raw).Trim()
    Write-Host "Version:"
    Write-Host "  $version"
}

Write-Host ""
Write-Host "Required files"
$null = Check-File "SKILL.md"
$null = Check-File "scripts\claude_review.py"

Write-Host ""
Write-Host "Required commands"
$pythonOk = Check-Command "python"
$gitOk = Check-Command "git"
$claudeOk = Check-Command "claude"

Write-Host ""
Write-Host "Versions"
if ($pythonOk) { python --version }
if ($gitOk) { git --version }
if ($claudeOk) { claude --version }

Write-Host ""
Write-Host "Claude authentication"
Write-Host "[INFO] Not verified: doctor makes no LLM request and does not claim Claude authentication status."

Write-Host ""
Write-Host "Configuration"
Write-Host "Default Critic: Sonnet"
Write-Host "Final Opus mode: configured"
Write-Host "Full Opus mode: configured"
Write-Host ""
Write-Host "No LLM request was made by doctor."

if ($checksFailed -gt 0) {
    exit 1
}

exit 0
