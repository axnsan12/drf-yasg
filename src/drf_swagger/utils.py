from collections import OrderedDict

from django.core.validators import RegexValidator
from django.utils.encoding import force_text
from rest_framework import serializers
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin

from . import openapi
from .errors import SwaggerGenerationError

no_body = object()


def is_list_view(path, method, view):
    """Return True if the given path/method appears to represent a list view (as opposed to a detail/instance view)."""
    # for ViewSets, it could be the default 'list' view, or a list_route
    action = getattr(view, 'action', '')
    method = getattr(view, action, None)
    detail = getattr(method, 'detail', None)
    suffix = getattr(view, 'suffix', None)
    if action == 'list' or detail is False or suffix == 'List':
        return True

    if action in ('retrieve', 'update', 'partial_update', 'destroy') or detail is True or suffix == 'Instance':
        # a detail_route is surely not a list route
        return False

    # for APIView, if it's a detail view it can't also be a list view
    if isinstance(view, (RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin)):
        return False

    # if the last component in the path is parameterized it's probably not a list view
    path_components = path.strip('/').split('/')
    if path_components and '{' in path_components[-1]:
        return False

    # otherwise assume it's a list route
    return True


def swagger_auto_schema(method=None, methods=None, auto_schema=None, request_body=None, manual_parameters=None,
                        operation_description=None, responses=None):
    def decorator(view_method):
        data = {
            'auto_schema': auto_schema,
            'request_body': request_body,
            'manual_parameters': manual_parameters,
            'operation_description': operation_description,
            'responses': responses,
        }
        data = {k: v for k, v in data.items() if v is not None}

        bind_to_methods = getattr(view_method, 'bind_to_methods', [])
        # if the method is actually a function based view
        view_cls = getattr(view_method, 'cls', None)
        http_method_names = getattr(view_cls, 'http_method_names', [])
        if bind_to_methods or http_method_names:
            # detail_route, list_route or api_view
            assert bool(http_method_names) != bool(bind_to_methods), "this should never happen"
            available_methods = http_method_names + bind_to_methods
            existing_data = getattr(view_method, 'swagger_auto_schema', {})

            if http_method_names:
                _route = "api_view"
            else:
                _route = "detail_route" if view_method.detail else "list_route"

            _methods = methods
            if len(available_methods) > 1:
                assert methods or method, \
                    "on multi-method %s, you must specify swagger_auto_schema on a per-method basis " \
                    "using one of the `method` or `methods` arguments" % _route
                assert bool(methods) != bool(method), "specify either method or methods"
                if method:
                    _methods = [method.lower()]
                else:
                    _methods = [mth.lower() for mth in methods]
                assert not isinstance(_methods, str), "`methods` expects to receive; use `method` for a single arg"
                assert not any(mth in existing_data for mth in _methods), "method defined multiple times"
                assert all(mth in available_methods for mth in _methods), "method not bound to %s" % _route

                existing_data.update((mth.lower(), data) for mth in _methods)
            else:
                existing_data[available_methods[0]] = data
            view_method.swagger_auto_schema = existing_data
        else:
            assert methods is None, \
                "the methods argument should only be specified when decorating a detail_route or list_route; you " \
                "should also ensure that you put the swagger_auto_schema decorator AFTER (above) the _route decorator"
            view_method.swagger_auto_schema = data

        return view_method

    return decorator


def serializer_field_to_swagger(field, swagger_object_type, definitions=None, **kwargs):
    """Convert a drf Serializer or Field instance into a Swagger object.

    :param rest_framework.serializers.Field field: the source field
    :param type[openapi.SwaggerDict] swagger_object_type: should be one of Schema, Parameter, Items
    :param drf_swagger.openapi.ReferenceResolver definitions: used to serialize Schemas by reference
    :param kwargs: extra attributes for constructing the object;
       if swagger_object_type is Parameter, `name` and `in_` should be provided
    :return: the swagger object
    :rtype: openapi.Parameter, openapi.Items, openapi.Schema
    """
    assert swagger_object_type in (openapi.Schema, openapi.Parameter, openapi.Items)
    assert not isinstance(field, openapi.SwaggerDict), "passed field is already a SwaggerDict object"
    title = force_text(field.label) if field.label else None
    title = title if swagger_object_type == openapi.Schema else None  # only Schema has title
    title = None
    description = force_text(field.help_text) if field.help_text else None
    description = description if swagger_object_type != openapi.Items else None  # Items has no description either

    def SwaggerType(**instance_kwargs):
        if swagger_object_type == openapi.Parameter:
            instance_kwargs['required'] = field.required
        instance_kwargs.update(kwargs)
        return swagger_object_type(title=title, description=description, **instance_kwargs)

    # arrays in Schema have Schema elements, arrays in Parameter and Items have Items elements
    ChildSwaggerType = openapi.Schema if swagger_object_type == openapi.Schema else openapi.Items

    # ------ NESTED
    if isinstance(field, (serializers.ListSerializer, serializers.ListField)):
        child_schema = serializer_field_to_swagger(field.child, ChildSwaggerType, definitions)
        return SwaggerType(
            type=openapi.TYPE_ARRAY,
            items=child_schema,
        )
    elif isinstance(field, serializers.Serializer):
        if swagger_object_type != openapi.Schema:
            raise SwaggerGenerationError("cannot instantiate nested serializer as " + swagger_object_type.__name__)
        assert definitions is not None, "ReferenceResolver required when instantiating Schema"

        serializer = field
        if hasattr(serializer, '__ref_name__'):
            ref_name = serializer.__ref_name__
        else:
            ref_name = type(serializer).__name__
            if ref_name.endswith('Serializer'):
                ref_name = ref_name[:-len('Serializer')]

        def make_schema_definition():
            properties = OrderedDict()
            required = []
            for key, value in serializer.fields.items():
                properties[key] = serializer_field_to_swagger(value, ChildSwaggerType, definitions)
                if value.read_only:
                    properties[key].read_only = value.read_only
                if value.required:
                    required.append(key)

            return SwaggerType(
                type=openapi.TYPE_OBJECT,
                properties=properties,
                required=required or None,
            )

        if not ref_name:
            return make_schema_definition()

        definitions.setdefault(ref_name, make_schema_definition)
        return openapi.SchemaRef(definitions, ref_name)
    elif isinstance(field, serializers.ManyRelatedField):
        child_schema = serializer_field_to_swagger(field.child_relation, ChildSwaggerType, definitions)
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
        if swagger_object_type != openapi.Parameter:
            raise SwaggerGenerationError("parameter of type file is supported only in formData Parameter")
        return SwaggerType(type=openapi.TYPE_FILE)
    elif isinstance(field, serializers.JSONField):
        return SwaggerType(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_BINARY if field.binary else None
        )
    elif isinstance(field, serializers.DictField) and swagger_object_type == openapi.Schema:
        child_schema = serializer_field_to_swagger(field.child, ChildSwaggerType, definitions)
        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            additional_properties=child_schema
        )

    # TODO unhandled fields: TimeField DurationField HiddenField ModelField NullBooleanField?

    # everything else gets string by default
    return SwaggerType(type=openapi.TYPE_STRING)


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
