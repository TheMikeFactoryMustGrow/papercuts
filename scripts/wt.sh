#!/usr/bin/env bash
# wt.sh — shared bare clone per repo + one git worktree per task.
#   wt.sh get <repo-url> <branch>   -> prints worktree path on stdout
#   wt.sh done <path>               -> removes worktree if clean & fully pushed; else keeps + logs
#   wt.sh list                      -> lists all worktrees under WT_ROOT
#   wt.sh session                   -> prints this session's id and its worktree (if any)
# Env: WT_ROOT (default /workspace) -> $WT_ROOT/repos/<key>.git, $WT_ROOT/wt/<key>/<branch>-<id>
#      WT_LOG  (default $WT_ROOT/repos/wt.log)
#      WT_SESSION  session id (default: unix session id of the caller, "sid-<SID>")
#
# Canonical copy: papercuts repo, scripts/wt.sh. Rules: R-GIT-01 (papercuts SKILL.md "Fleet git hygiene").
# R-GIT-01(c): ONE worktree per session. `get` records the worktree in
#   $WT_ROOT/sessions/<session>.wt and refuses a second worktree while that one
#   still exists (re-`get` of the same repo+branch returns the existing path).
#   `done` releases the claim. This script never runs `pull --rebase --autostash`;
#   never do that in a shared working copy either.
# Merged check: `done` treats a branch as pushed/done when commits are reachable
#   from origin OR `gh` reports a MERGED PR from this repo (not a fork) for the branch
#   whose head commit is local HEAD or contains it (covers squash merges; a commit made
#   after the merge, or a reused branch name, is KEPT).
set -euo pipefail
WT_ROOT="${WT_ROOT:-/workspace}"
REPOS="$WT_ROOT/repos"; TREES="$WT_ROOT/wt"
WT_LOG="${WT_LOG:-$REPOS/wt.log}"
SESS_DIR="$WT_ROOT/sessions"
mkdir -p "$REPOS" "$TREES" "$SESS_DIR"
session_id(){ local s="${WT_SESSION:-}"
  if [[ -z "$s" ]]; then s="sid-$(ps -o sid= -p $$ | tr -d ' ')"; fi
  printf '%s' "${s//[^A-Za-z0-9._-]/_}"; }
SESSION="$(session_id)"; SESS_FILE="$SESS_DIR/$SESSION.wt"
# gh_merged <repo-url> <branch> <gitdir> <worktree> -> 0 only if a MERGED PR from this repo's own
#   branch (not a fork with the same name) has a head commit equal to, or descending from, local HEAD.
#   Branch-name match alone is not enough: a reused name or a commit made after the merge must be KEPT.
gh_merged(){ local u="${1%.git}" slug owner head line o oid num; u="${u#*://}"; u="${u#*@}"; u="${u/:/\/}"; slug="${u#*/}"
  owner=$(key_for "$1"); owner="${owner%%__*}"; owner="${owner,,}"
  command -v gh >/dev/null 2>&1 || return 1
  head=$(git -C "$4" rev-parse HEAD) || return 1
  local out; out=$(gh pr list --repo "$slug" --head "$2" --state merged --limit 100 \
    --json number,headRefOid,headRepositoryOwner \
    -q '.[] | "\(.headRepositoryOwner.login) \(.headRefOid) \(.number)"' 2>/dev/null) || return 1
  while read -r o oid num; do
    [[ -n "$oid" && "${o,,}" == "$owner" ]] || continue
    [[ "$oid" == "$head" ]] && return 0
    git -C "$3" cat-file -e "$oid^{commit}" 2>/dev/null || git -C "$3" fetch --quiet origin "refs/pull/$num/head" 2>/dev/null || true
    git -C "$3" merge-base --is-ancestor "$head" "$oid" 2>/dev/null && return 0
  done <<<"$out"
  return 1; }
log(){ printf '%s %s %s\n' "$(date '+%F %T %Z')" "${AGENT_NAME:-$(whoami)}" "$*" >>"$WT_LOG"; echo "wt: $*" >&2; }
die(){ log "ERROR $*"; exit 1; }
key_for(){ local u="${1%.git}"; u="${u%/}"; u="${u#*://}"; u="${u#*@}"; u="${u/:/\/}"
  local repo="${u##*/}"; local rest="${u%/*}"; local owner="${rest##*/}"; echo "${owner}__${repo}"; }
locked(){ local lock="$1"; shift; exec 9>"$lock"; flock -w 600 9 || die "lock timeout $lock"; "$@"; local rc=$?; exec 9>&-; return $rc; }

ensure_repo(){ # $1 url $2 gitdir
  if [[ ! -d "$2" ]]; then
    git clone --bare --quiet "$1" "$2.tmp.$$" && mv "$2.tmp.$$" "$2"
    git -C "$2" config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
    git -C "$2" config core.logAllRefUpdates true
    git -C "$2" for-each-ref --format='%(refname)' refs/heads | while read -r r; do git -C "$2" update-ref -d "$r"; done
  fi
  git -C "$2" fetch --quiet --prune origin
  git -C "$2" remote set-head origin --auto >/dev/null 2>&1 || true
}

cmd_get(){
  local url="$1" br="$2" key gd dir id
  key=$(key_for "$url"); gd="$REPOS/$key.git"
  if [[ -f "$SESS_FILE" ]]; then
    local cur curkey curbr; read -r cur curkey curbr < "$SESS_FILE" || true
    if [[ -n "$cur" && -d "$cur" ]]; then
      if [[ "$curkey" == "$key" && "$curbr" == "$br" ]]; then log "REUSE session=$SESSION $cur"; echo "$cur"; return 0; fi
      die "refusing: session $SESSION already has worktree $cur ($curkey $curbr); run 'wt.sh done $cur' first (R-GIT-01 c)"
    fi
    rm -f "$SESS_FILE"
  fi
  id="$(date +%m%d%H%M%S)-$$-$RANDOM"
  dir="$TREES/$key/${br//\//_}-$id"; mkdir -p "$TREES/$key"
  _get(){
    ensure_repo "$url" "$gd"
    git -C "$gd" worktree prune
    if git -C "$gd" show-ref --verify --quiet "refs/heads/$br"; then
      if git -C "$gd" worktree list --porcelain | grep -qx "branch refs/heads/$br"; then
        log "WARN branch $br already checked out in another worktree; detached at origin/$br"
        git -C "$gd" worktree add --quiet --detach "$dir" "origin/$br" >&2
      else
        git -C "$gd" worktree add --quiet "$dir" "$br" >&2
      fi
    elif git -C "$gd" show-ref --verify --quiet "refs/remotes/origin/$br"; then
      git -C "$gd" worktree add --quiet --track -b "$br" "$dir" "origin/$br" >&2
    else
      local base; base=$(git -C "$gd" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)
      git -C "$gd" worktree add --quiet --no-track -b "$br" "$dir" "$base" >&2
    fi
  }
  locked "$gd.lock" _get || die "get failed $url $br"
  printf '%s %s %s\n' "$dir" "$key" "$br" > "$SESS_FILE"
  log "GET session=$SESSION $key $br -> $dir"
  echo "$dir"
}

cmd_done(){
  local p; p=$(cd "$1" 2>/dev/null && pwd -P) || die "no such path $1"
  local gd; gd=$(git -C "$p" rev-parse --path-format=absolute --git-common-dir 2>/dev/null) || die "not a git worktree: $p"
  [[ "$gd" == "$(cd "$REPOS" && pwd -P)"/* ]] || die "refusing: $p is not managed by wt.sh (common dir $gd)"
  [[ "$(git -C "$p" rev-parse --show-toplevel)" == "$p" ]] || die "refusing: pass the worktree root, not a subdir"
  _done(){
    git -C "$gd" fetch --quiet --prune origin || { log "KEEP $p reason=fetch-failed (cannot prove pushed)"; return 0; }
    local dirty unpushed br merged=0 url
    url=$(git -C "$gd" config --get remote.origin.url || true)
    br=$(git -C "$p" symbolic-ref --quiet --short HEAD || true)
    dirty=$(git -C "$p" status --porcelain --untracked-files=all --ignored=no | head -5)
    if [[ -n "$dirty" ]]; then log "KEEP $p reason=dirty files: $(echo "$dirty" | tr '\n' ' ')"; return 0; fi
    unpushed=$(git -C "$p" rev-list --count HEAD --not --remotes=origin)
    if [[ "$unpushed" != 0 ]]; then
      if [[ -n "$br" ]] && gh_merged "$url" "$br" "$gd" "$p"; then merged=1; log "MERGED $p branch=$br (PR merged per gh; unreachable commits=$unpushed, e.g. squash)"
      else log "KEEP $p reason=unpushed commits=$unpushed"; return 0; fi
    fi
    git -C "$gd" worktree remove "$p"
    git -C "$gd" worktree prune
    if [[ -n "$br" ]] && { [[ $merged == 1 ]] || [[ $(git -C "$gd" rev-list --count "refs/heads/$br" --not --remotes=origin) == 0 ]]; }; then
      git -C "$gd" branch -D --quiet "$br" >/dev/null || true
    fi
    release_session "$p"
    log "REMOVED $p branch=${br:-detached}"
  }
  locked "$gd.lock" _done
}

release_session(){ local f cur; for f in "$SESS_DIR"/*.wt; do [[ -f "$f" ]] || continue
  read -r cur _ < "$f" || true; [[ "$cur" == "$1" ]] && rm -f "$f"; done; return 0; }
cmd_session(){ echo "session=$SESSION"; [[ -f "$SESS_FILE" ]] && cat "$SESS_FILE" || true; }
cmd_list(){ for gd in "$REPOS"/*.git; do [[ -d "$gd" ]] && git -C "$gd" worktree list; done; }

case "${1:-}" in
  get)  [[ $# -eq 3 ]] || die "usage: wt.sh get <repo-url> <branch>"; cmd_get "$2" "$3";;
  done) [[ $# -eq 2 ]] || die "usage: wt.sh done <path>"; cmd_done "$2";;
  list) cmd_list;;
  session) cmd_session;;
  *) echo "usage: wt.sh get <repo-url> <branch> | done <path> | list | session" >&2; exit 2;;
esac
