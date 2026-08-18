# Security

PingPong is a local orchestration skill, but normal reviews intentionally send project context through the Claude Code CLI you have configured.

## Sensitive data

Before using PingPong on a repository, understand the review payload described in [docs/DESIGN.md](docs/DESIGN.md). It can include task text, selected project specifications, Git diffs, untracked text files, and deterministic gate output.

Do not place secrets in test fixtures or examples. Do not commit API keys, tokens, wallet keys, private keys, credentials, customer data, or private source material to this public repository.

## Reporting a vulnerability

Please do not publish exploitable details or real credentials in a public issue.

For a security concern that can be described safely, open a GitHub issue with the minimum reproduction needed and omit sensitive data. If private details are required, contact the maintainer through the GitHub profile associated with this repository to arrange a private disclosure path.

## Scope

Useful security reports include issues such as:

- unintended project file mutation by the critic path;
- unsafe command construction or argument handling;
- accidental secret disclosure beyond the documented review payload;
- installation/path behavior that can execute an unintended reviewer script;
- bypasses of the explicit model-selection or read-only critic constraints.
