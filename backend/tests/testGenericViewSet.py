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


Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()


class BaseApiTest(APITestCase):

    def create_applicatioin(self):
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
        self.create_applicatioin()
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
        self.createdModels = {"operations": []}
        self.createdModels['operations'].append(Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['operations'].append(Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['operations'].append(Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))

        response = self.view(self.get_request('get', user=self.admin_user), Model="Operations")

        assert response.data["count"] == 3
        for message in self.createdModels['operations']:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0

    def test_filter(self):
        self.createdModels = {"operations": []}
        self.createdModels['operations'].append(Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        self.createdModels['operations'].append(Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z"))
        Operation.objects.create(type="bambi", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        response = self.view(self.get_request('get', user=self.regular_user, query_parameters='?filter={"type": "flood"}'), Model="Operations")
        assert response.data["count"] == 2
        for message in self.createdModels['operations']:
            assert [x["id"] for x in response.data['results']].index(str(message.id)) >= 0


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
        response = self.view(request, Model="Operations")
        message = Operation.objects.get(id=response.data['id'])
        assert message.name == "FirstOperation"
        assert message.type == "flood"


class PutUpdate(BaseApiTest):
    
    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'put': 'update', "patch": "patch"})

    def test_basic_update(self):
        message = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")

        payload = {
                "name": "FirstOperation2",
            }
        request = self.get_request(
            'patch',
            user=self.admin_user,
            payload=payload
        )
        response = self.view(request, Model="Operations", id=str(message.id))

        assert response.status_code == 200
        assert response.data['id'] == str(message.id)
        
        retrieved_message = Operation.objects.get(id=response.data['id'])
        assert retrieved_message.name == "FirstOperation2"
        assert retrieved_message.type == "flood"
        
        
class GetRetrieve(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'get': 'retrieve'})

    def test_basic_retrieve(self):
        message = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")

        request = self.get_request(
            'get',
            user=self.admin_user,
        )
        response = self.view(request, Model="Operations", id=str(message.id))
        
        assert response.status_code == 200
        assert response.data['name'] == "FirstOperation"
        assert response.data['type'] == "flood"


class DeleteDestroy(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'delete': 'destroy'})


    def test_basic_delete(self):
        message = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")

        request = self.get_request(
            'delete',
            user=self.admin_user,
        )
        response = self.view(request, Model="Operations", id=str(message.id))
        assert response.data is None
        assert response.status_code == 204
