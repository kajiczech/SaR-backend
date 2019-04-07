from rest_framework import viewsets, serializers, permissions
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.apps import apps
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from backend.core.api.GenericViewSet import GenericViewSet
from backend.core.api.filters.ImplicitFilter import ImplicitFilter
from backend.core.api.filters.RequestFilter import RequestFilter
from backend.core.api.permissions.IsAssignedUser import IsAssignedUser
from backend.core.managers import BaseManager
from backend.core.models import BaseModel
from django.contrib.auth import get_user_model


class LinkViewSet(GenericViewSet):

    link: str = None
    parent_model: BaseModel = None
    parent: BaseModel = None
    
    def __init__(self, application, **kwargs):
        self.application = application
        super(GenericViewSet, self).__init__(**kwargs)

    def initialize_request(self, request, *args, **kwargs):
        application = self.application
        if self.kwargs['Model'] == 'user':
            self.parent_model = get_user_model()
        else:
            self.parent_model = apps.get_model(application, self.kwargs['Model'])
        self.link = self.kwargs['Link']
        self.queryset = self.parent_model.objects
        self.model = getattr(self.parent_model, self.link).field.model

        request = super(ModelViewSet, self).initialize_request(request, *args, **kwargs)
        return request


    def get_queryset(self):
        queryset = self.parent_model.objects
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return getattr(obj, self.link).all()

    def get_serializer_class(self):
        return self.model.get_serializer()

    def destroy(self, request, *args, **kwargs):
        self.queryset.remove(self.kwargs['ids'])





