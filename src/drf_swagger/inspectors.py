import inspect
from collections import OrderedDict

import coreschema
from rest_framework import serializers, status
from rest_framework.request import is_form_media_type
from rest_framework.schemas import AutoSchema
from rest_framework.status import is_success
from rest_framework.viewsets import GenericViewSet

from drf_swagger.errors import SwaggerGenerationError
from drf_swagger.utils import serializer_field_to_swagger
from . import openapi
from .utils import no_body, is_list_view


def force_serializer_instance(serializer):
    if inspect.isclass(serializer):
        assert issubclass(serializer, serializers.BaseSerializer), "Serializer class or instance required"
        return serializer()

    assert isinstance(serializer, serializers.BaseSerializer), "Serializer class or instance required"
    return serializer


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
            if isinstance(body_override, openapi.Schema):
                return body_override
            return force_serializer_instance(body_override)
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
        return openapi.Parameter(name='data', in_=openapi.IN_BODY, required=True, schema=schema)

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

    def get_paged_response_schema(self, response_schema):
        """Add appropriate paging fields to a response Schema.

        :param openapi.Schema response_schema: the response schema that must be paged.
        """
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                'next': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                'previous': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                'results': response_schema,
            },
            required=['count', 'results']
        )

        return paged_schema

    def get_default_responses(self):
        method = self.method.lower()

        default_status = status.HTTP_200_OK
        default_schema = ''
        if method == 'post':
            default_status = status.HTTP_201_CREATED
            default_schema = self.get_request_serializer()
        elif method == 'delete':
            default_status = status.HTTP_204_NO_CONTENT
        elif method in ('get', 'put', 'patch'):
            default_schema = self.get_request_serializer()

        default_schema = default_schema or ''
        if default_schema:
            if not isinstance(default_schema, openapi.Schema):
                default_schema = self.field_to_swagger(default_schema, openapi.Schema)
            if is_list_view(self.path, self.method, self.view) and self.method.lower() == 'get':
                default_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=default_schema)
            if self.should_page():
                default_schema = self.get_paged_response_schema(default_schema)

        return {str(default_status): default_schema}

    def get_response_serializers(self):
        """Return the response codes that this view is expected to return, and the serializer for each response body.
        The return value should be a dict where the keys are possible status codes, and values are either strings,
        `Serializer` or `openapi.Response` objects.

        :return dict: the response serializers
        """
        manual_responses = self.overrides.get('responses', None) or {}
        manual_responses = OrderedDict((str(sc), resp) for sc, resp in manual_responses.items())

        responses = {}
        if not any(is_success(int(sc)) for sc in manual_responses if sc != 'default'):
            responses = self.get_default_responses()

        responses.update((str(sc), resp) for sc, resp in manual_responses.items())
        return responses

    def get_response_schemas(self, response_serializers):
        """Return the `openapi.Response` objects calculated for this view.

        :param dict response_serializers: result of get_response_serializers
        :return dict[str, openapi.Response]: a dictionary of status code to Response object
        """
        responses = {}
        for sc, serializer in response_serializers.items():
            if isinstance(serializer, str):
                response = openapi.Response(
                    description=serializer
                )
            elif isinstance(serializer, openapi.Response):
                response = serializer
                if not isinstance(response.schema, openapi.Schema):
                    serializer = force_serializer_instance(response.schema)
                    response.schema = self.field_to_swagger(serializer, openapi.Schema)
            elif isinstance(serializer, openapi.Schema):
                response = openapi.Response(
                    description='',
                    schema=serializer,
                )
            else:
                serializer = force_serializer_instance(serializer)
                response = openapi.Response(
                    description='',
                    schema=self.field_to_swagger(serializer, openapi.Schema),
                )

            responses[str(sc)] = response

        return responses

    def get_query_parameters(self):
        """Return the query parameters accepted by this view."""
        return self.get_filter_parameters() + self.get_pagination_parameters()

    def should_filter(self):
        if not getattr(self.view, 'filter_backends', None):
            return False

        if self.method.lower() not in ["get", "delete"]:
            return False

        if not isinstance(self.view, GenericViewSet):
            return True

        return is_list_view(self.path, self.method, self.view)

    def get_filter_backend_parameters(self, filter_backend):
        """Get the filter parameters for a single filter backend **instance**.

        :param BaseFilterBackend filter_backend: the filter backend
        """
        fields = []
        if hasattr(filter_backend, 'get_schema_fields'):
            fields = filter_backend.get_schema_fields(self.view)
        return [self.coreapi_field_to_parameter(field) for field in fields]

    def get_filter_parameters(self):
        """Return the parameters added to the view by its filter backends."""
        if not self.should_filter():
            return []

        fields = []
        for filter_backend in self.view.filter_backends:
            fields += self.get_filter_backend_parameters(filter_backend())

        return fields

    def should_page(self):
        if not hasattr(self.view, 'paginator'):
            return False

        if self.view.paginator is None:
            return False

        if self.method.lower() != 'get':
            return False

        return is_list_view(self.path, self.method, self.view)

    def get_paginator_parameters(self, paginator):
        """Get the pagination parameters for a single paginator **instance**.

        :param BasePagination paginator: the paginator
        """
        fields = []
        if hasattr(paginator, 'get_schema_fields'):
            fields = paginator.get_schema_fields(self.view)

        return [self.coreapi_field_to_parameter(field) for field in fields]

    def get_pagination_parameters(self):
        """Return the parameters added to the view by its paginator."""
        if not self.should_page():
            return []

        return self.get_paginator_parameters(self.view.paginator)

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
