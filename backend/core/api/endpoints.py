from django.contrib.auth import get_user_model
from rest_framework import viewsets, serializers, permissions, status
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.apps import apps
from rest_framework.response import Response

from backend.core.api.GenericViewSet import GenericViewSet
from backend.core.api.filters.ImplicitFilter import ImplicitFilter
from backend.core.api.filters.RequestFilter import RequestFilter
from backend.core.api.permissions.IsAssignedUser import IsAssignedUser
from backend.core.models import BaseModel, User


class MeView(GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    model = get_user_model()

    def me(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class RegisterUserView(GenericViewSet):
    permission_classes = []
    model = get_user_model()

    def register_user(self, request, *args, **kwargs):
        # @var BaseSerializer
        return super().create(request, *args, **kwargs)
