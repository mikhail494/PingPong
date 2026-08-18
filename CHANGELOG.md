# Changelog

All notable changes to PingPong are documented here.

The project is pre-1.0, so workflow and packaging details may still change between minor releases.

## Unreleased

- Reworked the public documentation around the Builder/Critic model.
- Added repository validation that makes no LLM requests.
- Added architecture, contribution, and security documentation.
- Corrected Codex skill UI metadata to reflect Sonnet as the default critic.

## v0.1.1 - 2026-08-18

- Made the skill installation location-independent.
- Removed the legacy second-copy installation path under `.agents`.
- Made `doctor.ps1` self-contained through `$PSScriptRoot`.
- Removed the unnecessary separate Codex CLI authentication check.
- Added explicit `SKILL_DIR` handling in the skill workflow.
- Clean-room tested standard GitHub installation into the Codex skills directory.
- Verified the installed critic end-to-end with Claude Sonnet and `CLAUDE_CRITIC_OK`.

## v0.1.0 - 2026-08-18

Initial working prototype:

- Codex as Builder/Fixer.
- Claude as independent read-only Critic.
- Sonnet default mode.
- Final-Opus and full-Opus modes.
- Structured `PASS`, `FAIL`, and `USER_REQUIRED` verdicts.
- Deterministic gate precedence.
- Git diff, staged diff, status, and untracked-text review context.
- Evidence-focused review rules for correctness and domain-sensitive code.
