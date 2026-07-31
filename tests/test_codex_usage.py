from __future__ import annotations

import importlib.util
import os
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "codex-usage"
    / "scripts"
    / "codex_usage.py"
)
SPEC = importlib.util.spec_from_file_location("codex_usage", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
codex_usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(codex_usage)


class CodexUsageTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
