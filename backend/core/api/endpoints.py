from base64 import b64encode
from django.core.exceptions import ValidationError
from django.db.models import ManyToManyField, ForeignKey
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet
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


class GenericEndpoint(viewsets.ModelViewSet):
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


class LinkEndpoint(GenericEndpoint):
    link: str = None
    parent_model: BaseModel = None
    parent: BaseModel = None

    def initialize_request(self, request, *args, **kwargs):
        self.parent_model = self.get_model(kwargs['Model'])
        self.link = self.kwargs['Link']
        self.queryset = self.parent_model.objects
        self.model = self.get_related_model(self.parent_model, self.link)
        request = super(ModelViewSet, self).initialize_request(request, *args, **kwargs)

        return request

    @staticmethod
    def get_related_model(parent_model, link):
        link_field = getattr(parent_model, link).field
        if isinstance(link_field, ForeignKey) or isinstance(link_field, ManyToManyField):
            return link_field.model
        else:
            return link_field.related_model

    def load_parent_object(self):
        if self.parent:
            return
        queryset = self.parent_model.objects
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        self.parent = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, self.parent)

    def get_queryset(self):
        return self.get_parent_set().all()

    def get_serializer_class(self):

        return self.model.api_controller.get_serializer(view=self)

    def remove(self, request, *args, **kwargs):
        errors = {}
        for id in request.data['ids']:
            try:
                self.get_parent_set().remove(self.model.objects.get(id=id))
            except (self.model.DoesNotExist, ValidationError, self.parent_model.DoesNotExist) as e:
                errors[id] = e
        if errors.__len__():
            data = {'errors': errors}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    def get_parent_set(self):
        self.load_parent_object()
        return getattr(self.parent, self.link)

    def add(self, request, *args, **kwargs):
        errors = {}
        for id in request.data['ids']:
            try:
                self.get_parent_set().add(self.model.objects.get(id=id))
            except (self.model.DoesNotExist, ValidationError, self.parent_model.DoesNotExist) as e:
                errors[id] = e
        if errors.__len__():
            data = {'errors': errors}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class MeEndpoint(GenericEndpoint):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    model = get_user_model()

    def me(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class RegisterUserEndpoint(GenericEndpoint):
    permission_classes = []
    model = get_user_model()

    def register_user(self, request, *args, **kwargs):
        # @var BaseSerializer
        return super().create(request, *args, **kwargs)
