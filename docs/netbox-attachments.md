# netbox-attachments Integration

inventory-monitor optionally integrates with the
[netbox-attachments](https://github.com/Kani999/netbox-attachments) plugin
to display attachment counts on Contract and Invoice list views.

## Requirements

- netbox-attachments **>= 11.0.0**
- NetBox **>= 4.5.4**
- inventory-monitor **>= 13.1.0**

> **Note:** inventory-monitor 13.0.x does not support netbox-attachments.
> If you used netbox-attachments with inventory-monitor 12.x, upgrade
> netbox-attachments to >= 11.0.0 before enabling this integration.

## Installation

1. Install netbox-attachments:

   ```
   pip install "netbox-attachments>=11.0.0"
   ```

2. Add `netbox_attachments` to `PLUGINS` in your NetBox configuration.

3. Enable the integration in your inventory-monitor plugin config:

   ```python
   PLUGINS_CONFIG = {
       "inventory_monitor": {
           "enable_netbox_attachments": True,
       }
   }
   ```

4. Run migrations:

   ```
   python manage.py migrate
   ```

## Behaviour without netbox-attachments

If `enable_netbox_attachments` is `False` (the default) or if the package is not
installed, the plugin starts normally — attachment columns are simply absent from
list views. No errors are raised.
