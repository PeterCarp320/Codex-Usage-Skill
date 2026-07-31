# Codex Usage skill

A portable Codex skill for checking your current Codex usage in a compact snapshot.

It reports:

- Current rate-limit usage and reset time
- Available reset credits and their expiry times
- Lifetime online token count and current usage streak
- Dominant model from local Codex metadata
- Optional detailed local, online, TXT, JSON, and CSV reports

## Install

Copy and paste this exact prompt into Codex:

```text
Install the codex-usage skill from https://github.com/PeterCarp320/codex-usage-skill/tree/main/codex-usage
```

Codex installs the skill into its local skills directory. The skill is available on your next turn.

## Run

On your next turn, invoke the installed skill with:

```text
$codex-usage
```

Codex may display that text as a clickable skill chip. Custom skills are invoked with `$skill-name`; `/codex-usage` is not a supported custom-skill command.

## Requirements

- A current Codex Desktop or Codex CLI login
- Python 3.10 or newer
- No OpenAI API key
- No third-party Python packages

## Privacy and security

- Local-only reports make no network calls.
- Online reports use the existing local Codex login and make read-only `GET` requests only to `https://chatgpt.com/backend-api`.
- Access tokens, account identifiers, emails, prompts, responses, project paths, absolute filesystem paths, and session identifiers are not printed or stored.
- The online usage endpoints are undocumented and may change. Their output is operational information, not official billing data.
- Exported reports contain usage statistics and should be reviewed before sharing.

See `SECURITY.md` for the complete data flow and security notes.

## License and attribution

The bundled command-line implementation is derived from [MacSteini/Codex-Usage](https://github.com/MacSteini/Codex-Usage) at commit [`c40350a`](https://github.com/MacSteini/Codex-Usage/commit/c40350a75e85c451d4edfa58fa2d0958c1ef25e2). The upstream project is licensed under the MIT License.

The MIT License permits use, copying, modification, publication, and distribution provided that the original copyright and permission notice are retained. This repository preserves that notice in `LICENSE` and `codex-usage/references/Codex-Usage-LICENCE.txt`. Modifications in this repository are released under the same MIT License.
