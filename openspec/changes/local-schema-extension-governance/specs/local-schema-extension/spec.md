# Spec Delta

## Purpose

规范本 Fork 在持续同步官方 Release 的前提下，如何命名本地 Migration、优先扩展哪些表，以及文档与 PR 准入如何约束大规模本地 Schema 变更。

## ADDED Requirements

### Requirement: Local Migration version naming
系统 SHALL 要求新增的本地 Schema Migration 使用「当前官方基线产品版本目录 + 高序号序列」命名，且 MUST NOT 占用尚未发布的官方 semver 作为本地产品版本号。

#### Scenario: Append local DDL under current baseline
- **WHEN** 开发者在官方基线为 `v1.9.2` 时新增本地 DDL
- **THEN** 脚本路径符合 `backend/crm/src/main/resources/migration/1.9.2/(ddl|dml)/V1.9.2_<seq>__<desc>.sql`，且 `<seq>` 落在保留给本地补丁的高序号区间（`9000`–`9999`）

#### Scenario: Reject inventing next official version for local work
- **WHEN** 提案或 PR 使用尚未由官方发布的版本目录（例如官方仍为 `1.9.2` 时使用 `1.10.0`）承载纯本地 Schema
- **THEN** 变更被视为不合规，文档与审查要求改回当前基线高序号或独立旁路方案

#### Scenario: After upstream sync use new baseline folder
- **WHEN** 官方基线已推进到更高版本（例如 `v1.10.0`）且需继续追加本地 Schema
- **THEN** 新本地脚本放在新基线版本目录下的 `9xxx` 序号，MUST NOT 回填改写旧版本目录中已发布文件

### Requirement: Published migrations remain immutable
系统 SHALL 保持已发布 Migration 文件内容不可变；本地修复或官方冲突补偿 MUST 通过新增更高序号脚本交付，仅在已登记的兼容例外清单允许时恢复历史文件原文。

#### Scenario: Compensation instead of rewrite
- **WHEN** 需要在已执行的官方脚本之上补交索引或列
- **THEN** 使用同版本目录下新的 `9xxx` 补偿 Migration，而不是修改原 `V*_1` / `V*_2` 文件内容（除非走已批准的 checksum 兼容例外流程）

### Requirement: Table change preference order
系统 SHALL 要求本地 Schema 扩展按以下优先级选型，且 PR/OpenSpec MUST 说明为何未采用更高优先级方案：新表（Fork 前缀）→ 旁路扩展表（`*_ext` 等，按业务主键关联）→ 自定义表单/模块表单元数据/组织配置 → 对官方表的兼容性 ALTER。

#### Scenario: Prefer side table over core ALTER
- **WHEN** 需求要为客户增加大量本地字段
- **THEN** 默认新建旁路表（例如 `customer_ext`）或自定义表单承载，而不是直接大量 `ALTER TABLE customer`

#### Scenario: Document downgrade justification
- **WHEN** PR 选择直接 ALTER 官方核心表
- **THEN** 说明中 MUST 写明更高优先级方案不可行的原因，以及上游同步冲突时的补偿策略

### Requirement: High-churn official tables guidance
系统 SHALL 将合同、订单、商机相关高频变更表标为高冲突风险，并要求本地大规模扩展优先旁路；线索、客户主表虽近期官方 DDL 较少，仍 MUST 优先旁路而非改列类型或删除列。

#### Scenario: Contract field extension
- **WHEN** 本地需要扩展合同发票/回款字段存储
- **THEN** 优先旁路表或自定义表单，避免与官方对 `contract_*_field*` 的子表行列改造直接冲突

### Requirement: Allowed and forbidden DDL on official tables
当必须修改官方表时，系统 SHALL 仅允许可空或带安全默认值的 `ADD COLUMN`、以及使用本地命名前缀的新增索引；MUST NOT 对官方拥有的列执行 `DROP`/`RENAME`/不兼容类型变更，MUST NOT 改写历史 Migration。

#### Scenario: Safe additive column
- **WHEN** 经论证必须在官方表增加本地列
- **THEN** 列可为空或提供安全默认值，脚本尽量幂等，索引名使用本地可识别前缀（如 `idx_fork_`）

#### Scenario: Forbidden destructive change
- **WHEN** 变更包含删除官方列、重命名官方列或不兼容修改官方列类型
- **THEN** 该方案被拒绝，须改为旁路表或独立模块表

### Requirement: Documentation and review gates
系统 SHALL 在项目开发准则、ADR 与治理文档中收录本能力；涉及大规模本地 Schema 或跨模块表扩展的变更 MUST 附 OpenSpec（或引用本能力文档），并在 PR 中声明数据库影响。

#### Scenario: AGENTS entry points updated
- **WHEN** 本变更完成实施
- **THEN** 根目录与 `backend/AGENTS.md` 指向本地 Schema 扩展规则，且存在可阅读的 ADR 与 `docs/governance` 操作说明

#### Scenario: PR calls out schema impact
- **WHEN** PR 新增本地 `9xxx` Migration 或旁路表
- **THEN** PR 模板中的数据库影响项被填写，而非标为无关时却实际改库
