from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor.filtersets import ExternalInventoryFilterSet
from inventory_monitor.forms import ExternalInventoryFilterForm, ExternalInventoryForm, ExternalInventoryBulkEditForm
from inventory_monitor.models import ExternalInventory
from inventory_monitor.tables import ExternalInventoryTable


@register_model_view(ExternalInventory)
class ExternalInventoryView(generic.ObjectView):
    queryset = ExternalInventory.objects.all()


@register_model_view(ExternalInventory, "list", path="", detail=False)
class ExternalInventoryListView(generic.ObjectListView):
    queryset = ExternalInventory.objects.all()
    table = ExternalInventoryTable
    filterset = ExternalInventoryFilterSet
    filterset_form = ExternalInventoryFilterForm
    actions = {
        "add": {"add"},
        "export": set(),
        "bulk_edit": {"change"},
        "bulk_delete": {"delete"},
    }


@register_model_view(ExternalInventory, "add", detail=False)
@register_model_view(ExternalInventory, "edit")
class ExternalInventoryEditView(generic.ObjectEditView):
    queryset = ExternalInventory.objects.all()
    form = ExternalInventoryForm


@register_model_view(ExternalInventory, "delete")
class ExternalInventoryDeleteView(generic.ObjectDeleteView):
    queryset = ExternalInventory.objects.all()


@register_model_view(ExternalInventory, "bulk_edit", path="edit", detail=False)
class ExternalInventoryBulkEditView(generic.BulkEditView):
    queryset = ExternalInventory.objects.all()
    filterset = ExternalInventoryFilterSet
    table = ExternalInventoryTable
    form = ExternalInventoryBulkEditForm


@register_model_view(ExternalInventory, "bulk_delete", path="delete", detail=False)
class ExternalInventoryBulkDeleteView(generic.BulkDeleteView):
    queryset = ExternalInventory.objects.all()
    filterset = ExternalInventoryFilterSet
    table = ExternalInventoryTable
    default_return_url = "plugins:inventory_monitor:externalinventory_list"
