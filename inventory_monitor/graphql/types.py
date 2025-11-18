from typing import Annotated, List

import strawberry
import strawberry_django
from core.graphql.types import ContentType
from dcim.graphql.types import (
    DeviceType,
    LocationType,
    SiteType,
)
from netbox.graphql.types import NetBoxObjectType
from tenancy.graphql.types import TenantType

import inventory_monitor.models as models

from .enums import (
    InventoryMonitorAssignmentStatusEnum,
    InventoryMonitorContractTypeEnum,
    InventoryMonitorLifecycleStatusEnum,
    InventoryMonitorRMAStatusEnum,
)
from .filters import (
    InventoryMonitorAssetFilter,
    InventoryMonitorAssetServiceFilter,
    InventoryMonitorAssetTypeFilter,
    InventoryMonitorContractFilter,
    InventoryMonitorContractorFilter,
    InventoryMonitorExternalInventoryFilter,
    InventoryMonitorInvoiceFilter,
    InventoryMonitorProbeFilter,
    InventoryMonitorRMAFilter,
)


@strawberry_django.type(models.ExternalInventory, fields="__all__", filters=InventoryMonitorExternalInventoryFilter)
class InventoryMonitorExternalInventoryType(NetBoxObjectType):
    external_id: str | None
    inventory_number: str
    name: str
    serial_number: str | None
    person_id: str | None
    person_name: str | None
    location_code: str | None
    location: str | None
    department_code: str | None
    project_code: str | None
    user_name: str | None
    user_note: str | None
    split_asset: str | None
    status: str | None

    # Relationship to assets
    assets: List[Annotated["InventoryMonitorAssetType", strawberry.lazy("inventory_monitor.graphql.types")]]


@strawberry_django.type(models.Asset, fields="__all__", filters=InventoryMonitorAssetFilter)
class InventoryMonitorAssetType(NetBoxObjectType):
    # Basic identification fields
    partnumber: str | None
    description: str | None
    serial: str

    # Status fields
    assignment_status: InventoryMonitorAssignmentStatusEnum | None
    lifecycle_status: InventoryMonitorLifecycleStatusEnum | None

    # Assignment fields (GenericForeignKey)
    assigned_object_type: Annotated["ContentType", strawberry.lazy("core.graphql.types")] | None
    assigned_object_id: int | None

    # Related objects
    type: Annotated["InventoryMonitorAssetTypeType", strawberry.lazy("inventory_monitor.graphql.types")] | None
    order_contract: Annotated["InventoryMonitorContractType", strawberry.lazy("inventory_monitor.graphql.types")] | None

    # Additional information
    project: str | None
    vendor: str | None
    quantity: int
    price: str | None  # DecimalField as string
    currency: str | None

    # Warranty information
    warranty_start: str | None  # DateField as string
    warranty_end: str | None  # DateField as string

    # Notes
    comments: str

    # Relationship back to External Inventory objects
    external_inventory_items: List[
        Annotated["InventoryMonitorExternalInventoryType", strawberry.lazy("inventory_monitor.graphql.types")]
    ]

    # Services relationship
    services: List[Annotated["InventoryMonitorAssetServiceType", strawberry.lazy("inventory_monitor.graphql.types")]]

    # RMAs relationship
    rmas: List[Annotated["InventoryMonitorRMAType", strawberry.lazy("inventory_monitor.graphql.types")]]


@strawberry_django.type(models.AssetType, fields="__all__", filters=InventoryMonitorAssetTypeFilter)
class InventoryMonitorAssetTypeType(NetBoxObjectType):
    name: str
    slug: str
    description: str
    color: str

    # Assets relationship
    assets: List[Annotated["InventoryMonitorAssetType", strawberry.lazy("inventory_monitor.graphql.types")]]


@strawberry_django.type(models.AssetService, fields="__all__", filters=InventoryMonitorAssetServiceFilter)
class InventoryMonitorAssetServiceType(NetBoxObjectType):
    service_start: str | None  # DateField as string
    service_end: str | None  # DateField as string
    service_price: str | None  # DecimalField as string
    service_currency: str | None  # Currency code
    service_category: str | None
    service_category_vendor: str | None
    comments: str

    # Related objects
    asset: Annotated["InventoryMonitorAssetType", strawberry.lazy("inventory_monitor.graphql.types")] | None
    contract: Annotated["InventoryMonitorContractType", strawberry.lazy("inventory_monitor.graphql.types")] | None


@strawberry_django.type(models.Contract, fields="__all__", filters=InventoryMonitorContractFilter)
class InventoryMonitorContractType(NetBoxObjectType):
    name: str
    name_internal: str
    type: Annotated["InventoryMonitorContractTypeEnum", strawberry.lazy("inventory_monitor.graphql.enums")] | None
    price: str | None  # DecimalField as string
    currency: str  # Currency code
    signed: str | None  # DateField as string
    accepted: str | None  # DateField as string
    invoicing_start: str | None  # DateField as string
    invoicing_end: str | None  # DateField as string
    comments: str

    # Related objects
    contractor: Annotated["InventoryMonitorContractorType", strawberry.lazy("inventory_monitor.graphql.types")] | None
    parent: Annotated["InventoryMonitorContractType", strawberry.lazy("inventory_monitor.graphql.types")] | None

    # Relationships
    subcontracts: List[Annotated["InventoryMonitorContractType", strawberry.lazy("inventory_monitor.graphql.types")]]
    assets: List[Annotated["InventoryMonitorAssetType", strawberry.lazy("inventory_monitor.graphql.types")]]
    services: List[Annotated["InventoryMonitorAssetServiceType", strawberry.lazy("inventory_monitor.graphql.types")]]
    invoices: List[Annotated["InventoryMonitorInvoiceType", strawberry.lazy("inventory_monitor.graphql.types")]]


@strawberry_django.type(models.Contractor, fields="__all__", filters=InventoryMonitorContractorFilter)
class InventoryMonitorContractorType(NetBoxObjectType):
    name: str
    company: str | None
    address: str | None
    comments: str

    # Tenant relationship
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None

    # Contracts relationship
    contracts: List[Annotated["InventoryMonitorContractType", strawberry.lazy("inventory_monitor.graphql.types")]]


@strawberry_django.type(models.Invoice, fields="__all__", filters=InventoryMonitorInvoiceFilter)
class InventoryMonitorInvoiceType(NetBoxObjectType):
    name: str
    name_internal: str
    project: str | None
    price: str  # DecimalField as string (required)
    invoicing_start: str | None  # DateField as string
    invoicing_end: str | None  # DateField as string
    comments: str

    # Related contract
    contract: Annotated["InventoryMonitorContractType", strawberry.lazy("inventory_monitor.graphql.types")]


@strawberry_django.type(models.Probe, fields="__all__", filters=InventoryMonitorProbeFilter)
class InventoryMonitorProbeType(NetBoxObjectType):
    time: str  # DateTimeField as string
    creation_time: str | None  # DateTimeField as string
    device_descriptor: str | None
    site_descriptor: str | None
    location_descriptor: str | None
    part: str | None
    name: str
    serial: str
    description: str
    comments: str
    discovered_data: str  # JSONField as string
    category: str | None

    # DCIM relationships
    device: Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")] | None
    site: Annotated["SiteType", strawberry.lazy("dcim.graphql.types")] | None
    location: Annotated["LocationType", strawberry.lazy("dcim.graphql.types")] | None


@strawberry_django.type(models.RMA, fields="__all__", filters=InventoryMonitorRMAFilter)
class InventoryMonitorRMAType(NetBoxObjectType):
    rma_number: str | None
    original_serial: str | None
    replacement_serial: str | None
    status: InventoryMonitorRMAStatusEnum | None
    date_issued: str | None  # DateField as string
    date_replaced: str | None  # DateField as string
    issue_description: str
    vendor_response: str

    # Related asset
    asset: Annotated["InventoryMonitorAssetType", strawberry.lazy("inventory_monitor.graphql.types")]
