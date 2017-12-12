import json

import pytest
from requests import Request
from rest_framework import permissions
from rest_framework.test import APIRequestFactory
from ruamel import yaml

from drf_swagger import openapi, codecs
from drf_swagger.generators import OpenAPISchemaGenerator
from drf_swagger.views import get_schema_view


def test_schema_generates_without_errors(generator):
    generator.get_schema(None, True)


def test_schema_is_valid(generator, codec_yaml):
    swagger = generator.get_schema(request=None, public=False)
    codec_yaml.encode(swagger)


def test_non_public(generator, codec_yaml):
    factory = APIRequestFactory()
    request = factory.get('/swagger.json')
    view = get_schema_view(openapi.Info('bla', 'ble'), public=False, permission_classes=(permissions.AllowAny,))
    view = view.without_ui()
    response = view(request)
    swagger = response.data
    assert len(swagger['paths']) == 0


def test_invalid_schema_fails(codec_json):
    # noinspection PyTypeChecker
    bad_generator = OpenAPISchemaGenerator(
        info=openapi.Info(
            title="Test generator", default_version="v1",
            contact=openapi.Contact(name=69, email=[])
        ),
        version="v2",
    )

    swagger = bad_generator.get_schema(None, True)
    with pytest.raises(codecs.SwaggerValidationError):
        codec_json.encode(swagger)


def test_json_codec_roundtrip(codec_json, generator, validate_schema):
    swagger = generator.get_schema(None, True)
    json_bytes = codec_json.encode(swagger)
    validate_schema(json.loads(json_bytes.decode('utf-8')))


def test_yaml_codec_roundtrip(codec_yaml, generator, validate_schema):
    swagger = generator.get_schema(None, True)
    yaml_bytes = codec_yaml.encode(swagger)
    assert b'omap' not in yaml_bytes
    validate_schema(yaml.safe_load(yaml_bytes.decode('utf-8')))

