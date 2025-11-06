from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.filter_mixins import NetBoxModelFilterMixin
from strawberry.scalars import ID
from strawberry_django import FilterLookup

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from dcim.graphql.filters import (
        DeviceFilter,
        LocationFilter,
        SiteFilter,
    )
    from tenancy.graphql.filters import TenantFilter

    # Import the enum types
    from .enums import (
        InventoryMonitorAssignmentStatusEnum,
        InventoryMonitorContractTypeEnum,
        InventoryMonitorLifecycleStatusEnum,
        InventoryMonitorRMAStatusEnum,
    )

from inventory_monitor.models import (
    RMA,
    Asset,
    AssetService,
    AssetType,
    Contract,
    Contractor,
    ExternalInventory,
    Invoice,
    Probe,
)

__all__ = (
    "InventoryMonitorExternalInventoryFilter",
    "InventoryMonitorAssetFilter",
    "InventoryMonitorAssetTypeFilter",
    "InventoryMonitorAssetServiceFilter",
    "InventoryMonitorContractFilter",
    "InventoryMonitorContractorFilter",
    "InventoryMonitorInvoiceFilter",
    "InventoryMonitorProbeFilter",
    "InventoryMonitorRMAFilter",
)


@strawberry_django.filter_type(ExternalInventory, lookups=True)
class InventoryMonitorExternalInventoryFilter(NetBoxModelFilterMixin):
    external_id: FilterLookup[str] | None = strawberry_django.filter_field()
    inventory_number: FilterLookup[str] | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    serial_number: FilterLookup[str] | None = strawberry_django.filter_field()
    person_id: FilterLookup[str] | None = strawberry_django.filter_field()
    person_name: FilterLookup[str] | None = strawberry_django.filter_field()
    location_code: FilterLookup[str] | None = strawberry_django.filter_field()
    location: FilterLookup[str] | None = strawberry_django.filter_field()
    department_code: FilterLookup[str] | None = strawberry_django.filter_field()
    project_code: FilterLookup[str] | None = strawberry_django.filter_field()
    user_name: FilterLookup[str] | None = strawberry_django.filter_field()
    user_note: FilterLookup[str] | None = strawberry_django.filter_field()
    split_asset: FilterLookup[str] | None = strawberry_django.filter_field()
    status: FilterLookup[str] | None = strawberry_django.filter_field()

    # Relationship filters
    assets: Annotated["InventoryMonitorAssetFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    asset_id: ID | None = strawberry_django.filter_field()

    # Custom filter for has_assets (boolean filter)
    has_assets: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Asset, lookups=True)
class InventoryMonitorAssetFilter(NetBoxModelFilterMixin):
    # Basic identification filters
    partnumber: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()

    # Status filters - use Union for proper type annotation
    assignment_status: (
        Annotated["InventoryMonitorAssignmentStatusEnum", strawberry.lazy("inventory_monitor.graphql.enums")] | None
    ) = strawberry_django.filter_field()
    lifecycle_status: (
        Annotated["InventoryMonitorLifecycleStatusEnum", strawberry.lazy("inventory_monitor.graphql.enums")] | None
    ) = strawberry_django.filter_field()

    # Additional information filters
    project: FilterLookup[str] | None = strawberry_django.filter_field()
    vendor: FilterLookup[str] | None = strawberry_django.filter_field()

    # Numeric filters
    quantity: FilterLookup[int] | None = strawberry_django.filter_field()
    price: FilterLookup[str] | None = strawberry_django.filter_field()  # DecimalField
    currency: FilterLookup[str] | None = strawberry_django.filter_field()

    # Date filters
    warranty_start: FilterLookup[str] | None = strawberry_django.filter_field()
    warranty_end: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related object filters
    type: Annotated["InventoryMonitorAssetTypeFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    type_id: ID | None = strawberry_django.filter_field()

    order_contract: (
        Annotated["InventoryMonitorContractFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    order_contract_id: ID | None = strawberry_django.filter_field()

    # Assignment filters (GenericForeignKey)
    assigned_object_type: Annotated["ContentTypeFilter", strawberry.lazy("core.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_id: FilterLookup[int] | None = strawberry_django.filter_field()

    # Relationship filters back to External Inventory
    external_inventory_items: (
        Annotated["InventoryMonitorExternalInventoryFilter", strawberry.lazy("inventory_monitor.graphql.filters")]
        | None
    ) = strawberry_django.filter_field()
    external_inventory_item_id: FilterLookup[ID] | None = strawberry_django.filter_field()

    # Custom boolean filter
    has_external_inventory_items: FilterLookup[bool] | None = strawberry_django.filter_field()

    # External Inventory number filter (related field)
    external_inventory_number: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(AssetType, lookups=True)
class InventoryMonitorAssetTypeFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    color: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(AssetService, lookups=True)
class InventoryMonitorAssetServiceFilter(NetBoxModelFilterMixin):
    service_start: FilterLookup[str] | None = strawberry_django.filter_field()
    service_end: FilterLookup[str] | None = strawberry_django.filter_field()
    service_price: FilterLookup[str] | None = strawberry_django.filter_field()
    service_currency: FilterLookup[str] | None = strawberry_django.filter_field()
    service_category: FilterLookup[str] | None = strawberry_django.filter_field()
    service_category_vendor: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related object filters
    asset: Annotated["InventoryMonitorAssetFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    asset_id: ID | None = strawberry_django.filter_field()

    contract: (
        Annotated["InventoryMonitorContractFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    contract_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Contract, lookups=True)
class InventoryMonitorContractFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    name_internal: FilterLookup[str] | None = strawberry_django.filter_field()
    type: Annotated["InventoryMonitorContractTypeEnum", strawberry.lazy("inventory_monitor.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    price: FilterLookup[str] | None = strawberry_django.filter_field()
    currency: FilterLookup[str] | None = strawberry_django.filter_field()
    signed: FilterLookup[str] | None = strawberry_django.filter_field()
    accepted: FilterLookup[str] | None = strawberry_django.filter_field()
    invoicing_start: FilterLookup[str] | None = strawberry_django.filter_field()
    invoicing_end: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related object filters
    contractor: (
        Annotated["InventoryMonitorContractorFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    contractor_id: ID | None = strawberry_django.filter_field()

    parent: Annotated["InventoryMonitorContractFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    parent_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Contractor, lookups=True)
class InventoryMonitorContractorFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    company: FilterLookup[str] | None = strawberry_django.filter_field()
    address: FilterLookup[str] | None = strawberry_django.filter_field()

    # Tenant filter
    tenant: Annotated["TenantFilter", strawberry.lazy("tenancy.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Invoice, lookups=True)
class InventoryMonitorInvoiceFilter(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    name_internal: FilterLookup[str] | None = strawberry_django.filter_field()
    project: FilterLookup[str] | None = strawberry_django.filter_field()
    price: FilterLookup[str] | None = strawberry_django.filter_field()
    invoicing_start: FilterLookup[str] | None = strawberry_django.filter_field()
    invoicing_end: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related contract filter
    contract: (
        Annotated["InventoryMonitorContractFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    contract_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Probe, lookups=True)
class InventoryMonitorProbeFilter(NetBoxModelFilterMixin):
    # Note: Probe doesn't inherit from NetBoxModel, so it might need different handling
    # You may need to adjust this based on your actual Probe model

    time: FilterLookup[str] | None = strawberry_django.filter_field()
    creation_time: FilterLookup[str] | None = strawberry_django.filter_field()
    device_descriptor: FilterLookup[str] | None = strawberry_django.filter_field()
    site_descriptor: FilterLookup[str] | None = strawberry_django.filter_field()
    location_descriptor: FilterLookup[str] | None = strawberry_django.filter_field()
    part: FilterLookup[str] | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
    category: FilterLookup[str] | None = strawberry_django.filter_field()

    # DCIM relationship filters
    device: Annotated["DeviceFilter", strawberry.lazy("dcim.graphql.filters")] | None = strawberry_django.filter_field()
    device_id: ID | None = strawberry_django.filter_field()

    site: Annotated["SiteFilter", strawberry.lazy("dcim.graphql.filters")] | None = strawberry_django.filter_field()
    site_id: ID | None = strawberry_django.filter_field()

    location: Annotated["LocationFilter", strawberry.lazy("dcim.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    location_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(RMA, lookups=True)
class InventoryMonitorRMAFilter(NetBoxModelFilterMixin):
    rma_number: FilterLookup[str] | None = strawberry_django.filter_field()
    original_serial: FilterLookup[str] | None = strawberry_django.filter_field()
    replacement_serial: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated["InventoryMonitorRMAStatusEnum", strawberry.lazy("inventory_monitor.graphql.enums")] | None = (
        strawberry_django.filter_field()
    )
    date_issued: FilterLookup[str] | None = strawberry_django.filter_field()
    date_replaced: FilterLookup[str] | None = strawberry_django.filter_field()

    # Related asset filter
    asset: Annotated["InventoryMonitorAssetFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    asset_id: ID | None = strawberry_django.filter_field()

    # Custom filter for both serials (like in Django filterset)
    serial: FilterLookup[str] | None = strawberry_django.filter_field()
