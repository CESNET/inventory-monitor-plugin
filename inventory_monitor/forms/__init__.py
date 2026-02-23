# Asset forms
from inventory_monitor.forms.asset import (
    AssetForm,
    AssetFilterForm,
    AssetBulkEditForm,
    AssetBulkImportForm,
    AssetExternalInventoryAssignmentForm,
)

# Asset Service forms
from inventory_monitor.forms.asset_service import (
    AssetServiceForm,
    AssetServiceFilterForm,
    AssetServiceBulkEditForm,
    AssetServiceBulkImportForm,
)

# Asset Type forms
from inventory_monitor.forms.asset_type import (
    AssetTypeForm,
    AssetTypeBulkEditForm,
    AssetTypeFilterForm,
    AssetTypeBulkImportForm,
)

# Contract forms
from inventory_monitor.forms.contract import (
    ContractForm,
    ContractFilterForm,
    ContractBulkEditForm,
    ContractBulkImportForm,
)

# Contractor forms
from inventory_monitor.forms.contractor import (
    ContractorForm,
    ContractorFilterForm,
    ContractorBulkEditForm,
    ContractorBulkImportForm,
)

# External Inventory forms
from inventory_monitor.forms.external_inventory import (
    ExternalInventoryForm,
    ExternalInventoryBulkEditForm,
    ExternalInventoryFilterForm,
    ExternalInventoryBulkImportForm,
)

# Invoice forms
from inventory_monitor.forms.invoice import (
    InvoiceForm,
    InvoiceFilterForm,
    InvoiceBulkEditForm,
    InvoiceBulkImportForm,
)

# Probe forms
from inventory_monitor.forms.probe import (
    ProbeForm,
    ProbeFilterForm,
    ProbeDiffForm,
    ProbeBulkEditForm,
    ProbeBulkImportForm,
)

# RMA forms
from inventory_monitor.forms.rma import (
    RMAForm,
    RMAFilterForm,
    RMABulkEditForm,
    RMABulkImportForm,
)

# Define __all__ to explicitly list what should be available when importing from this module
__all__ = [
    # Asset forms
    "AssetForm",
    "AssetFilterForm",
    "AssetBulkEditForm",
    "AssetBulkImportForm",
    "AssetExternalInventoryAssignmentForm",
    # Asset Service forms
    "AssetServiceForm",
    "AssetServiceFilterForm",
    "AssetServiceBulkEditForm",
    "AssetServiceBulkImportForm",
    # Asset Type forms
    "AssetTypeForm",
    "AssetTypeBulkEditForm",
    "AssetTypeFilterForm",
    "AssetTypeBulkImportForm",
    # Contract forms
    "ContractForm",
    "ContractFilterForm",
    "ContractBulkEditForm",
    "ContractBulkImportForm",
    # Contractor forms
    "ContractorForm",
    "ContractorFilterForm",
    "ContractorBulkEditForm",
    "ContractorBulkImportForm",
    # External Inventory forms
    "ExternalInventoryForm",
    "ExternalInventoryBulkEditForm",
    "ExternalInventoryFilterForm",
    "ExternalInventoryBulkImportForm",
    # Invoice forms
    "InvoiceForm",
    "InvoiceFilterForm",
    "InvoiceBulkEditForm",
    "InvoiceBulkImportForm",
    # Probe forms
    "ProbeForm",
    "ProbeFilterForm",
    "ProbeDiffForm",
    "ProbeBulkEditForm",
    "ProbeBulkImportForm",
    # RMA forms
    "RMAForm",
    "RMAFilterForm",
    "RMABulkEditForm",
    "RMABulkImportForm",
]
