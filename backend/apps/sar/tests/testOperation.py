from django.contrib.auth import get_user_model
from django.test import TestCase

from backend.apps.sar.models import *

class TestOperation(TestCase):

    def test_created_by_added_to_attendees(self):
        user = get_user_model().objects.create(
            username="admin",
            is_staff=True
        )
        operation = Operation.objects.create(created_by=user, type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        link = operation.operations_attendees.get(attendee=user)
        assert link.attendee_role == AttendeeRoles.organizer
