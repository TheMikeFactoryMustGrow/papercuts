#!/usr/bin/env python3
"""Rich-context papercut logging: required fields, escape, grandfathering, dedupe.

The new fields improve future feedback. They gate *new* logs only.
`papercut check` is informational (exit 0) and is not a gate on resolve or sanding.

Required: goal, attempted, happened, workaround, ideal_outcome.
Optional: suggested_fix. Legacy proposed_fix entries stay valid as history.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERCUT = ROOT / "scripts" / "papercut"

REQUIRED = ("goal", "attempted", "happened", "workaround", "ideal_outcome")
FLAGS = {
    "goal": "--goal",
    "attempted": "--attempted",
    "happened": "--happened",
    "workaround": "--workaround",
    "ideal_outcome": "--ideal-outcome",
    "suggested_fix": "--suggested-fix",
}

FULL = {
    "goal": "Install the CLI so the next agent can log friction.",
    "attempted": "papercut install --grok",
    "happened": "command not found: papercut because ~/.local/bin was not on PATH.",
    "workaround": "called scripts/papercut directly",
    "ideal_outcome": "install exits 0 and `papercut status` works from a new shell, so the next agent can log without a hardcoded script path.",
}

LEGACY = (
    "\n"
    "2026-08-06T03:27:18.616Z - m1 - a1\n"
    "\n"
    "First: the SIGPIPE guard bug.\n"
    "\n"
)

LEGACY_PROPOSED_FIX = (
    "\n"
    "2026-11-18T13:20:00.000Z - test-model - test-bot\n"
    "\n"
    "goal: Install the CLI so the next agent can log friction.\n"
    "attempted: papercut install --grok\n"
    "happened: command not found: papercut because ~/.local/bin was not on PATH.\n"
    "workaround: called scripts/papercut directly\n"
    "proposed_fix: Have install print a PATH check and fail if the shim is not reachable.\n"
    "\n"
)


def run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PAPERCUT), "-C", str(repo), *args],
        cwd=repo,
        text=True,
        capture_output=True,
        env=os.environ.copy(),
    )


def log_args(fields: dict[str, str | None], model: str = "test-model", author: str = "test-bot") -> list[str]:
    args = ["log", "-m", model, "-a", author]
    for key, flag in FLAGS.items():
        val = fields.get(key)
        if val is None:
            continue
        args.extend([flag, val])
    return args


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        r = run(self.repo, "enable")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def open_text(self) -> str:
        return (self.repo / ".agent-papercuts" / "open.md").read_text(encoding="utf-8")

    def history_text(self) -> str:
        p = self.repo / ".agent-papercuts" / "history.jsonl"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def logged_events(self) -> list[str]:
        return [ln for ln in self.history_text().splitlines() if '"event": "logged"' in ln or '"event":"logged"' in ln]

    def test_missing_field_is_rejected_and_named(self) -> None:
        for key in REQUIRED:
            with self.subTest(missing=key):
                fields = dict(FULL)
                fields[key] = None
                before = self.open_text()
                hist_before = self.history_text()
                r = run(self.repo, *log_args(fields))
                self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
                err = (r.stderr + r.stdout).lower()
                self.assertIn("missing", err)
                self.assertIn(key, err)
                self.assertEqual(self.open_text(), before)
                self.assertEqual(self.history_text(), hist_before)

    def test_blank_field_is_rejected_and_named(self) -> None:
        fields = dict(FULL)
        fields["happened"] = "   "
        before = self.open_text()
        r = run(self.repo, *log_args(fields))
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("happened", (r.stderr + r.stdout).lower())
        self.assertEqual(self.open_text(), before)

    def test_bare_message_without_fields_is_rejected(self) -> None:
        before = self.open_text()
        r = run(self.repo, "log", "-m", "ci", "Smoke: enable path works.")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        err = (r.stderr + r.stdout).lower()
        self.assertIn("missing", err)
        for key in REQUIRED:
            self.assertIn(key, err)
        self.assertNotIn("proposed_fix", err)
        self.assertNotIn("suggested_fix", err)
        self.assertEqual(self.open_text(), before)

    def test_complete_log_is_accepted_without_suggested_fix(self) -> None:
        r = run(self.repo, *log_args(dict(FULL)))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        text = self.open_text()
        self.assertIn("goal:", text)
        self.assertIn(FULL["goal"], text)
        self.assertIn("attempted:", text)
        self.assertIn("happened:", text)
        self.assertIn("workaround:", text)
        self.assertIn("ideal_outcome:", text)
        self.assertIn(FULL["ideal_outcome"], text)
        self.assertNotIn("proposed_fix:", text)
        self.assertNotIn("suggested_fix:", text)
        self.assertEqual(len(self.logged_events()), 1)
        lst = run(self.repo, "list")
        self.assertEqual(lst.returncode, 0, lst.stderr)
        self.assertIn("(1 total", lst.stdout)

    def test_optional_suggested_fix_is_recorded_when_present(self) -> None:
        fields = dict(FULL)
        fields["suggested_fix"] = "Have install print a PATH check and fail if the shim is not reachable."
        r = run(self.repo, *log_args(fields))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        text = self.open_text()
        self.assertIn("ideal_outcome:", text)
        self.assertIn("suggested_fix: Have install print a PATH check and fail if the shim is not reachable.", text)

    def test_omitting_suggested_fix_is_not_a_missing_field(self) -> None:
        r = run(self.repo, *log_args(dict(FULL)))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        err = (r.stderr + r.stdout).lower()
        self.assertNotIn("missing", err)
        self.assertNotIn("suggested_fix", err)

    def test_workaround_none_is_accepted(self) -> None:
        fields = dict(FULL)
        fields["workaround"] = "none"
        r = run(self.repo, *log_args(fields))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("workaround: none", self.open_text())

    def test_unknown_escape_is_accepted(self) -> None:
        fields = dict(FULL)
        fields["attempted"] = "unknown — tool inputs were not retained after the crash"
        r = run(self.repo, *log_args(fields))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("unknown — tool inputs were not retained after the crash", self.open_text())

    def test_unknown_without_reason_is_rejected(self) -> None:
        for raw in ("unknown", "unknown —", "unknown --"):
            with self.subTest(raw=raw):
                fields = dict(FULL)
                fields["goal"] = raw
                before = self.open_text()
                r = run(self.repo, *log_args(fields))
                self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
                err = (r.stderr + r.stdout).lower()
                self.assertIn("goal", err)
                self.assertEqual(self.open_text(), before)

    def test_labeled_body_is_accepted(self) -> None:
        body = "\n".join(
            [
                f"goal: {FULL['goal']}",
                f"attempted: {FULL['attempted']}",
                f"happened: {FULL['happened']}",
                f"workaround: {FULL['workaround']}",
                f"ideal_outcome: {FULL['ideal_outcome']}",
            ]
        )
        r = run(self.repo, "log", "-m", "test-model", "-a", "test-bot", body)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("goal:", self.open_text())
        self.assertIn("ideal_outcome:", self.open_text())
        self.assertIn(FULL["ideal_outcome"], self.open_text())

    def test_dedupe_retry_does_not_duplicate(self) -> None:
        first = run(self.repo, *log_args(dict(FULL)))
        self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
        second = run(self.repo, *log_args(dict(FULL)))
        self.assertEqual(second.returncode, 0, second.stderr + second.stdout)
        combined = (second.stdout + second.stderr).lower()
        self.assertTrue(
            "already" in combined or "duplicate" in combined or "idempotent" in combined,
            second.stdout + second.stderr,
        )
        self.assertEqual(len(self.logged_events()), 1)
        lst = run(self.repo, "list")
        self.assertIn("(1 total", lst.stdout)

    def test_different_goal_is_not_a_duplicate(self) -> None:
        self.assertEqual(run(self.repo, *log_args(dict(FULL))).returncode, 0)
        fields = dict(FULL)
        fields["goal"] = "A different intent: document the PATH gotcha in the README."
        r = run(self.repo, *log_args(fields))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        lst = run(self.repo, "list")
        self.assertIn("(2 total", lst.stdout)
        self.assertEqual(len(self.logged_events()), 2)

    def test_check_reports_thin_items_and_exits_zero(self) -> None:
        open_path = self.repo / ".agent-papercuts" / "open.md"
        open_path.write_text(self.open_text() + LEGACY, encoding="utf-8")
        before = open_path.read_text(encoding="utf-8")
        r = run(self.repo, "check")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        out = r.stdout + r.stderr
        self.assertIn("2026-08-06T03:27:18.616Z", out)
        lower = out.lower()
        self.assertTrue("thin" in lower or "missing" in lower, out)
        for key in REQUIRED:
            self.assertIn(key, lower)
        self.assertEqual(open_path.read_text(encoding="utf-8"), before, "check must not rewrite history")

    def test_check_exits_zero_when_all_complete(self) -> None:
        self.assertEqual(run(self.repo, *log_args(dict(FULL))).returncode, 0)
        r = run(self.repo, "check")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertRegex((r.stdout + r.stderr).lower(), r"0 thin|no thin|all complete")

    def test_grandfathered_entry_lists_and_resolves(self) -> None:
        open_path = self.repo / ".agent-papercuts" / "open.md"
        open_path.write_text(self.open_text() + LEGACY, encoding="utf-8")
        lst = run(self.repo, "list")
        self.assertEqual(lst.returncode, 0, lst.stderr)
        self.assertIn("SIGPIPE", lst.stdout)
        self.assertIn("(1 total", lst.stdout)
        resolved = run(
            self.repo,
            "resolve",
            "--stamp",
            "2026-08-06T03:27:18.616Z",
            "-n",
            "Guard SIGPIPE; grandfathered thin entries still clear.",
        )
        self.assertEqual(resolved.returncode, 0, resolved.stderr + resolved.stdout)
        lst2 = run(self.repo, "list")
        self.assertIn("empty log", lst2.stdout)
        self.assertNotIn("SIGPIPE", self.open_text())

    def test_legacy_proposed_fix_stays_valid_as_history(self) -> None:
        open_path = self.repo / ".agent-papercuts" / "open.md"
        open_path.write_text(self.open_text() + LEGACY_PROPOSED_FIX, encoding="utf-8")
        before = open_path.read_text(encoding="utf-8")
        self.assertIn("proposed_fix:", before)
        lst = run(self.repo, "list")
        self.assertEqual(lst.returncode, 0, lst.stderr)
        self.assertIn("proposed_fix", lst.stdout)
        self.assertIn("(1 total", lst.stdout)
        checked = run(self.repo, "check")
        self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
        out = (checked.stdout + checked.stderr).lower()
        self.assertIn("ideal_outcome", out)
        self.assertTrue("thin" in out or "missing" in out, checked.stdout + checked.stderr)
        self.assertEqual(open_path.read_text(encoding="utf-8"), before, "check must not rewrite history")
        resolved = run(
            self.repo,
            "resolve",
            "--stamp",
            "2026-11-18T13:20:00.000Z",
            "-n",
            "Legacy proposed_fix entries still clear; the fixer works backwards from ideal_outcome going forward.",
        )
        self.assertEqual(resolved.returncode, 0, resolved.stderr + resolved.stdout)
        self.assertIn("empty log", run(self.repo, "list").stdout)
        self.assertIn("proposed_fix", self.history_text())


if __name__ == "__main__":
    unittest.main()
