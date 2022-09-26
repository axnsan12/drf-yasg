import datetime
import inspect
import logging
import operator
import typing
import uuid
import pkg_resources
from packaging import version
from collections import OrderedDict
from decimal import Decimal
from inspect import signature as inspect_signature

from django.core import validators
from django.db import models
from rest_framework import serializers
from rest_framework.settings import api_settings as rest_framework_settings

from .. import openapi
from ..errors import SwaggerGenerationError
from ..utils import (
    decimal_as_float, field_value_to_representation, filter_none, get_serializer_class, get_serializer_ref_name
)
from .base import FieldInspector, NotHandled, SerializerInspector, call_view_method


drf_version = pkg_resources.get_distribution("djangorestframework").version

logger = logging.getLogger(__name__)


class InlineSerializerInspector(SerializerInspector):
    """Provides serializer conversions using :meth:`.FieldInspector.field_to_swagger_object`."""

    #: whether to output :class:`.Schema` definitions inline or into the ``definitions`` section
    use_definitions = False

    def get_schema(self, serializer):
        return self.probe_field_inspectors(serializer, openapi.Schema, self.use_definitions)

    def add_manual_parameters(self, serializer, parameters):
        """Add/replace parameters from the given list of automatically generated request parameters. This method
        is called only when the serializer is converted into a list of parameters for use in a form data request.

        :param serializer: serializer instance
        :param list[openapi.Parameter] parameters: generated parameters
        :return: modified parameters
        :rtype: list[openapi.Parameter]
        """
        return parameters

    def get_request_parameters(self, serializer, in_):
        fields = getattr(serializer, 'fields', {})
        parameters = [
            self.probe_field_inspectors(
                value, openapi.Parameter, self.use_definitions,
                name=self.get_parameter_name(key), in_=in_
            )
            for key, value
            in fields.items()
            if not getattr(value, 'read_only', False)
        ]

        return self.add_manual_parameters(serializer, parameters)

    def get_property_name(self, field_name):
        return field_name

    def get_parameter_name(self, field_name):
        return field_name

    def get_serializer_ref_name(self, serializer):
        return get_serializer_ref_name(serializer)

    def _has_ref_name(self, serializer):
        serializer_meta = getattr(serializer, 'Meta', None)
        return hasattr(serializer_meta, 'ref_name')

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, (serializers.ListSerializer, serializers.ListField)):
            child_schema = self.probe_field_inspectors(field.child, ChildSwaggerType, use_references)
            limits = find_limits(field) or {}
            return SwaggerType(
                type=openapi.TYPE_ARRAY,
                items=child_schema,
                **limits
            )
        elif isinstance(field, serializers.Serializer):
            if swagger_object_type != openapi.Schema:
                raise SwaggerGenerationError("cannot instantiate nested serializer as " + swagger_object_type.__name__)

            ref_name = self.get_serializer_ref_name(field)

            def make_schema_definition(serializer=field):
                properties = OrderedDict()
                required = []
                for property_name, child in serializer.fields.items():
                    property_name = self.get_property_name(property_name)
                    prop_kwargs = {
                        'read_only': bool(child.read_only) or None
                    }
                    prop_kwargs = filter_none(prop_kwargs)

                    child_schema = self.probe_field_inspectors(
                        child, ChildSwaggerType, use_references, **prop_kwargs
                    )
                    properties[property_name] = child_schema

                    if child.required and not getattr(child_schema, 'read_only', False):
                        required.append(property_name)

                result = SwaggerType(
                    # the title is derived from the field name and is better to
                    # be omitted from models
                    use_field_title=False,
                    type=openapi.TYPE_OBJECT,
                    properties=properties,
                    required=required or None,
                )

                setattr(result, '_NP_serializer', get_serializer_class(serializer))
                return result

            if not ref_name or not use_references:
                return make_schema_definition()

            definitions = self.components.with_scope(openapi.SCHEMA_DEFINITIONS)
            actual_schema = definitions.setdefault(ref_name, make_schema_definition)
            actual_schema._remove_read_only()

            actual_serializer = getattr(actual_schema, '_NP_serializer', None)
            this_serializer = get_serializer_class(field)
            if actual_serializer and actual_serializer != this_serializer:  # pragma: no cover
                explicit_refs = self._has_ref_name(actual_serializer) and self._has_ref_name(this_serializer)
                if not explicit_refs:
                    raise SwaggerGenerationError(
                        "Schema for %s would override distinct serializer %s because they implicitly share the same "
                        "ref_name; explicitly set the ref_name attribute on both serializers' Meta classes"
                        % (actual_serializer, this_serializer))

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


def get_queryset_from_view(view, serializer=None):
    """Try to get the queryset of the given view

    :param view: the view instance or class
    :param serializer: if given, will check that the view's get_serializer_class return matches this serializer
    :return: queryset or ``None``
    """
    try:
        queryset = call_view_method(view, 'get_queryset', 'queryset')

        if queryset is not None and serializer is not None:
            # make sure the view is actually using *this* serializer
            assert type(serializer) == call_view_method(view, 'get_serializer_class', 'serializer_class')

        return queryset
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
        descriptor = getattr(model, source)
        try:
            return descriptor.rel.related_model
        except Exception:
            return descriptor.field.remote_field.model
    except Exception:  # pragma: no cover
        return None


class RelatedFieldInspector(FieldInspector):
    """Provides conversions for ``RelatedField``\\ s."""

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
                parent_serializer = get_parent_serializer(field)

                serializer_meta = getattr(parent_serializer, 'Meta', None)
                this_model = getattr(serializer_meta, 'model', None)
                if not this_model:
                    view_queryset = get_queryset_from_view(self.view, parent_serializer)
                    this_model = getattr(view_queryset, 'model', None)

                source = getattr(field, 'source', '') or field.field_name
                if not source and isinstance(field.parent, serializers.ManyRelatedField):
                    source = field.parent.field_name

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
            if isinstance(validator, validators.URLValidator) or validator == validators.validate_ipv4_address:
                # skip the default url and IP regexes because they are complex and unhelpful
                # validate_ipv4_address is a RegexValidator instance in Django 1.11
                continue
            if regex_validator is not None:
                # bail if multiple validators are found - no obvious way to choose
                return None  # pragma: no cover
            regex_validator = validator

    # regex_validator.regex should be a compiled re object...
    try:
        pattern = getattr(getattr(regex_validator, 'regex', None), 'pattern', None)
    except Exception:  # pragma: no cover
        logger.warning('failed to compile regex validator of ' + str(regex_field), exc_info=True)
        return None

    if pattern:
        # attempt some basic cleanup to remove regex constructs not supported by JavaScript
        #  -- swagger uses javascript-style regexes - see https://github.com/swagger-api/swagger-editor/issues/1601
        if pattern.endswith('\\Z') or pattern.endswith('\\z'):
            pattern = pattern[:-2] + '$'

    return pattern


numeric_fields = (serializers.IntegerField, serializers.FloatField, serializers.DecimalField)
limit_validators = [
    # minimum and maximum apply to numbers
    (validators.MinValueValidator, numeric_fields, 'minimum', operator.__gt__),
    (validators.MaxValueValidator, numeric_fields, 'maximum', operator.__lt__),

    # minLength and maxLength apply to strings
    (validators.MinLengthValidator, serializers.CharField, 'min_length', operator.__gt__),
    (validators.MaxLengthValidator, serializers.CharField, 'max_length', operator.__lt__),

    # minItems and maxItems apply to lists
    (validators.MinLengthValidator, (serializers.ListField, serializers.ListSerializer), 'min_items', operator.__gt__),
    (validators.MaxLengthValidator, (serializers.ListField, serializers.ListSerializer), 'max_items', operator.__lt__),
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

    if isinstance(field, serializers.DecimalField) and not decimal_as_float(field):
        return limits

    for validator in field.validators:
        if not hasattr(validator, 'limit_value'):
            continue

        limit_value = validator.limit_value
        if isinstance(limit_value, Decimal) and decimal_as_float(field):
            limit_value = float(limit_value)

        for validator_class, attr, improves in applicable_limits:
            if isinstance(validator, validator_class):
                if attr not in limits or improves(limit_value, limits[attr]):
                    limits[attr] = limit_value

    if hasattr(field, "allow_blank") and not field.allow_blank:
        if limits.get('min_length', 0) < 1:
            limits['min_length'] = 1

    return OrderedDict(sorted(limits.items()))


def decimal_field_type(field):
    return openapi.TYPE_NUMBER if decimal_as_float(field) else openapi.TYPE_STRING


model_field_to_basic_type = [
    (models.AutoField, (openapi.TYPE_INTEGER, None)),
    (models.BinaryField, (openapi.TYPE_STRING, openapi.FORMAT_BINARY)),
    (models.BooleanField, (openapi.TYPE_BOOLEAN, None)),
    (models.DateTimeField, (openapi.TYPE_STRING, openapi.FORMAT_DATETIME)),
    (models.DateField, (openapi.TYPE_STRING, openapi.FORMAT_DATE)),
    (models.DecimalField, (decimal_field_type, openapi.FORMAT_DECIMAL)),
    (models.DurationField, (openapi.TYPE_STRING, None)),
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
    (serializers.BooleanField, (openapi.TYPE_BOOLEAN, None)),
    (serializers.IntegerField, (openapi.TYPE_INTEGER, None)),
    (serializers.FloatField, (openapi.TYPE_NUMBER, None)),
    (serializers.DecimalField, (decimal_field_type, openapi.FORMAT_DECIMAL)),
    (serializers.DurationField, (openapi.TYPE_STRING, None)),
    (serializers.DateField, (openapi.TYPE_STRING, openapi.FORMAT_DATE)),
    (serializers.DateTimeField, (openapi.TYPE_STRING, openapi.FORMAT_DATETIME)),
    (serializers.ModelField, (openapi.TYPE_STRING, None)),
]

if version.parse(drf_version) < version.parse("3.14.0"):
    model_field_to_basic_type.append(
        (models.NullBooleanField, (openapi.TYPE_BOOLEAN, None))
    )

    serializer_field_to_basic_type.append(
        (serializers.NullBooleanField, (openapi.TYPE_BOOLEAN, None)),
    )

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
            if callable(swagger_type):
                swagger_type = swagger_type(field)
            if callable(format):
                format = format(field)
            break
    else:  # pragma: no cover
        return None

    pattern = None
    if swagger_type == openapi.TYPE_STRING:
        pattern = find_regex(field)

    limits = find_limits(field)

    result = OrderedDict([
        ('type', swagger_type),
        ('format', format),
        ('pattern', pattern)
    ])
    result.update(limits)
    result = filter_none(result)
    return result


def decimal_return_type():
    return openapi.TYPE_STRING if rest_framework_settings.COERCE_DECIMAL_TO_STRING else openapi.TYPE_NUMBER


def get_origin_type(hint_class):
    return getattr(hint_class, '__origin__', None) or hint_class


def hint_class_issubclass(hint_class, check_class):
    origin_type = get_origin_type(hint_class)
    return inspect.isclass(origin_type) and issubclass(origin_type, check_class)


hinting_type_info = [
    (bool, (openapi.TYPE_BOOLEAN, None)),
    (int, (openapi.TYPE_INTEGER, None)),
    (str, (openapi.TYPE_STRING, None)),
    (float, (openapi.TYPE_NUMBER, None)),
    (dict, (openapi.TYPE_OBJECT, None)),
    (Decimal, (decimal_return_type, openapi.FORMAT_DECIMAL)),
    (uuid.UUID, (openapi.TYPE_STRING, openapi.FORMAT_UUID)),
    (datetime.datetime, (openapi.TYPE_STRING, openapi.FORMAT_DATETIME)),
    (datetime.date, (openapi.TYPE_STRING, openapi.FORMAT_DATE)),
]


if hasattr(typing, 'get_args'):
    # python >=3.8
    typing_get_args = typing.get_args
else:
    # python <3.8
    def typing_get_args(tp):
        return getattr(tp, '__args__', ())


def inspect_collection_hint_class(hint_class):
    args = typing_get_args(hint_class)
    child_class = args[0] if args else str
    child_type_info = get_basic_type_info_from_hint(child_class) or {'type': openapi.TYPE_STRING}

    return OrderedDict([
        ('type', openapi.TYPE_ARRAY),
        ('items', openapi.Items(**child_type_info)),
    ])


hinting_type_info.append(((typing.Sequence, typing.AbstractSet), inspect_collection_hint_class))


def _get_union_types(hint_class):
    origin_type = get_origin_type(hint_class)
    if origin_type is typing.Union:
        return hint_class.__args__


def get_basic_type_info_from_hint(hint_class):
    """Given a class (eg from a SerializerMethodField's return type hint,
    return its basic type information - ``type``, ``format``, ``pattern``,
    and any applicable min/max limit values.

    :param hint_class: the class
    :return: the extracted attributes as a dictionary, or ``None`` if the field type is not known
    :rtype: OrderedDict
    """
    union_types = _get_union_types(hint_class)

    if union_types:
        # Optional is implemented as Union[T, None]
        if len(union_types) == 2 and isinstance(None, union_types[1]):
            result = get_basic_type_info_from_hint(union_types[0])
            if result:
                result['x-nullable'] = True

            return result

        return None

    for check_class, info in hinting_type_info:
        if hint_class_issubclass(hint_class, check_class):
            if callable(info):
                return info(hint_class)

            swagger_type, format = info
            if callable(swagger_type):
                swagger_type = swagger_type()

            return OrderedDict([
                ('type', swagger_type),
                ('format', format),
            ])

    return None


class SerializerMethodFieldInspector(FieldInspector):
    """Provides conversion for SerializerMethodField, optionally using information from the swagger_serializer_method
    decorator.
    """

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        if not isinstance(field, serializers.SerializerMethodField):
            return NotHandled

        method = getattr(field.parent, field.method_name, None)
        if method is None:
            return NotHandled

        # attribute added by the swagger_serializer_method decorator
        serializer = getattr(method, "_swagger_serializer", None)

        if serializer:
            # in order of preference for description, use:
            # 1) field.help_text from SerializerMethodField(help_text)
            # 2) serializer.help_text from swagger_serializer_method(serializer)
            # 3) method's docstring
            description = field.help_text
            if description is None:
                description = getattr(serializer, 'help_text', None)
            if description is None:
                description = method.__doc__

            label = field.label
            if label is None:
                label = getattr(serializer, 'label', None)

            if inspect.isclass(serializer):
                serializer_kwargs = {
                    "help_text": description,
                    "label": label,
                    "read_only": True,
                }

                serializer = method._swagger_serializer(**serializer_kwargs)
            else:
                serializer.help_text = description
                serializer.label = label
                serializer.read_only = True

            return self.probe_field_inspectors(serializer, swagger_object_type, use_references, read_only=True)
        else:
            # look for Python 3.5+ style type hinting of the return value
            hint_class = inspect_signature(method).return_annotation

            if not inspect.isclass(hint_class) and hasattr(hint_class, '__args__'):
                hint_class = hint_class.__args__[0]
            if inspect.isclass(hint_class) and not issubclass(hint_class, inspect._empty):
                type_info = get_basic_type_info_from_hint(hint_class)

                if type_info is not None:
                    SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type,
                                                                            use_references, **kwargs)
                    return SwaggerType(**type_info)

        return NotHandled


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

        if isinstance(field, serializers.ChoiceField):
            enum_type = openapi.TYPE_STRING
            enum_values = []
            for choice in field.choices.keys():
                if isinstance(field, serializers.MultipleChoiceField):
                    choice = field_value_to_representation(field, [choice])[0]
                else:
                    choice = field_value_to_representation(field, choice)

                enum_values.append(choice)

            # for ModelSerializer, try to infer the type from the associated model field
            serializer = get_parent_serializer(field)
            if isinstance(serializer, serializers.ModelSerializer):
                model = getattr(getattr(serializer, 'Meta'), 'model')
                # Use the parent source for nested fields
                model_field = get_model_field(model, field.source or field.parent.source)
                # If the field has a base_field its type must be used
                if getattr(model_field, "base_field", None):
                    model_field = model_field.base_field
                if model_field:
                    model_type = get_basic_type_info(model_field)
                    if model_type:
                        enum_type = model_type.get('type', enum_type)
            else:
                # Try to infer field type based on enum values
                enum_value_types = {type(v) for v in enum_values}
                if len(enum_value_types) == 1:
                    values_type = get_basic_type_info_from_hint(next(iter(enum_value_types)))
                    if values_type:
                        enum_type = values_type.get('type', enum_type)

            if isinstance(field, serializers.MultipleChoiceField):
                result = SwaggerType(
                    type=openapi.TYPE_ARRAY,
                    items=ChildSwaggerType(
                        type=enum_type,
                        enum=enum_values
                    )
                )
                if swagger_object_type == openapi.Parameter:
                    if result['in'] in (openapi.IN_FORM, openapi.IN_QUERY):
                        result.collection_format = 'multi'
            else:
                result = SwaggerType(type=enum_type, enum=enum_values)

            return result

        return NotHandled


class FileFieldInspector(FieldInspector):
    """Provides conversions for ``FileField``\\ s."""

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


class HiddenFieldInspector(FieldInspector):
    """Hide ``HiddenField``."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        if isinstance(field, serializers.HiddenField):
            return None

        return NotHandled


class JSONFieldInspector(FieldInspector):
    """Provides conversion for ``JSONField``."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)

        if isinstance(field, serializers.JSONField) and swagger_object_type == openapi.Schema:
            return SwaggerType(type=openapi.TYPE_OBJECT)

        return NotHandled


class StringDefaultFieldInspector(FieldInspector):
    """For otherwise unhandled fields, return them as plain :data:`.TYPE_STRING` objects."""

    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):  # pragma: no cover
        # TODO unhandled fields: TimeField
        SwaggerType, ChildSwaggerType = self._get_partial_types(field, swagger_object_type, use_references, **kwargs)
        return SwaggerType(type=openapi.TYPE_STRING)


try:
    from djangorestframework_camel_case.parser import CamelCaseJSONParser
    from djangorestframework_camel_case.render import CamelCaseJSONRenderer, camelize
except ImportError:  # pragma: no cover
    CamelCaseJSONParser = CamelCaseJSONRenderer = None

    def camelize(data):
        return data


class CamelCaseJSONFilter(FieldInspector):
    """Converts property names to camelCase if ``djangorestframework_camel_case`` is used."""

    def camelize_string(self, s):
        """Hack to force ``djangorestframework_camel_case`` to camelize a plain string.

        :param str s: the string
        :return: camelized string
        :rtype: str
        """
        return next(iter(camelize({s: ''})))

    def camelize_schema(self, schema):
        """Recursively camelize property names for the given schema using ``djangorestframework_camel_case``.
        The target schema object must be modified in-place.

        :param openapi.Schema schema: the :class:`.Schema` object
        """
        if getattr(schema, 'properties', {}):
            schema.properties = OrderedDict(
                (self.camelize_string(key), self.camelize_schema(openapi.resolve_ref(val, self.components)) or val)
                for key, val in schema.properties.items()
            )

            if getattr(schema, 'required', []):
                schema.required = [self.camelize_string(p) for p in schema.required]

    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(result, openapi.Schema.OR_REF) and self.is_camel_case():
            schema = openapi.resolve_ref(result, self.components)
            self.camelize_schema(schema)

        return result

    if CamelCaseJSONParser and CamelCaseJSONRenderer:
        def is_camel_case(self):
            return (
                any(issubclass(parser, CamelCaseJSONParser) for parser in self.get_parser_classes()) or
                any(issubclass(renderer, CamelCaseJSONRenderer) for renderer in self.get_renderer_classes())
            )
    else:
        def is_camel_case(self):
            return False


try:
    from rest_framework_recursive.fields import RecursiveField
except ImportError:  # pragma: no cover
    class RecursiveFieldInspector(FieldInspector):
        """Provides conversion for RecursiveField (https://github.com/heywbj/django-rest-framework-recursive)"""
        pass
else:
    class RecursiveFieldInspector(FieldInspector):
        """Provides conversion for RecursiveField (https://github.com/heywbj/django-rest-framework-recursive)"""

        def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
            if isinstance(field, RecursiveField) and swagger_object_type == openapi.Schema:
                assert use_references is True, "Can not create schema for RecursiveField when use_references is False"

                proxied = field.proxied
                if isinstance(field.proxied, serializers.ListSerializer):
                    proxied = proxied.child

                ref_name = get_serializer_ref_name(proxied)
                assert ref_name is not None, "Can't create RecursiveField schema for inline " + str(type(proxied))

                definitions = self.components.with_scope(openapi.SCHEMA_DEFINITIONS)

                ref = openapi.SchemaRef(definitions, ref_name, ignore_unresolved=True)
                if isinstance(field.proxied, serializers.ListSerializer):
                    ref = openapi.Items(type=openapi.TYPE_ARRAY, items=ref)

                return ref

            return NotHandled

