## 变更说明

说明问题、影响范围和验证结果；涉及上游同步时附官方 Release/Tag、commit SHA 与 Release Notes。

## 二开准入检查

- [ ] 是否修改、删除或重命名官方基线文件？如是，已登记 `UPSTREAM_MODIFICATIONS.md` 并说明扩展为何不可行。
- [ ] 是否存在不必要的 Core 修改，或能通过配置、扩展点、事件、适配器、独立模块实现？
- [ ] 是否新增跨模块依赖？是否避免跨领域直接访问 Mapper？
- [ ] 是否修改数据库？是否只新增合法 Migration，且未改写历史 Migration？
- [ ] 是否修改官方表？是否评估扩展表？
- [ ] 是否影响 RBAC、组织、数据范围、状态机、金额、幂等或 Audit Log？
- [ ] 是否需要 Domain Event、外部 Adapter、权限资源或 API 文档？
- [ ] 是否新增或更新 OpenSpec、ADR、运行手册和 `UPSTREAM_MODIFICATIONS.md`？
- [ ] 是否避免无关重构、批量格式化和依赖升级？依赖升级是否使用独立 PR？

## 验证

- [ ] 已运行受影响的后端/前端检查，并附结果。
- [ ] 已确认 Migration、集成、E2E、Staging、升级与回滚的适用状态；未接入项没有标记为通过。
- [ ] 提交信息符合 [Conventional Commits](https://www.conventionalcommits.org/)。
