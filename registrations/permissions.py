from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.request import Request

from events.auth import ApiKeyUser


class EventPublisherAdminPermission(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request: Request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        event = obj.event

        if not user.is_admin(obj.event.publisher):
            return False

        if isinstance(user, ApiKeyUser):
            # allow updating only if the api key matches event data source
            if event.data_source != user.data_source:
                return False
        else:
            # without api key, the event data_source has to be editable
            if not event.is_user_editable_resources():
                return False

        return True
