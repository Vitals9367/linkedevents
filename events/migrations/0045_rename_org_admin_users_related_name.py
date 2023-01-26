# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-24 12:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0044_add_apikey_user_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="admin_users",
            field=models.ManyToManyField(
                blank=True,
                related_name="admin_old_organizations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
