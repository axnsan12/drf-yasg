import copy
import json
import os

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from ruamel import yaml

from drf_yasg import openapi, codecs
from drf_yasg.generators import OpenAPISchemaGenerator


@pytest.fixture
def mock_schema_request(db):
    from rest_framework.test import force_authenticate

    factory = APIRequestFactory()
    user = User.objects.create_user(username='admin', is_staff=True, is_superuser=True)

    request = factory.get('/swagger.json')
    force_authenticate(request, user=user)
    request = APIView().initialize_request(request)
    return request


@pytest.fixture
def codec_json():
    return codecs.OpenAPICodecJson(['flex', 'ssv'])


@pytest.fixture
def codec_yaml():
    return codecs.OpenAPICodecYaml(['ssv', 'flex'])


@pytest.fixture
def swagger(mock_schema_request):
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
    )
    return generator.get_schema(mock_schema_request, True)


@pytest.fixture
def swagger_dict(swagger):
    json_bytes = codec_json().encode(swagger)
    return json.loads(json_bytes.decode('utf-8'))


@pytest.fixture
def validate_schema(db):
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
