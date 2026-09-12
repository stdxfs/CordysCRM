-- Preserve V1.9.1_2 checksum compatibility and deliver the upstream index separately.
SET @cordys_index_count = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'sys_operation_log'
      AND index_name = 'idx_create_time'
);

SET @cordys_index_matches = (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'sys_operation_log'
      AND index_name = 'idx_create_time'
      AND non_unique = 1
      AND seq_in_index = 1
      AND column_name = 'create_time'
      AND sub_part IS NULL
);

SET @cordys_index_sql = CASE
    WHEN @cordys_index_count = 0 THEN
        'CREATE INDEX idx_create_time ON sys_operation_log (create_time)'
    WHEN @cordys_index_count = 1 AND @cordys_index_matches = 1 THEN
        'SELECT 1'
    ELSE
        'CREATE INDEX idx_create_time ON sys_operation_log (create_time)'
END;

PREPARE cordys_index_statement FROM @cordys_index_sql;
EXECUTE cordys_index_statement;
DEALLOCATE PREPARE cordys_index_statement;
