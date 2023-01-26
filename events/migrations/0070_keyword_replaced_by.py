# Generated by Django 2.2.9 on 2020-01-20 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0069_video"),
    ]

    operations = [
        migrations.AddField(
            model_name="keyword",
            name="replaced_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="aliases",
                to="events.Keyword",
            ),
        ),
    ]
