# Generated by Django 2.2.13 on 2022-05-09 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0086_private_datasource"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="alt_text_ar",
            field=models.CharField(
                blank=True, max_length=320, null=True, verbose_name="Alt text"
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="alt_text_en",
            field=models.CharField(
                blank=True, max_length=320, null=True, verbose_name="Alt text"
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="alt_text_fi",
            field=models.CharField(
                blank=True, max_length=320, null=True, verbose_name="Alt text"
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="alt_text_ru",
            field=models.CharField(
                blank=True, max_length=320, null=True, verbose_name="Alt text"
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="alt_text_sv",
            field=models.CharField(
                blank=True, max_length=320, null=True, verbose_name="Alt text"
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="alt_text_zh_hans",
            field=models.CharField(
                blank=True, max_length=320, null=True, verbose_name="Alt text"
            ),
        ),
    ]
