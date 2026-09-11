-- Read-only Cordys migration preflight. Pipe batch output to migration_preflight.py.
SELECT
    COALESCE((
        SELECT CAST(checksum AS CHAR)
        FROM cordys_crm_version
        WHERE version = '1.9.1.2'
        ORDER BY installed_rank DESC
        LIMIT 1
    ), 'MISSING') AS historical_checksum,
    COALESCE((
        SELECT CAST(success AS CHAR)
        FROM cordys_crm_version
        WHERE version = '1.9.1.2'
        ORDER BY installed_rank DESC
        LIMIT 1
    ), 'MISSING') AS historical_success,
    COALESCE((
        SELECT CAST(success AS CHAR)
        FROM cordys_crm_version
        WHERE version = '1.9.1.9000'
        ORDER BY installed_rank DESC
        LIMIT 1
    ), 'MISSING') AS compensation_success,
    (
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'sys_operation_log'
          AND index_name = 'idx_create_time'
    ) AS index_columns,
    (
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'sys_operation_log'
          AND index_name = 'idx_create_time'
          AND non_unique = 1
          AND seq_in_index = 1
          AND column_name = 'create_time'
          AND sub_part IS NULL
    ) AS matching_index_columns;
