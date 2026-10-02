# Design

## Context

See `proposal.md` - Why。现有硬约束已由 ADR 0001/0002、`AGENTS.md` 与治理脚本覆盖：官方基线、扩展优先、历史 Migration 不可改写、`9xxx` 仅作为兼容个案出现。本设计把「本地大规模改表 + 持续吃官方更新」落成可执行约定，并映射到文档入口。

当前基线：`governance/upstream-baseline.env` → 官方 `v1.9.2`。Flyway 版本比较按点分数字段排序；目录名必须与文件名前缀一致（见 `scripts/governance/checks.py` 的 `version()`）。

近半年官方 DDL 活跃度（`v1.6.0`–`v1.9.2`）用于冲突提示，不是永久黑名单：合同 / 订单 / 商机字段表改动最多；客户主表无 DDL；线索仅池隐藏字段一处。

## Goals / Non-Goals

**Goals:**

- 给出本地 Migration 的标准命名与目录策略，与官方 semver 解耦。
- 给出表改造决策树与高冲突表清单，降低 upstream-sync 合并成本。
- 把规则写入 ADR + governance 专文 + AGENTS 入口 + PR 模板自检。
- 与既有「历史不可变 / 兼容例外清单 / 补偿 Migration」流程一致。

**Non-Goals:**

- 不在本变更落地任何业务表 DDL。
- 不修改 Flyway `validate-on-migrate` 等运行时开关。
- 不强制本轮就增强 CI 对 `9xxx`/`*_ext` 的静态正则检查（可列为后续可选任务）。
- 不引入第二套平行数据库或独立 Flyway schema。

## Decisions

### D1：本地序号占用 `9000`–`9999`

- **选择**：在**当前官方基线版本目录**下追加 `V<baseline>_<9000-9999>__<desc>.sql`。
- **理由**：与已验证先例 `V1.9.1_9000` 一致；官方同补丁版本内通常只用小序号（`_1`/`_2`）；高序号降低碰撞，且仍小于下一产品小版本（如 `1.10.0.1`）。
- **备选**：自建 `90.x` / `100.x` 产品线 — 否决，易与未来官方大版本冲突，且偏离现有目录习惯。
- **备选**：始终开新目录 `1.9.2.1` — 否决，官方目录为三段式 `x.y.z`，额外段增加门禁与心智负担。

### D2：禁止用「下一个官方版本号」承载纯本地变更

- **选择**：官方未发 `1.10.0` 前，禁止本地独占 `migration/1.10.0/`。
- **理由**：upstream-sync 合并时官方同路径脚本会直接冲突或双写语义。
- **同步后**：基线升到 `1.10.0` 后，**新的**本地脚本写在 `1.10.0/ddl/V1.10.0_9xxx__…`；旧 `1.9.2_9xxx` 保持不可变。

### D3：表改造决策树（强制说明降级理由）

```
1. 新表（建议前缀 xf_ / ext_ / 独立模块表名）
2. 旁路扩展表（<resource>_ext，resource_id 关联）
3. 自定义表单 / sys_module_form* 元数据 / 组织配置
4. 官方表 ADD COLUMN（可空或安全默认）+ 本地索引前缀
5. （禁止）DROP/RENAME/不兼容 MODIFY 官方列；改写历史 SQL
```

独立新领域仍走 ADR 0002：OpenSpec 定义独立模块，不塞进官方 `crm` 包无规划扩张。

### D4：高冲突表提示（文档清单，可随同步修订）

| 风险 | 表示例 | 本地策略 |
|------|--------|----------|
| 高 | `contract*`、`contract_*_field*`、`sales_order*`、`opportunity_field*`、`opportunity_quotation*`、`business_title*`、`*_stage_config` | 默认旁路 |
| 中 | `clue*`、`customer*` 主数据与 field 表 | 优先旁路；禁止破坏性 DDL |
| 低（仍勿改历史） | 纯新建 Fork 表、自定义表单数据表 | 直接本地 `9xxx` |

清单放在 `docs/governance/local-schema-extension.md`，注明「基于观察、随官方同步更新」，不写死进 CI。

### D5：文档分层

| 层级 | 文件 | 作用 |
|------|------|------|
| 长期决策 | `docs/adr/0003-local-schema-extension.md` | 为何采用 9xxx + 旁路优先 |
| 操作手册 | `docs/governance/local-schema-extension.md` | 命名示例、决策树、冲突表、同步步骤 |
| 编码入口 | `AGENTS.md`、`backend/AGENTS.md` | 各 3–6 行摘要 + 链接 |
| 审查 | `.github/PULL_REQUEST_TEMPLATE.md` | 数据库扩展自检一句 |

### D6：与官方同步的操作顺序

1. 本地功能在当前基线 `9xxx` 落地并合并 develop。
2. `upstream-sync`：fetch 官方 Release → merge（保留祖先）→ 阅读 CI 报告的官方 Migration diff。
3. 若官方 ALTER 了本地也改过的表：新增**新基线**下的 `9xxx` reconcile 脚本，不改旧脚本。
4. 更新基线登记；旧库升级仍遵循「代码合并 ≠ 数据库升级」。

### D7：描述性文件名约定

- 推荐：`V1.9.2_9001__fork_customer_ext.sql`、`V1.9.2_9002__fork_reconcile_contract_col.sql`
- `fork_` 前缀便于 diff 与审查识别；非门禁强制，但文档推荐。

## Risks / Trade-offs

- [官方在同版本插入 `_3`…`_8999` 之外的超高序号] → 概率低；若碰撞，由基线检查报重复版本，未部署前改本地序号。
- [旁路表增加 JOIN/查询复杂度] → 用 Service 封装；接受换同步安全。
- [开发者仍直接改官方表] → AGENTS + PR 模板 + OpenSpec 审查；本轮不做强硬 CI。
- [高冲突表清单过时] → 手册写明「同步后按官方 DDL diff 修订」；不绑定版本号永久正确。
- [与 `validate-on-migrate=false` 并存] → 不依赖运行时校验代替治理；历史不可变仍靠脚本门禁。

## Migration Plan

1. 合并本变更文档（无 DDL）。
2. 此后新的本地 Schema PR 按手册执行。
3. 已存在的 `V1.9.1_9000` 保持原样，作为兼容先例引用。
4. 回退：删除/还原新增文档与 AGENTS 段落即可，无数据回滚问题。

## Open Questions

- 是否在后续变更中为 `9xxx` 与禁止占用下一官方版本增加 `scripts/governance` 静态检查：本设计默认「文档先行」，CI 增强另开变更。
