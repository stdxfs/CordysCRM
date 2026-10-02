-- Remove the tender module, its role permissions and third-party config.
-- The 1.4.0 scripts stay unchanged so already-applied checksums remain valid.

SET SESSION innodb_lock_wait_timeout = 7200;

DELETE FROM sys_role_permission WHERE permission_id = 'TENDER:READ';

DELETE FROM sys_module WHERE module_key = 'tender';

DELETE FROM sys_organization_config_detail WHERE type = 'TENDER';

SET SESSION innodb_lock_wait_timeout = DEFAULT;
