# Generated by Django 2.2.13 on 2022-01-20 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0085_remove_feedback_limit"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasource",
            name="private",
            field=models.BooleanField(
                db_index=True,
                default=False,
                verbose_name="Do not show events created by this data_source by default.",
            ),
        ),
        migrations.AlterField(
            model_name="feedback",
            name="body",
            field=models.TextField(blank=True, max_length=10000, verbose_name="Body"),
        ),
    ]
