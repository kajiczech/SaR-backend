from django.core.exceptions import ValidationError
from django.db.models import ManyToManyField, ForeignKey
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.core.api.GenericViewSet import GenericViewSet
from backend.core.models import BaseModel


class LinkViewSet(GenericViewSet):
    link: str = None
    parent_model: BaseModel = None
    parent: BaseModel = None

    def initialize_request(self, request, *args, **kwargs):
        self.parent_model = self.get_model(kwargs['Model'])
        self.link = self.kwargs['Link']
        self.queryset = self.parent_model.objects
        if isinstance(getattr(self.parent_model, self.link).field, ForeignKey):
            self.model = getattr(self.parent_model, self.link).field.model
        else:
            self.model = getattr(self.parent_model, self.link).field.related_model
        request = super(ModelViewSet, self).initialize_request(request, *args, **kwargs)

        return request

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



