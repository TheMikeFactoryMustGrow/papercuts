# Collision avoidance

## Problem

A consumer repo might legitimately use names like `PAPERCUTS.md`, `.papercuts/`,
or a binary called `papercut` for **their product** (e.g. a papercut-themed game).
This package must not overwrite or claim those files.

## Guarantees

| Risk | Mitigation |
|------|------------|
| Root `PAPERCUTS.md` is product content | **Never write** unless file carries ownership marker `<!-- agent-papercuts:v1 -->` |
| `.papercuts/` used by product | Default data dir is **`.agent-papercuts/`** |
| Open log path already foreign | Refuse write; `status` reports `log=foreign` / `foreign_root_PAPERCUTS_md=true` |
| CLI name `papercut` taken | Install also as **`agent-papercut`**; do not overwrite unrelated real files |
| AGENTS.md section clash | Marked block `<!-- agent-papercuts:begin -->…<!-- agent-papercuts:end -->` only |

## Canonical layout (default)

```
.agent-papercuts/
  README.md          # “this is agent tooling, not product”
  open.md            # open sanding list (owned marker in header)
  history.jsonl      # shadow ledger
```

## Ownership marker

Every open log we create starts with:

```html
<!-- agent-papercuts:v1 -->
```

Commands that mutate the open list (`log`, `resolve`, `init --force`) **abort**
if the file exists without this marker (or a recognized legacy owned header).

## Legacy

Older installs that already used owned `PAPERCUTS.md` / `.papercuts/history.jsonl`
are still **read** if ownership checks pass. New `enable` always prefers
`.agent-papercuts/`. `status` may print `legacy_open=…`.

## Overrides (advanced)

```bash
export PAPERCUT_OPEN_PATH=.my-tooling/friction-open.md
export PAPERCUT_HISTORY_PATH=.my-tooling/friction-history.jsonl
```

Paths are relative to the git root unless absolute.

## What we still cannot fully avoid

- **Skill directory names** (`~/.claude/skills/papercuts`) — user-level, not in their repo  
- **PATH name** if both `papercut` and `agent-papercut` are taken as unrelated binaries — install skips clobbering real files  

If both are blocked, run: `python3 /path/to/papercuts/scripts/papercut …`
