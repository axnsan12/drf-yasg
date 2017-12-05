import datetime

from django_filters.rest_framework import DjangoFilterBackend, filters
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from articles import serializers
from articles.models import Article


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ArticleViewSet class docstring

    retrieve:
    retrieve class docstring

    destroy:
    destroy class docstring
    """
    queryset = Article.objects.all()
    lookup_field = 'slug'
    serializer_class = serializers.ArticleSerializer

    pagination_class = LimitOffsetPagination
    max_page_size = 5
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
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

    @detail_route(
        methods=['get', 'post'],
        parser_classes=(MultiPartParser,),
        serializer_class=serializers.ImageUploadSerializer,
    )
    def image(self, request, slug=None):
        """
        image method docstring
        """
        pass

    def update(self, request, *args, **kwargs):
        """update method docstring"""
        return super(ArticleViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """destroy method docstring"""
        return super(ArticleViewSet, self).destroy(request, *args, **kwargs)
