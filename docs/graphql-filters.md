# GraphQL Filters

The plugin exposes all models via the NetBox GraphQL API at `/graphql/`. Every list query accepts a
`filters` argument.

## Filter field types

Lookup names come from `strawberry-django` and are **snake_case** — `i_contains`, not `icontains`.

| Field type | GraphQL type | Available lookups |
|---|---|---|
| CharField / TextField | `StrFilterLookup` | `exact`, `i_exact`, `contains`, `i_contains`, `starts_with`, `i_starts_with`, `ends_with`, `i_ends_with`, `regex`, `i_regex`, `in_list`, `is_null` |
| DateField | `DateFilterLookup` | `exact`, `gt`, `gte`, `lt`, `lte`, `range`, `in_list`, `is_null`, plus date parts (`year`, `month`, `day`, `week`, `quarter`, …) |
| DateTimeField | `DatetimeFilterLookup` | as `DateFilterLookup`, plus `date`, `time`, `hour`, `minute`, `second` |
| IntegerField | `IntFilterLookup` | `exact`, `gt`, `gte`, `lt`, `lte`, `range`, `in_list`, `is_null` |
| DecimalField | `DecimalFilterLookup` | as `IntFilterLookup` |
| BooleanField | `BoolFilterLookup` | `exact`, `is_null` |
| ForeignKey | the related model's filter | nest freely; a matching `<field>_id: ID` is also provided |

Every filter input also accepts `AND`, `OR`, `NOT` (nested filters) and `DISTINCT`.

## Contacts and ownership

`Asset`, `AssetService`, `Contract`, `Contractor`, `ExternalInventory`, `Invoice` and `RMA` support
both features and expose them as filters *and* output fields. `AssetType` and `Probe` do not.

| Filter | Type | Notes |
|---|---|---|
| `owner` | `OwnerFilter` | nest to reach `name`, `description`, `group`, `users`, `user_groups` |
| `owner_id` | `ID` | |
| `contacts` | `ContactAssignmentFilter` | nest to reach `contact`, `role`, `priority` |

There is no flat `owner_group` filter — filter by group by nesting through `owner`. NetBox core ships
no GraphQL owner filter at all, so `owner`/`owner_id` come from this plugin's
`inventory_monitor.graphql.filter_mixins.OwnerFilterMixin`.

## Example queries

### Filter assets by warranty date

```graphql
{
  inventory_monitor_asset_list(filters: { warranty_start: { gte: "2024-01-01" } }) {
    id
    partnumber
    warranty_start
  }
}
```

### Filter assets by part number (case-insensitive substring)

```graphql
{
  inventory_monitor_asset_list(filters: { partnumber: { i_contains: "sfp" } }) {
    id
    partnumber
    serial
  }
}
```

### Filter by owner

```graphql
{
  inventory_monitor_asset_list(
    filters: { owner: { name: { exact: "701 - Oddělení síťové infrastruktury" } } }
  ) {
    id
    serial
    owner { name group { name } }
  }
}
```

### Filter by owner group

Nest through `owner`; there is no flat `owner_group` filter.

```graphql
{
  inventory_monitor_external_inventory_list(
    filters: { owner: { group: { name: { exact: "NOC" } } } }
  ) {
    id
    inventory_number
  }
}
```

### Filter by assigned contact or contact role

```graphql
{
  inventory_monitor_external_inventory_list(
    filters: { contacts: { role: { name: { exact: "Owner" } } } }
  ) {
    id
    inventory_number
    contacts {
      contact { name email }
      role { name }
      priority
    }
  }
}
```

### Filter RMAs by serial number

```graphql
{
  inventory_monitor_rma_list(filters: { original_serial: { contains: "ABC" } }) {
    id
    original_serial
    replacement_serial
  }
}
```

### Combine filters

Sibling filters are combined with AND. Use `OR` / `NOT` for anything else.

```graphql
{
  inventory_monitor_contract_list(filters: {
    invoicing_start: { gte: "2023-01-01" }
    name: { i_contains: "support" }
  }) {
    id
    name
    invoicing_start
    invoicing_end
  }
}
```

`OR` and `NOT` take a **single** nested filter object, not a list — chain them for more terms.

```graphql
{
  inventory_monitor_asset_list(filters: {
    vendor: { exact: "Cisco" }
    OR: { vendor: { exact: "Juniper" } }
  }) {
    id
    serial
    vendor
  }
}
```

## Available list queries

| Query | Model | Contacts / Ownership |
|---|---|---|
| `inventory_monitor_asset_list` | Asset | yes |
| `inventory_monitor_asset_type_list` | AssetType | no |
| `inventory_monitor_asset_service_list` | AssetService | yes |
| `inventory_monitor_contract_list` | Contract | yes |
| `inventory_monitor_contractor_list` | Contractor | yes |
| `inventory_monitor_invoice_list` | Invoice | yes |
| `inventory_monitor_probe_list` | Probe | no |
| `inventory_monitor_rma_list` | RMA | yes |
| `inventory_monitor_external_inventory_list` | ExternalInventory | yes |
