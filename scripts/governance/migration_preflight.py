#!/usr/bin/env python3
"""Classify the tab-separated output of migration-preflight.sql without changing a database."""
import sys


PUBLISHED_CHECKSUM = "1138237749"
CANDIDATE_CHECKSUM = "-1994966056"


def assess(historical_checksum, historical_success, compensation_success, index_columns, matching_columns):
    if historical_success != "1":
        return "BLOCK_FAILED_HISTORY", "V1.9.1.2 is missing or unsuccessful"
    if historical_checksum == CANDIDATE_CHECKSUM:
        return "BLOCK_CANDIDATE_CHECKSUM", "database was initialized with the rewritten candidate migration"
    if historical_checksum != PUBLISHED_CHECKSUM:
        return "BLOCK_UNKNOWN_CHECKSUM", "V1.9.1.2 checksum is not an approved value"
    try:
        index_count = int(index_columns)
        matching_count = int(matching_columns)
    except ValueError:
        return "BLOCK_INVALID_RESULT", "index metadata is not numeric"
    if index_count not in (0, 1) or matching_count != index_count:
        return "BLOCK_INDEX_CONFLICT", "idx_create_time has an unexpected definition"
    if compensation_success == "MISSING":
        return "READY_UPGRADE", "published checksum is valid and compensation migration is pending"
    if compensation_success != "1":
        return "BLOCK_FAILED_COMPENSATION", "V1.9.1.9000 exists but is unsuccessful"
    if index_count != 1:
        return "BLOCK_MISSING_INDEX", "compensation migration is recorded but the expected index is missing"
    return "READY_CURRENT", "checksum, compensation migration and index are consistent"


def main():
    fields = sys.stdin.read().strip().split("\t")
    if len(fields) != 5:
        print("BLOCK_INVALID_RESULT: expected five tab-separated values", file=sys.stderr)
        return 2
    status, detail = assess(*fields)
    print(status + ": " + detail)
    return 0 if status.startswith("READY_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
