import enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.manager import ManagerDescriptor
from rest_framework import viewsets, serializers, permissions, generics

from backend.core.managers import *
from rest_framework.utils import html, model_meta, representation

import uuid


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
    deleted = models.IntegerField(default=0)

    objects = BaseManager()
    private_fields = []

    @classmethod
    def get_serializer(cls, fields_to_serialize=None):
        if fields_to_serialize is None:
            fields_to_serialize = cls.get_field_names_for_serializer()

        # Make sure private fields are never fetched
        fields_to_serialize = [item for item in fields_to_serialize if item not in cls.private_fields]

        class BaseSerializer(serializers.ModelSerializer):
            class Meta:
                model = cls
                fields = fields_to_serialize
        return BaseSerializer

    class Meta:
        abstract = True
        ordering = ['-date_modified']

    def delete(self, from_db=False, using=None, keep_parents=False):
        # TODO Before and after delete logic

        if from_db:
            super(BaseModel, self).delete(using, keep_parents)
            return
        self.deleted = 1
        self.save()

    @classmethod
    def get_implicit_filter(cls, user):

        return {}

    @classmethod
    def get_field_names_for_serializer(cls):
        """Taken from Serializers.ModelSerializer, because model.get_fields returns some additional fields"""
        model_info = model_meta.get_field_info(cls)
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        return (
            [model_info.pk.name] +
            list(model_info.fields) +
            list(model_info.forward_relations)
        )


class User(AbstractUser, BaseModel):

    private_fields = ["password"]
