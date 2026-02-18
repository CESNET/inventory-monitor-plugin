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
)

# Asset Type forms
from inventory_monitor.forms.asset_type import (
    AssetTypeForm,
    AssetTypeBulkEditForm,
    AssetTypeFilterForm,
)

# Contract forms
from inventory_monitor.forms.contract import (
    ContractForm,
    ContractFilterForm,
    ContractBulkEditForm,
)

# Contractor forms
from inventory_monitor.forms.contractor import (
    ContractorForm,
    ContractorFilterForm,
    ContractorBulkEditForm,
)

# External Inventory forms
from inventory_monitor.forms.external_inventory import (
    ExternalInventoryForm,
    ExternalInventoryBulkEditForm,
    ExternalInventoryFilterForm,
)

# Invoice forms
from inventory_monitor.forms.invoice import (
    InvoiceForm,
    InvoiceFilterForm,
    InvoiceBulkEditForm,
)

# Probe forms
from inventory_monitor.forms.probe import (
    ProbeForm,
    ProbeFilterForm,
    ProbeDiffForm,
    ProbeBulkEditForm,
)

# RMA forms
from inventory_monitor.forms.rma import (
    RMAForm,
    RMAFilterForm,
    RMABulkEditForm,
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
    # Asset Type forms
    "AssetTypeForm",
    "AssetTypeBulkEditForm",
    "AssetTypeFilterForm",
    # Contract forms
    "ContractForm",
    "ContractFilterForm",
    "ContractBulkEditForm",
    # Contractor forms
    "ContractorForm",
    "ContractorFilterForm",
    "ContractorBulkEditForm",
    # External Inventory forms
    "ExternalInventoryForm",
    "ExternalInventoryBulkEditForm",
    "ExternalInventoryFilterForm",
    # Invoice forms
    "InvoiceForm",
    "InvoiceFilterForm",
    "InvoiceBulkEditForm",
    # Probe forms
    "ProbeForm",
    "ProbeFilterForm",
    "ProbeDiffForm",
    "ProbeBulkEditForm",
    # RMA forms
    "RMAForm",
    "RMAFilterForm",
    "RMABulkEditForm",
]
