# 上游修改登记

基线：`1Panel-dev/CordysCRM` 的 `4d169a35b22d9d375e911f7f5c703004258bd440`（`v1.9.2`，2026-09-17）。此前基线为 `a0ef69d31fd98c338199579353840f34ef679197`（`v1.9.1`）。

本次官方自身改写 1.9.1.2 迁移以新增日志索引。本 Fork 将该历史脚本恢复为此前已发布内容，并通过新的补偿 Migration 交付索引，以兼容旧库 checksum。不会自动升级已有本地或服务器数据库。详见 docs/governance/upstream-8221-validation.md。

规则：修改、删除或重命名该基线中存在的官方文件前，必须先更新本文件和 `governance/upstream-modifications-allowlist.txt`。业务源码必须说明为何配置、扩展点、事件、适配器或独立模块不可行；缺少登记会被 CI 拒绝。

## 活跃治理修改

| 文件 | 修改目的 | 修改类型 | 冲突风险 | 验证与回退 |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | 将扩展优先、Migration 与上游修改规则提供给所有编码入口 | Governance | 低 | 治理脚本；回退本文件改动 |
| `backend/AGENTS.md` | 限制未来 ERP/Travel 业务进入官方 `crm` 模块 | Governance | 低 | PR 审查；回退本文件改动 |
| `backend/crm/src/main/resources/migration/1.9.1/ddl/V1.9.1_2__ga_ddl.sql` | 恢复已发布 checksum；索引改由 `V1.9.1_9000` 交付 | Migration compatibility | 中 | 旧库/新库双路径迁移；移除前须先解决已部署数据库的 checksum 一致性 |
| `frontend/AGENTS.md` | 约束官方页面改动与扩展槽优先级 | Governance | 低 | PR 审查；回退本文件改动 |
| `frontend/.gitignore` | 忽略本地生成的 `pnpm-lock.yaml`，避免安装依赖后产生工作区改动 | Build governance | 中：CI 依赖解析不再固定 | 检查忽略规则与 CI 安装；移除忽略规则并重新跟踪锁文件 |
| `.github/PULL_REQUEST_TEMPLATE.md` | 增加二开准入问题 | Governance | 低 | PR 创建检查；回退模板改动 |
| `.github/workflows/codecov.yml` | 移除继承的官方 Codecov 工作流 | Fork automation isolation | 中 | 统一治理门禁；从上游恢复该文件 |
| `.github/workflows/frontend-build.yml` | 移除重复的继承前端检查 | Fork automation isolation | 低 | 统一治理门禁；从上游恢复该文件 |
| `.github/workflows/build-and-push.yml` | 移除访问官方内部仓库且可重写标签的发布工作流 | Fork automation isolation | 高 | 工作流清单检查；仅在公司发布方案就绪后以新工作流替代 |
| `.github/workflows/build-and-push-base.yml` | 移除访问官方镜像命名空间的基础镜像发布工作流 | Fork automation isolation | 中 | 工作流清单检查；仅在公司发布方案就绪后以新工作流替代 |
| `.github/workflows/sync2gitee.yml` | 移除将 Fork 自动镜像到官方 Gitee 组织的工作流 | Fork automation isolation | 中 | 工作流清单检查；从上游恢复该文件 |

## 已回退业务修改

| 文件 | 原修改目的 | 状态 | 回退方式 |
| --- | --- | --- | --- |
| `frontend/packages/web/src/views/dashboard/index.vue` | 绕过 DataEase 仪表盘许可拦截 | 已回退 | `git revert edb53331b` |
| `frontend/packages/web/src/views/system/business/components/integrationList.vue` | 绕过 DataEase 编辑和同步许可拦截 | 已回退 | `git revert edb53331b` |

## 标讯移除

标讯是官方菜单中的大单网 iframe，没有可单独关闭嵌入的扩展点。模块开关和集成开关仍会初始化配置、权限和菜单，因此按要求删除官方标讯代码。已发布的 1.4.0 Migration 不改写；新增 `backend/crm/src/main/resources/migration/1.9.2/dml/V1.9.2_9000__remove_tender.sql` 清理已有库中的模块、角色权限和第三方配置。冲突风险中等：上游若继续修改下列文件会产生冲突。回退时恢复这些文件并删除补偿 Migration；已执行过该脚本的库需另行补回数据。

- `backend/crm/src/main/java/cn/cordys/common/constants/PermissionConstants.java`
- `backend/crm/src/main/java/cn/cordys/common/constants/ThirdConfigTypeConstants.java`
- `backend/crm/src/main/java/cn/cordys/common/constants/ThirdDetailType.java`
- `backend/crm/src/main/java/cn/cordys/crm/integration/common/request/TenderThirdConfigRequest.java`
- `backend/crm/src/main/java/cn/cordys/crm/integration/sso/service/TokenService.java`
- `backend/crm/src/main/java/cn/cordys/crm/integration/tender/constant/TenderApiPaths.java`
- `backend/crm/src/main/java/cn/cordys/crm/integration/tender/controller/TenderController.java`
- `backend/crm/src/main/java/cn/cordys/crm/integration/tender/dto/TenderDetailDTO.java`
- `backend/crm/src/main/java/cn/cordys/crm/system/service/IntegrationConfigService.java`
- `backend/crm/src/main/resources/i18n/cordys-crm_en_US.properties`
- `backend/crm/src/main/resources/i18n/cordys-crm_zh_CN.properties`
- `backend/crm/src/main/resources/permission.json`
- `frontend/packages/lib-shared/api/modules/system/business.ts`
- `frontend/packages/lib-shared/api/requrls/system/business.ts`
- `frontend/packages/lib-shared/enums/commonEnum.ts`
- `frontend/packages/lib-shared/enums/moduleEnum.ts`
- `frontend/packages/lib-shared/models/system/business.ts`
- `frontend/packages/web/src/api/modules/index.ts`
- `frontend/packages/web/src/assets/svg/dadan.svg`
- `frontend/packages/web/src/config/business.ts`
- `frontend/packages/web/src/enums/routeEnum.ts`
- `frontend/packages/web/src/layout/components/layout-sider.vue`
- `frontend/packages/web/src/layout/default-layout.vue`
- `frontend/packages/web/src/layout/page-content.vue`
- `frontend/packages/web/src/locale/en-US/index.ts`
- `frontend/packages/web/src/locale/zh-CN/index.ts`
- `frontend/packages/web/src/router/constants.ts`
- `frontend/packages/web/src/router/routes/modules/tender.ts`
- `frontend/packages/web/src/store/modules/app/index.ts`
- `frontend/packages/web/src/views/system/business/components/integrationList.vue`
- `frontend/packages/web/src/views/system/business/locale/en-US.ts`
- `frontend/packages/web/src/views/system/business/locale/zh-CN.ts`
- `frontend/packages/web/src/views/system/module/components/configCard.vue`
- `frontend/packages/web/src/views/system/module/index.vue`
- `frontend/packages/web/src/views/system/module/locale/en-US.ts`
- `frontend/packages/web/src/views/system/module/locale/zh-CN.ts`
- `frontend/packages/web/src/views/tender/index.vue`

当前活跃的官方**业务源码**修改：标讯移除，见上一节。
