#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
exec python3 scripts/governance/checks.py migrations "${1:-${GOVERNANCE_BASE_SHA:-HEAD^}}" "${2:-committed}"
