# ADR 0001：使用固定官方基线治理 Fork

## Context

项目需长期同步 CordysCRM 官方更新，同时避免未登记的官方源码侵入。

## Decision

以 `governance/upstream-baseline.env` 中的官方 commit 作为机器检查基线。官方文件修改必须登记。单人流程修订：允许必要、局部、可测试、可回退的业务补丁，重要架构变化才要求 OpenSpec/ADR；不以修改比例作为准入条件。保留此前治理提交作为历史。

## Alternatives

仅依赖人工 Code Review。该方式无法可靠发现遗漏登记，未采用。

## Consequences

每次官方升级都必须独立审查并更新基线；新增公司业务文件不受该检查限制。
