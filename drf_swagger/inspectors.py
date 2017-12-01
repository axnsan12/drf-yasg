import functools
from collections import OrderedDict

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.serializers import Field
from rest_framework.schemas import AutoSchema
from django.utils.encoding import force_text

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


def field_to_swagger(field, swagger_object_type):
    """Convert a Django Rest Framework serializer Field into a Swagger definition.

    :param Field field: the source field
    :param type swagger_object_type: should be one of Schema, Parameter, Items
    :return: the swagger object
    """
    assert swagger_object_type in (openapi.Schema, openapi.Parameter, openapi.Items)
    title = force_text(field.label) if field.label else ''
    title = title if swagger_object_type == openapi.Schema else None  # only Schema has title
    description = force_text(field.help_text) if field.help_text else ''
    description = description if swagger_object_type != openapi.Items else None  # Items has no description either

    SwaggerType = functools.partial(swagger_object_type, title=title, description=description)
    # arrays in Schema have Schema elements, arrays in Parameter and Items have Items elements
    ChildSwaggerType = openapi.Schema if SwaggerType == openapi.Schema else openapi.Items

    # ------ NESTED
    if isinstance(field, (serializers.ListSerializer, serializers.ListField)):
        child_schema = field_to_swagger(field.child, ChildSwaggerType)
        return SwaggerType(
            type=openapi.TYPE_ARRAY,
            items=child_schema,
        )
    elif isinstance(field, serializers.Serializer):
        # TODO: what about BaseSerializer?
        if swagger_object_type != openapi.Schema:
            raise SwaggerGenerationError("cannot instantiate nested serializer as "
                                         + swagger_object_type.__class__.__name__)
        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict(
                (key, field_to_swagger(value, ChildSwaggerType))
                for key, value
                in field.fields.items()
            )
        )
    elif isinstance(field, serializers.ManyRelatedField):
        child_schema = field_to_swagger(field.child_relation, ChildSwaggerType)
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
        return SwaggerType(type=openapi.TYPE_FILE)
    elif isinstance(field, serializers.JSONField):
        return SwaggerType(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_BINARY if field.binary else None
        )
    elif isinstance(field, serializers.DictField) and swagger_object_type == openapi.Schema:
        child_schema = field_to_swagger(field.child, ChildSwaggerType)
        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            additional_properties=child_schema
        )

    # TODO unhandled fields: TimeField DurationField HiddenField ModelField NullBooleanField?
    # TODO: return info about required/allowed empty

    # everything else gets string by default
    return SwaggerType(type=openapi.TYPE_STRING)


class SwaggerAutoSchema(AutoSchema):
    pass
