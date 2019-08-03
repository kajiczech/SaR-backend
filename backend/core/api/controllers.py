from rest_framework import serializers
from rest_framework.utils import model_meta


class BaseApiController:
    # Which fields are not returned in serialization
    hidden_fields = []

    def __init__(self, model, hidden_fields=None, url_name=None):
        self.hidden_fields = hidden_fields or []
        self.url_name = url_name
        self.model = model

    def get_serializer(self, view=None, fields_to_serialize=None):
        if fields_to_serialize is None:
            fields_to_serialize = self.get_field_names_for_serializer(self.model)

        # Make sure private fields are never fetched
        if not view:
            fields_to_serialize = [item for item in fields_to_serialize if item not in self.hidden_fields]
        elif view.action == 'list' or view.action == 'retrieve':
            fields_to_serialize = [item for item in fields_to_serialize if item not in self.hidden_fields]

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


class ManyToManyController(BaseApiController):

    def __init__(self, model, first_link, first_model, second_link, second_model, *args, **kwargs):
        self.first_link = first_link
        self.second_link = second_link

        # We could do it like this if we didn't loaded the controllers before the models are loaded - this throws AppRegistryException
        # self.first_model = model._meta.get_field(first_link).related_model
        # self.second_model = model._meta.get_field(second_link).related_model

        self.first_model = first_model
        self.second_model = second_model

        super().__init__(model, *args, **kwargs)

    def get_serializer(self, view=None, fields_to_serialize=None):
        serializer = super().get_serializer(view=view, fields_to_serialize=fields_to_serialize)
        serializer.attendee = self.first_model.api_controller.get_serializer()()
        serializer.operation = self.second_model.api_controller.get_serializer()()

        # We need to create the class like this, because the fields are registered upon class creation
        #        # BaseSerializer._declared_fields[self.first_link] = serializer()
        # would also work. Still has not decided what is less ugly

        BaseSerializer = type('BaseSerializer', (serializer,), {
            self.first_link: self.first_model.api_controller.get_serializer()(),
            self.second_link: self.second_model.api_controller.get_serializer()()
        })

        return BaseSerializer
