import inspect
from collections import OrderedDict

import coreschema
from rest_framework import serializers, status
from rest_framework.request import is_form_media_type
from rest_framework.schemas import AutoSchema
from rest_framework.status import is_success
from rest_framework.viewsets import GenericViewSet

from . import openapi
from .errors import SwaggerGenerationError
from .utils import serializer_field_to_swagger, no_body, is_list_view, param_list_to_odict


def force_serializer_instance(serializer):
    """Force `serializer` into a ``Serializer`` instance. If it is not a ``Serializer`` class or instance, raises
    an assertion error.

    :param serializer: serializer class or instance
    :return: serializer instance
    """
    if inspect.isclass(serializer):
        assert issubclass(serializer, serializers.BaseSerializer), "Serializer required, not %s" % serializer.__name__
        return serializer()

    assert isinstance(serializer, serializers.BaseSerializer), \
        "Serializer class or instance required, not %s" % type(serializer).__name__
    return serializer


class SwaggerAutoSchema(object):
    body_methods = ('PUT', 'PATCH', 'POST')  #: methods allowed to have a request body

    def __init__(self, view, path, method, overrides, components):
        """Inspector class responsible for providing :class:`.Operation` definitions given a

        :param view: the view associated with this endpoint
        :param str path: the path component of the operation URL
        :param str method: the http method of the operation
        :param dict overrides: manual overrides as passed to :func:`@swagger_auto_schema <.swagger_auto_schema>`
        :param openapi.ReferenceResolver components: referenceable components
        """
        super(SwaggerAutoSchema, self).__init__()
        self._sch = AutoSchema()
        self.view = view
        self.path = path
        self.method = method
        self.overrides = overrides
        self.components = components
        self._sch.view = view

    def get_operation(self, operation_keys):
        """Get an :class:`.Operation` for the given API endpoint (path, method).
        This includes query, body parameters and response schemas.

        :param tuple[str] operation_keys: an array of keys describing the hierarchical layout of this view in the API;
          e.g. ``('snippets', 'list')``, ``('snippets', 'retrieve')``, etc.
        :rtype: openapi.Operation
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
        """Return the request body parameters for this view. |br|
        This is either:

        -  a list with a single object Parameter with a :class:`.Schema` derived from the request serializer
        -  a list of primitive Parameters parsed as form data

        :param list[str] consumes: a list of accepted MIME types as returned by :meth:`.get_consumes`
        :return: a (potentially empty) list of :class:`.Parameter`\ s either ``in: body`` or ``in: formData``
        :rtype: list[openapi.Parameter]
        """
        serializer = self.get_request_serializer()
        schema = None
        if serializer is None:
            return []

        if isinstance(serializer, openapi.Schema.OR_REF):
            schema = serializer

        if any(is_form_media_type(encoding) for encoding in consumes):
            if schema is not None:
                raise SwaggerGenerationError("form request body cannot be a Schema")
            return self.get_request_form_parameters(serializer)
        else:
            if schema is None:
                schema = self.get_request_body_schema(serializer)
            return [self.make_body_parameter(schema)]

    def get_view_serializer(self):
        """Return the serializer as defined by the view's ``get_serializer()`` method.

        :return: the view's ``Serializer``
        """
        if not hasattr(self.view, 'get_serializer'):
            return None
        kwargs = {'context': self.view.get_serializer_context()}
        return self.view.get_serializer(**kwargs)

    def get_request_serializer(self):
        """Return the request serializer (used for parsing the request payload) for this endpoint.

        :return: the request serializer, or one of :class:`.Schema`, :class:`.SchemaRef`, ``None``
        """
        body_override = self.overrides.get('request_body', None)

        if body_override is not None:
            if body_override is no_body:
                return None
            if self.method not in self.body_methods:
                raise SwaggerGenerationError("request_body can only be applied to PUT, PATCH or POST views; "
                                             "are you looking for query_serializer or manual_parameters?")
            if isinstance(body_override, openapi.Schema.OR_REF):
                return body_override
            return force_serializer_instance(body_override)
        elif self.method in self.body_methods:
            return self.get_view_serializer()

        return None

    def get_request_form_parameters(self, serializer):
        """Given a Serializer, return a list of ``in: formData`` :class:`.Parameter`\ s.

        :param serializer: the view's request serializer as returned by :meth:`.get_request_serializer`
        :rtype: list[openapi.Parameter]
        """
        return self.serializer_to_parameters(serializer, in_=openapi.IN_FORM)

    def get_request_body_schema(self, serializer):
        """Return the :class:`.Schema` for a given request's body data. Only applies to PUT, PATCH and POST requests.

        :param serializer: the view's request serializer as returned by :meth:`.get_request_serializer`
        :rtype: openapi.Schema
        """
        return self.serializer_to_schema(serializer)

    def make_body_parameter(self, schema):
        """Given a :class:`.Schema` object, create an ``in: body`` :class:`.Parameter`.

        :param openapi.Schema schema: the request body schema
        :rtype: openapi.Parameter
        """
        return openapi.Parameter(name='data', in_=openapi.IN_BODY, required=True, schema=schema)

    def add_manual_parameters(self, parameters):
        """Add/replace parameters from the given list of automatically generated request parameters.

        :param list[openapi.Parameter] parameters: genereated parameters
        :return: modified parameters
        :rtype: list[openapi.Parameter]
        """
        parameters = param_list_to_odict(parameters)
        manual_parameters = self.overrides.get('manual_parameters', None) or []

        if any(param.in_ == openapi.IN_BODY for param in manual_parameters):  # pragma: no cover
            raise SwaggerGenerationError("specify the body parameter as a Schema or Serializer in request_body")
        if any(param.in_ == openapi.IN_FORM for param in manual_parameters):  # pragma: no cover
            if any(param.in_ == openapi.IN_BODY for param in parameters.values()):
                raise SwaggerGenerationError("cannot add form parameters when the request has a request schema; "
                                             "did you forget to set an appropriate parser class on the view?")

        parameters.update(param_list_to_odict(manual_parameters))
        return list(parameters.values())

    def get_responses(self):
        """Get the possible responses for this view as a swagger :class:`.Responses` object.

        :return: the documented responses
        :rtype: openapi.Responses
        """
        response_serializers = self.get_response_serializers()
        return openapi.Responses(
            responses=self.get_response_schemas(response_serializers)
        )

    def get_paged_response_schema(self, response_schema):
        """Add appropriate paging fields to a response :class:`.Schema`.

        :param openapi.Schema response_schema: the response schema that must be paged.
        :rtype: openapi.Schema
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
        """Get the default responses determined for this view from the request serializer and request method.

        :type: dict[str, openapi.Schema]
        """
        method = self.method.lower()

        default_status = status.HTTP_200_OK
        default_schema = ''
        if method == 'post':
            default_status = status.HTTP_201_CREATED
            default_schema = self.get_request_serializer() or self.get_view_serializer()
        elif method == 'delete':
            default_status = status.HTTP_204_NO_CONTENT
        elif method in ('get', 'put', 'patch'):
            default_schema = self.get_request_serializer() or self.get_view_serializer()

        default_schema = default_schema or ''
        if any(is_form_media_type(encoding) for encoding in self.get_consumes()):
            default_schema = ''
        if default_schema:
            if not isinstance(default_schema, openapi.Schema):
                default_schema = self.serializer_to_schema(default_schema)
            if is_list_view(self.path, self.method, self.view) and self.method.lower() == 'get':
                default_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=default_schema)
            if self.should_page():
                default_schema = self.get_paged_response_schema(default_schema)

        return {str(default_status): default_schema}

    def get_response_serializers(self):
        """Return the response codes that this view is expected to return, and the serializer for each response body.
        The return value should be a dict where the keys are possible status codes, and values are either strings,
        ``Serializer``\ s, :class:`.Schema`, :class:`.SchemaRef` or :class:`.Response` objects. See
        :func:`@swagger_auto_schema <.swagger_auto_schema>` for more details.

        :return: the response serializers
        :rtype: dict
        """
        manual_responses = self.overrides.get('responses', None) or {}
        manual_responses = OrderedDict((str(sc), resp) for sc, resp in manual_responses.items())

        responses = {}
        if not any(is_success(int(sc)) for sc in manual_responses if sc != 'default'):
            responses = self.get_default_responses()

        responses.update((str(sc), resp) for sc, resp in manual_responses.items())
        return responses

    def get_response_schemas(self, response_serializers):
        """Return the :class:`.openapi.Response` objects calculated for this view.

        :param dict response_serializers: response serializers as returned by :meth:`.get_response_serializers`
        :return: a dictionary of status code to :class:`.Response` object
        :rtype: dict[str, openapi.Response]
        """
        responses = {}
        for sc, serializer in response_serializers.items():
            if isinstance(serializer, str):
                response = openapi.Response(
                    description=serializer
                )
            elif isinstance(serializer, openapi.Response):
                response = serializer
                if not isinstance(response.schema, openapi.Schema.OR_REF):
                    serializer = force_serializer_instance(response.schema)
                    response.schema = self.serializer_to_schema(serializer)
            elif isinstance(serializer, openapi.Schema.OR_REF):
                response = openapi.Response(
                    description='',
                    schema=serializer,
                )
            else:
                serializer = force_serializer_instance(serializer)
                response = openapi.Response(
                    description='',
                    schema=self.serializer_to_schema(serializer),
                )

            responses[str(sc)] = response

        return responses

    def get_query_serializer(self):
        """Return the query serializer (used for parsing query parameters) for this endpoint.

        :return: the query serializer, or ``None``
        """
        query_serializer = self.overrides.get('query_serializer', None)
        if query_serializer is not None:
            query_serializer = force_serializer_instance(query_serializer)
        return query_serializer

    def get_query_parameters(self):
        """Return the query parameters accepted by this view.

        :rtype: list[openapi.Parameter]
        """
        natural_parameters = self.get_filter_parameters() + self.get_pagination_parameters()

        query_serializer = self.get_query_serializer()
        serializer_parameters = []
        if query_serializer is not None:
            serializer_parameters = self.serializer_to_parameters(query_serializer, in_=openapi.IN_QUERY)

            if len(set(param_list_to_odict(natural_parameters)) & set(param_list_to_odict(serializer_parameters))) != 0:
                raise SwaggerGenerationError(
                    "your query_serializer contains fields that conflict with the "
                    "filter_backend or paginator_class on the view - %s %s" % (self.method, self.path)
                )

        return natural_parameters + serializer_parameters

    def should_filter(self):
        """Determine whether filter backend parameters should be included for this request.

        :rtype: bool
        """
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
        :rtype: list[openapi.Parameter]
        """
        fields = []
        if hasattr(filter_backend, 'get_schema_fields'):
            fields = filter_backend.get_schema_fields(self.view)
        return [self.coreapi_field_to_parameter(field) for field in fields]

    def get_filter_parameters(self):
        """Return the parameters added to the view by its filter backends.

        :rtype: list[openapi.Parameter]
        """
        if not self.should_filter():
            return []

        fields = []
        for filter_backend in self.view.filter_backends:
            fields += self.get_filter_backend_parameters(filter_backend())

        return fields

    def should_page(self):
        """Determine whether paging parameters and structure should be added to this operation's request and response.

        :rtype: bool
        """
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
        :rtype: list[openapi.Parameter]
        """
        fields = []
        if hasattr(paginator, 'get_schema_fields'):
            fields = paginator.get_schema_fields(self.view)

        return [self.coreapi_field_to_parameter(field) for field in fields]

    def get_pagination_parameters(self):
        """Return the parameters added to the view by its paginator.

        :rtype: list[openapi.Parameter]
        """
        if not self.should_page():
            return []

        return self.get_paginator_parameters(self.view.paginator)

    def get_description(self):
        """Return an operation description determined as appropriate from the view's method and class docstrings.

        :return: the operation description
        :rtype: str
        """
        description = self.overrides.get('operation_description', None)
        if description is None:
            description = self._sch.get_description(self.path, self.method)
        return description

    def get_consumes(self):
        """Return the MIME types this endpoint can consume.

        :rtype: list[str]
        """
        media_types = [parser.media_type for parser in getattr(self.view, 'parser_classes', [])]
        if all(is_form_media_type(encoding) for encoding in media_types):
            return media_types
        return media_types[:1]

    def serializer_to_schema(self, serializer):
        """Convert a DRF Serializer instance to an :class:`.openapi.Schema`.

        :param serializers.BaseSerializer serializer: the ``Serializer`` instance
        :rtype: openapi.Schema
        """
        definitions = self.components.with_scope(openapi.SCHEMA_DEFINITIONS)
        return serializer_field_to_swagger(serializer, openapi.Schema, definitions)

    def serializer_to_parameters(self, serializer, in_):
        """Convert a DRF serializer into a list of :class:`.Parameter`\ s using :meth:`.field_to_parameter`

        :param serializers.BaseSerializer serializer: the ``Serializer`` instance
        :param str in_: the location of the parameters, one of the `openapi.IN_*` constants
        :rtype: list[openapi.Parameter]
        """
        fields = getattr(serializer, 'fields', {})
        return [
            self.field_to_parameter(value, key, in_)
            for key, value
            in fields.items()
        ]

    def field_to_parameter(self, field, name, in_):
        """Convert a DRF serializer Field to a swagger :class:`.Parameter` object.

        :param coreapi.Field field:
        :param str name: the name of the parameter
        :param str in_: the location of the parameter, one of the `openapi.IN_*` constants
        :rtype: openapi.Parameter
        """
        return serializer_field_to_swagger(field, openapi.Parameter, name=name, in_=in_)

    def coreapi_field_to_parameter(self, field):
        """Convert an instance of `coreapi.Field` to a swagger :class:`.Parameter` object.

        :param coreapi.Field field:
        :rtype: openapi.Parameter
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
            type=coreapi_types.get(type(field.schema), openapi.TYPE_STRING),
            required=field.required,
            description=field.schema.description,
        )
