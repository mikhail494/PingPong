# Contributing

Thanks for taking a look at PingPong. The project is intentionally small, so focused changes are easier to review than broad rewrites.

## Core invariants

Changes should preserve these properties unless the change explicitly proposes a new design:

1. **Codex builds; Claude critiques.** Claude must remain read-only with respect to the project being reviewed.
2. **Deterministic gates outrank model opinions.** A failing required correctness gate cannot be waived by either model.
3. **Codex verifies Claude findings.** PingPong should not blindly apply critic output.
4. **No silent Opus escalation.** Sonnet remains the default critic unless the user explicitly requests an Opus mode.
5. **Ambiguity is explicit.** Material missing domain semantics should stop with `USER_REQUIRED`, not be guessed.
6. **Installation is location-independent.** Do not add hardcoded `.agents`, `.codex`, or user-specific runtime paths.
7. **User work is preserved.** Never reset, revert, stash, or delete unrelated project work without explicit permission.

## Local checks

Zero-LLM checks:

```powershell
python -m py_compile scripts\claude_review.py
python scripts\claude_review.py --help
powershell -NoProfile -ExecutionPolicy Bypass -File .\doctor.ps1
```

`doctor.ps1` does not make a model request. It checks packaging and local dependencies only.

A real critic self-test does consume Claude usage:

```text
$pingpong self-test
```

Run it only when the change affects installation, skill path resolution, or Claude invocation.

## Pull requests

Please keep pull requests narrow and include:

- what behavior changed;
- why the change is needed;
- which zero-LLM checks passed;
- whether a real Claude self-test was run;
- any compatibility or packaging impact.

Do not commit API keys, tokens, private repositories, private prompts, customer data, or other sensitive fixtures.
