# GraphQL Filters

The plugin exposes all models via the NetBox GraphQL API at `/graphql/`. Every list query accepts a `filters` argument.

## Filter field types

| Field type | GraphQL type | Available lookups |
|---|---|---|
| CharField / TextField | `StrFilterLookup` | `exact`, `contains`, `icontains`, `startswith`, `endswith`, `in` |
| DateField | `DateFilterLookup` | `exact`, `gt`, `gte`, `lt`, `lte`, `in` |
| DateTimeField | `DatetimFilterLookup` | `exact`, `gt`, `gte`, `lt`, `lte`, `in` |
| IntegerField / DecimalField | `IntFilterLookup` / `DecimalFilterLookup` | `exact`, `gt`, `gte`, `lt`, `lte`, `in` |
| Custom cross-column | `StrBaseFilterLookup` | `exact`, `gt`, `gte`, `lt`, `lte`, `in` |

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

### Filter assets by part number (string contains)

```graphql
{
  inventory_monitor_asset_list(filters: { partnumber: { contains: "SFP" } }) {
    id
    partnumber
    serial
  }
}
```

### Filter RMAs by serial number (cross-column exact match)

The `serial` filter searches across both `original_serial` and `replacement_serial` at once. Only `exact` is supported; for partial matches use the individual fields.

```graphql
{
  inventory_monitor_rma_list(filters: { serial: { exact: "ABC123" } }) {
    id
    original_serial
    replacement_serial
  }
}
```

For partial matching on individual serial fields:

```graphql
{
  inventory_monitor_rma_list(filters: { original_serial: { contains: "ABC" } }) {
    id
    original_serial
    replacement_serial
  }
}
```

### Filter contracts by date range and name

Multiple filters are combined with AND logic.

```graphql
{
  inventory_monitor_contract_list(filters: {
    invoicing_start: { gte: "2023-01-01" }
    name: { contains: "support" }
  }) {
    id
    name
    invoicing_start
    invoicing_end
  }
}
```

## Available list queries

| Query | Model |
|---|---|
| `inventory_monitor_asset_list` | Asset |
| `inventory_monitor_asset_type_list` | AssetType |
| `inventory_monitor_asset_service_list` | AssetService |
| `inventory_monitor_contract_list` | Contract |
| `inventory_monitor_contractor_list` | Contractor |
| `inventory_monitor_invoice_list` | Invoice |
| `inventory_monitor_probe_list` | Probe |
| `inventory_monitor_rma_list` | RMA |
| `inventory_monitor_external_inventory_list` | ExternalInventory |
