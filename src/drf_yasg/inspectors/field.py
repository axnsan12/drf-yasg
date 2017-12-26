import operator
from collections import OrderedDict

from django.core import validators
from django.db import models
from rest_framework import serializers
from rest_framework.settings import api_settings as rest_framework_settings

from .base import NotHandled, SerializerInspector, FieldInspector
from .. import openapi
from ..errors import SwaggerGenerationError
from ..utils import filter_none


class InlineSerializerInspector(SerializerInspector):
    """Provides serializer conversions using :meth:`.FieldInspector.field_to_swagger_object`."""

    #: whether to output :class:`.Schema` definitions inline or into the ``definitions`` section
    use_definitions = False

    def get_schema(self, serializer):
        return self.probe_field_inspectors(serializer, openapi.Schema, self.use_definitions)

    def get_request_parameters(self, serializer, in_):
        fields = getattr(serializer, 'fields', {})
        return [
            self.probe_field_inspectors(
                value, openapi.Parameter, self.use_definitions,
                name=self.get_parameter_name(key), in_=in_
            )
            for key, value
            in fields.items()
        ]

    def get_property_name(self, field_name):
        return field_name

    def get_parameter_name(self, field_name):
        return field_name

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, (serializers.ListSerializer, serializers.ListField)):
            child_schema = self.probe_field_inspectors(field.child, ChildSwaggerType, use_references)
            return SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=child_schema,
            )
        elif isinstance(field, serializers.Serializer):
            if swagger_object_type != openapi.Schema:
                raise SwaggerGenerationError("cannot instantiate nested serializer as " + swagger_object_type.__name__)

            serializer = field
            serializer_meta = getattr(serializer, 'Meta', None)
            if hasattr(serializer_meta, 'ref_name'):
                ref_name = serializer_meta.ref_name
            else:
                ref_name = type(serializer).__name__
                if ref_name.endswith('Serializer'):
                    ref_name = ref_name[:-len('Serializer')]

            def make_schema_definition():
                properties = OrderedDict()
                required = []
                for key, value in serializer.fields.items():
                    key = self.get_property_name(key)
                    properties[key] = self.probe_field_inspectors(value, ChildSwaggerType, use_references)
                    if value.required:
                        required.append(key)

                return SwaggerType(
                    type=openapi.TYPE_OBJECT,
                    properties=properties,
                    required=required or None,
                )

            if not ref_name or not use_references:
                return make_schema_definition()

            definitions = self.components.with_scope(openapi.SCHEMA_DEFINITIONS)
            definitions.setdefault(ref_name, make_schema_definition)
            return openapi.SchemaRef(definitions, ref_name)

        return NotHandled


class ReferencingSerializerInspector(InlineSerializerInspector):
    use_definitions = True


def get_queryset_field(queryset, field_name):
    """Try to get information about a model and model field from a queryset.

    :param queryset: the queryset
    :param field_name: target field name
    :returns: the model and target field from the queryset as a 2-tuple; both elements can be ``None``
    :rtype: tuple
    """
    model = getattr(queryset, 'model', None)
    model_field = get_model_field(model, field_name)
    return model, model_field


def get_model_field(model, field_name):
    """Try to get the given field from a django db model.

    :param model: the model
    :param field_name: target field name
    :return: model field or ``None``
    """
    try:
        if field_name == 'pk':
            return model._meta.pk
        else:
            return model._meta.get_field(field_name)
    except Exception:  # pragma: no cover
        return None


def get_parent_serializer(field):
    """Get the nearest parent ``Serializer`` instance for the given field.

    :return: ``Serializer`` or ``None``
    """
    while field is not None:
        if isinstance(field, serializers.Serializer):
            return field

        field = field.parent

    return None  # pragma: no cover


def get_related_model(model, source):
    """Try to find the other side of a model relationship given the name of a related field.

    :param model: one side of the relationship
    :param str source: related field name
    :return: related model or ``None``
    """
    try:
        return getattr(model, source).rel.related_model
    except Exception:  # pragma: no cover
        return None


class RelatedFieldInspector(FieldInspector):
    """Provides conversions for ``RelatedField``\ s."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, serializers.ManyRelatedField):
            child_schema = self.probe_field_inspectors(field.child_relation, ChildSwaggerType, use_references)
            return SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=child_schema,
                unique_items=True,
            )

        if not isinstance(field, serializers.RelatedField):
            return NotHandled

        field_queryset = getattr(field, 'queryset', None)

        if isinstance(field, (serializers.PrimaryKeyRelatedField, serializers.SlugRelatedField)):
            if getattr(field, 'pk_field', ''):
                # a PrimaryKeyRelatedField can have a `pk_field` attribute which is a
                # serializer field that will convert the PK value
                result = self.probe_field_inspectors(field.pk_field, swagger_object_type, use_references, **kwargs)
                # take the type, format, etc from `pk_field`, and the field-level information
                # like title, description, default from the PrimaryKeyRelatedField
                return SwaggerType(existing_object=result)

            target_field = getattr(field, 'slug_field', 'pk')
            if field_queryset is not None:
                # if the RelatedField has a queryset, try to get the related model field from there
                model, model_field = get_queryset_field(field_queryset, target_field)
            else:
                # if the RelatedField has no queryset (e.g. read only), try to find the target model
                # from the view queryset or ModelSerializer model, if present
                view_queryset = getattr(self.view, 'queryset', None)
                serializer_meta = getattr(get_parent_serializer(field), 'Meta', None)
                this_model = getattr(view_queryset, 'model', None) or getattr(serializer_meta, 'model', None)
                source = getattr(field, 'source', '') or field.field_name
                model = get_related_model(this_model, source)
                model_field = get_model_field(model, target_field)

            attrs = get_basic_type_info(model_field) or {'type': openapi.TYPE_STRING}
            return SwaggerType(**attrs)
        elif isinstance(field, serializers.HyperlinkedRelatedField):
            return SwaggerType(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI)

        return SwaggerType(type=openapi.TYPE_STRING)


def find_regex(regex_field):
    """Given a ``Field``, look for a ``RegexValidator`` and try to extract its pattern and return it as a string.

    :param serializers.Field regex_field: the field instance
    :return: the extracted pattern, or ``None``
    :rtype: str
    """
    regex_validator = None
    for validator in regex_field.validators:
        if isinstance(validator, validators.RegexValidator):
            if regex_validator is not None:
                # bail if multiple validators are found - no obvious way to choose
                return None  # pragma: no cover
            regex_validator = validator

    # regex_validator.regex should be a compiled re object...
    return getattr(getattr(regex_validator, 'regex', None), 'pattern', None)


numeric_fields = (serializers.IntegerField, serializers.FloatField, serializers.DecimalField)
limit_validators = [
    # minimum and maximum apply to numbers
    (validators.MinValueValidator, numeric_fields, 'minimum', operator.__gt__),
    (validators.MaxValueValidator, numeric_fields, 'maximum', operator.__lt__),

    # minLength and maxLength apply to strings
    (validators.MinLengthValidator, serializers.CharField, 'min_length', operator.__gt__),
    (validators.MaxLengthValidator, serializers.CharField, 'max_length', operator.__lt__),

    # minItems and maxItems apply to lists
    (validators.MinLengthValidator, serializers.ListField, 'min_items', operator.__gt__),
    (validators.MaxLengthValidator, serializers.ListField, 'max_items', operator.__lt__),
]


def find_limits(field):
    """Given a ``Field``, look for min/max value/length validators and return appropriate limit validation attributes.

    :param serializers.Field field: the field instance
    :return: the extracted limits
    :rtype: OrderedDict
    """
    limits = {}
    applicable_limits = [
        (validator, attr, improves)
        for validator, field_class, attr, improves in limit_validators
        if isinstance(field, field_class)
    ]

    for validator in field.validators:
        if not hasattr(validator, 'limit_value'):
            continue

        for validator_class, attr, improves in applicable_limits:
            if isinstance(validator, validator_class):
                if attr not in limits or improves(validator.limit_value, limits[attr]):
                    limits[attr] = validator.limit_value

    return OrderedDict(sorted(limits.items()))


model_field_to_basic_type = [
    (models.AutoField, (openapi.TYPE_INTEGER, None)),
    (models.BinaryField, (openapi.TYPE_STRING, openapi.FORMAT_BINARY)),
    (models.BooleanField, (openapi.TYPE_BOOLEAN, None)),
    (models.NullBooleanField, (openapi.TYPE_BOOLEAN, None)),
    (models.DateTimeField, (openapi.TYPE_STRING, openapi.FORMAT_DATETIME)),
    (models.DateField, (openapi.TYPE_STRING, openapi.FORMAT_DATE)),
    (models.DecimalField, (openapi.TYPE_NUMBER, None)),
    (models.DurationField, (openapi.TYPE_INTEGER, None)),
    (models.FloatField, (openapi.TYPE_NUMBER, None)),
    (models.IntegerField, (openapi.TYPE_INTEGER, None)),
    (models.IPAddressField, (openapi.TYPE_STRING, openapi.FORMAT_IPV4)),
    (models.GenericIPAddressField, (openapi.TYPE_STRING, openapi.FORMAT_IPV6)),
    (models.SlugField, (openapi.TYPE_STRING, openapi.FORMAT_SLUG)),
    (models.TextField, (openapi.TYPE_STRING, None)),
    (models.TimeField, (openapi.TYPE_STRING, None)),
    (models.UUIDField, (openapi.TYPE_STRING, openapi.FORMAT_UUID)),
    (models.CharField, (openapi.TYPE_STRING, None)),
]

ip_format = {'ipv4': openapi.FORMAT_IPV4, 'ipv6': openapi.FORMAT_IPV6}

serializer_field_to_basic_type = [
    (serializers.EmailField, (openapi.TYPE_STRING, openapi.FORMAT_EMAIL)),
    (serializers.SlugField, (openapi.TYPE_STRING, openapi.FORMAT_SLUG)),
    (serializers.URLField, (openapi.TYPE_STRING, openapi.FORMAT_URI)),
    (serializers.IPAddressField, (openapi.TYPE_STRING, lambda field: ip_format.get(field.protocol, None))),
    (serializers.UUIDField, (openapi.TYPE_STRING, openapi.FORMAT_UUID)),
    (serializers.RegexField, (openapi.TYPE_STRING, None)),
    (serializers.CharField, (openapi.TYPE_STRING, None)),
    ((serializers.BooleanField, serializers.NullBooleanField), (openapi.TYPE_BOOLEAN, None)),
    (serializers.IntegerField, (openapi.TYPE_INTEGER, None)),
    ((serializers.FloatField, serializers.DecimalField), (openapi.TYPE_NUMBER, None)),
    (serializers.DurationField, (openapi.TYPE_NUMBER, None)),  # ?
    (serializers.DateField, (openapi.TYPE_STRING, openapi.FORMAT_DATE)),
    (serializers.DateTimeField, (openapi.TYPE_STRING, openapi.FORMAT_DATETIME)),
    (serializers.ModelField, (openapi.TYPE_STRING, None)),
]

basic_type_info = serializer_field_to_basic_type + model_field_to_basic_type


def get_basic_type_info(field):
    """Given a serializer or model ``Field``, return its basic type information - ``type``, ``format``, ``pattern``,
    and any applicable min/max limit values.

    :param field: the field instance
    :return: the extracted attributes as a dictionary, or ``None`` if the field type is not known
    :rtype: OrderedDict
    """
    if field is None:
        return None

    for field_class, type_format in basic_type_info:
        if isinstance(field, field_class):
            swagger_type, format = type_format
            if callable(format):
                format = format(field)
            break
    else:  # pragma: no cover
        return None

    pattern = find_regex(field) if format in (None, openapi.FORMAT_SLUG) else None
    limits = find_limits(field)

    result = OrderedDict([
        ('type', swagger_type),
        ('format', format),
        ('pattern', pattern)
    ])
    result.update(limits)
    result = filter_none(result)
    return result


class SimpleFieldInspector(FieldInspector):
    """Provides conversions for fields which can be described using just ``type``, ``format``, ``pattern``
    and min/max validators.
    """

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        type_info = get_basic_type_info(field)
        if type_info is None:
            return NotHandled

        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)
        return SwaggerType(**type_info)


class ChoiceFieldInspector(FieldInspector):
    """Provides conversions for ``ChoiceField`` and ``MultipleChoiceField``."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, serializers.MultipleChoiceField):
            return SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=ChildSwaggerType(
                    type=openapi.TYPE_STRING,
                    enum=list(field.choices.keys())
                )
            )
        elif isinstance(field, serializers.ChoiceField):
            return SwaggerType(type=openapi.TYPE_STRING, enum=list(field.choices.keys()))

        return NotHandled


class FileFieldInspector(FieldInspector):
    """Provides conversions for ``FileField``\ s."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, serializers.FileField):
            # swagger 2.0 does not support specifics about file fields, so ImageFile gets no special treatment
            # OpenAPI 3.0 does support it, so a future implementation could handle this better
            err = SwaggerGenerationError("FileField is supported only in a formData Parameter or response Schema")
            if swagger_object_type == openapi.Schema:
                # FileField.to_representation returns URL or file name
                result = SwaggerType(type=openapi.TYPE_STRING, read_only=True)
                if getattr(field, 'use_url', rest_framework_settings.UPLOADED_FILES_USE_URL):
                    result.format = openapi.FORMAT_URI
                return result
            elif swagger_object_type == openapi.Parameter:
                param = SwaggerType(type=openapi.TYPE_FILE)
                if param['in'] != openapi.IN_FORM:
                    raise err  # pragma: no cover
                return param
            else:
                raise err  # pragma: no cover

        return NotHandled


class DictFieldInspector(FieldInspector):
    """Provides conversion for ``DictField``."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, serializers.DictField) and swagger_object_type == openapi.Schema:
            child_schema = self.probe_field_inspectors(field.child, ChildSwaggerType, use_references)
            return SwaggerType(
                type=openapi.TYPE_OBJECT,
                additional_properties=child_schema
            )

        return NotHandled


class StringDefaultFieldInspector(FieldInspector):
    """For otherwise unhandled fields, return them as plain :data:`.TYPE_STRING` objects."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):  # pragma: no cover
        # TODO unhandled fields: TimeField HiddenField JSONField
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)
        return SwaggerType(type=openapi.TYPE_STRING)


try:
    from djangorestframework_camel_case.parser import CamelCaseJSONParser
    from djangorestframework_camel_case.render import CamelCaseJSONRenderer
    from djangorestframework_camel_case.render import camelize
except ImportError:  # pragma: no cover
    class CamelCaseJSONFilter(FieldInspector):
        pass
else:
    def camelize_string(s):
        """Hack to force ``djangorestframework_camel_case`` to camelize a plain string."""
        return next(iter(camelize({s: ''})))

    def camelize_schema(schema_or_ref, components):
        """Recursively camelize property names for the given schema using ``djangorestframework_camel_case``."""
        schema = openapi.resolve_ref(schema_or_ref, components)
        if getattr(schema, 'properties', {}):
            schema.properties = OrderedDict(
                (camelize_string(key), camelize_schema(val, components))
                for key, val in schema.properties.items()
            )

            if getattr(schema, 'required', []):
                schema.required = [camelize_string(p) for p in schema.required]

        return schema_or_ref

    class CamelCaseJSONFilter(FieldInspector):
        def is_camel_case(self):
            return any(issubclass(parser, CamelCaseJSONParser) for parser in self.view.parser_classes) \
                   or any(issubclass(renderer, CamelCaseJSONRenderer) for renderer in self.view.renderer_classes)

        def process_result(self, result, method_name, obj, **kwargs):
            if isinstance(result, openapi.Schema.OR_REF) and self.is_camel_case():
                return camelize_schema(result, self.components)

            return result
