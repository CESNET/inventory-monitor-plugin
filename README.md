# NetBox Inventory Monitor Plugin

A comprehensive NetBox plugin for asset management with semi-automatic discovery processes. This plugin extends NetBox with powerful inventory tracking capabilities, including asset lifecycle management, probe monitoring, contract tracking, and RMA (Return Merchandise Authorization) processing.

[![Version](https://img.shields.io/badge/version-11.1.0b3-blue.svg)](https://gitlab.cesnet.cz/701/done/inventory-monitor-plugin)
[![NetBox](https://img.shields.io/badge/netbox-4.4.x-green.svg)](https://github.com/netbox-community/netbox)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

---

## Features

- **🏷️ Asset Management**: Track physical and logical assets with detailed metadata
- **📊 Probe Monitoring**: Visual status indicators for discovery data populated by external scripts (e.g., SNMP scans)
- **📝 Contract Tracking**: Manage contracts, contractors, and invoicing with multi-currency support
- **🔄 RMA Processing**: Complete RMA workflow with serial number tracking
- **🏢 External Inventory**: Integration with external inventory systems with configurable status mappings
- **🛠️ Asset Services**: Track maintenance and service contracts with multi-currency pricing
- **📈 Lifecycle Management**: Full asset lifecycle status tracking
- **🔍 Advanced Search**: Powerful filtering and search capabilities with GraphQL support
- **🎨 Visual Interface**: Rich UI with status indicators and color coding
- **🔌 NetBox Integration**: Native NetBox plugin following best practices
- **💱 Multi-Currency Support**: Configurable currency support for all financial fields (assets, contracts, invoices, services)

---

## Table of Contents

- [Features](#features)
- [Data Model Overview](#data-model-overview)
- [Data Models](#data-models)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API](#api)
- [Development](#development)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Data Model Overview

```mermaid
classDiagram
    class AssetType {
        +CharField name
        +SlugField slug
        +CharField description
        +ColorField color
    }

    class Asset {
        +CharField serial
        +CharField partnumber
        +CharField assignment_status
        +CharField lifecycle_status
        +GenericForeignKey assigned_object
        +ForeignKey type
        +ForeignKey order_contract
        +CharField project
        +CharField vendor
        +DecimalField price
        +CharField currency
        +DateField warranty_start
        +DateField warranty_end
        +is_recently_probed()
    }

    class AssetService {
        +DateField service_start
        +DateField service_end
        +DecimalField service_price
        +CharField service_currency
        +CharField service_category
        +CharField service_category_vendor
        +ForeignKey asset
        +ForeignKey contract
    }

    class Contract {
        +CharField name
        +CharField name_internal
        +ForeignKey contractor
        +CharField type
        +DecimalField price
        +CharField currency
        +DateField signed
        +DateField invoicing_start
        +DateField invoicing_end
        +ForeignKey parent
    }

    class Contractor {
        +CharField name
        +CharField company
        +CharField address
        +ForeignKey tenant
    }

    class Invoice {
        +CharField name
        +CharField project
        +ForeignKey contract
        +DecimalField price
        +CharField currency
        +DateField invoicing_start
        +DateField invoicing_end
    }

    class Probe {
        +DateTimeField time
        +CharField device_descriptor
        +CharField site_descriptor
        +CharField location_descriptor
        +CharField serial
        +ForeignKey device
        +ForeignKey site
        +ForeignKey location
        +JSONField discovered_data
        +is_recently_probed()
    }

    class RMA {
        +CharField rma_number
        +ForeignKey asset
        +CharField original_serial
        +CharField replacement_serial
        +CharField status
        +DateField date_issued
        +DateField date_replaced
        +update_asset_serial()
    }

    class ExternalInventory {
        +CharField inventory_number
        +CharField status
        +CharField project_code
        +CharField user_name
        +ManyToManyField assets
    }

    AssetType --> Asset : "type"
    Asset --> AssetService : "asset"
    Asset --> RMA : "asset"
    Asset --> Probe : "serial"
    Contract --> Asset : "order_contract"
    Contract --> AssetService : "contract"
    Contractor --> Contract : "contractor"
    Contract --> Invoice : "contract"
    Contract --> Contract : "parent"
    ExternalInventory --> Asset : "assets"

    Asset --> Device : "assigned_object"
    Asset --> Site : "assigned_object"
    Asset --> Location : "assigned_object"
```

---

## Data Models

### Core Models

#### **Asset**
The central model representing physical or logical inventory items.

**Key Fields:**
- `serial`: Unique identifier for the asset
- `partnumber`: Manufacturer part number
- `description`: Asset description
- `assignment_status`: Current assignment status (reserved, deployed, loaned, stocked)
- `lifecycle_status`: Lifecycle stage (new, in_stock, in_use, in_maintenance, retired, disposed)
- `assigned_object`: Generic foreign key to NetBox objects (Device, Site, Location, Rack, Module)
- `type`: Link to AssetType for categorization
- `order_contract`: Associated purchase contract
- `project`: Project identifier
- `vendor`: Vendor name
- `quantity`: Number of items (default: 1)
- `price`: Asset purchase price (DecimalField, nullable)
- `currency`: Price currency (CharField, nullable - required only when price is set and non-zero)
- `warranty_start/end`: Warranty period tracking

**Special Features:**
- Probe status integration with `is_recently_probed()` method
- Generic assignment to Site, Location, Rack, Device, Module via GenericForeignKey
- Integration with External Inventory systems via many-to-many relationship
- Multi-currency support with configurable currency codes and symbols
- Currency validation enforced only when price > 0
- External inventory assignment management with dedicated form
- Comprehensive filtering including external inventory number search

#### **Probe**
Discovery and monitoring data collection points populated by external scripts (e.g., SNMP discovery tools).

**Key Fields:**
- `time`: Timestamp of the probe data collection
- `serial`: Links to Asset via serial number matching
- `device_descriptor`, `site_descriptor`, `location_descriptor`: Context information from discovery
- `discovered_data`: JSON field for flexible data storage from external tools
- `category`: Probe type classification

**Note**: Probe data is populated by external discovery scripts, not generated by the plugin itself.

#### **Contract & Contractor**
Business relationship management with full currency support.

**Contract Features:**
- Hierarchical contracts (parent/child relationships)
- Contract types (purchase, service, support, warranty, lease, subscription, other)
- Invoice tracking with multi-currency support
- Service associations
- Asset procurement tracking
- Multi-currency pricing support with configurable currencies
- Currency required only when price is set and non-zero (price can be None, 0, or > 0)
- Date tracking (signed, invoicing_start, invoicing_end)

#### **RMA (Return Merchandise Authorization)**
Complete RMA workflow management with serial number tracking.

**Key Features:**
- Status tracking (investigating, authorized, shipped, in_transit, completed, cancelled)
- Automatic serial number updates upon completion
- Original and replacement serial number tracking
- Integration with Asset lifecycle
- Date tracking (issued, replaced)
- Associated with Assets via foreign key

#### **AssetService**
Service and maintenance contract tracking.

**Features:**
- Service period management
- Pricing with multi-currency support (service_price, service_currency)
- Category tracking (service_category, service_category_vendor)
- Links to both Assets and Contracts
- Currency required only when service price is set

#### **ExternalInventory**
Integration with external inventory management systems.

**Key Fields:**
- `external_id`: Unique identifier from external system
- `inventory_number`: Asset number from external system
- `name`: Item name or description
- `serial_number`: Serial or production number
- `person_id/person_name`: Responsible person information
- `location_code/location`: Location information
- `department_code`: Department code
- `project_code`: Project code
- `user_name/user_note`: User information and notes
- `split_asset`: Whether this is a split/shared asset
- `status`: Current status code (configurable via plugin settings)
- `assets`: Many-to-many relationship with Assets

**Features:**
- Many-to-many relationship with Assets
- Configurable status display with labels and colors
- Status configuration via plugin settings
- Dynamic status tooltips with customizable templates
- Project code tracking
- Comprehensive filtering by all fields
- RMA integration via external_id matching

---

## Installation

### Requirements

- NetBox 4.4.0 or higher
- Python 3.10 or higher

### From PyPI (Recommended)

```bash
pip install inventory-monitor
```

### From Source

```bash
git clone https://github.com/CESNET/inventory-monitor-plugin.git
cd inventory-monitor-plugin
pip install .
```

### NetBox Configuration

1. Add the plugin to your NetBox `configuration.py`:

```python
PLUGINS = [
    "inventory_monitor",
]
```

2. Run database migrations:

```bash
python manage.py migrate
```

3. Restart NetBox services:

```bash
sudo systemctl restart netbox netbox-rq
```

---

## Configuration

### Plugin Settings

Configure the plugin in your NetBox `configuration.py`:

```python
PLUGINS_CONFIG = {
    "inventory_monitor": {
        # Probe Status Settings
        "probe_recent_days": 7,  # Days to consider probe "recent"
        
        # Currency Settings
        "currencies": [
            ("CZK", "Czech Koruna", "Kč"),
            ("EUR", "Euro", "€"),
            ("USD", "US Dollar", "$"),
            ("GBP", "British Pound", "£"),
            ("JPY", "Japanese Yen", "¥"),
        ],
        "default_currency": "EUR",  # Default currency for new records
        
        # External Inventory Status Configuration (Optional)
        "external_inventory_status_config": {
            "1": {"label": "Active", "color": "success"},
            "0": {"label": "Pending Activation", "color": "warning"},
            "2": {"label": "Decommissioned", "color": "danger"},
        },
        
        # Custom tooltip template for status display (Optional)
        "external_inventory_tooltip_template": "<span class='badge text-bg-{color}'>{code}</span> {label}",
    }
}
```

### Configuration Options

#### Probe Status Settings
- **`probe_recent_days`** (default: 7): Number of days to consider a probe "recent". Affects visual indicators and status badges.

#### Currency Settings
- **`currencies`** (default: see example above): List of available currencies for all financial models (Assets, Contracts, Invoices, AssetServices). Each item is a tuple of `(currency_code, display_name, symbol)`. 
  - `currency_code`: Currency identifier (e.g., "EUR", "USD", "CZK") - no length restrictions
  - `display_name`: Human-readable name shown in forms
  - `symbol`: Currency symbol for display (e.g., "€", "$", "Kč") - **optional** (if omitted, currency code is used)
- **`default_currency`** (default: "EUR"): Default currency code used when creating new records. Must match one of the codes in the `currencies` list.

**Price and Currency Validation:**
- Price fields are DecimalField (max_digits=19, decimal_places=2, nullable)
- **`price = None`**: No pricing information - currency optional
- **`price = 0`**: Free/no charge - currency optional  
- **`price > 0`**: Actual cost - currency **required** and validated in model's clean() method
- Applies to: Asset.price, Contract.price, Invoice.price, AssetService.service_price

#### External Inventory Status Configuration
- **`external_inventory_status_config`** (optional): Maps status codes to display labels and Bootstrap colors. If not configured, status displays as-is without special formatting.
- **`external_inventory_tooltip_template`** (optional, default: `"<span class='badge text-bg-{color}'>{code}</span> {label}"`): Template string for formatting status tooltips

**Status Configuration Structure:**
```python
{
    "status_code": {
        "label": "Human readable label",
        "color": "bootstrap_color_class"  # primary, secondary, success, danger, warning, info, light, dark
    }
}
```

**Template Variables:**
- `{code}`: The status code
- `{label}`: The display label from configuration
- `{color}`: The Bootstrap color class

**How it works:**
- ExternalInventory model provides `get_status_color()` and `get_status_display()` methods
- Status badge shown in tables using configured colors
- Tooltip generated dynamically from all configured statuses
- Form help text automatically populated with available status codes
- If not configured, displays raw status value without special formatting

### Integration with NetBox Attachments

For file attachments, install and configure [netbox-attachments](https://github.com/Kani999/netbox-attachments):

```bash
pip install netbox-attachments
```

---

## Usage

### Accessing the Plugin

After installation, the plugin adds an "Inventory Monitor" section to the NetBox navigation menu with the following sections:

#### Assets
- **Assets**: Main asset inventory management
- **Asset Types**: Asset categorization and classification
- **RMA**: Return Merchandise Authorization tracking
- **External Inventory**: External system integration
- **Services**: Asset service and maintenance contracts

#### Network Probe
- **Probes**: Discovery and monitoring data
- **Data Locations**: Probe data organization

#### Contracts
- **Contractors**: Vendor and service provider management
- **Contracts**: Business agreement tracking
- **Invoices**: Billing and invoice management

### Basic Workflow

1. **Set up Asset Types**: Define categories for your assets
2. **Add Contractors**: Register vendors and service providers
3. **Create Contracts**: Define business agreements
4. **Register Assets**: Add inventory items with full metadata
5. **Populate Probe Data**: Use external scripts (SNMP, discovery tools) to populate monitoring data
6. **Track Services**: Manage maintenance and service contracts
7. **Process RMAs**: Handle return merchandise authorizations

### Probe Status Monitoring

The plugin provides visual feedback for probe status:
- **Green indicators**: Recent probes (within configured days)
- **Red indicators**: Stale probes (older than configured threshold)
- **Status badges**: Clear visual indicators in asset lists and details

### Asset Assignment

Assets can be assigned to any NetBox object using GenericForeignKey:
- Devices
- Sites
- Locations
- Racks
- Modules

### External Inventory Assignment

The plugin provides a dedicated form (`AssetExternalInventoryAssignmentForm`) for managing the many-to-many relationship between Assets and External Inventory items. This form:

- **Skips unrelated model validation** - Overrides `_post_clean()` to avoid validating price/currency when only managing external inventory relationships
- **Uses `clean_fields()` instead of `full_clean()`** - Prevents cross-field validation errors for fields not in the form
- **Manages only the many-to-many relationship** - Doesn't modify other Asset fields like price, currency, serial, etc.
- **Creates snapshots** - Automatically creates snapshots of ExternalInventory items when relationships change
- **Accessible via Asset detail page** - "Edit External Inventory" button provides direct access

This specialized form prevents validation errors like `'AssetExternalInventoryAssignmentForm' has no field named 'currency'` that would occur if the full Asset model validation ran.

---

## API

The plugin provides a full REST API following NetBox patterns:

### Available Endpoints

- `/api/plugins/inventory-monitor/assets/` - Asset management
- `/api/plugins/inventory-monitor/asset-types/` - Asset type management
- `/api/plugins/inventory-monitor/probes/` - Probe data access
- `/api/plugins/inventory-monitor/contracts/` - Contract management
- `/api/plugins/inventory-monitor/contractors/` - Contractor management
- `/api/plugins/inventory-monitor/invoices/` - Invoice tracking
- `/api/plugins/inventory-monitor/asset-services/` - Service management
- `/api/plugins/inventory-monitor/rmas/` - RMA processing
- `/api/plugins/inventory-monitor/external-inventory/` - External inventory integration

### API Features

- **Full CRUD operations** on all models
- **Advanced filtering** with NetBox's built-in filter backend
- **Pagination** for large datasets
- **Search capabilities** across relevant fields
- **Bulk operations** for efficient data management
- **OpenAPI/Swagger documentation** at `/api/docs/`


---

## Development

### Architecture Overview

The plugin follows NetBox plugin best practices:

#### Models Architecture
```
Asset ←→ Probe (via serial number matching)
Asset → AssetType
Asset → Contract (order_contract)
Asset ← GenericForeignKey (assigned to Device, Site, Location, Rack, Module)
Asset ←→ RMA (via serial numbers: original_serial, replacement_serial)
Asset ←→ ExternalInventory (many-to-many via assets field)
Asset ← AssetService (via asset ForeignKey)

Contract → Contractor (via contractor ForeignKey)
Contract → Contract (parent, self-referential for hierarchical contracts)
Contract ← Invoice (via contract ForeignKey)
Contract ← AssetService (via contract ForeignKey)

ExternalInventory ←→ Asset (many-to-many relationship)
ExternalInventory ← RMA (matched via external_id for display)
```

#### Key Components
1. **Models**: Core business logic with probe status methods, currency validation, date status mixins
2. **Views**: Standard NetBox generic views (ObjectView, ObjectListView, ObjectEditView, ObjectDeleteView, BulkEditView, BulkImportView, BulkDeleteView)
3. **Tables**: Django-tables2 with probe status indicators, color-coded status badges, custom column templates
4. **Forms**: NetBox forms with custom validation, currency choices, specialized assignment forms
5. **Filtersets**: Comprehensive filtering for all models with custom lookups
6. **Templates**: Custom templates with integrated status visualization, HTMX support for dynamic updates
7. **API**: DRF-based REST API following NetBox patterns with full CRUD operations
8. **GraphQL**: Strawberry GraphQL schema with queries for all models
9. **Template Tags**: Custom template tags for status display and external inventory tooltips
10. **Settings Helpers**: Centralized configuration access via settings.py module

### Performance Considerations

- **Database Optimizations**: Proper indexing on frequently queried fields (serial, inventory_number, status, etc.)
- **Query Optimization**: Use of `select_related()` and `prefetch_related()` in views and tables
- **Caching**: Consider caching probe status for large asset lists
- **M2M Relationships**: External inventory assignments use efficient many-to-many queries

### Settings Access Pattern

```python
# Recommended approach - use helper functions
from inventory_monitor.settings import (
    get_probe_recent_days,
    get_currency_choices,
    get_external_inventory_status_config_safe,
    get_external_inventory_tooltip_template,
)

days = get_probe_recent_days()
currencies = get_currency_choices()
status_config, is_configured = get_external_inventory_status_config_safe()
tooltip_template = get_external_inventory_tooltip_template()

# Alternative approach - direct settings access
from inventory_monitor.settings import get_plugin_settings
settings = get_plugin_settings()
days = settings.get("probe_recent_days", 7)
```

---

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

## Acknowledgments

- Built for the [NetBox](https://github.com/netbox-community/netbox) ecosystem
- Part of the CESNET infrastructure management toolkit