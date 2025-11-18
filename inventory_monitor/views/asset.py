from core.models import ObjectType
from django.contrib import messages
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.forms.asset import AssetExternalInventoryAssignmentForm
from inventory_monitor.models import Asset


@register_model_view(models.Asset)
class AssetView(generic.ObjectView):
    queryset = models.Asset.objects.all()


@register_model_view(models.Asset, "list", path="", detail=False)
class AssetListView(generic.ObjectListView):
    queryset = (
        models.Asset.objects.all()
        .select_related("type", "order_contract", "assigned_object_type")  # Use select_related for FK fields
        .prefetch_related("services")
        .prefetch_related("tags")
        .prefetch_related("external_inventory_items")
        .prefetch_related("rmas")  # Prefetch RMAs to avoid N+1 queries in get_related_probes
        .annotate(services_count=Count("services"))
        .annotate(services_to=ArrayAgg("services__service_end"))
        .annotate(services_contracts=ArrayAgg("services__contract__name"))
    )
    filterset = filtersets.AssetFilterSet
    filterset_form = forms.AssetFilterForm
    table = tables.EnhancedAssetTable  # Changed to show probe status with green rows
    template_name = "inventory_monitor/asset_list.html"  # Custom template with CSS
    actions = {
        "add": {"add"},
        "export": set(),
        "bulk_edit": {"change"},
        "bulk_delete": {"delete"},
    }
    
    def get_queryset(self, request):
        """Override to apply probe data annotations to avoid N+1 queries."""
        queryset = super().get_queryset(request)
        # Annotate with probe data computed in database
        return Asset.annotate_with_probe_data(queryset)


@register_model_view(models.Asset, "add", detail=False)
@register_model_view(models.Asset, "edit")
class AssetEditView(generic.ObjectEditView):
    queryset = models.Asset.objects.all()
    form = forms.AssetForm

    def alter_object(self, instance, request, url_args, url_kwargs):
        if not instance.pk:
            assigned_object_type = request.GET.get("assigned_object_type")
            assigned_object_id = request.GET.get("assigned_object_id")

            if assigned_object_type and assigned_object_id:
                instance.assigned_object_type = ObjectType.objects.get(pk=assigned_object_type)
                instance.assigned_object_id = assigned_object_id

        return instance


@register_model_view(models.Asset, "delete")
class AssetDeleteView(generic.ObjectDeleteView):
    queryset = models.Asset.objects.all()


@register_model_view(models.Asset, "bulk_edit", path="edit", detail=False)
class AssetBulkEditView(generic.BulkEditView):
    queryset = models.Asset.objects.all()
    filterset = filtersets.AssetFilterSet
    table = tables.EnhancedAssetTable
    form = forms.AssetBulkEditForm


@register_model_view(models.Asset, "bulk_delete", path="delete", detail=False)
class AssetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Asset.objects.all()
    filterset = filtersets.AssetFilterSet
    table = tables.EnhancedAssetTable
    default_return_url = "plugins:inventory_monitor:asset_list"


@register_model_view(models.Asset, "bulk_import", path="import", detail=False)
class AssetBulkImportView(generic.BulkImportView):
    queryset = models.Asset.objects.all()
    model_form = forms.AssetBulkImportForm


@register_model_view(models.Asset, "external_inventory_assignment", path="assign-external-inventory")
class AssetExternalInventoryAssignmentView(generic.ObjectEditView):
    """
    View for assigning External Inventory objects to an Asset
    """

    queryset = Asset.objects.all()
    form = AssetExternalInventoryAssignmentForm
    template_name = "inventory_monitor/asset_external_inventory_assignment.html"

    def get_object(self, **kwargs):
        """Get the Asset object to assign External Inventory objects to"""
        if not kwargs:
            return self.queryset.model()

        if "pk" not in kwargs:
            return super().get_object(**kwargs)

        return get_object_or_404(Asset, pk=self.kwargs["pk"])

    def get_return_url(self, request, instance=None):
        """Return to the asset detail page after successful assignment"""
        return reverse("plugins:inventory_monitor:asset", args=[self.kwargs["pk"]])

    def form_valid(self, form):
        """Handle successful form submission"""
        response = super().form_valid(form)

        # Add success message
        external_inventory_count = form.cleaned_data["external_inventory_items"].count()
        messages.success(
            self.request,
            _("Successfully assigned {} External Inventory object(s) to asset {}").format(
                external_inventory_count, form.instance
            ),
        )

        return response

    def get_extra_context(self, request, instance):
        """Add extra context for the template"""
        device_asset_tag = (
            instance.assigned_object.asset_tag
            if (
                instance.assigned_object_type
                and instance.assigned_object_type.model == "device"
                and getattr(instance.assigned_object, "asset_tag", None)
                and getattr(instance.assigned_object, "serial", None) == instance.serial
            )
            else None
        )
        return {
            "asset": instance,
            "title": f"Assign External Inventory Objects to {instance}",
            "device_asset_tags": device_asset_tag,
        }
