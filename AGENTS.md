# AGENTS.md — papercuts package

You are in the **papercuts distribution package**, not a random app repo.
Your job is usually **install / enable / improve this package** — not invent a
new cleanup skill from scratch.

## What this package is

A platform-agnostic way for coding agents to:

1. **Log** tiny non-blocking friction to a per-repo `PAPERCUTS.md`  
2. **Sand** that list later (cluster-first light-causal fixes — **not** formal RCA per item)

## Do this when a human shares this repo

### A) Machine install (once)

```bash
chmod +x scripts/papercut
./scripts/papercut install
command -v papercut || export PATH="$HOME/.local/bin:$PATH"
```

Installs:

- Skill → `~/.claude/skills/papercuts` and `~/.grok/skills/papercuts`  
- CLI → `~/.local/bin/papercut`

### B) Enable in a *consumer* project (once per project)

**Critical:** `install` alone does not turn on capture in a project. You must
also create the **snippet** and **log**.

```bash
cd /path/to/their-project
papercut status          # see needs_enable
papercut enable          # AGENTS.md snippet + PAPERCUTS.md
papercut status          # project_enabled=true
```

`papercut enable` does:

| Creates / updates | Content |
|-------------------|---------|
| `AGENTS.md` | Marked `<!-- papercuts:begin -->…<!-- papercuts:end -->` block from `templates/AGENTS.snippet.md` |
| `PAPERCUTS.md` | Header from `templates/PAPERCUTS.header.md` (empty sanding list) |

**Do not** copy the entire SKILL.md into every project. Projects only need the
short AGENTS snippet; the skill stays machine-global (or harness-global).

If the skill is already installed and the user is **in** a consumer project, you
can enable without them cloning this package: run `papercut status`, then **ask**
before `papercut enable` (skill bootstrap gate). That is the preferred “new repo”
on-ramp.

### C) If they only asked “what is this?”

Summarize from `README.md` + `docs/DESIGN.md`. Offer install + enable. Emphasize
**three pieces**: machine skill/CLI, project AGENTS snippet, project PAPERCUTS.md.

## What not to do

| Don’t | Why |
|-------|-----|
| Rewrite a new RCA skill per project | SKILL.md already defines sand protocol |
| Run formal 5-Why on every log line | Spec is cluster-first light-causal |
| Auto-edit the user’s home AGENTS without asking | Promotion is proposal-only |
| Put all friction in one global log | Logs are per git root |
| File Linear/GitHub issues for every papercut | Different system; papercuts are sanding |

## If improving this package

- Keep CLI **Python stdlib only** (no node/yarn required).  
- Keep consumer surface **tiny** (snippet + PAPERCUTS.md).  
- Skill stays the home of fix protocol depth.  
- See `docs/DESIGN.md` before adding steps (bias to delete).

## Quick smoke test after install

```bash
cd /tmp && mkdir -p pc-test && cd pc-test && git init -q
papercut enable
papercut -m test "Smoke: enable path works."
papercut list
```
