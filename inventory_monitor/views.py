from dcim.models import InventoryItem
from dcim.tables.devices import InventoryItemTable
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Count, OuterRef, Subquery, Value
from django.shortcuts import render
from django.views.generic import View
from netbox.views import generic

from . import filtersets, forms, models, tables
from .helpers import get_content_type

try:
    from netbox_attachments.models import NetBoxAttachment

    attachments_model_exists = True
except ModuleNotFoundError:
    attachments_model_exists = False

# Probe


class ProbeView(generic.ObjectView):
    queryset = models.Probe.objects.all()

    def get_extra_context(self, request, instance):
        probes_sub_count_serial = (
            models.Probe.objects.filter(serial=OuterRef("serial"))
            .values("serial")
            .annotate(changes_count=Count("*"))
        )
        probe_table = tables.ProbeTable(
            models.Probe.objects.filter(serial=instance.serial).annotate(
                changes_count=Subquery(probes_sub_count_serial.values("changes_count"))
            )
        )
        probe_table.configure(request)

        inventory_items = InventoryItem.objects.filter(
            custom_field_data__inventory_monitor_probe=instance.id
        )
        inventory_items_table = InventoryItemTable(inventory_items)
        inventory_items_table.configure(request)

        return {
            "probe_table": probe_table,
            "inventory_items_table": inventory_items_table,
        }


class ProbeListView(generic.ObjectListView):
    sub_count_serial = (
        models.Probe.objects.filter(serial=OuterRef("serial"))
        .values("serial")
        .annotate(changes_count=Count("*"))
    )
    queryset = models.Probe.objects.prefetch_related("tags", "device").annotate(
        changes_count=Subquery(sub_count_serial.values("changes_count"))
    )

    table = tables.ProbeTable
    filterset = filtersets.ProbeFilterSet
    filterset_form = forms.ProbeFilterForm


class ProbeEditView(generic.ObjectEditView):
    queryset = models.Probe.objects.all()
    form = forms.ProbeForm


class ProbeDeleteView(generic.ObjectDeleteView):
    queryset = models.Probe.objects.all()


class ProbeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Probe.objects.all()
    filterset = filtersets.ProbeFilterSet
    table = tables.ProbeTable


# Contractor
class ContractorView(generic.ObjectView):
    queryset = models.Contractor.objects.all()

    def get_extra_context(self, request, instance):
        if attachments_model_exists:
            try:
                contract_content_type = get_content_type(
                    app_label="inventory_monitor", model="contract"
                )
                subquery_attachments_count = (
                    NetBoxAttachment.objects.filter(
                        object_id=OuterRef("id"), content_type=contract_content_type
                    )
                    .values("object_id")
                    .annotate(attachments_count=Count("*"))
                )
                contracts = (
                    models.Contract.objects.filter(contractor=instance)
                    .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                    .annotate(invoices_count=Count("invoices", distinct=True))
                    .annotate(
                        attachments_count=Subquery(
                            subquery_attachments_count.values("attachments_count")
                        )
                    )
                )
            except ContentType.DoesNotExist as e:
                contracts = models.Contract.objects.filter(contractor=instance)
        else:
            contracts = models.Contract.objects.filter(contractor=instance)

        contracts_table = tables.ContractTable(contracts)
        contracts_table.configure(request)

        return {"contracts_table": contracts_table}


class ContractorListView(generic.ObjectListView):
    queryset = models.Contractor.objects.prefetch_related("tags").annotate(
        contracts_count=Count("contracts")
    )

    filterset = filtersets.ContractorFilterSet
    filterset_form = forms.ContractorFilterForm
    table = tables.ContractorTable


class ContractorEditView(generic.ObjectEditView):
    queryset = models.Contractor.objects.all()
    form = forms.ContractorForm


class ContractorDeleteView(generic.ObjectDeleteView):
    queryset = models.Contractor.objects.all()


# Contract
class ContractView(generic.ObjectView):
    if attachments_model_exists:
        try:
            contract_content_type = get_content_type(
                app_label="inventory_monitor", model="contract"
            )
            subquery_attachments_count = (
                NetBoxAttachment.objects.filter(
                    object_id=OuterRef("id"), content_type=contract_content_type
                )
                .values("object_id")
                .annotate(attachments_count=Count("*"))
            )
            queryset = (
                models.Contract.objects.all()
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(
                    attachments_count=Subquery(
                        subquery_attachments_count.values("attachments_count")
                    )
                )
            )
        except ContentType.DoesNotExist as e:
            models.Contract.objects.all().annotate(
                subcontracts_count=Count("subcontracts", distinct=True)
            ).annotate(invoices_count=Count("invoices", distinct=True)).annotate(
                attachments_count=Value(0)
            )
    else:
        queryset = (
            models.Contract.objects.all()
            .annotate(subcontracts_count=Count("subcontracts", distinct=True))
            .annotate(invoices_count=Count("invoices", distinct=True))
            .annotate(attachments_count=Value(0))
        )

    def get_extra_context(self, request, instance):
        if attachments_model_exists:
            try:
                contract_content_type = get_content_type(
                    app_label="inventory_monitor", model="contract"
                )
                subquery_contract_attachments_count = (
                    NetBoxAttachment.objects.filter(
                        object_id=OuterRef("id"), content_type=contract_content_type
                    )
                    .values("object_id")
                    .annotate(attachments_count=Count("*"))
                )

                subcontracts = (
                    models.Contract.objects.filter(parent=instance)
                    .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                    .annotate(invoices_count=Count("invoices", distinct=True))
                    .annotate(
                        attachments_count=Subquery(
                            subquery_contract_attachments_count.values(
                                "attachments_count"
                            )
                        )
                    )
                )

                invoice_content_type = get_content_type(
                    app_label="inventory_monitor", model="invoice"
                )

                subquery_attachments_count = (
                    NetBoxAttachment.objects.filter(
                        object_id=OuterRef("id"), content_type=invoice_content_type
                    )
                    .values("object_id")
                    .annotate(attachments_count=Count("*"))
                )

                invoices = instance.invoices.all().annotate(
                    attachments_count=Subquery(
                        subquery_attachments_count.values("attachments_count")
                    )
                )
            except ContentType.DoesNotExist as e:
                subcontracts = (
                    models.Contract.objects.filter(parent=instance)
                    .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                    .annotate(invoices_count=Count("invoices", distinct=True))
                    .annotate(attachments_count=Value(0))
                )

                invoices = instance.invoices.all().annotate(attachments_count=Value(0))
        else:
            subcontracts = (
                models.Contract.objects.filter(parent=instance)
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(attachments_count=Value(0))
            )

            invoices = instance.invoices.all().annotate(attachments_count=Value(0))

        subcontracts_table = tables.ContractTable(subcontracts)
        subcontracts_table.configure(request)
        invoices_table = tables.InvoiceTable(invoices)
        invoices_table.configure(request)

        return {
            "subcontracts_table": subcontracts_table,
            "invoices_table": invoices_table,
        }


class ContractListView(generic.ObjectListView):
    if attachments_model_exists:
        try:
            contract_content_type = get_content_type(
                app_label="inventory_monitor", model="contract"
            )
            subquery_attachments_count = (
                NetBoxAttachment.objects.filter(
                    object_id=OuterRef("id"), content_type=contract_content_type
                )
                .values("object_id")
                .annotate(attachments_count=Count("*"))
            )
            queryset = (
                models.Contract.objects.all()
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(
                    attachments_count=Subquery(
                        subquery_attachments_count.values("attachments_count")
                    )
                )
            )
        except ContentType.DoesNotExist as e:
            queryset = (
                models.Contract.objects.all()
                .annotate(subcontracts_count=Count("subcontracts", distinct=True))
                .annotate(invoices_count=Count("invoices", distinct=True))
                .annotate(attachments_count=Value(0))
            )
    else:
        queryset = (
            models.Contract.objects.all()
            .annotate(subcontracts_count=Count("subcontracts", distinct=True))
            .annotate(invoices_count=Count("invoices", distinct=True))
            .annotate(attachments_count=Value(0))
        )

    filterset = filtersets.ContractFilterSet
    filterset_form = forms.ContractFilterForm
    table = tables.ContractTable


class ContractEditView(generic.ObjectEditView):
    queryset = models.Contract.objects.all().annotate(
        subcontracts_count=Count("subcontracts")
    )
    form = forms.ContractForm


class ContractDeleteView(generic.ObjectDeleteView):
    queryset = models.Contract.objects.all()


# Invoice
class InvoiceView(generic.ObjectView):
    queryset = models.Invoice.objects.all()


class InvoiceListView(generic.ObjectListView):
    if attachments_model_exists:
        try:
            invoice_content_type = get_content_type(
                app_label="inventory_monitor", model="invoice"
            )
            subquery_attachments_count = (
                NetBoxAttachment.objects.filter(
                    object_id=OuterRef("id"), content_type=invoice_content_type
                )
                .values("object_id")
                .annotate(attachments_count=Count("*"))
            )
            queryset = models.Invoice.objects.all().annotate(
                attachments_count=Subquery(
                    subquery_attachments_count.values("attachments_count")
                )
            )
        except ContentType.DoesNotExist as e:
            queryset = models.Invoice.objects.all().annotate(attachments_count=Value(0))
    else:
        queryset = models.Invoice.objects.all().annotate(attachments_count=Value(0))

    filterset = filtersets.InvoiceFilterSet
    filterset_form = forms.InvoiceFilterForm
    table = tables.InvoiceTable


class InvoiceEditView(generic.ObjectEditView):
    queryset = models.Invoice.objects.all()
    form = forms.InvoiceForm


class InvoiceDeleteView(generic.ObjectDeleteView):
    queryset = models.Invoice.objects.all()


# Component
class ComponentView(generic.ObjectView):
    queryset = models.Component.objects.all()

    def get_extra_context(self, request, instance):
        table = tables.ComponentServiceTable(instance.services.all())
        table.configure(request)

        return {
            "component_services_table": table,
        }


class ComponentListView(generic.ObjectListView):
    queryset = (
        models.Component.objects.all()
        .prefetch_related("services")
        .prefetch_related("tags")
        .annotate(services_count=Count("services"))
        .annotate(services_to=ArrayAgg("services__service_end"))
        .annotate(services_contracts=ArrayAgg("services__contract__name"))
    )
    filterset = filtersets.ComponentFilterSet
    filterset_form = forms.ComponentFilterForm
    table = tables.ComponentTable


class ComponentEditView(generic.ObjectEditView):
    queryset = models.Component.objects.all()
    form = forms.ComponentForm


class ComponentDeleteView(generic.ObjectDeleteView):
    queryset = models.Component.objects.all()


# ComponentService
class ComponentServiceView(generic.ObjectView):
    queryset = models.ComponentService.objects.all()


class ComponentServiceListView(generic.ObjectListView):
    queryset = models.ComponentService.objects.all()
    filterset = filtersets.ComponentServiceFilterSet
    filterset_form = forms.ComponentServiceFilterForm
    table = tables.ComponentServiceTable


class ComponentServiceEditView(generic.ObjectEditView):
    queryset = models.ComponentService.objects.all()
    form = forms.ComponentServiceForm


class ComponentServiceDeleteView(generic.ObjectDeleteView):
    queryset = models.ComponentService.objects.all()


class ProbeDiffView(View):
    def post(self, request):
        # load from, to and device_id from request
        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")
        device_id = request.POST.get("device")

        probes_added = models.Probe.objects.filter(
            device_id=device_id,
            creation_time__gte=date_from,
            creation_time__lte=date_to,
        )
        probes_removed = models.Probe.objects.filter(
            device_id=device_id, time__gte=date_from, time__lte=date_to
        )

        form = forms.ProbeDiffForm(
            initial={
                "date_from": date_from,
                "date_to": date_to,
                "device": device_id,
            }
        )

        return render(
            request,
            "./inventory_monitor/probe_diff.html",
            {
                "probes_added": probes_added,
                "probes_removed": probes_removed,
                "form": form,
            },
        )

    def get(self, request):
        form = forms.ProbeDiffForm()

        return render(
            request,
            "./inventory_monitor/probe_diff.html",
            {
                "form": form,
            },
        )
