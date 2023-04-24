import urllib.parse
from datetime import date, timedelta

import pytz
from django.contrib.auth.models import AnonymousUser
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from rest_framework import relations, serializers
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.fields import DateTimeField

from events.api import EventSerializer
from events.api import JSONLDRelatedField as BaseJSONLDRelatedField
from events.api import LinkedEventsSerializer
from events.auth import ApiKeyUser
from events.models import Event
from registrations.models import Registration, SeatReservationCode, SignUp
from registrations.utils import code_validity_duration


class SignUpSerializer(serializers.ModelSerializer):
    view_name = "signup"

    def create(self, validated_data):
        registration = validated_data["registration"]
        already_attending = SignUp.objects.filter(
            registration=registration, attendee_status=SignUp.AttendeeStatus.ATTENDING
        ).count()
        already_waitlisted = SignUp.objects.filter(
            registration=registration,
            attendee_status=SignUp.AttendeeStatus.WAITING_LIST,
        ).count()
        attendee_capacity = registration.maximum_attendee_capacity
        waiting_list_capacity = registration.waiting_list_capacity
        if registration.audience_min_age or registration.audience_max_age:
            if "date_of_birth" not in validated_data.keys():
                raise DRFPermissionDenied("Date of birth has to be specified.")
            dob = validated_data["date_of_birth"]
            today = date.today()
            current_age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.year))
            )
            if (
                registration.audience_min_age
                and current_age < registration.audience_min_age
            ):
                raise DRFPermissionDenied("The participant is too young.")
            if (
                registration.audience_max_age
                and current_age > registration.audience_max_age
            ):
                raise DRFPermissionDenied("The participant is too old.")
        if (attendee_capacity is None) or (already_attending < attendee_capacity):
            signup = super().create(validated_data)
            signup.send_notification("confirmation")
            return signup
        elif (waiting_list_capacity is None) or (
            already_waitlisted < waiting_list_capacity
        ):
            signup = super().create(validated_data)
            signup.attendee_status = SignUp.AttendeeStatus.WAITING_LIST
            signup.save()
            return signup
        else:
            raise DRFPermissionDenied("The waiting list is already full")

    class Meta:
        fields = "__all__"
        model = SignUp


class JSONLDRelatedField(BaseJSONLDRelatedField):
    def get_queryset(self):
        return relations.HyperlinkedRelatedField.get_queryset(self)


class RegistrationSerializer(LinkedEventsSerializer):
    view_name = "registration-detail"

    signups = serializers.SerializerMethodField()

    current_attendee_count = serializers.SerializerMethodField()

    current_waiting_list_count = serializers.SerializerMethodField()

    data_source = serializers.SerializerMethodField()

    publisher = serializers.SerializerMethodField()

    event = JSONLDRelatedField(
        serializer=EventSerializer,
        many=False,
        view_name="event-detail",
        queryset=Event.objects.all(),
    )

    created_time = DateTimeField(
        default_timezone=pytz.UTC, required=False, allow_null=True
    )

    last_modified_time = DateTimeField(
        default_timezone=pytz.UTC, required=False, allow_null=True
    )

    created_by = serializers.StringRelatedField(required=False, allow_null=True)

    last_modified_by = serializers.StringRelatedField(required=False, allow_null=True)

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance=instance, *args, **kwargs)

        event_dict = kwargs["context"]["request"].data.get("event", None)

        # Check user permissions if creating a new registration.
        # LinkedEventsSerializer __init__ checks permissions in case of new registration
        if not instance and isinstance(event_dict, dict) and "@id" in event_dict:
            event_url = event_dict["@id"]
            event_id = urllib.parse.unquote(event_url.rstrip("/").split("/")[-1])
            user = kwargs["context"]["user"]

            try:
                event = Event.objects.get(pk=event_id)
                error_message = _(f"User {user} cannot modify event {event}")

                if not user.is_admin(event.publisher):
                    raise DRFPermissionDenied(error_message)

                if isinstance(user, ApiKeyUser):
                    # allow updating only if the api key matches instance data source
                    if event.data_source != user.data_source:
                        raise DRFPermissionDenied(_(error_message))
                else:
                    # allow updating only if event data_source has user_editable_resources set to True
                    if not event.is_user_editable_resources():
                        raise DRFPermissionDenied(_(error_message))
            except Event.DoesNotExist:
                pass

    def create(self, request, *args, **kwargs):
        try:
            instance = super().create(request, *args, **kwargs)
        except IntegrityError as error:
            if "duplicate key value violates unique constraint" in str(error):
                raise serializers.ValidationError(
                    {"event": _("Event already has a registration.")}
                )
            else:
                raise error
        return instance

    def get_signups(self, obj):
        params = self.context["request"].query_params
        if params.get("include", None) == "signups":
            #  only the organization admins should be able to access the signup information
            user = self.context["user"]
            event = obj.event
            if not isinstance(user, AnonymousUser) and user.is_admin(event.publisher):
                queryset = SignUp.objects.filter(registration__id=obj.id)
                return SignUpSerializer(queryset, many=True, read_only=True).data
            else:
                return _(
                    "Only the admins of the organization that published the event {event_id} have access rights."
                ).format(event_id=event.id)
        else:
            return None

    def get_current_attendee_count(self, obj):
        return obj.signups.filter(attendee_status=SignUp.AttendeeStatus.ATTENDING).count()

    def get_current_waiting_list_count(self, obj):
        return obj.signups.filter(attendee_status=SignUp.AttendeeStatus.WAITING_LIST).count()

    def get_data_source(self, obj):
        return obj.data_source.id
    def get_publisher(self, obj):
        return obj.publisher.id

    # LinkedEventsSerializer validates name which doesn't exist in Registration model
    def validate(self, data):
        return data

    class Meta:
        fields = "__all__"
        model = Registration


class SeatReservationCodeSerializer(serializers.ModelSerializer):
    timestamp = DateTimeField(default_timezone=pytz.UTC, required=False)
    expiration = serializers.SerializerMethodField()

    class Meta:
        fields = ("seats", "code", "timestamp", "registration", "expiration")
        model = SeatReservationCode

    def get_expiration(self, obj):
        return obj.timestamp + timedelta(minutes=code_validity_duration(obj.seats))
