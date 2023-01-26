# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-09-27 09:21
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Place = apps.get_model("events", "Place")
    AdministrativeDivision = apps.get_model("munigeo", "AdministrativeDivision")

    for place in Place.geo_objects.filter(position__isnull=False):
        place.divisions.set(
            AdministrativeDivision.objects.filter(
                type__type__in=("district", "sub_district", "neighborhood", "muni"),
                geometry__boundary__contains=place.position,
            )
        )


class Migration(migrations.Migration):

    dependencies = [
        ("munigeo", "0003_add_modified_time_to_address_and_street"),
        ("events", "0030_merge"),
    ]

    operations = [
        migrations.AddField(
            model_name="place",
            name="divisions",
            field=models.ManyToManyField(
                blank=True,
                related_name="places",
                to="munigeo.AdministrativeDivision",
                verbose_name="Divisions",
            ),
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
