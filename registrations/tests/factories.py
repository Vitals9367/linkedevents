import factory

from events.models import DataSource, Event
from registrations.models import Registration


class DataSourceFactory(factory.django.DjangoModelFactory):
    id = factory.Sequence(lambda n: "data-source-{0}".format(n))

    class Meta:
        model = DataSource


class OrganizationFactory(factory.django.DjangoModelFactory):
    data_source = factory.SubFactory(DataSourceFactory)

    class Meta:
        model = "django_orghierarchy.Organization"


class EventFactory(factory.django.DjangoModelFactory):
    data_source = factory.SubFactory(DataSourceFactory)
    publisher = factory.SubFactory(OrganizationFactory)

    class Meta:
        model = Event


class RegistrationFactory(factory.django.DjangoModelFactory):
    event = factory.SubFactory(EventFactory)

    class Meta:
        model = Registration
