from django.urls import re_path
import coreapi
import coreschema
from rest_framework import pagination

from testproj.urls import required_urlpatterns

from .url_versioning import SnippetList, VersionedSchemaView, VERSION_PREFIX_URL


class FilterBackendWithoutParams:
    def filter_queryset(self, request, queryset, view):
        return queryset


class OldFilterBackend(FilterBackendWithoutParams):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='test_param',
                required=False,
                location='query',
                schema=coreschema.String(
                    title='Test',
                    description="Test description"
                )
            )
        ]


class PaginatorV1(pagination.LimitOffsetPagination):
    def get_paginated_response_schema(self, schema):
        response_schema = super().get_paginated_response_schema(schema)
        del response_schema['properties']['count']
        return response_schema


class PaginatorV2(pagination.LimitOffsetPagination):
    def __getattribute__(self, item):
        if item in {'get_paginated_response_schema', 'get_schema_operation_parameters'}:
            raise AttributeError
        return super().__getattribute__(item)


class PaginatorV3(PaginatorV1):
    def get_paginated_response_schema(self, schema):
        response_schema = super().get_paginated_response_schema(schema)
        response_schema['required'] = ['results']
        return response_schema

    def __getattribute__(self, item):
        if item == 'get_schema_fields':
            raise AttributeError()
        return super().__getattribute__(item)


class SnippetsV1(SnippetList):
    filter_backends = list(SnippetList.filter_backends) + [FilterBackendWithoutParams, OldFilterBackend]
    pagination_class = PaginatorV1


class SnippetsV2(SnippetList):
    pagination_class = PaginatorV2


class SnippetsV3(SnippetList):
    pagination_class = PaginatorV3


urlpatterns = required_urlpatterns + [
    re_path(VERSION_PREFIX_URL + r"snippets/$", SnippetsV1.as_view()),
    re_path(VERSION_PREFIX_URL + r"other_snippets/$", SnippetsV2.as_view()),
    re_path(VERSION_PREFIX_URL + r"ya_snippets/$", SnippetsV3.as_view()),
    re_path(VERSION_PREFIX_URL + r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(),
            name='vschema-json'),
]
