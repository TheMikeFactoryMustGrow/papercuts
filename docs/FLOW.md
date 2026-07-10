# Flow (short)

## Log path (ambient)

```
friction mid-task
    → real papercut? (not self-error / not experiment noise)
        no  → continue, no log
        yes → papercut "…" → continue task
```

## Fix path (user-triggered)

```
locate PAPERCUTS.md
    → empty? stop (empty-ok)
    → load + cluster by shared preventive fix
    → light-causal diagnose + classify (fixable / defer / reclassify / promote)
    → for each fixable cluster:
          smallest preventive fix
          → prevents recurrence?
                yes → clear cluster from log
                no  → defer + reason (do not clear)
    → report
    → promote-candidates? propose only (no silent global config edits)
```

See `SKILL.md` for the full protocol.
