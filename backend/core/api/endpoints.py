

from rest_framework import viewsets, serializers, permissions, status
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.apps import apps
from rest_framework.response import Response

from backend.core.api.filters.ImplicitFilter import ImplicitFilter
from backend.core.api.filters.RequestFilter import RequestFilter
from backend.core.api.permissions.IsAssignedUser import IsAssignedUser
from backend.core.models import BaseModel, User


class MeView(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]

    def me(self, request, *args, **kwargs):
        # @var BaseSerializer
        serializer = request.user.api_controller.get_serializer()(instance=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
