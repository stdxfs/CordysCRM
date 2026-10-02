# 客户自定义表单：库层配置正确做法

面向本 Fork 在 MariaDB 上维护客户模块表单（`form_key=customer`）时的操作约定。优先使用系统「表单设计」UI 保存；必须改库时按本文执行。

## 1. 数据落在哪

| 用途 | 表 | 要点 |
| --- | --- | --- |
| 表单头 | `sys_module_form` | `form_key='customer'` + `organization_id` 定位一张表单 |
| 表单布局等 | `sys_module_form_blob` | `id = form.id`，`prop` 为表单级 JSON |
| 字段元数据 | `sys_module_field` | `form_id`、`name`、`type`、`internal_key`、`pos`、`mobile` |
| 字段完整配置 | `sys_module_field_blob` | **`id` 与 `sys_module_field.id` 相同**；`prop` 为字段整份 JSON |
| 客户填写值 | `customer_field` / `customer_field_blob` | `resource_id=customer.id`，`field_id=字段 id` |

前端/接口读配置时以 **`sys_module_field_blob.prop`** 为准（含展示名、选项、显隐、校验等）。`sys_module_field.name` 须与 `prop.name` 保持一致。

标准业务列（如名称、负责人）由 `BusinessModuleField` 映射到 `customer` 主表；其余自定义值进 `customer_field*`。

## 2. 选项字段：必须同时维护两份

`SELECT` / `SELECT_MULTIPLE` / `RADIO` / `CHECKBOX` 在 `optionSource` 为空或为 `custom` 时，运行时逻辑（`ModuleFormService.setFieldRefOption`）为：

- 若 `customOptions` **非空** → 用 `customOptions` **覆盖** `options` 再下发；
- 若 `customOptions` 为空 → 用 `options` 回填 `customOptions`。

因此改选项时正确做法是：

```text
prop.options = <新选项>
prop.customOptions = <同一份新选项>
prop.optionSource = 'custom'
```

只改 `options` 不改 `customOptions` 时，页面仍会显示旧选项。

`defaultValue` 必须落在当前选项的 `value` 集合内；无默认值时显式设为 `null`，避免「选项不存在」。

## 3. 显隐与按类型必填

产品没有「条件必填」独立配置。正确组合是：

1. 用 `SELECT`/`RADIO` 作控制字段（如 `customerEntityType`：`person` / `agency`）；
2. 在该字段 `prop.showControlRules` 上配置：某 `value` → 要显示的 `fieldIds` 列表；
3. 各分支专用字段在自身 `prop.rules` 中带 `{ "key": "required" }`；
4. 未命中显隐规则的字段不渲染，前端一般不会校验其必填。

`showControlRules` 结构：

```json
[
  { "value": "person", "fieldIds": ["<字段id>", "..."] },
  { "value": "agency", "fieldIds": ["<字段id>", "..."] }
]
```

控制字段上若还有「来源 → 线上详情」这类显隐，`value` 必须与**当前** `options`/`customOptions` 的 `value` 一致（例如 `xhs`，而不是历史遗留的 `"1"`）。

## 4. 增删改字段定义

### 新增

同一事务内成对插入，**两侧 id 相同**：

1. `INSERT sys_module_field`（含 `form_id`、`pos`、`type`、`internal_key`、`name`…）
2. `INSERT sys_module_field_blob`（`prop` 含完整配置，且 `prop.id`/`prop.pos`/`prop.type`/`prop.name`/`prop.internalKey` 与行数据一致）

`id` 使用应用侧雪花字符串（`IDGenerator.nextStr()` 同类），全局唯一。已有客户数据依赖的字段 **不要更换 id**。

### 修改

- 改名、类型、排序、移动端：同步更新 `sys_module_field` **与** `prop` 内对应字段。
- 改选项/显隐/校验：更新 `prop`；选项类同步 `options` 与 `customOptions`。
- 调整 `pos` 时顺延同表单其他字段，并写回各字段 `prop.pos`。

### 删除

1. 删除 `customer_field` / `customer_field_blob` 中该 `field_id` 的实例值  
2. 从其他字段的 `showControlRules` / `linkProp` 中移除对该 id 的引用  
3. 删除 `sys_module_field_blob`、`sys_module_field`  
4. 检查公海隐藏字段、视图条件等是否仍引用该 id  

官方 UI 保存表单时是「该表单字段全删再按保留的 id 全量插入」；库层做增量时务必保留已有字段 id。

## 5. 中文与 SQL 写入

含中文的 `prop` / `name` 不要经「默认 `json.dumps` + shell `-e`」多层转义。正确做法：

1. 本地用 UTF-8 写好 `.sql`（`SET NAMES utf8mb4;`）  
2. `docker cp` 进容器  
3. `mysql --default-character-set=utf8mb4 < file.sql`  

或在应用内用官方保存 API / `ModuleFormCacheService`，由框架序列化。

校验：`prop.name`、选项 `label`、分割线标题等须为可读中文，且与 `sys_module_field.name` 一致。

## 6. 缓存

配置缓存在 Redis：

- `form_cache::{organizationId}:customer`
- `field_cache::{organizationId}:customer`

改库后必须删除对应 key（或重启应用）再验收 UI。仅改库不失效缓存时，页面会继续用旧配置。

本环境内置 Redis 常见密码见 `installer/conf/cordys-crm.properties`（`CordysCRM@redis`）。

## 7. 推荐操作顺序

1. 备份：`sys_module_field`、`sys_module_field_blob`、以及相关 `customer_field*`  
2. 事务内改定义（成对、保 id、选项双写、显隐 value 对齐）  
3. 提交后清 `form_cache` / `field_cache`  
4. 浏览器强刷后验收：选项文案、默认值、主体分流显隐、来源→线上详情显隐、必填  

## 8. 本环境客户表单锚点（100001）

| 项 | 值 |
| --- | --- |
| `organization_id` | `100001` |
| `form_id` | `459878125661069319` |
| 主体字段 | `internal_key=customerEntityType`，id `179087151044900001` |
| 主体取值 | `person` / `agency` |

自然人 / 代理公司专用字段及 `showControlRules` 挂在主体字段上；公共字段（名称、行业、等级、来源、标签、地区、负责人等）两侧共用。

## 9. 验收要点

- 选项下拉为新中文文案，无旧码旧标签  
- 客户主体切换后，仅对应分支字段显示且必填生效  
- 来源选小红书/抖音/视频号/私域微信时，出现「线上来源详情」  
- `SELECT prop FROM sys_module_field_blob` 中无 `u4e00` 这类缺反斜杠的伪 Unicode 串  
