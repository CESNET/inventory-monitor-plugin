from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label="Inventory Monitor",
    icon_class="mdi mdi-monitor",
    groups=(
        (
            "Assets",
            (
                PluginMenuItem(
                    link="plugins:inventory_monitor:asset_list",
                    link_text="Assets",
                    permissions=["inventory_monitor.view_asset"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:asset_add",
                            title="Add Asset",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_asset"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:asset_bulk_import",
                            title="Import Assets",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_asset"],
                        ),
                    ],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:assettype_list",
                    link_text="Asset Types",
                    permissions=["inventory_monitor.view_assettype"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:assettype_add",
                            title="Add Asset Type",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_assettype"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:assettype_bulk_import",
                            title="Import Asset Types",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_assettype"],
                        ),
                    ],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:rma_list",
                    link_text="RMA",
                    permissions=["inventory_monitor.view_rma"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:rma_add",
                            title="Add RMA",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_rma"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:rma_bulk_import",
                            title="Import RMA",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_rma"],
                        ),
                    ],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:externalinventory_list",
                    link_text="External Inventory",
                    permissions=["inventory_monitor.view_externalinventory"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:externalinventory_add",
                            title="Add External Inventory",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_externalinventory"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:externalinventory_bulk_import",
                            title="Import External Inventory",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_externalinventory"],
                        ),
                    ],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:assetservice_list",
                    link_text="Services",
                    permissions=["inventory_monitor.view_assetservice"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:assetservice_add",
                            title="Add Service",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_assetservice"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:assetservice_bulk_import",
                            title="Import Services",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_assetservice"],
                        ),
                    ],
                ),
            ),
        ),
        (
            "Network Probe",
            (
                PluginMenuItem(
                    link="plugins:inventory_monitor:probe_list",
                    link_text="Probes",
                    permissions=["inventory_monitor.view_probe"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:probe_add",
                            title="Add Probe",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_probe"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:probe_bulk_import",
                            title="Import Probes",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_probe"],
                        ),
                    ],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:probediff",
                    link_text="Network Changes",
                    permissions=["inventory_monitor.view_probediff"],
                ),
            ),
        ),
        (
            "Contracts",
            (
                PluginMenuItem(
                    link="plugins:inventory_monitor:contractor_list",
                    link_text="Contractors",
                    permissions=["inventory_monitor.view_contractor"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:contractor_add",
                            title="Add Contractor",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_contractor"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:contractor_bulk_import",
                            title="Import Contractors",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_contractor"],
                        ),
                    ],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:contract_list",
                    link_text="Contracts",
                    permissions=["inventory_monitor.view_contract"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:contract_add",
                            title="Add Contract",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_contract"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:contract_bulk_import",
                            title="Import Contracts",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_contract"],
                        ),
                    ],
                ),
                PluginMenuItem(
                    link="plugins:inventory_monitor:invoice_list",
                    link_text="Invoices",
                    permissions=["inventory_monitor.view_invoice"],
                    buttons=[
                        PluginMenuButton(
                            link="plugins:inventory_monitor:invoice_add",
                            title="Add Invoice",
                            icon_class="mdi mdi-plus-thick",
                            color=ButtonColorChoices.GREEN,
                            permissions=["inventory_monitor.add_invoice"],
                        ),
                        PluginMenuButton(
                            link="plugins:inventory_monitor:invoice_bulk_import",
                            title="Import Invoices",
                            icon_class="mdi mdi-upload",
                            color=ButtonColorChoices.CYAN,
                            permissions=["inventory_monitor.add_invoice"],
                        ),
                    ],
                ),
            ),
        ),
    ),
)
