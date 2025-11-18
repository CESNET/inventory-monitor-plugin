from core.models import ObjectType
from django.db.models import Count, OuterRef, Subquery, Value
from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_object_type_or_none

# Attempt to import NetBoxAttachment and set a flag based on its availability
try:
    from netbox_attachments.models import NetBoxAttachment

    attachments_model_exists = True
except (ModuleNotFoundError, Exception):
    attachments_model_exists = False


def get_invoice_queryset():
    """
    Generates the queryset for Invoice objects, optionally annotating with attachment counts.
    """
    base_queryset = models.Invoice.objects.select_related("contract")
    if attachments_model_exists:
        try:
            invoice_object_type = get_object_type_or_none(app_label="inventory_monitor", model="invoice")

            if not invoice_object_type:
                return base_queryset.annotate(attachments_count=Value(0))

            subquery_attachments_count = (
                NetBoxAttachment.objects.filter(object_id=OuterRef("id"), object_type=invoice_object_type)
                .values("object_id")
                .annotate(attachments_count=Count("*"))
            )
            return base_queryset.annotate(
                attachments_count=Subquery(subquery_attachments_count.values("attachments_count"))
            )
        except (ObjectType.DoesNotExist, ValueError):
            pass
    return base_queryset.annotate(attachments_count=Value(0))


@register_model_view(models.Invoice)
class InvoiceView(generic.ObjectView):
    queryset = models.Invoice.objects.all()


@register_model_view(models.Invoice, "list", path="", detail=False)
class InvoiceListView(generic.ObjectListView):
    filterset = filtersets.InvoiceFilterSet
    filterset_form = forms.InvoiceFilterForm
    table = tables.InvoiceTable
    queryset = get_invoice_queryset()
    actions = {
        "add": {"add"},
        "export": set(),
        "bulk_edit": {"change"},
        "bulk_delete": {"delete"},
    }


@register_model_view(models.Invoice, "add", detail=False)
@register_model_view(models.Invoice, "edit")
class InvoiceEditView(generic.ObjectEditView):
    queryset = models.Invoice.objects.all()
    form = forms.InvoiceForm


@register_model_view(models.Invoice, "delete")
class InvoiceDeleteView(generic.ObjectDeleteView):
    queryset = models.Invoice.objects.all()


@register_model_view(models.Invoice, "bulk_edit", path="edit", detail=False)
class InvoiceBulkEditView(generic.BulkEditView):
    queryset = models.Invoice.objects.all()
    filterset = filtersets.InvoiceFilterSet
    table = tables.InvoiceTable
    form = forms.InvoiceBulkEditForm


@register_model_view(models.Invoice, "bulk_delete", path="delete", detail=False)
class InvoiceBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Invoice.objects.all()
    filterset = filtersets.InvoiceFilterSet
    table = tables.InvoiceTable
    default_return_url = "plugins:inventory_monitor:invoice_list"
