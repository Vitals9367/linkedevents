# Generated by Django 2.2.13 on 2021-11-25 13:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("registrations", "0004_auto_20211125_1551"),
    ]

    operations = [
        migrations.AlterField(
            model_name="signup",
            name="cancellation_code",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, verbose_name="Cancellation code"
            ),
        ),
        migrations.AlterField(
            model_name="signup",
            name="city",
            field=models.CharField(
                blank=True, default="", max_length=50, verbose_name="City"
            ),
        ),
        migrations.AlterField(
            model_name="signup",
            name="email",
            field=models.EmailField(
                blank=True,
                default=None,
                max_length=254,
                null=True,
                verbose_name="E-mail",
            ),
        ),
        migrations.AlterField(
            model_name="signup",
            name="extra_info",
            field=models.TextField(blank=True, default="", verbose_name="Extra info"),
        ),
        migrations.AlterField(
            model_name="signup",
            name="membership_number",
            field=models.CharField(
                blank=True, default="", max_length=50, verbose_name="Membership number"
            ),
        ),
        migrations.AlterField(
            model_name="signup",
            name="name",
            field=models.CharField(max_length=50, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="signup",
            name="phone_number",
            field=models.CharField(
                blank=True,
                default=None,
                max_length=18,
                null=True,
                verbose_name="Phone number",
            ),
        ),
    ]
