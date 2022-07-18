from django.urls import path
from rest_framework import generics, versioning

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from testproj.urls import required_urlpatterns


class SnippetList(generics.ListCreateAPIView):
    """SnippetList classdoc"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    versioning_class = versioning.NamespaceVersioning

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        """post method docstring"""
        return super(SnippetList, self).post(request, *args, **kwargs)


app_name = 'test_ns_versioning'

urlpatterns = required_urlpatterns + [
    path("", SnippetList.as_view())
]
