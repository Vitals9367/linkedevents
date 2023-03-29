# Generated by Django 3.2 on 2023-02-01 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0003_create_default_user_created_template"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationtemplate",
            name="type",
            field=models.CharField(
                choices=[
                    ("unpublished_event_deleted", "Unpublished event deleted"),
                    ("event_published", "Event published"),
                    ("draft_posted", "Draft posted"),
                    ("user_created", "User created"),
                ],
                db_index=True,
                max_length=100,
                unique=True,
                verbose_name="Type",
            ),
        ),
    ]