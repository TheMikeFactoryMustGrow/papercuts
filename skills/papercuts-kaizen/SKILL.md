---
name: papercuts-kaizen
description: >
  Longer-cycle review of agent friction history (papercuts shadow ledger).
  Cluster patterns over weeks/months, score recurrence after "fixed", run
  optional deep RCA only on escalated clusters, and propose systemic sanding
  (docs, AGENTS, tooling). Use when the user says "papercuts kaizen",
  "/papercuts-kaizen", "quarterly papercut review", "pattern review on
  papercuts", or "what friction patterns keep coming back". Not for day-to-day
  sanding — use the papercuts skill for that.
metadata:
  short-description: "Long-cycle papercuts pattern review"
---

# Papercuts Kaizen

## Goal

**Find systemic agent-DX debt in the historical record** — not clear one open
ticket. The open list (`PAPERCUTS.md`) is a short sensor. The **shadow ledger**
(`.papercuts/history.jsonl`) is the compounding archive.

### Success (done when)

1. History + open log loaded and summarized (volume, resolved rate, repeats)  
2. Clusters formed by **shared preventive mechanism** (not one row = one RCA)  
3. Each top cluster has a disposition: delete-requirement / simplify / fix / watch / accept  
4. **Deep RCA** only on escalated clusters (see bar below)  
5. Report delivered; any global-config promotions are **proposals only**  

### Failure (do not)

- Treat this as the daily sand pass (use **papercuts** skill instead)  
- Formal 5-Why on every historical line  
- Silent home-AGENTS / org-wide edits  
- Invent history if the ledger is empty — say so and stop or offer enable  

---

## Data sources

| Source | Path | Role |
|--------|------|------|
| Shadow ledger | `.papercuts/history.jsonl` | `logged` + `resolved` events (primary) |
| Open list | `PAPERCUTS.md` | Still-open friction |
| Stats | `papercut history --stats` | Quick counts / repeats |

**Retention model:** open list is **delete-on-fix** via `papercut resolve`.
Every `log` and `resolve` also appends to the ledger. Hand-deleting from
`PAPERCUTS.md` **skips history** — call that out if you see it.

---

## When to run

- User asks for kaizen / quarterly review / pattern review  
- Suggested cadence: **monthly or quarterly**, or after ~20+ resolved events  
- Not every session  

---

## Procedure

### K0 Bootstrap

```bash
papercut status
papercut history --stats
papercut history -n 30
papercut list -n 20
```

If `needs_enable=true`, offer `papercut enable` (ask first) — same rule as papercuts skill.

If `history_events=0` and open log empty: **nothing to kaizen**. Explain that
history builds when agents `log` and `resolve`. Stop.

### K1 Load window

Default window: **last 90 days** (or all history if smaller).  
User can override (“last year”, “since March”).

Build working sets:

- all `logged` events in window  
- all `resolved` events in window  
- current open entries  

### K2 Cluster by mechanism

Group by **same durable preventive change** (same doc, script, AGENTS rule,
tooling default). Prefer under-clustering.

For each cluster record:

- size (logged count)  
- resolved count + notes  
- still open?  
- **recurrence**: logged again after a resolve with same/similar body  

### K3 Score and rank

Prioritize clusters with:

1. High volume  
2. Recurrence after resolve (fix didn’t stick)  
3. Multi-file / multi-agent / harness-level smell  
4. Still open and old  

Top N (default **5**) go to the disposition ladder.

### K4 Disposition ladder (Elon order)

For each top cluster, walk in order; stop when disposition is clear:

1. **Question the requirement** — should this workflow exist at all?  
2. **Delete** — remove dead steps/docs that cause the cut  
3. **Simplify** — fewer steps, clearer path  
4. **Fix** — smallest preventive change (or propose if out of scope)  
5. **Watch** — track next period; no change yet  
6. **Accept** — common-cause noise; don’t overfit  

Record the ladder answer in the report.

### K5 Deep RCA (escalation only)

**Escalate** a cluster to deeper RCA only if **any** of:

- size ≥ **5** logged in window, or  
- **recurrence** after resolve ≥ **2**, or  
- user explicitly asked for deep dive on that theme  

Deep RCA means a short structured writeup (symptoms → mechanism → why it survives →
fix options) — **not** a 5-Why theater document for every row. Cap at a few
paragraphs per escalated cluster.

### K6 Act or propose

| Scope | Action |
|-------|--------|
| Repo-local, fixable now | Optional small fixes **if user asked to implement**; else propose |
| Harness / global agent config | **Propose only** |
| Needs product decision | Defer with owner question |

Default for kaizen: **analyze + propose**; implement only if user said “and fix them”.

### K7 Report

Deliver:

1. Window + data volumes (`logged`, `resolved`, open)  
2. Top clusters table (size, recurrence, disposition)  
3. Escalated RCA notes (if any)  
4. Concrete proposals (file paths / AGENTS lines)  
5. What to watch next period  
6. If history is thin: how to improve capture (`resolve` not hand-delete)  

---

## CLI cheatsheet

```bash
papercut history --stats
papercut history --event resolved -n 50
papercut history --event logged -n 50
papercut list
```

---

## Relation to other skills

| Skill | Cadence | Job |
|-------|---------|-----|
| **papercuts** | Session / week | Sand open list (light-causal) |
| **papercuts-kaizen** | Month / quarter | Pattern mine ledger + systemic proposals |
| Skill-ops kaizen (other systems) | Plugin run quality | **Do not merge** data or procedures |

---

## Install

Shipped with the papercuts package:

```bash
./scripts/papercut install   # installs papercuts + papercuts-kaizen
```
