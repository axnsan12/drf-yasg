import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from articles import serializers
from articles.models import Article
from drf_swagger.utils import swagger_auto_schema


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
    serializer_class = serializers.ArticleSerializer

    pagination_class = LimitOffsetPagination
    max_page_size = 5
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('title',)
    ordering_fields = ('date_modified',)
    ordering = ('username',)

    @list_route(methods=['get'])
    def today(self, request):
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        articles = self.get_queryset().filter(date_created__range=(today_min, today_max)).all()
        serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(method='get', operation_description="image GET description override")
    @swagger_auto_schema(method='post', request_body=serializers.ImageUploadSerializer, responses={200: 'success'})
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
