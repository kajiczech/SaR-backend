import enum

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

import uuid

from backend.core.api.controllers import BaseApiController


class StringEnum(enum.Enum):
    """Enum which can be compared to string and saves a string to DB"""
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return repr(self.value) == repr(other)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_entered = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    api_controller = None

    class Meta:
        abstract = True
        ordering = ['-date_modified']

class Role(BaseModel):
    Name =      models.CharField(max_length=31, blank=True, null=True)


Role.api_controller = BaseApiController(model=Role)


class AccessLevels(StringEnum):
    none = 'none'
    owner = 'owner'
    shared = 'shared'
    admin = 'admin'


class RoleViewPermission(BaseModel):
    model =                     models.CharField(max_length=31, blank=True, null=True)
    application =               models.CharField(max_length=31, blank=True, null=True)
    access_level =              models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in AccessLevels],
        default=AccessLevels.owner
    )


RoleViewPermission.api_controller = BaseApiController(model=RoleViewPermission)


class RoleActionPermission(BaseModel):
    model =                     models.CharField(max_length=31, blank=True, null=True)
    application =               models.CharField(max_length=31, blank=True, null=True)
    access_level =              models.CharField(
        max_length=31,
        choices=[(a.name, a.value) for a in AccessLevels],
        default=AccessLevels.owner
    )


RoleActionPermission.api_controller = BaseApiController(model=RoleActionPermission)


class User(AbstractUser, BaseModel):

    roles = models.ManyToManyField(Role, "users", blank=True)
    #     Overriding password, so it can be blank
    password = models.CharField(_('password'), max_length=128, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Update password only when it is changed, so we don't hash hashed password
        if self.pk:
            try:
                saved = User.objects.get(pk=self.pk)
                if self.password != saved.password:
                    self.password = make_password(self.password)
            except (User.DoesNotExist, ValueError):
                self.password = make_password(self.password)
        else:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


User.api_controller = BaseApiController(model=User)

