from django.db import models

from backend.core.api.controllers import BaseApiController
from backend.core.models import BaseModel, StringEnum
from django.contrib.auth import get_user_model

from backend.core.models import User


class OperationTypes(StringEnum):
    bambi = "bambi"
    firefighters = "Firefighters"
    earthquake = "Earthquake"
    flood = "Flood"


class OperationStatuses(StringEnum):
    active = "Active"
    scheduled = "Scheduled"
    canceled = "Canceled"
    held = "Held"


class Operation(BaseModel):

    created_by =              models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="created_operations"
    )
    type =               models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in OperationTypes],
        default=OperationTypes.bambi
    )

    status = models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in OperationStatuses],
        default=OperationStatuses.scheduled
    )
    name =              models.CharField(max_length=255, blank=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    start_latitude =          models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    start_longitude =         models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    description =          models.TextField(blank=True, null=True)

    attendees = models.ManyToManyField(get_user_model(), related_name="operations", through='OperationsAttendees')


Operation.api_controller = BaseApiController(Operation)


class AttendeeRoles(StringEnum):
    organizer = "Organizer"
    scout = 'Scout'
    resolver = "Resolver"


class OperationsAttendees(BaseModel):
    # userModel.objects.filter(
    #   operations_attendees__attendee_role = 'Organizer',
    #   operations_attendees__operation=operation
    # )
    # [x.attendee for x in operation.operations_attendees.filter(attendee_role="Organizer")]
    attendee = models.ForeignKey(get_user_model(), related_name="operations_attendees", on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, related_name="operations_attendees", on_delete=models.CASCADE)
    attendee_role = models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in AttendeeRoles],
        default=AttendeeRoles.resolver
    )

    @classmethod
    def get_serializer(cls, fields_to_serialize=None):
        serializer = super().get_serializer(fields_to_serialize)

        class BaseSerializer(serializer):
            attendee = get_user_model().get_serializer()()
            operation = Operation.get_serializer()()

        return BaseSerializer


OperationsAttendees.api_controller = BaseApiController(OperationsAttendees, url_name='operationsattendees')


class GeotagStatuses(StringEnum):
    open = "Open"
    resolved = "Resolved"
    unresolved = "Unresolved"
    in_progress = "In Progress"


class GeotagTypes(StringEnum):
    drone = "Drone"
    mobile = "Mobile"
    remote = "Remote"


class Geotag(BaseModel):
    created_by =    models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="created_geotags",
    )
    resolved_by =   models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="resolved_geotags"
    )
    operation =     models.ForeignKey(Operation, related_name="geotags", on_delete=models.CASCADE)
    solvers =       models.ManyToManyField(get_user_model(), related_name="geotags_to_resolve")


    type =               models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in GeotagTypes],
        default=GeotagTypes.drone
    )

    status =        models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in GeotagStatuses],
        default=GeotagStatuses.open
    )
    name =              models.CharField(max_length=255, blank=False)
    description =       models.TextField(blank=True, null=True)
    latitude =          models.DecimalField(max_digits=9, decimal_places=6)
    longitude =         models.DecimalField(max_digits=9, decimal_places=6)
    altitude =          models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)


Geotag.api_controller = BaseApiController(Geotag)


class GeofenceTypes(StringEnum):
    coordinates = "Coordinates"


class GeofenceStatuses(StringEnum):
    open = "Open"
    resolved = "Resolved"
    unresolved = "Unresolved"
    in_proggress = "In Progress"


class Geofence(BaseModel):
    created_by =        models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="created_geofences"
    )
    operation =         models.ForeignKey(Operation, related_name="geofences", on_delete=models.CASCADE)
    type =               models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in GeofenceTypes],
        default=GeofenceTypes.coordinates
    )

    status =            models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in GeofenceStatuses],
        default=GeofenceStatuses.open
    )

    name =              models.CharField(max_length=255, blank=False)
    description =       models.TextField(blank=True, null=True)
    coordinates =       models.TextField(blank=True, null=True)


Geofence.api_controller = BaseApiController(Geofence)


class CheckedPointTypes(StringEnum):
    drone = "Drone"
    mobile = "Mobile"
    remote = "Remote"


class CheckedPoint(BaseModel):
    operation =         models.ForeignKey(Operation, related_name="checked_points", on_delete=models.CASCADE)
    created_by =        models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="created_checked_points"
    )

    type =              models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in GeofenceTypes],
        default=CheckedPointTypes.drone
    )
    radius =            models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    latitude =          models.DecimalField(max_digits=9, decimal_places=6)
    longitude =         models.DecimalField(max_digits=9, decimal_places=6)


CheckedPoint.api_controller = BaseApiController(CheckedPoint)


class InvitationStatuses(StringEnum):
    open = "Open"
    accepted = "Accepted"
    rejected = "Rejected"


class InvitationTypes(StringEnum):
    regular = "Regular"
    organizer = "Organizer"


class Invitation(BaseModel):
    invitee = models.ForeignKey(get_user_model(), related_name="invitations", on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, related_name="invitations", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in InvitationTypes],
        default=InvitationTypes.regular
    )

    status = models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in InvitationStatuses],
        default=InvitationStatuses.open
    )


Invitation.api_controller = BaseApiController(Invitation)
