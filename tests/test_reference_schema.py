import enum
import json
from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import FieldInspector, FilterInspector, PaginatorInspector, SerializerInspector


def test_reference_schema(swagger_dict, reference_schema, compare_schemas):
    compare_schemas(swagger_dict, reference_schema)


class VerisonEnum(enum.Enum):
    V1 = 'v1'
    V2 = 'v2'


class NoOpFieldInspector(FieldInspector):
    pass


class NoOpSerializerInspector(SerializerInspector):
    pass


class NoOpFilterInspector(FilterInspector):
    pass


class NoOpPaginatorInspector(PaginatorInspector):
    pass


def test_noop_inspectors(swagger_settings, mock_schema_request, codec_json, reference_schema, compare_schemas):
    from drf_yasg import app_settings

    def set_inspectors(inspectors, setting_name):
        inspectors = [__name__ + '.' + inspector.__name__ for inspector in inspectors]
        swagger_settings[setting_name] = inspectors + app_settings.SWAGGER_DEFAULTS[setting_name]

    set_inspectors([NoOpFieldInspector, NoOpSerializerInspector], 'DEFAULT_FIELD_INSPECTORS')
    set_inspectors([NoOpFilterInspector], 'DEFAULT_FILTER_INSPECTORS')
    set_inspectors([NoOpPaginatorInspector], 'DEFAULT_PAGINATOR_INSPECTORS')

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test generator", default_version=VerisonEnum.V1),
        version=VerisonEnum.V2,
    )
    swagger = generator.get_schema(mock_schema_request, True)

    json_bytes = codec_json.encode(swagger)
    swagger_dict = json.loads(json_bytes.decode('utf-8'), object_pairs_hook=OrderedDict)
    compare_schemas(swagger_dict, reference_schema)


def test_no_nested_model(swagger_dict):
    # ForeignKey models in deep ModelViewSets might wrongly be labeled as 'Nested' in the definitions section
    # see https://github.com/axnsan12/drf-yasg/issues/59
    assert 'Nested' not in swagger_dict['definitions']
