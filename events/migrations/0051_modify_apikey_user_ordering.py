# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-27 12:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0050_lengthen_offer_price_field"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="apikeyuser",
            options={"ordering": ("id",)},
        ),
    ]
