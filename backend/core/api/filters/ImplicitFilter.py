from django.db.models.query import QuerySet
from rest_framework import filters

from backend.core.api import GenericViewSet


class ImplicitFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view: GenericViewSet):
        filter_def = view.model.api_controller.get_implicit_filter(request.user)
        return queryset.filter(**filter_def)
