# papercuts

**Give coding agents a way to log tiny friction — then sand it later.**

Agents constantly hit dead-end tool calls, broken docs, flaky commands, and
gotchas. They usually push through without saying anything. Papercuts makes
that friction visible and fixable.

Inspired by [Steve Ruiz](https://x.com/steveruizok/status/2075303919664734295).

## Install with an agent

Paste this to an agent that can run shell commands:

```text
1) Clone https://github.com/TheMikeFactoryMustGrow/papercuts (or use my checkout).
2) Run: chmod +x scripts/papercut && ./scripts/papercut install
3) In my project repo: run papercut status; if needs_enable, ask me then papercut enable.
4) Confirm with papercut status (project_enabled=true).
```

Or, if the skill is **already** installed on the machine, in any project:

> Set up papercuts in this repo

The **papercuts** skill checks status and **asks before** writing AGENTS.md /
PAPERCUTS.md. Later: “fix the papercuts”. Quarterly: “papercuts kaizen”.

| Audience | Read this |
|----------|-----------|
| **Humans** | this README |
| **Agents opening this package** | [`AGENTS.md`](./AGENTS.md) |
| **Day-to-day sand** | skill [`SKILL.md`](./SKILL.md) / `skills/papercuts/` |
| **Long-cycle patterns** | skill [`skills/papercuts-kaizen/SKILL.md`](./skills/papercuts-kaizen/SKILL.md) |

---

## Does the coworker flow make sense?

**Almost — with one important correction.**

| What you imagined | Better packaging |
|-------------------|------------------|
| Share repo link → agent reads it → **creates** a skill for cleanup RCA | Share repo link → **install** the skill once (it’s already written) |
| Agent adds guidance to the project’s AGENTS.md | Yes — or run `papercut enable` |
| Formal RCA on every item | **No** — cluster-first **light-causal** (1–3 sentences per shared cause) |

**Recommended coworker onboarding:**

1. Share this repo URL.  
2. **Once per machine:** `./scripts/papercut install` (skill + `papercut` CLI).  
3. **Once per project:** `papercut enable` (AGENTS.md **snippet** + **PAPERCUTS.md** log).  
4. Work as usual — agents log mid-task.  
5. Periodically: “fix the papercuts” / `/papercuts`.  
6. Quarterly (or when history is rich): “papercuts kaizen” / `/papercuts-kaizen`.

Agents should **not** reinvent the sand skill in every project. They need:

| Layer | What | Command |
|-------|------|---------|
| **Machine** | Skills + CLI | `papercut install` (papercuts **and** papercuts-kaizen) |
| **Project** | AGENTS snippet + open log + history ledger | `papercut enable` |
---

## Architecture (agnostic)

```
┌─────────────────────────────────────────────────────────┐
│  This package (install once per machine)                │
│    SKILL.md     → sand / fix protocol                   │
│    scripts/papercut → log + install + enable            │
└─────────────────────────────────────────────────────────┘
                         │
          papercut install│  (skill dirs + ~/.local/bin)
                         ▼
┌─────────────────────────────────────────────────────────┐
│  Any project repo                                       │
│    AGENTS.md     ← snippet (papercut enable)            │
│    PAPERCUTS.md  ← append-only sensor (per repo)        │
└─────────────────────────────────────────────────────────┘
```

| Layer | What | Who reads it |
|-------|------|--------------|
| **README.md** | Why, install, human workflow | Humans |
| **AGENTS.md** (this package) | How to install/spread papercuts | Agents in *this* repo |
| **templates/AGENTS.snippet.md** | Drop-in block for *other* repos | Copied into project AGENTS.md |
| **SKILL.md** | Full log + fix protocol | Agents when skill is invoked |
| **PAPERCUTS.md** (per project) | The sanding list | Agents + humans |

**Why not only AGENTS.md in each project?**  
AGENTS.md is great for a short “log when you hit friction” rule. It is a poor place
for the full fix protocol (clustering, gates, anti-patterns). That belongs in a
**skill** so it loads only when someone asks to sand.

**Why not one global PAPERCUTS.md?**  
Friction is usually project-local. Keep the log at the **git root** of each repo.

---

## Install

Requirements: Python 3.9+ (stdlib only).

```bash
git clone <this-repo-url> papercuts
cd papercuts
chmod +x scripts/papercut
./scripts/papercut install
```

This copies the skill into:

- `~/.claude/skills/papercuts` (Claude Code and many Claude-compatible harnesses)  
- `~/.grok/skills/papercuts` (Grok)  

…and symlinks the CLI to `~/.local/bin/papercut` (ensure that dir is on `PATH`).

Optional flags: `--claude`, `--grok`, `--agents` (only one harness).

### Enable in a project (snippet + log)

Installing the skill alone is **not** enough for ambient capture. Each project
also needs two files at the **git root**:

| File | Purpose | How it gets there |
|------|---------|-------------------|
| **AGENTS.md** snippet | Tells agents to log friction mid-task | `papercut enable` |
| **PAPERCUTS.md** | **Open** sanding list (cleared on fix) | `papercut enable` (or `init`) |
| **`.papercuts/history.jsonl`** | **Shadow ledger** (append-only for kaizen) | Created on enable / first log |

```bash
cd /path/to/your-project
papercut enable
papercut status    # expect project_enabled=true
```

**What `enable` writes:**

1. **AGENTS.md** — creates the file or appends a marked block:

```markdown
<!-- papercuts:begin -->
## Log papercuts
… papercut -m <model> "what you were doing → what got in the way" …
<!-- papercuts:end -->
```

   Source template: [`templates/AGENTS.snippet.md`](./templates/AGENTS.snippet.md).  
   Re-run with `papercut enable --force` to refresh the block.

2. **PAPERCUTS.md** — header only until agents log:

```markdown
# PAPERCUTS
Agent-logged friction …
```

   Source template: [`templates/PAPERCUTS.header.md`](./templates/PAPERCUTS.header.md).

It does **not** copy `SKILL.md` into the project. The skill stays machine-global.

If the project only has `CLAUDE.md` (no AGENTS.md):

```bash
papercut enable --prefer-claude
```

**Manual alternative** (if you prefer not to run the CLI): copy the contents of
`templates/AGENTS.snippet.md` into your project `AGENTS.md`, and copy
`templates/PAPERCUTS.header.md` to `PAPERCUTS.md` at the repo root.

**Check anytime:**

```bash
papercut status
# needs_enable=true  → run enable (or ask an agent to set up papercuts)
# project_enabled=true → ready for capture
```

---

## Daily use

**Log (agents, mid-work):**

```bash
papercut -m claude-opus "While running tests, vitest cwd is apps/web so root-relative paths miss."
# also appends event=logged to .papercuts/history.jsonl
```

**Inspect:**

```bash
papercut list
papercut path
papercut history --stats
```

**Clear after a real fix (agents — do not hand-delete):**

```bash
papercut resolve --stamp 2026-07-10T01:21:31.404Z -n "Documented apps/web test cwd in AGENTS.md"
```

Open list shrinks; history keeps the row for long-cycle review.

**Sand (human → agent):**

> Fix the papercuts  
> /papercuts  
> Sand PAPERCUTS.md  

Cluster-first light-causal; clear via `resolve` only when the fix prevents recurrence.

**Long cycle (human → agent):**

> Papercuts kaizen  
> /papercuts-kaizen  
> What friction patterns keep coming back?  

Mines `.papercuts/history.jsonl` for volume, recurrence after “fixed”, and
systemic proposals. Deep RCA only on escalated clusters.

**First time in a repo (human → agent):**

> Set up papercuts here  

The skill will **not** write AGENTS.md / PAPERCUTS.md without your confirmation.

---

## Design constraints we learned

See [`docs/DESIGN.md`](./docs/DESIGN.md) for the full list. Highlights:

1. **Log is a sensor; sanded surface is the product.** Emptying the file without fixes is vanity.  
2. **Cluster-first light-causal**, not per-item 5-Why (kaizen escalates only top patterns).  
3. **Never clear without a preventive change** — and clear via `papercut resolve` so history remains.  
4. **Open list ≠ archive.** Delete-on-fix open list + append-only shadow ledger.  
5. **Promotion (global agent config) is proposal-only** — no silent home-AGENTS edits.  
6. **Do not merge** with issue trackers or skill-ops / eval incident systems.  
7. **Ambient log** + **user-triggered sand** + **rare kaizen** — three cadences.
---

## Repo layout

```
papercuts/
  README.md
  AGENTS.md
  SKILL.md                      # day-to-day sand skill (also skills/papercuts/)
  skills/
    papercuts/SKILL.md
    papercuts-kaizen/SKILL.md   # long-cycle pattern review
  scripts/papercut              # CLI: log, resolve, history, enable, install
  templates/
  docs/
```

---

## License

MIT — see [LICENSE](./LICENSE).
