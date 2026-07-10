# papercuts

**Give coding agents a way to log tiny friction — then sand it later.**

Agents constantly hit dead-end tool calls, broken docs, flaky commands, and
gotchas. They usually push through without saying anything. Papercuts makes
that friction visible and fixable.

Inspired by [Steve Ruiz](https://x.com/steveruizok/status/2075303919664734295).

| Audience | Read this |
|----------|-----------|
| **Humans** | this README |
| **Agents opening this repo** | [`AGENTS.md`](./AGENTS.md) |
| **Agents fixing a project’s log** | installed skill [`SKILL.md`](./SKILL.md) |

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
2. Once per machine: `./scripts/papercut install` (or ask an agent: “install papercuts from this repo”).  
3. Once per project: `papercut enable` (adds a short AGENTS.md block + empty `PAPERCUTS.md`).  
4. Work as usual — agents log mid-task.  
5. Periodically: “fix the papercuts” / `/papercuts`.

Agents should **not** reinvent the sand skill in every project. They only need:

- **Project:** short AGENTS.md snippet (permission to complain + how to log)  
- **Machine:** skill + CLI (how to sand)

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

### Enable in a project

```bash
cd /path/to/your-project
papercut enable
```

Creates/updates `AGENTS.md` (marked block) and `PAPERCUTS.md`.

If the project only has `CLAUDE.md`:

```bash
papercut enable --prefer-claude
```

---

## Daily use

**Log (agents, mid-work):**

```bash
papercut -m claude-opus "While running tests, vitest cwd is apps/web so root-relative paths miss."
```

**Inspect:**

```bash
papercut list
papercut path
```

**Sand (human → agent):**

> Fix the papercuts  
> /papercuts  
> Sand PAPERCUTS.md  

The skill clusters related entries, applies the **smallest preventive fix**, and
clears only what actually prevents recurrence. It does **not** run formal RCA on
every line by default.

---

## Design constraints we learned

See [`docs/DESIGN.md`](./docs/DESIGN.md) for the full list. Highlights:

1. **Log is a sensor; sanded surface is the product.** Emptying the file without fixes is vanity.  
2. **Cluster-first light-causal**, not per-item 5-Why.  
3. **Never clear without a preventive change** (or explicit noise reclassify).  
4. **Promotion (global agent config) is proposal-only** — no silent home-AGENTS edits.  
5. **Do not merge** with issue trackers or skill-ops / eval incident systems.  
6. **Ambient log** (AGENTS.md) + **user-triggered fix** (skill) — not unprompted session mining.

---

## Repo layout

```
papercuts/
  README.md                 # humans
  AGENTS.md                 # agents working on / installing this package
  SKILL.md                  # skill body (installed to harness skill dirs)
  LICENSE
  scripts/papercut          # CLI
  templates/
    AGENTS.snippet.md       # block for consumer projects
    PAPERCUTS.header.md
  docs/
    DESIGN.md               # constraints & architecture decisions
    FLOW.md                 # log + fix paths (short)
```

---

## License

MIT — see [LICENSE](./LICENSE).
