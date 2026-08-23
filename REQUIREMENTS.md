# REQUIREMENTS — hard-rule register

**Fitness metric:** friction gets logged in the moment and later sanded — capture cost near zero, zero collisions with product files.

Every hard rule is one row: id, requirement, named author, one-sentence why, enforcement. Rule docs cite IDs; they do not restate this register. Hard-rule changes update this register **in the same change**.

| ID | Requirement | Author | Why | Enforcement |
|----|-------------|--------|-----|-------------|
| R-CLI-01 | The `papercut` CLI is Python stdlib only — no pip installs, no node | Mike (AGENTS.md, repo inception) | Consumers install with one clone on any machine; zero dependency surface | CI runs everything on stock runner Python; review |
| R-CLI-02 | Data lives under `.agent-papercuts/`, never a root `PAPERCUTS.md` or foreign file without the ownership marker | Mike (docs/COLLISIONS.md) | A product file with the same name must never be claimed or clobbered | CLI ownership-marker checks; CI behavior smoke |
| R-CLI-03 | The inline `AGENTS_SNIPPET` constant stays byte-identical (between markers) to `templates/AGENTS.snippet.md` | Mike (2026-08-22 drift finding, PR #3) | Two copies of the snippet exist by design (template + no-template fallback); silent drift ships two different contracts | CI snippet-parity check, both paths |
| R-SCOPE-01 | Ambient "log friction mid-task" guidance goes in **project** AGENTS.md only — home/global briefs carry a pointer at most | Mike (docs/HOME-VS-REPO.md) | Global ambient capture pollutes unrelated repos and non-consenting projects | Review; install-prompt wording |
| R-PR-01 | Draft = still working; ready-for-review = the done-signal, flipped by the authoring session the moment Accept-if checks pass — never left to Mike | Mike (fleet ruling 2026-08-09; re-affirmed 2026-08-22) | Review routines consume only non-draft PRs; ready work parked in draft is invisible and stalls | Session PR-state check at every turn end |
| R-FLEET-01 | `fleet.yaml` rows accumulate only through papercuts-adopt with enablement verified in-session; fleet-status reads the registry, never edits it | Mike (ruling 2026-08-23, fleet-status design pass) | A registry that drifts from reality makes the liveness eval sweep the wrong repos and miss silent ones | papercuts-adopt skill Mode 2; review |
| R-SKILL-01 | Every `skills/*/SKILL.md` carries the six contract elements: when-to-use, inputs-and-access, sequence, validation, return, approval-gates | Mike (six-element standard, ratified for this repo 2026-08-23) | A skill missing its contract surface fails unpredictably across runtimes; hand audits found three gaps the day this rule landed | CI skill-lint step |
| R-SKILL-02 | Root `SKILL.md` stays byte-identical to `skills/papercuts/SKILL.md` | Mike (ruling 2026-08-23, MOC/RCA review) | The root copy is an unguarded duplicate — drift ships two versions of the sand protocol under one name | CI `cmp` in skill-lint step |
| R-REG-01 | This register stays well-formed: fitness metric present, every row has 5 non-empty cells (id/requirement/author/why/enforcement), IDs unique | Mike (ruling 2026-08-23, "CI to help enforce it") | An unlintable register silently stops being the source of truth that Phase-1 requirement analysis depends on | CI register-lint step |
