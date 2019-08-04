from backend.apps.sar.models import *
from backend.core.api.GenericViewSet import GenericViewSet
from backend.core.tests.testGenericViewSet import BaseApiTest

class TestManyToManyController(BaseApiTest):

    def setUp(self):
        super().setUp()
        self.view = GenericViewSet.as_view({'get': 'retrieve'})

    def test_basic_serialization(self):
        pass
        # operation = Operation.objects.create(type="flood", name="FirstOperation",
        #                                      start_date="2019-04-06T14:43:56.630468Z"
        #                                      )
        # link = OperationsAttendees.objects.create(attendee=self.regular_user, operation=operation,
        #                                           attendee_role='Organizer'
        #                                           )
        #
        # response = self.view(self.get_request('get', user=self.admin_user), Model="OperationsAttendees", id=link.id)
        #
        # assert response.data["attendee"]['id'] == str(self.regular_user.id)
        # assert response.data["operation"]['id'] == str(operation.id)
        # assert response.data["attendee_role"] == 'Organizer'
