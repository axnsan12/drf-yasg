from django.conf.urls import url
from rest_framework import fields, generics, versioning

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from testproj.urls import SchemaView, required_urlpatterns


class SnippetSerializerV2(SnippetSerializer):
    v2field = fields.IntegerField(help_text="version 2.0 field")

    class Meta:
        ref_name = 'SnippetV2'


class SnippetList(generics.ListCreateAPIView):
    """SnippetList classdoc"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    versioning_class = versioning.URLPathVersioning

    def get_serializer_class(self):
        context = self.get_serializer_context()
        request = context['request']
        if int(float(request.version)) >= 2:
            return SnippetSerializerV2
        else:
            return SnippetSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        """post method docstring"""
        return super(SnippetList, self).post(request, *args, **kwargs)


VERSION_PREFIX_URL = r"^versioned/url/v(?P<version>1.0|2.0)/"


class VersionedSchemaView(SchemaView):
    versioning_class = versioning.URLPathVersioning


urlpatterns = required_urlpatterns + [
    url(VERSION_PREFIX_URL + r"snippets/$", SnippetList.as_view()),
    url(VERSION_PREFIX_URL + r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(), name='vschema-json'),
]
