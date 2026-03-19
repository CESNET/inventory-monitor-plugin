# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [13.3.0] - 2026-03-19

### Breaking Changes

- **Date status indicators now require explicit configuration.** Warranty and
  Service status progress bars (on detail pages and in table columns) are no
  longer shown by default. You must configure `warning_days` in plugin settings
  to enable them. See [Configuration](#configuration) for details.

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
