<!--
  Agents and humans: fill every section that applies.
  Reviewers evaluate the *reasoning*, not only the diff.
-->

## Summary

<!-- 1–3 bullets: what changed in concrete terms -->

-

## Problem / opportunity

<!-- What was wrong, missing, or costly *before* this PR? Who felt it? -->



## First principles

<!--
  Why this change is correct *in principle*:
  - Fitness: friction gets logged in the moment and later sanded — capture cost near zero, no collisions with product files
  - Hard rules live in REQUIREMENTS.md with author + why — docs cite IDs
  - CLI stays Python stdlib only; consumer surface stays tiny (snippet + .agent-papercuts/)
  - Bias to delete (docs/DESIGN.md) before adding steps
-->

| Principle | How this PR honors it |
| --- | --- |
| | |
| | |

### Alternatives considered

<!-- What we could have done instead, and why we rejected it. "None" if trivial. -->

-

### Non-goals

<!-- What this PR deliberately does *not* change. -->

-

## How to evaluate this update

**Accept if:**

- [ ]
- [ ]

**Reject / send back if:**

- [ ]

**Manual / scripted checks run:**

```text
# commands run + results
```

## Impact surface

- [ ] `papercut` CLI (`scripts/papercut` — skill copies are symlinks to it)
- [ ] Skills (`SKILL.md`, `skills/papercuts/`, `skills/papercuts-kaizen/`)
- [ ] Templates (`templates/` — AGENTS snippet is mirrored inline in the CLI; CI guards parity)
- [ ] Hard-rule register (`REQUIREMENTS.md`)
- [ ] CI / repo hygiene only
- [ ] Docs only

**Blast radius (one line):**


## Version

<!-- No version home yet; this repo ships from main. Tick the first box unless that changes. -->

- [ ] No versioned content → **no bump**

## Risk & rollback

**Risk level:** Low / Medium / High

**If this is wrong, rollback is:**



## Test plan

<!-- CI runs syntax + snippet parity + behavior smoke + regressions; list anything beyond that. -->

- [ ]

---

### Agent notes (optional)

<!-- Handoff: open questions, follow-ups, files deliberately left alone -->
