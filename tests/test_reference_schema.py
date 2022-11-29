import json
from collections import OrderedDict

import pytest

from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import FieldInspector, FilterInspector, PaginatorInspector, SerializerInspector
from drf_yasg.openapi import SchemaRef


def test_reference_schema(swagger_dict, reference_schema, compare_schemas):
    compare_schemas(swagger_dict, reference_schema)


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
        info=openapi.Info(title="Test generator", default_version="v1"),
        version="v2",
    )
    swagger = generator.get_schema(mock_schema_request, True)

    json_bytes = codec_json.encode(swagger)
    swagger_dict = json.loads(json_bytes.decode('utf-8'), object_pairs_hook=OrderedDict)
    compare_schemas(swagger_dict, reference_schema)


def test_no_nested_model(swagger_dict):
    # ForeignKey models in deep ModelViewSets might wrongly be labeled as 'Nested' in the definitions section
    # see https://github.com/axnsan12/drf-yasg/issues/59
    assert 'Nested' not in swagger_dict['definitions']


@pytest.mark.parametrize('read_only_input,read_only_expected,description',
                         [(None, False, None), (False, False, ''), (True, True, 'sample')])
def test_shema_ref_setattr(resolver_mock, read_only_input, read_only_expected, description):
    ref = SchemaRef(resolver=resolver_mock, schema_name='some_name', read_only=read_only_input,
                    description=description, ignore_unresolved=True)
    additional_props = ref.all_of[1]
    assert 'readOnly' in additional_props
    assert ref['readOnly'] == read_only_expected
    assert additional_props['readOnly'] == read_only_expected
    if description is None:
        assert 'description' not in additional_props
    else:
        assert 'description' in additional_props
        assert ref['description'] == description
        assert additional_props['description'] == description


def test_schema_ref_checks(resolver_mock):
    ref = SchemaRef(resolver=resolver_mock, schema_name='some_name', read_only=True,
                    description='test', ignore_unresolved=True)

    with pytest.raises(NotImplementedError):
        ref['all_of'] = []

    with pytest.raises(NotImplementedError):
        del ref['allOf']

    with pytest.raises(NotImplementedError):
        del ref['all_of']

    with pytest.raises(NotImplementedError):
        del ref['$ref']

    ref['$ref'] = "test/reference"
    assert ref['$ref'] == "test/reference"
