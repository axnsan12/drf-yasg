import collections
import functools
from collections import OrderedDict

import coreschema
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

    def get_operation(self, operation_keys, path, method):
        """Get an Operation for the given API endpoint (path, method).
        This includes query, body parameters and response schemas.

        :param tuple[str] operation_keys: an array of keys describing the hierarchical layout of this view in the API;
          e.g. ('snippets', 'list'), ('snippets', 'retrieve'), etc.
        :param str path: the view's path
        :param str method: HTTP request method
        :return openapi.Operation: the resulting Operation object
        """
        body = self.get_request_body_parameters(path, method)
        query = self.get_query_parameters(path, method)
        parameters = body + query

        parameters = [param for param in parameters if param is not None]
        description = self.get_description(path, method)
        responses = self.get_responses(path, method)
        return openapi.Operation(
            operation_id='_'.join(operation_keys),
            description=description,
            responses=responses,
            parameters=parameters,
            tags=[operation_keys[0]]
        )

    def get_request_body_parameters(self, path, method):
        """Return the request body parameters for this view.
        This is either:
          - a list with a single object Parameter with a Schema derived from the request serializer
          - a list of primitive Parameters parsed as form data

        :param str path: the view's path
        :param str method: HTTP request method
        :return list[Parameter]: a (potentially empty) list of openapi.Parameter in: either `body` or `formData`
        """
        # only PUT, PATCH or POST can have a request body
        if method not in ('PUT', 'PATCH', 'POST'):
            return []

        serializer = self.get_request_serializer(path, method)
        if serializer is None:
            return []

        encoding = self._sch.get_encoding(path, method)
        if 'form' in encoding:
            return [
                self.field_to_swagger(value, openapi.Parameter, name=key, in_=openapi.IN_FORM)
                for key, value
                in serializer.fields.items()
            ]
        else:
            schema = self.get_request_body_schema(path, method, serializer)
            return [openapi.Parameter(name='data', in_=openapi.IN_BODY, schema=schema)]

    def get_request_serializer(self, path, method):
        """Return the request serializer (used for parsing the request payload) for this endpoint.

        :param str path: the view's path
        :param str method: HTTP request method
        :return serializers.Serializer: the request serializer
        """
        # TODO: only GenericAPIViews have defined serializers;
        # APIViews and plain ViewSets will need some kind of manual treatment
        if not hasattr(self.view, 'get_serializer'):
            return None

        return self.view.get_serializer()

    def get_request_body_schema(self, path, method, serializer):
        """Return the Schema for a given request's body data. Only applies to PUT, PATCH and POST requests.

        :param str path: the view's path
        :param str method: HTTP request method
        :param serializer: the view's request serialzier
        :return openapi.Schema: the request body schema
        """
        return self.field_to_swagger(serializer, openapi.Schema)

    def get_responses(self, path, method):
        """Get the possible responses for this view as a swagger Responses object.

        :param str path: the view's path
        :param str method: HTTP request method
        :return Responses: the documented responses
        """
        response_serializers = self.get_response_serializers(path, method)
        return openapi.Responses(
            responses=self.get_response_schemas(path, method, response_serializers)
        )

    def get_response_serializers(self, path, method):
        """Return the response codes that this view is expected to return, and the serializer for each response body.
        The return value should be a dict where the keys are possible status codes, and values are either strings,
        `Serializer`s or `openapi.Response` objects.

        :param str path: the view's path
        :param str method: HTTP request method
        :return dict: the response serializers
        """
        if method.lower() == 'post':
            return {'201': ''}
        if method.lower() == 'delete':
            return {'204': ''}
        return {'200': ''}

    def get_response_schemas(self, path, method, response_serializers):
        """Return the `openapi.Response` objects calculated for this view.

        :param str path: the view's path
        :param str method: HTTP request method
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

    def get_query_parameters(self, path, method):
        """Return the query parameters accepted by this view.

        :param str path: the view's path
        :param str method: HTTP request method
        :return list[openapi.Parameter]: the query parameters
        """
        return self.get_filter_parameters(path, method) + self.get_pagination_parameters(path, method)

    def get_filter_parameters(self, path, method):
        """Return the parameters added to the view by its filter backends.

        :param str path: the view's path
        :param str method: HTTP request method
        :return list[openapi.Parameter]: the filter query parameters
        """
        return [
            self.coreapi_field_to_parameter(field)
            for field in self._sch.get_filter_fields(path, method)
        ]

    def get_pagination_parameters(self, path, method):
        """Return the parameters added to the view by its paginator.

        :param str path: the view's path
        :param str method: HTTP request method
        :return list[openapi.Parameter]: the pagination query parameters
        """
        return [
            self.coreapi_field_to_parameter(field)
            for field in self._sch.get_pagination_fields(path, method)
        ]

    def coreapi_field_to_parameter(self, field):
        """Convert an instance of `coreapi.Field` to a swagger Parameter object.

        :param coreapi.Field field: the coreapi field
        :return openapi.Parameter: the equivalent openapi primitive Parameter
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

    def get_description(self, path, method):
        """Return an operation description determined as appropriate from the view's method and class docstrings.

        :param str path: the view's path
        :param str method: HTTP request method
        :return str: the operation description
        """
        return self._sch.get_description(path, method)

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
                raise SwaggerGenerationError("parameter of type file is supported only in formData Parameter")
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
