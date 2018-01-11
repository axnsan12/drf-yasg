from djangorestframework_camel_case.parser import CamelCaseJSONParser
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from inflection import camelize
from rest_framework import generics

from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


class CamelCaseOperationIDAutoSchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys):
        operation_id = super(CamelCaseOperationIDAutoSchema, self).get_operation_id(operation_keys)
        return camelize(operation_id, uppercase_first_letter=False)


class SnippetList(generics.ListCreateAPIView):
    """SnippetList classdoc"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    parser_classes = (CamelCaseJSONParser,)
    renderer_classes = (CamelCaseJSONRenderer,)
    swagger_schema = CamelCaseOperationIDAutoSchema

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        """post method docstring"""
        return super(SnippetList, self).post(request, *args, **kwargs)


class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    SnippetDetail classdoc

    put:
    put class docstring

    patch:
    patch class docstring
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    pagination_class = None

    parser_classes = (CamelCaseJSONParser,)
    renderer_classes = (CamelCaseJSONRenderer,)
    swagger_schema = CamelCaseOperationIDAutoSchema

    def patch(self, request, *args, **kwargs):
        """patch method docstring"""
        return super(SnippetDetail, self).patch(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            description="path parameter override",
            required=True
        )
    ])
    def delete(self, request, *args, **kwargs):
        """delete method docstring"""
        return super(SnippetDetail, self).patch(request, *args, **kwargs)
