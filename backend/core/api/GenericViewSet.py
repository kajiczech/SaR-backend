from base64 import b64encode

from django.contrib.auth import get_user_model
from rest_framework import viewsets, serializers, permissions
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from django.apps import apps
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from django.utils.six.moves.urllib import parse as urlparse

from backend.core.api.filters.ImplicitFilter import ImplicitFilter
from backend.core.api.filters.RequestFilter import RequestFilter
from backend.core.api.permissions.IsAssignedUser import IsAssignedUser
from backend.core.models import BaseModel


class GenericPagination(CursorPagination):
    page_size = 20
    ordering = '-date_modified'
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': len(self.page),
            'results': data
        })

    def encode_cursor(self, cursor):
        """
        Returning only encoded cursor instead of whole url
        """
        tokens = {}
        if cursor.offset != 0:
            tokens['o'] = str(cursor.offset)
        if cursor.reverse:
            tokens['r'] = '1'
        if cursor.position is not None:
            tokens['p'] = cursor.position

        querystring = urlparse.urlencode(tokens, doseq=True)
        encoded = b64encode(querystring.encode('ascii')).decode('ascii')
        return encoded


class GenericViewSet(viewsets.ModelViewSet):
    
    filter_backends = [RequestFilter, ImplicitFilter]
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope, IsAssignedUser]
    application = None
    model: BaseModel = None
    lookup_field = 'id'

    pagination_class = GenericPagination


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

    def list(self, request, *args, **kwargs):

        try:
            ordering_fields = [request.query_params['order_by'], GenericPagination.ordering]

            class Pagination(GenericPagination):
                ordering = ordering_fields

            # The only way, how to change paginator class in the view
            self._paginator = Pagination()
        except KeyError:
            pass

        return super().list(request, *args, **kwargs)



