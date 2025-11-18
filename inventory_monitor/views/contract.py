from core.models import ObjectType
from django.db.models import Count, OuterRef, Subquery, Value
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


def get_attachments_count_query(model_name):
    if not attachments_model_exists:
        return Value(0)

    object_type = get_object_type_or_none(app_label="inventory_monitor", model=model_name)

    if not object_type:
        return Value(0)

    try:
        return Subquery(
            NetBoxAttachment.objects.filter(object_id=OuterRef("id"), object_type=object_type)
            .values("object_id")
            .annotate(attachments_count=Count("*"))
            .values("attachments_count")
        )
    except (ObjectType.DoesNotExist, ValueError):
        return Value(0)


def annotate_queryset_with_counts(queryset):
    queryset = queryset.select_related("contractor", "parent").annotate(
        subcontracts_count=Count("subcontracts", distinct=True),
        invoices_count=Count("invoices", distinct=True),
        attachments_count=get_attachments_count_query("contract"),
    )
    return queryset


@register_model_view(models.Contract)
class ContractView(generic.ObjectView):
    queryset = annotate_queryset_with_counts(models.Contract.objects.all())


@register_model_view(models.Contract, 'list', path='', detail=False)
class ContractListView(generic.ObjectListView):
    queryset = annotate_queryset_with_counts(models.Contract.objects.all())
    filterset = filtersets.ContractFilterSet
    filterset_form = forms.ContractFilterForm
    table = tables.ContractTable
    actions = {
        "add": {"add"},
        "export": set(),
        "bulk_edit": {"change"},
        "bulk_delete": {"delete"},
    }


@register_model_view(models.Contract, 'add', detail=False)
@register_model_view(models.Contract, 'edit')
class ContractEditView(generic.ObjectEditView):
    queryset = models.Contract.objects.all().annotate(subcontracts_count=Count("subcontracts"))
    form = forms.ContractForm


@register_model_view(models.Contract, 'delete')
class ContractDeleteView(generic.ObjectDeleteView):
    queryset = models.Contract.objects.all()


@register_model_view(models.Contract, 'bulk_edit', path='edit', detail=False)
class ContractBulkEditView(generic.BulkEditView):
    queryset = models.Contract.objects.all()
    filterset = filtersets.ContractFilterSet
    table = tables.ContractTable
    form = forms.ContractBulkEditForm


@register_model_view(models.Contract, 'bulk_delete', path='delete', detail=False)
class ContractBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Contract.objects.all()
    filterset = filtersets.ContractFilterSet
    table = tables.ContractTable
    default_return_url = "plugins:inventory_monitor:contract_list"
