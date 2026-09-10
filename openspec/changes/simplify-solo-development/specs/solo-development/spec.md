## ADDED Requirements
### Requirement: Risk-based checks
系统 SHALL 根据变更范围执行检查，并拒绝分类失败、应执行却跳过或取消的任务。
#### Scenario: Documentation only
- **WHEN** PR 到 develop 且仅修改文档
- **THEN** 仅执行轻量治理检查
#### Scenario: Upstream candidate
- **WHEN** PR 引入官方新基线
- **THEN** 保留官方祖先，执行完整构建并单独报告官方历史 Migration 变化
### Requirement: Migration boundaries
系统 SHALL 区分 committed、staged、worktree，拒绝本地历史迁移改写及重复或倒序的新版本。
#### Scenario: Existing directory addition
- **WHEN** 新 SQL 位于已有目录且完整版本唯一并高于历史版本
- **THEN** 静态检查通过
### Requirement: Candidate is not deployment
系统 MUST 允许保存尚未验证的候选分支，并将新库验证与已有数据库升级安全分别记录。
#### Scenario: Historical checksum changes
- **WHEN** 官方历史 checksum 改变但新开发库可正常初始化
- **THEN** 允许验证候选，保留旧库不兼容说明，不自动升级旧库
