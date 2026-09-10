# 上游同步流程

`upstream` 固定为官方 CordysCRM，`origin` 固定为公司 Fork。`upstream` 仅用于 fetch；本地 push URL 必须失效。

```text
official release / tag
        ↓
upstream-sync
        ↓  (build, migration, integration review)
develop
        ↓  (staging and release checks)
release/*
        ↓
main
```

## 分支规则

- `main` 是生产稳定分支，只能通过 PR 合并，必须通过治理门禁。
- `develop` 是日常集成分支。
- `upstream-sync` 专用于引入官方 ref；不能承载业务功能。
- `feature/*`、`fix/*` 从 `develop` 创建；`release/*` 从 `develop` 创建。
- 生产修复从 `main` 创建并回合 `develop`。

## 同步步骤

1. 记录官方 Release/Tag、commit SHA、Release Notes 和候选镜像 digest。
2. 在 `upstream-sync` 获取候选 ref，运行 `scripts/governance/check-upstream-merge.sh <ref>`。
3. 审查文件、Migration、权限、框架、API 和前端组件影响，禁止用 Flyway repair 掩盖校验差异。
4. 运行治理门禁；通过后以 `upstream-sync -> develop` PR 合并。
5. 完成 Staging、E2E、升级与回滚证据后，按 release 流程进入 `main`。

更新 `governance/upstream-baseline.env` 是单独的上游同步 PR 行为，必须同时更新修改登记和验证证据。
