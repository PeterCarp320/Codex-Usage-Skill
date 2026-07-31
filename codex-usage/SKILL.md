---
name: codex-usage
description: Show Codex usage information from local Codex state and read-only Codex/ChatGPT backend endpoints. Use when the user asks to check Codex usage, reset credits, rate-limit windows, local usage metadata, online usage/profile data, token totals, or export Codex usage reports.
---

# Codex Usage

## Quick snapshot

Resolve the skill root as the directory containing this `SKILL.md`, then run:

```bash
python3 "<skill-root>/scripts/snapshot_codex_usage.py"
```

Default to this compact snapshot unless the user asks for more detail.

## Detailed reports

Run the bundled `codex_usage.py` script from the resolved skill root:

```bash
python3 "<skill-root>/scripts/codex_usage.py" all --no-colour
```

- Use `local-usage --no-colour` for local-only data with no network calls.
- Use `resets --no-colour` for reset credits only.
- Use `online-usage --no-colour` for online usage and profile data.
- Add `--json` for machine-readable output.
- Use `export --report all --format txt` for an export, or choose `json` or `csv`.

## Behavior and privacy

- Read Codex state from `$CODEX_HOME` when set, otherwise from `~/.codex`.
- Treat `local-usage` as network-free. Do not print prompts, responses, project paths, absolute filesystem paths, or authentication data.
- Treat `resets`, `online-usage`, and `all` as online modes. They read the current local Codex login and make read-only `GET` requests only to `https://chatgpt.com/backend-api`.
- Never print, persist, or expose the access token or account identifier.
- Treat online data as operational information, not official billing data. The endpoints are undocumented and may change.
- If the local login is missing, expired, or malformed, explain that Codex needs a current local login and offer the local-only report.

## Response format

For the compact snapshot, list every returned reset-credit expiry from soonest to latest. When both rate-limit windows exist, label them `Session limit` and `Weekly limit`. When only the primary window exists, label it `Weekly limit` and omit `Session limit`.

Keep the snapshot compact. Show session reset time as hours and minutes. Show weekly reset time as days and hours when at least one full day remains, otherwise as hours and minutes. Omit the allowed-right-now line and detailed local token counters.

Retain the upstream MIT license notice in `references/Codex-Usage-LICENCE.txt`.
