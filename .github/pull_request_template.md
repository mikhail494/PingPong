## What changed?

<!-- Keep the change focused. Describe the behavior, not just the files. -->

## Why?

<!-- What problem does this solve? -->

## Validation

- [ ] `python -m py_compile scripts/claude_review.py`
- [ ] `python scripts/claude_review.py --help`
- [ ] `powershell -NoProfile -ExecutionPolicy Bypass -File .\doctor.ps1`
- [ ] Real `$pingpong self-test` run if this change affects installation, path resolution, or Claude invocation
- [ ] No secrets, private repositories, private prompts, or customer data added

## Core invariants

- [ ] Codex remains the only Builder/Fixer
- [ ] Claude remains read-only with respect to the reviewed project
- [ ] Deterministic gates outrank model opinions
- [ ] Sonnet remains the default; no silent Opus escalation
- [ ] Missing domain semantics are not invented
- [ ] Final PASS still applies to the exact project state reviewed
