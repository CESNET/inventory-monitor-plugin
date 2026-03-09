from django.db.models import Count
from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables


@register_model_view(models.Contractor)
class ContractorView(generic.ObjectView):
    queryset = models.Contractor.objects.all()


@register_model_view(models.Contractor, "list", path="", detail=False)
class ContractorListView(generic.ObjectListView):
    queryset = (
        models.Contractor.objects.select_related("tenant")
        .prefetch_related("tags")
        .annotate(contracts_count=Count("contracts"))
    )
    filterset = filtersets.ContractorFilterSet
    filterset_form = forms.ContractorFilterForm
    table = tables.ContractorTable


@register_model_view(models.Contractor, "add", detail=False)
@register_model_view(models.Contractor, "edit")
class ContractorEditView(generic.ObjectEditView):
    queryset = models.Contractor.objects.all()
    form = forms.ContractorForm


@register_model_view(models.Contractor, "delete")
class ContractorDeleteView(generic.ObjectDeleteView):
    queryset = models.Contractor.objects.all()


@register_model_view(models.Contractor, "bulk_edit", path="edit", detail=False)
class ContractorBulkEditView(generic.BulkEditView):
    queryset = models.Contractor.objects.all()
    filterset = filtersets.ContractorFilterSet
    table = tables.ContractorTable
    form = forms.ContractorBulkEditForm


@register_model_view(models.Contractor, "bulk_delete", path="delete", detail=False)
class ContractorBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Contractor.objects.all()
    filterset = filtersets.ContractorFilterSet
    table = tables.ContractorTable
    default_return_url = "plugins:inventory_monitor:contractor_list"


@register_model_view(models.Contractor, "bulk_import", path="import", detail=False)
class ContractorBulkImportView(generic.BulkImportView):
    queryset = models.Contractor.objects.all()
    model_form = forms.ContractorBulkImportForm
