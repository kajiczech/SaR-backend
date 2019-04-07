from django.contrib import admin


def get_class_for_admin(model):
    # TODO: move this to some utils

    class Admin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]

    return Admin


def register_model(model):
    admin.site.register(model, get_class_for_admin(model))
