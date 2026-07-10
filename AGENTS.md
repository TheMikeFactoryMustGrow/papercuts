# AGENTS.md — papercuts package

You are in the **papercuts distribution package**, not a random app repo.
Your job is usually **install / enable / improve this package** — not invent a
new cleanup skill from scratch.

## What this package is

A platform-agnostic way for coding agents to:

1. **Log** tiny non-blocking friction to a per-repo `.agent-papercuts/open.md` (+ history ledger)  
2. **Sand** open items later (cluster-first light-causal — **not** formal RCA per item) via **papercuts**  
3. **Kaizen** on the shadow ledger quarterly via **papercuts-kaizen** (patterns / optional deep RCA)
## Do this when a human shares this repo

### A) Machine install (once)

```bash
chmod +x scripts/papercut
./scripts/papercut install
command -v papercut || export PATH="$HOME/.local/bin:$PATH"
```

Installs:

- Skills → `papercuts` **and** `papercuts-kaizen` under `~/.claude/skills` and `~/.grok/skills`  
- CLI → `~/.local/bin/papercut`
### B) Enable in a *consumer* project (once per project)

**Critical:** `install` alone does not turn on capture in a project. You must
also create the **snippet** and **log**.

```bash
cd /path/to/their-project
papercut status          # see needs_enable
papercut enable          # AGENTS.md snippet + `.agent-papercuts/`
papercut status          # project_enabled=true
```

`papercut enable` does:

| Creates / updates | Content |
|-------------------|---------|
| `AGENTS.md` | Marked `<!-- papercuts:begin -->…<!-- papercuts:end -->` block from `templates/AGENTS.snippet.md` |
| `.agent-papercuts/open.md` | Open sanding list |
| `.agent-papercuts/history.jsonl` | Shadow ledger (append-only) |
**Do not** copy the entire SKILL.md into every project. Projects only need the
short AGENTS snippet; the skill stays machine-global (or harness-global).

If the skill is already installed and the user is **in** a consumer project, you
can enable without them cloning this package: run `papercut status`, then **ask**
before `papercut enable` (skill bootstrap gate). That is the preferred “new repo”
on-ramp.

### C) If they only asked “what is this?”

Summarize from `README.md` + `docs/DESIGN.md`. Offer install + enable. Emphasize
**three pieces**: machine skill/CLI, project AGENTS snippet, project `.agent-papercuts/`.

### D) Home / global AGENTS

If the user asks to “add papercuts to my global AGENTS,” paste only
`templates/HOME-AGENTS.snippet.md` (pointer). **Do not** paste the full project
ambient-log block into home. See `docs/HOME-VS-REPO.md`.

## What not to do

| Don’t | Why |
|-------|-----|
| Rewrite a new RCA skill per project | SKILL.md already defines sand protocol |
| Run formal 5-Why on every log line | Spec is cluster-first light-causal |
| Auto-edit the user’s home AGENTS without asking | Promotion is proposal-only |
| Put ambient log instructions in **home** AGENTS | Capture is per-repo after `enable` |
| Put all friction in one global log | Logs are per git root under `.agent-papercuts/` |
| File Linear/GitHub issues for every papercut | Different system; papercuts are sanding |

## If improving this package

- Keep CLI **Python stdlib only** (no node/yarn required).  
- Keep consumer surface **tiny** (snippet + `.agent-papercuts/`).  
- Skill stays the home of fix protocol depth.  
- See `docs/DESIGN.md` before adding steps (bias to delete).

## Quick smoke test after install

```bash
cd /tmp && mkdir -p pc-test && cd pc-test && git init -q
papercut enable
papercut -m test "Smoke: enable path works."
papercut list
```

<!-- agent-papercuts:begin -->
## Log agent papercuts

When you hit **small friction** while working — a tool call that missed and had
to be retried, a confusing or undocumented setup step, a flaky command, a stale
cache, a misleading error, a non-obvious gotcha — log it via:

```bash
papercut -m <model> "one or two sentences: what you were doing → what got in the way"
```

Data lives under **`.agent-papercuts/`** (open list + history), not a root
`PAPERCUTS.md`, so it does not collide with product files. Do this
**proactively, in the moment**.

Sand: skill **papercuts** ("fix the papercuts"). Clear with `papercut resolve`
(not hand-delete). Long cycle: **papercuts-kaizen**.
<!-- agent-papercuts:end -->
