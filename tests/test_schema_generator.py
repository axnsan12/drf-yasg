import json

import pytest
from drf_swagger import openapi, codecs
from drf_swagger.generators import OpenAPISchemaGenerator
from ruamel import yaml


def validate_schema(swagger):
    from flex.core import parse as validate_flex
    from swagger_spec_validator.validator20 import validate_spec as validate_ssv

    validate_flex(swagger)
    validate_ssv(swagger)


def test_schema_generates_without_errors(generator):
    generator.get_schema(None, True)


def test_schema_is_valid(generator, codec_yaml):
    swagger = generator.get_schema(None, True)
    codec_yaml.encode(swagger)


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


def test_json_codec_roundtrip(codec_json, generator):
    swagger = generator.get_schema(None, True)
    json_bytes = codec_json.encode(swagger)
    validate_schema(json.loads(json_bytes.decode('utf-8')))


def test_yaml_codec_roundtrip(codec_yaml, generator):
    swagger = generator.get_schema(None, True)
    json_bytes = codec_yaml.encode(swagger)
    validate_schema(yaml.safe_load(json_bytes.decode('utf-8')))
