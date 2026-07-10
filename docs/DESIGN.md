# Design notes — constraints we learned

This is the distilled design record for people (and agents) packaging or
extending papercuts. It is intentionally harness-agnostic.

## Problem

Coding agents hit small friction constantly and **under-report** it. They retry,
work around, and move on. That hides sandable repo and tooling debt.

## Goal (Working Backwards)

**Concrete output:** a *sanded agent surface* — preventive changes so the next
agent is less likely to hit the same cut — plus a short report.

**Not the product:** an empty `PAPERCUTS.md`, a full RCA dossier, or a ticket
flood.

**Goal statement for the skill:**

> Leave the next agent better off for friction already logged: remove or prevent
> each open papercut’s cause with the smallest durable change. The log is a
> sensor; the sanded surface is the product.

## Two loops (+ bootstrap)

| Loop | Trigger | Output |
|------|---------|--------|
| **Bootstrap** | Skill invoke / “set up papercuts” | Optional `papercut enable` after user yes |
| **Log** | Ambient, mid-task | One entry in repo `PAPERCUTS.md` |
| **Fix / sand** | User asks | Preventive fixes + cleared/deferred entries + report |

**Bootstrap gate:** on skill invoke, `papercut status`. If snippet or log is
missing, **ask** before `papercut enable`. Never silent project edits.

Do **not** auto-mine session transcripts unless the user asks. Under-reporting
is the default failure mode of agents; over-reporting is rarer and easy to skip
on a fix pass.

## Analysis depth

**Cluster-first light-causal** — not formal RCA on every item.

1. Group entries that share one preventive fix.  
2. Per cluster: 1–3 sentences (*doing → blocked by → prevent with*).  
3. Fix once; clear all members.  
4. Clear **only if** the fix likely prevents recurrence; else defer with reason.

Formal 5-Why / dossiers were considered and **rejected** as default: they
optimize theater over sanding. Optional only if the user asks.

## What lives where

| Concern | Home |
|---------|------|
| Permission to log + one-liner | Project `AGENTS.md` snippet |
| Full sand protocol | Skill (`SKILL.md`) |
| Human onboarding | Package `README.md` |
| Agent onboarding for *this package* | Package `AGENTS.md` |
| Friction list | Per-repo `PAPERCUTS.md` at git root |
| Machine install | `papercut install` → skill dirs + PATH |

### Why README + AGENTS + skill (not one file)

- **Humans** want narrative, install, and “why.”  
- **Agents in the package** need bootstrap steps without the whole essay.  
- **Agents mid-task** need a short always-on rule (snippet), not the full fix graph.  
- **Agents sanding** need the full protocol only when invoked (skill).

Loading the full fix protocol into every session via AGENTS.md is prompt bloat.
Loading nothing means agents never log.

## Hard rules

1. **Never delete a log entry without a preventive change** (or explicit
   reclassify-as-noise).  
2. **No drive-by refactors** — stay on the cluster’s cause.  
3. **Promotion is proposal-only** — do not silently edit user-global agent
   config (home AGENTS, org defaults).  
4. **Finite snapshot** on a fix pass — ignore ambient appends mid-pass.  
5. **Separate systems** — not an issue tracker; not skill-ops/eval incident logs.

## Scope ladder (when fixing)

| Class | Where the fix lands |
|-------|---------------------|
| Repo-local | Docs, project AGENTS.md, scripts, config in that git root |
| Harness / machine | PATH, skill install, MCP — **propose** only |
| Multi-repo pattern | Same — propose promotion; don’t dual-write a global log |

## Packaging decisions

| Decision | Choice | Rejected alternative |
|----------|--------|----------------------|
| Runtime | Python 3 stdlib CLI | yarn/node-only tool |
| Skill install | User skill dirs (Claude/Grok/agents) | Recreate skill per repo |
| Project enable | Marked AGENTS.md block + `PAPERCUTS.md` | Vendor full skill into every repo |
| Log location | Per git root | Single machine-wide log |
| Default RCA | Light-causal cluster | Mandatory 5-Why |
| Session mining | Off by default | Always-on review |

## Metrics worth caring about later

- Entries logged per active project-week (sensor alive?)  
- Fraction of fix runs with delete-without-fix = 0 (must stay zero)  
- Recurrence of the same signature after a “fix”  
- Fix blast radius (files touched per cluster)

## Non-goals

- Replacing issue trackers  
- Auto-filing tickets  
- Slack “venting” (fine as a separate culture tool; not this package)  
- Merging with skill verification / kaizen incident frameworks  

## Credit

Pattern popularized by Steve Ruiz’s papercuts CLI + AGENTS.md note (2026).
This package generalizes it for multi-harness agent fleets.
