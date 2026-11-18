<!-- agent-papercuts:begin -->
## Log agent papercuts

When you hit **small friction** while working — a tool call that missed and had
to be retried, a confusing or undocumented setup step, a flaky command, a stale
cache, a misleading error, a non-obvious gotcha — log it via:

```bash
papercut -m <model> \
  --goal "<what you were trying to do, and why>" \
  --attempted "<tool or command and its inputs; redact secrets>" \
  --happened "<the error or the wrong result>" \
  --workaround "<what you did instead, or none>" \
  --proposed-fix "<the change you think would fix it>"
```

Every field is required. If you cannot fill one, use `unknown — <reason>` so
logging is never blocked. These fields improve later feedback; they do **not**
gate fixing already-open items. `papercut check` reports thin entries and
always exits 0. Resolve and sand as usual.

Data lives under **`.agent-papercuts/`** (open list + history), not a root
`PAPERCUTS.md`, so it does not collide with product files. Do this
**proactively, in the moment**.

Entries are repo files: **commit them, and they ride the session's PR** —
include `.agent-papercuts/` changes in the branch you push. An entry logged in
an ephemeral container but never pushed is lost with the container.

Sand: skill **papercuts** ("fix the papercuts"). Clear with `papercut resolve`
(not hand-delete). Long cycle: **papercuts-kaizen**.

No `papercut` on PATH? One-time machine install (CLI → `~/.local/bin`):
`git clone https://github.com/TheMikeFactoryMustGrow/papercuts && papercuts/scripts/papercut install`

Cannot install (restricted machine, cloud container)? The format is the tool — append by hand:
if `.agent-papercuts/open.md` does not exist, start it with the ownership marker line
`<!-- agent-papercuts:v1 -->` (without it the CLI treats the file as foreign and refuses it later);
then append `<UTC ISO-8601 stamp> - <model> - <author>`, a blank line, and the five fields
(`goal`, `attempted`, `happened`, `workaround`, `proposed_fix`) as `field: value` lines
(`<model>` and `<author>` are single tokens, no spaces — `jane-doe`, not `Jane Doe`).
`.agent-papercuts/history.jsonl` gets ONE physical line per entry —
`{"event": "logged", "entry_stamp": "<stamp>", "model": "…", "author": "…", "body": "…", "ts": "<stamp>", "repo_root": "<abs git root>"}`
— string values JSON-escaped (quotes, backslashes, newlines), or the line silently drops from history views.

No shell and no file write either (plain chat surface)? Do not drop the papercut:
state it verbatim in your reply, flagged `PAPERCUT:`, so the user or a shelled
session can log it properly later.
<!-- agent-papercuts:end -->
