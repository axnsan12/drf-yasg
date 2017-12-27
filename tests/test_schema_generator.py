import json
from collections import OrderedDict

import pytest

from drf_yasg import codecs, openapi
from drf_yasg.codecs import yaml_sane_load
from drf_yasg.generators import OpenAPISchemaGenerator


def test_schema_is_valid(swagger, codec_yaml):
    codec_yaml.encode(swagger)


def test_invalid_schema_fails(codec_json, mock_schema_request):
    # noinspection PyTypeChecker
    bad_generator = OpenAPISchemaGenerator(
        info=openapi.Info(
            title="Test generator", default_version="v1",
            contact=openapi.Contact(name=69, email=[])
        ),
        version="v2",
    )

    swagger = bad_generator.get_schema(mock_schema_request, True)
    with pytest.raises(codecs.SwaggerValidationError):
        codec_json.encode(swagger)


def test_json_codec_roundtrip(codec_json, swagger, validate_schema):
    json_bytes = codec_json.encode(swagger)
    validate_schema(json.loads(json_bytes.decode('utf-8')))


def test_yaml_codec_roundtrip(codec_yaml, swagger, validate_schema):
    yaml_bytes = codec_yaml.encode(swagger)
    assert b'omap' not in yaml_bytes  # ensure no ugly !!omap is outputted
    assert b'&id' not in yaml_bytes and b'*id' not in yaml_bytes  # ensure no YAML references are generated
    validate_schema(yaml_sane_load(yaml_bytes.decode('utf-8')))


def test_yaml_and_json_match(codec_yaml, codec_json, swagger):
    yaml_schema = yaml_sane_load(codec_yaml.encode(swagger).decode('utf-8'))
    json_schema = json.loads(codec_json.encode(swagger).decode('utf-8'), object_pairs_hook=OrderedDict)
    assert yaml_schema == json_schema


def test_basepath_only(mock_schema_request):
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
        url='/basepath/',
    )

    swagger = generator.get_schema(mock_schema_request, public=True)
    assert 'host' not in swagger
    assert 'schemes' not in swagger
    assert swagger['basePath'] == '/'  # base path is not implemented for now
    assert swagger['info']['version'] == 'v2'
