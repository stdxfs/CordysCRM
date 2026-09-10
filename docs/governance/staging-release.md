# Staging、E2E、升级与回滚准入

本文件定义生产发布前必须具备的证据。当前仓库尚未配置 Staging，因此这些项目均为**未接入**；未接入不等于通过。

| 准入项 | 最低证据 | 当前状态 |
| --- | --- | --- |
| Staging | `staging` GitHub Environment、`STAGING_CRM_URL`、候选 commit 和镜像 digest | 未接入 |
| E2E | 独立测试账号、登录/权限/核心业务回归报告 | 未接入 |
| 数据升级 | 固定旧版本数据库、代表性数据、迁移前后校验和与数据保留报告 | 未接入 |
| 回滚演练 | 旧镜像 digest、数据库备份恢复记录、文件与配置恢复记录、恢复后健康和业务验证 | 未接入 |

## 手动 Staging 预检

运行 `Staging Preflight` 工作流前，管理员必须在 GitHub Environment `staging` 配置：

- Variable：`STAGING_CRM_URL`
- Secret：`STAGING_SMOKE_USERNAME`、`STAGING_SMOKE_PASSWORD`

工作流只验证候选标识、环境配置和 HTTP 可达性；它不部署、不登录，也不代表 E2E 通过。

## 回滚要求

回滚必须使用不可变镜像 digest。执行前记录当前 digest、目标回滚 digest、数据库备份 ID、上传文件备份 ID、配置版本和变更单。恢复后必须重新执行健康检查、登录、权限和受影响业务的验证。不得使用 `latest` 作为候选或回滚依据。
