import json
from collections import OrderedDict

import pytest

from drf_yasg.codecs import yaml_sane_load


def _validate_text_schema_view(client, validate_schema, path, loader):
    response = client.get(path)
    assert response.status_code == 200
    validate_schema(loader(response.content.decode('utf-8')))


def _validate_ui_schema_view(client, path, string):
    response = client.get(path)
    assert response.status_code == 200
    assert string in response.content.decode('utf-8')


def test_swagger_json(client, validate_schema):
    _validate_text_schema_view(client, validate_schema, "/swagger.json", json.loads)


def test_swagger_yaml(client, validate_schema):
    _validate_text_schema_view(client, validate_schema, "/swagger.yaml", yaml_sane_load)


def test_exception_middleware(client, swagger_settings, db):
    swagger_settings['SECURITY_DEFINITIONS'] = {
        'bad': {
            'bad_attribute': 'should not be accepted'
        }
    }

    response = client.get('/swagger.json')
    assert response.status_code == 500
    assert 'errors' in json.loads(response.content.decode('utf-8'))


def test_swagger_ui(client, validate_schema):
    _validate_ui_schema_view(client, '/swagger/', 'swagger-ui-dist/swagger-ui-bundle.js')
    _validate_text_schema_view(client, validate_schema, '/swagger/?format=openapi', json.loads)


def test_redoc(client, validate_schema):
    _validate_ui_schema_view(client, '/redoc/', 'redoc/redoc.min.js')
    _validate_text_schema_view(client, validate_schema, '/redoc/?format=openapi', json.loads)


def test_caching(client, validate_schema):
    prev_schema = None

    for i in range(3):
        _validate_text_schema_view(client, validate_schema, '/cached/swagger.yaml', yaml_sane_load)

        json_schema = client.get('/cached/swagger.json')
        assert json_schema.status_code == 200
        json_schema = json.loads(json_schema.content.decode('utf-8'), object_pairs_hook=OrderedDict)
        if prev_schema is None:
            validate_schema(json_schema)
            prev_schema = json_schema
        else:
            from datadiff.tools import assert_equal
            assert_equal(prev_schema, json_schema)


@pytest.mark.urls('urlconfs.non_public_urls')
def test_non_public(client):
    response = client.get('/private/swagger.yaml')
    swagger = yaml_sane_load(response.content.decode('utf-8'))
    assert len(swagger['paths']) == 0
