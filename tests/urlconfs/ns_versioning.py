from django.conf.urls import include, url
from rest_framework import versioning

from testproj.urls import SchemaView, required_urlpatterns

from . import ns_version1, ns_version2

VERSION_PREFIX_NS = r"^versioned/ns/"


class VersionedSchemaView(SchemaView):
    versioning_class = versioning.NamespaceVersioning


schema_patterns = [
    url(r'swagger(?P<format>.json|.yaml)$', VersionedSchemaView.without_ui(), name='ns-schema')
]


urlpatterns = required_urlpatterns + [
    url(VERSION_PREFIX_NS + r"v1.0/snippets/", include(ns_version1, namespace='1.0')),
    url(VERSION_PREFIX_NS + r"v2.0/snippets/", include(ns_version2)),
    url(VERSION_PREFIX_NS + r'v1.0/', include((schema_patterns, '1.0'))),
    url(VERSION_PREFIX_NS + r'v2.0/', include((schema_patterns, '2.0'))),
]
