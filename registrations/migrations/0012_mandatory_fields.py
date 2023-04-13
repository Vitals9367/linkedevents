# Generated by Django 3.2.18 on 2023-04-05 12:12

from django.db import migrations, models

from registrations.models import MandatoryField


def create_initial_mandatory_fields(apps, schema_editor):
    MandatoryField.objects.create(
        id=MandatoryField.DefaultMandatoryField.NAME,
        name_fi="Nimi",
        name_en="Name",
        name_sv="Namn",
        type=MandatoryField.MandatoryFieldType.PERSON,
    )

    MandatoryField.objects.create(
        id=MandatoryField.DefaultMandatoryField.CITY,
        name_fi="Kaupunki",
        name_en="City",
        name_sv="Stad",
        type=MandatoryField.MandatoryFieldType.PERSON,
    )

    MandatoryField.objects.create(
        id=MandatoryField.DefaultMandatoryField.ADDRESS,
        name_fi="Osoite",
        name_en="Address",
        name_sv="Adress",
        type=MandatoryField.MandatoryFieldType.PERSON,
    )

    MandatoryField.objects.create(
        id=MandatoryField.DefaultMandatoryField.PHONE_NUMBER,
        name_fi="Puhelinnumero",
        name_en="Phone number",
        name_sv="Telefonnummer",
        type=MandatoryField.MandatoryFieldType.CONTACT,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("registrations", "0011_seatreservationcode"),
    ]

    operations = [
        migrations.CreateModel(
            name="MandatoryField",
            fields=[
                (
                    "id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "name_fi",
                    models.CharField(max_length=255, null=True, verbose_name="Name"),
                ),
                (
                    "name_sv",
                    models.CharField(max_length=255, null=True, verbose_name="Name"),
                ),
                (
                    "name_en",
                    models.CharField(max_length=255, null=True, verbose_name="Name"),
                ),
                (
                    "name_zh_hans",
                    models.CharField(max_length=255, null=True, verbose_name="Name"),
                ),
                (
                    "name_ru",
                    models.CharField(max_length=255, null=True, verbose_name="Name"),
                ),
                (
                    "name_ar",
                    models.CharField(max_length=255, null=True, verbose_name="Name"),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("contact", "Contact details"),
                            ("person", "Registrant's basic information"),
                        ],
                        default="contact",
                        max_length=25,
                        verbose_name="Type",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="registration",
            name="mandatory_fields",
            field=models.ManyToManyField(
                blank=True,
                to="registrations.MandatoryField",
                verbose_name="Mandatory fields",
            ),
        ),
        migrations.RunPython(
            code=create_initial_mandatory_fields,
            reverse_code=migrations.operations.special.RunPython.noop,
        ),
    ]