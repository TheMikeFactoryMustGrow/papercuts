---
name: papercuts-adopt
description: >
  Roll papercuts capture into a repo and register it in the fleet — the
  install-the-machinery counterpart to papercuts (sand) and papercuts-kaizen
  (pattern review). Use when the user says "adopt papercuts in <repo>",
  "roll papercuts out to <repo>", "papercuts adopt", "/papercuts-adopt",
  "is <repo> wired for papercuts", or during a fleet rollout pass. Mode 1
  checks compliance; Mode 2 enables + registers via PR. Not for logging or
  fixing papercuts — use the papercuts skill for that.
metadata:
  short-description: "Enable papercuts in a repo + register it in the fleet"
---

# Papercuts Adopt

## Goal

**A repo that captures friction durably, and a fleet registry that knows it.**

Enablement without registration is invisible to fleet-status and kaizen;
registration without verified enablement is a lie in the registry. Adopt does
both, or reports exactly which half is missing.

The skill family:

| Skill | Cadence | Job |
|-------|---------|-----|
| **papercuts-adopt** | Once per repo | Machinery in + registry row |
| **papercuts** | Session / week | Sand the open list |
| **papercuts-kaizen** | Month / quarter | Pattern-mine the ledger |

Shared data layer: per-repo `.agent-papercuts/` + the package repo's
`fleet.yaml` registry (+ future `fleet-status` snapshots).

## Mode 1 — Check ("is this repo wired?")

From the target repo root:

```bash
papercut status
# or: python3 <skills-dir>/papercuts-adopt/scripts/papercut status
```

Report a gap table, not prose:

| Check | How |
|-------|-----|
| Enabled | `project_enabled=true` in status |
| Snippet current | Marked block in AGENTS.md matches the package `templates/AGENTS.snippet.md` (extract between `<!-- agent-papercuts:begin/end -->`, compare) |
| Data committed | `.agent-papercuts/` tracked by git, not ignored |
| Registered | Repo has a row in the papercuts package repo's `fleet.yaml` |

An enabled repo with a stale snippet is a gap (re-run `papercut enable` to
refresh); an enabled repo missing from `fleet.yaml` is a gap (fleet-status
will never sweep it).

## Mode 2 — Adopt ("set it up")

1. **Ask before enabling** if the user pointed you here without an explicit
   adopt request (same gate as the papercuts skill). An explicit "adopt/roll
   out" IS the yes.
2. `papercut enable` from the repo root; confirm `papercut status` →
   `project_enabled=true`.
3. **Commit the machinery on the session branch**: AGENTS.md snippet block +
   `.agent-papercuts/` (open.md, history.jsonl). On pr-only repos this lands
   as a PR (why-first body where the repo has the template); entries and
   machinery alike ride the session's PR — never leave them uncommitted in an
   ephemeral container.
4. **Register the repo**: append a row to `fleet.yaml` in the papercuts
   package repo (name, enabled date) — its own small PR there. The registry
   accumulates only through adopt; fleet-status reads it, never edits it.
5. Optional pairing: if the repo lacks why-first PR machinery, offer
   `/pr-template` Mode 2 in the same rollout pass (separate PR).

Done when: status green in the target repo, machinery merged (or PR open and
ready), and the `fleet.yaml` row merged (or PR open and ready). Anything
less: report which half is open.

## Failure (do not)

- Enable silently on an ambiguous ask
- Register a repo whose enablement you did not verify this session
- Hand-edit `fleet.yaml` rows for repos you did not adopt (fix via the repo's
  own adopt pass)
- Copy SKILL.md files into the target repo — skills stay on the machine;
  the snippet is the only ambient text a repo carries

## Install

Shipped with the papercuts package:

```bash
./scripts/papercut install   # installs papercuts + papercuts-kaizen + papercuts-adopt
```
