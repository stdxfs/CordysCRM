## Why

官方候选改写了已发布的 `V1.9.1_2__ga_ddl.sql`，导致已经执行旧版本脚本的数据库因 Flyway checksum 不一致而无法启动或继续迁移。需要恢复不可变的历史迁移，并把新增索引作为独立迁移交付，使既有开发库和全新数据库使用同一条可验证的升级路径。

## What Changes

- 将 `V1.9.1_2__ga_ddl.sql` 恢复为旧官方基线中已被执行的内容及 checksum。
- 新增唯一且更高版本的 DDL Migration，创建 `sys_operation_log(create_time)` 索引。
- 为迁移治理检查补充回归覆盖，防止未来上游同步再次静默改写已发布 Migration。
- 在隔离 MySQL 中分别验证旧基线库升级和全新建库，并记录适用范围与回退方式。
- 登记这项必要且可移除的官方文件兼容补丁；不对现有本地或服务器数据库执行 `repair`、重建或自动部署。

## Capabilities

### New Capabilities

- `migration-upgrade-compatibility`: 规定历史 Migration checksum 稳定、索引通过后续版本交付，以及旧库和新库双路径验收要求。

### Modified Capabilities

无。

## Impact

- 影响 `backend/crm` 的 Flyway Migration 资源、治理校验脚本及其测试。
- 不改变应用 API、业务模型或依赖版本。
- 兼容目标是旧基线数据库与修复后的全新数据库；此前由候选 `8221b91c` 临时创建且已记录新 checksum 的数据库不自动修复，必须先识别后按专项步骤处理。
