import datetime

from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from articles import serializers
from articles.models import Article
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema


class NoPagingAutoSchema(SwaggerAutoSchema):
    def should_page(self):
        return False


class ArticlePagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 25


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="description from swagger_auto_schema via method_decorator"
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
    filter_fields = ('title',)
    ordering_fields = ('date_modified', 'date_created')
    ordering = ('date_created',)

    @swagger_auto_schema(auto_schema=NoPagingAutoSchema)
    @list_route(methods=['get'])
    def today(self, request):
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        articles = self.get_queryset().filter(date_created__range=(today_min, today_max)).all()
        serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(method='get', operation_description="image GET description override")
    @swagger_auto_schema(method='post', request_body=serializers.ImageUploadSerializer)
    @detail_route(methods=['get', 'post'], parser_classes=(MultiPartParser,))
    def image(self, request, slug=None):
        """
        image method docstring
        """
        pass

    def update(self, request, *args, **kwargs):
        """update method docstring"""
        return super(ArticleViewSet, self).update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="partial_update description override", responses={404: 'slug not found'})
    def partial_update(self, request, *args, **kwargs):
        """partial_update method docstring"""
        return super(ArticleViewSet, self).partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """destroy method docstring"""
        return super(ArticleViewSet, self).destroy(request, *args, **kwargs)
