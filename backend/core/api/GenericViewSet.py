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

    def initialize_request(self, request, *args, **kwargs):
        if not self.model:
            self.model = self.get_model(kwargs['Model'])
        self.queryset = self.model.objects
        request = super().initialize_request(request, *args, **kwargs)
        return request

    @staticmethod
    def get_model(model_name_plural):
        found_model = None
        for model in apps.get_models():
            if not issubclass(model, BaseModel):
                continue
            """
            @var model BaseModel
            """
            plural_name_lowercase = model.api_controller.get_url_name()
            if plural_name_lowercase == model_name_plural.lower():
                found_model = model
                break

        if not found_model:
            raise LookupError(
                "Could not find model by its plural name " + model_name_plural)
        if not issubclass(found_model, BaseModel):
            raise LookupError(
                "Model is not instance of BaseModel")

        return found_model

    def get_serializer_class(self):
        return self.model.api_controller.get_serializer(view=self)

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



