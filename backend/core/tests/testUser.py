from oauth2_provider import views
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from backend.core.api.GenericViewSet import GenericViewSet
from django.contrib.auth import get_user_model
from oauth2_provider.models import get_application_model
from oauth2_provider.models import get_access_token_model

from backend.core.api.endpoints import RegisterUserView, MeView
from backend.core.tests.testGenericViewSet import BaseApiTest

Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()


class TestUserCreateAndUpdate(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.oauth2_view = views.TokenView.as_view()
        self.generic_view = self.view = GenericViewSet.as_view({'post': 'create', "put": "update"})
        self.user_create_view = RegisterUserView.as_view({'post': "register_user"})
        self.me_view = MeView.as_view({'get': "me"})

    def get_put_request(self, user=None, query_parameters=None, payload=None):
        factory = APIRequestFactory()
        request = factory.put(query_parameters, payload, format="json")
        if user:
            force_authenticate(request, user=user, token=user.token)
        return request

    def test_basic_create_and_update(self):
        payload = {
            "username": "test",
            "password": "test"
        }
        created_user = self.generic_view(self.get_request('post', user=self.admin_user, payload=payload), Model="users")
        assert created_user.status_code == 201

        response = self.client.post("/api/v1/oauth2/token", {
            "client_id": "web", "username": "test", "password": "test", "grant_type": "password"
        })

        assert response.status_code == 200

        payload = {
            "username": "test",
            "is_staff": True
        }

        response = self.generic_view(self.get_request('put', user=self.admin_user, payload=payload), Model="users", id=created_user.data['id'])

        assert response.status_code == 200

        response = self.client.post("/api/v1/oauth2/token", {
            "client_id": "web", "username": "test", "password": "test", "grant_type": "password"
        })
        assert response.status_code == 200

        payload = {
            "username": "test",
            "password": "new_password"
        }
        response = self.generic_view(self.get_request('put', user=self.admin_user, payload=payload), Model="users", id=created_user.data['id'])
        assert response.status_code == 200

        response = self.client.post("/api/v1/oauth2/token", {
            "client_id": "web", "username": "test", "password": "new_password", "grant_type": "password"
        })

        assert response.status_code == 200

    def testUserRegister(self):
        response = self.user_create_view(self.get_request('post', payload={
            "username": "test",
            "password": "test",
            "email": "test@test.com"
        }))

        assert response.status_code == 201
        user = get_user_model().objects.get(username="test")
        assert user.email == "test@test.com"

    def testMe(self):
        response = self.me_view(self.get_request('get', self.admin_user))
        assert response.status_code == 200
        assert response.data['id'] == str(self.admin_user.id)
