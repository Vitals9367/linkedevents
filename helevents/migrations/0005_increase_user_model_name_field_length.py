# Generated by Django 3.2 on 2023-02-01 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("helevents", "0004_auto_20180109_1727"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="last name"
            ),
        ),
    ]
