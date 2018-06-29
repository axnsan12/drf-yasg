import logging
from collections import OrderedDict

from rest_framework.request import is_form_media_type
from rest_framework.schemas import AutoSchema
from rest_framework.status import is_success

from .. import openapi
from ..errors import SwaggerGenerationError
from ..utils import (
    force_serializer_instance, get_consumes, get_produces, guess_response_status, is_list_view, no_body,
    param_list_to_odict
)
from .base import ViewInspector

log = logging.getLogger(__name__)


class SwaggerAutoSchema(ViewInspector):
    def __init__(self, view, path, method, components, request, overrides):
        super(SwaggerAutoSchema, self).__init__(view, path, method, components, request, overrides)
        self._sch = AutoSchema()
        self._sch.view = view

    def get_operation(self, operation_keys):
        consumes = self.get_consumes()
        produces = self.get_produces()

        body = self.get_request_body_parameters(consumes)
        query = self.get_query_parameters()
        parameters = body + query
        parameters = [param for param in parameters if param is not None]
        parameters = self.add_manual_parameters(parameters)

        operation_id = self.get_operation_id(operation_keys)
        description = self.get_description()
        security = self.get_security()
        assert security is None or isinstance(security, list), "security must be a list of securiy requirement objects"
        tags = self.get_tags(operation_keys)

        responses = self.get_responses()

        return openapi.Operation(
            operation_id=operation_id,
            description=description,
            responses=responses,
            parameters=parameters,
            consumes=consumes,
            produces=produces,
            tags=tags,
            security=security
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
            return [self.make_body_parameter(schema)] if schema is not None else []

    def get_view_serializer(self):
        """Return the serializer as defined by the view's ``get_serializer()`` method.

        :return: the view's ``Serializer``
        """
        if not hasattr(self.view, 'get_serializer'):
            return None
        try:
            return self.view.get_serializer()
        except Exception:
            log.warning("view's get_serializer raised exception (%s %s %s)",
                        self.method, self.path, type(self.view).__name__, exc_info=True)
            return None

    def get_request_serializer(self):
        """Return the request serializer (used for parsing the request payload) for this endpoint.

        :return: the request serializer, or one of :class:`.Schema`, :class:`.SchemaRef`, ``None``
        """
        body_override = self.overrides.get('request_body', None)

        if body_override is not None:
            if body_override is no_body:
                return None
            if self.method not in self.body_methods:
                raise SwaggerGenerationError("request_body can only be applied to (" + ','.join(self.body_methods) +
                                             "); are you looking for query_serializer or manual_parameters?")
            if isinstance(body_override, openapi.Schema.OR_REF):
                return body_override
            return force_serializer_instance(body_override)
        elif self.method in self.implicit_body_methods:
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
                raise SwaggerGenerationError("cannot add form parameters when the request has a request body; "
                                             "did you forget to set an appropriate parser class on the view?")
            if self.method not in self.body_methods:
                raise SwaggerGenerationError("form parameters can only be applied to (" + ','.join(self.body_methods) +
                                             ") HTTP methods")

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

    def get_default_responses(self):
        """Get the default responses determined for this view from the request serializer and request method.

        :type: dict[str, openapi.Schema]
        """
        method = self.method.lower()

        default_status = guess_response_status(method)
        default_schema = ''
        if method in ('get', 'post', 'put', 'patch'):
            default_schema = self.get_request_serializer() or self.get_view_serializer()

        default_schema = default_schema or ''
        if any(is_form_media_type(encoding) for encoding in self.get_consumes()):
            default_schema = ''
        if default_schema and not isinstance(default_schema, openapi.Schema):
            default_schema = self.serializer_to_schema(default_schema) or ''

        if default_schema:
            if is_list_view(self.path, self.method, self.view) and self.method.lower() == 'get':
                default_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=default_schema)
            if self.should_page():
                default_schema = self.get_paginated_response(default_schema) or default_schema

        return OrderedDict({str(default_status): default_schema})

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

        responses = OrderedDict()
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
        responses = OrderedDict()
        for sc, serializer in response_serializers.items():
            if isinstance(serializer, str):
                response = openapi.Response(
                    description=serializer
                )
            elif not serializer:
                continue
            elif isinstance(serializer, openapi.Response):
                response = serializer
                if hasattr(response, 'schema') and not isinstance(response.schema, openapi.Schema.OR_REF):
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

    def get_operation_id(self, operation_keys):
        """Return an unique ID for this operation. The ID must be unique across
        all :class:`.Operation` objects in the API.

        :param tuple[str] operation_keys: an array of keys derived from the pathdescribing the hierarchical layout
            of this view in the API; e.g. ``('snippets', 'list')``, ``('snippets', 'retrieve')``, etc.
        :rtype: str
        """
        operation_id = self.overrides.get('operation_id', '')
        if not operation_id:
            operation_id = '_'.join(operation_keys)
        return operation_id

    def get_description(self):
        """Return an operation description determined as appropriate from the view's method and class docstrings.

        :return: the operation description
        :rtype: str
        """
        description = self.overrides.get('operation_description', None)
        if description is None:
            description = self._sch.get_description(self.path, self.method)
        return description

    def get_security(self):
        """Return a list of security requirements for this operation.

        Returning an empty list marks the endpoint as unauthenticated (i.e. removes all accepted
        authentication schemes). Returning ``None`` will inherit the top-level secuirty requirements.

        :return: security requirements
        :rtype: list[dict[str,list[str]]]"""
        return self.overrides.get('security', None)

    def get_tags(self, operation_keys):
        """Get a list of tags for this operation. Tags determine how operations relate with each other, and in the UI
        each tag will show as a group containing the operations that use it.

        :param tuple[str] operation_keys: an array of keys derived from the pathdescribing the hierarchical layout
            of this view in the API; e.g. ``('snippets', 'list')``, ``('snippets', 'retrieve')``, etc.
        :rtype: list[str]
        """
        return [operation_keys[0]]

    def get_consumes(self):
        """Return the MIME types this endpoint can consume.

        :rtype: list[str]
        """
        return get_consumes(getattr(self.view, 'parser_classes', []))

    def get_produces(self):
        """Return the MIME types this endpoint can produce.

        :rtype: list[str]
        """
        return get_produces(getattr(self.view, 'renderer_classes', []))
