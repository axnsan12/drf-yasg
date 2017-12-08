import functools
import inspect
from collections import OrderedDict

import coreschema
from django.core.validators import RegexValidator
from django.utils.encoding import force_text
from rest_framework import serializers
from rest_framework.request import is_form_media_type
from rest_framework.schemas import AutoSchema
from rest_framework.viewsets import GenericViewSet

from drf_swagger.errors import SwaggerGenerationError
from . import openapi
from .utils import no_body, is_list_view


def serializer_field_to_swagger(field, swagger_object_type, **kwargs):
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
        child_schema = serializer_field_to_swagger(field.child, ChildSwaggerType)
        return SwaggerType(
            type=openapi.TYPE_ARRAY,
            items=child_schema,
        )
    elif isinstance(field, serializers.Serializer):
        if swagger_object_type != openapi.Schema:
            raise SwaggerGenerationError("cannot instantiate nested serializer as "
                                         + swagger_object_type.__name__)
        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict(
                (key, serializer_field_to_swagger(value, ChildSwaggerType))
                for key, value
                in field.fields.items()
            )
        )
    elif isinstance(field, serializers.ManyRelatedField):
        child_schema = serializer_field_to_swagger(field.child_relation, ChildSwaggerType)
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
            raise SwaggerGenerationError("parameter of type file is supported only in formData Parameter")
        return SwaggerType(type=openapi.TYPE_FILE)
    elif isinstance(field, serializers.JSONField):
        return SwaggerType(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_BINARY if field.binary else None
        )
    elif isinstance(field, serializers.DictField) and swagger_object_type == openapi.Schema:
        child_schema = serializer_field_to_swagger(field.child, ChildSwaggerType)
        return SwaggerType(
            type=openapi.TYPE_OBJECT,
            additional_properties=child_schema
        )

    # TODO unhandled fields: TimeField DurationField HiddenField ModelField NullBooleanField?
    # TODO: return info about required/allowed empty

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


class SwaggerAutoSchema(object):
    def __init__(self, view, path, method, overrides):
        super(SwaggerAutoSchema, self).__init__()
        self._sch = AutoSchema()
        self.view = view
        self.path = path
        self.method = method
        self.overrides = overrides
        self._sch.view = view

    def get_operation(self, operation_keys):
        """Get an Operation for the given API endpoint (path, method).
        This includes query, body parameters and response schemas.

        :param tuple[str] operation_keys: an array of keys describing the hierarchical layout of this view in the API;
          e.g. ('snippets', 'list'), ('snippets', 'retrieve'), etc.
        :return openapi.Operation: the resulting Operation object
        """
        consumes = self.get_consumes()

        body = self.get_request_body_parameters(consumes)
        query = self.get_query_parameters()
        parameters = body + query

        parameters = [param for param in parameters if param is not None]
        parameters = self.add_manual_parameters(parameters)

        description = self.get_description()

        responses = self.get_responses()
        # manual_responses = self.overrides.get('responses', None) or {}
        return openapi.Operation(
            operation_id='_'.join(operation_keys),
            description=description,
            responses=responses,
            parameters=parameters,
            consumes=consumes,
            tags=[operation_keys[0]],
        )

    def get_request_body_parameters(self, consumes):
        """Return the request body parameters for this view.
        This is either:
          - a list with a single object Parameter with a Schema derived from the request serializer
          - a list of primitive Parameters parsed as form data

        :param list[str] consumes: a list of MIME types this request accepts as body
        :return list[Parameter]: a (potentially empty) list of openapi.Parameter in: either `body` or `formData`
        """
        # only PUT, PATCH or POST can have a request body
        if self.method not in ('PUT', 'PATCH', 'POST'):
            return []

        serializer = self.get_request_serializer()
        schema = None
        if serializer is None:
            return []

        if isinstance(serializer, openapi.Schema):
            schema = serializer

        if any(is_form_media_type(encoding) for encoding in consumes):
            if schema is not None:
                raise SwaggerGenerationError("form request body cannot be a Schema")
            return self.get_request_form_parameters(serializer)
        else:
            if schema is None:
                schema = self.get_request_body_schema(serializer)
            return [self.make_body_parameter(schema)]

    def get_request_serializer(self):
        """Return the request serializer (used for parsing the request payload) for this endpoint.

        :return serializers.Serializer: the request serializer
        """
        body_override = self.overrides.get('request_body', None)

        if body_override is not None:
            if body_override is no_body:
                return None
            if inspect.isclass(body_override):
                assert issubclass(body_override, serializers.Serializer)
                return body_override()
            return body_override
        else:
            if not hasattr(self.view, 'get_serializer'):
                return None
            return self.view.get_serializer()

    def get_request_form_parameters(self, serializer):
        """Given a Serializer, return a list of in: formData Parameters.

        :param serializer: the view's request serialzier
        """
        return [
            self.field_to_swagger(value, openapi.Parameter, name=key, in_=openapi.IN_FORM)
            for key, value
            in serializer.fields.items()
        ]

    def get_request_body_schema(self, serializer):
        """Return the Schema for a given request's body data. Only applies to PUT, PATCH and POST requests.

        :param serializer: the view's request serialzier
        :return openapi.Schema: the request body schema
        """
        return self.field_to_swagger(serializer, openapi.Schema)

    def make_body_parameter(self, schema):
        """Given a Schema object, create an in: body Parameter.

        :param openapi.Schema schema: the request body schema
        """
        return openapi.Parameter(name='data', in_=openapi.IN_BODY, schema=schema)

    def add_manual_parameters(self, parameters):
        """Add/replace parameters from the given list of automatically generated request parameters.

        :param list[openapi.Parameter] parameters: genereated parameters
        :return list[openapi.Parameter]: modified parameters
        """
        parameters = OrderedDict(((param.name, param.in_), param) for param in parameters)
        manual_parameters = self.overrides.get('manual_parameters', None) or []

        if any(param.in_ == openapi.IN_BODY for param in manual_parameters):
            raise SwaggerGenerationError("specify the body parameter as a Schema or Serializer in request_body")
        if any(param.in_ == openapi.IN_FORM for param in manual_parameters):
            if any(param.in_ == openapi.IN_BODY for param in parameters.values()):
                raise SwaggerGenerationError("cannot add form parameters when the request has a request schema; "
                                             "did you forget to set an appropriate parser class on the view?")

        parameters.update(((param.name, param.in_), param) for param in manual_parameters)
        return list(parameters.values())

    def get_responses(self):
        """Get the possible responses for this view as a swagger Responses object.

        :return Responses: the documented responses
        """
        response_serializers = self.get_response_serializers()
        return openapi.Responses(
            responses=self.get_response_schemas(response_serializers)
        )

    def get_response_serializers(self):
        """Return the response codes that this view is expected to return, and the serializer for each response body.
        The return value should be a dict where the keys are possible status codes, and values are either strings,
        `Serializer` or `openapi.Response` objects.

        :return dict: the response serializers
        """
        if self.method.lower() == 'post':
            return {'201': ''}
        if self.method.lower() == 'delete':
            return {'204': ''}
        return {'200': ''}

    def get_response_schemas(self, response_serializers):
        """Return the `openapi.Response` objects calculated for this view.

        :param dict response_serializers: result of get_response_serializers
        :return dict[str, openapi.Response]: a dictionary of status code to Response object
        """
        responses = {}
        for status, serializer in response_serializers.items():
            if isinstance(serializer, str):
                response = openapi.Response(
                    description=serializer
                )
            elif isinstance(serializer, openapi.Response):
                response = serializer
            else:
                response = openapi.Response(
                    description='',
                    schema=self.field_to_swagger(serializer, openapi.Schema)
                )

            responses[str(status)] = response

        return responses

    def get_query_parameters(self):
        """Return the query parameters accepted by this view."""
        return self.get_filter_parameters() + self.get_pagination_parameters()

    def should_filter(self):
        if getattr(self.view, 'filter_backends', None) is None:
            return False

        if self.method.lower() not in ["get", "put", "patch", "delete"]:
            return False

        if not isinstance(self.view, GenericViewSet):
            return True

        return is_list_view(self.path, self.method, self.view)

    def get_filter_parameters(self):
        """Return the parameters added to the view by its filter backends."""
        if not self.should_filter():
            return []

        fields = []
        for filter_backend in self.view.filter_backends:
            filter = filter_backend()
            if hasattr(filter, 'get_schema_fields'):
                fields += filter.get_schema_fields(self.view)
        return [self.coreapi_field_to_parameter(field) for field in fields]

    def should_page(self):
        if not hasattr(self.view, 'paginator'):
            return False

        return is_list_view(self.path, self.method, self.view)

    def get_pagination_parameters(self):
        """Return the parameters added to the view by its paginator."""
        if not self.should_page():
            return []

        paginator = self.view.paginator
        if not hasattr(paginator, 'get_schema_fields'):
            return []

        return [self.coreapi_field_to_parameter(field) for field in paginator.get_schema_fields(self.view)]

    def coreapi_field_to_parameter(self, field):
        """Convert an instance of `coreapi.Field` to a swagger Parameter object.

        :param coreapi.Field field: the coreapi field
        """
        location_to_in = {
            'query': openapi.IN_QUERY,
            'path': openapi.IN_PATH,
            'form': openapi.IN_FORM,
            'body': openapi.IN_FORM,
        }
        coreapi_types = {
            coreschema.Integer: openapi.TYPE_INTEGER,
            coreschema.Number: openapi.TYPE_NUMBER,
            coreschema.String: openapi.TYPE_STRING,
            coreschema.Boolean: openapi.TYPE_BOOLEAN,
        }
        return openapi.Parameter(
            name=field.name,
            in_=location_to_in[field.location],
            type=coreapi_types.get(field.schema.__class__, openapi.TYPE_STRING),
            required=field.required,
            description=field.schema.description,
        )

    def get_description(self):
        """Return an operation description determined as appropriate from the view's method and class docstrings.

        :return str: the operation description
        """
        description = self.overrides.get('operation_description', None)
        if description is None:
            description = self._sch.get_description(self.path, self.method)
        return description

    def get_consumes(self):
        """Return the MIME types this endpoint can consume."""
        media_types = [parser.media_type for parser in getattr(self.view, 'parser_classes', [])]
        if all(is_form_media_type(encoding) for encoding in media_types):
            return media_types
        return media_types[:1]

    def field_to_swagger(self, field, swagger_object_type, **kwargs):
        return serializer_field_to_swagger(field, swagger_object_type, **kwargs)
