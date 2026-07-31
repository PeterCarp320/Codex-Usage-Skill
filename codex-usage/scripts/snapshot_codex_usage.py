#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parents[1]
RUNNER = SKILL_DIR / "scripts" / "codex_usage.py"


def fmt_int(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return str(value).lower() if isinstance(value, bool) else "-"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def fmt_percent(value: Any) -> str:
    if value is None:
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return f"{int(number)}%"
    return f"{number:.1f}%"


def seconds_from(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return None


def fmt_hours_minutes(value: Any) -> str:
    seconds = seconds_from(value)
    if seconds is None:
        return str(value)
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    return f"{hours} hrs, {minutes} mins"


def fmt_weekly_reset(value: Any) -> str:
    seconds = seconds_from(value)
    if seconds is None:
        return str(value)
    if seconds < 86400:
        return fmt_hours_minutes(seconds)
    days, remainder = divmod(seconds, 86400)
    hours = remainder // 3600
    return f"{days} days, {hours} hrs"


def main() -> int:
    try:
        result = subprocess.run(
            [sys.executable, str(RUNNER), "all", "--json"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(exc.stderr or exc.stdout or str(exc))
        return exc.returncode
    except subprocess.TimeoutExpired:
        sys.stderr.write("Timed out while collecting Codex usage.\n")
        return 1

    data = json.loads(result.stdout)
    reset = data.get("reset_credits", {})
    local = data.get("local_usage", {})
    online = data.get("online_usage", {})
    endpoints = online.get("endpoints", {})

    rate_data = endpoints.get("rate_limit_status", {}).get("data", {})
    profile_stats = endpoints.get("profile", {}).get("data", {}).get("stats", {})
    rate_limit = rate_data.get("rate_limit", {})
    primary = rate_limit.get("primary_window", {})
    weekly = rate_limit.get("secondary_window")

    credits = sorted(
        reset.get("credits") or [],
        key=lambda credit: credit.get("expires_at") or credit.get("expires_at_local") or "",
    )

    sessions = local.get("sessions", {})
    model_totals = sessions.get("model_token_totals", {})
    dominant_model = "-"
    if model_totals:
        dominant_model = max(
            model_totals.items(),
            key=lambda item: (item[1] or {}).get("total_tokens", 0),
        )[0]

    print(f"Latest snapshot, retrieved {data.get('retrieved_at_local', '-')}:")
    print()
    print(f"- Plan: `{rate_data.get('plan_type', '-')}`")
    if weekly is None:
        print(
            f"- Weekly limit: {fmt_percent(primary.get('used_percent'))} used, "
            f"resets in {fmt_weekly_reset(primary.get('reset_after_seconds'))}"
        )
    else:
        print(
            f"- Session limit: {fmt_percent(primary.get('used_percent'))} used, "
            f"resets in {fmt_hours_minutes(primary.get('reset_after_seconds'))}"
        )
        print(
            f"- Weekly limit: {fmt_percent(weekly.get('used_percent'))} used, "
            f"resets in {fmt_weekly_reset(weekly.get('reset_after_seconds'))}"
        )
    print(f"- Reset credits: {fmt_int(reset.get('available_count'))} available")
    if credits:
        print("- Reset credit expiries:")
        for index, credit in enumerate(credits, start=1):
            status = credit.get("status", "-")
            expires_at = credit.get("expires_at_local", "-")
            remaining = credit.get("time_remaining", "-")
            print(f"  {index}. {expires_at} ({remaining}, {status})")
    else:
        print("- Reset credit expiries: none returned")
    print(f"- Lifetime tokens online: {fmt_int(profile_stats.get('lifetime_tokens'))}")
    print(f"- Current streak: {fmt_int(profile_stats.get('current_streak_days'))} days")
    print(f"- Dominant local model: `{dominant_model}`")
    print()
    print(
        f"Online calls: {fmt_int(online.get('network_calls_made'))} read-only GET calls. "
        f"Local usage mode remains network-free."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
