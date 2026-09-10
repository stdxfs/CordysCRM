## Why

当前 Fork 仅比官方上游多一个直接修改官方 Vue 页面的提交，且缺少可验证的登记、分支治理和升级门禁。需要先清除这类业务源码侵入，并把后续二开和官方同步纳入可审计的交付流程。

## What Changes

- 回退现有 DataEase 前端许可绕过，使业务源码恢复到已固定的官方基线。
- 初始化 OpenSpec，并建立上游基线、官方修改登记、ADR、分支治理与 PR 准入规则。
- 新增自动检查：未登记的官方文件修改、历史 Migration 改写、后端 Flyway/Testcontainers 集成测试、前端类型检查与构建、上游合并可行性。
- 建立 Staging、E2E 与回滚的准入清单和手动验证骨架；未接入环境时不得将其视为生产发布验证。
- 修正 Fork 中继承的自动化配置，避免常规 CI 或发布流程使用官方内部仓库、凭据或可变 `latest` 作为发布证据。

## Capabilities

### New Capabilities

- `upstream-safe-governance`: 对上游源码差异、数据库迁移、分支流转和发布验证提供可执行的准入控制。

### Modified Capabilities

- 无。

## Impact

影响 Git 分支与远端配置、GitHub Actions、PR 模板、项目开发指引和 OpenSpec 工件。不会新增 ERP、Travel 或其他业务功能，不改变公开 API、数据库结构或运行时业务行为；DataEase 页面恢复为官方许可行为。
