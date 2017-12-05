import json

from ruamel import yaml


def _validate_text_schema_view(client, validate_schema, path, loader):
    response = client.get(path)
    assert response.status_code == 200
    validate_schema(loader(response.content))


def _validate_ui_schema_view(client, path, string):
    response = client.get(path)
    assert response.status_code == 200
    assert string in response.content.decode('utf-8')


def test_swagger_json(client, validate_schema):
    _validate_text_schema_view(client, validate_schema, "/swagger.json", json.loads)


def test_swagger_yaml(client, validate_schema):
    _validate_text_schema_view(client, validate_schema, "/swagger.yaml", yaml.safe_load)


def test_exception_middleware(client, bad_settings):
    response = client.get('/swagger.json')
    assert response.status_code == 500
    assert 'errors' in json.loads(response.content)


def test_swagger_ui(client, validate_schema):
    _validate_ui_schema_view(client, '/swagger/', 'swagger-ui-dist/swagger-ui-bundle.js')
    _validate_text_schema_view(client, validate_schema, '/swagger/?format=openapi', json.loads)


def test_redoc(client, validate_schema):
    _validate_ui_schema_view(client, '/redoc/', 'redoc/redoc.min.js')
    _validate_text_schema_view(client, validate_schema, '/redoc/?format=openapi', json.loads)
