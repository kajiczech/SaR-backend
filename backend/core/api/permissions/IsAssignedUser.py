from rest_framework import permissions

from backend.core.models import BaseModel


class IsAssignedUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: BaseModel):
        try:
            obj.user
        except AttributeError:
            pass
        else:
            if not request.user.is_staff:
                if obj.user is not request.user:
                    return False
        return True
