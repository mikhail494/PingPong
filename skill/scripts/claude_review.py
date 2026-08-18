import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


MAX_FILE_CHARS = 100_000

CRITIC_SYSTEM_PROMPT = """
You are an independent adversarial software critic.

You are NOT the implementer.
You are read-only.
You have no tools.
Do not modify anything.
Do not invent requirements.
Do not perform stylistic review unless style affects correctness.

Your only job is to falsify correctness using the evidence supplied
in the user message and return exactly the requested JSON.
""".strip()


def fail(message, code=2, **extra):
    payload = {"ok": False, "error": message, **extra}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


def run_git(repo, *args):
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())

    return proc.stdout


def read_if_exists(path):
    if not path.is_file():
        return None

    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def collect_untracked(repo):
    raw = run_git(
        repo,
        "ls-files",
        "--others",
        "--exclude-standard",
    )

    files = []

    for rel in raw.splitlines():
        rel = rel.strip()

        if not rel:
            continue

        path = repo / rel

        if not path.is_file():
            continue

        try:
            data = path.read_bytes()
        except OSError:
            continue

        if b"\x00" in data[:8192]:
            files.append(
                f"\n===== UNTRACKED BINARY: {rel} =====\n"
                "(binary content omitted)"
            )
            continue

        text = data.decode("utf-8", errors="replace")

        if len(text) > MAX_FILE_CHARS:
            text = (
                text[:MAX_FILE_CHARS]
                + f"\n\n[TRUNCATED after {MAX_FILE_CHARS} characters]"
            )

        files.append(
            f"\n===== UNTRACKED FILE: {rel} =====\n{text}"
        )

    return "\n".join(files) if files else "(none)"


def detect_actual_model(payload, requested):
    usage = payload.get("modelUsage", {})

    for key, value in usage.items():
        canonical = value.get("canonicalModel", "")

        if requested.lower() in key.lower():
            return canonical or key

        if requested.lower() in canonical.lower():
            return canonical

    if usage:
        key = list(usage.keys())[-1]
        value = usage[key]
        return value.get("canonicalModel") or key

    return None


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--repo",
        required=True,
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
    )

    parser.add_argument(
        "--mode",
        choices=["implementation"],
        default="implementation",
    )

    parser.add_argument(
        "--model",
        choices=["sonnet", "opus"],
        default="sonnet",
    )

    parser.add_argument("--task-file")
    parser.add_argument("--gate-file")
    parser.add_argument("--out")

    args = parser.parse_args()

    repo = Path(args.repo).resolve()

    if not repo.is_dir():
        return fail(
            f"Repo not found: {repo}"
        )

    claude = (
        shutil.which("claude.cmd")
        or shutil.which("claude")
    )

    if not claude:
        return fail(
            "Claude CLI not found in PATH"
        )

    if args.self_test:
        prompt = "Reply exactly: CLAUDE_CRITIC_OK"

    else:
        if not args.task_file:
            return fail(
                "--task-file is required for review mode"
            )

        task_path = Path(args.task_file)

        if not task_path.is_absolute():
            task_path = repo / task_path

        if not task_path.is_file():
            return fail(
                f"Task file not found: {task_path}"
            )

        task = task_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        try:
            unstaged = run_git(
                repo,
                "diff",
                "--no-ext-diff",
            )

            staged = run_git(
                repo,
                "diff",
                "--cached",
                "--no-ext-diff",
            )

            status = run_git(
                repo,
                "status",
                "--short",
            )

            untracked = collect_untracked(repo)

        except Exception as exc:
            return fail(
                "Could not read git state",
                detail=str(exc),
            )

        gate_output = (
            "(no deterministic gate output supplied)"
        )

        if args.gate_file:
            gate_path = Path(args.gate_file)

            if not gate_path.is_absolute():
                gate_path = repo / gate_path

            if gate_path.is_file():
                gate_output = gate_path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )

        authoritative_candidates = [
            repo / "AGENTS.md",
            repo / "spec" / "STRATEGY_SPEC.md",
            repo / "spec" / "RULES.md",
            repo / "STRATEGY_SPEC.md",
            repo / "RULES.md",
        ]

        authoritative = []

        for path in authoritative_candidates:
            text = read_if_exists(path)

            if text is not None:
                authoritative.append(
                    f"\n===== {path.relative_to(repo)} =====\n{text}"
                )

        authoritative_text = (
            "\n".join(authoritative)
            if authoritative
            else "(no authoritative project specification files found)"
        )

        prompt = f"""
Review the implementation below.

Evaluate ONLY against:

1. the explicit user task,
2. authoritative project specifications supplied below,
3. actual Git changes/new files,
4. deterministic gate output.

EVIDENCE DISCIPLINE

A BLOCKER or HIGH finding requires concrete evidence that the implementation:

- violates an explicit task requirement,
- violates an explicit authoritative specification,
- contradicts deterministic test/gate evidence,
- contains a demonstrable correctness defect,
- or contains a demonstrable security/safety defect.

Do NOT promote hypothetical robustness concerns into BLOCKER/HIGH merely
because another contract could have been chosen.

Do NOT infer requirements from:

- hypothetical future callers,
- unspecified validation,
- stylistic preferences,
- alternative architectures,
- theoretical edge cases not required by task/spec.

Such observations may be MEDIUM or LOW only when genuinely useful.

For trading-related code, aggressively look for EVIDENCE-BASED:

- invented or altered trading semantics,
- lookahead bias,
- repainting,
- candle-close timing errors,
- impossible historical fills,
- stop-loss / take-profit ordering ambiguity,
- fee or slippage mistakes,
- state divergence between backtest, paper, shadow, and live,
- incorrect indicator calculations,
- race conditions,
- unsafe execution or recovery behavior.

TRADING SEMANTICS RULE

If correctness requires choosing between multiple plausible trading
interpretations and the authoritative material does not resolve it:

verdict MUST be USER_REQUIRED.

Never choose the trading interpretation yourself.

SEVERITY

BLOCKER:
Unsafe to continue or fundamentally wrong.

HIGH:
Demonstrable correctness bug or material explicit requirement violation.

MEDIUM:
Real non-blocking concern supported by evidence.

LOW:
Minor optional improvement.

VERDICT

PASS:
Zero BLOCKER and zero HIGH findings.

FAIL:
At least one evidence-backed BLOCKER/HIGH finding that Codex can fix
using existing evidence.

USER_REQUIRED:
A material issue cannot be resolved without a human/expert decision.

Return ONLY valid JSON:

{{
  "verdict": "PASS|FAIL|USER_REQUIRED",
  "summary": "short summary",
  "findings": [
    {{
      "id": "C001",
      "severity": "BLOCKER|HIGH|MEDIUM|LOW",
      "title": "short title",
      "evidence": "specific evidence",
      "required_action": "specific corrective action or human question"
    }}
  ]
}}

No markdown fences.
No prose outside JSON.

===== USER TASK =====
{task}

===== AUTHORITATIVE PROJECT MATERIAL =====
{authoritative_text}

===== GIT STATUS =====
{status}

===== UNSTAGED DIFF =====
{unstaged if unstaged.strip() else "(none)"}

===== STAGED DIFF =====
{staged if staged.strip() else "(none)"}

===== UNTRACKED FILES =====
{untracked}

===== DETERMINISTIC GATES =====
{gate_output}
""".strip()

    cmd = [
        claude,
        "-p",
        "--model", args.model,
        "--output-format", "json",
        "--max-turns", "1",
        "--permission-mode", "plan",
        "--tools", "",
        "--system-prompt", CRITIC_SYSTEM_PROMPT,
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo),
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )

    except subprocess.TimeoutExpired:
        return fail(
            "Claude timed out",
            3,
        )

    if proc.returncode != 0:
        return fail(
            "Claude process failed",
            proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
        )

    raw_stdout = proc.stdout.lstrip()
    decoder = json.JSONDecoder()

    try:
        outer, json_end = decoder.raw_decode(
            raw_stdout
        )

    except json.JSONDecodeError:
        return fail(
            "Claude CLI returned invalid outer JSON",
            4,
            stdout=proc.stdout.strip(),
        )

    result = outer.get(
        "result",
        "",
    ).strip()

    actual_model = detect_actual_model(
        outer,
        args.model,
    )

    if args.self_test:
        output = {
            "ok": result == "CLAUDE_CRITIC_OK",
            "critic": "claude",
            "requested_model": args.model,
            "model": actual_model,
            "result": result,
        }

        print(
            json.dumps(
                output,
                ensure_ascii=False,
                indent=2,
            )
        )

        return (
            0
            if output["ok"]
            else 5
        )

    try:
        critique = json.loads(result)

    except json.JSONDecodeError:
        return fail(
            "Critic did not return valid critique JSON",
            5,
            result=result,
        )

    verdict = critique.get("verdict")

    if verdict not in {
        "PASS",
        "FAIL",
        "USER_REQUIRED",
    }:
        return fail(
            "Critic returned invalid verdict",
            6,
            critique=critique,
        )

    default_dir = repo / ".pingpong"
    default_dir.mkdir(
        exist_ok=True,
    )

    if args.out:
        out_file = Path(args.out)

        if not out_file.is_absolute():
            out_file = repo / out_file

        out_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    else:
        out_file = (
            default_dir
            / "last_critique.json"
        )

    output = {
        "ok": True,
        "critic": "claude",
        "requested_model": args.model,
        "model": actual_model,
        "verdict": verdict,
        "findings": len(
            critique.get("findings", [])
        ),
        "critique": critique,
    }

    out_file.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    output["saved_to"] = str(out_file)

    print(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())