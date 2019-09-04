from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from oauth2_provider.models import get_application_model
import json
Application = get_application_model()


class Authentication(APITestCase):

    def create_applicatioin(self):
        self.app = Application.objects.create(
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
            redirect_uris='https://none',
            name='web',
            client_id="web",
            user=self.admin_user
        )

    def setUp(self):
        self.admin_user = get_user_model()(
            username="admin",
            password="admin",
            email="admin@google.com",
            is_staff=True
        )
        self.admin_user.save()
        self.create_applicatioin()

    def testEmailLogin(self):
        response = self.client.post("/api/v1/oauth2/token", {
            "client_id": "web", "email": "admin@google.com", "password": "admin", "grant_type": "password"
        })

        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8"))['access_token']
