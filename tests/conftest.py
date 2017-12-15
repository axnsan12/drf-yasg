import copy
import json
import os

import pytest
from ruamel import yaml

from drf_yasg import openapi, codecs
from drf_yasg.generators import OpenAPISchemaGenerator


@pytest.fixture
def generator():
    return OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
    )


@pytest.fixture
def codec_json():
    return codecs.OpenAPICodecJson(['flex', 'ssv'])


@pytest.fixture
def codec_yaml():
    return codecs.OpenAPICodecYaml(['ssv', 'flex'])


@pytest.fixture
def swagger(generator):
    return generator.get_schema(None, True)


@pytest.fixture
def swagger_dict(generator):
    swagger = generator.get_schema(None, True)
    json_bytes = codec_json().encode(swagger)
    return json.loads(json_bytes.decode('utf-8'))


@pytest.fixture
def validate_schema():
    def validate_schema(swagger):
        from flex.core import parse as validate_flex
        from swagger_spec_validator.validator20 import validate_spec as validate_ssv

        validate_flex(copy.deepcopy(swagger))
        validate_ssv(copy.deepcopy(swagger))

    return validate_schema


@pytest.fixture
def swagger_settings(settings):
    swagger_settings = copy.deepcopy(settings.SWAGGER_SETTINGS)
    settings.SWAGGER_SETTINGS = swagger_settings
    return swagger_settings


@pytest.fixture
def redoc_settings(settings):
    redoc_settings = copy.deepcopy(settings.REDOC_SETTINGS)
    settings.REDOC_SETTINGS = redoc_settings
    return redoc_settings


@pytest.fixture
def reference_schema():
    with open(os.path.join(os.path.dirname(__file__), 'reference.yaml')) as reference:
        return yaml.safe_load(reference)
