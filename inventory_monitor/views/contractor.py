from core.models import ObjectType
from django.db.models import Count, OuterRef, Subquery
from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_object_type_or_none

# Attempt to import NetBoxAttachment and set a flag based on its availability
attachments_model_exists = False
try:
    from netbox_attachments.models import NetBoxAttachment

    attachments_model_exists = True
except (ModuleNotFoundError, RuntimeError):
    pass


def annotate_contracts_with_attachments(contracts, instance):
    try:
        contract_object_type = get_object_type_or_none(app_label="inventory_monitor", model="contract")
        subquery_attachments_count = (
            NetBoxAttachment.objects.filter(object_id=OuterRef("id"), object_type=contract_object_type)
            .values("object_id")
            .annotate(attachments_count=Count("*"))
        )
        return contracts.annotate(attachments_count=Subquery(subquery_attachments_count.values("attachments_count")))
    except (ObjectType.DoesNotExist, ValueError):
        # Return contracts without attachment count if there's an error
        return contracts


@register_model_view(models.Contractor)
class ContractorView(generic.ObjectView):
    queryset = models.Contractor.objects.all()


@register_model_view(models.Contractor, 'list', path='', detail=False)
class ContractorListView(generic.ObjectListView):
    queryset = models.Contractor.objects.select_related("tenant").prefetch_related("tags").annotate(contracts_count=Count("contracts"))
    filterset = filtersets.ContractorFilterSet
    filterset_form = forms.ContractorFilterForm
    table = tables.ContractorTable
    actions = {
        "add": {"add"},
        "export": set(),
        "bulk_edit": {"change"},
        "bulk_delete": {"delete"},
    }


@register_model_view(models.Contractor, 'add', detail=False)
@register_model_view(models.Contractor, 'edit')
class ContractorEditView(generic.ObjectEditView):
    queryset = models.Contractor.objects.all()
    form = forms.ContractorForm


@register_model_view(models.Contractor, 'delete')
class ContractorDeleteView(generic.ObjectDeleteView):
    queryset = models.Contractor.objects.all()


@register_model_view(models.Contractor, 'bulk_edit', path='edit', detail=False)
class ContractorBulkEditView(generic.BulkEditView):
    queryset = models.Contractor.objects.all()
    filterset = filtersets.ContractorFilterSet
    table = tables.ContractorTable
    form = forms.ContractorBulkEditForm


@register_model_view(models.Contractor, 'bulk_delete', path='delete', detail=False)
class ContractorBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Contractor.objects.all()
    filterset = filtersets.ContractorFilterSet
    table = tables.ContractorTable
    default_return_url = "plugins:inventory_monitor:contractor_list"
