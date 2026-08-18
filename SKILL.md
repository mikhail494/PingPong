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

Before transitioning to the final Opus gate, any project-required or Codex-selected supplementary read-only reviewer agents may run. They are supplemental only: Codex remains the only model allowed to modify project files, deterministic gates still outrank model opinions, and supplementary reviewers never replace the required Sonnet/Opus critics.

If supplementary reviewers cause Codex to make project changes after a Sonnet PASS, that Sonnet PASS no longer triggers the final Opus gate. Rerun deterministic gates and Sonnet on the changed project state within the configured Sonnet round limit. Transition to Opus only after all supplementary reviews and resulting fixes are complete and the current project state has the required Sonnet PASS.

Once the current project state has Sonnet PASS and all permitted supplementary reviews are complete:

1. Run one independent Opus review.
2. If Opus returns PASS, freeze the reviewed project diff and finish without further implementation changes or extra reviewer agents.
3. If Opus returns FAIL, independently verify the findings.
4. Fix only valid BLOCKER/HIGH findings.
5. Rerun deterministic gates.
6. Run Opus one final time.
7. If Opus still does not PASS, stop and report rather than looping indefinitely.

Any project-file change after a required Opus PASS invalidates that PASS. If such a change occurs, the deterministic gates and required final critic must review the new diff again within the configured round limit; otherwise do not report PingPong PASS.

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

MEDIUM/LOW do not block completion unless independent verification shows that they actually expose an explicit requirement, correctness, security, or safety violation.

A critic PASS with only MEDIUM/LOW observations does not trigger another implementation/review round merely because the suggestions are useful. Report optional observations instead of polishing indefinitely.

Do not perform unrelated cleanup merely because Claude suggested it.

### 7. Repeat

After valid blocking fixes:

- rerun deterministic gates,
- rerun the selected Critic.

Do not repeat solely to address optional MEDIUM/LOW findings after PASS.

Respect the model-specific round limits.

### 7A. Supplementary reviewers

Project-required or Codex-selected supplementary reviewer agents are allowed when they materially help verify the task. They must be read-only; only Codex may mutate project files.

In `final-opus` mode, all supplementary reviewer agents must finish before the final Opus gate. If their findings lead to project changes, rerun deterministic gates and obtain a Sonnet PASS on that changed state before transitioning to Opus.

Supplementary reviewers:

- do not replace deterministic gates;
- do not replace the required Claude critic for the selected PingPong mode;
- must not silently expand task scope;
- do not justify optional cleanup or polishing loops;
- must never run after the final required Opus PASS in a way that can cause further project changes.

The final Opus review should therefore see the project state after all permitted supplementary reviews and all accepted fixes.

### 8. PASS and finality invariant

Completion requires:

- required deterministic gates PASS,
- final required Claude review PASS,
- no unresolved valid BLOCKER/HIGH.

The final required critic PASS applies only to the exact project state it reviewed.

After the final required PASS:

- freeze implementation changes;
- do not spawn additional review agents that can cause further fixes;
- do not perform cleanup, hardening, refactors, or optional improvements;
- re-check `git status --short` and the relevant Git diff immediately before reporting completion.

If any project file changes after that PASS, the PASS is invalidated. Rerun deterministic gates and the required final critic on the new state within the configured round limit. If the round limit does not permit another required review, stop and report that final verification was not completed; do not claim PASS.

Changes limited to PingPong's own review/audit logs under `.pingpong/` do not invalidate the reviewed project diff unless those files are part of the task or project deliverable.

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
- optional MEDIUM/LOW observations left unimplemented after PASS,
- supplementary reviewer agents used before the final critic, if any,
- whether the project diff changed after the final required critic PASS,
- USER_REQUIRED status if applicable.

Example:

PingPong PASS
Builder: Codex
Critic: Sonnet
Sonnet rounds: 2
Supplementary reviewers: none
Final Opus gate: PASS
Deterministic gates: PASS
Post-final-pass project changes: none