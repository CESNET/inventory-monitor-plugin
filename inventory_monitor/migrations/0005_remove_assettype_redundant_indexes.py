from django.db import migrations


class Migration(migrations.Migration):
    """
    Remove redundant non-unique indexes on AssetType.name and AssetType.slug.
    These fields already have unique=True which creates a unique index;
    the explicit Meta.indexes entries created duplicate non-unique indexes
    that caused conflicts with netbox-branching's schema reconciliation.
    """

    dependencies = [
        ("inventory_monitor", "0004_alter_asset_tags_alter_assetservice_tags_and_more"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="assettype",
            name="inventory_m_name_a65ffe_idx",
        ),
        migrations.RemoveIndex(
            model_name="assettype",
            name="inventory_m_slug_e2f652_idx",
        ),
    ]
