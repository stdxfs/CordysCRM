## Why
单人开发需要减少重复构建和文档负担。官方历史 Migration 改动应限制已有数据库升级，而不阻止保存同步候选。
## What Changes
- 分级检查、短 PR、可追踪的小型官方补丁和保留官方祖先的 merge 流程。
- Migration 检查区分官方变化、本地修改及工作区状态。
- 使用独立新开发库验证官方候选；保留旧库不兼容证据。
## Capabilities
### New Capabilities
- `solo-development`: 单人开发维护规则和分级自动化。
### Modified Capabilities
## Impact
影响治理脚本、CI、文档和分支保护，不改变业务 API，不部署服务器。
