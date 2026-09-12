## Purpose

为 Cordys 二开仓库提供可重复验证的数据库升级契约，确保已执行的历史 Migration 保持 checksum 稳定，同时让旧库和全新数据库都能获得后续官方 DDL 修正。

## ADDED Requirements

### Requirement: 已发布 Migration 保持兼容
系统 SHALL 为旧基线数据库保留 `V1.9.1_2__ga_ddl.sql` 的原始内容与 checksum，不得要求对正常旧库执行 Flyway `repair` 才能升级。

#### Scenario: 旧基线数据库执行校验
- **WHEN** 数据库已经成功执行旧基线的全部 Migration，且 `V1.9.1_2` 记录的是旧 checksum
- **THEN** 修复版本的 Migration 校验 MUST 成功，并继续执行尚未应用的新 Migration

### Requirement: 索引通过后续 Migration 交付
系统 SHALL 使用唯一且高于官方基线最高版本的新增 Migration 创建 `sys_operation_log(create_time)` 索引，而不是在已发布脚本中追加 DDL。

#### Scenario: 旧库升级获得索引
- **WHEN** 不含该索引的旧基线数据库迁移到修复版本
- **THEN** 迁移 MUST 成功，且目标表上 MUST 只存在一个预期名称和列定义的索引

#### Scenario: 全新数据库初始化
- **WHEN** 空数据库直接使用修复版本执行全部 Migration
- **THEN** 所有 Migration MUST 成功，历史脚本 checksum MUST 与旧基线一致，且目标索引 MUST 存在

### Requirement: 迁移例外必须精确受控
治理检查 SHALL 默认拒绝修改官方基线中已经存在的 Migration；唯一允许的兼容性恢复 MUST 同时绑定精确路径、官方基线内容摘要和恢复后内容摘要，任一内容漂移都必须失败。

#### Scenario: 未登记或内容漂移
- **WHEN** 官方历史 Migration 被修改但没有精确例外，或其内容摘要不再匹配已登记值
- **THEN** CI Migration 门禁 MUST 失败并指出异常路径

### Requirement: 非预期数据库状态必须停止
升级预检 SHALL 区分旧 checksum、修复后新库状态以及候选改写脚本产生的 checksum，不得自动执行 `repair`、删除索引或篡改 schema history。

#### Scenario: 检测到候选改写 checksum
- **WHEN** 数据库的 `V1.9.1_2` 已记录候选改写后的 checksum
- **THEN** 升级 MUST 停止，并提供备份后专项规范化路径，不得继续自动迁移
