from backend.core.tests.models import *
from django.contrib.auth import get_user_model
from oauth2_provider.models import get_application_model
from oauth2_provider.models import get_access_token_model

from backend.core.api.LinkViewSet import LinkViewSet
from backend.core.tests.testGenericViewSet import BaseApiTest

Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()


class GetRetrieve(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = LinkViewSet.as_view({'get': 'list'})

    def test_basic_list(self):
        self.createdModels = {"models": []}
        self.createdModels["models"].append(
            TestModel.objects.create(
                type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )
        self.createdModels["models"].append(
            TestModel.objects.create(
                type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )
        self.createdModels["models"].append(
            TestModel.objects.create(
                type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )

        response = self.view(self.get_request('get', self.admin_user), id=str(self.admin_user.id), Model="users", Link="created_test_models")

        assert response.data["count"] == 3
        for message in self.createdModels["models"]:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0

        response = self.view(self.get_request('get', self.admin_user), id=str(self.createdModels['models'][0].id), Model="TestModels", Link="attendees")
        assert response.status_code == 200


    def test_filter(self):
        self.createdModels = {"models": []}
        self.createdModels["models"].append(
            TestModel.objects.create(
                type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
                created_by=self.admin_user
            )
        )
        TestModel.objects.create(
            type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
            created_by=self.regular_user
        )

        TestModel.objects.create(
            type="bambi", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
            created_by=self.admin_user
        )
        response = self.view(self.get_request('get', user=self.regular_user, query_parameters='?filter={"type": "flood"}'), id=str(self.admin_user.id), Model="users", Link="created_test_models")
        assert response.data["count"] == 1
        for message in self.createdModels["models"]:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0




class PostAdd(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.view = LinkViewSet.as_view({'post': 'add'})

    def test_add(self):
        operation = TestModel.objects.create(
            type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
        )

        payload = {
            "ids": [str(operation.id)],
        }
        request = self.get_request(
            'post',
            user=self.admin_user,
            payload=payload
        )
        assert self.admin_user.created_test_models.count() == 0
        response = self.view(request, id=str(self.admin_user.id), Model="users", Link="created_test_models")
        assert response.status_code == 200
        assert self.admin_user.created_test_models.count() == 1

    def test_bad_add(self):
        operation = TestModel.objects.create(
            type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
        )

        payload = {
            "ids": [str(self.admin_user.id)],
        }
        request = self.get_request(
            'post',
            user=self.admin_user,
            payload=payload
        )
        assert self.admin_user.created_test_models.count() == 0
        response = self.view(request, id=str(self.admin_user.id), Model="users", Link="created_test_models")
        assert response.status_code == 400
        assert self.admin_user.created_test_models.count() == 0
        assert response.data['errors'][str(self.admin_user.id)]


class DeleteRemove(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = LinkViewSet.as_view({'delete': 'remove'})

    def test_delete(self):
        operation = TestModel.objects.create(
            type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
            created_by=self.admin_user
        )
        assert self.admin_user.created_test_models.count() == 1

        payload = {
            "ids": [str(operation.id)],
        }
        request = self.get_request(
            'delete',
            user=self.admin_user,
            payload=payload
        )
        response = self.view(request, id=str(self.admin_user.id), Model="users", Link="created_test_models")
        assert response.status_code == 200
        assert self.admin_user.created_test_models.count() == 0

    def test_bad_delete(self):
        operation = TestModel.objects.create(
            type="flood", name="FirstTestModel", start_date="2019-04-06T14:43:56.630468Z",
        )

        payload = {
            "ids": [str(self.admin_user.id)],
        }
        request = self.get_request(
            'delete',
            user=self.admin_user,
            payload=payload
        )
        assert self.admin_user.created_test_models.count() == 0
        response = self.view(request, id=str(self.admin_user.id), Model="users", Link="created_test_models")
        assert response.status_code == 400
        assert self.admin_user.created_test_models.count() == 0
        assert response.data['errors'][str(self.admin_user.id)]

