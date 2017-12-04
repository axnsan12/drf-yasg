import functools
from collections import OrderedDict

from django.core.validators import RegexValidator
from django.utils.encoding import force_text
from rest_framework import serializers
from rest_framework.schemas import AutoSchema

from drf_swagger.errors import SwaggerGenerationError
from . import openapi


def find_regex(regex_field):
    regex_validator = None
    for validator in regex_field.validators:
        if isinstance(validator, RegexValidator):
            if regex_validator is not None:
                # bail if multiple validators are found - no obvious way to choose
                return None
            regex_validator = validator

    # regex_validator.regex should be a compiled re object...
    return getattr(getattr(regex_validator, 'regex', None), 'pattern', None)


class SwaggerAutoSchema(object):
    def __init__(self, view):
        super().__init__()
        self._sch = AutoSchema()
        self.view = view
        self._sch.view = view

    def get_operation(self, operation_id, path, method):
        """Get an Operation for the given API endpoint (path, method).
        This includes query, body parameters and response schemas.

        :param str operation_id: swagger operation id; should be unique across document
        :param str path: request path
        :param str method: request http method
        :return openapi.Operation: the resulting Operation object
        """
        body = self.get_request_body_param(path, method)
        parameters = [body]

        parameters = [param for param in parameters if param is not None]
        description = self._sch.get_description(path, method)
        responses = self.get_responses(path, method)
        return openapi.Operation(
            operation_id=operation_id,
            description=description,
            responses=responses,
            parameters=parameters
        )

    def get_responses(self, path, method):
        empty_response = {'description': ''}
        if method.lower() == 'post':
            return {'201': empty_response}
        if method.lower() == 'delete':
            return {'204': empty_response}
        return {'200': empty_response}

    def field_to_swagger(self, field, swagger_object_type, **kwargs):
        """Convert a drf Serializer or Field instance into a Swagger object.

        :param rest_framework.serializers.Field field: the source field
        :param type swagger_object_type: should be one of Schema, Parameter, Items
        :param kwargs: extra attributes for constructing the object;
           if swagger_object_type is Parameter, `name` and `in_` should be provided
        :return Swagger,Parameter,Items: the swagger object
        """
        assert swagger_object_type in (openapi.Schema, openapi.Parameter, openapi.Items)
        title = force_text(field.label) if field.label else None
        title = title if swagger_object_type == openapi.Schema else None  # only Schema has title
        title = None
        description = force_text(field.help_text) if field.help_text else None
        description = description if swagger_object_type != openapi.Items else None  # Items has no description either

        SwaggerType = functools.partial(swagger_object_type, title=title, description=description, **kwargs)
        # arrays in Schema have Schema elements, arrays in Parameter and Items have Items elements
        ChildSwaggerType = openapi.Schema if swagger_object_type == openapi.Schema else openapi.Items

        # ------ NESTED
        if isinstance(field, (serializers.ListSerializer, serializers.ListField)):
            child_schema = self.field_to_swagger(field.child, ChildSwaggerType)
            return SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=child_schema,
            )
        elif isinstance(field, serializers.Serializer):
            # TODO: what about BaseSerializer?
            if swagger_object_type != openapi.Schema:
                raise SwaggerGenerationError("cannot instantiate nested serializer as "
                                             + swagger_object_type.__name__)
            return SwaggerType(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict(
                    (key, self.field_to_swagger(value, ChildSwaggerType))
                    for key, value
                    in field.fields.items()
                )
            )
        elif isinstance(field, serializers.ManyRelatedField):
            child_schema = self.field_to_swagger(field.child_relation, ChildSwaggerType)
            return SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=child_schema,
                unique_items=True,  # is this OK?
            )
        elif isinstance(field, serializers.RelatedField):
            # TODO: infer type for PrimaryKeyRelatedField?
            return SwaggerType(type=openapi.TYPE_STRING)
        # ------ CHOICES
        elif isinstance(field, serializers.MultipleChoiceField):
            return SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=ChildSwaggerType(
                    type=openapi.TYPE_STRING,
                    enum=list(field.choices.keys())
                )
            )
        elif isinstance(field, serializers.ChoiceField):
            return SwaggerType(type=openapi.TYPE_STRING, enum=list(field.choices.keys()))
        # ------ BOOL
        elif isinstance(field, serializers.BooleanField):
            return SwaggerType(type=openapi.TYPE_BOOLEAN)
        # ------ NUMERIC
        elif isinstance(field, (serializers.DecimalField, serializers.FloatField)):
            # TODO: min_value max_value
            return SwaggerType(type=openapi.TYPE_NUMBER)
        elif isinstance(field, serializers.IntegerField):
            # TODO: min_value max_value
            return SwaggerType(type=openapi.TYPE_INTEGER)
        # ------ STRING
        elif isinstance(field, serializers.EmailField):
            return SwaggerType(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL)
        elif isinstance(field, serializers.RegexField):
            return SwaggerType(type=openapi.TYPE_STRING, pattern=find_regex(field))
        elif isinstance(field, serializers.SlugField):
            return SwaggerType(type=openapi.TYPE_STRING, format=openapi.FORMAT_SLUG)
        elif isinstance(field, serializers.URLField):
            return SwaggerType(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI)
        elif isinstance(field, serializers.IPAddressField):
            format = {'ipv4': openapi.FORMAT_IPV4, 'ipv6': openapi.FORMAT_IPV6}.get(field.protocol, None)
            return SwaggerType(type=openapi.TYPE_STRING, format=format)
        elif isinstance(field, serializers.CharField):
            # TODO: min_length max_length (for all CharField subclasses above too)
            return SwaggerType(type=openapi.TYPE_STRING)
        elif isinstance(field, serializers.UUIDField):
            return SwaggerType(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID)
        # ------ DATE & TIME
        elif isinstance(field, serializers.DateField):
            return SwaggerType(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)
        elif isinstance(field, serializers.DateTimeField):
            return SwaggerType(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
        # ------ OTHERS
        elif isinstance(field, serializers.FileField):
            # swagger 2.0 does not support specifics about file fields, so ImageFile gets no special treatment
            # OpenAPI 3.0 does support it, so a future implementation could handle this better
            # TODO: appropriate produces/consumes somehow/somewhere?
            if swagger_object_type != openapi.Parameter:
                raise SwaggerGenerationError("parameter of type file can not be nested")
            return SwaggerType(type=openapi.TYPE_FILE)
        elif isinstance(field, serializers.JSONField):
            return SwaggerType(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_BINARY if field.binary else None
            )
        elif isinstance(field, serializers.DictField) and swagger_object_type == openapi.Schema:
            child_schema = self.field_to_swagger(field.child, ChildSwaggerType)
            return SwaggerType(
                type=openapi.TYPE_OBJECT,
                additional_properties=child_schema
            )

        # TODO unhandled fields: TimeField DurationField HiddenField ModelField NullBooleanField?
        # TODO: return info about required/allowed empty

        # everything else gets string by default
        return SwaggerType(type=openapi.TYPE_STRING)

    def get_request_body_schema(self, path, method, serializer):
        """Return the Schema for a given request's body data. Only applies to PUT, PATCH and POST requests.

        :param str path: the view's path
        :param str method: HTTP request method
        :param serializer: the view's request serialzier
        :return openapi.Schema: the request body schema
        """
        return self.field_to_swagger(serializer, openapi.Schema)

    def get_request_body_param(self, path, method):
        """Return a request body Schema determined by the view's serializer class.

        :param str path: the view's path
        :param str method: HTTP request method
        :return: an openapi.Parameter with in: body
        """
        # only PUT, PATCH or POST can have a request body
        if method not in ('PUT', 'PATCH', 'POST'):
            return None

        # TODO: only GenericAPIViews have defined serializers;
        # APIViews and plain ViewSets will need some kind of manual treatment
        if not hasattr(self.view, 'get_serializer'):
            return None

        serializer = self.view.get_serializer()
        schema = self.get_request_body_schema(path, method, serializer)
        return openapi.Parameter(name='data', in_=openapi.IN_BODY, schema=schema)
