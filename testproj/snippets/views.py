from rest_framework import generics
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer


class SnippetList(generics.ListCreateAPIView):
    """SnippetList classdoc"""
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def post(self, request, *args, **kwargs):
        """post method docstring"""
        return super().post(request, *args, **kwargs)


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

    def patch(self, request, *args, **kwargs):
        """patch method docstring"""
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """delete method docstring"""
        return super().patch(request, *args, **kwargs)
