from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables
from inventory_monitor.helpers import get_attachments_count_subquery


def get_invoice_queryset():
    return models.Invoice.objects.select_related("contract").annotate(
        attachments_count=get_attachments_count_subquery("invoice"),
    )


@register_model_view(models.Invoice)
class InvoiceView(generic.ObjectView):
    queryset = models.Invoice.objects.all()


@register_model_view(models.Invoice, "list", path="", detail=False)
class InvoiceListView(generic.ObjectListView):
    filterset = filtersets.InvoiceFilterSet
    filterset_form = forms.InvoiceFilterForm
    table = tables.InvoiceTable
    queryset = get_invoice_queryset()


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


@register_model_view(models.Invoice, "bulk_import", path="import", detail=False)
class InvoiceBulkImportView(generic.BulkImportView):
    queryset = models.Invoice.objects.all()
    model_form = forms.InvoiceBulkImportForm
