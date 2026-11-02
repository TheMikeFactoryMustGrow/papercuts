#!/usr/bin/env bash
# Behavior tests for scripts/wt.sh (local bare "origin", stubbed gh). Run: bash tests/wt_test.sh
set -euo pipefail
WT="$(cd "$(dirname "$0")/.." && pwd)/scripts/wt.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export WT_ROOT="$T/root" GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
fail(){ echo "FAIL: $*" >&2; exit 1; }
# origin repo with main
git init -q --bare -b main "$T/o/acme/proj.git"
git clone -q "$T/o/acme/proj.git" "$T/seed" 2>/dev/null
git -C "$T/seed" commit -q --allow-empty -m init && git -C "$T/seed" push -q origin HEAD:main
URL="file://$T/o/acme/proj.git"
# gh stub: reports MERGED for branches listed in $T/merged
mkdir -p "$T/bin"; cat > "$T/bin/gh" <<STUB
#!/usr/bin/env bash
for a in "\$@"; do [[ \$prev == --head ]] && br=\$a; prev=\$a; done
grep -qx "\$br" "$T/merged" 2>/dev/null && echo 1 || echo 0
STUB
chmod +x "$T/bin/gh"; export PATH="$T/bin:$PATH"

# 1. one worktree per session
export WT_SESSION=s1
d1=$("$WT" get "$URL" feat-a)
[[ -d "$d1" ]] || fail "get did not create worktree"
[[ "$("$WT" get "$URL" feat-a)" == "$d1" ]] || fail "re-get same branch should reuse"
if "$WT" get "$URL" feat-b 2>/dev/null; then fail "second worktree in same session allowed"; fi
d2=$(WT_SESSION=s2 "$WT" get "$URL" feat-b) || fail "other session blocked"
"$WT" done "$d1"; [[ ! -d "$d1" ]] || fail "clean worktree not removed"
d3=$("$WT" get "$URL" feat-c) || fail "session not released after done"
echo "ok one-worktree-per-session"

# 2. unpushed + not merged -> KEEP
git -C "$d3" commit -q --allow-empty -m work
"$WT" done "$d3"; [[ -d "$d3" ]] || fail "unpushed unmerged worktree removed"
# 3. squash-merged (commits not on origin, but gh says MERGED) -> removed
echo feat-c > "$T/merged"
"$WT" done "$d3"; [[ ! -d "$d3" ]] || fail "squash-merged worktree kept"
git -C "$WT_ROOT/repos/acme__proj.git" show-ref --verify --quiet refs/heads/feat-c && fail "merged branch not deleted"
echo "ok squash-merge-is-done"
grep -q -- '--autostash' "$WT" && grep -v '^#' "$WT" | grep -q -- '--autostash' && fail "wt.sh runs autostash"
echo "ok no-autostash"
echo "wt.sh tests passed"
