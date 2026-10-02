# Proposal

## Why

Fork 需要大规模扩展本地表结构，同时持续吸纳官方 Release。现有准则已覆盖「扩展优先」与「历史 Migration 不可改写」，但缺少可执行的本地 Migration 命名约定、表改造优先级与高冲突官方表清单，开发者只能依赖口头建议，无法稳定复用 `V*.9000` 兼容先例。

## What Changes

- 新增「本地 Schema 扩展治理」能力：规定本地 Migration 命名、目录归属、与官方 semver 的边界。
- 规定表改造优先级：新表 / 旁路扩展表 / 自定义表单与配置 → 谨慎 ALTER 官方表；禁止改写历史脚本与危险 DDL。
- 固化高冲突表提示（基于近半年官方 DDL：合同、订单、商机字段表优先旁路）。
- 将上述规则写入项目文档：`docs/adr`、`docs/governance`、根/`backend` `AGENTS.md`，并在 PR 模板中增加数据库扩展自检项。
- 不在本变更中落地具体业务表 DDL；不改 Flyway 运行时配置。

## Capabilities

### New Capabilities

- `local-schema-extension`: 本地 Schema 扩展时的 Migration 命名、表选择优先级、官方同步兼容与文档准入要求。

### Modified Capabilities

无（主规格库尚未归档既有能力；本变更只引入新能力，不改写其他 change 中的 delta）。

## Impact

- 文档与治理指引：`AGENTS.md`、`backend/AGENTS.md`、`docs/adr/`、`docs/governance/`、`.github/PULL_REQUEST_TEMPLATE.md`。
- 不强制立刻改治理脚本；若后续要对 `9xxx` 命名做静态检查，另开变更。
- 不影响现有已发布 Migration 与运行中数据库；新本地 DDL 从当前官方基线（`v1.9.2`）起按新规则追加。
