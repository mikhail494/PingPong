# FAQ

## Does Claude edit my project?

No. PingPong keeps Claude in the **Critic** role. The current Codex session is the only Builder/Fixer.

## Does PingPong replace tests?

No. Deterministic checks outrank both models. Tests, lint, type checks, builds, and project-specific gates remain the strongest evidence in the loop.

## Which Claude model is used by default?

Claude Sonnet. Opus is used only when you explicitly invoke an Opus mode.

## What does `USER_REQUIRED` mean?

The reviewer found a material ambiguity that cannot be resolved from the task, project specifications, implementation state, or deterministic evidence. PingPong stops instead of inventing a domain rule.

## What project data can be sent to Claude?

Depending on the review, PingPong can include the task, selected authoritative project files, staged and unstaged diffs, Git status, untracked text files, and deterministic gate output. See [SECURITY.md](../SECURITY.md) and [DESIGN.md](DESIGN.md).

## Does PingPong need a separate Codex CLI process?

No. The current Codex session is the Builder/Fixer.

## Does it need a Claude API key?

PingPong uses your locally installed and authenticated Claude Code CLI. It does not manage Claude authentication or billing itself.

## Is it Windows-only?

Windows is the primary clean-room tested environment today. The reviewer runner is Python-based, but packaging and workflow behavior outside Windows should be treated as less tested until verified.

## Can I use PingPong for trading or other domain-sensitive systems?

Yes, but domain semantics must live in authoritative project material. If the evidence does not resolve an important interpretation, the correct outcome is `USER_REQUIRED`, not a model guess.

## Why not let both models edit code?

The asymmetry is intentional. Separating implementation from critique makes it easier to reason about responsibility, verify findings, and keep the final reviewed diff stable.
