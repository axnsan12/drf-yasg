from django.shortcuts import render, resolve_url
from rest_framework.renderers import BaseRenderer, TemplateHTMLRenderer
from rest_framework.utils import json

from drf_yasg.openapi import Swagger

from .app_settings import redoc_settings, swagger_settings
from .codecs import VALIDATORS, OpenAPICodecJson, OpenAPICodecYaml


class _SpecRenderer(BaseRenderer):
    """Base class for text renderers. Handles encoding and validation."""
    charset = None
    validators = []
    codec_class = None

    @classmethod
    def with_validators(cls, validators):
        assert all(vld in VALIDATORS for vld in validators), "allowed validators are " + ", ".join(VALIDATORS)
        return type(cls.__name__, (cls,), {'validators': validators})

    def render(self, data, media_type=None, renderer_context=None):
        assert self.codec_class, "must override codec_class"
        codec = self.codec_class(self.validators)
        return codec.encode(data)


class OpenAPIRenderer(_SpecRenderer):
    """Renders the schema as a JSON document with the ``application/openapi+json`` specific mime type."""
    media_type = 'application/openapi+json'
    format = 'openapi'
    codec_class = OpenAPICodecJson


class SwaggerJSONRenderer(_SpecRenderer):
    """Renders the schema as a JSON document with the generic ``application/json`` mime type."""
    media_type = 'application/json'
    format = '.json'
    codec_class = OpenAPICodecJson


class SwaggerYAMLRenderer(_SpecRenderer):
    """Renders the schema as a YAML document."""
    media_type = 'application/yaml'
    format = '.yaml'
    codec_class = OpenAPICodecYaml


class _UIRenderer(BaseRenderer):
    """Base class for web UI renderers. Handles loading and passing settings to the appropriate template."""
    media_type = 'text/html'
    charset = 'utf-8'
    template = ''

    def render(self, swagger, accepted_media_type=None, renderer_context=None):
        if not isinstance(swagger, Swagger):
            # if `swagger` is not a ``Swagger`` object, it means we somehow got a non-success ``Response``
            # in that case, it's probably better to let the default ``TemplateHTMLRenderer`` render it
            # see https://github.com/axnsan12/drf-yasg/issues/58
            return TemplateHTMLRenderer().render(swagger, accepted_media_type, renderer_context)
        self.set_context(renderer_context, swagger)
        return render(
            renderer_context['request'],
            self.template,
            renderer_context
        )

    def set_context(self, renderer_context, swagger):
        renderer_context['title'] = swagger.info.title
        renderer_context['version'] = swagger.info.version
        renderer_context['swagger_settings'] = json.dumps(self.get_swagger_ui_settings())
        renderer_context['redoc_settings'] = json.dumps(self.get_redoc_settings())
        renderer_context['oauth2_config'] = json.dumps(self.get_oauth2_config())
        renderer_context['USE_SESSION_AUTH'] = swagger_settings.USE_SESSION_AUTH
        renderer_context.update(self.get_auth_urls())

    def get_auth_urls(self):
        urls = {}
        if swagger_settings.LOGIN_URL is not None:
            urls['LOGIN_URL'] = resolve_url(swagger_settings.LOGIN_URL)
        if swagger_settings.LOGOUT_URL is not None:
            urls['LOGOUT_URL'] = resolve_url(swagger_settings.LOGOUT_URL)

        return urls

    def get_swagger_ui_settings(self):
        data = {
            'operationsSorter': swagger_settings.OPERATIONS_SORTER,
            'tagsSorter': swagger_settings.TAGS_SORTER,
            'docExpansion': swagger_settings.DOC_EXPANSION,
            'deepLinking': swagger_settings.DEEP_LINKING,
            'showExtensions': swagger_settings.SHOW_EXTENSIONS,
            'defaultModelRendering': swagger_settings.DEFAULT_MODEL_RENDERING,
            'defaultModelExpandDepth': swagger_settings.DEFAULT_MODEL_DEPTH,
            'defaultModelsExpandDepth': swagger_settings.DEFAULT_MODEL_DEPTH,
            'oauth2RedirectUrl': swagger_settings.OAUTH2_REDIRECT_URL,
        }
        data = {k: v for k, v in data.items() if v is not None}
        if swagger_settings.VALIDATOR_URL != '':
            data['validatorUrl'] = swagger_settings.VALIDATOR_URL

        return data

    def get_redoc_settings(self):
        data = {
            'lazyRendering': redoc_settings.LAZY_RENDERING,
            'hideHostname': redoc_settings.HIDE_HOSTNAME,
            'expandResponses': redoc_settings.EXPAND_RESPONSES,
            'pathInMiddle': redoc_settings.PATH_IN_MIDDLE,
        }

        return data

    def get_oauth2_config(self):
        data = swagger_settings.OAUTH2_CONFIG
        assert isinstance(data, dict), "OAUTH2_CONFIG must be a dict"
        return data


class SwaggerUIRenderer(_UIRenderer):
    """Renders a swagger-ui web interface for schema browisng.
    Also requires :class:`.OpenAPIRenderer` as an available renderer on the same view.
    """
    template = 'drf-yasg/swagger-ui.html'
    format = 'swagger'


class ReDocRenderer(_UIRenderer):
    """Renders a ReDoc web interface for schema browisng.
    Also requires :class:`.OpenAPIRenderer` as an available renderer on the same view.
    """
    template = 'drf-yasg/redoc.html'
    format = 'redoc'


class ReDocAlphaRenderer(_UIRenderer):
    """Renders a ReDoc web interface for schema browisng.
    Also requires :class:`.OpenAPIRenderer` as an available renderer on the same view.
    """
    template = 'drf-yasg/redoc-alpha.html'
    format = 'redoc'
