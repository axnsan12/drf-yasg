import json
from collections import OrderedDict

import pytest

try:
    import coreschema
except ImportError:
    coreschema = None

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


@pytest.mark.skipif(coreschema is None, reason="Do not test without coreschema.")
@pytest.mark.urls('urlconfs.coreschema')
def test_paginator_schema(client, swagger_settings):
    swagger_settings['DEFAULT_FILTER_INSPECTORS'] = [
        'drf_yasg.inspectors.CoreAPICompatInspector',
        'drf_yasg.inspectors.DrfAPICompatInspector',
    ]
    swagger_settings['DEFAULT_PAGINATOR_INSPECTORS'] = [
        'drf_yasg.inspectors.CoreAPICompatInspector',
        'drf_yasg.inspectors.DrfAPICompatInspector',
    ]

    response = client.get('/versioned/url/v1.0/swagger.yaml')
    swagger = yaml_sane_load(response.content.decode('utf-8'))

    assert swagger['paths']['/snippets/']['get']['responses']['200']['schema']['type'] == 'object'
    assert swagger['paths']['/snippets/']['get']['responses']['200']['schema']['required'] == ['results']
    assert swagger['paths']['/snippets/']['get']['parameters'][0]['name'] == 'test_param'
    assert swagger['paths']['/snippets/']['get']['parameters'][0]['type'] == 'string'
    assert swagger['paths']['/snippets/']['get']['parameters'][1]['name'] == 'limit'
    assert swagger['paths']['/snippets/']['get']['parameters'][1]['in'] == 'query'
    assert swagger['paths']['/snippets/']['get']['parameters'][1]['type'] == 'integer'

    assert swagger['paths']['/other_snippets/']['get']['responses']['200']['schema']['type'] == 'array'
    assert swagger['paths']['/other_snippets/']['get']['parameters'][0]['name'] == 'limit'
    assert swagger['paths']['/other_snippets/']['get']['parameters'][0]['in'] == 'query'
    assert swagger['paths']['/other_snippets/']['get']['parameters'][0]['type'] == 'integer'


@pytest.mark.urls('urlconfs.additional_fields_checks')
def test_extra_field_inspections(client, swagger_settings):
    # swagger_settings[]
    response = client.get('/versioned/url/v1.0/swagger.json')
    swagger = json.loads(response.content.decode('utf-8'))

    assert swagger['definitions']['Snippets']['properties']['url']['type'] == 'string'
    assert swagger['definitions']['Snippets']['properties']['url']['format'] == 'uri'
    assert swagger['definitions']['Snippets']['properties']['ipv4']['type'] == 'string'
    assert swagger['definitions']['Snippets']['properties']['uri']['type'] == 'string'
    assert swagger['definitions']['Snippets']['properties']['uri']['format'] == 'uri'
    assert swagger['definitions']['Snippets']['properties']['tracks']['type'] == 'array'
    assert swagger['definitions']['Snippets']['properties']['tracks']['items']['type'] == 'string'

    assert swagger['definitions']['SnippetsV2']['properties']['url']['type'] == 'string'
    assert swagger['definitions']['SnippetsV2']['properties']['url']['format'] == 'uri'

    assert swagger['definitions']['SnippetsV2']['properties']['other_owner_snippets']['type'] == 'array'
    assert swagger['definitions']['SnippetsV2']['properties']['other_owner_snippets']['items']['type'] == 'integer'

    # Cannt check type of queryset in property descriptor.
    assert swagger['definitions']['SnippetsV2']['properties']['owner_snippets']['type'] == 'array'
    assert swagger['definitions']['SnippetsV2']['properties']['owner_snippets']['items']['type'] == 'string'
