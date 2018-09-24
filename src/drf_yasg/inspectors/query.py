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
        return openapi.Parameter(
            name=field.name,
            in_=location_to_in[field.location],
            type=coreapi_types.get(type(field.schema), openapi.TYPE_STRING),
            required=field.required,
            description=force_real_str(field.schema.description) if field.schema else None,
        )


class DjangoRestResponsePagination(PaginatorInspector):
    """Provides response schema pagination warpping for django-rest-framework's LimitOffsetPagination,
    PageNumberPagination and CursorPagination
    """

    COUNT_SCHEMA = openapi.Schema(
        type=openapi.TYPE_INTEGER,
        description='Total number of items available.')
    NEXT_SCHEMA = openapi.Schema(
        type=openapi.TYPE_INTEGER,
        format=openapi.FORMAT_URI,
        description='Next items in the paginated sequence.')
    PREVIOUS_SCHEMA = openapi.Schema(
        type=openapi.TYPE_INTEGER,
        format=openapi.FORMAT_URI,
        description='Previous items in the paginated sequence.')

    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        if isinstance(paginator, (LimitOffsetPagination, PageNumberPagination, CursorPagination)):
            has_count = not isinstance(paginator, CursorPagination)
            if not response_schema.get('description'):
                response_schema['description'] = 'List of paginated items'
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('count', self.COUNT_SCHEMA if has_count else None),
                    ('next', self.NEXT_SCHEMA),
                    ('previous', self.PREVIOUS_SCHEMA),
                    ('results', response_schema),
                )),
                required=['results']
            )

            if has_count:
                paged_schema.required.insert(0, 'count')

        return paged_schema
