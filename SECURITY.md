# Security and privacy

## What the skill reads

- Local usage mode reads metadata and token counters under `$CODEX_HOME`, or `~/.codex` when that variable is not set.
- Online modes read the existing Codex access token and account identifier from the local `auth.json` file.

## Network behavior

- Local usage mode makes no network requests.
- Online modes make authenticated `GET` requests only to relative paths under `https://chatgpt.com/backend-api`.
- The URL builder rejects absolute or third-party endpoint URLs so credentials cannot be redirected to another host.

## Output protections

- Authentication values and account identifiers are never printed or written to exports.
- Online responses are recursively redacted for sensitive keys and email addresses before display or export.
- Local reports omit project names, working directories, absolute filesystem paths, and session identifiers.
- Exported reports still contain usage statistics and should be reviewed before sharing.

## Reporting a vulnerability

Use the repository's private GitHub vulnerability-reporting feature when it is enabled. Do not include real access tokens, account identifiers, or private usage exports in a public issue.
