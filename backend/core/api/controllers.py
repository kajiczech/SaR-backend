from rest_framework import serializers
from rest_framework.utils import model_meta


class BaseApiController:
    # Which fields are not returned in serialization
    private_fields = []

    def __init__(self, model, private_fields=None, url_name=None):
        self.private_fields = private_fields or []
        self.url_name = url_name
        self.model = model

    def get_serializer(self, fields_to_serialize=None):
        if fields_to_serialize is None:
            fields_to_serialize = self.get_field_names_for_serializer(self.model)

        # Make sure private fields are never fetched
        fields_to_serialize = [item for item in fields_to_serialize if item not in self.private_fields]

        class BaseSerializer(serializers.ModelSerializer):
            class Meta:
                model = self.model
                fields = fields_to_serialize
        return BaseSerializer

    def get_implicit_filter(self, user):
        filter_def = {}
        return filter_def

    @staticmethod
    def get_field_names_for_serializer(model):
        """Taken from Serializers.ModelSerializer, because model.get_fields returns some additional fields"""
        model_info = model_meta.get_field_info(model)
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        return (
            [model_info.pk.name] +
            list(model_info.fields) +
            list(model_info.forward_relations)
        )

    def get_url_name(self):
        if self.url_name:
            return self.url_name.lower()
        return self.model.__name__.lower() + "s"


class AssignableApiController(BaseApiController):

    assignment_field = 'user'

    def __init__(self, model, assignment_field='user', *args, **kwargs):
        self.assignment_field = assignment_field
        super().__init__(model, *args, **kwargs)

    def get_implicit_filter(self, user):
        filter_def = {}

        if not user.is_staff:
                filter_def[self.assignment_field] = user.id

        return filter_def
