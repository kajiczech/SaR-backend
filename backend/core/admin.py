from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from .models import *


def get_class_for_admin(model):
    # TODO: move this to some utils

    class Admin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]

    return Admin


def register_model(model):
    admin.site.register(model, get_class_for_admin(model))


register_model(Role)
register_model(RoleActionPermission)
register_model(RoleViewPermission)


# Special handling for user model, so it correctly saved password
class UserAdmin(auth_admin.UserAdmin):
    pass


admin.site.register(User, UserAdmin)
