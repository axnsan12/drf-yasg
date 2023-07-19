from django.urls import re_path
from rest_framework import fields, generics, versioning

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from testproj.urls import SchemaView, required_urlpatterns


class SnippetV1Serializer(SnippetSerializer):
    v1field = fields.IntegerField(help_text="version 1.0 field")


class SnippetSerializerV2(SnippetV1Serializer):
    v2field = fields.IntegerField(help_text="version 2.0 field")

    class Meta:
        # Same name for check failing
        ref_name = 'SnippetV1'


class SnippetList(generics.ListCreateAPIView):
    """SnippetList classdoc"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetV1Serializer
    versioning_class = versioning.URLPathVersioning

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        """post method docstring"""
        return super(SnippetList, self).post(request, *args, **kwargs)


class SnippetsV2(SnippetList):
    serializer_class = SnippetSerializerV2


VERSION_PREFIX_URL = r"^versioned/url/v(?P<version>1.0|2.0)/"


class VersionedSchemaView(SchemaView):
    versioning_class = versioning.URLPathVersioning


urlpatterns = required_urlpatterns + [
    re_path(VERSION_PREFIX_URL + r"snippets/$", SnippetList.as_view()),
    re_path(VERSION_PREFIX_URL + r"other_snippets/$", SnippetsV2.as_view()),
    re_path(VERSION_PREFIX_URL + r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(),
            name='vschema-json'),
]
