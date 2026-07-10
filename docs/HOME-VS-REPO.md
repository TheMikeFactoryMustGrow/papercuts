# Home vs repo instructions

Help users put papercuts guidance in the **right layer**.

## Rule

| Layer | What belongs | What does **not** |
|-------|----------------|-------------------|
| **Machine / home** (`~/.grok/AGENTS.md`, `~/.claude/Claude.md`, etc.) | “Papercuts is installed; capture is **per-repo**.” One short pointer. | Ambient “log every friction to PAPERCUTS.md” — wrong scope, wrong path |
| **Project** (`AGENTS.md` after `papercut enable`) | Full ambient log snippet + where data lives (`.agent-papercuts/`) | Full sand/kaizen protocol (that’s the **skill**) |
| **Skill** (installed once) | Sand + kaizen procedures | — |

## Why home should stay thin

Friction is **project-scoped**. A global rule encourages logging into whatever cwd happens to be, or inventing a machine-wide log. That fights collision safety and muddies the sand list.

Home AGENTS only needs:

```markdown
## Papercuts (per-repo only)

Friction capture is project-scoped under `.agent-papercuts/`.
Ambient logging applies only when the repo has been `papercut enable`’d.
Skills: **papercuts** (sand) + **papercuts-kaizen** (long cycle).
```

See also `templates/HOME-AGENTS.snippet.md`.

## Successful install path (for docs / agents)

1. **Machine once:** `./scripts/papercut install`  
2. **Each project once:** `papercut enable` (or skill bootstrap ask)  
3. **Work:** agents log mid-task from the **project** AGENTS snippet  
4. **Sand / kaizen:** skills, user-triggered  

Do **not** tell users to paste the full project snippet into home AGENTS.
