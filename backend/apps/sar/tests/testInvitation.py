from django.contrib.auth import get_user_model
from django.test import TestCase

from backend.apps.sar.models import *

class TestInvitation(TestCase):

    def test_basic_invitation(self):
        user = get_user_model().objects.create(
            username="admin",
            is_staff=True
        )
        operation = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        assert len(operation.attendees.all()) == 0
        assert len(OperationsAttendees.objects.all()) == 0
        invitation = Invitation.objects.create(invitee=user, operation=operation)
        invitation.status = 'accepted'
        invitation.save()
        assert OperationsAttendees.objects.all()[0].attendee_role == AttendeeRoles.undefined
        assert operation.attendees.all()[0].id == user.id

    def test_organizer_invitation(self):
        user = get_user_model().objects.create(
            username="admin",
            is_staff=True
        )
        operation = Operation.objects.create(type="flood", name="FirstOperation", start_date="2019-04-06T14:43:56.630468Z")
        assert len(operation.attendees.all()) == 0
        assert len(OperationsAttendees.objects.all()) == 0
        invitation = Invitation.objects.create(invitee=user, operation=operation, type="organizer")
        invitation.status = 'accepted'
        invitation.save()
        assert OperationsAttendees.objects.all()[0].attendee_role == AttendeeRoles.organizer
        assert operation.attendees.all()[0].id == user.id
