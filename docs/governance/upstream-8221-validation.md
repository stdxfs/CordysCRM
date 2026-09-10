# 官方候选 8221b91c 验证

旧官方基线：11ddfef84c49fce62bc4847d21df618b2b213964。
候选：8221b91c9f665d401b48353a4bbf48a33b1e3d3e。

无文本合并冲突，保留官方 merge 祖先。官方在 V1.9.1_2__ga_ddl.sql 增加 sys_operation_log(create_time) 索引。

## 已知旧库风险

此前隔离 MySQL 8.4 / Flyway 11.15.0 实验：旧基线执行 139 条迁移，checksum 1138237749；候选校验值 -1994966056，validate 和开启校验的 migrate 均失败。索引数量仍为 0。该实验是模拟库，不是现网数据库副本。未执行 repair。

## 当前新库验收

- 构建与测试：PR #6 的后端测试、web/mobile 类型检查及构建全部通过（Actions 34489429620）。独立候选工作树使用 JDK 21 打包 backend/app 成功，运行应用源码与官方 SHA 一致。
- 独立新库：MySQL 8.4 + Flyway 11.15.0 成功执行 139 条迁移；1.9.1.2 checksum 为 -1994966056，success=1；sys_operation_log 的 idx_create_time 存在（information_schema 返回 1）。
- 应用启动：使用候选 app-main.jar、Java 21、独立 MySQL/Redis；开启 validate-on-migrate，应用再次成功验证 139 条迁移。Quartz 保持默认启用；关闭它会缺失 ScheduleManager Bean。
- HTTP 验证：获取 RSA 公钥、加密登录、/is-login 查询均通过；/account/add 创建唯一测试客户、/account/get/{id} 校验名称、/account/page 查询通过。退出后 /is-login 返回 HTTP 200 空响应，没有登录用户。
- 验证限制：这是 API 冒烟及新库验证，不包含浏览器 E2E、旧库数据升级、生产回滚或服务器部署。试验数据全部位于 cordys_solo 独立容器库。

新库准入项已满足，待最终 PR 检查通过后允许以 merge 进入 develop；main 保持治理版本。不会自动部署服务器或覆盖已有开发库。正式使用新开发基线前需单独备份并切换具体数据库。
