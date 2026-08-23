# Fleet review TODO — AGENTS / CLAUDE platform-agnostic cleanup

**Created:** 2026-07-10  
**Trigger:** Next time Mike works in each repo (not a batch cleanup now).

## Goal

For each enabled project, when next in that tree:

1. Review **`AGENTS.md`** (primary, platform-agnostic).  
2. Review **`CLAUDE.md`** if present — prefer thin shim pointing at AGENTS, not a second full policy.  
3. Confirm papercuts block is present and still correct (`.agent-papercuts/`, not root `PAPERCUTS.md`).  
4. Note anything that should move from home/global briefs into the project.

## Checklist (repos enabled 2026-07-10)

| Repo | Path | Next-visit review |
|------|------|-------------------|
| Linglepedia | `~/git/Linglepedia` | [ ] AGENTS + CLAUDE platform-agnostic |
| beancount | `~/Documents/beancount` | [ ] |
| Bean-Counter-Knowledge | `~/Documents/Bean-Counter-Knowledge` | [ ] |
| bean-counter | `~/code/bean-counter` | [ ] |
| gix-equity-comp-tool | `~/code/gix-equity-comp-tool` | [ ] |
| finance-dashboard | `~/code/finance-dashboard` | [ ] |
| gix-pipeline | `~/code/gix-pipeline` | [ ] |
| imessage-search | `~/code/imessage-search` | [ ] |
| process-design-plugin | `~/code/process-design-plugin` | [ ] (AGENTS created by enable) |
| google-workspace-mcp-config | `~/code/google-workspace-mcp-config` | [ ] (AGENTS created by enable) |
| partnerships-pipeline-agent | `~/code/partnerships-pipeline-agent` | [ ] (AGENTS created by enable) |
| karpathy-autoresearch | `~/code/karpathy-autoresearch` | [ ] |
| wbr-app | `~/code/wbr-app` | [ ] (AGENTS created by enable) |
| papercuts (this package) | `~/code/papercuts` | [ ] |

## Done when

- [ ] All rows checked  
- [ ] No project relies on home AGENTS for ambient papercuts logging  
- [ ] CLAUDE.md nowhere duplicates a full second policy without pointing at AGENTS  

When a row is done, tick it and date the commit that cleaned the briefs.

## Capture-liveness eval (Mike, 2026-08-23) — DESIGNED, NOT BUILT

**Problem:** enabled ≠ working. As of 2026-08-23, ~12 repos are enabled but only Linglepedia shows real capture (17 logged / 12 resolved); the rest are silent, and silence is ambiguous — frictionless work or broken capture (snippet ignored, CLI missing in that environment, hand-append drift). Nothing measures it. This is the dmaic-control regression guard for the *capture process itself*, distinct from the CI suite (which guards the tool's code).

**Metrics (all derivable from existing per-repo `.agent-papercuts/history.jsonl` + git activity — no new instrumentation):**

| Metric | Calculation | Red flag |
|---|---|---|
| Capture rate | `logged` events per repo per week | 0 while the repo had commits that week |
| Silent-repo detection | enabled + 0 logs in N days AND git commits in the window | capture failing → investigate that repo's snippet/PATH |
| Sanding latency | age of oldest entry in `open.md` | > ~30d — logs nobody sands kill the habit |
| Loop closure | `resolved`/`logged` ratio, trailing | falling trend |

**Mechanism:** a stdlib `papercut fleet-status` subcommand (or standalone script) sweeping a repo list, JSON out; run as a scheduled routine that pings Mike only on threshold breach. Baseline row per repo on first run.

**Refinements (Mike-ratified 2026-08-23, second pass):**

- **Registry via adopt** — the repo list is `fleet.yaml` in this repo, appended only by the `papercuts-adopt` skill in the same pass that verifies enablement. fleet-status reads it, never edits it; the list never drifts from reality.
- **Health-signal definitions** — a healthy repo *oscillates* (captures keep arriving, sanding keeps draining). A declining open count and a low open/resolved ratio are NOT the health signals. The pathological states are the flat lines: **zero captures despite git activity** (silent repo) and **captures with no resolutions** (logging into a void). Primary metrics: capture rate per unit of git activity, and sanding latency; open/resolved ratio is the secondary trend. A repo with 0 logged in 90 active days is worse than one with 8 open.
- **Append-only snapshots** — each sweep lands as a PR to this repo appending `fleet-status/<date>.json` (or one JSONL), never overwriting a status file; kaizen gets trend history for free and every sweep is reviewable. Threshold alerts (silent repo, latency > N days) go in the sweep PR's body.
- **Skill family (ratified)** — adopt / sand (papercuts) / kaizen, all in this repo, with fleet-status as the shared data layer. Cheapest-model routine runs the sweep script and files the snapshot PR; judgment stays in the skills.

**Thresholds + playbooks (Mike-ratified 2026-08-23, dmaic-analyze pass):**

Causal chain — every output traces to a lever:

| Output metric | Controllable inputs | External inputs (bounds) |
|---|---|---|
| capture_rate | snippet_current, cli_available (env setup line), entries-ride-the-PR rule | git_activity (no work → no captures, legitimately) |
| silent_repo | snippet_current, cli_available | git_activity (an idle repo is dormant, not silent) |
| sanding_latency | sanding_session_cadence (/papercuts runs) | Mike's available time |
| loop_closure | sanding_session_cadence, resolve-via-CLI discipline | capture volume |

| Metric | Green | Yellow | Red | First action on red (owner: the sweep session; escalation: Mike) |
|---|---|---|---|---|
| capture_rate | ≥1 logged in any 30d window with commits | 0 logged in 30d WITH commits | 0 logged in 60d WITH commits | Open that repo's AGENTS.md: snippet stale/missing → queue adopt Mode 1; snippet current but CLI absent/unverified in that repo's environments → escalate as infra gap (env setup line); snippet current AND CLI confirmed → escalate as "instruction ignored". Document in the sweep PR body. |
| silent_repo | — (derived flag) | = yellow capture_rate | = red capture_rate | Same playbook — silent_repo IS red capture_rate's detector; one investigation, not two. |
| sanding_latency | oldest open <30d | 30–60d | >60d | Sweep PR body lists repo + oldest entry; Mike decides sand-now vs batch (next sanding session, not an SLA). |
| loop_closure | trailing resolved/logged ≥0.5 | 0.3–0.5, or <0.3 with ≤5 open (low volume — same bound as red) | <0.3 with >5 open | Check for hand-deleted entries first (history vs open.md mismatch = discipline failure), then treat as latency. |

Known failure modes (all observed or near-missed 2026-08): snippet stale after a CLI update; CLI absent in a cloud container; entries logged but never pushed; hand-deleted entries starving history; genuine frictionless dormancy (the false positive git_activity bounds against). First sweep writes baseline rows and alerts on nothing; yellow queues a re-check next sweep, never a ping.

**Next step (thresholds now ratified):** build the `fleet-status` subcommand (one PR) + the sweep routine (one PR) — chartered for a fresh session.
