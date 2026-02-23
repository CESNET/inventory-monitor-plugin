# Asset views
from inventory_monitor.views.asset import (
    AssetView,
    AssetListView,
    AssetEditView,
    AssetDeleteView,
    AssetBulkEditView,
    AssetBulkDeleteView,
    AssetBulkImportView,
    AssetExternalInventoryAssignmentView,
)

# Asset Service views
from inventory_monitor.views.asset_service import (
    AssetServiceView,
    AssetServiceListView,
    AssetServiceCreateView,
    AssetServiceEditView,
    AssetServiceDeleteView,
    AssetServiceBulkEditView,
    AssetServiceBulkDeleteView,
    AssetServiceBulkImportView,
)

# Asset Type views
from inventory_monitor.views.asset_type import (
    AssetTypeView,
    AssetTypeListView,
    AssetTypeEditView,
    AssetTypeDeleteView,
    AssetTypeBulkEditView,
    AssetTypeBulkDeleteView,
    AssetTypeBulkImportView,
)

# Contract views
from inventory_monitor.views.contract import (
    ContractView,
    ContractListView,
    ContractEditView,
    ContractDeleteView,
    ContractBulkEditView,
    ContractBulkDeleteView,
    ContractBulkImportView,
)

# Contractor views
from inventory_monitor.views.contractor import (
    ContractorView,
    ContractorListView,
    ContractorEditView,
    ContractorDeleteView,
    ContractorBulkEditView,
    ContractorBulkDeleteView,
    ContractorBulkImportView,
)

# External Inventory views
from inventory_monitor.views.external_inventory import (
    ExternalInventoryView,
    ExternalInventoryListView,
    ExternalInventoryEditView,
    ExternalInventoryDeleteView,
    ExternalInventoryBulkEditView,
    ExternalInventoryBulkDeleteView,
    ExternalInventoryBulkImportView,
)

# Invoice views
from inventory_monitor.views.invoice import (
    InvoiceView,
    InvoiceListView,
    InvoiceEditView,
    InvoiceDeleteView,
    InvoiceBulkEditView,
    InvoiceBulkDeleteView,
    InvoiceBulkImportView,
)

# Probe views
from inventory_monitor.views.probe import (
    ProbeView,
    ProbeListView,
    ProbeEditView,
    ProbeDeleteView,
    ProbeBulkDeleteView,
    ProbeBulkEditView,
    ProbeBulkImportView,
    ProbeDiffView,
)

# RMA views
from inventory_monitor.views.rma import (
    RMAView,
    RMAListView,
    RMAEditView,
    RMADeleteView,
    RMABulkEditView,
    RMABulkDeleteView,
    RMABulkImportView,
)

# Define __all__ to explicitly list what should be available when importing from this module
__all__ = [
    # Asset views
    "AssetView",
    "AssetListView",
    "AssetEditView",
    "AssetDeleteView",
    "AssetBulkEditView",
    "AssetBulkDeleteView",
    "AssetBulkImportView",
    "AssetExternalInventoryAssignmentView",
    # Asset Service views
    "AssetServiceView",
    "AssetServiceListView",
    "AssetServiceCreateView",
    "AssetServiceEditView",
    "AssetServiceDeleteView",
    "AssetServiceBulkEditView",
    "AssetServiceBulkDeleteView",
    "AssetServiceBulkImportView",
    # Asset Type views
    "AssetTypeView",
    "AssetTypeListView",
    "AssetTypeEditView",
    "AssetTypeDeleteView",
    "AssetTypeBulkEditView",
    "AssetTypeBulkDeleteView",
    "AssetTypeBulkImportView",
    # Contract views
    "ContractView",
    "ContractListView",
    "ContractEditView",
    "ContractDeleteView",
    "ContractBulkEditView",
    "ContractBulkDeleteView",
    "ContractBulkImportView",
    # Contractor views
    "ContractorView",
    "ContractorListView",
    "ContractorEditView",
    "ContractorDeleteView",
    "ContractorBulkEditView",
    "ContractorBulkDeleteView",
    "ContractorBulkImportView",
    # External Inventory views
    "ExternalInventoryView",
    "ExternalInventoryListView",
    "ExternalInventoryEditView",
    "ExternalInventoryDeleteView",
    "ExternalInventoryBulkEditView",
    "ExternalInventoryBulkDeleteView",
    "ExternalInventoryBulkImportView",
    # Invoice views
    "InvoiceView",
    "InvoiceListView",
    "InvoiceEditView",
    "InvoiceDeleteView",
    "InvoiceBulkEditView",
    "InvoiceBulkDeleteView",
    "InvoiceBulkImportView",
    # Probe views
    "ProbeView",
    "ProbeListView",
    "ProbeEditView",
    "ProbeDeleteView",
    "ProbeBulkDeleteView",
    "ProbeBulkEditView",
    "ProbeBulkImportView",
    "ProbeDiffView",
    # RMA views
    "RMAView",
    "RMAListView",
    "RMAEditView",
    "RMADeleteView",
    "RMABulkEditView",
    "RMABulkDeleteView",
    "RMABulkImportView",
]
