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

No `papercut` on PATH? One-time machine install (CLI → `~/.local/bin`):
`git clone https://github.com/TheMikeFactoryMustGrow/papercuts && papercuts/scripts/papercut install`
Cannot install (restricted machine, cloud container)? The format is the tool — append by hand:
if `.agent-papercuts/open.md` does not exist, start it with the ownership marker line
`<!-- agent-papercuts:v1 -->` (without it the CLI treats the file as foreign and refuses it later);
then append `<UTC ISO-8601 stamp> - <model> - <author>`, a blank line, a one-paragraph body.
`.agent-papercuts/history.jsonl` gets ONE physical line per entry —
`{"event": "logged", "entry_stamp": "<stamp>", "model": "…", "author": "…", "body": "…", "ts": "<stamp>", "repo_root": "<abs git root>"}`
— string values JSON-escaped (quotes, backslashes, newlines), or the line silently drops from history views.
<!-- agent-papercuts:end -->
