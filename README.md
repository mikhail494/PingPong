# PingPong

PingPong is a cross-model development review loop for Codex.

Codex acts as the Builder/Fixer.
Claude acts as an independent read-only Critic.
Deterministic tests and quality gates outrank both models.

## Modes

Default:

    $pingpong <task>

Uses Claude Sonnet as Critic.

Final Opus:

    $pingpong final-opus <task>

Uses Sonnet for the normal review loop, then Opus as a final independent gate.

Full Opus:

    $pingpong opus <task>

Uses Opus for all critique rounds.

## Install

From PowerShell:

    powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1

The skill is installed to:

    %USERPROFILE%\.agents\skills\pingpong

## Update

    powershell -NoProfile -ExecutionPolicy Bypass -File .\update.ps1

## Doctor

Doctor does not call an LLM and does not consume model usage:

    powershell -NoProfile -ExecutionPolicy Bypass -File .\doctor.ps1

## Uninstall

    powershell -NoProfile -ExecutionPolicy Bypass -File .\uninstall.ps1

## Development model

PingPong intentionally separates responsibilities:

- Codex can modify project files.
- Claude is the independent Critic.
- Claude findings are not blindly accepted.
- Codex must verify findings against task, specification, code and tests.
- Missing or ambiguous domain semantics must be escalated instead of invented.
- Review loops have hard round limits.

## Status

Current version: 0.1.0

This is an early working prototype.