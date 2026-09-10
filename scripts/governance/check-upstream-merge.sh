#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

# shellcheck disable=SC1091
source governance/upstream-baseline.env
candidate_ref=${1:-"${UPSTREAM_REF}"}
remote_name=governance-upstream

if git remote get-url "$remote_name" >/dev/null 2>&1; then
  git remote set-url "$remote_name" "$UPSTREAM_URL"
else
  git remote add "$remote_name" "$UPSTREAM_URL"
fi
git fetch --no-tags "$remote_name" "$candidate_ref:refs/remotes/${remote_name}/candidate"
candidate="${remote_name}/candidate"
merge_base=$(git merge-base HEAD "$candidate")
report=$(mktemp)
trap 'rm -f "$report"' EXIT

if ! git merge-tree --write-tree HEAD "$candidate" >"$report" 2>&1; then
  cat "$report" >&2
  echo "Upstream merge feasibility check failed for $candidate_ref." >&2
  exit 1
fi

echo "Candidate: $candidate_ref"
echo "Merge base: $merge_base"
echo "Affected files:"
git diff --name-status "$merge_base" "$candidate"
echo "Migration impact:"
git diff --name-status "$merge_base" "$candidate" -- backend/crm/src/main/resources/migration
