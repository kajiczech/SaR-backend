from backend.core.tests.models import *
from backend.core.api.endpoints import GenericEndpoint
from backend.core.tests.testGenericEndpoint import BaseApiTest


class TestManyToManyController(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = GenericEndpoint.as_view({'get': 'retrieve'})

    def test_basic_serialization(self):

        operation = TestModel.objects.create(type="flood", name="FirstOperation",
                                             start_date="2019-04-06T14:43:56.630468Z"
                                             )
        link = M2mLinkModel.objects.create(attendee=self.regular_user, operation=operation,
                                           attendee_role='Organizer'
                                           )

        response = self.view(self.get_request('get', user=self.admin_user), Model="M2mLinkModels", id=link.id)

        assert response.data["attendee"]['id'] == str(self.regular_user.id)
        assert response.data["operation"]['id'] == str(operation.id)
        assert response.data["attendee_role"] == 'Organizer'
