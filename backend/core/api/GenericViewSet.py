from django.contrib.auth import get_user_model
from rest_framework import viewsets, serializers, permissions
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.apps import apps

from backend.core.api.filters.ImplicitFilter import ImplicitFilter
from backend.core.api.filters.RequestFilter import RequestFilter
from backend.core.api.permissions.IsAssignedUser import IsAssignedUser
from backend.core.models import BaseModel


class GenericViewSet(viewsets.ModelViewSet):
    
    filter_backends = [RequestFilter, ImplicitFilter]
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope, IsAssignedUser]
    
    application = None
    model: BaseModel = None
    lookup_field = 'id'
    
    def __init__(self, application, **kwargs):
        self.application = application
        super(GenericViewSet, self).__init__(**kwargs)

    def initialize_request(self, request, *args, **kwargs):
        if self.kwargs['Model'] == 'user':
            self.model = get_user_model()
        else:
            self.model = apps.get_model(self.application, self.kwargs['Model'])
        self.queryset = self.model.objects
        request = super().initialize_request(request, *args, **kwargs)
        return request

    def get_serializer_class(self):
        return self.model.get_serializer()

    def create(self, request, *args, **kwargs):
        """
        Dont allow non-admin users to create record for other users, set user to current user when not specified
        """
        try:
            request.data["user"]
        except KeyError:
            request.data["user"] = self.request.user.id

        if not self.request.user.is_staff:
            request.data["user"] = self.request.user.id

        return super().create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().update(request, partial=True, *args, **kwargs)



