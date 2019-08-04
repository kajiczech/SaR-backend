from django.contrib.auth import get_user_model
from django.db import models

from backend.core.api.controllers import BaseApiController, ManyToManyController
from backend.core.models import StringEnum, BaseModel, User


class Types(StringEnum):
    bambi = "bambi"
    firefighters = "Firefighters"
    earthquake = "Earthquake"
    flood = "Flood"


class Statuses(StringEnum):
    active = "Active"
    scheduled = "Scheduled"
    canceled = "Canceled"
    held = "Held"


class TestModel(BaseModel):

    created_by =              models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="created_test_models"
    )
    type =               models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in Types],
        default=Types.bambi
    )

    status = models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in Statuses],
        default=Statuses.scheduled
    )
    name =              models.CharField(max_length=255, blank=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    start_latitude =          models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    start_longitude =         models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    description =          models.TextField(blank=True, null=True)

    attendees = models.ManyToManyField(get_user_model(), related_name="test_models", through='M2mLinkModel')


TestModel.api_controller = BaseApiController(TestModel)


class Roles(StringEnum):
    organizer = "Organizer"
    scout = 'Scout'
    resolver = "Resolver"
    undefined = "Undefined"


class M2mLinkModel(BaseModel):
    # userModel.objects.filter(
    #   operations_attendees__attendee_role = 'Organizer',
    #   operations_attendees__operation=operation
    # )
    # [x.attendee for x in operation.operations_attendees.filter(attendee_role="Organizer")]
    attendee = models.ForeignKey(get_user_model(), related_name="M2mLinkModel", on_delete=models.CASCADE)
    operation = models.ForeignKey(TestModel, related_name="M2mLinkModel", on_delete=models.CASCADE)
    attendee_role = models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in Roles],
    )


M2mLinkModel.api_controller = ManyToManyController(M2mLinkModel, 'attendee', get_user_model(),
                                                          'operation', TestModel)

