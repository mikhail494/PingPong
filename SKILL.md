---
name: pingpong
description: Cross-model development loop where Codex builds and fixes while Claude independently critiques. Sonnet is default; Opus can be requested for high-stakes review.
---

# PingPong

Codex is the Builder/Fixer.

Claude is an independent read-only Critic.

Deterministic gates outrank both models.

## Invocation modes

### Default

`$pingpong <task>`

Critic: Sonnet.

Use for normal development.

Maximum Sonnet review rounds: 4.

### Final Opus

`$pingpong final-opus <task>`

Use Sonnet for the normal build/fix loop.

Once Sonnet returns PASS:

1. Run one independent Opus review.
2. If Opus returns PASS, finish.
3. If Opus returns FAIL, independently verify the findings.
4. Fix only valid BLOCKER/HIGH findings.
5. Rerun deterministic gates.
6. Run Opus one final time.
7. If Opus still does not PASS, stop and report rather than looping indefinitely.

This is the preferred mode for important changes where Opus should be conserved.

### Full Opus

`$pingpong opus <task>`

Use Opus as Critic for every review round.

Maximum Opus review rounds: 3.

Use only when explicitly requested.

## Task authoring contract

A PingPong task may be written directly by the user or prepared by another planning chat.

Treat everything after the invocation mode as the authoritative task scope. A strong task states the goal, constraints or non-goals, acceptance criteria, and required tests or gates.

Do not require special planner syntax beyond the PingPong invocation itself. Do not silently expand the task. If material domain semantics are missing, resolve them only from authoritative project evidence; otherwise stop with USER_REQUIRED rather than inventing them.

## Self-test

`$pingpong self-test`

Use Sonnet.

`SKILL_DIR` is not a predefined environment variable. When PingPong is
invoked, determine the actual absolute directory from which this `SKILL.md`
was loaded and use that directory as the skill root. If the loaded path cannot
be determined unambiguously, stop rather than guessing. Before executing a
reviewer command, explicitly set `SKILL_DIR` in the current shell/session to
that directory, or substitute the absolute path directly. The reviewer script
is always a sibling under the skill root; never assume `.agents`, `.codex`, or
another fixed global skill directory.

Run:

python "$SKILL_DIR/scripts/claude_review.py" --repo . --self-test --model sonnet

Success requires:

`CLAUDE_CRITIC_OK`

Do not modify project files during self-test.

## Normal workflow

### 0. Safety

Before changing anything:

- confirm the current repository,
- run `git status --short`,
- preserve unrelated user changes,
- never reset/revert/stash/delete user work without explicit permission.

Normal PingPong development requires a Git repository.

If the project is not a Git repository, stop and report that local Git must be initialized first.

### 1. Parse mode

If the first task token is:

`opus`

remove that token from the actual task and use Claude model `opus`.

If the first task token is:

`final-opus`

remove that token from the actual task and use the hybrid workflow described above.

Otherwise use Claude model `sonnet`.

Do not silently escalate to Opus.

### 2. Capture task

Create:

`.pingpong/current_task.md`

containing the requested task faithfully.

Do not silently expand scope.

### 3. Build

Implement the task yourself.

Codex is the only model allowed to modify project files.

Never invent missing trading semantics.

If a material trading interpretation is ambiguous:

stop with USER_REQUIRED.

### 4. Deterministic gates

Run all relevant project checks that exist:

- tests,
- lint,
- typecheck,
- build,
- project-specific verification.

Save meaningful output to:

`.pingpong/gates.txt`

A failing deterministic correctness gate cannot be overridden by either model.

### 5. Claude review

Use the reviewer script from the installed skill directory:

`$SKILL_DIR/scripts/claude_review.py`

Here `SKILL_DIR` is the shell/session variable explicitly set to the absolute
directory from which the loaded `SKILL.md` came, as described in Self-test.

For Sonnet:

python "$SKILL_DIR/scripts/claude_review.py" `
  --repo . `
  --model sonnet `
  --mode implementation `
  --task-file .pingpong/current_task.md `
  --gate-file .pingpong/gates.txt `
  --out .pingpong/runs/round_NN_sonnet.json

For Opus:

python "$SKILL_DIR/scripts/claude_review.py" `
  --repo . `
  --model opus `
  --mode implementation `
  --task-file .pingpong/current_task.md `
  --gate-file .pingpong/gates.txt `
  --out .pingpong/runs/round_NN_opus.json

### 6. Evaluate Claude independently

Never blindly obey the Critic.

For every BLOCKER/HIGH:

- verify it against task/spec/code/tests,
- fix it if valid,
- reject it if invalid only with concrete evidence.

MEDIUM/LOW do not block completion unless they expose a real requirement violation.

Do not perform unrelated cleanup merely because Claude suggested it.

### 7. Repeat

After valid fixes:

- rerun deterministic gates,
- rerun the selected Critic.

Respect the model-specific round limits.

### 8. PASS

Completion requires:

- required deterministic gates PASS,
- final required Claude review PASS,
- no unresolved valid BLOCKER/HIGH.

### 9. USER_REQUIRED

Stop when:

- trading semantics are materially ambiguous,
- authoritative sources conflict,
- safe continuation requires a human decision.

Never let either model invent the answer.

### 10. Final response

Report:

- implemented work,
- deterministic gate result,
- Critic model(s),
- review rounds per model,
- final verdict,
- valid findings fixed,
- Claude findings rejected with evidence,
- USER_REQUIRED status if applicable.

Example:

PingPong PASS
Builder: Codex
Critic: Sonnet
Sonnet rounds: 2
Final Opus gate: PASS
Deterministic gates: PASS
