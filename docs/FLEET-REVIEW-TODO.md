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
