import pytest

from drf_yasg.errors import SwaggerGenerationError
from drf_yasg.codecs import yaml_sane_load


def _get_versioned_schema(prefix, client, validate_schema, path='/snippets/'):
    response = client.get(prefix + '/swagger.yaml')
    assert response.status_code == 200
    swagger = yaml_sane_load(response.content.decode('utf-8'))
    _check_base(swagger, prefix, validate_schema, path)
    return swagger


def _get_versioned_schema_management(prefix, call_generate_swagger, validate_schema, kwargs, path='/snippets/'):
    output = call_generate_swagger(format='yaml', api_url='http://localhost' + prefix + '/swagger.yaml', **kwargs)
    swagger = yaml_sane_load(output)
    _check_base(swagger, prefix, validate_schema, path)
    return swagger


def _check_base(swagger, prefix, validate_schema, path):
    assert swagger['basePath'] == prefix
    validate_schema(swagger)
    assert path in swagger['paths']
    return swagger


def _check_v1(swagger, path='/snippets/'):
    assert swagger['info']['version'] == '1.0'
    versioned_post = swagger['paths'][path]['post']
    assert versioned_post['responses']['201']['schema']['$ref'] == '#/definitions/Snippet'
    assert 'v2field' not in swagger['definitions']['Snippet']['properties']
    assert '/snippets_excluded/' not in swagger['paths']


def _check_v2(swagger, path='/snippets/'):
    assert swagger['info']['version'] == '2.0'
    versioned_post = swagger['paths'][path]['post']
    assert versioned_post['responses']['201']['schema']['$ref'] == '#/definitions/SnippetV2'
    assert 'v2field' in swagger['definitions']['SnippetV2']['properties']
    v2field = swagger['definitions']['SnippetV2']['properties']['v2field']
    assert v2field['description'] == 'version 2.0 field'
    assert '/snippets_excluded/' not in swagger['paths']


@pytest.mark.urls('urlconfs.url_versioning')
def test_url_v2(client, validate_schema):
    swagger = _get_versioned_schema('/versioned/url/v2.0', client, validate_schema)
    _check_v2(swagger)


@pytest.mark.urls('urlconfs.url_versioning_extra')
def test_url_v2_extra(client, validate_schema):
    swagger = _get_versioned_schema('/versioned/url/v2.0', client, validate_schema, path='/extra/snippets/')
    _check_v2(swagger, path='/extra/snippets/')


@pytest.mark.urls('urlconfs.overrided_serializer_name')
def test_url_same_ref_names(client, validate_schema):
    for v in {'v1.0', 'v2.0'}:
        try:
            client.get(f'/versioned/url/{v}/swagger.yaml')
        except SwaggerGenerationError:
            pass
        else:
            raise AssertionError('drf_yasg.errors.SwaggerGenerationError is not raised')


@pytest.mark.urls('urlconfs.url_versioning')
def test_url_v1(client, validate_schema):
    swagger = _get_versioned_schema('/versioned/url/v1.0', client, validate_schema)
    _check_v1(swagger)


@pytest.mark.urls('urlconfs.ns_versioning')
def test_ns_v1(client, validate_schema):
    swagger = _get_versioned_schema('/versioned/ns/v1.0', client, validate_schema)
    _check_v1(swagger)


@pytest.mark.urls('urlconfs.ns_versioning')
def test_ns_v2(client, validate_schema):
    swagger = _get_versioned_schema('/versioned/ns/v2.0', client, validate_schema)
    _check_v2(swagger)


@pytest.mark.urls('urlconfs.url_versioning')
def test_url_v2_management(call_generate_swagger, validate_schema):
    kwargs = {'api_version': '2.0'}
    swagger = _get_versioned_schema_management('/versioned/url/v2.0', call_generate_swagger, validate_schema, kwargs)
    _check_v2(swagger)


@pytest.mark.urls('urlconfs.url_versioning_extra')
def test_url_v2_management_extra(call_generate_swagger, validate_schema):
    kwargs = {'api_version': '2.0'}
    swagger = _get_versioned_schema_management(
        '/versioned/url/v2.0',
        call_generate_swagger,
        validate_schema,
        kwargs,
        path='/extra/snippets/'
    )
    _check_v2(swagger, path='/extra/snippets/')


@pytest.mark.urls('urlconfs.ns_versioning')
def test_ns_v2_management(call_generate_swagger, validate_schema):
    kwargs = {'api_version': '2.0'}
    swagger = _get_versioned_schema_management('/versioned/ns/v2.0', call_generate_swagger, validate_schema, kwargs)
    _check_v2(swagger)
