from django.db.models import Count, OuterRef, Subquery
from django.shortcuts import render
from django.views.generic import View
from netbox.views import generic
from utilities.views import ObjectPermissionRequiredMixin, register_model_view

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


class ProbeDiffView(ObjectPermissionRequiredMixin, View):
    queryset = models.Probe.objects.all()
    template_name = "inventory_monitor/probe_diff.html"

    def get_required_permission(self):
        return "inventory_monitor.view_probe"

    def get(self, request):
        return render(request, self.template_name, {"form": forms.ProbeDiffForm()})

    def post(self, request):
        form = forms.ProbeDiffForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            # self.queryset is restricted to the user's permitted objects by the mixin
            probes = self.queryset.filter(device=form.cleaned_data["device"])
            date_from, date_to = form.cleaned_data["date_from"], form.cleaned_data["date_to"]
            context["probes_added"] = probes.filter(
                creation_time__date__gte=date_from, creation_time__date__lte=date_to
            )
            context["probes_removed"] = probes.filter(time__date__gte=date_from, time__date__lte=date_to)
        return render(request, self.template_name, context)
