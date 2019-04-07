import json

from rest_framework import filters


class RequestFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_json = request.query_params.get('filter')
        if not filter_json:
            return queryset
        filter_def = json.loads(filter_json)
        return queryset.filter(**filter_def)
