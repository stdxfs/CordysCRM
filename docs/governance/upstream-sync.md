# 单人开发和上游维护

日常：develop → feature/* 或 fix/* → 自查 PR → develop。main 是阶段性稳定代码，develop → main 使用 PR。无需第二位审批者，无需固定 release/* 分支；合入 main 不自动部署。

main 保留 required 检查、PR、禁止强推删除、管理员约束；不要求线性历史。上游与长期分支之间用 merge 保留官方祖先；不要 rebase 或 squash 官方历史。已有分支和治理历史保留。

## 官方同步

1. git fetch upstream，优先稳定 Release；需要最新 main 时锁定其 SHA。
2. 在 upstream-sync 合并 develop，再 merge 官方 SHA。允许提交和推送尚未验证的候选，使用草稿 PR 记录失败。
3. 单独更新 governance/upstream-baseline.env 和登记中的当前基线。固定官方来源并校验 SHA 可达性、祖先关系；其他分支不得更新基线（develop 向 main 推进已集成基线除外）。
4. CI 分别报告旧/新官方 Migration 差异与候选相对官方的本地补丁。官方历史变化不是本地篡改，也不是旧库升级已通过。
5. 全量构建、新开发库迁移、索引及应用启动/登录/基础操作通过后合入 develop。旧库兼容问题继续记录；main 不自动跟进。

## 检查范围

verify-migrations.sh BASE [committed|staged|worktree]：默认 committed，比较 BASE 与 HEAD；staged 比较 BASE 与索引；worktree 包括未跟踪 SQL。未提交合并必须用 staged/worktree。

verify-upstream-modifications.sh [committed|staged|worktree] 同样显式指定范围；提交检查不能证明未提交修改安全。

纯文档到 develop 只跑策略；web/mobile 按包构建，共享或依赖变化跑两端；后端变化跑后端测试。main、上游同步、基础设施及未知文件变化执行全量。分类失败、意外跳过或取消不能通过 required；上游预检只报告，不重复构建。

小修复写简短 PR 和必要登记，重要功能/跨模块/复杂升级写 OpenSpec，长期架构决定写 ADR。不提前建设 ERP、Travel 或 Extension Core。
