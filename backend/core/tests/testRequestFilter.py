from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
import json

from rest_framework.request import Request

from backend.core.api.filters.RequestFilter import RequestFilter
from backend.core.tests.models import TestModel


class RequestFilterTest(TestCase):

    def setUp(self):
        self.filter_models = {}
        TestModel.objects.create(type="flood", name="1", start_date="2019-04-06T14:43:56.630468Z")
        TestModel.objects.create(type="flood", name="2", start_date="2019-04-06T14:43:56.630468Z")
        TestModel.objects.create(type="earthquake", name="3", start_date="2019-04-06T14:43:56.630468Z")
        TestModel.objects.create(type="flood", name="4", start_date="2019-04-06T14:50:56.630468Z",
                                 end_date="2019-04-06T14:50:56.630468Z")

        super().setUp()

        self.regular_user = get_user_model().objects.create(
            username="regular",
            is_staff=False
        )

    @staticmethod
    def do_filter(queryset, filter):
        request = Request(HttpRequest())
        filter_json = json.dumps(filter)

        request.query_params.appendlist('filter', filter_json)
        test_instance = RequestFilter()
        return test_instance.filter_queryset(request, queryset, None)

    def test_basic_filter(self):
        queryset = TestModel.objects.all()
        filter_def = {'type': "flood"}
        filtered_queryset = self.do_filter(queryset, filter_def)
        assert filtered_queryset.count() == 3

        assert filtered_queryset.get(name='1')
        assert filtered_queryset.get(name='2')
        assert filtered_queryset.get(name='4')

    def test_or_filter(self):
        queryset = TestModel.objects.all()
        filter_def = {"$or": {'type': "earthquake", 'name': "1"}}

        filtered_queryset = self.do_filter(queryset, filter_def)
        assert filtered_queryset.count() == 2

        assert filtered_queryset.get(name='1')
        assert filtered_queryset.get(name='3')

        filter_def = {'type': "flood", '$or': {"name": "1", "start_date": "2019-04-06T14:50:56.630468Z"}}
        filtered_queryset = self.do_filter(queryset, filter_def)
        assert filtered_queryset.count() == 2

        assert filtered_queryset.get(name='1')
        assert filtered_queryset.get(name='4')

    def test_and_filter(self):
        queryset = TestModel.objects.all()
        filter_def = {"$and": {'type': "earthquake", 'name': "1"}}

        filtered_queryset = self.do_filter(queryset, filter_def)
        assert filtered_queryset.count() == 0

        filter_def = {
            "type": "flood",
            "$or": {
                    "name__startswith": "1",
                    "$and": {
                            "start_date__gte": "2019-04-06T14:50:56.630468Z",
                            "end_date__lte": "2019-04-07T14:50:56.630468Z",

                    }
            },
        }

        filtered_queryset = self.do_filter(queryset, filter_def)
        assert filtered_queryset.count() == 2
        assert filtered_queryset.get(name='1')
        assert filtered_queryset.get(name='4')
