from django.urls import include, path, re_path
from rest_framework import versioning

from testproj.urls import SchemaView, required_urlpatterns

from . import ns_version1, ns_version2

VERSION_PREFIX_NS = r"versioned/ns/"


class VersionedSchemaView(SchemaView):
    versioning_class = versioning.NamespaceVersioning


schema_patterns = [
    re_path(r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(), name='ns-schema')
]


urlpatterns = required_urlpatterns + [
    path(VERSION_PREFIX_NS + "v1.0/snippets/", include(ns_version1, namespace='1.0')),
    path(VERSION_PREFIX_NS + "v2.0/snippets/", include(ns_version2)),
    path(VERSION_PREFIX_NS + "v1.0/", include((schema_patterns, '1.0'))),
    path(VERSION_PREFIX_NS + "v2.0/", include((schema_patterns, '2.0'))),
]
