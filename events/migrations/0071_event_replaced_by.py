# Generated by Django 2.2.9 on 2020-01-30 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0070_keyword_replaced_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="replaced_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="aliases",
                to="events.Event",
            ),
        ),
    ]
