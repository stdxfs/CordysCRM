## Context
用户确认当前数据是可重建的开发数据，选择轻量 PR。原始治理历史保留。
## Goals / Non-Goals
减少无关验证和重复手续；保留安全边界。暂不实现业务模块、生产自动化或自定义升级 SQL。
## Decisions
- main 保留 PR、required、禁止强推删除，取消线性历史。develop 日常集成，upstream-sync 保存并验证候选。
- 文档只跑策略；前端按 web/mobile/shared 范围；后端跑测试；main、官方同步、治理基础设施变更跑全量。未知路径默认全量。
- 汇总只接受计划内跳过；分类失败或任务取消不得放行。
- 对固定官方 SHA 做双端 tree diff；普通 PR 禁止改变基线，同步必须验证官方可达性及祖先关系。官方 Migration 差异单独报告，本地历史 SQL 保持不可变。
- 新迁移允许加入原有目录，但版本必须唯一且大于已有最高版本。提供 committed/staged/worktree 明确检查范围。
- 新库验证使用隔离容器；已有库的 checksum 不兼容保留证据。部署与 Git 合并分离。
## Risks / Trade-offs
新库验证不证明旧数据升级安全。全量检查仍需数分钟，但只在相关变化或稳定版本时运行。
## Migration Plan
先合入治理 PR 并验证保护，再合并固定官方候选至同步分支，通过构建、新库和基础业务验证后进入 develop。main 不自动跟进官方候选。
