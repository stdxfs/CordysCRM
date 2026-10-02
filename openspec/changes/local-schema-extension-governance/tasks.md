# Tasks

## 1. 长期决策与操作手册

- [ ] 1.1 新增 `docs/adr/0003-local-schema-extension.md`，固化 9xxx 命名与旁路优先决策，并引用 ADR 0001/0002；确认文件可被打开且编号不与现有 ADR 冲突
- [ ] 1.2 新增 `docs/governance/local-schema-extension.md`，写入命名示例、决策树、高冲突表清单、官方同步步骤与禁止项；确认与 `design.md` 决策一致且可独立阅读

## 2. 编码入口与审查模板

- [ ] 2.1 更新根目录 `AGENTS.md` 二开治理段：摘要本地 Schema 规则并链接到 ADR 0003 与 governance 手册；确认链接路径有效
- [ ] 2.2 更新 `backend/AGENTS.md`「数据库与资源文件」：补充 `9000`–`9999` 本地序号、禁止占用未发布官方版本、旁路优先；确认与根准则不矛盾
- [ ] 2.3 更新 `.github/PULL_REQUEST_TEMPLATE.md`：在数据库影响处增加本地扩展/旁路表/高冲突表自检提示；确认模板仍简洁可用

## 3. 交叉引用与校验

- [ ] 3.1 在 `docs/governance/upstream-sync.md` 增加一句指向本地 Schema 扩展手册（同步后处理官方 DDL 冲突时阅读）；确认无重复长文
- [ ] 3.2 运行 `openspec validate local-schema-extension-governance --strict`（或等价命令）并通过；人工核对上述文档交叉链接无死链
