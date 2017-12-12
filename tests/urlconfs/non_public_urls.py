from django.conf.urls import url
from django.urls import include
from rest_framework import permissions

import testproj.urls
from drf_swagger import openapi
from drf_swagger.views import get_schema_view

view = get_schema_view(
    openapi.Info('bla', 'ble'),
    public=False,
    permission_classes=(permissions.AllowAny,)
)
view = view.without_ui(cache_timeout=None)

urlpatterns = [
    url(r'^', include(testproj.urls)),
    url(r'^private/swagger.yaml', view, name='schema-private'),
]
