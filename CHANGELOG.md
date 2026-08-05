# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [13.5.0] - 2026-08-05

### Added

- **Color-coded Service End and Warranty End dates.** The `Service End` and
  `Warranty End` columns in asset tables (and `Service End` in asset service
  tables) now render each date as a badge — **red** when the date has passed,
  **orange** when it falls within the configured warning window, **green**
  when it is further out or open-ended. Hovering a badge shows the same
  human-readable message as the status bars ("Expired 11 years ago",
  "Expires in 45 days"). Assets with several services get one badge per
  service, aligned with the `Service Start` and `Service Status` columns. A
  service with no end date is open-ended coverage and shows a green `∞` badge;
  an unset `Warranty End` is missing data and keeps the usual placeholder. (#22)
- Asset type badges in the asset table now pick black or white text based on
  the type color, using NetBox's `fgcolor` filter. Dark type colors such as
  blue or purple were previously unreadable. (#22)
- **`Service Status` and `Warranty Status` filters** on the Asset list, matching
  the color bands above: *Expired* / *Expiring soon* / *Valid* / *No service
  records* (*Not set* for warranty). Both are multi-select and return the union
  of the selected bands. Service Status uses any-match semantics — an asset with
  one expired and one valid service appears under both. Available in the UI and
  over REST (`?service_status=expired`). (#22)

### Fixed

- Date status messages said "Expired in 0 days" for a date falling on today.
  They now read "Expired today" / "Expires today". This also affects the
  existing Service, Warranty and Invoicing status bars.

### Changed

- **`warning_days` now falls back to defaults** (`service: 60`, `warranty: 60`,
  `invoicing: 30`) when a key is not configured, so color indicators work out of
  the box. Previously a missing key meant no colors at all. **Deployments that
  relied on omitting `warning_days` to suppress color indicators will now see
  them** — set the key explicitly to `None` (e.g. `"warning_days": {"service":
  None}`) to keep them off.

## [13.4.1] - 2026-06-18

### Fixed

- Added the missing `currency` field to the Invoice REST API serializer
  (`InvoiceSerializer`). The field existed on the model, form, table, and
  filterset but was absent from the API, so invoice currency could not be
  read or written via REST/GraphQL. (#8)

## [13.4.0] - 2026-05-11

### Changed

- Expanded NetBox compatibility window to **4.5.4 – 4.6.99**. The plugin now
  installs on NetBox 4.6.x (Django 6.0) in addition to 4.5.x. No functional or
  API changes — verified that all NetBox APIs used by the plugin
  (`NetBoxModel`, `NetBoxModelForm`, `NetBoxTable`, `NetBoxModelFilterSet`,
  `NetBoxModelSerializer`, `PluginTemplateExtension.models`, `ObjectType`,
  `RestrictedQuerySet`, `ChoiceSet`) remain stable across both versions.
- Widened `django` dependency pin to `>=5.0,<7.0` so the pip resolver accepts
  the Django 6.0 shipped with NetBox 4.6.

## [13.3.0] - 2026-03-19

### Breaking Changes

- **Date status indicators now require explicit configuration.** Warranty and
  Service status progress bars (on detail pages and in table columns) are no
  longer shown by default. You must configure `warning_days` in plugin settings
  to enable color-coded progress bars. Without configuration, status columns
  fall back to displaying the date range (e.g. `2025-03-19 — 2026-12-19`)
  instead of a placeholder dash. See [Configuration](#configuration) for details.

### Added

- **"Assets (Service Contract)" tab on Contract detail page:** New tab displays
  assets linked to the contract through asset services (AssetService), complementing
  the existing "Assets (Order Contract)" tab which shows directly ordered assets.
  Includes a "Show only active services" toggle to filter out assets whose services
  have expired (service_end < today). Supports full table configuration and filtering
  via the standard Asset filterset.

- **Configurable color-coded status columns:** New "Service Status", "Warranty
  Status", and "Invoicing Status" columns with progress bar indicators
  (red = expired, orange = expiring within threshold, green = valid, blue =
  future start). Hover tooltip shows the date range. Date columns (start/end)
  remain as plain text. Available on Asset, Contract, and Invoice tables.
  Requires `warning_days` config — each attribute is independently configurable.

- **"Service Start" column in asset tables:** New column showing service start
  dates alongside the existing "Service End" column.

- **Humanized time deltas:** Status progress bars now show "3 months ago",
  "2 years ago" instead of raw day counts for large durations
  (< 90 days → days, < 2 years → months, 2+ years → years).

- **Invoicing status for Contract and Invoice models:** New `DateStatusMixin`
  on Contract and Invoice with `get_invoicing_status()` method. New
  "Invoicing Status" column available in Contract and Invoice tables.

### Changed

- **Default table columns updated:** Status columns (`warranty_status`,
  `services_status`, `invoicing_status`, `service_status`) are now shown by
  default. Start/end date columns remain available via Configure Table.

- **Consistent date format:** All date displays in the plugin now use
  `YYYY-MM-DD` format (previously some used `YYYY-M-DD` without leading zero).

## [13.2.0] - 2026-03-19

### Added

- **Asset "Has Duplicates" filter:** New boolean filter on the Asset list view
  (UI filter form and REST API) that identifies assets with duplicate serial
  numbers. Useful for data hygiene — quickly find assets that were accidentally
  entered more than once. Supports three states: Yes (show only duplicates),
  No (show only unique serials), All (no filtering).

## [13.1.1] - 2026-03-19

### Fixed

- **AssetService CSV import:** Asset lookup now uses `serial` field instead of
  primary key. Previously, importing asset-services via CSV with serial numbers
  (e.g. `ABCDE39H1AC`) failed with "Object not found" because the form
  attempted to match the value against the numeric primary key.

## [13.1.0] - 2026-03-06

> **Requires NetBox >= 4.5.4** (strawberry-graphql-django >= 0.79.0).
> NetBox 4.5.0–4.5.3 is **not supported** by this release.

### Breaking Changes

- **Minimum NetBox version raised to 4.5.4.** The GraphQL layer now uses
  `StrFilterLookup` (introduced in strawberry-graphql-django 0.79.0, shipped with
  NetBox 4.5.4). Installations running NetBox 4.5.0–4.5.3 will fail to start.
  Use inventory-monitor v13.0.x for those versions.

- **GraphQL filter types changed.** All `CharField`/`TextField` filter fields
  migrated from `FilterLookup[str]` to `StrFilterLookup[str]`. This eliminates
  `DuplicatedTypeName` schema errors introduced in strawberry-graphql-django 0.79.0.
  Custom GraphQL clients or tooling that relied on the old `FilterLookup` type name
  in introspection results may need updating.

### Added

- **Optional [netbox-attachments](https://github.com/Kani999/netbox-attachments)
  integration** (re-introduced; requires netbox-attachments >= 11.0.0).
  - Enable with `enable_netbox_attachments: True` in plugin config (default: `False`).
  - Adds attachment counts to Contract and Invoice list views.
  - Plugin starts normally without netbox-attachments installed when the setting
    is disabled. See `docs/netbox-attachments.md` for setup instructions.
  - Note: versions 13.0.x had no netbox-attachments support.
    If you used netbox-attachments with inventory-monitor 12.x, upgrade
    netbox-attachments to >= 11.0.0 before enabling this setting.

### Fixed

- Removed undocumented cross-column `serial` GraphQL filter from RMA documentation.
  The filter had no resolver and would raise a runtime error when queried.
  Use `original_serial` or `replacement_serial` filters instead.

## [13.0.x]

See git history for changes in the 13.0.x series.
