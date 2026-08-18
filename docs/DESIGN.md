# Design

PingPong is a deliberately asymmetric two-model development loop.

Its goal is not to create a committee of agents. Its goal is to separate **implementation authority** from **independent review** while keeping deterministic checks above both models.

## Roles

### Codex: Builder/Fixer

Codex owns project mutations. It:

- implements the user task;
- runs available deterministic gates;
- receives Claude findings;
- verifies those findings against the task, specifications, code, and test evidence;
- fixes findings that are actually supported;
- may reject unsupported findings with concrete evidence.

### Claude: Critic

Claude is invoked through the local Claude Code CLI with tools disabled for the review turn. It is instructed to act as a read-only adversarial reviewer, not an implementer.

The critic does not decide project architecture merely because an alternative design is possible. Blocking findings must be evidence-backed.

### Supplementary reviewers

A project workflow or Codex may use additional specialized read-only reviewer agents when they materially help verify the task. They are supplemental rather than authoritative:

- only Codex may mutate project files;
- they do not replace deterministic gates;
- they do not replace the required Claude critic for the selected PingPong mode;
- they must not expand task scope merely to polish the implementation.

In `final-opus` mode, all supplementary reviews must complete **before** the final Opus gate. If their findings cause project changes after a Sonnet PASS, deterministic gates and Sonnet must review the changed state again within the configured round limit before Opus runs.

This preserves the useful specialization of extra reviewers while ensuring that the final Opus verdict applies to the actual final project diff.

## Trust ordering

PingPong uses the following ordering when sources disagree:

1. deterministic required gates;
2. explicit user task;
3. authoritative project specifications;
4. actual implementation state and Git evidence;
5. model interpretation.

A model cannot override a failing deterministic correctness gate.

## Review payload

For a normal implementation review, `scripts/claude_review.py` can supply Claude with:

- the captured task;
- authoritative project files when present, including `AGENTS.md`, `spec/STRATEGY_SPEC.md`, `spec/RULES.md`, `STRATEGY_SPEC.md`, and `RULES.md`;
- unstaged Git diff;
- staged Git diff;
- `git status --short`;
- untracked text files;
- deterministic gate output.

Untracked files that appear binary are represented as binary placeholders rather than raw content. Untracked text is capped at 100,000 characters per file.

## Verdicts

The critic returns structured JSON with one of three verdicts.

### PASS

No unresolved `BLOCKER` or `HIGH` findings remain.

### FAIL

There is at least one concrete blocking issue that Codex can resolve from the evidence already available.

### USER_REQUIRED

A material decision cannot be resolved from the available evidence and requires a human or domain expert.

This is especially important in domain-sensitive systems. A plausible guess is not treated as a valid specification.

## Finding severity

- **BLOCKER**: unsafe to continue or fundamentally incorrect.
- **HIGH**: demonstrable correctness/security issue or material explicit-requirement violation.
- **MEDIUM**: real, evidence-supported, non-blocking concern.
- **LOW**: minor or optional improvement.

Hypothetical future callers, unspecified validation preferences, style choices, and alternative architectures are not sufficient by themselves for blocking severity.

## Loop bounds

PingPong intentionally prevents infinite model-to-model debate.

- Default Sonnet mode: at most 4 critic rounds.
- Full Opus mode: at most 3 critic rounds.
- Final-Opus mode: Sonnet handles the normal loop; any permitted supplementary reviewers complete before the transition to Opus; after the current project state has Sonnet PASS, Opus performs one independent final review. If Opus finds a valid blocking issue, Codex may fix it and Opus gets one final check.

If supplementary review changes the project after a Sonnet PASS, that PASS no longer authorizes the transition to Opus. Gates and Sonnet must review the new state again within the normal Sonnet round budget.

If the required verdict still cannot be reached, PingPong stops and reports the state instead of looping forever.

## Finality invariant

The final required critic PASS applies only to the exact project state it reviewed.

After the final required PASS, implementation is frozen. No additional reviewer agent, cleanup pass, refactor, or optional hardening step may mutate the project and still rely on the previous PASS.

If a project file changes after the final PASS, that verdict is invalidated. Deterministic gates and the required final critic must review the new state again within the configured round limit before PingPong may report PASS.

A critic PASS containing only optional `MEDIUM`/`LOW` observations does not by itself justify another build/review cycle.

## Domain-sensitive review

Project-specific semantics belong in the project, not in PingPong.

For trading systems, for example, the critic is instructed to look for evidence-backed problems such as lookahead bias, repainting, candle-close timing mistakes, impossible historical fills, fee/slippage errors, state divergence between simulation and live modes, unsafe execution/recovery, and invented strategy semantics.

If multiple plausible domain interpretations exist and authoritative material does not choose one, the correct verdict is `USER_REQUIRED`.

## Installation model

The repository root is the skill root. Runtime commands resolve the reviewer relative to the actual loaded `SKILL.md` rather than assuming a fixed `.agents` or `.codex` path.

This allows Codex's normal GitHub skill installation workflow to install a single copy of PingPong and use that copy directly.

## Non-goals

PingPong does not aim to:

- replace deterministic tests;
- make Claude an autonomous code editor;
- spawn a second Codex process as Builder;
- turn supplementary reviewers into additional project authorities;
- silently choose expensive models;
- invent missing product or domain requirements;
- hide disagreement between the critic and builder.
