from django.db.models import Count
from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_attachments_count_subquery


def annotate_queryset_with_counts(queryset):
    queryset = queryset.select_related("contractor", "parent").annotate(
        subcontracts_count=Count("subcontracts", distinct=True),
        invoices_count=Count("invoices", distinct=True),
        attachments_count=get_attachments_count_subquery("contract"),
    )
    return queryset


@register_model_view(models.Contract)
class ContractView(generic.ObjectView):
    queryset = annotate_queryset_with_counts(models.Contract.objects.all())


@register_model_view(models.Contract, "list", path="", detail=False)
class ContractListView(generic.ObjectListView):
    queryset = annotate_queryset_with_counts(models.Contract.objects.all())
    filterset = filtersets.ContractFilterSet
    filterset_form = forms.ContractFilterForm
    table = tables.ContractTable


@register_model_view(models.Contract, "add", detail=False)
@register_model_view(models.Contract, "edit")
class ContractEditView(generic.ObjectEditView):
    queryset = models.Contract.objects.all().annotate(subcontracts_count=Count("subcontracts"))
    form = forms.ContractForm


@register_model_view(models.Contract, "delete")
class ContractDeleteView(generic.ObjectDeleteView):
    queryset = models.Contract.objects.all()


@register_model_view(models.Contract, "bulk_edit", path="edit", detail=False)
class ContractBulkEditView(generic.BulkEditView):
    queryset = models.Contract.objects.all()
    filterset = filtersets.ContractFilterSet
    table = tables.ContractTable
    form = forms.ContractBulkEditForm


@register_model_view(models.Contract, "bulk_delete", path="delete", detail=False)
class ContractBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Contract.objects.all()
    filterset = filtersets.ContractFilterSet
    table = tables.ContractTable
    default_return_url = "plugins:inventory_monitor:contract_list"


@register_model_view(models.Contract, "bulk_import", path="import", detail=False)
class ContractBulkImportView(generic.BulkImportView):
    queryset = models.Contract.objects.all()
    model_form = forms.ContractBulkImportForm
