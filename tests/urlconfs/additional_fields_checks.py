from django.urls import re_path
from rest_framework import serializers

from testproj.urls import required_urlpatterns

from .url_versioning import SnippetList, SnippetSerializer, VersionedSchemaView, VERSION_PREFIX_URL


class SnippetsSerializer(serializers.HyperlinkedModelSerializer, SnippetSerializer):
    ipv4 = serializers.IPAddressField(required=False)
    uri = serializers.URLField(required=False)
    tracks = serializers.RelatedField(
        read_only=True,
        allow_null=True,
        allow_empty=True,
        many=True,
    )

    class Meta:
        fields = tuple(SnippetSerializer().fields.keys()) + ('ipv4', 'uri', 'tracks', 'url',)
        model = SnippetList.queryset.model


class SnippetsV2Serializer(SnippetSerializer):
    url = serializers.HyperlinkedRelatedField(view_name='snippets-detail', source='*', read_only=True)
    other_owner_snippets = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='owner.snippets',
        many=True
    )
    owner_snippets = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True
    )


class SnippetsV1(SnippetList):
    serializer_class = SnippetsSerializer

    def get_serializer_class(self):
        return self.serializer_class


class SnippetsV2(SnippetsV1):
    serializer_class = SnippetsV2Serializer


urlpatterns = required_urlpatterns + [
    re_path(VERSION_PREFIX_URL + r"snippets/$", SnippetsV1.as_view()),
    re_path(VERSION_PREFIX_URL + r"other_snippets/$", SnippetsV2.as_view()),
    re_path(VERSION_PREFIX_URL + r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(),
            name='vschema-json'),
]
