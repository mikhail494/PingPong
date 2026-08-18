# PingPong

Cross-model development review loop for Codex.

Codex builds.
Claude independently critiques.
Codex verifies the critique, fixes valid findings, and repeats until the quality gate passes.

## Why

Instead of:

Codex -> you review -> corrective prompt -> Codex -> you review again

PingPong runs:

Codex -> Claude Critic -> Codex Fix -> Claude Critic -> PASS

You stay in the Codex chat.

## Install with Codex

Give Codex this repository URL and say:

> Install this repository globally as the `pingpong` Codex skill. Verify that Claude Code is available, run PingPong doctor, and do not modify the current project.

After installation, use:

    $pingpong <task>

## Manual install

Clone the repository directly into your global Codex skills directory.

Windows PowerShell:

    git clone <REPOSITORY_URL> "$env:USERPROFILE\.agents\skills\pingpong"

Then run:

    powershell -NoProfile -ExecutionPolicy Bypass -File "$env:USERPROFILE\.agents\skills\pingpong\doctor.ps1"

## Requirements

- Codex
- Claude Code CLI
- Git
- Python
- authenticated Codex and Claude sessions

PingPong uses your locally installed Claude Code CLI. Check your own Claude authentication, plan and billing configuration before use.

## Modes

### Default

    $pingpong <task>

Codex builds and Claude Sonnet reviews.

Use this for normal development.

### Final Opus

    $pingpong final-opus <task>

Sonnet handles the normal critique loop.

After Sonnet passes, Claude Opus performs an independent final review.

This is the recommended mode for important changes when you want stronger final review without spending Opus usage on every round.

### Full Opus

    $pingpong opus <task>

Claude Opus reviews every round.

Use for high-stakes work when explicitly needed.

## What PingPong does

1. Captures the requested task.
2. Codex implements it.
3. Runs available deterministic quality gates.
4. Sends the task, specifications, Git changes and gate results to Claude.
5. Claude returns PASS, FAIL or USER_REQUIRED with structured findings.
6. Codex independently checks every important finding.
7. Valid findings are fixed.
8. Unsupported findings may be rejected with evidence.
9. The loop repeats with hard round limits.

## Safety model

Codex is the Builder/Fixer.

Claude is the Critic.

Claude does not edit the project.

Deterministic tests and quality gates outrank both models.

PingPong must not invent missing domain semantics. If an important decision cannot be resolved from available evidence, it stops with USER_REQUIRED.

## Trading and other high-stakes domains

PingPong can apply additional adversarial scrutiny to domain-sensitive code, but domain-specific rules should live in the project being reviewed, not in PingPong itself.

For trading systems the Critic specifically looks for evidence-backed problems such as:

- lookahead bias
- repainting
- candle timing errors
- impossible historical fills
- incorrect fee or slippage handling
- backtest/live divergence
- unsafe execution or recovery behavior
- invented trading semantics

## Doctor

Doctor makes no LLM request and consumes no model usage.

From the repository:

    powershell -NoProfile -ExecutionPolicy Bypass -File .\doctor.ps1

## Update

If installed with Git:

    git -C "$env:USERPROFILE\.agents\skills\pingpong" pull

## Status

Early working prototype.

Current version: 0.1.0

Tested first on Windows with Codex + Claude Code.

## License

MIT