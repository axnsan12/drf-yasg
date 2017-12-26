import warnings
from functools import wraps

from django.utils.cache import add_never_cache_headers
from django.utils.decorators import available_attrs
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .generators import OpenAPISchemaGenerator
from .renderers import (
    SwaggerJSONRenderer, SwaggerYAMLRenderer, SwaggerUIRenderer, ReDocRenderer, OpenAPIRenderer,
)

SPEC_RENDERERS = (SwaggerYAMLRenderer, SwaggerJSONRenderer, OpenAPIRenderer)
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


def get_schema_view(info, url=None, patterns=None, urlconf=None, public=False, validators=None,
                    generator_class=OpenAPISchemaGenerator,
                    authentication_classes=api_settings.DEFAULT_AUTHENTICATION_CLASSES,
                    permission_classes=api_settings.DEFAULT_PERMISSION_CLASSES):
    """
    Create a SchemaView class with default renderers and generators.

    :param .Info info: Required. Swagger API Info object
    :param str url: API base url; if left blank will be deduced from the location the view is served at
    :param patterns: passed to SchemaGenerator
    :param urlconf: passed to SchemaGenerator
    :param bool public: if False, includes only endpoints the current user has access to
    :param list validators: a list of validator names to apply; allowed values are ``flex``, ``ssv``
    :param type generator_class: schema generator class to use; should be a subclass of :class:`.OpenAPISchemaGenerator`
    :param tuple authentication_classes: authentication classes for the schema view itself
    :param tuple permission_classes: permission classes for the schema view itself
    :return: SchemaView class
    :rtype: type[.SchemaView]
    """
    _public = public
    _generator_class = generator_class
    _auth_classes = authentication_classes
    _perm_classes = permission_classes
    validators = validators or []
    _spec_renderers = tuple(renderer.with_validators(validators) for renderer in SPEC_RENDERERS)

    class SchemaView(APIView):
        _ignore_model_permissions = True
        schema = None  # exclude from schema
        public = _public
        generator_class = _generator_class
        authentication_classes = _auth_classes
        permission_classes = _perm_classes
        renderer_classes = _spec_renderers

        def get(self, request, version='', format=None):
            generator = self.generator_class(info, request.version or version or '', url, patterns, urlconf)
            schema = generator.get_schema(request, self.public)
            if schema is None:
                raise exceptions.PermissionDenied()  # pragma: no cover
            return Response(schema)

        @classmethod
        def apply_cache(cls, view, cache_timeout, cache_kwargs):
            """Override this method to customize how caching is applied to the view.

            Arguments described in :meth:`.as_cached_view`.
            """
            if not cls.public:
                view = vary_on_headers('Cookie', 'Authorization')(view)
            view = cache_page(cache_timeout, **cache_kwargs)(view)
            view = deferred_never_cache(view)  # disable in-browser caching
            return view

        @classmethod
        def as_cached_view(cls, cache_timeout=0, cache_kwargs=None, **initkwargs):
            """
            Calls .as_view() and wraps the result in a cache_page decorator.
            See https://docs.djangoproject.com/en/1.11/topics/cache/

            :param int cache_timeout: same as cache_page; set to 0 for no cache
            :param dict cache_kwargs: dictionary of kwargs to be passed to cache_page
            :param initkwargs: kwargs for .as_view()
            :return: a view instance
            """
            cache_kwargs = cache_kwargs or {}
            view = cls.as_view(**initkwargs)
            if cache_timeout != 0:
                view = cls.apply_cache(view, cache_timeout, cache_kwargs)
            elif cache_kwargs:
                warnings.warn("cache_kwargs ignored because cache_timeout is 0 (disabled)")
            return view

        @classmethod
        def without_ui(cls, cache_timeout=0, cache_kwargs=None):
            """
            Instantiate this view with just JSON and YAML renderers, optionally wrapped with cache_page.
            See https://docs.djangoproject.com/en/1.11/topics/cache/.

            :param int cache_timeout: same as cache_page; set to 0 for no cache
            :param dict cache_kwargs: dictionary of kwargs to be passed to cache_page
            :return: a view instance
            """
            return cls.as_cached_view(cache_timeout, cache_kwargs, renderer_classes=_spec_renderers)

        @classmethod
        def with_ui(cls, renderer='swagger', cache_timeout=0, cache_kwargs=None):
            """
            Instantiate this view with a Web UI renderer, optionally wrapped with cache_page.
            See https://docs.djangoproject.com/en/1.11/topics/cache/.

            :param str renderer: UI renderer; allowed values are ``swagger``, ``redoc``
            :param int cache_timeout: same as cache_page; set to 0 for no cache
            :param dict cache_kwargs: dictionary of kwargs to be passed to cache_page
            :return: a view instance
            """
            assert renderer in UI_RENDERERS, "supported default renderers are " + ", ".join(UI_RENDERERS)
            renderer_classes = UI_RENDERERS[renderer] + _spec_renderers

            return cls.as_cached_view(cache_timeout, cache_kwargs, renderer_classes=renderer_classes)

    return SchemaView
