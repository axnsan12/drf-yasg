import json
import typing
from collections import OrderedDict

import pytest
from django.contrib.postgres import fields as postgres_fields
from django.db import models
from django.urls import path
from django.utils.inspect import get_func_args
from django_fake_model import models as fake_models
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


def test_security_requirements(swagger_settings, mock_schema_request):
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
        url='',
    )
    swagger_settings['SECURITY_REQUIREMENTS'] = []

    swagger = generator.get_schema(mock_schema_request, public=True)
    assert swagger['security'] == []

    swagger_settings['SECURITY_REQUIREMENTS'] = None
    swagger_settings['SECURITY_DEFINITIONS'] = None

    swagger = generator.get_schema(mock_schema_request, public=True)
    assert 'security' not in swagger


def test_default_url(swagger_settings, mock_schema_request):
    swagger_settings['DEFAULT_API_URL'] = 'http://api.example.com'
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
    )

    swagger = generator.get_schema(public=True)
    assert swagger['host'] == 'api.example.com'
    assert swagger['basePath'] == '/'


def _basename_or_base_name(basename):
    # freaking DRF... TODO: remove when dropping support for DRF 3.8
    if 'basename' in get_func_args(routers.BaseRouter.register):
        return {'basename': basename}
    else:
        return {'base_name': basename}


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
    router.register(r'details', DetailViewSet, **_basename_or_base_name('details'))

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
        path('test/', test_override),
        path('test/', test_view),
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
    endpoints = generator.get_endpoints(None)
    assert len(endpoints['/test/'][1]) == 1


try:
    from rest_framework.decorators import MethodMapper, action
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
    router.register(r'action', ActionViewSet, **_basename_or_base_name('action'))

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


@pytest.mark.parametrize('choices, expected_type', [
    (['A', 'B'], openapi.TYPE_STRING),
    ([u'A', u'B'], openapi.TYPE_STRING),
    ([123, 456], openapi.TYPE_INTEGER),
    ([1.2, 3.4], openapi.TYPE_NUMBER),
    (['A', 456], openapi.TYPE_STRING)
])
def test_choice_field(choices, expected_type):
    class DetailSerializer(serializers.Serializer):
        detail = serializers.ChoiceField(choices)

    class DetailViewSet(viewsets.ViewSet):
        @swagger_auto_schema(responses={200: openapi.Response("OK", DetailSerializer)})
        def retrieve(self, request, pk=None):
            return Response({'detail': None})

    router = routers.DefaultRouter()
    router.register(r'details', DetailViewSet, **_basename_or_base_name('details'))

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version="v1"),
        patterns=router.urls
    )

    swagger = generator.get_schema(None, True)
    property_schema = swagger['definitions']['Detail']['properties']['detail']

    assert property_schema == openapi.Schema(title='Detail', type=expected_type, enum=choices)


@pytest.mark.parametrize('choices, field, expected_type', [
    ([1, 2, 3], models.IntegerField, openapi.TYPE_INTEGER),
    (["A", "B"], models.CharField, openapi.TYPE_STRING),
])
def test_nested_choice_in_array_field(choices, field, expected_type):

    # Create a model class on the fly to avoid warnings about using the several
    # model class name several times
    model_class = type(
        "%sModel" % field.__name__,
        (fake_models.FakeModel,),
        {
            "array": postgres_fields.ArrayField(
                field(choices=((i, "choice %s" % i) for i in choices))
            ),
            "__module__": "test_models",
        }
    )

    class ArraySerializer(serializers.ModelSerializer):
        class Meta:
            model = model_class
            fields = ("array",)

    class ArrayViewSet(viewsets.ModelViewSet):
        serializer_class = ArraySerializer

    router = routers.DefaultRouter()
    router.register(r'arrays', ArrayViewSet, **_basename_or_base_name('arrays'))

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title='Test array model generator', default_version='v1'),
        patterns=router.urls
    )

    swagger = generator.get_schema(None, True)
    property_schema = swagger['definitions']['Array']['properties']['array']['items']
    assert property_schema == openapi.Schema(title='Array', type=expected_type, enum=choices)


def test_json_field():
    class TestJSONFieldSerializer(serializers.Serializer):
        json = serializers.JSONField()

    class JSONViewSet(viewsets.ModelViewSet):
        serializer_class = TestJSONFieldSerializer

    router = routers.DefaultRouter()
    router.register(r'jsons', JSONViewSet, **_basename_or_base_name('jsons'))

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title='Test json field generator', default_version='v1'),
        patterns=router.urls
    )

    swagger = generator.get_schema(None, True)
    property_schema = swagger["definitions"]["TestJSONField"]["properties"]["json"]
    assert property_schema == openapi.Schema(title='Json', type=openapi.TYPE_OBJECT)


@pytest.mark.parametrize('py_type, expected_type', [
    (str, openapi.TYPE_STRING),
    (int, openapi.TYPE_INTEGER),
    (float, openapi.TYPE_NUMBER),
    (bool, openapi.TYPE_BOOLEAN),
])
def test_optional_return_type(py_type, expected_type):

    class OptionalMethodSerializer(serializers.Serializer):
        x = serializers.SerializerMethodField()

        def get_x(self, instance):
            pass

        # Add the type annotation here in order to avoid a SyntaxError in py27
        get_x.__annotations__["return"] = typing.Optional[py_type]

    class OptionalMethodViewSet(viewsets.ViewSet):
        @swagger_auto_schema(responses={200: openapi.Response("OK", OptionalMethodSerializer)})
        def retrieve(self, request, pk=None):
            return Response({'optional': None})

    router = routers.DefaultRouter()
    router.register(r'optional', OptionalMethodViewSet, **_basename_or_base_name('optional'))

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title='Test optional parameter', default_version='v1'),
        patterns=router.urls
    )
    swagger = generator.get_schema(None, True)
    property_schema = swagger["definitions"]["OptionalMethod"]["properties"]["x"]
    assert property_schema == openapi.Schema(title='X', type=expected_type, readOnly=True)


EXPECTED_DESCRIPTION = """\
  description: |-
    This is a demo project for the [drf-yasg](https://github.com/axnsan12/drf-yasg) Django Rest Framework library.

    The `swagger-ui` view can be found [here](/cached/swagger).
    The `ReDoc` view can be found [here](/cached/redoc).
    The swagger YAML document can be found [here](/cached/swagger.yaml).

    You can log in using the pre-existing `admin` user with password `passwordadmin`.
"""


def test_multiline_strings(call_generate_swagger):
    output = call_generate_swagger(format='yaml')
    print("|\n|".join(output.splitlines()[:20]))
    assert EXPECTED_DESCRIPTION in output
