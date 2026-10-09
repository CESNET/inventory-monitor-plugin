from django.urls import include, path
from netbox.views.generic import ObjectChangeLogView
from utilities.urls import get_model_urls

from inventory_monitor import models, views

app_name = "inventory_monitor"  # Add this line to define the app namespace

urlpatterns = (
    ## Probes
    path("probes/", views.ProbeListView.as_view(), name="probe_list"),
    path("probes/add/", views.ProbeEditView.as_view(), name="probe_add"),
    path("probes/<int:pk>/", views.ProbeView.as_view(), name="probe"),
    path("probes/<int:pk>/edit/", views.ProbeEditView.as_view(), name="probe_edit"),
    path("probes/<int:pk>/delete/", views.ProbeDeleteView.as_view(), name="probe_delete"),
    path(
        "probes/delete/",
        views.ProbeBulkDeleteView.as_view(),
        name="probe_bulk_delete",
    ),
    # INFO: Changelog needs to be add manually, cause Probe model is not derived from NetBoxModel
    path(
        "probes/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="probe_changelog",
        kwargs={"model": models.Probe},
    ),
    # Adds url's like changelog, journal, attachments (from plugin) and etc.
    path(
        "probes/<int:pk>/",
        include(get_model_urls("inventory_monitor", "probe")),
    ),
    path(
        "probes/",
        include(get_model_urls("inventory_monitor", "probe", detail=False)),
    ),
    ## Probe Diff
    path("probe_diff/", views.ProbeDiffView.as_view(), name="probediff"),
    ## Contracts
    path("contracts/", include(get_model_urls("inventory_monitor", "contract", detail=False))),
    path("contracts/<int:pk>/", include(get_model_urls("inventory_monitor", "contract"))),
    ## Invoice
    path("invoices/", include(get_model_urls("inventory_monitor", "invoice", detail=False))),
    path("invoices/<int:pk>/", include(get_model_urls("inventory_monitor", "invoice"))),
    ## Asset
    path("assets/", include(get_model_urls("inventory_monitor", "asset", detail=False))),
    path("assets/<int:pk>/", include(get_model_urls("inventory_monitor", "asset"))),
    ## AssetType
    path("asset-types/", include(get_model_urls("inventory_monitor", "assettype", detail=False))),
    path("asset-types/<int:pk>/", include(get_model_urls("inventory_monitor", "assettype"))),
    ## External Inventory (formerly ABRA)
    path("external-inventory/", include(get_model_urls("inventory_monitor", "externalinventory", detail=False))),
    path("external-inventory/<int:pk>/", include(get_model_urls("inventory_monitor", "externalinventory"))),
    ## AssetService
    path(
        "asset-services/<int:pk>/",
        include(get_model_urls("inventory_monitor", "assetservice")),
    ),
    path(
        "asset-services/",
        include(get_model_urls("inventory_monitor", "assetservice", detail=False)),
    ),
    ## RMA
    path("rmas/", include(get_model_urls("inventory_monitor", "rma", detail=False))),
    path("rmas/<int:pk>/", include(get_model_urls("inventory_monitor", "rma"))),
    ## Contractor
    path("contractors/", include(get_model_urls("inventory_monitor", "contractor", detail=False))),
    path("contractors/<int:pk>/", include(get_model_urls("inventory_monitor", "contractor"))),
)
