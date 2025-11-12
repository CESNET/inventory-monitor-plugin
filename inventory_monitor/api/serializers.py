# NetBox serializers
from core.models import ObjectType
from dcim.api.serializers import (
    DeviceSerializer,
    LocationSerializer,
    SiteSerializer,
)
from drf_spectacular.utils import extend_schema_field
from netbox.api.fields import ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer
from utilities.api import get_serializer_for_model

# Local models
from inventory_monitor.models import (
    ASSIGNED_OBJECT_MODELS_QUERY,
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

#
# Base serializers
#


class AssetTypeSerializer(NetBoxModelSerializer):
    """Serializer for AssetType objects"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:assettype-detail")

    class Meta:
        model = AssetType
        fields = [
            "id",
            "url",
            "name",
            "slug",
            "description",
            "color",
            "display",
            "custom_fields",
            "created",
            "last_updated",
            "tags",
        ]

        brief_fields = [
            "id",
            "url",
            "name",
            "slug",
            "color",
            "display",
        ]


class ContractorSerializer(NetBoxModelSerializer):
    """Serializer for Contractor objects"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:contractor-detail")
    tenant = TenantSerializer(nested=True)

    class Meta:
        model = Contractor
        fields = [
            "id",
            "url",
            "display",
            "name",
            "company",
            "address",
            "description",
            "tenant",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = ["id", "url", "display", "name", "company", "address", "description"]


class ContractSerializer(NetBoxModelSerializer):
    """Serializer for Contract objects"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:contract-detail")
    contractor = ContractorSerializer(nested=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
            "description",
            "contractor",
            "type",
            "contract_type",
            "price",
            "currency",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
            "parent",
            "tags",
            "comments",
            "custom_fields",
        ]
        brief_fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
            "description",
        ]

    def get_fields(self):
        """Handle nested parent contract references"""
        fields = super(ContractSerializer, self).get_fields()
        fields["parent"] = ContractSerializer(nested=True)
        return fields


#
# Main objects serializers
#


class AssetSerializer(NetBoxModelSerializer):
    """
    Serializer for Asset objects supporting GenericForeignKey relationships
    """

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:asset-detail")
    # Related object serializers
    order_contract = ContractSerializer(nested=True)
    type = AssetTypeSerializer(nested=True)

    # Generic relationship fields
    assigned_object_type = ContentTypeField(
        queryset=ObjectType.objects.filter(ASSIGNED_OBJECT_MODELS_QUERY),
        required=False,
        allow_null=True,
    )
    assigned_object = serializers.SerializerMethodField(read_only=True, allow_null=True)

    asset_numbers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Asset
        fields = (
            # Identification fields
            "id",
            "url",
            "display",
            "partnumber",
            "serial",
            "asset_numbers",
            "description",
            # Assignment fields
            "assigned_object_type",
            "assigned_object_id",
            "assigned_object",
            "assignment_status",
            "lifecycle_status",
            # Related objects
            "type",
            "order_contract",
            # Additional information
            "project",
            "vendor",
            "quantity",
            "price",
            "currency",
            # Warranty information
            "warranty_start",
            "warranty_end",
            # Notes and metadata
            "comments",
            "custom_fields",
            "tags",
            "created",
            "last_updated",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "partnumber",
            "serial",
            "asset_numbers",
            "type",
            "description",
            "assignment_status",
            "assigned_object",
            "order_contract",
            "lifecycle_status",
            "custom_fields",
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, obj):
        """
        Dynamically serialize the assigned object based on its type

        Returns:
            dict: Serialized representation of the assigned object
            None: If no object is assigned
        """
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {"request": self.context["request"]}
        return serializer(obj.assigned_object, nested=True, context=context).data

    @extend_schema_field(serializers.CharField(read_only=True))
    def get_asset_numbers(self, obj):
        """Get External Inventory asset numbers as comma-separated string"""
        return obj.get_external_inventory_asset_numbers_display()


class ProbeSerializer(NetBoxModelSerializer):
    """Serializer for Probe objects"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:probe-detail")
    device = DeviceSerializer(allow_null=True, nested=True)
    site = SiteSerializer(allow_null=True, nested=True)
    location = LocationSerializer(allow_null=True, nested=True)

    class Meta:
        model = Probe
        fields = [
            "id",
            "url",
            "display",
            "name",
            "time",
            "serial",
            "part",
            "device_descriptor",
            "device",
            "site_descriptor",
            "site",
            "location_descriptor",
            "location",
            "description",
            "category",
            "discovered_data",
            "tags",
            "comments",
            "custom_fields",
            "creation_time",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "name",
            "serial",
            "time",
            "creation_time",
        ]


class InvoiceSerializer(NetBoxModelSerializer):
    """Serializer for Invoice objects"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:invoice-detail")
    contract = ContractSerializer(nested=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "url",
            "display",
            "name",
            "name_internal",
            "project",
            "description",
            "contract",
            "price",
            "invoicing_start",
            "invoicing_end",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = ["id", "url", "display", "name", "name_internal", "description"]


class AssetServiceSerializer(NetBoxModelSerializer):
    """Serializer for AssetService objects"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:assetservice-detail")
    contract = ContractSerializer(nested=True)
    asset = AssetSerializer(nested=True)

    class Meta:
        model = AssetService
        fields = [
            "id",
            "url",
            "display",
            "service_start",
            "service_end",
            "service_price",
            "service_currency",
            "service_category",
            "service_category_vendor",
            "description",
            "asset",
            "contract",
            "tags",
            "comments",
            "custom_fields",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "service_start",
            "service_end",
            "service_price",
            "description",
            "asset",
            "contract",
        ]


class RMASerializer(NetBoxModelSerializer):
    """Serializer for RMA (Return Merchandise Authorization) objects"""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:rma-detail")
    asset = AssetSerializer(nested=True)

    class Meta:
        model = RMA
        fields = [
            "id",
            "url",
            "display",
            "rma_number",
            "asset",
            "original_serial",
            "replacement_serial",
            "status",
            "date_issued",
            "date_replaced",
            "issue_description",
            "vendor_response",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]

        brief_fields = [
            "id",
            "url",
            "display",
            "rma_number",
            "asset",
            "original_serial",
            "replacement_serial",
            "status",
            "date_issued",
            "date_replaced",
        ]


class ExternalInventorySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:inventory_monitor-api:externalinventory-detail")
    assets = SerializedPKRelatedField(
        queryset=Asset.objects.all(),
        serializer=AssetSerializer,
        nested=True,
        required=False,
        many=True,
    )

    class Meta:
        model = ExternalInventory
        fields = [
            "id",
            "url",
            "display",
            "external_id",
            "inventory_number",
            "name",
            "serial_number",
            "person_id",
            "person_name",
            "location_code",
            "location",
            "department_code",
            "project_code",
            "user_name",
            "user_note",
            "split_asset",
            "status",
            "assets",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        ]
