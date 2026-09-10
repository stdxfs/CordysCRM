#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

base_ref=${1:-${GOVERNANCE_BASE_SHA:-HEAD^}}
migration_root=backend/crm/src/main/resources/migration
git rev-parse --verify "${base_ref}^{commit}" >/dev/null

failures=0
while IFS=$'\t' read -r status path; do
  [[ -n "$status" ]] || continue
  case "$status" in
    M|D|R*|C*)
      echo "Published migration files are immutable: $status $path" >&2
      failures=1
      ;;
    A)
      if [[ ! "$path" =~ ^backend/crm/src/main/resources/migration/([0-9]+(\.[0-9]+)*)/(ddl|dml)/V([0-9]+(\.[0-9]+)*)_[0-9][0-9_]*__.+\.sql$ ]]; then
        echo "Invalid migration path or filename: $path" >&2
        failures=1
        continue
      fi
      directory_version=${BASH_REMATCH[1]}
      filename_version=${BASH_REMATCH[4]}
      if [[ "$directory_version" != "$filename_version" ]]; then
        echo "Migration directory and filename versions differ: $path" >&2
        failures=1
      fi
      if git ls-tree -r --name-only "$base_ref" -- "$migration_root/$directory_version/" | grep -q .; then
        echo "New migration cannot be added to an existing baseline version directory: $path" >&2
        failures=1
      fi
      ;;
    *)
      echo "Unsupported migration change status: $status $path" >&2
      failures=1
      ;;
  esac
done < <(git diff --name-status --find-renames "${base_ref}...HEAD" -- "$migration_root")

if (( failures )); then
  exit 1
fi

echo "Migration immutability and naming checks passed against $base_ref."
