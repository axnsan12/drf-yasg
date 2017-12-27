from django.conf.urls import include, url
from rest_framework import permissions

import testproj.urls
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

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
