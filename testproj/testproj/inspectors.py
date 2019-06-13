from drf_yasg import openapi
from drf_yasg.inspectors import NotHandled, PaginatorInspector


class UnknownPaginatorInspector(PaginatorInspector):
    def get_paginator_parameters(self, paginator):
        if hasattr(paginator, 'paginator_query_args'):
            return [openapi.Parameter(name=arg, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
                    for arg in getattr(paginator, 'paginator_query_args')]

        return NotHandled
