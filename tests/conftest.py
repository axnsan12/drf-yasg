import copy
import json
import os
from collections import OrderedDict
from io import StringIO

import pytest
from datadiff.tools import assert_equal
from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from drf_yasg import codecs, openapi
from drf_yasg.codecs import yaml_sane_dump, yaml_sane_load
from drf_yasg.generators import OpenAPISchemaGenerator


@pytest.fixture
def mock_schema_request(db):
    from rest_framework.test import force_authenticate

    factory = APIRequestFactory()
    user = User.objects.get(username='admin')
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
def swagger_dict(swagger, codec_json):
    json_bytes = codec_json.encode(swagger)
    return json.loads(json_bytes.decode('utf-8'), object_pairs_hook=OrderedDict)


@pytest.fixture
def validate_schema():
    def validate_schema(swagger):
        try:
            from flex.core import parse as validate_flex

            validate_flex(copy.deepcopy(swagger))
        except ImportError:
            pass

        from swagger_spec_validator.validator20 import validate_spec as validate_ssv

        validate_ssv(copy.deepcopy(swagger))

    return validate_schema


@pytest.fixture
def call_generate_swagger():
    def call_generate_swagger(output_file='-', overwrite=False, format='', api_url='',
                              mock=False, user=None, private=False, generator_class_name='', **kwargs):
        out = StringIO()
        call_command(
            'generate_swagger', stdout=out,
            output_file=output_file, overwrite=overwrite, format=format, api_url=api_url, mock=mock, user=user,
            private=private, generator_class_name=generator_class_name, **kwargs
        )
        return out.getvalue()

    return call_generate_swagger


@pytest.fixture
def compare_schemas():
    def compare_schemas(schema1, schema2):
        schema1 = OrderedDict(schema1)
        schema2 = OrderedDict(schema2)
        ignore = ['info', 'host', 'schemes', 'basePath', 'securityDefinitions']
        for attr in ignore:
            schema1.pop(attr, None)
            schema2.pop(attr, None)

        # print diff between YAML strings because it's prettier
        assert_equal(yaml_sane_dump(schema1, binary=False), yaml_sane_dump(schema2, binary=False))

    return compare_schemas


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
        return yaml_sane_load(reference)
