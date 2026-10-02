# 客户数据表结构与外在引用

依据 `backend/crm/src/main/resources/migration` 中的建表与变更脚本，以及 `cn.cordys.crm.customer.domain` 实体整理。当前脚本**没有声明数据库外键**，下文连线都是按字段注释、索引和业务用法得到的逻辑引用。

时间字段均为毫秒时间戳（`BIGINT`）。`create_user` / `update_user` / `owner` / `follower` / `operator` / `user_id` 逻辑指向 `sys_user.id`。`organization_id` 逻辑指向 `sys_organization.id`。

`CustomerContactBlob`（`@Table(name = "customer_contact_blob")`）没有对应建表脚本，实际大文本表是 `customer_contact_field_blob`，因此不纳入图。

## 客户域内部关系

```mermaid
erDiagram
    customer_pool ||--o{ customer : "pool_id"
    customer_pool ||--o{ customer_pool_pick_rule : "pool_id"
    customer_pool ||--o{ customer_pool_recycle_rule : "pool_id"
    customer_pool ||--o{ customer_pool_hidden_field : "pool_id"

    customer ||--o{ customer_contact : "customer_id"
    customer ||--o{ customer_field : "resource_id"
    customer ||--o{ customer_field_blob : "resource_id"
    customer ||--o{ customer_collaboration : "customer_id"
    customer ||--o{ customer_owner : "customer_id"
    customer ||--o{ customer_relation : "source_customer_id"
    customer ||--o{ customer_relation : "target_customer_id"

    customer_contact ||--o{ customer_contact_field : "resource_id"
    customer_contact ||--o{ customer_contact_field_blob : "resource_id"

    customer_capacity }o--|| sys_organization : "organization_id"
```

`customer_capacity` 按组织与范围限制负责人库容，不直接挂在单条客户上。`customer_relation` 的两端都指向 `customer`，分别表示集团客户与子公司客户。

## 客户主数据

```mermaid
erDiagram
    customer {
        varchar id PK "主键"
        varchar name "客户名称"
        varchar owner "负责人，指向 sys_user"
        bigint collection_time "领取时间"
        varchar pool_id "公海 ID，可空"
        bit in_shared_pool "是否在公海，默认 0"
        varchar organization_id "组织 ID"
        varchar follower "最新跟进人"
        bigint follow_time "最新跟进时间"
        varchar reason_id "公海原因，指向 sys_dict"
        varchar create_user "创建人"
        varchar update_user "更新人"
        bigint create_time "创建时间"
        bigint update_time "更新时间"
    }
    customer_field {
        varchar id PK
        varchar resource_id "客户 ID"
        varchar field_id "自定义字段，指向 sys_module_field"
        varchar field_value "属性值，最长 255"
    }
    customer_field_blob {
        varchar id PK
        varchar resource_id "客户 ID"
        varchar field_id "自定义字段，指向 sys_module_field"
        text field_value "大文本属性值"
    }
    customer_owner {
        varchar id PK
        varchar customer_id "客户 ID"
        varchar owner "历史责任人"
        bigint collection_time "领取时间"
        bigint end_time "结束时间"
        varchar operator "操作人"
        varchar reason_id "公海原因，可空，1.2.1 新增"
    }
    customer_collaboration {
        varchar id PK
        varchar customer_id "客户 ID"
        varchar user_id "协作人，指向 sys_user"
        varchar collaboration_type "只读或协作"
        varchar create_user
        varchar update_user
        bigint create_time
        bigint update_time
    }
    customer_relation {
        varchar id PK
        varchar source_customer_id "集团客户"
        varchar target_customer_id "子公司客户"
        bigint create_time
    }
    customer ||--o{ customer_field : resource_id
    customer ||--o{ customer_field_blob : resource_id
    customer ||--o{ customer_owner : customer_id
    customer ||--o{ customer_collaboration : customer_id
    customer ||--o{ customer_relation : source_or_target
```

`customer.reason_id` 于 1.1.1 增加。索引：`organization_id`、`pool_id`、`follower`、`follow_time`、`reason_id`。`customer_field` 复合索引为 `(resource_id, field_id, field_value)`。

## 公海与库容

```mermaid
erDiagram
    customer_pool {
        varchar id PK
        text scope_id "可见范围 ID 列表，JSON"
        text owner_id "管理员 ID 列表，JSON"
        varchar organization_id
        varchar name "公海名称"
        bit enable "启用，默认 1"
        bit auto "自动回收，默认 0"
        varchar create_user
        varchar update_user
        bigint create_time
        bigint update_time
    }
    customer_pool_pick_rule {
        varchar id PK
        varchar pool_id
        bit limit_on_number "限制领取数量，默认 1"
        int pick_number "领取数量"
        bit limit_pre_owner "限制前归属人，默认 1"
        int pick_interval_days "领取间隔天数"
        bit limit_new "限制新数据，默认 0，1.1.1 新增"
        int new_pick_interval "新数据领取保护，1.1.1 新增"
        varchar create_user
        varchar update_user
        bigint create_time
        bigint update_time
    }
    customer_pool_recycle_rule {
        varchar id PK
        varchar pool_id
        varchar operator "操作符"
        text condition "回收条件"
        varchar create_user
        varchar update_user
        bigint create_time
        bigint update_time
    }
    customer_pool_hidden_field {
        varchar pool_id PK "公海池 ID"
        varchar field_id PK "字段 ID，指向 sys_module_field"
    }
    customer_capacity {
        varchar id PK
        varchar organization_id
        text scope_id "范围 ID 列表，JSON"
        int capacity "库容，空表示不限制"
        text filter "过滤条件，1.0.1 新增"
        varchar create_user
        varchar update_user
        bigint create_time
        bigint update_time
    }
    customer_pool ||--o{ customer_pool_pick_rule : pool_id
    customer_pool ||--o{ customer_pool_recycle_rule : pool_id
    customer_pool ||--o{ customer_pool_hidden_field : pool_id
```

`scope_id`、`owner_id` 存的是 JSON 数组，分别对应部门/人员范围和用户，不是单列外键。`customer_pool_hidden_field` 主键为 `(pool_id, field_id)`。

## 联系人

```mermaid
erDiagram
    customer_contact {
        varchar id PK
        varchar customer_id "客户 ID，1.2.3 起可空"
        varchar name "联系人姓名"
        varchar phone "电话"
        varchar owner "责任人"
        bit enable "是否停用，默认 0"
        varchar disable_reason "停用原因"
        varchar organization_id
        varchar create_user
        varchar update_user
        bigint create_time
        bigint update_time
    }
    customer_contact_field {
        varchar id PK
        varchar resource_id "联系人 ID"
        varchar field_id "自定义字段"
        varchar field_value
    }
    customer_contact_field_blob {
        varchar id PK
        varchar resource_id "联系人 ID"
        varchar field_id "自定义字段"
        text field_value
    }
    customer ||--o{ customer_contact : customer_id
    customer_contact ||--o{ customer_contact_field : resource_id
    customer_contact ||--o{ customer_contact_field_blob : resource_id
```

建表注释把 `customer_contact_field.resource_id` 写成了「客户 id」，查询与实体实际按联系人记录关联。索引：`customer_contact(customer_id, organization_id, phone)`。

## 外在引用

其他业务表通过 `customer_id`、`contact_id` 或线索转化字段指向客户域。发票、回款计划、回款记录、报价单不直接存客户 ID，而是经合同或商机间接到达客户。

```mermaid
erDiagram
    clue }o--o| customer : "transition_id 转化为客户"
    opportunity }o--o| customer : "customer_id 可空"
    opportunity }o--|| customer_contact : "contact_id"
    follow_up_record }o--o| customer : "customer_id 可空"
    follow_up_record }o--o| customer_contact : "contact_id 可空"
    follow_up_plan }o--o| customer : "customer_id 可空"
    follow_up_plan }o--o| customer_contact : "contact_id 可空"
    contract }o--|| customer : "customer_id"
    sales_order }o--o| customer : "customer_id 可空"
    sales_order }o--o| contract : "contract_id"
    opportunity ||--o{ opportunity_quotation : "opportunity_id"
    contract ||--o{ contract_invoice : "contract_id"
    contract ||--o{ contract_payment_plan : "contract_id"
    contract ||--o{ contract_payment_record : "contract_id"
```

| 外部表 | 引用列 | 指向 | 约束与索引 |
| --- | --- | --- | --- |
| `clue` | `transition_id` | `customer.id`（`transition_type` 表示转为客户时） | 可空，注释为客户或商机 ID |
| `opportunity` | `customer_id` | `customer.id` | 1.1.9 起可空；`idx_customer_id` |
| `opportunity` | `contact_id` | `customer_contact.id` | 建表为非空 |
| `follow_up_record` | `customer_id` / `contact_id` | 客户 / 联系人 | 均可空，各有索引；也可指向线索或商机 |
| `follow_up_plan` | `customer_id` / `contact_id` | 客户 / 联系人 | 均可空，各有索引 |
| `contract` | `customer_id` | `customer.id` | 非空；`idx_customer_id` |
| `sales_order` | `customer_id` | `customer.id` | 可空；`idx_customer_id`；同时可指向 `contract` |

间接路径：

- `opportunity_quotation.opportunity_id` → `opportunity.customer_id`
- `contract_invoice.contract_id` → `contract.customer_id`
- `contract_payment_plan.contract_id` → `contract.customer_id`
- `contract_payment_record.contract_id` → `contract.customer_id`

## 系统表引用

```mermaid
erDiagram
    sys_organization ||--o{ customer : organization_id
    sys_organization ||--o{ customer_pool : organization_id
    sys_organization ||--o{ customer_contact : organization_id
    sys_organization ||--o{ customer_capacity : organization_id
    sys_user ||--o{ customer : "owner / follower / create_user / update_user"
    sys_user ||--o{ customer_contact : owner
    sys_user ||--o{ customer_collaboration : user_id
    sys_user ||--o{ customer_owner : "owner / operator"
    sys_dict ||--o{ customer : reason_id
    sys_dict ||--o{ customer_owner : reason_id
    sys_module_field ||--o{ customer_field : field_id
    sys_module_field ||--o{ customer_field_blob : field_id
    sys_module_field ||--o{ customer_contact_field : field_id
    sys_module_field ||--o{ customer_contact_field_blob : field_id
    sys_module_field ||--o{ customer_pool_hidden_field : field_id
    sys_department ||--o{ customer_pool : "scope_id JSON"
    sys_department ||--o{ customer_capacity : "scope_id JSON"
```

`sys_attachment.resource_id` 与 `sys_operation_log.resource_id` 是按模块区分的多态资源 ID。客户、联系人附件和操作日志会写入这两张表，但列本身不专属于客户表。

库层维护客户自定义表单字段的正确做法见 [customer-module-form-ops.md](./customer-module-form-ops.md)。
