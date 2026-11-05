import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("inventory_monitor", "0008_alter_owner_related_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="externalinventory",
            name="external_location_id",
            field=models.CharField(
                blank=True,
                help_text="Identifier of the location in the external inventory system",
                max_length=64,
                null=True,
                verbose_name="External Location ID",
            ),
        ),
        migrations.AddIndex(
            model_name="externalinventory",
            index=models.Index(fields=["external_location_id"], name="ext_inv_extlocid_idx"),
        ),
        migrations.AddField(
            model_name="externalinventory",
            name="location_assigned_object_id",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="externalinventory",
            name="location_assigned_object_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(("app_label", "dcim"), ("model__in", ("region", "site", "location"))),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddIndex(
            model_name="externalinventory",
            index=models.Index(
                fields=["location_assigned_object_type", "location_assigned_object_id"],
                name="ext_inv_loc_assigned_idx",
            ),
        ),
    ]
