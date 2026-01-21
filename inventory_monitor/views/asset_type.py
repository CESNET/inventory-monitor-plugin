from netbox.views import generic
from utilities.query import count_related
from utilities.views import GetRelatedModelsMixin, register_model_view

from inventory_monitor import filtersets, forms, models, tables


@register_model_view(models.AssetType)
class AssetTypeView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = models.AssetType.objects.all()

    def get_extra_context(self, request, instance):
        return {
            "related_models": self.get_related_models(request, instance),
        }


@register_model_view(models.AssetType, "list", path="", detail=False)
class AssetTypeListView(generic.ObjectListView):
    queryset = models.AssetType.objects.annotate(asset_count=count_related(models.Asset, "type"))
    table = tables.AssetTypeTable
    filterset = filtersets.AssetTypeFilterSet
    filterset_form = forms.AssetTypeFilterForm
    actions = {
        "add": {"add"},
        "export": set(),
        "bulk_edit": {"change"},
        "bulk_delete": {"delete"},
    }


@register_model_view(models.AssetType, "add", detail=False)
@register_model_view(models.AssetType, "edit")
class AssetTypeEditView(generic.ObjectEditView):
    queryset = models.AssetType.objects.all()
    form = forms.AssetTypeForm


@register_model_view(models.AssetType, "delete")
class AssetTypeDeleteView(generic.ObjectDeleteView):
    queryset = models.AssetType.objects.all()


@register_model_view(models.AssetType, "bulk_edit", path="edit", detail=False)
class AssetTypeBulkEditView(generic.BulkEditView):
    queryset = models.AssetType.objects.all()
    filterset = filtersets.AssetTypeFilterSet
    table = tables.AssetTypeTable
    form = forms.AssetTypeBulkEditForm


@register_model_view(models.AssetType, "bulk_delete", path="delete", detail=False)
class AssetTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AssetType.objects.all()
    filterset = filtersets.AssetTypeFilterSet
    table = tables.AssetTypeTable
    default_return_url = "plugins:inventory_monitor:assettype_list"
