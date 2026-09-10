# ADR 0002：二开采用扩展优先策略

## Context

未来 ERP、Travel 和外部集成需要与 CordysCRM 上游独立演进。

## Decision

新增需求按配置、扩展点、独立模块、事件、适配器、局部覆盖、官方核心修改的顺序评估。ERP、Travel、Integration 不得无规划进入 `backend/crm`；具体模块在首个领域需求的 OpenSpec 变更中设计。

## Alternatives

直接在 `crm` 中实现业务需求。该方式会增加上游冲突和迁移风险，未采用。

## Consequences

首个领域功能必须同时说明模块边界、权限、审计、状态机、迁移与测试策略。
