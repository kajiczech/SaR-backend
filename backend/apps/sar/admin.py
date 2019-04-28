from django.contrib import admin

from .models import *


def get_class_for_admin(model):
    # TODO: move this to some utils

    class Admin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]

    return Admin


def register_model(model):
    admin.site.register(model, get_class_for_admin(model))


register_model(Geofence)
register_model(Geotag)
register_model(Invitation)
register_model(Operation)
register_model(OperationsAttendees)
register_model(CheckedPoint)
