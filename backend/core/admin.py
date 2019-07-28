from django.contrib import admin

from .models import *


def get_class_for_admin(model):
    # TODO: move this to some utils

    class Admin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]

    return Admin


def register_model(model):
    admin.site.register(model, get_class_for_admin(model))


register_model(User)
register_model(Role)
register_model(RoleActionPermission)
register_model(RoleViewPermission)
