import warnings
from functools import wraps

from django.utils.cache import add_never_cache_headers
from django.utils.decorators import available_attrs
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import exceptions, renderers
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .generators import OpenAPISchemaGenerator
from .renderers import (
    SwaggerJSONRenderer, SwaggerYAMLRenderer, SwaggerUIRenderer, ReDocRenderer, OpenAPIRenderer,
)

SPEC_RENDERERS = (SwaggerYAMLRenderer, SwaggerJSONRenderer, OpenAPIRenderer)
SPEC_RENDERERS = {
    False: tuple(renderer.with_validators([]) for renderer in SPEC_RENDERERS),
    True: SPEC_RENDERERS,
}
UI_RENDERERS = {
    'swagger': (SwaggerUIRenderer, ReDocRenderer),
    'redoc': (ReDocRenderer, SwaggerUIRenderer),
}


def deferred_never_cache(view_func):
    """
    Decorator that adds headers to a response so that it will
    never be cached.
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)

        # It is necessary to defer the add_never_cache_headers call because
        # cache_page also defers its cache update operation; if we do not defer
        # this, cache_page will give up because it will see and obey the "never
        # cache" headers
        def callback(response):
            add_never_cache_headers(response)
            return response

        response.add_post_render_callback(callback)
        return response

    return _wrapped_view_func


def get_schema_view(info, url=None, patterns=None, urlconf=None, *, public=False, validate=False,
                    authentication_classes=api_settings.DEFAULT_AUTHENTICATION_CLASSES,
                    permission_classes=api_settings.DEFAULT_PERMISSION_CLASSES):
    _auth_classes = authentication_classes
    _perm_classes = permission_classes
    _public = public

    class SchemaView(APIView):
        _ignore_model_permissions = True
        schema = None  # exclude from schema
        public = _public
        authentication_classes = _auth_classes
        permission_classes = _perm_classes
        renderer_classes = SPEC_RENDERERS[bool(validate)]

        def __init__(self, **kwargs):
            super(SchemaView, self).__init__(**kwargs)
            if self.renderer_classes is None:
                if renderers.BrowsableAPIRenderer in api_settings.DEFAULT_RENDERER_CLASSES:
                    self.renderer_classes = [
                        renderers.CoreJSONRenderer,
                        renderers.BrowsableAPIRenderer,
                    ]
                else:
                    self.renderer_classes = [renderers.CoreJSONRenderer]

        def get(self, request, version='', format=None):
            generator = OpenAPISchemaGenerator(info, version, url, patterns, urlconf)
            schema = generator.get_schema(request, self.public)
            if schema is None:
                raise exceptions.PermissionDenied()
            return Response(schema)

        @classmethod
        def _cached(cls, view, cache_timeout, cache_kwargs):
            if cache_timeout != 0:
                view = vary_on_headers('Cookie', 'Authorization', 'Accept')(view)
                view = cache_page(cache_timeout, **cache_kwargs)(view)
                view = deferred_never_cache(view)  # disable in-browser caching
            elif cache_kwargs:
                warnings.warn("cache_kwargs ignored because cache_timeout is 0 (disabled)")
            return view

        @classmethod
        def as_cached_view(cls, cache_timeout=0, **cache_kwargs):
            return cls._cached(cls.as_view(), cache_timeout, cache_kwargs)

        @classmethod
        def without_ui(cls, cache_timeout=0, **cache_kwargs):
            renderer_classes = SPEC_RENDERERS[bool(validate)]
            return cls._cached(cls.as_view(renderer_classes=renderer_classes), cache_timeout, cache_kwargs)

        @classmethod
        def with_ui(cls, renderer='swagger', cache_timeout=0, **cache_kwargs):
            assert renderer in UI_RENDERERS, "supported default renderers are " + ", ".join(UI_RENDERERS)
            renderer_classes = (*UI_RENDERERS[renderer], *SPEC_RENDERERS[bool(validate)])

            view = cls.as_view(renderer_classes=renderer_classes)
            return cls._cached(view, cache_timeout, cache_kwargs)

    return SchemaView
