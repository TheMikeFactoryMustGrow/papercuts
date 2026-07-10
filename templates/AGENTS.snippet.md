<!-- papercuts:begin -->
## Log papercuts

When you hit **small friction** while working — a tool call that missed and had
to be retried, a confusing or undocumented setup step, a flaky command, a stale
cache, a misleading error, a non-obvious gotcha — log it to this repo's
`PAPERCUTS.md` via:

```bash
papercut -m <model> "one or two sentences: what you were doing → what got in the way"
```

Do this **proactively, in the moment**, even when none of these are blocking —
together they show where the repo needs sanding. Distinct from git history
(what shipped) and from issue trackers (real bugs / tracked work).

To sand later: use the **papercuts** skill, or ask to "fix the papercuts" /
"sand PAPERCUTS.md". Analysis is **cluster-first light-causal** (not formal
RCA per item). If `papercut` is missing from PATH, run the installed skill
script or see the papercuts package README.
<!-- papercuts:end -->
