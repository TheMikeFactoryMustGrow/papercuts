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

    # --- Oracle review of e99c709: --contains, one-line bodies, idempotency, usage ---

    def log_two_unrelated(self) -> None:
        a = dict(
            goal="Install the CLI so the next agent can log friction.",
            attempted="papercut install --grok",
            happened="command not found: papercut because ~/.local/bin was not on PATH.",
            workaround="called scripts/papercut directly",
            ideal_outcome="install exits 0 and `papercut status` runs from a new shell, so the next agent can log without a hardcoded script path.",
        )
        b = dict(FULL)
        b.update(
            goal="Render the weekly report as a PDF.",
            attempted="pandoc report.md -o report.pdf",
            happened="pandoc: xelatex not found.",
            workaround="used the HTML export",
            ideal_outcome="pandoc produces report.pdf without extra installs, so the report can be attached.",
        )
        self.assertEqual(run(self.repo, *log_args(a)).returncode, 0)
        self.assertEqual(run(self.repo, *log_args(b)).returncode, 0)

    def test_resolve_contains_ignores_field_labels(self) -> None:
        self.log_two_unrelated()
        for needle in ("work", "workaround", "goal", "happened", "ideal", "attempted", "ideal_outcome"):
            with self.subTest(needle=needle):
                before = self.open_text()
                r = run(self.repo, "resolve", "--contains", needle, "-n", "test")
                self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("no open entries matching", r.stderr)
                self.assertEqual(self.open_text(), before)
        self.assertIn("(2 total", run(self.repo, "list").stdout)

    def test_resolve_contains_matches_field_values_and_is_selective(self) -> None:
        self.log_two_unrelated()
        r = run(self.repo, "resolve", "--contains", "xelatex", "-n", "documented the install")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("(1 total", run(self.repo, "list").stdout)
        self.assertNotIn("xelatex", self.open_text())
        self.assertIn("papercut install --grok", self.open_text())

    def test_resolve_contains_multi_match_needs_all(self) -> None:
        self.log_two_unrelated()
        before = self.open_text()
        r = run(self.repo, "resolve", "--contains", "can", "-n", "x")  # both values say "can"
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("--all", r.stderr)
        self.assertEqual(self.open_text(), before)
        ok = run(self.repo, "resolve", "--contains", "can", "--all", "-n", "x")
        self.assertEqual(ok.returncode, 0, ok.stderr + ok.stdout)
        self.assertIn("empty log", run(self.repo, "list").stdout)

    def test_needs_mike_contains_ignores_field_labels(self) -> None:
        self.log_two_unrelated()
        before = self.open_text()
        r = run(self.repo, "needs-mike", "--contains", "work", "-r", "policy call")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.open_text(), before)
        self.assertNotIn("needs-Mike", self.open_text())
        ok = run(self.repo, "needs-mike", "--contains", "xelatex", "-r", "policy call", "--date", "2026-11-18")
        self.assertEqual(ok.returncode, 0, ok.stderr + ok.stdout)
        self.assertEqual(self.open_text().count("> needs-Mike"), 1)

    def test_needs_mike_contains_multi_match_needs_all(self) -> None:
        self.log_two_unrelated()
        r = run(self.repo, "needs-mike", "--contains", "can", "-r", "x")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertNotIn("needs-Mike", self.open_text())
        ok = run(self.repo, "needs-mike", "--contains", "can", "--all", "-r", "x")
        self.assertEqual(ok.returncode, 0, ok.stderr + ok.stdout)
        self.assertEqual(self.open_text().count("> needs-Mike"), 2)

    def test_contains_does_not_match_needs_mike_marker(self) -> None:
        self.log_two_unrelated()
        self.assertEqual(run(self.repo, "needs-mike", "--stamp", self.first_stamp(), "-r", "policy call").returncode, 0)
        r = run(self.repo, "resolve", "--contains", "needs-mike", "-n", "x")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("(2 total", run(self.repo, "list").stdout)

    def first_stamp(self) -> str:
        import re

        return re.findall(r"^(\d{4}-\d{2}-\d{2}T\S+) - ", self.open_text(), re.MULTILINE)[0]

    def test_legacy_free_text_contains_still_matches(self) -> None:
        open_path = self.repo / ".agent-papercuts" / "open.md"
        open_path.write_text(self.open_text() + LEGACY, encoding="utf-8")
        r = run(self.repo, "resolve", "--contains", "sigpipe", "-n", "guard fixed")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("empty log", run(self.repo, "list").stdout)

    def stored_fields(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for ln in self.open_text().splitlines():
            for key in REQUIRED + ("suggested_fix",):
                if ln.startswith(key + ":"):
                    self.assertNotIn(key, out, f"{key} stored twice:\n{self.open_text()}")
                    out[key] = ln[len(key) + 1 :].strip()
        return out

    def assert_clean_fields(self) -> None:
        stored = self.stored_fields()
        self.assertEqual(stored["goal"], "G the goal")
        self.assertEqual(stored["attempted"], "A did a thing")
        self.assertEqual(stored["happened"], "H it broke")
        self.assertEqual(stored["workaround"], "W used another way")
        self.assertEqual(stored["ideal_outcome"], "I it just works")
        self.assertEqual(self.open_text().count("goal:"), 1)

    ONE_LINE = "goal: G the goal attempted: A did a thing happened: H it broke workaround: W used another way ideal_outcome: I it just works"

    def test_one_line_labeled_body_single_argument(self) -> None:
        r = run(self.repo, "log", "-m", "m", "-a", "a", self.ONE_LINE)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assert_clean_fields()
        self.assertIn("goal: G the goal", self.history_text())
        self.assertNotIn("goal: G the goal attempted", self.history_text())

    def test_one_line_labeled_body_multiple_arguments(self) -> None:
        r = run(self.repo, "log", "-m", "m", "-a", "a", *self.ONE_LINE.split(" "))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assert_clean_fields()

    def test_mixed_line_and_inline_labeled_body_is_refused_not_guessed(self) -> None:
        # Line-start labels are authoritative in a multi-line body; labels inside a
        # value are not split out, so attempted/workaround stay missing.
        body = "goal: G the goal attempted: A did a thing\nhappened: H it broke workaround: W used another way\nideal_outcome: I it just works"
        before, hist = self.open_text(), self.history_text()
        r = run(self.repo, "log", "-m", "m", "-a", "a", body)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        head = r.stderr.split("usage:")[0]
        self.assertIn("attempted", head)
        self.assertIn("workaround", head)
        self.assertEqual(self.open_text(), before)
        self.assertEqual(self.history_text(), hist)

    def assert_multiline_refused(self, lines: list[str], missing: str, fabricated: str) -> None:
        before, hist = self.open_text(), self.history_text()
        r = run(self.repo, "log", "-m", "m", "-a", "a", "\n".join(lines))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        head = r.stderr.split("usage:")[0]
        self.assertIn(missing, head)
        self.assertEqual(self.open_text(), before, "nothing may be written")
        self.assertEqual(self.history_text(), hist, "nothing may be written to history")
        self.assertNotIn(fabricated, self.open_text())

    def test_multiline_missing_ideal_outcome_is_not_fabricated_from_a_value(self) -> None:
        self.assert_multiline_refused(
            [
                "goal: G", "attempted: A",
                "happened: timeout after ideal_outcome: was never printed",
                "workaround: W",
            ],
            "ideal_outcome", "was never printed",
        )

    def test_multiline_missing_workaround_is_not_fabricated_from_a_value(self) -> None:
        self.assert_multiline_refused(
            [
                "goal: G", "attempted: A",
                "happened: it failed after workaround: none was found",
                "ideal_outcome: I",
            ],
            "workaround", "none was found",
        )

    def test_multiline_value_with_label_and_all_fields_is_unchanged(self) -> None:
        body = "\n".join(
            ["goal: G", "attempted: A", "happened: timeout after ideal_outcome: was never printed",
             "workaround: W", "ideal_outcome: I"]
        )
        r = run(self.repo, "log", "-m", "m", "-a", "a", body)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("happened: timeout after ideal_outcome: was never printed", self.open_text())
        self.assertEqual(self.stored_fields()["ideal_outcome"], "I")

    def test_one_line_and_newline_bodies_dedupe_to_one_entry(self) -> None:
        self.assertEqual(run(self.repo, "log", "-m", "m", "-a", "a", self.ONE_LINE).returncode, 0)
        newline = self.ONE_LINE.replace(" attempted:", "\nattempted:").replace(" happened:", "\nhappened:")
        newline = newline.replace(" workaround:", "\nworkaround:").replace(" ideal_outcome:", "\nideal_outcome:")
        r = run(self.repo, "log", "-m", "m", "-a", "a", newline)
        self.assertIn("already logged", r.stdout)
        self.assertIn("(1 total", run(self.repo, "list").stdout)

    def test_newline_body_value_mentioning_a_label_is_kept(self) -> None:
        body = "\n".join(
            [
                "goal: avoid the workaround: hand-editing open.md",
                "attempted: A", "happened: H", "workaround: W", "ideal_outcome: I",
            ]
        )
        self.assertEqual(run(self.repo, "log", "-m", "m", "-a", "a", body).returncode, 0)
        self.assertIn("goal: avoid the workaround: hand-editing open.md", self.open_text())
        self.assertEqual(self.stored_fields()["workaround"], "W")

    def test_one_line_body_missing_a_field_names_it(self) -> None:
        body = self.ONE_LINE.replace(" ideal_outcome: I it just works", "")
        before = self.open_text()
        r = run(self.repo, "log", "-m", "m", "-a", "a", body)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("ideal_outcome", r.stderr)
        self.assertNotIn("goal (", r.stderr.split("usage:")[0])
        self.assertEqual(self.open_text(), before)

    def test_retry_after_needs_mike_is_a_noop(self) -> None:
        self.assertEqual(run(self.repo, *log_args(dict(FULL))).returncode, 0)
        nm = run(self.repo, "needs-mike", "--stamp", self.first_stamp(), "-r", "policy call", "--date", "2026-11-18")
        self.assertEqual(nm.returncode, 0, nm.stderr + nm.stdout)
        parked = self.open_text()
        hist = self.history_text()
        self.assertIn("> needs-Mike (2026-11-18 sand): policy call", parked)
        retry = run(self.repo, *log_args(dict(FULL)))
        self.assertEqual(retry.returncode, 0, retry.stderr + retry.stdout)
        self.assertIn("already logged", retry.stdout)
        self.assertEqual(self.open_text(), parked)
        self.assertEqual(self.history_text(), hist)
        self.assertEqual(len(self.logged_events()), 1)

    def test_needs_mike_marker_never_enters_a_field_value(self) -> None:
        self.assertEqual(run(self.repo, *log_args(dict(FULL))).returncode, 0)
        run(self.repo, "needs-mike", "--stamp", self.first_stamp(), "-r", "policy call")
        out = run(self.repo, "check")
        self.assertEqual(out.returncode, 0)
        self.assertIn("0 thin", out.stdout)
        # the marker is also stripped from a retry-after-edit comparison
        again = run(self.repo, "needs-mike", "--stamp", self.first_stamp(), "-r", "updated", "--date", "2026-11-19")
        self.assertEqual(again.returncode, 0, again.stderr + again.stdout)
        self.assertEqual(self.open_text().count("> needs-Mike"), 1)
        self.assertIn("already logged", run(self.repo, *log_args(dict(FULL))).stdout)

    def test_dedupe_includes_suggested_fix(self) -> None:
        self.assertEqual(run(self.repo, *log_args(dict(FULL))).returncode, 0)
        with_fix = dict(FULL, suggested_fix="Have install print a PATH check.")
        r = run(self.repo, *log_args(with_fix))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("already logged", r.stdout)
        self.assertIn("(2 total", run(self.repo, "list").stdout)
        again = run(self.repo, *log_args(with_fix))
        self.assertIn("already logged", again.stdout)
        other = run(self.repo, *log_args(dict(FULL, suggested_fix="Document PATH in the README.")))
        self.assertNotIn("already logged", other.stdout)
        self.assertIn("(3 total", run(self.repo, "list").stdout)
        self.assertEqual(len(self.logged_events()), 3)

    def test_legacy_proposed_fix_entry_dedupes_against_same_suggested_fix(self) -> None:
        open_path = self.repo / ".agent-papercuts" / "open.md"
        open_path.write_text(self.open_text() + LEGACY_PROPOSED_FIX, encoding="utf-8")
        fields = dict(
            FULL,
            suggested_fix="Have install print a PATH check and fail if the shim is not reachable.",
        )
        # LEGACY_PROPOSED_FIX has no ideal_outcome, so it is thin, not a dup of a complete retry.
        r = run(self.repo, *log_args(fields))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("(2 total", run(self.repo, "list").stdout)

    def test_refusal_prints_flag_spellings_usage_and_enable_force_hint(self) -> None:
        r = run(self.repo, "log", "-m", "ci", "Smoke: the old one-liner.")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        err = r.stderr
        for flag in ("--goal", "--attempted", "--happened", "--workaround", "--ideal-outcome", "--suggested-fix"):
            self.assertIn(flag, err)
        self.assertIn("usage:", err)
        self.assertIn("papercut enable --force", err)
        self.assertIn("unknown — <reason>", err)

    def test_old_one_liner_snippet_repo_gets_a_clear_message(self) -> None:
        # A repo enabled before R-CLI-04 still teaches `papercut -m <model> "…"`.
        md = self.repo / "AGENTS.md"
        md.write_text(
            "<!-- agent-papercuts:begin -->\n```bash\npapercut -m <model> \"one or two sentences\"\n```\n<!-- agent-papercuts:end -->\n",
            encoding="utf-8",
        )
        # Exactly what the stale snippet tells agents to run: no subcommand, no -C.
        r = subprocess.run(
            [str(PAPERCUT), "-m", "old-model", "one or two sentences of friction"],
            cwd=self.repo, text=True, capture_output=True, env=os.environ.copy(),
        )
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("papercut enable --force", r.stderr)
        self.assertIn("--ideal-outcome", r.stderr)
        enabled = run(self.repo, "enable", "--force")
        self.assertEqual(enabled.returncode, 0, enabled.stderr + enabled.stdout)
        self.assertIn("--ideal-outcome", md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
