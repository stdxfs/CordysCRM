# 仓库贡献指南

## 项目结构与模块组织

Cordys CRM 是 Maven 多模块项目。`backend/framework` 存放通用基础设施，`backend/crm` 包含领域与 API 代码，`backend/app` 提供 Spring Boot 启动入口。后端测试位于 `backend/crm/src/test`。`frontend/packages` 是 pnpm 工作区，包含桌面端 `web`、移动端 `mobile` 和公共包 `lib-shared`。项目文档位于 `docs`，容器文件和示例配置位于 `installer`。

进入子目录工作前，同时阅读 `backend/AGENTS.md` 或 `frontend/AGENTS.md`。系统边界参见 `docs/architecture.md`，完整环境与开发流程参见 `docs/development.md`。

## 构建、测试与开发命令

- `./mvnw install -N`：将根 Parent POM 安装到本地仓库。
- `./mvnw clean package`：构建完整应用，包括前端。
- `./mvnw -f backend/pom.xml test`：运行后端测试。
- `pnpm --dir frontend install --frozen-lockfile`：严格按锁文件安装前端依赖。
- `pnpm --dir frontend build`：对所有前端工作区执行类型检查和构建。
- `pnpm --dir frontend --filter @cordys/web dev`：启动桌面端；将包名替换为 `@cordys/mobile` 可启动移动端。
- `pnpm --dir frontend --filter @cordys/web lint`：执行 ESLint 并自动修复；样式检查使用 `lint:styles`。

开发环境使用 Java 21 和 Node.js 18 或更高版本。更多环境说明参见 `BUILD.md` 与 `frontend/REDEME.md`。

## 编码风格与命名约定

Java 使用四空格缩进，包名统一置于 `cn.cordys` 下；类名使用 PascalCase，成员使用 camelCase。领域代码应放入对应的功能包。前端使用两空格缩进、单引号、分号和 120 字符行宽。类型与组件使用 PascalCase，函数及组合式函数使用 camelCase（如 `useLoading`）；文件名遵循相邻代码的既有风格，通常使用 kebab-case。提交前运行 ESLint、Stylelint 和 Prettier。

## 测试规范

后端测试使用 JUnit 5、Spring Boot Test 和 Testcontainers。测试文件命名为 `*Test.java`，包结构应与生产代码一致。变更业务行为时，应补充针对性测试及必要的 SQL 或资源夹具。项目已配置 JaCoCo，虽未规定固定覆盖率，但 PR 应为新增或修改逻辑补充合理覆盖。前端目前没有自动化测试脚本，至少应执行类型检查、代码检查及对应的生产构建。

## 提交与拉取请求规范

提交信息遵循 Commitlint 强制的 Conventional Commits，例如 `fix: correct invoice validation`、`feat: add customer filter` 或 `refactor: simplify AI conditions`。提交和 PR 应保持小而聚焦，并能独立合并；开发重要功能前先创建 Issue 讨论。PR 需说明变更原因和内容，确认测试结果，并说明文档影响。关联相关 Issue；涉及可见界面变化时附截图。Issue、测试夹具和 PR 中不得包含凭据、客户数据、IP 地址或未脱敏日志。

## 二开治理（强制）

本 Fork 的治理基线、上游同步流程和官方文件登记见 `governance/`、`UPSTREAM_MODIFICATIONS.md` 与 `docs/governance/upstream-sync.md`。二开优先级固定为：配置、扩展点、独立模块、事件/Hook、适配器、局部覆盖、官方核心修改。新增业务默认不修改官方 Core；修改前必须在 OpenSpec 提案中说明扩展不可行原因，并登记到 `UPSTREAM_MODIFICATIONS.md`。

不得改写已发布的 Migration；修复必须新增按版本排序的脚本。不得在业务 PR 中顺带升级核心依赖、批量格式化官方项目或重构无关官方代码；依赖升级与官方同步均使用独立 PR。开发前读取相关 OpenSpec 变更和 ADR，完成后更新任务、验证记录和必要文档。
