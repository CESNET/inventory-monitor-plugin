from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables


@register_model_view(models.AssetService)
class AssetServiceView(generic.ObjectView):
    queryset = models.AssetService.objects.all()


@register_model_view(models.AssetService, 'list')
class AssetServiceListView(generic.ObjectListView):
    queryset = models.AssetService.objects.select_related("asset", "contract__contractor")
    filterset = filtersets.AssetServiceFilterSet
    filterset_form = forms.AssetServiceFilterForm
    table = tables.AssetServiceTable


@register_model_view(models.AssetService, 'add')
class AssetServiceCreateView(generic.ObjectEditView):
    queryset = models.AssetService.objects.all()
    form = forms.AssetServiceForm


@register_model_view(models.AssetService, 'edit')
class AssetServiceEditView(generic.ObjectEditView):
    queryset = models.AssetService.objects.all()
    form = forms.AssetServiceForm


@register_model_view(models.AssetService, 'delete')
class AssetServiceDeleteView(generic.ObjectDeleteView):
    queryset = models.AssetService.objects.all()


@register_model_view(models.AssetService, 'bulk_edit', path='edit', detail=False)
class AssetServiceBulkEditView(generic.BulkEditView):
    queryset = models.AssetService.objects.all()
    filterset = filtersets.AssetServiceFilterSet
    table = tables.AssetServiceTable
    form = forms.AssetServiceBulkEditForm


@register_model_view(models.AssetService, 'bulk_delete', path='delete', detail=False)
class AssetServiceBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AssetService.objects.all()
    filterset = filtersets.AssetServiceFilterSet
    table = tables.AssetServiceTable
