from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm

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


# Special handling for user model, so it correctly saves a password
class UserCreationOverrideForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = self.cleaned_data["password1"]
        if commit:
            user.save()
        return user


class AdminPasswordChangeOverrideForm(AdminPasswordChangeForm):
    def save(self, commit=True):
        password = self.cleaned_data["password1"]
        self.user.password = password
        if commit:
            self.user.save()
        return self.user


class UserAdmin(auth_admin.UserAdmin):
    add_form = UserCreationOverrideForm
    change_password_form = AdminPasswordChangeOverrideForm


admin.site.register(User, UserAdmin)
