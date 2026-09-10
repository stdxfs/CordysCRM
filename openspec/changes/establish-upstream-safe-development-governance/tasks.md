## 1. OpenSpec 与现有侵入整改

- [x] 1.1 初始化 OpenSpec 项目上下文并完成治理变更工件；通过 `openspec validate establish-upstream-safe-development-governance --strict` 验证。
- [x] 1.2 使用可回退提交恢复两处 DataEase 官方许可判断；通过与固定上游基线比较确认业务源码无活跃差异。
- [x] 1.3 建立上游基线、修改登记和 ADR；通过治理脚本验证登记允许清单与文档一致。

## 2. 日常开发与分支治理

- [x] 2.1 将扩展优先级、官方修改登记、Migration 和依赖升级规则接入项目指引与 PR 模板；人工检查所有准入问题均可回答。
- [x] 2.2 创建 `develop` 与 `upstream-sync` 长期分支、推送到 `origin` 并禁用本地 `upstream` 推送；通过 `git branch -r` 和失败的 upstream push dry-run 验证。
- [x] 2.3 配置 `main` 分支仅通过 PR 合并且要求统一治理检查；通过 GitHub API 查询保护规则验证。

## 3. 可执行专项门禁

- [x] 3.1 实现未登记官方源码差异与历史 Migration 静态检查；使用临时 Git 差异场景验证违规时失败、合规时通过。
- [x] 3.2 实现统一 PR 治理门禁，运行后端 Testcontainers/Flyway 集成测试及前端类型检查和构建；远端 Java 21 门禁通过，本地 JDK 17 不兼容已记录。
- [x] 3.3 实现上游同步验证工作流；在本地使用指定上游基线验证无冲突合并摘要与零远端写入。
- [x] 3.4 交付 Staging、E2E、升级与回滚运行手册及手动 Staging 预检骨架；验证未配置环境时任务明确失败且不执行部署。

## 4. Fork 自动化与最终验证

- [x] 4.1 隔离或停用依赖官方内部仓库/令牌的继承发布自动化；检查常规治理工作流只访问当前 Fork 和公开上游。
- [x] 4.2 执行 OpenSpec、Shell、后端、前端和 Git 差异验证；确认所有任务有证据后更新任务状态。
