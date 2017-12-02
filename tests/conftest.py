import pytest
from ruamel import yaml

from drf_swagger import openapi, codecs
from drf_swagger.generators import OpenAPISchemaGenerator


@pytest.fixture
def generator():
    return OpenAPISchemaGenerator(
        info=openapi.Info("Test generator", "v1"),
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
    json_bytes = codec_yaml().encode(swagger)
    return yaml.safe_load(json_bytes.decode('utf-8'))
