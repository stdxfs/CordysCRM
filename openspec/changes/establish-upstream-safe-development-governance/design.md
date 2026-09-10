## Context

当前 Fork 的 `main` 比 `upstream/main` 多一个 DataEase 许可绕过提交，且未建立 OpenSpec、官方修改登记、长期治理分支或专项发布门禁。现有后端测试使用 Testcontainers 启动 MySQL/Redis 并启用 Flyway，但 Flyway 校验配置为关闭；现有发布工作流包含官方内部仓库和可变标签逻辑。

## Goals / Non-Goals

**Goals:**

- 将活跃业务源码差异恢复为零，并用固定基线防止未登记侵入。
- 建立可协作的 `main`、`develop`、`upstream-sync` 流程。
- 在不引入新业务模块的前提下，提供可运行的静态、迁移、集成、前端和上游同步检查。
- 让环境验证缺失成为明确的发布阻断项。

**Non-Goals:**

- 不实现 ERP、Travel、Extension Core、领域事件或新的运行时 API。
- 不自动部署 Staging、不自动执行远程回滚、不修改生产数据。
- 不修改或 repair 官方历史 Migration 以掩盖校验问题。

## Decisions

### 固定基线与差异登记

将当前已验证的 `upstream/main` commit 记录为基线。脚本只检查该基线已追踪文件的 M/D/R 差异；新增的公司业务文件不被误判为官方侵入。允许的治理文件使用机器可读清单，并在 `UPSTREAM_MODIFICATIONS.md` 中提供人类可审计说明。

替代方案是只依赖人工 PR 审查。它无法稳定阻止遗漏登记，故不采用。

### 回退而非重写历史

使用 `git revert` 回退 DataEase 许可绕过提交，在 Git 历史中保留原因和可恢复性。避免重置、强推或删除已有提交。

替代方案是把页面补丁迁移到新的扩展机制。该机制属于未来业务设计，本轮明确不实现。

### 分层验证

治理门禁始终生成一个汇总 required check；该检查依赖官方差异、Migration 静态检查、后端 Testcontainers/Flyway 集成测试和前端类型检查/构建。上游同步用独立工作流验证候选 ref 的合并与构建，绝不写入远端。

Migration 校验分为两个层次：本轮自动验证空库初始化、历史脚本不可改写和新脚本格式；跨版本数据升级保留为具备固定旧制品和代表性数据后才可启用的发布专项，不能被空库测试替代。

### Staging 与回滚边界

手动 Staging 骨架仅验证环境配置和候选标识，不执行部署；回滚以版本化运行手册和证据清单落地。候选镜像一律用 digest 标识，`latest` 不能作为验证或回滚依据。

## Risks / Trade-offs

- [固定基线会在官方升级后失效] → 上游同步 PR 完成评估后，单独更新基线、登记和相关验证记录。
- [全量后端与前端检查耗时较长] → 用统一汇总结果确保不出现路径过滤导致的缺失 required check；后续可在有可靠路径分析后优化。
- [没有 Staging 凭据无法自动验收环境] → 明确标记未接入并阻断生产发布，而不产生虚假的绿色结果。
- [单人维护无法满足独立审批] → `main` 强制走 PR 与 required check；在具备第二位维护者前，审批人数由仓库管理员明确配置，不在 CI 中伪造审批。

## Migration Plan

1. 在治理分支初始化 OpenSpec 并回退现有业务补丁。
2. 提交治理文件和工作流，在 PR 中运行基础检查。
3. 合并后创建并推送 `develop` 与 `upstream-sync`，禁用本地 `upstream` 推送。
4. 只在 required check 已成功产生后配置 `main` 分支保护。
5. 后续首次官方升级单独建立 `upstream-sync` PR，记录候选 ref、Migration 影响、Staging 与回滚证据。

回退治理变更时，保留已创建的审计记录；应用和数据库均未在本变更中修改。
