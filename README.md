# Codex Usage skill

This repository contains a portable Codex skill that reports:

- Current Codex rate-limit usage and reset times
- Available reset credits and their expiry times
- Online usage/profile statistics
- Local usage metadata without network calls
- Optional TXT, JSON, and CSV exports

## Install with Codex

Copy the URL of the `codex-usage` folder in this repository, then ask Codex:

```text
Install the codex-usage skill from <GitHub folder URL>.
```

For a repository on the `main` branch, the folder URL has this form:

```text
https://github.com/OWNER/REPOSITORY/tree/main/codex-usage
```

On the next turn, run:

```text
/codex-usage
```

The skill requires a current Codex Desktop or CLI login and Python 3.10 or newer. It does not require an OpenAI API key or third-party Python packages.

## Privacy and security

- Local-only reports make no network calls.
- Online reports read the existing local Codex login and make read-only `GET` requests only to `https://chatgpt.com/backend-api`.
- Access tokens, account identifiers, emails, prompts, responses, project paths, and absolute filesystem paths are not printed or stored.
- Online usage endpoints are undocumented and may change. Their output is operational information, not official billing data.
- Exported reports contain usage statistics. Review them before sharing.

See `SECURITY.md` for the complete data-flow and security notes.

## Short sharing prompt

After publishing, replace the URL below with the public folder URL:

```text
Install this Codex usage skill from <GitHub folder URL>, then run /codex-usage.
```

## Attribution

The bundled command-line implementation is derived from [MacSteini/Codex-Usage](https://github.com/MacSteini/Codex-Usage) at commit `c40350a75e85c451d4edfa58fa2d0958c1ef25e2` and is distributed under the MIT License. See `LICENSE` and `codex-usage/references/Codex-Usage-LICENCE.txt`.
