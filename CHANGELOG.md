# Changelog

All notable changes to PingPong are documented here.

The project is pre-1.0, so workflow and packaging details may still change between minor releases.

## Unreleased

- Reworked the public documentation around the Builder/Critic model.
- Added repository validation that makes no LLM requests.
- Added architecture, contribution, and security documentation.
- Corrected Codex skill UI metadata to reflect Sonnet as the default critic.
- Added task-authoring guidance for planning chats that generate ready-to-paste PingPong commands.
- Added a finality invariant: the final critic PASS applies only to the exact project diff it reviewed.
- Project changes after the final required PASS now invalidate that PASS and require gates plus the required final critic to run again.
- A PASS containing only optional MEDIUM/LOW observations no longer triggers extra implementation/review rounds merely for polishing.
- Extra reviewer agents must not cause project changes after the final required PASS.
- Supplementary project/Codex reviewer agents are explicitly allowed before the final Opus gate; any fixes they trigger must be included in the state rechecked by deterministic gates and Sonnet before Opus runs.

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