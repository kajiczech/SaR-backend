from django.db.models.query import QuerySet
from rest_framework import filters


class ImplicitFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_def = view.model.get_implicit_filter(request.user)
        return queryset.filter(**filter_def)
