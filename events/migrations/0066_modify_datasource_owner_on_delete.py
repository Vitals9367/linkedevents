# Generated by Django 2.2.9 on 2020-01-08 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0065_set_editable_false_on_mptt_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datasource",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="owned_systems",
                to="django_orghierarchy.Organization",
            ),
        ),
    ]
