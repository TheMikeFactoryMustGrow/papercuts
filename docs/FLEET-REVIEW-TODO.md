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

**Next step:** design the thresholds/owner via dmaic-analyze, then build the subcommand (one PR) + the routine (one PR).
