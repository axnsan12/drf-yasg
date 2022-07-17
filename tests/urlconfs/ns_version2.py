from django.urls import path
from rest_framework import fields

from snippets.serializers import SnippetSerializer
from testproj.urls import required_urlpatterns

from .ns_version1 import SnippetList as SnippetListV1


class SnippetSerializerV2(SnippetSerializer):
    v2field = fields.IntegerField(help_text="version 2.0 field")

    class Meta:
        ref_name = 'SnippetV2'


class SnippetListV2(SnippetListV1):
    serializer_class = SnippetSerializerV2


app_name = '2.0'

urlpatterns = required_urlpatterns + [
    path("", SnippetListV2.as_view())
]
