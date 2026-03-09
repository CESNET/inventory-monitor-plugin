from decimal import Decimal
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from netbox.graphql.filters import NetBoxModelFilter
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, FilterLookup, StrFilterLookup

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
class InventoryMonitorExternalInventoryFilter(NetBoxModelFilter):
    external_id: StrFilterLookup[str] | None = strawberry_django.filter_field()
    inventory_number: StrFilterLookup[str] | None = strawberry_django.filter_field()
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    serial_number: StrFilterLookup[str] | None = strawberry_django.filter_field()
    person_id: StrFilterLookup[str] | None = strawberry_django.filter_field()
    person_name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    location_code: StrFilterLookup[str] | None = strawberry_django.filter_field()
    location: StrFilterLookup[str] | None = strawberry_django.filter_field()
    department_code: StrFilterLookup[str] | None = strawberry_django.filter_field()
    project_code: StrFilterLookup[str] | None = strawberry_django.filter_field()
    user_name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    user_note: StrFilterLookup[str] | None = strawberry_django.filter_field()
    split_asset: StrFilterLookup[str] | None = strawberry_django.filter_field()
    status: StrFilterLookup[str] | None = strawberry_django.filter_field()

    # Relationship filters
    assets: Annotated["InventoryMonitorAssetFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    asset_id: ID | None = strawberry_django.filter_field()

    # Custom filter for has_assets (boolean filter)
    has_assets: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Asset, lookups=True)
class InventoryMonitorAssetFilter(NetBoxModelFilter):
    # Basic identification filters
    partnumber: StrFilterLookup[str] | None = strawberry_django.filter_field()
    description: StrFilterLookup[str] | None = strawberry_django.filter_field()
    serial: StrFilterLookup[str] | None = strawberry_django.filter_field()

    # Status filters - use BaseFilterLookup for enum fields (NetBox 4.5+ requirement)
    assignment_status: (
        BaseFilterLookup[
            Annotated["InventoryMonitorAssignmentStatusEnum", strawberry.lazy("inventory_monitor.graphql.enums")]  # type: ignore
        ]
        | None
    ) = strawberry_django.filter_field()
    lifecycle_status: (
        BaseFilterLookup[
            Annotated["InventoryMonitorLifecycleStatusEnum", strawberry.lazy("inventory_monitor.graphql.enums")]  # pyright: ignore[reportInvalidTypeForm]
        ]
        | None
    ) = strawberry_django.filter_field()

    # Additional information filters
    project: StrFilterLookup[str] | None = strawberry_django.filter_field()
    vendor: StrFilterLookup[str] | None = strawberry_django.filter_field()

    # Numeric filters
    quantity: FilterLookup[int] | None = strawberry_django.filter_field()
    price: FilterLookup[Decimal] | None = strawberry_django.filter_field()  # DecimalField
    currency: StrFilterLookup[str] | None = strawberry_django.filter_field()

    # Date filters
    warranty_start: strawberry.auto = strawberry_django.filter_field()
    warranty_end: strawberry.auto = strawberry_django.filter_field()

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
    external_inventory_number: BaseFilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(AssetType, lookups=True)
class InventoryMonitorAssetTypeFilter(NetBoxModelFilter):
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    slug: StrFilterLookup[str] | None = strawberry_django.filter_field()
    description: StrFilterLookup[str] | None = strawberry_django.filter_field()
    color: StrFilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(AssetService, lookups=True)
class InventoryMonitorAssetServiceFilter(NetBoxModelFilter):
    service_start: strawberry.auto = strawberry_django.filter_field()
    service_end: strawberry.auto = strawberry_django.filter_field()
    service_price: FilterLookup[Decimal] | None = strawberry_django.filter_field()
    service_currency: StrFilterLookup[str] | None = strawberry_django.filter_field()
    service_category: StrFilterLookup[str] | None = strawberry_django.filter_field()
    service_category_vendor: StrFilterLookup[str] | None = strawberry_django.filter_field()

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
class InventoryMonitorContractFilter(NetBoxModelFilter):
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    name_internal: StrFilterLookup[str] | None = strawberry_django.filter_field()
    type: (
        BaseFilterLookup[
            Annotated["InventoryMonitorContractTypeEnum", strawberry.lazy("inventory_monitor.graphql.enums")]  # pyright: ignore[reportInvalidTypeForm]
        ]
        | None
    ) = strawberry_django.filter_field()
    price: FilterLookup[Decimal] | None = strawberry_django.filter_field()
    currency: StrFilterLookup[str] | None = strawberry_django.filter_field()
    signed: strawberry.auto = strawberry_django.filter_field()
    accepted: strawberry.auto = strawberry_django.filter_field()
    invoicing_start: strawberry.auto = strawberry_django.filter_field()
    invoicing_end: strawberry.auto = strawberry_django.filter_field()

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
class InventoryMonitorContractorFilter(NetBoxModelFilter):
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    company: StrFilterLookup[str] | None = strawberry_django.filter_field()
    address: StrFilterLookup[str] | None = strawberry_django.filter_field()

    # Tenant filter
    tenant: Annotated["TenantFilter", strawberry.lazy("tenancy.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Invoice, lookups=True)
class InventoryMonitorInvoiceFilter(NetBoxModelFilter):
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    name_internal: StrFilterLookup[str] | None = strawberry_django.filter_field()
    project: StrFilterLookup[str] | None = strawberry_django.filter_field()
    price: FilterLookup[Decimal] | None = strawberry_django.filter_field()
    invoicing_start: strawberry.auto = strawberry_django.filter_field()
    invoicing_end: strawberry.auto = strawberry_django.filter_field()

    # Related contract filter
    contract: (
        Annotated["InventoryMonitorContractFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None
    ) = strawberry_django.filter_field()
    contract_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(Probe, lookups=True)
class InventoryMonitorProbeFilter(NetBoxModelFilter):
    # Note: Probe doesn't inherit from NetBoxModel, so it might need different handling
    # You may need to adjust this based on your actual Probe model

    time: strawberry.auto = strawberry_django.filter_field()
    creation_time: strawberry.auto = strawberry_django.filter_field()
    device_descriptor: StrFilterLookup[str] | None = strawberry_django.filter_field()
    site_descriptor: StrFilterLookup[str] | None = strawberry_django.filter_field()
    location_descriptor: StrFilterLookup[str] | None = strawberry_django.filter_field()
    part: StrFilterLookup[str] | None = strawberry_django.filter_field()
    name: StrFilterLookup[str] | None = strawberry_django.filter_field()
    serial: StrFilterLookup[str] | None = strawberry_django.filter_field()
    category: StrFilterLookup[str] | None = strawberry_django.filter_field()

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
class InventoryMonitorRMAFilter(NetBoxModelFilter):
    rma_number: StrFilterLookup[str] | None = strawberry_django.filter_field()
    original_serial: StrFilterLookup[str] | None = strawberry_django.filter_field()
    replacement_serial: StrFilterLookup[str] | None = strawberry_django.filter_field()
    status: (
        BaseFilterLookup[Annotated["InventoryMonitorRMAStatusEnum", strawberry.lazy("inventory_monitor.graphql.enums")]]  # pyright: ignore[reportInvalidTypeForm]
        | None
    ) = strawberry_django.filter_field()
    date_issued: strawberry.auto = strawberry_django.filter_field()
    date_replaced: strawberry.auto = strawberry_django.filter_field()

    # Related asset filter
    asset: Annotated["InventoryMonitorAssetFilter", strawberry.lazy("inventory_monitor.graphql.filters")] | None = (
        strawberry_django.filter_field()
    )
    asset_id: ID | None = strawberry_django.filter_field()

    # Custom filter for both serials (like in Django filterset)
    serial: BaseFilterLookup[str] | None = strawberry_django.filter_field()
