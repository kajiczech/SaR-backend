import json

from django.db.models import Q
from rest_framework import filters


class RequestFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_json = request.query_params.get('filter')
        if not filter_json:
            return queryset
        filter_def = json.loads(filter_json)
        query = self.get_query(filter_def)
        return queryset.filter(query)

    def get_query(self, filter_def, and_operand=True):
        """
        :param filter_def: Dictionary
        :param and_operand: Bool whether the operand in query is `and` or `or` . Could not figure out better name
        :return:
        """
        query = Q()
        for key, value in filter_def.items():

            if key.lower() == '$or':
                child_query = self.get_query(value, False)
            elif key.lower() == '$and':
                child_query = self.get_query(value, True)
            else:
                child_query = Q(**{key: value})

            if and_operand:
                query &= child_query
            else:
                query |= child_query

        return query




