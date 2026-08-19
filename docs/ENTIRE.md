# Entire checkpoints

Entire stores the work behind an agent-assisted commit as a checkpoint. It is
separate from ordinary GitHub activity: connecting a repository or pushing an
old commit does not reconstruct past agent sessions.

## What you need

- the Entire CLI installed;
- an Entire account login;
- a local clone of the repository;
- the Codex integration enabled in that clone;
- a Codex CLI session that makes a change and then commits it.

Frankfurt (or another Entire region) controls where checkpoint data is stored.
It does not enable checkpoint capture by itself.

## Windows setup

Install the stable CLI with Scoop:

```powershell
scoop bucket add entire https://github.com/entireio/scoop-bucket.git
scoop install entire/cli
entire version
```

Log in once:

```powershell
entire login
```

From the repository root, enable the Codex hooks:

```powershell
entire enable -y --agent codex
```

This creates `.entire/settings.json` and `.codex/hooks.json`, and installs the
Git hooks that connect agent sessions to commits.

## Create the first checkpoint

Start Codex CLI from the same repository, make a small change, and commit it:

```powershell
codex

# after the agent session ends
git add .
git commit -m "Describe the change"
git push
```

The first checkpoint appears only when the commit follows a captured Codex
CLI session. A manual commit without an active agent session is still a valid
Git commit, but it does not create an Entire checkpoint.

Verify locally:

```powershell
entire status
entire checkpoint list
```

Checkpoints are stored as Git refs under `entire/checkpoints/v1`; they do not
add files or extra commits to the working branch.

## If Home step 03 stays red

- Check that the correct repository is selected.
- Run `entire status`.
- Run `entire checkpoint list`.
- If the hooks are missing or stale, run `entire enable -y --agent codex` again from the repository root.
- An ordinary Git commit does not create a checkpoint.
- The commit must follow a real Codex CLI session that was captured by Entire.

## Common confusion

### “The repository has commits, but Entire shows no activity”

GitHub commits alone are not enough. Entire needs its CLI hooks and a captured
agent session. Enable the repository locally, then create a new agent-assisted
commit.

### “I use Codex in the web app”

The documented integration in this repository is for Codex CLI. A browser chat
session does not automatically trigger the local Git hooks. Use `codex` from
the repository root when you need an Entire checkpoint.

### “Do I need to rewrite old commits?”

No. Do not rewrite history just to populate Entire. Enable the hooks and start
capturing from the next agent-assisted commit.

## Privacy

Checkpoint data can include prompts, transcripts, tool calls, token usage, and
file changes. Treat a public checkpoint branch as public repository data and
review the repository's [security guidance](../SECURITY.md) before enabling it
for sensitive work.
