# Generated by Django 1.11.11 on 2018-04-25 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0051_modify_apikey_user_ordering"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="last_modified_time",
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
