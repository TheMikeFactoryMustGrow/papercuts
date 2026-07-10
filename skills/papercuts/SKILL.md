---
name: papercuts
description: >
  Log and fix agent friction ("papercuts") — dead-end tool calls, broken links,
  flaky commands, misleading errors, undocumented gotchas. Use when the user
  says "log a papercut", "fix papercuts", "sand the papercuts", "work through
  PAPERCUTS.md", "enable papercuts", "set up papercuts in this repo", runs
  /papercuts, or asks what friction agents hit. Also the workflow for proactive
  in-session logging via the papercut CLI. On invoke, check whether the project
  has the AGENTS snippet and PAPERCUTS.md; offer enable if missing.
metadata:
  short-description: "Log/fix agent friction (PAPERCUTS.md)"
---

# Papercuts

## Goal

**Leave the next agent better off for friction already logged.**

Remove or prevent each open papercut’s cause with the **smallest durable change**.
The log is a **sensor**; the **sanded agent surface** (docs, AGENTS.md, scripts,
config — or a *proposed* harness/skill patch) is the **product**.

A project needs **three** pieces (not just the skill):

| Piece | Where | Role |
|-------|--------|------|
| **Skill + CLI** | Machine (`papercut install`) | How to sand + how to log |
| **AGENTS.md snippet** | Project (`papercut enable`) | Permission to log mid-task |
| **PAPERCUTS.md** | Project git root | Open sanding list (delete-on-fix) |
| **`.papercuts/history.jsonl`** | Project git root | Shadow ledger for long-cycle kaizen |

Running this skill in a **new repo** is a supported way to get the project pieces
in place — see **Bootstrap gate** below.

### Success (done when)

Every open entry in scope is one of:

1. **Fixed** — preventive change landed; entries cleared from the log  
2. **Deferred** — explicit reason (product decision / external dep / unsure)  
3. **Reclassified** — not a papercut (real bug → mention once; noise → drop)

If the project was not enabled and the user accepted enable: snippet + log exist.

### Failure (do not)

- Clear log entries without a preventive change  
- Drive-by refactors unrelated to logged cuts  
- Formal RCA dossiers / per-item 5-Why by default  
- Silent edits to user-global or org-wide agent config without approval  
- **Auto-run `papercut enable` without asking the user**  

Inspired by [Steve Ruiz](https://x.com/steveruizok/status/2075303919664734295).

---

## Bootstrap gate (run first on every skill invoke)

Before log-or-fix work, check whether **this repo** is set up for future capture.

```bash
papercut status
# or: python3 <skills-dir>/papercuts/scripts/papercut status
```

Read the key fields:

| Field | Meaning |
|-------|---------|
| `needs_enable=true` | Snippet and/or `PAPERCUTS.md` missing |
| `snippet=missing` | No papercuts block in AGENTS.md / CLAUDE.md |
| `log=missing` | No `PAPERCUTS.md` at repo root |
| `project_enabled=true` | Both present — proceed |

### If `needs_enable=true`

**Stop and ask the user** (do not enable silently):

> This repo doesn’t have papercuts project setup yet (AGENTS.md snippet and/or
> PAPERCUTS.md). Enable them so future sessions can capture friction here?
> I can run `papercut enable` (adds a short AGENTS.md block + creates the log).

| User answer | Action |
|-------------|--------|
| **Yes** | `papercut enable` (from repo root / correct `-C`). Confirm with `papercut status`. Then continue. |
| **No** | Proceed without ambient capture. You may still `papercut init` + log **if** the user is actively logging this session; do not add the AGENTS snippet. |
| **Log only this once** | `papercut init` if needed, then log — still **no** AGENTS snippet unless they yes later. |

### If skill/CLI missing (`cli_on_path=false` and no skill path)

Tell the user machine install is needed once:

```bash
# from a papercuts package checkout
./scripts/papercut install
```

Do not invent a new skill. Point at the package repo / installed skill.

### Easy “new repo” path

User opens a project and runs `/papercuts` or “set up papercuts here”:

1. Bootstrap gate → `status` → ask → `enable` on yes  
2. If they also wanted a sand pass and the log is empty → report empty-ok (setup succeeded)  
3. If they only wanted setup → stop after enable + short confirm of files created  

---

## Analysis depth (not formal RCA)

**Cluster-first light-causal — not RCA on every item one-by-one.**

| Do | Don’t |
|----|--------|
| Group entries that share **one** preventive fix | Write a 5-Why per row |
| 1–3 sentences per cluster: *doing → blocked by → prevent with* | Produce an RCA document |
| Fix once; clear all members of the cluster | Re-diagnose members separately when the cause is the same |

Deeper causal analysis only if the **user** explicitly asks.

---

## Two entry paths (after bootstrap)

| Entry | When | Path |
|-------|------|------|
| **Log (ambient)** | Mid-task friction | L1 → LG1 → L2 → continue work |
| **Fix (user)** | `/papercuts`, “fix/sand/clear papercuts” | F1…F9 → report |
| **Enable only** | “set up papercuts in this repo” | Bootstrap gate → enable → stop |

---

## CLI

```bash
papercut status                              # project setup check
papercut enable                              # AGENTS snippet + PAPERCUTS.md + history dir
papercut "one or two sentences: …"           # log (also appends history event=logged)
papercut log -m <model-tag> -a <author> "…"
papercut list
papercut list -n 10
papercut resolve --stamp <ts> -n "what you fixed"   # clear open entry + history event=resolved
papercut resolve --contains "vitest" -n "…"
papercut resolve --index 1 --index 2 -n "…"           # indices from list (newest first)
papercut history -n 20
papercut history --stats
papercut path
papercut init                                # log file only (no AGENTS snippet)
papercut install                             # machine: papercuts + papercuts-kaizen + PATH
```

**Retention:** open list is **delete-on-fix** via `resolve`. History is **append-only**.
Never hand-delete entries from `PAPERCUTS.md` — that skips the ledger and starves kaizen.
**Log location:** git repo root nearest cwd (walk up to `.git`); else cwd.

**If `papercut` is missing from PATH**, run the skill’s script:

```bash
python3 <skills-dir>/papercuts/scripts/papercut status
```

Common skill dirs: `~/.claude/skills`, `~/.grok/skills`, `~/.agents/skills`.

---

## Path L — Log (proactive, in the moment)

If you hit friction and **status** would show `needs_enable=true`, you may still
log **after** a quick user ask to enable (preferred) or one-shot `init` (session only).

Keep working the user’s task. Papercuts are non-blocking.

1. **L1** — Notice friction (tool miss, bad docs, flaky command, gotcha, broken path).  
2. **LG1** — Real papercut?  
   - Yes: environmental/tooling/docs/gotcha; you recovered or worked around  
   - No: pure “I should have read the file,” pure experiment noise → **do not log**  
   - Ambiguous → prefer log (later fix pass can skip)  
3. **L2** — `papercut -m <model> "…"` immediately (don’t batch until end).  
4. Continue the task.

**Don’t:** open the issue tracker for papercuts; mine the full session transcript unprompted.

---

## Path F — Fix (user-triggered only)

### F0 Bootstrap

Run **Bootstrap gate** first. If user declines enable and log is missing → empty-ok / nothing to sand.

### F1 Locate

```bash
papercut path && papercut list
```

State the resolved path in your report. Wrong tree → stop and clarify.

### FG1 Empty?

No open entries → say empty-ok and **stop** (still fine after a successful enable).

### F2 Load + cluster

Parse open entries. **Same cluster** iff the same durable change would prevent both
(same doc line, script, AGENTS rule, config default). When unsure, under-cluster
(keep separate) — do not over-clear.

### F3 Diagnose (light-causal + classify)

Per cluster, **1–3 sentences** only. Classify each:

| Class | Meaning |
|-------|---------|
| **fixable-now** | Local to this scope; no product decision; context readable |
| **defer** | Needs human/product/external; or fix uncertain |
| **reclassify** | Real bug or noise — not a papercut |
| **promote-candidate** | Cause lives in user-global agent config, skill install, PATH, MCP, or multi-repo pattern |

### FG2 Any fixable-now?

No → report deferred-only (reasons) and **stop**.  
Yes → F5 for each fixable cluster (finite **F2 snapshot** — ignore mid-pass ambient appends).

### F5 Smallest preventive fix

- Prefer docs / AGENTS.md / helpers over clever code  
- Prefer deleting dead steps over adding warnings  
- One PR-sized batch unless user asked for a single item  
- If blast radius looks large (>~5 files), stop that cluster → defer or ask  

### FG3 Prevents recurrence?

Would a future agent following current docs/tools still hit the same failure mode?

- **Yes** → F7 clear all members of the cluster from `PAPERCUTS.md`  
- **No / unsure / partial** → F6 defer with reason; **do not clear**

### F7 Clear (only after FG3 yes)

**Always use the CLI** (writes shadow history):

```bash
papercut resolve --stamp <entry-stamp> -n "one-line preventive fix"
# or after clustering several stamps:
papercut resolve --stamp A --stamp B -n "same fix for both"
```

Do **not** hand-edit entries out of `PAPERCUTS.md`.  
Open list = delete-on-fix. History = `.papercuts/history.jsonl` for **papercuts-kaizen**.

### F8 Sanded-surface report

Always deliver:

- Fixed clusters (light-causal one-liner each) + resolve notes  
- Deferred (+ why)  
- Reclassified  
- Remaining open: `papercut list -n 5`  
- Files touched  
- If enable ran this session: note that project is now set up for capture  
- Mention `papercut history --stats` if many resolves this session  

### FG4 / F9 Promotion (proposal only)

If harness/skill-level candidates exist: **propose** exact patch text for global
agent config / skill / PATH install. **Do not apply** without user confirmation.

---

## What `papercut enable` creates (for humans and agents)

1. **AGENTS.md** (or appends to existing) — marked block:

```markdown
<!-- papercuts:begin -->
## Log papercuts
… instruction to call papercut mid-task …
<!-- papercuts:end -->
```

Template: package `templates/AGENTS.snippet.md`.

2. **PAPERCUTS.md** at git root — header only until agents log.  
   Template: package `templates/PAPERCUTS.header.md`.

3. **`.papercuts/history.jsonl`** — empty shadow ledger (created on enable / first log).

It does **not** copy SKILL.md into the project. Skills stay on the machine.

**Longer cycle:** skill **papercuts-kaizen** mines the ledger for systemic patterns
(quarterly / monthly). Day-to-day sanding stays here.

---

## Distinction from other systems

| Artifact | Purpose |
|----------|---------|
| `PAPERCUTS.md` | Tiny agent-DX sanding sensor |
| Issue tracker | Real bugs / tracked work |
| Git history | What shipped |
| Skill incident / eval logs | Skill or product quality systems (keep separate) |

---

## Machine install (once)

```bash
# From the papercuts package checkout:
./scripts/papercut install
```

Then in any project (or via this skill’s bootstrap ask):

```bash
papercut enable
papercut status   # project_enabled=true
```
