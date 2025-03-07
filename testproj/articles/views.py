import datetime

from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response

from articles import serializers
from articles.models import Article
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.inspectors import DrfAPICompatInspector, FieldInspector, NotHandled, SwaggerAutoSchema
from drf_yasg.utils import no_body, swagger_auto_schema


class DjangoFilterDescriptionInspector(DrfAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', '') or param.get('description') == param.name:
                    param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

            return result

        return NotHandled


class NoSchemaTitleInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        # remove the `title` attribute of all Schema objects
        if isinstance(result, openapi.Schema.OR_REF):
            # traverse any references and alter the Schema object in place
            schema = openapi.resolve_ref(result, self.components)
            schema.pop('title', None)

            # no ``return schema`` here, because it would mean we always generate
            # an inline `object` instead of a definition reference

        # return back the same object that we got - i.e. a reference if we got a reference
        return result


class NoTitleAutoSchema(SwaggerAutoSchema):
    field_inspectors = [NoSchemaTitleInspector] + swagger_settings.DEFAULT_FIELD_INSPECTORS


class NoPagingAutoSchema(NoTitleAutoSchema):
    def should_page(self):
        return False


class ArticlePagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 25


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="description from swagger_auto_schema via method_decorator",
    filter_inspectors=[DjangoFilterDescriptionInspector],
))
class ArticleViewSet(viewsets.ModelViewSet):
    """
    ArticleViewSet class docstring

    retrieve:
    retrieve class docstring

    destroy:
    destroy class docstring

    partial_update:
    partial_update class docstring
    """
    queryset = Article.objects.all()
    lookup_field = 'slug'
    lookup_value_regex = r'[a-z0-9]+(?:-[a-z0-9]+)'
    serializer_class = serializers.ArticleSerializer

    pagination_class = ArticlePagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('title',)
    # django-filter 1.1 compatibility; was renamed to filterset_fields in 2.0
    # TODO: remove when dropping support for Django 1.11
    filter_fields = filterset_fields
    ordering_fields = ('date_modified', 'date_created')
    ordering = ('date_created',)

    swagger_schema = NoTitleAutoSchema

    from rest_framework.decorators import action

    @swagger_auto_schema(auto_schema=NoPagingAutoSchema, filter_inspectors=[DjangoFilterDescriptionInspector])
    @action(detail=False, methods=['get'])
    def today(self, request):
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        articles = self.get_queryset().filter(date_created__range=(today_min, today_max)).all()
        serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(method='get', operation_description="image GET description override")
    @swagger_auto_schema(method='post', request_body=serializers.ImageUploadSerializer)
    @swagger_auto_schema(method='delete', manual_parameters=[openapi.Parameter(
        name='delete_form_param', in_=openapi.IN_FORM,
        type=openapi.TYPE_INTEGER,
        description="this should not crash (form parameter on DELETE method)"
    )])
    @action(detail=True, methods=['get', 'post', 'delete'], parser_classes=(MultiPartParser, FileUploadParser))
    def image(self, request, slug=None):
        """
        image method docstring
        """
        pass

    @swagger_auto_schema(request_body=no_body, operation_id='no_body_test')
    def update(self, request, *args, **kwargs):
        """update method docstring"""
        return super(ArticleViewSet, self).update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="partial_update description override", responses={404: 'slug not found'},
                         operation_summary='partial_update summary', deprecated=True)
    def partial_update(self, request, *args, **kwargs):
        """partial_update method docstring"""
        return super(ArticleViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """destroy method docstring"""
        return super(ArticleViewSet, self).destroy(request, *args, **kwargs)
