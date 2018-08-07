import json
from collections import OrderedDict

import pytest
from django.conf.urls import url
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from drf_yasg import codecs, openapi
from drf_yasg.codecs import yaml_sane_load
from drf_yasg.errors import SwaggerGenerationError
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.utils import swagger_auto_schema


def test_schema_is_valid(swagger, codec_yaml):
    codec_yaml.encode(swagger)


def test_invalid_schema_fails(codec_json, mock_schema_request):
    # noinspection PyTypeChecker
    bad_generator = OpenAPISchemaGenerator(
        info=openapi.Info(
            title="Test generator", default_version="v1",
            contact=openapi.Contact(name=69, email=[])
        ),
        version="v2",
    )

    swagger = bad_generator.get_schema(mock_schema_request, True)
    with pytest.raises(codecs.SwaggerValidationError):
        codec_json.encode(swagger)


def test_json_codec_roundtrip(codec_json, swagger, validate_schema):
    json_bytes = codec_json.encode(swagger)
    validate_schema(json.loads(json_bytes.decode('utf-8')))


def test_yaml_codec_roundtrip(codec_yaml, swagger, validate_schema):
    yaml_bytes = codec_yaml.encode(swagger)
    assert b'omap' not in yaml_bytes  # ensure no ugly !!omap is outputted
    assert b'&id' not in yaml_bytes and b'*id' not in yaml_bytes  # ensure no YAML references are generated
    validate_schema(yaml_sane_load(yaml_bytes.decode('utf-8')))


def test_yaml_and_json_match(codec_yaml, codec_json, swagger):
    yaml_schema = yaml_sane_load(codec_yaml.encode(swagger).decode('utf-8'))
    json_schema = json.loads(codec_json.encode(swagger).decode('utf-8'), object_pairs_hook=OrderedDict)
    assert yaml_schema == json_schema


def test_basepath_only(mock_schema_request):
    with pytest.raises(SwaggerGenerationError):
        generator = OpenAPISchemaGenerator(
            info=openapi.Info(title="Test generator", default_version="v1"),
            version="v2",
            url='/basepath/',
        )

        generator.get_schema(mock_schema_request, public=True)


def test_no_netloc(mock_schema_request):
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
        url='',
    )

    swagger = generator.get_schema(mock_schema_request, public=True)
    assert 'host' not in swagger and 'schemes' not in swagger
    assert swagger['info']['version'] == 'v2'


def test_securiy_requirements(swagger_settings, mock_schema_request):
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
        url='',
    )
    swagger_settings['SECURITY_REQUIREMENTS'] = []

    swagger = generator.get_schema(mock_schema_request, public=True)
    assert swagger['security'] == []


def test_replaced_serializer():
    class DetailSerializer(serializers.Serializer):
        detail = serializers.CharField()

    class DetailViewSet(viewsets.ViewSet):
        serializer_class = DetailSerializer

        @swagger_auto_schema(responses={404: openapi.Response("Not found or Not accessible", DetailSerializer)})
        def retrieve(self, request, pk=None):
            serializer = DetailSerializer({'detail': None})
            return Response(serializer.data)

    router = routers.DefaultRouter()
    router.register(r'details', DetailViewSet, base_name='details')

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
        url='',
        patterns=router.urls
    )

    for _ in range(3):
        swagger = generator.get_schema(None, True)
        assert 'Detail' in swagger['definitions']
        assert 'detail' in swagger['definitions']['Detail']['properties']
        responses = swagger['paths']['/details/{id}/']['get']['responses']
        assert '404' in responses
        assert responses['404']['schema']['$ref'] == "#/definitions/Detail"


def test_url_order():
    # this view with description override should show up in the schema ...
    @swagger_auto_schema(method='get', operation_description="description override")
    @api_view()
    def test_override(request, pk=None):
        return Response({"message": "Hello, world!"})

    # ... instead of this view which appears later in the url patterns
    @api_view()
    def test_view(request, pk=None):
        return Response({"message": "Hello, world!"})

    patterns = [
        url(r'^/test/$', test_override),
        url(r'^/test/$', test_view),
    ]

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
        url='',
        patterns=patterns
    )

    # description override is successful
    swagger = generator.get_schema(None, True)
    assert swagger['paths']['/test/']['get']['description'] == 'description override'

    # get_endpoints only includes one endpoint
    assert len(generator.get_endpoints(None)['/test/'][1]) == 1


try:
    from rest_framework.decorators import action, MethodMapper
except ImportError:
    action = MethodMapper = None


@pytest.mark.skipif(not MethodMapper or not action, reason="action.mapping test (djangorestframework>=3.9 required)")
def test_action_mapping():
    class ActionViewSet(viewsets.ViewSet):
        @swagger_auto_schema(method='get', operation_id='mapping_get')
        @swagger_auto_schema(method='delete', operation_id='mapping_delete')
        @action(detail=False, methods=['get', 'delete'], url_path='test')
        def action_main(self, request):
            """mapping docstring get/delete"""
            pass

        @swagger_auto_schema(operation_id='mapping_post')
        @action_main.mapping.post
        def action_post(self, request):
            """mapping docstring post"""
            pass

    router = routers.DefaultRouter()
    router.register(r'action', ActionViewSet, base_name='action')

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
        url='',
        patterns=router.urls
    )

    for _ in range(3):
        swagger = generator.get_schema(None, True)
        action_ops = swagger['paths']['/test/']
        methods = ['get', 'post', 'delete']
        assert all(mth in action_ops for mth in methods)
        assert all(action_ops[mth]['operationId'] == 'mapping_' + mth for mth in methods)
        assert action_ops['post']['description'] == 'mapping docstring post'
        assert action_ops['get']['description'] == 'mapping docstring get/delete'
        assert action_ops['delete']['description'] == 'mapping docstring get/delete'
