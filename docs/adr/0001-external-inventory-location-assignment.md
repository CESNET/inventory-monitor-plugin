# ADR 0001: External Inventory placement via a generic relation on the model

Date: 2026-11-05
Status: Accepted

## Context

External Inventory records carry a free-text `location` / `location_code` from the external
system. Operators want to see, on a NetBox Site (or Region/Location) page, which external items
sit there, and to filter "everything under this site". NetBox itself has no way to show that
for a plugin model, so the link between an item and a dcim object has to live somewhere.

Three options were on the table:

1. **Custom fields on External Inventory** of type `object`, one per target model (`region`,
   `site`, `location`), with the reverse view provided by the separately installed
   `netbox-cf-backrefs` plugin. No schema change, but three fields where one relation is meant,
   a generic reverse tab whose columns the plugin cannot control, and a dependency on another
   plugin being installed and configured on every instance.
2. **A Custom Object type** mirroring the external location table, related to dcim objects and to
   External Inventory. Makes external locations first-class in NetBox, but means syncing a second
   object type and still gives no native view on the Site page.
3. **A `GenericForeignKey` on the model**, exactly like `Asset.assigned_object`, limited to
   Region/Site/Location, plus a plugin-owned tab on those dcim pages and hierarchical filters.

## Decision

Option 3. `ExternalInventory.location_assigned_object` (`location_assigned_object_type` /
`location_assigned_object_id`) is a generic relation restricted to `dcim.region`, `dcim.site`
and `dcim.location`. One shared helper (`helpers.location_assignment_q`) defines what "under
this object" means, and both the dcim tabs and the `region_id` / `site_id` / `location_id`
filters use it.

The free-text `location` and `location_code` stay untouched: they are the external system's own
value, the relation is NetBox's interpretation of it. How the mapping is decided (by hand, by an
importer, from custom fields on the dcim objects) is outside the plugin.

## Consequences

- One migration (`0009`) and a plugin release; instances must upgrade before an importer can
  write the relation.
- The model stays generic: nothing in it names a specific external system.
- Device/rack placement is deliberately not a target here; that is what the linked
  `Asset.assigned_object` already expresses.
- Reversing this later means a data migration back to custom fields; the cost is why the choice
  is recorded.
