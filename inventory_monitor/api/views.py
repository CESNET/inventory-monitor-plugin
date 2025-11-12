from netbox.api.viewsets import NetBoxModelViewSet

from inventory_monitor import filtersets, models
from inventory_monitor.api.serializers import (
    AssetSerializer,
    AssetServiceSerializer,
    AssetTypeSerializer,
    ContractorSerializer,
    ContractSerializer,
    ExternalInventorySerializer,
    InvoiceSerializer,
    ProbeSerializer,
    RMASerializer,
)
from inventory_monitor.filtersets import ExternalInventoryFilterSet
from inventory_monitor.models import ExternalInventory


class ProbeViewSet(NetBoxModelViewSet):
    queryset = models.Probe.objects.select_related("device", "site", "location").prefetch_related("tags")
    serializer_class = ProbeSerializer
    filterset_class = filtersets.ProbeFilterSet


class ContractorViewSet(NetBoxModelViewSet):
    queryset = models.Contractor.objects.select_related("tenant").prefetch_related("tags")
    serializer_class = ContractorSerializer
    filterset_class = filtersets.ContractorFilterSet


class ContractViewSet(NetBoxModelViewSet):
    queryset = models.Contract.objects.select_related("contractor").prefetch_related("tags")
    serializer_class = ContractSerializer
    filterset_class = filtersets.ContractFilterSet


class InvoiceViewSet(NetBoxModelViewSet):
    queryset = models.Invoice.objects.select_related("contract").prefetch_related("tags")
    serializer_class = InvoiceSerializer
    filterset_class = filtersets.InvoiceFilterSet


class AssetViewSet(NetBoxModelViewSet):
    queryset = models.Asset.objects.select_related("type", "order_contract").prefetch_related("tags")
    serializer_class = AssetSerializer
    filterset_class = filtersets.AssetFilterSet


class AssetTypeViewSet(NetBoxModelViewSet):
    queryset = models.AssetType.objects.prefetch_related("tags")
    serializer_class = AssetTypeSerializer
    filterset_class = filtersets.AssetTypeFilterSet


class AssetServiceViewSet(NetBoxModelViewSet):
    queryset = models.AssetService.objects.select_related("asset", "contract").prefetch_related("tags")
    serializer_class = AssetServiceSerializer
    filterset_class = filtersets.AssetServiceFilterSet


class RMAViewSet(NetBoxModelViewSet):
    queryset = models.RMA.objects.select_related("asset").prefetch_related("tags")
    serializer_class = RMASerializer
    filterset_class = filtersets.RMAFilterSet


class ExternalInventoryViewSet(NetBoxModelViewSet):
    queryset = ExternalInventory.objects.prefetch_related("assets", "tags")
    serializer_class = ExternalInventorySerializer
    filterset_class = ExternalInventoryFilterSet
