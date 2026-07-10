# Flow (short)

## Bootstrap (every skill invoke)

```
papercut status
    → needs_enable?
        yes → ask user to enable for future capture
                yes → papercut enable → continue
                no  → continue without snippet (optional init for one-shot log)
        no  → continue
```

## Log path (ambient)

```
friction mid-task
    → real papercut? (not self-error / not experiment noise)
        no  → continue, no log
        yes → papercut "…" → continue task
```

## Fix path (user-triggered)

```
bootstrap (above)
    → locate open log (`papercut path`)
    → empty? stop (empty-ok)
    → load + cluster by shared preventive fix
    → light-causal diagnose + classify (fixable / defer / reclassify / promote)
    → for each fixable cluster:
          smallest preventive fix
          → prevents recurrence?
                yes → papercut resolve --stamp … -n "fix"  (open list + history)
                no  → defer + reason (do not clear)
    → report
    → promote-candidates? propose only (no silent global config edits)
```

## Kaizen path (rare / quarterly)

```
papercut history --stats + history + open list
    → cluster by mechanism over window
    → rank (volume, recurrence after resolve)
    → disposition ladder per top cluster
    → deep RCA only if escalated
    → propose (implement only if asked)
    → report
```

See `SKILL.md` and `skills/papercuts-kaizen/SKILL.md`.