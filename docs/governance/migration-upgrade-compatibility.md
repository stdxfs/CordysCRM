# V1.9.1.2 Migration 兼容升级

官方候选 `8221b91c` 在已发布的 `V1.9.1_2__ga_ddl.sql` 中追加索引，导致旧数据库的 Flyway checksum 校验失败。本 Fork 恢复旧脚本，并由 `V1.9.1_9000__operation_log_create_time_index.sql` 交付该索引。

代码合并不等于数据库升级。以下步骤只适用于已确定目标、完成备份并停止写入的环境；先在本地开发库验证，再单独安排服务器操作。

## 只读预检

MySQL 客户端应通过本机 option file、交互输入或密钥管理工具取得凭据，不要把密码写入命令、脚本或日志。

```bash
mysql --batch --skip-column-names "$CORDYS_DB_NAME" \
  < scripts/governance/migration-preflight.sql \
  | python3 scripts/governance/migration_preflight.py
```

只有以下两个状态允许继续：

| 状态 | 含义 | 操作 |
| --- | --- | --- |
| `READY_UPGRADE` | `V1.9.1.2` 是已发布 checksum，补偿迁移尚未执行 | 备份后使用修复版本正常启动或执行 Flyway migrate |
| `READY_CURRENT` | 历史 checksum、补偿迁移和索引均一致 | 无需处理 |

任何 `BLOCK_*` 都必须停止。尤其是：

- `BLOCK_CANDIDATE_CHECKSUM`：数据库执行过候选改写脚本。
- `BLOCK_UNKNOWN_CHECKSUM`：历史脚本来源不明。
- `BLOCK_FAILED_HISTORY` / `BLOCK_FAILED_COMPENSATION`：存在失败记录。
- `BLOCK_INDEX_CONFLICT`：同名索引定义不是单列 `create_time` 普通索引。
- `BLOCK_MISSING_INDEX`：补偿迁移显示成功，但索引不存在。

预检只读取 `cordys_crm_version` 和 `information_schema.statistics`，不会执行 `repair` 或 DDL。

## 旧库标准升级

1. 记录应用 commit、数据库名和 Flyway schema history，停止应用写入。
2. 对明确的目标数据库完成可恢复备份，并验证备份文件可读。
3. 执行只读预检，确认结果为 `READY_UPGRADE`。
4. 使用与项目锁定版本一致的 Flyway 执行 validate/migrate，或启动启用了 Migration 校验的修复版本应用。
5. 再次执行预检，结果必须为 `READY_CURRENT`。
6. 核对 `V1.9.1.2` checksum 仍为 `1138237749`，`V1.9.1.9000` 成功，并完成应用启动和基础业务验证。

升级失败时停止应用，保留日志，不运行 `repair`。应用代码可以回退；新增索引默认保留。若必须回退数据库，应恢复升级前备份，不直接修改 schema history。

## 候选 checksum 的专项规范化

`-1994966056` 表示数据库由曾经改写历史脚本的候选版本初始化。该状态不走标准升级，也不由 CI 或部署脚本自动处理。

仅当能证明数据库来自该短期候选、索引定义完全正确且已有可恢复备份时，才可在独立维护窗口评估一次性人工规范化：停止应用，以修复版本的 Migration 资源运行 Flyway `repair`，确认修复日志只把 `V1.9.1.2` checksum 规范为 `1138237749`，随后运行 migrate，使 `V1.9.1.9000` 记录索引交付。任一检查不符必须恢复备份并停止。

对于可丢弃的开发数据，重建空数据库通常更简单。生产或来源不明的数据库必须先在副本上演练，不得照搬此步骤。

## 全新数据库

空数据库会先执行恢复后的 `V1.9.1.2`，再执行 `V1.9.1.9000`。初始化完成后运行预检，必须返回 `READY_CURRENT`。全新建库通过不能替代旧库升级验证。

## 实施验证记录（2026-09-11）

验证使用隔离的 MySQL 8.4、Flyway 11.15.0 和 Java 21，未连接常驻本地库或服务器数据库。

- 旧库路径：旧基线先成功执行 139 条 Migration，`V1.9.1.2` checksum 为 `1138237749`，且目标索引不存在；预检返回 `READY_UPGRADE`。修复版本 migrate 成功校验 140 条并执行 1 条补偿 Migration，随后严格 validate 通过。
- 新库路径：空库直接成功执行 140 条 Migration，随后严格 validate 通过。
- 一致性：两条路径的 `V1.9.1.2` checksum 均为 `1138237749`，`V1.9.1.9000` checksum 均为 `-215160370`，成功记录均为 140 条，目标索引均为单列 `create_time` 且仅有一个。
- SQL 边界：目标索引缺失时创建、正确存在时跳过、同名错误定义时因重复索引名失败。预检已覆盖旧 checksum、候选 checksum、未知 checksum、失败历史、失败补偿及索引异常。
- 应用启动：修复版本应用成功重新校验 140 条 Migration，确认 schema 无待执行项并启动 HTTP 服务；公钥接口返回正常业务响应。

该记录证明隔离新库和模拟旧库的兼容性，不代表任何真实环境已经升级，也不替代升级前备份与真实数据副本演练。
