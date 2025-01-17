from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("Request conflict with the current state of the target resource")
    default_code = "conflict"
