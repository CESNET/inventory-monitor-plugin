from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import render
from django.views.generic import View
from netbox.views import generic
from utilities.views import register_model_view

from inventory_monitor import filtersets, forms, models, tables


class ProbeView(generic.ObjectView):
    queryset = models.Probe.objects.all()


class ProbeListView(generic.ObjectListView):
    sub_count_serial = (
        models.Probe.objects.filter(serial=OuterRef("serial")).values("serial").annotate(changes_count=Count("*"))
    )
    queryset = (
        models.Probe.objects.select_related("device", "site", "location")
        .prefetch_related("tags")
        .annotate(changes_count=Subquery(sub_count_serial.values("changes_count")))
    )

    table = tables.EnhancedProbeTable
    filterset = filtersets.ProbeFilterSet
    filterset_form = forms.ProbeFilterForm
    template_name = "inventory_monitor/probe_list.html"  # Custom template with CSS


class ProbeEditView(generic.ObjectEditView):
    queryset = models.Probe.objects.all()
    form = forms.ProbeForm


class ProbeDeleteView(generic.ObjectDeleteView):
    queryset = models.Probe.objects.all()


class ProbeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Probe.objects.all()
    filterset = filtersets.ProbeFilterSet
    table = tables.ProbeTable


@register_model_view(models.Probe, "bulk_edit", path="edit", detail=False)
class ProbeBulkEditView(generic.BulkEditView):
    queryset = models.Probe.objects.all()
    filterset = filtersets.ProbeFilterSet
    table = tables.ProbeTable
    form = forms.ProbeBulkEditForm


@register_model_view(models.Probe, "bulk_import", path="import", detail=False)
class ProbeBulkImportView(generic.BulkImportView):
    queryset = models.Probe.objects.all()
    model_form = forms.ProbeBulkImportForm


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
        probes_removed = models.Probe.objects.filter(device_id=device_id, time__gte=date_from, time__lte=date_to)

        form = forms.ProbeDiffForm(
            initial={
                "date_from": date_from,
                "date_to": date_to,
                "device": device_id,
            }
        )

        return render(
            request,
            "inventory_monitor/probe_diff.html",
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
