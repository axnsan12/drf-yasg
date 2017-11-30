from django.conf.urls import url, include
from django.contrib import admin

from drf_swagger.views import get_schema_view
from drf_swagger import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="*Some TOS*",
        contact=openapi.Contact(email="cristi@cvjd.me"),
        license=openapi.License("BSD License"),
    ),
    validate=True,
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger(?P<format>.json|.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),

    url(r'^admin/', admin.site.urls),
    url(f'^snippets/', include('snippets.urls')),
]
