from collections import OrderedDict

from datadiff.tools import assert_equal

from drf_yasg.codecs import yaml_sane_dump
from drf_yasg.inspectors import FieldInspector, SerializerInspector, PaginatorInspector, FilterInspector


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


def test_noop_inspectors(swagger_settings, swagger_dict, reference_schema, compare_schemas):
    from drf_yasg import app_settings

    def set_inspectors(inspectors, setting_name):
        swagger_settings[setting_name] = inspectors + app_settings.SWAGGER_DEFAULTS[setting_name]

    set_inspectors([NoOpFieldInspector, NoOpSerializerInspector], 'DEFAULT_FIELD_INSPECTORS')
    set_inspectors([NoOpFilterInspector], 'DEFAULT_FILTER_INSPECTORS')
    set_inspectors([NoOpPaginatorInspector], 'DEFAULT_PAGINATOR_INSPECTORS')
    compare_schemas(swagger_dict, reference_schema)
