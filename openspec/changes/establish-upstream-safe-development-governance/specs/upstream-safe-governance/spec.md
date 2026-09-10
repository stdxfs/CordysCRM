## Purpose

为 CordysCRM 的公司 Fork 提供可验证的上游兼容治理，使定制开发、官方版本同步和生产发布能在保留完整 Git 历史的前提下独立演进。

## ADDED Requirements

### Requirement: 上游业务源码修改必须可追踪
系统 SHALL 以固定的官方上游基线检查受 Git 追踪的官方文件差异。任何对官方业务源码的修改、删除或重命名 MUST 在变更登记中逐项说明替代方案、风险、验证与回退方式；未登记差异 MUST 使治理门禁失败。

#### Scenario: 未登记的官方源码改动
- **WHEN** PR 修改了官方基线中存在的业务源码文件且该文件未列入登记允许清单
- **THEN** 治理门禁失败并输出该文件路径

#### Scenario: 已登记的治理文件改动
- **WHEN** PR 修改了登记允许的治理文件
- **THEN** 治理门禁允许该差异并要求登记文档保持同步

### Requirement: 历史 Migration 不可改写
系统 SHALL 检查 PR 中的 Migration 差异。已有 Migration 文件 MUST 不得被修改、删除或重命名；新增 Migration MUST 使用既有目录和命名格式，且不得回填到基准中已经存在的版本目录。

#### Scenario: 修改历史 Migration
- **WHEN** PR 修改、删除或重命名基准分支已存在的 Migration 文件
- **THEN** Migration 门禁失败并指出违规文件

#### Scenario: 新增独立版本 Migration
- **WHEN** PR 在新的版本目录中新增命名合法的 Migration 文件
- **THEN** Migration 静态检查通过，并由集成测试实际执行 Flyway 迁移

### Requirement: 上游同步必须经过验证
系统 SHALL 在上游同步分支或手动同步任务中获取指定官方 ref，验证合并可行性、输出变更摘要，并运行后端集成测试及前端构建。该流程 MUST 不自动合并、推送或发布。

#### Scenario: 上游 ref 可无冲突合并
- **WHEN** 同步任务对指定官方 ref 执行合并可行性检查且不存在冲突
- **THEN** 任务输出候选 ref、合并基点、受影响文件和 Migration 摘要

#### Scenario: 上游 ref 存在冲突
- **WHEN** 同步任务检测到 Git 合并冲突
- **THEN** 任务失败且不修改任何远端分支

### Requirement: 发布环境验证必须显式声明
系统 SHALL 将 Staging、E2E、升级验证与回滚演练分别记录为发布准入项。环境、测试账号、候选镜像 digest 或回滚证据未配置时，系统 MUST 将该项标记为未接入，不得将健康检查视为 E2E 或完整回滚验证。

#### Scenario: Staging 环境尚未接入
- **WHEN** 手动执行 Staging 骨架工作流且所需环境变量或密钥未配置
- **THEN** 工作流失败并说明缺少的配置，不产生部署动作

#### Scenario: 发布候选完成验证
- **WHEN** 发布候选具备 Staging、E2E、升级和回滚演练的记录
- **THEN** 发布清单允许将该候选标记为具备生产发布资格
