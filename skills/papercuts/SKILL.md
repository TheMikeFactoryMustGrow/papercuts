---
name: papercuts
description: >
  Log and fix agent friction ("papercuts") — dead-end tool calls, broken links,
  flaky commands, misleading errors, undocumented gotchas. Use when the user
  says "log a papercut", "fix papercuts", "sand the papercuts", "work through
  PAPERCUTS.md", runs /papercuts, or asks what friction agents hit. Also the
  workflow for proactive in-session logging via the papercut CLI.
metadata:
  short-description: "Log/fix agent friction (PAPERCUTS.md)"
---

# Papercuts

## Goal

**Leave the next agent better off for friction already logged.**

Remove or prevent each open papercut’s cause with the **smallest durable change**.
The log is a **sensor**; the **sanded agent surface** (docs, AGENTS.md, scripts,
config — or a *proposed* harness/skill patch) is the **product**.

### Success (done when)

Every open entry in scope is one of:

1. **Fixed** — preventive change landed; entries cleared from the log  
2. **Deferred** — explicit reason (product decision / external dep / unsure)  
3. **Reclassified** — not a papercut (real bug → mention once; noise → drop)

### Failure (do not)

- Clear log entries without a preventive change  
- Drive-by refactors unrelated to logged cuts  
- Formal RCA dossiers / per-item 5-Why by default  
- Silent edits to user-global or org-wide agent config without approval  

Inspired by [Steve Ruiz](https://x.com/steveruizok/status/2075303919664734295).

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

## Two entry paths

| Entry | When | Path |
|-------|------|------|
| **Log (ambient)** | Mid-task friction | L1 → LG1 → L2 → continue work |
| **Fix (user)** | `/papercuts`, “fix/sand/clear papercuts” | F1…F9 → report |

---

## CLI

```bash
papercut "one or two sentences: what you were doing → what got in the way"
papercut log -m <model-tag> -a <author> "message"
papercut list
papercut list -n 10
papercut path
papercut init
```

**Log location:** git repo root nearest cwd (walk up to `.git`); else cwd.

**If `papercut` is missing from PATH**, run the skill’s script:

```bash
python3 <skills-dir>/papercuts/scripts/papercut log "message"
```

Common skill dirs: `~/.claude/skills`, `~/.grok/skills`, `~/.agents/skills`.

---

## Path L — Log (proactive, in the moment)

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

### F1 Locate

```bash
papercut path && papercut list
```

State the resolved path in your report. Wrong tree → stop and clarify.

### FG1 Empty?

No open entries → say empty-ok and **stop**.

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

Default: **delete-on-fix**. No required “Resolved” archive section.

### F8 Sanded-surface report

Always deliver:

- Fixed clusters (light-causal one-liner each)  
- Deferred (+ why)  
- Reclassified  
- Remaining open: `papercut list -n 5`  
- Files touched  

### FG4 / F9 Promotion (proposal only)

If harness/skill-level candidates exist: **propose** exact patch text for global
agent config / skill / PATH install. **Do not apply** without user confirmation.

---

## Distinction from other systems

| Artifact | Purpose |
|----------|---------|
| `PAPERCUTS.md` | Tiny agent-DX sanding sensor |
| Issue tracker | Real bugs / tracked work |
| Git history | What shipped |
| Skill incident / eval logs | Skill or product quality systems (keep separate) |

---

## Bootstrap (once per machine + once per project)

```bash
# From this package checkout:
./scripts/papercut install          # skill + CLI
cd /path/to/your-project && papercut enable   # AGENTS.md snippet + PAPERCUTS.md
```
