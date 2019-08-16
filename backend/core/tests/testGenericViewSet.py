import logging

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.contrib.auth.models import User

from backend.core.tests.models import *
# from backend.apps.sar.models import *

from backend.core.api.GenericViewSet import GenericViewSet
from rest_framework.test import APITestCase
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
from oauth2_provider.models import get_application_model
from oauth2_provider.models import get_access_token_model
from decimal import *


Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()


# TODO: Create some test models, don't use ones from a different application
# https://stackoverflow.com/questions/502916/django-how-to-create-a-model-dynamically-just-for-testing

class BaseApiTest(APITestCase):

    def create_application(self):
        self.app = Application.objects.create(
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
            redirect_uris='https://none',
            name='web',
            client_id="web",
            user=self.admin_user
        )

    def create_token(self, user):
        access_token = AccessToken.objects.create(
            user=user,
            scope='read write',
            expires=timezone.now() + timedelta(seconds=300),
            token='secret-access-token-key' + user.username,
            application=self.app
        )
        return access_token

    def setUp(self):
        super().setUp()
        self.admin_user = get_user_model().objects.create(
            username="admin",
            is_staff=True
        )
        
        self.regular_user = get_user_model().objects.create(
            username="regular",
            is_staff=False
        )
        self.create_application()
        self.admin_user.token = self.create_token(self.admin_user)
        self.regular_user.token = self.create_token(self.regular_user)

    @staticmethod
    def get_request(method, user=None, query_parameters="", payload=None, format="json"):
        factory = APIRequestFactory()
        request = getattr(factory, method)(query_parameters, payload, format=format)
        if user:
            force_authenticate(request, user=user, token=user.token)
        return request


class GetList(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'get': 'list'})

    def test_basic_list(self):
        self.createdModels = {"models": []}
        self.createdModels['models'].append(TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['models'].append(TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['models'].append(TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))

        response = self.view(self.get_request('get', user=self.admin_user), Model="TestModels")

        assert len(response.data["results"]) == 3
        for message in self.createdModels['models']:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0

    def test_filter(self):
        self.createdModels = {"models": []}
        self.createdModels['models'].append(TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['models'].append(TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        TestModel.objects.create(type="bambi", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        response = self.view(self.get_request('get', user=self.regular_user, query_parameters='?filter={"type": "flood"}'), Model="TestModels")
        assert len(response.data["results"]) == 2
        for message in self.createdModels['models']:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0

    def test_pagination(self):
        self.createdModels = {"models": []}
        for i in range(0, 50):
            self.createdModels['models'].append(
                TestModel.objects.create(type="flood", name="FirstOperation",
                                         start_date="2019-04-06T14:43:{}.630468Z".format(i)))



        response = self.view(self.get_request('get', user=self.regular_user, query_parameters='?limit=100'),
                             Model="TestModels")
        assert len(response.data["results"]) == 50
        assert str(self.createdModels['models'][49].id) == response.data['results'][0]['id']

        response = self.view(self.get_request('get', user=self.regular_user, query_parameters='?limit=7'),
                             Model="TestModels")

        assert len(response.data["results"]) == 7
        assert str(self.createdModels['models'][49].id) == response.data['results'][0]['id']

        response = self.view(self.get_request('get', user=self.regular_user, query_parameters='?limit=7'),
                             Model="TestModels")

        assert len(response.data["results"]) == 7
        assert str(self.createdModels['models'][49].id) == response.data['results'][0]['id']

        response = self.view(
            self.get_request('get', user=self.regular_user, query_parameters='?limit=7&cursor=' + str(response.data['next'])),
            Model="TestModels")

        assert len(response.data["results"]) == 7
        assert str(self.createdModels['models'][42].id) == response.data['results'][0]['id']

        response_previous = self.view(
            self.get_request('get', user=self.regular_user, query_parameters='?limit=7&cursor=' + str(response.data['previous'])),
            Model="TestModels")

        assert len(response_previous.data["results"]) == 7
        assert str(self.createdModels['models'][49].id) == response_previous.data['results'][0]['id']

        response = self.view(
            self.get_request('get', user=self.regular_user,
                             query_parameters='?limit=50&cursor=' + str(response.data['next'])),
            Model="TestModels")

        assert response.data["count"] == 36
        assert str(self.createdModels['models'][35].id) == response.data['results'][0]['id']

    def test_ordering(self):
        self.createdModels = {"models": []}
        self.createdModels['models'].append(
            TestModel.objects.create(type="flood", name="FirstOperation", price=20,
                                     start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['models'].append(
            TestModel.objects.create(type="flood", name="FirstOperation", price=5,
                                     start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['models'].append(
            TestModel.objects.create(type="flood", name="FirstOperation", price=20,
                                     start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['models'].append(
            TestModel.objects.create(type="flood", name="FirstOperation", price=10,
                                     start_date="2019-04-06T14:43:56.630468Z"))

        response = self.view(
            self.get_request('get', user=self.regular_user,
                             query_parameters=''),
            Model="TestModels")
        assert response.data['results'][0]['id'] == str(self.createdModels['models'][3].id)

        response = self.view(
            self.get_request('get', user=self.regular_user,
                             query_parameters='?order_by=-price'),
            Model="TestModels")
        assert response.data['results'][0]['id'] == str(self.createdModels['models'][2].id)

        response = self.view(
            self.get_request('get', user=self.regular_user,
                             query_parameters='?order_by=price'),
            Model="TestModels")
        assert response.data['results'][0]['id'] == str(self.createdModels['models'][1].id)


class PostCreate(BaseApiTest):
    
    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'post': 'create'})
    
    def test_basic_create(self):
        payload = {
                "name": "FirstOperation",
                "type": "flood",
                "start_date" : "2019-04-06T14:43:56.630468Z"
            }
        request = self.get_request(
            'post',
            user=self.admin_user,
            payload=payload
        )
        response = self.view(request, Model="TestModels")
        assert response.status_code == 201

        message = TestModel.objects.get(id=response.data['id'])
        assert message.name == "FirstOperation"
        assert message.type == "flood"


class PutUpdate(BaseApiTest):
    
    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'put': 'update', "patch": "patch"})

    def test_basic_update(self):
        message = TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")

        payload = {
                "name": "FirstOperation2",
            }
        request = self.get_request(
            'patch',
            user=self.admin_user,
            payload=payload
        )
        response = self.view(request, Model="TestModels", id=str(message.id))

        assert response.status_code == 200
        assert response.data['id'] == str(message.id)
        
        retrieved_message = TestModel.objects.get(id=response.data['id'])
        assert retrieved_message.name == "FirstOperation2"
        assert retrieved_message.type == "flood"
        
        
class GetRetrieve(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'get': 'retrieve'})

    def test_basic_retrieve(self):
        message = TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")

        request = self.get_request(
            'get',
            user=self.admin_user,
        )
        response = self.view(request, Model="TestModels", id=str(message.id))
        
        assert response.status_code == 200
        assert response.data['name'] == "FirstOperation"
        assert response.data['type'] == "flood"


class DeleteDestroy(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'delete': 'destroy'})

    def test_basic_delete(self):
        message = TestModel.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")

        request = self.get_request(
            'delete',
            user=self.admin_user,
        )
        response = self.view(request, Model="TestModels", id=str(message.id))
        assert response.data is None
        assert response.status_code == 204
