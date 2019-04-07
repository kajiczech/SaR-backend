from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.contrib.auth.models import User

from backend.apps.sar.models import *
from backend.core.api.GenericViewSet import GenericViewSet
from rest_framework.test import APITestCase
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from oauth2_provider.models import get_application_model
from oauth2_provider.models import get_access_token_model
from decimal import *

from backend.core.api.LinkViewSet import LinkViewSet
from backend.tests.testGenericViewSet import BaseApiTest

Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()


class GetRetrieve(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = LinkViewSet.as_view({'get': 'list'}, application='sar')

    def getRequest(self, user, payload=""):
        factory = APIRequestFactory()
        request = factory.get(payload)
        force_authenticate(request, user=user, token=user.token)
        return request

    def test_basic_list(self):
        self.createdModels = {"operations": []}
        self.createdModels['operations'].append(
            Operation.objects.create(
                type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )
        self.createdModels['operations'].append(
            Operation.objects.create(
                type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )
        self.createdModels['operations'].append(
            Operation.objects.create(
                type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )

        response = self.view(self.getRequest(self.admin_user), id=str(self.admin_user.id), Model="user", Link="created_operations")

        assert response.data["count"] == 3
        for message in self.createdModels['operations']:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0

    def test_filter(self):
        self.createdModels = {"operations": []}
        self.createdModels['operations'].append(
            Operation.objects.create(
                type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )
        Operation.objects.create(
            type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
            created_by=self.regular_user
        )

        Operation.objects.create(
            type="bambi", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
            created_by=self.admin_user
        )
        response = self.view(self.getRequest(self.regular_user, '?filter={"type": "flood"}'), id=str(self.admin_user.id), Model="user", Link="created_operations")
        assert response.data["count"] == 1
        for message in self.createdModels['operations']:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0




class PostAdd(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.view = LinkViewSet.as_view({'post': 'add'}, application='sar')

    def getRequest(self, user, payload=None):
        factory = APIRequestFactory()
        request = factory.post("", payload, format="json")
        force_authenticate(request, user=user, token=user.token)
        return request


    def test_add(self):
        operation = Operation.objects.create(
            type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
        )

        payload = {
            "ids": [str(operation.id)],
        }
        request = self.getRequest(
            self.admin_user,
            payload
        )
        assert self.admin_user.created_operations.count() == 0
        response = self.view(request, id=str(self.admin_user.id), Model="user", Link="created_operations")
        assert response.status_code == 200
        assert self.admin_user.created_operations.count() == 1

    def test_bad_add(self):
        operation = Operation.objects.create(
            type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
        )

        payload = {
            "ids": [str(self.admin_user.id)],
        }
        request = self.getRequest(
            self.admin_user,
            payload
        )
        assert self.admin_user.created_operations.count() == 0
        response = self.view(request, id=str(self.admin_user.id), Model="user", Link="created_operations")
        assert response.status_code == 400
        assert self.admin_user.created_operations.count() == 0
        assert response.data['errors'][0] == str(self.admin_user.id)


class DeleteRemove(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = LinkViewSet.as_view({'delete': 'remove'}, application='sar')

    def getRequest(self, user, payload=None):
        factory = APIRequestFactory()
        request = factory.delete("", payload, format="json")
        force_authenticate(request, user=user, token=user.token)
        return request

    def test_delete(self):
        operation = Operation.objects.create(
            type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
            created_by=self.admin_user
        )
        assert self.admin_user.created_operations.count() == 1

        payload = {
            "ids": [str(operation.id)],
        }
        request = self.getRequest(
            self.admin_user,
            payload
        )
        response = self.view(request, id=str(self.admin_user.id), Model="user", Link="created_operations")
        assert response.status_code == 200
        assert self.admin_user.created_operations.count() == 0

    def test_bad_delete(self):
        operation = Operation.objects.create(
            type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z",
        )

        payload = {
            "ids": [str(self.admin_user.id)],
        }
        request = self.getRequest(
            self.admin_user,
            payload
        )
        assert self.admin_user.created_operations.count() == 0
        response = self.view(request, id=str(self.admin_user.id), Model="user", Link="created_operations")
        assert response.status_code == 400
        assert self.admin_user.created_operations.count() == 0
        assert response.data['errors'][0] == str(self.admin_user.id)
