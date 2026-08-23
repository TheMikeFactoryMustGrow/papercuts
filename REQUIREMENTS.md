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
