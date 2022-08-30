# Generated by Django 2.2.13 on 2021-04-20 05:28

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0081_event_local'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordlabel',
            name='search_vector_en',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddField(
            model_name='keywordlabel',
            name='search_vector_fi',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddField(
            model_name='keywordlabel',
            name='search_vector_sv',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql=["UPDATE events_keywordlabel SET search_vector_fi = to_tsvector('finnish', name) WHERE language_id='fi';"  # noqa E501
                                       "UPDATE events_keywordlabel SET search_vector_en = to_tsvector('english', name) WHERE language_id='en';"  # noqa E501
                                       "UPDATE events_keywordlabel SET search_vector_sv = to_tsvector('swedish', name) WHERE language_id='sv';"  # noqa E501
                                       "CREATE TRIGGER fi_trigger BEFORE INSERT OR UPDATE ON events_keywordlabel FOR EACH ROW WHEN (NEW.language_id='fi') EXECUTE PROCEDURE tsvector_update_trigger(search_vector_fi, 'pg_catalog.finnish', name);"  # noqa E501
                                       "CREATE TRIGGER en_trigger BEFORE INSERT OR UPDATE ON events_keywordlabel FOR EACH ROW WHEN (NEW.language_id='en') EXECUTE PROCEDURE tsvector_update_trigger(search_vector_en, 'pg_catalog.english', name);"  # noqa E501
                                       "CREATE TRIGGER sv_trigger BEFORE INSERT OR UPDATE ON events_keywordlabel FOR EACH ROW WHEN (NEW.language_id='sv') EXECUTE PROCEDURE tsvector_update_trigger(search_vector_sv, 'pg_catalog.swedish', name);"  # noqa E501
                                       ],
                                  reverse_sql=["DROP TRIGGER fi_trigger ON events_keywordlabel;"
                                               "DROP TRIGGER en_trigger ON events_keywordlabel;"
                                               "DROP TRIGGER sv_trigger ON events_keywordlabel;"
                                  ]  # noqa E124
                )  # noqa E124
            ]

        )
    ]