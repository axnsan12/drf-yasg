from django.urls import re_path

from testproj.urls import required_urlpatterns

from .url_versioning import SnippetList, VERSION_PREFIX_URL, VersionedSchemaView

urlpatterns = required_urlpatterns + [
    re_path(VERSION_PREFIX_URL + r"extra/snippets/$", SnippetList.as_view()),
    re_path(VERSION_PREFIX_URL + r"extra2/snippets/$", SnippetList.as_view()),
    re_path(VERSION_PREFIX_URL + r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(),
            name='vschema-json'),
]
