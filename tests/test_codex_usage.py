from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(
    os.environ.get(
        "CODEX_USAGE_MODULE",
        Path(__file__).resolve().parents[1]
        / "codex-usage"
        / "scripts"
        / "codex_usage.py",
    )
)
SPEC = importlib.util.spec_from_file_location("codex_usage", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
codex_usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(codex_usage)


class CodexUsageTests(unittest.TestCase):
    def test_profile_allowlist_omits_identity_fields(self) -> None:
        data = {
            "user_id": "private-user-id",
            "profile": {"display_name": "Private Name"},
            "stats": {
                "lifetime_tokens": 123,
                "current_streak_days": 7,
                "unexpected_private_field": "private",
            },
        }
        self.assertEqual(
            codex_usage.allowlisted_online_data("profile", data),
            {
                "stats": {
                    "lifetime_tokens": 123,
                    "current_streak_days": 7,
                }
            },
        )

    def test_profile_allowlist_preserves_usage_statistics(self) -> None:
        data = {
            "stats": {
                "lifetime_tokens": 123,
                "peak_daily_tokens": 45,
                "current_streak_days": 7,
                "longest_streak_days": 11,
                "total_threads": 9,
                "fast_mode_usage_percentage": 12.5,
                "most_used_reasoning_effort": "high",
                "most_used_reasoning_effort_percentage": 72.0,
                "daily_usage_buckets": [
                    {
                        "start_date": "2026-07-31",
                        "tokens": 10,
                        "private_note": "omit",
                    }
                ],
            }
        }
        self.assertEqual(
            codex_usage.allowlisted_online_data("profile", data),
            {
                "stats": {
                    "lifetime_tokens": 123,
                    "peak_daily_tokens": 45,
                    "current_streak_days": 7,
                    "longest_streak_days": 11,
                    "total_threads": 9,
                    "fast_mode_usage_percentage": 12.5,
                    "most_used_reasoning_effort": "high",
                    "most_used_reasoning_effort_percentage": 72.0,
                    "daily_usage_buckets": [
                        {"start_date": "2026-07-31", "tokens": 10}
                    ],
                }
            },
        )

    def test_rate_limit_allowlist_preserves_usage_and_omits_identity(self) -> None:
        window = {
            "used_percent": 25,
            "reset_after_seconds": 3600,
            "reset_at": 1_800_000_000,
            "private": "omit",
        }
        data = {
            "user_id": "private-user-id",
            "plan_type": "pro",
            "rate_limit_reached_type": "none",
            "rate_limit": {
                "allowed": True,
                "limit_reached": False,
                "primary_window": window,
                "secondary_window": window,
            },
            "credits": {
                "balance": 10,
                "has_credits": True,
                "unlimited": False,
                "overage_limit_reached": False,
                "private": "omit",
            },
            "additional_rate_limits": [
                {
                    "limit_name": "fast",
                    "metered_feature": "fast-mode",
                    "rate_limit": {
                        "limit_reached": False,
                        "primary_window": window,
                    },
                    "private": "omit",
                }
            ],
        }
        result = codex_usage.allowlisted_online_data("rate_limit_status", data)
        self.assertNotIn("user_id", result)
        self.assertEqual(result["plan_type"], "pro")
        self.assertEqual(result["rate_limit"]["primary_window"]["used_percent"], 25)
        self.assertNotIn("private", result["credits"])
        self.assertNotIn("private", result["additional_rate_limits"][0])

    def test_daily_usage_allowlist_preserves_usage_only(self) -> None:
        data = {
            "units": "credits",
            "group_by": "date",
            "display_name": "Private Name",
            "data": [
                {
                    "date": "2026-07-31",
                    "product_surface_usage_values": {
                        "codex": 5,
                        "private": "omit",
                    },
                    "models": [
                        {
                            "model": "gpt-example",
                            "speed": "fast",
                            "credits": 5,
                            "private": "omit",
                        }
                    ],
                    "private": "omit",
                }
            ],
        }
        self.assertEqual(
            codex_usage.allowlisted_online_data(
                "daily_token_usage_breakdown", data
            ),
            {
                "units": "credits",
                "group_by": "date",
                "data": [
                    {
                        "date": "2026-07-31",
                        "product_surface_usage_values": {"codex": 5},
                        "models": [
                            {
                                "model": "gpt-example",
                                "speed": "fast",
                                "credits": 5,
                            }
                        ],
                    }
                ],
            },
        )

    def test_daily_usage_allowlist_preserves_summary_totals(self) -> None:
        result = codex_usage.allowlisted_online_data(
            "daily_token_usage_breakdown",
            {
                "data": [
                    {
                        "date": "2026-07-31",
                        "credits": 1,
                        "total": 2,
                        "total_credits": 3,
                    }
                ]
            },
        )
        self.assertEqual(
            result,
            {
                "data": [
                    {
                        "date": "2026-07-31",
                        "credits": 1,
                        "total": 2,
                        "total_credits": 3,
                    }
                ]
            },
        )

    def test_credit_event_allowlist_omits_free_text_and_identity(self) -> None:
        data = {
            "user_id": "private-user-id",
            "data": [
                {
                    "created_at": "2026-07-31T12:00:00Z",
                    "type": "usage",
                    "credits": 2,
                    "reason": "Private free text reason",
                    "description": "Private free text",
                    "display_name": "Private Name",
                }
            ],
        }
        self.assertEqual(
            codex_usage.allowlisted_online_data("credit_usage_events", data),
            {
                "data": [
                    {
                        "created_at": "2026-07-31T12:00:00Z",
                        "type": "usage",
                        "credits": 2,
                    }
                ]
            },
        )

    def test_online_collection_applies_endpoint_allowlists(self) -> None:
        responses = {
            "/wham/usage": {
                "user_id": "private-user-id",
                "plan_type": "pro",
            },
            "/wham/usage/daily-token-usage-breakdown": {"data": []},
            "/wham/usage/credit-usage-events": {"data": []},
            "/wham/profiles/me": {
                "profile": {"display_name": "Private Name"},
                "stats": {"lifetime_tokens": 123},
            },
        }

        def fake_fetch(
            path: str, access_token: str, account_id: str
        ) -> dict[str, object]:
            return {"ok": True, "status": 200, "data": responses[path]}

        with mock.patch.object(
            codex_usage, "load_auth", return_value=("fake-token", "fake-account")
        ), mock.patch.object(codex_usage, "fetch_json", side_effect=fake_fetch):
            result = codex_usage.collect_online_usage()

        self.assertEqual(
            result["endpoints"]["profile"]["data"],
            {"stats": {"lifetime_tokens": 123}},
        )
        self.assertEqual(
            result["endpoints"]["rate_limit_status"]["data"],
            {"plan_type": "pro"},
        )

    def test_secure_export_open_uses_owner_only_permissions(self) -> None:
        fake_handle = object()
        with (
            mock.patch.object(codex_usage.os, "open", return_value=123) as raw_open,
            mock.patch.object(
                codex_usage.os, "fdopen", return_value=fake_handle
            ) as fd_open,
        ):
            result = codex_usage.open_secure_text(Path("report.json"))

        self.assertIs(result, fake_handle)
        flags = raw_open.call_args.args[1]
        mode = raw_open.call_args.args[2]
        self.assertEqual(mode, 0o600)
        self.assertTrue(flags & os.O_EXCL)
        fd_open.assert_called_once_with(
            123,
            "w",
            encoding="utf-8",
            newline=None,
        )

    def test_cross_origin_redirects_are_rejected(self) -> None:
        request = urllib.request.Request(
            "https://chatgpt.com/backend-api/wham/usage",
            headers={
                "Authorization": "Bearer fake",
                "ChatGPT-Account-ID": "fake-account",
            },
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            codex_usage.SameOriginRedirectHandler().redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://example.invalid/capture",
            )
        raised.exception.close()

    def test_build_url_accepts_only_backend_relative_paths(self) -> None:
        self.assertEqual(
            codex_usage.build_url("/wham/usage"),
            "https://chatgpt.com/backend-api/wham/usage",
        )
        with self.assertRaises(ValueError):
            codex_usage.build_url("https://example.com/steal-token")

    def test_redact_removes_sensitive_values_and_emails(self) -> None:
        value = {
            "access_token": "secret",
            "profile": {"email": "person@example.com", "usage": 10},
        }
        self.assertEqual(
            codex_usage.redact(value),
            {
                "access_token": "[REDACTED]",
                "profile": {"email": "[REDACTED]", "usage": 10},
            },
        )

    def test_local_path_labels_do_not_include_the_home_directory(self) -> None:
        codex_home = Path(os.path.expanduser("~/.codex"))
        label = codex_usage.local_path_label(codex_home / "state_5.sqlite", codex_home)
        self.assertEqual(label, "~/.codex/state_5.sqlite")
        self.assertNotIn(str(Path.home()), label)

    def test_auth_and_export_labels_do_not_include_absolute_paths(self) -> None:
        codex_home = Path(os.path.expanduser("~/.codex"))
        self.assertEqual(
            codex_usage.auth_path_label(codex_home),
            "~/.codex/auth.json",
        )
        self.assertEqual(
            codex_usage.export_path_label(
                Path("/private/example/codex_all_report_2026.json")
            ),
            "codex_all_report_2026.json",
        )

    def test_missing_auth_error_uses_a_portable_path(self) -> None:
        missing_home = "/private/codex-usage-test-missing-home"
        environment = os.environ.copy()
        environment["CODEX_HOME"] = missing_home
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH), "resets", "--no-colour"],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(missing_home, result.stderr)
        self.assertIn("$CODEX_HOME/auth.json", result.stderr)


if __name__ == "__main__":
    unittest.main()
