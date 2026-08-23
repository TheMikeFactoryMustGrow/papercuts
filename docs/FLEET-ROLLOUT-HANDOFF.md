# Fleet rollout session handoff — papercuts + why-first

**Charter (Mike, 2026-08-23, PC-TIMING approved):** a dedicated session that rolls
the standard recipe out across the fleet, one repo at a time, with tests — and
logs every adoption as v1-bar leg-1 evidence for BOTH tools (papercuts CLI and
the pr-template skill). Runs independently of the process-design-plugin
harden-to-v1 session; neither blocks the other.

**Bootstrap prompt for the session:**
> Read docs/FLEET-ROLLOUT-HANDOFF.md in TheMikeFactoryMustGrow/papercuts and run
> the fleet-rollout charter it defines. Create a /goal with the milestones below.
> Deliver via small PRs, one outcome each, submit-when-ready.

## The recipe (ratified — adopt skill Mode 2 step 5)

Per repo: **papercuts-adopt Mode 2 + /pr-template Mode 2 in the same pass, as
separate PRs.** Exception: a knowledge vault gets papercuts only — pr-template's
scope guard applies (flag, don't "fix", a vault).

## Milestones

1. **Inventory** — enumerate all repos (`list_repos` for the account; `fleet.yaml`
   holds the 14 already papercuts-enabled). Classify each: code/tool vs vault vs
   archive-skip. Output: one table, ratified by Mike before any adoption.
2. **Batch 1 (validate the recipe): gym-plan-analyzer, imessage-search,
   beancount, guesty-owners-connect.** One repo at a time; after each, run the
   per-repo test (below) before starting the next. Note: imessage-search and
   beancount are already papercuts-enabled (fleet.yaml, 2026-07-10) — for
   those two, batch 1 means **pr-template Mode 2 + adopt Mode 1 check**
   (snippet currency, registry row), per the milestone-4 rule; only
   gym-plan-analyzer and guesty-owners-connect get the full Mode 2 adoption.
3. **Recipe retro** — after batch 1: did any adoption need a contract change to
   either tool? Contract changes reset the leg-1 clock and go back to the owning
   repo as their own PRs; content fixes are fine.
4. **Full sweep** — remaining code repos from the inventory, same loop. Vaults:
   papercuts-only pass. Already-enabled repos: adopt Mode 1 check (snippet
   currency, fleet.yaml row) instead of Mode 2.
5. **Close** — fleet.yaml complete and accurate; leg-1 evidence summary (N
   adoptions, zero contract changes over the window — or the list of resets);
   handoff note for the fleet-status build session.

## Per-repo test (Done-when, from the adopt skill + pr-template)

- `papercut status` → `project_enabled=true`; snippet matches current template.
- One smoke papercut logged AND resolved in the repo (proves the loop, not just
  the files); entries ride the session's PR.
- fleet.yaml row merged in this repo.
- Code repos: pr-template Mode 2 bar — gap table closed, register lint green on
  real ledger AND red on a seeded defect, adoption PR body uses the template.

## Constraints the session must know

- **Live-tree inventory guard** (pr-template Mode 1, v0.1.2): build every gap
  table from the actual repo tree, never from conversation memory or a
  compaction summary. List a directory before creating anything in it.
- **Submit discipline (R-PR-01)**: draft = still working; flip ready yourself
  when Accept-if passes. **Merge-race guards**: after a post-approval push,
  re-request review; a stacked PR is retargeted to main the moment its base PR
  merges (2026-08-23: occurrence #4 was a stacked PR merging into its
  already-merged base branch).
- **Write channels per repos.yaml** (Linglepedia `_claude_config/repos.yaml`):
  pr-only vs push-master varies by repo — check before pushing.
- **Registry integrity (R-FLEET-01)**: fleet.yaml rows only via adopt with
  enablement verified in-session.
- Every adoption is leg-1 evidence: note the tool versions used (papercut from
  main; pr-template skill version) in each adoption PR body.

## Provenance

Chartered in the papercuts-CI session (session_01Rqzr7FBLS3PsgprA1b9sgK),
decision round 2026-08-23: PC-RECIPE + PC-TIMING approved. Sibling charter:
process-design-plugin `docs/HARDEN-V1-HANDOFF.md` (independent session).
