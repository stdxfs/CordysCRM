# ADR 0001：使用固定官方基线治理 Fork

## Context

项目需长期同步 CordysCRM 官方更新，同时避免未登记的官方源码侵入。

## Decision

以 `governance/upstream-baseline.env` 中的官方 commit 作为机器检查基线。对基线文件的 M/D/R 差异必须进入登记清单；业务源码默认不允许存在活跃差异。

## Alternatives

仅依赖人工 Code Review。该方式无法可靠发现遗漏登记，未采用。

## Consequences

每次官方升级都必须独立审查并更新基线；新增公司业务文件不受该检查限制。
