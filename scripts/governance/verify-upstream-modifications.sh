#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

# shellcheck disable=SC1091
source governance/upstream-baseline.env
allowlist=governance/upstream-modifications-allowlist.txt
registry=UPSTREAM_MODIFICATIONS.md

git cat-file -e "${UPSTREAM_COMMIT}^{commit}"
test -f "$allowlist"
test -f "$registry"

failures=0
while IFS=$'\t' read -r status path; do
  [[ -n "$status" ]] || continue
  case "$status" in
    M|D)
      if ! grep -Fqx -- "$path" "$allowlist"; then
        echo "Unregistered upstream file change: $status $path" >&2
        failures=1
      fi
      ;;
    R*|C*)
      echo "Renaming or copying an upstream file requires a dedicated review: $status $path" >&2
      failures=1
      ;;
  esac
done < <(git diff --name-status --find-renames "${UPSTREAM_COMMIT}...HEAD")

while IFS= read -r path; do
  [[ -n "$path" && "${path:0:1}" != "#" ]] || continue
  if ! grep -Fq -- "\`$path\`" "$registry"; then
    echo "Allowlisted path is missing from $registry: $path" >&2
    failures=1
  fi
done < "$allowlist"

if (( failures )); then
  exit 1
fi

echo "Upstream modification registration passed for ${UPSTREAM_COMMIT}."
