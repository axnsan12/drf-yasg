from collections import OrderedDict

import coreschema
from rest_framework.pagination import CursorPagination, LimitOffsetPagination, PageNumberPagination

from .. import openapi
from ..utils import force_real_str
from .base import FilterInspector, PaginatorInspector


class CoreAPICompatInspector(PaginatorInspector, FilterInspector):
    """Converts ``coreapi.Field``\\ s to :class:`.openapi.Parameter`\\ s for filters and paginators that implement a
    ``get_schema_fields`` method.
    """

    def get_paginator_parameters(self, paginator):
        fields = []
        if hasattr(paginator, 'get_schema_fields'):
            fields = paginator.get_schema_fields(self.view)

        return [self.coreapi_field_to_parameter(field) for field in fields]

    def get_filter_parameters(self, filter_backend):
        fields = []
        if hasattr(filter_backend, 'get_schema_fields'):
            fields = filter_backend.get_schema_fields(self.view)
        return [self.coreapi_field_to_parameter(field) for field in fields]

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

        coreschema_attrs = ['format', 'pattern', 'enum', 'min_length', 'max_length']
        schema = field.schema
        return openapi.Parameter(
            name=field.name,
            in_=location_to_in[field.location],
            required=field.required,
            description=force_real_str(schema.description) if schema else None,
            type=coreapi_types.get(type(schema), openapi.TYPE_STRING),
            **OrderedDict((attr, getattr(schema, attr, None)) for attr in coreschema_attrs)
        )


class DjangoRestResponsePagination(PaginatorInspector):
    """Provides response schema pagination wrapping for django-rest-framework's LimitOffsetPagination,
    PageNumberPagination and CursorPagination
    """

    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        if isinstance(paginator, (LimitOffsetPagination, PageNumberPagination, CursorPagination)):
            has_count = not isinstance(paginator, CursorPagination)
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('count', openapi.Schema(type=openapi.TYPE_INTEGER) if has_count else None),
                    ('next', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('previous', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('results', response_schema),
                )),
                required=['results']
            )

            if has_count:
                paged_schema.required.insert(0, 'count')

        return paged_schema
