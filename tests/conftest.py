import json
import os

import pytest
from ruamel import yaml

from drf_swagger import openapi, codecs
from drf_swagger.generators import OpenAPISchemaGenerator


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
def swagger_dict():
    swagger = generator().get_schema(None, True)
    json_bytes = codec_json().encode(swagger)
    return json.loads(json_bytes.decode('utf-8'))


@pytest.fixture
def validate_schema():
    def validate_schema(swagger):
        from flex.core import parse as validate_flex
        from swagger_spec_validator.validator20 import validate_spec as validate_ssv

        validate_flex(swagger)
        validate_ssv(swagger)

    return validate_schema


@pytest.fixture
def bad_settings():
    from drf_swagger.app_settings import swagger_settings, SWAGGER_DEFAULTS
    bad_security = {
        'bad': {
            'bad_attribute': 'should not be accepted'
        }
    }
    SWAGGER_DEFAULTS['SECURITY_DEFINITIONS'].update(bad_security)
    yield swagger_settings
    del SWAGGER_DEFAULTS['SECURITY_DEFINITIONS']['bad']


@pytest.fixture
def reference_schema():
    with open(os.path.join(os.path.dirname(__file__), 'reference.yaml')) as reference:
        return yaml.safe_load(reference)
