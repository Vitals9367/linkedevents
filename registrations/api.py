from datetime import datetime, timedelta
from uuid import UUID

import pytz
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.db import models
from django.db.models import Q, Sum
from django.utils.translation import ugettext as _
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from events.api import (
    _filter_event_queryset,
    JSONAPIViewMixin,
    RegistrationSerializer,
    UserDataSourceAndOrganizationMixin,
)
from events.models import Event
from events.permissions import (
    DataSourceResourceEditPermission,
    GuestDelete,
    GuestGet,
    GuestPost,
)
from linkedevents.registry import register_view
from registrations.models import Registration, SeatReservationCode, SignUp
from registrations.serializers import SeatReservationCodeSerializer, SignUpSerializer
from registrations.utils import code_validity_duration


class SignUpViewSet(
    JSONAPIViewMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SignUpSerializer
    queryset = SignUp.objects.all()
    permission_classes = [GuestPost | GuestDelete | GuestGet]

    def get_signup_by_code(self, code):
        try:
            UUID(code)
        except ValueError:
            raise DRFPermissionDenied("Malformed UUID.")
        qs = SignUp.objects.filter(cancellation_code=code)
        if qs.count() == 0:
            raise DRFPermissionDenied(
                "Cancellation code did not match any registration"
            )
        return qs[0]

    def delete(self, request, *args, **kwargs):
        code = request.data.get("cancellation_code", "no code")
        if code == "no code":
            raise DRFPermissionDenied("cancellation_code parameter has to be provided")
        signup = self.get_signup_by_code(code)
        waitlisted = SignUp.objects.filter(
            registration=signup.registration,
            attendee_status=SignUp.AttendeeStatus.WAITING_LIST,
        ).order_by("id")
        signup.send_notification("cancellation")
        signup.delete()
        if len(waitlisted) > 0:
            first_on_list = waitlisted[0]
            first_on_list.attendee_status = SignUp.AttendeeStatus.ATTENDING
            first_on_list.save()
        return Response("SignUp deleted.", status=status.HTTP_200_OK)


register_view(SignUpViewSet, "signup")


class SignUpEditViewSet(
    JSONAPIViewMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SignUpSerializer
    queryset = SignUp.objects.all()
    permission_classes = (IsAuthenticated,)


register_view(SignUpEditViewSet, "signup_edit")


class RegistrationViewSet(
    UserDataSourceAndOrganizationMixin,
    JSONAPIViewMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RegistrationSerializer
    queryset = Registration.objects.all()

    permission_classes = [
        DataSourceResourceEditPermission,
    ]

    def perform_create(self, serializer):
        # Check object level permissions for event which has the relevant data_source.
        event = serializer.validated_data.get("event")
        self.check_object_permissions(self.request, event)
        super().perform_create(serializer)

    def perform_update(self, serializer):
        # Check object level permissions for event which has the relevant data_source.
        event = serializer.validated_data.get("event", serializer.instance.event)
        self.check_object_permissions(self.request, event)
        super().perform_update(serializer)

    def filter_queryset(self, queryset):
        events = Event.objects.exclude(registration=None)

        # Copy query_params to get mutable version of it
        query_params = self.request.query_params.copy()
        # By default _filter_event_queryset only returns events with GENERAL type.
        # This causes problem when getting a registration details, so filter registrations
        # by event_type only when explicitly set
        if not query_params.get("event_type"):
            event_types = {k[1].lower(): k[0] for k in Event.TYPE_IDS}
            query_params["event_type"] = ",".join(event_types.keys())

        events = _filter_event_queryset(events, query_params)

        val = self.request.query_params.get("admin_user", None)
        if val and str(val).lower() == "true":
            if isinstance(self.request.user, AnonymousUser):
                events = Event.objects.none()
            else:
                events = self.request.user.get_editable_events(events)
        registrations = Registration.objects.filter(event__in=events)

        return registrations

    @action(methods=["post"], detail=True, permission_classes=[GuestPost])
    def reserve_seats(self, request, pk=None, version=None):
        def none_to_unlim(val):
            # Null value in the waiting_list_capacity or maximum_attendee_capacity
            # signifies that the amount of seats is unlimited
            if val is None:
                return 10000
            else:
                return val

        try:
            registration = Registration.objects.get(id=pk)
        except Registration.DoesNotExist:
            raise NotFound(detail=f"Registration {pk} doesn't exist.", code=404)
        waitlist = request.data.get("waitlist", False)
        if waitlist:
            waitlist_seats = none_to_unlim(registration.waiting_list_capacity)
        else:
            waitlist_seats = 0  # if waitlist is False, waiting list is not to be used

        maximum_attendee_capacity = none_to_unlim(
            registration.maximum_attendee_capacity
        )

        seats_capacity = maximum_attendee_capacity + waitlist_seats
        seats_reserved = registration.reservations.filter(
            timestamp__gte=datetime.now()
            - timedelta(minutes=settings.SEAT_RESERVATION_DURATION)
        ).aggregate(seats_sum=(Sum("seats", output_field=models.FloatField())))[
            "seats_sum"
        ]
        if seats_reserved is None:
            seats_reserved = 0
        seats_taken = registration.signups.count()
        seats_available = seats_capacity - (seats_reserved + seats_taken)

        if request.data.get("seats", 0) > seats_available:
            return Response(
                status=status.HTTP_409_CONFLICT, data="Not enough seats available."
            )
        else:
            code = SeatReservationCode()
            code.registration = registration
            code.seats = request.data.get("seats")
            free_seats = maximum_attendee_capacity - registration.signups.count()
            code.save()
            data = SeatReservationCodeSerializer(code).data
            data["seats_at_event"] = (
                min(free_seats, code.seats) if free_seats > 0 else 0
            )
            waitlist_spots = code.seats - data["seats_at_event"]
            data["waitlist_spots"] = waitlist_spots if waitlist_spots else 0

            return Response(data, status=status.HTTP_201_CREATED)

    def get_signup_by_code(self, code, registration):
        try:
            UUID(code)
        except ValueError:
            raise DRFPermissionDenied("Malformed UUID.")
        try:
            signup = SignUp.objects.get(
                cancellation_code=code, registration=registration
            )
        except SignUp.DoesNotExist:
            raise DRFPermissionDenied("Cancellation code did not match any signup")
        return signup
    
    def check_signup_permissions(self, request):
        registration = self.get_object()

        # GET is one of the SAFE_METHODS. 
        # Override method to force check_object_permissions and check_permissions to check permissions
        request.method = "POST"
        self.check_permissions(request)

        try:
            self.check_object_permissions(request, registration.event)
        except:
            raise DRFPermissionDenied()

    @action(methods=["post"], detail=True, permission_classes=[GuestPost])
    def signup(self, request, pk=None, *args, **kwargs):
        attending = []
        waitlisted = []
        if "reservation_code" not in request.data.keys():
            raise serializers.ValidationError(
                {"registration": "Reservation code is missing"}
            )

        try:
            reservation = SeatReservationCode.objects.get(
                code=request.data["reservation_code"]
            )
        except SeatReservationCode.DoesNotExist:
            msg = f"Reservation code {request.data['reservation_code']} doesn't exist."
            raise NotFound(detail=msg, code=404)

        if str(reservation.registration.id) != pk:
            msg = f"Registration code {request.data['reservation_code']} doesn't match the registration {pk}"
            raise serializers.ValidationError({"reservation_code": msg})

        if len(request.data["signups"]) > reservation.seats:
            raise serializers.ValidationError(
                {"signups": "Number of signups exceeds the number of requested seats"}
            )

        expiration = reservation.timestamp + timedelta(
            minutes=code_validity_duration(reservation.seats)
        )
        if datetime.now().astimezone(pytz.utc) > expiration:
            raise serializers.ValidationError({"code": "Reservation code has expired."})

        for i in request.data["signups"]:
            i["registration"] = pk

        # First check that all the signups are valid and then actually create them
        for i in request.data["signups"]:
            serializer = SignUpSerializer(data=i)
            if not serializer.is_valid():
                raise serializers.ValidationError(serializer.errors)

        for i in request.data["signups"]:
            signup = SignUpSerializer(data=i, many=False)
            signup.is_valid()
            signee = signup.create(validated_data=signup.validated_data)
            if signee.attendee_status == SignUp.AttendeeStatus.ATTENDING:
                attending.append({"id": signee.id, "name": signee.name})
            else:
                waitlisted.append({"id": signee.id, "name": signee.name})
        reservation.delete()
        data = {
            "attending": {"count": len(attending), "people": attending},
            "waitlisted": {"count": len(waitlisted), "people": waitlisted},
        }

        return Response(data, status=status.HTTP_201_CREATED)

    # Endpoint to get a single signup
    @action(
        methods=["get"],
        url_path=r"signup/(?P<signup_pk>\w+)",
        detail=True,
        permission_classes=[DataSourceResourceEditPermission],
    )
    def signup(self, request, signup_pk=None, *args, **kwargs):
        user = request.user
        registration = self.get_object()

        # Non admin users can get signup by cancellation_code
        if isinstance(user, AnonymousUser) or not registration.can_be_edited_by(user):
            code = request.GET.get("cancellation_code", None)
            if not code:
                raise DRFPermissionDenied(
                    _("cancellation_code parameter has to be provided")
                )
            signup = self.get_signup_by_code(code, registration)
        else:
            # Admin users can get signup without cancellation_code
            self.check_signup_permissions(request)
            try:
                signup = SignUp.objects.get(
                    pk=signup_pk, registration=registration
                )
            except SignUp.DoesNotExist:
                raise NotFound()
            
        return Response(SignUpSerializer(signup).data)

    # Endpoint to get signup list
    @action(
        methods=["get"],
        url_path=r"signup",
        detail=True,
        permission_classes=[DataSourceResourceEditPermission],
    )
    def signups(self, request, *args, **kwargs):
        # Only admin users are allowed to get list of signups
        self.check_signup_permissions(request)

        registration = self.get_object()
        signups = registration.signups.all()

        val = request.query_params.get("text", None)
        if val:
            signups = signups.filter(
                Q(name__icontains=val)
                | Q(email__icontains=val)
                | Q(extra_info__icontains=val)
                | Q(membership_number__icontains=val)
                | Q(phone_number__icontains=val)
            )

        val = request.query_params.get("attendee_status", None)
        if val:
            if val in ["waitlisted", "attending"]:
                signups = signups.filter(attendee_status=val)
            else:
                raise DRFPermissionDenied(
                    f"attendee_status can take values waitlisted and attending, not {val}"
                )
        return Response(SignUpSerializer(signups, many=True).data)


register_view(RegistrationViewSet, "registration")
