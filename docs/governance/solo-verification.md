# 单人流程验证记录

治理 PR #4 已合入 develop；PR #5 已通过完整后端、web、mobile、策略与 required 检查并以 merge 进入 main。

main 仍要求 PR 和 required、限制管理员、禁止强推删除；已取消线性历史。不要求第二位审批者。官方候选独立保存在 upstream-sync 草稿 PR #6，未自动部署。

本地回归覆盖：文档/单端/共享/后端/未知路径分类；应运行任务意外 skipped、cancelled 和分类失败；已提交/暂存/工作区 SQL 范围；已有目录新增合法迁移；重复规范化版本、倒序及无效引用拒绝。

本记录 PR #7 已实际验证 develop 上轻量路径：backend/web/mobile skipped，policy/classify/required success（Actions 34490026565）。新库与旧库升级结论仍分开记录；Staging/E2E/回滚文档属于发布骨架。
