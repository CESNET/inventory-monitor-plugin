from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables


@register_model_view(models.RMA)
class RMAView(generic.ObjectView):
    queryset = models.RMA.objects.all()


@register_model_view(models.RMA, "list", path="", detail=False)
class RMAListView(generic.ObjectListView):
    queryset = models.RMA.objects.select_related("asset")
    table = tables.RMATable
    filterset = filtersets.RMAFilterSet
    filterset_form = forms.RMAFilterForm
    actions = {
        "add": {"add"},
        "export": set(),
        "bulk_edit": {"change"},
        "bulk_delete": {"delete"},
    }


@register_model_view(models.RMA, "add", detail=False)
@register_model_view(models.RMA, "edit")
class RMAEditView(generic.ObjectEditView):
    queryset = models.RMA.objects.all()
    form = forms.RMAForm


@register_model_view(models.RMA, "delete")
class RMADeleteView(generic.ObjectDeleteView):
    queryset = models.RMA.objects.all()


@register_model_view(models.RMA, "bulk_edit", path="edit", detail=False)
class RMABulkEditView(generic.BulkEditView):
    queryset = models.RMA.objects.all()
    filterset = filtersets.RMAFilterSet
    table = tables.RMATable
    form = forms.RMABulkEditForm


@register_model_view(models.RMA, "bulk_delete", path="delete", detail=False)
class RMABulkDeleteView(generic.BulkDeleteView):
    queryset = models.RMA.objects.all()
    filterset = filtersets.RMAFilterSet
    table = tables.RMATable
    default_return_url = "plugins:inventory_monitor:rma_list"
