# 上游修改登记

基线：`1Panel-dev/CordysCRM` 的 `a0ef69d31fd98c338199579353840f34ef679197`（`v1.9.1` / `main`，2026-09-12）。此前基线为 `8221b91c9f665d401b48353a4bbf48a33b1e3d3e`。

本次官方自身改写 1.9.1.2 迁移以新增日志索引。本 Fork 将该历史脚本恢复为此前已发布内容，并通过新的补偿 Migration 交付索引，以兼容旧库 checksum。不会自动升级已有本地或服务器数据库。详见 docs/governance/upstream-8221-validation.md。

规则：修改、删除或重命名该基线中存在的官方文件前，必须先更新本文件和 `governance/upstream-modifications-allowlist.txt`。业务源码必须说明为何配置、扩展点、事件、适配器或独立模块不可行；缺少登记会被 CI 拒绝。

## 活跃治理修改

| 文件 | 修改目的 | 修改类型 | 冲突风险 | 验证与回退 |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | 将扩展优先、Migration 与上游修改规则提供给所有编码入口 | Governance | 低 | 治理脚本；回退本文件改动 |
| `backend/AGENTS.md` | 限制未来 ERP/Travel 业务进入官方 `crm` 模块 | Governance | 低 | PR 审查；回退本文件改动 |
| `backend/crm/src/main/resources/migration/1.9.1/ddl/V1.9.1_2__ga_ddl.sql` | 恢复已发布 checksum；索引改由 `V1.9.1_9000` 交付 | Migration compatibility | 中 | 旧库/新库双路径迁移；移除前须先解决已部署数据库的 checksum 一致性 |
| `frontend/AGENTS.md` | 约束官方页面改动与扩展槽优先级 | Governance | 低 | PR 审查；回退本文件改动 |
| `frontend/.gitignore` | 跟踪 `pnpm-lock.yaml`，使 CI 的锁定依赖安装可复现 | Build governance | 低 | 锁文件检查；恢复忽略规则 |
| `.github/PULL_REQUEST_TEMPLATE.md` | 增加二开准入问题 | Governance | 低 | PR 创建检查；回退模板改动 |
| `.github/workflows/codecov.yml` | 移除继承的官方 Codecov 工作流 | Fork automation isolation | 中 | 统一治理门禁；从上游恢复该文件 |
| `.github/workflows/frontend-build.yml` | 移除重复的继承前端检查 | Fork automation isolation | 低 | 统一治理门禁；从上游恢复该文件 |
| `.github/workflows/build-and-push.yml` | 移除访问官方内部仓库且可重写标签的发布工作流 | Fork automation isolation | 高 | 工作流清单检查；仅在公司发布方案就绪后以新工作流替代 |
| `.github/workflows/build-and-push-base.yml` | 移除访问官方镜像命名空间的基础镜像发布工作流 | Fork automation isolation | 中 | 工作流清单检查；仅在公司发布方案就绪后以新工作流替代 |
| `.github/workflows/sync2gitee.yml` | 移除将 Fork 自动镜像到官方 Gitee 组织的工作流 | Fork automation isolation | 中 | 工作流清单检查；从上游恢复该文件 |

## 已回退业务修改

| 文件 | 原修改目的 | 状态 | 回退方式 |
| --- | --- | --- | --- |
| `frontend/packages/web/src/views/dashboard/index.vue` | 绕过 DataEase 仪表盘许可拦截 | 已回退 | `git revert edb53331b` |
| `frontend/packages/web/src/views/system/business/components/integrationList.vue` | 绕过 DataEase 编辑和同步许可拦截 | 已回退 | `git revert edb53331b` |

当前活跃的官方**业务源码**修改：无。
