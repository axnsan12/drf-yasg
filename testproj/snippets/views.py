from djangorestframework_camel_case.parser import CamelCaseJSONParser
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from inflection import camelize
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser, FormParser

from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from snippets.models import Snippet, SnippetViewer
from snippets.serializers import SnippetSerializer, SnippetViewerSerializer


class CamelCaseOperationIDAutoSchema(SwaggerAutoSchema):
    def get_operation_id(self, operation_keys):
        operation_id = super(CamelCaseOperationIDAutoSchema, self).get_operation_id(operation_keys)
        return camelize(operation_id, uppercase_first_letter=False)


class SnippetList(generics.ListCreateAPIView):
    """SnippetList classdoc"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    parser_classes = (FormParser, CamelCaseJSONParser, FileUploadParser)
    renderer_classes = (CamelCaseJSONRenderer,)
    swagger_schema = CamelCaseOperationIDAutoSchema

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        """post method docstring"""
        return super(SnippetList, self).post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='snippets_delete_bulk',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'body': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='this should not crash (request body on DELETE method)'
                )
            }
        ),
    )
    def delete(self, *args, **kwargs):
        """summary from docstring

        description body is here, summary is not included
        """
        pass


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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="path parameter override",
                required=True
            ),
        ],
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="this should not crash (response object with no schema)"
            )
        }
    )
    def delete(self, request, *args, **kwargs):
        """delete method docstring"""
        return super(SnippetDetail, self).patch(request, *args, **kwargs)


class SnippetViewerList(generics.ListAPIView):
    """SnippetViewerList classdoc"""
    serializer_class = SnippetViewerSerializer
    pagination_class = PageNumberPagination

    parser_classes = (FormParser, CamelCaseJSONParser, FileUploadParser)
    renderer_classes = (CamelCaseJSONRenderer,)
    swagger_schema = CamelCaseOperationIDAutoSchema
    lookup_url_kwarg = 'snippet_pk'

    def get_object(self):
        queryset = Snippet.objects.all()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        return SnippetViewer.objects.filter(snippet=self.get_object())
